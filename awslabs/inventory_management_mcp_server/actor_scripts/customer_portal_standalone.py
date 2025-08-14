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
        print(f"[PORTAL] {title}")
        print("=" * 80)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"[SUCCESS] {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"[ERROR] {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"[INFO] {message}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"[WARNING] {message}")
        
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
            
    def authenticate_customer(self) -> bool:
        """Authenticate customer login"""
        self.clear_screen()
        self.print_header("CUSTOMER PORTAL - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your customer credentials:")
        print("[NOTE] Demo credentials: CUST001 / customer123")
        
        customer_id = input("\n[USER] Customer ID: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
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
                'address': '123 Main Street, Andheri West, Mumbai, Maharashtra - 400001',
                'pincode': '400001',
                'city': 'Mumbai',
                'state': 'Maharashtra',
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
                print(f"[USER] Customer: {self.current_customer.get('name', 'Unknown')}")
                print(f"[ID] Customer ID: {self.customer_id}")
                print(f"[EMAIL] Email: {self.current_customer.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. [CART] Order Management")
            print("2. [ORDER] Order Tracking")
            print("3. [PAYMENT] Payment Management")
            print("4. [GENERATE] Feedback & Reviews")
            print("5. [USER] Profile Management")
            print("6. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-6): ").strip()
            
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
            print("1. [CART] Browse Products")
            print("2. [CLIPBOARD] Place New Order")
            print("3. [ORDER] View Order History")
            print("4. [FLOW] Reorder")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
            print(f"[CART] Available Products ({len(products)} products):")
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
            print(f"\n[CATEGORY] Available Categories:")
            for category in categories:
                category_products = [p for p in products if p.get('category') == category]
                print(f"  • {category}: {len(category_products)} products")
                
            # Show price ranges
            prices = [product.get('sellingPrice', 0) for product in products]
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                print(f"\n[PRICE] Price Range:")
                print(f"  • Minimum: {min_price}")
                print(f"  • Maximum: {max_price}")
                print(f"  • Average: {avg_price:.2f}")
                
        except Exception as e:
            self.print_error(f"Error browsing products: {str(e)}")
            
        input("Press Enter to continue...")
        
    def place_new_order(self):
        """Place a new order with comprehensive product selection and delivery options"""
        self.clear_screen()
        self.print_header("PLACE NEW ORDER")
        
        try:
            # Step 1: Browse and select products with variants
            selected_products = self.enhanced_product_selection()
            
            if not selected_products:
                self.print_info("No products selected.")
                input("Press Enter to continue...")
                return
                
            # Step 2: Address selection and delivery time slots
            delivery_info = self.select_delivery_address_and_slot()
            
            if not delivery_info:
                self.print_info("Delivery setup cancelled.")
                input("Press Enter to continue...")
                return
                
            # Step 3: Payment method selection
            payment_method = self.select_payment_method()
            
            if not payment_method:
                self.print_info("Payment method selection cancelled.")
                input("Press Enter to continue...")
                return
                
            # Step 4: Order confirmation and placement
            self.confirm_and_place_order(selected_products, delivery_info, payment_method)
                
        except Exception as e:
            self.print_error(f"Error placing order: {str(e)}")
            
        input("Press Enter to continue...")
        
    def enhanced_product_selection(self):
        """Enhanced product browsing with variants and detailed selection"""
        self.clear_screen()
        self.print_header("[CART] PRODUCT SELECTION")
        
        selected_products = []
        total_amount = Decimal('0')
        
        while True:
            print("\n[SHOPPING] Product Browsing Options:")
            print("1. [CATEGORY] Browse by Category")
            print("2. [AUDIT] Search Products")
            print("3. [VIEW] View All Products")
            print("4. [CART] View Shopping Cart")
            print("5. [SUCCESS] Proceed to Checkout")
            print("6. [ERROR] Cancel Order")
            
            choice = input("\n[TARGET] Select option (1-6): ").strip()
            
            if choice == '1':
                product = self.browse_by_category()
                if product:
                    item = self.select_product_variant_and_quantity(product)
                    if item:
                        selected_products.append(item)
                        total_amount += item['total']
                        self.print_success(f"[SUCCESS] Added to cart: {item['name']} x{item['quantity']} = ₹{item['total']}")
                        
            elif choice == '2':
                product = self.search_products()
                if product:
                    item = self.select_product_variant_and_quantity(product)
                    if item:
                        selected_products.append(item)
                        total_amount += item['total']
                        self.print_success(f"[SUCCESS] Added to cart: {item['name']} x{item['quantity']} = ₹{item['total']}")
                        
            elif choice == '3':
                product = self.view_all_products()
                if product:
                    item = self.select_product_variant_and_quantity(product)
                    if item:
                        selected_products.append(item)
                        total_amount += item['total']
                        self.print_success(f"[SUCCESS] Added to cart: {item['name']} x{item['quantity']} = ₹{item['total']}")
                        
            elif choice == '4':
                self.display_shopping_cart(selected_products, total_amount)
                
            elif choice == '5':
                if selected_products:
                    return selected_products
                else:
                    self.print_error("[ERROR] Your cart is empty. Please add some products first.")
                    
            elif choice == '6':
                return None
                
            else:
                self.print_error("[ERROR] Invalid choice. Please try again.")
                
    def browse_by_category(self):
        """Browse products by category"""
        self.clear_screen()
        self.print_header("[CATEGORY] BROWSE BY CATEGORY")
        
        try:
            # Get all products to extract categories
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products available.")
                return None
                
            # Get unique categories
            categories = list(set(product.get('category', 'Uncategorized') for product in products))
            categories.sort()
            
            print("[CLIPBOARD] Available Categories:")
            print("-" * 50)
            for i, category in enumerate(categories, 1):
                category_products = [p for p in products if p.get('category') == category]
                print(f"{i:2d}. {category:<20} ({len(category_products)} products)")
            print("-" * 50)
            
            choice = input(f"\n[TARGET] Select category (1-{len(categories)}): ").strip()
            
            try:
                category_index = int(choice) - 1
                if 0 <= category_index < len(categories):
                    selected_category = categories[category_index]
                    return self.display_category_products(selected_category, products)
                else:
                    self.print_error("Invalid category selection.")
                    return None
            except ValueError:
                self.print_error("Invalid category number.")
                return None
                
        except Exception as e:
            self.print_error(f"Error browsing categories: {str(e)}")
            return None
            
    def display_category_products(self, category, all_products):
        """Display products in selected category"""
        self.clear_screen()
        self.print_header(f"[CATEGORY] CATEGORY: {category.upper()}")
        
        category_products = [p for p in all_products if p.get('category') == category]
        
        if not category_products:
            self.print_info(f"No products found in {category} category.")
            return None
            
        print(f"[ORDER] Products in {category} ({len(category_products)} items):")
        print("-" * 100)
        print(f"{'#':<3} {'Product Name':<30} {'Price':<12} {'Brand':<15} {'In Stock':<10}")
        print("-" * 100)
        
        for i, product in enumerate(category_products, 1):
            in_stock = "[SUCCESS] Yes" if product.get('minStock', 0) > 0 else "[ERROR] No"
            print(f"{i:<3} {product.get('name', 'N/A')[:29]:<30} "
                  f"₹{product.get('sellingPrice', 0):<11} "
                  f"{product.get('brand', 'N/A')[:14]:<15} "
                  f"{in_stock:<10}")
                  
        print("-" * 100)
        
        choice = input(f"\n[TARGET] Select product (1-{len(category_products)}) or 'back' to return: ").strip()
        
        if choice.lower() == 'back':
            return None
            
        try:
            product_index = int(choice) - 1
            if 0 <= product_index < len(category_products):
                return category_products[product_index]
            else:
                self.print_error("Invalid product selection.")
                return None
        except ValueError:
            self.print_error("Invalid product number.")
            return None
            
    def search_products(self):
        """Search products by name or keyword"""
        self.clear_screen()
        self.print_header("[AUDIT] SEARCH PRODUCTS")
        
        search_term = input("[AUDIT] Enter product name or keyword: ").strip()
        
        if not search_term:
            self.print_error("Search term cannot be empty.")
            return None
            
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            # Filter products based on search term
            matching_products = []
            search_lower = search_term.lower()
            
            for product in products:
                product_name = product.get('name', '').lower()
                product_category = product.get('category', '').lower()
                product_brand = product.get('brand', '').lower()
                
                if (search_lower in product_name or 
                    search_lower in product_category or 
                    search_lower in product_brand):
                    matching_products.append(product)
                    
            if not matching_products:
                self.print_info(f"No products found matching '{search_term}'.")
                return None
                
            print(f"[AUDIT] Search Results for '{search_term}' ({len(matching_products)} found):")
            print("-" * 100)
            print(f"{'#':<3} {'Product Name':<30} {'Category':<15} {'Price':<12} {'Brand':<15}")
            print("-" * 100)
            
            for i, product in enumerate(matching_products, 1):
                print(f"{i:<3} {product.get('name', 'N/A')[:29]:<30} "
                      f"{product.get('category', 'N/A')[:14]:<15} "
                      f"₹{product.get('sellingPrice', 0):<11} "
                      f"{product.get('brand', 'N/A')[:14]:<15}")
                      
            print("-" * 100)
            
            choice = input(f"\n[TARGET] Select product (1-{len(matching_products)}) or 'back' to return: ").strip()
            
            if choice.lower() == 'back':
                return None
                
            try:
                product_index = int(choice) - 1
                if 0 <= product_index < len(matching_products):
                    return matching_products[product_index]
                else:
                    self.print_error("Invalid product selection.")
                    return None
            except ValueError:
                self.print_error("Invalid product number.")
                return None
                
        except Exception as e:
            self.print_error(f"Error searching products: {str(e)}")
            return None
            
    def view_all_products(self):
        """View all available products"""
        self.clear_screen()
        self.print_header("[VIEW] ALL PRODUCTS")
        
        try:
            response = self.products_table.scan()
            products = response.get('Items', [])
            
            if not products:
                self.print_info("No products available.")
                return None
                
            # Sort products by category and name
            products.sort(key=lambda x: (x.get('category', ''), x.get('name', '')))
            
            print(f"[ORDER] All Products ({len(products)} items):")
            print("-" * 120)
            print(f"{'#':<3} {'Product Name':<30} {'Category':<15} {'Price':<12} {'Brand':<15} {'Stock':<10}")
            print("-" * 120)
            
            for i, product in enumerate(products, 1):
                stock_status = "[SUCCESS] Available" if product.get('minStock', 0) > 0 else "[ERROR] Out of Stock"
                print(f"{i:<3} {product.get('name', 'N/A')[:29]:<30} "
                      f"{product.get('category', 'N/A')[:14]:<15} "
                      f"₹{product.get('sellingPrice', 0):<11} "
                      f"{product.get('brand', 'N/A')[:14]:<15} "
                      f"{stock_status:<10}")
                      
            print("-" * 120)
            
            # Pagination for large product lists
            if len(products) > 20:
                self.print_info(f"[NOTE] Showing all {len(products)} products. Consider using search or category filter for easier browsing.")
                
            choice = input(f"\n[TARGET] Select product (1-{len(products)}) or 'back' to return: ").strip()
            
            if choice.lower() == 'back':
                return None
                
            try:
                product_index = int(choice) - 1
                if 0 <= product_index < len(products):
                    return products[product_index]
                else:
                    self.print_error("Invalid product selection.")
                    return None
            except ValueError:
                self.print_error("Invalid product number.")
                return None
                
        except Exception as e:
            self.print_error(f"Error viewing products: {str(e)}")
            return None
            
    def select_product_variant_and_quantity(self, product):
        """Select product variants and quantity"""
        self.clear_screen()
        self.print_header(f"[ORDER] {product.get('name', 'Unknown Product')}")
        
        # Display product details
        print("[CLIPBOARD] Product Information:")
        print("-" * 60)
        print(f"[CATEGORY] Name: {product.get('name', 'N/A')}")
        print(f"[ACCOUNT] Brand: {product.get('brand', 'N/A')}")
        print(f"[CATEGORY] Category: {product.get('category', 'N/A')}")
        print(f"[PRICE] Price: ₹{product.get('sellingPrice', 0)}")
        print(f"[GENERATE] Description: {product.get('description', 'No description available')}")
        print("-" * 60)
        
        # Check for variants
        variants = product.get('variants', {})
        selected_variant = {}
        
        if variants:
            print("\n[VARIANT] Available Variants:")
            
            # Size variants
            if 'sizes' in variants and variants['sizes']:
                print(f"[SIZE] Sizes: {', '.join(variants['sizes'])}")
                size_choice = input("[SIZE] Select size (or press Enter for default): ").strip()
                if size_choice and size_choice in variants['sizes']:
                    selected_variant['size'] = size_choice
                elif variants['sizes']:
                    selected_variant['size'] = variants['sizes'][0]  # Default to first size
                    
            # Color variants
            if 'colors' in variants and variants['colors']:
                print(f"[COLOR] Colors: {', '.join(variants['colors'])}")
                color_choice = input("[COLOR] Select color (or press Enter for default): ").strip()
                if color_choice and color_choice in variants['colors']:
                    selected_variant['color'] = color_choice
                elif variants['colors']:
                    selected_variant['color'] = variants['colors'][0]  # Default to first color
                    
            # Weight variants
            if 'weights' in variants and variants['weights']:
                print(f"[WEIGHT] Weights: {', '.join(variants['weights'])}")
                weight_choice = input("[WEIGHT] Select weight (or press Enter for default): ").strip()
                if weight_choice and weight_choice in variants['weights']:
                    selected_variant['weight'] = weight_choice
                elif variants['weights']:
                    selected_variant['weight'] = variants['weights'][0]  # Default to first weight
                    
        # Quantity selection
        print(f"\n[ORDER] Quantity Selection:")
        print(f"[NOTE] Available stock: {product.get('minStock', 0)} units")
        
        while True:
            try:
                quantity_input = input("[ORDER] Enter quantity: ").strip()
                quantity = int(quantity_input)
                
                if quantity <= 0:
                    self.print_error("[ERROR] Quantity must be greater than 0.")
                    continue
                    
                available_stock = product.get('minStock', 0)
                if quantity > available_stock:
                    self.print_error(f"[ERROR] Only {available_stock} units available.")
                    continue
                    
                break
                
            except ValueError:
                self.print_error("[ERROR] Please enter a valid number.")
                
        # Calculate total price
        unit_price = Decimal(str(product.get('sellingPrice', 0)))
        total_price = unit_price * quantity
        
        # Display selection summary
        print(f"\n[CLIPBOARD] Selection Summary:")
        print("-" * 40)
        print(f"[ORDER] Product: {product.get('name')}")
        if selected_variant:
            for key, value in selected_variant.items():
                print(f"[VARIANT] {key.capitalize()}: {value}")
        print(f"[TRACK] Quantity: {quantity}")
        print(f"[PRICE] Unit Price: ₹{unit_price}")
        print(f"[PRICE] Total Price: ₹{total_price}")
        print("-" * 40)
        
        confirm = input("\n[CONFIRM] Add to cart? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            # Create cart item
            cart_item = {
                'productId': product['productId'],
                'name': product.get('name'),
                'unitPrice': unit_price,
                'quantity': quantity,
                'total': total_price,
                'variants': selected_variant
            }
            
            return cart_item
        else:
            return None
            
    def display_shopping_cart(self, selected_products, total_amount):
        """Display current shopping cart"""
        self.clear_screen()
        self.print_header("[CART] SHOPPING CART")
        
        if not selected_products:
            self.print_info("[CART] Your cart is empty.")
            input("Press Enter to continue...")
            return
            
        print(f"[SHOPPING] Cart Contents ({len(selected_products)} items):")
        print("-" * 100)
        print(f"{'#':<3} {'Product':<25} {'Variants':<20} {'Qty':<5} {'Unit Price':<12} {'Total':<12}")
        print("-" * 100)
        
        for i, item in enumerate(selected_products, 1):
            variants_str = ""
            if item.get('variants'):
                variant_parts = []
                for key, value in item['variants'].items():
                    variant_parts.append(f"{key}:{value}")
                variants_str = ", ".join(variant_parts)
                
            print(f"{i:<3} {item['name'][:24]:<25} {variants_str[:19]:<20} "
                  f"{item['quantity']:<5} ₹{item['unitPrice']:<11} ₹{item['total']:<11}")
                  
        print("-" * 100)
        print(f"[PRICE] Total Amount: ₹{sum(item['total'] for item in selected_products)}")
        print("-" * 100)
        
        print("\n[CART] Cart Management:")
        print("1. [ADD] Continue Shopping")
        print("2. [DELETE] Remove Item")
        print("3. [FLOW] Update Quantity")
        print("4. [CLEAR] Clear Cart")
        
        choice = input("\n[TARGET] Select option (1-4) or Enter to continue: ").strip()
        
        if choice == '2':
            self.remove_cart_item(selected_products)
        elif choice == '3':
            self.update_cart_quantity(selected_products)
        elif choice == '4':
            if input("[CONFIRM] Clear entire cart? (yes/no): ").strip().lower() == 'yes':
                selected_products.clear()
                self.print_success("[CLEAR] Cart cleared!")
                
        input("Press Enter to continue...")
        
    def remove_cart_item(self, selected_products):
        """Remove item from cart"""
        if not selected_products:
            return
            
        try:
            item_choice = input(f"[DELETE] Remove item number (1-{len(selected_products)}): ").strip()
            item_index = int(item_choice) - 1
            
            if 0 <= item_index < len(selected_products):
                removed_item = selected_products.pop(item_index)
                self.print_success(f"[DELETE] Removed: {removed_item['name']}")
            else:
                self.print_error("[ERROR] Invalid item number.")
                
        except ValueError:
            self.print_error("[ERROR] Invalid item number.")
            
    def update_cart_quantity(self, selected_products):
        """Update quantity of cart item"""
        if not selected_products:
            return
            
        try:
            item_choice = input(f"[FLOW] Update item number (1-{len(selected_products)}): ").strip()
            item_index = int(item_choice) - 1
            
            if 0 <= item_index < len(selected_products):
                item = selected_products[item_index]
                
                new_qty_input = input(f"[ORDER] New quantity for {item['name']} (current: {item['quantity']}): ").strip()
                new_qty = int(new_qty_input)
                
                if new_qty > 0:
                    item['quantity'] = new_qty
                    item['total'] = item['unitPrice'] * new_qty
                    self.print_success(f"[FLOW] Updated: {item['name']} quantity to {new_qty}")
                else:
                    self.print_error("[ERROR] Quantity must be greater than 0.")
            else:
                self.print_error("[ERROR] Invalid item number.")
                
        except ValueError:
            self.print_error("[ERROR] Invalid input.")
            
    def select_delivery_address_and_slot(self):
        """Select delivery address and time slot based on pincode"""
        self.clear_screen()
        self.print_header("[ADDRESS] DELIVERY ADDRESS & TIME SLOT")
        
        # Step 1: Address Selection
        print("[HOME] Address Selection:")
        print("1. [HOME] Use Default Address")
        print("2. [ADD] Add New Address")
        print("3. [CLIPBOARD] Select from Saved Addresses")
        
        address_choice = input("\n[TARGET] Select option (1-3): ").strip()
        
        selected_address = None
        
        if address_choice == '1':
            # Use default address
            default_address = self.current_customer.get('address', '')
            default_pincode = self.current_customer.get('pincode', '')
            
            if default_address and default_pincode:
                selected_address = {
                    'address': default_address,
                    'pincode': default_pincode,
                    'type': 'Default'
                }
                print(f"[HOME] Using default address: {default_address}")
                print(f"[POSTAL] Pincode: {default_pincode}")
            else:
                self.print_error("[ERROR] No default address found. Please add an address.")
                return None
                
        elif address_choice == '2':
            # Add new address
            selected_address = self.add_new_delivery_address()
            if not selected_address:
                return None
                
        elif address_choice == '3':
            # Select from saved addresses
            selected_address = self.select_saved_address()
            if not selected_address:
                return None
        else:
            self.print_error("[ERROR] Invalid address option.")
            return None
            
        # Step 2: Time Slot Selection based on pincode
        available_slots = self.get_delivery_slots_by_pincode(selected_address['pincode'])
        
        if not available_slots:
            self.print_error(f"[ERROR] No delivery slots available for pincode {selected_address['pincode']}")
            return None
            
        selected_slot = self.select_delivery_time_slot(available_slots)
        
        if not selected_slot:
            return None
            
        # Combine address and slot information
        delivery_info = {
            'address': selected_address['address'],
            'pincode': selected_address['pincode'],
            'addressType': selected_address['type'],
            'deliveryDate': selected_slot['date'],
            'timeSlot': selected_slot['timeSlot'],
            'slotId': selected_slot['slotId'],
            'deliveryFee': selected_slot.get('deliveryFee', 0)
        }
        
        return delivery_info
        
    def add_new_delivery_address(self):
        """Add a new delivery address"""
        print("\n[ADD] Add New Delivery Address:")
        
        # Collect address information
        house_no = input("[HOME] House/Flat Number: ").strip()
        street = input("🛣️ Street/Area: ").strip()
        city = input("🏙️ City: ").strip()
        state = input("🗾 State: ").strip()
        pincode = input("[POSTAL] Pincode: ").strip()
        
        if not all([house_no, street, city, state, pincode]):
            self.print_error("[ERROR] All address fields are required.")
            return None
            
        # Validate pincode
        if not pincode.isdigit() or len(pincode) != 6:
            self.print_error("[ERROR] Invalid pincode. Please enter a 6-digit pincode.")
            return None
            
        # Combine address
        full_address = f"{house_no}, {street}, {city}, {state} - {pincode}"
        
        print(f"\n[ADDRESS] New Address: {full_address}")
        confirm = input("[CONFIRM] Confirm this address? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            return {
                'address': full_address,
                'pincode': pincode,
                'type': 'New'
            }
        else:
            return None
            
    def select_saved_address(self):
        """Select from saved addresses (simulated)"""
        # In a real system, this would fetch from customer's saved addresses
        saved_addresses = [
            {'address': 'Home: 123 Main Street, Mumbai, Maharashtra - 400001', 'pincode': '400001', 'type': 'Home'},
            {'address': 'Office: 456 Business District, Mumbai, Maharashtra - 400051', 'pincode': '400051', 'type': 'Office'},
            {'address': 'Parents: 789 Residential Area, Pune, Maharashtra - 411001', 'pincode': '411001', 'type': 'Family'}
        ]
        
        if not saved_addresses:
            self.print_info("[CLIPBOARD] No saved addresses found.")
            return None
            
        print("\n[CLIPBOARD] Saved Addresses:")
        print("-" * 80)
        for i, addr in enumerate(saved_addresses, 1):
            print(f"{i}. {addr['type']}: {addr['address']}")
        print("-" * 80)
        
        try:
            choice = input(f"\n[TARGET] Select address (1-{len(saved_addresses)}): ").strip()
            addr_index = int(choice) - 1
            
            if 0 <= addr_index < len(saved_addresses):
                return saved_addresses[addr_index]
            else:
                self.print_error("[ERROR] Invalid address selection.")
                return None
                
        except ValueError:
            self.print_error("[ERROR] Invalid address number.")
            return None
            
    def get_delivery_slots_by_pincode(self, pincode):
        """Get available delivery slots based on pincode"""
        # Simulate pincode-based slot availability
        pincode_zones = {
            # Metro cities - More slots available
            '400001': 'Metro', '400051': 'Metro', '110001': 'Metro', '560001': 'Metro',
            '600001': 'Metro', '700001': 'Metro', '500001': 'Metro',
            
            # Tier-1 cities - Limited slots
            '411001': 'Tier1', '302001': 'Tier1', '380001': 'Tier1', '452001': 'Tier1',
            
            # Tier-2 cities - Few slots
            '440001': 'Tier2', '462001': 'Tier2', '781001': 'Tier2'
        }
        
        zone = pincode_zones.get(pincode, 'Remote')
        
        # Generate slots based on zone
        slots = []
        today = datetime.now()
        
        if zone == 'Metro':
            # Metro: Same day, next day, and day after with multiple time slots
            for day_offset in range(0, 3):
                delivery_date = today + timedelta(days=day_offset)
                date_str = delivery_date.strftime('%Y-%m-%d')
                day_name = delivery_date.strftime('%A')
                
                if day_offset == 0:  # Today
                    # Limited slots for today (only if before 2 PM)
                    if today.hour < 14:
                        slots.extend([
                            {'slotId': f'{date_str}-evening', 'date': date_str, 'timeSlot': '6:00 PM - 9:00 PM', 'deliveryFee': 0, 'type': 'Same Day'},
                        ])
                else:
                    # Full slots for future days
                    slots.extend([
                        {'slotId': f'{date_str}-morning', 'date': date_str, 'timeSlot': '9:00 AM - 12:00 PM', 'deliveryFee': 0, 'type': 'Standard'},
                        {'slotId': f'{date_str}-afternoon', 'date': date_str, 'timeSlot': '2:00 PM - 5:00 PM', 'deliveryFee': 0, 'type': 'Standard'},
                        {'slotId': f'{date_str}-evening', 'date': date_str, 'timeSlot': '6:00 PM - 9:00 PM', 'deliveryFee': 0, 'type': 'Standard'},
                    ])
                    
        elif zone == 'Tier1':
            # Tier-1: Next day and day after with limited slots
            for day_offset in range(1, 4):
                delivery_date = today + timedelta(days=day_offset)
                date_str = delivery_date.strftime('%Y-%m-%d')
                
                slots.extend([
                    {'slotId': f'{date_str}-morning', 'date': date_str, 'timeSlot': '10:00 AM - 1:00 PM', 'deliveryFee': 25, 'type': 'Standard'},
                    {'slotId': f'{date_str}-evening', 'date': date_str, 'timeSlot': '5:00 PM - 8:00 PM', 'deliveryFee': 25, 'type': 'Standard'},
                ])
                
        elif zone == 'Tier2':
            # Tier-2: 2-5 days with basic slots
            for day_offset in range(2, 6):
                delivery_date = today + timedelta(days=day_offset)
                date_str = delivery_date.strftime('%Y-%m-%d')
                
                slots.append({'slotId': f'{date_str}-standard', 'date': date_str, 'timeSlot': '10:00 AM - 6:00 PM', 'deliveryFee': 50, 'type': 'Standard'})
                
        else:
            # Remote: 5-7 days with single slot
            for day_offset in range(5, 8):
                delivery_date = today + timedelta(days=day_offset)
                date_str = delivery_date.strftime('%Y-%m-%d')
                
                slots.append({'slotId': f'{date_str}-standard', 'date': date_str, 'timeSlot': '9:00 AM - 6:00 PM', 'deliveryFee': 100, 'type': 'Remote'})
                
        return slots
        
    def select_delivery_time_slot(self, available_slots):
        """Select delivery time slot"""
        self.clear_screen()
        self.print_header("⏰ DELIVERY TIME SLOT SELECTION")
        
        if not available_slots:
            self.print_info("[ERROR] No delivery slots available.")
            return None
            
        print("[DATE] Available Delivery Slots:")
        print("-" * 90)
        print(f"{'#':<3} {'Date':<12} {'Day':<10} {'Time Slot':<20} {'Type':<12} {'Delivery Fee':<12}")
        print("-" * 90)
        
        for i, slot in enumerate(available_slots, 1):
            date_obj = datetime.strptime(slot['date'], '%Y-%m-%d')
            day_name = date_obj.strftime('%A')
            fee_str = f"₹{slot['deliveryFee']}" if slot['deliveryFee'] > 0 else "Free"
            
            print(f"{i:<3} {slot['date']:<12} {day_name:<10} {slot['timeSlot']:<20} "
                  f"{slot['type']:<12} {fee_str:<12}")
                  
        print("-" * 90)
        
        try:
            choice = input(f"\n[TARGET] Select time slot (1-{len(available_slots)}): ").strip()
            slot_index = int(choice) - 1
            
            if 0 <= slot_index < len(available_slots):
                selected_slot = available_slots[slot_index]
                
                print(f"\n[SUCCESS] Selected Slot:")
                print(f"[DATE] Date: {selected_slot['date']}")
                print(f"⏰ Time: {selected_slot['timeSlot']}")
                print(f"[DELIVERY] Type: {selected_slot['type']}")
                print(f"[PRICE] Delivery Fee: ₹{selected_slot['deliveryFee']}")
                
                confirm = input("\n[CONFIRM] Confirm this slot? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    return selected_slot
                else:
                    return None
            else:
                self.print_error("[ERROR] Invalid slot selection.")
                return None
                
        except ValueError:
            self.print_error("[ERROR] Invalid slot number.")
            return None
            
    def select_payment_method(self):
        """Select payment method"""
        self.clear_screen()
        self.print_header("[PAYMENT] PAYMENT METHOD SELECTION")
        
        payment_methods = [
            {'id': 'cod', 'name': 'Cash on Delivery', 'description': 'Pay when order is delivered', 'fee': 0},
            {'id': 'upi', 'name': 'UPI Payment', 'description': 'PhonePe, GPay, Paytm, BHIM', 'fee': 0},
            {'id': 'card', 'name': 'Credit/Debit Card', 'description': 'Visa, Mastercard, RuPay', 'fee': 0},
            {'id': 'netbanking', 'name': 'Net Banking', 'description': 'Direct bank transfer', 'fee': 0},
            {'id': 'wallet', 'name': 'Digital Wallet', 'description': 'Paytm, PhonePe, Amazon Pay', 'fee': 0}
        ]
        
        print("[PAYMENT] Available Payment Methods:")
        print("-" * 80)
        print(f"{'#':<3} {'Method':<20} {'Description':<30} {'Fee':<10}")
        print("-" * 80)
        
        for i, method in enumerate(payment_methods, 1):
            fee_str = f"₹{method['fee']}" if method['fee'] > 0 else "Free"
            print(f"{i:<3} {method['name']:<20} {method['description']:<30} {fee_str:<10}")
            
        print("-" * 80)
        
        try:
            choice = input(f"\n[TARGET] Select payment method (1-{len(payment_methods)}): ").strip()
            method_index = int(choice) - 1
            
            if 0 <= method_index < len(payment_methods):
                selected_method = payment_methods[method_index]
                
                print(f"\n[SUCCESS] Selected Payment Method:")
                print(f"[PAYMENT] Method: {selected_method['name']}")
                print(f"[GENERATE] Description: {selected_method['description']}")
                print(f"[PRICE] Fee: ₹{selected_method['fee']}")
                
                # Additional processing for online payment methods
                if selected_method['id'] != 'cod':
                    print(f"\n[NOTE] Note: You will be redirected to secure payment gateway after order confirmation.")
                    
                confirm = input("\n[CONFIRM] Confirm this payment method? (yes/no): ").strip().lower()
                
                if confirm == 'yes':
                    return selected_method
                else:
                    return None
            else:
                self.print_error("[ERROR] Invalid payment method selection.")
                return None
                
        except ValueError:
            self.print_error("[ERROR] Invalid payment method number.")
            return None
            
    def confirm_and_place_order(self, selected_products, delivery_info, payment_method):
        """Final order confirmation and placement"""
        self.clear_screen()
        self.print_header("[CLIPBOARD] ORDER CONFIRMATION")
        
        # Calculate totals
        subtotal = sum(item['total'] for item in selected_products)
        delivery_fee = Decimal(str(delivery_info.get('deliveryFee', 0)))
        payment_fee = Decimal(str(payment_method.get('fee', 0)))
        total_amount = subtotal + delivery_fee + payment_fee
        
        # Display comprehensive order summary
        print("[SHOPPING] ORDER SUMMARY")
        print("=" * 80)
        
        # Products
        print("\n[ORDER] Items:")
        print("-" * 80)
        for i, item in enumerate(selected_products, 1):
            variants_str = ""
            if item.get('variants'):
                variant_parts = [f"{k}:{v}" for k, v in item['variants'].items()]
                variants_str = f" ({', '.join(variant_parts)})"
                
            print(f"{i}. {item['name']}{variants_str}")
            print(f"   Quantity: {item['quantity']} × ₹{item['unitPrice']} = ₹{item['total']}")
            
        # Delivery Info
        print(f"\n[DELIVERY] Delivery Information:")
        print("-" * 80)
        print(f"[ADDRESS] Address: {delivery_info['address']}")
        print(f"[POSTAL] Pincode: {delivery_info['pincode']}")
        print(f"[DATE] Date: {delivery_info['deliveryDate']}")
        print(f"⏰ Time Slot: {delivery_info['timeSlot']}")
        
        # Payment Info
        print(f"\n[PAYMENT] Payment Information:")
        print("-" * 80)
        print(f"[PAYMENT] Method: {payment_method['name']}")
        print(f"[GENERATE] Description: {payment_method['description']}")
        
        # Cost Breakdown
        print(f"\n[PRICE] Cost Breakdown:")
        print("-" * 80)
        print(f"Subtotal:      ₹{subtotal}")
        print(f"Delivery Fee:  ₹{delivery_fee}")
        print(f"Payment Fee:   ₹{payment_fee}")
        print("-" * 30)
        print(f"TOTAL:         ₹{total_amount}")
        print("=" * 80)
        
        # Final confirmation
        print(f"\n[CONFIRM] FINAL CONFIRMATION")
        print(f"[NOTE] By placing this order, you agree to our terms and conditions.")
        print(f"[NOTE] Order will be processed immediately after confirmation.")
        
        final_confirm = input(f"\n[TARGET] Place Order? (type 'CONFIRM' to proceed): ").strip()
        
        if final_confirm.upper() == 'CONFIRM':
            try:
                # Generate order ID
                order_id = f'ORD-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
                
                # Create order item
                order_item = {
                    'orderId': order_id,
                    'customerId': self.customer_id,
                    'orderDate': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'items': selected_products,
                    'subtotal': subtotal,
                    'deliveryFee': delivery_fee,
                    'paymentFee': payment_fee,
                    'totalAmount': total_amount,
                    'deliveryAddress': delivery_info['address'],
                    'pincode': delivery_info['pincode'],
                    'deliveryDate': delivery_info['deliveryDate'],
                    'timeSlot': delivery_info['timeSlot'],
                    'slotId': delivery_info['slotId'],
                    'paymentMethod': payment_method['name'],
                    'paymentId': payment_method['id'],
                    'status': 'CONFIRMED',
                    'orderType': 'CUSTOMER_PORTAL',
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                # Save order to database
                self.orders_table.put_item(Item=order_item)
                
                # Log audit
                self.log_audit('ORDER_PLACED', order_id, 
                              f"Customer {self.customer_id} placed order for ₹{total_amount} "
                              f"with {len(selected_products)} items")
                
                # Success message
                self.clear_screen()
                self.print_header("[SUCCESS] ORDER PLACED SUCCESSFULLY!")
                
                print("[SUMMARY] Congratulations! Your order has been placed successfully.")
                print("-" * 60)
                print(f"[CLIPBOARD] Order ID: {order_id}")
                print(f"[PRICE] Total Amount: ₹{total_amount}")
                print(f"[DATE] Delivery Date: {delivery_info['deliveryDate']}")
                print(f"⏰ Time Slot: {delivery_info['timeSlot']}")
                print(f"[PAYMENT] Payment Method: {payment_method['name']}")
                print("-" * 60)
                
                print(f"\n[EMAIL] Order confirmation will be sent to your email.")
                print(f"[MOBILE] You can track your order status in the Order Tracking section.")
                print(f"[HELP] For any queries, contact customer support with Order ID: {order_id}")
                
                if payment_method['id'] != 'cod':
                    print(f"\n[PAYMENT] Next Steps:")
                    print(f"   1. You will receive payment link via SMS/Email")
                    print(f"   2. Complete payment within 30 minutes")
                    print(f"   3. Order will be processed after successful payment")
                else:
                    print(f"\n[ORDER] Next Steps:")
                    print(f"   1. Order is being processed")
                    print(f"   2. You'll receive updates via SMS/Email")
                    print(f"   3. Keep cash ready for delivery")
                
                self.print_success("Thank you for shopping with us! [SHOPPING]")
                
            except Exception as e:
                self.print_error(f"[ERROR] Error placing order: {str(e)}")
                
        else:
            self.print_info("[ERROR] Order cancelled.")
        
    def order_tracking_menu(self):
        """Order Tracking Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER TRACKING")
            print("1. [ORDER] Track Order Status")
            print("2. [ADDRESS] View Delivery Updates")
            print("3. [MOBILE] Receive Notifications")
            print("4. [TRACK] Order Analytics")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [PAYMENT] Make Online Payment")
            print("2. [TRACK] View Payment History")
            print("3. 📄 Download Invoices")
            print("4. [PRICE] Payment Methods")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [RATING] Rate Delivery Experience")
            print("2. [GENERATE] Review Products")
            print("3. [BUG] Report Issues")
            print("4. [CHAT] Submit Feedback")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [USER] Update Profile")
            print("2. [ADDRESS] Manage Addresses")
            print("3. [NOTIFY] Notification Settings")
            print("4. [PASSWORD] Security Settings")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
            print(f"[ORDER] Your Order History ({len(customer_orders)} orders):")
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
            
            print(f"\n[TRACK] Order Summary:")
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
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
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