#!/usr/bin/env python3
"""
Multi-Order Fulfillment Simulator
Creates multiple orders using different customers, warehouse managers, and delivery personnel
Provides comprehensive reporting on order distribution and user assignments
"""

import sys
import os
import time
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from collections import defaultdict

# Add the parent directory to the path to import the portals
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from awslabs.inventory_management_mcp_server.actors.customer_portal import CustomerPortal
from awslabs.inventory_management_mcp_server.actors.warehouse_manager_portal import WarehouseManagerPortal
from awslabs.inventory_management_mcp_server.actors.delivery_portal import DeliveryPortal

class MultiOrderFulfillmentSimulator:
    """Simulates multiple order fulfillment workflows with different users"""
    
    def __init__(self):
        self.customer_portal = CustomerPortal()
        self.warehouse_portal = WarehouseManagerPortal()
        self.delivery_portal = DeliveryPortal()
        
        # Multiple test users for realistic simulation
        self.test_customers = [
            {
                'email': 'john.doe@example.com',
                'password': 'password123',
                'firstName': 'John',
                'lastName': 'Doe',
                'phone': '+919876543001',
                'address': {
                    'type': 'home',
                    'street': '123 MG Road',
                    'area': 'Banjara Hills',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500034',
                    'landmark': 'Near Metro Station'
                }
            },
            {
                'email': 'jane.smith@example.com',
                'password': 'password123',
                'firstName': 'Jane',
                'lastName': 'Smith',
                'phone': '+919876543002',
                'address': {
                    'type': 'home',
                    'street': '456 Jubilee Hills',
                    'area': 'Jubilee Hills',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500033',
                    'landmark': 'Near Shopping Mall'
                }
            },
            {
                'email': 'rajesh.sharma@example.com',
                'password': 'password123',
                'firstName': 'Rajesh',
                'lastName': 'Sharma',
                'phone': '+919876543003',
                'address': {
                    'type': 'home',
                    'street': '789 HITEC City',
                    'area': 'HITEC City',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500081',
                    'landmark': 'Near IT Park'
                }
            },
            {
                'email': 'priya.patel@example.com',
                'password': 'password123',
                'firstName': 'Priya',
                'lastName': 'Patel',
                'phone': '+919876543004',
                'address': {
                    'type': 'office',
                    'street': '321 Gachibowli',
                    'area': 'Gachibowli',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500032',
                    'landmark': 'Near Tech Tower'
                }
            },
            {
                'email': 'amit.singh@example.com',
                'password': 'password123',
                'firstName': 'Amit',
                'lastName': 'Singh',
                'phone': '+919876543005',
                'address': {
                    'type': 'home',
                    'street': '654 Kondapur',
                    'area': 'Kondapur',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500084',
                    'landmark': 'Near Metro Station'
                }
            }
        ]
        
        # Multiple warehouse managers/staff
        self.warehouse_managers = [
            {
                'email': 'warehouse@promodeagro.com',
                'password': 'password123',
                'name': 'Amit Patel',
                'role': 'Warehouse Manager',
                'department': 'Warehouse Operations'
            },
            {
                'email': 'logistics@promodeagro.com',
                'password': 'password123',
                'name': 'Suresh Kumar',
                'role': 'Logistics Manager',
                'department': 'Logistics & Transportation'
            }
        ]
        
        # Multiple delivery personnel
        self.delivery_personnel = [
            {
                'employee_id': 'EMP-001',
                'password': 'password123',
                'name': 'Ravi Kumar',
                'vehicle': 'MH12AB1234 (Bike)',
                'shift': 'Morning',
                'area': 'Central Hyderabad'
            },
            {
                'employee_id': 'EMP-002',
                'password': 'password123',
                'name': 'Suresh Reddy',
                'vehicle': 'MH12CD5678 (Bike)',
                'shift': 'Evening',
                'area': 'West Hyderabad'
            },
            {
                'employee_id': 'EMP-003',
                'password': 'password123',
                'name': 'Amit Singh',
                'vehicle': 'MH12EF9012 (Van)',
                'shift': 'Full Day',
                'area': 'East Hyderabad'
            },
            {
                'employee_id': 'EMP-004',
                'password': 'password123',
                'name': 'Priya Sharma',
                'vehicle': 'MH12GH3456 (Bike)',
                'shift': 'Morning',
                'area': 'North Hyderabad'
            },
            {
                'employee_id': 'EMP-005',
                'password': 'password123',
                'name': 'Kiran Patel',
                'vehicle': 'MH12IJ7890 (Van)',
                'shift': 'Evening',
                'area': 'South Hyderabad'
            }
        ]
        
        # Product catalog for varied orders
        self.product_catalog = [
            {'productID': 'prod-001', 'name': 'Fresh Tomatoes', 'price': 45.00, 'variant': 'Premium Quality - 1kg'},
            {'productID': 'prod-002', 'name': 'Organic Potatoes', 'price': 35.00, 'variant': 'Organic - 1kg'},
            {'productID': 'prod-003', 'name': 'Fresh Onions', 'price': 25.00, 'variant': 'Regular - 1kg'},
            {'productID': 'prod-004', 'name': 'Green Vegetables', 'price': 55.00, 'variant': 'Mixed Pack - 1kg'},
            {'productID': 'prod-005', 'name': 'Fresh Fruits', 'price': 85.00, 'variant': 'Seasonal Mix - 1kg'},
            {'productID': 'prod-006', 'name': 'Organic Rice', 'price': 120.00, 'variant': 'Basmati - 5kg'},
            {'productID': 'prod-007', 'name': 'Fresh Milk', 'price': 28.00, 'variant': 'Full Cream - 1L'},
            {'productID': 'prod-008', 'name': 'Organic Eggs', 'price': 65.00, 'variant': 'Farm Fresh - 12 pieces'}
        ]
        
        # Tracking data
        self.orders_created = []
        self.user_assignments = {
            'customers': defaultdict(list),
            'warehouse_managers': defaultdict(list),
            'delivery_personnel': defaultdict(list)
        }
        self.order_stats = {
            'total_orders': 0,
            'successful_deliveries': 0,
            'total_value': 0.0,
            'processing_time': 0
        }
        
    def print_simulation_header(self, title: str):
        """Print simulation section header"""
        print("\n" + "=" * 100)
        print(f"🎬 [MULTI-ORDER SIMULATION] {title}")
        print("=" * 100)
        
    def print_step(self, step: str, status: str = "RUNNING"):
        """Print simulation step"""
        status_emoji = {
            'RUNNING': '🔄',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'INFO': 'ℹ️'
        }
        print(f"\n{status_emoji.get(status, '🔄')} {step}")
        print("-" * 80)
        
    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input"""
        input(f"\n💡 {message}")
        
    def get_user_input_for_simulation(self):
        """Get simulation parameters from user"""
        try:
            print("🎯 MULTI-ORDER SIMULATION CONFIGURATION")
            print("=" * 60)
            
            # Get number of orders
            while True:
                try:
                    num_orders = int(input("📦 How many orders to simulate? (1-20): ").strip())
                    if 1 <= num_orders <= 20:
                        break
                    else:
                        print("❌ Please enter a number between 1 and 20")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            # Get simulation speed
            print("\n⚡ Simulation Speed:")
            print("1. Fast (minimal delays)")
            print("2. Normal (with delays)")
            print("3. Slow (detailed view)")
            
            while True:
                try:
                    speed_choice = int(input("Select speed (1-3): ").strip())
                    if 1 <= speed_choice <= 3:
                        break
                    else:
                        print("❌ Please enter 1, 2, or 3")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            speed_map = {1: 'fast', 2: 'normal', 3: 'slow'}
            simulation_speed = speed_map[speed_choice]
            
            # Get detailed reporting option
            detailed_report = input("\n📊 Generate detailed report? (y/n): ").strip().lower() == 'y'
            
            return {
                'num_orders': num_orders,
                'speed': simulation_speed,
                'detailed_report': detailed_report
            }
            
        except KeyboardInterrupt:
            print("\n⚠️ Configuration cancelled")
            return None

    def create_random_cart(self):
        """Create a random cart with 1-4 products"""
        cart = []
        num_products = random.randint(1, 4)
        selected_products = random.sample(self.product_catalog, num_products)
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            total = product['price'] * quantity
            
            cart.append({
                'productID': product['productID'],
                'productName': product['name'],
                'quantity': quantity,
                'price': product['price'],
                'variant': product['variant'],
                'total': total
            })
        
        return cart

    def create_order_for_customer(self, customer, order_number):
        """Create a single order for a specific customer"""
        try:
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # Authenticate customer
            self.customer_portal.current_user = {
                'userID': f"user-{customer['firstName'].lower()}-{random.randint(100, 999)}",
                'email': customer['email'],
                'firstName': customer['firstName'],
                'lastName': customer['lastName'],
                'phone': customer['phone'],
                'status': 'active',
                'emailVerified': True
            }
            
            # Create random cart
            cart = self.create_random_cart()
            cart_total = sum(item['total'] for item in cart)
            delivery_charge = 25.00
            final_total = cart_total + delivery_charge
            
            # Create address
            address_data = {
                'userID': self.customer_portal.current_user.get('userID'),
                'addressID': f"addr-{random.randint(1000, 9999)}",
                **customer['address'],
                'isDefault': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
            
            # Create delivery slot
            slot_data = {
                'slotID': f'slot-{random.choice(["morning", "afternoon", "evening"])}-{random.randint(1, 3)}',
                'slotName': random.choice(['Morning Slot', 'Afternoon Slot', 'Evening Slot']),
                'timeRange': random.choice(['9:00 AM - 12:00 PM', '2:00 PM - 5:00 PM', '6:00 PM - 9:00 PM']),
                'date': (datetime.now() + timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d'),
                'deliveryCharge': delivery_charge
            }
            
            # Create order data
            order_data = {
                'orderID': order_id,
                'customerEmail': customer['email'],
                'userID': self.customer_portal.current_user.get('userID'),
                'customerName': f"{customer['firstName']} {customer['lastName']}",
                'customerPhone': customer['phone'],
                'items': cart,
                'deliveryAddress': address_data,
                'deliverySlot': slot_data,
                'cartTotal': Decimal(str(cart_total)),
                'deliveryCharge': Decimal(str(delivery_charge)),
                'totalAmount': Decimal(str(final_total)),
                'paymentMethod': random.choice(['online', 'cod']),
                'status': 'placed',
                'orderDate': datetime.now(timezone.utc).isoformat(),
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
            
            # Store order in database
            try:
                self.customer_portal.orders_table.put_item(Item=order_data)
                print(f"✅ Order {order_id} created in database")
            except Exception as e:
                print(f"⚠️ Database storage failed for {order_id}: {str(e)}")
            
            # Track order
            self.orders_created.append({
                'orderID': order_id,
                'customer': f"{customer['firstName']} {customer['lastName']}",
                'customerEmail': customer['email'],
                'totalAmount': float(final_total),
                'items': len(cart),
                'area': customer['address']['area'],
                'pincode': customer['address']['pincode'],
                'paymentMethod': order_data['paymentMethod']
            })
            
            # Track customer usage
            self.user_assignments['customers'][customer['email']].append(order_id)
            
            print(f"📦 Order #{order_number}: {order_id}")
            print(f"   Customer: {customer['firstName']} {customer['lastName']}")
            print(f"   Items: {len(cart)} products")
            print(f"   Total: ₹{final_total:.2f}")
            print(f"   Area: {customer['address']['area']}")
            
            return order_id
            
        except Exception as e:
            print(f"❌ Failed to create order for {customer['firstName']}: {str(e)}")
            return None

    def process_orders_batch(self, warehouse_manager, orders_batch):
        """Process a batch of orders with a specific warehouse manager"""
        try:
            # Authenticate warehouse manager
            self.warehouse_portal.current_user = {
                'userID': f"user-warehouse-{random.randint(100, 999)}",
                'email': warehouse_manager['email'],
                'firstName': warehouse_manager['name'].split()[0],
                'lastName': warehouse_manager['name'].split()[-1],
                'roles': ['warehouse_manager'],
                'status': 'active'
            }
            
            print(f"👤 Warehouse Manager: {warehouse_manager['name']} ({warehouse_manager['email']})")
            
            processed_orders = []
            
            for order in orders_batch:
                order_id = order['orderID']
                
                # Pack order
                try:
                    customer_email = order['customerEmail']
                    self.warehouse_portal.orders_table.update_item(
                        Key={
                            'orderID': order_id,
                            'customerEmail': customer_email
                        },
                        UpdateExpression='SET #status = :status, #packed_at = :packed_at, #packed_by = :packed_by',
                        ExpressionAttributeNames={
                            '#status': 'status',
                            '#packed_at': 'packedAt',
                            '#packed_by': 'packedBy'
                        },
                        ExpressionAttributeValues={
                            ':status': 'packed',
                            ':packed_at': datetime.now(timezone.utc).isoformat(),
                            ':packed_by': self.warehouse_portal.current_user.get('userID')
                        }
                    )
                    print(f"   📦 Packed: {order_id}")
                except Exception as e:
                    print(f"   ⚠️ Pack failed for {order_id}: {str(e)}")
                
                # Create route
                route_id = f"RT-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
                route_data = {
                    'entityID': route_id,
                    'entityType': 'delivery_route',
                    'routeID': route_id,
                    'routeName': f'Route to {order["area"]}',
                    'routeDate': datetime.now().date().isoformat(),
                    'orders': [order_id],
                    'totalOrders': 1,
                    'completedOrders': 0,
                    'status': 'planned',
                    'targetPincode': order['pincode'],
                    'createdBy': self.warehouse_portal.current_user.get('userID'),
                    'createdAt': datetime.now(timezone.utc).isoformat()
                }
                
                try:
                    self.warehouse_portal.logistics_table.put_item(Item=route_data)
                    print(f"   🗺️ Route created: {route_id}")
                except Exception as e:
                    print(f"   ⚠️ Route creation failed for {route_id}: {str(e)}")
                
                # Assign random delivery personnel
                assigned_rider = random.choice(self.delivery_personnel)
                
                try:
                    # Update route with rider
                    self.warehouse_portal.logistics_table.update_item(
                        Key={
                            'entityID': route_id,
                            'entityType': 'delivery_route'
                        },
                        UpdateExpression='SET #driver_id = :driver_id, #driver_name = :driver_name',
                        ExpressionAttributeNames={
                            '#driver_id': 'driverID',
                            '#driver_name': 'driverName'
                        },
                        ExpressionAttributeValues={
                            ':driver_id': assigned_rider['employee_id'],
                            ':driver_name': assigned_rider['name']
                        }
                    )
                    
                    # Update order with route
                    self.warehouse_portal.orders_table.update_item(
                        Key={
                            'orderID': order_id,
                            'customerEmail': order['customerEmail']
                        },
                        UpdateExpression='SET #route_id = :route_id, #status = :status',
                        ExpressionAttributeNames={
                            '#route_id': 'routeID',
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':route_id': route_id,
                            ':status': 'out_for_delivery'
                        }
                    )
                    print(f"   🚚 Assigned to: {assigned_rider['name']}")
                except Exception as e:
                    print(f"   ⚠️ Assignment failed for {order_id}: {str(e)}")
                
                processed_orders.append({
                    'orderID': order_id,
                    'routeID': route_id,
                    'assignedRider': assigned_rider['name'],
                    'riderEmployeeID': assigned_rider['employee_id'],
                    'warehouseManager': warehouse_manager['name']
                })
                
                # Track assignments
                self.user_assignments['warehouse_managers'][warehouse_manager['email']].append(order_id)
                self.user_assignments['delivery_personnel'][assigned_rider['employee_id']].append(order_id)
            
            return processed_orders
            
        except Exception as e:
            print(f"❌ Batch processing failed: {str(e)}")
            return []

    def deliver_orders_batch(self, processed_orders):
        """Simulate delivery of processed orders"""
        try:
            delivered_orders = []
            
            for order_info in processed_orders:
                order_id = order_info['orderID']
                route_id = order_info['routeID']
                rider_name = order_info['assignedRider']
                rider_id = order_info['riderEmployeeID']
                
                # Set delivery personnel
                self.delivery_portal.current_user = {
                    'staffID': f'staff-{rider_id}',
                    'employeeID': rider_id,
                    'name': rider_name,
                    'department': 'delivery',
                    'status': 'active'
                }
                
                # Simulate delivery
                delivery_success = random.choice([True, True, True, False])  # 75% success rate
                
                if delivery_success:
                    # Complete delivery
                    delivery_time = datetime.now(timezone.utc).isoformat()
                    
                    try:
                        # Find customer email for this order
                        customer_email = None
                        for order in self.orders_created:
                            if order['orderID'] == order_id:
                                customer_email = order['customerEmail']
                                break
                        
                        if customer_email:
                            self.delivery_portal.orders_table.update_item(
                                Key={
                                    'orderID': order_id,
                                    'customerEmail': customer_email
                                },
                                UpdateExpression='SET #status = :status, #delivery_time = :delivery_time, #delivered_by = :delivered_by',
                                ExpressionAttributeNames={
                                    '#status': 'status',
                                    '#delivery_time': 'deliveryTime',
                                    '#delivered_by': 'deliveredBy'
                                },
                                ExpressionAttributeValues={
                                    ':status': 'delivered',
                                    ':delivery_time': delivery_time,
                                    ':delivered_by': rider_id
                                }
                            )
                        
                        print(f"   ✅ Delivered: {order_id} by {rider_name}")
                        self.order_stats['successful_deliveries'] += 1
                        
                    except Exception as e:
                        print(f"   ⚠️ Delivery update failed for {order_id}: {str(e)}")
                    
                    delivered_orders.append({
                        **order_info,
                        'status': 'delivered',
                        'deliveryTime': delivery_time
                    })
                else:
                    print(f"   ❌ Failed delivery: {order_id} by {rider_name}")
                    delivered_orders.append({
                        **order_info,
                        'status': 'failed_delivery',
                        'failureReason': random.choice(['Customer not available', 'Wrong address', 'Payment issue'])
                    })
            
            return delivered_orders
            
        except Exception as e:
            print(f"❌ Delivery batch processing failed: {str(e)}")
            return []

    def generate_comprehensive_report(self, config, all_delivered_orders):
        """Generate comprehensive final report"""
        try:
            self.print_simulation_header("COMPREHENSIVE SIMULATION REPORT")
            
            print("📊 SIMULATION OVERVIEW:")
            print(f"   📦 Total Orders Requested: {config['num_orders']}")
            print(f"   ✅ Orders Successfully Created: {len(self.orders_created)}")
            print(f"   🚚 Orders Successfully Delivered: {self.order_stats['successful_deliveries']}")
            print(f"   ❌ Failed Deliveries: {len(self.orders_created) - self.order_stats['successful_deliveries']}")
            
            total_value = sum(order['totalAmount'] for order in self.orders_created)
            print(f"   💰 Total Order Value: ₹{total_value:,.2f}")
            
            success_rate = (self.order_stats['successful_deliveries'] / len(self.orders_created) * 100) if self.orders_created else 0
            print(f"   📈 Delivery Success Rate: {success_rate:.1f}%")
            
            print("\n" + "=" * 80)
            
            # Customer usage report
            print("👥 CUSTOMER USAGE REPORT:")
            print("-" * 50)
            for customer_email, order_ids in self.user_assignments['customers'].items():
                customer_name = next((c['firstName'] + ' ' + c['lastName'] for c in self.test_customers if c['email'] == customer_email), 'Unknown')
                customer_orders = [o for o in self.orders_created if o['customerEmail'] == customer_email]
                customer_total = sum(o['totalAmount'] for o in customer_orders)
                
                print(f"📧 {customer_name} ({customer_email}):")
                print(f"   📦 Orders: {len(order_ids)}")
                print(f"   💰 Total Spent: ₹{customer_total:,.2f}")
                print(f"   📋 Order IDs: {', '.join(order_ids)}")
                print()
            
            # Warehouse manager usage report
            print("🏭 WAREHOUSE MANAGER USAGE REPORT:")
            print("-" * 50)
            for manager_email, order_ids in self.user_assignments['warehouse_managers'].items():
                manager_name = next((w['name'] for w in self.warehouse_managers if w['email'] == manager_email), 'Unknown')
                
                print(f"📧 {manager_name} ({manager_email}):")
                print(f"   📦 Orders Processed: {len(order_ids)}")
                print(f"   📋 Order IDs: {', '.join(order_ids)}")
                print()
            
            # Delivery personnel usage report
            print("🚚 DELIVERY PERSONNEL USAGE REPORT:")
            print("-" * 50)
            for rider_id, order_ids in self.user_assignments['delivery_personnel'].items():
                rider_name = next((r['name'] for r in self.delivery_personnel if r['employee_id'] == rider_id), 'Unknown')
                rider_vehicle = next((r['vehicle'] for r in self.delivery_personnel if r['employee_id'] == rider_id), 'Unknown')
                
                delivered_count = len([o for o in all_delivered_orders if o.get('riderEmployeeID') == rider_id and o.get('status') == 'delivered'])
                failed_count = len([o for o in all_delivered_orders if o.get('riderEmployeeID') == rider_id and o.get('status') == 'failed_delivery'])
                
                print(f"🆔 {rider_name} ({rider_id}):")
                print(f"   🚛 Vehicle: {rider_vehicle}")
                print(f"   📦 Total Assigned: {len(order_ids)}")
                print(f"   ✅ Delivered: {delivered_count}")
                print(f"   ❌ Failed: {failed_count}")
                print(f"   📈 Success Rate: {(delivered_count/len(order_ids)*100):.1f}%" if order_ids else "0%")
                print(f"   📋 Order IDs: {', '.join(order_ids)}")
                print()
            
            # Area-wise distribution
            print("📍 AREA-WISE DELIVERY DISTRIBUTION:")
            print("-" * 50)
            area_stats = defaultdict(list)
            for order in self.orders_created:
                area_stats[order['area']].append(order)
            
            for area, orders in area_stats.items():
                delivered_in_area = len([o for o in all_delivered_orders if any(ord['orderID'] == o.get('orderID') for ord in orders) and o.get('status') == 'delivered'])
                total_value_area = sum(o['totalAmount'] for o in orders)
                
                print(f"📍 {area}:")
                print(f"   📦 Orders: {len(orders)}")
                print(f"   ✅ Delivered: {delivered_in_area}")
                print(f"   💰 Total Value: ₹{total_value_area:,.2f}")
                print()
            
            # Time-based analysis
            print("⏰ SIMULATION TIMING ANALYSIS:")
            print("-" * 50)
            simulation_duration = time.time() - getattr(self, 'start_time', time.time())
            avg_order_processing_time = simulation_duration / len(self.orders_created) if self.orders_created else 0
            
            print(f"🕒 Total Simulation Time: {simulation_duration:.2f} seconds")
            print(f"⚡ Average Order Processing Time: {avg_order_processing_time:.2f} seconds")
            print(f"📊 Orders per Minute: {(len(self.orders_created) / (simulation_duration / 60)):.1f}" if simulation_duration > 0 else "N/A")
            
            print("\n" + "=" * 80)
            print("🎉 MULTI-ORDER SIMULATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Report generation failed: {str(e)}")

    def run_multi_order_simulation(self):
        """Run the complete multi-order simulation"""
        try:
            self.start_time = time.time()
            
            print("🎬 AURORA SPARK - MULTI-ORDER FULFILLMENT SIMULATION")
            print("=" * 100)
            print("This simulation creates multiple orders using different users across all portals")
            print("and provides comprehensive reporting on order distribution and user assignments.")
            print("=" * 100)
            
            # Get simulation configuration
            config = self.get_user_input_for_simulation()
            if not config:
                return False
            
            print(f"\n🎯 SIMULATION CONFIGURATION:")
            print(f"   📦 Orders to create: {config['num_orders']}")
            print(f"   ⚡ Speed: {config['speed'].title()}")
            print(f"   📊 Detailed report: {'Yes' if config['detailed_report'] else 'No'}")
            
            self.wait_for_user("Press Enter to start multi-order simulation...")
            
            # Phase 1: Create multiple orders
            self.print_simulation_header("PHASE 1: CREATING MULTIPLE ORDERS")
            
            print(f"🔄 Creating {config['num_orders']} orders with different customers...")
            
            for i in range(config['num_orders']):
                customer = random.choice(self.test_customers)
                print(f"\n📦 Creating Order #{i+1}/{config['num_orders']}:")
                print(f"   Customer: {customer['firstName']} {customer['lastName']} ({customer['email']})")
                
                order_id = self.create_order_for_customer(customer, i+1)
                if order_id:
                    print(f"   ✅ Order created: {order_id}")
                else:
                    print(f"   ❌ Order creation failed")
                
                # Add delay based on speed
                if config['speed'] == 'slow':
                    time.sleep(1)
                elif config['speed'] == 'normal':
                    time.sleep(0.5)
            
            print(f"\n✅ Phase 1 Complete: {len(self.orders_created)} orders created")
            self.wait_for_user()
            
            # Phase 2: Process orders with warehouse managers
            self.print_simulation_header("PHASE 2: WAREHOUSE PROCESSING & RIDER ASSIGNMENT")
            
            # Distribute orders among warehouse managers
            orders_per_manager = len(self.orders_created) // len(self.warehouse_managers)
            remaining_orders = len(self.orders_created) % len(self.warehouse_managers)
            
            all_processed_orders = []
            order_index = 0
            
            for i, manager in enumerate(self.warehouse_managers):
                # Calculate orders for this manager
                orders_for_manager = orders_per_manager + (1 if i < remaining_orders else 0)
                if orders_for_manager == 0:
                    continue
                
                batch = self.orders_created[order_index:order_index + orders_for_manager]
                order_index += orders_for_manager
                
                print(f"\n🏭 Warehouse Manager: {manager['name']}")
                print(f"   📦 Processing {len(batch)} orders...")
                
                processed_batch = self.process_orders_batch(manager, batch)
                all_processed_orders.extend(processed_batch)
                
                if config['speed'] == 'slow':
                    time.sleep(1)
                elif config['speed'] == 'normal':
                    time.sleep(0.3)
            
            print(f"\n✅ Phase 2 Complete: {len(all_processed_orders)} orders processed and assigned")
            self.wait_for_user()
            
            # Phase 3: Deliver orders
            self.print_simulation_header("PHASE 3: ORDER DELIVERY")
            
            print(f"🚚 Delivering {len(all_processed_orders)} orders...")
            all_delivered_orders = self.deliver_orders_batch(all_processed_orders)
            
            print(f"\n✅ Phase 3 Complete: {len(all_delivered_orders)} delivery attempts completed")
            self.wait_for_user()
            
            # Generate comprehensive report
            self.generate_comprehensive_report(config, all_delivered_orders)
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Multi-order simulation interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Multi-order simulation failed: {str(e)}")
            return False


def main():
    """Main function to run the multi-order simulation"""
    try:
        simulator = MultiOrderFulfillmentSimulator()
        success = simulator.run_multi_order_simulation()
        
        if success:
            print("\n🎉 Multi-order simulation completed successfully!")
        else:
            print("\n❌ Multi-order simulation failed or was interrupted")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ System Error: {str(e)}")
        print("Please contact system administrator")


if __name__ == "__main__":
    main()
