"""
MLSRealEstateLead: Global lead type for MLS (Multiple Listing Service) real estate data.
Designed for integration with campaign, call, social, and text modules.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class MLSRealEstateLead(BaseModel):
    lead_id: str = Field(..., description="Unique identifier for the lead (MLS or internal)")
    mls_number: Optional[str] = Field(None, description="MLS listing number")
    property_address: str = Field(..., description="Property address")
    city: str = Field(..., description="City where the property is located")
    state: str = Field(..., description="State where the property is located")
    zip_code: str = Field(..., description="ZIP or postal code")
    price: Optional[float] = Field(None, description="Listing price")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, description="Square footage of the property")
    lot_size: Optional[float] = Field(None, description="Lot size in acres or square feet")
    year_built: Optional[int] = Field(None, description="Year the property was built")
    property_type: Optional[str] = Field(None, description="Type of property (single family, condo, etc.)")
    status: Optional[str] = Field(None, description="Listing status (active, pending, sold, etc.)")
    agent_name: Optional[str] = Field(None, description="Listing agent's name")
    agent_phone: Optional[str] = Field(None, description="Listing agent's phone number")
    agent_email: Optional[str] = Field(None, description="Listing agent's email address")
    open_house_dates: Optional[List[str]] = Field(default_factory=list, description="List of open house dates (ISO 8601)")
    description: Optional[str] = Field(None, description="Property description")
    images: Optional[List[str]] = Field(default_factory=list, description="URLs of property images")
    virtual_tour_url: Optional[str] = Field(None, description="URL to virtual tour or video walkthrough")
    source: Optional[str] = Field(None, description="Source system or MLS provider")
    created_at: Optional[str] = Field(None, description="Lead creation timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(None, description="Last updated timestamp (ISO 8601)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Custom tags or labels for segmentation")
    # todo: Add fields for campaign, call, social, and text integrations as needed

    class Config:
        title = "MLSRealEstateLead"
        arbitrary_types_allowed = True
