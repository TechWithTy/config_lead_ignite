"""
Product data models for the application.

This package contains Pydantic models for product-related data structures,
including marketplace integrations, shipping information, and core product types.
"""
# Core enums and base models
from .enums import LicenseType, ProductCategory
from .supplier import SupplierContactInfo, SupplierVerification, DropshippingIntegration

# Marketplace integrations
from .marketplace.ali_express import (
    AliexpressShippingOption,
    AliexpressVariantAttribute,
    AliexpressVariant,
    AliexpressDropshippingItem
)

from .marketplace.amazon import (
    AmazonDiscount,
    AmazonShippingOption,
    AmazonFulfillment,
    AmazonDropshippingItem
)

# Core product models
from .product import (
    Review,
    SalesIncentive,
    ProductFaq,
    TechLicense,
    SizingChartItem,
    ProductVariantType,
    ProductColorVariant,
    ProductSizeVariant,
    ProductType
)

# Shipping models
from .shipping import (
    WeightUnit,
    DimensionUnit,
    ShippingDimensions,
    ShippingWeight,
    ShippingTimeEstimate,
    ShippingPriceBreakdown,
    ShippingPrice,
    ShippingCarrier,
    ShippingOption,
    ProductShippingInfo
)

# A/B Testing models
from .ab_test import (
    AbTestKpi,
    ABTestCopy,
    AbTestVariant,
    FacebookPixelUser,
    ABTestStatus,
    ABTest
)

__all__ = [
    # Enums
    'LicenseType',
    'ProductCategory',
    'WeightUnit',
    'DimensionUnit',
    'ABTestStatus',
    
    # Supplier models
    'SupplierContactInfo',
    'SupplierVerification',
    'DropshippingIntegration',
    
    # Marketplace models
    'AliexpressShippingOption',
    'AliexpressVariantAttribute',
    'AliexpressVariant',
    'AliexpressDropshippingItem',
    'AmazonDiscount',
    'AmazonShippingOption',
    'AmazonFulfillment',
    'AmazonDropshippingItem',
    
    # Core product models
    'Review',
    'SalesIncentive',
    'ProductFaq',
    'TechLicense',
    'SizingChartItem',
    'ProductVariantType',
    'ProductColorVariant',
    'ProductSizeVariant',
    'ProductType',
    
    # Shipping models
    'ShippingDimensions',
    'ShippingWeight',
    'ShippingTimeEstimate',
    'ShippingPriceBreakdown',
    'ShippingPrice',
    'ShippingCarrier',
    'ShippingOption',
    'ProductShippingInfo',
    
    # A/B Testing models
    'AbTestKpi',
    'ABTestCopy',
    'AbTestVariant',
    'FacebookPixelUser',
    'ABTest'
]
