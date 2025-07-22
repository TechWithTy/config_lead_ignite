# ======================================================
# User Model (Lead Ignite)
# ======================================================
# * Main user schema for all core, analytics, campaign, and settings data
# * Organized by domain for clarity and maintainability
# ======================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime

# --- Core Identity & Contact Info ---
from config_lead_ignite._data.user.core import (
    PII, ContactInfo, LocationInfo, OnboardingStatus
)

# --- Company & Marketing ---
from config_lead_ignite._data.user.company.company_info import CompanyInfo as GlobalCompanyInfo
from config_lead_ignite._data.user.context.marketing_profile import MarketingProfile

# --- Socials & Links ---
from config_lead_ignite._data.user.socials.social_links import SocialLinks

# --- Team & Permissions ---
from config_lead_ignite._data.user.team.global_team import GlobalTeam

# --- Billing & Subscriptions ---
from config_lead_ignite._data.user.billing.global_billing import GlobalBilling

# --- Analytics, Research, Kanban, Blogs ---
from config_lead_ignite._data.user.analytics.global_analytics import GlobalAnalytics
from config_lead_ignite._data.user.research.global_research_stats import GlobalResearchStats
from config_lead_ignite._data.user.kanban.global_kanban import GlobalKanban
from config_lead_ignite._data.user.blogs.global_blog import GlobalBlog

# --- Campaigns & AI ---
from config_lead_ignite._data.user.campaign.global_campaign import GlobalCampaign
from config_lead_ignite._data.user.ai_config.global_ai_config import GlobalAIConfig
from config_lead_ignite._data.user.context.global_ai_context import GlobalAIContext
from config_lead_ignite._data.user.media.media_models import MediaAsset

# --- User Settings & Misc ---
from config_lead_ignite._data.user.settings.global_user_settings import GlobalUserSettings
from config_lead_ignite._data.user.cache.saved_search import SavedSearch

# --- Affiliate System ---
from config_lead_ignite._data.user.affiliate.models import AffiliateProfile

# --- Testing Program ---
from config_lead_ignite._data.user.testing.models import (
    BetaTester, 
    PilotTester, 
    TesterType
)

# --- AI Chat Threads ---
from config_lead_ignite._data.user.ai_chat_threads.models import (
    Thread, 
    Message, 
    AIProfile,
    ParticipantRole,
    ThreadSettings,
    MessageType,
    MessageStatus
)

# --- Shopping Cart ---
from config_lead_ignite._data.user.cart import CartState


