"""
Example usage of the new imminent stockout risk detection tools.

This script demonstrates how to use the new preventive stockout
detection features added on 2026-02-08.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.stockout_risk import (
    detect_imminent_stockout_risk,
    get_pending_order_summary
)


def print_separator(title=""):
    """Print a nice separator."""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print(f"\n{'-' * 80}\n")


def test_imminent_stockout_detection():
    """Test the imminent stockout risk detection."""
    print_separator("TEST 1: Imminent Stockout Risk Detection")
    
    # Detect products at risk in the next 7 days
    at_risk = detect_imminent_stockout_risk(
        days_forecast=30,
        days_history=90,
        min_days_threshold=7
    )
    
    print(f"Found {len(at_risk)} products at risk of stockout\n")
    
    # Show critical products
    critical = [p for p in at_risk if p['risk_level'] in ['CRITICAL', 'HIGH']]
    print(f"🔴 {len(critical)} CRITICAL/HIGH risk products:\n")
    
    for product in critical[:5]:  # Top 5
        print(f"Product: {product['name']}")
        print(f"  SKU: {product['sku']}")
        print(f"  Current Stock: {product['current_stock']:.2f} units")
        print(f"  Daily Sales: {product['avg_daily_sales']:.2f} units/day")
        print(f"  Days Until Stockout: {product['days_until_stockout']:.1f} days")
        print(f"  Risk Level: {product['risk_level']}")
        
        # Pending orders info
        po = product['pending_orders']
        if po['count'] > 0:
            print(f"  Pending Orders: {po['count']} orders, {po['total_quantity']:.0f} units")
            print(f"  Orders Sufficient: {'✅ Yes' if po['is_sufficient'] else '❌ No'}")
            if po['is_delayed']:
                print(f"  ⚠️  ORDER DELAYED: {po['oldest_order_days']} days pending")
        else:
            print(f"  Pending Orders: ❌ NONE")
        
        print(f"  Gap to Cover: {product['gap_quantity']:.0f} units")
        print(f"  Potential Lost Revenue: R$ {product['potential_lost_revenue']:,.2f}")
        print(f"  Recommendation: {product['recommendation']}")
        print()


def test_pending_orders_summary():
    """Test the pending orders summary."""
    print_separator("TEST 2: Pending Purchase Orders Summary")
    
    pending = get_pending_order_summary()
    
    print(f"Found {len(pending)} pending purchase orders\n")
    
    # Show delayed orders
    delayed = [p for p in pending if p['is_delayed']]
    if delayed:
        print(f"⚠️  {len(delayed)} DELAYED orders (> 7 days):\n")
        
        for order in delayed[:5]:  # Top 5
            print(f"Order: {order['order_number']}")
            print(f"  Supplier: {order['supplier_name']}")
            print(f"  Order Date: {order['order_date']}")
            print(f"  Days Pending: {order['days_pending']} days")
            print(f"  Products: {len(order['products'])} items")
            print(f"  Total Value: R$ {order['total_value']:,.2f}")
            print(f"  Items:")
            for item in order['products'][:3]:  # First 3 items
                print(f"    - {item['product_name']}: {item['quantity']:.0f} units @ R$ {item['unit_price']:.2f}")
            print()
    else:
        print("✅ No delayed orders found!")
    
    # Show all pending orders
    if pending:
        print(f"\nAll Pending Orders:\n")
        total_value = sum(p['total_value'] for p in pending)
        print(f"Total pending value: R$ {total_value:,.2f}\n")
        
        for order in pending[:10]:  # Top 10
            status = "⏰ DELAYED" if order['is_delayed'] else "⏳ Pending"
            print(f"{status} | {order['order_number']} | {order['supplier_name']} | "
                  f"{order['days_pending']}d | R$ {order['total_value']:,.2f}")


def test_specific_product():
    """Test checking a specific product's risk and pending orders."""
    print_separator("TEST 3: Specific Product Analysis")
    
    # Get at-risk products
    at_risk = detect_imminent_stockout_risk(min_days_threshold=30)
    
    if not at_risk:
        print("No products at risk found.")
        return
    
    # Pick first product
    product = at_risk[0]
    product_id = product['product_id']
    
    print(f"Analyzing Product: {product['name']} (ID: {product_id})\n")
    
    # Get pending orders for this product
    pending = get_pending_order_summary(product_id=product_id)
    
    print(f"Risk Analysis:")
    print(f"  Current Stock: {product['current_stock']:.2f} units")
    print(f"  Daily Demand: {product['avg_daily_sales']:.2f} units/day")
    print(f"  Days Until Stockout: {product['days_until_stockout']:.1f} days")
    print(f"  Forecasted Demand (30d): {product['forecasted_demand']:.2f} units")
    print(f"  Risk Level: {product['risk_level']}\n")
    
    print(f"Pending Orders: {len(pending)} orders\n")
    
    if pending:
        for order in pending:
            print(f"  Order {order['order_number']}:")
            print(f"    Supplier: {order['supplier_name']}")
            print(f"    Date: {order['order_date']} ({order['days_pending']} days ago)")
            
            for item in order['products']:
                if item['product_id'] == product_id:
                    print(f"    Quantity: {item['quantity']:.0f} units @ R$ {item['unit_price']:.2f}")
                    print(f"    Subtotal: R$ {item['subtotal']:,.2f}")
            print()
    
    print(f"Action Required: {product['recommendation']}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  STOCKOUT RISK DETECTION TOOLS - TEST SUITE")
    print("  Added: 2026-02-08")
    print("=" * 80)
    
    try:
        # Test 1: Detect products at risk
        test_imminent_stockout_detection()
        
        # Test 2: View all pending orders
        test_pending_orders_summary()
        
        # Test 3: Analyze specific product
        test_specific_product()
        
        print_separator()
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
