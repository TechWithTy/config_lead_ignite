from pydantic import BaseModel, Field
from typing import Optional

class MarketingProfile(BaseModel):
    """Marketing SaaS-specific and professional summary."""
    target_audience: str = Field(
        "SMB Owners, Marketing Leads, SaaS Founders",
        description="Primary audience for marketing/outreach",
    )
    professional_summary: str = Field(
        "Marketing SaaS specialist with expertise in growth strategy, automation, and customer engagement. Proven track record in launching successful B2B campaigns and driving SaaS product adoption.",
        description="Short summary of professional background",
    )
    resume_url: Optional[str] = Field(
        "https://www.linkedin.com/in/your-linkedin-url", description="Resume/LinkedIn"
    )
    portfolio_site: Optional[str] = Field(
        "https://www.yourportfolio.com/", description="Link to marketing portfolio"
    )
    website: Optional[str] = Field(None, description="Personal or company website")
