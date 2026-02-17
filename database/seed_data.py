"""
Fake data generator for Stock Management POC.

This script generates realistic data for 6 months of operations:
- Products (from CSV + generated)
- Suppliers
- Purchase orders
- Sales
- Stock movements

Usage:
    python database/seed_data.py
"""

import random
import csv
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker
from sqlalchemy.orm import Session

from database.connection import SessionLocal, init_db, drop_all_tables
from database.schema import (
    Product, Supplier, PurchaseOrder, PurchaseOrderItem,
    SaleOrder, SaleOrderItem, StockMovement
)

# Initialize Faker with Portuguese locale
fake = Faker('pt_BR')
random.seed(42)  # For reproducibility

# Configuration
NUM_SUPPLIERS = 12
NUM_ADDITIONAL_PRODUCTS = 40  # Products to generate beyond CSV
MONTHS_HISTORY = 6
START_DATE = datetime.now() - timedelta(days=30 * MONTHS_HISTORY)


class DataGenerator:
    """Main data generator class."""
    
    def __init__(self, session: Session):
        self.session = session
        self.suppliers = []
        self.products = []
        self.purchase_orders = []
        self.sale_orders = []
        
    def generate_all(self):
        """Generate all fake data."""
        print("\n" + "=" * 60)
        print("🎲 Generating Fake Data for Stock Management POC")
        print("=" * 60)
        
        print("\n📦 Step 1: Loading products from CSV...")
        self.load_products_from_csv()
        
        print("📦 Step 2: Generating additional products...")
        self.generate_additional_products()
        
        print("🏢 Step 3: Generating suppliers...")
        self.generate_suppliers()
        
        print("🛒 Step 4: Generating purchase orders (6 months)...")
        self.generate_purchase_orders()
        
        print("💰 Step 5: Generating sales (6 months)...")
        self.generate_sales()
        
        print("📊 Step 6: Creating special scenarios...")
        self.create_special_scenarios()
        
        print("\n✅ Data generation completed!")
        self.print_summary()
    
    def load_products_from_csv(self):
        """Load products from stock.csv file."""
        try:
            with open('stock.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse CSV data
                        code = row.get('Código', '').strip()
                        name = row.get('Descrição', '').strip()
                        brand = row.get('Marca', '').strip()
                        category = row.get('Grupo', '').strip() or row.get('Dpto', '').strip()
                        
                        # Parse prices (handle Brazilian number format)
                        sale_price_str = row.get('Pr Venda', '0').replace('.', '').replace(',', '.')
                        cost_price_str = row.get('Pr Compra', '0').replace('.', '').replace(',', '.')
                        stock_str = row.get('Estoque', '0').replace('.', '').replace(',', '.')
                        
                        sale_price = Decimal(sale_price_str) if sale_price_str else Decimal('0')
                        cost_price = Decimal(cost_price_str) if cost_price_str else Decimal('0')
                        current_stock = Decimal(stock_str) if stock_str else Decimal('0')
                        
                        # Skip if essential data is missing
                        if not name or sale_price <= 0:
                            continue
                        
                        product = Product(
                            sku=f"SKU{code.zfill(6)}",
                            gtin=row.get('Código NCM', ''),
                            name=name[:255],
                            category=category[:100] if category else 'Geral',
                            brand=brand[:100] if brand else 'Genérico',
                            sale_price=sale_price,
                            cost_price=cost_price if cost_price > 0 else sale_price * Decimal('0.6'),
                            current_stock=Decimal('0'),  # Will be set by stock movements
                            min_stock=Decimal('5'),
                            is_active=True
                        )
                        
                        self.session.add(product)
                        self.products.append(product)
                        
                    except Exception as e:
                        print(f"   ⚠️  Error parsing row: {e}")
                        continue
                
                self.session.commit()
                print(f"   ✅ Loaded {len(self.products)} products from CSV")
                
        except FileNotFoundError:
            print("   ⚠️  stock.csv not found, will generate all products")
        except Exception as e:
            print(f"   ⚠️  Error reading CSV: {e}")
    
    def generate_additional_products(self):
        """Generate additional products to reach target."""
        categories = [
            'Alimentos', 'Bebidas', 'Limpeza', 'Higiene', 'Mercearia',
            'Frios e Laticínios', 'Carnes', 'Hortifruti', 'Padaria', 'Congelados'
        ]
        
        brands = [
            'Nestlé', 'Coca-Cola', 'Sadia', 'Perdigão', 'Kibon',
            'Omo', 'Dove', 'Colgate', 'Johnson', 'Pão de Açúcar'
        ]
        
        product_templates = [
            'Arroz Tipo 1 {}kg', 'Feijão Preto {}kg', 'Óleo de Soja {}L',
            'Açúcar Cristal {}kg', 'Café Torrado {}g', 'Leite Integral {}L',
            'Macarrão {}g', 'Refrigerante {}L', 'Sabão em Pó {}kg',
            'Papel Higiênico {} Rolos', 'Sabonete {}g', 'Shampoo {}ml',
            'Detergente {}ml', 'Água Sanitária {}L', 'Biscoito {}g'
        ]
        
        current_count = len(self.products)
        target = NUM_ADDITIONAL_PRODUCTS
        
        for i in range(target):
            template = random.choice(product_templates)
            size = random.choice(['500', '1', '2', '5', '200', '300'])
            name = template.format(size)
            
            cost = Decimal(random.uniform(2, 50)).quantize(Decimal('0.01'))
            margin = Decimal(random.uniform(1.3, 2.5))
            
            product = Product(
                sku=f"SKU{str(current_count + i + 1).zfill(6)}",
                gtin=fake.ean13(),
                name=f"{name} {random.choice(brands)}",
                category=random.choice(categories),
                brand=random.choice(brands),
                sale_price=(cost * margin).quantize(Decimal('0.01')),
                cost_price=cost,
                current_stock=Decimal('0'),
                min_stock=Decimal(random.randint(5, 20)),
                is_active=True
            )
            
            self.session.add(product)
            self.products.append(product)
        
        self.session.commit()
        print(f"   ✅ Generated {target} additional products")
    
    def generate_suppliers(self):
        """Generate suppliers."""
        supplier_names = [
            'Distribuidora Alimentos Ltda', 'Comercial Bebidas S.A.',
            'Atacadão Produtos Ltda', 'Fornecedor Geral EIRELI',
            'Distribuição Nacional S.A.', 'Mega Distribuidora Ltda',
            'Produtos Regionais Ltda', 'Importadora Alimentos S.A.',
            'Atacado Varejo Ltda', 'Distribuição Express EIRELI',
            'Fornecedor Premium Ltda', 'Comercial Atacado S.A.'
        ]
        
        for name in supplier_names[:NUM_SUPPLIERS]:
            supplier = Supplier(
                name=name,
                tax_id=fake.cnpj(),
                email=fake.company_email(),
                phone=fake.phone_number(),
                address=fake.street_address(),
                city=fake.city(),
                state=fake.estado_sigla(),
                is_active=True
            )
            
            self.session.add(supplier)
            self.suppliers.append(supplier)
        
        self.session.commit()
        print(f"   ✅ Generated {len(self.suppliers)} suppliers")
    
    def generate_purchase_orders(self):
        """Generate purchase orders over 6 months."""
        num_orders = 120
        current_date = START_DATE
        
        for i in range(num_orders):
            # Distribute orders over time
            days_offset = (MONTHS_HISTORY * 30 * i) // num_orders
            order_date = START_DATE + timedelta(days=days_offset)
            
            supplier = random.choice(self.suppliers)
            
            # Create order
            order = PurchaseOrder(
                order_number=f"PO{str(i+1).zfill(6)}",
                supplier_id=supplier.id,
                order_date=order_date.date(),
                received_date=(order_date + timedelta(days=random.randint(1, 7))).date(),
                status='RECEIVED',
                total_amount=Decimal('0')
            )
            
            self.session.add(order)
            self.session.flush()
            
            # Add items (3-8 products per order)
            num_items = random.randint(3, 8)
            selected_products = random.sample(self.products, min(num_items, len(self.products)))
            
            total = Decimal('0')
            for product in selected_products:
                quantity = Decimal(random.randint(10, 100))
                unit_price = product.cost_price
                
                item = PurchaseOrderItem(
                    purchase_order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                self.session.add(item)
                total += quantity * unit_price
                
                # Create stock movement (PURCHASE)
                stock_before = product.current_stock
                stock_after = stock_before + quantity
                
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='PURCHASE',
                    reference_id=order.id,
                    quantity=quantity,
                    unit_cost=unit_price,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    movement_date=order_date
                )
                
                self.session.add(movement)
                product.current_stock = stock_after
            
            order.total_amount = total
            self.purchase_orders.append(order)
        
        self.session.commit()
        print(f"   ✅ Generated {len(self.purchase_orders)} purchase orders")
    
    def generate_sales(self):
        """Generate sales following realistic patterns."""
        # 80/20 rule: 20% of products generate 80% of sales
        high_demand_products = random.sample(self.products, len(self.products) // 5)
        
        num_sales = 800
        current_date = START_DATE
        
        sales_created = 0
        for i in range(num_sales):
            # Distribute sales over time
            days_offset = (MONTHS_HISTORY * 30 * i) // num_sales
            sale_date = START_DATE + timedelta(days=days_offset)
            
            # Skip if weekend (lower sales)
            if sale_date.weekday() >= 5 and random.random() < 0.4:
                continue
            
            # Create sale
            sale = SaleOrder(
                order_number=f"SO{str(i+1).zfill(6)}",
                sale_date=sale_date.date(),
                status='PAID',
                total_amount=Decimal('0')
            )
            
            self.session.add(sale)
            self.session.flush()
            
            # Add items (1-5 products per sale)
            num_items = random.randint(1, 5)
            
            # 80% chance of high-demand products
            if random.random() < 0.8:
                pool = high_demand_products
            else:
                pool = self.products
            
            # Filter products with stock
            available_products = [p for p in pool if p.current_stock > 0]
            if not available_products:
                continue
            
            selected_products = random.sample(
                available_products,
                min(num_items, len(available_products))
            )
            
            total = Decimal('0')
            for product in selected_products:
                # Quantity between 1-5, but not more than available
                max_qty = min(5, float(product.current_stock))
                if max_qty < 1:
                    continue
                
                quantity = Decimal(random.randint(1, int(max_qty)))
                unit_price = product.sale_price
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                self.session.add(item)
                total += quantity * unit_price
                
                # Create stock movement (SALE)
                stock_before = product.current_stock
                stock_after = stock_before - quantity
                
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='SALE',
                    reference_id=sale.id,
                    quantity=-quantity,  # Negative for outbound
                    unit_cost=product.cost_price,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    movement_date=sale_date
                )
                
                self.session.add(movement)
                product.current_stock = stock_after
            
            if total > 0:
                sale.total_amount = total
                self.sale_orders.append(sale)
                sales_created += 1
        
        self.session.commit()
        print(f"   ✅ Generated {sales_created} sales")
    
    def create_special_scenarios(self):
        """Create special scenarios for testing AI agent."""
        
        # Scenario 1: Stock rupture (products with 0 stock but recent sales)
        products_to_rupture = random.sample(self.products, 5)
        for product in products_to_rupture:
            if product.current_stock > 0:
                # Create adjustment to zero out stock
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='SALE',
                    quantity=-product.current_stock,
                    stock_before=product.current_stock,
                    stock_after=Decimal('0'),
                    movement_date=datetime.now() - timedelta(days=3),
                    notes='Scenario: Stock rupture'
                )
                self.session.add(movement)
                product.current_stock = Decimal('0')
        
        # Scenario 2: Slow-moving products (no sales in 60+ days)
        products_to_slow = random.sample(self.products, 8)
        old_date = datetime.now() - timedelta(days=90)
        for product in products_to_slow:
            if product.current_stock < 50:
                # Add old stock
                quantity = Decimal(random.randint(30, 80))
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='PURCHASE',
                    quantity=quantity,
                    stock_before=product.current_stock,
                    stock_after=product.current_stock + quantity,
                    movement_date=old_date,
                    notes='Scenario: Slow-moving stock'
                )
                self.session.add(movement)
                product.current_stock += quantity
        
        # Scenario 3: Simulated loss (divergence)
        products_with_loss = random.sample(self.products, 3)
        for product in products_with_loss:
            if product.current_stock > 10:
                loss_qty = Decimal(random.randint(5, 15))
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='LOSS',
                    quantity=-loss_qty,
                    stock_before=product.current_stock,
                    stock_after=product.current_stock - loss_qty,
                    movement_date=datetime.now() - timedelta(days=random.randint(1, 20)),
                    notes='Scenario: Simulated loss/theft'
                )
                self.session.add(movement)
                product.current_stock -= loss_qty
        
        # Scenario 4: Imminent stockout risk (NEW - 2026-02-08)
        # Products with low stock, high demand, and no/insufficient purchase orders
        print("   🎯 Creating imminent stockout risk scenarios...")
        
        # 4A: Products at risk WITHOUT any purchase order (CRITICAL)
        at_risk_no_po = random.sample(self.products, 6)
        for i, product in enumerate(at_risk_no_po):
            # Set low stock (will run out in 2-5 days)
            low_stock = Decimal(random.randint(8, 25))
            product.current_stock = low_stock
            
            # Create recent high-demand sales (5-10 units/day)
            daily_demand = random.randint(5, 10)
            for days_ago in range(1, 15):  # Last 14 days of sales
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'RISK-NO-PO-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                # Vary quantity around daily demand
                quantity = Decimal(random.randint(daily_demand - 2, daily_demand + 2))
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # NO purchase order created (this is the critical scenario)
            print(f"      🔴 {product.name}: {low_stock} units, ~{daily_demand} units/day demand, NO PO")
        
        # 4B: Products at risk WITH insufficient purchase order (HIGH RISK)
        at_risk_insufficient_po = random.sample(
            [p for p in self.products if p not in at_risk_no_po], 4
        )
        for i, product in enumerate(at_risk_insufficient_po):
            # Set very low stock (will run out in 1-3 days)
            low_stock = Decimal(random.randint(5, 15))
            product.current_stock = low_stock
            
            # Create recent sales showing high demand
            daily_demand = random.randint(4, 8)
            for days_ago in range(1, 10):
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'RISK-INSUF-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                quantity = Decimal(random.randint(daily_demand - 1, daily_demand + 1))
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # Create INSUFFICIENT purchase order (only covers 10 days instead of 30)
            if self.suppliers:
                supplier = random.choice(self.suppliers)
                po_date = datetime.now() - timedelta(days=2)
                
                # Insufficient quantity (only 40-60 units for 30-day demand of 120-240)
                insufficient_qty = Decimal(random.randint(40, 60))
                
                po = PurchaseOrder(
                    order_number=f'PO-INSUF-{i}-{random.randint(1000, 9999)}',
                    supplier_id=supplier.id,
                    order_date=po_date.date(),
                    total_amount=insufficient_qty * product.cost_price,
                    status='PENDING'  # Still pending
                )
                self.session.add(po)
                self.session.flush()
                
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=product.id,
                    quantity=insufficient_qty,
                    unit_price=product.cost_price
                )
                self.session.add(po_item)
                
                print(f"      🟠 {product.name}: {low_stock} units, ~{daily_demand} units/day, PO: {insufficient_qty} units (INSUFFICIENT)")
        
        # 4C: Products at risk WITH delayed purchase order (HIGH RISK)
        at_risk_delayed_po = random.sample(
            [p for p in self.products if p not in at_risk_no_po and p not in at_risk_insufficient_po], 3
        )
        for i, product in enumerate(at_risk_delayed_po):
            # Set low stock
            low_stock = Decimal(random.randint(10, 20))
            product.current_stock = low_stock
            
            # Create recent sales
            daily_demand = random.randint(3, 6)
            for days_ago in range(1, 12):
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'RISK-DELAY-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                quantity = Decimal(random.randint(daily_demand - 1, daily_demand + 1))
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # Create DELAYED purchase order (placed 10-15 days ago, still pending)
            if self.suppliers:
                supplier = random.choice(self.suppliers)
                po_date = datetime.now() - timedelta(days=random.randint(10, 15))  # OLD!
                
                # Sufficient quantity but DELAYED
                sufficient_qty = Decimal(random.randint(80, 120))
                
                po = PurchaseOrder(
                    order_number=f'PO-DELAY-{i}-{random.randint(1000, 9999)}',
                    supplier_id=supplier.id,
                    order_date=po_date.date(),
                    total_amount=sufficient_qty * product.cost_price,
                    status='PENDING'  # STILL PENDING after 10-15 days!
                )
                self.session.add(po)
                self.session.flush()
                
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=product.id,
                    quantity=sufficient_qty,
                    unit_price=product.cost_price
                )
                self.session.add(po_item)
                
                days_delayed = (datetime.now().date() - po_date.date()).days
                print(f"      ⏰ {product.name}: {low_stock} units, ~{daily_demand} units/day, PO: {sufficient_qty} units (DELAYED {days_delayed} days)")
        
        # 4D: Products at risk but WITH sufficient purchase order (LOW RISK - for comparison)
        at_risk_ok_po = random.sample(
            [p for p in self.products 
             if p not in at_risk_no_po 
             and p not in at_risk_insufficient_po 
             and p not in at_risk_delayed_po], 2
        )
        for i, product in enumerate(at_risk_ok_po):
            # Set lowish stock
            low_stock = Decimal(random.randint(15, 30))
            product.current_stock = low_stock
            
            # Create recent sales
            daily_demand = random.randint(3, 5)
            for days_ago in range(1, 10):
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'RISK-OK-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                quantity = Decimal(random.randint(daily_demand - 1, daily_demand + 1))
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # Create SUFFICIENT and RECENT purchase order (GOOD scenario for comparison)
            if self.suppliers:
                supplier = random.choice(self.suppliers)
                po_date = datetime.now() - timedelta(days=random.randint(1, 3))  # Recent
                
                # Sufficient quantity for 30+ days
                sufficient_qty = Decimal(random.randint(120, 180))
                
                po = PurchaseOrder(
                    order_number=f'PO-OK-{i}-{random.randint(1000, 9999)}',
                    supplier_id=supplier.id,
                    order_date=po_date.date(),
                    total_amount=sufficient_qty * product.cost_price,
                    status='PENDING'
                )
                self.session.add(po)
                self.session.flush()
                
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=product.id,
                    quantity=sufficient_qty,
                    unit_price=product.cost_price
                )
                self.session.add(po_item)
                
                print(f"      ✅ {product.name}: {low_stock} units, ~{daily_demand} units/day, PO: {sufficient_qty} units (OK)")
        
        # Scenario 5: Operational Availability Issues (NEW - 2026-02-08)
        # Products received, have stock, but NOT selling (operational problem)
        print("   🏪 Creating operational availability issue scenarios...")
        
        # 5A: Products with good sales history but sudden drop after receiving new stock
        operational_issues = random.sample(
            [p for p in self.products 
             if p not in at_risk_no_po 
             and p not in at_risk_insufficient_po 
             and p not in at_risk_delayed_po
             and p not in at_risk_ok_po], 5
        )
        
        for i, product in enumerate(operational_issues):
            # Step 1: Create GOOD sales history (30-60 days ago)
            daily_demand = random.randint(4, 8)
            for days_ago in range(60, 15, -1):  # 60 days ago to 15 days ago
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'OP-GOOD-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                quantity = Decimal(random.randint(daily_demand - 1, daily_demand + 1))
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # Step 2: Product received purchase order 14 days ago (RECEIVED)
            if self.suppliers:
                supplier = random.choice(self.suppliers)
                po_date = datetime.now() - timedelta(days=14)
                received_date = datetime.now() - timedelta(days=12)  # Received 2 days later
                
                received_qty = Decimal(random.randint(100, 200))
                
                po = PurchaseOrder(
                    order_number=f'PO-RECEIVED-{i}-{random.randint(1000, 9999)}',
                    supplier_id=supplier.id,
                    order_date=po_date.date(),
                    received_date=received_date.date(),
                    total_amount=received_qty * product.cost_price,
                    status='RECEIVED'  # KEY: Already received!
                )
                self.session.add(po)
                self.session.flush()
                
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=product.id,
                    quantity=received_qty,
                    unit_price=product.cost_price
                )
                self.session.add(po_item)
                
                # Add stock movement for receipt
                stock_before = product.current_stock
                stock_after = stock_before + received_qty
                
                movement = StockMovement(
                    product_id=product.id,
                    movement_type='PURCHASE',
                    reference_id=po.id,
                    quantity=received_qty,
                    unit_cost=product.cost_price,
                    stock_before=stock_before,
                    stock_after=stock_after,
                    movement_date=received_date,
                    notes='PO received - added to depot'
                )
                self.session.add(movement)
                product.current_stock = stock_after
            
            # Step 3: NO SALES or very few sales in last 12 days (after receipt!)
            # This indicates product is in depot but not available for sale
            # Simulate only 1-2 sales in 12 days (vs expected ~60 sales)
            rare_sales = random.randint(1, 2)
            for _ in range(rare_sales):
                days_ago = random.randint(1, 12)
                sale_date = datetime.now() - timedelta(days=days_ago)
                
                sale = SaleOrder(
                    order_number=f'OP-RARE-{i}-{days_ago}-{random.randint(1000, 9999)}',
                    sale_date=sale_date.date(),
                    total_amount=Decimal('0'),
                    status='PAID'
                )
                self.session.add(sale)
                self.session.flush()
                
                quantity = Decimal(random.randint(1, 2))  # Very low
                
                item = SaleOrderItem(
                    sale_order_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.sale_price
                )
                self.session.add(item)
                sale.total_amount = quantity * product.sale_price
            
            # Ensure product has good stock level
            if product.current_stock < 80:
                product.current_stock = Decimal(random.randint(100, 150))
            
            expected_sales = daily_demand * 12
            actual_sales = rare_sales
            lost_sales = expected_sales - actual_sales
            
            print(f"      🏪 {product.name}: Stock={product.current_stock:.0f}, "
                  f"Historical={daily_demand} un/day, "
                  f"Recent={rare_sales} sales in 12d (expected {expected_sales}), "
                  f"Lost {lost_sales} sales! (Operational issue)")
        
        self.session.commit()
        print(f"   ✅ Created special test scenarios (including 20 total scenarios)")
    
    def print_summary(self):
        """Print summary of generated data."""
        total_stock_value = sum(
            float(p.current_stock * p.cost_price) for p in self.products
        )
        
        print("\n" + "=" * 60)
        print("📊 DATA SUMMARY")
        print("=" * 60)
        print(f"Products: {len(self.products)}")
        print(f"Suppliers: {len(self.suppliers)}")
        print(f"Purchase Orders: {len(self.purchase_orders)}")
        print(f"Sales: {len(self.sale_orders)}")
        print(f"Total Stock Value: R$ {total_stock_value:,.2f}")
        print(f"Period: {START_DATE.date()} to {datetime.now().date()}")
        print("=" * 60)


def main():
    """Main execution function."""
    print("\n🎯 Starting data generation process...")
    
    # Initialize database first
    print("\n📁 Initializing database...")
    init_db()
    
    # Ask if user wants to clean existing data
    response = input("\n⚠️  Do you want to clean existing data first? [yes/no]: ").strip().lower()
    if response == 'yes':
        drop_all_tables()
        init_db()
        print("✅ Database cleaned and recreated")
    
    # Generate data
    session = SessionLocal()
    try:
        generator = DataGenerator(session)
        generator.generate_all()
    except Exception as e:
        print(f"\n❌ Error during data generation: {e}")
        session.rollback()
        raise
    finally:
        session.close()
    
    print("\n🎉 Data generation completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Verify data: python -c 'from database.connection import SessionLocal; from database.schema import Product; print(SessionLocal().query(Product).count(), \"products\")'")
    print("   2. Start building AI tools: Create tools/stock_analysis.py")
    print()


if __name__ == "__main__":
    main()
