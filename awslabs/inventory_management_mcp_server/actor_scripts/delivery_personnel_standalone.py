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
from datetime import datetime, timezone, timedelta
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
        print(f"[DELIVERY] {title}")
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
        self.print_header("DELIVERY PERSONNEL - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your credentials:")
        print("[NOTE] Demo credentials: rider / rider123")
        
        username = input("\n[USER] Username: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
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
                print(f"[USER] User: {self.current_user.get('name', 'Unknown')}")
                print(f"🛵 Role: {self.current_user.get('role', 'Unknown')}")
                print(f"[EMAIL] Email: {self.current_user.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. [CLIPBOARD] Runsheet Acceptance")
            print("2. [ORDER] Order Delivery")
            print("3. [PRICE] Cash Collection")
            print("4. 👥 Customer Interaction")
            print("5. [TRACK] Status Updates")
            print("6. [PAYMENT] Daily Settlement")
            print("7. [REPORT] Performance Analytics")
            print("8. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-8): ").strip()
            
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
            print("1. [CLIPBOARD] View Assigned Runsheets")
            print("2. [SUCCESS] Accept/Reject Assignments")
            print("3. 📥 Download Route Information")
            print("4. [TRACK] View Runsheet History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
            print(f"[CLIPBOARD] Your Assigned Deliveries:")
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
            print(f"[ORDER] Total Deliveries: {len(rider_deliveries)}")
            
            # Count by status
            status_counts = {}
            for delivery in rider_deliveries:
                status = delivery.get('deliveryStatus', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print("\n[TRACK] Status Breakdown:")
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
            print("3. [GENERATE] Record Delivery Exceptions")
            print("4. [TRACK] View Delivery History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
            delivery_choice = input("\n[TARGET] Select delivery number to navigate: ").strip()
            
            try:
                delivery_index = int(delivery_choice) - 1
                if 0 <= delivery_index < len(pending_deliveries):
                    selected_delivery = pending_deliveries[delivery_index]
                    
                    print(f"\n🗺️ Navigating to:")
                    print(f"[ADDRESS] Address: {selected_delivery.get('deliveryAddress', 'N/A')}")
                    print(f"[ORDER] Order: {selected_delivery.get('orderId', 'N/A')}")
                    print(f"[DATE] Date: {selected_delivery.get('deliveryDate', 'N/A')}")
                    
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
            print("1. [PRICE] Collect Cash Payments")
            print("2. [GENERATE] Record Payment Details")
            print("3. 🧾 Issue Receipts")
            print("4. [TRACK] View Collection History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
            print("[PRICE] Completed Deliveries for Cash Collection:")
            for i, delivery in enumerate(completed_deliveries, 1):
                print(f"{i}. Order {delivery.get('orderId', 'N/A')} - {delivery.get('deliveryAddress', 'N/A')}")
                
            delivery_choice = input("\n[TARGET] Select delivery number: ").strip()
            
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
                        
                        print(f"\n[PRICE] Cash Collection Details:")
                        print(f"[ORDER] Order: {selected_delivery.get('orderId', 'N/A')}")
                        print(f"[ADDRESS] Address: {selected_delivery.get('deliveryAddress', 'N/A')}")
                        print(f"💵 Amount Due: {order_amount}")
                        
                        # Collect payment
                        payment_method = input("[PAYMENT] Payment Method (CASH/CARD/UPI): ").strip().upper()
                        amount_collected = input("[PRICE] Amount Collected: ").strip()
                        
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
            print("1. [CHAT] Handle Customer Queries")
            print("2. [GENERATE] Capture Customer Feedback")
            print("3. [FLOW] Manage Returns/Exchanges")
            print("4. [TRACK] View Interaction History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [TRACK] Update Delivery Status")
            print("2. [INTERRUPTED] Report Delays or Issues")
            print("3. [SUCCESS] Mark Runsheet Completion")
            print("4. [REPORT] View Status History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [PRICE] Submit Collected Cash")
            print("2. [TRACK] Reconcile Daily Transactions")
            print("3. [GENERATE] Report Discrepancies")
            print("4. [REPORT] View Settlement History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
            print("1. [TRACK] Delivery Performance")
            print("2. [PRICE] Collection Performance")
            print("3. ⏰ Time Analytics")
            print("4. [REPORT] Customer Satisfaction")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
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
                
    def accept_reject_assignments(self):
        """Accept or reject delivery assignments"""
        self.clear_screen()
        self.print_header("ACCEPT/REJECT ASSIGNMENTS")
        
        try:
            # Get pending assignments for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            pending_assignments = [delivery for delivery in deliveries 
                                 if delivery.get('riderId') == self.current_rider_id 
                                 and delivery.get('deliveryStatus') == 'ASSIGNED']
            
            if not pending_assignments:
                self.print_info("No pending assignments found.")
                input("Press Enter to continue...")
                return
                
            print(f"[CLIPBOARD] Pending Assignments ({len(pending_assignments)} assignments):")
            print("-" * 120)
            print(f"{'#':<3} {'Order ID':<15} {'Customer':<20} {'Address':<30} {'Amount':<10} {'Date':<12} {'Priority':<10}")
            print("-" * 120)
            
            for i, assignment in enumerate(pending_assignments, 1):
                # Get order details for amount
                try:
                    order_response = self.orders_table.scan(
                        FilterExpression='orderId = :oid',
                        ExpressionAttributeValues={':oid': assignment.get('orderId')}
                    )
                    order_amount = order_response['Items'][0].get('totalAmount', 0) if order_response['Items'] else 0
                    customer_id = order_response['Items'][0].get('customerId', 'N/A') if order_response['Items'] else 'N/A'
                except:
                    order_amount = 0
                    customer_id = 'N/A'
                    
                delivery_date = assignment.get('deliveryDate', 'N/A')[:10] if assignment.get('deliveryDate') else 'N/A'
                priority = assignment.get('priority', 'NORMAL')
                
                print(f"{i:<3} {assignment.get('orderId', 'N/A'):<15} "
                      f"{customer_id:<20} "
                      f"{assignment.get('deliveryAddress', 'N/A')[:29]:<30} "
                      f"₹{order_amount:<9} "
                      f"{delivery_date:<12} "
                      f"{priority:<10}")
                      
            print("-" * 120)
            
            # Select assignment to accept/reject
            try:
                choice = input(f"\n[TARGET] Select assignment number (1-{len(pending_assignments)}) or 'all' for all: ").strip()
                
                if choice.lower() == 'all':
                    # Accept all assignments
                    action = input("\n[CONFIRM] Accept all assignments? (yes/no): ").strip().lower()
                    if action == 'yes':
                        for assignment in pending_assignments:
                            self.update_assignment_status(assignment, 'ACCEPTED')
                        self.print_success(f"[SUCCESS] All {len(pending_assignments)} assignments accepted!")
                    else:
                        self.print_info("Bulk action cancelled.")
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(pending_assignments):
                        selected_assignment = pending_assignments[choice_num - 1]
                        
                        print(f"\n[CLIPBOARD] Assignment Details:")
                        print(f"   [ORDER] Order ID: {selected_assignment.get('orderId')}")
                        print(f"   [ADDRESS] Address: {selected_assignment.get('deliveryAddress')}")
                        print(f"   [DATE] Delivery Date: {selected_assignment.get('deliveryDate')}")
                        print(f"   ⏰ Time Slot: {selected_assignment.get('timeSlot', 'N/A')}")
                        
                        action = input("\n[CONFIRM] Action (accept/reject): ").strip().lower()
                        
                        if action == 'accept':
                            self.update_assignment_status(selected_assignment, 'ACCEPTED')
                            self.print_success("[SUCCESS] Assignment accepted!")
                        elif action == 'reject':
                            reason = input("[GENERATE] Rejection reason: ").strip()
                            self.update_assignment_status(selected_assignment, 'REJECTED', reason)
                            self.print_success("[ERROR] Assignment rejected!")
                        else:
                            self.print_error("Invalid action.")
                    else:
                        self.print_error("Invalid assignment number.")
                        
            except ValueError:
                self.print_error("Invalid selection.")
                
        except Exception as e:
            self.print_error(f"Error processing assignments: {str(e)}")
            
        input("Press Enter to continue...")
        
    def update_assignment_status(self, assignment: Dict[str, Any], status: str, reason: str = ""):
        """Update assignment status"""
        try:
            update_expression = 'SET deliveryStatus = :status, updatedAt = :updated'
            expression_values = {
                ':status': status,
                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            if reason:
                update_expression += ', rejectionReason = :reason'
                expression_values[':reason'] = reason
                
            self.deliveries_table.update_item(
                Key={'deliveryId': assignment['deliveryId'], 'orderId': assignment['orderId']},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Log audit
            action_text = f"Assignment {status.lower()}"
            if reason:
                action_text += f" - Reason: {reason}"
            self.log_audit('ASSIGNMENT_STATUS_UPDATE', assignment['deliveryId'], action_text)
            
        except Exception as e:
            self.print_error(f"Error updating assignment status: {str(e)}")
        
    def download_route_information(self):
        """Download route information for accepted assignments"""
        self.clear_screen()
        self.print_header("DOWNLOAD ROUTE INFORMATION")
        
        try:
            # Get accepted assignments for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            accepted_assignments = [delivery for delivery in deliveries 
                                  if delivery.get('riderId') == self.current_rider_id 
                                  and delivery.get('deliveryStatus') == 'ACCEPTED']
            
            if not accepted_assignments:
                self.print_info("No accepted assignments found for route generation.")
                input("Press Enter to continue...")
                return
                
            print(f"🗺️ Route Information for {len(accepted_assignments)} Deliveries:")
            print("=" * 80)
            
            # Generate optimized route (simplified)
            route_data = self.generate_delivery_route(accepted_assignments)
            
            print(f"\n[ADDRESS] Route Summary:")
            print(f"   [DELIVERY] Total Deliveries: {len(accepted_assignments)}")
            print(f"   [SIZE] Estimated Distance: {route_data['total_distance']:.1f} km")
            print(f"   ⏰ Estimated Time: {route_data['total_time']} minutes")
            print(f"   [COMPLETE] Start Location: {route_data['start_location']}")
            
            print(f"\n🗺️ Delivery Sequence:")
            print("-" * 100)
            print(f"{'Stop#':<6} {'Order ID':<15} {'Address':<40} {'Est. Time':<12} {'Notes':<15}")
            print("-" * 100)
            
            for i, stop in enumerate(route_data['stops'], 1):
                print(f"{i:<6} {stop['orderId']:<15} {stop['address'][:39]:<40} "
                      f"{stop['estimated_time']:<12} {stop['notes']:<15}")
                      
            print("-" * 100)
            
            # Route download options
            print(f"\n📥 Download Options:")
            print("1. [MOBILE] View Mobile-Friendly Route")
            print("2. 🗺️ Generate Navigation Links")
            print("3. [CLIPBOARD] Print Route Summary")
            print("4. [EMAIL] Email Route Information")
            
            download_choice = input("\n[TARGET] Select download option (1-4): ").strip()
            
            if download_choice == '1':
                self.display_mobile_route(route_data)
            elif download_choice == '2':
                self.generate_navigation_links(route_data)
            elif download_choice == '3':
                self.print_route_summary(route_data)
            elif download_choice == '4':
                self.email_route_information(route_data)
            else:
                self.print_error("Invalid download option.")
                
        except Exception as e:
            self.print_error(f"Error downloading route information: {str(e)}")
            
        input("Press Enter to continue...")
        
    def generate_delivery_route(self, assignments: list) -> Dict[str, Any]:
        """Generate optimized delivery route"""
        try:
            # Simple route optimization (in real implementation, use actual mapping service)
            stops = []
            total_distance = 0
            total_time = 0
            
            for assignment in assignments:
                # Calculate estimated travel time and distance (simplified)
                estimated_time = f"{15 + len(stops) * 5}-{20 + len(stops) * 5} min"
                estimated_distance = 2.5 + (len(stops) * 1.2)  # km
                
                stop = {
                    'orderId': assignment.get('orderId'),
                    'address': assignment.get('deliveryAddress', 'N/A'),
                    'estimated_time': estimated_time,
                    'distance_from_prev': estimated_distance,
                    'notes': assignment.get('deliveryNotes', 'Standard delivery'),
                    'priority': assignment.get('priority', 'NORMAL'),
                    'timeSlot': assignment.get('timeSlot', 'N/A')
                }
                stops.append(stop)
                total_distance += estimated_distance
                total_time += 20  # Average 20 minutes per delivery
                
            # Sort by priority and time slots for optimization
            stops.sort(key=lambda x: (x['priority'] != 'HIGH', x['timeSlot']))
            
            return {
                'stops': stops,
                'total_distance': total_distance,
                'total_time': total_time,
                'start_location': 'Main Warehouse',
                'route_id': f'ROUTE-{self.current_rider_id}-{datetime.now().strftime("%Y%m%d")}'
            }
            
        except Exception as e:
            self.print_error(f"Error generating route: {str(e)}")
            return {'stops': [], 'total_distance': 0, 'total_time': 0, 'start_location': 'Unknown'}
            
    def display_mobile_route(self, route_data: Dict[str, Any]):
        """Display mobile-friendly route"""
        print(f"\n[MOBILE] Mobile Route View:")
        print("=" * 50)
        print(f"Route: {route_data['route_id']}")
        print(f"Distance: {route_data['total_distance']:.1f}km")
        print(f"Time: {route_data['total_time']}min")
        print("=" * 50)
        
        for i, stop in enumerate(route_data['stops'], 1):
            print(f"\n{i}. {stop['orderId']}")
            print(f"   [ADDRESS] {stop['address']}")
            print(f"   ⏰ {stop['estimated_time']}")
            print(f"   [GENERATE] {stop['notes']}")
            
    def generate_navigation_links(self, route_data: Dict[str, Any]):
        """Generate navigation links for each stop"""
        print(f"\n🗺️ Navigation Links:")
        print("-" * 60)
        
        for i, stop in enumerate(route_data['stops'], 1):
            # Generate Google Maps link (simplified)
            address = stop['address'].replace(' ', '+')
            maps_link = f"https://maps.google.com/maps?q={address}"
            
            print(f"{i}. Order: {stop['orderId']}")
            print(f"   [ADDRESS] Address: {stop['address']}")
            print(f"   🗺️ Maps Link: {maps_link}")
            print(f"   [CLIPBOARD] Copy this link to your navigation app")
            print()
            
    def print_route_summary(self, route_data: Dict[str, Any]):
        """Print detailed route summary"""
        print(f"\n[CLIPBOARD] ROUTE SUMMARY - {route_data['route_id']}")
        print("=" * 80)
        print(f"Rider: {self.current_user.get('name', 'Unknown')}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Total Stops: {len(route_data['stops'])}")
        print(f"Estimated Distance: {route_data['total_distance']:.1f} km")
        print(f"Estimated Time: {route_data['total_time']} minutes")
        print("=" * 80)
        
        for i, stop in enumerate(route_data['stops'], 1):
            print(f"\nSTOP {i}: {stop['orderId']}")
            print(f"Address: {stop['address']}")
            print(f"Time Slot: {stop['timeSlot']}")
            print(f"Estimated Arrival: {stop['estimated_time']}")
            print(f"Priority: {stop['priority']}")
            print(f"Notes: {stop['notes']}")
            print("-" * 40)
            
    def email_route_information(self, route_data: Dict[str, Any]):
        """Email route information (simulation)"""
        email = self.current_user.get('email', 'rider@company.com')
        print(f"\n[EMAIL] Emailing route information to: {email}")
        print(f"   [CLIPBOARD] Subject: Delivery Route - {route_data['route_id']}")
        print(f"   [ORDER] {len(route_data['stops'])} deliveries included")
        print(f"   [SIZE] Route distance: {route_data['total_distance']:.1f}km")
        
        # In real implementation, would send actual email
        self.print_success("[SUCCESS] Route information sent to your email!")
        
    def view_runsheet_history(self):
        """View runsheet history for the rider"""
        self.clear_screen()
        self.print_header("VIEW RUNSHEET HISTORY")
        
        try:
            # Get all historical deliveries for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            rider_deliveries = [delivery for delivery in deliveries 
                              if delivery.get('riderId') == self.current_rider_id]
            
            if not rider_deliveries:
                self.print_info("No runsheet history found.")
                input("Press Enter to continue...")
                return
                
            # Sort by date (most recent first)
            rider_deliveries.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            
            print(f"[TRACK] Runsheet History ({len(rider_deliveries)} total deliveries):")
            
            # Filter options
            print(f"\n[AUDIT] Filter Options:")
            print("1. All History")
            print("2. Last 7 Days")
            print("3. Last 30 Days")
            print("4. Specific Date Range")
            print("5. By Status")
            
            filter_choice = input("\n[TARGET] Select filter (1-5): ").strip()
            
            filtered_deliveries = rider_deliveries
            
            if filter_choice == '2':
                # Last 7 days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
                filtered_deliveries = [d for d in rider_deliveries 
                                     if datetime.fromisoformat(d.get('createdAt', '').replace('Z', '+00:00')) >= cutoff_date]
            elif filter_choice == '3':
                # Last 30 days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
                filtered_deliveries = [d for d in rider_deliveries 
                                     if datetime.fromisoformat(d.get('createdAt', '').replace('Z', '+00:00')) >= cutoff_date]
            elif filter_choice == '4':
                # Date range
                start_date = input("[DATE] Start date (YYYY-MM-DD): ").strip()
                end_date = input("[DATE] End date (YYYY-MM-DD): ").strip()
                # Add date filtering logic here
            elif filter_choice == '5':
                # By status
                status_filter = input("[TRACK] Status (DELIVERED/FAILED/CANCELLED): ").strip().upper()
                filtered_deliveries = [d for d in rider_deliveries 
                                     if d.get('deliveryStatus') == status_filter]
                                     
            # Display filtered results
            print(f"\n[CLIPBOARD] Runsheet History ({len(filtered_deliveries)} records):")
            print("-" * 120)
            print(f"{'Date':<12} {'Order ID':<15} {'Address':<25} {'Status':<15} {'Amount':<10} {'Time':<10} {'Notes':<20}")
            print("-" * 120)
            
            for delivery in filtered_deliveries[:20]:  # Show max 20 records
                delivery_date = delivery.get('deliveryDate', 'N/A')[:10] if delivery.get('deliveryDate') else 'N/A'
                delivery_time = delivery.get('deliveredAt', 'N/A')[11:16] if delivery.get('deliveredAt') else 'N/A'
                
                # Get order amount
                try:
                    order_response = self.orders_table.scan(
                        FilterExpression='orderId = :oid',
                        ExpressionAttributeValues={':oid': delivery.get('orderId')}
                    )
                    order_amount = order_response['Items'][0].get('totalAmount', 0) if order_response['Items'] else 0
                except:
                    order_amount = 0
                    
                print(f"{delivery_date:<12} {delivery.get('orderId', 'N/A'):<15} "
                      f"{delivery.get('deliveryAddress', 'N/A')[:24]:<25} "
                      f"{delivery.get('deliveryStatus', 'N/A'):<15} "
                      f"₹{order_amount:<9} "
                      f"{delivery_time:<10} "
                      f"{delivery.get('deliveryNotes', 'N/A')[:19]:<20}")
                      
            print("-" * 120)
            
            # Summary statistics
            total_delivered = len([d for d in filtered_deliveries if d.get('deliveryStatus') == 'DELIVERED'])
            total_failed = len([d for d in filtered_deliveries if d.get('deliveryStatus') == 'FAILED'])
            success_rate = (total_delivered / len(filtered_deliveries) * 100) if filtered_deliveries else 0
            
            print(f"\n[TRACK] Summary Statistics:")
            print(f"   [SUCCESS] Delivered: {total_delivered}")
            print(f"   [ERROR] Failed: {total_failed}")
            print(f"   [REPORT] Success Rate: {success_rate:.1f}%")
            print(f"   [CLIPBOARD] Total Records: {len(filtered_deliveries)}")
            
        except Exception as e:
            self.print_error(f"Error viewing runsheet history: {str(e)}")
            
        input("Press Enter to continue...")
        
    def capture_delivery_proof(self):
        """Capture delivery proof for completed deliveries"""
        self.clear_screen()
        self.print_header("CAPTURE DELIVERY PROOF")
        
        try:
            # Get deliveries in IN_TRANSIT status for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            in_transit_deliveries = [delivery for delivery in deliveries 
                                   if delivery.get('riderId') == self.current_rider_id 
                                   and delivery.get('deliveryStatus') == 'IN_TRANSIT']
            
            if not in_transit_deliveries:
                self.print_info("No deliveries in transit found.")
                input("Press Enter to continue...")
                return
                
            print(f"📸 Deliveries Ready for Proof Capture ({len(in_transit_deliveries)} deliveries):")
            print("-" * 100)
            print(f"{'#':<3} {'Order ID':<15} {'Address':<40} {'Delivery Date':<15} {'Time Slot':<15}")
            print("-" * 100)
            
            for i, delivery in enumerate(in_transit_deliveries, 1):
                delivery_date = delivery.get('deliveryDate', 'N/A')[:10] if delivery.get('deliveryDate') else 'N/A'
                time_slot = delivery.get('timeSlot', 'N/A')
                
                print(f"{i:<3} {delivery.get('orderId', 'N/A'):<15} "
                      f"{delivery.get('deliveryAddress', 'N/A')[:39]:<40} "
                      f"{delivery_date:<15} "
                      f"{time_slot:<15}")
                      
            print("-" * 100)
            
            # Select delivery for proof capture
            try:
                choice = input(f"\n[TARGET] Select delivery number (1-{len(in_transit_deliveries)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(in_transit_deliveries):
                    selected_delivery = in_transit_deliveries[choice_num - 1]
                    self.process_delivery_proof_capture(selected_delivery)
                else:
                    self.print_error("Invalid delivery selection.")
            except ValueError:
                self.print_error("Invalid number.")
                
        except Exception as e:
            self.print_error(f"Error capturing delivery proof: {str(e)}")
            
        input("Press Enter to continue...")
        
    def process_delivery_proof_capture(self, delivery: Dict[str, Any]):
        """Process delivery proof capture for a specific delivery"""
        try:
            order_id = delivery.get('orderId')
            delivery_id = delivery.get('deliveryId')
            
            print(f"\n📸 Capture Delivery Proof for Order: {order_id}")
            print(f"[ADDRESS] Address: {delivery.get('deliveryAddress')}")
            
            # Delivery completion options
            print(f"\n[ORDER] Delivery Status Options:")
            print("1. [SUCCESS] Successfully Delivered")
            print("2. [ERROR] Delivery Failed")
            print("3. [FLOW] Partial Delivery")
            print("4. [HOME] Customer Not Available")
            print("5. [ADDRESS] Wrong Address")
            
            status_choice = input("\n[TARGET] Select delivery status (1-5): ").strip()
            
            status_map = {
                '1': 'DELIVERED',
                '2': 'FAILED',
                '3': 'PARTIAL_DELIVERY',
                '4': 'CUSTOMER_UNAVAILABLE',
                '5': 'WRONG_ADDRESS'
            }
            
            if status_choice not in status_map:
                self.print_error("Invalid status selection.")
                return
                
            delivery_status = status_map[status_choice]
            
            # Get delivery details based on status
            if delivery_status == 'DELIVERED':
                self.process_successful_delivery(delivery, delivery_id)
            elif delivery_status == 'FAILED':
                self.process_failed_delivery(delivery, delivery_id)
            elif delivery_status == 'PARTIAL_DELIVERY':
                self.process_partial_delivery(delivery, delivery_id)
            else:
                self.process_exception_delivery(delivery, delivery_id, delivery_status)
                
        except Exception as e:
            self.print_error(f"Error processing delivery proof: {str(e)}")
            
    def process_successful_delivery(self, delivery: Dict[str, Any], delivery_id: str):
        """Process successful delivery proof"""
        try:
            print(f"\n[SUCCESS] Recording Successful Delivery")
            
            # Capture delivery proof details
            customer_name = input("[USER] Customer Name (who received): ").strip()
            delivery_time = datetime.now().strftime('%H:%M')
            
            # Proof of delivery options
            print(f"\n📸 Proof of Delivery Options:")
            print("1. 📸 Photo of delivered items")
            print("2. ✍️ Customer signature")
            print("3. [MOBILE] SMS confirmation")
            print("4. [EMAIL] Email confirmation")
            print("5. [ID] ID verification")
            
            proof_types = []
            while True:
                proof_choice = input("[TARGET] Select proof type (1-5) or 'done' to finish: ").strip()
                
                if proof_choice.lower() == 'done':
                    break
                elif proof_choice in ['1', '2', '3', '4', '5']:
                    proof_map = {
                        '1': 'PHOTO',
                        '2': 'SIGNATURE',
                        '3': 'SMS_CONFIRMATION',
                        '4': 'EMAIL_CONFIRMATION',
                        '5': 'ID_VERIFICATION'
                    }
                    
                    proof_type = proof_map[proof_choice]
                    if proof_type not in proof_types:
                        proof_types.append(proof_type)
                        self.print_success(f"[SUCCESS] {proof_type} added")
                    else:
                        self.print_warning("Proof type already added")
                else:
                    self.print_error("Invalid proof type")
                    
            # Delivery notes
            delivery_notes = input("\n[GENERATE] Delivery Notes (optional): ").strip()
            
            # Customer satisfaction
            satisfaction_rating = input("[RATING] Customer Satisfaction (1-5): ").strip()
            if not satisfaction_rating.isdigit() or not (1 <= int(satisfaction_rating) <= 5):
                satisfaction_rating = "5"  # Default
                
            # Update delivery record
            self.deliveries_table.update_item(
                Key={'deliveryId': delivery_id, 'orderId': delivery['orderId']},
                UpdateExpression='SET deliveryStatus = :status, deliveredAt = :delivered_time, '
                                'customerName = :customer, proofTypes = :proof, '
                                'deliveryNotes = :notes, satisfactionRating = :rating, '
                                'completedBy = :rider, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':status': 'DELIVERED',
                    ':delivered_time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':customer': customer_name,
                    ':proof': proof_types,
                    ':notes': delivery_notes,
                    ':rating': int(satisfaction_rating),
                    ':rider': self.current_rider_id,
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Log audit
            self.log_audit('DELIVERY_COMPLETED', delivery_id, 
                          f"Delivery completed successfully. Customer: {customer_name}, Proof: {', '.join(proof_types)}")
            
            self.print_success("[SUCCESS] Delivery completed successfully!")
            print(f"   [USER] Delivered to: {customer_name}")
            print(f"   ⏰ Time: {delivery_time}")
            print(f"   📸 Proof types: {', '.join(proof_types)}")
            print(f"   [RATING] Satisfaction: {satisfaction_rating}/5")
            
        except Exception as e:
            self.print_error(f"Error processing successful delivery: {str(e)}")
            
    def process_failed_delivery(self, delivery: Dict[str, Any], delivery_id: str):
        """Process failed delivery"""
        try:
            print(f"\n[ERROR] Recording Failed Delivery")
            
            # Failure reasons
            print(f"\n[GENERATE] Failure Reasons:")
            print("1. [HOME] Customer not available")
            print("2. [ADDRESS] Wrong/incomplete address")
            print("3. [SUPPORT] Phone not reachable")
            print("4. [PRICE] Payment issues")
            print("5. [ERROR] Customer refused delivery")
            print("6. 🌧️ Weather conditions")
            print("7. 🚫 Access denied")
            print("8. [ORDER] Product damage")
            print("9. [TOOL] Other")
            
            reason_choice = input("\n[TARGET] Select failure reason (1-9): ").strip()
            
            reason_map = {
                '1': 'CUSTOMER_UNAVAILABLE',
                '2': 'WRONG_ADDRESS',
                '3': 'PHONE_UNREACHABLE',
                '4': 'PAYMENT_ISSUES',
                '5': 'CUSTOMER_REFUSED',
                '6': 'WEATHER_CONDITIONS',
                '7': 'ACCESS_DENIED',
                '8': 'PRODUCT_DAMAGE',
                '9': 'OTHER'
            }
            
            failure_reason = reason_map.get(reason_choice, 'OTHER')
            
            # Additional details
            failure_details = input("[GENERATE] Additional failure details: ").strip()
            
            # Retry options
            print(f"\n[FLOW] Next Steps:")
            print("1. [DATE] Schedule retry delivery")
            print("2. [SUPPORT] Contact customer")
            print("3. [FLOW] Return to warehouse")
            print("4. [CLIPBOARD] Mark for manual follow-up")
            
            next_action = input("\n[TARGET] Select next action (1-4): ").strip()
            
            action_map = {
                '1': 'RETRY_SCHEDULED',
                '2': 'CONTACT_CUSTOMER',
                '3': 'RETURN_TO_WAREHOUSE',
                '4': 'MANUAL_FOLLOWUP'
            }
            
            next_action_type = action_map.get(next_action, 'MANUAL_FOLLOWUP')
            
            # Schedule retry if selected
            retry_date = None
            if next_action == '1':
                retry_date = input("[DATE] Retry date (YYYY-MM-DD): ").strip()
                
            # Update delivery record
            update_expression = ('SET deliveryStatus = :status, failureReason = :reason, '
                               'failureDetails = :details, nextAction = :action, '
                               'attemptedAt = :attempted, completedBy = :rider, updatedAt = :updated')
            expression_values = {
                ':status': 'FAILED',
                ':reason': failure_reason,
                ':details': failure_details,
                ':action': next_action_type,
                ':attempted': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                ':rider': self.current_rider_id,
                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            if retry_date:
                update_expression += ', retryDate = :retry'
                expression_values[':retry'] = retry_date
                
            self.deliveries_table.update_item(
                Key={'deliveryId': delivery_id, 'orderId': delivery['orderId']},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            # Log audit
            self.log_audit('DELIVERY_FAILED', delivery_id, 
                          f"Delivery failed. Reason: {failure_reason}, Next action: {next_action_type}")
            
            self.print_success("[ERROR] Failed delivery recorded!")
            print(f"   [GENERATE] Reason: {failure_reason}")
            print(f"   [FLOW] Next action: {next_action_type}")
            if retry_date:
                print(f"   [DATE] Retry scheduled: {retry_date}")
                
        except Exception as e:
            self.print_error(f"Error processing failed delivery: {str(e)}")
            
    def process_partial_delivery(self, delivery: Dict[str, Any], delivery_id: str):
        """Process partial delivery"""
        try:
            print(f"\n[FLOW] Recording Partial Delivery")
            
            # Get order items for partial delivery selection
            order_response = self.orders_table.scan(
                FilterExpression='orderId = :oid',
                ExpressionAttributeValues={':oid': delivery.get('orderId')}
            )
            
            if not order_response['Items']:
                self.print_error("Order details not found")
                return
                
            order = order_response['Items'][0]
            order_items = order.get('items', [])
            
            print(f"\n[ORDER] Order Items:")
            delivered_items = []
            
            for i, item in enumerate(order_items, 1):
                print(f"{i}. {item.get('name', 'Unknown')} x{item.get('quantity', 0)}")
                
                delivered = input(f"   [SUCCESS] Delivered? (yes/no): ").strip().lower()
                
                if delivered == 'yes':
                    delivered_qty = input(f"   [TRACK] Quantity delivered: ").strip()
                    if delivered_qty.isdigit():
                        delivered_items.append({
                            'productId': item.get('productId'),
                            'name': item.get('name'),
                            'requestedQty': item.get('quantity', 0),
                            'deliveredQty': int(delivered_qty),
                            'status': 'DELIVERED'
                        })
                    else:
                        self.print_error("Invalid quantity")
                else:
                    reason = input(f"   [GENERATE] Reason for non-delivery: ").strip()
                    delivered_items.append({
                        'productId': item.get('productId'),
                        'name': item.get('name'),
                        'requestedQty': item.get('quantity', 0),
                        'deliveredQty': 0,
                        'status': 'NOT_DELIVERED',
                        'reason': reason
                    })
                    
            # Customer details
            customer_name = input("\n[USER] Customer Name: ").strip()
            delivery_notes = input("[GENERATE] Delivery Notes: ").strip()
            
            # Update delivery record
            self.deliveries_table.update_item(
                Key={'deliveryId': delivery_id, 'orderId': delivery['orderId']},
                UpdateExpression='SET deliveryStatus = :status, partialItems = :items, '
                                'customerName = :customer, deliveryNotes = :notes, '
                                'deliveredAt = :delivered_time, completedBy = :rider, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':status': 'PARTIAL_DELIVERY',
                    ':items': delivered_items,
                    ':customer': customer_name,
                    ':notes': delivery_notes,
                    ':delivered_time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':rider': self.current_rider_id,
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Log audit
            delivered_count = len([item for item in delivered_items if item['status'] == 'DELIVERED'])
            self.log_audit('PARTIAL_DELIVERY', delivery_id, 
                          f"Partial delivery completed. {delivered_count}/{len(order_items)} items delivered")
            
            self.print_success("[FLOW] Partial delivery recorded!")
            print(f"   [SUCCESS] Items delivered: {delivered_count}/{len(order_items)}")
            print(f"   [USER] Customer: {customer_name}")
            
        except Exception as e:
            self.print_error(f"Error processing partial delivery: {str(e)}")
            
    def process_exception_delivery(self, delivery: Dict[str, Any], delivery_id: str, status: str):
        """Process delivery exceptions"""
        try:
            print(f"\n[INTERRUPTED] Recording Delivery Exception: {status}")
            
            # Exception details
            exception_details = input("[GENERATE] Exception details: ").strip()
            contact_attempts = input("[SUPPORT] Customer contact attempts made: ").strip()
            
            # Photos/evidence
            evidence_captured = input("📸 Evidence captured? (yes/no): ").strip().lower()
            evidence_types = []
            
            if evidence_captured == 'yes':
                print("📸 Evidence types:")
                print("1. Photo of address")
                print("2. Photo of building/gate")
                print("3. Screenshot of calls")
                print("4. Other")
                
                evidence_choice = input("Select evidence type (1-4): ").strip()
                evidence_map = {
                    '1': 'ADDRESS_PHOTO',
                    '2': 'BUILDING_PHOTO',
                    '3': 'CALL_SCREENSHOT',
                    '4': 'OTHER'
                }
                evidence_types.append(evidence_map.get(evidence_choice, 'OTHER'))
                
            # Next steps
            next_steps = input("[FLOW] Planned next steps: ").strip()
            
            # Update delivery record
            self.deliveries_table.update_item(
                Key={'deliveryId': delivery_id, 'orderId': delivery['orderId']},
                UpdateExpression='SET deliveryStatus = :status, exceptionDetails = :details, '
                                'contactAttempts = :attempts, evidence = :evidence, '
                                'nextSteps = :next_steps, attemptedAt = :attempted, '
                                'completedBy = :rider, updatedAt = :updated',
                ExpressionAttributeValues={
                    ':status': status,
                    ':details': exception_details,
                    ':attempts': contact_attempts,
                    ':evidence': evidence_types,
                    ':next_steps': next_steps,
                    ':attempted': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':rider': self.current_rider_id,
                    ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            # Log audit
            self.log_audit('DELIVERY_EXCEPTION', delivery_id, 
                          f"Delivery exception: {status}. Details: {exception_details}")
            
            self.print_success("[INTERRUPTED] Delivery exception recorded!")
            print(f"   [GENERATE] Status: {status}")
            print(f"   [CLIPBOARD] Details: {exception_details}")
            
        except Exception as e:
            self.print_error(f"Error processing delivery exception: {str(e)}")
        
    def record_delivery_exceptions(self):
        """Record delivery exceptions and issues"""
        self.clear_screen()
        self.print_header("RECORD DELIVERY EXCEPTIONS")
        
        try:
            print("[GENERATE] Delivery Exception Recording System")
            print("[NOTE] Report issues encountered during delivery attempts")
            
            # Exception types
            print(f"\n[INTERRUPTED] Exception Types:")
            print("1. [HOME] Address Issues")
            print("2. [USER] Customer Issues")
            print("3. [ORDER] Product Issues")
            print("4. 🚗 Vehicle/Transport Issues")
            print("5. 🌧️ Weather/Environment Issues")
            print("6. [TOOL] System/Technical Issues")
            print("7. [CLIPBOARD] Documentation Issues")
            print("8. 🚫 Security/Safety Issues")
            
            exception_choice = input("\n[TARGET] Select exception type (1-8): ").strip()
            
            exception_map = {
                '1': 'ADDRESS_ISSUES',
                '2': 'CUSTOMER_ISSUES',
                '3': 'PRODUCT_ISSUES',
                '4': 'VEHICLE_ISSUES',
                '5': 'WEATHER_ISSUES',
                '6': 'SYSTEM_ISSUES',
                '7': 'DOCUMENTATION_ISSUES',
                '8': 'SECURITY_ISSUES'
            }
            
            exception_type = exception_map.get(exception_choice, 'OTHER')
            
            # Exception details
            order_id = input("\n[ORDER] Order ID (if applicable): ").strip()
            exception_description = input("[GENERATE] Exception Description: ").strip()
            
            # Impact assessment
            print(f"\n[TRACK] Impact Level:")
            print("1. 🟢 Low - Minor delay expected")
            print("2. 🟡 Medium - Significant delay possible")
            print("3. 🔴 High - Delivery at risk")
            print("4. [ISSUE] Critical - Immediate action required")
            
            impact_choice = input("\n[TARGET] Select impact level (1-4): ").strip()
            
            impact_map = {
                '1': 'LOW',
                '2': 'MEDIUM',
                '3': 'HIGH',
                '4': 'CRITICAL'
            }
            
            impact_level = impact_map.get(impact_choice, 'MEDIUM')
            
            # Actions taken
            actions_taken = input("\n[TOOL] Actions already taken: ").strip()
            
            # Support needed
            support_needed = input("[HELP] Support needed? (yes/no): ").strip().lower()
            support_type = ""
            
            if support_needed == 'yes':
                print("[HELP] Support types:")
                print("1. [SUPPORT] Customer contact assistance")
                print("2. 🗺️ Navigation/address help")
                print("3. [TOOL] Technical support")
                print("4. 👮 Security assistance")
                print("5. 🚗 Vehicle/transport help")
                
                support_choice = input("Select support type (1-5): ").strip()
                support_map = {
                    '1': 'CUSTOMER_CONTACT',
                    '2': 'NAVIGATION_HELP',
                    '3': 'TECHNICAL_SUPPORT',
                    '4': 'SECURITY_ASSISTANCE',
                    '5': 'TRANSPORT_HELP'
                }
                support_type = support_map.get(support_choice, 'GENERAL')
                
            # Create exception record
            exception_record = {
                'exceptionId': f'EXC-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'riderId': self.current_rider_id,
                'orderId': order_id or 'N/A',
                'exceptionType': exception_type,
                'description': exception_description,
                'impactLevel': impact_level,
                'actionsTaken': actions_taken,
                'supportNeeded': support_needed == 'yes',
                'supportType': support_type,
                'reportedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'status': 'OPEN',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Store in notifications table for manager attention
            self.notifications_table.put_item(Item=exception_record)
            
            # Log audit
            self.log_audit('EXCEPTION_REPORTED', exception_record['exceptionId'], 
                          f"Exception reported: {exception_type} - {impact_level} impact")
            
            self.print_success("[SUCCESS] Delivery exception recorded!")
            print(f"   [ID] Exception ID: {exception_record['exceptionId']}")
            print(f"   [INTERRUPTED] Type: {exception_type}")
            print(f"   [TRACK] Impact: {impact_level}")
            
            if support_needed == 'yes':
                print(f"   [HELP] Support requested: {support_type}")
                print(f"   [SUPPORT] Support team will be notified")
                
        except Exception as e:
            self.print_error(f"Error recording delivery exception: {str(e)}")
            
        input("Press Enter to continue...")
        
    def view_delivery_history(self):
        """View comprehensive delivery history"""
        self.clear_screen()
        self.print_header("VIEW DELIVERY HISTORY")
        
        try:
            # Get all deliveries for this rider
            response = self.deliveries_table.scan()
            deliveries = response.get('Items', [])
            
            rider_deliveries = [delivery for delivery in deliveries 
                              if delivery.get('riderId') == self.current_rider_id]
            
            if not rider_deliveries:
                self.print_info("No delivery history found.")
                input("Press Enter to continue...")
                return
                
            # Sort by most recent first
            rider_deliveries.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)
            
            print(f"[TRACK] Delivery History Overview ({len(rider_deliveries)} total deliveries):")
            
            # Quick stats
            delivered_count = len([d for d in rider_deliveries if d.get('deliveryStatus') == 'DELIVERED'])
            failed_count = len([d for d in rider_deliveries if d.get('deliveryStatus') == 'FAILED'])
            success_rate = (delivered_count / len(rider_deliveries) * 100) if rider_deliveries else 0
            
            print(f"\n[REPORT] Quick Statistics:")
            print(f"   [SUCCESS] Successful: {delivered_count}")
            print(f"   [ERROR] Failed: {failed_count}")
            print(f"   [TRACK] Success Rate: {success_rate:.1f}%")
            
            # Filter options
            print(f"\n[AUDIT] View Options:")
            print("1. Recent Deliveries (Last 10)")
            print("2. Today's Deliveries")
            print("3. This Week's Deliveries")
            print("4. This Month's Deliveries")
            print("5. By Status")
            print("6. By Date Range")
            print("7. Detailed Analysis")
            
            view_choice = input("\n[TARGET] Select view option (1-7): ").strip()
            
            if view_choice == '1':
                self.show_recent_deliveries(rider_deliveries[:10])
            elif view_choice == '2':
                today_deliveries = self.filter_deliveries_by_date(rider_deliveries, 0)
                self.show_delivery_list(today_deliveries, "Today's Deliveries")
            elif view_choice == '3':
                week_deliveries = self.filter_deliveries_by_date(rider_deliveries, 7)
                self.show_delivery_list(week_deliveries, "This Week's Deliveries")
            elif view_choice == '4':
                month_deliveries = self.filter_deliveries_by_date(rider_deliveries, 30)
                self.show_delivery_list(month_deliveries, "This Month's Deliveries")
            elif view_choice == '5':
                self.show_deliveries_by_status(rider_deliveries)
            elif view_choice == '6':
                self.show_deliveries_by_date_range(rider_deliveries)
            elif view_choice == '7':
                self.show_detailed_delivery_analysis(rider_deliveries)
            else:
                self.print_error("Invalid view option.")
                
        except Exception as e:
            self.print_error(f"Error viewing delivery history: {str(e)}")
            
        input("Press Enter to continue...")
        
    def show_recent_deliveries(self, deliveries: list):
        """Show recent deliveries"""
        print(f"\n[CLIPBOARD] Recent Deliveries ({len(deliveries)} entries):")
        print("-" * 120)
        print(f"{'Date':<12} {'Order ID':<15} {'Status':<15} {'Address':<30} {'Customer':<20} {'Notes':<20}")
        print("-" * 120)
        
        for delivery in deliveries:
            delivery_date = delivery.get('deliveryDate', 'N/A')[:10] if delivery.get('deliveryDate') else 'N/A'
            status = delivery.get('deliveryStatus', 'N/A')
            address = delivery.get('deliveryAddress', 'N/A')[:29]
            customer = delivery.get('customerName', 'N/A')[:19]
            notes = delivery.get('deliveryNotes', 'N/A')[:19]
            
            print(f"{delivery_date:<12} {delivery.get('orderId', 'N/A'):<15} "
                  f"{status:<15} {address:<30} {customer:<20} {notes:<20}")
                  
        print("-" * 120)
        
    def filter_deliveries_by_date(self, deliveries: list, days_back: int) -> list:
        """Filter deliveries by date range"""
        if days_back == 0:
            # Today only
            today = datetime.now().date()
            return [d for d in deliveries 
                   if d.get('deliveryDate', '')[:10] == str(today)]
        else:
            # Last N days
            cutoff_date = datetime.now() - timedelta(days=days_back)
            return [d for d in deliveries 
                   if datetime.fromisoformat(d.get('updatedAt', '').replace('Z', '+00:00')) >= cutoff_date]
                   
    def show_delivery_list(self, deliveries: list, title: str):
        """Show delivery list with title"""
        print(f"\n[CLIPBOARD] {title} ({len(deliveries)} deliveries):")
        if deliveries:
            self.show_recent_deliveries(deliveries)
        else:
            print("   No deliveries found for this period.")
            
    def show_deliveries_by_status(self, deliveries: list):
        """Show deliveries filtered by status"""
        status_filter = input("\n[TRACK] Enter status (DELIVERED/FAILED/IN_TRANSIT/etc.): ").strip().upper()
        filtered_deliveries = [d for d in deliveries if d.get('deliveryStatus') == status_filter]
        self.show_delivery_list(filtered_deliveries, f"{status_filter} Deliveries")
        
    def show_deliveries_by_date_range(self, deliveries: list):
        """Show deliveries for a specific date range"""
        start_date = input("[DATE] Start date (YYYY-MM-DD): ").strip()
        end_date = input("[DATE] End date (YYYY-MM-DD): ").strip()
        
        # Simple date filtering (in production, would use proper date parsing)
        filtered_deliveries = [d for d in deliveries 
                             if start_date <= d.get('deliveryDate', '')[:10] <= end_date]
        
        self.show_delivery_list(filtered_deliveries, f"Deliveries from {start_date} to {end_date}")
        
    def show_detailed_delivery_analysis(self, deliveries: list):
        """Show detailed delivery analysis"""
        print(f"\n[TRACK] Detailed Delivery Analysis:")
        print("=" * 80)
        
        # Status breakdown
        status_counts = {}
        for delivery in deliveries:
            status = delivery.get('deliveryStatus', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        print(f"\n[REPORT] Status Breakdown:")
        for status, count in status_counts.items():
            percentage = (count / len(deliveries) * 100) if deliveries else 0
            print(f"   {status}: {count} ({percentage:.1f}%)")
            
        # Monthly trends (simplified)
        monthly_counts = {}
        for delivery in deliveries:
            month = delivery.get('deliveryDate', '')[:7] if delivery.get('deliveryDate') else 'Unknown'
            monthly_counts[month] = monthly_counts.get(month, 0) + 1
            
        print(f"\n[DATE] Monthly Distribution:")
        for month, count in sorted(monthly_counts.items(), reverse=True)[:6]:
            print(f"   {month}: {count} deliveries")
            
        # Average delivery time (if available)
        completed_deliveries = [d for d in deliveries if d.get('deliveryStatus') == 'DELIVERED']
        if completed_deliveries:
            print(f"\n⏰ Performance Metrics:")
            print(f"   [ORDER] Total Completed: {len(completed_deliveries)}")
            print(f"   [REPORT] Completion Rate: {len(completed_deliveries)/len(deliveries)*100:.1f}%")
            
            # Customer satisfaction average
            satisfactions = [d.get('satisfactionRating', 0) for d in completed_deliveries 
                           if d.get('satisfactionRating')]
            if satisfactions:
                avg_satisfaction = sum(satisfactions) / len(satisfactions)
                print(f"   [RATING] Avg Satisfaction: {avg_satisfaction:.1f}/5.0")
        
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
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
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