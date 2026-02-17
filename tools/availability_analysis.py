"""
Availability analysis tools for AI Agent.

This module contains tools for detecting and analyzing
product availability issues and patterns.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem, StockMovement


def detect_availability_issues(days_period: int = 90) -> List[Dict[str, Any]]:
    """
    Detect products with recurring availability problems.
    
    This tool identifies products that frequently run out of stock,
    helping to optimize inventory policies and prevent chronic stock-outs.
    
    Algorithm:
    1. Track all stock-out events (stock reaching 0)
    2. Calculate frequency and duration of stock-outs
    3. Measure lost sales during stock-out periods
    4. Identify patterns and chronic issues
    
    Args:
        days_period: Historical period to analyze in days (default: 90)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - stockout_events: Number of times stock reached zero
        - total_days_out: Total days out of stock
        - availability_rate: % of time product was available
        - lost_sales_count: Estimated sales lost during stockouts
        - current_status: IN_STOCK/OUT_OF_STOCK
        - issue_severity: CRITICAL/HIGH/MEDIUM based on frequency
        - recommendation: Suggested action
    
    Example:
        >>> issues = detect_availability_issues(days_period=90)
        >>> chronic = [i for i in issues if i['issue_severity'] == 'CRITICAL']
        >>> print(f"Found {len(chronic)} products with chronic availability issues")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_period)
        
        # Get all products that have had sales
        products_with_sales = session.query(Product.id).join(
            SaleOrderItem, Product.id == SaleOrderItem.product_id
        ).join(
            SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
        ).filter(
            SaleOrder.sale_date >= cutoff_date.date()
        ).distinct().all()
        
        product_ids = [p.id for p in products_with_sales]
        
        results = []
        
        for product_id in product_ids:
            product = session.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                continue
            
            # Get all stock movements that resulted in zero stock
            stockout_movements = session.query(StockMovement).filter(
                and_(
                    StockMovement.product_id == product_id,
                    StockMovement.stock_after == 0,
                    StockMovement.movement_date >= cutoff_date
                )
            ).order_by(StockMovement.movement_date).all()
            
            if not stockout_movements:
                continue  # No stockouts in period
            
            # Calculate stockout periods
            stockout_events = len(stockout_movements)
            total_days_out = 0
            
            for stockout in stockout_movements:
                # Find next stock-in movement
                next_stock_in = session.query(StockMovement).filter(
                    and_(
                        StockMovement.product_id == product_id,
                        StockMovement.movement_date > stockout.movement_date,
                        StockMovement.stock_after > 0
                    )
                ).order_by(StockMovement.movement_date).first()
                
                if next_stock_in:
                    days_out = (next_stock_in.movement_date - stockout.movement_date).days
                else:
                    # Still out of stock
                    days_out = (datetime.now() - stockout.movement_date).days
                
                total_days_out += days_out
            
            # Calculate availability rate
            availability_rate = ((days_period - total_days_out) / days_period * 100) if days_period > 0 else 0
            
            # Estimate lost sales during stockouts
            # Get average daily sales when in stock
            total_sales = session.query(
                func.sum(SaleOrderItem.quantity)
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrderItem.product_id == product_id,
                    SaleOrder.sale_date >= cutoff_date.date(),
                    SaleOrder.status == 'PAID'
                )
            ).scalar() or 0
            
            days_available = days_period - total_days_out
            avg_daily_sales = float(total_sales) / days_available if days_available > 0 else 0
            
            lost_sales_count = int(avg_daily_sales * total_days_out)
            
            # Determine severity
            if availability_rate < 80:
                issue_severity = "CRITICAL"
                recommendation = "URGENT: Review min/max stock levels and increase safety stock"
            elif availability_rate < 90:
                issue_severity = "HIGH"
                recommendation = "IMPORTANT: Adjust reorder point and increase order frequency"
            else:
                issue_severity = "MEDIUM"
                recommendation = "MONITOR: Minor availability issues, optimize reorder timing"
            
            # Current status
            current_status = "IN_STOCK" if product.current_stock > 0 else "OUT_OF_STOCK"
            
            results.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'stockout_events': stockout_events,
                'total_days_out': total_days_out,
                'availability_rate': round(availability_rate, 1),
                'lost_sales_count': lost_sales_count,
                'current_status': current_status,
                'issue_severity': issue_severity,
                'recommendation': recommendation
            })
        
        # Sort by severity then by lost sales
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        results.sort(key=lambda x: (severity_order[x['issue_severity']], -x['lost_sales_count']))
        
        return results
        
    finally:
        session.close()
