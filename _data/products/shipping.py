"""
Shipping and delivery related models.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

class WeightUnit(str, Enum):
    """Units for weight measurement."""
    KILOGRAMS = "kg"
    GRAMS = "g"
    POUNDS = "lb"
    OUNCES = "oz"

class DimensionUnit(str, Enum):
    """Units for dimensional measurement."""
    CENTIMETERS = "cm"
    INCHES = "in"
    METERS = "m"
    FEET = "ft"

class ShippingDimensions(BaseModel):
    """Package dimensions for shipping."""
    length: float = Field(..., ge=0, description="Length of the package")
    width: float = Field(..., ge=0, description="Width of the package")
    height: float = Field(..., ge=0, description="Height of the package")
    unit: DimensionUnit = Field(
        DimensionUnit.CENTIMETERS,
        description="Unit of measurement"
    )
    girth: Optional[float] = Field(
        None,
        ge=0,
        description="Girth of the package (for certain shipping methods)"
    )
    
    @validator('girth', always=True)
    def calculate_girth(cls, v, values):
        """Calculate girth if not provided."""
        if v is None and all(f in values for f in ['length', 'width', 'height']):
            # Girth is typically 2 * (width + height) for most carriers
            return 2 * (values['width'] + values['height'])
        return v

class ShippingWeight(BaseModel):
    """Package weight for shipping calculations."""
    value: float = Field(..., ge=0, description="Weight value")
    unit: WeightUnit = Field(
        WeightUnit.KILOGRAMS,
        description="Unit of weight"
    )
    
    def convert_to(self, target_unit: WeightUnit) -> 'ShippingWeight':
        """Convert weight to another unit."""
        if self.unit == target_unit:
            return self
            
        # Convert to grams as intermediate unit
        in_grams = {
            WeightUnit.KILOGRAMS: self.value * 1000,
            WeightUnit.GRAMS: self.value,
            WeightUnit.POUNDS: self.value * 453.59237,
            WeightUnit.OUNCES: self.value * 28.34952
        }[self.unit]
        
        # Convert to target unit
        converted_value = {
            WeightUnit.KILOGRAMS: in_grams / 1000,
            WeightUnit.GRAMS: in_grams,
            WeightUnit.POUNDS: in_grams / 453.59237,
            WeightUnit.OUNCES: in_grams / 28.34952
        }[target_unit]
        
        return ShippingWeight(value=converted_value, unit=target_unit)

class ShippingTimeEstimate(BaseModel):
    """Estimated delivery time frame."""
    min_days: int = Field(
        ...,
        alias="minDays",
        ge=0,
        description="Minimum estimated delivery days"
    )
    max_days: int = Field(
        ...,
        alias="maxDays",
        ge=0,
        description="Maximum estimated delivery days"
    )
    guaranteed: bool = Field(
        False,
        description="Whether the delivery time is guaranteed"
    )
    delivery_window: Optional[Dict[str, str]] = Field(
        None,
        alias="deliveryWindow",
        description="Specific delivery time windows"
    )
    cutoff_time: Optional[str] = Field(
        None,
        alias="cutoffTime",
        description="Order cutoff time for same-day processing"
    )
    
    @validator('max_days')
    def validate_max_days(cls, v, values):
        """Ensure max_days is not less than min_days."""
        if 'min_days' in values and v < values['min_days']:
            raise ValueError("max_days cannot be less than min_days")
        return v

class ShippingPriceBreakdown(BaseModel):
    """Detailed breakdown of shipping costs."""
    base: float = Field(..., ge=0, description="Base shipping cost")
    fuel_surcharge: Optional[float] = Field(
        None,
        alias="fuelSurcharge",
        ge=0,
        description="Additional fuel surcharge"
    )
    handling_fee: Optional[float] = Field(
        None,
        alias="handlingFee",
        ge=0,
        description="Handling fee"
    )
    insurance: Optional[float] = Field(
        None,
        ge=0,
        description="Insurance cost"
    )
    tax: Optional[float] = Field(
        None,
        ge=0,
        description="Taxes on shipping"
    )
    discount: Optional[float] = Field(
        None,
        le=0,
        description="Discount applied to shipping"
    )
    
    @property
    def total(self) -> float:
        """Calculate total shipping cost."""
        total = self.base
        if self.fuel_surcharge:
            total += self.fuel_surcharge
        if self.handling_fee:
            total += self.handling_fee
        if self.insurance:
            total += self.insurance
        if self.tax:
            total += self.tax
        if self.discount:
            total += self.discount
        return max(0, total)

class ShippingPrice(BaseModel):
    """Shipping price information."""
    amount: float = Field(..., ge=0, description="Total shipping cost")
    currency: str = Field("USD", description="Currency code (ISO 4217)")
    tax_included: bool = Field(
        False,
        alias="taxIncluded",
        description="Whether tax is included in the amount"
    )
    breakdown: Optional[ShippingPriceBreakdown] = Field(
        None,
        description="Detailed cost breakdown"
    )
    discount: Optional[Dict[str, Any]] = Field(
        None,
        description="Discount information if applicable"
    )
    
    @validator('amount')
    def validate_amount(cls, v, values):
        """Ensure amount matches breakdown total if provided."""
        if 'breakdown' in values and values['breakdown']:
            breakdown_total = values['breakdown'].total
            if not abs(v - breakdown_total) < 0.01:  # Handle floating point imprecision
                raise ValueError("Amount must match breakdown total")
        return v

class ShippingCarrier(BaseModel):
    """Shipping carrier/service provider."""
    name: str = Field(..., description="Carrier name")
    service_level: str = Field(
        ...,
        alias="serviceLevel",
        description="Service level/type"
    )
    carrier_code: Optional[str] = Field(
        None,
        alias="carrierCode",
        description="Carrier-specific code"
    )
    tracking_url: Optional[HttpUrl] = Field(
        None,
        alias="trackingUrl",
        description="Base URL for tracking"
    )
    logo_url: Optional[HttpUrl] = Field(
        None,
        alias="logoUrl",
        description="URL to carrier's logo"
    )
    phone: Optional[str] = Field(
        None,
        description="Customer service phone number"
    )
    email: Optional[str] = Field(
        None,
        description="Customer service email"
    )

class ShippingOption(BaseModel):
    """Available shipping option for a product."""
    id: str = Field(..., description="Unique identifier for the option")
    label: str = Field(..., description="Display name")
    carrier: ShippingCarrier = Field(..., description="Carrier information")
    price: ShippingPrice = Field(..., description="Pricing details")
    estimated_delivery: ShippingTimeEstimate = Field(
        ...,
        alias="estimatedDelivery",
        description="Delivery time estimate"
    )
    is_available: bool = Field(
        True,
        alias="isAvailable",
        description="Whether this option is currently available"
    )
    requires_signature: bool = Field(
        False,
        alias="requiresSignature",
        description="Whether a signature is required upon delivery"
    )
    insurance_available: bool = Field(
        False,
        alias="insuranceAvailable",
        description="Whether shipping insurance is available"
    )
    max_insurance_amount: Optional[float] = Field(
        None,
        alias="maxInsuranceAmount",
        ge=0,
        description="Maximum insurance amount available"
    )
    additional_services: List[Dict[str, Any]] = Field(
        default_factory=list,
        alias="additionalServices",
        description="Additional services available (e.g., Saturday delivery)"
    )

class ProductShippingInfo(BaseModel):
    """Complete shipping information for a product."""
    package_dimensions: ShippingDimensions = Field(
        ...,
        alias="packageDimensions",
        description="Dimensions of the packaged product"
    )
    package_weight: ShippingWeight = Field(
        ...,
        alias="packageWeight",
        description="Weight of the packaged product"
    )
    available_options: List[ShippingOption] = Field(
        ...,
        alias="availableOptions",
        description="Available shipping methods"
    )
    default_option_id: Optional[str] = Field(
        None,
        alias="defaultOptionId",
        description="ID of the default shipping option"
    )
    origin_country: str = Field(
        ...,
        alias="originCountry",
        description="ISO country code of origin"
    )
    destination_country: Optional[str] = Field(
        None,
        alias="destinationCountry",
        description="Default destination country (ISO code)"
    )
    customs_value: Optional[float] = Field(
        None,
        alias="customsValue",
        ge=0,
        description="Declared value for customs"
    )
    hazardous: bool = Field(
        False,
        description="Whether the item is considered hazardous"
    )
    restricted: bool = Field(
        False,
        description="Whether the item has shipping restrictions"
    )
    restrictions: List[str] = Field(
        default_factory=list,
        description="List of shipping restrictions"
    )
    
    def get_shipping_option(self, option_id: str) -> Optional[ShippingOption]:
        """Get a shipping option by ID."""
        return next(
            (opt for opt in self.available_options if opt.id == option_id),
            None
        )
    
    def get_default_option(self) -> Optional[ShippingOption]:
        """Get the default shipping option if available."""
        if not self.default_option_id:
            return None
        return self.get_shipping_option(self.default_option_id)
