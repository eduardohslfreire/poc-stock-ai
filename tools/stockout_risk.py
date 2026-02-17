"""
Stockout risk detection tools for AI Agent.

This module contains tools for detecting imminent stockout risks
and analyzing whether products have sufficient purchase orders
to cover future demand.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import (
    Product, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem
)


def detect_imminent_stockout_risk(
    days_forecast: int = 30,
    days_history: int = 90,
    min_days_threshold: int = 7
) -> List[Dict[str, Any]]:
    """
    Detect products at risk of stockout that don't have adequate purchase orders.
    
    This is a PREVENTIVE tool that identifies products that will run out of stock
    soon based on current sales velocity, and checks if there are sufficient
    pending purchase orders to prevent the stockout.
    
    Key differences from detect_stock_rupture():
    - detect_stock_rupture(): Products already at stock=0 (reactive)
    - detect_imminent_stockout_risk(): Products about to reach stock=0 (preventive)
    
    Algorithm:
    1. Calculate average daily sales from history
    2. Estimate days until stockout (current_stock / daily_sales)
    3. Check if days_until_stockout < threshold
    4. Verify if there are pending purchase orders
    5. Calculate if pending orders are sufficient
    6. Flag products that need urgent action
    
    Args:
        days_forecast: Days to forecast demand for (default: 30)
        days_history: Historical days to analyze sales (default: 90)
        min_days_threshold: Alert if stockout within this many days (default: 7)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Current stock level
        - avg_daily_sales: Average daily sales (units)
        - days_until_stockout: Estimated days until stock runs out
        - forecasted_demand: Projected demand for forecast period
        - pending_orders: Dictionary with pending order information:
            - count: Number of pending orders
            - total_quantity: Total quantity in pending orders
            - is_sufficient: Whether pending orders cover forecasted demand
            - oldest_order_days: Days since oldest pending order
            - is_delayed: Whether oldest order is likely delayed (>7 days)
            - orders: List of pending order details
        - gap_quantity: Additional quantity needed beyond pending orders
        - risk_level: HIGH/MEDIUM/LOW based on urgency
        - recommendation: Suggested action
        - potential_lost_revenue: Estimated revenue loss if stockout occurs
    
    Example:
        >>> at_risk = detect_imminent_stockout_risk(min_days_threshold=7)
        >>> for item in at_risk:
        >>>     print(f"{item['name']}: {item['days_until_stockout']} days until stockout")
        >>>     if not item['pending_orders']['is_sufficient']:
        >>>         print(f"  ⚠️ Need to order {item['gap_quantity']} more units!")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_history)
        
        # Get all active products with stock > 0
        products = session.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.current_stock > 0
            )
        ).all()
        
        at_risk_products = []
        
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
            
            # Skip products with no sales history
            if total_sold == 0:
                continue
            
            # Calculate average daily sales
            avg_daily_sales = total_sold / days_history
            
            # Calculate days until stockout
            current_stock = float(product.current_stock)
            
            if avg_daily_sales > 0:
                days_until_stockout = current_stock / avg_daily_sales
            else:
                continue  # No demand, no risk
            
            # Only include products that will run out soon
            if days_until_stockout > min_days_threshold:
                continue
            
            # Forecast demand for the forecast period
            forecasted_demand = avg_daily_sales * days_forecast
            
            # === CHECK PENDING PURCHASE ORDERS ===
            pending_orders_query = session.query(
                PurchaseOrder.id,
                PurchaseOrder.order_number,
                PurchaseOrder.order_date,
                PurchaseOrderItem.quantity,
                PurchaseOrderItem.unit_price
            ).join(
                PurchaseOrderItem, PurchaseOrder.id == PurchaseOrderItem.purchase_order_id
            ).filter(
                and_(
                    PurchaseOrderItem.product_id == product.id,
                    PurchaseOrder.status == 'PENDING'
                )
            ).all()
            
            # Process pending orders
            pending_orders_info = {
                'count': 0,
                'total_quantity': 0,
                'is_sufficient': False,
                'oldest_order_days': None,
                'is_delayed': False,
                'orders': []
            }
            
            if pending_orders_query:
                pending_orders_info['count'] = len(pending_orders_query)
                
                oldest_order_date = None
                for po in pending_orders_query:
                    qty = float(po.quantity)
                    pending_orders_info['total_quantity'] += qty
                    
                    pending_orders_info['orders'].append({
                        'order_id': po.id,
                        'order_number': po.order_number,
                        'order_date': po.order_date.isoformat(),
                        'quantity': qty,
                        'unit_price': float(po.unit_price)
                    })
                    
                    if oldest_order_date is None or po.order_date < oldest_order_date:
                        oldest_order_date = po.order_date
                
                # Calculate age of oldest order
                if oldest_order_date:
                    pending_orders_info['oldest_order_days'] = (datetime.now().date() - oldest_order_date).days
                    pending_orders_info['is_delayed'] = pending_orders_info['oldest_order_days'] > 7
                
                # Check if pending orders are sufficient
                total_needed = forecasted_demand - current_stock
                pending_orders_info['is_sufficient'] = pending_orders_info['total_quantity'] >= total_needed
            
            # Calculate gap (how much more to order)
            total_available = current_stock + pending_orders_info['total_quantity']
            gap_quantity = max(0, forecasted_demand - total_available)
            
            # Determine risk level
            if days_until_stockout <= 3 and not pending_orders_info['is_sufficient']:
                risk_level = "CRITICAL"
            elif days_until_stockout <= 3 or (pending_orders_info['is_delayed'] and not pending_orders_info['is_sufficient']):
                risk_level = "HIGH"
            elif not pending_orders_info['is_sufficient']:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Generate recommendation
            if pending_orders_info['count'] == 0:
                recommendation = f"URGENT: Create purchase order for at least {int(gap_quantity)} units immediately"
            elif not pending_orders_info['is_sufficient']:
                recommendation = f"ORDER MORE: Pending orders insufficient. Need {int(gap_quantity)} additional units"
            elif pending_orders_info['is_delayed']:
                recommendation = f"FOLLOW UP: Pending order is {pending_orders_info['oldest_order_days']} days old. Contact supplier"
            else:
                recommendation = "MONITOR: Pending orders should cover demand"
            
            # Calculate potential lost revenue
            daily_revenue = avg_daily_sales * float(product.sale_price)
            # If no pending orders, losses start when stock runs out
            days_of_potential_loss = max(0, days_forecast - days_until_stockout)
            potential_lost_revenue = daily_revenue * days_of_potential_loss
            
            at_risk_products.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'current_stock': round(current_stock, 2),
                'avg_daily_sales': round(avg_daily_sales, 2),
                'days_until_stockout': round(days_until_stockout, 1),
                'forecasted_demand': round(forecasted_demand, 2),
                'pending_orders': pending_orders_info,
                'gap_quantity': round(gap_quantity, 2),
                'risk_level': risk_level,
                'recommendation': recommendation,
                'potential_lost_revenue': round(potential_lost_revenue, 2),
                'unit_sale_price': float(product.sale_price),
                'unit_cost': float(product.cost_price)
            })
        
        # Sort by risk level then by days until stockout
        risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        at_risk_products.sort(key=lambda x: (risk_order[x['risk_level']], x['days_until_stockout']))
        
        return at_risk_products
        
    finally:
        session.close()


