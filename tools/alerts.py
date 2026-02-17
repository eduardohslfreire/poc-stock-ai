"""
Alerts and dashboard tools for AI Agent.

This module consolidates alerts from all other tools to provide
a comprehensive overview of stock health and critical issues.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_

from database.connection import SessionLocal
from database.schema import Product, SaleOrder, SaleOrderItem, StockMovement

# Import other tools
from tools.stock_analysis import detect_stock_rupture, analyze_slow_moving_stock
from tools.loss_detection import detect_stock_losses, get_explicit_losses
from tools.purchase_suggestions import suggest_purchase_order
from tools.stockout_risk import detect_imminent_stockout_risk


def get_stock_alerts() -> Dict[str, Any]:
    """
    Get comprehensive stock alerts and health dashboard.
    
    This tool aggregates critical information from all analysis modules
    to provide a complete overview of inventory health, critical issues,
    and recommended actions.
    
    Returns:
        Dictionary containing:
        - summary: Overall health metrics
            - total_products: Total active products
            - products_with_stock: Products with stock > 0
            - total_stock_value: Total inventory value
            - alerts_count: Total number of alerts
        - critical_alerts: List of critical issues requiring immediate action
        - warnings: List of important issues requiring attention
        - recommendations: List of suggested actions
        - metrics: Key performance indicators
    
    Example:
        >>> alerts = get_stock_alerts()
        >>> print(f"Critical issues: {len(alerts['critical_alerts'])}")
        >>> for alert in alerts['critical_alerts']:
        >>>     print(f"- {alert['message']}")
    """
    session = SessionLocal()
    
    try:
        # === SUMMARY METRICS ===
        total_products = session.query(Product).filter(Product.is_active == True).count()
        products_with_stock = session.query(Product).filter(
            and_(Product.is_active == True, Product.current_stock > 0)
        ).count()
        
        total_stock_value = session.query(
            func.sum(Product.current_stock * Product.cost_price)
        ).filter(Product.is_active == True).scalar() or 0
        
        # === COLLECT ALERTS FROM ALL TOOLS ===
        critical_alerts = []
        warnings = []
        recommendations = []
        
        # 1. Imminent Stockout Risk (Critical - PREVENTIVE)
        stockout_risks = detect_imminent_stockout_risk(days_forecast=30, min_days_threshold=7)
        critical_risks = [r for r in stockout_risks if r['risk_level'] in ['CRITICAL', 'HIGH']]
        
        for risk in critical_risks[:5]:  # Top 5 most critical
            icon = '🔴' if risk['risk_level'] == 'CRITICAL' else '🟠'
            critical_alerts.append({
                'type': 'IMMINENT_STOCKOUT',
                'severity': risk['risk_level'],
                'product_id': risk['product_id'],
                'product_name': risk['name'],
                'message': f"{icon} {risk['name']} - Will run out in {risk['days_until_stockout']:.1f} days",
                'detail': f"Pending orders: {'Insufficient' if not risk['pending_orders']['is_sufficient'] else 'Sufficient'}. Gap: {risk['gap_quantity']:.0f} units",
                'action': risk['recommendation']
            })
        
        # 2. Stock Ruptures (Critical - REACTIVE)
        ruptures = detect_stock_rupture(days_lookback=14)
        for rupture in ruptures[:5]:  # Top 5 most critical
            critical_alerts.append({
                'type': 'STOCK_RUPTURE',
                'severity': 'CRITICAL',
                'product_id': rupture['product_id'],
                'product_name': rupture['name'],
                'message': f"🔴 {rupture['name']} - Out of stock with recent demand ({rupture['recent_sales_count']} sales)",
                'detail': f"Lost revenue: R$ {rupture['lost_revenue_estimate']:,.2f}",
                'action': 'Purchase immediately to avoid further losses'
            })
        
        # 3. Slow-Moving Stock (Warning)
        slow_moving = analyze_slow_moving_stock(days_threshold=60)
        urgent_slow = [s for s in slow_moving if 'URGENT' in s['recommendation']]
        
        for item in urgent_slow[:3]:  # Top 3 most urgent
            warnings.append({
                'type': 'SLOW_MOVING',
                'severity': 'HIGH',
                'product_id': item['product_id'],
                'product_name': item['name'],
                'message': f"🟠 {item['name']} - No sales for {item['days_without_sale']} days",
                'detail': f"Capital tied up: R$ {item['stock_value']:,.2f}",
                'action': 'Apply discount/promotion or return to supplier'
            })
        
        # 4. Stock Losses (Critical if found)
        losses = detect_stock_losses(tolerance_percentage=5.0)
        for loss in losses[:3]:  # Top 3 discrepancies
            critical_alerts.append({
                'type': 'STOCK_LOSS',
                'severity': 'CRITICAL',
                'product_id': loss['product_id'],
                'product_name': loss['name'],
                'message': f"⚠️ {loss['name']} - Stock discrepancy detected ({loss['discrepancy_percentage']:.1f}%)",
                'detail': f"Estimated loss value: R$ {loss['estimated_loss_value']:,.2f}",
                'action': loss['recommendation']
            })
        
        # 5. Low Stock on High-Demand Products (Warning - now mostly covered by imminent stockout)
        session_db = SessionLocal()
        try:
            # Get products sold recently
            recent_sales = session_db.query(
                Product.id,
                Product.name,
                Product.current_stock,
                Product.sale_price,
                func.sum(SaleOrderItem.quantity).label('qty_sold')
            ).join(
                SaleOrderItem, Product.id == SaleOrderItem.product_id
            ).join(
                SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
            ).filter(
                and_(
                    SaleOrder.sale_date >= (datetime.now() - timedelta(days=7)).date(),
                    SaleOrder.status == 'PAID'
                )
            ).group_by(
                Product.id, Product.name, Product.current_stock, Product.sale_price
            ).all()
            
            for item in recent_sales:
                daily_demand = float(item.qty_sold) / 7
                days_of_stock = float(item.current_stock) / daily_demand if daily_demand > 0 else 999
                
                if 0 < days_of_stock < 7 and item.current_stock > 0:  # Less than a week of stock
                    warnings.append({
                        'type': 'LOW_STOCK_HIGH_DEMAND',
                        'severity': 'MEDIUM',
                        'product_id': item.id,
                        'product_name': item.name,
                        'message': f"🟡 {item.name} - Low stock for high-demand product",
                        'detail': f"Only {days_of_stock:.1f} days of stock remaining (current: {item.current_stock:.0f} units)",
                        'action': 'Replenish stock urgently'
                    })
        finally:
            session_db.close()
        
        # 6. Purchase Recommendations
        purchase_suggestions = suggest_purchase_order(days_forecast=30)
        high_priority = [p for p in purchase_suggestions if p['priority'] == 'HIGH']
        
        if high_priority:
            recommendations.append({
                'type': 'PURCHASE_NEEDED',
                'message': f"📦 {len(high_priority)} products need urgent replenishment",
                'detail': f"Total order value: R$ {sum(p['order_value'] for p in high_priority):,.2f}",
                'action': 'Review and create purchase orders'
            })
        
        # 7. Explicit Losses
        explicit_losses = get_explicit_losses(days_period=30)
        if explicit_losses:
            total_loss_value = sum(l['loss_value'] for l in explicit_losses)
            warnings.append({
                'type': 'RECORDED_LOSSES',
                'severity': 'MEDIUM',
                'message': f"💔 {len(explicit_losses)} loss events recorded in last 30 days",
                'detail': f"Total value lost: R$ {total_loss_value:,.2f}",
                'action': 'Review security and handling procedures'
            })
        
        # === KEY METRICS ===
        # Stock turnover rate (last 30 days)
        sales_30d = session.query(
            func.sum(SaleOrderItem.quantity * SaleOrderItem.unit_price)
        ).join(
            SaleOrder, SaleOrderItem.sale_order_id == SaleOrder.id
        ).filter(
            and_(
                SaleOrder.sale_date >= (datetime.now() - timedelta(days=30)).date(),
                SaleOrder.status == 'PAID'
            )
        ).scalar() or 0
        
        # Products below minimum stock
        below_min = session.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.current_stock < Product.min_stock,
                Product.min_stock > 0
            )
        ).count()
        
        metrics = {
            'total_products': total_products,
            'products_with_stock': products_with_stock,
            'products_out_of_stock': total_products - products_with_stock,
            'total_stock_value': round(float(total_stock_value), 2),
            'sales_last_30_days': round(float(sales_30d), 2),
            'products_below_min_stock': below_min,
            'stock_ruptures_count': len(ruptures),
            'slow_moving_count': len(slow_moving),
            'purchase_recommendations': len(purchase_suggestions)
        }
        
        # Overall health score (0-100)
        health_score = 100
        health_score -= len(critical_alerts) * 15  # -15 per critical
        health_score -= len(warnings) * 5  # -5 per warning
        health_score = max(0, health_score)
        
        if health_score >= 80:
            health_status = "EXCELLENT"
        elif health_score >= 60:
            health_status = "GOOD"
        elif health_score >= 40:
            health_status = "FAIR"
        else:
            health_status = "POOR"
        
        return {
            'generated_at': datetime.now().isoformat(),
            'health_score': health_score,
            'health_status': health_status,
            'summary': {
                'total_products': total_products,
                'products_with_stock': products_with_stock,
                'total_stock_value': round(float(total_stock_value), 2),
                'alerts_count': len(critical_alerts) + len(warnings)
            },
            'critical_alerts': critical_alerts,
            'warnings': warnings,
            'recommendations': recommendations,
            'metrics': metrics
        }
        
    finally:
        session.close()
