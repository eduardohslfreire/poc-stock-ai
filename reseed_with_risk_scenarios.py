"""
Regenerate database with imminent stockout risk scenarios.

This script drops the existing database and creates a new one with
special scenarios designed to test the detect_imminent_stockout_risk() tool.
"""

import sys
from database.seed_data import main as seed_main

print("\n" + "=" * 70)
print("🔄 REGENERATING DATABASE WITH RISK SCENARIOS")
print("=" * 70)
print("\n⚠️  WARNING: This will DELETE all existing data!")
print("=" * 70)

response = input("\nContinue? (yes/no): ").strip().lower()

if response != 'yes':
    print("\n❌ Operation cancelled.")
    sys.exit(0)

print("\n🚀 Starting database regeneration...\n")

try:
    # Run the seed script (it handles drop and create)
    seed_main()
    
    print("\n" + "=" * 70)
    print("✅ DATABASE REGENERATED SUCCESSFULLY!")
    print("=" * 70)
    
    print("\n📊 New Scenarios Created:")
    print("-" * 70)
    print("1. 🔴 CRITICAL: 6 products without purchase orders")
    print("   - Low stock (8-25 units)")
    print("   - High demand (5-10 units/day)")
    print("   - NO purchase orders")
    print("   - Will run out in 2-5 days")
    
    print("\n2. 🟠 HIGH RISK: 4 products with insufficient purchase orders")
    print("   - Very low stock (5-15 units)")
    print("   - High demand (4-8 units/day)")
    print("   - Has purchase orders but INSUFFICIENT quantity")
    print("   - Will run out even with pending orders")
    
    print("\n3. ⏰ HIGH RISK: 3 products with delayed purchase orders")
    print("   - Low stock (10-20 units)")
    print("   - Medium demand (3-6 units/day)")
    print("   - Has purchase orders but DELAYED (10-15 days old)")
    print("   - May run out before order arrives")
    
    print("\n4. ✅ LOW RISK: 2 products with sufficient purchase orders")
    print("   - Lowish stock (15-30 units)")
    print("   - Low-medium demand (3-5 units/day)")
    print("   - Has SUFFICIENT and RECENT purchase orders")
    print("   - For comparison (good scenario)")
    
    print("\n" + "=" * 70)
    print("🧪 How to Test:")
    print("=" * 70)
    print("\n1. Start the agent:")
    print("   streamlit run app/streamlit_app.py")
    
    print("\n2. Ask the agent:")
    print('   "Quais produtos têm risco de ficar sem estoque?"')
    print('   "Me mostre produtos que vão zerar nos próximos 7 dias"')
    print('   "Há produtos sem pedido de compra?"')
    print('   "Quais pedidos estão atrasados?"')
    
    print("\n3. Test the tool directly:")
    print("   python examples/test_stockout_risk.py")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error during regeneration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
