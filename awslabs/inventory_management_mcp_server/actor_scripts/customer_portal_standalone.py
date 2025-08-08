#!/usr/bin/env python3
# customer_portal_standalone.py
"""
Customer Portal Standalone Script
Run this script in a separate terminal window for Customer operations.
Simulates external customer portal interactions.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional


class CustomerPortalStandalone:
    """Standalone Customer Portal with External Operations"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.customers_table = self.dynamodb.Table('InventoryManagement-Customers')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.deliveries_table = self.dynamodb.Table('InventoryManagement-Deliveries')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
        self.current_customer = None
        self.customer_id = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"👤 {title}")
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
            
    def authenticate_customer(self) -> bool:
        """Authenticate customer login"""
        self.clear_screen()
        self.print_header("CUSTOMER PORTAL - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your customer credentials:")
        print("💡 Demo credentials: CUST001 / customer123")
        
        customer_id = input("\n👤 Customer ID: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not customer_id or not password:
            self.print_error("Customer ID and password are required")
            return False
            
        customer = self.authenticate_customer_db(customer_id, password)
        if customer:
            self.current_customer = customer
            self.customer_id = customer_id
            self.print_success(f"Welcome, {customer.get('name', customer_id)}!")
            self.print_info(f"Customer ID: {customer_id}")
            self.print_info(f"Status: {customer.get('status', 'Unknown')}")
            return True
        else:
            self.print_error("Invalid credentials or customer not found.")
            return False
            
    def authenticate_customer_db(self, customer_id: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate customer against DynamoDB Customers table"""
        try:
            # First try to find the customer by scanning (since we don't know the exact key structure)
            response = self.customers_table.scan(
                FilterExpression='customerId = :customerId',
                ExpressionAttributeValues={':customerId': customer_id}
            )
            
            if response['Items']:
                customer = response['Items'][0]
                # For demo purposes, check if password matches (in real system, this would be hashed)
                if self.verify_password(password, customer.get('password', 'customer123')):
                    return customer
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simplified for demo)"""
        return input_password == stored_password
        
    def create_demo_customer(self):
        """Create demo customer if it doesn't exist"""
        try:
            demo_customer = {
                'customerId': 'CUST001',
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+919876543210',
                'address': '123 Main St, Mumbai',
                'status': 'ACTIVE',
                'membershipLevel': 'GOLD',
                'totalOrders': 25,
                'totalSpent': Decimal('15000'),
                'lastOrderDate': '2024-01-15',
                'isActive': True,
                'password': 'customer123',  # In real system, this would be hashed
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Check if customer already exists
            response = self.customers_table.scan(
                FilterExpression='customerId = :customerId',
                ExpressionAttributeValues={':customerId': 'CUST001'}
            )
            
            if not response['Items']:
                self.customers_table.put_item(Item=demo_customer)
                self.print_success("Demo Customer created!")
                self.print_info("Customer ID: CUST001")
                self.print_info("Password: customer123")
            else:
                self.print_info("Demo customer already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo customer: {str(e)}")
            
    def show_main_menu(self):
        """Show Customer Portal main menu"""
        while True:
            self.clear_screen()
            self.print_header("CUSTOMER PORTAL DASHBOARD")
            
            if self.current_customer:
                print(f"👤 Customer: {self.current_customer.get('name', 'Unknown')}")
                print(f"🆔 Customer ID: {self.customer_id}")
                print(f"📧 Email: {self.current_customer.get('email', 'Unknown')}")
                print(f"📅 Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📋 Available Operations:")
            print("1. 🛒 Order Management")
            print("2. 📦 Order Tracking")
            print("3. 💳 Payment Management")
            print("4. 📝 Feedback & Reviews")
            print("5. 👤 Profile Management")
            print("6. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-6): ").strip()
            
            if choice == '1':
                self.order_management_menu()
            elif choice == '2':
                self.order_tracking_menu()
            elif choice == '3':
                self.payment_management_menu()
            elif choice == '4':
                self.feedback_reviews_menu()
            elif choice == '5':
                self.profile_management_menu()
            elif choice == '6':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Customer Portal!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def order_management_menu(self):
        """Order Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER MANAGEMENT")
            print("1. 🛒 Browse Products")
            print("2. 📋 Place New Order")
            print("3. 📦 View Order History")
            print("4. 🔄 Reorder")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.browse_products()
            elif choice == '2':
                self.place_new_order()
            elif choice == '3':
                self.view_order_history()
            elif choice == '4':
                self.reorder()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def browse_products(self):
        """Browse available products"""
        self.clear_screen()
        self.print_header("BROWSE PRODUCTS")
        
        try:
            # Get available products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products available.")
                input("Press Enter to continue...")
                return
                
            print(f"🛒 Available Products ({len(products)} products):")
            print("-" * 100)
            print(f"{'Product ID':<15} {'Name':<25} {'Category':<15} {'Price':<12} {'Stock':<8}")
            print("-" * 100)
            
            for product in products:
                print(f"{product.get('productId', 'N/A'):<15} "
                      f"{product.get('name', 'N/A')[:24]:<25} "
                      f"{product.get('category', 'N/A'):<15} "
                      f"{product.get('sellingPrice', 0):<12} "
                      f"{product.get('minStock', 0):<8}")
                      
            print("-" * 100)
            
            # Show product categories
            categories = set(product.get('category', 'Unknown') for product in products)
            print(f"\n🏷️ Available Categories:")
            for category in categories:
                category_products = [p for p in products if p.get('category') == category]
                print(f"  • {category}: {len(category_products)} products")
                
            # Show price ranges
            prices = [product.get('sellingPrice', 0) for product in products]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                print(f"\n💰 Price Range:")
                print(f"  • Minimum: {min_price}")
                print(f"  • Maximum: {max_price}")
                print(f"  • Average: {avg_price:.2f}")
                
        except Exception as e:
            self.print_error(f"Error browsing products: {str(e)}")
            
        input("Press Enter to continue...")
        
    def place_new_order(self):
        """Place a new order"""
        self.clear_screen()
        self.print_header("PLACE NEW ORDER")
        
        try:
            # Get available products
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products available for ordering.")
                input("Press Enter to continue...")
                return
                
            print("🛒 Available Products:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product.get('name', 'N/A')} - {product.get('sellingPrice', 0)} - {product.get('category', 'N/A')}")
                
            # Select products
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
                            price = Decimal(str(selected_product.get('sellingPrice', 0)))
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
                
            # Order summary
            print(f"\n📋 Order Summary:")
            print("-" * 60)
            for item in selected_products:
                print(f"  • {item['name']} x{item['quantity']} = {item['total']}")
            print("-" * 60)
            print(f"💰 Total Amount: {total_amount}")
            
            # Delivery details
            delivery_address = input("\n📍 Delivery Address (or press Enter for default): ").strip()
            if not delivery_address:
                delivery_address = self.current_customer.get('address', 'Default Address')
                
            delivery_date = input("📅 Preferred Delivery Date (YYYY-MM-DD): ").strip()
            if not delivery_date:
                delivery_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
                
            # Confirm order
            confirm = input("\n❓ Confirm order? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                # Create order
                order_id = f'ORD-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
                
                order_item = {
                    'orderId': order_id,
                    'customerId': self.customer_id,
                    'orderDate': datetime.now().isoformat(),
                    'deliveryAddress': delivery_address,
                    'deliveryDate': delivery_date,
                    'totalAmount': total_amount,
                    'status': 'PENDING',
                    'items': selected_products,
                    'paymentMethod': 'Cash on Delivery',
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                self.orders_table.put_item(Item=order_item)
                
                # Log audit
                self.log_audit('ORDER_PLACED', order_id, f"Customer {self.customer_id} placed order for {total_amount}")
                
                self.print_success(f"Order placed successfully!")
                self.print_info(f"Order ID: {order_id}")
                self.print_info(f"Total Amount: {total_amount}")
                self.print_info(f"Expected Delivery: {delivery_date}")
                
            else:
                self.print_info("Order cancelled.")
                
        except Exception as e:
            self.print_error(f"Error placing order: {str(e)}")
            
        input("Press Enter to continue...")
        
    def order_tracking_menu(self):
        """Order Tracking Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER TRACKING")
            print("1. 📦 Track Order Status")
            print("2. 📍 View Delivery Updates")
            print("3. 📱 Receive Notifications")
            print("4. 📊 Order Analytics")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.track_order_status()
            elif choice == '2':
                self.view_delivery_updates()
            elif choice == '3':
                self.receive_notifications()
            elif choice == '4':
                self.order_analytics()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def payment_management_menu(self):
        """Payment Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PAYMENT MANAGEMENT")
            print("1. 💳 Make Online Payment")
            print("2. 📊 View Payment History")
            print("3. 📄 Download Invoices")
            print("4. 💰 Payment Methods")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.make_online_payment()
            elif choice == '2':
                self.view_payment_history()
            elif choice == '3':
                self.download_invoices()
            elif choice == '4':
                self.payment_methods()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def feedback_reviews_menu(self):
        """Feedback & Reviews Operations"""
        while True:
            self.clear_screen()
            self.print_header("FEEDBACK & REVIEWS")
            print("1. ⭐ Rate Delivery Experience")
            print("2. 📝 Review Products")
            print("3. 🐛 Report Issues")
            print("4. 💬 Submit Feedback")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.rate_delivery_experience()
            elif choice == '2':
                self.review_products()
            elif choice == '3':
                self.report_issues()
            elif choice == '4':
                self.submit_feedback()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def profile_management_menu(self):
        """Profile Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("PROFILE MANAGEMENT")
            print("1. 👤 Update Profile")
            print("2. 📍 Manage Addresses")
            print("3. 🔔 Notification Settings")
            print("4. 🔒 Security Settings")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.update_profile()
            elif choice == '2':
                self.manage_addresses()
            elif choice == '3':
                self.notification_settings()
            elif choice == '4':
                self.security_settings()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    # Placeholder methods for other operations
    def view_order_history(self):
        self.clear_screen()
        self.print_header("VIEW ORDER HISTORY")
        
        try:
            # Get orders for this customer
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            customer_orders = [order for order in orders if order.get('customerId') == self.customer_id]
            
            if not customer_orders:
                self.print_info("No order history found.")
                input("Press Enter to continue...")
                return
                
            print(f"📦 Your Order History ({len(customer_orders)} orders):")
            print("-" * 100)
            print(f"{'Order ID':<20} {'Order Date':<15} {'Amount':<12} {'Status':<15} {'Delivery Date':<15}")
            print("-" * 100)
            
            for order in customer_orders:
                print(f"{order.get('orderId', 'N/A'):<20} "
                      f"{order.get('orderDate', 'N/A')[:10]:<15} "
                      f"{order.get('totalAmount', 0):<12} "
                      f"{order.get('status', 'N/A'):<15} "
                      f"{order.get('deliveryDate', 'N/A')[:10]:<15}")
                      
            print("-" * 100)
            
            # Summary statistics
            total_spent = sum(Decimal(str(order.get('totalAmount', 0))) for order in customer_orders)
            completed_orders = [o for o in customer_orders if o.get('status') == 'COMPLETED']
            
            print(f"\n📊 Order Summary:")
            print(f"  • Total Orders: {len(customer_orders)}")
            print(f"  • Completed Orders: {len(completed_orders)}")
            print(f"  • Total Spent: {total_spent}")
            print(f"  • Average Order Value: {total_spent / len(customer_orders) if customer_orders else 0:.2f}")
            
        except Exception as e:
            self.print_error(f"Error viewing order history: {str(e)}")
            
        input("Press Enter to continue...")
        
    def reorder(self):
        self.clear_screen()
        self.print_header("REORDER")
        self.print_info("Reorder functionality will be implemented.")
        input("Press Enter to continue...")
        
    def track_order_status(self):
        self.clear_screen()
        self.print_header("TRACK ORDER STATUS")
        self.print_info("Order status tracking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_delivery_updates(self):
        self.clear_screen()
        self.print_header("VIEW DELIVERY UPDATES")
        self.print_info("Delivery updates viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def receive_notifications(self):
        self.clear_screen()
        self.print_header("RECEIVE NOTIFICATIONS")
        self.print_info("Notification receiving functionality will be implemented.")
        input("Press Enter to continue...")
        
    def order_analytics(self):
        self.clear_screen()
        self.print_header("ORDER ANALYTICS")
        self.print_info("Order analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def make_online_payment(self):
        self.clear_screen()
        self.print_header("MAKE ONLINE PAYMENT")
        self.print_info("Online payment functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_payment_history(self):
        self.clear_screen()
        self.print_header("VIEW PAYMENT HISTORY")
        self.print_info("Payment history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def download_invoices(self):
        self.clear_screen()
        self.print_header("DOWNLOAD INVOICES")
        self.print_info("Invoice download functionality will be implemented.")
        input("Press Enter to continue...")
        
    def payment_methods(self):
        self.clear_screen()
        self.print_header("PAYMENT METHODS")
        self.print_info("Payment methods management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def rate_delivery_experience(self):
        self.clear_screen()
        self.print_header("RATE DELIVERY EXPERIENCE")
        self.print_info("Delivery experience rating functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_products(self):
        self.clear_screen()
        self.print_header("REVIEW PRODUCTS")
        self.print_info("Product review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def report_issues(self):
        self.clear_screen()
        self.print_header("REPORT ISSUES")
        self.print_info("Issue reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def submit_feedback(self):
        self.clear_screen()
        self.print_header("SUBMIT FEEDBACK")
        self.print_info("Feedback submission functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_profile(self):
        self.clear_screen()
        self.print_header("UPDATE PROFILE")
        self.print_info("Profile update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def manage_addresses(self):
        self.clear_screen()
        self.print_header("MANAGE ADDRESSES")
        self.print_info("Address management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def notification_settings(self):
        self.clear_screen()
        self.print_header("NOTIFICATION SETTINGS")
        self.print_info("Notification settings functionality will be implemented.")
        input("Press Enter to continue...")
        
    def security_settings(self):
        self.clear_screen()
        self.print_header("SECURITY SETTINGS")
        self.print_info("Security settings functionality will be implemented.")
        input("Press Enter to continue...")
        
    def logout(self):
        """Logout current customer"""
        if self.current_customer:
            self.print_success(f"Goodbye, {self.current_customer.get('name', 'Customer')}!")
            self.current_customer = None
            self.customer_id = None
        else:
            self.print_info("No customer logged in")
            
    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': f'CUSTOMER_{self.customer_id}',
                'action': action,
                'entityId': entity_id,
                'details': details,
                'ipAddress': '127.0.0.1',
                'userAgent': 'CustomerPortal-Standalone',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")
            
    def run(self):
        """Main run method"""
        try:
            # Create demo customer if needed
            self.create_demo_customer()
            
            # Authenticate customer
            if not self.authenticate_customer():
                self.print_error("Authentication failed. Exiting.")
                sys.exit(1)
                
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\n⚠️  System interrupted by user")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
        finally:
            self.print_success("Thank you for using the Customer Portal!")


def main():
    """Main entry point"""
    customer_portal = CustomerPortalStandalone()
    customer_portal.run()


if __name__ == '__main__':
    main() 