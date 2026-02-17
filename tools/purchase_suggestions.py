"""
Purchase suggestion tools for AI Agent.

This module contains tools for generating optimal purchase
recommendations based on sales history and demand forecasting.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import (
    Product, Supplier, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem
)


def suggest_purchase_order(
    days_forecast: int = 30,
    days_history: int = 90,
    min_order_value: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Suggest purchase orders based on sales history and demand forecasting.
    
    This tool analyzes sales patterns to recommend what products to purchase
    and in what quantities to meet future demand while avoiding overstock.
    
    Algorithm:
    1. Calculate average daily sales from history period
    2. Project demand for forecast period
    3. Consider current stock levels
    4. Subtract current stock from projected demand
    5. Apply safety stock buffer
    6. Recommend purchase quantity
    
    Args:
        days_forecast: Days to forecast demand for (default: 30)
        days_history: Historical days to analyze (default: 90)
        min_order_value: Minimum order value to include (default: R$ 100)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Current stock level
        - avg_daily_sales: Average daily sales (units)
        - forecasted_demand: Projected demand for forecast period
        - stock_needed: Stock needed (demand - current)
        - suggested_quantity: Recommended purchase quantity (with buffer)
        - unit_cost: Product cost price
        - order_value: Total order value for this product
        - priority: HIGH/MEDIUM/LOW based on urgency
        - last_sale_date: Date of last sale
        - days_until_stockout: Estimated days until stock runs out
        - pending_orders: Information about pending purchase orders:
            - has_pending: Whether product has pending orders
            - total_quantity: Total quantity in pending orders
            - order_count: Number of pending orders
            - is_sufficient: Whether pending orders cover forecasted demand
    
    Example:
        >>> suggestions = suggest_purchase_order(days_forecast=30)
        >>> total_value = sum(s['order_value'] for s in suggestions)
        >>> print(f"Suggested order total: R$ {total_value:,.2f}")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_history)
        
        # Get all active products
        products = session.query(Product).filter(Product.is_active == True).all()
        
        suggestions = []
        
        for product in products:
            # Calculate sales in history period
            sales_data = session.query(
                func.sum(SaleOrderItem.quantity).label('total_sold'),
                func.count(func.distinct(SaleOrder.id)).label('sales_count'),
                func.max(SaleOrder.sale_date).label('last_sale')
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrderItem.product_id == product.id,
                    SaleOrder.sale_date >= cutoff_date.date(),
                    SaleOrder.status == 'PAID'
                )
            ).first()
            
            total_sold = float(sales_data.total_sold or 0)
            sales_count = sales_data.sales_count or 0
            last_sale = sales_data.last_sale
            
            # Skip products with no sales history
            if total_sold == 0:
                continue
            
            # Calculate average daily sales
            avg_daily_sales = total_sold / days_history
            
            # Forecast demand for the next period
            forecasted_demand = avg_daily_sales * days_forecast
            
            # Current stock
            current_stock = float(product.current_stock)
            
            # Calculate stock needed
            stock_needed = forecasted_demand - current_stock
            
            # Skip if we have enough stock
            if stock_needed <= 0:
                continue
            
            # Add safety buffer (20% extra)
            safety_buffer = 1.2
            suggested_quantity = stock_needed * safety_buffer
            
            # Round to reasonable quantity
            if suggested_quantity < 10:
                suggested_quantity = round(suggested_quantity)
            elif suggested_quantity < 100:
                suggested_quantity = round(suggested_quantity / 5) * 5  # Round to nearest 5
            else:
                suggested_quantity = round(suggested_quantity / 10) * 10  # Round to nearest 10
            
            # Ensure minimum order quantity
            if suggested_quantity < 1:
                suggested_quantity = 1
            
            # Calculate order value
            unit_cost = float(product.cost_price)
            order_value = suggested_quantity * unit_cost
            
            # Skip if order value is too low
            if order_value < min_order_value:
                continue
            
            # Calculate days until stockout
            if avg_daily_sales > 0:
                days_until_stockout = int(current_stock / avg_daily_sales)
            else:
                days_until_stockout = 999
            
            # === CHECK PENDING PURCHASE ORDERS ===
            pending_orders_data = session.query(
                func.count(PurchaseOrder.id).label('order_count'),
                func.sum(PurchaseOrderItem.quantity).label('total_quantity')
            ).join(
                PurchaseOrderItem, PurchaseOrder.id == PurchaseOrderItem.purchase_order_id
            ).filter(
                and_(
                    PurchaseOrderItem.product_id == product.id,
                    PurchaseOrder.status == 'PENDING'
                )
            ).first()
            
            pending_quantity = float(pending_orders_data.total_quantity or 0)
            pending_count = pending_orders_data.order_count or 0
            has_pending = pending_count > 0
            
            # Check if pending orders are sufficient
            is_sufficient = (current_stock + pending_quantity) >= forecasted_demand
            
            pending_orders = {
                'has_pending': has_pending,
                'total_quantity': pending_quantity,
                'order_count': pending_count,
                'is_sufficient': is_sufficient
            }
            
            # Determine priority (considering pending orders)
            if days_until_stockout <= 7 and not is_sufficient:
                priority = "HIGH"
            elif days_until_stockout <= 14 and not is_sufficient:
                priority = "MEDIUM"
            elif not is_sufficient:
                priority = "LOW"
            else:
                priority = "LOW"  # Has sufficient pending orders
            
            suggestions.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'current_stock': current_stock,
                'avg_daily_sales': round(avg_daily_sales, 2),
                'forecasted_demand': round(forecasted_demand, 2),
                'stock_needed': round(stock_needed, 2),
                'suggested_quantity': int(suggested_quantity),
                'unit_cost': unit_cost,
                'order_value': round(order_value, 2),
                'priority': priority,
                'last_sale_date': last_sale.isoformat() if last_sale else None,
                'days_until_stockout': days_until_stockout if days_until_stockout < 999 else None,
                'pending_orders': pending_orders
            })
        
        # Sort by priority then by order value
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        suggestions.sort(key=lambda x: (priority_order[x['priority']], -x['order_value']))
        
        return suggestions
        
    finally:
        session.close()


def group_suggestions_by_supplier() -> List[Dict[str, Any]]:
    """
    Group purchase suggestions by supplier for consolidated orders.
    
    This tool takes purchase suggestions and groups them by supplier,
    making it easier to create actual purchase orders.
    
    Returns:
        List of dictionaries containing:
        - supplier_id: Supplier ID
        - supplier_name: Supplier name
        - products_count: Number of products to order
        - products: List of products with quantities
        - total_order_value: Total value for this supplier
        - high_priority_items: Number of high-priority items
    
    Example:
        >>> grouped = group_suggestions_by_supplier()
        >>> for supplier in grouped:
        >>>     print(f"{supplier['supplier_name']}: R$ {supplier['total_order_value']:,.2f}")
    """
    session = SessionLocal()
    
    try:
        # Get suggestions first
        suggestions = suggest_purchase_order(days_forecast=30)
        
        if not suggestions:
            return []
        
        # Get supplier for each product (last supplier who provided it)
        supplier_groups = {}
        
        for suggestion in suggestions:
            # Find last supplier for this product
            last_purchase = session.query(
                Supplier.id,
                Supplier.name
            ).join(
                PurchaseOrder, Supplier.id == PurchaseOrder.supplier_id
            ).join(
                PurchaseOrderItem, PurchaseOrder.id == PurchaseOrderItem.purchase_order_id
            ).filter(
                PurchaseOrderItem.product_id == suggestion['product_id']
            ).order_by(
                PurchaseOrder.order_date.desc()
            ).first()
            
            if not last_purchase:
                # No previous supplier, skip
                continue
            
            supplier_id = last_purchase.id
            supplier_name = last_purchase.name
            
            if supplier_id not in supplier_groups:
                supplier_groups[supplier_id] = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'products': [],
                    'total_order_value': 0,
                    'high_priority_items': 0
                }
            
            supplier_groups[supplier_id]['products'].append({
                'product_id': suggestion['product_id'],
                'sku': suggestion['sku'],
                'name': suggestion['name'],
                'quantity': suggestion['suggested_quantity'],
                'unit_cost': suggestion['unit_cost'],
                'order_value': suggestion['order_value'],
                'priority': suggestion['priority']
            })
            
            supplier_groups[supplier_id]['total_order_value'] += suggestion['order_value']
            
            if suggestion['priority'] == 'HIGH':
                supplier_groups[supplier_id]['high_priority_items'] += 1
        
        # Convert to list and add products count
        result = []
        for supplier_data in supplier_groups.values():
            supplier_data['products_count'] = len(supplier_data['products'])
            result.append(supplier_data)
        
        # Sort by total order value (descending)
        result.sort(key=lambda x: x['total_order_value'], reverse=True)
        
        return result
        
    finally:
        session.close()
