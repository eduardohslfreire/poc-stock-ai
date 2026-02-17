"""
Database setup script.

This script initializes the database by creating all tables.
Run this before seeding data.

Usage:
    python setup_db.py
"""

from database.connection import init_db, drop_all_tables, DATABASE_URL

def main():
    print("=" * 60)
    print("🚀 Stock Management POC - Database Setup")
    print("=" * 60)
    print(f"\n📁 Database: {DATABASE_URL}\n")
    
    # Ask for confirmation if recreating
    choice = input("Do you want to (1) Create tables or (2) Recreate (drop + create)? [1/2]: ").strip()
    
    if choice == '2':
        confirm = input("⚠️  WARNING: This will delete ALL data! Are you sure? [yes/no]: ").strip().lower()
        if confirm == 'yes':
            print("\n🗑️  Dropping all tables...")
            drop_all_tables()
        else:
            print("\n❌ Operation cancelled.")
            return
    
    print("\n🔨 Creating tables...")
    init_db()
    
    print("\n✅ Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Configure your .env file with OPENAI_API_KEY")
    print("   2. Run: python database/seed_data.py (to populate with fake data)")
    print("   3. Run: streamlit run app/streamlit_app.py (to start the app)")
    print()

if __name__ == "__main__":
    main()
