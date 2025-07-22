"""
Cart state management and operations.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, TypeVar, Type, TYPE_CHECKING
from pydantic import BaseModel, Field

from ..exceptions import CartError
from .cart_item import CartItem
from .cart_summary import CartSummary

# Avoid circular imports
if TYPE_CHECKING:
    from ...products import ProductType, ProductVariantType

T = TypeVar('T', bound='CartState')

class CartState(BaseModel):
    """Current state of the user's shopping cart."""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this cart"
    )
    user_id: Optional[str] = Field(
        None,
        alias="userId",
        description="ID of the user who owns this cart"
    )
    items: List[CartItem] = Field(
        default_factory=list,
        description="Items in the cart"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="createdAt",
        description="When the cart was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        alias="updatedAt",
        description="When the cart was last updated"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional cart metadata"
    )
    
    # Cart methods
    def add_item(
        self: T,
        product: 'ProductType',
        quantity: int = 1,
        variant: Optional['ProductVariantType'] = None,
        notes: Optional[str] = None
    ) -> T:
        """Add an item to the cart or update quantity if it exists."""
        if quantity < 1:
            raise CartError("Quantity must be at least 1")
        
        # Create cart item from product
        item_id = f"{product.id}:{variant.id if variant else 'base'}"
        
        # Check if item already exists in cart
        existing_item = next((i for i in self.items if i.id == item_id), None)
        
        if existing_item:
            # Update quantity of existing item
            existing_item.quantity += quantity
            existing_item.subtotal = existing_item.quantity * existing_item.unit_price
        else:
            # Create new cart item
            from .product_variant import ProductVariant  # Avoid circular import
            
            selected_variant = None
            if variant:
                selected_variant = ProductVariant(
                    id=variant.id,
                    name=variant.name,
                    price=float(variant.price),
                    sku=getattr(variant, 'sku', None),
                    requires_shipping=getattr(variant, 'requires_shipping', True)
                )
            
            new_item = CartItem(
                id=item_id,
                product_id=product.id,
                name=product.name,
                price=float(product.price),
                selected_variant=selected_variant,
                quantity=quantity,
                image=product.images[0] if hasattr(product, 'images') and product.images else None,
                category=getattr(product, 'category', None),
                notes=notes,
                requires_shipping=getattr(product, 'requires_shipping', True)
            )
            
            self.items.append(new_item)
        
        self.updated_at = datetime.utcnow()
        return self
    
    def remove_item(self: T, item_id: str) -> T:
        """Remove an item from the cart by ID."""
        self.items = [item for item in self.items if item.id != item_id]
        self.updated_at = datetime.utcnow()
        return self
    
    def update_quantity(self: T, item_id: str, quantity: int) -> T:
        """Update the quantity of an item in the cart."""
        if quantity < 1:
            return self.remove_item(item_id)
            
        for item in self.items:
            if item.id == item_id:
                item.quantity = quantity
                item.subtotal = item.unit_price * quantity
                break
                
        self.updated_at = datetime.utcnow()
        return self
    
    def clear(self: T) -> T:
        """Remove all items from the cart."""
        self.items = []
        self.updated_at = datetime.utcnow()
        return self
    
    # Calculated properties
    @property
    def item_count(self) -> int:
        """Get the total number of unique items in the cart."""
        return len(self.items)
    
    @property
    def total_quantity(self) -> int:
        """Get the total quantity of all items in the cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self) -> float:
        """Calculate the subtotal of all items in the cart."""
        return sum(item.subtotal for item in self.items)
    
    @property
    def requires_shipping(self) -> bool:
        """Check if any items in the cart require shipping."""
        return any(item.requires_shipping for item in self.items)
    
    def get_summary(
        self,
        shipping_cost: float = 0.0,
        tax_rate: Optional[float] = None,
        discount_amount: float = 0.0
    ) -> CartSummary:
        """Generate a summary of the cart's contents and costs."""
        subtotal = self.subtotal
        
        # Calculate tax if rate is provided
        tax = 0.0
        if tax_rate is not None:
            tax = (subtotal - discount_amount) * (tax_rate / 100)
        
        # Create and return summary
        return CartSummary(
            subtotal=subtotal,
            shipping=shipping_cost,
            tax=tax,
            discount=discount_amount,
            total=subtotal + shipping_cost + tax - discount_amount,
            item_count=self.item_count,
            total_quantity=self.total_quantity,
            requires_shipping=self.requires_shipping,
            tax_rate=tax_rate
        )
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
