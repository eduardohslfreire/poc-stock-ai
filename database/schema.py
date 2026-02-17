"""
Database schema models using SQLAlchemy ORM.

This module defines all database tables for the Stock Management system:
- Product: Product catalog with pricing and stock
- Supplier: Supplier information
- PurchaseOrder: Purchase orders from suppliers
- PurchaseOrderItem: Items in each purchase order
- SaleOrder: Sales to customers
- SaleOrderItem: Items in each sale
- StockMovement: Complete stock movement history
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, 
    Date, Text, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from database.connection import Base


class Product(Base):
    """Product catalog table."""
    
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    gtin = Column(String(14), index=True)  # EAN/Barcode
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    brand = Column(String(100))
    
    # Pricing
    sale_price = Column(Numeric(15, 2), nullable=False)
    cost_price = Column(Numeric(15, 2), nullable=False)
    
    # Stock control
    current_stock = Column(Numeric(15, 3), default=0, nullable=False)
    min_stock = Column(Numeric(15, 3), default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_items = relationship("PurchaseOrderItem", back_populates="product")
    sale_items = relationship("SaleOrderItem", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}', stock={self.current_stock})>"


class Supplier(Base):
    """Supplier information table."""
    
    __tablename__ = 'supplier'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(18), unique=True, nullable=False)  # CNPJ
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(2))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', tax_id='{self.tax_id}')>"


class PurchaseOrder(Base):
    """Purchase order from suppliers."""
    
    __tablename__ = 'purchase_order'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False, index=True)
    
    # Dates
    order_date = Column(Date, nullable=False, index=True)
    received_date = Column(Date)
    
    # Amounts
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status: PENDING, RECEIVED, CANCELLED
    status = Column(String(20), nullable=False, default='PENDING', index=True)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'RECEIVED', 'CANCELLED')",
            name='check_purchase_status'
        ),
    )
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, number='{self.order_number}', status='{self.status}')>"


class PurchaseOrderItem(Base):
    """Items in purchase orders."""
    
    __tablename__ = 'purchase_order_item'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"


class SaleOrder(Base):
    """Sales order."""
    
    __tablename__ = 'sale_order'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Dates
    sale_date = Column(Date, nullable=False, index=True)
    
    # Amounts
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status: PENDING, PAID, CANCELLED
    status = Column(String(20), nullable=False, default='PAID', index=True)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("SaleOrderItem", back_populates="sale_order", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'PAID', 'CANCELLED')",
            name='check_sale_status'
        ),
    )
    
    def __repr__(self):
        return f"<SaleOrder(id={self.id}, number='{self.order_number}', status='{self.status}')>"


class SaleOrderItem(Base):
    """Items in sales orders."""
    
    __tablename__ = 'sale_order_item'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_order_id = Column(Integer, ForeignKey('sale_order.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sale_order = relationship("SaleOrder", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    
    def __repr__(self):
        return f"<SaleOrderItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"


class StockMovement(Base):
    """Complete stock movement history."""
    
    __tablename__ = 'stock_movement'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, index=True)
    
    # Movement Type: PURCHASE, SALE, ADJUSTMENT, RETURN, LOSS
    movement_type = Column(String(20), nullable=False, index=True)
    
    # Reference to origin document
    reference_id = Column(Integer)  # ID of purchase_order or sale_order
    
    # Quantities
    quantity = Column(Numeric(15, 3), nullable=False)  # positive for IN, negative for OUT
    unit_cost = Column(Numeric(15, 2))
    
    stock_before = Column(Numeric(15, 3), nullable=False)
    stock_after = Column(Numeric(15, 3), nullable=False)
    
    movement_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    notes = Column(Text)
    
    # Relationships
    product = relationship("Product", back_populates="stock_movements")
    
    __table_args__ = (
        CheckConstraint(
            "movement_type IN ('PURCHASE', 'SALE', 'ADJUSTMENT', 'RETURN', 'LOSS')",
            name='check_movement_type'
        ),
    )
    
    def __repr__(self):
        return f"<StockMovement(id={self.id}, type='{self.movement_type}', qty={self.quantity})>"
