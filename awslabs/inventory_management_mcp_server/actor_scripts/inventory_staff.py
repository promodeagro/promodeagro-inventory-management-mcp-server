# inventory_staff.py
import boto3
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional
from auth_manager import AuthManager


class InventoryStaff:
    """Inventory Staff Operations for Inventory Management System"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth = auth_manager
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.batches_table = self.dynamodb.Table('InventoryManagement-Batches')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        self.order_items_table = self.dynamodb.Table('InventoryManagement-OrderItems')
        self.deliveries_table = self.dynamodb.Table('InventoryManagement-Deliveries')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"📦 {title}")
        print("=" * 60)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
        
    def show_menu(self):
        """Show Inventory Staff main menu"""
        while True:
            self.print_header("INVENTORY STAFF DASHBOARD")
            user_info = self.auth.get_current_user_info()
            print(f"👤 User: {user_info.get('name', 'Unknown')}")
            print(f"📦 Role: {user_info.get('role', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}")
            
            print("\n📋 Available Operations:")
            print("1. 📥 Stock Receiving")
            print("2. 📦 Stock Movement")
            print("3. 📋 Order Fulfillment")
            print("4. 🔢 Inventory Counting")
            print("5. 📝 Stock Adjustment Recording")
            print("6. 🏷️ Labeling and Tagging")
            print("7. 📊 Daily Reports")
            print("8. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-8): ").strip()
            
            if choice == '1':
                self.stock_receiving_menu()
            elif choice == '2':
                self.stock_movement_menu()
            elif choice == '3':
                self.order_fulfillment_menu()
            elif choice == '4':
                self.inventory_counting_menu()
            elif choice == '5':
                self.stock_adjustment_menu()
            elif choice == '6':
                self.labeling_tagging_menu()
            elif choice == '7':
                self.daily_reports_menu()
            elif choice == '8':
                self.auth.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Inventory Staff system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def stock_receiving_menu(self):
        """Stock Receiving Operations"""
        while True:
            self.print_header("STOCK RECEIVING")
            print("1. 📥 Scan Incoming Products")
            print("2. 📊 Record Quantity and Quality")
            print("3. 📍 Update Stock Locations")
            print("4. ✅ Confirm Receipt")
            print("5. 📋 View Receiving Schedule")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.scan_incoming_products()
            elif choice == '2':
                self.record_quantity_quality()
            elif choice == '3':
                self.update_stock_locations()
            elif choice == '4':
                self.confirm_receipt()
            elif choice == '5':
                self.view_receiving_schedule()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def scan_incoming_products(self):
        """Scan incoming products"""
        self.print_header("SCAN INCOMING PRODUCTS")
        
        try:
            # Get products for scanning
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found for scanning.")
                return
                
            print("📦 Available Products for Receiving:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product to scan (or enter product ID): ").strip()
            
            # Try to find product by ID first
            selected_product = None
            for product in products:
                if product.get('productId') == product_choice:
                    selected_product = product
                    break
                    
            # If not found by ID, try by number
            if not selected_product and product_choice.isdigit():
                try:
                    product_index = int(product_choice) - 1
                    if 0 <= product_index < len(products):
                        selected_product = products[product_index]
                except ValueError:
                    pass
                    
            if selected_product:
                product_id = selected_product['productId']
                product_name = selected_product.get('name', 'N/A')
                
                print(f"\n📦 Selected: {product_name}")
                print(f"🆔 Product ID: {product_id}")
                
                # Get batch information
                batch_response = self.batches_table.query(
                    KeyConditionExpression='productId = :product_id',
                    ExpressionAttributeValues={':product_id': product_id}
                )
                batches = batch_response.get('Items', [])
                
                if batches:
                    print("\n📦 Available Batches:")
                    for batch in batches:
                        print(f"   • {batch.get('batchNumber', 'N/A')} - Qty: {batch.get('currentQuantity', 0)}")
                        
                # Record receiving details
                quantity = input("📊 Enter received quantity: ").strip()
                quality_status = input("🧪 Quality status (GOOD/DAMAGED/EXPIRED): ").strip().upper()
                location = input("📍 Storage location: ").strip()
                
                if quantity.isdigit() and quality_status in ['GOOD', 'DAMAGED', 'EXPIRED']:
                    # Update stock levels
                    self.update_stock_level(product_id, location, int(quantity), quality_status)
                    
                    # Log audit
                    self.log_audit('STOCK_RECEIVING', product_id, 
                                 f"Received {quantity} units of {product_name} with quality {quality_status}")
                    
                    self.print_success(f"Successfully recorded receipt of {quantity} units of {product_name}")
                else:
                    self.print_error("Invalid quantity or quality status.")
            else:
                self.print_error("Product not found.")
                
        except Exception as e:
            self.print_error(f"Error scanning incoming products: {str(e)}")
            
    def update_stock_level(self, product_id: str, location: str, quantity: int, quality_status: str):
        """Update stock level for received items"""
        try:
            # Check if stock level record exists
            response = self.stock_levels_table.get_item(
                Key={'productId': product_id, 'location': location}
            )
            
            if 'Item' in response:
                # Update existing record
                current_item = response['Item']
                total_stock = current_item.get('totalStock', 0)
                available_stock = current_item.get('availableStock', 0)
                damaged_stock = current_item.get('damagedStock', 0)
                
                if quality_status == 'GOOD':
                    available_stock += quantity
                elif quality_status == 'DAMAGED':
                    damaged_stock += quantity
                    
                total_stock += quantity
                
                self.stock_levels_table.update_item(
                    Key={'productId': product_id, 'location': location},
                    UpdateExpression='SET totalStock = :total, availableStock = :available, damagedStock = :damaged, lastUpdated = :updated',
                    ExpressionAttributeValues={
                        ':total': total_stock,
                        ':available': available_stock,
                        ':damaged': damaged_stock,
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
            else:
                # Create new record
                stock_item = {
                    'productId': product_id,
                    'location': location,
                    'totalStock': quantity,
                    'availableStock': quantity if quality_status == 'GOOD' else 0,
                    'reservedStock': 0,
                    'damagedStock': quantity if quality_status == 'DAMAGED' else 0,
                    'expiredStock': quantity if quality_status == 'EXPIRED' else 0,
                    'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                self.stock_levels_table.put_item(Item=stock_item)
                
        except Exception as e:
            self.print_error(f"Error updating stock level: {str(e)}")
            
    def stock_movement_menu(self):
        """Stock Movement Operations"""
        while True:
            self.print_header("STOCK MOVEMENT")
            print("1. 📦 Pick Products for Orders")
            print("2. 🔄 Transfer Stock Between Locations")
            print("3. 🔢 Perform Cycle Counts")
            print("4. 📍 Update Stock Locations")
            print("5. 📊 Movement History")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.pick_products_for_orders()
            elif choice == '2':
                self.transfer_stock_between_locations()
            elif choice == '3':
                self.perform_cycle_counts()
            elif choice == '4':
                self.update_stock_locations()
            elif choice == '5':
                self.movement_history()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def pick_products_for_orders(self):
        """Pick products for orders"""
        self.print_header("PICK PRODUCTS FOR ORDERS")
        
        try:
            # Get pending orders
            response = self.orders_table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'PENDING'}
            )
            orders = response.get('Items', [])
            
            if not orders:
                self.print_info("No pending orders found.")
                return
                
            print("📋 Pending Orders:")
            for i, order in enumerate(orders, 1):
                print(f"{i}. Order {order.get('orderId', 'N/A')} - {order.get('customerName', 'N/A')}")
                
            order_choice = input("\n🎯 Select order to pick (or enter order ID): ").strip()
            
            selected_order = None
            for order in orders:
                if order.get('orderId') == order_choice:
                    selected_order = order
                    break
                    
            if not selected_order and order_choice.isdigit():
                try:
                    order_index = int(order_choice) - 1
                    if 0 <= order_index < len(orders):
                        selected_order = orders[order_index]
                except ValueError:
                    pass
                    
            if selected_order:
                order_id = selected_order['orderId']
                customer_name = selected_order.get('customerName', 'N/A')
                
                print(f"\n📋 Selected Order: {order_id}")
                print(f"👤 Customer: {customer_name}")
                
                # Get order items
                items_response = self.order_items_table.query(
                    KeyConditionExpression='orderId = :order_id',
                    ExpressionAttributeValues={':order_id': order_id}
                )
                order_items = items_response.get('Items', [])
                
                if order_items:
                    print("\n📦 Order Items to Pick:")
                    for item in order_items:
                        product_id = item.get('productId', 'N/A')
                        quantity = item.get('quantity', 0)
                        print(f"   • {product_id} - Qty: {quantity}")
                        
                    # Confirm picking
                    confirm = input("\n✅ Confirm picking all items? (y/n): ").strip().lower()
                    if confirm == 'y':
                        # Update stock levels (reserve items)
                        for item in order_items:
                            product_id = item.get('productId')
                            quantity = item.get('quantity', 0)
                            self.reserve_stock_for_order(product_id, quantity)
                            
                        # Update order status
                        self.orders_table.update_item(
                            Key={'orderId': order_id, 'customerId': selected_order['customerId']},
                            UpdateExpression='SET #status = :status, updatedAt = :updated',
                            ExpressionAttributeNames={'#status': 'status'},
                            ExpressionAttributeValues={
                                ':status': 'PICKED',
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                        # Log audit
                        self.log_audit('ORDER_PICKING', order_id, f"Picked order for {customer_name}")
                        
                        self.print_success(f"Successfully picked order {order_id}")
                    else:
                        self.print_info("Picking cancelled.")
                else:
                    self.print_info("No items found for this order.")
            else:
                self.print_error("Order not found.")
                
        except Exception as e:
            self.print_error(f"Error picking products: {str(e)}")
            
    def reserve_stock_for_order(self, product_id: str, quantity: int):
        """Reserve stock for order"""
        try:
            # Get stock levels for this product
            response = self.stock_levels_table.query(
                KeyConditionExpression='productId = :product_id',
                ExpressionAttributeValues={':product_id': product_id}
            )
            stock_items = response.get('Items', [])
            
            for stock_item in stock_items:
                available = stock_item.get('availableStock', 0)
                reserved = stock_item.get('reservedStock', 0)
                
                if available >= quantity:
                    # Update stock levels
                    self.stock_levels_table.update_item(
                        Key={'productId': product_id, 'location': stock_item['location']},
                        UpdateExpression='SET availableStock = :available, reservedStock = :reserved, lastUpdated = :updated',
                        ExpressionAttributeValues={
                            ':available': available - quantity,
                            ':reserved': reserved + quantity,
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    break
                    
        except Exception as e:
            self.print_error(f"Error reserving stock: {str(e)}")
            
    def order_fulfillment_menu(self):
        """Order Fulfillment Operations"""
        while True:
            self.print_header("ORDER FULFILLMENT")
            print("1. 📦 Pick and Pack Orders")
            print("2. ✅ Verify Order Accuracy")
            print("3. 📦 Prepare for Dispatch")
            print("4. 📋 View Fulfillment Queue")
            print("5. 📊 Fulfillment Performance")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.pick_and_pack_orders()
            elif choice == '2':
                self.verify_order_accuracy()
            elif choice == '3':
                self.prepare_for_dispatch()
            elif choice == '4':
                self.view_fulfillment_queue()
            elif choice == '5':
                self.fulfillment_performance()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def inventory_counting_menu(self):
        """Inventory Counting Operations"""
        while True:
            self.print_header("INVENTORY COUNTING")
            print("1. 🔢 Perform Daily Cycle Counts")
            print("2. 📊 Conduct Periodic Full Counts")
            print("3. 📝 Report Count Variances")
            print("4. 📋 View Counting Schedule")
            print("5. 📈 Counting Accuracy Reports")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.perform_daily_cycle_counts()
            elif choice == '2':
                self.conduct_periodic_full_counts()
            elif choice == '3':
                self.report_count_variances()
            elif choice == '4':
                self.view_counting_schedule()
            elif choice == '5':
                self.counting_accuracy_reports()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def stock_adjustment_menu(self):
        """Stock Adjustment Recording Operations"""
        while True:
            self.print_header("STOCK ADJUSTMENT RECORDING")
            print("1. 📝 Report Damaged Goods")
            print("2. ⚠️ Record Stock Discrepancies")
            print("3. 🗑️ Document Wastage")
            print("4. 📋 View Adjustment Requests")
            print("5. 📊 Adjustment History")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.report_damaged_goods()
            elif choice == '2':
                self.record_stock_discrepancies()
            elif choice == '3':
                self.document_wastage()
            elif choice == '4':
                self.view_adjustment_requests()
            elif choice == '5':
                self.adjustment_history()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def labeling_tagging_menu(self):
        """Labeling and Tagging Operations"""
        while True:
            self.print_header("LABELING AND TAGGING")
            print("1. 🏷️ Print Product Labels")
            print("2. 📦 Apply Batch/Expiry Information")
            print("3. 📍 Tag Storage Locations")
            print("4. 📋 View Labeling Queue")
            print("5. 📊 Labeling Reports")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.print_product_labels()
            elif choice == '2':
                self.apply_batch_expiry_info()
            elif choice == '3':
                self.tag_storage_locations()
            elif choice == '4':
                self.view_labeling_queue()
            elif choice == '5':
                self.labeling_reports()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def daily_reports_menu(self):
        """Daily Reports Operations"""
        while True:
            self.print_header("DAILY REPORTS")
            print("1. 📊 Daily Activity Summary")
            print("2. 📦 Items Processed Today")
            print("3. ⚠️ Issues and Discrepancies")
            print("4. 📈 Performance Metrics")
            print("5. 📋 Task Completion Status")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.daily_activity_summary()
            elif choice == '2':
                self.items_processed_today()
            elif choice == '3':
                self.issues_and_discrepancies()
            elif choice == '4':
                self.performance_metrics()
            elif choice == '5':
                self.task_completion_status()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                
    # Placeholder methods for other operations
    def record_quantity_quality(self):
        self.print_info("Quantity and quality recording functionality will be implemented.")
        
    def update_stock_locations(self):
        self.print_info("Stock location update functionality will be implemented.")
        
    def confirm_receipt(self):
        self.print_info("Receipt confirmation functionality will be implemented.")
        
    def view_receiving_schedule(self):
        self.print_info("Receiving schedule viewing functionality will be implemented.")
        
    def transfer_stock_between_locations(self):
        self.print_info("Stock transfer functionality will be implemented.")
        
    def perform_cycle_counts(self):
        self.print_info("Cycle count functionality will be implemented.")
        
    def movement_history(self):
        self.print_info("Movement history functionality will be implemented.")
        
    def pick_and_pack_orders(self):
        self.print_info("Pick and pack functionality will be implemented.")
        
    def verify_order_accuracy(self):
        self.print_info("Order accuracy verification functionality will be implemented.")
        
    def prepare_for_dispatch(self):
        self.print_info("Dispatch preparation functionality will be implemented.")
        
    def view_fulfillment_queue(self):
        self.print_info("Fulfillment queue viewing functionality will be implemented.")
        
    def fulfillment_performance(self):
        self.print_info("Fulfillment performance functionality will be implemented.")
        
    def perform_daily_cycle_counts(self):
        self.print_info("Daily cycle count functionality will be implemented.")
        
    def conduct_periodic_full_counts(self):
        self.print_info("Periodic full count functionality will be implemented.")
        
    def report_count_variances(self):
        self.print_info("Count variance reporting functionality will be implemented.")
        
    def view_counting_schedule(self):
        self.print_info("Counting schedule viewing functionality will be implemented.")
        
    def counting_accuracy_reports(self):
        self.print_info("Counting accuracy reporting functionality will be implemented.")
        
    def report_damaged_goods(self):
        self.print_info("Damaged goods reporting functionality will be implemented.")
        
    def record_stock_discrepancies(self):
        self.print_info("Stock discrepancy recording functionality will be implemented.")
        
    def document_wastage(self):
        self.print_info("Wastage documentation functionality will be implemented.")
        
    def view_adjustment_requests(self):
        self.print_info("Adjustment request viewing functionality will be implemented.")
        
    def adjustment_history(self):
        self.print_info("Adjustment history functionality will be implemented.")
        
    def print_product_labels(self):
        self.print_info("Product label printing functionality will be implemented.")
        
    def apply_batch_expiry_info(self):
        self.print_info("Batch/expiry information application functionality will be implemented.")
        
    def tag_storage_locations(self):
        self.print_info("Storage location tagging functionality will be implemented.")
        
    def view_labeling_queue(self):
        self.print_info("Labeling queue viewing functionality will be implemented.")
        
    def labeling_reports(self):
        self.print_info("Labeling reporting functionality will be implemented.")
        
    def daily_activity_summary(self):
        self.print_info("Daily activity summary functionality will be implemented.")
        
    def items_processed_today(self):
        self.print_info("Items processed today functionality will be implemented.")
        
    def issues_and_discrepancies(self):
        self.print_info("Issues and discrepancies functionality will be implemented.")
        
    def performance_metrics(self):
        self.print_info("Performance metrics functionality will be implemented.")
        
    def task_completion_status(self):
        self.print_info("Task completion status functionality will be implemented.")
        
    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': self.auth.current_user.get('userId'),
                'action': action,
                'entityId': entity_id,
                'details': details,
                'ipAddress': '127.0.0.1',
                'userAgent': 'InventoryStaff-CLI',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")


if __name__ == '__main__':
    auth = AuthManager()
    if auth.login():
        inventory_staff = InventoryStaff(auth)
        inventory_staff.show_menu()
    else:
        print("❌ Login failed. Exiting.")
        sys.exit(1) 