class User(BaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize cart with user ID if available
        if hasattr(self, 'pii') and hasattr(self.pii, 'user_id') and hasattr(self, 'cart') and not self.cart.user_id:
            self.cart.user_id = str(self.pii.user_id)

    # === Core Identity ===
    pii: PII
    contact: ContactInfo
    media: List[MediaAsset]
    location: LocationInfo
    onboarding: OnboardingStatus

    # === Organization & Socials ===
    company: GlobalCompanyInfo
    marketing: MarketingProfile
    socials: SocialLinks

    # === Campaigns & Content ===
    campaigns: GlobalCampaign = Field(default_factory=GlobalCampaign, description="User's global campaign")
    blogs: GlobalBlog = Field(default_factory=GlobalBlog, description="User's global blog")
    kanban: GlobalKanban = Field(default_factory=GlobalKanban, description="User's global kanban")

    # === Analytics, Research, AI ===
    analytics: Optional[GlobalAnalytics] = Field(None, description="Aggregated analytics for all social platforms")
    research: List[GlobalResearchStats] = Field(default_factory=list, description="Research results for topics of interest")
    ai_context: Optional[GlobalAIContext] = Field(None, description="AI context for the user")
    ai_config: Optional[GlobalAIConfig] = Field(None, description="AI config for the user")

    # === Team & Billing ===
    teams: List[GlobalTeam] = Field(default_factory=list, description="List of tenant_ids for all orgs/teams this user belongs to")
    billing: GlobalBilling = Field(default_factory=GlobalBilling, description="User's billing history")

    # === User Preferences & Saved Data ===
    user_settings: Optional[GlobalUserSettings] = Field(None, description="User settings")
    saved_searches: List[SavedSearch] = Field(default_factory=list, description="User's saved searches")

    # === Affiliate System ===
    affiliate_profile: Optional[AffiliateProfile] = Field(
        None,
        description="Affiliate profile and settings if user is an affiliate"
    )

    # === Testing Program ===
    beta_tester: Optional[BetaTester] = Field(
        None,
        description="Beta testing profile if user is a beta tester"
    )
    pilot_tester: Optional[PilotTester] = Field(
        None,
        description="Pilot testing profile if user is a pilot tester"
    )

    # === AI Chat Threads ===
    ai_chat_threads: List[Thread] = Field(
        default_factory=list,
        description="List of AI chat threads the user is participating in"
    )
    ai_profiles: List[AIProfile] = Field(
        default_factory=list,
        description="User's custom AI profiles and configurations"
    )
    default_ai_profile_id: Optional[UUID] = Field(
        None,
        description="ID of the user's default AI profile"
    )
    
    # === Shopping Cart ===
    cart: CartState = Field(
        default_factory=CartState,
        description="User's shopping cart"
    )
    
    # === Feature Flags & Archival ===
    feature_flags: dict = Field(default_factory=dict, description="Feature flags for staged rollouts (key: flag name, value: enabled)")
    is_deleted: bool = Field(False, description="Soft delete flag for user")
    archived_at: Optional[str] = Field(None, description="Archival timestamp (ISO 8601)")

    # === AI Chat Thread Methods ===
    
    async def create_chat_thread(
        self,
        title: Optional[str] = None,
        is_group: bool = False,
        is_public: bool = False,
        participant_ids: Optional[List[UUID]] = None,
        ai_profile_ids: Optional[List[UUID]] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Optional[Thread]:
        """
        Create a new chat thread with the current user as the creator.
        
        Args:
            title: Optional title for the thread
            is_group: Whether this is a group thread
            is_public: Whether the thread is public
            participant_ids: List of user IDs to add as participants
            ai_profile_ids: List of AI profile IDs to add as participants
            settings: Additional thread settings
            
        Returns:
            The created thread or None if creation failed
        """
        try:
            # Create the thread
            thread = Thread(
                title=title or f"Chat with {self.pii.first_name}",
                creator_id=self.pii.user_id,
                is_group=is_group,
                is_public=is_public,
                settings=settings or {}
            )
            
            # Add to user's threads
            self.ai_chat_threads.append(thread)
            
            # Add creator as admin
            thread.add_participant(
                user_id=self.pii.user_id,
                role=ParticipantRole.ADMIN
            )
            
            # Add other participants
            if participant_ids:
                for user_id in participant_ids:
                    if user_id != self.pii.user_id:  # Don't add creator again
                        thread.add_participant(
                            user_id=user_id,
                            role=ParticipantRole.USER
                        )
            
            # Add AI participants
            if ai_profile_ids:
                for ai_profile_id in ai_profile_ids:
                    thread.add_ai_participant(ai_profile_id)
            
            return thread
            
        except Exception as e:
            print(f"Failed to create chat thread: {str(e)}")
            return None
    
    def get_chat_thread(self, thread_id: UUID) -> Optional[Thread]:
        """Get a chat thread by ID if the user has access to it."""
        for thread in self.ai_chat_threads:
            if thread.id == thread_id:
                return thread
        return None
    
    def get_chat_threads(
        self,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Thread]:
        """
        Get user's chat threads with pagination and filtering.
        
        Args:
            include_archived: Whether to include archived threads
            limit: Maximum number of threads to return
            offset: Number of threads to skip for pagination
            
        Returns:
            List of threads the user has access to
        """
        threads = [
            t for t in self.ai_chat_threads
            if include_archived or not t.is_archived
        ]
        
        # Sort by most recently updated
        threads.sort(key=lambda t: t.updated_at, reverse=True)
        
        return threads[offset:offset + limit]
    
    async def archive_chat_thread(self, thread_id: UUID) -> bool:
        """Archive a chat thread."""
        thread = self.get_chat_thread(thread_id)
        if not thread:
            return False
            
        thread.is_archived = True
        thread.updated_at = datetime.utcnow()
        return True
    
    async def unarchive_chat_thread(self, thread_id: UUID) -> bool:
        """Unarchive a chat thread."""
        thread = self.get_chat_thread(thread_id)
        if not thread:
            return False
            
        thread.is_archived = False
        thread.updated_at = datetime.utcnow()
        return True
    
    async def delete_chat_thread(self, thread_id: UUID) -> bool:
        """Permanently delete a chat thread."""
        thread = self.get_chat_thread(thread_id)
        if not thread:
            return False
            
        # Check if user has permission to delete
        participant = thread.get_participant(self.pii.user_id)
        if not participant or participant.role not in [ParticipantRole.ADMIN, ParticipantRole.OWNER]:
            return False
            
        # Remove from user's threads
        self.ai_chat_threads = [t for t in self.ai_chat_threads if t.id != thread_id]
        return True
    
    # === AI Profile Management ===
    
    def add_ai_profile(self, profile: AIProfile) -> bool:
        """Add an AI profile to the user's collection."""
        if not isinstance(profile, AIProfile):
            return False
            
        # Check for duplicate ID
        if any(p.id == profile.id for p in self.ai_profiles):
            return False
            
        self.ai_profiles.append(profile)
        
        # Set as default if this is the first profile
        if len(self.ai_profiles) == 1:
            self.default_ai_profile_id = profile.id
            
        return True
    
    def get_ai_profile(self, profile_id: UUID) -> Optional[AIProfile]:
        """Get an AI profile by ID."""
        return next((p for p in self.ai_profiles if p.id == profile_id), None)
    
    def set_default_ai_profile(self, profile_id: UUID) -> bool:
        """Set the default AI profile."""
        if any(p.id == profile_id for p in self.ai_profiles):
            self.default_ai_profile_id = profile_id
            return True
        return False
    
    def remove_ai_profile(self, profile_id: UUID) -> bool:
        """Remove an AI profile."""
        initial_count = len(self.ai_profiles)
        self.ai_profiles = [p for p in self.ai_profiles if p.id != profile_id]
        
        # Update default if needed
        if self.default_ai_profile_id == profile_id:
            self.default_ai_profile_id = self.ai_profiles[0].id if self.ai_profiles else None
            
        return len(self.ai_profiles) < initial_count
    
    # === Validation & Utilities ===
    
    @field_validator('default_ai_profile_id')
    def validate_default_ai_profile(cls, v, values):
        """Validate that the default_ai_profile_id exists in ai_profiles."""
        if v is None:
            return v
            
        if 'ai_profiles' not in values:
            return v
            
        if not any(p.id == v for p in values['ai_profiles']):
            # Reset to None if the referenced profile doesn't exist
            return None
            
        return v
    @classmethod
    def validate_unique(cls, users: List['User'], user_id: str, email: str, tenant_id: str) -> bool:
        """
        // ! Validate uniqueness of user_id, email, and tenant_id (in-memory check only).
        // ! Must enforce at DB level for production.
        """
        for user in users:
            if user.pii.user_id == user_id or user.contact.email == email or getattr(user, 'tenant_id', None) == tenant_id:
                return False
        return True
    
    def update_testing_profile(self, tester_data: dict):
        """
        Update or create a testing profile for the user.
        
        Args:
            tester_data: Dictionary containing tester information
            
        Returns:
            The updated testing profile (BetaTester or PilotTester)
        """
        from config_lead_ignite._data.user.testing.models import TesterType
        
        tester_type = tester_data.get('tester_type')
        
        if tester_type == TesterType.BETA:
            if self.beta_tester is None:
                self.beta_tester = BetaTester(
                    user_id=self.pii.user_id,
                    **tester_data
                )
            else:
                # Update existing beta tester
                for key, value in tester_data.items():
                    if hasattr(self.beta_tester, key):
                        setattr(self.beta_tester, key, value)
            return self.beta_tester
            
        elif tester_type == TesterType.PILOT:
            if self.pilot_tester is None:
                self.pilot_tester = PilotTester(
                    user_id=self.pii.user_id,
                    **tester_data
                )
            else:
                # Update existing pilot tester
                for key, value in tester_data.items():
                    if hasattr(self.pilot_tester, key):
                        setattr(self.pilot_tester, key, value)
            return self.pilot_tester
            
        return None

# * End of User model

    class Config:
        use_enum_values = True