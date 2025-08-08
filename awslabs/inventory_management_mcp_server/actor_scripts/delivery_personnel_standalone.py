#!/usr/bin/env python3
# delivery_personnel_standalone.py
"""
Delivery Personnel/Rider Standalone Script
Run this script in a separate terminal window for Delivery Personnel operations.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional


class DeliveryPersonnelStandalone:
    """Standalone Delivery Personnel with Field Operations"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        self.deliveries_table = self.dynamodb.Table('InventoryManagement-Deliveries')
        self.riders_table = self.dynamodb.Table('InventoryManagement-Riders')
        self.cash_collections_table = self.dynamodb.Table('InventoryManagement-CashCollections')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
        self.current_user = None
        self.current_role = None
        self.current_rider_id = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"🛵 {title}")
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
        self.print_header("DELIVERY PERSONNEL - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your credentials:")
        print("💡 Demo credentials: rider / rider123")
        
        username = input("\n👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'DELIVERY_PERSONNEL':
            self.current_user = user
            self.current_role = user.get('role')
            self.current_rider_id = user.get('userId')  # Use userId as riderId
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Rider ID: {self.current_rider_id}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            self.print_error("Only Delivery Personnel role can access this system.")
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
        """Create demo delivery personnel user if not exists"""
        try:
            demo_user = {
                'userId': 'rider',
                'role': 'DELIVERY_PERSONNEL',
                'name': 'Amit Kumar',
                'email': 'amit.rider@company.com',
                'phone': '+919876543214',
                'password': 'rider123',
                'permissions': [
                    'RUNSHEET_VIEW', 'ORDER_DELIVERY', 'CASH_COLLECTION',
                    'STATUS_UPDATE', 'CUSTOMER_INTERACTION'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            response = self.users_table.get_item(
                Key={'userId': 'rider', 'role': 'DELIVERY_PERSONNEL'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Delivery Personnel user created!")
                self.print_info("Username: rider")
                self.print_info("Password: rider123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Delivery Personnel main menu"""
        while True:
            self.clear_screen()
            self.print_header("DELIVERY PERSONNEL DASHBOARD")
            
            if self.current_user:
                print(f"👤 User: {self.current_user.get('name', 'Unknown')}")
                print(f"🛵 Role: {self.current_user.get('role', 'Unknown')}")
                print(f"📧 Email: {self.current_user.get('email', 'Unknown')}")
                print(f"📅 Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n📋 Available Operations:")
            print("1. 📋 Runsheet Acceptance")
            print("2. 📦 Order Delivery")
            print("3. 💰 Cash Collection")
            print("4. 👥 Customer Interaction")
            print("5. 📊 Status Updates")
            print("6. 💳 Daily Settlement")
            print("7. 📈 Performance Analytics")
            print("8. 🔐 Logout")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select operation (0-8): ").strip()
            
            if choice == '1':
                self.runsheet_acceptance_menu()
            elif choice == '2':
                self.order_delivery_menu()
            elif choice == '3':
                self.cash_collection_menu()
            elif choice == '4':
                self.customer_interaction_menu()
            elif choice == '5':
                self.status_updates_menu()
            elif choice == '6':
                self.daily_settlement_menu()
            elif choice == '7':
                self.performance_analytics_menu()
            elif choice == '8':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Delivery Personnel system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def runsheet_acceptance_menu(self):
        """Runsheet Acceptance Operations"""
        while True:
            self.clear_screen()
            self.print_header("RUNSHEET ACCEPTANCE")
            print("1. 📋 View Assigned Runsheets")
            print("2. ✅ Accept/Reject Assignments")
            print("3. 📥 Download Route Information")
            print("4. 📊 View Runsheet History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.view_assigned_runsheets()
            elif choice == '2':
                self.accept_reject_assignments()
            elif choice == '3':
                self.download_route_information()
            elif choice == '4':
                self.view_runsheet_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def view_assigned_runsheets(self):
        """View assigned runsheets"""
        self.clear_screen()
        self.print_header("VIEW ASSIGNED RUNSHEETS")
        
        try:
            # Get deliveries assigned to this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            rider_deliveries = [delivery for delivery in deliveries if delivery.get('riderId') == self.current_rider_id]
            
            if not rider_deliveries:
                self.print_info("No runsheets assigned to you.")
                input("Press Enter to continue...")
                return
                
            print(f"📋 Your Assigned Deliveries:")
            print("-" * 80)
            print(f"{'Order ID':<20} {'Address':<30} {'Status':<15} {'Date':<15}")
            print("-" * 80)
            
            for delivery in rider_deliveries:
                print(f"{delivery.get('orderId', 'N/A'):<20} "
                      f"{delivery.get('deliveryAddress', 'N/A')[:29]:<30} "
                      f"{delivery.get('deliveryStatus', 'N/A'):<15} "
                      f"{delivery.get('deliveryDate', 'N/A')[:10]:<15}")
                      
            print("-" * 80)
            
            # Show route summary
            route_name = rider_deliveries[0].get('routeName', 'Default Route') if rider_deliveries else 'No Route'
            print(f"\n🗺️ Route: {route_name}")
            print(f"📦 Total Deliveries: {len(rider_deliveries)}")
            
            # Count by status
            status_counts = {}
            for delivery in rider_deliveries:
                status = delivery.get('deliveryStatus', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print("\n📊 Status Breakdown:")
            for status, count in status_counts.items():
                print(f"  - {status}: {count}")
                
        except Exception as e:
            self.print_error(f"Error viewing runsheets: {str(e)}")
            
        input("Press Enter to continue...")
        
    def order_delivery_menu(self):
        """Order Delivery Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER DELIVERY")
            print("1. 🗺️ Navigate to Delivery Locations")
            print("2. 📸 Capture Delivery Proof")
            print("3. 📝 Record Delivery Exceptions")
            print("4. 📊 View Delivery History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.navigate_to_delivery_locations()
            elif choice == '2':
                self.capture_delivery_proof()
            elif choice == '3':
                self.record_delivery_exceptions()
            elif choice == '4':
                self.view_delivery_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def navigate_to_delivery_locations(self):
        """Navigate to delivery locations"""
        self.clear_screen()
        self.print_header("NAVIGATE TO DELIVERY LOCATIONS")
        
        try:
            # Get pending deliveries for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            pending_deliveries = [delivery for delivery in deliveries 
                                if delivery.get('riderId') == self.current_rider_id 
                                and delivery.get('deliveryStatus') in ['ASSIGNED', 'IN_TRANSIT']]
            
            if not pending_deliveries:
                self.print_info("No pending deliveries found.")
                input("Press Enter to continue...")
                return
                
            print("🗺️ Pending Deliveries:")
            for i, delivery in enumerate(pending_deliveries, 1):
                print(f"{i}. Order {delivery.get('orderId', 'N/A')} - {delivery.get('deliveryAddress', 'N/A')}")
                
            delivery_choice = input("\n🎯 Select delivery number to navigate: ").strip()
            
            try:
                delivery_index = int(delivery_choice) - 1
                if 0 <= delivery_index < len(pending_deliveries):
                    selected_delivery = pending_deliveries[delivery_index]
                    
                    print(f"\n🗺️ Navigating to:")
                    print(f"📍 Address: {selected_delivery.get('deliveryAddress', 'N/A')}")
                    print(f"📦 Order: {selected_delivery.get('orderId', 'N/A')}")
                    print(f"📅 Date: {selected_delivery.get('deliveryDate', 'N/A')}")
                    
                    # Update delivery status to IN_TRANSIT
                    self.deliveries_table.update_item(
                        Key={'deliveryId': selected_delivery['deliveryId'], 'orderId': selected_delivery['orderId']},
                        UpdateExpression='SET deliveryStatus = :status, updatedAt = :updated',
                        ExpressionAttributeValues={
                            ':status': 'IN_TRANSIT',
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    # Log audit
                    self.log_audit('DELIVERY_NAVIGATION', selected_delivery['deliveryId'], f"Started navigation to {selected_delivery.get('deliveryAddress', 'N/A')}")
                    
                    self.print_success(f"Navigation started for Order {selected_delivery.get('orderId', 'N/A')}")
                    self.print_info("Status updated to IN_TRANSIT")
                    
                else:
                    self.print_error("Invalid delivery selection.")
            except ValueError:
                self.print_error("Invalid delivery number.")
                
        except Exception as e:
            self.print_error(f"Error navigating to delivery: {str(e)}")
            
        input("Press Enter to continue...")
        
    def cash_collection_menu(self):
        """Cash Collection Operations"""
        while True:
            self.clear_screen()
            self.print_header("CASH COLLECTION")
            print("1. 💰 Collect Cash Payments")
            print("2. 📝 Record Payment Details")
            print("3. 🧾 Issue Receipts")
            print("4. 📊 View Collection History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.collect_cash_payments()
            elif choice == '2':
                self.record_payment_details()
            elif choice == '3':
                self.issue_receipts()
            elif choice == '4':
                self.view_collection_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def collect_cash_payments(self):
        """Collect cash payments"""
        self.clear_screen()
        self.print_header("COLLECT CASH PAYMENTS")
        
        try:
            # Get completed deliveries for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            completed_deliveries = [delivery for delivery in deliveries 
                                  if delivery.get('riderId') == self.current_rider_id 
                                  and delivery.get('deliveryStatus') == 'DELIVERED']
            
            if not completed_deliveries:
                self.print_info("No completed deliveries found for cash collection.")
                input("Press Enter to continue...")
                return
                
            print("💰 Completed Deliveries for Cash Collection:")
            for i, delivery in enumerate(completed_deliveries, 1):
                print(f"{i}. Order {delivery.get('orderId', 'N/A')} - {delivery.get('deliveryAddress', 'N/A')}")
                
            delivery_choice = input("\n🎯 Select delivery number: ").strip()
            
            try:
                delivery_index = int(delivery_choice) - 1
                if 0 <= delivery_index < len(completed_deliveries):
                    selected_delivery = completed_deliveries[delivery_index]
                    
                    # Get order details for amount
                    order_response = self.orders_table.get_item(
                        Key={'orderId': selected_delivery['orderId'], 'customerId': 'CUST001'}
                    )
                    
                    if 'Item' in order_response:
                        order = order_response['Item']
                        order_amount = order.get('totalAmount', 0)
                        
                        print(f"\n💰 Cash Collection Details:")
                        print(f"📦 Order: {selected_delivery.get('orderId', 'N/A')}")
                        print(f"📍 Address: {selected_delivery.get('deliveryAddress', 'N/A')}")
                        print(f"💵 Amount Due: {order_amount}")
                        
                        # Collect payment
                        payment_method = input("💳 Payment Method (CASH/CARD/UPI): ").strip().upper()
                        amount_collected = input("💰 Amount Collected: ").strip()
                        
                        if amount_collected.replace('.', '').isdigit():
                            # Create cash collection record
                            collection_item = {
                                'collectionId': f'CC-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                                'riderId': self.current_rider_id,
                                'deliveryId': selected_delivery['deliveryId'],
                                'amountCollected': Decimal(amount_collected),
                                'collectionDate': datetime.now().isoformat(),
                                'paymentMethod': payment_method,
                                'status': 'COMPLETED',
                                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                            
                            self.cash_collections_table.put_item(Item=collection_item)
                            
                            # Log audit
                            self.log_audit('CASH_COLLECTION', selected_delivery['deliveryId'], f"Collected {amount_collected} via {payment_method}")
                            
                            self.print_success(f"Cash collection recorded successfully!")
                            self.print_info(f"Amount: {amount_collected}")
                            self.print_info(f"Method: {payment_method}")
                            
                        else:
                            self.print_error("Invalid amount.")
                    else:
                        self.print_error("Order details not found.")
                        
                else:
                    self.print_error("Invalid delivery selection.")
            except ValueError:
                self.print_error("Invalid delivery number.")
                
        except Exception as e:
            self.print_error(f"Error collecting cash: {str(e)}")
            
        input("Press Enter to continue...")
        
    def customer_interaction_menu(self):
        """Customer Interaction Operations"""
        while True:
            self.clear_screen()
            self.print_header("CUSTOMER INTERACTION")
            print("1. 💬 Handle Customer Queries")
            print("2. 📝 Capture Customer Feedback")
            print("3. 🔄 Manage Returns/Exchanges")
            print("4. 📊 View Interaction History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.handle_customer_queries()
            elif choice == '2':
                self.capture_customer_feedback()
            elif choice == '3':
                self.manage_returns_exchanges()
            elif choice == '4':
                self.view_interaction_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def status_updates_menu(self):
        """Status Updates Operations"""
        while True:
            self.clear_screen()
            self.print_header("STATUS UPDATES")
            print("1. 📊 Update Delivery Status")
            print("2. ⚠️ Report Delays or Issues")
            print("3. ✅ Mark Runsheet Completion")
            print("4. 📈 View Status History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.update_delivery_status()
            elif choice == '2':
                self.report_delays_issues()
            elif choice == '3':
                self.mark_runsheet_completion()
            elif choice == '4':
                self.view_status_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def daily_settlement_menu(self):
        """Daily Settlement Operations"""
        while True:
            self.clear_screen()
            self.print_header("DAILY SETTLEMENT")
            print("1. 💰 Submit Collected Cash")
            print("2. 📊 Reconcile Daily Transactions")
            print("3. 📝 Report Discrepancies")
            print("4. 📈 View Settlement History")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.submit_collected_cash()
            elif choice == '2':
                self.reconcile_daily_transactions()
            elif choice == '3':
                self.report_discrepancies()
            elif choice == '4':
                self.view_settlement_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def performance_analytics_menu(self):
        """Performance Analytics Operations"""
        while True:
            self.clear_screen()
            self.print_header("PERFORMANCE ANALYTICS")
            print("1. 📊 Delivery Performance")
            print("2. 💰 Collection Performance")
            print("3. ⏰ Time Analytics")
            print("4. 📈 Customer Satisfaction")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select operation (1-5): ").strip()
            
            if choice == '1':
                self.delivery_performance()
            elif choice == '2':
                self.collection_performance()
            elif choice == '3':
                self.time_analytics()
            elif choice == '4':
                self.customer_satisfaction()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    # Placeholder methods for other operations
    def accept_reject_assignments(self):
        self.clear_screen()
        self.print_header("ACCEPT/REJECT ASSIGNMENTS")
        self.print_info("Assignment acceptance/rejection functionality will be implemented.")
        input("Press Enter to continue...")
        
    def download_route_information(self):
        self.clear_screen()
        self.print_header("DOWNLOAD ROUTE INFORMATION")
        self.print_info("Route information download functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_runsheet_history(self):
        self.clear_screen()
        self.print_header("VIEW RUNSHEET HISTORY")
        self.print_info("Runsheet history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def capture_delivery_proof(self):
        self.clear_screen()
        self.print_header("CAPTURE DELIVERY PROOF")
        self.print_info("Delivery proof capture functionality will be implemented.")
        input("Press Enter to continue...")
        
    def record_delivery_exceptions(self):
        self.clear_screen()
        self.print_header("RECORD DELIVERY EXCEPTIONS")
        self.print_info("Delivery exception recording functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_delivery_history(self):
        self.clear_screen()
        self.print_header("VIEW DELIVERY HISTORY")
        self.print_info("Delivery history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def record_payment_details(self):
        self.clear_screen()
        self.print_header("RECORD PAYMENT DETAILS")
        self.print_info("Payment detail recording functionality will be implemented.")
        input("Press Enter to continue...")
        
    def issue_receipts(self):
        self.clear_screen()
        self.print_header("ISSUE RECEIPTS")
        self.print_info("Receipt issuance functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_collection_history(self):
        self.clear_screen()
        self.print_header("VIEW COLLECTION HISTORY")
        self.print_info("Collection history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def handle_customer_queries(self):
        self.clear_screen()
        self.print_header("HANDLE CUSTOMER QUERIES")
        self.print_info("Customer query handling functionality will be implemented.")
        input("Press Enter to continue...")
        
    def capture_customer_feedback(self):
        self.clear_screen()
        self.print_header("CAPTURE CUSTOMER FEEDBACK")
        self.print_info("Customer feedback capture functionality will be implemented.")
        input("Press Enter to continue...")
        
    def manage_returns_exchanges(self):
        self.clear_screen()
        self.print_header("MANAGE RETURNS/EXCHANGES")
        self.print_info("Returns/exchanges management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_interaction_history(self):
        self.clear_screen()
        self.print_header("VIEW INTERACTION HISTORY")
        self.print_info("Interaction history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_delivery_status(self):
        self.clear_screen()
        self.print_header("UPDATE DELIVERY STATUS")
        self.print_info("Delivery status update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def report_delays_issues(self):
        self.clear_screen()
        self.print_header("REPORT DELAYS OR ISSUES")
        self.print_info("Delay/issue reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def mark_runsheet_completion(self):
        self.clear_screen()
        self.print_header("MARK RUNSHEET COMPLETION")
        self.print_info("Runsheet completion marking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_status_history(self):
        self.clear_screen()
        self.print_header("VIEW STATUS HISTORY")
        self.print_info("Status history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def submit_collected_cash(self):
        self.clear_screen()
        self.print_header("SUBMIT COLLECTED CASH")
        self.print_info("Collected cash submission functionality will be implemented.")
        input("Press Enter to continue...")
        
    def reconcile_daily_transactions(self):
        self.clear_screen()
        self.print_header("RECONCILE DAILY TRANSACTIONS")
        self.print_info("Daily transaction reconciliation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def report_discrepancies(self):
        self.clear_screen()
        self.print_header("REPORT DISCREPANCIES")
        self.print_info("Discrepancy reporting functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_settlement_history(self):
        self.clear_screen()
        self.print_header("VIEW SETTLEMENT HISTORY")
        self.print_info("Settlement history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def delivery_performance(self):
        self.clear_screen()
        self.print_header("DELIVERY PERFORMANCE")
        self.print_info("Delivery performance analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def collection_performance(self):
        self.clear_screen()
        self.print_header("COLLECTION PERFORMANCE")
        self.print_info("Collection performance analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def time_analytics(self):
        self.clear_screen()
        self.print_header("TIME ANALYTICS")
        self.print_info("Time analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def customer_satisfaction(self):
        self.clear_screen()
        self.print_header("CUSTOMER SATISFACTION")
        self.print_info("Customer satisfaction analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.print_success(f"Goodbye, {self.current_user.get('name', 'User')}!")
            self.current_user = None
            self.current_role = None
            self.current_rider_id = None
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
                'userAgent': 'DeliveryPersonnel-Standalone',
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
            self.print_success("Thank you for using the Delivery Personnel system!")


def main():
    """Main entry point"""
    delivery_personnel = DeliveryPersonnelStandalone()
    delivery_personnel.run()


if __name__ == '__main__':
    main() 