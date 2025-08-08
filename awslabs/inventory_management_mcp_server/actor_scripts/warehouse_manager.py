# warehouse_manager.py
import boto3
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional
from auth_manager import AuthManager


class WarehouseManager:
    """Warehouse Manager Operations for Inventory Management System"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth = auth_manager
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.batches_table = self.dynamodb.Table('InventoryManagement-Batches')
        self.suppliers_table = self.dynamodb.Table('InventoryManagement-Suppliers')
        self.purchase_orders_table = self.dynamodb.Table('InventoryManagement-PurchaseOrders')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"🏢 {title}")
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
        """Show Warehouse Manager main menu"""
        while True:
            self.print_header("WAREHOUSE MANAGER DASHBOARD")
            user_info = self.auth.get_current_user_info()
            print(f"👤 User: {user_info.get('name', 'Unknown')}")
            print(f"🏢 Role: {user_info.get('role', 'Unknown')}")
            print(f"📧 Email: {user_info.get('email', 'Unknown')}")
            
            print("\n📋 Available Operations:")
            print("1. 📊 Inventory Planning")
            print("2. 🏭 Warehouse Operations Management")
            print("3. 🧪 Quality Control")
            print("4. ✅ Stock Adjustment Approval")
            print("5. 📦 Receiving Management")
            print("6. ⏰ Expiry Management")
            print("7. 🏗️ Space Optimization")
            print("8. 📈 Reports & Analytics")
            print("9. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-9): ").strip()
            
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
                self.auth.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Warehouse Manager system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                
    def inventory_planning_menu(self):
        """Inventory Planning Operations"""
        while True:
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
                
    def view_stock_levels(self):
        """View current stock levels"""
        self.print_header("CURRENT STOCK LEVELS")
        
        try:
            response = self.stock_levels_table.scan()
            items = response.get('Items', [])
            
            if not items:
                self.print_info("No stock levels found.")
                return
                
            print(f"📊 Found {len(items)} stock level records:")
            print("-" * 80)
            print(f"{'Product ID':<15} {'Location':<25} {'Total':<8} {'Available':<10} {'Reserved':<10} {'Damaged':<10}")
            print("-" * 80)
            
            for item in items:
                print(f"{item.get('productId', 'N/A'):<15} "
                      f"{item.get('location', 'N/A'):<25} "
                      f"{item.get('totalStock', 0):<8} "
                      f"{item.get('availableStock', 0):<10} "
                      f"{item.get('reservedStock', 0):<10} "
                      f"{item.get('damagedStock', 0):<10}")
                      
        except Exception as e:
            self.print_error(f"Error viewing stock levels: {str(e)}")
            
    def set_reorder_points(self):
        """Set reorder points for products"""
        self.print_header("SET REORDER POINTS")
        
        try:
            # Get products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
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
            
    def set_safety_stock_levels(self):
        """Set safety stock levels"""
        self.print_header("SET SAFETY STOCK LEVELS")
        self.print_info("Safety stock levels help prevent stockouts during unexpected demand.")
        
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
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
            
    def review_stock_optimization(self):
        """Review stock optimization recommendations"""
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
                print("-" * 60)
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
                    print("-" * 60)
            else:
                self.print_success("No low stock alerts. Inventory levels are healthy!")
                
        except Exception as e:
            self.print_error(f"Error reviewing stock optimization: {str(e)}")
            
    def plan_seasonal_adjustments(self):
        """Plan seasonal inventory adjustments"""
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
            
    def warehouse_operations_menu(self):
        """Warehouse Operations Management"""
        while True:
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
                
    def quality_control_menu(self):
        """Quality Control Operations"""
        while True:
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
                
    def stock_adjustment_approval_menu(self):
        """Stock Adjustment Approval Operations"""
        while True:
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
                
    def receiving_management_menu(self):
        """Receiving Management Operations"""
        while True:
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
                
    def expiry_management_menu(self):
        """Expiry Management Operations"""
        while True:
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
                
    def space_optimization_menu(self):
        """Space Optimization Operations"""
        while True:
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
                
    def reports_analytics_menu(self):
        """Reports and Analytics"""
        while True:
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
                
    # Placeholder methods for other operations
    def assign_tasks_to_staff(self):
        self.print_info("Task assignment functionality will be implemented.")
        
    def monitor_warehouse_productivity(self):
        self.print_info("Productivity monitoring functionality will be implemented.")
        
    def optimize_warehouse_layout(self):
        self.print_info("Layout optimization functionality will be implemented.")
        
    def view_task_assignments(self):
        self.print_info("Task assignment viewing functionality will be implemented.")
        
    def set_quality_protocols(self):
        self.print_info("Quality protocol setting functionality will be implemented.")
        
    def review_quality_metrics(self):
        self.print_info("Quality metrics review functionality will be implemented.")
        
    def manage_product_recalls(self):
        self.print_info("Product recall management functionality will be implemented.")
        
    def view_quality_reports(self):
        self.print_info("Quality report viewing functionality will be implemented.")
        
    def review_pending_adjustments(self):
        self.print_info("Pending adjustments review functionality will be implemented.")
        
    def approve_adjustments(self):
        self.print_info("Adjustment approval functionality will be implemented.")
        
    def reject_adjustments(self):
        self.print_info("Adjustment rejection functionality will be implemented.")
        
    def investigate_discrepancies(self):
        self.print_info("Discrepancy investigation functionality will be implemented.")
        
    def view_adjustment_history(self):
        self.print_info("Adjustment history viewing functionality will be implemented.")
        
    def oversee_goods_receiving(self):
        self.print_info("Goods receiving oversight functionality will be implemented.")
        
    def resolve_receiving_discrepancies(self):
        self.print_info("Receiving discrepancy resolution functionality will be implemented.")
        
    def approve_putaway_strategies(self):
        self.print_info("Put-away strategy approval functionality will be implemented.")
        
    def view_receiving_schedule(self):
        self.print_info("Receiving schedule viewing functionality will be implemented.")
        
    def receiving_performance(self):
        self.print_info("Receiving performance functionality will be implemented.")
        
    def monitor_expiring_products(self):
        self.print_info("Expiring products monitoring functionality will be implemented.")
        
    def approve_markdown_strategies(self):
        self.print_info("Markdown strategy approval functionality will be implemented.")
        
    def coordinate_disposal_activities(self):
        self.print_info("Disposal activity coordination functionality will be implemented.")
        
    def expiry_analytics(self):
        self.print_info("Expiry analytics functionality will be implemented.")
        
    def expiry_alerts(self):
        self.print_info("Expiry alerts functionality will be implemented.")
        
    def analyze_capacity_utilization(self):
        self.print_info("Capacity utilization analysis functionality will be implemented.")
        
    def plan_storage_reorganization(self):
        self.print_info("Storage reorganization planning functionality will be implemented.")
        
    def monitor_temperature_zones(self):
        self.print_info("Temperature zone monitoring functionality will be implemented.")
        
    def space_efficiency_reports(self):
        self.print_info("Space efficiency reporting functionality will be implemented.")
        
    def inventory_reports(self):
        self.print_info("Inventory reporting functionality will be implemented.")
        
    def performance_analytics(self):
        self.print_info("Performance analytics functionality will be implemented.")
        
    def cost_analysis(self):
        self.print_info("Cost analysis functionality will be implemented.")
        
    def alert_reports(self):
        self.print_info("Alert reporting functionality will be implemented.")
        
    def increase_seasonal_stock(self):
        self.print_info("Seasonal stock increase functionality will be implemented.")
        
    def decrease_seasonal_stock(self):
        self.print_info("Seasonal stock decrease functionality will be implemented.")
        
    def set_seasonal_reorder_points(self):
        self.print_info("Seasonal reorder point setting functionality will be implemented.")
        
    def view_seasonal_trends(self):
        self.print_info("Seasonal trends viewing functionality will be implemented.")
        
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
                'userAgent': 'WarehouseManager-CLI',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")


if __name__ == '__main__':
    auth = AuthManager()
    if auth.login():
        warehouse_mgr = WarehouseManager(auth)
        warehouse_mgr.show_menu()
    else:
        print("❌ Login failed. Exiting.")
        sys.exit(1) 