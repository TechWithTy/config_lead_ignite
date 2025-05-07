from pydantic import BaseModel, Field
from typing import Optional, List
from config._data.user.invitation import Invitation

class CompanyInfo(BaseModel):
    """Company or organization details.
    // todo: Add DB-level unique constraint on company (company_name)
    // SaaS: Supports invitations, team management, plan change tracking, feature flags, and soft deletes.

    Company/organization details, including invitations, OAuth, plan history, and feature flags.

    * Invitations are tracked as a list of Invitation objects.
    * Supports OAuth identity providers.
    * Designed for extensibility (teams, compliance, audit).
    """
    tenant_id: str = Field(..., description="Unique tenant/org identifier for multi-tenancy")  # ! Must be unique per org (DB constraint)
    company: Optional[str] = Field(None, description="Company or organization name")  # ! Should be unique (DB constraint)
    job_title: Optional[str] = Field(None, description="User's job title/role")
    industry: Optional[str] = Field(None, description="User's industry or sector")
    company_size: Optional[str] = Field(None, description="User's company size")
    company_url: Optional[str] = Field(None, description="User's company URL")
    company_logo: Optional[str] = Field(None, description="User's company logo")
    company_description: Optional[str] = Field(None, description="User's company description")
    company_location: Optional[str] = Field(None, description="User's company location")
    company_phone: Optional[str] = Field(None, description="User's company phone number")
    company_email: Optional[str] = Field(None, description="User's company email address")
    company_website: Optional[str] = Field(None, description="User's company website")

    # --- Invitations ---
    invitations: List[Invitation] = Field(default_factory=list, description="List of invitations sent to users")

    # --- OAuth support ---
    oauth_provider: Optional[str] = Field(None, description="OAuth provider used for company SSO (e.g., Google, Microsoft)")
    oauth_provider_id: Optional[str] = Field(None, description="OAuth provider unique ID")
    oauth_connected_at: Optional[str] = Field(None, description="Timestamp when OAuth was connected (ISO 8601)")
    # todo: Add support for multiple providers, OAuth token refresh, and audit logging

    # Team management
    team_members: Optional[list] = Field(default_factory=list, description="List of user_ids for all team members in this company/org")
    # Plan upgrade/downgrade tracking
    plan_history: Optional[list] = Field(default_factory=list, description="History of plan changes (list of dicts with plan info and timestamps)")
    # Feature flags
    feature_flags: Optional[dict] = Field(default_factory=dict, description="Feature flags for staged rollouts (key: flag name, value: enabled)")
    # Soft delete/archival
    is_deleted: bool = Field(False, description="Soft delete flag for company/org")
    archived_at: Optional[str] = Field(None, description="Archival timestamp (ISO 8601)")
