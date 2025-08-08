#!/usr/bin/env python3
# inventory_staff_standalone.py
"""
Inventory Staff Standalone Script
Run this script in a separate terminal window for Inventory Staff operations.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional


class InventoryStaffStandalone:
    """Standalone Inventory Staff with Front-line Operations"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.batches_table = self.dynamodb.Table('InventoryManagement-Batches')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders') # Added orders_table
        
        self.current_user = None
        self.current_role = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"📦 {title}")
        print("=" * 80)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
        
    def test_aws_connection(self) -> bool:
        """Test AWS connection and credentials"""
        try:
            sts = boto3.client('sts', region_name=self.region_name)
            identity = sts.get_caller_identity()
            print(f"🔐 AWS Identity: {identity['Arn']}")
            print(f"🏢 AWS Account: {identity['Account']}")
            print(f"🌍 AWS Region: {self.region_name}")
            return True
        except Exception as e:
            self.print_error(f"AWS connection failed: {str(e)}")
            return False
            
    def authenticate_user(self) -> bool:
        """Authenticate user login"""
        self.clear_screen()
        self.print_header("INVENTORY STAFF - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your credentials:")
        print("💡 Demo credentials: inventory_staff / inventory123")
        
        username = input("\n👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'INVENTORY_STAFF':
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            return False
            
    def authenticate_user_db(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against DynamoDB Users table"""
        try:
            response = self.users_table.query(
                KeyConditionExpression='userId = :username',
                FilterExpression='isActive = :active',
                ExpressionAttributeValues={
                    ':username': username,
                    ':active': True
                }
            )
            
            if response['Items']:
                user = response['Items'][0]
                if self.verify_password(password, user.get('password', '')):
                    return user
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simplified for demo)"""
        return input_password == stored_password
        
    def create_demo_user(self):
        """Create demo inventory staff user if not exists"""
        try:
            demo_user = {
                'userId': 'inventory_staff',
                'role': 'INVENTORY_STAFF',
                'name': 'Priya Sharma',
                'email': 'priya@company.com',
                'phone': '+919876543212',
                'password': 'inventory123',
                'permissions': [
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'STOCK_MOVEMENT',
                    'ORDER_FULFILLMENT', 'INVENTORY_COUNTING'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            response = self.users_table.get_item(
                Key={'userId': 'inventory_staff', 'role': 'INVENTORY_STAFF'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Inventory Staff user created!")
                self.print_info("Username: inventory_staff")
                self.print_info("Password: inventory123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Inventory Staff main menu"""
        while True:
            self.clear_screen()
            self.print_header("INVENTORY STAFF DASHBOARD")
            
            if self.current_user:
                print(f"👤 User: {self.current_user.get('name', 'Unknown')}")
                print(f"📦 Role: {self.current_user.get('role', 'Unknown')}")
                print(f"📅 Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📋 Available Operations:")
            print("1. 📥 Stock Receiving")
            print("2. 📦 Stock Movement")
            print("3. 📋 Order Fulfillment")
            print("4. 🔢 Inventory Counting")
            print("5. 🏷️ Labeling & Tagging")
            print("6. 📊 Stock Adjustments")
            print("7. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-7): ").strip()
            
            if choice == '1':
                self.stock_receiving_menu()
            elif choice == '2':
                self.stock_movement_menu()
            elif choice == '3':
                self.order_fulfillment_menu()
            elif choice == '4':
                self.inventory_counting_menu()
            elif choice == '5':
                self.labeling_tagging_menu()
            elif choice == '6':
                self.stock_adjustments_menu()
            elif choice == '7':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Inventory Staff system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def stock_receiving_menu(self):
        """Stock Receiving Operations"""
        while True:
            self.clear_screen()
            self.print_header("STOCK RECEIVING")
            print("1. 📥 Scan Incoming Products")
            print("2. 📊 Record Quantity & Quality")
            print("3. 📍 Update Stock Locations")
            print("4. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-4): ").strip()
            
            if choice == '1':
                self.scan_incoming_products()
            elif choice == '2':
                self.record_quantity_quality()
            elif choice == '3':
                self.update_stock_locations()
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def scan_incoming_products(self):
        """Scan incoming products"""
        self.clear_screen()
        self.print_header("SCAN INCOMING PRODUCTS")
        
        try:
            print("📥 Please scan or enter product information:")
            
            product_id = input("🆔 Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                input("Press Enter to continue...")
                return
                
            # Check if product exists
            response = self.products_table.get_item(
                Key={'productId': product_id, 'category': 'VEGETABLES'}
            )
            
            if 'Item' not in response:
                self.print_warning("Product not found. Creating new product entry...")
                product_name = input("📝 Product Name: ").strip()
                category = input("🏷️ Category: ").strip()
                
                product_item = {
                    'productId': product_id,
                    'category': category,
                    'name': product_name,
                    'description': f'Received product: {product_name}',
                    'brand': 'Unknown',
                    'baseUnit': 'PCS',
                    'defaultUnit': 'PCS',
                    'hasVariants': False,
                    'variantTypes': [],
                    'costPrice': Decimal('0'),
                    'sellingPrice': Decimal('0'),
                    'minStock': 0,
                    'reorderPoint': 0,
                    'supplierId': 'UNKNOWN',
                    'expiryTracking': False,
                    'batchRequired': False,
                    'storageLocation': 'GENERAL',
                    'specialHandling': 'NONE',
                    'images': [],
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                self.products_table.put_item(Item=product_item)
                self.print_success(f"Product '{product_name}' created successfully!")
            else:
                product = response['Item']
                self.print_success(f"Product found: {product.get('name', 'Unknown')}")
                
            # Get receiving details
            quantity = input("📊 Quantity Received: ").strip()
            quality_status = input("✅ Quality Status (GOOD/DAMAGED/EXPIRED): ").strip().upper()
            batch_number = input("📦 Batch Number: ").strip()
            supplier_id = input("🏪 Supplier ID: ").strip()
            location = input("📍 Storage Location: ").strip()
            
            if not quantity.isdigit():
                self.print_error("Invalid quantity")
                input("Press Enter to continue...")
                return
                
            # Create batch record
            batch_item = {
                'batchId': f'BATCH-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'productId': product_id,
                'variantId': None,
                'unitId': 'PCS',
                'batchNumber': batch_number,
                'manufacturingDate': datetime.now().strftime('%Y-%m-%d'),
                'expiryDate': input("⏰ Expiry Date (YYYY-MM-DD): ").strip(),
                'initialQuantity': int(quantity),
                'currentQuantity': int(quantity),
                'unitQuantity': Decimal(quantity),
                'supplierId': supplier_id,
                'qualityStatus': quality_status,
                'temperature': Decimal('20.0'),
                'location': location,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Update stock levels
            stock_key = f"{location}#null#PCS"
            stock_item = {
                'productId': product_id,
                'location': stock_key,
                'variantId': None,
                'unitId': 'PCS',
                'totalStock': int(quantity),
                'availableStock': int(quantity),
                'reservedStock': 0,
                'damagedStock': 0 if quality_status == 'GOOD' else int(quantity),
                'expiredStock': 0,
                'baseUnitQuantity': Decimal(quantity),
                'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Save to DynamoDB
            self.batches_table.put_item(Item=batch_item)
            self.stock_levels_table.put_item(Item=stock_item)
            
            # Log audit
            self.log_audit('STOCK_RECEIVING', product_id, f"Received {quantity} units of {product_id}")
            
            self.print_success(f"Stock receiving completed!")
            self.print_info(f"Product: {product_id}")
            self.print_info(f"Quantity: {quantity}")
            self.print_info(f"Location: {location}")
            
        except Exception as e:
            self.print_error(f"Error scanning incoming products: {str(e)}")
            
        input("Press Enter to continue...")
        
    def stock_movement_menu(self):
        """Stock Movement Operations"""
        while True:
            self.clear_screen()
            self.print_header("STOCK MOVEMENT")
            print("1. 📦 Pick Products for Orders")
            print("2. 🔄 Transfer Stock Between Locations")
            print("3. 📊 Perform Cycle Counts")
            print("4. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-4): ").strip()
            
            if choice == '1':
                self.pick_products_for_orders()
            elif choice == '2':
                self.transfer_stock_between_locations()
            elif choice == '3':
                self.perform_cycle_counts()
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def order_fulfillment_menu(self):
        """Order Fulfillment Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER FULFILLMENT")
            print("1. 📦 Pick and Pack Orders")
            print("2. ✅ Verify Order Accuracy")
            print("3. 📦 Prepare for Dispatch")
            print("4. 📊 View Dispatch History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.pick_and_pack_orders()
            elif choice == '2':
                self.verify_order_accuracy()
            elif choice == '3':
                self.prepare_for_dispatch()
            elif choice == '4':
                self.view_dispatch_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def inventory_counting_menu(self):
        """Inventory Counting Operations"""
        while True:
            self.clear_screen()
            self.print_header("INVENTORY COUNTING")
            print("1. 🔢 Perform Daily Cycle Counts")
            print("2. 📊 Conduct Periodic Full Counts")
            print("3. 📈 Report Count Variances")
            print("4. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-4): ").strip()
            
            if choice == '1':
                self.perform_daily_cycle_counts()
            elif choice == '2':
                self.conduct_periodic_full_counts()
            elif choice == '3':
                self.report_count_variances()
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def labeling_tagging_menu(self):
        """Labeling and Tagging Operations"""
        while True:
            self.clear_screen()
            self.print_header("LABELING & TAGGING")
            print("1. 🏷️ Print Product Labels")
            print("2. 📦 Apply Batch/Expiry Information")
            print("3. 📍 Tag Storage Locations")
            print("4. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-4): ").strip()
            
            if choice == '1':
                self.print_product_labels()
            elif choice == '2':
                self.apply_batch_expiry_info()
            elif choice == '3':
                self.tag_storage_locations()
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def stock_adjustments_menu(self):
        """Stock Adjustments Operations"""
        while True:
            self.clear_screen()
            self.print_header("STOCK ADJUSTMENTS")
            print("1. 🗑️ Report Damaged Goods")
            print("2. 📊 Record Stock Discrepancies")
            print("3. 📝 Document Wastage")
            print("4. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-4): ").strip()
            
            if choice == '1':
                self.report_damaged_goods()
            elif choice == '2':
                self.record_stock_discrepancies()
            elif choice == '3':
                self.document_wastage()
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    # Placeholder methods for other operations
    def record_quantity_quality(self):
        self.clear_screen()
        self.print_header("RECORD QUANTITY & QUALITY")
        self.print_info("Quantity and quality recording functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_stock_locations(self):
        self.clear_screen()
        self.print_header("UPDATE STOCK LOCATIONS")
        self.print_info("Stock location update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def pick_products_for_orders(self):
        self.clear_screen()
        self.print_header("PICK PRODUCTS FOR ORDERS")
        self.print_info("Product picking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def transfer_stock_between_locations(self):
        self.clear_screen()
        self.print_header("TRANSFER STOCK BETWEEN LOCATIONS")
        self.print_info("Stock transfer functionality will be implemented.")
        input("Press Enter to continue...")
        
    def perform_cycle_counts(self):
        self.clear_screen()
        self.print_header("PERFORM CYCLE COUNTS")
        self.print_info("Cycle counting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def pick_and_pack_orders(self):
        """Pick and pack customer orders"""
        self.clear_screen()
        self.print_header("PICK AND PACK ORDERS")
        
        try:
            # Get pending orders that need packing
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            # Filter orders that need packing (PENDING or CONFIRMED status)
            pending_orders = [order for order in orders 
                             if order.get('status') in ['PENDING', 'CONFIRMED']]
            
            if not pending_orders:
                self.print_info("No orders pending for pick and pack.")
                input("Press Enter to continue...")
                return
                
            print(f"\n📦 Orders Pending for Pick and Pack ({len(pending_orders)} orders):")
            print("-" * 100)
            print(f"{'Order ID':<25} {'Customer':<20} {'Total Amount':<15} {'Status':<15} {'Order Date':<15}")
            print("-" * 100)
            
            for order in pending_orders:
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{order.get('totalAmount', 0):<15} "
                      f"{order.get('status', 'N/A'):<15} "
                      f"{order.get('orderDate', 'N/A')[:10]:<15}")
                      
            print("-" * 100)
            
            # Select order to pack
            order_choice = input("\n🎯 Select order number to pack (or 'all' for all orders): ").strip()
            
            if order_choice.lower() == 'all':
                orders_to_pack = pending_orders
            else:
                try:
                    order_index = int(order_choice) - 1
                    if 0 <= order_index < len(pending_orders):
                        orders_to_pack = [pending_orders[order_index]]
                    else:
                        self.print_error("Invalid order selection.")
                        input("Press Enter to continue...")
                        return
                except ValueError:
                    self.print_error("Invalid order number.")
                    input("Press Enter to continue...")
            
            # Process each order
            for order in orders_to_pack:
                self.process_order_packing(order)
                
        except Exception as e:
            self.print_error(f"Error in pick and pack: {str(e)}")
            input("Press Enter to continue...")

    def process_order_packing(self, order):
        """Process packing for a specific order"""
        order_id = order.get('orderId')
        customer_id = order.get('customerId')
        
        print(f"\n📦 Processing Order: {order_id}")
        print(f"👤 Customer: {customer_id}")
        print(f"💰 Total Amount: {order.get('totalAmount', 0)}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n📋 Order Items to Pack:")
        for i, item in enumerate(order_items, 1):
            print(f"  {i}. {item.get('name', 'N/A')} x{item.get('quantity', 0)}")
        
        # Check stock availability
        print(f"\n🔍 Checking Stock Availability...")
        stock_issues = []
        
        for item in order_items:
            product_id = item.get('productId')
            required_qty = item.get('quantity', 0)
            
            # Check stock levels
            stock_response = self.stock_levels_table.scan(
                FilterExpression='productId = :productId',
                ExpressionAttributeValues={':productId': product_id}
            )
            
            stock_items = stock_response.get('Items', [])
            if stock_items:
                current_stock = stock_items[0].get('currentStock', 0)
                if current_stock < required_qty:
                    stock_issues.append({
                        'product': item.get('name', 'N/A'),
                        'required': required_qty,
                        'available': current_stock,
                        'shortage': required_qty - current_stock
                    })
            else:
                stock_issues.append({
                    'product': item.get('name', 'N/A'),
                    'required': required_qty,
                    'available': 0,
                    'shortage': required_qty
                })
        
        if stock_issues:
            print(f"\n⚠️ Stock Issues Found:")
            for issue in stock_issues:
                print(f"  • {issue['product']}: Need {issue['required']}, Available {issue['available']}")
            
            choice = input("\n❓ Continue with partial packing? (yes/no): ").strip().lower()
            if choice != 'yes':
                self.print_info("Packing cancelled due to stock issues.")
                return
        
        # Start packing process
        print(f"\n📦 Starting Packing Process...")
        
        packed_items = []
        for item in order_items:
            product_id = item.get('productId')
            product_name = item.get('name', 'N/A')
            quantity = item.get('quantity', 0)
            
            print(f"\n📦 Packing: {product_name} x{quantity}")
            
            # Simulate packing process
            packing_time = input(f"⏱️ Enter packing time for {product_name} (in minutes): ").strip()
            if not packing_time.isdigit():
                packing_time = "5"  # Default 5 minutes
            
            quality_check = input(f"✅ Quality check passed for {product_name}? (yes/no): ").strip().lower()
            if quality_check != 'yes':
                print(f"❌ Quality check failed for {product_name}. Item rejected.")
                continue
            
            packed_items.append({
                'productId': product_id,
                'name': product_name,
                'quantity': quantity,
                'packingTime': int(packing_time),
                'packedBy': self.current_user.get('userId'),
                'packedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            })
            
            print(f"✅ {product_name} packed successfully!")
        
        if not packed_items:
            self.print_warning("No items were packed.")
            return
        
        # Update order status
        try:
            self.orders_table.update_item(
                Key={'orderId': order_id, 'customerId': customer_id},
                UpdateExpression='SET #status = :status, packedAt = :packed, packedBy = :packer, updatedAt = :updated',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'PACKED',
                    ':packed': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':packer': self.current_user.get('userId'),
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Update stock levels
            self.update_stock_after_packing(packed_items)
            
            # Log audit
            self.log_audit('ORDER_PACKED', order_id, f"Order {order_id} packed with {len(packed_items)} items")
            
            self.print_success(f"✅ Order {order_id} packed successfully!")
            self.print_info(f"📦 Items packed: {len(packed_items)}")
            self.print_info(f"👤 Packed by: {self.current_user.get('name', 'Unknown')}")
            self.print_info(f"📦 Status updated to: PACKED")
            
        except Exception as e:
            self.print_error(f"Error updating order status: {str(e)}")

    def update_stock_after_packing(self, packed_items):
        """Update stock levels after packing"""
        try:
            for item in packed_items:
                product_id = item.get('productId')
                quantity = item.get('quantity', 0)
                
                # Get current stock
                stock_response = self.stock_levels_table.scan(
                    FilterExpression='productId = :productId',
                    ExpressionAttributeValues={':productId': product_id}
                )
                
                stock_items = stock_response.get('Items', [])
                if stock_items:
                    current_stock = stock_items[0].get('currentStock', 0)
                    new_stock = current_stock - quantity
                    
                    # Update stock level
                    self.stock_levels_table.update_item(
                        Key={'productId': product_id, 'locationId': stock_items[0].get('locationId', 'MAIN')},
                        UpdateExpression='SET currentStock = :stock, lastUpdated = :updated',
                        ExpressionAttributeValues={
                            ':stock': max(0, new_stock),  # Don't go below 0
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    print(f"📊 Stock updated for {item.get('name')}: {current_stock} → {max(0, new_stock)}")
                    
        except Exception as e:
            self.print_error(f"Error updating stock levels: {str(e)}")

    def verify_order_accuracy(self):
        """Verify order accuracy before dispatch"""
        self.clear_screen()
        self.print_header("VERIFY ORDER ACCURACY")
        
        try:
            # Get packed orders that need verification
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            packed_orders = [order for order in orders 
                            if order.get('status') == 'PACKED']
            
            if not packed_orders:
                self.print_info("No packed orders found for verification.")
                input("Press Enter to continue...")
                return
                
            print(f"✅ Orders Pending Verification ({len(packed_orders)} orders):")
            print("-" * 100)
            print(f"{'Order ID':<25} {'Customer':<20} {'Total Amount':<15} {'Packed Date':<20}")
            print("-" * 100)
            
            for order in packed_orders:
                packed_date = order.get('packedAt', 'N/A')[:10] if order.get('packedAt') else 'N/A'
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{order.get('totalAmount', 0):<15} "
                      f"{packed_date:<20}")
                      
            print("-" * 100)
            
            # Select order to verify
            order_choice = input("\n🎯 Select order number to verify: ").strip()
            
            try:
                order_index = int(order_choice) - 1
                if 0 <= order_index < len(packed_orders):
                    selected_order = packed_orders[order_index]
                    self.verify_specific_order(selected_order)
                else:
                    self.print_error("Invalid order selection.")
            except ValueError:
                self.print_error("Invalid order number.")
                
        except Exception as e:
            self.print_error(f"Error in order verification: {str(e)}")
            input("Press Enter to continue...")

    def verify_specific_order(self, order):
        """Verify a specific order"""
        order_id = order.get('orderId')
        customer_id = order.get('customerId')
        
        print(f"\n✅ Verifying Order: {order_id}")
        print(f"👤 Customer: {customer_id}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n📋 Order Items to Verify:")
        verification_results = []
        
        for i, item in enumerate(order_items, 1):
            print(f"\n📦 Item {i}: {item.get('name', 'N/A')}")
            print(f"   Quantity: {item.get('quantity', 0)}")
            print(f"   Price: {item.get('price', 0)}")
            
            # Quality checks
            quality_check = input(f"   ✅ Quality check passed? (yes/no): ").strip().lower()
            quantity_check = input(f"   📊 Quantity correct? (yes/no): ").strip().lower()
            packaging_check = input(f"   📦 Packaging intact? (yes/no): ").strip().lower()
            
            verification_results.append({
                'item': item.get('name', 'N/A'),
                'quality': quality_check == 'yes',
                'quantity': quantity_check == 'yes',
                'packaging': packaging_check == 'yes',
                'all_passed': quality_check == 'yes' and quantity_check == 'yes' and packaging_check == 'yes'
            })
            
            if verification_results[-1]['all_passed']:
                print(f"   ✅ Item {i} verified successfully!")
            else:
                print(f"   ❌ Item {i} has issues!")
        
        # Overall verification
        all_passed = all(result['all_passed'] for result in verification_results)
        
        if all_passed:
            print(f"\n✅ All items verified successfully!")
            
            # Update order status to VERIFIED
            try:
                self.orders_table.update_item(
                    Key={'orderId': order_id, 'customerId': customer_id},
                    UpdateExpression='SET #status = :status, verifiedAt = :verified, verifiedBy = :verifier, updatedAt = :updated',
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': 'VERIFIED',
                        ':verified': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                        ':verifier': self.current_user.get('userId'),
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                
                # Log audit
                self.log_audit('ORDER_VERIFIED', order_id, f"Order {order_id} verified successfully")
                
                self.print_success(f"✅ Order {order_id} verified and ready for dispatch!")
                
            except Exception as e:
                self.print_error(f"Error updating order status: {str(e)}")
        else:
            print(f"\n❌ Order verification failed!")
            print(f"📋 Issues found:")
            for result in verification_results:
                if not result['all_passed']:
                    issues = []
                    if not result['quality']:
                        issues.append("Quality")
                    if not result['quantity']:
                        issues.append("Quantity")
                    if not result['packaging']:
                        issues.append("Packaging")
                    print(f"   • {result['item']}: {', '.join(issues)}")
            
            choice = input("\n❓ Mark order for repacking? (yes/no): ").strip().lower()
            if choice == 'yes':
                try:
                    self.orders_table.update_item(
                        Key={'orderId': order_id, 'customerId': customer_id},
                        UpdateExpression='SET #status = :status, updatedAt = :updated',
                        ExpressionAttributeNames={
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':status': 'NEEDS_REPACKING',
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    self.print_info("Order marked for repacking.")
                except Exception as e:
                    self.print_error(f"Error updating order status: {str(e)}")
        
        input("Press Enter to continue...")
        
    def prepare_for_dispatch(self):
        """Prepare orders for dispatch"""
        self.clear_screen()
        self.print_header("PREPARE FOR DISPATCH")
        
        try:
            # Get verified orders ready for dispatch
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            verified_orders = [order for order in orders 
                              if order.get('status') == 'VERIFIED']
            
            if not verified_orders:
                self.print_info("No verified orders found for dispatch preparation.")
                input("Press Enter to continue...")
                return
                
            print(f"📦 Orders Ready for Dispatch ({len(verified_orders)} orders):")
            print("-" * 120)
            print(f"{'Order ID':<25} {'Customer':<20} {'Total Amount':<15} {'Verified Date':<20} {'Delivery Address':<30}")
            print("-" * 120)
            
            for order in verified_orders:
                verified_date = order.get('verifiedAt', 'N/A')[:10] if order.get('verifiedAt') else 'N/A'
                delivery_address = order.get('deliveryAddress', 'N/A')[:30]
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{order.get('totalAmount', 0):<15} "
                      f"{verified_date:<20} "
                      f"{delivery_address:<30}")
                      
            print("-" * 120)
            
            # Select order to prepare
            order_choice = input("\n🎯 Select order number to prepare for dispatch: ").strip()
            
            try:
                order_index = int(order_choice) - 1
                if 0 <= order_index < len(verified_orders):
                    selected_order = verified_orders[order_index]
                    self.prepare_specific_order(selected_order)
                else:
                    self.print_error("Invalid order selection.")
            except ValueError:
                self.print_error("Invalid order number.")
                
        except Exception as e:
            self.print_error(f"Error in dispatch preparation: {str(e)}")
            input("Press Enter to continue...")

    def prepare_specific_order(self, order):
        """Prepare a specific order for dispatch"""
        order_id = order.get('orderId')
        customer_id = order.get('customerId')
        
        print(f"\n📦 Preparing Order for Dispatch: {order_id}")
        print(f"👤 Customer: {customer_id}")
        print(f"📍 Delivery Address: {order.get('deliveryAddress', 'N/A')}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n📋 Preparing Items for Dispatch:")
        
        # Packaging preparation
        print(f"\n📦 Packaging Preparation:")
        packaging_materials = input("   📦 Packaging materials ready? (yes/no): ").strip().lower()
        labels_printed = input("   🏷️ Shipping labels printed? (yes/no): ").strip().lower()
        documentation_complete = input("   📄 Documentation complete? (yes/no): ").strip().lower()
        
        if packaging_materials != 'yes' or labels_printed != 'yes' or documentation_complete != 'yes':
            self.print_error("❌ Dispatch preparation incomplete!")
            input("Press Enter to continue...")
            return
        
        # Item preparation
        print(f"\n📦 Item Preparation:")
        for i, item in enumerate(order_items, 1):
            print(f"   📦 Item {i}: {item.get('name', 'N/A')}")
            properly_packaged = input(f"      ✅ Properly packaged? (yes/no): ").strip().lower()
            labeled_correctly = input(f"      🏷️ Labeled correctly? (yes/no): ").strip().lower()
            
            if properly_packaged != 'yes' or labeled_correctly != 'yes':
                self.print_error(f"❌ Item {i} not ready for dispatch!")
                input("Press Enter to continue...")
                return
        
        # Final checks
        print(f"\n✅ Final Dispatch Checks:")
        weight_verified = input("   ⚖️ Weight verified? (yes/no): ").strip().lower()
        dimensions_checked = input("   📐 Dimensions checked? (yes/no): ").strip().lower()
        fragile_items_marked = input("   🚨 Fragile items marked? (yes/no): ").strip().lower()
        
        if weight_verified != 'yes' or dimensions_checked != 'yes' or fragile_items_marked != 'yes':
            self.print_error("❌ Final checks incomplete!")
            input("Press Enter to continue...")
            return
        
        # Update order status to READY_FOR_DISPATCH
        try:
            self.orders_table.update_item(
                Key={'orderId': order_id, 'customerId': customer_id},
                UpdateExpression='SET #status = :status, preparedAt = :prepared, preparedBy = :preparer, updatedAt = :updated',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'READY_FOR_DISPATCH',
                    ':prepared': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':preparer': self.current_user.get('userId'),
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Log audit
            self.log_audit('ORDER_DISPATCH_READY', order_id, f"Order {order_id} prepared for dispatch")
            
            self.print_success(f"✅ Order {order_id} prepared for dispatch successfully!")
            self.print_info(f"📦 Status: READY_FOR_DISPATCH")
            self.print_info(f"📦 Ready for delivery pickup")
            
        except Exception as e:
            self.print_error(f"Error updating order status: {str(e)}")
        
        input("Press Enter to continue...")

    def view_dispatch_history(self):
        """View dispatch preparation history"""
        self.clear_screen()
        self.print_header("DISPATCH PREPARATION HISTORY")
        
        try:
            # Get orders prepared for dispatch
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            prepared_orders = [order for order in orders 
                              if order.get('status') == 'READY_FOR_DISPATCH' and 
                              order.get('preparedBy') == self.current_user.get('userId')]
            
            if not prepared_orders:
                self.print_info("No dispatch preparation history found for your account.")
                input("Press Enter to continue...")
                return
                
            print(f"📦 Your Dispatch Preparation History ({len(prepared_orders)} orders):")
            print("-" * 120)
            print(f"{'Order ID':<25} {'Customer':<20} {'Prepared Date':<20} {'Items Count':<15}")
            print("-" * 120)
            
            for order in prepared_orders:
                prepared_date = order.get('preparedAt', 'N/A')[:19] if order.get('preparedAt') else 'N/A'
                items_count = len(order.get('items', []))
                
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{prepared_date:<20} "
                      f"{items_count:<15}")
                      
            print("-" * 120)
            
            # Summary
            total_items = sum(len(order.get('items', [])) for order in prepared_orders)
            print(f"\n📊 Summary:")
            print(f"  • Total Orders Prepared: {len(prepared_orders)}")
            print(f"  • Total Items Prepared: {total_items}")
            
        except Exception as e:
            self.print_error(f"Error viewing dispatch history: {str(e)}")
            
        input("Press Enter to continue...")
        
    def perform_daily_cycle_counts(self):
        self.clear_screen()
        self.print_header("PERFORM DAILY CYCLE COUNTS")
        self.print_info("Daily cycle counting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def conduct_periodic_full_counts(self):
        self.clear_screen()
        self.print_header("CONDUCT PERIODIC FULL COUNTS")
        self.print_info("Periodic full counting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def report_count_variances(self):
        self.clear_screen()
        self.print_header("REPORT COUNT VARIANCES")
        self.print_info("Count variance reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def print_product_labels(self):
        self.clear_screen()
        self.print_header("PRINT PRODUCT LABELS")
        self.print_info("Product label printing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def apply_batch_expiry_info(self):
        self.clear_screen()
        self.print_header("APPLY BATCH/EXPIRY INFORMATION")
        self.print_info("Batch/expiry information application functionality will be implemented.")
        input("Press Enter to continue...")
        
    def tag_storage_locations(self):
        self.clear_screen()
        self.print_header("TAG STORAGE LOCATIONS")
        self.print_info("Storage location tagging functionality will be implemented.")
        input("Press Enter to continue...")
        
    def report_damaged_goods(self):
        self.clear_screen()
        self.print_header("REPORT DAMAGED GOODS")
        self.print_info("Damaged goods reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def record_stock_discrepancies(self):
        self.clear_screen()
        self.print_header("RECORD STOCK DISCREPANCIES")
        self.print_info("Stock discrepancy recording functionality will be implemented.")
        input("Press Enter to continue...")
        
    def document_wastage(self):
        self.clear_screen()
        self.print_header("DOCUMENT WASTAGE")
        self.print_info("Wastage documentation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.print_success(f"Goodbye, {self.current_user.get('name', 'User')}!")
            self.current_user = None
            self.current_role = None
        else:
            self.print_info("No user logged in")
            
    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': self.current_user.get('userId'),
                'action': action,
                'entityId': entity_id,
                'details': details,
                'ipAddress': '127.0.0.1',
                'userAgent': 'InventoryStaff-Standalone',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")
            
    def run(self):
        """Main run method"""
        try:
            # Create demo user if needed
            self.create_demo_user()
            
            # Authenticate user
            if not self.authenticate_user():
                self.print_error("Authentication failed. Exiting.")
                sys.exit(1)
                
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\n⚠️  System interrupted by user")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
        finally:
            self.print_success("Thank you for using the Inventory Staff system!")


def main():
    """Main entry point"""
    inventory_staff = InventoryStaffStandalone()
    inventory_staff.run()


if __name__ == '__main__':
    main() 