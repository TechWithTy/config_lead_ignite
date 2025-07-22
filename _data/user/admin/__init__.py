"""
Admin and Support Models

This module contains models for admin and support functionality including:
- Role-based access control (RBAC)
- Audit logging
- User management
- Credit system
- Event logging
"""

from .role import Role, UserRole
from .audit_log import AuditLog, AuditAction, AuditResourceType
from .credit import CreditAdjustment, CreditType
from .event_log import EventLog, EventType

__all__ = [
    # Role Management
    'Role',
    'UserRole',
    
    # Audit Logging
    'AuditLog',
    'AuditAction',
    'AuditResourceType',
    
    # Credit System
    'CreditAdjustment',
    'CreditType',
    
    # Event Logging
    'EventLog',
    'EventType'
]
