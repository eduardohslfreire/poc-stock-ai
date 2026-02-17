"""
Test script for Tool #4: detect_stock_losses

This script tests the stock loss detection tools.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.loss_detection import detect_stock_losses, get_explicit_losses

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #4: detect_stock_losses & get_explicit_losses")
    print("=" * 70)
    
    # Test 1: Detect discrepancies
    print("\n📊 Test 1: Detecting stock discrepancies (5% tolerance)")
    print("-" * 70)
    
    results = detect_stock_losses(tolerance_percentage=5.0)
    
    print(f"\n✅ Found {len(results)} products with discrepancies\n")
    
    if results:
        # Group by severity
        critical = [r for r in results if r['severity'] == 'CRITICAL']
        high = [r for r in results if r['severity'] == 'HIGH']
        medium = [r for r in results if r['severity'] == 'MEDIUM']
        
        print(f"🔴 CRITICAL: {len(critical)} products")
        print(f"🟠 HIGH: {len(high)} products")
        print(f"🟡 MEDIUM: {len(medium)} products\n")
        
        print("🚨 MOST CRITICAL DISCREPANCIES:")
        print("-" * 70)
        
        for i, product in enumerate(results[:5], 1):
            severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}
            icon = severity_icon.get(product['severity'], "⚪")
            
            print(f"\n{i}. {icon} {product['name']} (SKU: {product['sku']})")
            print(f"   Category: {product['category']}")
            print(f"   Expected Stock: {product['expected_stock']:.2f}")
            print(f"   Actual Stock: {product['current_stock']:.2f}")
            print(f"   📉 Discrepancy: {product['discrepancy']:.2f} units ({product['discrepancy_percentage']:.1f}%)")
            print(f"   💰 Estimated Loss Value: R$ {product['estimated_loss_value']:,.2f}")
            print(f"   Explicit Loss Movements: {product['loss_movements']}")
            print(f"   Last Movement: {product['last_movement_date']}")
            print(f"   Severity: {product['severity']}")
            print(f"   📋 {product['recommendation']}")
        
        # Calculate totals
        total_discrepancy = sum(abs(p['discrepancy']) for p in results)
        total_loss_value = sum(p['estimated_loss_value'] for p in results)
        
        print("\n" + "=" * 70)
        print("📈 DISCREPANCY SUMMARY")
        print("=" * 70)
        print(f"Total Products with Issues: {len(results)}")
        print(f"Total Discrepancy: {total_discrepancy:.2f} units")
        print(f"💰 Total Estimated Loss Value: R$ {total_loss_value:,.2f}")
        print(f"🔴 Critical Issues: {len(critical)}")
        print(f"🟠 High Priority: {len(high)}")
        print(f"🟡 Medium Priority: {len(medium)}")
        
    else:
        print("✅ No significant discrepancies detected! Stock records are accurate.")
    
    # Test 2: Get explicit losses
    print("\n" + "=" * 70)
    print("\n📊 Test 2: Explicit Loss Movements (last 90 days)")
    print("-" * 70)
    
    losses = get_explicit_losses(days_period=90)
    
    print(f"\n✅ Found {len(losses)} explicit loss records\n")
    
    if losses:
        print("💔 RECORDED LOSSES:")
        print("-" * 70)
        
        for i, loss in enumerate(losses[:10], 1):  # Show top 10
            print(f"\n{i}. {loss['product_name']} (SKU: {loss['sku']})")
            print(f"   Category: {loss['category']}")
            print(f"   Quantity Lost: {loss['quantity_lost']:.2f} units")
            print(f"   💰 Loss Value: R$ {loss['loss_value']:,.2f}")
            print(f"   Date: {loss['loss_date']} ({loss['days_ago']} days ago)")
            print(f"   Notes: {loss['notes']}")
        
        # Summary
        total_quantity_lost = sum(l['quantity_lost'] for l in losses)
        total_value_lost = sum(l['loss_value'] for l in losses)
        
        print("\n" + "=" * 70)
        print("📈 LOSS SUMMARY (90 days)")
        print("=" * 70)
        print(f"Total Loss Events: {len(losses)}")
        print(f"Total Quantity Lost: {total_quantity_lost:.2f} units")
        print(f"💰 Total Value Lost: R$ {total_value_lost:,.2f}")
        
        # By category
        from collections import defaultdict
        by_category = defaultdict(lambda: {'count': 0, 'value': 0})
        for loss in losses:
            by_category[loss['category']]['count'] += 1
            by_category[loss['category']]['value'] += loss['loss_value']
        
        print(f"\n📊 Losses by Category:")
        for category, data in sorted(by_category.items(), key=lambda x: x[1]['value'], reverse=True)[:5]:
            print(f"   {category}: {data['count']} events - R$ {data['value']:,.2f}")
        
    else:
        print("✅ No explicit losses recorded in the last 90 days!")
    
    # Test 3: Stricter tolerance
    print("\n" + "=" * 70)
    print("\n📊 Test 3: Detecting with stricter tolerance (2%)")
    print("-" * 70)
    
    results_strict = detect_stock_losses(tolerance_percentage=2.0)
    print(f"\n✅ Found {len(results_strict)} products with 2%+ discrepancy\n")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #4 TEST COMPLETED!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
