"""
Test script to verify AI agent setup without making API calls.

This script validates that all components are properly imported and configured.
"""

import sys
import os

print("=" * 70)
print("🧪 TESTING AI AGENT SETUP")
print("=" * 70)

# Test 1: Import all tools
print("\n✅ Test 1: Importing all tools...")
try:
    from tools.stock_analysis import detect_stock_rupture, analyze_slow_moving_stock
    from tools.supplier_analysis import analyze_supplier_performance
    from tools.loss_detection import detect_stock_losses, get_explicit_losses
    from tools.purchase_suggestions import suggest_purchase_order, group_suggestions_by_supplier
    from tools.sales_analysis import get_top_selling_products, get_sales_by_category
    from tools.turnover_analysis import analyze_purchase_to_sale_time, get_inventory_age_distribution
    from tools.alerts import get_stock_alerts
    from tools.availability_analysis import detect_availability_issues
    from tools.profitability_analysis import calculate_profitability_analysis, get_profitability_summary
    from tools.abc_analysis import get_abc_analysis
    print("   ✅ All tools imported successfully!")
except Exception as e:
    print(f"   ❌ Error importing tools: {e}")
    sys.exit(1)

# Test 2: Import agent modules
print("\n✅ Test 2: Importing agent modules...")
try:
    from agent.prompts import SYSTEM_PROMPT, WELCOME_MESSAGE, ERROR_MESSAGE
    from agent.stock_agent import create_tools, create_stock_agent
    print("   ✅ Agent modules imported successfully!")
except Exception as e:
    print(f"   ❌ Error importing agent modules: {e}")
    sys.exit(1)

# Test 3: Create tools list
print("\n✅ Test 3: Creating tools list...")
try:
    tools = create_tools()
    print(f"   ✅ Created {len(tools)} tools successfully!")
    print(f"\n   📋 Tools registered:")
    for i, tool in enumerate(tools, 1):
        print(f"      {i:2}. {tool.name}")
except Exception as e:
    print(f"   ❌ Error creating tools: {e}")
    sys.exit(1)

# Test 4: Check environment variables
print("\n✅ Test 4: Checking environment configuration...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    print(f"   ✅ OPENAI_API_KEY found: {masked_key}")
else:
    print("   ⚠️  OPENAI_API_KEY not found in .env")
    print("      Agent creation will fail without it!")

model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
print(f"   ✅ OPENAI_MODEL: {model}")

db_url = os.getenv('DATABASE_URL', 'sqlite:///stock.db')
print(f"   ✅ DATABASE_URL: {db_url}")

# Test 5: Check database
print("\n✅ Test 5: Checking database...")
import os.path
if os.path.exists('stock.db'):
    size = os.path.getsize('stock.db')
    print(f"   ✅ Database found: stock.db ({size:,} bytes)")
    
    # Quick query to check data
    from database.connection import SessionLocal
    from database.schema import Product, SaleOrder
    
    session = SessionLocal()
    try:
        product_count = session.query(Product).count()
        sale_count = session.query(SaleOrder).count()
        print(f"   ✅ Products: {product_count}")
        print(f"   ✅ Sales: {sale_count}")
    finally:
        session.close()
else:
    print("   ⚠️  Database not found: stock.db")
    print("      Run: python setup_db.py && python database/seed_data.py")

# Test 6: Test Streamlit app import
print("\n✅ Test 6: Testing Streamlit app...")
try:
    # We can't fully import streamlit app (it runs immediately)
    # But we can check if the file exists and has no syntax errors
    app_path = 'app/streamlit_app.py'
    if os.path.exists(app_path):
        print(f"   ✅ Streamlit app found: {app_path}")
        # Compile to check syntax
        with open(app_path, 'r') as f:
            compile(f.read(), app_path, 'exec')
        print("   ✅ No syntax errors in Streamlit app")
    else:
        print(f"   ❌ Streamlit app not found: {app_path}")
except Exception as e:
    print(f"   ❌ Error in Streamlit app: {e}")

# Summary
print("\n" + "=" * 70)
print("📊 SETUP VALIDATION SUMMARY")
print("=" * 70)

checks = {
    "Tools Import": "✅",
    "Agent Modules": "✅",
    "Tools List": "✅",
    "Environment": "✅" if api_key else "⚠️",
    "Database": "✅" if os.path.exists('stock.db') else "⚠️",
    "Streamlit App": "✅"
}

for check, status in checks.items():
    print(f"   {status} {check}")

if all(status == "✅" for status in checks.values()):
    print("\n🎉 ALL CHECKS PASSED!")
    print("\n🚀 Ready to run: python run_app.py")
else:
    print("\n⚠️  Some checks have warnings. Review messages above.")
    if not api_key:
        print("\n🔑 IMPORTANT: Configure OPENAI_API_KEY in .env file!")

print("\n" + "=" * 70)
