"""
A/B Testing models for product variations and experiments.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

class AbTestKpi(BaseModel):
    """Key Performance Indicator for A/B test variants."""
    name: str = Field(..., description="Name of the KPI")
    value: float = Field(..., description="Current value of the KPI")
    goal: Optional[float] = Field(
        None,
        description="Target goal for this KPI"
    )
    unit: Optional[str] = Field(
        None,
        description="Unit of measurement for the KPI value"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of what this KPI measures"
    )

class ABTestCopy(BaseModel):
    """Copy variations for A/B testing."""
    cta: str = Field(..., description="Call to action text")
    button_cta: Optional[str] = Field(
        None,
        alias="buttonCta",
        description="Button-specific call to action"
    )
    tagline: Optional[str] = Field(
        None,
        description="Short tagline or headline"
    )
    subtitle: Optional[str] = Field(
        None,
        description="Subtitle or secondary headline"
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description"
    )
    whats_in_it_for_me: str = Field(
        ...,
        alias="whatsInItForMe",
        description="Value proposition for the user"
    )
    target_audience: str = Field(
        ...,
        alias="targetAudience",
        description="Description of the target audience"
    )
    pain_point: str = Field(
        ...,
        alias="painPoint",
        description="Customer pain point being addressed"
    )
    solution: str = Field(
        ...,
        description="How this variant solves the pain point"
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="List of key highlights or features"
    )
    highlighted_words: List[str] = Field(
        default_factory=list,
        alias="highlightedWords",
        description="Words to highlight in the UI"
    )
    additional_info: Optional[str] = Field(
        None,
        alias="additionalInfo",
        description="Any additional information or notes"
    )
    ai_generated: Optional[Dict[str, Any]] = Field(
        None,
        alias="aiGenerated",
        description="Metadata about AI generation if applicable"
    )

class AbTestVariant(BaseModel):
    """A single variant in an A/B test."""
    name: str = Field(..., description="Name of the variant")
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Traffic percentage allocated to this variant (0-100)"
    )
    copy: Optional[ABTestCopy] = Field(
        None,
        description="Copy variations for this variant"
    )
    variant_description: Optional[str] = Field(
        None,
        alias="variantDescription",
        description="Description of what makes this variant different"
    )
    kpis: List[AbTestKpi] = Field(
        default_factory=list,
        description="Key performance indicators for this variant"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this variant"
    )
    
    @validator('percentage')
    def validate_percentage(cls, v):
        """Ensure percentage is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v

class FacebookPixelUser(BaseModel):
    """Facebook Pixel user information for tracking."""
    id: str = Field(..., description="Facebook user ID")
    email: Optional[str] = Field(
        None,
        description="User's email address (hashed if PII)"
    )
    phone: Optional[str] = Field(
        None,
        description="User's phone number (hashed if PII)"
    )
    external_id: Optional[str] = Field(
        None,
        alias="externalId",
        description="External user ID"
    )
    client_ip_address: Optional[str] = Field(
        None,
        alias="clientIpAddress",
        description="IP address of the user's device"
    )
    client_user_agent: Optional[str] = Field(
        None,
        alias="clientUserAgent",
        description="User agent string of the user's browser"
    )
    fbc: Optional[str] = Field(
        None,
        description="Facebook click ID (fbc) for tracking ad clicks"
    )
    fbp: Optional[str] = Field(
        None,
        description="Facebook browser ID (fbp) for tracking browsers"
    )
    subscription_id: Optional[str] = Field(
        None,
        alias="subscriptionId",
        description="Subscription ID if applicable"
    )
    fb_login_id: Optional[str] = Field(
        None,
        alias="fbLoginId",
        description="Facebook login ID"
    )

class ABTestStatus(str, Enum):
    """Status of an A/B test."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ABTest(BaseModel):
    """Complete A/B test configuration and results."""
    id: str = Field(..., description="Unique identifier for the test")
    name: str = Field(..., description="Name of the A/B test")
    description: Optional[str] = Field(
        None,
        description="Detailed description of the test"
    )
    variants: List[AbTestVariant] = Field(
        ...,
        min_items=2,
        description="List of test variants (at least 2 required)"
    )
    start_date: datetime = Field(
        ...,
        alias="startDate",
        description="When the test is scheduled to start"
    )
    end_date: Optional[datetime] = Field(
        None,
        alias="endDate",
        description="When the test is scheduled to end (optional)"
    )
    status: ABTestStatus = Field(
        ABTestStatus.DRAFT,
        description="Current status of the test"
    )
    is_active: bool = Field(
        False,
        alias="isActive",
        description="Whether the test is currently active"
    )
    facebook_pixel_users: List[FacebookPixelUser] = Field(
        default_factory=list,
        alias="facebookPixelUsers",
        description="Users being tracked via Facebook Pixel"
    )
    target_audience: Optional[str] = Field(
        None,
        alias="targetAudience",
        description="Description of the target audience for this test"
    )
    kpis: List[AbTestKpi] = Field(
        default_factory=list,
        description="Key performance indicators for the overall test"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the test"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the test"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="createdAt",
        description="When the test was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="updatedAt",
        description="When the test was last updated"
    )
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date if provided."""
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v
    
    @validator('variants')
    def validate_variants_percentage(cls, v):
        """Ensure variant percentages sum to 100%."""
        total = sum(variant.percentage for variant in v)
        if not (99.9 <= total <= 100.1):  # Allow for floating point imprecision
            raise ValueError("Sum of variant percentages must be 100%")
        return v
    
    def get_variant(self, name: str) -> Optional[AbTestVariant]:
        """Get a variant by name."""
        return next((v for v in self.variants if v.name == name), None)
    
    def get_winning_variant(self) -> Optional[AbTestVariant]:
        """Get the variant with the highest KPI value."""
        if not self.variants or not all(v.kpis for v in self.variants):
            return None
            
        # Find variant with highest primary KPI value
        return max(
            self.variants,
            key=lambda v: v.kpis[0].value if v.kpis else 0
        )
