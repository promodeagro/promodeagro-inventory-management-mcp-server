#!/usr/bin/env python3
# warehouse_manager_standalone.py
"""
Warehouse Manager Standalone Script
Run this script in a separate terminal window for Warehouse Manager operations.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional


class WarehouseManagerStandalone:
    """Standalone Warehouse Manager with Authentication"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.batches_table = self.dynamodb.Table('InventoryManagement-Batches')
        self.suppliers_table = self.dynamodb.Table('InventoryManagement-Suppliers')
        self.purchase_orders_table = self.dynamodb.Table('InventoryManagement-PurchaseOrders')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
        self.current_user = None
        self.current_role = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"🏢 {title}")
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
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️  {message}")
        
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
        self.print_header("WAREHOUSE MANAGER - LOGIN")
        
        # Test AWS connection
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your credentials:")
        print("💡 Demo credentials: warehouse_mgr / warehouse123")
        
        # Get username and password
        username = input("\n👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        # Authenticate user
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'WAREHOUSE_MANAGER':
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Permissions: {', '.join(user.get('permissions', []))}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            self.print_error("Only Warehouse Manager role can access this system.")
            return False
            
    def authenticate_user_db(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against DynamoDB Users table"""
        try:
            # Query user by username
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
                # In a real system, you'd hash and compare passwords
                # For demo purposes, we'll use simple comparison
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
        """Create demo warehouse manager user if not exists"""
        try:
            demo_user = {
                'userId': 'warehouse_mgr',
                'role': 'WAREHOUSE_MANAGER',
                'name': 'Amit Patel',
                'email': 'amit@company.com',
                'phone': '+919876543211',
                'password': 'warehouse123',
                'permissions': [
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                    'WAREHOUSE_MANAGEMENT', 'QUALITY_CONTROL', 'RECEIVING_MANAGEMENT',
                    'EXPIRY_MANAGEMENT', 'SPACE_OPTIMIZATION'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Check if user already exists
            response = self.users_table.get_item(
                Key={'userId': 'warehouse_mgr', 'role': 'WAREHOUSE_MANAGER'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Warehouse Manager user created!")
                self.print_info("Username: warehouse_mgr")
                self.print_info("Password: warehouse123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Warehouse Manager main menu"""
        while True:
            self.clear_screen()
            self.print_header("WAREHOUSE MANAGER DASHBOARD")
            
            if self.current_user:
                print(f"👤 User: {self.current_user.get('name', 'Unknown')}")
                print(f"🏢 Role: {self.current_user.get('role', 'Unknown')}")
                print(f"📧 Email: {self.current_user.get('email', 'Unknown')}")
                print(f"📅 Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📋 Available Operations:")
            print("1. 📊 Inventory Planning")
            print("2. 🏭 Warehouse Operations Management")
            print("3. 🧪 Quality Control")
            print("4. ✅ Stock Adjustment Approval")
            print("5. 📦 Receiving Management")
            print("6. ⏰ Expiry Management")
            print("7. 🏗️ Space Optimization")
            print("8. 📈 Reports & Analytics")
            print("9. 📦 Product Management")
            print("10. 📋 Purchase Order Management")
            print("11. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-11): ").strip()
            
            if choice == '1':
                self.inventory_planning_menu()
            elif choice == '2':
                self.warehouse_operations_menu()
            elif choice == '3':
                self.quality_control_menu()
            elif choice == '4':
                self.stock_adjustment_approval_menu()
            elif choice == '5':
                self.receiving_management_menu()
            elif choice == '6':
                self.expiry_management_menu()
            elif choice == '7':
                self.space_optimization_menu()
            elif choice == '8':
                self.reports_analytics_menu()
            elif choice == '9':
                self.product_management_menu()
            elif choice == '10':
                self.purchase_order_management_menu()
            elif choice == '11':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Warehouse Manager system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def inventory_planning_menu(self):
        """Inventory Planning Operations"""
        while True:
            self.clear_screen()
            self.print_header("INVENTORY PLANNING")
            print("1. 📊 View Stock Levels")
            print("2. ⚠️ Set Reorder Points")
            print("3. 🛡️ Set Safety Stock Levels")
            print("4. 📈 Review Stock Optimization")
            print("5. 🌱 Plan Seasonal Adjustments")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.view_stock_levels()
            elif choice == '2':
                self.set_reorder_points()
            elif choice == '3':
                self.set_safety_stock_levels()
            elif choice == '4':
                self.review_stock_optimization()
            elif choice == '5':
                self.plan_seasonal_adjustments()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def view_stock_levels(self):
        """View current stock levels"""
        self.clear_screen()
        self.print_header("CURRENT STOCK LEVELS")
        
        try:
            response = self.stock_levels_table.scan()
            items = response.get('Items', [])
            
            if not items:
                self.print_info("No stock levels found.")
                input("Press Enter to continue...")
                return
                
            print(f"📊 Found {len(items)} stock level records:")
            print("-" * 100)
            print(f"{'Product ID':<15} {'Location':<30} {'Total':<8} {'Available':<10} {'Reserved':<10} {'Damaged':<10}")
            print("-" * 100)
            
            for item in items:
                print(f"{item.get('productId', 'N/A'):<15} "
                      f"{item.get('location', 'N/A'):<30} "
                      f"{item.get('totalStock', 0):<8} "
                      f"{item.get('availableStock', 0):<10} "
                      f"{item.get('reservedStock', 0):<10} "
                      f"{item.get('damagedStock', 0):<10}")
                      
            print("-" * 100)
            
        except Exception as e:
            self.print_error(f"Error viewing stock levels: {str(e)}")
            
        input("Press Enter to continue...")
        
    def set_reorder_points(self):
        """Set reorder points for products"""
        self.clear_screen()
        self.print_header("SET REORDER POINTS")
        
        try:
            # Get products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                current_reorder = product.get('reorderPoint', 0)
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')}) - Current: {current_reorder}")
                
            product_choice = input("\n🎯 Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n📦 Selected: {selected_product.get('name', 'N/A')}")
                    current_reorder = selected_product.get('reorderPoint', 0)
                    print(f"Current reorder point: {current_reorder}")
                    
                    new_reorder = input("Enter new reorder point: ").strip()
                    if new_reorder.isdigit():
                        # Update product
                        self.products_table.update_item(
                            Key={'productId': product_id, 'category': selected_product['category']},
                            UpdateExpression='SET reorderPoint = :reorder, updatedAt = :updated',
                            ExpressionAttributeValues={
                                ':reorder': int(new_reorder),
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                        # Log audit
                        self.log_audit('REORDER_POINT_UPDATE', product_id, f"Updated reorder point from {current_reorder} to {new_reorder}")
                        
                        self.print_success(f"Reorder point updated to {new_reorder}")
                    else:
                        self.print_error("Invalid reorder point value.")
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error setting reorder points: {str(e)}")
            
        input("Press Enter to continue...")
        
    def set_safety_stock_levels(self):
        """Set safety stock levels"""
        self.clear_screen()
        self.print_header("SET SAFETY STOCK LEVELS")
        self.print_info("Safety stock levels help prevent stockouts during unexpected demand.")
        
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                current_safety = product.get('minStock', 0)
                print(f"{i}. {product.get('name', 'N/A')} - Current safety: {current_safety}")
                
            product_choice = input("\n🎯 Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n📦 Selected: {selected_product.get('name', 'N/A')}")
                    current_safety = selected_product.get('minStock', 0)
                    print(f"Current safety stock: {current_safety}")
                    
                    new_safety = input("Enter new safety stock level: ").strip()
                    if new_safety.isdigit():
                        # Update product
                        self.products_table.update_item(
                            Key={'productId': product_id, 'category': selected_product['category']},
                            UpdateExpression='SET minStock = :safety, updatedAt = :updated',
                            ExpressionAttributeValues={
                                ':safety': int(new_safety),
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                        # Log audit
                        self.log_audit('SAFETY_STOCK_UPDATE', product_id, f"Updated safety stock from {current_safety} to {new_safety}")
                        
                        self.print_success(f"Safety stock level updated to {new_safety}")
                    else:
                        self.print_error("Invalid safety stock value.")
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error setting safety stock levels: {str(e)}")
            
        input("Press Enter to continue...")
        
    def review_stock_optimization(self):
        """Review stock optimization recommendations"""
        self.clear_screen()
        self.print_header("STOCK OPTIMIZATION REVIEW")
        
        try:
            # Get low stock items
            response = self.stock_levels_table.scan()
            stock_levels = response.get('Items', [])
            
            low_stock_items = []
            for item in stock_levels:
                available = item.get('availableStock', 0)
                total = item.get('totalStock', 0)
                if available < total * 0.2:  # Less than 20% available
                    low_stock_items.append(item)
                    
            if low_stock_items:
                print("⚠️ LOW STOCK ALERTS:")
                print("-" * 80)
                for item in low_stock_items:
                    product_id = item.get('productId', 'N/A')
                    location = item.get('location', 'N/A')
                    available = item.get('availableStock', 0)
                    total = item.get('totalStock', 0)
                    percentage = (available / total * 100) if total > 0 else 0
                    
                    print(f"📦 Product: {product_id}")
                    print(f"📍 Location: {location}")
                    print(f"📊 Available: {available}/{total} ({percentage:.1f}%)")
                    print(f"💡 Recommendation: {'URGENT REORDER' if percentage < 10 else 'PLAN REORDER'}")
                    print("-" * 80)
            else:
                self.print_success("No low stock alerts. Inventory levels are healthy!")
                
        except Exception as e:
            self.print_error(f"Error reviewing stock optimization: {str(e)}")
            
        input("Press Enter to continue...")
        
    def plan_seasonal_adjustments(self):
        """Plan seasonal inventory adjustments"""
        self.clear_screen()
        self.print_header("SEASONAL INVENTORY ADJUSTMENTS")
        
        print("🌱 Seasonal Adjustment Planning:")
        print("1. 📈 Increase stock for high-demand seasons")
        print("2. 📉 Reduce stock for low-demand seasons")
        print("3. 🎯 Set seasonal reorder points")
        print("4. 📊 View seasonal trends")
        
        choice = input("\n🎯 Select adjustment type (1-4): ").strip()
        
        if choice == '1':
            self.increase_seasonal_stock()
        elif choice == '2':
            self.decrease_seasonal_stock()
        elif choice == '3':
            self.set_seasonal_reorder_points()
        elif choice == '4':
            self.view_seasonal_trends()
        else:
            self.print_error("Invalid choice.")
            
        input("Press Enter to continue...")
        
    def warehouse_operations_menu(self):
        """Warehouse Operations Management"""
        while True:
            self.clear_screen()
            self.print_header("WAREHOUSE OPERATIONS MANAGEMENT")
            print("1. 👥 Assign Tasks to Staff")
            print("2. 📊 Monitor Warehouse Productivity")
            print("3. 🏗️ Optimize Warehouse Layout")
            print("4. 📋 View Task Assignments")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.assign_tasks_to_staff()
            elif choice == '2':
                self.monitor_warehouse_productivity()
            elif choice == '3':
                self.optimize_warehouse_layout()
            elif choice == '4':
                self.view_task_assignments()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def quality_control_menu(self):
        """Quality Control Operations"""
        while True:
            self.clear_screen()
            self.print_header("QUALITY CONTROL")
            print("1. 🧪 Set Quality Inspection Protocols")
            print("2. 📊 Review Quality Metrics")
            print("3. 🚨 Manage Product Recalls")
            print("4. 📋 View Quality Reports")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.set_quality_protocols()
            elif choice == '2':
                self.review_quality_metrics()
            elif choice == '3':
                self.manage_product_recalls()
            elif choice == '4':
                self.view_quality_reports()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def stock_adjustment_approval_menu(self):
        """Stock Adjustment Approval Operations"""
        while True:
            self.clear_screen()
            self.print_header("STOCK ADJUSTMENT APPROVAL")
            print("1. 📋 Review Pending Adjustments")
            print("2. ✅ Approve Adjustments")
            print("3. ❌ Reject Adjustments")
            print("4. 🔍 Investigate Discrepancies")
            print("5. 📊 View Adjustment History")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.review_pending_adjustments()
            elif choice == '2':
                self.approve_adjustments()
            elif choice == '3':
                self.reject_adjustments()
            elif choice == '4':
                self.investigate_discrepancies()
            elif choice == '5':
                self.view_adjustment_history()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def receiving_management_menu(self):
        """Receiving Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("RECEIVING MANAGEMENT")
            print("1. 📦 Oversee Goods Receiving")
            print("2. ⚠️ Resolve Receiving Discrepancies")
            print("3. ✅ Approve Put-Away Strategies")
            print("4. 📋 View Receiving Schedule")
            print("5. 📊 Receiving Performance")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.oversee_goods_receiving()
            elif choice == '2':
                self.resolve_receiving_discrepancies()
            elif choice == '3':
                self.approve_putaway_strategies()
            elif choice == '4':
                self.view_receiving_schedule()
            elif choice == '5':
                self.receiving_performance()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def expiry_management_menu(self):
        """Expiry Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("EXPIRY MANAGEMENT")
            print("1. ⏰ Monitor Expiring Products")
            print("2. 💰 Approve Markdown Strategies")
            print("3. 🗑️ Coordinate Disposal Activities")
            print("4. 📊 Expiry Analytics")
            print("5. ⚠️ Expiry Alerts")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.monitor_expiring_products()
            elif choice == '2':
                self.approve_markdown_strategies()
            elif choice == '3':
                self.coordinate_disposal_activities()
            elif choice == '4':
                self.expiry_analytics()
            elif choice == '5':
                self.expiry_alerts()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def space_optimization_menu(self):
        """Space Optimization Operations"""
        while True:
            self.clear_screen()
            self.print_header("SPACE OPTIMIZATION")
            print("1. 📊 Analyze Capacity Utilization")
            print("2. 🏗️ Plan Storage Reorganization")
            print("3. 🌡️ Monitor Temperature Zones")
            print("4. 📈 Space Efficiency Reports")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.analyze_capacity_utilization()
            elif choice == '2':
                self.plan_storage_reorganization()
            elif choice == '3':
                self.monitor_temperature_zones()
            elif choice == '4':
                self.space_efficiency_reports()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def reports_analytics_menu(self):
        """Reports and Analytics"""
        while True:
            self.clear_screen()
            self.print_header("REPORTS & ANALYTICS")
            print("1. 📊 Inventory Reports")
            print("2. 📈 Performance Analytics")
            print("3. 💰 Cost Analysis")
            print("4. ⚠️ Alert Reports")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.inventory_reports()
            elif choice == '2':
                self.performance_analytics()
            elif choice == '3':
                self.cost_analysis()
            elif choice == '4':
                self.alert_reports()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def product_management_menu(self):
        """Product Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PRODUCT MANAGEMENT")
            print("1. 📋 View All Products")
            print("2. 🔍 View Product Details")
            print("3. ✏️ Update Product Information")
            print("4. 🎨 Manage Product Variants")
            print("5. 📏 Manage Product Units")
            print("6. 💰 Update Product Pricing")
            print("7. 📊 Product Performance Analytics")
            print("8. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-8): ").strip()
            
            if choice == '1':
                self.view_all_products()
            elif choice == '2':
                self.view_product_details()
            elif choice == '3':
                self.update_product_information()
            elif choice == '4':
                self.manage_product_variants()
            elif choice == '5':
                self.manage_product_units()
            elif choice == '6':
                self.update_product_pricing()
            elif choice == '7':
                self.product_performance_analytics()
            elif choice == '8':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def view_all_products(self):
        """View all products in the system"""
        self.clear_screen()
        self.print_header("ALL PRODUCTS")
        
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print(f"📦 Found {len(products)} products:")
            print("-" * 120)
            print(f"{'Product ID':<15} {'Name':<25} {'Category':<15} {'Brand':<15} {'Cost':<8} {'Price':<8} {'Stock':<8}")
            print("-" * 120)
            
            for product in products:
                print(f"{product.get('productId', 'N/A'):<15} "
                      f"{product.get('name', 'N/A')[:24]:<25} "
                      f"{product.get('category', 'N/A'):<15} "
                      f"{product.get('brand', 'N/A')[:14]:<15} "
                      f"{product.get('costPrice', 0):<8} "
                      f"{product.get('sellingPrice', 0):<8} "
                      f"{product.get('minStock', 0):<8}")
                      
            print("-" * 120)
            
        except Exception as e:
            self.print_error(f"Error viewing products: {str(e)}")
            
        input("Press Enter to continue...")
        
    def view_product_details(self):
        """View detailed information about a specific product"""
        self.clear_screen()
        self.print_header("PRODUCT DETAILS")
        
        try:
            # Get products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    
                    print(f"\n📦 Product Details:")
                    print("-" * 60)
                    print(f"🆔 Product ID: {selected_product.get('productId', 'N/A')}")
                    print(f"📝 Name: {selected_product.get('name', 'N/A')}")
                    print(f"📄 Description: {selected_product.get('description', 'N/A')}")
                    print(f"🏷️ Category: {selected_product.get('category', 'N/A')}")
                    print(f"🏢 Brand: {selected_product.get('brand', 'N/A')}")
                    print(f"💰 Cost Price: {selected_product.get('costPrice', 0)}")
                    print(f"💵 Selling Price: {selected_product.get('sellingPrice', 0)}")
                    print(f"📦 Min Stock: {selected_product.get('minStock', 0)}")
                    print(f"⚠️ Reorder Point: {selected_product.get('reorderPoint', 0)}")
                    print(f"🏪 Supplier ID: {selected_product.get('supplierId', 'N/A')}")
                    print(f"📍 Storage Location: {selected_product.get('storageLocation', 'N/A')}")
                    print(f"🎨 Has Variants: {selected_product.get('hasVariants', False)}")
                    print(f"📏 Base Unit: {selected_product.get('baseUnit', 'N/A')}")
                    print(f"📏 Default Unit: {selected_product.get('defaultUnit', 'N/A')}")
                    print(f"⏰ Expiry Tracking: {selected_product.get('expiryTracking', False)}")
                    print(f"📦 Batch Required: {selected_product.get('batchRequired', False)}")
                    print(f"🌡️ Special Handling: {selected_product.get('specialHandling', 'N/A')}")
                    print("-" * 60)
                    
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error viewing product details: {str(e)}")
            
        input("Press Enter to continue...")
        
    def update_product_information(self):
        """Update product information"""
        self.clear_screen()
        self.print_header("UPDATE PRODUCT INFORMATION")
        
        try:
            # Get products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n📦 Selected: {selected_product.get('name', 'N/A')}")
                    print("What would you like to update?")
                    print("1. 💰 Cost Price")
                    print("2. 💵 Selling Price")
                    print("3. 📦 Min Stock")
                    print("4. ⚠️ Reorder Point")
                    print("5. 📍 Storage Location")
                    print("6. 🌡️ Special Handling")
                    
                    update_choice = input("\n🎯 Select field to update (1-6): ").strip()
                    
                    if update_choice == '1':
                        new_cost = input("Enter new cost price: ").strip()
                        if new_cost.replace('.', '').isdigit():
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET costPrice = :cost, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':cost': Decimal(new_cost),
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_COST_UPDATE', product_id, f"Updated cost price to {new_cost}")
                            self.print_success(f"Cost price updated to {new_cost}")
                        else:
                            self.print_error("Invalid cost price value.")
                            
                    elif update_choice == '2':
                        new_price = input("Enter new selling price: ").strip()
                        if new_price.replace('.', '').isdigit():
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET sellingPrice = :price, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':price': Decimal(new_price),
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_PRICE_UPDATE', product_id, f"Updated selling price to {new_price}")
                            self.print_success(f"Selling price updated to {new_price}")
                        else:
                            self.print_error("Invalid selling price value.")
                            
                    elif update_choice == '3':
                        new_min_stock = input("Enter new min stock: ").strip()
                        if new_min_stock.isdigit():
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET minStock = :minStock, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':minStock': int(new_min_stock),
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_MIN_STOCK_UPDATE', product_id, f"Updated min stock to {new_min_stock}")
                            self.print_success(f"Min stock updated to {new_min_stock}")
                        else:
                            self.print_error("Invalid min stock value.")
                            
                    elif update_choice == '4':
                        new_reorder = input("Enter new reorder point: ").strip()
                        if new_reorder.isdigit():
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET reorderPoint = :reorder, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':reorder': int(new_reorder),
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_REORDER_UPDATE', product_id, f"Updated reorder point to {new_reorder}")
                            self.print_success(f"Reorder point updated to {new_reorder}")
                        else:
                            self.print_error("Invalid reorder point value.")
                            
                    elif update_choice == '5':
                        new_location = input("Enter new storage location: ").strip()
                        if new_location:
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET storageLocation = :location, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':location': new_location,
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_LOCATION_UPDATE', product_id, f"Updated storage location to {new_location}")
                            self.print_success(f"Storage location updated to {new_location}")
                        else:
                            self.print_error("Invalid storage location.")
                            
                    elif update_choice == '6':
                        new_handling = input("Enter new special handling: ").strip()
                        if new_handling:
                            self.products_table.update_item(
                                Key={'productId': product_id, 'category': selected_product['category']},
                                UpdateExpression='SET specialHandling = :handling, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':handling': new_handling,
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            self.log_audit('PRODUCT_HANDLING_UPDATE', product_id, f"Updated special handling to {new_handling}")
                            self.print_success(f"Special handling updated to {new_handling}")
                        else:
                            self.print_error("Invalid special handling.")
                    else:
                        self.print_error("Invalid choice.")
                        
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error updating product information: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_product_variants(self):
        """Manage product variants"""
        self.clear_screen()
        self.print_header("MANAGE PRODUCT VARIANTS")
        self.print_info("Product variant management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def manage_product_units(self):
        """Manage product units"""
        self.clear_screen()
        self.print_header("MANAGE PRODUCT UNITS")
        self.print_info("Product unit management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_product_pricing(self):
        """Update product pricing"""
        self.clear_screen()
        self.print_header("UPDATE PRODUCT PRICING")
        self.print_info("Product pricing update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def product_performance_analytics(self):
        """Product performance analytics"""
        self.clear_screen()
        self.print_header("PRODUCT PERFORMANCE ANALYTICS")
        self.print_info("Product performance analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    # Placeholder methods for other operations
    def assign_tasks_to_staff(self):
        self.clear_screen()
        self.print_header("ASSIGN TASKS TO STAFF")
        self.print_info("Task assignment functionality will be implemented.")
        input("Press Enter to continue...")
        
    def monitor_warehouse_productivity(self):
        self.clear_screen()
        self.print_header("MONITOR WAREHOUSE PRODUCTIVITY")
        self.print_info("Productivity monitoring functionality will be implemented.")
        input("Press Enter to continue...")
        
    def optimize_warehouse_layout(self):
        self.clear_screen()
        self.print_header("OPTIMIZE WAREHOUSE LAYOUT")
        self.print_info("Layout optimization functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_task_assignments(self):
        self.clear_screen()
        self.print_header("VIEW TASK ASSIGNMENTS")
        self.print_info("Task assignment viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def set_quality_protocols(self):
        self.clear_screen()
        self.print_header("SET QUALITY PROTOCOLS")
        self.print_info("Quality protocol setting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_quality_metrics(self):
        self.clear_screen()
        self.print_header("REVIEW QUALITY METRICS")
        self.print_info("Quality metrics review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def manage_product_recalls(self):
        self.clear_screen()
        self.print_header("MANAGE PRODUCT RECALLS")
        self.print_info("Product recall management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_quality_reports(self):
        self.clear_screen()
        self.print_header("VIEW QUALITY REPORTS")
        self.print_info("Quality report viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_pending_adjustments(self):
        self.clear_screen()
        self.print_header("REVIEW PENDING ADJUSTMENTS")
        self.print_info("Pending adjustments review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def approve_adjustments(self):
        self.clear_screen()
        self.print_header("APPROVE ADJUSTMENTS")
        self.print_info("Adjustment approval functionality will be implemented.")
        input("Press Enter to continue...")
        
    def reject_adjustments(self):
        self.clear_screen()
        self.print_header("REJECT ADJUSTMENTS")
        self.print_info("Adjustment rejection functionality will be implemented.")
        input("Press Enter to continue...")
        
    def investigate_discrepancies(self):
        self.clear_screen()
        self.print_header("INVESTIGATE DISCREPANCIES")
        self.print_info("Discrepancy investigation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_adjustment_history(self):
        self.clear_screen()
        self.print_header("VIEW ADJUSTMENT HISTORY")
        self.print_info("Adjustment history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def oversee_goods_receiving(self):
        self.clear_screen()
        self.print_header("OVERSEE GOODS RECEIVING")
        self.print_info("Goods receiving oversight functionality will be implemented.")
        input("Press Enter to continue...")
        
    def resolve_receiving_discrepancies(self):
        self.clear_screen()
        self.print_header("RESOLVE RECEIVING DISCREPANCIES")
        self.print_info("Receiving discrepancy resolution functionality will be implemented.")
        input("Press Enter to continue...")
        
    def approve_putaway_strategies(self):
        self.clear_screen()
        self.print_header("APPROVE PUT-AWAY STRATEGIES")
        self.print_info("Put-away strategy approval functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_receiving_schedule(self):
        self.clear_screen()
        self.print_header("VIEW RECEIVING SCHEDULE")
        self.print_info("Receiving schedule viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def receiving_performance(self):
        self.clear_screen()
        self.print_header("RECEIVING PERFORMANCE")
        self.print_info("Receiving performance functionality will be implemented.")
        input("Press Enter to continue...")
        
    def monitor_expiring_products(self):
        self.clear_screen()
        self.print_header("MONITOR EXPIRING PRODUCTS")
        self.print_info("Expiring products monitoring functionality will be implemented.")
        input("Press Enter to continue...")
        
    def approve_markdown_strategies(self):
        self.clear_screen()
        self.print_header("APPROVE MARKDOWN STRATEGIES")
        self.print_info("Markdown strategy approval functionality will be implemented.")
        input("Press Enter to continue...")
        
    def coordinate_disposal_activities(self):
        self.clear_screen()
        self.print_header("COORDINATE DISPOSAL ACTIVITIES")
        self.print_info("Disposal activity coordination functionality will be implemented.")
        input("Press Enter to continue...")
        
    def expiry_analytics(self):
        self.clear_screen()
        self.print_header("EXPIRY ANALYTICS")
        self.print_info("Expiry analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def expiry_alerts(self):
        self.clear_screen()
        self.print_header("EXPIRY ALERTS")
        self.print_info("Expiry alerts functionality will be implemented.")
        input("Press Enter to continue...")
        
    def analyze_capacity_utilization(self):
        self.clear_screen()
        self.print_header("ANALYZE CAPACITY UTILIZATION")
        self.print_info("Capacity utilization analysis functionality will be implemented.")
        input("Press Enter to continue...")
        
    def plan_storage_reorganization(self):
        self.clear_screen()
        self.print_header("PLAN STORAGE REORGANIZATION")
        self.print_info("Storage reorganization planning functionality will be implemented.")
        input("Press Enter to continue...")
        
    def monitor_temperature_zones(self):
        self.clear_screen()
        self.print_header("MONITOR TEMPERATURE ZONES")
        self.print_info("Temperature zone monitoring functionality will be implemented.")
        input("Press Enter to continue...")
        
    def space_efficiency_reports(self):
        self.clear_screen()
        self.print_header("SPACE EFFICIENCY REPORTS")
        self.print_info("Space efficiency reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def inventory_reports(self):
        self.clear_screen()
        self.print_header("INVENTORY REPORTS")
        self.print_info("Inventory reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def performance_analytics(self):
        self.clear_screen()
        self.print_header("PERFORMANCE ANALYTICS")
        self.print_info("Performance analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def cost_analysis(self):
        self.clear_screen()
        self.print_header("COST ANALYSIS")
        self.print_info("Cost analysis functionality will be implemented.")
        input("Press Enter to continue...")
        
    def alert_reports(self):
        self.clear_screen()
        self.print_header("ALERT REPORTS")
        self.print_info("Alert reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def increase_seasonal_stock(self):
        self.clear_screen()
        self.print_header("INCREASE SEASONAL STOCK")
        self.print_info("Seasonal stock increase functionality will be implemented.")
        input("Press Enter to continue...")
        
    def decrease_seasonal_stock(self):
        self.clear_screen()
        self.print_header("DECREASE SEASONAL STOCK")
        self.print_info("Seasonal stock decrease functionality will be implemented.")
        input("Press Enter to continue...")
        
    def set_seasonal_reorder_points(self):
        self.clear_screen()
        self.print_header("SET SEASONAL REORDER POINTS")
        self.print_info("Seasonal reorder point setting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_seasonal_trends(self):
        self.clear_screen()
        self.print_header("VIEW SEASONAL TRENDS")
        self.print_info("Seasonal trends viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def purchase_order_management_menu(self):
        """Purchase Order Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PURCHASE ORDER MANAGEMENT")
            print("1. 📋 Create New Purchase Order")
            print("2. 📊 View All Purchase Orders")
            print("3. 🔍 View Purchase Order Details")
            print("4. ✏️ Update Purchase Order")
            print("5. 📈 Purchase Order Analytics")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.create_new_purchase_order()
            elif choice == '2':
                self.view_all_purchase_orders()
            elif choice == '3':
                self.view_purchase_order_details()
            elif choice == '4':
                self.update_purchase_order()
            elif choice == '5':
                self.purchase_order_analytics()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def create_new_purchase_order(self):
        """Create a new purchase order"""
        self.clear_screen()
        self.print_header("CREATE NEW PURCHASE ORDER")
        
        try:
            # Get available suppliers
            response = self.suppliers_table.scan()
            suppliers = response.get('Items', [])
            
            if not suppliers:
                self.print_error("No suppliers found. Please add suppliers first.")
                input("Press Enter to continue...")
                return
                
            print("🏪 Available Suppliers:")
            for i, supplier in enumerate(suppliers, 1):
                print(f"{i}. {supplier.get('name', 'N/A')} - {supplier.get('supplierId', 'N/A')}")
                
            supplier_choice = input("\n🎯 Select supplier number: ").strip()
            
            try:
                supplier_index = int(supplier_choice) - 1
                if 0 <= supplier_index < len(suppliers):
                    selected_supplier = suppliers[supplier_index]
                    supplier_id = selected_supplier['supplierId']
                    
                    print(f"\n🏪 Selected Supplier: {selected_supplier.get('name', 'N/A')}")
                    
                    # Get available products
                    products_response = self.products_table.scan()
                    products = products_response.get('Items', [])
                    
                    if not products:
                        self.print_error("No products found.")
                        input("Press Enter to continue...")
                        return
                        
                    print("\n📦 Available Products:")
                    for i, product in enumerate(products, 1):
                        print(f"{i}. {product.get('name', 'N/A')} - {product.get('sellingPrice', 0)}")
                        
                    # Select products for the order
                    selected_products = []
                    total_amount = Decimal('0')
                    
                    while True:
                        product_choice = input("\n🎯 Select product number (or 'done' to finish): ").strip()
                        
                        if product_choice.lower() == 'done':
                            break
                            
                        try:
                            product_index = int(product_choice) - 1
                            if 0 <= product_index < len(products):
                                selected_product = products[product_index]
                                quantity = input(f"📦 Quantity for {selected_product.get('name')}: ").strip()
                                
                                if quantity.isdigit() and int(quantity) > 0:
                                    qty = int(quantity)
                                    price = Decimal(str(selected_product.get('costPrice', 0)))
                                    item_total = price * qty
                                    
                                    selected_products.append({
                                        'productId': selected_product['productId'],
                                        'name': selected_product.get('name'),
                                        'quantity': qty,
                                        'price': price,
                                        'total': item_total
                                    })
                                    
                                    total_amount += item_total
                                    self.print_success(f"Added {qty} x {selected_product.get('name')} = {item_total}")
                                else:
                                    self.print_error("Invalid quantity.")
                            else:
                                self.print_error("Invalid product selection.")
                        except ValueError:
                            self.print_error("Invalid product number.")
                            
                    if not selected_products:
                        self.print_info("No products selected.")
                        input("Press Enter to continue...")
                        return
                        
                    # Order details
                    delivery_date = input("\n📅 Expected Delivery Date (YYYY-MM-DD): ").strip()
                    if not delivery_date:
                        delivery_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                        
                    notes = input("\n📝 Order Notes (optional): ").strip()
                    
                    # Order summary
                    print(f"\n📋 Purchase Order Summary:")
                    print("-" * 60)
                    print(f"🏪 Supplier: {selected_supplier.get('name', 'N/A')}")
                    print(f"📅 Delivery Date: {delivery_date}")
                    print(f"📝 Notes: {notes or 'None'}")
                    print("-" * 60)
                    for item in selected_products:
                        print(f"  • {item['name']} x{item['quantity']} = {item['total']}")
                    print("-" * 60)
                    print(f"💰 Total Amount: {total_amount}")
                    
                    # Confirm order
                    confirm = input("\n❓ Confirm purchase order? (yes/no): ").strip().lower()
                    
                    if confirm == 'yes':
                        # Create purchase order
                        po_id = f'PO-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
                        
                        po_item = {
                            'poId': po_id,
                            'supplierId': supplier_id,
                            'orderDate': datetime.now().isoformat(),
                            'expectedDeliveryDate': delivery_date,
                            'totalAmount': total_amount,
                            'status': 'PENDING',
                            'items': selected_products,
                            'notes': notes,
                            'createdBy': self.current_user.get('userId'),
                            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                        
                        self.purchase_orders_table.put_item(Item=po_item)
                        
                        # Log audit
                        self.log_audit('PO_CREATED', po_id, f"Created purchase order for {supplier_id} with total {total_amount}")
                        
                        self.print_success(f"Purchase order created successfully!")
                        self.print_info(f"PO ID: {po_id}")
                        self.print_info(f"Supplier: {selected_supplier.get('name', 'N/A')}")
                        self.print_info(f"Total Amount: {total_amount}")
                        self.print_info(f"Status: PENDING")
                        
                    else:
                        self.print_info("Purchase order cancelled.")
                        
                else:
                    self.print_error("Invalid supplier selection.")
            except ValueError:
                self.print_error("Invalid supplier number.")
                
        except Exception as e:
            self.print_error(f"Error creating purchase order: {str(e)}")
            
        input("Press Enter to continue...")
        
    def view_all_purchase_orders(self):
        """View all purchase orders"""
        self.clear_screen()
        self.print_header("VIEW ALL PURCHASE ORDERS")
        
        try:
            response = self.purchase_orders_table.scan()
            purchase_orders = response.get('Items', [])
            
            if not purchase_orders:
                self.print_info("No purchase orders found.")
                input("Press Enter to continue...")
                return
                
            print(f"📋 Purchase Orders ({len(purchase_orders)} orders):")
            print("-" * 120)
            print(f"{'PO ID':<20} {'Supplier ID':<15} {'Order Date':<15} {'Amount':<12} {'Status':<15} {'Delivery Date':<15}")
            print("-" * 120)
            
            for po in purchase_orders:
                print(f"{po.get('poId', 'N/A'):<20} "
                      f"{po.get('supplierId', 'N/A'):<15} "
                      f"{po.get('orderDate', 'N/A')[:10]:<15} "
                      f"{po.get('totalAmount', 0):<12} "
                      f"{po.get('status', 'N/A'):<15} "
                      f"{po.get('expectedDeliveryDate', 'N/A')[:10]:<15}")
                      
            print("-" * 120)
            
            # Status breakdown
            status_counts = {}
            for po in purchase_orders:
                status = po.get('status', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print(f"\n📊 Status Breakdown:")
            for status, count in status_counts.items():
                print(f"  • {status}: {count} orders")
                
            # Total value
            total_value = sum(Decimal(str(po.get('totalAmount', 0))) for po in purchase_orders)
            print(f"\n💰 Total Value: {total_value}")
            
        except Exception as e:
            self.print_error(f"Error viewing purchase orders: {str(e)}")
            
        input("Press Enter to continue...")
        
    def view_purchase_order_details(self):
        """View detailed purchase order information"""
        self.clear_screen()
        self.print_header("VIEW PURCHASE ORDER DETAILS")
        
        try:
            response = self.purchase_orders_table.scan()
            purchase_orders = response.get('Items', [])
            
            if not purchase_orders:
                self.print_info("No purchase orders found.")
                input("Press Enter to continue...")
                return
                
            print("📋 Available Purchase Orders:")
            for i, po in enumerate(purchase_orders, 1):
                print(f"{i}. {po.get('poId', 'N/A')} - {po.get('supplierId', 'N/A')} - {po.get('totalAmount', 0)}")
                
            po_choice = input("\n🎯 Select purchase order number: ").strip()
            
            try:
                po_index = int(po_choice) - 1
                if 0 <= po_index < len(purchase_orders):
                    selected_po = purchase_orders[po_index]
                    
                    print(f"\n📋 Purchase Order Details:")
                    print("-" * 60)
                    print(f"🆔 PO ID: {selected_po.get('poId', 'N/A')}")
                    print(f"🏪 Supplier ID: {selected_po.get('supplierId', 'N/A')}")
                    print(f"📅 Order Date: {selected_po.get('orderDate', 'N/A')[:19]}")
                    print(f"📅 Expected Delivery: {selected_po.get('expectedDeliveryDate', 'N/A')}")
                    print(f"💰 Total Amount: {selected_po.get('totalAmount', 0)}")
                    print(f"📊 Status: {selected_po.get('status', 'N/A')}")
                    print(f"👤 Created By: {selected_po.get('createdBy', 'N/A')}")
                    print(f"📝 Notes: {selected_po.get('notes', 'None')}")
                    print("-" * 60)
                    
                    # Show order items
                    items = selected_po.get('items', [])
                    if items:
                        print("📦 Order Items:")
                        for item in items:
                            print(f"  • {item.get('name', 'N/A')} x{item.get('quantity', 0)} = {item.get('total', 0)}")
                    else:
                        print("📦 No items found.")
                        
                else:
                    self.print_error("Invalid purchase order selection.")
            except ValueError:
                self.print_error("Invalid purchase order number.")
                
        except Exception as e:
            self.print_error(f"Error viewing purchase order details: {str(e)}")
            
        input("Press Enter to continue...")
        
    def update_purchase_order(self):
        """Update purchase order status"""
        self.clear_screen()
        self.print_header("UPDATE PURCHASE ORDER")
        self.print_info("Purchase order update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def purchase_order_analytics(self):
        """Purchase order analytics"""
        self.clear_screen()
        self.print_header("PURCHASE ORDER ANALYTICS")
        self.print_info("Purchase order analytics functionality will be implemented.")
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
                'userAgent': 'WarehouseManager-Standalone',
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
            self.print_success("Thank you for using the Warehouse Manager system!")


def main():
    """Main entry point"""
    warehouse_mgr = WarehouseManagerStandalone()
    warehouse_mgr.run()


if __name__ == '__main__':
    main() 