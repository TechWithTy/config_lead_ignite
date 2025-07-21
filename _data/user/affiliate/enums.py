"""Enums for the affiliate system."""
from enum import Enum, auto

class NetworkSize(str, Enum):
    """Represents the size of an affiliate's network."""
    ONE_TO_100 = "1-100"
    HUNDRED_TO_1K = "101-1,000"
    ONEK_TO_10K = "1,001-10,000"
    TENK_TO_100K = "10,001-100,000"
    OVER_100K = "100,001+"

class AccountType(str, Enum):
    """Type of bank account for affiliate payouts."""
    CHECKING = "checking"
    SAVINGS = "savings"

class AffiliateStatus(str, Enum):
    """Current status of an affiliate."""
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

class RealEstateExperience(str, Enum):
    """Level of real estate experience."""
    YES = "yes"
    NO = "no"
    INDIRECT = "indirect"

class PaymentMethod(str, Enum):
    """Available payment methods for affiliates."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    WISE = "wise"
    CRYPTO = "crypto"

class PayoutSchedule(str, Enum):
    """Available payout schedules."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class CommissionTier(str, Enum):
    """Commission tiers for affiliates."""
    STANDARD = "standard"  # 10%
    SILVER = "silver"      # 15%
    GOLD = "gold"          # 20%
    PLATINUM = "platinum"  # 25%
