"""
Supplier analysis tools for AI Agent.

This module contains tools for analyzing supplier performance
based on product turnover and sales metrics.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import (
    Product, Supplier, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem, StockMovement
)


def analyze_supplier_performance(
    metric: str = 'turnover_rate',
    days_period: int = 90
) -> List[Dict[str, Any]]:
    """
    Analyze supplier performance based on product sales metrics.
    
    This tool evaluates suppliers by analyzing how well their supplied
    products sell, helping identify best and worst performing suppliers.
    
    Args:
        metric: Performance metric to use:
            - 'turnover_rate': Sales velocity (higher is better)
            - 'revenue': Total revenue generated
            - 'slow_moving': Percentage of slow-moving products (lower is better)
        days_period: Period to analyze in days (default: 90)
    
    Returns:
        List of dictionaries containing:
        - supplier_id: Supplier ID
        - supplier_name: Supplier name
        - tax_id: Supplier CNPJ
        - products_supplied: Number of unique products supplied
        - total_purchased: Total value purchased from supplier
        - total_revenue: Total revenue from supplier's products
        - avg_turnover_rate: Average product turnover rate
        - products_in_stock: Products still in inventory
        - slow_moving_products: Number of slow-moving products
        - slow_moving_percentage: % of products that are slow-moving
        - performance_score: Overall performance score (0-100)
        - rating: Performance rating (Excellent/Good/Fair/Poor)
    
    Example:
        >>> results = analyze_supplier_performance(metric='turnover_rate')
        >>> best = results[0]
        >>> print(f"Best supplier: {best['supplier_name']} (score: {best['performance_score']})")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_period)
        slow_threshold = 30  # Days without sale = slow-moving
        
        suppliers = session.query(Supplier).filter(Supplier.is_active == True).all()
        results = []
        
        for supplier in suppliers:
            # Get all products purchased from this supplier
            purchased_products = session.query(
                Product.id,
                Product.name,
                Product.current_stock,
                Product.cost_price,
                Product.sale_price
            ).join(
                PurchaseOrderItem, Product.id == PurchaseOrderItem.product_id
            ).join(
                PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id
            ).filter(
                PurchaseOrder.supplier_id == supplier.id
            ).distinct().all()
            
            if not purchased_products:
                continue
            
            product_ids = [p.id for p in purchased_products]
            
            # Calculate total purchased from supplier
            total_purchased = session.query(
                func.sum(PurchaseOrderItem.quantity * PurchaseOrderItem.unit_price)
            ).join(
                PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id
            ).filter(
                and_(
                    PurchaseOrder.supplier_id == supplier.id,
                    PurchaseOrder.order_date >= cutoff_date.date()
                )
            ).scalar() or Decimal('0')
            
            # Calculate total revenue from supplier's products
            total_revenue = session.query(
                func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price)
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrderItem.product_id.in_(product_ids),
                    SaleOrder.sale_date >= cutoff_date.date(),
                    SaleOrder.status == 'PAID'
                )
            ).scalar() or Decimal('0')
            
            # Calculate turnover metrics for each product
            turnover_rates = []
            slow_moving_count = 0
            products_in_stock = 0
            
            for product in purchased_products:
                if product.current_stock > 0:
                    products_in_stock += 1
                
                # Get sales count in period
                sales_count = session.query(func.count(SaleOrderItem.id)).join(
                    SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
                ).filter(
                    and_(
                        SaleOrderItem.product_id == product.id,
                        SaleOrder.sale_date >= cutoff_date.date(),
                        SaleOrder.status == 'PAID'
                    )
                ).scalar() or 0
                
                # Get quantity sold in period
                qty_sold = session.query(func.sum(SaleOrderItem.quantity)).join(
                    SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
                ).filter(
                    and_(
                        SaleOrderItem.product_id == product.id,
                        SaleOrder.sale_date >= cutoff_date.date(),
                        SaleOrder.status == 'PAID'
                    )
                ).scalar() or 0
                
                # Check if slow-moving (no sales in last 30 days)
                recent_sales = session.query(func.count(SaleOrderItem.id)).join(
                    SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
                ).filter(
                    and_(
                        SaleOrderItem.product_id == product.id,
                        SaleOrder.sale_date >= (datetime.now() - timedelta(days=slow_threshold)).date(),
                        SaleOrder.status == 'PAID'
                    )
                ).scalar() or 0
                
                if recent_sales == 0 and product.current_stock > 0:
                    slow_moving_count += 1
                
                # Calculate turnover rate (sales per day)
                if qty_sold > 0:
                    turnover_rate = float(qty_sold) / days_period
                    turnover_rates.append(turnover_rate)
            
            # Calculate metrics
            avg_turnover = sum(turnover_rates) / len(turnover_rates) if turnover_rates else 0
            slow_moving_pct = (slow_moving_count / len(purchased_products) * 100) if purchased_products else 0
            
            # Calculate performance score (0-100)
            # Based on: turnover rate (50%), revenue (30%), low slow-moving % (20%)
            turnover_score = min(avg_turnover * 10, 50)  # Max 50 points
            revenue_score = min(float(total_revenue) / 10000 * 30, 30)  # Max 30 points
            slow_moving_score = max(20 - (slow_moving_pct / 5), 0)  # Max 20 points, penalize slow-moving
            
            performance_score = turnover_score + revenue_score + slow_moving_score
            
            # Rating
            if performance_score >= 75:
                rating = "Excellent"
            elif performance_score >= 60:
                rating = "Good"
            elif performance_score >= 40:
                rating = "Fair"
            else:
                rating = "Poor"
            
            results.append({
                'supplier_id': supplier.id,
                'supplier_name': supplier.name,
                'tax_id': supplier.tax_id,
                'products_supplied': len(purchased_products),
                'total_purchased': float(total_purchased),
                'total_revenue': float(total_revenue),
                'avg_turnover_rate': round(avg_turnover, 3),
                'products_in_stock': products_in_stock,
                'slow_moving_products': slow_moving_count,
                'slow_moving_percentage': round(slow_moving_pct, 1),
                'performance_score': round(performance_score, 1),
                'rating': rating
            })
        
        # Sort by selected metric
        if metric == 'turnover_rate':
            results.sort(key=lambda x: x['avg_turnover_rate'], reverse=True)
        elif metric == 'revenue':
            results.sort(key=lambda x: x['total_revenue'], reverse=True)
        elif metric == 'slow_moving':
            results.sort(key=lambda x: x['slow_moving_percentage'])
        else:
            # Default: by performance score
            results.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return results
        
    finally:
        session.close()
