"""Constants and default values for the affiliate system."""
from decimal import Decimal
from datetime import timedelta

# Default commission rates by tier (as Decimal for financial precision)
COMMISSION_RATES = {
    'standard': Decimal('0.10'),  # 10%
    'silver': Decimal('0.15'),    # 15%
    'gold': Decimal('0.20'),      # 20%
    'platinum': Decimal('0.25'),  # 25%
}

# Minimum payout amounts by currency (in cents)
MINIMUM_PAYOUTS = {
    'USD': 5000,  # $50.00
    'EUR': 4500,  # €45.00
    'GBP': 4000,  # £40.00
}

# Affiliate cookie settings
AFFILIATE_COOKIE_NAME = 'aff_id'
AFFILIATE_COOKIE_AGE = timedelta(days=365)  # 1 year

# Default settings for new affiliates
DEFAULT_AFFILIATE_SETTINGS = {
    'auto_approve': False,  # Require manual approval
    'require_w9': True,     # Require W9 for US-based affiliates
    'payout_schedule': 'monthly',
    'payment_method': 'bank_transfer',
    'tier': 'standard',
}

# Validation constants
MIN_NETWORK_SIZE = 1
MAX_NETWORK_SIZE = 1000000
MIN_COMMISSION_RATE = Decimal('0.01')  # 1%
MAX_COMMISSION_RATE = Decimal('0.50')  # 50%

# Performance thresholds for commission tiers
TIER_THRESHOLDS = {
    'silver': {
        'min_referrals': 10,
        'min_commission': Decimal('1000.00'),
        'conversion_rate': Decimal('0.05'),  # 5%
    },
    'gold': {
        'min_referrals': 50,
        'min_commission': Decimal('5000.00'),
        'conversion_rate': Decimal('0.10'),  # 10%
    },
    'platinum': {
        'min_referrals': 200,
        'min_commission': Decimal('20000.00'),
        'conversion_rate': Decimal('0.15'),  # 15%
    },
}

# Email templates for affiliate communications
EMAIL_TEMPLATES = {
    'welcome': 'affiliate/emails/welcome.html',
    'payout': 'affiliate/emails/payout_processed.html',
    'tier_upgrade': 'affiliate/emails/tier_upgraded.html',
}

# API rate limits
RATE_LIMITS = {
    'create_referral': '100/day',
    'generate_links': '50/hour',
    'check_commissions': '60/minute',
}

# Supported currencies for payouts
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']

# Default cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'affiliate_stats': 3600,  # 1 hour
    'leaderboard': 1800,      # 30 minutes
    'tier_benefits': 86400,   # 24 hours
}
