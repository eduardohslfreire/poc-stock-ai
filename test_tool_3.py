"""
Test script for Tool #3: analyze_supplier_performance

This script tests the supplier performance analysis tool.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.supplier_analysis import analyze_supplier_performance

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #3: analyze_supplier_performance")
    print("=" * 70)
    
    # Test 1: By turnover rate
    print("\n📊 Test 1: Ranking suppliers by TURNOVER RATE (90 days)")
    print("-" * 70)
    
    results = analyze_supplier_performance(metric='turnover_rate', days_period=90)
    
    print(f"\n✅ Analyzed {len(results)} suppliers\n")
    
    if results:
        print("🏆 TOP 5 SUPPLIERS (by turnover rate):")
        print("-" * 70)
        
        for i, supplier in enumerate(results[:5], 1):
            print(f"\n{i}. {supplier['supplier_name']}")
            print(f"   CNPJ: {supplier['tax_id']}")
            print(f"   Products Supplied: {supplier['products_supplied']}")
            print(f"   💰 Total Purchased: R$ {supplier['total_purchased']:,.2f}")
            print(f"   💵 Total Revenue: R$ {supplier['total_revenue']:,.2f}")
            print(f"   📈 Avg Turnover Rate: {supplier['avg_turnover_rate']:.3f} units/day")
            print(f"   📦 Products in Stock: {supplier['products_in_stock']}")
            print(f"   🐌 Slow-Moving Products: {supplier['slow_moving_products']} ({supplier['slow_moving_percentage']:.1f}%)")
            print(f"   ⭐ Performance Score: {supplier['performance_score']:.1f}/100 - {supplier['rating']}")
        
        print("\n\n🚨 BOTTOM 3 SUPPLIERS (worst performance):")
        print("-" * 70)
        
        for i, supplier in enumerate(results[-3:], 1):
            print(f"\n{i}. {supplier['supplier_name']}")
            print(f"   ⭐ Performance Score: {supplier['performance_score']:.1f}/100 - {supplier['rating']}")
            print(f"   📈 Avg Turnover: {supplier['avg_turnover_rate']:.3f} units/day")
            print(f"   🐌 Slow-Moving: {supplier['slow_moving_percentage']:.1f}%")
            print(f"   💵 Revenue: R$ {supplier['total_revenue']:,.2f}")
        
        # Summary statistics
        total_revenue = sum(s['total_revenue'] for s in results)
        avg_score = sum(s['performance_score'] for s in results) / len(results)
        excellent = [s for s in results if s['rating'] == 'Excellent']
        poor = [s for s in results if s['rating'] == 'Poor']
        
        print("\n" + "=" * 70)
        print("📈 SUMMARY")
        print("=" * 70)
        print(f"Total Suppliers Analyzed: {len(results)}")
        print(f"💵 Total Revenue (all suppliers): R$ {total_revenue:,.2f}")
        print(f"⭐ Average Performance Score: {avg_score:.1f}/100")
        print(f"🏆 Excellent Suppliers: {len(excellent)}")
        print(f"⚠️  Poor Suppliers: {len(poor)}")
    
    # Test 2: By revenue
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Ranking suppliers by REVENUE")
    print("-" * 70)
    
    results_revenue = analyze_supplier_performance(metric='revenue', days_period=90)
    
    print(f"\n💰 TOP 3 SUPPLIERS (by revenue generated):\n")
    for i, supplier in enumerate(results_revenue[:3], 1):
        print(f"{i}. {supplier['supplier_name']}")
        print(f"   Revenue: R$ {supplier['total_revenue']:,.2f}")
        print(f"   Rating: {supplier['rating']}\n")
    
    # Test 3: By slow-moving percentage
    print("=" * 70)
    print("\n📊 Test 3: Suppliers with LEAST slow-moving products")
    print("-" * 70)
    
    results_slow = analyze_supplier_performance(metric='slow_moving', days_period=90)
    
    print(f"\n✅ TOP 3 SUPPLIERS (lowest slow-moving %):\n")
    for i, supplier in enumerate(results_slow[:3], 1):
        print(f"{i}. {supplier['supplier_name']}")
        print(f"   Slow-Moving: {supplier['slow_moving_percentage']:.1f}%")
        print(f"   Products: {supplier['slow_moving_products']}/{supplier['products_supplied']}\n")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #3 TEST COMPLETED!")
    print("=" * 70)
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
