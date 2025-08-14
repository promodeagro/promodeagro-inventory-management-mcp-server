#!/usr/bin/env python3
# super_admin_standalone.py
"""
Super Admin Standalone Script
Run this script in a separate terminal window for Super Admin operations.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional


class SuperAdminStandalone:
    """Standalone Super Admin with Full System Management"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.categories_table = self.dynamodb.Table('InventoryManagement-Categories')
        self.suppliers_table = self.dynamodb.Table('InventoryManagement-Suppliers')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.settings_table = self.dynamodb.Table('InventoryManagement-Settings')
        
        self.current_user = None
        self.current_role = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"👑 {title}")
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
        self.print_header("SUPER ADMIN - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your credentials:")
        print("💡 Demo credentials: admin / admin123")
        
        username = input("\n👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'SUPER_ADMIN':
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Permissions: {', '.join(user.get('permissions', []))}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            self.print_error("Only Super Admin role can access this system.")
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
        """Create demo super admin user if not exists"""
        try:
            demo_user = {
                'userId': 'admin',
                'role': 'SUPER_ADMIN',
                'name': 'System Administrator',
                'email': 'admin@company.com',
                'phone': '+919876543210',
                'password': 'admin123',
                'permissions': [
                    'SYSTEM_CONFIG', 'USER_MANAGEMENT', 'INTEGRATION_MANAGEMENT',
                    'SYSTEM_MONITORING', 'BACKUP_RECOVERY', 'LICENSE_MANAGEMENT',
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                    'PRODUCT_CREATE', 'PRODUCT_DELETE', 'PRODUCT_UPDATE',
                    'USER_CREATE', 'USER_DELETE', 'USER_UPDATE'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            response = self.users_table.get_item(
                Key={'userId': 'admin', 'role': 'SUPER_ADMIN'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Super Admin user created!")
                self.print_info("Username: admin")
                self.print_info("Password: admin123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Super Admin main menu"""
        while True:
            self.clear_screen()
            self.print_header("SUPER ADMIN DASHBOARD")
            
            if self.current_user:
                print(f"👤 User: {self.current_user.get('name', 'Unknown')}")
                print(f"👑 Role: {self.current_user.get('role', 'Unknown')}")
                print(f"📧 Email: {self.current_user.get('email', 'Unknown')}")
                print(f"📅 Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📋 Available Operations:")
            print("1. 📦 Product Management")
            print("2. 👥 User Management")
            print("3. 🏪 Supplier Management")
            print("4. 🏷️ Category Management")
            print("5. ⚙️ System Configuration")
            print("6. 📊 System Monitoring")
            print("7. 🔐 Security Management")
            print("8. 📈 Analytics & Reports")
            print("9. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-9): ").strip()
            
            if choice == '1':
                self.product_management_menu()
            elif choice == '2':
                self.user_management_menu()
            elif choice == '3':
                self.supplier_management_menu()
            elif choice == '4':
                self.category_management_menu()
            elif choice == '5':
                self.system_configuration_menu()
            elif choice == '6':
                self.system_monitoring_menu()
            elif choice == '7':
                self.security_management_menu()
            elif choice == '8':
                self.analytics_reports_menu()
            elif choice == '9':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Super Admin system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def product_management_menu(self):
        """Product Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PRODUCT MANAGEMENT")
            print("1. 📋 View All Products")
            print("2. ➕ Create New Product")
            print("3. 🔍 View Product Details")
            print("4. ✏️ Update Product Information")
            print("5. 🗑️ Delete Product")
            print("6. 🎨 Manage Product Variants")
            print("7. 📏 Manage Product Units")
            print("8. 💰 Update Product Pricing")
            print("9. 📊 Product Performance Analytics")
            print("10. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-10): ").strip()
            
            if choice == '1':
                self.view_all_products()
            elif choice == '2':
                self.create_new_product()
            elif choice == '3':
                self.view_product_details()
            elif choice == '4':
                self.update_product_information()
            elif choice == '5':
                self.delete_product()
            elif choice == '6':
                self.manage_product_variants()
            elif choice == '7':
                self.manage_product_units()
            elif choice == '8':
                self.update_product_pricing()
            elif choice == '9':
                self.product_performance_analytics()
            elif choice == '10':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def create_new_product(self):
        """Create a new product"""
        self.clear_screen()
        self.print_header("CREATE NEW PRODUCT")
        
        try:
            print("📝 Please enter product details:")
            
            # Get basic product information
            product_id = input("🆔 Product ID: ").strip()
            if not product_id:
                self.print_error("Product ID is required")
                input("Press Enter to continue...")
                return
                
            name = input("📝 Product Name: ").strip()
            if not name:
                self.print_error("Product name is required")
                input("Press Enter to continue...")
                return
                
            description = input("📄 Description: ").strip()
            
            # Get category selection
            category = self.get_category_selection()
            if not category:
                return
                
            # Get brand selection
            brand = self.get_brand_selection()
            if not brand:
                return
            
            # Get pricing information
            cost_price = input("💰 Cost Price: ").strip()
            selling_price = input("💵 Selling Price: ").strip()
            
            # Get inventory settings
            min_stock = input("📦 Min Stock: ").strip()
            reorder_point = input("⚠️ Reorder Point: ").strip()
            
            # Get supplier information
            supplier_id = input("🏪 Supplier ID: ").strip()
            storage_location = input("📍 Storage Location: ").strip()
            special_handling = input("🌡️ Special Handling: ").strip()
            
            # Get product configuration
            has_variants = input("🎨 Has Variants? (y/n): ").strip().lower() == 'y'
            base_unit = input("📏 Base Unit: ").strip()
            default_unit = input("📏 Default Unit: ").strip()
            expiry_tracking = input("⏰ Expiry Tracking? (y/n): ").strip().lower() == 'y'
            batch_required = input("📦 Batch Required? (y/n): ").strip().lower() == 'y'
            
            # Create product item
            product_item = {
                'productId': product_id,
                'category': category,
                'name': name,
                'description': description,
                'brand': brand,
                'baseUnit': base_unit,
                'defaultUnit': default_unit,
                'hasVariants': has_variants,
                'variantTypes': [],
                'costPrice': Decimal(cost_price) if cost_price.replace('.', '').isdigit() else Decimal('0'),
                'sellingPrice': Decimal(selling_price) if selling_price.replace('.', '').isdigit() else Decimal('0'),
                'minStock': int(min_stock) if min_stock.isdigit() else 0,
                'reorderPoint': int(reorder_point) if reorder_point.isdigit() else 0,
                'supplierId': supplier_id,
                'expiryTracking': expiry_tracking,
                'batchRequired': batch_required,
                'storageLocation': storage_location,
                'specialHandling': special_handling,
                'images': [],
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Save to DynamoDB
            self.products_table.put_item(Item=product_item)
            
            # Log audit
            self.log_audit('PRODUCT_CREATE', product_id, f"Created new product: {name}")
            
            self.print_success(f"Product '{name}' created successfully!")
            self.print_info(f"Product ID: {product_id}")
            
        except Exception as e:
            self.print_error(f"Error creating product: {str(e)}")
            
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
        
    def delete_product(self):
        """Delete a product"""
        self.clear_screen()
        self.print_header("DELETE PRODUCT")
        
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product number to delete: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    product_id = selected_product['productId']
                    product_name = selected_product.get('name', 'Unknown')
                    
                    print(f"\n⚠️ WARNING: You are about to delete:")
                    print(f"📦 Product: {product_name}")
                    print(f"🆔 ID: {product_id}")
                    
                    confirm = input("\n❓ Are you sure? (yes/no): ").strip().lower()
                    
                    if confirm == 'yes':
                        # Delete product
                        self.products_table.delete_item(
                            Key={'productId': product_id, 'category': selected_product['category']}
                        )
                        
                        # Log audit
                        self.log_audit('PRODUCT_DELETE', product_id, f"Deleted product: {product_name}")
                        
                        self.print_success(f"Product '{product_name}' deleted successfully!")
                    else:
                        self.print_info("Product deletion cancelled.")
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error deleting product: {str(e)}")
            
        input("Press Enter to continue...")
        
    def user_management_menu(self):
        """User Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("USER MANAGEMENT")
            print("1. 📋 View All Users")
            print("2. ➕ Create New User")
            print("3. ✏️ Update User")
            print("4. 🗑️ Delete User")
            print("5. 🔐 Manage Permissions")
            print("6. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-6): ").strip()
            
            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.create_new_user()
            elif choice == '3':
                self.update_user()
            elif choice == '4':
                self.delete_user()
            elif choice == '5':
                self.manage_permissions()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def create_new_user(self):
        """Create a new user"""
        self.clear_screen()
        self.print_header("CREATE NEW USER")
        
        try:
            print("📝 Please enter user details:")
            
            user_id = input("🆔 User ID: ").strip()
            if not user_id:
                self.print_error("User ID is required")
                input("Press Enter to continue...")
                return
                
            name = input("📝 Full Name: ").strip()
            email = input("📧 Email: ").strip()
            phone = input("📞 Phone: ").strip()
            password = input("🔒 Password: ").strip()
            
            print("\n👑 Available Roles:")
            print("1. SUPER_ADMIN")
            print("2. WAREHOUSE_MANAGER")
            print("3. INVENTORY_STAFF")
            print("4. LOGISTICS_MANAGER")
            print("5. DELIVERY_PERSONNEL")
            print("6. AUDITOR")
            
            role_choice = input("\n🎯 Select role (1-6): ").strip()
            roles = ['SUPER_ADMIN', 'WAREHOUSE_MANAGER', 'INVENTORY_STAFF', 
                    'LOGISTICS_MANAGER', 'DELIVERY_PERSONNEL', 'AUDITOR']
            
            if role_choice.isdigit() and 1 <= int(role_choice) <= 6:
                role = roles[int(role_choice) - 1]
            else:
                self.print_error("Invalid role selection")
                input("Press Enter to continue...")
                return
                
            # Create user item
            user_item = {
                'userId': user_id,
                'role': role,
                'name': name,
                'email': email,
                'phone': phone,
                'password': password,
                'permissions': self.get_default_permissions(role),
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Save to DynamoDB
            self.users_table.put_item(Item=user_item)
            
            # Log audit
            self.log_audit('USER_CREATE', user_id, f"Created new user: {name} ({role})")
            
            self.print_success(f"User '{name}' created successfully!")
            self.print_info(f"User ID: {user_id}")
            self.print_info(f"Role: {role}")
            
        except Exception as e:
            self.print_error(f"Error creating user: {str(e)}")
            
        input("Press Enter to continue...")
        
    def get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for a role"""
        permissions_map = {
            'SUPER_ADMIN': [
                'SYSTEM_CONFIG', 'USER_MANAGEMENT', 'INTEGRATION_MANAGEMENT',
                'SYSTEM_MONITORING', 'BACKUP_RECOVERY', 'LICENSE_MANAGEMENT',
                'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                'PRODUCT_CREATE', 'PRODUCT_DELETE', 'PRODUCT_UPDATE'
            ],
            'WAREHOUSE_MANAGER': [
                'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                'WAREHOUSE_MANAGEMENT', 'QUALITY_CONTROL', 'RECEIVING_MANAGEMENT',
                'EXPIRY_MANAGEMENT', 'SPACE_OPTIMIZATION'
            ],
            'INVENTORY_STAFF': [
                'INVENTORY_READ', 'INVENTORY_WRITE', 'STOCK_MOVEMENT',
                'ORDER_FULFILLMENT', 'INVENTORY_COUNTING'
            ],
            'LOGISTICS_MANAGER': [
                'ROUTE_PLANNING', 'DELIVERY_MANAGEMENT', 'RIDER_MANAGEMENT',
                'RUNSHEET_MANAGEMENT', 'PERFORMANCE_MONITORING'
            ],
            'DELIVERY_PERSONNEL': [
                'RUNSHEET_VIEW', 'ORDER_DELIVERY', 'CASH_COLLECTION',
                'STATUS_UPDATE', 'CUSTOMER_INTERACTION'
            ],
            'AUDITOR': [
                'TRANSACTION_VERIFICATION', 'COMPLIANCE_CHECKING',
                'INVENTORY_VERIFICATION', 'REPORT_GENERATION', 'PROCESS_REVIEW'
            ]
        }
        return permissions_map.get(role, [])
        
    def view_all_users(self):
        """View all users in the system"""
        self.clear_screen()
        self.print_header("ALL USERS")
        
        try:
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            if not users:
                self.print_info("No users found in the system.")
                input("Press Enter to continue...")
                return
                
            print(f"👥 Found {len(users)} users:")
            print("-" * 100)
            print(f"{'User ID':<15} {'Name':<25} {'Role':<20} {'Email':<25} {'Status':<10}")
            print("-" * 100)
            
            for user in users:
                status = "ACTIVE" if user.get('isActive', False) else "INACTIVE"
                print(f"{user.get('userId', 'N/A'):<15} "
                      f"{user.get('name', 'N/A')[:24]:<25} "
                      f"{user.get('role', 'N/A'):<20} "
                      f"{user.get('email', 'N/A')[:24]:<25} "
                      f"{status:<10}")
                      
            print("-" * 100)
            
        except Exception as e:
            self.print_error(f"Error viewing users: {str(e)}")
            
        input("Press Enter to continue...")
        
    def supplier_management_menu(self):
        """Supplier Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("SUPPLIER MANAGEMENT")
            print("1. 👥 View All Suppliers")
            print("2. ➕ Add New Supplier")
            print("3. ✏️ Update Supplier Information")
            print("4. 🗑️ Delete Supplier")
            print("5. 📊 Supplier Performance Analytics")
            print("6. 📋 Supplier Contracts Management")
            print("7. 💰 Payment Terms Management")
            print("8. 📈 Supplier Reports")
            print("9. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-9): ").strip()
            
            if choice == '1':
                self.view_all_suppliers()
            elif choice == '2':
                self.add_new_supplier()
            elif choice == '3':
                self.update_supplier_information()
            elif choice == '4':
                self.delete_supplier()
            elif choice == '5':
                self.supplier_performance_analytics()
            elif choice == '6':
                self.supplier_contracts_management()
            elif choice == '7':
                self.payment_terms_management()
            elif choice == '8':
                self.supplier_reports()
            elif choice == '9':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def category_management_menu(self):
        """Category Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("CATEGORY MANAGEMENT")
            print("1. 🏷️ View All Categories")
            print("2. ➕ Add New Category")
            print("3. ✏️ Update Category Information")
            print("4. 🗑️ Delete Category")
            print("5. 🌳 Manage Category Hierarchy")
            print("6. 📊 Category Analytics")
            print("7. 🔄 Bulk Category Operations")
            print("8. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-8): ").strip()
            
            if choice == '1':
                self.view_all_categories()
            elif choice == '2':
                self.add_new_category()
            elif choice == '3':
                self.update_category_information()
            elif choice == '4':
                self.delete_category()
            elif choice == '5':
                self.manage_category_hierarchy()
            elif choice == '6':
                self.category_analytics()
            elif choice == '7':
                self.bulk_category_operations()
            elif choice == '8':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def system_configuration_menu(self):
        """System Configuration Operations"""
        while True:
            self.clear_screen()
            self.print_header("SYSTEM CONFIGURATION")
            print("1. ⚙️ General System Settings")
            print("2. 🔐 Security Configuration")
            print("3. 📧 Email & Notification Settings")
            print("4. 💰 Financial Settings")
            print("5. 📊 Inventory Settings")
            print("6. 🚚 Delivery Configuration")
            print("7. 🏢 Company Information")
            print("8. 🔄 Backup & Maintenance")
            print("9. 🌐 API Configuration")
            print("10. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-10): ").strip()
            
            if choice == '1':
                self.general_system_settings()
            elif choice == '2':
                self.security_configuration()
            elif choice == '3':
                self.email_notification_settings()
            elif choice == '4':
                self.financial_settings()
            elif choice == '5':
                self.inventory_settings()
            elif choice == '6':
                self.delivery_configuration()
            elif choice == '7':
                self.company_information()
            elif choice == '8':
                self.backup_maintenance()
            elif choice == '9':
                self.api_configuration()
            elif choice == '10':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def system_monitoring_menu(self):
        """System Monitoring Operations"""
        while True:
            self.clear_screen()
            self.print_header("SYSTEM MONITORING")
            print("1. 📊 System Health Dashboard")
            print("2. 💾 Database Performance")
            print("3. 👥 User Activity Monitoring")
            print("4. 📈 Performance Metrics")
            print("5. 🚨 System Alerts & Warnings")
            print("6. 📋 Audit Logs Review")
            print("7. 🔄 System Resource Usage")
            print("8. 📊 Real-time Statistics")
            print("9. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-9): ").strip()
            
            if choice == '1':
                self.system_health_dashboard()
            elif choice == '2':
                self.database_performance()
            elif choice == '3':
                self.user_activity_monitoring()
            elif choice == '4':
                self.performance_metrics()
            elif choice == '5':
                self.system_alerts_warnings()
            elif choice == '6':
                self.audit_logs_review()
            elif choice == '7':
                self.system_resource_usage()
            elif choice == '8':
                self.realtime_statistics()
            elif choice == '9':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def security_management_menu(self):
        """Security Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("SECURITY MANAGEMENT")
            print("1. 🔐 Authentication Settings")
            print("2. 🛡️ Authorization & Permissions")
            print("3. 🔒 Password Policies")
            print("4. 🚨 Security Alerts")
            print("5. 📊 Security Audit")
            print("6. 🔑 API Key Management")
            print("7. 🌐 IP Access Control")
            print("8. 📋 Session Management")
            print("9. 🔄 Security Backup")
            print("10. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-10): ").strip()
            
            if choice == '1':
                self.authentication_settings()
            elif choice == '2':
                self.authorization_permissions()
            elif choice == '3':
                self.password_policies()
            elif choice == '4':
                self.security_alerts()
            elif choice == '5':
                self.security_audit()
            elif choice == '6':
                self.api_key_management()
            elif choice == '7':
                self.ip_access_control()
            elif choice == '8':
                self.session_management()
            elif choice == '9':
                self.security_backup()
            elif choice == '10':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def analytics_reports_menu(self):
        """Analytics and Reports Operations"""
        while True:
            self.clear_screen()
            self.print_header("ANALYTICS & REPORTS")
            print("1. 📊 Business Intelligence Dashboard")
            print("2. 📈 Sales Analytics")
            print("3. 📦 Inventory Analytics")
            print("4. 👥 User Analytics")
            print("5. 🚚 Delivery Analytics")
            print("6. 💰 Financial Reports")
            print("7. 📋 Operational Reports")
            print("8. 🎯 Custom Reports")
            print("9. 📤 Export Reports")
            print("10. 📅 Scheduled Reports")
            print("11. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-11): ").strip()
            
            if choice == '1':
                self.business_intelligence_dashboard()
            elif choice == '2':
                self.sales_analytics()
            elif choice == '3':
                self.inventory_analytics()
            elif choice == '4':
                self.user_analytics()
            elif choice == '5':
                self.delivery_analytics()
            elif choice == '6':
                self.financial_reports()
            elif choice == '7':
                self.operational_reports()
            elif choice == '8':
                self.custom_reports()
            elif choice == '9':
                self.export_reports()
            elif choice == '10':
                self.scheduled_reports()
            elif choice == '11':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def view_product_details(self):
        """View detailed product information"""
        self.clear_screen()
        self.print_header("PRODUCT DETAILS")
        
        try:
            # Get all products first
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product number to view details: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    self.display_product_details(selected_product)
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error viewing product details: {str(e)}")
            
        input("Press Enter to continue...")
        
    def display_product_details(self, product: Dict[str, Any]):
        """Display comprehensive product details"""
        self.clear_screen()
        self.print_header(f"PRODUCT DETAILS - {product.get('name', 'Unknown')}")
        
        print("📋 BASIC INFORMATION")
        print("-" * 60)
        print(f"🆔 Product ID: {product.get('productId', 'N/A')}")
        print(f"📝 Name: {product.get('name', 'N/A')}")
        print(f"📄 Description: {product.get('description', 'N/A')}")
        print(f"🏷️ Category: {product.get('category', 'N/A')}")
        print(f"🏢 Brand: {product.get('brand', 'N/A')}")
        
        print("\n💰 PRICING INFORMATION")
        print("-" * 60)
        print(f"💲 Cost Price: ₹{product.get('costPrice', 0)}")
        print(f"💵 Selling Price: ₹{product.get('sellingPrice', 0)}")
        
        # Calculate margin if both prices exist
        cost_price = float(product.get('costPrice', 0))
        selling_price = float(product.get('sellingPrice', 0))
        if cost_price > 0 and selling_price > 0:
            margin = ((selling_price - cost_price) / selling_price) * 100
            print(f"📊 Profit Margin: {margin:.2f}%")
        
        print("\n📦 INVENTORY INFORMATION")
        print("-" * 60)
        print(f"📏 Base Unit: {product.get('baseUnit', 'N/A')}")
        print(f"📏 Default Unit: {product.get('defaultUnit', 'N/A')}")
        print(f"📦 Min Stock: {product.get('minStock', 0)}")
        print(f"⚠️ Reorder Point: {product.get('reorderPoint', 0)}")
        print(f"🏪 Supplier ID: {product.get('supplierId', 'N/A')}")
        
        print("\n🎨 PRODUCT CONFIGURATION")
        print("-" * 60)
        print(f"🎨 Has Variants: {'Yes' if product.get('hasVariants', False) else 'No'}")
        if product.get('variantTypes'):
            print(f"🔧 Variant Types: {', '.join(product.get('variantTypes', []))}")
        print(f"⏰ Expiry Tracking: {'Yes' if product.get('expiryTracking', False) else 'No'}")
        print(f"📦 Batch Required: {'Yes' if product.get('batchRequired', False) else 'No'}")
        
        print("\n📍 STORAGE INFORMATION")
        print("-" * 60)
        print(f"📍 Storage Location: {product.get('storageLocation', 'N/A')}")
        print(f"🌡️ Special Handling: {product.get('specialHandling', 'N/A')}")
        
        print("\n🖼️ MEDIA INFORMATION")
        print("-" * 60)
        images = product.get('images', [])
        if images:
            print(f"🖼️ Images: {len(images)} image(s)")
            for i, image in enumerate(images, 1):
                print(f"   {i}. {image}")
        else:
            print("🖼️ Images: No images available")
        
        print("\n📅 AUDIT INFORMATION")
        print("-" * 60)
        created_at = product.get('createdAt', 'N/A')
        updated_at = product.get('updatedAt', 'N/A')
        if created_at != 'N/A':
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                print(f"📅 Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"📅 Created: {created_at}")
        if updated_at != 'N/A':
            try:
                updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                print(f"🔄 Updated: {updated_date.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"🔄 Updated: {updated_at}")
                
        # Try to get current stock level
        try:
            stock_response = self.dynamodb.Table('InventoryManagement-StockLevels').query(
                KeyConditionExpression='productId = :pid',
                ExpressionAttributeValues={':pid': product.get('productId')}
            )
            if stock_response.get('Items'):
                print(f"\n📊 CURRENT STOCK LEVELS")
                print("-" * 60)
                for stock in stock_response['Items']:
                    location = stock.get('location', 'Unknown')
                    current_stock = stock.get('currentStock', 0)
                    print(f"📍 {location}: {current_stock} units")
        except Exception as e:
            pass  # Stock level info is optional
            
    def get_category_selection(self) -> Optional[str]:
        """Get category selection from available categories"""
        try:
            # Get existing categories
            response = self.categories_table.scan()
            categories = response.get('Items', [])
            
            if categories:
                print("\n🏷️ Available Categories:")
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat.get('categoryId', 'N/A')} - {cat.get('name', 'N/A')}")
                    
                print(f"{len(categories) + 1}. Create New Category")
                
                choice = input(f"\n🎯 Select category (1-{len(categories) + 1}): ").strip()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        return categories[choice_num - 1].get('categoryId', '')
                    elif choice_num == len(categories) + 1:
                        return self.create_new_category()
                    else:
                        self.print_error("Invalid category selection")
                        return None
                except ValueError:
                    self.print_error("Invalid category number")
                    return None
            else:
                self.print_info("No categories found. Creating new category...")
                return self.create_new_category()
                
        except Exception as e:
            self.print_error(f"Error getting categories: {str(e)}")
            # Fallback to manual entry
            return input("🏷️ Category: ").strip()
            
    def get_brand_selection(self) -> Optional[str]:
        """Get brand selection from available brands"""
        try:
            # Get existing brands from products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            # Extract unique brands
            brands = list(set([p.get('brand', '') for p in products if p.get('brand', '').strip()]))
            brands.sort()
            
            if brands:
                print("\n🏢 Available Brands:")
                for i, brand in enumerate(brands, 1):
                    print(f"{i}. {brand}")
                    
                print(f"{len(brands) + 1}. Enter New Brand")
                
                choice = input(f"\n🎯 Select brand (1-{len(brands) + 1}): ").strip()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(brands):
                        return brands[choice_num - 1]
                    elif choice_num == len(brands) + 1:
                        new_brand = input("🏢 Enter new brand name: ").strip()
                        return new_brand if new_brand else None
                    else:
                        self.print_error("Invalid brand selection")
                        return None
                except ValueError:
                    self.print_error("Invalid brand number")
                    return None
            else:
                return input("🏢 Brand: ").strip()
                
        except Exception as e:
            self.print_error(f"Error getting brands: {str(e)}")
            # Fallback to manual entry
            return input("🏢 Brand: ").strip()
            
    def create_new_category(self) -> Optional[str]:
        """Create a new category"""
        try:
            category_id = input("🆔 Category ID: ").strip()
            if not category_id:
                self.print_error("Category ID is required")
                return None
                
            category_name = input("📝 Category Name: ").strip()
            if not category_name:
                self.print_error("Category name is required")
                return None
                
            description = input("📄 Description (optional): ").strip()
            parent_category = input("👆 Parent Category (optional): ").strip()
            
            category_item = {
                'categoryId': category_id,
                'status': 'ACTIVE',
                'name': category_name,
                'description': description,
                'parentCategory': parent_category if parent_category else None,
                'level': 1 if not parent_category else 2,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.categories_table.put_item(Item=category_item)
            self.print_success(f"Category '{category_name}' created successfully!")
            
            # Log audit
            self.log_audit('CATEGORY_CREATE', category_id, f"Created new category: {category_name}")
            
            return category_id
            
        except Exception as e:
            self.print_error(f"Error creating category: {str(e)}")
            return None
        
    def update_product_information(self):
        """Update product information"""
        self.clear_screen()
        self.print_header("UPDATE PRODUCT INFORMATION")
        
        try:
            # Get all products first
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')})")
                
            product_choice = input("\n🎯 Select product number to update: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    self.perform_product_update(selected_product)
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error updating product: {str(e)}")
            
        input("Press Enter to continue...")
        
    def perform_product_update(self, product: Dict[str, Any]):
        """Perform product update with field selection"""
        self.clear_screen()
        self.print_header(f"UPDATE PRODUCT - {product.get('name', 'Unknown')}")
        
        print("📝 Select field to update:")
        print("1. Product Name")
        print("2. Description")
        print("3. Category")
        print("4. Brand")
        print("5. Cost Price")
        print("6. Selling Price")
        print("7. Min Stock")
        print("8. Reorder Point")
        print("9. Storage Location")
        print("10. Special Handling")
        print("11. Update Multiple Fields")
        print("0. Cancel")
        
        choice = input("\n🎯 Select field (0-11): ").strip()
        
        try:
            if choice == '1':
                self.update_product_field(product, 'name', 'Product Name')
            elif choice == '2':
                self.update_product_field(product, 'description', 'Description')
            elif choice == '3':
                new_category = self.get_category_selection()
                if new_category:
                    self.update_product_field(product, 'category', 'Category', new_category)
            elif choice == '4':
                new_brand = self.get_brand_selection()
                if new_brand:
                    self.update_product_field(product, 'brand', 'Brand', new_brand)
            elif choice == '5':
                self.update_product_field(product, 'costPrice', 'Cost Price', convert_to_decimal=True)
            elif choice == '6':
                self.update_product_field(product, 'sellingPrice', 'Selling Price', convert_to_decimal=True)
            elif choice == '7':
                self.update_product_field(product, 'minStock', 'Min Stock', convert_to_int=True)
            elif choice == '8':
                self.update_product_field(product, 'reorderPoint', 'Reorder Point', convert_to_int=True)
            elif choice == '9':
                self.update_product_field(product, 'storageLocation', 'Storage Location')
            elif choice == '10':
                self.update_product_field(product, 'specialHandling', 'Special Handling')
            elif choice == '11':
                self.update_multiple_product_fields(product)
            elif choice == '0':
                self.print_info("Update cancelled.")
                return
            else:
                self.print_error("Invalid choice.")
                
        except Exception as e:
            self.print_error(f"Error updating product field: {str(e)}")
            
    def update_product_field(self, product: Dict[str, Any], field_name: str, field_display: str, 
                           new_value: str = None, convert_to_decimal: bool = False, convert_to_int: bool = False):
        """Update a specific product field"""
        try:
            if new_value is None:
                current_value = product.get(field_name, 'N/A')
                print(f"\nCurrent {field_display}: {current_value}")
                new_value = input(f"New {field_display}: ").strip()
                
            if not new_value:
                self.print_error(f"{field_display} cannot be empty")
                return
                
            # Convert value if needed
            if convert_to_decimal:
                try:
                    new_value = Decimal(new_value)
                except ValueError:
                    self.print_error("Invalid number format")
                    return
            elif convert_to_int:
                try:
                    new_value = int(new_value)
                except ValueError:
                    self.print_error("Invalid number format")
                    return
                    
            # Update the product
            update_expression = f"SET {field_name} = :new_value, updatedAt = :updated_at"
            expression_values = {
                ':new_value': new_value,
                ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Log audit
            self.log_audit('PRODUCT_UPDATE', product['productId'], 
                          f"Updated {field_display}: {product.get(field_name, 'N/A')} -> {new_value}")
            
            self.print_success(f"{field_display} updated successfully!")
            
        except Exception as e:
            self.print_error(f"Error updating {field_display}: {str(e)}")
            
    def update_multiple_product_fields(self, product: Dict[str, Any]):
        """Update multiple product fields at once"""
        self.clear_screen()
        self.print_header(f"UPDATE MULTIPLE FIELDS - {product.get('name', 'Unknown')}")
        
        updates = {}
        
        # Collect all field updates
        print("📝 Enter new values (press Enter to skip a field):")
        
        name = input(f"Product Name [{product.get('name', 'N/A')}]: ").strip()
        if name:
            updates['name'] = name
            
        description = input(f"Description [{product.get('description', 'N/A')}]: ").strip()
        if description:
            updates['description'] = description
            
        cost_price = input(f"Cost Price [{product.get('costPrice', 0)}]: ").strip()
        if cost_price:
            try:
                updates['costPrice'] = Decimal(cost_price)
            except ValueError:
                self.print_warning("Invalid cost price format, skipping")
                
        selling_price = input(f"Selling Price [{product.get('sellingPrice', 0)}]: ").strip()
        if selling_price:
            try:
                updates['sellingPrice'] = Decimal(selling_price)
            except ValueError:
                self.print_warning("Invalid selling price format, skipping")
                
        min_stock = input(f"Min Stock [{product.get('minStock', 0)}]: ").strip()
        if min_stock:
            try:
                updates['minStock'] = int(min_stock)
            except ValueError:
                self.print_warning("Invalid min stock format, skipping")
                
        reorder_point = input(f"Reorder Point [{product.get('reorderPoint', 0)}]: ").strip()
        if reorder_point:
            try:
                updates['reorderPoint'] = int(reorder_point)
            except ValueError:
                self.print_warning("Invalid reorder point format, skipping")
                
        storage_location = input(f"Storage Location [{product.get('storageLocation', 'N/A')}]: ").strip()
        if storage_location:
            updates['storageLocation'] = storage_location
            
        special_handling = input(f"Special Handling [{product.get('specialHandling', 'N/A')}]: ").strip()
        if special_handling:
            updates['specialHandling'] = special_handling
            
        if not updates:
            self.print_info("No fields to update.")
            return
            
        # Confirm updates
        print(f"\n📋 Fields to update:")
        for field, value in updates.items():
            print(f"  • {field}: {value}")
            
        confirm = input("\n❓ Proceed with updates? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            try:
                # Build update expression
                update_expression = "SET "
                expression_values = {}
                
                for i, (field, value) in enumerate(updates.items()):
                    if i > 0:
                        update_expression += ", "
                    update_expression += f"{field} = :val{i}"
                    expression_values[f':val{i}'] = value
                    
                # Add updated timestamp
                update_expression += ", updatedAt = :updated_at"
                expression_values[':updated_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                
                self.products_table.update_item(
                    Key={
                        'productId': product['productId'],
                        'category': product['category']
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values
                )
                
                # Log audit
                update_details = ', '.join([f"{k}: {v}" for k, v in updates.items()])
                self.log_audit('PRODUCT_UPDATE', product['productId'], 
                              f"Updated multiple fields - {update_details}")
                
                self.print_success("Product updated successfully!")
                
            except Exception as e:
                self.print_error(f"Error updating product: {str(e)}")
        else:
            self.print_info("Update cancelled.")
        
    def manage_product_variants(self):
        """Manage product variants"""
        self.clear_screen()
        self.print_header("MANAGE PRODUCT VARIANTS")
        
        try:
            # Get products with variants
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                has_variants = "✅" if product.get('hasVariants', False) else "❌"
                print(f"{i}. {product.get('name', 'N/A')} (ID: {product.get('productId', 'N/A')}) - Variants: {has_variants}")
                
            product_choice = input("\n🎯 Select product number to manage variants: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    self.manage_product_variant_operations(selected_product)
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error managing variants: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_product_variant_operations(self, product: Dict[str, Any]):
        """Manage variant operations for a specific product"""
        while True:
            self.clear_screen()
            self.print_header(f"MANAGE VARIANTS - {product.get('name', 'Unknown')}")
            
            print(f"📦 Product: {product.get('name', 'N/A')}")
            print(f"🎨 Has Variants: {'Yes' if product.get('hasVariants', False) else 'No'}")
            
            variant_types = product.get('variantTypes', [])
            if variant_types:
                print(f"🔧 Current Variant Types: {', '.join(variant_types)}")
            else:
                print("🔧 Current Variant Types: None")
            
            print("\n📋 Variant Operations:")
            print("1. Enable/Disable Variants")
            print("2. Add Variant Type")
            print("3. Remove Variant Type")
            print("4. View Existing Variants")
            print("5. Create Product Variant")
            print("0. Back to Product Management")
            
            choice = input("\n🎯 Select operation (0-5): ").strip()
            
            if choice == '1':
                self.toggle_product_variants(product)
                break
            elif choice == '2':
                self.add_variant_type(product)
                break
            elif choice == '3':
                self.remove_variant_type(product)
                break
            elif choice == '4':
                self.view_product_variants(product)
            elif choice == '5':
                self.create_product_variant(product)
                break
            elif choice == '0':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def toggle_product_variants(self, product: Dict[str, Any]):
        """Enable or disable variants for a product"""
        try:
            current_status = product.get('hasVariants', False)
            new_status = not current_status
            
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET hasVariants = :status, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':status': new_status,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            status_text = "enabled" if new_status else "disabled"
            self.print_success(f"Product variants {status_text} successfully!")
            
            # Log audit
            self.log_audit('PRODUCT_VARIANT_TOGGLE', product['productId'], 
                          f"Variants {status_text} for product: {product.get('name', 'Unknown')}")
            
        except Exception as e:
            self.print_error(f"Error toggling variants: {str(e)}")
            
    def add_variant_type(self, product: Dict[str, Any]):
        """Add a new variant type to a product"""
        try:
            print("\n🎨 Available Variant Types:")
            print("1. Size (Small, Medium, Large, XL, etc.)")
            print("2. Color (Red, Blue, Green, etc.)")
            print("3. Weight (1kg, 2kg, 5kg, etc.)")
            print("4. Volume (100ml, 250ml, 500ml, etc.)")
            print("5. Custom Type")
            
            type_choice = input("\n🎯 Select variant type (1-5): ").strip()
            
            variant_type = None
            if type_choice == '1':
                variant_type = 'Size'
            elif type_choice == '2':
                variant_type = 'Color'
            elif type_choice == '3':
                variant_type = 'Weight'
            elif type_choice == '4':
                variant_type = 'Volume'
            elif type_choice == '5':
                variant_type = input("Enter custom variant type name: ").strip()
            else:
                self.print_error("Invalid variant type selection")
                return
                
            if not variant_type:
                self.print_error("Variant type name cannot be empty")
                return
                
            # Get current variant types
            current_types = product.get('variantTypes', [])
            
            if variant_type in current_types:
                self.print_error(f"Variant type '{variant_type}' already exists")
                return
                
            # Add new variant type
            current_types.append(variant_type)
            
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET variantTypes = :types, hasVariants = :has_variants, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':types': current_types,
                    ':has_variants': True,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            self.print_success(f"Variant type '{variant_type}' added successfully!")
            
            # Log audit
            self.log_audit('VARIANT_TYPE_ADD', product['productId'], 
                          f"Added variant type '{variant_type}' to product: {product.get('name', 'Unknown')}")
            
        except Exception as e:
            self.print_error(f"Error adding variant type: {str(e)}")
            
    def remove_variant_type(self, product: Dict[str, Any]):
        """Remove a variant type from a product"""
        try:
            current_types = product.get('variantTypes', [])
            
            if not current_types:
                self.print_info("No variant types to remove")
                return
                
            print("\n🔧 Current Variant Types:")
            for i, variant_type in enumerate(current_types, 1):
                print(f"{i}. {variant_type}")
                
            choice = input(f"\n🎯 Select variant type to remove (1-{len(current_types)}): ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(current_types):
                    removed_type = current_types.pop(choice_num - 1)
                    
                    self.products_table.update_item(
                        Key={
                            'productId': product['productId'],
                            'category': product['category']
                        },
                        UpdateExpression="SET variantTypes = :types, updatedAt = :updated_at",
                        ExpressionAttributeValues={
                            ':types': current_types,
                            ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    self.print_success(f"Variant type '{removed_type}' removed successfully!")
                    
                    # Log audit
                    self.log_audit('VARIANT_TYPE_REMOVE', product['productId'], 
                                  f"Removed variant type '{removed_type}' from product: {product.get('name', 'Unknown')}")
                else:
                    self.print_error("Invalid variant type selection")
            except ValueError:
                self.print_error("Invalid variant type number")
                
        except Exception as e:
            self.print_error(f"Error removing variant type: {str(e)}")
            
    def view_product_variants(self, product: Dict[str, Any]):
        """View existing variants for a product"""
        try:
            # Get product variants (this would query a separate variants table in a real system)
            self.print_info("Product variant viewing functionality")
            print(f"\n📦 Product: {product.get('name', 'N/A')}")
            print(f"🎨 Has Variants: {'Yes' if product.get('hasVariants', False) else 'No'}")
            
            variant_types = product.get('variantTypes', [])
            if variant_types:
                print(f"🔧 Variant Types: {', '.join(variant_types)}")
                print("\n💡 Note: Individual variant records would be stored in a separate ProductVariants table")
                print("💡 Each variant would have its own SKU, pricing, and inventory tracking")
            else:
                print("🔧 No variant types configured")
                
        except Exception as e:
            self.print_error(f"Error viewing variants: {str(e)}")
            
        input("Press Enter to continue...")
        
    def create_product_variant(self, product: Dict[str, Any]):
        """Create a new product variant"""
        try:
            if not product.get('hasVariants', False):
                self.print_error("Product does not have variants enabled")
                return
                
            variant_types = product.get('variantTypes', [])
            if not variant_types:
                self.print_error("No variant types configured for this product")
                return
                
            self.print_info("Creating product variant (conceptual implementation)")
            print(f"\n📦 Base Product: {product.get('name', 'N/A')}")
            print(f"🔧 Available Variant Types: {', '.join(variant_types)}")
            
            variant_sku = input("\n🆔 Variant SKU: ").strip()
            if not variant_sku:
                self.print_error("Variant SKU is required")
                return
                
            variant_name = input("📝 Variant Name: ").strip()
            if not variant_name:
                self.print_error("Variant name is required")
                return
                
            # Collect variant attributes
            variant_attributes = {}
            for variant_type in variant_types:
                value = input(f"🎨 {variant_type}: ").strip()
                if value:
                    variant_attributes[variant_type] = value
                    
            variant_price = input("💰 Variant Price (optional): ").strip()
            
            print(f"\n📋 Variant Summary:")
            print(f"🆔 SKU: {variant_sku}")
            print(f"📝 Name: {variant_name}")
            print(f"🎨 Attributes: {variant_attributes}")
            if variant_price:
                print(f"💰 Price: ₹{variant_price}")
                
            print("\n💡 Note: In a production system, this would create:")
            print("  • A record in ProductVariants table")
            print("  • Separate inventory tracking")
            print("  • Individual pricing rules")
            print("  • Unique barcode/SKU mapping")
            
            self.print_success("Variant creation process completed (conceptual)")
            
        except Exception as e:
            self.print_error(f"Error creating variant: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_product_units(self):
        """Manage product units"""
        self.clear_screen()
        self.print_header("MANAGE PRODUCT UNITS")
        
        try:
            # Get all products first
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                base_unit = product.get('baseUnit', 'N/A')
                default_unit = product.get('defaultUnit', 'N/A')
                print(f"{i}. {product.get('name', 'N/A')} - Base: {base_unit}, Default: {default_unit}")
                
            product_choice = input("\n🎯 Select product number to manage units: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    self.manage_product_unit_operations(selected_product)
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error managing units: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_product_unit_operations(self, product: Dict[str, Any]):
        """Manage unit operations for a specific product"""
        while True:
            self.clear_screen()
            self.print_header(f"MANAGE UNITS - {product.get('name', 'Unknown')}")
            
            print(f"📦 Product: {product.get('name', 'N/A')}")
            print(f"📏 Base Unit: {product.get('baseUnit', 'N/A')}")
            print(f"📏 Default Unit: {product.get('defaultUnit', 'N/A')}")
            
            print("\n📋 Unit Operations:")
            print("1. Update Base Unit")
            print("2. Update Default Unit")
            print("3. View Standard Units")
            print("4. Unit Conversion Info")
            print("0. Back to Product Management")
            
            choice = input("\n🎯 Select operation (0-4): ").strip()
            
            if choice == '1':
                self.update_base_unit(product)
                break
            elif choice == '2':
                self.update_default_unit(product)
                break
            elif choice == '3':
                self.view_standard_units()
            elif choice == '4':
                self.show_unit_conversion_info()
            elif choice == '0':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def update_base_unit(self, product: Dict[str, Any]):
        """Update product base unit"""
        try:
            print(f"\nCurrent Base Unit: {product.get('baseUnit', 'N/A')}")
            
            print("\n📏 Standard Units:")
            standard_units = ["kg", "g", "liter", "ml", "piece", "box", "pack", "meter", "cm"]
            for i, unit in enumerate(standard_units, 1):
                print(f"{i}. {unit}")
            print(f"{len(standard_units) + 1}. Custom Unit")
            
            choice = input(f"\n🎯 Select unit (1-{len(standard_units) + 1}): ").strip()
            
            new_unit = None
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(standard_units):
                    new_unit = standard_units[choice_num - 1]
                elif choice_num == len(standard_units) + 1:
                    new_unit = input("Enter custom unit: ").strip()
                else:
                    self.print_error("Invalid unit selection")
                    return
            except ValueError:
                self.print_error("Invalid unit number")
                return
                
            if not new_unit:
                self.print_error("Unit cannot be empty")
                return
                
            # Update the product
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET baseUnit = :unit, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':unit': new_unit,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            self.print_success(f"Base unit updated to '{new_unit}' successfully!")
            
            # Log audit
            self.log_audit('PRODUCT_UNIT_UPDATE', product['productId'], 
                          f"Updated base unit from '{product.get('baseUnit', 'N/A')}' to '{new_unit}'")
            
        except Exception as e:
            self.print_error(f"Error updating base unit: {str(e)}")
            
    def update_default_unit(self, product: Dict[str, Any]):
        """Update product default unit"""
        try:
            print(f"\nCurrent Default Unit: {product.get('defaultUnit', 'N/A')}")
            
            print("\n📏 Standard Units:")
            standard_units = ["kg", "g", "liter", "ml", "piece", "box", "pack", "meter", "cm"]
            for i, unit in enumerate(standard_units, 1):
                print(f"{i}. {unit}")
            print(f"{len(standard_units) + 1}. Custom Unit")
            
            choice = input(f"\n🎯 Select unit (1-{len(standard_units) + 1}): ").strip()
            
            new_unit = None
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(standard_units):
                    new_unit = standard_units[choice_num - 1]
                elif choice_num == len(standard_units) + 1:
                    new_unit = input("Enter custom unit: ").strip()
                else:
                    self.print_error("Invalid unit selection")
                    return
            except ValueError:
                self.print_error("Invalid unit number")
                return
                
            if not new_unit:
                self.print_error("Unit cannot be empty")
                return
                
            # Update the product
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET defaultUnit = :unit, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':unit': new_unit,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            self.print_success(f"Default unit updated to '{new_unit}' successfully!")
            
            # Log audit
            self.log_audit('PRODUCT_UNIT_UPDATE', product['productId'], 
                          f"Updated default unit from '{product.get('defaultUnit', 'N/A')}' to '{new_unit}'")
            
        except Exception as e:
            self.print_error(f"Error updating default unit: {str(e)}")
            
    def view_standard_units(self):
        """View standard unit categories"""
        self.clear_screen()
        self.print_header("STANDARD UNITS")
        
        print("📏 WEIGHT UNITS:")
        print("  • kg (kilogram)")
        print("  • g (gram)")
        print("  • mg (milligram)")
        print("  • ton (metric ton)")
        
        print("\n🧴 VOLUME UNITS:")
        print("  • liter (liter)")
        print("  • ml (milliliter)")
        print("  • gallon")
        print("  • cup")
        
        print("\n📦 COUNT UNITS:")
        print("  • piece")
        print("  • box")
        print("  • pack")
        print("  • dozen")
        
        print("\n📐 LENGTH UNITS:")
        print("  • meter")
        print("  • cm (centimeter)")
        print("  • mm (millimeter)")
        print("  • inch")
        print("  • feet")
        
        print("\n💡 Unit Management Best Practices:")
        print("  • Base Unit: Primary measurement unit for the product")
        print("  • Default Unit: Most commonly used unit for transactions")
        print("  • Use consistent units within product categories")
        print("  • Consider customer preferences and industry standards")
        
        input("Press Enter to continue...")
        
    def show_unit_conversion_info(self):
        """Show unit conversion information"""
        self.clear_screen()
        self.print_header("UNIT CONVERSION INFORMATION")
        
        print("🔄 Common Weight Conversions:")
        print("  • 1 kg = 1000 g")
        print("  • 1 g = 1000 mg")
        print("  • 1 ton = 1000 kg")
        
        print("\n🔄 Common Volume Conversions:")
        print("  • 1 liter = 1000 ml")
        print("  • 1 gallon = 3.785 liters")
        print("  • 1 cup = 250 ml")
        
        print("\n🔄 Common Length Conversions:")
        print("  • 1 meter = 100 cm")
        print("  • 1 cm = 10 mm")
        print("  • 1 inch = 2.54 cm")
        print("  • 1 feet = 30.48 cm")
        
        print("\n💡 Note: In a production system:")
        print("  • Unit conversions would be stored in UnitConversions table")
        print("  • Automatic conversion between compatible units")
        print("  • Real-time price calculations based on unit conversions")
        print("  • Inventory tracking across multiple units")
        
        input("Press Enter to continue...")
        
    def update_product_pricing(self):
        """Update product pricing"""
        self.clear_screen()
        self.print_header("UPDATE PRODUCT PRICING")
        
        try:
            # Get all products first
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found in the system.")
                input("Press Enter to continue...")
                return
                
            print("📦 Available Products:")
            for i, product in enumerate(products, 1):
                cost_price = product.get('costPrice', 0)
                selling_price = product.get('sellingPrice', 0)
                print(f"{i}. {product.get('name', 'N/A')} - Cost: ₹{cost_price}, Selling: ₹{selling_price}")
                
            product_choice = input("\n🎯 Select product number to update pricing: ").strip()
            
            try:
                product_index = int(product_choice) - 1
                if 0 <= product_index < len(products):
                    selected_product = products[product_index]
                    self.manage_product_pricing_operations(selected_product)
                else:
                    self.print_error("Invalid product selection.")
            except ValueError:
                self.print_error("Invalid product number.")
                
        except Exception as e:
            self.print_error(f"Error updating pricing: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_product_pricing_operations(self, product: Dict[str, Any]):
        """Manage pricing operations for a specific product"""
        while True:
            self.clear_screen()
            self.print_header(f"MANAGE PRICING - {product.get('name', 'Unknown')}")
            
            cost_price = float(product.get('costPrice', 0))
            selling_price = float(product.get('sellingPrice', 0))
            
            print(f"📦 Product: {product.get('name', 'N/A')}")
            print(f"💲 Cost Price: ₹{cost_price}")
            print(f"💵 Selling Price: ₹{selling_price}")
            
            if cost_price > 0 and selling_price > 0:
                margin = ((selling_price - cost_price) / selling_price) * 100
                print(f"📊 Profit Margin: {margin:.2f}%")
                markup = ((selling_price - cost_price) / cost_price) * 100
                print(f"📈 Markup: {markup:.2f}%")
            
            print("\n📋 Pricing Operations:")
            print("1. Update Cost Price")
            print("2. Update Selling Price")
            print("3. Bulk Price Update")
            print("4. Calculate Margin/Markup")
            print("5. Price History")
            print("6. Competitive Pricing")
            print("0. Back to Product Management")
            
            choice = input("\n🎯 Select operation (0-6): ").strip()
            
            if choice == '1':
                self.update_cost_price(product)
                break
            elif choice == '2':
                self.update_selling_price(product)
                break
            elif choice == '3':
                self.bulk_price_update(product)
                break
            elif choice == '4':
                self.calculate_pricing_metrics(product)
            elif choice == '5':
                self.show_price_history(product)
            elif choice == '6':
                self.show_competitive_pricing(product)
            elif choice == '0':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def update_cost_price(self, product: Dict[str, Any]):
        """Update product cost price"""
        try:
            current_cost = product.get('costPrice', 0)
            print(f"\nCurrent Cost Price: ₹{current_cost}")
            
            new_cost = input("New Cost Price: ₹").strip()
            if not new_cost:
                self.print_error("Cost price cannot be empty")
                return
                
            try:
                new_cost_decimal = Decimal(new_cost)
                if new_cost_decimal < 0:
                    self.print_error("Cost price cannot be negative")
                    return
            except ValueError:
                self.print_error("Invalid price format")
                return
                
            # Update the product
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET costPrice = :price, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':price': new_cost_decimal,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            self.print_success(f"Cost price updated to ₹{new_cost_decimal} successfully!")
            
            # Log audit
            self.log_audit('PRICE_UPDATE', product['productId'], 
                          f"Updated cost price from ₹{current_cost} to ₹{new_cost_decimal}")
            
        except Exception as e:
            self.print_error(f"Error updating cost price: {str(e)}")
            
    def update_selling_price(self, product: Dict[str, Any]):
        """Update product selling price"""
        try:
            current_price = product.get('sellingPrice', 0)
            print(f"\nCurrent Selling Price: ₹{current_price}")
            
            new_price = input("New Selling Price: ₹").strip()
            if not new_price:
                self.print_error("Selling price cannot be empty")
                return
                
            try:
                new_price_decimal = Decimal(new_price)
                if new_price_decimal < 0:
                    self.print_error("Selling price cannot be negative")
                    return
            except ValueError:
                self.print_error("Invalid price format")
                return
                
            # Update the product
            self.products_table.update_item(
                Key={
                    'productId': product['productId'],
                    'category': product['category']
                },
                UpdateExpression="SET sellingPrice = :price, updatedAt = :updated_at",
                ExpressionAttributeValues={
                    ':price': new_price_decimal,
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            self.print_success(f"Selling price updated to ₹{new_price_decimal} successfully!")
            
            # Log audit
            self.log_audit('PRICE_UPDATE', product['productId'], 
                          f"Updated selling price from ₹{current_price} to ₹{new_price_decimal}")
            
        except Exception as e:
            self.print_error(f"Error updating selling price: {str(e)}")
            
    def bulk_price_update(self, product: Dict[str, Any]):
        """Bulk update both cost and selling price"""
        try:
            current_cost = product.get('costPrice', 0)
            current_selling = product.get('sellingPrice', 0)
            
            print(f"\nCurrent Prices:")
            print(f"💲 Cost Price: ₹{current_cost}")
            print(f"💵 Selling Price: ₹{current_selling}")
            
            print("\n📝 Enter new prices (press Enter to skip):")
            
            new_cost = input(f"New Cost Price [₹{current_cost}]: ").strip()
            new_selling = input(f"New Selling Price [₹{current_selling}]: ").strip()
            
            updates = {}
            
            if new_cost:
                try:
                    cost_decimal = Decimal(new_cost)
                    if cost_decimal >= 0:
                        updates['costPrice'] = cost_decimal
                    else:
                        self.print_warning("Invalid cost price, skipping")
                except ValueError:
                    self.print_warning("Invalid cost price format, skipping")
                    
            if new_selling:
                try:
                    selling_decimal = Decimal(new_selling)
                    if selling_decimal >= 0:
                        updates['sellingPrice'] = selling_decimal
                    else:
                        self.print_warning("Invalid selling price, skipping")
                except ValueError:
                    self.print_warning("Invalid selling price format, skipping")
                    
            if not updates:
                self.print_info("No price updates to apply.")
                return
                
            # Show pricing analysis
            if 'costPrice' in updates and 'sellingPrice' in updates:
                cost = float(updates['costPrice'])
                selling = float(updates['sellingPrice'])
                if cost > 0 and selling > 0:
                    margin = ((selling - cost) / selling) * 100
                    markup = ((selling - cost) / cost) * 100
                    print(f"\n📊 Pricing Analysis:")
                    print(f"📈 Profit Margin: {margin:.2f}%")
                    print(f"📈 Markup: {markup:.2f}%")
                    
            confirm = input("\n❓ Proceed with price updates? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Build update expression
                update_expression = "SET updatedAt = :updated_at"
                expression_values = {
                    ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                for field, value in updates.items():
                    update_expression += f", {field} = :{field}"
                    expression_values[f':{field}'] = value
                    
                self.products_table.update_item(
                    Key={
                        'productId': product['productId'],
                        'category': product['category']
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values
                )
                
                self.print_success("Prices updated successfully!")
                
                # Log audit
                update_details = ', '.join([f"{k}: ₹{v}" for k, v in updates.items()])
                self.log_audit('BULK_PRICE_UPDATE', product['productId'], 
                              f"Bulk price update - {update_details}")
            else:
                self.print_info("Price update cancelled.")
                
        except Exception as e:
            self.print_error(f"Error in bulk price update: {str(e)}")
            
    def calculate_pricing_metrics(self, product: Dict[str, Any]):
        """Calculate and display pricing metrics"""
        self.clear_screen()
        self.print_header("PRICING METRICS CALCULATOR")
        
        cost_price = float(product.get('costPrice', 0))
        selling_price = float(product.get('sellingPrice', 0))
        
        print(f"📦 Product: {product.get('name', 'N/A')}")
        print(f"💲 Cost Price: ₹{cost_price}")
        print(f"💵 Selling Price: ₹{selling_price}")
        
        if cost_price > 0 and selling_price > 0:
            # Calculate metrics
            profit = selling_price - cost_price
            margin = (profit / selling_price) * 100
            markup = (profit / cost_price) * 100
            
            print(f"\n📊 PRICING ANALYSIS:")
            print("-" * 40)
            print(f"💰 Profit per Unit: ₹{profit:.2f}")
            print(f"📈 Profit Margin: {margin:.2f}%")
            print(f"📈 Markup: {markup:.2f}%")
            
            # Pricing recommendations
            print(f"\n💡 PRICING RECOMMENDATIONS:")
            print("-" * 40)
            
            if margin < 10:
                print("⚠️  Low margin - Consider increasing selling price")
            elif margin > 50:
                print("⚠️  High margin - May be overpriced, check competition")
            else:
                print("✅ Healthy margin range")
                
            # Calculate break-even scenarios
            print(f"\n🎯 BREAK-EVEN SCENARIOS:")
            print("-" * 40)
            recommended_margins = [20, 30, 40]
            for target_margin in recommended_margins:
                target_price = cost_price / (1 - target_margin/100)
                print(f"For {target_margin}% margin: ₹{target_price:.2f}")
                
        else:
            print("\n⚠️  Insufficient pricing data for analysis")
            print("Please ensure both cost and selling prices are set")
            
        input("Press Enter to continue...")
        
    def show_price_history(self, product: Dict[str, Any]):
        """Show price history (conceptual)"""
        self.clear_screen()
        self.print_header("PRICE HISTORY")
        
        print(f"📦 Product: {product.get('name', 'N/A')}")
        print("\n💡 Price History Feature (Conceptual)")
        print("In a production system, this would show:")
        print("  • Historical price changes")
        print("  • Date and time of each change")
        print("  • User who made the change")
        print("  • Reason for price change")
        print("  • Price trend analysis")
        
        print(f"\n📅 Current Price Information:")
        print(f"💲 Cost Price: ₹{product.get('costPrice', 0)}")
        print(f"💵 Selling Price: ₹{product.get('sellingPrice', 0)}")
        print(f"🔄 Last Updated: {product.get('updatedAt', 'N/A')}")
        
        input("Press Enter to continue...")
        
    def show_competitive_pricing(self, product: Dict[str, Any]):
        """Show competitive pricing analysis (conceptual)"""
        self.clear_screen()
        self.print_header("COMPETITIVE PRICING")
        
        print(f"📦 Product: {product.get('name', 'N/A')}")
        print("\n💡 Competitive Pricing Feature (Conceptual)")
        print("In a production system, this would show:")
        print("  • Competitor price comparisons")
        print("  • Market average pricing")
        print("  • Price positioning analysis")
        print("  • Pricing recommendations")
        print("  • Market trend indicators")
        
        selling_price = float(product.get('sellingPrice', 0))
        print(f"\n📊 Current Pricing Analysis:")
        print(f"💵 Our Price: ₹{selling_price}")
        print(f"📈 Simulated Market Range: ₹{selling_price * 0.9:.2f} - ₹{selling_price * 1.2:.2f}")
        print(f"📍 Market Position: {'Competitive' if selling_price > 0 else 'Not Set'}")
        
        input("Press Enter to continue...")
        
    def product_performance_analytics(self):
        """Product performance analytics"""
        self.clear_screen()
        self.print_header("PRODUCT PERFORMANCE ANALYTICS")
        
        try:
            # Get all products for analysis
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products found for analysis.")
                input("Press Enter to continue...")
                return
                
            print("📊 Analytics Dashboard:")
            print("1. Overall Product Summary")
            print("2. Pricing Analysis")
            print("3. Category Analysis")
            print("4. Brand Analysis")
            print("5. Profitability Analysis")
            print("6. Inventory Health Check")
            print("7. Product Lifecycle Analysis")
            print("0. Back to Product Management")
            
            choice = input("\n🎯 Select analysis type (0-7): ").strip()
            
            if choice == '1':
                self.show_product_summary(products)
            elif choice == '2':
                self.show_pricing_analysis(products)
            elif choice == '3':
                self.show_category_analysis(products)
            elif choice == '4':
                self.show_brand_analysis(products)
            elif choice == '5':
                self.show_profitability_analysis(products)
            elif choice == '6':
                self.show_inventory_health_check(products)
            elif choice == '7':
                self.show_product_lifecycle_analysis(products)
            elif choice == '0':
                return
            else:
                self.print_error("Invalid choice. Please try again.")
                
        except Exception as e:
            self.print_error(f"Error in analytics: {str(e)}")
            
        input("Press Enter to continue...")
        
    def show_product_summary(self, products: List[Dict[str, Any]]):
        """Show overall product summary"""
        self.clear_screen()
        self.print_header("PRODUCT SUMMARY")
        
        total_products = len(products)
        products_with_variants = len([p for p in products if p.get('hasVariants', False)])
        products_with_expiry = len([p for p in products if p.get('expiryTracking', False)])
        products_with_batches = len([p for p in products if p.get('batchRequired', False)])
        
        # Category distribution
        categories = {}
        brands = {}
        
        for product in products:
            category = product.get('category', 'Unknown')
            brand = product.get('brand', 'Unknown')
            
            categories[category] = categories.get(category, 0) + 1
            brands[brand] = brands.get(brand, 0) + 1
            
        print(f"📊 OVERALL STATISTICS:")
        print("-" * 50)
        print(f"📦 Total Products: {total_products}")
        print(f"🎨 Products with Variants: {products_with_variants} ({(products_with_variants/total_products*100):.1f}%)")
        print(f"⏰ Products with Expiry Tracking: {products_with_expiry} ({(products_with_expiry/total_products*100):.1f}%)")
        print(f"📦 Products with Batch Tracking: {products_with_batches} ({(products_with_batches/total_products*100):.1f}%)")
        
        print(f"\n🏷️ CATEGORY DISTRIBUTION:")
        print("-" * 50)
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total_products) * 100
            print(f"{category}: {count} products ({percentage:.1f}%)")
            
        print(f"\n🏢 BRAND DISTRIBUTION:")
        print("-" * 50)
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total_products) * 100
            print(f"{brand}: {count} products ({percentage:.1f}%)")
            
    def show_pricing_analysis(self, products: List[Dict[str, Any]]):
        """Show pricing analysis"""
        self.clear_screen()
        self.print_header("PRICING ANALYSIS")
        
        # Calculate pricing statistics
        cost_prices = [float(p.get('costPrice', 0)) for p in products if float(p.get('costPrice', 0)) > 0]
        selling_prices = [float(p.get('sellingPrice', 0)) for p in products if float(p.get('sellingPrice', 0)) > 0]
        
        if cost_prices and selling_prices:
            avg_cost = sum(cost_prices) / len(cost_prices)
            avg_selling = sum(selling_prices) / len(selling_prices)
            min_cost = min(cost_prices)
            max_cost = max(cost_prices)
            min_selling = min(selling_prices)
            max_selling = max(selling_prices)
            
            # Calculate margins for products with both prices
            margins = []
            for product in products:
                cost = float(product.get('costPrice', 0))
                selling = float(product.get('sellingPrice', 0))
                if cost > 0 and selling > 0:
                    margin = ((selling - cost) / selling) * 100
                    margins.append(margin)
                    
            print(f"💰 PRICING STATISTICS:")
            print("-" * 50)
            print(f"Average Cost Price: ₹{avg_cost:.2f}")
            print(f"Average Selling Price: ₹{avg_selling:.2f}")
            print(f"Cost Price Range: ₹{min_cost:.2f} - ₹{max_cost:.2f}")
            print(f"Selling Price Range: ₹{min_selling:.2f} - ₹{max_selling:.2f}")
            
            if margins:
                avg_margin = sum(margins) / len(margins)
                min_margin = min(margins)
                max_margin = max(margins)
                
                print(f"\n📊 MARGIN ANALYSIS:")
                print("-" * 50)
                print(f"Average Margin: {avg_margin:.2f}%")
                print(f"Margin Range: {min_margin:.2f}% - {max_margin:.2f}%")
                
                # Margin distribution
                low_margin = len([m for m in margins if m < 20])
                medium_margin = len([m for m in margins if 20 <= m <= 40])
                high_margin = len([m for m in margins if m > 40])
                
                print(f"\n📈 MARGIN DISTRIBUTION:")
                print("-" * 50)
                print(f"Low Margin (<20%): {low_margin} products")
                print(f"Medium Margin (20-40%): {medium_margin} products")
                print(f"High Margin (>40%): {high_margin} products")
        else:
            print("⚠️  Insufficient pricing data for analysis")
            
    def show_category_analysis(self, products: List[Dict[str, Any]]):
        """Show category analysis"""
        self.clear_screen()
        self.print_header("CATEGORY ANALYSIS")
        
        category_stats = {}
        
        for product in products:
            category = product.get('category', 'Unknown')
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'total_cost': 0,
                    'total_selling': 0,
                    'with_variants': 0,
                    'with_expiry': 0
                }
                
            stats = category_stats[category]
            stats['count'] += 1
            
            cost = float(product.get('costPrice', 0))
            selling = float(product.get('sellingPrice', 0))
            
            if cost > 0:
                stats['total_cost'] += cost
            if selling > 0:
                stats['total_selling'] += selling
                
            if product.get('hasVariants', False):
                stats['with_variants'] += 1
            if product.get('expiryTracking', False):
                stats['with_expiry'] += 1
                
        print(f"🏷️ CATEGORY BREAKDOWN:")
        print("-" * 80)
        print(f"{'Category':<20} {'Count':<8} {'Avg Cost':<12} {'Avg Price':<12} {'Variants':<10} {'Expiry':<8}")
        print("-" * 80)
        
        for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            count = stats['count']
            avg_cost = stats['total_cost'] / count if count > 0 else 0
            avg_selling = stats['total_selling'] / count if count > 0 else 0
            variant_pct = (stats['with_variants'] / count * 100) if count > 0 else 0
            expiry_pct = (stats['with_expiry'] / count * 100) if count > 0 else 0
            
            print(f"{category[:19]:<20} {count:<8} ₹{avg_cost:<11.2f} ₹{avg_selling:<11.2f} {variant_pct:<9.1f}% {expiry_pct:<7.1f}%")
            
    def show_brand_analysis(self, products: List[Dict[str, Any]]):
        """Show brand analysis"""
        self.clear_screen()
        self.print_header("BRAND ANALYSIS")
        
        brand_stats = {}
        
        for product in products:
            brand = product.get('brand', 'Unknown')
            if brand not in brand_stats:
                brand_stats[brand] = {
                    'count': 0,
                    'total_cost': 0,
                    'total_selling': 0,
                    'categories': set()
                }
                
            stats = brand_stats[brand]
            stats['count'] += 1
            stats['categories'].add(product.get('category', 'Unknown'))
            
            cost = float(product.get('costPrice', 0))
            selling = float(product.get('sellingPrice', 0))
            
            if cost > 0:
                stats['total_cost'] += cost
            if selling > 0:
                stats['total_selling'] += selling
                
        print(f"🏢 BRAND BREAKDOWN:")
        print("-" * 80)
        print(f"{'Brand':<20} {'Count':<8} {'Categories':<12} {'Avg Cost':<12} {'Avg Price':<12}")
        print("-" * 80)
        
        for brand, stats in sorted(brand_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            count = stats['count']
            cat_count = len(stats['categories'])
            avg_cost = stats['total_cost'] / count if count > 0 else 0
            avg_selling = stats['total_selling'] / count if count > 0 else 0
            
            print(f"{brand[:19]:<20} {count:<8} {cat_count:<12} ₹{avg_cost:<11.2f} ₹{avg_selling:<11.2f}")
            
    def show_profitability_analysis(self, products: List[Dict[str, Any]]):
        """Show profitability analysis"""
        self.clear_screen()
        self.print_header("PROFITABILITY ANALYSIS")
        
        profitable_products = []
        
        for product in products:
            cost = float(product.get('costPrice', 0))
            selling = float(product.get('sellingPrice', 0))
            
            if cost > 0 and selling > 0:
                profit = selling - cost
                margin = (profit / selling) * 100
                
                profitable_products.append({
                    'name': product.get('name', 'Unknown'),
                    'category': product.get('category', 'Unknown'),
                    'cost': cost,
                    'selling': selling,
                    'profit': profit,
                    'margin': margin
                })
                
        if profitable_products:
            # Sort by profit margin
            profitable_products.sort(key=lambda x: x['margin'], reverse=True)
            
            print(f"📈 TOP PROFITABLE PRODUCTS:")
            print("-" * 90)
            print(f"{'Product':<25} {'Category':<15} {'Cost':<10} {'Price':<10} {'Profit':<10} {'Margin':<8}")
            print("-" * 90)
            
            for i, product in enumerate(profitable_products[:10]):
                print(f"{product['name'][:24]:<25} "
                      f"{product['category'][:14]:<15} "
                      f"₹{product['cost']:<9.2f} "
                      f"₹{product['selling']:<9.2f} "
                      f"₹{product['profit']:<9.2f} "
                      f"{product['margin']:<7.1f}%")
                      
            # Profitability summary
            total_profit = sum(p['profit'] for p in profitable_products)
            avg_margin = sum(p['margin'] for p in profitable_products) / len(profitable_products)
            
            print(f"\n💰 PROFITABILITY SUMMARY:")
            print("-" * 50)
            print(f"Total Products Analyzed: {len(profitable_products)}")
            print(f"Average Margin: {avg_margin:.2f}%")
            print(f"Total Potential Profit: ₹{total_profit:.2f}")
        else:
            print("⚠️  No products with complete pricing data found")
            
    def show_inventory_health_check(self, products: List[Dict[str, Any]]):
        """Show inventory health check"""
        self.clear_screen()
        self.print_header("INVENTORY HEALTH CHECK")
        
        print("🏥 INVENTORY HEALTH ANALYSIS:")
        print("-" * 60)
        
        # Check for missing critical information
        missing_cost_price = [p for p in products if not p.get('costPrice') or float(p.get('costPrice', 0)) <= 0]
        missing_selling_price = [p for p in products if not p.get('sellingPrice') or float(p.get('sellingPrice', 0)) <= 0]
        missing_supplier = [p for p in products if not p.get('supplierId', '').strip()]
        missing_reorder_point = [p for p in products if not p.get('reorderPoint') or int(p.get('reorderPoint', 0)) <= 0]
        
        print(f"❌ Missing Cost Price: {len(missing_cost_price)} products")
        print(f"❌ Missing Selling Price: {len(missing_selling_price)} products")
        print(f"❌ Missing Supplier ID: {len(missing_supplier)} products")
        print(f"⚠️  Missing Reorder Point: {len(missing_reorder_point)} products")
        
        # Show problematic products
        if missing_cost_price:
            print(f"\n💲 PRODUCTS MISSING COST PRICE:")
            for product in missing_cost_price[:5]:
                print(f"  • {product.get('name', 'Unknown')} (ID: {product.get('productId', 'Unknown')})")
            if len(missing_cost_price) > 5:
                print(f"  ... and {len(missing_cost_price) - 5} more")
                
        if missing_selling_price:
            print(f"\n💵 PRODUCTS MISSING SELLING PRICE:")
            for product in missing_selling_price[:5]:
                print(f"  • {product.get('name', 'Unknown')} (ID: {product.get('productId', 'Unknown')})")
            if len(missing_selling_price) > 5:
                print(f"  ... and {len(missing_selling_price) - 5} more")
                
        # Health score
        total_issues = len(missing_cost_price) + len(missing_selling_price) + len(missing_supplier)
        health_score = max(0, 100 - (total_issues / len(products) * 100))
        
        print(f"\n🏥 INVENTORY HEALTH SCORE: {health_score:.1f}%")
        if health_score >= 90:
            print("✅ Excellent inventory health")
        elif health_score >= 70:
            print("⚠️  Good inventory health with minor issues")
        elif health_score >= 50:
            print("⚠️  Fair inventory health - attention needed")
        else:
            print("❌ Poor inventory health - immediate action required")
            
    def show_product_lifecycle_analysis(self, products: List[Dict[str, Any]]):
        """Show product lifecycle analysis"""
        self.clear_screen()
        self.print_header("PRODUCT LIFECYCLE ANALYSIS")
        
        print("🔄 PRODUCT LIFECYCLE OVERVIEW:")
        print("-" * 60)
        
        # Analyze creation dates
        now = datetime.now(timezone.utc)
        
        new_products = []  # Created in last 30 days
        recent_products = []  # Created in last 90 days
        mature_products = []  # Created more than 90 days ago
        
        for product in products:
            created_at = product.get('createdAt', '')
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_old = (now - created_date).days
                    
                    if days_old <= 30:
                        new_products.append(product)
                    elif days_old <= 90:
                        recent_products.append(product)
                    else:
                        mature_products.append(product)
                except:
                    mature_products.append(product)  # Fallback for invalid dates
            else:
                mature_products.append(product)  # No creation date
                
        print(f"🆕 New Products (≤30 days): {len(new_products)}")
        print(f"📈 Recent Products (31-90 days): {len(recent_products)}")
        print(f"🏛️ Mature Products (>90 days): {len(mature_products)}")
        
        # Product configuration maturity
        fully_configured = 0
        partially_configured = 0
        
        for product in products:
            config_score = 0
            
            if product.get('costPrice') and float(product.get('costPrice', 0)) > 0:
                config_score += 1
            if product.get('sellingPrice') and float(product.get('sellingPrice', 0)) > 0:
                config_score += 1
            if product.get('supplierId', '').strip():
                config_score += 1
            if product.get('minStock') and int(product.get('minStock', 0)) > 0:
                config_score += 1
            if product.get('reorderPoint') and int(product.get('reorderPoint', 0)) > 0:
                config_score += 1
                
            if config_score >= 4:
                fully_configured += 1
            elif config_score >= 2:
                partially_configured += 1
                
        print(f"\n⚙️ CONFIGURATION MATURITY:")
        print("-" * 40)
        print(f"✅ Fully Configured: {fully_configured} products")
        print(f"⚠️  Partially Configured: {partially_configured} products")
        print(f"❌ Poorly Configured: {len(products) - fully_configured - partially_configured} products")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        if len(new_products) > len(products) * 0.2:
            print("• High product creation rate - ensure proper onboarding")
        if partially_configured > 0:
            print("• Complete configuration for partially configured products")
        if len(missing_cost_price := [p for p in products if not p.get('costPrice') or float(p.get('costPrice', 0)) <= 0]) > 0:
            print(f"• Set cost prices for {len(missing_cost_price)} products")
        
    def update_user(self):
        """Update user information"""
        self.clear_screen()
        self.print_header("UPDATE USER")
        
        try:
            # Get all users first
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            if not users:
                self.print_info("No users found in the system.")
                input("Press Enter to continue...")
                return
                
            print("👥 Available Users:")
            for i, user in enumerate(users, 1):
                status = "ACTIVE" if user.get('isActive', False) else "INACTIVE"
                print(f"{i}. {user.get('name', 'N/A')} ({user.get('userId', 'N/A')}) - {user.get('role', 'N/A')} - {status}")
                
            user_choice = input("\n🎯 Select user number to update: ").strip()
            
            try:
                user_index = int(user_choice) - 1
                if 0 <= user_index < len(users):
                    selected_user = users[user_index]
                    self.perform_user_update(selected_user)
                else:
                    self.print_error("Invalid user selection.")
            except ValueError:
                self.print_error("Invalid user number.")
                
        except Exception as e:
            self.print_error(f"Error updating user: {str(e)}")
            
        input("Press Enter to continue...")
        
    def perform_user_update(self, user: Dict[str, Any]):
        """Perform user update with field selection"""
        self.clear_screen()
        self.print_header(f"UPDATE USER - {user.get('name', 'Unknown')}")
        
        print("📝 Select field to update:")
        print("1. Full Name")
        print("2. Email")
        print("3. Phone")
        print("4. Password")
        print("5. Role")
        print("6. Active Status")
        print("7. Update Multiple Fields")
        print("0. Cancel")
        
        choice = input("\n🎯 Select field (0-7): ").strip()
        
        try:
            if choice == '1':
                self.update_user_field(user, 'name', 'Full Name')
            elif choice == '2':
                self.update_user_field(user, 'email', 'Email')
            elif choice == '3':
                self.update_user_field(user, 'phone', 'Phone')
            elif choice == '4':
                self.update_user_field(user, 'password', 'Password')
            elif choice == '5':
                self.update_user_role(user)
            elif choice == '6':
                self.toggle_user_status(user)
            elif choice == '7':
                self.update_multiple_user_fields(user)
            elif choice == '0':
                self.print_info("Update cancelled.")
                return
            else:
                self.print_error("Invalid choice.")
                
        except Exception as e:
            self.print_error(f"Error updating user field: {str(e)}")
            
    def update_user_field(self, user: Dict[str, Any], field_name: str, field_display: str, new_value: str = None):
        """Update a specific user field"""
        try:
            if new_value is None:
                current_value = user.get(field_name, 'N/A')
                if field_name == 'password':
                    print(f"\nCurrent {field_display}: [HIDDEN]")
                else:
                    print(f"\nCurrent {field_display}: {current_value}")
                new_value = input(f"New {field_display}: ").strip()
                
            if not new_value:
                self.print_error(f"{field_display} cannot be empty")
                return
                
            # Update the user
            update_expression = f"SET {field_name} = :new_value, updatedAt = :updated_at"
            expression_values = {
                ':new_value': new_value,
                ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.users_table.update_item(
                Key={
                    'userId': user['userId'],
                    'role': user['role']
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Log audit
            if field_name == 'password':
                self.log_audit('USER_UPDATE', user['userId'], f"Updated password for user: {user.get('name', 'Unknown')}")
            else:
                self.log_audit('USER_UPDATE', user['userId'], 
                              f"Updated {field_display}: {user.get(field_name, 'N/A')} -> {new_value}")
            
            self.print_success(f"{field_display} updated successfully!")
            
        except Exception as e:
            self.print_error(f"Error updating {field_display}: {str(e)}")
            
    def update_user_role(self, user: Dict[str, Any]):
        """Update user role"""
        try:
            current_role = user.get('role', 'N/A')
            print(f"\nCurrent Role: {current_role}")
            
            print("\n👑 Available Roles:")
            roles = ['SUPER_ADMIN', 'WAREHOUSE_MANAGER', 'INVENTORY_STAFF', 
                    'LOGISTICS_MANAGER', 'DELIVERY_PERSONNEL', 'AUDITOR']
            
            for i, role in enumerate(roles, 1):
                print(f"{i}. {role}")
                
            role_choice = input(f"\n🎯 Select new role (1-{len(roles)}): ").strip()
            
            try:
                role_index = int(role_choice) - 1
                if 0 <= role_index < len(roles):
                    new_role = roles[role_index]
                    
                    if new_role == current_role:
                        self.print_info("User already has this role.")
                        return
                        
                    # Get new permissions for the role
                    new_permissions = self.get_default_permissions(new_role)
                    
                    # Update user role and permissions
                    self.users_table.update_item(
                        Key={
                            'userId': user['userId'],
                            'role': user['role']  # Current role for the key
                        },
                        UpdateExpression="SET #r = :new_role, permissions = :permissions, updatedAt = :updated_at",
                        ExpressionAttributeNames={
                            '#r': 'role'
                        },
                        ExpressionAttributeValues={
                            ':new_role': new_role,
                            ':permissions': new_permissions,
                            ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    self.print_success(f"User role updated from {current_role} to {new_role}!")
                    self.print_info(f"Permissions updated to match new role")
                    
                    # Log audit
                    self.log_audit('USER_ROLE_UPDATE', user['userId'], 
                                  f"Updated role from {current_role} to {new_role}")
                else:
                    self.print_error("Invalid role selection.")
            except ValueError:
                self.print_error("Invalid role number.")
                
        except Exception as e:
            self.print_error(f"Error updating user role: {str(e)}")
            
    def toggle_user_status(self, user: Dict[str, Any]):
        """Toggle user active status"""
        try:
            current_status = user.get('isActive', False)
            new_status = not current_status
            
            status_text = "activate" if new_status else "deactivate"
            
            print(f"\nCurrent Status: {'ACTIVE' if current_status else 'INACTIVE'}")
            confirm = input(f"\n❓ Are you sure you want to {status_text} this user? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                self.users_table.update_item(
                    Key={
                        'userId': user['userId'],
                        'role': user['role']
                    },
                    UpdateExpression="SET isActive = :status, updatedAt = :updated_at",
                    ExpressionAttributeValues={
                        ':status': new_status,
                        ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                
                status_text = "activated" if new_status else "deactivated"
                self.print_success(f"User {status_text} successfully!")
                
                # Log audit
                self.log_audit('USER_STATUS_UPDATE', user['userId'], 
                              f"User {status_text}: {user.get('name', 'Unknown')}")
            else:
                self.print_info("Status update cancelled.")
                
        except Exception as e:
            self.print_error(f"Error updating user status: {str(e)}")
            
    def update_multiple_user_fields(self, user: Dict[str, Any]):
        """Update multiple user fields at once"""
        self.clear_screen()
        self.print_header(f"UPDATE MULTIPLE FIELDS - {user.get('name', 'Unknown')}")
        
        updates = {}
        
        # Collect all field updates
        print("📝 Enter new values (press Enter to skip a field):")
        
        name = input(f"Full Name [{user.get('name', 'N/A')}]: ").strip()
        if name:
            updates['name'] = name
            
        email = input(f"Email [{user.get('email', 'N/A')}]: ").strip()
        if email:
            updates['email'] = email
            
        phone = input(f"Phone [{user.get('phone', 'N/A')}]: ").strip()
        if phone:
            updates['phone'] = phone
            
        password = input("New Password (leave empty to skip): ").strip()
        if password:
            updates['password'] = password
            
        if not updates:
            self.print_info("No fields to update.")
            return
            
        # Confirm updates
        print(f"\n📋 Fields to update:")
        for field, value in updates.items():
            display_value = "[HIDDEN]" if field == 'password' else value
            print(f"  • {field}: {display_value}")
            
        confirm = input("\n❓ Proceed with updates? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            try:
                # Build update expression
                update_expression = "SET "
                expression_values = {}
                
                for i, (field, value) in enumerate(updates.items()):
                    if i > 0:
                        update_expression += ", "
                    update_expression += f"{field} = :val{i}"
                    expression_values[f':val{i}'] = value
                    
                # Add updated timestamp
                update_expression += ", updatedAt = :updated_at"
                expression_values[':updated_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                
                self.users_table.update_item(
                    Key={
                        'userId': user['userId'],
                        'role': user['role']
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_values
                )
                
                # Log audit
                update_details = ', '.join([f"{k}: {'[HIDDEN]' if k == 'password' else v}" for k, v in updates.items()])
                self.log_audit('USER_UPDATE', user['userId'], 
                              f"Updated multiple fields - {update_details}")
                
                self.print_success("User updated successfully!")
                
            except Exception as e:
                self.print_error(f"Error updating user: {str(e)}")
        else:
            self.print_info("Update cancelled.")
        
    def delete_user(self):
        """Delete user"""
        self.clear_screen()
        self.print_header("DELETE USER")
        
        try:
            # Get all users first
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            if not users:
                self.print_info("No users found in the system.")
                input("Press Enter to continue...")
                return
                
            # Filter out current user (can't delete self)
            other_users = [user for user in users if user.get('userId') != self.current_user.get('userId')]
            
            if not other_users:
                self.print_info("No other users found to delete.")
                input("Press Enter to continue...")
                return
                
            print("👥 Available Users to Delete:")
            for i, user in enumerate(other_users, 1):
                status = "ACTIVE" if user.get('isActive', False) else "INACTIVE"
                print(f"{i}. {user.get('name', 'N/A')} ({user.get('userId', 'N/A')}) - {user.get('role', 'N/A')} - {status}")
                
            user_choice = input("\n🎯 Select user number to delete: ").strip()
            
            try:
                user_index = int(user_choice) - 1
                if 0 <= user_index < len(other_users):
                    selected_user = other_users[user_index]
                    self.confirm_user_deletion(selected_user)
                else:
                    self.print_error("Invalid user selection.")
            except ValueError:
                self.print_error("Invalid user number.")
                
        except Exception as e:
            self.print_error(f"Error deleting user: {str(e)}")
            
        input("Press Enter to continue...")
        
    def confirm_user_deletion(self, user: Dict[str, Any]):
        """Confirm and perform user deletion"""
        self.clear_screen()
        self.print_header("CONFIRM USER DELETION")
        
        print(f"⚠️  WARNING: You are about to delete:")
        print(f"👤 Name: {user.get('name', 'Unknown')}")
        print(f"🆔 User ID: {user.get('userId', 'Unknown')}")
        print(f"👑 Role: {user.get('role', 'Unknown')}")
        print(f"📧 Email: {user.get('email', 'Unknown')}")
        print(f"📱 Phone: {user.get('phone', 'Unknown')}")
        
        print(f"\n⚠️  CONSEQUENCES:")
        print(f"• This action cannot be undone")
        print(f"• User will lose access to the system immediately")
        print(f"• All audit logs will remain for compliance")
        print(f"• Associated data may become orphaned")
        
        # Additional warnings for specific roles
        user_role = user.get('role', '')
        if user_role == 'SUPER_ADMIN':
            print(f"\n🚨 CRITICAL WARNING:")
            print(f"• You are deleting another SUPER ADMIN")
            print(f"• Ensure at least one SUPER ADMIN remains active")
        elif user_role in ['WAREHOUSE_MANAGER', 'LOGISTICS_MANAGER']:
            print(f"\n⚠️  OPERATIONAL WARNING:")
            print(f"• This is a management role with operational responsibilities")
            print(f"• Ensure proper handover before deletion")
            
        print(f"\n🔐 Security Check:")
        print(f"Type '{user.get('userId', 'unknown')}' to confirm deletion:")
        
        confirmation = input("Confirmation: ").strip()
        
        if confirmation == user.get('userId', 'unknown'):
            try:
                # Perform deletion
                self.users_table.delete_item(
                    Key={
                        'userId': user['userId'],
                        'role': user['role']
                    }
                )
                
                # Log audit
                self.log_audit('USER_DELETE', user['userId'], 
                              f"Deleted user: {user.get('name', 'Unknown')} ({user.get('role', 'Unknown')})")
                
                self.print_success(f"User '{user.get('name', 'Unknown')}' deleted successfully!")
                
                # Additional cleanup message
                print(f"\n💡 Cleanup Recommendations:")
                print(f"• Review and reassign any tasks assigned to this user")
                print(f"• Update any reports or analytics that reference this user")
                print(f"• Notify team members about this user's removal")
                
            except Exception as e:
                self.print_error(f"Error deleting user: {str(e)}")
        else:
            self.print_info("User deletion cancelled - incorrect confirmation.")
            
        input("Press Enter to continue...")
        
    def manage_permissions(self):
        """Manage user permissions"""
        self.clear_screen()
        self.print_header("MANAGE PERMISSIONS")
        
        try:
            # Get all users first
            response = self.users_table.scan()
            users = response.get('Items', [])
            
            if not users:
                self.print_info("No users found in the system.")
                input("Press Enter to continue...")
                return
                
            print("👥 Available Users:")
            for i, user in enumerate(users, 1):
                permissions_count = len(user.get('permissions', []))
                status = "ACTIVE" if user.get('isActive', False) else "INACTIVE"
                print(f"{i}. {user.get('name', 'N/A')} ({user.get('role', 'N/A')}) - {permissions_count} permissions - {status}")
                
            user_choice = input("\n🎯 Select user number to manage permissions: ").strip()
            
            try:
                user_index = int(user_choice) - 1
                if 0 <= user_index < len(users):
                    selected_user = users[user_index]
                    self.manage_user_permissions_operations(selected_user)
                else:
                    self.print_error("Invalid user selection.")
            except ValueError:
                self.print_error("Invalid user number.")
                
        except Exception as e:
            self.print_error(f"Error managing permissions: {str(e)}")
            
        input("Press Enter to continue...")
        
    def manage_user_permissions_operations(self, user: Dict[str, Any]):
        """Manage permission operations for a specific user"""
        while True:
            self.clear_screen()
            self.print_header(f"MANAGE PERMISSIONS - {user.get('name', 'Unknown')}")
            
            current_permissions = user.get('permissions', [])
            
            print(f"👤 User: {user.get('name', 'N/A')}")
            print(f"👑 Role: {user.get('role', 'N/A')}")
            print(f"🔐 Current Permissions ({len(current_permissions)}):")
            
            if current_permissions:
                for i, permission in enumerate(current_permissions, 1):
                    print(f"  {i}. {permission}")
            else:
                print("  No permissions assigned")
            
            print("\n📋 Permission Operations:")
            print("1. View All Available Permissions")
            print("2. Add Permission")
            print("3. Remove Permission")
            print("4. Reset to Role Defaults")
            print("5. Copy Permissions from Another User")
            print("6. Export Permissions")
            print("0. Back to User Management")
            
            choice = input("\n🎯 Select operation (0-6): ").strip()
            
            if choice == '1':
                self.view_available_permissions()
            elif choice == '2':
                self.add_user_permission(user)
                break
            elif choice == '3':
                self.remove_user_permission(user)
                break
            elif choice == '4':
                self.reset_permissions_to_defaults(user)
                break
            elif choice == '5':
                self.copy_permissions_from_user(user)
                break
            elif choice == '6':
                self.export_user_permissions(user)
            elif choice == '0':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def view_available_permissions(self):
        """View all available permissions in the system"""
        self.clear_screen()
        self.print_header("AVAILABLE PERMISSIONS")
        
        # Define all available permissions categorized
        permission_categories = {
            'System Administration': [
                'SYSTEM_CONFIG', 'USER_MANAGEMENT', 'INTEGRATION_MANAGEMENT',
                'SYSTEM_MONITORING', 'BACKUP_RECOVERY', 'LICENSE_MANAGEMENT'
            ],
            'Inventory Management': [
                'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                'STOCK_MOVEMENT', 'ORDER_FULFILLMENT', 'INVENTORY_COUNTING'
            ],
            'Product Management': [
                'PRODUCT_CREATE', 'PRODUCT_DELETE', 'PRODUCT_UPDATE',
                'PRODUCT_READ', 'VARIANT_MANAGEMENT', 'PRICING_MANAGEMENT'
            ],
            'Warehouse Operations': [
                'WAREHOUSE_MANAGEMENT', 'QUALITY_CONTROL', 'RECEIVING_MANAGEMENT',
                'EXPIRY_MANAGEMENT', 'SPACE_OPTIMIZATION'
            ],
            'Logistics & Delivery': [
                'ROUTE_PLANNING', 'DELIVERY_MANAGEMENT', 'RIDER_MANAGEMENT',
                'RUNSHEET_MANAGEMENT', 'PERFORMANCE_MONITORING'
            ],
            'Field Operations': [
                'RUNSHEET_VIEW', 'ORDER_DELIVERY', 'CASH_COLLECTION',
                'STATUS_UPDATE', 'CUSTOMER_INTERACTION'
            ],
            'Audit & Compliance': [
                'TRANSACTION_VERIFICATION', 'COMPLIANCE_CHECKING',
                'INVENTORY_VERIFICATION', 'REPORT_GENERATION', 'PROCESS_REVIEW'
            ]
        }
        
        for category, permissions in permission_categories.items():
            print(f"\n🏷️ {category.upper()}:")
            print("-" * 50)
            for permission in permissions:
                print(f"  • {permission}")
                
        print(f"\n💡 Permission Guidelines:")
        print("• Users should only have permissions necessary for their role")
        print("• Regular review of permissions is recommended")
        print("• Critical permissions should be limited to trusted users")
        print("• Always follow principle of least privilege")
        
        input("Press Enter to continue...")
        
    def add_user_permission(self, user: Dict[str, Any]):
        """Add a permission to a user"""
        try:
            current_permissions = set(user.get('permissions', []))
            
            # Get all possible permissions
            all_permissions = [
                'SYSTEM_CONFIG', 'USER_MANAGEMENT', 'INTEGRATION_MANAGEMENT',
                'SYSTEM_MONITORING', 'BACKUP_RECOVERY', 'LICENSE_MANAGEMENT',
                'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                'STOCK_MOVEMENT', 'ORDER_FULFILLMENT', 'INVENTORY_COUNTING',
                'PRODUCT_CREATE', 'PRODUCT_DELETE', 'PRODUCT_UPDATE',
                'PRODUCT_READ', 'VARIANT_MANAGEMENT', 'PRICING_MANAGEMENT',
                'WAREHOUSE_MANAGEMENT', 'QUALITY_CONTROL', 'RECEIVING_MANAGEMENT',
                'EXPIRY_MANAGEMENT', 'SPACE_OPTIMIZATION',
                'ROUTE_PLANNING', 'DELIVERY_MANAGEMENT', 'RIDER_MANAGEMENT',
                'RUNSHEET_MANAGEMENT', 'PERFORMANCE_MONITORING',
                'RUNSHEET_VIEW', 'ORDER_DELIVERY', 'CASH_COLLECTION',
                'STATUS_UPDATE', 'CUSTOMER_INTERACTION',
                'TRANSACTION_VERIFICATION', 'COMPLIANCE_CHECKING',
                'INVENTORY_VERIFICATION', 'REPORT_GENERATION', 'PROCESS_REVIEW'
            ]
            
            # Filter out permissions user already has
            available_permissions = [p for p in all_permissions if p not in current_permissions]
            
            if not available_permissions:
                self.print_info("User already has all available permissions.")
                return
                
            print(f"\n🔐 Available Permissions to Add:")
            for i, permission in enumerate(available_permissions, 1):
                print(f"{i}. {permission}")
                
            permission_choice = input(f"\n🎯 Select permission to add (1-{len(available_permissions)}): ").strip()
            
            try:
                permission_index = int(permission_choice) - 1
                if 0 <= permission_index < len(available_permissions):
                    new_permission = available_permissions[permission_index]
                    
                    # Add permission to user
                    updated_permissions = list(current_permissions) + [new_permission]
                    
                    self.users_table.update_item(
                        Key={
                            'userId': user['userId'],
                            'role': user['role']
                        },
                        UpdateExpression="SET permissions = :permissions, updatedAt = :updated_at",
                        ExpressionAttributeValues={
                            ':permissions': updated_permissions,
                            ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    self.print_success(f"Permission '{new_permission}' added successfully!")
                    
                    # Log audit
                    self.log_audit('PERMISSION_ADD', user['userId'], 
                                  f"Added permission '{new_permission}' to user: {user.get('name', 'Unknown')}")
                else:
                    self.print_error("Invalid permission selection.")
            except ValueError:
                self.print_error("Invalid permission number.")
                
        except Exception as e:
            self.print_error(f"Error adding permission: {str(e)}")
            
    def remove_user_permission(self, user: Dict[str, Any]):
        """Remove a permission from a user"""
        try:
            current_permissions = user.get('permissions', [])
            
            if not current_permissions:
                self.print_info("User has no permissions to remove.")
                return
                
            print(f"\n🔐 Current Permissions:")
            for i, permission in enumerate(current_permissions, 1):
                print(f"{i}. {permission}")
                
            permission_choice = input(f"\n🎯 Select permission to remove (1-{len(current_permissions)}): ").strip()
            
            try:
                permission_index = int(permission_choice) - 1
                if 0 <= permission_index < len(current_permissions):
                    removed_permission = current_permissions[permission_index]
                    
                    # Remove permission from user
                    updated_permissions = [p for p in current_permissions if p != removed_permission]
                    
                    self.users_table.update_item(
                        Key={
                            'userId': user['userId'],
                            'role': user['role']
                        },
                        UpdateExpression="SET permissions = :permissions, updatedAt = :updated_at",
                        ExpressionAttributeValues={
                            ':permissions': updated_permissions,
                            ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    self.print_success(f"Permission '{removed_permission}' removed successfully!")
                    
                    # Log audit
                    self.log_audit('PERMISSION_REMOVE', user['userId'], 
                                  f"Removed permission '{removed_permission}' from user: {user.get('name', 'Unknown')}")
                else:
                    self.print_error("Invalid permission selection.")
            except ValueError:
                self.print_error("Invalid permission number.")
                
        except Exception as e:
            self.print_error(f"Error removing permission: {str(e)}")
            
    def reset_permissions_to_defaults(self, user: Dict[str, Any]):
        """Reset user permissions to role defaults"""
        try:
            user_role = user.get('role', '')
            default_permissions = self.get_default_permissions(user_role)
            
            print(f"\n🔄 Resetting permissions for role: {user_role}")
            print(f"📊 Current permissions: {len(user.get('permissions', []))}")
            print(f"📊 Default permissions: {len(default_permissions)}")
            
            confirm = input("\n❓ Proceed with permission reset? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                self.users_table.update_item(
                    Key={
                        'userId': user['userId'],
                        'role': user['role']
                    },
                    UpdateExpression="SET permissions = :permissions, updatedAt = :updated_at",
                    ExpressionAttributeValues={
                        ':permissions': default_permissions,
                        ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                
                self.print_success("Permissions reset to role defaults successfully!")
                
                # Log audit
                self.log_audit('PERMISSION_RESET', user['userId'], 
                              f"Reset permissions to defaults for role {user_role}: {user.get('name', 'Unknown')}")
            else:
                self.print_info("Permission reset cancelled.")
                
        except Exception as e:
            self.print_error(f"Error resetting permissions: {str(e)}")
            
    def copy_permissions_from_user(self, target_user: Dict[str, Any]):
        """Copy permissions from another user"""
        try:
            # Get all users except target user
            response = self.users_table.scan()
            all_users = response.get('Items', [])
            source_users = [u for u in all_users if u.get('userId') != target_user.get('userId')]
            
            if not source_users:
                self.print_info("No other users found to copy permissions from.")
                return
                
            print(f"\n👥 Available Users to Copy From:")
            for i, user in enumerate(source_users, 1):
                permissions_count = len(user.get('permissions', []))
                print(f"{i}. {user.get('name', 'N/A')} ({user.get('role', 'N/A')}) - {permissions_count} permissions")
                
            user_choice = input(f"\n🎯 Select user to copy from (1-{len(source_users)}): ").strip()
            
            try:
                user_index = int(user_choice) - 1
                if 0 <= user_index < len(source_users):
                    source_user = source_users[user_index]
                    source_permissions = source_user.get('permissions', [])
                    
                    print(f"\n📊 Permissions to copy ({len(source_permissions)}):")
                    for permission in source_permissions:
                        print(f"  • {permission}")
                        
                    confirm = input("\n❓ Copy these permissions? (yes/no): ").strip().lower()
                    
                    if confirm == 'yes':
                        self.users_table.update_item(
                            Key={
                                'userId': target_user['userId'],
                                'role': target_user['role']
                            },
                            UpdateExpression="SET permissions = :permissions, updatedAt = :updated_at",
                            ExpressionAttributeValues={
                                ':permissions': source_permissions,
                                ':updated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                        self.print_success("Permissions copied successfully!")
                        
                        # Log audit
                        self.log_audit('PERMISSION_COPY', target_user['userId'], 
                                      f"Copied permissions from {source_user.get('name', 'Unknown')} to {target_user.get('name', 'Unknown')}")
                    else:
                        self.print_info("Permission copy cancelled.")
                else:
                    self.print_error("Invalid user selection.")
            except ValueError:
                self.print_error("Invalid user number.")
                
        except Exception as e:
            self.print_error(f"Error copying permissions: {str(e)}")
            
    def export_user_permissions(self, user: Dict[str, Any]):
        """Export user permissions for review"""
        self.clear_screen()
        self.print_header("EXPORT USER PERMISSIONS")
        
        permissions = user.get('permissions', [])
        
        print(f"📋 PERMISSION EXPORT REPORT")
        print("=" * 60)
        print(f"👤 User: {user.get('name', 'N/A')}")
        print(f"🆔 User ID: {user.get('userId', 'N/A')}")
        print(f"👑 Role: {user.get('role', 'N/A')}")
        print(f"📧 Email: {user.get('email', 'N/A')}")
        print(f"📅 Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔐 Total Permissions: {len(permissions)}")
        
        print(f"\n📝 ASSIGNED PERMISSIONS:")
        print("-" * 40)
        
        if permissions:
            # Group permissions by category for better readability
            permission_categories = {
                'System': [p for p in permissions if any(keyword in p for keyword in ['SYSTEM', 'USER', 'INTEGRATION', 'MONITORING', 'BACKUP', 'LICENSE'])],
                'Inventory': [p for p in permissions if any(keyword in p for keyword in ['INVENTORY', 'STOCK', 'ADJUSTMENT'])],
                'Product': [p for p in permissions if any(keyword in p for keyword in ['PRODUCT', 'VARIANT', 'PRICING'])],
                'Warehouse': [p for p in permissions if any(keyword in p for keyword in ['WAREHOUSE', 'QUALITY', 'RECEIVING', 'EXPIRY', 'SPACE'])],
                'Logistics': [p for p in permissions if any(keyword in p for keyword in ['ROUTE', 'DELIVERY', 'RIDER', 'RUNSHEET', 'PERFORMANCE'])],
                'Field': [p for p in permissions if any(keyword in p for keyword in ['ORDER_DELIVERY', 'CASH_COLLECTION', 'STATUS_UPDATE', 'CUSTOMER'])],
                'Audit': [p for p in permissions if any(keyword in p for keyword in ['TRANSACTION', 'COMPLIANCE', 'VERIFICATION', 'REPORT', 'PROCESS'])]
            }
            
            for category, perms in permission_categories.items():
                if perms:
                    print(f"\n{category} Permissions:")
                    for perm in sorted(perms):
                        print(f"  ✓ {perm}")
                        
            # Show any uncategorized permissions
            categorized_perms = set()
            for perms in permission_categories.values():
                categorized_perms.update(perms)
            uncategorized = [p for p in permissions if p not in categorized_perms]
            if uncategorized:
                print(f"\nOther Permissions:")
                for perm in sorted(uncategorized):
                    print(f"  ✓ {perm}")
        else:
            print("No permissions assigned")
            
        print(f"\n💡 Notes:")
        print(f"• This export is for review and audit purposes")
        print(f"• Contact system administrator for permission changes")
        print(f"• Regular permission reviews are recommended")
        
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
                'userAgent': 'SuperAdmin-Standalone',
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
            self.print_success("Thank you for using the Super Admin system!")


def main():
    """Main entry point"""
    super_admin = SuperAdminStandalone()
    super_admin.run()


if __name__ == '__main__':
    main() 