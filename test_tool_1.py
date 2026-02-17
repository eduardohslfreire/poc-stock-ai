"""
Test script for Tool #1: detect_stock_rupture

This script tests the stock rupture detection tool.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.stock_analysis import detect_stock_rupture

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #1: detect_stock_rupture")
    print("=" * 70)
    
    # Test with default parameters (14 days)
    print("\n📊 Test 1: Detecting stock ruptures (last 14 days)")
    print("-" * 70)
    
    results = detect_stock_rupture(days_lookback=14)
    
    print(f"\n✅ Found {len(results)} products in stock rupture\n")
    
    if results:
        # Show top 5 most critical
        print("🔴 TOP 5 MOST CRITICAL RUPTURES:")
        print("-" * 70)
        
        for i, product in enumerate(results[:5], 1):
            print(f"\n{i}. {product['name']} (SKU: {product['sku']})")
            print(f"   Category: {product['category']}")
            print(f"   Current Stock: {product['current_stock']}")
            print(f"   Recent Sales: {product['recent_sales_count']} orders")
            print(f"   Total Sold (14d): {product['total_quantity_sold']} units")
            print(f"   Daily Demand: {product['estimated_daily_demand']} units/day")
            print(f"   Days Out of Stock: {product['days_out_of_stock']}")
            print(f"   💰 Estimated Lost Revenue: R$ {product['lost_revenue_estimate']:,.2f}")
            print(f"   Last Sale: {product['last_sale_date']}")
        
        # Calculate totals
        total_lost_revenue = sum(p['lost_revenue_estimate'] for p in results)
        total_daily_demand = sum(p['estimated_daily_demand'] for p in results)
        
        print("\n" + "=" * 70)
        print("📈 SUMMARY")
        print("=" * 70)
        print(f"Total Products in Rupture: {len(results)}")
        print(f"Total Daily Demand Unmet: {total_daily_demand:.2f} units/day")
        print(f"💰 Total Estimated Lost Revenue: R$ {total_lost_revenue:,.2f}")
        
    else:
        print("✅ No stock ruptures detected! Stock levels are healthy.")
    
    # Test with different timeframe
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Detecting ruptures (last 7 days)")
    print("-" * 70)
    
    results_7d = detect_stock_rupture(days_lookback=7)
    print(f"\n✅ Found {len(results_7d)} products in rupture (7-day window)\n")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #1 TEST COMPLETED!")
    print("=" * 70)
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
