"""
Test script for Tool #8: get_stock_alerts

This script tests the consolidated alerts dashboard.
"""

import sys
sys.path.insert(0, '/Users/efreire/poc-projects/poc-stock')

from tools.alerts import get_stock_alerts

def main():
    print("\n" + "=" * 70)
    print("🧪 TESTING TOOL #8: get_stock_alerts (Dashboard)")
    print("=" * 70)
    
    print("\n🔄 Generating comprehensive stock analysis...")
    print("   (This aggregates data from all 7 previous tools)\n")
    
    # Get comprehensive alerts
    dashboard = get_stock_alerts()
    
    # === HEADER ===
    print("=" * 70)
    print("📊 STOCK MANAGEMENT DASHBOARD")
    print("=" * 70)
    print(f"Generated: {dashboard['generated_at']}")
    print(f"Overall Health: {dashboard['health_status']} ({dashboard['health_score']}/100)")
    print("=" * 70)
    
    # === SUMMARY ===
    summary = dashboard['summary']
    print("\n📈 SUMMARY METRICS")
    print("-" * 70)
    print(f"Total Products: {summary['total_products']}")
    print(f"Products with Stock: {summary['products_with_stock']}")
    print(f"💰 Total Stock Value: R$ {summary['total_stock_value']:,.2f}")
    print(f"🚨 Total Alerts: {summary['alerts_count']}")
    
    # === KEY METRICS ===
    metrics = dashboard['metrics']
    print("\n📊 KEY PERFORMANCE INDICATORS")
    print("-" * 70)
    print(f"Products Out of Stock: {metrics['products_out_of_stock']}")
    print(f"Products Below Min Stock: {metrics['products_below_min_stock']}")
    print(f"Stock Ruptures Detected: {metrics['stock_ruptures_count']}")
    print(f"Slow-Moving Products: {metrics['slow_moving_count']}")
    print(f"Purchase Recommendations: {metrics['purchase_recommendations']}")
    print(f"💵 Sales (Last 30 Days): R$ {metrics['sales_last_30_days']:,.2f}")
    
    # === CRITICAL ALERTS ===
    critical = dashboard['critical_alerts']
    print("\n🔴 CRITICAL ALERTS")
    print("-" * 70)
    
    if critical:
        print(f"Found {len(critical)} critical issues requiring immediate action:\n")
        
        for i, alert in enumerate(critical, 1):
            print(f"{i}. {alert['message']}")
            print(f"   Type: {alert['type']}")
            print(f"   Detail: {alert['detail']}")
            print(f"   ⚡ Action: {alert['action']}\n")
    else:
        print("✅ No critical alerts! Everything is under control.\n")
    
    # === WARNINGS ===
    warnings = dashboard['warnings']
    print("=" * 70)
    print("🟠 WARNINGS")
    print("-" * 70)
    
    if warnings:
        print(f"Found {len(warnings)} warnings requiring attention:\n")
        
        # Group by type
        from collections import defaultdict
        by_type = defaultdict(list)
        for warning in warnings:
            by_type[warning['type']].append(warning)
        
        for warning_type, items in by_type.items():
            print(f"\n📌 {warning_type.replace('_', ' ').title()} ({len(items)} items):")
            for item in items[:3]:  # Show top 3 of each type
                print(f"   • {item['message']}")
                print(f"     {item['detail']}")
        print()
    else:
        print("✅ No warnings! Stock is healthy.\n")
    
    # === RECOMMENDATIONS ===
    recommendations = dashboard['recommendations']
    print("=" * 70)
    print("💡 RECOMMENDATIONS")
    print("-" * 70)
    
    if recommendations:
        print(f"Found {len(recommendations)} recommended actions:\n")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['message']}")
            print(f"   {rec['detail']}")
            print(f"   ⚡ Action: {rec['action']}\n")
    else:
        print("✅ No specific recommendations at this time.\n")
    
    # === HEALTH ASSESSMENT ===
    print("=" * 70)
    print("🏥 HEALTH ASSESSMENT")
    print("=" * 70)
    
    health_score = dashboard['health_score']
    health_status = dashboard['health_status']
    
    # Visual health bar
    bar_length = int(health_score / 5)
    bar_color = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🟠" if health_score >= 40 else "🔴"
    health_bar = bar_color * bar_length + "⬜" * (20 - bar_length)
    
    print(f"\nOverall Health: {health_status}")
    print(f"Score: {health_score}/100")
    print(f"\n{health_bar}\n")
    
    if health_score >= 80:
        print("✅ Inventory is in excellent condition!")
        print("   Continue monitoring and maintain current practices.")
    elif health_score >= 60:
        print("👍 Inventory is in good condition with minor issues.")
        print("   Address warnings to prevent them from becoming critical.")
    elif health_score >= 40:
        print("⚠️  Inventory needs attention.")
        print("   Several issues require immediate action to prevent losses.")
    else:
        print("🚨 URGENT: Inventory has critical issues!")
        print("   Immediate intervention required to avoid significant losses.")
    
    # === PRIORITY ACTIONS ===
    if critical or warnings:
        print("\n" + "=" * 70)
        print("📋 PRIORITY ACTION ITEMS")
        print("=" * 70)
        print("\nRecommended order of actions:\n")
        
        priority_actions = []
        
        # Critical items first
        for alert in critical:
            priority_actions.append(f"🔴 URGENT: {alert['action']} ({alert['product_name']})")
        
        # High-severity warnings
        high_warnings = [w for w in warnings if w.get('severity') == 'HIGH']
        for warning in high_warnings:
            if 'product_name' in warning:
                priority_actions.append(f"🟠 Important: {warning['action']} ({warning['product_name']})")
        
        # Recommendations
        for rec in recommendations:
            priority_actions.append(f"💡 Suggested: {rec['action']}")
        
        for i, action in enumerate(priority_actions[:10], 1):  # Top 10 actions
            print(f"{i}. {action}")
    
    print("\n" + "=" * 70)
    print("✅ TOOL #8 TEST COMPLETED!")
    print("=" * 70)
    
    print("\n📊 DASHBOARD SUMMARY:")
    print(f"   Health Status: {health_status}")
    print(f"   Critical Issues: {len(critical)}")
    print(f"   Warnings: {len(warnings)}")
    print(f"   Recommendations: {len(recommendations)}")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
