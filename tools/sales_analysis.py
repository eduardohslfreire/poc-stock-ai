"""
Sales analysis tools for AI Agent.

This module contains tools for analyzing sales performance,
top-selling products, and revenue metrics.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem


def get_top_selling_products(
    period: str = 'month',
    limit: int = 10,
    metric: str = 'revenue'
) -> List[Dict[str, Any]]:
    """
    Get top-selling products ranked by various metrics.
    
    This tool analyzes sales performance to identify best-selling products
    by revenue, quantity, or frequency, helping with inventory and marketing decisions.
    
    Args:
        period: Time period to analyze:
            - 'week': Last 7 days
            - 'month': Last 30 days (default)
            - 'quarter': Last 90 days
            - 'all': All time
        limit: Maximum number of products to return (default: 10)
        metric: Ranking metric:
            - 'revenue': Total revenue generated (default)
            - 'quantity': Total units sold
            - 'frequency': Number of separate sales
    
    Returns:
        List of dictionaries containing:
        - rank: Ranking position
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - total_revenue: Total revenue generated
        - total_quantity: Total units sold
        - sales_count: Number of separate sales
        - avg_sale_value: Average value per sale
        - avg_quantity_per_sale: Average quantity per sale
        - current_stock: Current stock level
        - stock_status: OK/LOW/OUT based on demand
        - percentage_of_total: % of total sales (for selected metric)
    
    Example:
        >>> top_revenue = get_top_selling_products(period='month', metric='revenue')
        >>> print(f"Top seller: {top_revenue[0]['name']} - R$ {top_revenue[0]['total_revenue']:,.2f}")
    """
    session = SessionLocal()
    
    try:
        # Determine date range
        if period == 'week':
            cutoff_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            cutoff_date = datetime.now() - timedelta(days=30)
        elif period == 'quarter':
            cutoff_date = datetime.now() - timedelta(days=90)
        else:  # 'all'
            cutoff_date = datetime.min
        
        # Query sales data
        query = session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            Product.current_stock,
            Product.sale_price,
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).label('total_revenue'),
            func.sum(SaleOrderItem.quantity).label('total_quantity'),
            func.count(func.distinct(SaleOrder.id)).label('sales_count'),
            func.avg(SaleOrderItem.quantity).label('avg_quantity')
        ).join(
            SaleOrderItem, Product.id == SaleOrderItem.product_id
        ).join(
            SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
        ).filter(
            and_(
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
        )
        
        # Order by selected metric
        if metric == 'revenue':
            query = query.order_by(func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).desc())
        elif metric == 'quantity':
            query = query.order_by(func.sum(SaleOrderItem.quantity).desc())
        elif metric == 'frequency':
            query = query.order_by(func.count(func.distinct(SaleOrder.id)).desc())
        
        results = query.limit(limit).all()
        
        # Calculate total for percentage
        if metric == 'revenue':
            total_metric = sum(float(r.total_revenue) for r in results)
        elif metric == 'quantity':
            total_metric = sum(float(r.total_quantity) for r in results)
        else:  # frequency
            total_metric = sum(r.sales_count for r in results)
        
        output = []
        for rank, row in enumerate(results, 1):
            total_revenue = float(row.total_revenue)
            total_quantity = float(row.total_quantity)
            sales_count = row.sales_count
            avg_quantity = float(row.avg_quantity) if row.avg_quantity else 0
            
            # Calculate average sale value
            avg_sale_value = total_revenue / sales_count if sales_count > 0 else 0
            
            # Determine stock status
            # Simple heuristic: if daily sales * 7 > current stock = LOW
            days_in_period = 7 if period == 'week' else 30 if period == 'month' else 90
            if period == 'all':
                days_in_period = 180  # Assume 6 months for 'all'
            
            daily_sales = total_quantity / days_in_period if days_in_period > 0 else 0
            week_demand = daily_sales * 7
            
            current_stock = float(row.current_stock)
            
            if current_stock == 0:
                stock_status = "OUT"
            elif current_stock < week_demand:
                stock_status = "LOW"
            else:
                stock_status = "OK"
            
            # Calculate percentage
            if metric == 'revenue':
                metric_value = total_revenue
            elif metric == 'quantity':
                metric_value = total_quantity
            else:
                metric_value = sales_count
            
            percentage = (metric_value / total_metric * 100) if total_metric > 0 else 0
            
            output.append({
                'rank': rank,
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'category': row.category or 'N/A',
                'total_revenue': round(total_revenue, 2),
                'total_quantity': round(total_quantity, 2),
                'sales_count': sales_count,
                'avg_sale_value': round(avg_sale_value, 2),
                'avg_quantity_per_sale': round(avg_quantity, 2),
                'current_stock': current_stock,
                'stock_status': stock_status,
                'percentage_of_total': round(percentage, 1)
            })
        
        return output
        
    finally:
        session.close()


def get_sales_by_category(period: str = 'month') -> List[Dict[str, Any]]:
    """
    Get sales performance grouped by product category.
    
    This tool provides category-level insights to identify which
    product categories are performing best.
    
    Args:
        period: Time period to analyze (week/month/quarter/all)
    
    Returns:
        List of dictionaries containing:
        - category: Category name
        - products_count: Number of products in category
        - total_revenue: Total revenue for category
        - total_quantity: Total units sold
        - sales_count: Number of sales
        - avg_product_revenue: Average revenue per product
        - percentage_of_total: % of total revenue
    
    Example:
        >>> by_category = get_sales_by_category(period='month')
        >>> top_cat = by_category[0]
        >>> print(f"Top category: {top_cat['category']} - R$ {top_cat['total_revenue']:,.2f}")
    """
    session = SessionLocal()
    
    try:
        # Determine date range
        if period == 'week':
            cutoff_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            cutoff_date = datetime.now() - timedelta(days=30)
        elif period == 'quarter':
            cutoff_date = datetime.now() - timedelta(days=90)
        else:  # 'all'
            cutoff_date = datetime.min
        
        # Query sales by category
        query = session.query(
            Product.category,
            func.count(func.distinct(Product.id)).label('products_count'),
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).label('total_revenue'),
            func.sum(SaleOrderItem.quantity).label('total_quantity'),
            func.count(func.distinct(SaleOrder.id)).label('sales_count')
        ).join(
            SaleOrderItem, Product.id == SaleOrderItem.product_id
        ).join(
            SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
        ).filter(
            and_(
                SaleOrder.sale_date >= cutoff_date.date(),
                SaleOrder.status == 'PAID'
            )
        ).group_by(
            Product.category
        ).order_by(
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).desc()
        ).all()
        
        # Calculate total revenue
        total_revenue = sum(float(r.total_revenue) for r in query)
        
        results = []
        for row in query:
            category = row.category or 'Uncategorized'
            products_count = row.products_count
            cat_revenue = float(row.total_revenue)
            cat_quantity = float(row.total_quantity)
            sales_count = row.sales_count
            
            avg_product_revenue = cat_revenue / products_count if products_count > 0 else 0
            percentage = (cat_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            results.append({
                'category': category,
                'products_count': products_count,
                'total_revenue': round(cat_revenue, 2),
                'total_quantity': round(cat_quantity, 2),
                'sales_count': sales_count,
                'avg_product_revenue': round(avg_product_revenue, 2),
                'percentage_of_total': round(percentage, 1)
            })
        
        return results
        
    finally:
        session.close()
