from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum
from typing import Optional

class BillingStatus(str, Enum):
    paid = "paid"
    pending = "pending"
    failed = "failed"
    refunded = "refunded"

class BillingHistoryItem(BaseModel):
    """Represents a single billing event or invoice for a user."""
    invoice_id: str = Field(..., description="Unique invoice or transaction ID")
    amount: float = Field(..., description="Amount billed")
    currency: str = Field(..., description="Currency code (e.g., USD)")
    date: str = Field(..., description="Billing date (ISO 8601)")
    description: Optional[str] = Field(None, description="Description or notes for the billing item")
    status: BillingStatus = Field(BillingStatus.paid, description="Status of the billing (paid, pending, failed, refunded)")
    payment_method: Optional[str] = Field(None, description="Payment method used (e.g., card, PayPal)")
    receipt_url: Optional[str] = Field(None, description="URL to view/download the receipt")
    refunded_at: Optional[str] = Field(None, description="Timestamp when refunded (ISO 8601)")
    # todo: Add audit fields and compliance info
