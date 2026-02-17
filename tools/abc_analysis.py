"""
ABC Analysis tools for AI Agent.

This module implements ABC classification (Pareto analysis)
to categorize products by their contribution to revenue or profit.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem


def get_abc_analysis(
    period: str = 'month',
    metric: str = 'revenue'
) -> Dict[str, Any]:
    """
    Perform ABC analysis (Pareto 80/20 classification) on products.
    
    ABC Analysis categorizes products into three classes:
    - Class A: ~20% of products generating ~80% of metric (high value)
    - Class B: ~30% of products generating ~15% of metric (medium value)
    - Class C: ~50% of products generating ~5% of metric (low value)
    
    Args:
        period: Time period to analyze (week/month/quarter/all)
        metric: Metric to use for classification:
            - 'revenue': Sales revenue (default)
            - 'profit': Gross profit
            - 'quantity': Units sold
    
    Returns:
        Dictionary containing:
        - classification: List of products with ABC class
            - product_id, sku, name, category
            - metric_value: Value of selected metric
            - percentage_of_total: % contribution
            - cumulative_percentage: Running % total
            - abc_class: A, B, or C
        - summary: Statistics by class
            - class_a/b/c: Count and metrics for each class
        - recommendations: Management strategies by class
    
    Example:
        >>> abc = get_abc_analysis(period='month', metric='revenue')
        >>> class_a = [p for p in abc['classification'] if p['abc_class'] == 'A']
        >>> print(f"Class A: {len(class_a)} products generating {abc['summary']['class_a']['percentage']:.1f}%")
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
        
        # Query products with sales
        products_data = session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            Product.cost_price,
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price).label('total_revenue'),
            func.sum(SaleOrderItem.quantity).label('total_quantity')
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
        ).all()
        
        if not products_data:
            return {
                'classification': [],
                'summary': {},
                'recommendations': []
            }
        
        # Calculate metric for each product
        products_list = []
        for row in products_data:
            total_revenue = float(row.total_revenue)
            total_quantity = float(row.total_quantity)
            cost_price = float(row.cost_price)
            
            # Calculate metric value
            if metric == 'revenue':
                metric_value = total_revenue
            elif metric == 'profit':
                total_cost = total_quantity * cost_price
                metric_value = total_revenue - total_cost
            else:  # 'quantity'
                metric_value = total_quantity
            
            products_list.append({
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'category': row.category or 'N/A',
                'metric_value': metric_value,
                'total_revenue': total_revenue,
                'total_quantity': total_quantity
            })
        
        # Sort by metric value (descending)
        products_list.sort(key=lambda x: x['metric_value'], reverse=True)
        
        # Calculate total and percentages
        total_metric = sum(p['metric_value'] for p in products_list)
        
        classification = []
        cumulative = 0
        
        for product in products_list:
            percentage = (product['metric_value'] / total_metric * 100) if total_metric > 0 else 0
            cumulative += percentage
            
            # Assign ABC class based on cumulative percentage
            if cumulative <= 80:
                abc_class = 'A'
            elif cumulative <= 95:
                abc_class = 'B'
            else:
                abc_class = 'C'
            
            classification.append({
                'product_id': product['product_id'],
                'sku': product['sku'],
                'name': product['name'],
                'category': product['category'],
                'metric_value': round(product['metric_value'], 2),
                'total_revenue': round(product['total_revenue'], 2),
                'total_quantity': round(product['total_quantity'], 2),
                'percentage_of_total': round(percentage, 2),
                'cumulative_percentage': round(cumulative, 2),
                'abc_class': abc_class
            })
        
        # Calculate summary statistics
        class_a = [p for p in classification if p['abc_class'] == 'A']
        class_b = [p for p in classification if p['abc_class'] == 'B']
        class_c = [p for p in classification if p['abc_class'] == 'C']
        
        summary = {
            'total_products': len(classification),
            'total_metric_value': round(total_metric, 2),
            'metric_name': metric,
            'class_a': {
                'count': len(class_a),
                'percentage_of_products': round(len(class_a) / len(classification) * 100, 1) if classification else 0,
                'total_value': round(sum(p['metric_value'] for p in class_a), 2),
                'percentage_of_total': round(sum(p['percentage_of_total'] for p in class_a), 1)
            },
            'class_b': {
                'count': len(class_b),
                'percentage_of_products': round(len(class_b) / len(classification) * 100, 1) if classification else 0,
                'total_value': round(sum(p['metric_value'] for p in class_b), 2),
                'percentage_of_total': round(sum(p['percentage_of_total'] for p in class_b), 1)
            },
            'class_c': {
                'count': len(class_c),
                'percentage_of_products': round(len(class_c) / len(classification) * 100, 1) if classification else 0,
                'total_value': round(sum(p['metric_value'] for p in class_c), 2),
                'percentage_of_total': round(sum(p['percentage_of_total'] for p in class_c), 1)
            }
        }
        
        # Recommendations by class
        recommendations = [
            {
                'class': 'A',
                'strategy': 'High Priority Management',
                'actions': [
                    'Maintain optimal stock levels at all times',
                    'Monitor closely and never allow stockouts',
                    'Negotiate best prices with suppliers',
                    'Consider volume discounts',
                    'Fast reorder process'
                ]
            },
            {
                'class': 'B',
                'strategy': 'Moderate Management',
                'actions': [
                    'Maintain adequate stock levels',
                    'Regular monitoring',
                    'Standard reorder procedures',
                    'Balance cost vs. availability'
                ]
            },
            {
                'class': 'C',
                'strategy': 'Minimal Management',
                'actions': [
                    'Order in larger batches less frequently',
                    'Minimal safety stock',
                    'Periodic review only',
                    'Consider discontinuing poor performers'
                ]
            }
        ]
        
        return {
            'classification': classification,
            'summary': summary,
            'recommendations': recommendations
        }
        
    finally:
        session.close()
