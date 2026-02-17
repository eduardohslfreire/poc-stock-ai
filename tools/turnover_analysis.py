"""
Inventory turnover analysis tools for AI Agent.

This module contains tools for analyzing the time between
purchase and sale, helping identify slow-moving inventory.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import (
    Product, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem, StockMovement
)


def analyze_purchase_to_sale_time(
    days_period: int = 90,
    min_purchases: int = 1
) -> List[Dict[str, Any]]:
    """
    Analyze time between purchase and first sale for products.
    
    This tool calculates how long products sit in inventory before
    being sold, helping identify slow-moving items and optimize
    purchasing decisions.
    
    Algorithm:
    1. Find all purchase orders in the period
    2. For each purchased product, find first sale after purchase
    3. Calculate time difference
    4. Aggregate statistics per product
    
    Args:
        days_period: Historical period to analyze in days (default: 90)
        min_purchases: Minimum purchases to include product (default: 1)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - purchases_count: Number of purchases analyzed
        - avg_days_to_sale: Average days from purchase to first sale
        - min_days_to_sale: Fastest sale after purchase
        - max_days_to_sale: Slowest sale after purchase
        - still_unsold_count: Purchases with no sale yet
        - current_stock: Current stock level
        - turnover_rating: FAST/MEDIUM/SLOW based on avg days
        - recommendation: Suggested action
    
    Example:
        >>> results = analyze_purchase_to_sale_time(days_period=90)
        >>> slow_movers = [r for r in results if r['turnover_rating'] == 'SLOW']
        >>> print(f"Found {len(slow_movers)} slow-moving products")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_period)
        
        # Get all products with purchases in the period
        products_with_purchases = session.query(Product.id).join(
            PurchaseOrderItem, Product.id == PurchaseOrderItem.product_id
        ).join(
            PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id
        ).filter(
            and_(
                PurchaseOrder.order_date >= cutoff_date.date(),
                PurchaseOrder.status == 'RECEIVED'
            )
        ).distinct().all()
        
        product_ids = [p.id for p in products_with_purchases]
        
        results = []
        
        for product_id in product_ids:
            product = session.query(Product).filter(Product.id == product_id).first()
            
            if not product:
                continue
            
            # Get all purchases for this product in the period
            purchases = session.query(
                PurchaseOrder.id,
                PurchaseOrder.received_date,
                PurchaseOrderItem.quantity
            ).join(
                PurchaseOrderItem, PurchaseOrder.id == PurchaseOrderItem.purchase_order_id
            ).filter(
                and_(
                    PurchaseOrderItem.product_id == product_id,
                    PurchaseOrder.order_date >= cutoff_date.date(),
                    PurchaseOrder.status == 'RECEIVED',
                    PurchaseOrder.received_date.isnot(None)
                )
            ).order_by(PurchaseOrder.received_date).all()
            
            if len(purchases) < min_purchases:
                continue
            
            # For each purchase, find time to first sale
            days_to_sale_list = []
            unsold_count = 0
            
            for purchase in purchases:
                purchase_date = purchase.received_date
                
                # Find first sale after this purchase
                first_sale = session.query(SaleOrder.sale_date).join(
                    SaleOrderItem, SaleOrder.id == SaleOrderItem.sale_order_id
                ).filter(
                    and_(
                        SaleOrderItem.product_id == product_id,
                        SaleOrder.sale_date >= purchase_date,
                        SaleOrder.status == 'PAID'
                    )
                ).order_by(SaleOrder.sale_date).first()
                
                if first_sale:
                    days_to_sale = (first_sale.sale_date - purchase_date).days
                    days_to_sale_list.append(days_to_sale)
                else:
                    unsold_count += 1
            
            # Skip if no sales data
            if not days_to_sale_list:
                continue
            
            # Calculate statistics
            avg_days = sum(days_to_sale_list) / len(days_to_sale_list)
            min_days = min(days_to_sale_list)
            max_days = max(days_to_sale_list)
            
            # Determine turnover rating
            if avg_days <= 7:
                turnover_rating = "FAST"
                recommendation = "Excellent turnover - maintain current inventory levels"
            elif avg_days <= 21:
                turnover_rating = "MEDIUM"
                recommendation = "Good turnover - monitor for optimization opportunities"
            else:
                turnover_rating = "SLOW"
                recommendation = "Slow turnover - consider reducing order quantities or frequency"
            
            results.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'purchases_count': len(purchases),
                'avg_days_to_sale': round(avg_days, 1),
                'min_days_to_sale': min_days,
                'max_days_to_sale': max_days,
                'still_unsold_count': unsold_count,
                'current_stock': float(product.current_stock),
                'turnover_rating': turnover_rating,
                'recommendation': recommendation
            })
        
        # Sort by avg days (slowest first)
        results.sort(key=lambda x: x['avg_days_to_sale'], reverse=True)
        
        return results
        
    finally:
        session.close()


