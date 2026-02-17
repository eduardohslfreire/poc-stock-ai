"""
Test script for Tool #6: get_top_selling_products

This script tests the sales analysis tools.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.sales_analysis import get_top_selling_products, get_sales_by_category

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #6: get_top_selling_products")
    print("=" * 70)
    
    # Test 1: Top by revenue
    print("\n📊 Test 1: Top 10 products by REVENUE (last 30 days)")
    print("-" * 70)
    
    top_revenue = get_top_selling_products(period='month', limit=10, metric='revenue')
    
    print(f"\n✅ Found {len(top_revenue)} top-selling products\n")
    
    if top_revenue:
        print("💰 TOP 10 BY REVENUE:")
        print("-" * 70)
        
        for product in top_revenue:
            status_icon = {"OK": "✅", "LOW": "⚠️", "OUT": "🔴"}
            icon = status_icon.get(product['stock_status'], "⚪")
            
            print(f"\n#{product['rank']}. {product['name']} (SKU: {product['sku']})")
            print(f"   Category: {product['category']}")
            print(f"   💰 Revenue: R$ {product['total_revenue']:,.2f} ({product['percentage_of_total']:.1f}%)")
            print(f"   📦 Units Sold: {product['total_quantity']:.0f}")
            print(f"   🛒 Sales Count: {product['sales_count']}")
            print(f"   📊 Avg Sale Value: R$ {product['avg_sale_value']:,.2f}")
            print(f"   📈 Avg Qty/Sale: {product['avg_quantity_per_sale']:.1f}")
            print(f"   {icon} Stock: {product['current_stock']:.0f} units ({product['stock_status']})")
        
        # Calculate totals
        total_revenue = sum(p['total_revenue'] for p in top_revenue)
        total_quantity = sum(p['total_quantity'] for p in top_revenue)
        
        print("\n" + "=" * 70)
        print("📈 TOP 10 SUMMARY")
        print("=" * 70)
        print(f"💰 Total Revenue: R$ {total_revenue:,.2f}")
        print(f"📦 Total Units Sold: {total_quantity:.0f}")
        
        # Stock alerts
        low_stock = [p for p in top_revenue if p['stock_status'] == 'LOW']
        out_stock = [p for p in top_revenue if p['stock_status'] == 'OUT']
        
        if out_stock or low_stock:
            print(f"\n⚠️  STOCK ALERTS:")
            print(f"   🔴 Out of Stock: {len(out_stock)} products")
            print(f"   ⚠️  Low Stock: {len(low_stock)} products")
    
    # Test 2: Top by quantity
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Top 5 products by QUANTITY SOLD")
    print("-" * 70)
    
    top_quantity = get_top_selling_products(period='month', limit=5, metric='quantity')
    
    print(f"\n📦 TOP 5 BY QUANTITY:\n")
    for product in top_quantity:
        print(f"#{product['rank']}. {product['name']}")
        print(f"   Units Sold: {product['total_quantity']:.0f} ({product['percentage_of_total']:.1f}%)\n")
    
    # Test 3: Top by frequency
    print("=" * 70)
    print("\n📊 Test 3: Top 5 products by SALES FREQUENCY")
    print("-" * 70)
    
    top_frequency = get_top_selling_products(period='month', limit=5, metric='frequency')
    
    print(f"\n🛒 TOP 5 BY FREQUENCY:\n")
    for product in top_frequency:
        print(f"#{product['rank']}. {product['name']}")
        print(f"   Sales Count: {product['sales_count']} orders ({product['percentage_of_total']:.1f}%)\n")
    
    # Test 4: By category
    print("=" * 70)
    print("\n📊 Test 4: Sales by CATEGORY (last 30 days)")
    print("-" * 70)
    
    by_category = get_sales_by_category(period='month')
    
    print(f"\n✅ Analyzed {len(by_category)} categories\n")
    
    if by_category:
        print("📊 CATEGORY PERFORMANCE:")
        print("-" * 70)
        
        for i, cat in enumerate(by_category, 1):
            print(f"\n{i}. {cat['category']}")
            print(f"   Products: {cat['products_count']}")
            print(f"   💰 Revenue: R$ {cat['total_revenue']:,.2f} ({cat['percentage_of_total']:.1f}%)")
            print(f"   📦 Units Sold: {cat['total_quantity']:.0f}")
            print(f"   🛒 Sales: {cat['sales_count']}")
            print(f"   📊 Avg per Product: R$ {cat['avg_product_revenue']:,.2f}")
        
        # Summary
        total_cat_revenue = sum(c['total_revenue'] for c in by_category)
        
        print("\n" + "=" * 70)
        print("📈 CATEGORY SUMMARY")
        print("=" * 70)
        print(f"Total Categories: {len(by_category)}")
        print(f"💰 Total Revenue: R$ {total_cat_revenue:,.2f}")
    
    # Test 5: Different periods
    print("\n" + "=" * 70)
    print("\n📊 Test 5: Comparing different periods (Top 3)")
    print("-" * 70)
    
    top_week = get_top_selling_products(period='week', limit=3, metric='revenue')
    top_quarter = get_top_selling_products(period='quarter', limit=3, metric='revenue')
    
    print(f"\n🗓️  LAST WEEK:")
    for i, p in enumerate(top_week, 1):
        print(f"   {i}. {p['name'][:40]} - R$ {p['total_revenue']:,.2f}")
    
    print(f"\n🗓️  LAST MONTH (30 days):")
    for i, p in enumerate(top_revenue[:3], 1):
        print(f"   {i}. {p['name'][:40]} - R$ {p['total_revenue']:,.2f}")
    
    print(f"\n🗓️  LAST QUARTER (90 days):")
    for i, p in enumerate(top_quarter, 1):
        print(f"   {i}. {p['name'][:40]} - R$ {p['total_revenue']:,.2f}")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #6 TEST COMPLETED!")
    print("=" * 70)
    
    return len(top_revenue) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
