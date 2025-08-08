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
            category = input("🏷️ Category: ").strip()
            brand = input("🏢 Brand: ").strip()
            
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
        self.clear_screen()
        self.print_header("SUPPLIER MANAGEMENT")
        self.print_info("Supplier management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def category_management_menu(self):
        """Category Management Operations"""
        self.clear_screen()
        self.print_header("CATEGORY MANAGEMENT")
        self.print_info("Category management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def system_configuration_menu(self):
        """System Configuration Operations"""
        self.clear_screen()
        self.print_header("SYSTEM CONFIGURATION")
        self.print_info("System configuration functionality will be implemented.")
        input("Press Enter to continue...")
        
    def system_monitoring_menu(self):
        """System Monitoring Operations"""
        self.clear_screen()
        self.print_header("SYSTEM MONITORING")
        self.print_info("System monitoring functionality will be implemented.")
        input("Press Enter to continue...")
        
    def security_management_menu(self):
        """Security Management Operations"""
        self.clear_screen()
        self.print_header("SECURITY MANAGEMENT")
        self.print_info("Security management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def analytics_reports_menu(self):
        """Analytics and Reports Operations"""
        self.clear_screen()
        self.print_header("ANALYTICS & REPORTS")
        self.print_info("Analytics and reports functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_product_details(self):
        """View detailed product information"""
        self.clear_screen()
        self.print_header("PRODUCT DETAILS")
        self.print_info("Product details viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_product_information(self):
        """Update product information"""
        self.clear_screen()
        self.print_header("UPDATE PRODUCT INFORMATION")
        self.print_info("Product information update functionality will be implemented.")
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
        
    def update_user(self):
        """Update user information"""
        self.clear_screen()
        self.print_header("UPDATE USER")
        self.print_info("User update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def delete_user(self):
        """Delete user"""
        self.clear_screen()
        self.print_header("DELETE USER")
        self.print_info("User deletion functionality will be implemented.")
        input("Press Enter to continue...")
        
    def manage_permissions(self):
        """Manage user permissions"""
        self.clear_screen()
        self.print_header("MANAGE PERMISSIONS")
        self.print_info("Permission management functionality will be implemented.")
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