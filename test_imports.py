"""
Test script to verify all tool imports are working correctly.
"""

print("Testing tool imports...")
print("=" * 60)

try:
    # Test imports
    from tools import (
        # Stock Analysis
        detect_stock_rupture,
        analyze_slow_moving_stock,
        
        # Stockout Risk (NEW)
        detect_imminent_stockout_risk,
        get_pending_order_summary,
        
        # Purchase
        suggest_purchase_order,
        group_suggestions_by_supplier,
        
        # Alerts
        get_stock_alerts,
        
        # Sales
        get_top_selling_products,
        get_sales_by_category,
        
        # Loss
        detect_stock_losses,
        get_explicit_losses,
        
        # ABC
        get_abc_analysis,
        
        # Supplier
        analyze_supplier_performance,
        
        # Turnover
        analyze_purchase_to_sale_time,
        get_inventory_age_distribution,
        
        # Profitability
        calculate_profitability_analysis,
        get_profitability_summary,
        
        # Availability
        detect_availability_issues,
    )
    
    print("✅ All imports successful!\n")
    
    # Test function signatures
    print("Testing function availability:")
    print("-" * 60)
    
    functions = [
        ("Stock Rupture Detection", detect_stock_rupture),
        ("Slow Moving Stock", analyze_slow_moving_stock),
        ("Imminent Stockout Risk (NEW)", detect_imminent_stockout_risk),
        ("Pending Orders Summary (NEW)", get_pending_order_summary),
        ("Purchase Suggestions", suggest_purchase_order),
        ("Group by Supplier", group_suggestions_by_supplier),
        ("Stock Alerts Dashboard", get_stock_alerts),
        ("Top Selling Products", get_top_selling_products),
        ("Sales by Category", get_sales_by_category),
        ("Stock Losses Detection", detect_stock_losses),
        ("Explicit Losses", get_explicit_losses),
        ("ABC Analysis", get_abc_analysis),
        ("Supplier Performance", analyze_supplier_performance),
        ("Purchase to Sale Time", analyze_purchase_to_sale_time),
        ("Inventory Age Distribution", get_inventory_age_distribution),
        ("Profitability Analysis", calculate_profitability_analysis),
        ("Profitability Summary", get_profitability_summary),
        ("Availability Issues", detect_availability_issues),
    ]
    
    for name, func in functions:
        print(f"✅ {name:<40} {func.__name__}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