def get_inventory_age_distribution() -> Dict[str, Any]:
    """
    Get distribution of inventory by age (time in stock).
    
    This tool analyzes current inventory to show how long products
    have been sitting in stock, helping identify aging inventory.
    
    Returns:
        Dictionary containing:
        - age_brackets: List of age brackets with counts
            - bracket: Age range (e.g., "0-7 days")
            - products_count: Number of products
            - total_value: Total inventory value
            - percentage: % of total inventory value
        - total_products: Total products analyzed
        - total_value: Total inventory value
        - avg_age_days: Average inventory age
        - oldest_product: Details of oldest inventory
    
    Example:
        >>> distribution = get_inventory_age_distribution()
        >>> old_stock = [b for b in distribution['age_brackets'] if '60+' in b['bracket']]
        >>> print(f"Old stock value: R$ {old_stock[0]['total_value']:,.2f}")
    """
    session = SessionLocal()
    
    try:
        # Define age brackets
        brackets = [
            {'name': '0-7 days', 'min': 0, 'max': 7},
            {'name': '8-14 days', 'min': 8, 'max': 14},
            {'name': '15-30 days', 'min': 15, 'max': 30},
            {'name': '31-60 days', 'min': 31, 'max': 60},
            {'name': '60+ days', 'min': 61, 'max': 9999}
        ]
        
        products_with_stock = session.query(Product).filter(
            Product.current_stock > 0
        ).all()
        
        # Calculate age for each product (last purchase date)
        age_data = []
        total_value = 0
        ages_for_avg = []
        oldest_product = None
        max_age = 0
        
        for product in products_with_stock:
            # Find last purchase (stock entry)
            last_purchase = session.query(StockMovement.movement_date).filter(
                and_(
                    StockMovement.product_id == product.id,
                    StockMovement.movement_type == 'PURCHASE'
                )
            ).order_by(StockMovement.movement_date.desc()).first()
            
            if not last_purchase:
                continue
            
            age_days = (datetime.now() - last_purchase.movement_date).days
            stock_value = float(product.current_stock * product.cost_price)
            
            age_data.append({
                'product': product,
                'age_days': age_days,
                'stock_value': stock_value
            })
            
            total_value += stock_value
            ages_for_avg.append(age_days)
            
            if age_days > max_age:
                max_age = age_days
                oldest_product = {
                    'name': product.name,
                    'sku': product.sku,
                    'age_days': age_days,
                    'stock': float(product.current_stock),
                    'value': stock_value
                }
        
        # Distribute into brackets
        bracket_results = []
        
        for bracket in brackets:
            products_in_bracket = [
                item for item in age_data
                if bracket['min'] <= item['age_days'] <= bracket['max']
            ]
            
            bracket_value = sum(item['stock_value'] for item in products_in_bracket)
            percentage = (bracket_value / total_value * 100) if total_value > 0 else 0
            
            bracket_results.append({
                'bracket': bracket['name'],
                'products_count': len(products_in_bracket),
                'total_value': round(bracket_value, 2),
                'percentage': round(percentage, 1)
            })
        
        # Calculate average age
        avg_age = sum(ages_for_avg) / len(ages_for_avg) if ages_for_avg else 0
        
        return {
            'age_brackets': bracket_results,
            'total_products': len(age_data),
            'total_value': round(total_value, 2),
            'avg_age_days': round(avg_age, 1),
            'oldest_product': oldest_product
        }
        
    finally:
        session.close()