def get_pending_order_summary(product_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get summary of all pending purchase orders, optionally filtered by product.
    
    This helper tool provides visibility into what purchase orders are pending
    and helps track order fulfillment.
    
    Args:
        product_id: Optional product ID to filter (default: None = all products)
    
    Returns:
        List of dictionaries containing:
        - purchase_order_id: Purchase order ID
        - order_number: Purchase order number
        - supplier_name: Supplier name
        - order_date: When order was placed
        - days_pending: Days since order was placed
        - is_delayed: Whether order is likely delayed (>7 days)
        - products: List of products in the order
        - total_value: Total order value
    
    Example:
        >>> pending = get_pending_order_summary()
        >>> delayed = [p for p in pending if p['is_delayed']]
        >>> print(f"{len(delayed)} delayed orders")
    """
    session = SessionLocal()
    
    try:
        query = session.query(PurchaseOrder).filter(
            PurchaseOrder.status == 'PENDING'
        )
        
        pending_orders = query.all()
        
        result = []
        for po in pending_orders:
            days_pending = (datetime.now().date() - po.order_date).days
            
            # Get items in this order
            items = []
            for item in po.items:
                # Filter by product_id if specified
                if product_id is not None and item.product_id != product_id:
                    continue
                
                items.append({
                    'product_id': item.product_id,
                    'product_name': item.product.name,
                    'sku': item.product.sku,
                    'quantity': float(item.quantity),
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.quantity * item.unit_price)
                })
            
            # Skip if filtering by product and no matching items
            if product_id is not None and not items:
                continue
            
            result.append({
                'purchase_order_id': po.id,
                'order_number': po.order_number,
                'supplier_name': po.supplier.name,
                'order_date': po.order_date.isoformat(),
                'days_pending': days_pending,
                'is_delayed': days_pending > 7,
                'products': items,
                'total_value': float(po.total_amount)
            })
        
        # Sort by days pending (most urgent first)
        result.sort(key=lambda x: x['days_pending'], reverse=True)
        
        return result
        
    finally:
        session.close()
