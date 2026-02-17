"""
Database connection configuration using SQLAlchemy.

This module provides database connection setup that works with both
SQLite (default for POC) and PostgreSQL (for production migration).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment or use SQLite default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///stock.db')

# Create engine (works with SQLite and PostgreSQL)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL debugging
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.
    
    Usage:
        with next(get_db()) as db:
            # use db session
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    
    This function creates all tables defined in schema.py
    if they don't exist yet.
    """
    # Import all models to ensure they're registered
    from database.schema import (
        Product, Supplier, PurchaseOrder, PurchaseOrderItem,
        SaleOrder, SaleOrderItem, StockMovement
    )
    
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DATABASE_URL}")


def drop_all_tables():
    """
    Drop all tables from database.
    
    ⚠️  WARNING: This will delete all data!
    Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print(f"🗑️  All tables dropped from: {DATABASE_URL}")
