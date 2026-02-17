"""
Test script for Tool #7: analyze_purchase_to_sale_time

This script tests the turnover analysis tools.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.turnover_analysis import analyze_purchase_to_sale_time, get_inventory_age_distribution

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #7: analyze_purchase_to_sale_time")
    print("=" * 70)
    
    # Test 1: Purchase to sale time analysis
    print("\n📊 Test 1: Analyzing purchase-to-sale time (90 days)")
    print("-" * 70)
    
    results = analyze_purchase_to_sale_time(days_period=90, min_purchases=1)
    
    print(f"\n✅ Analyzed {len(results)} products\n")
    
    if results:
        # Group by rating
        fast = [r for r in results if r['turnover_rating'] == 'FAST']
        medium = [r for r in results if r['turnover_rating'] == 'MEDIUM']
        slow = [r for r in results if r['turnover_rating'] == 'SLOW']
        
        print(f"⚡ FAST (≤7 days): {len(fast)} products")
        print(f"🚶 MEDIUM (8-21 days): {len(medium)} products")
        print(f"🐌 SLOW (>21 days): {len(slow)} products\n")
        
        print("🐌 TOP 10 SLOWEST TURNOVER:")
        print("-" * 70)
        
        for i, product in enumerate(results[:10], 1):
            rating_icon = {"FAST": "⚡", "MEDIUM": "🚶", "SLOW": "🐌"}
            icon = rating_icon.get(product['turnover_rating'], "⚪")
            
            print(f"\n{i}. {icon} {product['name']} (SKU: {product['sku']})")
            print(f"   Category: {product['category']}")
            print(f"   Purchases Analyzed: {product['purchases_count']}")
            print(f"   ⏱️  Avg Days to Sale: {product['avg_days_to_sale']:.1f} days")
            print(f"   ⚡ Fastest Sale: {product['min_days_to_sale']} days")
            print(f"   🐌 Slowest Sale: {product['max_days_to_sale']} days")
            print(f"   📦 Still Unsold: {product['still_unsold_count']} purchases")
            print(f"   Current Stock: {product['current_stock']:.0f} units")
            print(f"   Rating: {product['turnover_rating']}")
            print(f"   💡 {product['recommendation']}")
        
        print("\n\n⚡ TOP 5 FASTEST TURNOVER:")
        print("-" * 70)
        
        fastest = sorted(results, key=lambda x: x['avg_days_to_sale'])[:5]
        for i, product in enumerate(fastest, 1):
            print(f"\n{i}. {product['name'][:45]}")
            print(f"   Avg Days to Sale: {product['avg_days_to_sale']:.1f} days")
            print(f"   Rating: {product['turnover_rating']}")
        
        # Calculate statistics
        total_purchases = sum(p['purchases_count'] for p in results)
        avg_turnover = sum(p['avg_days_to_sale'] * p['purchases_count'] for p in results) / total_purchases if total_purchases > 0 else 0
        
        print("\n" + "=" * 70)
        print("📈 TURNOVER SUMMARY")
        print("=" * 70)
        print(f"Products Analyzed: {len(results)}")
        print(f"Total Purchases: {total_purchases}")
        print(f"Overall Avg Turnover: {avg_turnover:.1f} days")
        print(f"\n⚡ Fast Movers: {len(fast)} ({len(fast)/len(results)*100:.1f}%)")
        print(f"🚶 Medium: {len(medium)} ({len(medium)/len(results)*100:.1f}%)")
        print(f"🐌 Slow Movers: {len(slow)} ({len(slow)/len(results)*100:.1f}%)")
        
    else:
        print("⚠️  No purchase-to-sale data available for analysis")
    
    # Test 2: Inventory age distribution
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Inventory age distribution")
    print("-" * 70)
    
    distribution = get_inventory_age_distribution()
    
    print(f"\n✅ Analyzed {distribution['total_products']} products with stock\n")
    
    if distribution['total_products'] > 0:
        print("📊 AGE DISTRIBUTION:")
        print("-" * 70)
        
        for bracket in distribution['age_brackets']:
            bar_length = int(bracket['percentage'] / 2)  # Scale for display
            bar = "█" * bar_length
            
            print(f"\n{bracket['bracket']:15} {bar}")
            print(f"   Products: {bracket['products_count']}")
            print(f"   💰 Value: R$ {bracket['total_value']:,.2f}")
            print(f"   📊 Percentage: {bracket['percentage']:.1f}%")
        
        print("\n" + "=" * 70)
        print("📈 INVENTORY AGE SUMMARY")
        print("=" * 70)
        print(f"Total Products: {distribution['total_products']}")
        print(f"💰 Total Value: R$ {distribution['total_value']:,.2f}")
        print(f"⏱️  Average Age: {distribution['avg_age_days']:.1f} days")
        
        if distribution['oldest_product']:
            oldest = distribution['oldest_product']
            print(f"\n🕰️  OLDEST INVENTORY:")
            print(f"   Product: {oldest['name']}")
            print(f"   SKU: {oldest['sku']}")
            print(f"   Age: {oldest['age_days']} days")
            print(f"   Stock: {oldest['stock']:.0f} units")
            print(f"   💰 Value: R$ {oldest['value']:,.2f}")
        
        # Highlight concerns
        old_brackets = [b for b in distribution['age_brackets'] if '60+' in b['bracket']]
        if old_brackets and old_brackets[0]['total_value'] > 0:
            print(f"\n⚠️  OLD STOCK ALERT:")
            print(f"   Value in stock 60+ days: R$ {old_brackets[0]['total_value']:,.2f}")
            print(f"   That's {old_brackets[0]['percentage']:.1f}% of total inventory")
    
    # Test 3: Different time periods
    print("\n" + "=" * 70)
    print("\n📊 Test 3: Comparing different analysis periods")
    print("-" * 70)
    
    results_30d = analyze_purchase_to_sale_time(days_period=30)
    results_180d = analyze_purchase_to_sale_time(days_period=180)
    
    print(f"\n30-day period: {len(results_30d)} products analyzed")
    if results_30d:
        avg_30d = sum(p['avg_days_to_sale'] for p in results_30d) / len(results_30d)
        print(f"   Avg turnover: {avg_30d:.1f} days")
    
    print(f"\n90-day period: {len(results)} products analyzed")
    if results:
        avg_90d = sum(p['avg_days_to_sale'] for p in results) / len(results)
        print(f"   Avg turnover: {avg_90d:.1f} days")
    
    print(f"\n180-day period: {len(results_180d)} products analyzed")
    if results_180d:
        avg_180d = sum(p['avg_days_to_sale'] for p in results_180d) / len(results_180d)
        print(f"   Avg turnover: {avg_180d:.1f} days")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #7 TEST COMPLETED!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
