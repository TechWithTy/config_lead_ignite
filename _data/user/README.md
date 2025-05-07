# Modular User Domain Models

This folder contains modularized Pydantic models for user management in a SaaS context. Each major domain is split into its own file for maintainability, testability, and clarity.

## Structure

- **core.py**: Core identity models (PII, ContactInfo, LocationInfo, SecuritySettings, OnboardingStatus)
- **company_info.py**: Company/organization details, invitations, team management, plan history, feature flags, soft delete
- **marketing_profile.py**: Marketing and professional profile fields
- **social_links.py**: Social media/profile links
- **platform_access.py**: Role, permissions, account status, company owner flag
- **user_settings.py**: Arbitrary user preferences/settings
- **utils.py**: Shared enums and utility models (roles, permissions, credit usage, etc.)

## Usage Example

```python
from config._data.user.core import PII, ContactInfo, LocationInfo, SecuritySettings, OnboardingStatus
from config._data.user.company_info import CompanyInfo
from config._data.user.marketing_profile import MarketingProfile
from config._data.user.social_links import SocialLinks
from config._data.user.platform_access import PlatformAccess
from config._data.user.user_settings import UserSettings
from config._data.user.utils import RoleType, Permission

# Example: Constructing a user
user = User(
    tenant_id="org_123",
    pii=PII(user_id="u1", first_name="Jane", last_name="Doe"),
    contact=ContactInfo(email="jane@example.com"),
    location=LocationInfo(city="SF"),
    security=SecuritySettings(two_factor_enabled=True),
    onboarding=OnboardingStatus(completed=False),
    company=CompanyInfo(tenant_id="org_123", company="Acme Inc."),
    marketing=MarketingProfile(),
    socials=SocialLinks(linkedin="https://linkedin.com/in/janedoe"),
    platform=PlatformAccess(role=RoleType.admin),
    preferences=UserSettings(settings={"theme": "dark"})
)
```

## Best Practices

- **Type Safety**: Use `List[str]`, `Dict[str, Any]`, and Pydantic validators for strict schemas.
- **Separation of Concerns**: Add new user-related domains as new files/modules.
- **Testing**: Place tests in a sibling `tests/` directory or in each domain module.
- **Security**: Encrypt PII fields at rest. Use soft delete flags instead of hard deletion for recovery.
- **Extensibility**: Add fields for SaaS features (invitations, teams, feature flags, plan history) as needed.

## Extending

To add a new domain (e.g., notifications):
1. Create a new file (e.g., `notification_settings.py`).
2. Define the model.
3. Import and use it in `user.py` or other relevant modules.

---

_This structure follows clean code and pragmatic modular design for scalable SaaS applications._
