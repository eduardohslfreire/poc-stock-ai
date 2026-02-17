"""
Tools module for AI Agent.

This module contains all the analysis tools that the LangChain agent
can use to query and analyze stock data.
"""

# Stock Analysis
from tools.stock_analysis import (
    detect_stock_rupture,
    analyze_slow_moving_stock
)

# Stockout Risk (NEW - 2026-02-08)
from tools.stockout_risk import (
    detect_imminent_stockout_risk,
    get_pending_order_summary
)

# Purchase Suggestions (ENHANCED - 2026-02-08)
from tools.purchase_suggestions import (
    suggest_purchase_order,
    group_suggestions_by_supplier
)

# Alerts (ENHANCED - 2026-02-08)
from tools.alerts import get_stock_alerts

# Sales Analysis
from tools.sales_analysis import (
    get_top_selling_products,
    get_sales_by_category
)

# Loss Detection
from tools.loss_detection import (
    detect_stock_losses,
    get_explicit_losses
)

# ABC Analysis
from tools.abc_analysis import get_abc_analysis

# Supplier Analysis
from tools.supplier_analysis import analyze_supplier_performance

# Turnover Analysis
from tools.turnover_analysis import (
    analyze_purchase_to_sale_time,
    get_inventory_age_distribution
)

# Profitability Analysis
from tools.profitability_analysis import (
    calculate_profitability_analysis,
    get_profitability_summary
)

# Availability Analysis
from tools.availability_analysis import detect_availability_issues

# Operational Availability (NEW - 2026-02-08)
from tools.operational_availability import detect_operational_availability_issues

__all__ = [
    # Stock Analysis
    'detect_stock_rupture',
    'analyze_slow_moving_stock',
    
    # Stockout Risk (NEW)
    'detect_imminent_stockout_risk',
    'get_pending_order_summary',
    
    # Purchase
    'suggest_purchase_order',
    'group_suggestions_by_supplier',
    
    # Alerts
    'get_stock_alerts',
    
    # Sales
    'get_top_selling_products',
    'get_sales_by_category',
    
    # Loss
    'detect_stock_losses',
    'get_explicit_losses',
    
    # ABC
    'get_abc_analysis',
    
    # Supplier
    'analyze_supplier_performance',
    
    # Turnover
    'analyze_purchase_to_sale_time',
    'get_inventory_age_distribution',
    
    # Profitability
    'calculate_profitability_analysis',
    'get_profitability_summary',
    
    # Availability
    'detect_availability_issues',
    
    # Operational Availability (NEW)
    'detect_operational_availability_issues',
]
