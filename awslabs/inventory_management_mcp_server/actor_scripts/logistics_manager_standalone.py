import boto3
import getpass
import os
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional

class LogisticsManagerStandalone:
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        self.riders_table = self.dynamodb.Table('InventoryManagement-Riders')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        
        # Debug: Test riders table access
        try:
            print("DEBUG: Testing riders table access...")
            response = self.riders_table.scan(Limit=1)
            print(f"DEBUG: Riders table scan successful, found {len(response.get('Items', []))} items")
        except Exception as e:
            print(f"DEBUG: Error accessing riders table: {str(e)}")
        
        self.current_user = None
        self.current_role = None
        
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
        print(f"[INFO] {message}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"[INTERRUPTED] {message}")
        
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
        self.print_header("LOGISTICS MANAGER - LOGIN")
        
        # Test AWS connection
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your credentials:")
        print("[NOTE] Demo credentials: logistics_mgr / logistics123")
        
        # Get username and password
        username = input("\n[USER] Username: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        # Authenticate user
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'LOGISTICS_MANAGER':
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Permissions: {', '.join(user.get('permissions', []))}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            self.print_error("Only Logistics Manager role can access this system.")
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
                if self.verify_password(password, user.get('password', '')):
                    return user
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simple comparison for demo)"""
        return input_password == stored_password
        
    def create_demo_user(self):
        """Create demo logistics manager user if it doesn't exist"""
        try:
            demo_user = {
                'userId': 'logistics_mgr',
                'name': 'Rajesh Kumar',
                'email': 'rajesh@company.com',
                'role': 'LOGISTICS_MANAGER',
                'password': 'logistics123',
                'permissions': [
                    'ROUTE_PLANNING', 'DELIVERY_MANAGEMENT', 'RUNSHEET_CREATION',
                    'RIDER_ASSIGNMENT', 'PERFORMANCE_MONITORING', 'ANALYTICS'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Check if user already exists
            response = self.users_table.get_item(
                Key={'userId': 'logistics_mgr', 'role': 'LOGISTICS_MANAGER'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Logistics Manager user created!")
                self.print_info("Username: logistics_mgr")
                self.print_info("Password: logistics123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Logistics Manager main menu"""
        while True:
            self.clear_screen()
            self.print_header("LOGISTICS MANAGER DASHBOARD")
            
            if self.current_user:
                print(f"[USER] User: {self.current_user.get('name', 'Unknown')}")
                print(f"[ACCOUNT] Role: {self.current_user.get('role', 'Unknown')}")
                print(f"[EMAIL] Email: {self.current_user.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. 🗺️ Route Planning & Optimization")
            print("2.  Delivery Personnel Management")
            print("3. [CLIPBOARD] Runsheet Management")
            print("4. [TRACK] Delivery Performance Monitoring")
            print("5. [SUPPORT] Customer Communication")
            print("6. 🚛 Fleet Management")
            print("7. [REPORT] Analytics & Reports")
            print("8. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-8): ").strip()
            
            if choice == '1':
                self.route_planning_menu()
            elif choice == '2':
                self.delivery_personnel_menu()
            elif choice == '3':
                self.runsheet_management_menu()
            elif choice == '4':
                self.performance_monitoring_menu()
            elif choice == '5':
                self.customer_communication_menu()
            elif choice == '6':
                self.fleet_management_menu()
            elif choice == '7':
                self.analytics_reports_menu()
            elif choice == '8':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Logistics Manager system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def route_planning_menu(self):
        """Route Planning Operations"""
        while True:
            self.clear_screen()
            self.print_header("ROUTE PLANNING & OPTIMIZATION")
            print("1. 🗺️ Create Optimized Routes")
            print("2. [TRACK] View Route Analytics")
            print("3. [TOOL] Modify Existing Routes")
            print("4. [CLIPBOARD] Route Templates")
            print("5. [DELIVERY] Assign Routes to Riders")
            print("6. [REPORT] Route Performance Analysis")
            print("7. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-7): ").strip()
            
            if choice == '1':
                self.create_optimized_routes()
            elif choice == '2':
                self.view_route_analytics()
            elif choice == '3':
                self.modify_existing_routes()
            elif choice == '4':
                self.manage_route_templates()
            elif choice == '5':
                self.assign_routes_to_riders()
            elif choice == '6':
                self.route_performance_analysis()
            elif choice == '7':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def delivery_personnel_menu(self):
        """Delivery Personnel Management"""
        while True:
            self.clear_screen()
            self.print_header("DELIVERY PERSONNEL MANAGEMENT")
            print("1. 👥 View All Delivery Personnel")
            print("2. [ADD] Add New Delivery Personnel")
            print("3. ✏️ Update Personnel Information")
            print("4. [CLIPBOARD] Manage Personnel Assignments")
            print("5. [TRACK] Personnel Performance Review")
            print("6. [DATE] Manage Schedules & Availability")
            print("7. [DELIVERY] Vehicle Assignment")
            print("8. [PRICE] Personnel Analytics")
            print("9. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-9): ").strip()
            
            if choice == '1':
                self.view_all_personnel()
            elif choice == '2':
                self.add_new_personnel()
            elif choice == '3':
                self.update_personnel_info()
            elif choice == '4':
                self.manage_personnel_assignments()
            elif choice == '5':
                self.personnel_performance_review()
            elif choice == '6':
                self.manage_schedules_availability()
            elif choice == '7':
                self.vehicle_assignment()
            elif choice == '8':
                self.personnel_analytics()
            elif choice == '9':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
    def runsheet_management_menu(self):
        """Runsheet Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("RUNSHEET MANAGEMENT")
            print("1. [CLIPBOARD] Create Daily Runsheets")
            print("2. ✏️ Modify Runsheets in Real-time")
            print("3. [SUCCESS] Track Runsheet Completion")
            print("4. [TRACK] View Runsheet Analytics")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.create_daily_runsheets()
            elif choice == '2':
                self.modify_runsheets_realtime()
            elif choice == '3':
                self.track_runsheet_completion()
            elif choice == '4':
                self.runsheet_analytics()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def create_daily_runsheets(self):
        """Create daily runsheets from available orders"""
        self.clear_screen()
        self.print_header("CREATE DAILY RUNSHEETS")
        
        try:
            # Get orders ready for delivery
            print("DEBUG: Scanning orders table...")
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            print(f"DEBUG: Found {len(orders)} total orders")
            
            # Filter orders that are ready for delivery
            ready_orders = [order for order in orders 
                           if order.get('status') in ['READY_FOR_DISPATCH', 'READY_FOR_DELIVERY']]
            print(f"DEBUG: Found {len(ready_orders)} ready orders")
            
            if not ready_orders:
                self.print_info("No orders ready for runsheet creation.")
                self.print_info("Orders need to be in 'READY_FOR_DISPATCH' or 'READY_FOR_DELIVERY' status.")
                input("Press Enter to continue...")
                return
                
            print(f"[ORDER] Orders Ready for Runsheet Creation ({len(ready_orders)} orders):")
            print("-" * 120)
            print(f"{'Order ID':<25} {'Customer':<20} {'Amount':<12} {'Status':<20} {'Delivery Date':<15}")
            print("-" * 120)
            
            for order in ready_orders:
                delivery_date = order.get('deliveryDate', 'N/A')
                if delivery_date == 'N/A':
                    delivery_date = order.get('expectedDeliveryDate', 'N/A')
                
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{order.get('totalAmount', 0):<12} "
                      f"{order.get('status', 'N/A'):<20} "
                      f"{delivery_date:<15}")
                      
            print("-" * 120)
            
            # Get available riders with debug
            print("DEBUG: Starting riders table scan...")
            try:
                riders_response = self.riders_table.scan()
                print(f"DEBUG: Riders scan response: {riders_response}")
                riders = riders_response.get('Items', [])
                print(f"DEBUG: Found {len(riders)} riders in response")
                
                # Print each rider for debugging
                for i, rider in enumerate(riders):
                    print(f"DEBUG: Rider {i+1}: {rider}")
                    
            except Exception as e:
                print(f"ERROR scanning riders table: {str(e)}")
                print(f"ERROR type: {type(e)}")
                riders = []
            
            if not riders:
                self.print_error("No riders available for assignment.")
                print("DEBUG: No riders found - this is the issue!")
                input("Press Enter to continue...")
                return
                
            print(f"\n[DELIVERY] Available Riders ({len(riders)} riders):")
            for i, rider in enumerate(riders, 1):
                rider_name = rider.get('name', 'N/A')
                rider_id = rider.get('riderId', 'N/A')
                rider_status = rider.get('status', 'N/A')
                print(f"{i}. {rider_name} - {rider_id} - Status: {rider_status}")
            
            # Create runsheet
            print(f"\n[CLIPBOARD] Creating Runsheet...")
            
            # Select orders for runsheet
            selected_orders = []
            while True:
                order_choice = input("\n[TARGET] Select order number for runsheet (or 'done' to finish): ").strip()
                
                if order_choice.lower() == 'done':
                    break
                    
                try:
                    order_index = int(order_choice) - 1
                    if 0 <= order_index < len(ready_orders):
                        selected_order = ready_orders[order_index]
                        if selected_order not in selected_orders:
                            selected_orders.append(selected_order)
                            print(f"[SUCCESS] Added order: {selected_order.get('orderId')}")
                        else:
                            print(f"[INTERRUPTED] Order already selected.")
                    else:
                        self.print_error("Invalid order selection.")
                except ValueError:
                    self.print_error("Invalid order number.")
            
            if not selected_orders:
                self.print_info("No orders selected for runsheet.")
                input("Press Enter to continue...")
                return
            
            # Select rider
            rider_choice = input("\n[TARGET] Select rider number for assignment: ").strip()
            
            try:
                rider_index = int(rider_choice) - 1
                if 0 <= rider_index < len(riders):
                    selected_rider = riders[rider_index]
                    self.create_runsheet_with_orders(selected_orders, selected_rider)
                else:
                    self.print_error("Invalid rider selection.")
            except ValueError:
                self.print_error("Invalid rider number.")
                
        except Exception as e:
            self.print_error(f"Error creating runsheet: {str(e)}")
            print(f"DEBUG: Full error details: {type(e).__name__}: {str(e)}")
            input("Press Enter to continue...")

    def create_runsheet_with_orders(self, orders, rider):
        """Create a runsheet with selected orders and assign to rider"""
        try:
            # Generate runsheet ID
            runsheet_id = f'RUN-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            
            # Calculate total value
            total_value = sum(Decimal(str(order.get('totalAmount', 0))) for order in orders)
            
            # Update orders with rider assignment
            for order in orders:
                self.orders_table.update_item(
                    Key={'orderId': order.get('orderId'), 'customerId': order.get('customerId')},
                    UpdateExpression='SET #status = :status, assignedToRider = :rider, runsheetId = :runsheet, updatedAt = :updated',
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': 'ASSIGNED_TO_RIDER',
                        ':rider': rider.get('riderId'),
                        ':runsheet': runsheet_id,
                        ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
            
            # Log audit
            self.log_audit('RUNSHEET_CREATED', runsheet_id, f"Created runsheet with {len(orders)} orders for rider {rider.get('name')}")
            
            # Display runsheet summary
            print(f"\n[SUCCESS] Runsheet Created Successfully!")
            print(f"[DELIVERY] Runsheet ID: {runsheet_id}")
            print(f"[DELIVERY] Assigned to: {rider.get('name')} ({rider.get('riderId')})")
            print(f"[ORDER] Total Orders: {len(orders)}")
            print(f"[PRICE] Total Value: {total_value}")
            print(f"[DATE] Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n[ORDER] Orders in Runsheet:")
            for i, order in enumerate(orders, 1):
                print(f"  {i}. {order.get('orderId')} - {order.get('customerId')} - {order.get('totalAmount', 0)}")
            
        except Exception as e:
            self.print_error(f"Error creating runsheet: {str(e)}")

    def modify_runsheets_realtime(self):
        """Modify runsheets in real-time"""
        self.clear_screen()
        self.print_header("MODIFY RUNSHEETS REAL-TIME")
        self.print_info("Real-time runsheet modification functionality will be implemented.")
        input("Press Enter to continue...")

    def track_runsheet_completion(self):
        """Track runsheet completion and update order statuses"""
        self.clear_screen()
        self.print_header("TRACK RUNSHEET COMPLETION")

        try:
            # Get all orders assigned to riders
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            # Filter orders assigned to riders
            assigned_orders = [order for order in orders 
                              if order.get('status') == 'ASSIGNED_TO_RIDER']
            
            if not assigned_orders:
                self.print_info("No active runsheets found.")
                self.print_info("Orders need to be in 'ASSIGNED_TO_RIDER' status to appear here.")
                input("Press Enter to continue...")
                return
                
            print(f"[CLIPBOARD] Active Runsheets ({len(assigned_orders)} orders):")
            print("-" * 120)
            print(f"{'Order ID':<25} {'Customer':<20} {'Rider':<15} {'Status':<20} {'Assigned Date':<20}")
            print("-" * 120)
            
            for order in assigned_orders:
                assigned_date = order.get('updatedAt', 'N/A')[:19] if order.get('updatedAt') else 'N/A'
                print(f"{order.get('orderId', 'N/A'):<25} "
                      f"{order.get('customerId', 'N/A'):<20} "
                      f"{order.get('assignedToRider', 'N/A'):<15} "
                      f"{order.get('status', 'N/A'):<20} "
                      f"{assigned_date:<20}")
                      
            print("-" * 120)
            
            # Group orders by rider
            rider_assignments = {}
            for order in assigned_orders:
                rider_id = order.get('assignedToRider')
                if rider_id:
                    if rider_id not in rider_assignments:
                        rider_assignments[rider_id] = []
                    rider_assignments[rider_id].append(order)
            
            print(f"\n[DELIVERY] Runsheet Summary by Rider:")
            for rider_id, orders in rider_assignments.items():
                total_amount = sum(Decimal(str(order.get('totalAmount', 0))) for order in orders)
                print(f"  • {rider_id}: {len(orders)} orders, Total: {total_amount}")
            
            # Select order to update
            order_choice = input("\n[TARGET] Select order number to update status: ").strip()
            
            try:
                order_index = int(order_choice) - 1
                if 0 <= order_index < len(assigned_orders):
                    selected_order = assigned_orders[order_index]
                    self.update_order_delivery_status(selected_order)
                else:
                    self.print_error("Invalid order selection.")
            except ValueError:
                self.print_error("Invalid order number.")
                
        except Exception as e:
            self.print_error(f"Error tracking runsheet completion: {str(e)}")
            input("Press Enter to continue...")

    def update_order_delivery_status(self, order):
        """Update delivery status for a specific order"""
        order_id = order.get('orderId')
        customer_id = order.get('customerId')
        rider_id = order.get('assignedToRider')
        
        print(f"\n[ORDER] Updating Delivery Status for Order: {order_id}")
        print(f"[USER] Customer: {customer_id}")
        print(f"[DELIVERY] Rider: {rider_id}")
        print(f"[ORDER] Amount: {order.get('totalAmount', 0)}")
        
        print(f"\n[CLIPBOARD] Delivery Status Options:")
        print("1. �� Out for Delivery")
        print("2. [SUCCESS] Delivered Successfully")
        print("3. [ERROR] Delivery Failed")
        print("4. [FLOW] Return to Warehouse")
        print("5. [SUPPORT] Customer Not Available")
        
        status_choice = input("\n[TARGET] Select new status (1-5): ").strip()
        
        new_status = None
        status_description = ""
        
        if status_choice == '1':
            new_status = 'OUT_FOR_DELIVERY'
            status_description = "Order is out for delivery"
        elif status_choice == '2':
            new_status = 'DELIVERED'
            status_description = "Order delivered successfully"
        elif status_choice == '3':
            new_status = 'DELIVERY_FAILED'
            status_description = "Delivery failed"
        elif status_choice == '4':
            new_status = 'RETURNED_TO_WAREHOUSE'
            status_description = "Order returned to warehouse"
        elif status_choice == '5':
            new_status = 'CUSTOMER_NOT_AVAILABLE'
            status_description = "Customer not available for delivery"
        else:
            self.print_error("Invalid status choice.")
            return
        
        # Get additional details
        delivery_notes = input(f"\n[GENERATE] Delivery Notes (optional): ").strip()
        delivery_time = input(f"⏰ Delivery Time (HH:MM, optional): ").strip()
        
        try:
            # Update order status
            update_expression = 'SET #status = :status, updatedAt = :updated'
            expression_values = {
                ':status': new_status,
                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Add delivery notes if provided
            if delivery_notes:
                update_expression += ', deliveryNotes = :notes'
                expression_values[':notes'] = delivery_notes
            
            # Add delivery time if provided
            if delivery_time:
                update_expression += ', deliveryTime = :time'
                expression_values[':time'] = delivery_time
            
            # Add delivery date for completed deliveries
            if new_status == 'DELIVERED':
                update_expression += ', deliveredAt = :delivered'
                expression_values[':delivered'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            self.orders_table.update_item(
                Key={'orderId': order_id, 'customerId': customer_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues=expression_values
            )
            
            # Log audit
            self.log_audit('ORDER_STATUS_UPDATED', order_id, f"Order {order_id} status updated to {new_status} by {self.current_user.get('userId')}")
            
            self.print_success(f"[SUCCESS] Order {order_id} status updated to {new_status}!")
            self.print_info(f"[GENERATE] Notes: {delivery_notes or 'None'}")
            if delivery_time:
                self.print_info(f"⏰ Time: {delivery_time}")
            
            # If delivered, check if all orders for this rider are complete
            if new_status == 'DELIVERED':
                self.check_rider_completion(rider_id)
            
        except Exception as e:
            self.print_error(f"Error updating order status: {str(e)}")

    def check_rider_completion(self, rider_id):
        """Check if all orders assigned to a rider are completed"""
        try:
            # Get all orders for this rider
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            rider_orders = [order for order in orders 
                           if order.get('assignedToRider') == rider_id]
            
            delivered_orders = [order for order in rider_orders 
                              if order.get('status') == 'DELIVERED']
            
            if len(delivered_orders) == len(rider_orders) and len(rider_orders) > 0:
                self.print_success(f"[SUMMARY] All orders for rider {rider_id} have been delivered!")
                self.print_info(f"[TRACK] Completion: {len(delivered_orders)}/{len(rider_orders)} orders")
                
                # Calculate completion statistics
                total_amount = sum(Decimal(str(order.get('totalAmount', 0))) for order in delivered_orders)
                self.print_info(f"[PRICE] Total Delivered Value: {total_amount}")
                
        except Exception as e:
            self.print_error(f"Error checking rider completion: {str(e)}")

    def runsheet_analytics(self):
        """View runsheet analytics and performance metrics"""
        self.clear_screen()
        self.print_header("RUNSHEET ANALYTICS")
        
        try:
            # Get all orders
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            # Calculate analytics
            total_orders = len(orders)
            assigned_orders = len([o for o in orders if o.get('status') == 'ASSIGNED_TO_RIDER'])
            delivered_orders = len([o for o in orders if o.get('status') == 'DELIVERED'])
            out_for_delivery = len([o for o in orders if o.get('status') == 'OUT_FOR_DELIVERY'])
            failed_deliveries = len([o for o in orders if o.get('status') == 'DELIVERY_FAILED'])
            
            print(f"[CLIPBOARD] Runsheet Analytics Summary:")
            print("-" * 50)
            print(f"[ORDER] Total Orders: {total_orders}")
            print(f"[CLIPBOARD] Assigned to Riders: {assigned_orders}")
            print(f"[SUCCESS] Delivered: {delivered_orders}")
            print(f"[DELIVERY] Out for Delivery: {out_for_delivery}")
            print(f"[ERROR] Failed Deliveries: {failed_deliveries}")
            
            if total_orders > 0:
                delivery_rate = (delivered_orders / total_orders) * 100
                assignment_rate = (assigned_orders / total_orders) * 100
                print(f"[REPORT] Delivery Rate: {delivery_rate:.1f}%")
                print(f"[CLIPBOARD] Assignment Rate: {assignment_rate:.1f}%")
            
            # Rider performance
            print(f"\n[DELIVERY] Rider Performance:")
            riders_response = self.riders_table.scan()
            riders = riders_response.get('Items', [])
            
            for rider in riders:
                rider_orders = [o for o in orders if o.get('assignedToRider') == rider.get('riderId')]
                delivered_by_rider = [o for o in rider_orders if o.get('status') == 'DELIVERED']
                
                if rider_orders:
                    completion_rate = (len(delivered_by_rider) / len(rider_orders)) * 100
                    total_value = sum(Decimal(str(o.get('totalAmount', 0))) for o in delivered_by_rider)
                    print(f"  • {rider.get('name', 'N/A')}: {len(delivered_by_rider)}/{len(rider_orders)} delivered ({completion_rate:.1f}%) - ₹{total_value}")
            
            # Recent activity
            print(f"\n[DATE] Recent Activity (Last 7 days):")
            recent_orders = [o for o in orders if o.get('updatedAt', '') > (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()]
            print(f"  • Orders Updated: {len(recent_orders)}")
            
        except Exception as e:
            self.print_error(f"Error generating analytics: {str(e)}")
            
        input("Press Enter to continue...")

    def performance_monitoring_menu(self):
        """Performance Monitoring Operations"""
        self.clear_screen()
        self.print_header("DELIVERY PERFORMANCE MONITORING")
        self.print_info("Performance monitoring functionality will be implemented.")
        input("Press Enter to continue...")

    def customer_communication_menu(self):
        """Customer Communication Operations"""
        self.clear_screen()
        self.print_header("CUSTOMER COMMUNICATION")
        self.print_info("Customer communication functionality will be implemented.")
        input("Press Enter to continue...")

    def fleet_management_menu(self):
        """Fleet Management Operations"""
        self.clear_screen()
        self.print_header("FLEET MANAGEMENT")
        self.print_info("Fleet management functionality will be implemented.")
        input("Press Enter to continue...")

    def analytics_reports_menu(self):
        """Analytics & Reports Operations"""
        self.clear_screen()
        self.print_header("ANALYTICS & REPORTS")
        self.print_info("Analytics and reports functionality will be implemented.")
        input("Press Enter to continue...")
        
    def create_optimized_routes(self):
        """Create optimized delivery routes"""
        self.clear_screen()
        self.print_header("CREATE OPTIMIZED ROUTES")
        
        try:
            print("🗺️ Route Optimization for Delivery Efficiency")
            print("[NOTE] Create optimized routes based on location, capacity, and time constraints")
            
            # Get orders ready for routing
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            ready_orders = [order for order in orders 
                           if order.get('status') in ['READY_FOR_DISPATCH', 'READY_FOR_DELIVERY']]
            
            if not ready_orders:
                self.print_info("No orders available for route planning.")
                input("Press Enter to continue...")
                return
                
            print(f"\n[ORDER] Orders Available for Routing ({len(ready_orders)} orders):")
            print("-" * 100)
            print(f"{'Order ID':<20} {'Customer':<15} {'Address':<30} {'Amount':<10} {'Priority':<10}")
            print("-" * 100)
            
            for order in ready_orders:
                address = order.get('deliveryAddress', {})
                full_address = f"{address.get('street', '')}, {address.get('city', '')}"[:29]
                priority = order.get('priority', 'NORMAL')
                
                print(f"{order.get('orderId', 'N/A'):<20} "
                      f"{order.get('customerId', 'N/A'):<15} "
                      f"{full_address:<30} "
                      f"₹{order.get('totalAmount', 0):<9} "
                      f"{priority:<10}")
                      
            print("-" * 100)
            
            # Route optimization parameters
            print(f"\n[SETTINGS] Route Optimization Parameters:")
            print("1. [REGION] Geographic Optimization (by area/zone)")
            print("2. [TARGET] Priority-based Optimization")
            print("3. [ORDER] Capacity-based Optimization")
            print("4. ⏰ Time-window Optimization")
            print("5. [PRICE] Value-based Optimization")
            
            optimization_choice = input("\n[TARGET] Select optimization method (1-5): ").strip()
            
            optimization_methods = {
                '1': 'GEOGRAPHIC',
                '2': 'PRIORITY',
                '3': 'CAPACITY',
                '4': 'TIME_WINDOW',
                '5': 'VALUE_BASED'
            }
            
            selected_method = optimization_methods.get(optimization_choice, 'GEOGRAPHIC')
            
            # Get available riders
            riders_response = self.riders_table.scan()
            riders = riders_response.get('Items', [])
            
            if not riders:
                self.print_error("No riders available for route assignment.")
                input("Press Enter to continue...")
                return
                
            # Route parameters
            max_orders_per_route = self.get_route_parameter("Max orders per route", 8)
            max_route_duration = self.get_route_parameter("Max route duration (hours)", 8)
            
            # Generate optimized routes
            optimized_routes = self.generate_optimized_routes(
                ready_orders, riders, selected_method, 
                max_orders_per_route, max_route_duration
            )
            
            # Display optimized routes
            print(f"\n🗺️ OPTIMIZED ROUTES GENERATED")
            print("=" * 100)
            print(f"Optimization Method: {selected_method}")
            print(f"Total Routes: {len(optimized_routes)}")
            print("=" * 100)
            
            total_distance = 0
            total_time = 0
            
            for i, route in enumerate(optimized_routes, 1):
                print(f"\n[ADDRESS] Route {i}: {route['rider_name']} ({route['rider_id']})")
                print(f"   [ORDER] Orders: {len(route['orders'])}")
                print(f"   🗺️ Estimated Distance: {route['estimated_distance']:.1f} km")
                print(f"   ⏰ Estimated Time: {route['estimated_time']:.1f} hours")
                print(f"   [PRICE] Total Value: ₹{route['total_value']}")
                print(f"   [TARGET] Efficiency Score: {route['efficiency_score']:.1f}/10")
                
                total_distance += route['estimated_distance']
                total_time += route['estimated_time']
                
                print(f"   [CLIPBOARD] Order Sequence:")
                for j, order in enumerate(route['orders'], 1):
                    print(f"      {j}. {order.get('orderId')} - {order.get('customerId')} (₹{order.get('totalAmount', 0)})")
                    
            print(f"\n[TRACK] ROUTE OPTIMIZATION SUMMARY:")
            print(f"   🗺️ Total Distance: {total_distance:.1f} km")
            print(f"   ⏰ Total Time: {total_time:.1f} hours")
            print(f"   [ORDER] Total Orders: {sum(len(route['orders']) for route in optimized_routes)}")
            print(f"   [DELIVERY] Riders Utilized: {len(optimized_routes)}")
            
            # Route approval
            print(f"\n[CLIPBOARD] Route Actions:")
            print("1. [SUCCESS] Approve and Assign Routes")
            print("2. [TOOL] Modify Route Parameters")
            print("3. [SAVE] Save as Template")
            print("4. [ERROR] Cancel")
            
            action_choice = input("\n[TARGET] Select action (1-4): ").strip()
            
            if action_choice == '1':
                self.approve_and_assign_routes(optimized_routes)
            elif action_choice == '2':
                self.print_info("Returning to route optimization...")
                return self.create_optimized_routes()
            elif action_choice == '3':
                self.save_route_template(optimized_routes, selected_method)
            else:
                self.print_info("Route optimization cancelled.")
                
        except Exception as e:
            self.print_error(f"Error creating optimized routes: {str(e)}")
            
        input("Press Enter to continue...")
        
    def get_route_parameter(self, parameter_name: str, default_value: int) -> int:
        """Get route optimization parameter from user"""
        while True:
            try:
                value_input = input(f"[TRACK] {parameter_name} (default: {default_value}): ").strip()
                if not value_input:
                    return default_value
                return int(value_input)
            except ValueError:
                self.print_error(f"Invalid {parameter_name}. Please enter a valid number.")
                
    def generate_optimized_routes(self, orders: list, riders: list, method: str, 
                                  max_orders: int, max_duration: int) -> list:
        """Generate optimized routes based on selected method"""
        try:
            routes = []
            unassigned_orders = orders.copy()
            
            for rider in riders[:len(orders)//max_orders + 1]:  # Only use needed riders
                if not unassigned_orders:
                    break
                    
                # Apply optimization logic based on method
                if method == 'GEOGRAPHIC':
                    route_orders = self.select_orders_by_geography(unassigned_orders, max_orders)
                elif method == 'PRIORITY':
                    route_orders = self.select_orders_by_priority(unassigned_orders, max_orders)
                elif method == 'CAPACITY':
                    route_orders = self.select_orders_by_capacity(unassigned_orders, max_orders, rider)
                elif method == 'TIME_WINDOW':
                    route_orders = self.select_orders_by_time_window(unassigned_orders, max_orders)
                elif method == 'VALUE_BASED':
                    route_orders = self.select_orders_by_value(unassigned_orders, max_orders)
                else:
                    route_orders = unassigned_orders[:max_orders]
                
                if route_orders:
                    # Calculate route metrics
                    route_distance = self.calculate_route_distance(route_orders)
                    route_time = self.calculate_route_time(route_orders, route_distance)
                    total_value = sum(Decimal(str(order.get('totalAmount', 0))) for order in route_orders)
                    efficiency_score = self.calculate_efficiency_score(route_orders, route_distance, route_time)
                    
                    routes.append({
                        'rider_id': rider.get('riderId'),
                        'rider_name': rider.get('name', 'Unknown'),
                        'orders': route_orders,
                        'estimated_distance': route_distance,
                        'estimated_time': route_time,
                        'total_value': total_value,
                        'efficiency_score': efficiency_score,
                        'optimization_method': method
                    })
                    
                    # Remove assigned orders
                    for order in route_orders:
                        if order in unassigned_orders:
                            unassigned_orders.remove(order)
                            
            return routes
            
        except Exception as e:
            self.print_error(f"Error generating routes: {str(e)}")
            return []
            
    def select_orders_by_geography(self, orders: list, max_orders: int) -> list:
        """Select orders based on geographic proximity"""
        geographic_groups = {}
        
        for order in orders:
            address = order.get('deliveryAddress', {})
            city = address.get('city', 'Unknown')
            
            if city not in geographic_groups:
                geographic_groups[city] = []
            geographic_groups[city].append(order)
            
        # Return largest group up to max_orders
        if geographic_groups:
            largest_group = max(geographic_groups.values(), key=len)
            return largest_group[:max_orders]
        return orders[:max_orders]
        
    def select_orders_by_priority(self, orders: list, max_orders: int) -> list:
        """Select orders based on priority"""
        priority_order = {'URGENT': 1, 'HIGH': 2, 'NORMAL': 3, 'LOW': 4}
        
        sorted_orders = sorted(orders, 
                             key=lambda x: priority_order.get(x.get('priority', 'NORMAL'), 3))
        return sorted_orders[:max_orders]
        
    def select_orders_by_capacity(self, orders: list, max_orders: int, rider: dict) -> list:
        """Select orders based on rider capacity"""
        rider_capacity = rider.get('capacity', 10)  # Default capacity
        
        selected_orders = []
        current_capacity = 0
        
        for order in orders:
            order_size = order.get('orderSize', 1)  # Default size
            if current_capacity + order_size <= rider_capacity and len(selected_orders) < max_orders:
                selected_orders.append(order)
                current_capacity += order_size
                
        return selected_orders
        
    def select_orders_by_time_window(self, orders: list, max_orders: int) -> list:
        """Select orders based on delivery time windows"""
        sorted_orders = sorted(orders, 
                             key=lambda x: x.get('expectedDeliveryDate', '9999-12-31'))
        return sorted_orders[:max_orders]
        
    def select_orders_by_value(self, orders: list, max_orders: int) -> list:
        """Select orders based on value (highest value first)"""
        sorted_orders = sorted(orders, 
                             key=lambda x: float(x.get('totalAmount', 0)), reverse=True)
        return sorted_orders[:max_orders]
        
    def calculate_route_distance(self, orders: list) -> float:
        """Calculate estimated route distance"""
        base_distance = 5.0  # Base distance to start
        distance_per_order = 2.5  # Average distance between orders
        
        return base_distance + (len(orders) * distance_per_order)
        
    def calculate_route_time(self, orders: list, distance: float) -> float:
        """Calculate estimated route time"""
        travel_time = distance * 0.1  # 6 minutes per km average
        service_time = len(orders) * 0.25  # 15 minutes per order
        
        return travel_time + service_time
        
    def calculate_efficiency_score(self, orders: list, distance: float, time: float) -> float:
        """Calculate route efficiency score (1-10)"""
        if time == 0:
            return 0
            
        orders_per_hour = len(orders) / time if time > 0 else 0
        total_value = sum(float(order.get('totalAmount', 0)) for order in orders)
        value_per_km = total_value / distance if distance > 0 else 0
        
        # Normalize to 1-10 scale
        efficiency = min(10, (orders_per_hour * 2) + (value_per_km / 100))
        return max(1, efficiency)
        
    def approve_and_assign_routes(self, routes: list):
        """Approve and assign optimized routes"""
        try:
            print(f"\n[SUCCESS] APPROVING AND ASSIGNING ROUTES")
            print("=" * 60)
            
            for route in routes:
                route_id = f"ROUTE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{route['rider_id']}"
                
                # Update orders with route assignment
                for order in route['orders']:
                    self.orders_table.update_item(
                        Key={'orderId': order.get('orderId'), 'customerId': order.get('customerId')},
                        UpdateExpression='SET #status = :status, routeId = :route, assignedToRider = :rider, updatedAt = :updated',
                        ExpressionAttributeNames={'#status': 'status'},
                        ExpressionAttributeValues={
                            ':status': 'ROUTE_ASSIGNED',
                            ':route': route_id,
                            ':rider': route['rider_id'],
                            ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                self.log_audit('ROUTE_CREATED', route_id, 
                              f"Created route {route_id} for {route['rider_name']} with {len(route['orders'])} orders")
                
                print(f"[SUCCESS] Route {route_id} assigned to {route['rider_name']}")
                print(f"   [ORDER] Orders: {len(route['orders'])}")
                print(f"   🗺️ Distance: {route['estimated_distance']:.1f} km")
                print(f"   ⏰ Time: {route['estimated_time']:.1f} hours")
                
            self.print_success(f"[SUMMARY] All {len(routes)} routes have been approved and assigned!")
            
        except Exception as e:
            self.print_error(f"Error approving routes: {str(e)}")
            
    def save_route_template(self, routes: list, method: str):
        """Save route configuration as template"""
        try:
            template_name = input("\n[GENERATE] Template name: ").strip()
            if not template_name:
                template_name = f"Route_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
            template_data = {
                'templateId': f"TEMPLATE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'name': template_name,
                'optimizationMethod': method,
                'routeCount': len(routes),
                'totalOrders': sum(len(route['orders']) for route in routes),
                'totalDistance': sum(route['estimated_distance'] for route in routes),
                'totalTime': sum(route['estimated_time'] for route in routes),
                'createdBy': self.current_user.get('userId'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Store template in notifications table for retrieval
            self.notifications_table.put_item(Item=template_data)
            
            self.print_success(f"[SUCCESS] Route template '{template_name}' saved successfully!")
            
        except Exception as e:
            self.print_error(f"Error saving template: {str(e)}")
            
    def view_route_analytics(self):
        """View route analytics and performance metrics"""
        self.clear_screen()
        self.print_header("ROUTE ANALYTICS")
        
        try:
            # Get all orders with route assignments
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            route_orders = [order for order in orders if order.get('routeId')]
            
            if not route_orders:
                self.print_info("No route data available for analytics.")
                input("Press Enter to continue...")
                return
                
            # Group by routes
            routes_data = {}
            for order in route_orders:
                route_id = order.get('routeId')
                if route_id not in routes_data:
                    routes_data[route_id] = []
                routes_data[route_id].append(order)
                
            print(f"[TRACK] ROUTE ANALYTICS DASHBOARD")
            print("=" * 80)
            print(f"[ADDRESS] Total Routes: {len(routes_data)}")
            print(f"[ORDER] Total Routed Orders: {len(route_orders)}")
            print("=" * 80)
            
            # Route performance metrics
            for route_id, orders in routes_data.items():
                rider_id = orders[0].get('assignedToRider', 'Unknown')
                delivered_orders = [o for o in orders if o.get('status') == 'DELIVERED']
                total_value = sum(Decimal(str(o.get('totalAmount', 0))) for o in orders)
                
                completion_rate = (len(delivered_orders) / len(orders)) * 100 if orders else 0
                
                print(f"\n🗺️ Route: {route_id}")
                print(f"   [DELIVERY] Rider: {rider_id}")
                print(f"   [ORDER] Total Orders: {len(orders)}")
                print(f"   [SUCCESS] Delivered: {len(delivered_orders)}")
                print(f"   [REPORT] Completion Rate: {completion_rate:.1f}%")
                print(f"   [PRICE] Total Value: ₹{total_value}")
                
                # Status breakdown
                status_counts = {}
                for order in orders:
                    status = order.get('status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                print(f"   [TRACK] Status Breakdown: {dict(status_counts)}")
                
            # Overall performance
            total_delivered = len([o for o in route_orders if o.get('status') == 'DELIVERED'])
            overall_completion_rate = (total_delivered / len(route_orders)) * 100 if route_orders else 0
            
            print(f"\n[REPORT] OVERALL ROUTE PERFORMANCE:")
            print(f"   [TARGET] Overall Completion Rate: {overall_completion_rate:.1f}%")
            print(f"   [SUCCESS] Total Delivered: {total_delivered}/{len(route_orders)}")
            
        except Exception as e:
            self.print_error(f"Error viewing route analytics: {str(e)}")
            
        input("Press Enter to continue...")
        
    def modify_existing_routes(self):
        """Modify existing routes"""
        self.clear_screen()
        self.print_header("MODIFY EXISTING ROUTES")
        self.print_info("Route modification functionality allows real-time adjustments.")
        input("Press Enter to continue...")
        
    def manage_route_templates(self):
        """Manage route templates"""
        self.clear_screen()
        self.print_header("ROUTE TEMPLATES")
        self.print_info("Route template management functionality.")
        input("Press Enter to continue...")
        
    def assign_routes_to_riders(self):
        """Assign routes to riders"""
        self.clear_screen()
        self.print_header("ASSIGN ROUTES TO RIDERS")
        self.print_info("Route assignment functionality.")
        input("Press Enter to continue...")
        
    def route_performance_analysis(self):
        """Analyze route performance"""
        self.clear_screen()
        self.print_header("ROUTE PERFORMANCE ANALYSIS")
        self.print_info("Route performance analysis functionality.")
        input("Press Enter to continue...")

    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.print_success(f"Goodbye, {self.current_user.get('name', 'Unknown')}!")
            self.log_audit('LOGOUT', self.current_user.get('userId'), 'User logged out')
        self.current_user = None
        self.current_role = None

    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'action': action,
                'entityId': entity_id,
                'userId': self.current_user.get('userId') if self.current_user else 'SYSTEM',
                'userRole': self.current_role,
                'details': details,
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'ipAddress': '127.0.0.1'
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
        except Exception as e:
            print(f"Audit logging failed: {str(e)}")

    def run(self):
        """Main run method"""
        try:
            # Create demo user
            self.create_demo_user()
            
            # Authenticate user
            if not self.authenticate_user():
                return
            
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\nExiting...")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")

def main():
    """Main function"""
    app = LogisticsManagerStandalone()
    app.run()

if __name__ == "__main__":
    main() 