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
from typing import Dict, Any, Optional, List


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
        print(f"[ORDER] {title}")
        print("=" * 80)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"[SUCCESS] {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"[ERROR] {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"[INFO]  {message}")
        
    def test_aws_connection(self) -> bool:
        """Test AWS connection and credentials"""
        try:
            sts = boto3.client('sts', region_name=self.region_name)
            identity = sts.get_caller_identity()
            print(f"[SECURE] AWS Identity: {identity['Arn']}")
            print(f"[ACCOUNT] AWS Account: {identity['Account']}")
            print(f"[REGION] AWS Region: {self.region_name}")
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
            
        print("\n[SECURE] Please enter your credentials:")
        print("[NOTE] Demo credentials: inventory_staff / inventory123")
        
        username = input("\n[USER] Username: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
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
                print(f"[USER] User: {self.current_user.get('name', 'Unknown')}")
                print(f"[ORDER] Role: {self.current_user.get('role', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. 📥 Stock Receiving")
            print("2. [ORDER] Stock Movement")
            print("3. [CLIPBOARD] Order Fulfillment")
            print("4. [NUMBER] Inventory Counting")
            print("5. [CATEGORY] Labeling & Tagging")
            print("6. [TRACK] Stock Adjustments")
            print("7. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-7): ").strip()
            
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
            print("2. [TRACK] Record Quantity & Quality")
            print("3. [ADDRESS] Update Stock Locations")
            print("4. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
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
        """Scan incoming products with improved product recognition"""
        self.clear_screen()
        self.print_header("SCAN INCOMING PRODUCTS")
        
        try:
            print("📥 Please scan or enter product information:")
            print("[NOTE] Tip: You can scan barcode, enter Product ID, or search by name")
            
            # Multiple ways to identify product
            print("\n[AUDIT] Product Identification Methods:")
            print("1. Scan/Enter Product ID")
            print("2. Search by Product Name")
            print("3. Browse All Products")
            
            method = input("\n[TARGET] Select method (1-3): ").strip()
            
            product = None
            product_id = None
            
            if method == '1':
                product_id = input("[ID] Product ID/Barcode: ").strip()
                if not product_id:
                    self.print_error("Product ID is required")
                    input("Press Enter to continue...")
                    return
                    
                # Try to find product by scanning all categories
                product = self.find_product_by_id(product_id)
                
            elif method == '2':
                search_name = input("[AUDIT] Search product name: ").strip()
                if not search_name:
                    self.print_error("Product name is required")
                    input("Press Enter to continue...")
                    return
                    
                products = self.search_products_by_name(search_name)
                if products:
                    product = self.select_product_from_list(products)
                    if product:
                        product_id = product.get('productId')
                        
            elif method == '3':
                products = self.get_all_products()
                if products:
                    product = self.select_product_from_list(products)
                    if product:
                        product_id = product.get('productId')
            else:
                self.print_error("Invalid method selection")
                input("Press Enter to continue...")
                return
                
            # If product not found, offer to create new one
            if not product:
                if product_id:
                    self.print_warning(f"Product '{product_id}' not found in system.")
                    create_new = input("🆕 Create new product? (yes/no): ").strip().lower()
                    if create_new == 'yes':
                        product = self.create_new_product_entry(product_id)
                        if not product:
                            return
                    else:
                        self.print_info("Product receiving cancelled.")
                        input("Press Enter to continue...")
                        return
                else:
                    self.print_error("No product selected.")
                    input("Press Enter to continue...")
                    return
                    
            # Display product information
            self.print_success(f"[SUCCESS] Product Found: {product.get('name', 'Unknown')}")
            print(f"   [ID] Product ID: {product.get('productId', 'N/A')}")
            print(f"   [CATEGORY] Category: {product.get('category', 'N/A')}")
            print(f"   [ACCOUNT] Brand: {product.get('brand', 'N/A')}")
            print(f"   [SIZE] Unit: {product.get('baseUnit', 'N/A')}")
            
            # Get receiving details with validation
            quantity = self.get_validated_quantity()
            if quantity is None:
                return
                
            quality_status = self.get_quality_status()
            batch_number = input("\n[ORDER] Batch Number (optional): ").strip() or f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            supplier_id = self.get_supplier_selection()
            location = self.get_location_selection()
            expiry_date = self.get_expiry_date(product)
            
            # Create receiving record
            receiving_record = {
                'receivingId': f'RCV-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'productId': product_id,
                'productName': product.get('name', 'Unknown'),
                'category': product.get('category', 'Unknown'),
                'quantity': quantity,
                'qualityStatus': quality_status,
                'batchNumber': batch_number,
                'supplierId': supplier_id,
                'location': location,
                'expiryDate': expiry_date,
                'receivedBy': self.current_user.get('userId'),
                'receivedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Create batch record if required
            if product.get('batchRequired', False) or batch_number:
                batch_item = {
                    'batchId': f'BATCH-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                    'productId': product_id,
                    'variantId': None,
                    'unitId': product.get('baseUnit', 'PCS'),
                    'batchNumber': batch_number,
                    'manufacturingDate': datetime.now().strftime('%Y-%m-%d'),
                    'expiryDate': expiry_date,
                    'initialQuantity': quantity,
                    'currentQuantity': quantity,
                    'unitQuantity': Decimal(str(quantity)),
                    'supplierId': supplier_id,
                    'qualityStatus': quality_status,
                    'temperature': Decimal('20.0'),
                    'location': location,
                    'receivingId': receiving_record['receivingId'],
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                self.batches_table.put_item(Item=batch_item)
            
            # Update stock levels
            self.update_stock_levels_on_receiving(product_id, location, quantity, quality_status, product.get('baseUnit', 'PCS'))
            
            # Save receiving record to audit table (using existing audit structure)
            self.log_audit('STOCK_RECEIVING', product_id, 
                          f"Received {quantity} {product.get('baseUnit', 'units')} of {product.get('name', 'Unknown')} "
                          f"(Quality: {quality_status}, Location: {location})")
            
            # Display success summary
            self.print_success("📥 Stock Receiving Completed Successfully!")
            print(f"\n[TRACK] Receiving Summary:")
            print(f"   [ORDER] Product: {product.get('name', 'Unknown')}")
            print(f"   [ID] Product ID: {product_id}")
            print(f"   [TRACK] Quantity: {quantity} {product.get('baseUnit', 'units')}")
            print(f"   [SUCCESS] Quality: {quality_status}")
            print(f"   [ORDER] Batch: {batch_number}")
            print(f"   [SUPPLIER] Supplier: {supplier_id}")
            print(f"   [ADDRESS] Location: {location}")
            print(f"   ⏰ Expiry: {expiry_date}")
            print(f"   [USER] Received by: {self.current_user.get('name', 'Unknown')}")
            
        except Exception as e:
            self.print_error(f"Error scanning incoming products: {str(e)}")
            
        input("Press Enter to continue...")
        
    def find_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Find product by ID across all categories"""
        try:
            # Scan all products to find by productId
            response = self.products_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except Exception as e:
            self.print_error(f"Error finding product: {str(e)}")
            return None
            
    def search_products_by_name(self, search_name: str) -> List[Dict[str, Any]]:
        """Search products by name (partial match)"""
        try:
            response = self.products_table.scan()
            all_products = response.get('Items', [])
            
            # Filter products that contain search term in name
            matching_products = [
                product for product in all_products
                if search_name.lower() in product.get('name', '').lower()
            ]
            
            return matching_products[:10]  # Limit to 10 results
            
        except Exception as e:
            self.print_error(f"Error searching products: {str(e)}")
            return []
            
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products for browsing"""
        try:
            response = self.products_table.scan()
            return response.get('Items', [])
            
        except Exception as e:
            self.print_error(f"Error getting products: {str(e)}")
            return []
            
    def select_product_from_list(self, products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Allow user to select product from a list"""
        if not products:
            self.print_info("No products found.")
            return None
            
        print(f"\n[ORDER] Found {len(products)} product(s):")
        print("-" * 80)
        print(f"{'#':<3} {'Product ID':<15} {'Name':<30} {'Category':<15} {'Brand':<15}")
        print("-" * 80)
        
        for i, product in enumerate(products, 1):
            print(f"{i:<3} {product.get('productId', 'N/A'):<15} "
                  f"{product.get('name', 'N/A')[:29]:<30} "
                  f"{product.get('category', 'N/A'):<15} "
                  f"{product.get('brand', 'N/A')[:14]:<15}")
                  
        print("-" * 80)
        
        try:
            choice = input(f"\n[TARGET] Select product number (1-{len(products)}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(products):
                return products[choice_num - 1]
            else:
                self.print_error("Invalid selection.")
                return None
                
        except ValueError:
            self.print_error("Invalid number.")
            return None
            
    def create_new_product_entry(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Create a new product entry for receiving"""
        try:
            print(f"\n🆕 Creating new product entry for ID: {product_id}")
            
            product_name = input("[GENERATE] Product Name: ").strip()
            if not product_name:
                self.print_error("Product name is required")
                return None
                
            # Get available categories
            category = self.get_category_selection_for_receiving()
            if not category:
                category = input("[CATEGORY] Category: ").strip() or "GENERAL"
                
            brand = input("[ACCOUNT] Brand: ").strip() or "Unknown"
            base_unit = input("[SIZE] Base Unit (kg/liter/piece/box): ").strip() or "piece"
            
            product_item = {
                'productId': product_id,
                'category': category,
                'name': product_name,
                'description': f'Newly received product: {product_name}',
                'brand': brand,
                'baseUnit': base_unit,
                'defaultUnit': base_unit,
                'hasVariants': False,
                'variantTypes': [],
                'costPrice': Decimal('0'),
                'sellingPrice': Decimal('0'),
                'minStock': 0,
                'reorderPoint': 0,
                'supplierId': 'UNKNOWN',
                'expiryTracking': True,  # Default to true for safety
                'batchRequired': True,   # Default to true for traceability
                'storageLocation': 'GENERAL',
                'specialHandling': 'NONE',
                'images': [],
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.products_table.put_item(Item=product_item)
            self.print_success(f"[SUCCESS] Product '{product_name}' created successfully!")
            
            return product_item
            
        except Exception as e:
            self.print_error(f"Error creating product: {str(e)}")
            return None
            
    def get_validated_quantity(self) -> Optional[int]:
        """Get and validate quantity input"""
        while True:
            quantity_str = input("\n[TRACK] Quantity Received: ").strip()
            
            if not quantity_str:
                self.print_error("Quantity is required")
                continue
                
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    self.print_error("Quantity must be greater than 0")
                    continue
                return quantity
            except ValueError:
                self.print_error("Please enter a valid number")
                retry = input("Try again? (yes/no): ").strip().lower()
                if retry != 'yes':
                    return None
                    
    def get_quality_status(self) -> str:
        """Get quality status with validation"""
        print("\n[SUCCESS] Quality Status Options:")
        print("1. GOOD - Product in perfect condition")
        print("2. DAMAGED - Product has minor damage but usable")
        print("3. SEVERELY_DAMAGED - Product has major damage")
        print("4. EXPIRED - Product past expiry date")
        print("5. NEAR_EXPIRY - Product close to expiry")
        
        while True:
            choice = input("\n[TARGET] Select quality status (1-5): ").strip()
            
            quality_map = {
                '1': 'GOOD',
                '2': 'DAMAGED', 
                '3': 'SEVERELY_DAMAGED',
                '4': 'EXPIRED',
                '5': 'NEAR_EXPIRY'
            }
            
            if choice in quality_map:
                return quality_map[choice]
            else:
                self.print_error("Invalid selection. Please choose 1-5.")
                
    def get_supplier_selection(self) -> str:
        """Get supplier selection"""
        try:
            # Try to get existing suppliers
            suppliers_table = self.dynamodb.Table('InventoryManagement-Suppliers')
            response = suppliers_table.scan()
            suppliers = response.get('Items', [])
            
            if suppliers:
                print(f"\n[SUPPLIER] Available Suppliers:")
                for i, supplier in enumerate(suppliers[:10], 1):  # Show max 10
                    print(f"{i}. {supplier.get('supplierId', 'N/A')} - {supplier.get('name', 'N/A')}")
                    
                print(f"{len(suppliers[:10]) + 1}. Enter New Supplier")
                
                choice = input(f"\n[TARGET] Select supplier (1-{len(suppliers[:10]) + 1}): ").strip()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(suppliers[:10]):
                        return suppliers[choice_num - 1].get('supplierId', 'UNKNOWN')
                    elif choice_num == len(suppliers[:10]) + 1:
                        return input("[SUPPLIER] Enter Supplier ID: ").strip() or 'UNKNOWN'
                except ValueError:
                    pass
                    
        except Exception:
            pass  # Fall back to manual entry
            
        return input("\n[SUPPLIER] Supplier ID: ").strip() or 'UNKNOWN'
        
    def get_location_selection(self) -> str:
        """Get storage location selection"""
        print(f"\n[ADDRESS] Storage Location Options:")
        print("1. MAIN_WAREHOUSE - Main warehouse storage")
        print("2. COLD_STORAGE - Refrigerated storage")
        print("3. DRY_STORAGE - Dry goods storage")
        print("4. QUARANTINE - Quality check area")
        print("5. RETURNS - Returns processing area")
        print("6. Custom Location")
        
        choice = input("\n[TARGET] Select location (1-6): ").strip()
        
        location_map = {
            '1': 'MAIN_WAREHOUSE',
            '2': 'COLD_STORAGE',
            '3': 'DRY_STORAGE',
            '4': 'QUARANTINE',
            '5': 'RETURNS'
        }
        
        if choice in location_map:
            return location_map[choice]
        elif choice == '6':
            return input("[ADDRESS] Enter custom location: ").strip() or 'GENERAL'
        else:
            return 'MAIN_WAREHOUSE'  # Default
            
    def get_expiry_date(self, product: Dict[str, Any]) -> str:
        """Get expiry date if product requires expiry tracking"""
        if product.get('expiryTracking', False):
            expiry_date = input("\n⏰ Expiry Date (YYYY-MM-DD) or press Enter to skip: ").strip()
            
            if expiry_date:
                # Basic date format validation
                try:
                    datetime.strptime(expiry_date, '%Y-%m-%d')
                    return expiry_date
                except ValueError:
                    self.print_warning("Invalid date format. Using 'NO_EXPIRY'")
                    return 'NO_EXPIRY'
            else:
                return 'NO_EXPIRY'
        else:
            return 'NO_EXPIRY'
            
    def get_category_selection_for_receiving(self) -> Optional[str]:
        """Get category selection for new products"""
        try:
            # Get existing categories
            response = self.dynamodb.Table('InventoryManagement-Categories').scan()
            categories = response.get('Items', [])
            
            if categories:
                print(f"\n[CATEGORY] Available Categories:")
                for i, cat in enumerate(categories[:10], 1):
                    print(f"{i}. {cat.get('categoryId', 'N/A')} - {cat.get('name', 'N/A')}")
                    
                choice = input(f"\n[TARGET] Select category (1-{len(categories[:10])} or press Enter for manual): ").strip()
                
                if choice:
                    try:
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(categories[:10]):
                            return categories[choice_num - 1].get('categoryId')
                    except ValueError:
                        pass
                        
        except Exception:
            pass
            
        return None
        
    def update_stock_levels_on_receiving(self, product_id: str, location: str, quantity: int, quality_status: str, unit: str):
        """Update stock levels after receiving products"""
        try:
            # Create or update stock level record
            stock_key = f"{location}#null#{unit}"
            
            # Check if stock record exists
            try:
                response = self.stock_levels_table.get_item(
                    Key={'productId': product_id, 'location': stock_key}
                )
                
                if 'Item' in response:
                    # Update existing stock
                    current_item = response['Item']
                    new_total = current_item.get('totalStock', 0) + quantity
                    
                    if quality_status == 'GOOD':
                        new_available = current_item.get('availableStock', 0) + quantity
                        new_damaged = current_item.get('damagedStock', 0)
                    else:
                        new_available = current_item.get('availableStock', 0)
                        new_damaged = current_item.get('damagedStock', 0) + quantity
                    
                    self.stock_levels_table.update_item(
                        Key={'productId': product_id, 'location': stock_key},
                        UpdateExpression='SET totalStock = :total, availableStock = :available, damagedStock = :damaged, baseUnitQuantity = :base_qty, lastUpdated = :updated',
                        ExpressionAttributeValues={
                            ':total': new_total,
                            ':available': new_available,
                            ':damaged': new_damaged,
                            ':base_qty': Decimal(str(new_total)),
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                else:
                    # Create new stock record
                    stock_item = {
                        'productId': product_id,
                        'location': stock_key,
                        'variantId': None,
                        'unitId': unit,
                        'totalStock': quantity,
                        'availableStock': quantity if quality_status == 'GOOD' else 0,
                        'reservedStock': 0,
                        'damagedStock': quantity if quality_status != 'GOOD' else 0,
                        'expiredStock': 0,
                        'baseUnitQuantity': Decimal(str(quantity)),
                        'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                    
                    self.stock_levels_table.put_item(Item=stock_item)
                    
            except Exception as e:
                self.print_error(f"Error updating stock levels: {str(e)}")
                
        except Exception as e:
            self.print_error(f"Error in stock level update: {str(e)}")
        
    def stock_movement_menu(self):
        """Stock Movement Operations"""
        while True:
            self.clear_screen()
            self.print_header("STOCK MOVEMENT")
            print("1. [ORDER] Pick Products for Orders")
            print("2. [FLOW] Transfer Stock Between Locations")
            print("3. [TRACK] Perform Cycle Counts")
            print("4. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
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
            print("1. [ORDER] Pick and Pack Orders")
            print("2. [SUCCESS] Verify Order Accuracy")
            print("3. [ORDER] Prepare for Dispatch")
            print("4. [TRACK] View Dispatch History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [NUMBER] Perform Daily Cycle Counts")
            print("2. [TRACK] Conduct Periodic Full Counts")
            print("3. [REPORT] Report Count Variances")
            print("4. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
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
            print("1. [CATEGORY] Print Product Labels")
            print("2. [ORDER] Apply Batch/Expiry Information")
            print("3. [ADDRESS] Tag Storage Locations")
            print("4. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
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
            print("1. [DELETE] Report Damaged Goods")
            print("2. [TRACK] Record Stock Discrepancies")
            print("3. [GENERATE] Document Wastage")
            print("4. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
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
                
    def record_quantity_quality(self):
        """Record quantity and quality for received products"""
        self.clear_screen()
        self.print_header("RECORD QUANTITY & QUALITY")
        
        try:
            print("[TRACK] Quantity & Quality Recording System")
            print("[NOTE] Use this to verify and record quantities and quality checks")
            
            # Get recent receiving records to verify
            print("\n[CLIPBOARD] Recent Receiving Records:")
            print("1. Record for Existing Product")
            print("2. Quality Check for Batch")
            print("3. Quantity Verification")
            print("4. Damage Assessment")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
            if choice == '1':
                self.record_product_quantity_quality()
            elif choice == '2':
                self.perform_quality_check()
            elif choice == '3':
                self.verify_received_quantity()
            elif choice == '4':
                self.assess_product_damage()
            else:
                self.print_error("Invalid choice.")
                
        except Exception as e:
            self.print_error(f"Error in quantity & quality recording: {str(e)}")
            
        input("Press Enter to continue...")
        
    def record_product_quantity_quality(self):
        """Record quantity and quality for a specific product"""
        try:
            # Search for product
            product_id = input("\n[ID] Enter Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            product = self.find_product_by_id(product_id)
            if not product:
                self.print_error("Product not found")
                return
                
            print(f"\n[ORDER] Product: {product.get('name', 'Unknown')}")
            print(f"[ID] Product ID: {product_id}")
            
            # Get batch information if applicable
            batch_number = input("[ORDER] Batch Number (if applicable): ").strip()
            
            # Get current quantities
            current_qty = input("[TRACK] Current Quantity Count: ").strip()
            if not current_qty.isdigit():
                self.print_error("Invalid quantity")
                return
            current_qty = int(current_qty)
            
            # Quality assessment
            print(f"\n[SUCCESS] Quality Assessment:")
            print("1. Excellent - Perfect condition")
            print("2. Good - Minor cosmetic issues")
            print("3. Fair - Some damage but usable")
            print("4. Poor - Significant damage")
            print("5. Rejected - Not usable")
            
            quality_choice = input("\n[TARGET] Select quality level (1-5): ").strip()
            quality_map = {
                '1': 'EXCELLENT',
                '2': 'GOOD', 
                '3': 'FAIR',
                '4': 'POOR',
                '5': 'REJECTED'
            }
            
            if quality_choice not in quality_map:
                self.print_error("Invalid quality selection")
                return
                
            quality_status = quality_map[quality_choice]
            
            # Additional quality details
            quality_notes = input("[GENERATE] Quality Notes (optional): ").strip()
            damaged_qty = 0
            
            if quality_status in ['FAIR', 'POOR', 'REJECTED']:
                damaged_input = input("[TRACK] Quantity of damaged items: ").strip()
                if damaged_input.isdigit():
                    damaged_qty = int(damaged_input)
                    
            # Storage location
            location = self.get_location_selection()
            
            # Create quality record
            quality_record = {
                'qualityId': f'QC-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'productId': product_id,
                'batchNumber': batch_number or 'NO_BATCH',
                'recordedQuantity': current_qty,
                'qualityStatus': quality_status,
                'damagedQuantity': damaged_qty,
                'usableQuantity': current_qty - damaged_qty,
                'qualityNotes': quality_notes,
                'location': location,
                'checkedBy': self.current_user.get('userId'),
                'checkedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Update stock levels based on quality check
            self.update_stock_after_quality_check(product_id, location, current_qty, damaged_qty, quality_status)
            
            # Log audit
            self.log_audit('QUALITY_CHECK', product_id, 
                          f"Quality check: {current_qty} units, {quality_status}, {damaged_qty} damaged")
            
            # Display summary
            self.print_success("[SUCCESS] Quantity & Quality Recorded Successfully!")
            print(f"\n[TRACK] Quality Check Summary:")
            print(f"   [ORDER] Product: {product.get('name', 'Unknown')}")
            print(f"   [TRACK] Total Quantity: {current_qty}")
            print(f"   [SUCCESS] Quality Status: {quality_status}")
            print(f"   🔴 Damaged Quantity: {damaged_qty}")
            print(f"   [SUCCESS] Usable Quantity: {current_qty - damaged_qty}")
            print(f"   [ADDRESS] Location: {location}")
            print(f"   [USER] Checked by: {self.current_user.get('name', 'Unknown')}")
            
        except Exception as e:
            self.print_error(f"Error recording quantity & quality: {str(e)}")
            
    def perform_quality_check(self):
        """Perform quality check on batches"""
        try:
            # Get batches that need quality checking
            response = self.batches_table.scan()
            batches = response.get('Items', [])
            
            if not batches:
                self.print_info("No batches found for quality checking.")
                return
                
            # Filter recent batches (last 7 days)
            recent_batches = []
            current_time = datetime.now(timezone.utc)
            
            for batch in batches:
                try:
                    created_date = datetime.fromisoformat(batch.get('createdAt', '').replace('Z', '+00:00'))
                    days_diff = (current_time - created_date).days
                    if days_diff <= 7:
                        recent_batches.append(batch)
                except:
                    continue
                    
            if not recent_batches:
                self.print_info("No recent batches found for quality checking.")
                return
                
            print(f"\n[ORDER] Recent Batches ({len(recent_batches)} batches):")
            print("-" * 100)
            print(f"{'#':<3} {'Batch ID':<20} {'Product ID':<15} {'Quantity':<10} {'Quality':<15} {'Location':<15}")
            print("-" * 100)
            
            for i, batch in enumerate(recent_batches, 1):
                print(f"{i:<3} {batch.get('batchId', 'N/A'):<20} "
                      f"{batch.get('productId', 'N/A'):<15} "
                      f"{batch.get('currentQuantity', 0):<10} "
                      f"{batch.get('qualityStatus', 'N/A'):<15} "
                      f"{batch.get('location', 'N/A'):<15}")
                      
            print("-" * 100)
            
            try:
                choice = input(f"\n[TARGET] Select batch number for quality check (1-{len(recent_batches)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(recent_batches):
                    selected_batch = recent_batches[choice_num - 1]
                    self.perform_detailed_quality_check(selected_batch)
                else:
                    self.print_error("Invalid batch selection.")
                    
            except ValueError:
                self.print_error("Invalid number.")
                
        except Exception as e:
            self.print_error(f"Error in quality check: {str(e)}")
            
    def perform_detailed_quality_check(self, batch: Dict[str, Any]):
        """Perform detailed quality check on a specific batch"""
        try:
            batch_id = batch.get('batchId')
            product_id = batch.get('productId')
            current_qty = batch.get('currentQuantity', 0)
            
            print(f"\n[AUDIT] Detailed Quality Check")
            print(f"[ORDER] Batch ID: {batch_id}")
            print(f"[ID] Product ID: {product_id}")
            print(f"[TRACK] Current Quantity: {current_qty}")
            print(f"🌡️ Storage Temperature: {batch.get('temperature', 'N/A')}°C")
            print(f"⏰ Expiry Date: {batch.get('expiryDate', 'N/A')}")
            
            # Quality checks
            print(f"\n[AUDIT] Quality Inspection Checklist:")
            
            # Visual inspection
            visual_check = input("[VIEW] Visual inspection passed? (yes/no): ").strip().lower()
            
            # Expiry check
            expiry_check = input("⏰ Expiry date check passed? (yes/no): ").strip().lower()
            
            # Packaging check
            packaging_check = input("[ORDER] Packaging integrity check passed? (yes/no): ").strip().lower()
            
            # Temperature check
            temp_check = input("🌡️ Temperature requirements met? (yes/no): ").strip().lower()
            
            # Count verification
            count_verification = input("[TRACK] Physical count matches record? (yes/no): ").strip().lower()
            
            # Calculate overall quality score
            checks = [visual_check, expiry_check, packaging_check, temp_check, count_verification]
            passed_checks = sum(1 for check in checks if check == 'yes')
            quality_score = (passed_checks / len(checks)) * 100
            
            # Determine quality status
            if quality_score >= 90:
                new_quality_status = 'EXCELLENT'
            elif quality_score >= 75:
                new_quality_status = 'GOOD'
            elif quality_score >= 60:
                new_quality_status = 'FAIR'
            elif quality_score >= 40:
                new_quality_status = 'POOR'
            else:
                new_quality_status = 'REJECTED'
                
            # Get any issues found
            issues_found = input("[GENERATE] Issues found (if any): ").strip()
            
            # Update batch quality status
            self.batches_table.update_item(
                Key={'batchId': batch_id, 'productId': product_id},
                UpdateExpression='SET qualityStatus = :status, qualityScore = :score, lastQualityCheck = :check_date, qualityIssues = :issues, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':status': new_quality_status,
                    ':score': Decimal(str(quality_score)),
                    ':check_date': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':issues': issues_found,
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Log audit
            self.log_audit('BATCH_QUALITY_CHECK', batch_id, 
                          f"Quality check completed: {new_quality_status} ({quality_score:.1f}% score)")
            
            # Display results
            self.print_success("[SUCCESS] Quality Check Completed!")
            print(f"\n[TRACK] Quality Check Results:")
            print(f"   [ORDER] Batch: {batch_id}")
            print(f"   [TRACK] Quality Score: {quality_score:.1f}%")
            print(f"   [SUCCESS] Quality Status: {new_quality_status}")
            print(f"   [AUDIT] Checks Passed: {passed_checks}/{len(checks)}")
            if issues_found:
                print(f"   [INTERRUPTED] Issues: {issues_found}")
            print(f"   [USER] Checked by: {self.current_user.get('name', 'Unknown')}")
            
        except Exception as e:
            self.print_error(f"Error in detailed quality check: {str(e)}")
            
    def verify_received_quantity(self):
        """Verify quantities of recently received products"""
        try:
            print("[TRACK] Quantity Verification System")
            print("[NOTE] Verify that received quantities match delivery documents")
            
            # Get recent stock movements for verification
            print("\n[AUDIT] Recent Stock Receipts (Last 24 hours):")
            
            # This would typically query recent audit logs
            # For demo, we'll create a verification process
            
            product_id = input("\n[ID] Product ID to verify: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            # Get expected quantity from delivery documents
            expected_qty = input("[CLIPBOARD] Expected quantity (from delivery documents): ").strip()
            if not expected_qty.isdigit():
                self.print_error("Invalid expected quantity")
                return
            expected_qty = int(expected_qty)
            
            # Physical count
            actual_qty = input("[TRACK] Actual counted quantity: ").strip()
            if not actual_qty.isdigit():
                self.print_error("Invalid actual quantity")
                return
            actual_qty = int(actual_qty)
            
            # Calculate variance
            variance = actual_qty - expected_qty
            variance_percent = (variance / expected_qty * 100) if expected_qty > 0 else 0
            
            # Determine verification status
            if variance == 0:
                verification_status = 'EXACT_MATCH'
            elif abs(variance_percent) <= 2:  # 2% tolerance
                verification_status = 'WITHIN_TOLERANCE'
            elif variance > 0:
                verification_status = 'OVERAGE'
            else:
                verification_status = 'SHORTAGE'
                
            # Get verification notes
            notes = input("[GENERATE] Verification notes (reason for any variance): ").strip()
            
            # Create verification record
            verification_record = {
                'verificationId': f'VER-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'productId': product_id,
                'expectedQuantity': expected_qty,
                'actualQuantity': actual_qty,
                'variance': variance,
                'variancePercent': round(variance_percent, 2),
                'verificationStatus': verification_status,
                'notes': notes,
                'verifiedBy': self.current_user.get('userId'),
                'verifiedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Log audit
            self.log_audit('QUANTITY_VERIFICATION', product_id, 
                          f"Quantity verification: Expected {expected_qty}, Actual {actual_qty}, Variance {variance}")
            
            # Display results
            self.print_success("[SUCCESS] Quantity Verification Completed!")
            print(f"\n[TRACK] Verification Results:")
            print(f"   [ID] Product ID: {product_id}")
            print(f"   [CLIPBOARD] Expected Quantity: {expected_qty}")
            print(f"   [TRACK] Actual Quantity: {actual_qty}")
            print(f"   [REPORT] Variance: {variance} ({variance_percent:+.1f}%)")
            print(f"   [SUCCESS] Status: {verification_status}")
            if notes:
                print(f"   [GENERATE] Notes: {notes}")
            print(f"   [USER] Verified by: {self.current_user.get('name', 'Unknown')}")
            
            # Recommend actions based on variance
            if verification_status == 'SHORTAGE':
                print(f"\n[INTERRUPTED] Recommended Actions:")
                print(f"   • Contact supplier about shortage")
                print(f"   • Check for delivery errors")
                print(f"   • Review receiving process")
            elif verification_status == 'OVERAGE':
                print(f"\n[NOTE] Recommended Actions:")
                print(f"   • Verify delivery documents")
                print(f"   • Contact supplier about overage")
                print(f"   • Update inventory records")
                
        except Exception as e:
            self.print_error(f"Error in quantity verification: {str(e)}")
            
    def assess_product_damage(self):
        """Assess and record product damage"""
        try:
            print("[AUDIT] Product Damage Assessment")
            print("[NOTE] Record damage details for insurance and quality control")
            
            product_id = input("\n[ID] Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            batch_number = input("[ORDER] Batch Number (if applicable): ").strip()
            
            # Damage assessment
            print(f"\n[AUDIT] Damage Assessment:")
            print("1. Physical Damage - Dents, cracks, breaks")
            print("2. Packaging Damage - Torn, wet, opened packages")
            print("3. Quality Issues - Spoilage, contamination")
            print("4. Missing Items - Incomplete delivery")
            print("5. Wrong Product - Incorrect items delivered")
            
            damage_type_choice = input("\n[TARGET] Select damage type (1-5): ").strip()
            damage_type_map = {
                '1': 'PHYSICAL_DAMAGE',
                '2': 'PACKAGING_DAMAGE',
                '3': 'QUALITY_ISSUES',
                '4': 'MISSING_ITEMS',
                '5': 'WRONG_PRODUCT'
            }
            
            if damage_type_choice not in damage_type_map:
                self.print_error("Invalid damage type selection")
                return
                
            damage_type = damage_type_map[damage_type_choice]
            
            # Damage severity
            print(f"\n[TRACK] Damage Severity:")
            print("1. Minor - Cosmetic damage, still usable")
            print("2. Moderate - Some functionality affected")
            print("3. Major - Significantly compromised")
            print("4. Total Loss - Completely unusable")
            
            severity_choice = input("\n[TARGET] Select severity (1-4): ").strip()
            severity_map = {
                '1': 'MINOR',
                '2': 'MODERATE',
                '3': 'MAJOR',
                '4': 'TOTAL_LOSS'
            }
            
            if severity_choice not in severity_map:
                self.print_error("Invalid severity selection")
                return
                
            damage_severity = severity_map[severity_choice]
            
            # Damage details
            damaged_qty = input("[TRACK] Quantity of damaged items: ").strip()
            if not damaged_qty.isdigit():
                self.print_error("Invalid damaged quantity")
                return
            damaged_qty = int(damaged_qty)
            
            total_qty = input("[TRACK] Total quantity in batch/delivery: ").strip()
            if not total_qty.isdigit():
                self.print_error("Invalid total quantity")
                return
            total_qty = int(total_qty)
            
            # Damage description
            damage_description = input("[GENERATE] Detailed damage description: ").strip()
            
            # Cause of damage
            print(f"\n[AUDIT] Suspected Cause:")
            print("1. Shipping/Transport")
            print("2. Handling")
            print("3. Storage Conditions")
            print("4. Manufacturing Defect")
            print("5. Unknown")
            
            cause_choice = input("\n[TARGET] Select cause (1-5): ").strip()
            cause_map = {
                '1': 'SHIPPING_TRANSPORT',
                '2': 'HANDLING',
                '3': 'STORAGE_CONDITIONS',
                '4': 'MANUFACTURING_DEFECT',
                '5': 'UNKNOWN'
            }
            
            damage_cause = cause_map.get(cause_choice, 'UNKNOWN')
            
            # Financial impact
            unit_cost = input("[PRICE] Unit cost (if known): ").strip()
            if unit_cost and unit_cost.replace('.', '').isdigit():
                financial_impact = float(unit_cost) * damaged_qty
            else:
                financial_impact = 0
                
            # Photos/documentation
            photos_taken = input("📸 Photos taken for documentation? (yes/no): ").strip().lower()
            
            # Action required
            print(f"\n[TOOL] Action Required:")
            print("1. Return to Supplier")
            print("2. Dispose/Destroy")
            print("3. Repair/Refurbish")
            print("4. Sell as Damaged")
            print("5. Insurance Claim")
            
            action_choice = input("\n[TARGET] Select action (1-5): ").strip()
            action_map = {
                '1': 'RETURN_TO_SUPPLIER',
                '2': 'DISPOSE_DESTROY',
                '3': 'REPAIR_REFURBISH',
                '4': 'SELL_AS_DAMAGED',
                '5': 'INSURANCE_CLAIM'
            }
            
            required_action = action_map.get(action_choice, 'PENDING_DECISION')
            
            # Create damage assessment record
            damage_record = {
                'damageId': f'DMG-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'productId': product_id,
                'batchNumber': batch_number or 'NO_BATCH',
                'damageType': damage_type,
                'damageSeverity': damage_severity,
                'damagedQuantity': damaged_qty,
                'totalQuantity': total_qty,
                'damagePercent': round((damaged_qty / total_qty * 100), 2) if total_qty > 0 else 0,
                'damageDescription': damage_description,
                'suspectedCause': damage_cause,
                'financialImpact': financial_impact,
                'photosDocumented': photos_taken == 'yes',
                'requiredAction': required_action,
                'assessedBy': self.current_user.get('userId'),
                'assessedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'status': 'ASSESSMENT_COMPLETE',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Update stock levels to reflect damage
            self.update_stock_for_damage(product_id, damaged_qty, damage_severity)
            
            # Log audit
            self.log_audit('DAMAGE_ASSESSMENT', product_id, 
                          f"Damage assessment: {damaged_qty} units, {damage_severity} {damage_type}")
            
            # Display assessment summary
            self.print_success("[SUCCESS] Damage Assessment Completed!")
            print(f"\n[TRACK] Damage Assessment Summary:")
            print(f"   [ID] Product ID: {product_id}")
            print(f"   [AUDIT] Damage Type: {damage_type}")
            print(f"   [TRACK] Severity: {damage_severity}")
            print(f"   [TRACK] Damaged Quantity: {damaged_qty}/{total_qty} ({(damaged_qty/total_qty*100):.1f}%)")
            print(f"   [PRICE] Financial Impact: ₹{financial_impact:.2f}")
            print(f"   [TOOL] Required Action: {required_action}")
            print(f"   [USER] Assessed by: {self.current_user.get('name', 'Unknown')}")
            
            # Recommend next steps
            print(f"\n[NOTE] Next Steps:")
            if required_action == 'RETURN_TO_SUPPLIER':
                print(f"   • Contact supplier for return authorization")
                print(f"   • Prepare return documentation")
            elif required_action == 'INSURANCE_CLAIM':
                print(f"   • Contact insurance provider")
                print(f"   • Submit claim documentation")
            elif required_action == 'DISPOSE_DESTROY':
                print(f"   • Follow disposal procedures")
                print(f"   • Update inventory records")
                
        except Exception as e:
            self.print_error(f"Error in damage assessment: {str(e)}")
            
    def update_stock_after_quality_check(self, product_id: str, location: str, total_qty: int, damaged_qty: int, quality_status: str):
        """Update stock levels after quality check"""
        try:
            # Update stock levels to reflect quality assessment
            stock_key = f"{location}#null#PCS"
            
            # Calculate usable quantity
            usable_qty = total_qty - damaged_qty
            
            # Update or create stock record
            response = self.stock_levels_table.get_item(
                Key={'productId': product_id, 'location': stock_key}
            )
            
            if 'Item' in response:
                # Update existing record
                self.stock_levels_table.update_item(
                    Key={'productId': product_id, 'location': stock_key},
                    UpdateExpression='SET availableStock = :available, damagedStock = :damaged, lastUpdated = :updated',
                    ExpressionAttributeValues={
                        ':available': usable_qty,
                        ':damaged': damaged_qty,
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                    
        except Exception as e:
            self.print_error(f"Error updating stock after quality check: {str(e)}")
            
    def update_stock_for_damage(self, product_id: str, damaged_qty: int, severity: str):
        """Update stock levels to reflect damage"""
        try:
            # Find all stock records for this product
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            stock_items = response.get('Items', [])
            
            for item in stock_items:
                current_available = item.get('availableStock', 0)
                current_damaged = item.get('damagedStock', 0)
                
                # Move stock from available to damaged
                new_available = max(0, current_available - damaged_qty)
                new_damaged = current_damaged + damaged_qty
                
                self.stock_levels_table.update_item(
                    Key={'productId': product_id, 'location': item.get('location')},
                    UpdateExpression='SET availableStock = :available, damagedStock = :damaged, lastUpdated = :updated',
                    ExpressionAttributeValues={
                        ':available': new_available,
                        ':damaged': new_damaged,
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                break  # Update first matching record
                
        except Exception as e:
            self.print_error(f"Error updating stock for damage: {str(e)}")
            
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"[INTERRUPTED]  {message}")
        
    def update_stock_locations(self):
        """Update stock locations for received products"""
        self.clear_screen()
        self.print_header("UPDATE STOCK LOCATIONS")
        
        try:
            print("[ADDRESS] Stock Location Management System")
            print("[NOTE] Assign and update storage locations for products")
            
            print("\n[CLIPBOARD] Location Management Options:")
            print("1. Update Product Location")
            print("2. Move Stock Between Locations")
            print("3. View Current Stock Locations")
            print("4. Create New Storage Location")
            
            choice = input("\n[TARGET] Select operation (1-4): ").strip()
            
            if choice == '1':
                self.update_product_location()
            elif choice == '2':
                self.move_stock_between_locations()
            elif choice == '3':
                self.view_current_stock_locations()
            elif choice == '4':
                self.create_new_storage_location()
            else:
                self.print_error("Invalid choice.")
                
        except Exception as e:
            self.print_error(f"Error in stock location update: {str(e)}")
            
        input("Press Enter to continue...")
        
    def update_product_location(self):
        """Update storage location for a specific product"""
        try:
            # Get product to relocate
            product_id = input("\n[ID] Enter Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            # Find current stock locations for this product
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            stock_items = response.get('Items', [])
            
            if not stock_items:
                self.print_error("No stock found for this product")
                return
                
            # Display current locations
            print(f"\n[ADDRESS] Current Stock Locations for {product_id}:")
            print("-" * 80)
            print(f"{'#':<3} {'Location':<20} {'Available':<12} {'Damaged':<10} {'Reserved':<10} {'Total':<10}")
            print("-" * 80)
            
            for i, item in enumerate(stock_items, 1):
                location = item.get('location', 'Unknown').split('#')[0]  # Extract location part
                print(f"{i:<3} {location:<20} "
                      f"{item.get('availableStock', 0):<12} "
                      f"{item.get('damagedStock', 0):<10} "
                      f"{item.get('reservedStock', 0):<10} "
                      f"{item.get('totalStock', 0):<10}")
                      
            print("-" * 80)
            
            # Select location to update
            if len(stock_items) == 1:
                selected_item = stock_items[0]
            else:
                try:
                    choice = input(f"\n[TARGET] Select location to update (1-{len(stock_items)}): ").strip()
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(stock_items):
                        selected_item = stock_items[choice_num - 1]
                    else:
                        self.print_error("Invalid location selection")
                        return
                except ValueError:
                    self.print_error("Invalid number")
                    return
                    
            current_location = selected_item.get('location', '')
            current_location_name = current_location.split('#')[0]
            
            print(f"\n[ADDRESS] Current Location: {current_location_name}")
            
            # Get new location
            new_location = self.get_location_selection()
            
            if new_location == current_location_name:
                self.print_info("Product is already in the selected location.")
                return
                
            # Confirm the move
            print(f"\n[CLIPBOARD] Location Update Summary:")
            print(f"   [ID] Product ID: {product_id}")
            print(f"   [ADDRESS] From: {current_location_name}")
            print(f"   [ADDRESS] To: {new_location}")
            print(f"   [TRACK] Stock to Move: {selected_item.get('totalStock', 0)} units")
            
            confirm = input("\n[CONFIRM] Confirm location update? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Create new stock record for new location
                new_stock_key = f"{new_location}#null#{selected_item.get('unitId', 'PCS')}"
                
                # Check if record already exists at new location
                try:
                    existing_response = self.stock_levels_table.get_item(
                        Key={'productId': product_id, 'location': new_stock_key}
                    )
                    
                    if 'Item' in existing_response:
                        # Merge with existing stock
                        existing_item = existing_response['Item']
                        new_total = existing_item.get('totalStock', 0) + selected_item.get('totalStock', 0)
                        new_available = existing_item.get('availableStock', 0) + selected_item.get('availableStock', 0)
                        new_damaged = existing_item.get('damagedStock', 0) + selected_item.get('damagedStock', 0)
                        new_reserved = existing_item.get('reservedStock', 0) + selected_item.get('reservedStock', 0)
                        
                        self.stock_levels_table.update_item(
                            Key={'productId': product_id, 'location': new_stock_key},
                            UpdateExpression='SET totalStock = :total, availableStock = :available, damagedStock = :damaged, reservedStock = :reserved, lastUpdated = :updated',
                            ExpressionAttributeValues={
                                ':total': new_total,
                                ':available': new_available,
                                ':damaged': new_damaged,
                                ':reserved': new_reserved,
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                    else:
                        # Create new record
                        new_stock_item = {
                            'productId': product_id,
                            'location': new_stock_key,
                            'variantId': selected_item.get('variantId'),
                            'unitId': selected_item.get('unitId', 'PCS'),
                            'totalStock': selected_item.get('totalStock', 0),
                            'availableStock': selected_item.get('availableStock', 0),
                            'reservedStock': selected_item.get('reservedStock', 0),
                            'damagedStock': selected_item.get('damagedStock', 0),
                            'expiredStock': selected_item.get('expiredStock', 0),
                            'baseUnitQuantity': selected_item.get('baseUnitQuantity', Decimal('0')),
                            'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                        
                        self.stock_levels_table.put_item(Item=new_stock_item)
                        
                    # Delete old record
                    self.stock_levels_table.delete_item(
                        Key={'productId': product_id, 'location': current_location}
                    )
                    
                    # Log audit
                    self.log_audit('STOCK_RELOCATION', product_id, 
                                  f"Moved stock from {current_location_name} to {new_location}")
                    
                    self.print_success("[SUCCESS] Stock location updated successfully!")
                    print(f"   [ORDER] Product: {product_id}")
                    print(f"   [ADDRESS] New Location: {new_location}")
                    print(f"   [TRACK] Quantity Moved: {selected_item.get('totalStock', 0)} units")
                    
                except Exception as e:
                    self.print_error(f"Error updating stock location: {str(e)}")
            else:
                self.print_info("Location update cancelled.")
                
        except Exception as e:
            self.print_error(f"Error in product location update: {str(e)}")
            
    def move_stock_between_locations(self):
        """Move specific quantities between locations"""
        try:
            print("\n[FLOW] Stock Transfer Between Locations")
            
            # Get product details
            product_id = input("[ID] Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            # Get current stock locations
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            stock_items = response.get('Items', [])
            
            if not stock_items:
                self.print_error("No stock found for this product")
                return
                
            # Display available locations
            print(f"\n[ADDRESS] Available Source Locations:")
            print("-" * 60)
            print(f"{'#':<3} {'Location':<20} {'Available Stock':<15}")
            print("-" * 60)
            
            available_locations = []
            for i, item in enumerate(stock_items, 1):
                location_name = item.get('location', 'Unknown').split('#')[0]
                available_stock = item.get('availableStock', 0)
                if available_stock > 0:
                    available_locations.append(item)
                    print(f"{len(available_locations):<3} {location_name:<20} {available_stock:<15}")
                    
            print("-" * 60)
            
            if not available_locations:
                self.print_info("No locations with available stock found")
                return
                
            # Select source location
            try:
                source_choice = input(f"\n[TARGET] Select source location (1-{len(available_locations)}): ").strip()
                source_index = int(source_choice) - 1
                
                if 0 <= source_index < len(available_locations):
                    source_item = available_locations[source_index]
                else:
                    self.print_error("Invalid source location selection")
                    return
            except ValueError:
                self.print_error("Invalid number")
                return
                
            source_location = source_item.get('location', '').split('#')[0]
            available_qty = source_item.get('availableStock', 0)
            
            # Get quantity to move
            move_qty_str = input(f"[TRACK] Quantity to move (max {available_qty}): ").strip()
            if not move_qty_str.isdigit():
                self.print_error("Invalid quantity")
                return
                
            move_qty = int(move_qty_str)
            if move_qty <= 0 or move_qty > available_qty:
                self.print_error("Invalid quantity amount")
                return
                
            # Get destination location
            print(f"\n[ADDRESS] Select Destination Location:")
            dest_location = self.get_location_selection()
            
            if dest_location == source_location:
                self.print_error("Source and destination cannot be the same")
                return
                
            # Confirm transfer
            print(f"\n[CLIPBOARD] Stock Transfer Summary:")
            print(f"   [ID] Product: {product_id}")
            print(f"   [ADDRESS] From: {source_location}")
            print(f"   [ADDRESS] To: {dest_location}")
            print(f"   [TRACK] Quantity: {move_qty} units")
            
            confirm = input("\n[CONFIRM] Confirm stock transfer? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Update source location (reduce stock)
                self.stock_levels_table.update_item(
                    Key={'productId': product_id, 'location': source_item.get('location')},
                    UpdateExpression='SET availableStock = availableStock - :qty, totalStock = totalStock - :qty, lastUpdated = :updated',
                    ExpressionAttributeValues={
                        ':qty': move_qty,
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                
                # Update or create destination location
                dest_stock_key = f"{dest_location}#null#{source_item.get('unitId', 'PCS')}"
                
                try:
                    dest_response = self.stock_levels_table.get_item(
                        Key={'productId': product_id, 'location': dest_stock_key}
                    )
                    
                    if 'Item' in dest_response:
                        # Update existing destination
                        self.stock_levels_table.update_item(
                            Key={'productId': product_id, 'location': dest_stock_key},
                            UpdateExpression='SET availableStock = availableStock + :qty, totalStock = totalStock + :qty, lastUpdated = :updated',
                            ExpressionAttributeValues={
                                ':qty': move_qty,
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                    else:
                        # Create new destination record
                        new_dest_item = {
                            'productId': product_id,
                            'location': dest_stock_key,
                            'variantId': source_item.get('variantId'),
                            'unitId': source_item.get('unitId', 'PCS'),
                            'totalStock': move_qty,
                            'availableStock': move_qty,
                            'reservedStock': 0,
                            'damagedStock': 0,
                            'expiredStock': 0,
                            'baseUnitQuantity': Decimal(str(move_qty)),
                            'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                        
                        self.stock_levels_table.put_item(Item=new_dest_item)
                        
                    # Log audit
                    self.log_audit('STOCK_TRANSFER', product_id, 
                                  f"Transferred {move_qty} units from {source_location} to {dest_location}")
                    
                    self.print_success("[SUCCESS] Stock transfer completed successfully!")
                    print(f"   [ORDER] Product: {product_id}")
                    print(f"   [TRACK] Transferred: {move_qty} units")
                    print(f"   [ADDRESS] From: {source_location}")
                    print(f"   [ADDRESS] To: {dest_location}")
                    
                except Exception as e:
                    self.print_error(f"Error during stock transfer: {str(e)}")
            else:
                self.print_info("Stock transfer cancelled.")
                
        except Exception as e:
            self.print_error(f"Error in stock transfer: {str(e)}")
            
    def view_current_stock_locations(self):
        """View current stock distribution across locations"""
        try:
            print("\n[ADDRESS] Current Stock Locations Overview")
            
            # Option to view by product or by location
            print("\n[AUDIT] View Options:")
            print("1. View by Product")
            print("2. View by Location")
            print("3. View All Stock")
            
            view_choice = input("\n[TARGET] Select view (1-3): ").strip()
            
            if view_choice == '1':
                self.view_stock_by_product()
            elif view_choice == '2':
                self.view_stock_by_location()
            elif view_choice == '3':
                self.view_all_stock_locations()
            else:
                self.print_error("Invalid choice")
                
        except Exception as e:
            self.print_error(f"Error viewing stock locations: {str(e)}")
            
    def view_stock_by_product(self):
        """View stock locations for a specific product"""
        try:
            product_id = input("\n[ID] Enter Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                return
                
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            stock_items = response.get('Items', [])
            
            if not stock_items:
                self.print_info(f"No stock found for product {product_id}")
                return
                
            print(f"\n[ORDER] Stock Locations for Product: {product_id}")
            print("-" * 100)
            print(f"{'Location':<20} {'Total':<10} {'Available':<12} {'Reserved':<10} {'Damaged':<10} {'Expired':<10}")
            print("-" * 100)
            
            total_stock = 0
            total_available = 0
            
            for item in stock_items:
                location = item.get('location', 'Unknown').split('#')[0]
                total = item.get('totalStock', 0)
                available = item.get('availableStock', 0)
                reserved = item.get('reservedStock', 0)
                damaged = item.get('damagedStock', 0)
                expired = item.get('expiredStock', 0)
                
                print(f"{location:<20} {total:<10} {available:<12} {reserved:<10} {damaged:<10} {expired:<10}")
                
                total_stock += total
                total_available += available
                
            print("-" * 100)
            print(f"{'TOTAL':<20} {total_stock:<10} {total_available:<12}")
            print("-" * 100)
            
        except Exception as e:
            self.print_error(f"Error viewing stock by product: {str(e)}")
            
    def view_stock_by_location(self):
        """View all stock in a specific location"""
        try:
            # Show available locations
            response = self.stock_levels_table.scan()
            all_items = response.get('Items', [])
            
            locations = set()
            for item in all_items:
                location = item.get('location', '').split('#')[0]
                if location:
                    locations.add(location)
                    
            locations = sorted(list(locations))
            
            if not locations:
                self.print_info("No stock locations found")
                return
                
            print(f"\n[ADDRESS] Available Locations:")
            for i, location in enumerate(locations, 1):
                print(f"{i}. {location}")
                
            try:
                choice = input(f"\n[TARGET] Select location (1-{len(locations)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(locations):
                    selected_location = locations[choice_num - 1]
                else:
                    self.print_error("Invalid location selection")
                    return
            except ValueError:
                self.print_error("Invalid number")
                return
                
            # Get stock for selected location
            location_items = [item for item in all_items 
                            if item.get('location', '').split('#')[0] == selected_location]
            
            if not location_items:
                self.print_info(f"No stock found in location {selected_location}")
                return
                
            print(f"\n[ADDRESS] Stock in Location: {selected_location}")
            print("-" * 100)
            print(f"{'Product ID':<15} {'Total':<10} {'Available':<12} {'Reserved':<10} {'Damaged':<10} {'Unit':<8}")
            print("-" * 100)
            
            for item in location_items:
                product_id = item.get('productId', 'Unknown')
                total = item.get('totalStock', 0)
                available = item.get('availableStock', 0)
                reserved = item.get('reservedStock', 0)
                damaged = item.get('damagedStock', 0)
                unit = item.get('unitId', 'N/A')
                
                print(f"{product_id:<15} {total:<10} {available:<12} {reserved:<10} {damaged:<10} {unit:<8}")
                
            print("-" * 100)
            
        except Exception as e:
            self.print_error(f"Error viewing stock by location: {str(e)}")
            
    def view_all_stock_locations(self):
        """View all stock across all locations"""
        try:
            response = self.stock_levels_table.scan()
            all_items = response.get('Items', [])
            
            if not all_items:
                self.print_info("No stock records found")
                return
                
            print(f"\n[TRACK] All Stock Locations ({len(all_items)} records)")
            print("-" * 120)
            print(f"{'Product ID':<15} {'Location':<20} {'Total':<8} {'Available':<10} {'Reserved':<8} {'Damaged':<8} {'Unit':<6}")
            print("-" * 120)
            
            # Group by location for better readability
            by_location = {}
            for item in all_items:
                location = item.get('location', 'Unknown').split('#')[0]
                if location not in by_location:
                    by_location[location] = []
                by_location[location].append(item)
                
            for location in sorted(by_location.keys()):
                print(f"\n[ADDRESS] {location.upper()}:")
                for item in by_location[location]:
                    product_id = item.get('productId', 'Unknown')
                    total = item.get('totalStock', 0)
                    available = item.get('availableStock', 0)
                    reserved = item.get('reservedStock', 0)
                    damaged = item.get('damagedStock', 0)
                    unit = item.get('unitId', 'N/A')
                    
                    print(f"  {product_id:<13} {'':<20} {total:<8} {available:<10} {reserved:<8} {damaged:<8} {unit:<6}")
                    
            print("-" * 120)
            
        except Exception as e:
            self.print_error(f"Error viewing all stock locations: {str(e)}")
            
    def create_new_storage_location(self):
        """Create a new storage location"""
        try:
            print("\n🏗️ Create New Storage Location")
            
            # Get location details
            location_id = input("[ID] Location ID (e.g., ZONE_A_RACK_1): ").strip().upper()
            if not location_id:
                self.print_error("Location ID is required")
                return
                
            location_name = input("[GENERATE] Location Name: ").strip()
            if not location_name:
                location_name = location_id
                
            # Location type
            print(f"\n[CATEGORY] Location Type:")
            print("1. WAREHOUSE - General warehouse storage")
            print("2. COLD_STORAGE - Refrigerated storage")
            print("3. DRY_STORAGE - Dry goods storage")
            print("4. QUARANTINE - Quality check area")
            print("5. RETURNS - Returns processing")
            print("6. STAGING - Temporary staging area")
            
            type_choice = input("\n[TARGET] Select type (1-6): ").strip()
            type_map = {
                '1': 'WAREHOUSE',
                '2': 'COLD_STORAGE',
                '3': 'DRY_STORAGE',
                '4': 'QUARANTINE',
                '5': 'RETURNS',
                '6': 'STAGING'
            }
            
            location_type = type_map.get(type_choice, 'WAREHOUSE')
            
            # Additional details
            capacity = input("[TRACK] Storage Capacity (optional): ").strip()
            temperature_range = input("🌡️ Temperature Range (optional): ").strip()
            special_requirements = input("[INTERRUPTED] Special Requirements (optional): ").strip()
            
            # Create location record (this would typically go in a Locations table)
            location_record = {
                'locationId': location_id,
                'locationName': location_name,
                'locationType': location_type,
                'capacity': capacity or 'UNLIMITED',
                'temperatureRange': temperature_range or 'AMBIENT',
                'specialRequirements': special_requirements or 'NONE',
                'isActive': True,
                'createdBy': self.current_user.get('userId'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Log the creation (since we don't have a locations table, we'll log it)
            self.log_audit('LOCATION_CREATE', location_id, 
                          f"Created new storage location: {location_name} ({location_type})")
            
            self.print_success("[SUCCESS] Storage location created successfully!")
            print(f"\n[ADDRESS] Location Details:")
            print(f"   [ID] Location ID: {location_id}")
            print(f"   [GENERATE] Name: {location_name}")
            print(f"   [CATEGORY] Type: {location_type}")
            print(f"   [TRACK] Capacity: {capacity or 'Unlimited'}")
            print(f"   🌡️ Temperature: {temperature_range or 'Ambient'}")
            if special_requirements:
                print(f"   [INTERRUPTED] Requirements: {special_requirements}")
            print(f"   [USER] Created by: {self.current_user.get('name', 'Unknown')}")
            
            print(f"\n[NOTE] Location Usage:")
            print(f"   • Use location ID '{location_id}' when receiving products")
            print(f"   • Location is now available in stock movement operations")
            print(f"   • Update product assignments to utilize this location")
            
        except Exception as e:
            self.print_error(f"Error creating storage location: {str(e)}")
        
    def pick_products_for_orders(self):
        """Pick products for customer orders"""
        self.clear_screen()
        self.print_header("PICK PRODUCTS FOR ORDERS")
        
        try:
            print("[ORDER] Order Picking System")
            print("[NOTE] Select and prepare products for customer orders")
            
            # Get orders that need picking
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            # Filter orders that need picking (CONFIRMED, PENDING, or PROCESSING status)
            pickable_orders = [order for order in orders 
                              if order.get('status') in ['CONFIRMED', 'PENDING', 'PROCESSING']]
            
            if not pickable_orders:
                self.print_info("No orders available for picking.")
                input("Press Enter to continue...")
                return
                
            print(f"\n[CLIPBOARD] Orders Available for Picking ({len(pickable_orders)} orders):")
            print("-" * 120)
            print(f"{'#':<3} {'Order ID':<20} {'Customer':<15} {'Items':<8} {'Priority':<10} {'Order Date':<12} {'Amount':<10}")
            print("-" * 120)
            
            for i, order in enumerate(pickable_orders, 1):
                items_count = len(order.get('items', []))
                order_date = order.get('orderDate', 'N/A')[:10] if order.get('orderDate') else 'N/A'
                priority = order.get('priority', 'NORMAL')
                amount = order.get('totalAmount', 0)
                
                print(f"{i:<3} {order.get('orderId', 'N/A'):<20} "
                      f"{order.get('customerId', 'N/A'):<15} "
                      f"{items_count:<8} "
                      f"{priority:<10} "
                      f"{order_date:<12} "
                      f"₹{amount:<9}")
                      
            print("-" * 120)
            
            # Select order to pick
            try:
                choice = input(f"\n[TARGET] Select order to pick (1-{len(pickable_orders)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(pickable_orders):
                    selected_order = pickable_orders[choice_num - 1]
                    self.process_order_picking(selected_order)
                else:
                    self.print_error("Invalid order selection.")
            except ValueError:
                self.print_error("Invalid number.")
                
        except Exception as e:
            self.print_error(f"Error in order picking: {str(e)}")
            
        input("Press Enter to continue...")
        
    def process_order_picking(self, order: Dict[str, Any]):
        """Process picking for a specific order"""
        try:
            order_id = order.get('orderId')
            customer_id = order.get('customerId')
            order_items = order.get('items', [])
            
            print(f"\n[ORDER] Processing Order Picking: {order_id}")
            print(f"[USER] Customer: {customer_id}")
            print(f"[DATE] Order Date: {order.get('orderDate', 'N/A')[:10]}")
            print(f"[DELIVERY] Delivery Date: {order.get('deliveryDate', 'N/A')}")
            print(f"[PRICE] Total Amount: ₹{order.get('totalAmount', 0)}")
            
            if not order_items:
                self.print_warning("No items found in this order.")
                return
                
            # Display picking list
            print(f"\n[CLIPBOARD] Picking List ({len(order_items)} items):")
            print("-" * 100)
            print(f"{'#':<3} {'Product ID':<15} {'Product Name':<25} {'Qty Req':<8} {'Location':<15} {'Status':<10}")
            print("-" * 100)
            
            picking_results = []
            
            for i, item in enumerate(order_items, 1):
                product_id = item.get('productId', 'N/A')
                product_name = item.get('name', 'Unknown')
                required_qty = item.get('quantity', 0)
                
                # Find stock location for this product
                stock_location = self.find_best_stock_location(product_id, required_qty)
                location_name = stock_location.get('location', 'NOT_FOUND').split('#')[0] if stock_location else 'NOT_FOUND'
                available_qty = stock_location.get('availableStock', 0) if stock_location else 0
                
                # Determine picking status
                if available_qty >= required_qty:
                    status = "AVAILABLE"
                elif available_qty > 0:
                    status = "PARTIAL"
                else:
                    status = "OUT_OF_STOCK"
                    
                print(f"{i:<3} {product_id:<15} {product_name[:24]:<25} "
                      f"{required_qty:<8} {location_name:<15} {status:<10}")
                
                picking_results.append({
                    'item': item,
                    'stock_location': stock_location,
                    'location_name': location_name,
                    'available_qty': available_qty,
                    'status': status
                })
                
            print("-" * 100)
            
            # Check if all items can be picked
            out_of_stock_items = [r for r in picking_results if r['status'] == 'OUT_OF_STOCK']
            partial_items = [r for r in picking_results if r['status'] == 'PARTIAL']
            
            if out_of_stock_items:
                print(f"\n[INTERRUPTED] Stock Issues Found:")
                for result in out_of_stock_items:
                    print(f"   [ERROR] {result['item'].get('name', 'Unknown')}: Out of stock")
                    
            if partial_items:
                print(f"\n[INTERRUPTED] Partial Stock Available:")
                for result in partial_items:
                    print(f"   🔶 {result['item'].get('name', 'Unknown')}: "
                          f"Need {result['item'].get('quantity', 0)}, Available {result['available_qty']}")
                          
            # Ask if user wants to proceed
            if out_of_stock_items or partial_items:
                proceed = input(f"\n[CONFIRM] Proceed with partial picking? (yes/no): ").strip().lower()
                if proceed != 'yes':
                    self.print_info("Order picking cancelled.")
                    return
                    
            # Start picking process
            print(f"\n[START] Starting Picking Process...")
            picked_items = []
            
            for i, result in enumerate(picking_results, 1):
                item = result['item']
                product_id = item.get('productId')
                product_name = item.get('name', 'Unknown')
                required_qty = item.get('quantity', 0)
                available_qty = result['available_qty']
                location_name = result['location_name']
                
                if result['status'] == 'OUT_OF_STOCK':
                    print(f"\n{i}. [ERROR] {product_name} - Out of stock, skipping")
                    continue
                    
                pick_qty = min(required_qty, available_qty)
                
                print(f"\n{i}. [ORDER] Picking: {product_name}")
                print(f"   [ID] Product ID: {product_id}")
                print(f"   [ADDRESS] Location: {location_name}")
                print(f"   [TRACK] Quantity to Pick: {pick_qty}")
                
                # Confirm picking
                confirm_pick = input(f"   [SUCCESS] Confirm pick {pick_qty} units? (yes/no): ").strip().lower()
                
                if confirm_pick == 'yes':
                    # Record pick details with validation
                    while True:
                        pick_time = input(f"   [TIME] Time taken to pick (minutes): ").strip()
                        if pick_time.isdigit() and int(pick_time) > 0:
                            pick_time = int(pick_time)
                            break
                        elif pick_time == "":
                            pick_time = 5  # Default
                            break
                        else:
                            self.print_error("Please enter a valid number of minutes")
                    
                    # Quality check during picking
                    quality_ok = input(f"   [AUDIT] Quality check passed? (yes/no): ").strip().lower()
                    
                    if quality_ok == 'yes':
                        # Update stock levels
                        if result['stock_location']:
                            self.update_stock_after_picking(product_id, result['stock_location'], pick_qty)
                            
                        picked_items.append({
                            'productId': product_id,
                            'productName': product_name,
                            'quantityRequested': required_qty,
                            'quantityPicked': pick_qty,
                            'location': location_name,
                            'pickTime': pick_time,
                            'qualityCheck': 'PASSED',
                            'pickedBy': self.current_user.get('userId'),
                            'pickedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        })
                        
                        print(f"   [SUCCESS] {product_name} picked successfully!")
                    else:
                        quality_issue = input(f"   [GENERATE] Quality issue description: ").strip()
                        print(f"   [ERROR] {product_name} rejected due to quality issues: {quality_issue}")
                        
                        # Log quality issue
                        self.log_audit('PICK_QUALITY_ISSUE', product_id, 
                                      f"Quality issue during picking: {quality_issue}")
                else:
                    print(f"   [ERROR] {product_name} pick cancelled")
                    
            # Summary of picking
            print(f"\n[TRACK] Picking Summary:")
            print(f"   [ORDER] Order ID: {order_id}")
            print(f"   [CLIPBOARD] Items Requested: {len(order_items)}")
            print(f"   [SUCCESS] Items Picked: {len(picked_items)}")
            print(f"   [USER] Picked by: {self.current_user.get('name', 'Unknown')}")
            
            if picked_items:
                # Update order status
                if len(picked_items) == len(order_items):
                    new_status = 'PICKED'
                else:
                    new_status = 'PARTIALLY_PICKED'
                    
                # Update order with picking information
                try:
                    self.orders_table.update_item(
                        Key={'orderId': order_id, 'customerId': customer_id},
                        UpdateExpression='SET #status = :status, pickedItems = :picked, pickedAt = :pick_time, pickedBy = :picker, updatedAt = :updated',
                        ExpressionAttributeNames={
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':status': new_status,
                            ':picked': picked_items,
                            ':pick_time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            ':picker': self.current_user.get('userId'),
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    # Log audit
                    self.log_audit('ORDER_PICKED', order_id, 
                                  f"Order picked: {len(picked_items)}/{len(order_items)} items, Status: {new_status}")
                    
                    self.print_success(f"[SUCCESS] Order picking completed!")
                    print(f"   [ORDER] Order Status: {new_status}")
                    print(f"   [CLIPBOARD] Ready for packing/verification")
                    
                except Exception as e:
                    self.print_error(f"Error updating order: {str(e)}")
            else:
                self.print_warning("No items were picked for this order.")
                
        except Exception as e:
            self.print_error(f"Error processing order picking: {str(e)}")
            
    def find_best_stock_location(self, product_id: str, required_qty: int) -> Optional[Dict[str, Any]]:
        """Find the best stock location for picking a product"""
        try:
            # Get all stock locations for this product
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid AND availableStock > :zero',
                ExpressionAttributeValues={
                    ':pid': product_id,
                    ':zero': 0
                }
            )
            
            stock_items = response.get('Items', [])
            
            if not stock_items:
                return None
                
            # Sort by available stock (prefer locations with enough stock)
            stock_items.sort(key=lambda x: (
                x.get('availableStock', 0) >= required_qty,  # Prefer locations with enough stock
                x.get('availableStock', 0)  # Then by quantity available
            ), reverse=True)
            
            return stock_items[0]  # Return best location
            
        except Exception as e:
            self.print_error(f"Error finding stock location: {str(e)}")
            return None
            
    def update_stock_after_picking(self, product_id: str, stock_location: Dict[str, Any], picked_qty: int):
        """Update stock levels after picking"""
        try:
            location_key = stock_location.get('location')
            
            # Reserve the stock (move from available to reserved)
            self.stock_levels_table.update_item(
                Key={'productId': product_id, 'location': location_key},
                UpdateExpression='SET availableStock = availableStock - :qty, reservedStock = reservedStock + :qty, lastUpdated = :updated',
                ExpressionAttributeValues={
                    ':qty': picked_qty,
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            print(f"   [TRACK] Stock updated: {picked_qty} units reserved from {location_key.split('#')[0]}")
            
        except Exception as e:
            self.print_error(f"Error updating stock after picking: {str(e)}")
        
    def transfer_stock_between_locations(self):
        """Transfer stock between different locations"""
        self.clear_screen()
        self.print_header("TRANSFER STOCK BETWEEN LOCATIONS")
        
        try:
            print("[FLOW] Stock Transfer Management")
            print("[NOTE] Move inventory between storage locations with proper tracking")
            
            # Get current stock locations
            response = self.stock_levels_table.scan()
            stock_items = response.get('Items', [])
            
            if not stock_items:
                self.print_info("No stock available for transfer.")
                input("Press Enter to continue...")
                return
                
            print(f"\n[ORDER] Available Stock for Transfer:")
            print("-" * 100)
            print(f"{'#':<3} {'Product ID':<15} {'Location':<20} {'Available':<10} {'Total':<8}")
            print("-" * 100)
            
            for i, item in enumerate(stock_items, 1):
                print(f"{i:<3} {item.get('productId', 'N/A'):<15} "
                      f"{item.get('location', 'N/A'):<20} "
                      f"{item.get('availableStock', 0):<10} "
                      f"{item.get('totalStock', 0):<8}")
                      
            print("-" * 100)
            
            # Select source location
            source_choice = input(f"\n[TARGET] Select source stock number (1-{len(stock_items)}): ").strip()
            
            try:
                source_index = int(source_choice) - 1
                if 0 <= source_index < len(stock_items):
                    source_item = stock_items[source_index]
                    self.process_stock_transfer(source_item)
                else:
                    self.print_error("Invalid selection.")
            except ValueError:
                self.print_error("Invalid number.")
                
        except Exception as e:
            self.print_error(f"Error in stock transfer: {str(e)}")
            
        input("Press Enter to continue...")
        
    def perform_cycle_counts(self):
        """Perform cycle counts for inventory accuracy"""
        self.clear_screen()
        self.print_header("PERFORM CYCLE COUNTS")
        
        try:
            print("[FLOW] Cycle Count Management")
            print("[NOTE] Verify inventory accuracy through systematic counting")
            
            print(f"\n[TRACK] Cycle Count Options:")
            print("1. [ORDER] Count by Product")
            print("2. [ADDRESS] Count by Location")
            print("3. [CATEGORY] Count by Category")
            print("4. [TARGET] Random Sample Count")
            
            count_choice = input("\n[TARGET] Select count type (1-4): ").strip()
            
            if count_choice == '1':
                self.count_by_product()
            elif count_choice == '2':
                self.count_by_location()
            elif count_choice == '3':
                self.count_by_category()
            elif count_choice == '4':
                self.random_sample_count()
            else:
                self.print_error("Invalid choice.")
                
        except Exception as e:
            self.print_error(f"Error in cycle count: {str(e)}")
            
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
                
            print(f"\n[ORDER] Orders Pending for Pick and Pack ({len(pending_orders)} orders):")
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
            order_choice = input("\n[TARGET] Select order number to pack (or 'all' for all orders): ").strip()
            
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
        
        print(f"\n[ORDER] Processing Order: {order_id}")
        print(f"[USER] Customer: {customer_id}")
        print(f"[PRICE] Total Amount: {order.get('totalAmount', 0)}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n[CLIPBOARD] Order Items to Pack:")
        for i, item in enumerate(order_items, 1):
            print(f"  {i}. {item.get('name', 'N/A')} x{item.get('quantity', 0)}")
        
        # Check stock availability
        print(f"\n[AUDIT] Checking Stock Availability...")
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
            print(f"\n[INTERRUPTED] Stock Issues Found:")
            for issue in stock_issues:
                print(f"  • {issue['product']}: Need {issue['required']}, Available {issue['available']}")
            
            choice = input("\n[CONFIRM] Continue with partial packing? (yes/no): ").strip().lower()
            if choice != 'yes':
                self.print_info("Packing cancelled due to stock issues.")
                return
        
        # Start packing process
        print(f"\n[ORDER] Starting Packing Process...")
        
        packed_items = []
        for item in order_items:
            product_id = item.get('productId')
            product_name = item.get('name', 'N/A')
            quantity = item.get('quantity', 0)
            
            print(f"\n[ORDER] Packing: {product_name} x{quantity}")
            
            # Get packing time with validation
            while True:
                packing_time = input(f"[TIME] Enter packing time for {product_name} (in minutes): ").strip()
                if packing_time.isdigit() and int(packing_time) > 0:
                    packing_time = int(packing_time)
                    break
                elif packing_time == "":
                    packing_time = 5  # Default 5 minutes
                    break
                else:
                    self.print_error("Please enter a valid number of minutes")
            
            quality_check = input(f"[SUCCESS] Quality check passed for {product_name}? (yes/no): ").strip().lower()
            if quality_check != 'yes':
                print(f"[ERROR] Quality check failed for {product_name}. Item rejected.")
                continue
            
            packed_items.append({
                'productId': product_id,
                'name': product_name,
                'quantity': quantity,
                'packingTime': int(packing_time),
                'packedBy': self.current_user.get('userId'),
                'packedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            })
            
            print(f"[SUCCESS] {product_name} packed successfully!")
        
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
            
            self.print_success(f"[SUCCESS] Order {order_id} packed successfully!")
            self.print_info(f"[ORDER] Items packed: {len(packed_items)}")
            self.print_info(f"[USER] Packed by: {self.current_user.get('name', 'Unknown')}")
            self.print_info(f"[ORDER] Status updated to: PACKED")
            
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
                    
                    print(f"[TRACK] Stock updated for {item.get('name')}: {current_stock} → {max(0, new_stock)}")
                    
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
                
            print(f"[SUCCESS] Orders Pending Verification ({len(packed_orders)} orders):")
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
            order_choice = input("\n[TARGET] Select order number to verify: ").strip()
            
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
        
        print(f"\n[SUCCESS] Verifying Order: {order_id}")
        print(f"[USER] Customer: {customer_id}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n[CLIPBOARD] Order Items to Verify:")
        verification_results = []
        
        for i, item in enumerate(order_items, 1):
            print(f"\n[ORDER] Item {i}: {item.get('name', 'N/A')}")
            print(f"   Quantity: {item.get('quantity', 0)}")
            print(f"   Price: {item.get('price', 0)}")
            
            # Quality checks
            quality_check = input(f"   [SUCCESS] Quality check passed? (yes/no): ").strip().lower()
            quantity_check = input(f"   [TRACK] Quantity correct? (yes/no): ").strip().lower()
            packaging_check = input(f"   [ORDER] Packaging intact? (yes/no): ").strip().lower()
            
            verification_results.append({
                'item': item.get('name', 'N/A'),
                'quality': quality_check == 'yes',
                'quantity': quantity_check == 'yes',
                'packaging': packaging_check == 'yes',
                'all_passed': quality_check == 'yes' and quantity_check == 'yes' and packaging_check == 'yes'
            })
            
            if verification_results[-1]['all_passed']:
                print(f"   [SUCCESS] Item {i} verified successfully!")
            else:
                print(f"   [ERROR] Item {i} has issues!")
        
        # Overall verification
        all_passed = all(result['all_passed'] for result in verification_results)
        
        if all_passed:
            print(f"\n[SUCCESS] All items verified successfully!")
            
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
                
                self.print_success(f"[SUCCESS] Order {order_id} verified and ready for dispatch!")
                
            except Exception as e:
                self.print_error(f"Error updating order status: {str(e)}")
        else:
            print(f"\n[ERROR] Order verification failed!")
            print(f"[CLIPBOARD] Issues found:")
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
            
            choice = input("\n[CONFIRM] Mark order for repacking? (yes/no): ").strip().lower()
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
                
            print(f"[ORDER] Orders Ready for Dispatch ({len(verified_orders)} orders):")
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
            order_choice = input("\n[TARGET] Select order number to prepare for dispatch: ").strip()
            
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
        
        print(f"\n[ORDER] Preparing Order for Dispatch: {order_id}")
        print(f"[USER] Customer: {customer_id}")
        print(f"[ADDRESS] Delivery Address: {order.get('deliveryAddress', 'N/A')}")
        
        # Get order items
        order_items = order.get('items', [])
        
        if not order_items:
            self.print_warning("No items found in order.")
            return
        
        print(f"\n[CLIPBOARD] Preparing Items for Dispatch:")
        
        # Packaging preparation
        print(f"\n[ORDER] Packaging Preparation:")
        packaging_materials = input("   [ORDER] Packaging materials ready? (yes/no): ").strip().lower()
        labels_printed = input("   [CATEGORY] Shipping labels printed? (yes/no): ").strip().lower()
        documentation_complete = input("   📄 Documentation complete? (yes/no): ").strip().lower()
        
        if packaging_materials != 'yes' or labels_printed != 'yes' or documentation_complete != 'yes':
            self.print_error("[ERROR] Dispatch preparation incomplete!")
            input("Press Enter to continue...")
            return
        
        # Item preparation
        print(f"\n[ORDER] Item Preparation:")
        for i, item in enumerate(order_items, 1):
            print(f"   [ORDER] Item {i}: {item.get('name', 'N/A')}")
            properly_packaged = input(f"      [SUCCESS] Properly packaged? (yes/no): ").strip().lower()
            labeled_correctly = input(f"      [CATEGORY] Labeled correctly? (yes/no): ").strip().lower()
            
            if properly_packaged != 'yes' or labeled_correctly != 'yes':
                self.print_error(f"[ERROR] Item {i} not ready for dispatch!")
                input("Press Enter to continue...")
                return
        
        # Final checks
        print(f"\n[SUCCESS] Final Dispatch Checks:")
        weight_verified = input("   [WEIGHT] Weight verified? (yes/no): ").strip().lower()
        dimensions_checked = input("   📐 Dimensions checked? (yes/no): ").strip().lower()
        fragile_items_marked = input("   [ISSUE] Fragile items marked? (yes/no): ").strip().lower()
        
        if weight_verified != 'yes' or dimensions_checked != 'yes' or fragile_items_marked != 'yes':
            self.print_error("[ERROR] Final checks incomplete!")
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
            
            self.print_success(f"[SUCCESS] Order {order_id} prepared for dispatch successfully!")
            self.print_info(f"[ORDER] Status: READY_FOR_DISPATCH")
            self.print_info(f"[ORDER] Ready for delivery pickup")
            
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
                
            print(f"[ORDER] Your Dispatch Preparation History ({len(prepared_orders)} orders):")
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
            print(f"\n[TRACK] Summary:")
            print(f"  • Total Orders Prepared: {len(prepared_orders)}")
            print(f"  • Total Items Prepared: {total_items}")
            
        except Exception as e:
            self.print_error(f"Error viewing dispatch history: {str(e)}")
            
        input("Press Enter to continue...")
        
    def perform_daily_cycle_counts(self):
        """Perform daily cycle counts for ongoing inventory accuracy"""
        self.clear_screen()
        self.print_header("PERFORM DAILY CYCLE COUNTS")
        
        try:
            print("[DATE] Daily Cycle Count Schedule")
            print("[NOTE] Systematic daily counting to maintain inventory accuracy")
            
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            print(f"\n[DATE] Today's Date: {today}")
            print(f"[USER] Counter: {self.current_user.get('name', 'Unknown')}")
            
            # Get products scheduled for today (simplified - in real system would have scheduling)
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            # Select products for daily count (e.g., 10% of products daily)
            import random
            daily_count_size = max(1, len(products) // 10)  # 10% daily
            daily_products = random.sample(products, min(daily_count_size, len(products)))
            
            print(f"\n[ORDER] Products scheduled for today's cycle count ({len(daily_products)} items):")
            print("-" * 80)
            print(f"{'#':<3} {'Product ID':<15} {'Name':<30} {'Category':<15}")
            print("-" * 80)
            
            for i, product in enumerate(daily_products, 1):
                print(f"{i:<3} {product.get('productId', 'N/A'):<15} "
                      f"{product.get('name', 'N/A')[:29]:<30} "
                      f"{product.get('category', 'N/A'):<15}")
                      
            print("-" * 80)
            
            # Start counting
            count_results = []
            
            for i, product in enumerate(daily_products, 1):
                print(f"\n[ORDER] Counting Product {i}/{len(daily_products)}: {product.get('name', 'N/A')}")
                
                # Get stock levels for this product
                stock_response = self.stock_levels_table.scan(
                    FilterExpression='productId = :pid',
                    ExpressionAttributeValues={':pid': product.get('productId')}
                )
                
                stock_items = stock_response.get('Items', [])
                
                for stock_item in stock_items:
                    location = stock_item.get('location', 'N/A')
                    system_qty = stock_item.get('totalStock', 0)
                    
                    print(f"   [ADDRESS] Location: {location}")
                    print(f"   [TRACK] System Quantity: {system_qty}")
                    
                    # Get actual count
                    while True:
                        try:
                            actual_input = input(f"   [NUMBER] Actual Count: ").strip()
                            actual_qty = int(actual_input)
                            break
                        except ValueError:
                            self.print_error("   [ERROR] Please enter a valid number.")
                    
                    variance = actual_qty - system_qty
                    
                    # Record count
                    count_record = {
                        'countId': f"DAILY-{today}-{product.get('productId')}-{location}",
                        'countType': 'DAILY_CYCLE',
                        'productId': product.get('productId'),
                        'productName': product.get('name'),
                        'location': location,
                        'systemQuantity': system_qty,
                        'actualQuantity': actual_qty,
                        'variance': variance,
                        'countDate': today,
                        'countedBy': self.current_user.get('userId'),
                        'status': 'COMPLETED',
                        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                    
                    count_results.append(count_record)
                    self.notifications_table.put_item(Item=count_record)
                    
                    if variance != 0:
                        print(f"   [INTERRUPTED] Variance: {variance:+d} units")
                    else:
                        print(f"   [SUCCESS] Count matches system!")
                        
            # Summary
            total_variances = sum(1 for r in count_results if r['variance'] != 0)
            total_counted = len(count_results)
            
            print(f"\n[TRACK] DAILY CYCLE COUNT SUMMARY")
            print("=" * 60)
            print(f"[DATE] Date: {today}")
            print(f"[ORDER] Items Counted: {total_counted}")
            print(f"[SUCCESS] Accurate Counts: {total_counted - total_variances}")
            print(f"[INTERRUPTED] Variances Found: {total_variances}")
            print(f"[REPORT] Accuracy Rate: {((total_counted - total_variances) / total_counted * 100):.1f}%")
            
            # Log audit
            self.log_audit('DAILY_CYCLE_COUNT', f"DAILY-{today}", 
                          f"Completed daily cycle count: {total_counted} items, {total_variances} variances")
            
            self.print_success("[SUCCESS] Daily cycle count completed!")
            
        except Exception as e:
            self.print_error(f"Error in daily cycle count: {str(e)}")
            
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
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
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