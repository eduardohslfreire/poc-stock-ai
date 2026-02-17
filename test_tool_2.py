"""
Test script for Tool #2: analyze_slow_moving_stock

This script tests the slow-moving stock analysis tool.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.stock_analysis import analyze_slow_moving_stock

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #2: analyze_slow_moving_stock")
    print("=" * 70)
    
    # Test with default parameters (30 days)
    print("\n📊 Test 1: Analyzing slow-moving stock (30+ days without sale)")
    print("-" * 70)
    
    results = analyze_slow_moving_stock(days_threshold=30)
    
    print(f"\n✅ Found {len(results)} slow-moving products\n")
    
    if results:
        # Show top 10 by stock value
        print("💰 TOP 10 PRODUCTS BY TIED-UP CAPITAL:")
        print("-" * 70)
        
        for i, product in enumerate(results[:10], 1):
            days_display = f"{product['days_without_sale']} days" if product['days_without_sale'] else "Never sold"
            
            print(f"\n{i}. {product['name']} (SKU: {product['sku']})")
            print(f"   Category: {product['category']}")
            print(f"   Current Stock: {product['current_stock']:.2f} units")
            print(f"   💰 Stock Value: R$ {product['stock_value']:,.2f}")
            print(f"   Last Sale: {product['last_sale_date'] or 'Never'}")
            print(f"   Days Without Sale: {days_display}")
            print(f"   📋 {product['recommendation']}")
        
        # Calculate totals
        total_stock_value = sum(p['stock_value'] for p in results)
        never_sold = sum(1 for p in results if p['days_without_sale'] is None)
        urgent_count = sum(1 for p in results if 'URGENT' in p['recommendation'])
        
        print("\n" + "=" * 70)
        print("📈 SUMMARY")
        print("=" * 70)
        print(f"Total Slow-Moving Products: {len(results)}")
        print(f"Never Sold: {never_sold} products")
        print(f"Urgent Action Required: {urgent_count} products")
        print(f"💰 Total Capital Tied Up: R$ {total_stock_value:,.2f}")
        
        # Breakdown by urgency
        urgent = [p for p in results if 'URGENT' in p['recommendation']]
        important = [p for p in results if 'IMPORTANT' in p['recommendation']]
        monitor = [p for p in results if 'MONITOR' in p['recommendation']]
        
        print(f"\n🔴 URGENT (90+ days): {len(urgent)} products - R$ {sum(p['stock_value'] for p in urgent):,.2f}")
        print(f"🟡 IMPORTANT (60-90 days): {len(important)} products - R$ {sum(p['stock_value'] for p in important):,.2f}")
        print(f"🟢 MONITOR (30-60 days): {len(monitor)} products - R$ {sum(p['stock_value'] for p in monitor):,.2f}")
        
    else:
        print("✅ No slow-moving stock detected! Inventory is turning over well.")
    
    # Test with stricter threshold
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Analyzing very slow-moving stock (60+ days)")
    print("-" * 70)
    
    results_60d = analyze_slow_moving_stock(days_threshold=60)
    print(f"\n✅ Found {len(results_60d)} products without sale for 60+ days")
    
    if results_60d:
        total_value_60d = sum(p['stock_value'] for p in results_60d)
        print(f"💰 Capital tied up (60+ days): R$ {total_value_60d:,.2f}\n")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #2 TEST COMPLETED!")
    print("=" * 70)
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
