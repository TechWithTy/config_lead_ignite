from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class CreditType(str, Enum):
    """Types of credits in the system"""
    LEAD = "lead"
    AI = "ai"
    SKIP_TRACE = "skip_trace"
    CUSTOM = "custom"

class CreditAdjustmentReason(str, Enum):
    """Reasons for credit adjustments"""
    REFUND = "refund"
    GRANT = "grant"
    PURCHASE = "purchase"
    USAGE = "usage"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    PROMOTIONAL = "promotional"
    SYSTEM = "system"
    OTHER = "other"

class CreditBalance(BaseModel):
    """User's credit balance for a specific credit type"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    credit_type: CreditType
    balance: float = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }

class CreditTransaction(BaseModel):
    """Record of a credit transaction"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    credit_type: CreditType
    amount: float
    balance_before: float
    balance_after: float
    
    # Metadata
    reference_id: Optional[UUID] = None  # Reference to related entity (e.g., campaign_id)
    reference_type: Optional[str] = None  # Type of reference (e.g., 'campaign', 'subscription')
    
    # Adjustment details
    reason: CreditAdjustmentReason
    notes: Optional[str] = None
    
    # Who initiated this transaction
    actor_id: UUID  # Could be user_id or system
    actor_type: str = "system"  # 'user', 'admin', 'system'
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda dt: dt.isoformat()
        }
    
    @validator('amount')
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v

class CreditAdjustmentRequest(BaseModel):
    """Request model for adjusting user credits"""
    user_id: UUID
    credit_type: CreditType
    amount: float
    reason: CreditAdjustmentReason
    notes: Optional[str] = None
    reference_id: Optional[UUID] = None
    reference_type: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v

class UserCreditSummary(BaseModel):
    """Summary of a user's credits across all types"""
    user_id: UUID
    balances: Dict[CreditType, float]
    last_updated: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# Helper functions for credit operations
def calculate_new_balance(
    current_balance: float,
    adjustment: float,
    allow_negative: bool = False
) -> float:
    """Calculate new balance after an adjustment"""
    new_balance = current_balance + adjustment
    if not allow_negative and new_balance < 0:
        raise ValueError("Insufficient credits")
    return new_balance

def create_transaction(
    user_id: UUID,
    credit_type: CreditType,
    amount: float,
    current_balance: float,
    reason: CreditAdjustmentReason,
    actor_id: UUID,
    actor_type: str = "system",
    notes: Optional[str] = None,
    reference_id: Optional[UUID] = None,
    reference_type: Optional[str] = None
) -> CreditTransaction:
    """Helper to create a new credit transaction"""
    new_balance = calculate_new_balance(current_balance, amount)
    
    return CreditTransaction(
        user_id=user_id,
        credit_type=credit_type,
        amount=amount,
        balance_before=current_balance,
        balance_after=new_balance,
        reason=reason,
        actor_id=actor_id,
        actor_type=actor_type,
        notes=notes,
        reference_id=reference_id,
        reference_type=reference_type
    )
