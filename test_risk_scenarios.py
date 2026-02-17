"""
Test script to validate the imminent stockout risk scenarios.

This script calls detect_imminent_stockout_risk() and displays the results
to verify that the fake data was generated correctly.
"""

from tools.stockout_risk import detect_imminent_stockout_risk, get_pending_order_summary
from tools.stock_analysis import detect_stock_rupture


def print_separator(title="", char="="):
    """Print a nice separator."""
    if title:
        print(f"\n{char * 80}")
        print(f"  {title}")
        print(f"{char * 80}\n")
    else:
        print(f"\n{char * 80}\n")


def test_imminent_risks():
    """Test imminent stockout risk detection."""
    print_separator("🎯 TESTING IMMINENT STOCKOUT RISK SCENARIOS")
    
    # Detect products at risk in the next 7 days
    print("🔍 Calling detect_imminent_stockout_risk(days_forecast=30, min_days_threshold=7)...\n")
    
    at_risk = detect_imminent_stockout_risk(
        days_forecast=30,
        days_history=90,
        min_days_threshold=7
    )
    
    print(f"📊 Found {len(at_risk)} products at risk\n")
    
    if not at_risk:
        print("❌ NO PRODUCTS AT RISK FOUND!")
        print("   This might mean:")
        print("   1. Database was not regenerated with new scenarios")
        print("   2. All products have sufficient stock")
        print("   3. Products don't have recent sales")
        print("\n   Run: python reseed_with_risk_scenarios.py")
        return
    
    # Group by risk level
    by_risk = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for product in at_risk:
        by_risk[product['risk_level']].append(product)
    
    # Display by risk level
    for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        products = by_risk[risk_level]
        if not products:
            continue
        
        icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}[risk_level]
        print(f"{icon} {risk_level} RISK: {len(products)} products")
        print("-" * 80)
        
        for p in products[:10]:  # Show first 10
            print(f"\n  Product: {p['name']}")
            print(f"  SKU: {p['sku']}")
            print(f"  Current Stock: {p['current_stock']:.1f} units")
            print(f"  Daily Demand: {p['avg_daily_sales']:.2f} units/day")
            print(f"  Days Until Stockout: {p['days_until_stockout']:.1f} days")
            
            po = p['pending_orders']
            if po['count'] > 0:
                print(f"  Pending Orders: {po['count']} order(s), {po['total_quantity']:.0f} units")
                print(f"  Orders Sufficient: {'✅ Yes' if po['is_sufficient'] else '❌ No'}")
                if po['is_delayed']:
                    print(f"  ⏰ DELAYED: {po['oldest_order_days']} days pending!")
            else:
                print(f"  Pending Orders: ❌ NONE")
            
            print(f"  Gap to Cover: {p['gap_quantity']:.0f} units")
            print(f"  Potential Lost Revenue: R$ {p['potential_lost_revenue']:,.2f}")
            print(f"  💡 {p['recommendation']}")
        
        if len(products) > 10:
            print(f"\n  ... and {len(products) - 10} more")
        
        print()


