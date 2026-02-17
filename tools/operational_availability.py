"""
Operational availability detection tools for AI Agent.

This module detects products that have stock but are not selling,
indicating operational issues like products stuck in depot,
not restocked on shelves, or display problems.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem, PurchaseOrder, StockMovement


def detect_operational_availability_issues(
    recent_period_days: int = 14,
    historical_period_days: int = 60,
    drop_threshold_percentage: float = 70.0
) -> List[Dict[str, Any]]:
    """
    Detect products with stock that stopped selling despite good historical performance.
    
    This tool identifies OPERATIONAL PROBLEMS where products:
    - Have stock available (received from suppliers)
    - Had good sales historically
    - But suddenly stopped selling or selling much less
    - Indicating they're stuck in depot, not on shelves, or unavailable to customers
    
    This is different from stockout_risk because the product EXISTS but isn't ACCESSIBLE.
    
    Algorithm:
    1. Find products with current stock > 0
    2. Calculate average daily sales in historical period (30-90 days ago)
    3. Calculate average daily sales in recent period (last 14 days)
    4. Identify products with significant drop (>70% decrease)
    5. Verify they received stock recently (to rule out discontinued products)
    6. Flag as operational issue
    
    Args:
        recent_period_days: Recent period to analyze (default: 14 days)
        historical_period_days: Historical period to compare (default: 60 days)
        drop_threshold_percentage: Min % drop to flag as issue (default: 70%)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Current stock level
        - historical_daily_sales: Avg daily sales in historical period
        - recent_daily_sales: Avg daily sales in recent period
        - sales_drop_percentage: % decrease in sales
        - expected_sales_recent: What should have sold
        - actual_sales_recent: What actually sold
        - lost_sales: Difference (opportunity cost)
        - last_received_date: When last purchase order was received
        - days_since_received: Days since last receipt
        - potential_lost_revenue: Estimated revenue loss
        - issue_severity: CRITICAL/HIGH/MEDIUM
        - recommendation: Suggested action
    
    Example:
        >>> issues = detect_operational_availability_issues()
        >>> for issue in issues:
        >>>     print(f"{issue['name']}: {issue['sales_drop_percentage']:.0f}% drop in sales!")
        >>>     print(f"Lost {issue['lost_sales']} sales worth R$ {issue['potential_lost_revenue']:,.2f}")
    """
    session = SessionLocal()
    
    try:
        # Define date ranges
        today = datetime.now()
        recent_start = today - timedelta(days=recent_period_days)
        historical_end = today - timedelta(days=recent_period_days)
        historical_start = historical_end - timedelta(days=historical_period_days)
        
        # Get all products with stock
        products = session.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.current_stock > 0
            )
        ).all()
        
        issues = []
        
        for product in products:
            # Calculate historical sales (30-90 days ago)
            historical_sales = session.query(
                func.sum(SaleOrderItem.quantity).label('total')
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrderItem.product_id == product.id,
                    SaleOrder.sale_date >= historical_start.date(),
                    SaleOrder.sale_date < historical_end.date(),
                    SaleOrder.status == 'PAID'
                )
            ).scalar() or 0
            
            historical_daily_sales = float(historical_sales) / historical_period_days if historical_sales > 0 else 0
            
            # Skip products with no historical sales
            if historical_daily_sales < 0.5:  # Less than 0.5 units/day historically
                continue
            
            # Calculate recent sales (last 14 days)
            recent_sales = session.query(
                func.sum(SaleOrderItem.quantity).label('total'),
                func.count(func.distinct(SaleOrder.id)).label('count')
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrderItem.product_id == product.id,
                    SaleOrder.sale_date >= recent_start.date(),
                    SaleOrder.status == 'PAID'
                )
            ).first()
            
            recent_total_sales = float(recent_sales.total or 0)
            recent_sales_count = recent_sales.count or 0
            recent_daily_sales = recent_total_sales / recent_period_days
            
            # Calculate sales drop
            if historical_daily_sales > 0:
                sales_drop_percentage = ((historical_daily_sales - recent_daily_sales) / historical_daily_sales) * 100
            else:
                continue
            
            # Only flag if drop is significant (above threshold)
            if sales_drop_percentage < drop_threshold_percentage:
                continue
            
            # Check if product received stock recently (to rule out discontinued)
            last_receipt = session.query(
                PurchaseOrder.received_date,
                StockMovement.movement_date
            ).join(
                StockMovement,
                and_(
                    StockMovement.reference_id == PurchaseOrder.id,
                    StockMovement.movement_type == 'PURCHASE'
                )
            ).filter(
                and_(
                    StockMovement.product_id == product.id,
                    PurchaseOrder.status == 'RECEIVED'
                )
            ).order_by(PurchaseOrder.received_date.desc()).first()
            
            # Only flag if product received stock in last 30 days
            # (otherwise might be discontinued)
            if not last_receipt:
                continue
            
            last_received_date = last_receipt.received_date or last_receipt.movement_date.date()
            days_since_received = (datetime.now().date() - last_received_date).days
            
            if days_since_received > 30:
                continue
            
            # Calculate impact
            expected_sales_recent = historical_daily_sales * recent_period_days
            actual_sales_recent = recent_total_sales
            lost_sales = expected_sales_recent - actual_sales_recent
            potential_lost_revenue = lost_sales * float(product.sale_price)
            
            # Determine severity
            if sales_drop_percentage >= 90:
                issue_severity = "CRITICAL"
                recommendation = "URGENT: Check if product is available on shelves/online. Likely stuck in depot or not restocked."
            elif sales_drop_percentage >= 80:
                issue_severity = "HIGH"
                recommendation = "IMPORTANT: Verify product visibility and accessibility to customers."
            else:
                issue_severity = "MEDIUM"
                recommendation = "MONITOR: Sales significantly below normal. Check merchandising and display."
            
            issues.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'current_stock': float(product.current_stock),
                'historical_daily_sales': round(historical_daily_sales, 2),
                'recent_daily_sales': round(recent_daily_sales, 2),
                'sales_drop_percentage': round(sales_drop_percentage, 1),
                'expected_sales_recent': round(expected_sales_recent, 1),
                'actual_sales_recent': round(actual_sales_recent, 1),
                'lost_sales': round(lost_sales, 1),
                'last_received_date': last_received_date.isoformat(),
                'days_since_received': days_since_received,
                'potential_lost_revenue': round(potential_lost_revenue, 2),
                'issue_severity': issue_severity,
                'recommendation': recommendation
            })
        
        # Sort by severity then by lost revenue
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        issues.sort(key=lambda x: (severity_order[x['issue_severity']], -x['potential_lost_revenue']))
        
        return issues
        
    finally:
        session.close()
