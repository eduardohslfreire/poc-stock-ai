"""
Stock analysis tools for AI Agent.

This module contains tools for analyzing stock levels, ruptures,
and slow-moving inventory.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem, StockMovement


def detect_stock_rupture(days_lookback: int = 14) -> List[Dict[str, Any]]:
    """
    Detect products that are out of stock but had recent sales.
    
    This tool identifies stock ruptures - products with zero or negative stock
    that had sales in the recent period, indicating missed sales opportunities.
    
    Args:
        days_lookback: Number of days to look back for sales history (default: 14)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Current stock level
        - recent_sales_count: Number of sales in the period
        - last_sale_date: Date of last sale
        - total_quantity_sold: Total quantity sold in period
        - estimated_daily_demand: Average daily demand
        - days_out_of_stock: Estimated days without stock
        - lost_revenue_estimate: Estimated lost revenue (R$)
    
    Example:
        >>> results = detect_stock_rupture(days_lookback=14)
        >>> print(f"Found {len(results)} products in rupture")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_lookback)
        
        # Query products with no stock but recent sales
        query = session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            Product.current_stock,
            Product.sale_price,
            func.count(func.distinct(SaleOrder.id)).label('sales_count'),
            func.max(SaleOrder.sale_date).label('last_sale_date'),
            func.sum(SaleOrderItem.quantity).label('total_quantity_sold')
        ).join(
            SaleOrderItem, Product.id == SaleOrderItem.product_id
        ).join(
            SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
        ).filter(
            and_(
                Product.current_stock <= 0,
                SaleOrder.sale_date >= cutoff_date.date(),
                SaleOrder.status == 'PAID'
            )
        ).group_by(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            Product.current_stock,
            Product.sale_price
        ).order_by(
            func.sum(SaleOrderItem.quantity).desc()
        ).all()
        
        results = []
        for row in query:
            # Calculate metrics
            total_sold = float(row.total_quantity_sold or 0)
            daily_demand = total_sold / days_lookback
            
            # Estimate days out of stock (from last stock movement to now)
            last_outbound = session.query(StockMovement).filter(
                and_(
                    StockMovement.product_id == row.id,
                    StockMovement.stock_after == 0
                )
            ).order_by(StockMovement.movement_date.desc()).first()
            
            days_out = 0
            if last_outbound:
                days_out = (datetime.now() - last_outbound.movement_date).days
            
            # Estimate lost revenue (days out * daily demand * price)
            lost_revenue = days_out * daily_demand * float(row.sale_price)
            
            results.append({
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'category': row.category or 'N/A',
                'current_stock': float(row.current_stock),
                'recent_sales_count': row.sales_count,
                'last_sale_date': row.last_sale_date.isoformat() if row.last_sale_date else None,
                'total_quantity_sold': total_sold,
                'estimated_daily_demand': round(daily_demand, 2),
                'days_out_of_stock': days_out,
                'lost_revenue_estimate': round(lost_revenue, 2)
            })
        
        return results
        
    finally:
        session.close()


def analyze_slow_moving_stock(days_threshold: int = 30) -> List[Dict[str, Any]]:
    """
    Identify products with stock that haven't sold in a long time.
    
    This tool finds "dead stock" - products sitting in inventory without
    sales for an extended period, representing tied-up capital.
    
    Args:
        days_threshold: Minimum days without sales to be considered slow-moving (default: 30)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Current stock level
        - stock_value: Total value of stuck inventory (cost * quantity)
        - last_sale_date: Date of last sale (or None)
        - days_without_sale: Days since last sale
        - last_purchase_date: When stock was last purchased
        - recommendation: Suggested action
    
    Example:
        >>> results = analyze_slow_moving_stock(days_threshold=60)
        >>> total_value = sum(r['stock_value'] for r in results)
        >>> print(f"R$ {total_value:,.2f} tied up in slow-moving stock")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        # Get all products with stock
        products_with_stock = session.query(Product).filter(
            Product.current_stock > 0
        ).all()
        
        results = []
        for product in products_with_stock:
            # Find last sale
            last_sale = session.query(SaleOrder.sale_date).join(
                SaleOrderItem, SaleOrder.id == SaleOrderItem.sale_order_id
            ).filter(
                and_(
                    SaleOrderItem.product_id == product.id,
                    SaleOrder.status == 'PAID'
                )
            ).order_by(SaleOrder.sale_date.desc()).first()
            
            last_sale_date = last_sale[0] if last_sale else None
            
            # Calculate days without sale
            if last_sale_date:
                days_without_sale = (datetime.now().date() - last_sale_date).days
            else:
                # Never sold - use a large number
                days_without_sale = 9999
            
            # Only include if exceeds threshold
            if days_without_sale < days_threshold:
                continue
            
            # Find last purchase
            last_purchase = session.query(StockMovement.movement_date).filter(
                and_(
                    StockMovement.product_id == product.id,
                    StockMovement.movement_type == 'PURCHASE'
                )
            ).order_by(StockMovement.movement_date.desc()).first()
            
            last_purchase_date = last_purchase[0] if last_purchase else None
            
            # Calculate stock value
            stock_value = float(product.current_stock * product.cost_price)
            
            # Recommendation based on age
            if days_without_sale > 90:
                recommendation = "URGENT: Consider discount/promotion or return to supplier"
            elif days_without_sale > 60:
                recommendation = "IMPORTANT: Apply discount to move stock"
            else:
                recommendation = "MONITOR: Track sales, consider light promotion"
            
            results.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'current_stock': float(product.current_stock),
                'stock_value': round(stock_value, 2),
                'last_sale_date': last_sale_date.isoformat() if last_sale_date else None,
                'days_without_sale': days_without_sale if days_without_sale < 9999 else None,
                'last_purchase_date': last_purchase_date.isoformat() if last_purchase_date else None,
                'recommendation': recommendation
            })
        
        # Sort by stock value (highest first)
        results.sort(key=lambda x: x['stock_value'], reverse=True)
        
        return results
        
    finally:
        session.close()
