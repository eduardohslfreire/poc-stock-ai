"""
Profitability analysis tools for AI Agent.

This module contains tools for analyzing product profitability,
margins, and return on investment.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem, PurchaseOrder, PurchaseOrderItem


def calculate_profitability_analysis(
    period: str = 'month',
    min_sales: int = 1
) -> List[Dict[str, Any]]:
    """
    Calculate profitability metrics for products.
    
    This tool analyzes profit margins, gross profit, and ROI to identify
    most and least profitable products, helping with pricing and inventory decisions.
    
    Args:
        period: Time period to analyze (week/month/quarter/all)
        min_sales: Minimum sales required to include product (default: 1)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - total_revenue: Total sales revenue
        - total_cost: Total cost of goods sold
        - gross_profit: Total profit (revenue - cost)
        - profit_margin_pct: Profit margin percentage
        - units_sold: Total units sold
        - avg_sale_price: Average selling price
        - avg_cost_price: Average cost price
        - profit_per_unit: Average profit per unit
        - roi_percentage: Return on investment %
        - profitability_rating: HIGH/MEDIUM/LOW
        - recommendation: Suggested action
    
    Example:
        >>> analysis = calculate_profitability_analysis(period='month')
        >>> top_profit = analysis[0]
        >>> print(f"Most profitable: {top_profit['name']} - R$ {top_profit['gross_profit']:,.2f}")
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
        
        # Query sales data with costs
        sales_data = session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            Product.cost_price,
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).label('total_revenue'),
            func.sum(SaleOrderItem.quantity).label('units_sold'),
            func.avg(SaleOrderItem.unit_price).label('avg_sale_price')
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
            Product.cost_price
        ).having(
            func.sum(SaleOrderItem.quantity) >= min_sales
        ).all()
        
        results = []
        
        for row in sales_data:
            total_revenue = float(row.total_revenue)
            units_sold = float(row.units_sold)
            avg_sale_price = float(row.avg_sale_price)
            cost_price = float(row.cost_price)
            
            # Calculate costs and profit
            total_cost = units_sold * cost_price
            gross_profit = total_revenue - total_cost
            
            # Calculate margins and ratios
            profit_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            profit_per_unit = gross_profit / units_sold if units_sold > 0 else 0
            roi_percentage = (gross_profit / total_cost * 100) if total_cost > 0 else 0
            
            # Determine profitability rating
            if profit_margin_pct >= 40:
                profitability_rating = "HIGH"
                recommendation = "Excellent margins - maintain pricing and promote heavily"
            elif profit_margin_pct >= 25:
                profitability_rating = "MEDIUM"
                recommendation = "Good margins - consider increasing volume through promotions"
            elif profit_margin_pct >= 10:
                profitability_rating = "LOW"
                recommendation = "Low margins - review pricing or negotiate better supplier costs"
            else:
                profitability_rating = "POOR"
                recommendation = "Poor/negative margins - urgent review needed: increase price or discontinue"
            
            results.append({
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'category': row.category or 'N/A',
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'gross_profit': round(gross_profit, 2),
                'profit_margin_pct': round(profit_margin_pct, 1),
                'units_sold': round(units_sold, 2),
                'avg_sale_price': round(avg_sale_price, 2),
                'avg_cost_price': round(cost_price, 2),
                'profit_per_unit': round(profit_per_unit, 2),
                'roi_percentage': round(roi_percentage, 1),
                'profitability_rating': profitability_rating,
                'recommendation': recommendation
            })
        
        # Sort by gross profit (highest first)
        results.sort(key=lambda x: x['gross_profit'], reverse=True)
        
        return results
        
    finally:
        session.close()


def get_profitability_summary(period: str = 'month') -> Dict[str, Any]:
    """
    Get overall profitability summary and statistics.
    
    Args:
        period: Time period to analyze (week/month/quarter/all)
    
    Returns:
        Dictionary containing:
        - total_revenue: Total sales revenue
        - total_cost: Total cost of goods sold
        - total_profit: Total gross profit
        - overall_margin_pct: Overall profit margin %
        - products_analyzed: Number of products
        - profitable_products: Count of profitable products
        - unprofitable_products: Count of unprofitable products
        - top_profit_makers: Top 5 products by profit
        - bottom_performers: Bottom 5 products by profit
    
    Example:
        >>> summary = get_profitability_summary(period='month')
        >>> print(f"Overall margin: {summary['overall_margin_pct']:.1f}%")
    """
    session = SessionLocal()
    
    try:
        analysis = calculate_profitability_analysis(period=period, min_sales=1)
        
        if not analysis:
            return {
                'total_revenue': 0,
                'total_cost': 0,
                'total_profit': 0,
                'overall_margin_pct': 0,
                'products_analyzed': 0,
                'profitable_products': 0,
                'unprofitable_products': 0,
                'top_profit_makers': [],
                'bottom_performers': []
            }
        
        total_revenue = sum(p['total_revenue'] for p in analysis)
        total_cost = sum(p['total_cost'] for p in analysis)
        total_profit = sum(p['gross_profit'] for p in analysis)
        
        overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        profitable = [p for p in analysis if p['gross_profit'] > 0]
        unprofitable = [p for p in analysis if p['gross_profit'] <= 0]
        
        # Top 5 profit makers
        top_5 = sorted(analysis, key=lambda x: x['gross_profit'], reverse=True)[:5]
        top_profit_makers = [{
            'name': p['name'],
            'gross_profit': p['gross_profit'],
            'margin_pct': p['profit_margin_pct']
        } for p in top_5]
        
        # Bottom 5 performers
        bottom_5 = sorted(analysis, key=lambda x: x['gross_profit'])[:5]
        bottom_performers = [{
            'name': p['name'],
            'gross_profit': p['gross_profit'],
            'margin_pct': p['profit_margin_pct']
        } for p in bottom_5]
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'overall_margin_pct': round(overall_margin, 1),
            'products_analyzed': len(analysis),
            'profitable_products': len(profitable),
            'unprofitable_products': len(unprofitable),
            'top_profit_makers': top_profit_makers,
            'bottom_performers': bottom_performers
        }
        
    finally:
        session.close()
