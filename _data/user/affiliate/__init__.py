"""
Affiliate Management System

This module provides models and schemas for managing affiliate marketing functionality,
including affiliate profiles, referrals, commissions, and payouts.
"""
from .enums import (
    NetworkSize,
    AccountType,
    AffiliateStatus,
    RealEstateExperience,
    PaymentMethod,
    PayoutSchedule,
    CommissionTier
)

from .models import (
    AffiliateProfile,
    BankAccountInfo,
    TaxInfo,
    AffiliatePayout,
    AffiliateReferral,
    AffiliateNotificationPreferences
)

from .schemas import (
    AffiliateCreateRequest,
    BankAccountCreateRequest,
    TaxInfoRequest,
    PayoutRequest,
    ReferralCreateRequest,
    AffiliateResponse,
    BankAccountResponse,
    PayoutResponse,
    ReferralResponse,
    DashboardStatsResponse,
    CommissionTierInfo,
    AffiliateUpdateRequest,
    AdminAffiliateUpdateRequest
)

from . import constants

__all__ = [
    # Enums
    'NetworkSize',
    'AccountType',
    'AffiliateStatus',
    'RealEstateExperience',
    'PaymentMethod',
    'PayoutSchedule',
    'CommissionTier',
    
    # Models
    'AffiliateProfile',
    'BankAccountInfo',
    'TaxInfo',
    'AffiliatePayout',
    'AffiliateReferral',
    'AffiliateNotificationPreferences',
    
    # Request Schemas
    'AffiliateCreateRequest',
    'BankAccountCreateRequest',
    'TaxInfoRequest',
    'PayoutRequest',
    'ReferralCreateRequest',
    
    # Response Schemas
    'AffiliateResponse',
    'BankAccountResponse',
    'PayoutResponse',
    'ReferralResponse',
    'DashboardStatsResponse',
    'CommissionTierInfo',
    
    # Update Schemas
    'AffiliateUpdateRequest',
    'AdminAffiliateUpdateRequest',
    
    # Constants
    'constants'
]
