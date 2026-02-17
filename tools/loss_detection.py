"""
Loss detection tools for AI Agent.

This module contains tools for detecting potential stock losses,
theft, or discrepancies in inventory.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.schema import Product, StockMovement


def detect_stock_losses(tolerance_percentage: float = 5.0) -> List[Dict[str, Any]]:
    """
    Detect potential stock losses by analyzing discrepancies.
    
    This tool identifies products where there's a significant difference
    between expected stock (based on movements) and actual stock, which
    may indicate theft, damage, or recording errors.
    
    The analysis compares:
    - Expected stock: Sum of all IN movements - Sum of all OUT movements
    - Actual stock: Current stock in database
    
    Args:
        tolerance_percentage: Acceptable variance % before flagging as loss (default: 5%)
    
    Returns:
        List of dictionaries containing:
        - product_id: Product ID
        - sku: Product SKU
        - name: Product name
        - category: Product category
        - current_stock: Actual stock in system
        - expected_stock: Calculated expected stock
        - discrepancy: Difference (expected - actual)
        - discrepancy_percentage: Discrepancy as % of expected
        - estimated_loss_value: Financial value of loss (cost price)
        - last_movement_date: Date of last stock movement
        - loss_movements: Number of explicit LOSS movements
        - severity: CRITICAL/HIGH/MEDIUM based on discrepancy
        - recommendation: Suggested action
    
    Example:
        >>> results = detect_stock_losses(tolerance_percentage=5.0)
        >>> critical = [r for r in results if r['severity'] == 'CRITICAL']
        >>> print(f"Found {len(critical)} critical discrepancies")
    """
    session = SessionLocal()
    
    try:
        products = session.query(Product).filter(Product.is_active == True).all()
        results = []
        
        for product in products:
            # Get all stock movements for this product
            movements = session.query(StockMovement).filter(
                StockMovement.product_id == product.id
            ).order_by(StockMovement.movement_date).all()
            
            if not movements:
                continue  # Skip products with no movements
            
            # Calculate expected stock from movements
            expected_stock = Decimal('0')
            loss_movements_count = 0
            
            for movement in movements:
                expected_stock += movement.quantity
                if movement.movement_type == 'LOSS':
                    loss_movements_count += 1
            
            # Compare with actual stock
            actual_stock = product.current_stock
            discrepancy = expected_stock - actual_stock
            
            # Calculate percentage (avoid division by zero)
            if expected_stock != 0:
                discrepancy_pct = abs(float(discrepancy / expected_stock * 100))
            else:
                discrepancy_pct = 0
            
            # Only flag if discrepancy exceeds tolerance
            if discrepancy_pct <= tolerance_percentage:
                continue
            
            # Calculate financial impact
            estimated_loss_value = abs(float(discrepancy * product.cost_price))
            
            # Get last movement date
            last_movement = movements[-1]
            last_movement_date = last_movement.movement_date
            
            # Determine severity
            if discrepancy_pct > 20:
                severity = "CRITICAL"
                recommendation = "URGENT: Perform physical count and investigate immediately"
            elif discrepancy_pct > 10:
                severity = "HIGH"
                recommendation = "IMPORTANT: Schedule physical count and review security"
            else:
                severity = "MEDIUM"
                recommendation = "MONITOR: Review and correct inventory records"
            
            results.append({
                'product_id': product.id,
                'sku': product.sku,
                'name': product.name,
                'category': product.category or 'N/A',
                'current_stock': float(actual_stock),
                'expected_stock': float(expected_stock),
                'discrepancy': float(discrepancy),
                'discrepancy_percentage': round(discrepancy_pct, 2),
                'estimated_loss_value': round(estimated_loss_value, 2),
                'last_movement_date': last_movement_date.isoformat() if last_movement_date else None,
                'loss_movements': loss_movements_count,
                'severity': severity,
                'recommendation': recommendation
            })
        
        # Sort by severity then by loss value
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        results.sort(key=lambda x: (severity_order[x['severity']], -x['estimated_loss_value']))
        
        return results
        
    finally:
        session.close()


def get_explicit_losses(days_period: int = 90) -> List[Dict[str, Any]]:
    """
    Get all explicit loss movements recorded in the system.
    
    This tool retrieves stock movements that were explicitly marked as
    LOSS type, representing acknowledged losses, damages, or theft.
    
    Args:
        days_period: Number of days to look back (default: 90)
    
    Returns:
        List of dictionaries containing:
        - movement_id: Movement ID
        - product_id: Product ID
        - sku: Product SKU
        - product_name: Product name
        - quantity_lost: Quantity lost (absolute value)
        - loss_value: Financial value of loss
        - loss_date: Date of loss
        - notes: Notes about the loss
        - days_ago: Days since the loss occurred
    
    Example:
        >>> losses = get_explicit_losses(days_period=30)
        >>> total_value = sum(l['loss_value'] for l in losses)
        >>> print(f"Total losses in 30 days: R$ {total_value:,.2f}")
    """
    session = SessionLocal()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days_period)
        
        # Query loss movements
        losses = session.query(
            StockMovement.id,
            StockMovement.product_id,
            StockMovement.quantity,
            StockMovement.unit_cost,
            StockMovement.movement_date,
            StockMovement.notes,
            Product.sku,
            Product.name,
            Product.category
        ).join(
            Product, StockMovement.product_id == Product.id
        ).filter(
            and_(
                StockMovement.movement_type == 'LOSS',
                StockMovement.movement_date >= cutoff_date
            )
        ).order_by(
            StockMovement.movement_date.desc()
        ).all()
        
        results = []
        for loss in losses:
            quantity_lost = abs(float(loss.quantity))
            loss_value = quantity_lost * float(loss.unit_cost) if loss.unit_cost else 0
            days_ago = (datetime.now() - loss.movement_date).days
            
            results.append({
                'movement_id': loss.id,
                'product_id': loss.product_id,
                'sku': loss.sku,
                'product_name': loss.name,
                'category': loss.category or 'N/A',
                'quantity_lost': quantity_lost,
                'loss_value': round(loss_value, 2),
                'loss_date': loss.movement_date.isoformat(),
                'notes': loss.notes or 'No notes',
                'days_ago': days_ago
            })
        
        return results
        
    finally:
        session.close()
