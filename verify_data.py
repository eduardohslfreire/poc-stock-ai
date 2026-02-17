"""
Quick verification script to check database contents.

Usage:
    python verify_data.py
"""

from database.connection import SessionLocal
from database.schema import (
    Product, Supplier, PurchaseOrder, SaleOrder, StockMovement
)
from sqlalchemy import func

def main():
    session = SessionLocal()
    
    print("\n" + "=" * 60)
    print("🔍 DATABASE VERIFICATION")
    print("=" * 60)
    
    # Count records
    products_count = session.query(Product).count()
    suppliers_count = session.query(Supplier).count()
    purchases_count = session.query(PurchaseOrder).count()
    sales_count = session.query(SaleOrder).count()
    movements_count = session.query(StockMovement).count()
    
    print(f"\n📊 Record Counts:")
    print(f"   Products: {products_count}")
    print(f"   Suppliers: {suppliers_count}")
    print(f"   Purchase Orders: {purchases_count}")
    print(f"   Sales: {sales_count}")
    print(f"   Stock Movements: {movements_count}")
    
    # Sample data
    print(f"\n📦 Sample Products:")
    for product in session.query(Product).limit(5).all():
        print(f"   - {product.sku}: {product.name} (Stock: {product.current_stock})")
    
    print(f"\n🏢 Sample Suppliers:")
    for supplier in session.query(Supplier).limit(3).all():
        print(f"   - {supplier.name} ({supplier.tax_id})")
    
    # Stock statistics
    total_stock_value = session.query(
        func.sum(Product.current_stock * Product.cost_price)
    ).scalar() or 0
    
    products_with_stock = session.query(Product).filter(Product.current_stock > 0).count()
    products_without_stock = session.query(Product).filter(Product.current_stock == 0).count()
    
    print(f"\n💰 Stock Statistics:")
    print(f"   Total Stock Value: R$ {float(total_stock_value):,.2f}")
    print(f"   Products with Stock: {products_with_stock}")
    print(f"   Products without Stock: {products_without_stock}")
    
    # Recent activity
    recent_sales = session.query(SaleOrder).order_by(
        SaleOrder.sale_date.desc()
    ).limit(3).all()
    
    print(f"\n🛒 Recent Sales:")
    for sale in recent_sales:
        print(f"   - {sale.order_number}: R$ {sale.total_amount} ({sale.sale_date})")
    
    print("\n" + "=" * 60)
    print("✅ Verification completed!")
    print("=" * 60 + "\n")
    
    session.close()

if __name__ == "__main__":
    main()