def test_scenario_breakdown():
    """Show breakdown of expected scenarios."""
    print_separator("📋 EXPECTED SCENARIO BREAKDOWN", "=")
    
    at_risk = detect_imminent_stockout_risk(days_forecast=30, min_days_threshold=7)
    
    if not at_risk:
        print("❌ No products at risk found. Run reseed_with_risk_scenarios.py first.")
        return
    
    # Categorize
    no_po = [p for p in at_risk if p['pending_orders']['count'] == 0]
    with_insufficient = [p for p in at_risk 
                         if p['pending_orders']['count'] > 0 
                         and not p['pending_orders']['is_sufficient']]
    with_delayed = [p for p in at_risk 
                    if p['pending_orders']['count'] > 0 
                    and p['pending_orders']['is_delayed']]
    with_sufficient = [p for p in at_risk 
                       if p['pending_orders']['count'] > 0 
                       and p['pending_orders']['is_sufficient']]
    
    print("Scenario A: Products WITHOUT purchase orders")
    print(f"  Expected: ~6 products")
    print(f"  Found: {len(no_po)} products")
    if no_po:
        for p in no_po[:3]:
            print(f"    - {p['name']}: {p['current_stock']:.0f} units, {p['days_until_stockout']:.1f} days")
    
    print("\nScenario B: Products WITH INSUFFICIENT purchase orders")
    print(f"  Expected: ~4 products")
    print(f"  Found: {len(with_insufficient)} products")
    if with_insufficient:
        for p in with_insufficient[:3]:
            po = p['pending_orders']
            print(f"    - {p['name']}: PO qty={po['total_quantity']:.0f}, gap={p['gap_quantity']:.0f}")
    
    print("\nScenario C: Products WITH DELAYED purchase orders")
    print(f"  Expected: ~3 products")
    print(f"  Found: {len(with_delayed)} products")
    if with_delayed:
        for p in with_delayed[:3]:
            po = p['pending_orders']
            print(f"    - {p['name']}: PO delayed {po['oldest_order_days']} days")
    
    print("\nScenario D: Products WITH SUFFICIENT purchase orders")
    print(f"  Expected: ~2 products")
    print(f"  Found: {len(with_sufficient)} products")
    if with_sufficient:
        for p in with_sufficient[:2]:
            po = p['pending_orders']
            print(f"    - {p['name']}: PO qty={po['total_quantity']:.0f} (sufficient)")
    
    print("\n" + "=" * 80)
    print(f"✅ Total scenarios validated: {len(at_risk)}")


def test_pending_orders():
    """Test pending orders summary."""
    print_separator("📦 PENDING PURCHASE ORDERS")
    
    pending = get_pending_order_summary()
    
    if not pending:
        print("ℹ️  No pending orders found")
        return
    
    print(f"Found {len(pending)} pending purchase orders\n")
    
    # Show delayed orders
    delayed = [p for p in pending if p['is_delayed']]
    if delayed:
        print(f"⏰ DELAYED ORDERS ({len(delayed)}):")
        print("-" * 80)
        for order in delayed[:5]:
            print(f"\n  Order: {order['order_number']}")
            print(f"  Supplier: {order['supplier_name']}")
            print(f"  Order Date: {order['order_date']}")
            print(f"  Days Pending: {order['days_pending']} days")
            print(f"  Products: {len(order['products'])} items")
            print(f"  Total Value: R$ {order['total_value']:,.2f}")
    else:
        print("✅ No delayed orders")


def test_comparison():
    """Compare preventive vs reactive detection."""
    print_separator("🔄 COMPARISON: PREVENTIVE vs REACTIVE")
    
    # Preventive (NEW)
    at_risk = detect_imminent_stockout_risk(min_days_threshold=7)
    print(f"🔮 PREVENTIVE (will run out): {len(at_risk)} products")
    print("   Products with stock > 0 that will run out soon")
    
    # Reactive (OLD)
    ruptured = detect_stock_rupture(days_lookback=14)
    print(f"\n🚨 REACTIVE (already out): {len(ruptured)} products")
    print("   Products with stock = 0 that had recent sales")
    
    print(f"\n💡 Total products needing attention: {len(at_risk) + len(ruptured)}")
    print("   Preventive helps avoid the reactive scenario!")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  IMMINENT STOCKOUT RISK - SCENARIO VALIDATION")
    print("  Generated: 2026-02-08")
    print("=" * 80)
    
    try:
        # Test 1: Imminent risks
        test_imminent_risks()
        
        # Test 2: Scenario breakdown
        test_scenario_breakdown()
        
        # Test 3: Pending orders
        test_pending_orders()
        
        # Test 4: Comparison
        test_comparison()
        
        print_separator("✅ ALL TESTS COMPLETED", "=")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
