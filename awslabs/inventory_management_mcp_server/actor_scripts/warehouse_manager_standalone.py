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
        print(f"[ACCOUNT] {title}")
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
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"[INTERRUPTED]  {message}")
        
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
        self.print_header("WAREHOUSE MANAGER - LOGIN")
        
        # Test AWS connection
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your credentials:")
        print("[NOTE] Demo credentials: warehouse_mgr / warehouse123")
        
        # Get username and password
        username = input("\n[USER] Username: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
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
                print(f"[USER] User: {self.current_user.get('name', 'Unknown')}")
                print(f"[ACCOUNT] Role: {self.current_user.get('role', 'Unknown')}")
                print(f"[EMAIL] Email: {self.current_user.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. [TRACK] Inventory Planning")
            print("2. [WAREHOUSE] Warehouse Operations Management")
            print("3. [TEST] Quality Control")
            print("4. [SUCCESS] Stock Adjustment Approval")
            print("5. [ORDER] Receiving Management")
            print("6. ⏰ Expiry Management")
            print("7. 🏗️ Space Optimization")
            print("8. [REPORT] Reports & Analytics")
            print("9. [ORDER] Product Management")
            print("10. [CLIPBOARD] Purchase Order Management")
            print("11. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-11): ").strip()
            
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
            print("1. [TRACK] View Stock Levels")
            print("2. [INTERRUPTED] Set Reorder Points")
            print("3. 🛡️ Set Safety Stock Levels")
            print("4. [REPORT] Review Stock Optimization")
            print("5. 🌱 Plan Seasonal Adjustments")
            print("6. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-6): ").strip()
            
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
                
            print(f"[TRACK] Found {len(items)} stock level records:")
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
                
            print("[ORDER] Available Products:")
            for i, product in enumerate(products, 1):
                current_reorder = product.get('reorderPoint', 0)
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')}) - Current: {current_reorder}")
                
            product_choice = input("\n[TARGET] Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n[ORDER] Selected: {selected_product.get('name', 'N/A')}")
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
                
            print("[ORDER] Available Products:")
            for i, product in enumerate(products, 1):
                current_safety = product.get('minStock', 0)
                print(f"{i}. {product.get('name', 'N/A')} - Current safety: {current_safety}")
                
            product_choice = input("\n[TARGET] Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n[ORDER] Selected: {selected_product.get('name', 'N/A')}")
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
            overstock_items = []
            optimal_items = []
            
            for item in stock_levels:
                # Convert to consistent numeric types to fix the Decimal * float error
                available = Decimal(str(item.get('availableStock', 0)))
                total = Decimal(str(item.get('totalStock', 0)))
                reserved = Decimal(str(item.get('reservedStock', 0)))
                damaged = Decimal(str(item.get('damagedStock', 0)))
                
                if total > 0:
                    # Calculate percentages using Decimal arithmetic
                    available_percentage = (available / total * Decimal('100'))
                    
                    # Get product details for optimization recommendations
                    product_id = item.get('productId', 'N/A')
                    
                    # Try to get product info for reorder points and min stock
                    try:
                        product_response = self.products_table.scan(
                            FilterExpression='productId = :pid',
                            ExpressionAttributeValues={':pid': product_id}
                        )
                        
                        product_info = None
                        if product_response['Items']:
                            product_info = product_response['Items'][0]
                            
                        reorder_point = Decimal(str(product_info.get('reorderPoint', 0))) if product_info else Decimal('0')
                        min_stock = Decimal(str(product_info.get('minStock', 0))) if product_info else Decimal('0')
                        
                    except Exception:
                        reorder_point = Decimal('0')
                        min_stock = Decimal('0')
                    
                    # Calculate optimization metrics
                    stock_data = {
                        'productId': product_id,
                        'location': item.get('location', 'N/A'),
                        'available': int(available),
                        'total': int(total),
                        'reserved': int(reserved),
                        'damaged': int(damaged),
                        'available_percentage': float(available_percentage),
                        'reorder_point': int(reorder_point),
                        'min_stock': int(min_stock),
                        'turnover_days': self.calculate_turnover_days(product_id),
                        'demand_forecast': self.calculate_demand_forecast(product_id)
                    }
                    
                    # Categorize based on optimization analysis
                    if available <= reorder_point or available_percentage < Decimal('20'):
                        low_stock_items.append(stock_data)
                    elif available > (min_stock * Decimal('3')) and available_percentage > Decimal('80'):
                        overstock_items.append(stock_data)
                    else:
                        optimal_items.append(stock_data)
                        
            # Display optimization analysis
            print(f"[TRACK] Stock Optimization Analysis")
            print("=" * 100)
            
            if low_stock_items:
                print(f"\n[INTERRUPTED] LOW STOCK ALERTS ({len(low_stock_items)} items):")
                print("-" * 100)
                print(f"{'Product ID':<15} {'Location':<20} {'Available':<10} {'Total':<8} {'%':<6} {'Action':<20}")
                print("-" * 100)
                
                for item in low_stock_items:
                    urgency = "URGENT REORDER" if item['available_percentage'] < 10 else "PLAN REORDER"
                    reorder_qty = max(item['reorder_point'] * 2, item['min_stock'])
                    
                    print(f"{item['productId']:<15} "
                          f"{item['location']:<20} "
                          f"{item['available']:<10} "
                          f"{item['total']:<8} "
                          f"{item['available_percentage']:.1f}%{'':<3} "
                          f"{urgency}")
                    
                    print(f"{'':>15} Recommended order: {reorder_qty} units")
                    if item['turnover_days'] > 0:
                        print(f"{'':>15} Avg turnover: {item['turnover_days']} days")
                    print("-" * 100)
                    
            if overstock_items:
                print(f"\n[REPORT] OVERSTOCK ALERTS ({len(overstock_items)} items):")
                print("-" * 100)
                print(f"{'Product ID':<15} {'Location':<20} {'Available':<10} {'Total':<8} {'%':<6} {'Action':<20}")
                print("-" * 100)
                
                for item in overstock_items:
                    reduction_qty = item['available'] - (item['min_stock'] * 2)
                    
                    print(f"{item['productId']:<15} "
                          f"{item['location']:<20} "
                          f"{item['available']:<10} "
                          f"{item['total']:<8} "
                          f"{item['available_percentage']:.1f}%{'':<3} "
                          f"REDUCE STOCK")
                    
                    print(f"{'':>15} Consider reducing by: {reduction_qty} units")
                    if item['turnover_days'] > 0:
                        print(f"{'':>15} Slow turnover: {item['turnover_days']} days")
                    print("-" * 100)
                    
            if optimal_items:
                print(f"\n[SUCCESS] OPTIMAL STOCK LEVELS ({len(optimal_items)} items):")
                print("These items have healthy stock levels and good turnover rates.")
                
            # Summary statistics
            total_items = len(low_stock_items) + len(overstock_items) + len(optimal_items)
            if total_items > 0:
                print(f"\n[TRACK] OPTIMIZATION SUMMARY:")
                print(f"   [TARGET] Optimal: {len(optimal_items)} ({len(optimal_items)/total_items*100:.1f}%)")
                print(f"   [INTERRUPTED] Low Stock: {len(low_stock_items)} ({len(low_stock_items)/total_items*100:.1f}%)")
                print(f"   [REPORT] Overstock: {len(overstock_items)} ({len(overstock_items)/total_items*100:.1f}%)")
                
                # Calculate potential cost savings
                total_overstock_value = sum(self.get_product_value(item['productId']) * (item['available'] - item['min_stock']*2) 
                                           for item in overstock_items if item['available'] > item['min_stock']*2)
                
                if total_overstock_value > 0:
                    print(f"   [PRICE] Potential overstock value: ₹{total_overstock_value:,.2f}")
                    
            if not low_stock_items and not overstock_items:
                self.print_success("[SUMMARY] Excellent! All inventory levels are optimally balanced!")
                
        except Exception as e:
            self.print_error(f"Error reviewing stock optimization: {str(e)}")
            import traceback
            traceback.print_exc()
            
        input("Press Enter to continue...")
        
    def calculate_turnover_days(self, product_id: str) -> int:
        """Calculate average turnover days for a product"""
        try:
            # Simplified calculation - in real system would use historical sales data
            # For demo, return random realistic values
            import random
            return random.randint(7, 45)
        except:
            return 0
            
    def calculate_demand_forecast(self, product_id: str) -> dict:
        """Calculate demand forecast for a product"""
        try:
            # Simplified forecast - in real system would use ML/statistical models
            return {
                'next_7_days': 50,
                'next_30_days': 200,
                'trend': 'stable'
            }
        except:
            return {'next_7_days': 0, 'next_30_days': 0, 'trend': 'unknown'}
            
    def get_product_value(self, product_id: str) -> Decimal:
        """Get the monetary value of a product"""
        try:
            response = self.products_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            if response['Items']:
                product = response['Items'][0]
                return Decimal(str(product.get('costPrice', 0)))
            return Decimal('0')
        except:
            return Decimal('0')
        
    def plan_seasonal_adjustments(self):
        """Plan seasonal inventory adjustments"""
        self.clear_screen()
        self.print_header("SEASONAL INVENTORY ADJUSTMENTS")
        
        print("🌱 Seasonal Adjustment Planning:")
        print("1. [REPORT] Increase stock for high-demand seasons")
        print("2. 📉 Reduce stock for low-demand seasons")
        print("3. [TARGET] Set seasonal reorder points")
        print("4. [TRACK] View seasonal trends")
        
        choice = input("\n[TARGET] Select adjustment type (1-4): ").strip()
        
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
            print("2. [TRACK] Monitor Warehouse Productivity")
            print("3. 🏗️ Optimize Warehouse Layout")
            print("4. [CLIPBOARD] View Task Assignments")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [TEST] Set Quality Inspection Protocols")
            print("2. [TRACK] Review Quality Metrics")
            print("3. [ISSUE] Manage Product Recalls")
            print("4. [CLIPBOARD] View Quality Reports")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [CLIPBOARD] Review Pending Adjustments")
            print("2. [SUCCESS] Approve Adjustments")
            print("3. [ERROR] Reject Adjustments")
            print("4. [AUDIT] Investigate Discrepancies")
            print("5. [TRACK] View Adjustment History")
            print("6. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-6): ").strip()
            
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
            print("1. [ORDER] Oversee Goods Receiving")
            print("2. [INTERRUPTED] Resolve Receiving Discrepancies")
            print("3. [SUCCESS] Approve Put-Away Strategies")
            print("4. [CLIPBOARD] View Receiving Schedule")
            print("5. [TRACK] Receiving Performance")
            print("6. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-6): ").strip()
            
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
            print("2. [PRICE] Approve Markdown Strategies")
            print("3. [DELETE] Coordinate Disposal Activities")
            print("4. [TRACK] Expiry Analytics")
            print("5. [INTERRUPTED] Expiry Alerts")
            print("6. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-6): ").strip()
            
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
            print("1. [TRACK] Analyze Capacity Utilization")
            print("2. 🏗️ Plan Storage Reorganization")
            print("3. 🌡️ Monitor Temperature Zones")
            print("4. [REPORT] Space Efficiency Reports")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [TRACK] Inventory Reports")
            print("2. [REPORT] Performance Analytics")
            print("3. [PRICE] Cost Analysis")
            print("4. [INTERRUPTED] Alert Reports")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [CLIPBOARD] View All Products")
            print("2. [AUDIT] View Product Details")
            print("3. ✏️ Update Product Information")
            print("4. [VARIANT] Manage Product Variants")
            print("5. [SIZE] Manage Product Units")
            print("6. [PRICE] Update Product Pricing")
            print("7. [TRACK] Product Performance Analytics")
            print("8. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-8): ").strip()
            
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
                
            print(f"[ORDER] Found {len(products)} products:")
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
                
            print("[ORDER] Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n[TARGET] Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    
                    print(f"\n[ORDER] Product Details:")
                    print("-" * 60)
                    print(f"[ID] Product ID: {selected_product.get('productId', 'N/A')}")
                    print(f"[GENERATE] Name: {selected_product.get('name', 'N/A')}")
                    print(f"📄 Description: {selected_product.get('description', 'N/A')}")
                    print(f"[CATEGORY] Category: {selected_product.get('category', 'N/A')}")
                    print(f"[ACCOUNT] Brand: {selected_product.get('brand', 'N/A')}")
                    print(f"[PRICE] Cost Price: {selected_product.get('costPrice', 0)}")
                    print(f"💵 Selling Price: {selected_product.get('sellingPrice', 0)}")
                    print(f"[ORDER] Min Stock: {selected_product.get('minStock', 0)}")
                    print(f"[INTERRUPTED] Reorder Point: {selected_product.get('reorderPoint', 0)}")
                    print(f"[SUPPLIER] Supplier ID: {selected_product.get('supplierId', 'N/A')}")
                    print(f"[ADDRESS] Storage Location: {selected_product.get('storageLocation', 'N/A')}")
                    print(f"[VARIANT] Has Variants: {selected_product.get('hasVariants', False)}")
                    print(f"[SIZE] Base Unit: {selected_product.get('baseUnit', 'N/A')}")
                    print(f"[SIZE] Default Unit: {selected_product.get('defaultUnit', 'N/A')}")
                    print(f"⏰ Expiry Tracking: {selected_product.get('expiryTracking', False)}")
                    print(f"[ORDER] Batch Required: {selected_product.get('batchRequired', False)}")
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
                
            print("[ORDER] Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n[TARGET] Select product number: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    
                    print(f"\n[ORDER] Selected: {selected_product.get('name', 'N/A')}")
                    print("What would you like to update?")
                    print("1. [PRICE] Cost Price")
                    print("2. 💵 Selling Price")
                    print("3. [ORDER] Min Stock")
                    print("4. [INTERRUPTED] Reorder Point")
                    print("5. [ADDRESS] Storage Location")
                    print("6. 🌡️ Special Handling")
                    
                    update_choice = input("\n[TARGET] Select field to update (1-6): ").strip()
                    
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
        
    def assign_tasks_to_staff(self):
        """Assign tasks to warehouse staff"""
        self.clear_screen()
        self.print_header("ASSIGN TASKS TO STAFF")
        
        try:
            print("👥 Staff Task Assignment System")
            print("[NOTE] Delegate warehouse operations to improve efficiency")
            
            # Get available staff (from users with warehouse roles)
            staff_response = self.users_table.scan(
                FilterExpression='attribute_exists(#role) AND contains(#role, :inv_staff)',
                ExpressionAttributeNames={'#role': 'role'},
                ExpressionAttributeValues={':inv_staff': 'INVENTORY_STAFF'}
            )
            
            staff_members = staff_response.get('Items', [])
            
            if not staff_members:
                self.print_warning("No inventory staff found. Creating sample staff...")
                staff_members = self.create_sample_staff()
                
            # Task types
            print(f"\n[CLIPBOARD] Available Task Types:")
            print("1. [ORDER] Receiving & Inspection")
            print("2. [ADDRESS] Stock Movement & Put-away")
            print("3. [FLOW] Picking & Packing")
            print("4. [TRACK] Cycle Counting")
            print("5. [CLEANUP] Warehouse Maintenance")
            print("6. [AUDIT] Quality Control")
            print("7. [CLIPBOARD] Custom Task")
            
            task_choice = input("\n[TARGET] Select task type (1-7): ").strip()
            
            task_types = {
                '1': {'name': 'RECEIVING_INSPECTION', 'title': 'Receiving & Inspection', 'priority': 'HIGH'},
                '2': {'name': 'STOCK_MOVEMENT', 'title': 'Stock Movement & Put-away', 'priority': 'MEDIUM'},
                '3': {'name': 'PICKING_PACKING', 'title': 'Picking & Packing', 'priority': 'HIGH'},
                '4': {'name': 'CYCLE_COUNTING', 'title': 'Cycle Counting', 'priority': 'MEDIUM'},
                '5': {'name': 'MAINTENANCE', 'title': 'Warehouse Maintenance', 'priority': 'LOW'},
                '6': {'name': 'QUALITY_CONTROL', 'title': 'Quality Control', 'priority': 'HIGH'},
                '7': {'name': 'CUSTOM', 'title': 'Custom Task', 'priority': 'MEDIUM'}
            }
            
            if task_choice not in task_types:
                self.print_error("Invalid task type selection.")
                input("Press Enter to continue...")
                return
                
            selected_task_type = task_types[task_choice]
            
            # Task details
            if task_choice == '7':
                # Custom task
                task_title = input("\n[GENERATE] Task Title: ").strip()
                task_description = input("📄 Task Description: ").strip()
                
                priority_map = {'1': 'LOW', '2': 'MEDIUM', '3': 'HIGH', '4': 'URGENT'}
                priority_choice = input("⚡ Priority (1-Low, 2-Medium, 3-High, 4-Urgent): ").strip()
                priority = priority_map.get(priority_choice, 'MEDIUM')
                
            else:
                # Predefined task details
                task_details = self.get_predefined_task_details(selected_task_type['name'])
                task_title = task_details['title']
                task_description = task_details['description']
                priority = selected_task_type['priority']
                
            # Select staff member
            print(f"\n👥 Available Staff Members:")
            print("-" * 80)
            print(f"{'#':<3} {'Name':<20} {'Status':<15} {'Current Tasks':<12} {'Performance':<15}")
            print("-" * 80)
            
            for i, staff in enumerate(staff_members, 1):
                current_tasks = self.get_staff_current_tasks(staff.get('userId', ''))
                performance = self.get_staff_performance(staff.get('userId', ''))
                status = self.get_staff_status(staff.get('userId', ''))
                
                print(f"{i:<3} {staff.get('name', 'N/A')[:19]:<20} "
                      f"{status:<15} "
                      f"{current_tasks:<12} "
                      f"{performance:<15}")
                      
            print("-" * 80)
            
            staff_choice = input(f"\n[TARGET] Select staff member (1-{len(staff_members)}): ").strip()
            
            try:
                staff_index = int(staff_choice) - 1
                if 0 <= staff_index < len(staff_members):
                    selected_staff = staff_members[staff_index]
                    
                    # Due date
                    due_date = input("\n[DATE] Due Date (YYYY-MM-DD) or 'today': ").strip()
                    if due_date.lower() == 'today':
                        due_date = datetime.now().strftime('%Y-%m-%d')
                    elif not due_date:
                        due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                        
                    # Additional instructions
                    instructions = input("[GENERATE] Special Instructions (optional): ").strip()
                    
                    # Location/Area
                    location = input("[ADDRESS] Work Location/Area: ").strip() or "General Warehouse"
                    
                    # Estimated duration
                    duration = input("⏰ Estimated Duration (hours): ").strip()
                    if not duration.replace('.', '').isdigit():
                        duration = "4"  # Default 4 hours
                        
                    # Create task assignment
                    task_id = f'TASK-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
                    
                    task_assignment = {
                        'taskId': task_id,
                        'taskType': selected_task_type['name'],
                        'title': task_title,
                        'description': task_description,
                        'assignedTo': selected_staff['userId'],
                        'assignedBy': self.current_user.get('userId'),
                        'priority': priority,
                        'status': 'ASSIGNED',
                        'dueDate': due_date,
                        'location': location,
                        'estimatedDuration': float(duration),
                        'instructions': instructions,
                        'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                        'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                    
                    # Store task in notifications table
                    self.notifications_table.put_item(Item=task_assignment)
                    
                    # Log audit
                    self.log_audit('TASK_ASSIGNED', task_id, 
                                  f"Assigned {task_title} to {selected_staff.get('name')} - Priority: {priority}")
                    
                    # Display assignment summary
                    print(f"\n[SUCCESS] TASK ASSIGNED SUCCESSFULLY")
                    print("=" * 60)
                    print(f"[ID] Task ID: {task_id}")
                    print(f"[GENERATE] Title: {task_title}")
                    print(f"[USER] Assigned To: {selected_staff.get('name')}")
                    print(f"⚡ Priority: {priority}")
                    print(f"[DATE] Due Date: {due_date}")
                    print(f"[ADDRESS] Location: {location}")
                    print(f"⏰ Duration: {duration} hours")
                    print("=" * 60)
                    
                    # Send notification (simulation)
                    print(f"\n[EMAIL] Notification sent to {selected_staff.get('email', 'N/A')}")
                    print(f"[MOBILE] SMS alert sent to {selected_staff.get('phone', 'N/A')}")
                    
                else:
                    self.print_error("Invalid staff selection.")
            except ValueError:
                self.print_error("Invalid staff number.")
                
        except Exception as e:
            self.print_error(f"Error assigning task: {str(e)}")
            
        input("Press Enter to continue...")
        
    def create_sample_staff(self) -> list:
        """Create sample staff members for demo"""
        sample_staff = [
            {'userId': 'staff001', 'name': 'Raj Kumar', 'role': 'INVENTORY_STAFF', 'email': 'raj@company.com', 'phone': '+919876543201'},
            {'userId': 'staff002', 'name': 'Priya Singh', 'role': 'INVENTORY_STAFF', 'email': 'priya@company.com', 'phone': '+919876543202'},
            {'userId': 'staff003', 'name': 'Amit Patel', 'role': 'INVENTORY_STAFF', 'email': 'amit@company.com', 'phone': '+919876543203'}
        ]
        return sample_staff
        
    def get_predefined_task_details(self, task_type: str) -> dict:
        """Get predefined task details"""
        task_details = {
            'RECEIVING_INSPECTION': {
                'title': 'Receiving & Quality Inspection',
                'description': 'Receive incoming shipments, verify quantities, check quality, and update inventory records'
            },
            'STOCK_MOVEMENT': {
                'title': 'Stock Movement & Put-away',
                'description': 'Move received stock to designated storage locations and update location records'
            },
            'PICKING_PACKING': {
                'title': 'Order Picking & Packing',
                'description': 'Pick items for customer orders and pack them for shipment'
            },
            'CYCLE_COUNTING': {
                'title': 'Cycle Count Verification',
                'description': 'Perform cycle counts for assigned product categories and locations'
            },
            'MAINTENANCE': {
                'title': 'Warehouse Area Maintenance',
                'description': 'Clean and maintain warehouse areas, equipment, and storage systems'
            },
            'QUALITY_CONTROL': {
                'title': 'Quality Control Check',
                'description': 'Perform quality inspections on products and document findings'
            }
        }
        return task_details.get(task_type, {'title': 'General Task', 'description': 'Complete assigned warehouse task'})
        
    def get_staff_current_tasks(self, user_id: str) -> int:
        """Get current task count for a staff member"""
        try:
            # Simplified - in real system would query actual task assignments
            import random
            return random.randint(0, 5)
        except:
            return 0
            
    def get_staff_performance(self, user_id: str) -> str:
        """Get staff performance rating"""
        try:
            # Simplified - in real system would calculate from completed tasks
            ratings = ['Excellent', 'Good', 'Average', 'Needs Improvement']
            import random
            return random.choice(ratings)
        except:
            return 'N/A'
            
    def get_staff_status(self, user_id: str) -> str:
        """Get current staff status"""
        try:
            # Simplified - in real system would check actual availability
            statuses = ['Available', 'Busy', 'On Break', 'Off Duty']
            import random
            return random.choice(statuses)
        except:
            return 'Unknown'
        
    def monitor_warehouse_productivity(self):
        """Monitor warehouse productivity metrics"""
        self.clear_screen()
        self.print_header("MONITOR WAREHOUSE PRODUCTIVITY")
        
        try:
            print("[TRACK] Warehouse Productivity Dashboard")
            print("[NOTE] Track performance metrics and identify improvement opportunities")
            
            # Productivity metrics options
            print(f"\n[REPORT] Productivity Metrics:")
            print("1. 👥 Staff Performance")
            print("2. [ORDER] Order Fulfillment")
            print("3. [ADDRESS] Space Utilization")
            print("4. ⏰ Time Analytics")
            print("5. 🚛 Receiving Performance")
            print("6. [PRICE] Cost Efficiency")
            print("7. [TRACK] Overall Dashboard")
            
            metric_choice = input("\n[TARGET] Select metric to monitor (1-7): ").strip()
            
            if metric_choice == '1':
                self.show_staff_performance_metrics()
            elif metric_choice == '2':
                self.show_order_fulfillment_metrics()
            elif metric_choice == '3':
                self.show_space_utilization_metrics()
            elif metric_choice == '4':
                self.show_time_analytics()
            elif metric_choice == '5':
                self.show_receiving_performance()
            elif metric_choice == '6':
                self.show_cost_efficiency_metrics()
            elif metric_choice == '7':
                self.show_overall_productivity_dashboard()
            else:
                self.print_error("Invalid metric selection.")
                
        except Exception as e:
            self.print_error(f"Error monitoring productivity: {str(e)}")
            
        input("Press Enter to continue...")
        
    def show_staff_performance_metrics(self):
        """Show staff performance metrics"""
        print(f"\n👥 STAFF PERFORMANCE METRICS")
        print("=" * 80)
        
        # Simulated staff performance data
        staff_data = [
            {'name': 'Raj Kumar', 'tasks_completed': 45, 'accuracy': 98.5, 'efficiency': 92, 'attendance': 95},
            {'name': 'Priya Singh', 'tasks_completed': 52, 'accuracy': 96.8, 'efficiency': 88, 'attendance': 98},
            {'name': 'Amit Patel', 'tasks_completed': 38, 'accuracy': 99.2, 'efficiency': 85, 'attendance': 92}
        ]
        
        print(f"{'Staff Member':<20} {'Tasks':<8} {'Accuracy':<10} {'Efficiency':<12} {'Attendance':<12}")
        print("-" * 80)
        
        for staff in staff_data:
            print(f"{staff['name']:<20} "
                  f"{staff['tasks_completed']:<8} "
                  f"{staff['accuracy']:.1f}%{'':<6} "
                  f"{staff['efficiency']}%{'':<8} "
                  f"{staff['attendance']}%{'':<8}")
                  
        print("-" * 80)
        
        # Performance insights
        avg_accuracy = sum(s['accuracy'] for s in staff_data) / len(staff_data)
        avg_efficiency = sum(s['efficiency'] for s in staff_data) / len(staff_data)
        
        print(f"\n[TRACK] Team Performance Summary:")
        print(f"   [TARGET] Average Accuracy: {avg_accuracy:.1f}%")
        print(f"   ⚡ Average Efficiency: {avg_efficiency:.1f}%")
        print(f"   👥 Top Performer: {max(staff_data, key=lambda x: x['tasks_completed'])['name']}")
        
        print(f"\n[NOTE] Improvement Recommendations:")
        print(f"   • Schedule training for efficiency improvement")
        print(f"   • Implement performance incentives")
        print(f"   • Review workflow optimization opportunities")
        
    def show_order_fulfillment_metrics(self):
        """Show order fulfillment metrics"""
        print(f"\n[ORDER] ORDER FULFILLMENT METRICS")
        print("=" * 80)
        
        # Simulated fulfillment data
        fulfillment_data = {
            'orders_processed': 1247,
            'orders_completed': 1198,
            'orders_pending': 49,
            'avg_pick_time': '12.5 min',
            'avg_pack_time': '8.2 min',
            'accuracy_rate': 98.7,
            'on_time_shipment': 94.2
        }
        
        print(f"[TRACK] Daily Fulfillment Statistics:")
        print(f"   [ORDER] Orders Processed: {fulfillment_data['orders_processed']}")
        print(f"   [SUCCESS] Orders Completed: {fulfillment_data['orders_completed']}")
        print(f"   [WAIT] Orders Pending: {fulfillment_data['orders_pending']}")
        print(f"   [TARGET] Completion Rate: {fulfillment_data['orders_completed']/fulfillment_data['orders_processed']*100:.1f}%")
        
        print(f"\n⏰ Time Performance:")
        print(f"   [AUDIT] Average Pick Time: {fulfillment_data['avg_pick_time']}")
        print(f"   [ORDER] Average Pack Time: {fulfillment_data['avg_pack_time']}")
        print(f"   [DELIVERY] On-time Shipment: {fulfillment_data['on_time_shipment']}%")
        
        print(f"\n[REPORT] Quality Metrics:")
        print(f"   [SUCCESS] Order Accuracy: {fulfillment_data['accuracy_rate']}%")
        print(f"   [FLOW] Return Rate: {100 - fulfillment_data['accuracy_rate']:.1f}%")
        
        # Hourly breakdown
        print(f"\n⏰ Hourly Performance (Last 8 Hours):")
        print(f"{'Hour':<8} {'Orders':<8} {'Pick Time':<12} {'Accuracy':<10}")
        print("-" * 40)
        
        hourly_data = [
            ('9-10 AM', 156, '11.2 min', '99.1%'),
            ('10-11 AM', 142, '12.8 min', '98.5%'),
            ('11-12 PM', 165, '13.1 min', '97.8%'),
            ('1-2 PM', 134, '11.9 min', '99.2%')
        ]
        
        for hour, orders, pick_time, accuracy in hourly_data:
            print(f"{hour:<8} {orders:<8} {pick_time:<12} {accuracy:<10}")
            
    def show_space_utilization_metrics(self):
        """Show space utilization metrics"""
        print(f"\n[ADDRESS] SPACE UTILIZATION METRICS")
        print("=" * 80)
        
        # Simulated space data
        zones = [
            {'zone': 'Receiving', 'capacity': 1000, 'used': 750, 'efficiency': 85},
            {'zone': 'Storage A', 'capacity': 5000, 'used': 4200, 'efficiency': 92},
            {'zone': 'Storage B', 'capacity': 3000, 'used': 2100, 'efficiency': 78},
            {'zone': 'Picking', 'capacity': 800, 'used': 680, 'efficiency': 88},
            {'zone': 'Packing', 'capacity': 500, 'used': 420, 'efficiency': 91}
        ]
        
        print(f"{'Zone':<12} {'Capacity':<10} {'Used':<8} {'Utilization':<12} {'Efficiency':<12}")
        print("-" * 60)
        
        for zone in zones:
            utilization = zone['used'] / zone['capacity'] * 100
            print(f"{zone['zone']:<12} "
                  f"{zone['capacity']:<10} "
                  f"{zone['used']:<8} "
                  f"{utilization:.1f}%{'':<8} "
                  f"{zone['efficiency']}%{'':<8}")
                  
        print("-" * 60)
        
        # Utilization insights
        total_capacity = sum(z['capacity'] for z in zones)
        total_used = sum(z['used'] for z in zones)
        overall_utilization = total_used / total_capacity * 100
        
        print(f"\n[TRACK] Space Utilization Summary:")
        print(f"   [ORDER] Total Capacity: {total_capacity:,} sq ft")
        print(f"   [ADDRESS] Space Used: {total_used:,} sq ft")
        print(f"   [REPORT] Overall Utilization: {overall_utilization:.1f}%")
        
        # Recommendations
        underutilized = [z for z in zones if z['used']/z['capacity'] < 0.8]
        if underutilized:
            print(f"\n[NOTE] Optimization Opportunities:")
            for zone in underutilized:
                util_rate = zone['used']/zone['capacity']*100
                print(f"   • {zone['zone']}: {util_rate:.1f}% utilized - Consider reorganization")
                
    def show_time_analytics(self):
        """Show time analytics"""
        print(f"\n⏰ TIME ANALYTICS")
        print("=" * 80)
        
        # Process time breakdown
        process_times = {
            'Receiving': {'avg_time': 25, 'best_time': 18, 'worst_time': 45},
            'Put-away': {'avg_time': 15, 'best_time': 12, 'worst_time': 28},
            'Picking': {'avg_time': 12, 'best_time': 8, 'worst_time': 22},
            'Packing': {'avg_time': 8, 'best_time': 6, 'worst_time': 15},
            'Quality Check': {'avg_time': 5, 'best_time': 3, 'worst_time': 12}
        }
        
        print(f"{'Process':<15} {'Avg Time':<12} {'Best Time':<12} {'Worst Time':<12}")
        print("-" * 60)
        
        for process, times in process_times.items():
            print(f"{process:<15} "
                  f"{times['avg_time']} min{'':<6} "
                  f"{times['best_time']} min{'':<6} "
                  f"{times['worst_time']} min{'':<6}")
                  
        print("-" * 60)
        
        # Daily timeline
        print(f"\n[DATE] Daily Performance Timeline:")
        timeline_data = [
            ('8:00 AM', 'Peak receiving period'),
            ('10:00 AM', 'Optimal picking efficiency'),
            ('2:00 PM', 'Lunch break impact'),
            ('4:00 PM', 'End-of-day rush begins'),
            ('6:00 PM', 'Last shipment preparation')
        ]
        
        for time, activity in timeline_data:
            print(f"   {time}: {activity}")
            
    def show_receiving_performance(self):
        """Show receiving performance metrics"""
        print(f"\n🚛 RECEIVING PERFORMANCE")
        print("=" * 80)
        
        # Receiving metrics
        receiving_data = {
            'shipments_received': 45,
            'items_processed': 2847,
            'avg_processing_time': '32 min',
            'accuracy_rate': 97.8,
            'damage_rate': 1.2,
            'on_time_rate': 89.5
        }
        
        print(f"[ORDER] Daily Receiving Summary:")
        print(f"   [DELIVERY] Shipments Received: {receiving_data['shipments_received']}")
        print(f"   [CLIPBOARD] Items Processed: {receiving_data['items_processed']:,}")
        print(f"   ⏰ Avg Processing Time: {receiving_data['avg_processing_time']}")
        print(f"   [TARGET] Accuracy Rate: {receiving_data['accuracy_rate']}%")
        print(f"   💔 Damage Rate: {receiving_data['damage_rate']}%")
        print(f"   [TIMEOUT] On-time Rate: {receiving_data['on_time_rate']}%")
        
        # Supplier performance
        print(f"\n[SUPPLIER] Supplier Performance:")
        supplier_data = [
            ('Supplier A', 15, 98.5, 95.2),
            ('Supplier B', 12, 96.8, 87.3),
            ('Supplier C', 18, 99.1, 91.7)
        ]
        
        print(f"{'Supplier':<12} {'Shipments':<12} {'Accuracy':<10} {'On-time':<10}")
        print("-" * 50)
        for supplier, shipments, accuracy, ontime in supplier_data:
            print(f"{supplier:<12} {shipments:<12} {accuracy}%{'':<5} {ontime}%{'':<5}")
            
    def show_cost_efficiency_metrics(self):
        """Show cost efficiency metrics"""
        print(f"\n[PRICE] COST EFFICIENCY METRICS")
        print("=" * 80)
        
        # Cost breakdown
        cost_data = {
            'labor_cost_per_hour': 850,
            'cost_per_order': 12.50,
            'cost_per_item': 2.80,
            'storage_cost_per_sqft': 8.5,
            'equipment_cost_per_day': 1200
        }
        
        print(f"💵 Cost Breakdown:")
        print(f"   👥 Labor Cost per Hour: ₹{cost_data['labor_cost_per_hour']}")
        print(f"   [ORDER] Cost per Order: ₹{cost_data['cost_per_order']}")
        print(f"   [CLIPBOARD] Cost per Item: ₹{cost_data['cost_per_item']}")
        print(f"   [ADDRESS] Storage Cost per Sq Ft: ₹{cost_data['storage_cost_per_sqft']}")
        print(f"   [TOOL] Equipment Cost per Day: ₹{cost_data['equipment_cost_per_day']}")
        
        # Efficiency trends
        print(f"\n[REPORT] Monthly Efficiency Trends:")
        monthly_data = [
            ('January', 12.80, 95.2),
            ('February', 12.50, 96.8),
            ('March', 12.20, 97.5),
            ('April', 12.50, 96.1)
        ]
        
        print(f"{'Month':<12} {'Cost/Order':<12} {'Efficiency':<12}")
        print("-" * 40)
        for month, cost, efficiency in monthly_data:
            print(f"{month:<12} ₹{cost:<11} {efficiency}%{'':<8}")
            
    def show_overall_productivity_dashboard(self):
        """Show overall productivity dashboard"""
        print(f"\n[TRACK] OVERALL PRODUCTIVITY DASHBOARD")
        print("=" * 80)
        
        # Key performance indicators
        kpis = {
            'overall_efficiency': 91.5,
            'staff_utilization': 87.2,
            'space_utilization': 84.3,
            'cost_efficiency': 93.8,
            'quality_score': 96.7,
            'customer_satisfaction': 94.1
        }
        
        print(f"[REPORT] Key Performance Indicators:")
        print(f"   ⚡ Overall Efficiency: {kpis['overall_efficiency']}%")
        print(f"   👥 Staff Utilization: {kpis['staff_utilization']}%")
        print(f"   [ADDRESS] Space Utilization: {kpis['space_utilization']}%")
        print(f"   [PRICE] Cost Efficiency: {kpis['cost_efficiency']}%")
        print(f"   🏆 Quality Score: {kpis['quality_score']}%")
        print(f"   😊 Customer Satisfaction: {kpis['customer_satisfaction']}%")
        
        # Performance grade
        overall_score = sum(kpis.values()) / len(kpis)
        if overall_score >= 95:
            grade = "A+ (Excellent)"
        elif overall_score >= 90:
            grade = "A (Very Good)"
        elif overall_score >= 85:
            grade = "B (Good)"
        else:
            grade = "C (Needs Improvement)"
            
        print(f"\n🏆 Overall Performance Grade: {grade} ({overall_score:.1f}%)")
        
        # Action items
        print(f"\n[CLIPBOARD] Recommended Actions:")
        if kpis['staff_utilization'] < 90:
            print(f"   👥 Optimize staff scheduling and task allocation")
        if kpis['space_utilization'] < 85:
            print(f"   [ADDRESS] Review warehouse layout and storage optimization")
        if kpis['cost_efficiency'] < 95:
            print(f"   [PRICE] Analyze cost reduction opportunities")
        if len([k for k in kpis.values() if k < 90]) == 0:
            print(f"   [SUMMARY] Excellent performance! Continue current practices")
        
    def optimize_warehouse_layout(self):
        """Optimize warehouse layout for efficiency"""
        self.clear_screen()
        self.print_header("OPTIMIZE WAREHOUSE LAYOUT")
        
        try:
            print("🏗️ Warehouse Layout Optimization System")
            print("[NOTE] Analyze and improve warehouse space utilization")
            
            # Layout optimization options
            print(f"\n🏗️ Optimization Options:")
            print("1. [TRACK] Analyze Current Layout")
            print("2. [FLOW] ABC Analysis Optimization")
            print("3. [ADDRESS] Zone Efficiency Review")
            print("4. 🚛 Traffic Flow Analysis")
            print("5. [ORDER] Storage System Optimization")
            print("6. [NOTE] Layout Recommendations")
            
            layout_choice = input("\n[TARGET] Select optimization type (1-6): ").strip()
            
            if layout_choice == '1':
                self.analyze_current_layout()
            elif layout_choice == '2':
                self.abc_analysis_optimization()
            elif layout_choice == '3':
                self.zone_efficiency_review()
            elif layout_choice == '4':
                self.traffic_flow_analysis()
            elif layout_choice == '5':
                self.storage_system_optimization()
            elif layout_choice == '6':
                self.layout_recommendations()
            else:
                self.print_error("Invalid optimization option.")
                
        except Exception as e:
            self.print_error(f"Error optimizing warehouse layout: {str(e)}")
            
        input("Press Enter to continue...")
        
    def analyze_current_layout(self):
        """Analyze current warehouse layout"""
        print(f"\n[TRACK] CURRENT LAYOUT ANALYSIS")
        print("=" * 80)
        
        # Layout zones analysis
        layout_zones = [
            {'zone': 'Receiving Dock', 'area': 500, 'utilization': 75, 'efficiency': 82, 'bottleneck': False},
            {'zone': 'High-velocity Storage', 'area': 1200, 'utilization': 92, 'efficiency': 88, 'bottleneck': False},
            {'zone': 'Medium-velocity Storage', 'area': 2000, 'utilization': 78, 'efficiency': 85, 'bottleneck': False},
            {'zone': 'Low-velocity Storage', 'area': 1500, 'utilization': 65, 'efficiency': 72, 'bottleneck': True},
            {'zone': 'Picking Area', 'area': 800, 'utilization': 85, 'efficiency': 90, 'bottleneck': False},
            {'zone': 'Packing Area', 'area': 600, 'utilization': 88, 'efficiency': 93, 'bottleneck': False},
            {'zone': 'Shipping Dock', 'area': 400, 'utilization': 82, 'efficiency': 87, 'bottleneck': False}
        ]
        
        print(f"{'Zone':<20} {'Area (sqft)':<12} {'Utilization':<12} {'Efficiency':<12} {'Status':<12}")
        print("-" * 80)
        
        total_area = 0
        avg_utilization = 0
        avg_efficiency = 0
        
        for zone in layout_zones:
            status = "[INTERRUPTED] Bottleneck" if zone['bottleneck'] else "[SUCCESS] Optimal"
            print(f"{zone['zone']:<20} "
                  f"{zone['area']:<12} "
                  f"{zone['utilization']}%{'':<8} "
                  f"{zone['efficiency']}%{'':<8} "
                  f"{status:<12}")
                  
            total_area += zone['area']
            avg_utilization += zone['utilization']
            avg_efficiency += zone['efficiency']
            
        print("-" * 80)
        
        avg_utilization /= len(layout_zones)
        avg_efficiency /= len(layout_zones)
        
        print(f"\n[TRACK] Layout Summary:")
        print(f"   [ORDER] Total Area: {total_area:,} sq ft")
        print(f"   [REPORT] Average Utilization: {avg_utilization:.1f}%")
        print(f"   ⚡ Average Efficiency: {avg_efficiency:.1f}%")
        
        # Identify issues
        bottlenecks = [z for z in layout_zones if z['bottleneck']]
        low_efficiency = [z for z in layout_zones if z['efficiency'] < 80]
        
        if bottlenecks:
            print(f"\n[INTERRUPTED] Identified Bottlenecks:")
            for zone in bottlenecks:
                print(f"   • {zone['zone']}: {zone['efficiency']}% efficiency")
                
        if low_efficiency:
            print(f"\n📉 Low Efficiency Zones:")
            for zone in low_efficiency:
                print(f"   • {zone['zone']}: Needs improvement")
                
    def abc_analysis_optimization(self):
        """Perform ABC analysis for layout optimization"""
        print(f"\n[FLOW] ABC ANALYSIS OPTIMIZATION")
        print("=" * 80)
        
        # ABC classification of products
        abc_data = {
            'A_items': {'count': 150, 'revenue_percent': 70, 'frequency': 85, 'current_distance': 25},
            'B_items': {'count': 300, 'revenue_percent': 20, 'frequency': 60, 'current_distance': 45},
            'C_items': {'count': 550, 'revenue_percent': 10, 'frequency': 20, 'current_distance': 65}
        }
        
        print(f"[TRACK] Current ABC Distribution:")
        print(f"{'Category':<10} {'Items':<8} {'Revenue %':<12} {'Pick Freq':<12} {'Avg Distance':<15}")
        print("-" * 60)
        
        for category, data in abc_data.items():
            print(f"{category.replace('_', ' '):<10} "
                  f"{data['count']:<8} "
                  f"{data['revenue_percent']}%{'':<8} "
                  f"{data['frequency']}%{'':<8} "
                  f"{data['current_distance']} ft{'':<10}")
                  
        print("-" * 60)
        
        # Optimization recommendations
        print(f"\n[NOTE] ABC Optimization Recommendations:")
        print(f"   [ORDER] A-items (High value, High frequency):")
        print(f"      • Current avg distance: {abc_data['A_items']['current_distance']} ft")
        print(f"      • Recommended: Move to picking zone (10-15 ft)")
        print(f"      • Potential time savings: 40%")
        
        print(f"\n   [CLIPBOARD] B-items (Medium value, Medium frequency):")
        print(f"      • Current avg distance: {abc_data['B_items']['current_distance']} ft")
        print(f"      • Recommended: Secondary picking zone (20-30 ft)")
        print(f"      • Potential time savings: 25%")
        
        print(f"\n   📚 C-items (Low value, Low frequency):")
        print(f"      • Current avg distance: {abc_data['C_items']['current_distance']} ft")
        print(f"      • Recommended: Reserve storage (50+ ft)")
        print(f"      • Space optimization: 35%")
        
        # Implementation plan
        print(f"\n[CLIPBOARD] Implementation Plan:")
        print(f"   1. Relocate top 20 A-items to prime picking locations")
        print(f"   2. Create dedicated A-item zone near packing area")
        print(f"   3. Move slow-moving C-items to upper levels")
        print(f"   4. Establish clear ABC zone boundaries")
        print(f"   5. Regular review and reclassification (quarterly)")
        
    def zone_efficiency_review(self):
        """Review zone efficiency metrics"""
        print(f"\n[ADDRESS] ZONE EFFICIENCY REVIEW")
        print("=" * 80)
        
        # Zone performance metrics
        zone_metrics = [
            {'zone': 'Fast Pick Zone', 'picks_per_hour': 45, 'accuracy': 98.5, 'travel_time': 8, 'congestion': 15},
            {'zone': 'Bulk Storage', 'picks_per_hour': 20, 'accuracy': 96.8, 'travel_time': 25, 'congestion': 5},
            {'zone': 'Fragile Items', 'picks_per_hour': 12, 'accuracy': 99.2, 'travel_time': 18, 'congestion': 8},
            {'zone': 'Oversize Items', 'picks_per_hour': 8, 'accuracy': 97.1, 'travel_time': 35, 'congestion': 12}
        ]
        
        print(f"{'Zone':<15} {'Picks/Hour':<12} {'Accuracy':<10} {'Travel Time':<12} {'Congestion':<12}")
        print("-" * 70)
        
        for zone in zone_metrics:
            print(f"{zone['zone']:<15} "
                  f"{zone['picks_per_hour']:<12} "
                  f"{zone['accuracy']}%{'':<5} "
                  f"{zone['travel_time']} min{'':<6} "
                  f"{zone['congestion']}%{'':<8}")
                  
        print("-" * 70)
        
        # Efficiency scores
        print(f"\n[TRACK] Zone Efficiency Scores:")
        for zone in zone_metrics:
            # Calculate efficiency score (simplified formula)
            efficiency_score = (zone['picks_per_hour'] * zone['accuracy'] / 100) / (zone['travel_time'] + zone['congestion'])
            print(f"   {zone['zone']}: {efficiency_score:.2f}")
            
        # Recommendations
        print(f"\n[NOTE] Zone Optimization Recommendations:")
        high_congestion = [z for z in zone_metrics if z['congestion'] > 10]
        high_travel = [z for z in zone_metrics if z['travel_time'] > 20]
        
        if high_congestion:
            print(f"   🚶 High Congestion Zones:")
            for zone in high_congestion:
                print(f"      • {zone['zone']}: Consider widening aisles or alternate routing")
                
        if high_travel:
            print(f"   🚶 High Travel Time Zones:")
            for zone in high_travel:
                print(f"      • {zone['zone']}: Evaluate product placement and zone layout")
                
    def traffic_flow_analysis(self):
        """Analyze warehouse traffic flow"""
        print(f"\n🚛 TRAFFIC FLOW ANALYSIS")
        print("=" * 80)
        
        # Traffic patterns
        traffic_data = {
            'peak_hours': ['9-11 AM', '2-4 PM'],
            'bottleneck_points': ['Main Aisle Junction', 'Receiving Dock Entry', 'Packing Station'],
            'flow_efficiency': 78.5,
            'collision_incidents': 3,
            'wait_times': {'average': 2.3, 'peak': 5.7}
        }
        
        print(f"🚛 Traffic Flow Metrics:")
        print(f"   ⏰ Peak Traffic Hours: {', '.join(traffic_data['peak_hours'])}")
        print(f"   ⚡ Flow Efficiency: {traffic_data['flow_efficiency']}%")
        print(f"   [INTERRUPTED] Collision Incidents (weekly): {traffic_data['collision_incidents']}")
        print(f"   [TIME] Average Wait Time: {traffic_data['wait_times']['average']} min")
        print(f"   [TIME] Peak Wait Time: {traffic_data['wait_times']['peak']} min")
        
        print(f"\n[INTERRUPTED] Identified Bottlenecks:")
        for i, bottleneck in enumerate(traffic_data['bottleneck_points'], 1):
            print(f"   {i}. {bottleneck}")
            
        # Flow optimization suggestions
        print(f"\n[NOTE] Traffic Flow Optimization:")
        print(f"   🛣️ Create one-way traffic lanes in main aisles")
        print(f"   [ADDRESS] Install traffic signals at major intersections")
        print(f"   [EXIT] Add alternative routes to reduce congestion")
        print(f"   [MOBILE] Implement real-time traffic monitoring")
        print(f"   [TIMEOUT] Stagger shift times to reduce peak congestion")
        
        # Proposed layout changes
        print(f"\n[FLOW] Proposed Layout Improvements:")
        improvements = [
            {'area': 'Main Aisle', 'change': 'Widen from 8ft to 12ft', 'benefit': '+25% flow capacity'},
            {'area': 'Receiving', 'change': 'Add second entry point', 'benefit': '-40% wait time'},
            {'area': 'Cross Aisles', 'change': 'Add 3 new cross aisles', 'benefit': '+30% route options'}
        ]
        
        for improvement in improvements:
            print(f"   [ADDRESS] {improvement['area']}: {improvement['change']}")
            print(f"      [NOTE] Expected benefit: {improvement['benefit']}")
            
    def storage_system_optimization(self):
        """Optimize storage systems"""
        print(f"\n[ORDER] STORAGE SYSTEM OPTIMIZATION")
        print("=" * 80)
        
        # Current storage systems
        storage_systems = [
            {'system': 'Pallet Racking', 'capacity': 5000, 'utilization': 85, 'accessibility': 70, 'cost_per_slot': 150},
            {'system': 'Drive-in Racking', 'capacity': 2000, 'utilization': 92, 'accessibility': 45, 'cost_per_slot': 120},
            {'system': 'Cantilever Racking', 'capacity': 800, 'utilization': 78, 'accessibility': 85, 'cost_per_slot': 180},
            {'system': 'Mezzanine Storage', 'capacity': 1200, 'utilization': 65, 'accessibility': 60, 'cost_per_slot': 200}
        ]
        
        print(f"{'Storage System':<18} {'Capacity':<10} {'Util %':<8} {'Access %':<10} {'Cost/Slot':<12}")
        print("-" * 70)
        
        for system in storage_systems:
            print(f"{system['system']:<18} "
                  f"{system['capacity']:<10} "
                  f"{system['utilization']}%{'':<4} "
                  f"{system['accessibility']}%{'':<6} "
                  f"₹{system['cost_per_slot']:<11}")
                  
        print("-" * 70)
        
        # Storage optimization analysis
        print(f"\n[TRACK] Storage Optimization Analysis:")
        
        # Calculate efficiency scores
        for system in storage_systems:
            efficiency = (system['utilization'] + system['accessibility']) / 2
            cost_efficiency = efficiency / system['cost_per_slot'] * 100
            
            print(f"\n   {system['system']}:")
            print(f"      [REPORT] Efficiency Score: {efficiency:.1f}%")
            print(f"      [PRICE] Cost Efficiency: {cost_efficiency:.2f}")
            
            if system['utilization'] < 80:
                print(f"      [INTERRUPTED] Low utilization - consider densification")
            if system['accessibility'] < 60:
                print(f"      [INTERRUPTED] Poor accessibility - consider layout changes")
                
        # Recommendations
        print(f"\n[NOTE] Storage System Recommendations:")
        print(f"   [ORDER] High-turnover items: Use selective pallet racking")
        print(f"   📚 Low-turnover items: Use drive-in racking for density")
        print(f"   [SIZE] Long items: Optimize cantilever racking layout")
        print(f"   [REPORT] Vertical space: Expand mezzanine utilization")
        print(f"   🤖 Consider automation: Automated storage/retrieval systems")
        
    def layout_recommendations(self):
        """Provide comprehensive layout recommendations"""
        print(f"\n[NOTE] WAREHOUSE LAYOUT RECOMMENDATIONS")
        print("=" * 80)
        
        # Priority recommendations
        recommendations = [
            {
                'priority': 'HIGH',
                'category': 'ABC Optimization',
                'description': 'Relocate high-velocity items closer to picking areas',
                'impact': 'Reduce pick time by 30%',
                'cost': 'Low',
                'timeline': '2-3 weeks'
            },
            {
                'priority': 'HIGH',
                'category': 'Traffic Flow',
                'description': 'Create one-way traffic lanes in main aisles',
                'impact': 'Reduce congestion by 40%',
                'cost': 'Medium',
                'timeline': '1-2 weeks'
            },
            {
                'priority': 'MEDIUM',
                'category': 'Storage Density',
                'description': 'Implement vertical storage for slow-moving items',
                'impact': 'Increase capacity by 25%',
                'cost': 'High',
                'timeline': '4-6 weeks'
            },
            {
                'priority': 'MEDIUM',
                'category': 'Zone Design',
                'description': 'Consolidate similar product categories',
                'impact': 'Improve accuracy by 15%',
                'cost': 'Low',
                'timeline': '1-2 weeks'
            },
            {
                'priority': 'LOW',
                'category': 'Technology',
                'description': 'Install warehouse management system integration',
                'impact': 'Overall efficiency +20%',
                'cost': 'Very High',
                'timeline': '8-12 weeks'
            }
        ]
        
        # Group by priority
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            priority_recs = [r for r in recommendations if r['priority'] == priority]
            if priority_recs:
                print(f"\n🔥 {priority} PRIORITY RECOMMENDATIONS:")
                for rec in priority_recs:
                    print(f"   [CLIPBOARD] {rec['category']}: {rec['description']}")
                    print(f"      [NOTE] Impact: {rec['impact']}")
                    print(f"      [PRICE] Cost: {rec['cost']}")
                    print(f"      ⏰ Timeline: {rec['timeline']}")
                    print()
                    
        # Implementation roadmap
        print(f"[DATE] IMPLEMENTATION ROADMAP:")
        print("-" * 60)
        
        roadmap = [
            {'phase': 'Phase 1 (Weeks 1-2)', 'actions': ['Traffic flow optimization', 'Zone redesign']},
            {'phase': 'Phase 2 (Weeks 3-4)', 'actions': ['ABC relocation', 'Signage installation']},
            {'phase': 'Phase 3 (Weeks 5-8)', 'actions': ['Storage system upgrades', 'Staff training']},
            {'phase': 'Phase 4 (Weeks 9-12)', 'actions': ['Technology integration', 'Performance monitoring']}
        ]
        
        for phase in roadmap:
            print(f"\n{phase['phase']}:")
            for action in phase['actions']:
                print(f"   • {action}")
                
        # Expected outcomes
        print(f"\n[TRACK] EXPECTED OUTCOMES:")
        print(f"   ⚡ Overall Efficiency: +35%")
        print(f"   ⏰ Pick Time Reduction: 30%")
        print(f"   [ORDER] Capacity Increase: 25%")
        print(f"   [PRICE] Cost Savings: ₹2.5M annually")
        print(f"   [TARGET] Accuracy Improvement: +15%")
        print(f"   😊 Staff Satisfaction: +20%")
        
    def view_task_assignments(self):
        """View current task assignments"""
        self.clear_screen()
        self.print_header("VIEW TASK ASSIGNMENTS")
        
        try:
            print("[CLIPBOARD] Task Assignment Dashboard")
            print("[NOTE] Monitor and manage current warehouse task assignments")
            
            # Get task assignments (from notifications table)
            response = self.notifications_table.scan()
            all_items = response.get('Items', [])
            
            # Filter task assignments
            task_assignments = [item for item in all_items if item.get('taskId')]
            
            if not task_assignments:
                self.print_info("No task assignments found.")
                
                # Create sample task assignments for demo
                sample_tasks = self.create_sample_tasks()
                task_assignments = sample_tasks
                
            # Filter and display options
            print(f"\n[TRACK] Task View Options:")
            print("1. [CLIPBOARD] All Active Tasks")
            print("2. [USER] Tasks by Staff Member")
            print("3. ⚡ Tasks by Priority")
            print("4. [DATE] Tasks by Due Date")
            print("5. [TRACK] Task Status Summary")
            
            view_choice = input("\n[TARGET] Select view option (1-5): ").strip()
            
            if view_choice == '1':
                self.show_all_active_tasks(task_assignments)
            elif view_choice == '2':
                self.show_tasks_by_staff(task_assignments)
            elif view_choice == '3':
                self.show_tasks_by_priority(task_assignments)
            elif view_choice == '4':
                self.show_tasks_by_due_date(task_assignments)
            elif view_choice == '5':
                self.show_task_status_summary(task_assignments)
            else:
                self.print_error("Invalid view option.")
                
        except Exception as e:
            self.print_error(f"Error viewing task assignments: {str(e)}")
            
        input("Press Enter to continue...")
        
    def create_sample_tasks(self) -> list:
        """Create sample task assignments for demo"""
        sample_tasks = [
            {
                'taskId': 'TASK-20241201-001',
                'title': 'Receiving Inspection - Supplier A',
                'assignedTo': 'staff001',
                'assignedBy': 'warehouse_mgr',
                'priority': 'HIGH',
                'status': 'IN_PROGRESS',
                'dueDate': '2024-12-01',
                'location': 'Receiving Dock 1',
                'estimatedDuration': 4.0,
                'createdAt': '2024-12-01T08:00:00Z'
            },
            {
                'taskId': 'TASK-20241201-002',
                'title': 'Cycle Count - Zone A',
                'assignedTo': 'staff002',
                'assignedBy': 'warehouse_mgr',
                'priority': 'MEDIUM',
                'status': 'ASSIGNED',
                'dueDate': '2024-12-02',
                'location': 'Storage Zone A',
                'estimatedDuration': 6.0,
                'createdAt': '2024-12-01T09:00:00Z'
            },
            {
                'taskId': 'TASK-20241201-003',
                'title': 'Order Picking - Batch 45',
                'assignedTo': 'staff003',
                'assignedBy': 'warehouse_mgr',
                'priority': 'URGENT',
                'status': 'COMPLETED',
                'dueDate': '2024-12-01',
                'location': 'Picking Zone',
                'estimatedDuration': 3.0,
                'createdAt': '2024-12-01T07:00:00Z'
            }
        ]
        return sample_tasks
        
    def show_all_active_tasks(self, tasks: list):
        """Show all active task assignments"""
        active_tasks = [task for task in tasks if task.get('status') != 'COMPLETED']
        
        print(f"\n[CLIPBOARD] ALL ACTIVE TASKS ({len(active_tasks)} tasks)")
        print("=" * 120)
        print(f"{'Task ID':<20} {'Title':<25} {'Assigned To':<15} {'Priority':<10} {'Status':<12} {'Due Date':<12} {'Location':<20}")
        print("-" * 120)
        
        for task in active_tasks:
            print(f"{task.get('taskId', 'N/A'):<20} "
                  f"{task.get('title', 'N/A')[:24]:<25} "
                  f"{task.get('assignedTo', 'N/A'):<15} "
                  f"{task.get('priority', 'N/A'):<10} "
                  f"{task.get('status', 'N/A'):<12} "
                  f"{task.get('dueDate', 'N/A'):<12} "
                  f"{task.get('location', 'N/A')[:19]:<20}")
                  
        print("-" * 120)
        
        # Task status counts
        status_counts = {}
        for task in active_tasks:
            status = task.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print(f"\n[TRACK] Active Task Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} tasks")
            
    def show_tasks_by_staff(self, tasks: list):
        """Show tasks grouped by staff member"""
        print(f"\n[USER] TASKS BY STAFF MEMBER")
        print("=" * 80)
        
        # Group tasks by staff
        staff_tasks = {}
        for task in tasks:
            staff_id = task.get('assignedTo', 'Unassigned')
            if staff_id not in staff_tasks:
                staff_tasks[staff_id] = []
            staff_tasks[staff_id].append(task)
            
        for staff_id, staff_task_list in staff_tasks.items():
            active_tasks = [t for t in staff_task_list if t.get('status') != 'COMPLETED']
            completed_tasks = [t for t in staff_task_list if t.get('status') == 'COMPLETED']
            
            print(f"\n[USER] Staff: {staff_id}")
            print(f"   [CLIPBOARD] Active Tasks: {len(active_tasks)}")
            print(f"   [SUCCESS] Completed Tasks: {len(completed_tasks)}")
            
            if active_tasks:
                print(f"   [FLOW] Current Tasks:")
                for task in active_tasks:
                    priority_icon = "🔴" if task.get('priority') == 'URGENT' else "🟡" if task.get('priority') == 'HIGH' else "🟢"
                    print(f"      {priority_icon} {task.get('title', 'N/A')} - Due: {task.get('dueDate', 'N/A')}")
                    
    def show_tasks_by_priority(self, tasks: list):
        """Show tasks grouped by priority"""
        print(f"\n⚡ TASKS BY PRIORITY")
        print("=" * 80)
        
        priority_order = ['URGENT', 'HIGH', 'MEDIUM', 'LOW']
        
        for priority in priority_order:
            priority_tasks = [task for task in tasks if task.get('priority') == priority and task.get('status') != 'COMPLETED']
            
            if priority_tasks:
                priority_icon = "🔴" if priority == 'URGENT' else "🟡" if priority == 'HIGH' else "🟢"
                print(f"\n{priority_icon} {priority} PRIORITY ({len(priority_tasks)} tasks):")
                print("-" * 60)
                
                for task in priority_tasks:
                    print(f"   [CLIPBOARD] {task.get('title', 'N/A')}")
                    print(f"      [USER] Assigned: {task.get('assignedTo', 'N/A')}")
                    print(f"      [DATE] Due: {task.get('dueDate', 'N/A')}")
                    print(f"      [TRACK] Status: {task.get('status', 'N/A')}")
                    print()
                    
    def show_tasks_by_due_date(self, tasks: list):
        """Show tasks sorted by due date"""
        print(f"\n[DATE] TASKS BY DUE DATE")
        print("=" * 80)
        
        # Sort tasks by due date
        active_tasks = [task for task in tasks if task.get('status') != 'COMPLETED']
        sorted_tasks = sorted(active_tasks, key=lambda x: x.get('dueDate', '9999-12-31'))
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Categorize by urgency
        overdue = [t for t in sorted_tasks if t.get('dueDate', '') < current_date]
        today = [t for t in sorted_tasks if t.get('dueDate', '') == current_date]
        upcoming = [t for t in sorted_tasks if t.get('dueDate', '') > current_date]
        
        if overdue:
            print(f"\n🔴 OVERDUE TASKS ({len(overdue)} tasks):")
            for task in overdue:
                days_overdue = (datetime.now() - datetime.strptime(task.get('dueDate', current_date), '%Y-%m-%d')).days
                print(f"   [INTERRUPTED] {task.get('title', 'N/A')} - {days_overdue} days overdue")
                print(f"      [USER] {task.get('assignedTo', 'N/A')} - {task.get('priority', 'N/A')} priority")
                
        if today:
            print(f"\n🟡 DUE TODAY ({len(today)} tasks):")
            for task in today:
                print(f"   [DATE] {task.get('title', 'N/A')}")
                print(f"      [USER] {task.get('assignedTo', 'N/A')} - {task.get('priority', 'N/A')} priority")
                
        if upcoming:
            print(f"\n🟢 UPCOMING TASKS ({len(upcoming)} tasks):")
            for task in upcoming[:5]:  # Show next 5
                print(f"   [DATE] {task.get('title', 'N/A')} - Due: {task.get('dueDate', 'N/A')}")
                print(f"      [USER] {task.get('assignedTo', 'N/A')} - {task.get('priority', 'N/A')} priority")
                
    def show_task_status_summary(self, tasks: list):
        """Show task status summary and analytics"""
        print(f"\n[TRACK] TASK STATUS SUMMARY")
        print("=" * 80)
        
        # Status breakdown
        status_counts = {}
        priority_counts = {}
        
        for task in tasks:
            status = task.get('status', 'UNKNOWN')
            priority = task.get('priority', 'UNKNOWN')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        print(f"[CLIPBOARD] Task Status Distribution:")
        for status, count in status_counts.items():
            percentage = count / len(tasks) * 100 if tasks else 0
            print(f"   {status}: {count} tasks ({percentage:.1f}%)")
            
        print(f"\n⚡ Priority Distribution:")
        for priority, count in priority_counts.items():
            percentage = count / len(tasks) * 100 if tasks else 0
            print(f"   {priority}: {count} tasks ({percentage:.1f}%)")
            
        # Performance metrics
        completed_tasks = [t for t in tasks if t.get('status') == 'COMPLETED']
        completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
        
        print(f"\n[REPORT] Performance Metrics:")
        print(f"   [SUCCESS] Completion Rate: {completion_rate:.1f}%")
        print(f"   [CLIPBOARD] Total Tasks: {len(tasks)}")
        print(f"   [FLOW] Active Tasks: {len(tasks) - len(completed_tasks)}")
        
        # Staff workload
        staff_workload = {}
        for task in tasks:
            if task.get('status') != 'COMPLETED':
                staff = task.get('assignedTo', 'Unassigned')
                staff_workload[staff] = staff_workload.get(staff, 0) + 1
                
        if staff_workload:
            print(f"\n👥 Current Staff Workload:")
            for staff, workload in staff_workload.items():
                print(f"   {staff}: {workload} active tasks")
        
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
        """Increase stock levels for high-demand seasons"""
        self.clear_screen()
        self.print_header("INCREASE STOCK FOR HIGH-DEMAND SEASONS")
        
        try:
            print("[REPORT] Seasonal Stock Increase Planning")
            print("[NOTE] Proactively increase inventory for anticipated high-demand periods")
            
            # Get seasonal information
            print(f"\n🌱 Select Season:")
            print("1. 🌸 Spring (March-May)")
            print("2. ☀️ Summer (June-August)") 
            print("3. 🍂 Autumn (September-November)")
            print("4. ❄️ Winter (December-February)")
            print("5. [SUMMARY] Festival Season")
            print("6. [DATE] Custom Date Range")
            
            season_choice = input("\n[TARGET] Select season (1-6): ").strip()
            
            season_map = {
                '1': {'name': 'Spring', 'months': ['March', 'April', 'May'], 'multiplier': 1.3},
                '2': {'name': 'Summer', 'months': ['June', 'July', 'August'], 'multiplier': 1.5},
                '3': {'name': 'Autumn', 'months': ['September', 'October', 'November'], 'multiplier': 1.2},
                '4': {'name': 'Winter', 'months': ['December', 'January', 'February'], 'multiplier': 1.4},
                '5': {'name': 'Festival Season', 'months': ['October', 'November', 'December'], 'multiplier': 2.0},
                '6': {'name': 'Custom', 'months': [], 'multiplier': 1.0}
            }
            
            if season_choice not in season_map:
                self.print_error("Invalid season selection.")
                input("Press Enter to continue...")
                return
                
            selected_season = season_map[season_choice]
            
            if season_choice == '6':
                # Custom date range
                start_date = input("[DATE] Start date (YYYY-MM-DD): ").strip()
                end_date = input("[DATE] End date (YYYY-MM-DD): ").strip()
                multiplier_input = input("[TRACK] Demand multiplier (e.g., 1.5 for 50% increase): ").strip()
                
                try:
                    selected_season['multiplier'] = float(multiplier_input)
                    selected_season['start_date'] = start_date
                    selected_season['end_date'] = end_date
                except ValueError:
                    self.print_error("Invalid multiplier.")
                    input("Press Enter to continue...")
                    return
                    
            # Get products for seasonal adjustment
            print(f"\n[ORDER] Product Selection:")
            print("1. [TARGET] All Products")
            print("2. [CATEGORY] By Category")
            print("3. [CLIPBOARD] Select Individual Products")
            print("4. [TRACK] Based on Historical Demand")
            
            selection_choice = input("\n[TARGET] Select products (1-4): ").strip()
            
            selected_products = []
            
            if selection_choice == '1':
                # All products
                response = self.products_table.scan()
                selected_products = response.get('Items', [])
                
            elif selection_choice == '2':
                # By category
                response = self.products_table.scan()
                all_products = response.get('Items', [])
                
                # Get unique categories
                categories = list(set(product.get('category', 'Unknown') for product in all_products))
                
                print(f"\n📂 Available Categories:")
                for i, category in enumerate(categories, 1):
                    print(f"{i}. {category}")
                    
                cat_choice = input("\n[TARGET] Select category number: ").strip()
                
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        selected_category = categories[cat_index]
                        selected_products = [p for p in all_products if p.get('category') == selected_category]
                    else:
                        self.print_error("Invalid category selection.")
                        input("Press Enter to continue...")
                        return
                except ValueError:
                    self.print_error("Invalid category number.")
                    input("Press Enter to continue...")
                    return
                    
            elif selection_choice == '3':
                # Individual products
                response = self.products_table.scan()
                all_products = response.get('Items', [])
                
                print(f"\n[ORDER] Available Products:")
                for i, product in enumerate(all_products, 1):
                    print(f"{i}. {product.get('name', 'N/A')} (Current stock: {self.get_current_stock(product.get('productId'))})")
                    
                while True:
                    product_choice = input("\n[TARGET] Select product number (or 'done' to finish): ").strip()
                    
                    if product_choice.lower() == 'done':
                        break
                        
                    try:
                        product_index = int(product_choice) - 1
                        if 0 <= product_index < len(all_products):
                            selected_product = all_products[product_index]
                            if selected_product not in selected_products:
                                selected_products.append(selected_product)
                                self.print_success(f"Added {selected_product.get('name')}")
                            else:
                                self.print_warning("Product already selected.")
                        else:
                            self.print_error("Invalid product selection.")
                    except ValueError:
                        self.print_error("Invalid product number.")
                        
            elif selection_choice == '4':
                # Based on historical demand
                response = self.products_table.scan()
                all_products = response.get('Items', [])
                
                # Get products with high seasonal demand (simplified)
                for product in all_products:
                    seasonal_factor = self.get_seasonal_demand_factor(product.get('productId'), selected_season['name'])
                    if seasonal_factor > 1.2:  # Products with >20% seasonal increase
                        selected_products.append(product)
                        
            if not selected_products:
                self.print_info("No products selected for seasonal adjustment.")
                input("Press Enter to continue...")
                return
                
            # Calculate and display seasonal adjustments
            print(f"\n[TRACK] SEASONAL STOCK INCREASE PLAN - {selected_season['name']}")
            print("=" * 100)
            print(f"[REPORT] Demand Multiplier: {selected_season['multiplier']}x")
            print("=" * 100)
            print(f"{'Product':<25} {'Current Stock':<15} {'Recommended':<15} {'Increase':<12} {'Value':<12}")
            print("-" * 100)
            
            total_increase_value = Decimal('0')
            adjustment_plan = []
            
            for product in selected_products:
                product_id = product.get('productId')
                current_stock = self.get_current_stock(product_id)
                current_reorder = product.get('reorderPoint', 0)
                
                # Calculate seasonal adjustment
                seasonal_reorder = int(current_reorder * selected_season['multiplier'])
                recommended_stock = int(current_stock * selected_season['multiplier'])
                increase_needed = max(0, recommended_stock - current_stock)
                
                product_cost = Decimal(str(product.get('costPrice', 0)))
                increase_value = product_cost * increase_needed
                total_increase_value += increase_value
                
                adjustment_plan.append({
                    'product': product,
                    'current_stock': current_stock,
                    'recommended_stock': recommended_stock,
                    'increase_needed': increase_needed,
                    'seasonal_reorder': seasonal_reorder,
                    'increase_value': increase_value
                })
                
                print(f"{product.get('name', 'N/A')[:24]:<25} "
                      f"{current_stock:<15} "
                      f"{recommended_stock:<15} "
                      f"+{increase_needed:<11} "
                      f"₹{increase_value:<11}")
                      
            print("-" * 100)
            print(f"{'TOTAL INVESTMENT':<70} ₹{total_increase_value}")
            print("=" * 100)
            
            # Approval and implementation
            print(f"\n[CLIPBOARD] Implementation Options:")
            print("1. [SUCCESS] Approve and Create Purchase Orders")
            print("2. [GENERATE] Save as Draft Plan")
            print("3. [FLOW] Adjust Recommendations")
            print("4. [ERROR] Cancel")
            
            impl_choice = input("\n[TARGET] Select option (1-4): ").strip()
            
            if impl_choice == '1':
                # Create purchase orders
                confirm = input(f"\n[CONFIRM] Confirm seasonal stock increase (Total: ₹{total_increase_value})? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    for item in adjustment_plan:
                        if item['increase_needed'] > 0:
                            # Update seasonal reorder points
                            product = item['product']
                            self.products_table.update_item(
                                Key={'productId': product['productId'], 'category': product['category']},
                                UpdateExpression='SET seasonalReorderPoint = :sreorder, lastSeasonalAdjustment = :date, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':sreorder': item['seasonal_reorder'],
                                    ':date': datetime.now().isoformat(),
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            
                    # Log audit
                    self.log_audit('SEASONAL_STOCK_INCREASE', selected_season['name'], 
                                  f"Increased stock for {len(adjustment_plan)} products, Total value: {total_increase_value}")
                    
                    self.print_success("[SUCCESS] Seasonal stock increase plan implemented!")
                    self.print_info(f"[ORDER] {len(adjustment_plan)} products adjusted")
                    self.print_info(f"[PRICE] Total investment: ₹{total_increase_value}")
                    
                else:
                    self.print_info("Seasonal adjustment cancelled.")
                    
            elif impl_choice == '2':
                # Save as draft
                draft_id = f"DRAFT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                draft_data = {
                    'draftId': draft_id,
                    'type': 'SEASONAL_INCREASE',
                    'season': selected_season,
                    'adjustments': adjustment_plan,
                    'totalValue': float(total_increase_value),
                    'status': 'DRAFT',
                    'createdBy': self.current_user.get('userId'),
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                # Store in notifications table for later retrieval
                self.notifications_table.put_item(Item=draft_data)
                
                self.print_success(f"[SUCCESS] Seasonal plan saved as draft: {draft_id}")
                
            else:
                self.print_info("Seasonal adjustment cancelled.")
                
        except Exception as e:
            self.print_error(f"Error planning seasonal stock increase: {str(e)}")
            
        input("Press Enter to continue...")
        
    def get_current_stock(self, product_id: str) -> int:
        """Get current available stock for a product"""
        try:
            response = self.stock_levels_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            total_stock = 0
            for item in response.get('Items', []):
                total_stock += item.get('availableStock', 0)
                
            return total_stock
        except:
            return 0
            
    def get_seasonal_demand_factor(self, product_id: str, season: str) -> float:
        """Get seasonal demand factor for a product"""
        try:
            # Simplified - in real system would analyze historical sales data
            seasonal_factors = {
                'Spring': {'Fresh Produce': 1.4, 'Gardening': 1.8, 'default': 1.1},
                'Summer': {'Beverages': 1.6, 'Cooling': 1.9, 'default': 1.2},
                'Autumn': {'Warm Clothing': 1.5, 'default': 1.0},
                'Winter': {'Heating': 1.7, 'Holiday Items': 2.0, 'default': 1.1},
                'Festival Season': {'Gifts': 2.5, 'Decorations': 2.2, 'default': 1.8}
            }
            
            # Get product category
            response = self.products_table.scan(
                FilterExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product_id}
            )
            
            if response['Items']:
                category = response['Items'][0].get('category', 'default')
                return seasonal_factors.get(season, {}).get(category, seasonal_factors.get(season, {}).get('default', 1.0))
                
            return 1.0
        except:
            return 1.0
        
    def decrease_seasonal_stock(self):
        """Reduce stock levels for low-demand seasons"""
        self.clear_screen()
        self.print_header("REDUCE STOCK FOR LOW-DEMAND SEASONS")
        
        try:
            print("📉 Seasonal Stock Reduction Planning")
            print("[NOTE] Optimize inventory levels during low-demand periods")
            
            # Get current overstock items
            response = self.stock_levels_table.scan()
            stock_levels = response.get('Items', [])
            
            overstocked_items = []
            
            for item in stock_levels:
                available = item.get('availableStock', 0)
                
                # Get product info
                product_id = item.get('productId')
                try:
                    product_response = self.products_table.scan(
                        FilterExpression='productId = :pid',
                        ExpressionAttributeValues={':pid': product_id}
                    )
                    
                    if product_response['Items']:
                        product = product_response['Items'][0]
                        min_stock = product.get('minStock', 0)
                        
                        # Identify overstocked items (>3x min stock)
                        if available > min_stock * 3:
                            overstocked_items.append({
                                'product': product,
                                'stock_item': item,
                                'current_stock': available,
                                'min_stock': min_stock,
                                'excess_stock': available - (min_stock * 2),
                                'reduction_value': self.calculate_reduction_value(product, available - (min_stock * 2))
                            })
                except:
                    continue
                    
            if not overstocked_items:
                self.print_success("[SUMMARY] No overstocked items found. Inventory levels are optimal!")
                input("Press Enter to continue...")
                return
                
            # Display reduction opportunities
            print(f"\n[TRACK] STOCK REDUCTION OPPORTUNITIES")
            print("=" * 100)
            print(f"{'Product':<25} {'Current':<10} {'Min Stock':<10} {'Excess':<10} {'Reduction Value':<15}")
            print("-" * 100)
            
            total_reduction_value = Decimal('0')
            
            for item in overstocked_items:
                product = item['product']
                print(f"{product.get('name', 'N/A')[:24]:<25} "
                      f"{item['current_stock']:<10} "
                      f"{item['min_stock']:<10} "
                      f"{item['excess_stock']:<10} "
                      f"₹{item['reduction_value']:<14}")
                      
                total_reduction_value += item['reduction_value']
                
            print("-" * 100)
            print(f"{'TOTAL REDUCTION VALUE':<55} ₹{total_reduction_value}")
            print("=" * 100)
            
            # Reduction strategies
            print(f"\n[CLIPBOARD] Reduction Strategies:")
            print("1. [PRICE] Markdown/Discount Sales")
            print("2. [ORDER] Return to Supplier")
            print("3. [FLOW] Transfer to Other Locations")
            print("4. 🎁 Bundle with Popular Items")
            print("5. [DATE] Gradual Reduction Plan")
            
            strategy_choice = input("\n[TARGET] Select reduction strategy (1-5): ").strip()
            
            strategy_map = {
                '1': 'MARKDOWN_SALE',
                '2': 'RETURN_TO_SUPPLIER', 
                '3': 'TRANSFER_LOCATION',
                '4': 'BUNDLE_PRODUCTS',
                '5': 'GRADUAL_REDUCTION'
            }
            
            selected_strategy = strategy_map.get(strategy_choice, 'GRADUAL_REDUCTION')
            
            # Implementation details
            if strategy_choice == '1':
                discount_percent = input("[PRICE] Discount percentage (e.g., 20): ").strip()
                try:
                    discount = float(discount_percent)
                    print(f"\n[TRACK] Markdown Analysis:")
                    print(f"   [PRICE] Average discount: {discount}%")
                    print(f"   📉 Revenue impact: ₹{total_reduction_value * discount / 100}")
                except ValueError:
                    discount = 20  # Default
                    
            elif strategy_choice == '2':
                return_policy = input("[ORDER] Return policy terms: ").strip()
                print(f"\n[CLIPBOARD] Return to Supplier Plan:")
                print(f"   [GENERATE] Terms: {return_policy}")
                
            elif strategy_choice == '3':
                target_location = input("[ADDRESS] Target location for transfer: ").strip()
                print(f"\n[FLOW] Transfer Plan:")
                print(f"   [ADDRESS] Destination: {target_location}")
                
            # Confirm reduction plan
            confirm = input(f"\n[CONFIRM] Implement seasonal stock reduction plan? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                reduction_id = f"REDUCE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                # Create reduction records
                for item in overstocked_items:
                    # Update stock levels
                    stock_item = item['stock_item']
                    new_stock = item['current_stock'] - item['excess_stock']
                    
                    self.stock_levels_table.update_item(
                        Key={'productId': stock_item['productId'], 'location': stock_item['location']},
                        UpdateExpression='SET availableStock = :new_stock, lastReduction = :date, reductionStrategy = :strategy, updatedAt = :updated',
                        ExpressionAttributeValues={
                            ':new_stock': new_stock,
                            ':date': datetime.now().isoformat(),
                            ':strategy': selected_strategy,
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                # Log audit
                self.log_audit('SEASONAL_STOCK_REDUCTION', reduction_id, 
                              f"Reduced stock for {len(overstocked_items)} products using {selected_strategy}")
                
                self.print_success("[SUCCESS] Seasonal stock reduction plan implemented!")
                self.print_info(f"[ORDER] {len(overstocked_items)} products optimized")
                self.print_info(f"[PRICE] Potential value recovery: ₹{total_reduction_value}")
                
            else:
                self.print_info("Stock reduction cancelled.")
                
        except Exception as e:
            self.print_error(f"Error planning seasonal stock reduction: {str(e)}")
            
        input("Press Enter to continue...")
        
    def calculate_reduction_value(self, product: dict, excess_quantity: int) -> Decimal:
        """Calculate value of excess stock"""
        try:
            cost_price = Decimal(str(product.get('costPrice', 0)))
            return cost_price * excess_quantity
        except:
            return Decimal('0')
        
    def set_seasonal_reorder_points(self):
        """Set seasonal reorder points for products"""
        self.clear_screen()
        self.print_header("SET SEASONAL REORDER POINTS")
        
        try:
            print("[TARGET] Seasonal Reorder Point Management")
            print("[NOTE] Adjust reorder points based on seasonal demand patterns")
            
            # Get products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            # Season selection
            print(f"\n🌱 Select Season for Reorder Point Adjustment:")
            print("1. 🌸 Spring")
            print("2. ☀️ Summer") 
            print("3. 🍂 Autumn")
            print("4. ❄️ Winter")
            print("5. [SUMMARY] Festival Season")
            
            season_choice = input("\n[TARGET] Select season (1-5): ").strip()
            
            season_names = {
                '1': 'Spring',
                '2': 'Summer',
                '3': 'Autumn', 
                '4': 'Winter',
                '5': 'Festival Season'
            }
            
            selected_season = season_names.get(season_choice, 'Spring')
            
            print(f"\n[TRACK] Current vs Recommended Seasonal Reorder Points - {selected_season}")
            print("=" * 120)
            print(f"{'Product':<25} {'Category':<15} {'Current':<10} {'Seasonal':<12} {'Adjustment':<12} {'Justification':<30}")
            print("-" * 120)
            
            adjustment_recommendations = []
            
            for product in products:
                product_id = product.get('productId')
                current_reorder = product.get('reorderPoint', 0)
                category = product.get('category', 'Unknown')
                
                # Calculate seasonal adjustment factor
                seasonal_factor = self.get_seasonal_demand_factor(product_id, selected_season)
                seasonal_reorder = int(current_reorder * seasonal_factor)
                adjustment = seasonal_reorder - current_reorder
                
                # Justification based on historical patterns
                justification = self.get_seasonal_justification(category, selected_season, seasonal_factor)
                
                adjustment_recommendations.append({
                    'product': product,
                    'current_reorder': current_reorder,
                    'seasonal_reorder': seasonal_reorder,
                    'adjustment': adjustment,
                    'seasonal_factor': seasonal_factor,
                    'justification': justification
                })
                
                adjustment_symbol = "+" if adjustment > 0 else ""
                print(f"{product.get('name', 'N/A')[:24]:<25} "
                      f"{category[:14]:<15} "
                      f"{current_reorder:<10} "
                      f"{seasonal_reorder:<12} "
                      f"{adjustment_symbol}{adjustment:<11} "
                      f"{justification[:29]:<30}")
                      
            print("-" * 120)
            
            # Summary statistics
            increases = len([r for r in adjustment_recommendations if r['adjustment'] > 0])
            decreases = len([r for r in adjustment_recommendations if r['adjustment'] < 0])
            unchanged = len([r for r in adjustment_recommendations if r['adjustment'] == 0])
            
            print(f"\n[TRACK] Adjustment Summary:")
            print(f"   [REPORT] Increases: {increases} products")
            print(f"   📉 Decreases: {decreases} products") 
            print(f"   ⚡ Unchanged: {unchanged} products")
            
            # Approval options
            print(f"\n[CLIPBOARD] Implementation Options:")
            print("1. [SUCCESS] Apply All Recommendations")
            print("2. [TOOL] Apply Selected Products")
            print("3. [GENERATE] Save as Seasonal Template")
            print("4. [ERROR] Cancel")
            
            impl_choice = input("\n[TARGET] Select option (1-4): ").strip()
            
            if impl_choice == '1':
                # Apply all recommendations
                confirm = input(f"\n[CONFIRM] Apply seasonal reorder points for {selected_season}? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    applied_count = 0
                    
                    for rec in adjustment_recommendations:
                        if rec['adjustment'] != 0:
                            product = rec['product']
                            
                            # Update product with seasonal reorder point
                            self.products_table.update_item(
                                Key={'productId': product['productId'], 'category': product['category']},
                                UpdateExpression='SET seasonalReorderPoint = :sreorder, currentSeason = :season, seasonalFactor = :factor, updatedAt = :updated',
                                ExpressionAttributeValues={
                                    ':sreorder': rec['seasonal_reorder'],
                                    ':season': selected_season,
                                    ':factor': rec['seasonal_factor'],
                                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                                }
                            )
                            applied_count += 1
                            
                    # Log audit
                    self.log_audit('SEASONAL_REORDER_UPDATE', selected_season, 
                                  f"Updated seasonal reorder points for {applied_count} products")
                    
                    self.print_success(f"[SUCCESS] Seasonal reorder points updated!")
                    self.print_info(f"[ORDER] {applied_count} products adjusted for {selected_season}")
                    
                else:
                    self.print_info("Seasonal reorder point update cancelled.")
                    
            elif impl_choice == '2':
                # Apply selected products
                print(f"\n[ORDER] Select products to update:")
                selected_indices = []
                
                for i, rec in enumerate(adjustment_recommendations):
                    if rec['adjustment'] != 0:
                        apply = input(f"Update {rec['product'].get('name', 'N/A')} ({rec['adjustment']:+d})? (y/n): ").strip().lower()
                        if apply == 'y':
                            selected_indices.append(i)
                            
                if selected_indices:
                    for i in selected_indices:
                        rec = adjustment_recommendations[i]
                        product = rec['product']
                        
                        self.products_table.update_item(
                            Key={'productId': product['productId'], 'category': product['category']},
                            UpdateExpression='SET seasonalReorderPoint = :sreorder, currentSeason = :season, updatedAt = :updated',
                            ExpressionAttributeValues={
                                ':sreorder': rec['seasonal_reorder'],
                                ':season': selected_season,
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                    self.print_success(f"[SUCCESS] {len(selected_indices)} products updated!")
                    
            elif impl_choice == '3':
                # Save as template
                template_id = f"TEMPLATE-{selected_season}-{datetime.now().strftime('%Y%m%d')}"
                
                template_data = {
                    'templateId': template_id,
                    'season': selected_season,
                    'recommendations': adjustment_recommendations,
                    'createdBy': self.current_user.get('userId'),
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                self.notifications_table.put_item(Item=template_data)
                self.print_success(f"[SUCCESS] Seasonal template saved: {template_id}")
                
            else:
                self.print_info("Seasonal reorder point adjustment cancelled.")
                
        except Exception as e:
            self.print_error(f"Error setting seasonal reorder points: {str(e)}")
            
        input("Press Enter to continue...")
        
    def get_seasonal_justification(self, category: str, season: str, factor: float) -> str:
        """Get justification for seasonal adjustment"""
        try:
            if factor > 1.5:
                return f"High {season} demand"
            elif factor > 1.2:
                return f"Moderate {season} increase"
            elif factor < 0.8:
                return f"Low {season} demand"
            else:
                return "Stable demand"
        except:
            return "Historical pattern"
        
    def view_seasonal_trends(self):
        """View seasonal trends and analytics"""
        self.clear_screen()
        self.print_header("VIEW SEASONAL TRENDS")
        
        try:
            print("[TRACK] Seasonal Demand Trends & Analytics")
            print("[NOTE] Analyze historical patterns to optimize inventory planning")
            
            # Get products for trend analysis
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found for trend analysis.")
                input("Press Enter to continue...")
                return
                
            # Trend analysis options
            print(f"\n[REPORT] Trend Analysis Options:")
            print("1. [TRACK] Overall Seasonal Patterns")
            print("2. [CATEGORY] Category-wise Trends") 
            print("3. [ORDER] Product-specific Trends")
            print("4. [DATE] Year-over-Year Comparison")
            print("5. [FUTURE] Demand Forecasting")
            
            analysis_choice = input("\n[TARGET] Select analysis type (1-5): ").strip()
            
            if analysis_choice == '1':
                self.show_overall_seasonal_patterns()
            elif analysis_choice == '2':
                self.show_category_seasonal_trends()
            elif analysis_choice == '3':
                self.show_product_seasonal_trends()
            elif analysis_choice == '4':
                self.show_year_over_year_trends()
            elif analysis_choice == '5':
                self.show_demand_forecasting()
            else:
                self.print_error("Invalid analysis option.")
                
        except Exception as e:
            self.print_error(f"Error viewing seasonal trends: {str(e)}")
            
        input("Press Enter to continue...")
        
    def show_overall_seasonal_patterns(self):
        """Show overall seasonal demand patterns"""
        print(f"\n[TRACK] OVERALL SEASONAL DEMAND PATTERNS")
        print("=" * 80)
        
        # Simulated seasonal data - in real system would query historical sales
        seasonal_data = {
            'Spring': {'demand_index': 1.15, 'growth': '+15%', 'top_categories': ['Fresh Produce', 'Gardening', 'Cleaning']},
            'Summer': {'demand_index': 1.35, 'growth': '+35%', 'top_categories': ['Beverages', 'Cooling', 'Outdoor']},
            'Autumn': {'demand_index': 0.95, 'growth': '-5%', 'top_categories': ['Warm Clothing', 'Preserved Foods']},
            'Winter': {'demand_index': 1.25, 'growth': '+25%', 'top_categories': ['Heating', 'Holiday Items', 'Comfort Foods']},
            'Festival Season': {'demand_index': 1.85, 'growth': '+85%', 'top_categories': ['Gifts', 'Decorations', 'Special Foods']}
        }
        
        for season, data in seasonal_data.items():
            print(f"\n🌱 {season}:")
            print(f"   [REPORT] Demand Index: {data['demand_index']:.2f} ({data['growth']})")
            print(f"   🏆 Top Categories: {', '.join(data['top_categories'])}")
            
        print(f"\n[NOTE] Key Insights:")
        print(f"   • Summer shows highest overall demand increase (+35%)")
        print(f"   • Festival season creates exceptional spikes (+85%)")
        print(f"   • Autumn typically sees demand stabilization")
        print(f"   • Plan inventory increases 4-6 weeks before peak seasons")
        
    def show_category_seasonal_trends(self):
        """Show category-wise seasonal trends"""
        print(f"\n[CATEGORY] CATEGORY-WISE SEASONAL TRENDS")
        print("=" * 80)
        
        # Get product categories
        response = self.products_table.scan()
        products = response.get('Items', [])
        categories = list(set(product.get('category', 'Unknown') for product in products))
        
        print(f"{'Category':<20} {'Spring':<10} {'Summer':<10} {'Autumn':<10} {'Winter':<10} {'Festival':<10}")
        print("-" * 80)
        
        for category in categories[:10]:  # Show top 10 categories
            # Simulated category trends
            trends = {
                'Fresh Produce': {'Spring': 1.4, 'Summer': 1.2, 'Autumn': 0.9, 'Winter': 0.8, 'Festival': 1.1},
                'Beverages': {'Spring': 1.1, 'Summer': 1.6, 'Autumn': 0.9, 'Winter': 0.8, 'Festival': 1.3},
                'Electronics': {'Spring': 1.0, 'Summer': 1.1, 'Autumn': 1.0, 'Winter': 1.2, 'Festival': 2.0},
                'Clothing': {'Spring': 1.2, 'Summer': 0.8, 'Autumn': 1.3, 'Winter': 1.5, 'Festival': 1.4}
            }
            
            cat_trends = trends.get(category, {'Spring': 1.0, 'Summer': 1.0, 'Autumn': 1.0, 'Winter': 1.0, 'Festival': 1.0})
            
            print(f"{category[:19]:<20} "
                  f"{cat_trends['Spring']:<10.1f} "
                  f"{cat_trends['Summer']:<10.1f} "
                  f"{cat_trends['Autumn']:<10.1f} "
                  f"{cat_trends['Winter']:<10.1f} "
                  f"{cat_trends['Festival']:<10.1f}")
                  
    def show_product_seasonal_trends(self):
        """Show product-specific seasonal trends"""
        print(f"\n[ORDER] PRODUCT-SPECIFIC SEASONAL TRENDS")
        print("=" * 80)
        
        # Get products
        response = self.products_table.scan()
        products = response.get('Items', [])
        
        print(f"[ORDER] Select products for detailed trend analysis:")
        for i, product in enumerate(products[:10], 1):  # Show first 10
            print(f"{i}. {product.get('name', 'N/A')}")
            
        product_choice = input(f"\n[TARGET] Select product number (1-{min(10, len(products))}): ").strip()
        
        try:
            product_index = int(product_choice) - 1
            if 0 <= product_index < len(products):
                selected_product = products[product_index]
                
                print(f"\n[TRACK] Seasonal Trend Analysis: {selected_product.get('name', 'N/A')}")
                print("-" * 60)
                
                # Simulated product trends
                print(f"[REPORT] Historical Demand Patterns:")
                print(f"   🌸 Spring: 120% of baseline (+20%)")
                print(f"   ☀️ Summer: 80% of baseline (-20%)")
                print(f"   🍂 Autumn: 110% of baseline (+10%)")
                print(f"   ❄️ Winter: 140% of baseline (+40%)")
                print(f"   [SUMMARY] Festival: 200% of baseline (+100%)")
                
                print(f"\n[TRACK] Recommended Actions:")
                print(f"   • Increase stock by 40% before winter season")
                print(f"   • Reduce summer inventory to avoid overstock")
                print(f"   • Plan special promotions for spring launch")
                print(f"   • Prepare festival season inventory 6 weeks ahead")
                
        except ValueError:
            self.print_error("Invalid product selection.")
            
    def show_year_over_year_trends(self):
        """Show year-over-year comparison"""
        print(f"\n[DATE] YEAR-OVER-YEAR SEASONAL COMPARISON")
        print("=" * 80)
        
        # Simulated YoY data
        print(f"{'Season':<20} {'2022':<12} {'2023':<12} {'2024 (Proj)':<15} {'Growth':<10}")
        print("-" * 70)
        
        yoy_data = [
            ('Spring', '₹2.5M', '₹2.8M', '₹3.1M', '+12%'),
            ('Summer', '₹3.2M', '₹3.6M', '₹4.0M', '+11%'),
            ('Autumn', '₹2.1M', '₹2.2M', '₹2.4M', '+9%'),
            ('Winter', '₹2.8M', '₹3.2M', '₹3.6M', '+13%'),
            ('Festival', '₹4.5M', '₹5.2M', '₹6.1M', '+17%')
        ]
        
        for season, y2022, y2023, y2024, growth in yoy_data:
            print(f"{season:<20} {y2022:<12} {y2023:<12} {y2024:<15} {growth:<10}")
            
        print(f"\n[NOTE] Key Trends:")
        print(f"   [REPORT] Consistent growth across all seasons (9-17%)")
        print(f"   [SUMMARY] Festival season shows strongest growth (+17%)")
        print(f"   🌱 Spring and Winter showing accelerating growth")
        
    def show_demand_forecasting(self):
        """Show demand forecasting"""
        print(f"\n[FUTURE] SEASONAL DEMAND FORECASTING")
        print("=" * 80)
        
        # Simulated forecasting data
        print(f"[TRACK] Next 12 Months Demand Forecast:")
        print(f"\n{'Month':<15} {'Demand Index':<15} {'Confidence':<12} {'Key Drivers':<30}")
        print("-" * 80)
        
        forecast_data = [
            ('January', '1.25', '85%', 'Post-holiday, Winter products'),
            ('February', '1.15', '80%', 'Valentine season'),
            ('March', '1.30', '90%', 'Spring preparation'),
            ('April', '1.20', '85%', 'Spring peak'),
            ('May', '1.10', '75%', 'Pre-summer transition'),
            ('June', '1.35', '90%', 'Summer season start')
        ]
        
        for month, index, confidence, drivers in forecast_data:
            print(f"{month:<15} {index:<15} {confidence:<12} {drivers:<30}")
            
        print(f"\n[TARGET] Forecasting Recommendations:")
        print(f"   [REPORT] Prepare for March spring surge (+30% demand)")
        print(f"   ☀️ Build summer inventory for June launch")
        print(f"   [TRACK] High confidence in Q1-Q2 projections (80-90%)")
        print(f"   [INTERRUPTED] Monitor external factors (weather, economy)")
        
        print(f"\n[CLIPBOARD] Action Items:")
        print(f"   • Order spring inventory by February 15")
        print(f"   • Summer product launch preparation by May 1")
        print(f"   • Adjust staffing levels for peak seasons")
        
    def purchase_order_management_menu(self):
        """Purchase Order Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PURCHASE ORDER MANAGEMENT")
            print("1. [CLIPBOARD] Create New Purchase Order")
            print("2. [TRACK] View All Purchase Orders")
            print("3. [AUDIT] View Purchase Order Details")
            print("4. ✏️ Update Purchase Order")
            print("5. [REPORT] Purchase Order Analytics")
            print("6. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-6): ").strip()
            
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
                
            print("[SUPPLIER] Available Suppliers:")
            for i, supplier in enumerate(suppliers, 1):
                print(f"{i}. {supplier.get('name', 'N/A')} - {supplier.get('supplierId', 'N/A')}")
                
            supplier_choice = input("\n[TARGET] Select supplier number: ").strip()
            
            try:
                supplier_index = int(supplier_choice) - 1
                if 0 <= supplier_index < len(suppliers):
                    selected_supplier = suppliers[supplier_index]
                    supplier_id = selected_supplier['supplierId']
                    
                    print(f"\n[SUPPLIER] Selected Supplier: {selected_supplier.get('name', 'N/A')}")
                    
                    # Get available products
                    products_response = self.products_table.scan()
                    products = products_response.get('Items', [])
                    
                    if not products:
                        self.print_error("No products found.")
                        input("Press Enter to continue...")
                        return
                        
                    print("\n[ORDER] Available Products:")
                    for i, product in enumerate(products, 1):
                        print(f"{i}. {product.get('name', 'N/A')} - {product.get('sellingPrice', 0)}")
                        
                    # Select products for the order
                    selected_products = []
                    total_amount = Decimal('0')
                    
                    while True:
                        product_choice = input("\n[TARGET] Select product number (or 'done' to finish): ").strip()
                        
                        if product_choice.lower() == 'done':
                            break
                            
                        try:
                            product_index = int(product_choice) - 1
                            if 0 <= product_index < len(products):
                                selected_product = products[product_index]
                                quantity = input(f"[ORDER] Quantity for {selected_product.get('name')}: ").strip()
                                
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
                    delivery_date = input("\n[DATE] Expected Delivery Date (YYYY-MM-DD): ").strip()
                    if not delivery_date:
                        delivery_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                        
                    notes = input("\n[GENERATE] Order Notes (optional): ").strip()
                    
                    # Order summary
                    print(f"\n[CLIPBOARD] Purchase Order Summary:")
                    print("-" * 60)
                    print(f"[SUPPLIER] Supplier: {selected_supplier.get('name', 'N/A')}")
                    print(f"[DATE] Delivery Date: {delivery_date}")
                    print(f"[GENERATE] Notes: {notes or 'None'}")
                    print("-" * 60)
                    for item in selected_products:
                        print(f"  • {item['name']} x{item['quantity']} = {item['total']}")
                    print("-" * 60)
                    print(f"[PRICE] Total Amount: {total_amount}")
                    
                    # Confirm order
                    confirm = input("\n[CONFIRM] Confirm purchase order? (yes/no): ").strip().lower()
                    
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
                
            print(f"[CLIPBOARD] Purchase Orders ({len(purchase_orders)} orders):")
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
                
            print(f"\n[TRACK] Status Breakdown:")
            for status, count in status_counts.items():
                print(f"  • {status}: {count} orders")
                
            # Total value
            total_value = sum(Decimal(str(po.get('totalAmount', 0))) for po in purchase_orders)
            print(f"\n[PRICE] Total Value: {total_value}")
            
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
                
            print("[CLIPBOARD] Available Purchase Orders:")
            for i, po in enumerate(purchase_orders, 1):
                print(f"{i}. {po.get('poId', 'N/A')} - {po.get('supplierId', 'N/A')} - {po.get('totalAmount', 0)}")
                
            po_choice = input("\n[TARGET] Select purchase order number: ").strip()
            
            try:
                po_index = int(po_choice) - 1
                if 0 <= po_index < len(purchase_orders):
                    selected_po = purchase_orders[po_index]
                    
                    print(f"\n[CLIPBOARD] Purchase Order Details:")
                    print("-" * 60)
                    print(f"[ID] PO ID: {selected_po.get('poId', 'N/A')}")
                    print(f"[SUPPLIER] Supplier ID: {selected_po.get('supplierId', 'N/A')}")
                    print(f"[DATE] Order Date: {selected_po.get('orderDate', 'N/A')[:19]}")
                    print(f"[DATE] Expected Delivery: {selected_po.get('expectedDeliveryDate', 'N/A')}")
                    print(f"[PRICE] Total Amount: {selected_po.get('totalAmount', 0)}")
                    print(f"[TRACK] Status: {selected_po.get('status', 'N/A')}")
                    print(f"[USER] Created By: {selected_po.get('createdBy', 'N/A')}")
                    print(f"[GENERATE] Notes: {selected_po.get('notes', 'None')}")
                    print("-" * 60)
                    
                    # Show order items
                    items = selected_po.get('items', [])
                    if items:
                        print("[ORDER] Order Items:")
                        for item in items:
                            print(f"  • {item.get('name', 'N/A')} x{item.get('quantity', 0)} = {item.get('total', 0)}")
                    else:
                        print("[ORDER] No items found.")
                        
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
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
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