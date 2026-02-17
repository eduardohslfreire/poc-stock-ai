"""
Auto-seed database on first run (for Streamlit Cloud deployment).

This module checks if the database exists and is populated.
If not, it automatically generates the fake data.
"""

import os
from pathlib import Path
from database.connection import SessionLocal
from database.schema import Product


def check_database_exists() -> bool:
    """
    Check if database file exists and has data.
    
    Returns:
        True if database exists and has products, False otherwise
    """
    db_path = Path("stock.db")
    
    # Check if file exists
    if not db_path.exists():
        return False
    
    # Check if file has data
    try:
        session = SessionLocal()
        product_count = session.query(Product).count()
        session.close()
        return product_count > 0
    except Exception:
        return False


def auto_seed_if_needed(force: bool = False, verbose: bool = True) -> bool:
    """
    Automatically seed database if it doesn't exist or is empty.
    
    Args:
        force: Force re-seeding even if database exists
        verbose: Print status messages
    
    Returns:
        True if seeding was performed, False if skipped
    """
    if not force and check_database_exists():
        if verbose:
            print("✅ Database already exists and has data. Skipping seed.")
        return False
    
    if verbose:
        print("\n" + "=" * 70)
        print("🌱 AUTO-SEEDING DATABASE")
        print("=" * 70)
        print("\nThis is the first run. Generating fake data...")
        print("This will take ~30 seconds.\n")
    
    try:
        # Import and run seed
        from database.seed_data import main as seed_main
        seed_main()
        
        if verbose:
            print("\n✅ Database seeded successfully!")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"\n❌ Error during auto-seed: {e}")
            import traceback
            traceback.print_exc()
        raise


if __name__ == "__main__":
    """Allow running as standalone script."""
    auto_seed_if_needed(force=False, verbose=True)
