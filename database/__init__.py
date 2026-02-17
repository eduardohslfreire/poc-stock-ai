"""
Database module for Stock Management POC.

This module provides database connection, models, and data seeding functionality.
"""

from database.connection import engine, SessionLocal, get_db, init_db
from database.schema import (
    Product,
    Supplier,
    PurchaseOrder,
    PurchaseOrderItem,
    SaleOrder,
    SaleOrderItem,
    StockMovement,
)

__all__ = [
    'engine',
    'SessionLocal',
    'get_db',
    'init_db',
    'Product',
    'Supplier',
    'PurchaseOrder',
    'PurchaseOrderItem',
    'SaleOrder',
    'SaleOrderItem',
    'StockMovement',
]
