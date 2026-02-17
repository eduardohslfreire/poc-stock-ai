"""
Test script for Tool #5: suggest_purchase_order

This script tests the purchase suggestion tools.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.purchase_suggestions import suggest_purchase_order, group_suggestions_by_supplier

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #5: suggest_purchase_order")
    print("=" * 70)
    
    # Test 1: Purchase suggestions
    print("\n📊 Test 1: Generating purchase suggestions (30-day forecast)")
    print("-" * 70)
    
    suggestions = suggest_purchase_order(days_forecast=30, days_history=90)
    
    print(f"\n✅ Generated {len(suggestions)} purchase suggestions\n")
    
    if suggestions:
        # Group by priority
        high = [s for s in suggestions if s['priority'] == 'HIGH']
        medium = [s for s in suggestions if s['priority'] == 'MEDIUM']
        low = [s for s in suggestions if s['priority'] == 'LOW']
        
        print(f"🔴 HIGH Priority: {len(high)} products")
        print(f"🟡 MEDIUM Priority: {len(medium)} products")
        print(f"🟢 LOW Priority: {len(low)} products\n")
        
        print("🛒 TOP 10 PURCHASE RECOMMENDATIONS:")
        print("-" * 70)
        
        for i, item in enumerate(suggestions[:10], 1):
            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            icon = priority_icon.get(item['priority'], "⚪")
            
            print(f"\n{i}. {icon} {item['name']} (SKU: {item['sku']})")
            print(f"   Category: {item['category']}")
            print(f"   Current Stock: {item['current_stock']:.1f} units")
            print(f"   📊 Avg Daily Sales: {item['avg_daily_sales']:.2f} units/day")
            print(f"   📈 30-Day Forecast: {item['forecasted_demand']:.1f} units")
            print(f"   📦 Stock Needed: {item['stock_needed']:.1f} units")
            print(f"   ✅ Suggested Order: {item['suggested_quantity']} units")
            print(f"   💰 Order Value: R$ {item['order_value']:,.2f}")
            print(f"   ⏰ Days Until Stockout: {item['days_until_stockout'] or 'N/A'}")
            print(f"   Priority: {item['priority']}")
        
        # Calculate totals
        total_order_value = sum(s['order_value'] for s in suggestions)
        total_items = sum(s['suggested_quantity'] for s in suggestions)
        
        print("\n" + "=" * 70)
        print("📈 PURCHASE ORDER SUMMARY")
        print("=" * 70)
        print(f"Total Products to Order: {len(suggestions)}")
        print(f"Total Items: {total_items} units")
        print(f"💰 Total Order Value: R$ {total_order_value:,.2f}")
        print(f"\n🔴 High Priority: {len(high)} products - R$ {sum(s['order_value'] for s in high):,.2f}")
        print(f"🟡 Medium Priority: {len(medium)} products - R$ {sum(s['order_value'] for s in medium):,.2f}")
        print(f"🟢 Low Priority: {len(low)} products - R$ {sum(s['order_value'] for s in low):,.2f}")
        
    else:
        print("✅ No purchases needed! Stock levels are adequate.")
    
    # Test 2: Group by supplier
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Grouping suggestions by supplier")
    print("-" * 70)
    
    grouped = group_suggestions_by_supplier()
    
    print(f"\n✅ Grouped into {len(grouped)} supplier orders\n")
    
    if grouped:
        print("🏢 PURCHASE ORDERS BY SUPPLIER:")
        print("-" * 70)
        
        for i, supplier in enumerate(grouped, 1):
            print(f"\n{i}. {supplier['supplier_name']}")
            print(f"   Products to Order: {supplier['products_count']}")
            print(f"   High Priority Items: {supplier['high_priority_items']}")
            print(f"   💰 Total Order Value: R$ {supplier['total_order_value']:,.2f}")
            
            # Show top 3 products
            print(f"   Top Products:")
            for j, product in enumerate(supplier['products'][:3], 1):
                priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                icon = priority_icon.get(product['priority'], "⚪")
                print(f"      {j}. {icon} {product['name'][:40]} - {product['quantity']} units (R$ {product['order_value']:,.2f})")
        
        # Summary
        total_suppliers = len(grouped)
        total_value = sum(s['total_order_value'] for s in grouped)
        
        print("\n" + "=" * 70)
        print("📈 SUPPLIER ORDER SUMMARY")
        print("=" * 70)
        print(f"Total Suppliers: {total_suppliers}")
        print(f"💰 Total Value: R$ {total_value:,.2f}")
        print(f"Average Order per Supplier: R$ {total_value/total_suppliers:,.2f}")
    
    # Test 3: Different forecast periods
    print("\n" + "=" * 70)
    print("\n📊 Test 3: Comparing different forecast periods")
    print("-" * 70)
    
    suggestions_7d = suggest_purchase_order(days_forecast=7)
    suggestions_60d = suggest_purchase_order(days_forecast=60)
    
    print(f"\n7-day forecast: {len(suggestions_7d)} products")
    if suggestions_7d:
        print(f"   Total value: R$ {sum(s['order_value'] for s in suggestions_7d):,.2f}")
    
    print(f"\n30-day forecast: {len(suggestions)} products")
    if suggestions:
        print(f"   Total value: R$ {sum(s['order_value'] for s in suggestions):,.2f}")
    
    print(f"\n60-day forecast: {len(suggestions_60d)} products")
    if suggestions_60d:
        print(f"   Total value: R$ {sum(s['order_value'] for s in suggestions_60d):,.2f}")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #5 TEST COMPLETED!")
    print("=" * 70)
    
    return len(suggestions) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
