#!/usr/bin/env python3
"""
Real Order Creation Simulator
Creates actual orders using the customer portal methods for testing
"""

import sys
import os
import random
import time
from datetime import datetime, timezone

# Add the parent directory to the path to import the customer portal
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from awslabs.inventory_management_mcp_server.actors.customer_portal import CustomerPortal

class RealOrderSimulator:
    """Creates real orders using the customer portal"""
    
    def __init__(self):
        self.portal = CustomerPortal()
        
        # Test users (from our previous simulation)
        self.test_users = [
            {'email': 'john.doe@example.com', 'password': 'password123'},
            {'email': 'jane.smith@example.com', 'password': 'password123'},
            {'email': 'rajesh.sharma@example.com', 'password': 'password123'},
            {'email': 'priya.patel@example.com', 'password': 'password123'},
            {'email': 'amit.singh@example.com', 'password': 'password123'},
            {'email': 'sneha.kumar@example.com', 'password': 'password123'},
            {'email': 'vikram.reddy@example.com', 'password': 'password123'},
            {'email': 'anita.gupta@example.com', 'password': 'password123'},
        ]
        
        # Hyderabad pincodes that have delivery slots
        self.hyderabad_pincodes = ['500008', '500001', '500003', '500016', '500018', '500028', '500038', '500072', '500081', '500084']
        
    def print_step(self, message, step=None, total=None):
        """Print step with progress"""
        if step and total:
            print(f"[{step}/{total}] {message}")
        else:
            print(f"🔄 {message}")
    
    def authenticate_user(self, email, password):
        """Authenticate a user"""
        try:
            return self.portal.authenticate_user(email, password)
        except Exception as e:
            print(f"   ❌ Authentication failed for {email}: {str(e)}")
            return False
    
    def add_sample_address(self, pincode):
        """Add a sample address for the user"""
        try:
            # Check if user already has addresses
            if self.portal.current_user.get('addresses'):
                # Use existing address
                self.portal.selected_address = self.portal.current_user['addresses'][0]
                return True
            
            # Create a new address (this would normally be interactive)
            area_names = {
                '500008': 'Nampally',
                '500001': 'Secunderabad', 
                '500003': 'Himayatnagar',
                '500016': 'Malakpet',
                '500018': 'Tarnaka',
                '500028': 'Jubilee Hills',
                '500038': 'Srinagar Colony',
                '500072': 'Chandanagar',
                '500081': 'Gachibowli',
                '500084': 'Kondapur'
            }
            
            area = area_names.get(pincode, 'Hyderabad')
            
            # Simulate adding address by directly creating one
            import uuid
            new_address = {
                'id': str(uuid.uuid4()),
                'type': 'home',
                'addressLine1': f"{random.randint(1, 999)} {area} Colony",
                'addressLine2': f"Flat {random.randint(101, 505)}",
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': pincode,
                'landmark': f"Near {area} Metro Station",
                'isDefault': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
            
            # Add to user's addresses
            if 'addresses' not in self.portal.current_user:
                self.portal.current_user['addresses'] = []
            
            self.portal.current_user['addresses'].append(new_address)
            self.portal.selected_address = new_address
            
            # Update in database
            self.portal.users_table.update_item(
                Key={
                    'userID': self.portal.current_user['userID'],
                    'email': self.portal.current_user['email']
                },
                UpdateExpression='SET addresses = :addresses',
                ExpressionAttributeValues={
                    ':addresses': self.portal.current_user['addresses']
                }
            )
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to add address: {str(e)}")
            return False
    
    def select_delivery_slot(self, pincode):
        """Select a delivery slot for the given pincode"""
        try:
            # Get available slots
            slots = self.portal.get_available_slots(pincode)
            if not slots:
                print(f"   ⚠️  No delivery slots available for {pincode}")
                return False
            
            # Select a random slot
            selected_slot = random.choice(slots)
            self.portal.selected_slot = selected_slot
            
            slot_info = selected_slot.get('slotInfo', {})
            print(f"   ✅ Selected slot: {slot_info.get('timeSlot', 'Unknown')} - ₹{slot_info.get('deliveryCharge', 0)}")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to select delivery slot: {str(e)}")
            return False
    
    def add_products_to_cart(self, num_products=3):
        """Add random products to cart"""
        try:
            # Get available products
            products = self.portal.list_products()
            if not products:
                print("   ⚠️  No products available")
                return False
            
            # Filter active products
            active_products = [p for p in products if p.get('status') == 'active']
            if not active_products:
                print("   ⚠️  No active products available")
                return False
            
            # Clear existing cart
            self.portal.cart = []
            
            # Add random products
            selected_products = random.sample(active_products, min(num_products, len(active_products)))
            
            for product in selected_products:
                product_id = product.get('productID')
                quantity = random.randint(1, 3)
                
                # Check if product has variants
                if product.get('hasVariants') and product.get('variants'):
                    variant = random.choice(product['variants'])
                    variant_id = variant.get('variantID')
                    success = self.portal.add_to_cart(product_id, quantity, variant_id)
                else:
                    success = self.portal.add_to_cart(product_id, quantity)
                
                if success:
                    product_name = product.get('name', 'Unknown')
                    print(f"   ✅ Added {quantity}x {product_name}")
                else:
                    print(f"   ⚠️  Failed to add {product.get('name', 'Unknown')}")
            
            return len(self.portal.cart) > 0
            
        except Exception as e:
            print(f"   ❌ Failed to add products to cart: {str(e)}")
            return False
    
    def create_order_for_user(self, user_email, user_password):
        """Create a complete order for a user"""
        try:
            print(f"🔄 Creating order for {user_email}")
            
            # Step 1: Authenticate user
            if not self.authenticate_user(user_email, user_password):
                return False
            
            print(f"   ✅ Authenticated as {self.portal.current_user.get('firstName', '')} {self.portal.current_user.get('lastName', '')}")
            
            # Step 2: Add products to cart
            if not self.add_products_to_cart():
                return False
            
            print(f"   ✅ Added {len(self.portal.cart)} products to cart")
            
            # Step 3: Set address with Hyderabad pincode
            pincode = random.choice(self.hyderabad_pincodes)
            if not self.add_sample_address(pincode):
                return False
            
            print(f"   ✅ Set delivery address in {pincode}")
            
            # Step 4: Select delivery slot
            if not self.select_delivery_slot(pincode):
                return False
            
            # Step 5: Place the order
            print("   🔄 Placing order...")
            
            # Temporarily redirect input to simulate user confirmation
            import builtins
            
            # Simulate user confirming the order
            original_input = builtins.input
            builtins.input = lambda prompt: 'y'
            
            try:
                success = self.portal.place_order()
                if success:
                    print("   🎉 Order placed successfully!")
                    return True
                else:
                    print("   ❌ Order placement failed")
                    return False
            finally:
                # Restore original input
                builtins.input = original_input
            
        except Exception as e:
            print(f"   ❌ Failed to create order for {user_email}: {str(e)}")
            return False
        finally:
            # Clear portal state
            self.portal.current_user = None
            self.portal.cart = []
            self.portal.selected_address = None
            self.portal.selected_slot = None
    
    def run_order_simulation(self, num_orders=10):
        """Run the order creation simulation"""
        print("🚀 Real Order Creation Simulation")
        print("=" * 60)
        print(f"Creating {num_orders} real orders using customer portal methods")
        print("=" * 60)
        
        successful_orders = 0
        failed_orders = 0
        
        for i in range(num_orders):
            # Select a random user
            user = random.choice(self.test_users)
            
            self.print_step(f"Creating order {i+1}", i+1, num_orders)
            
            if self.create_order_for_user(user['email'], user['password']):
                successful_orders += 1
                print(f"   ✅ Order {i+1} created successfully")
            else:
                failed_orders += 1
                print(f"   ❌ Order {i+1} failed")
            
            # Small delay between orders
            time.sleep(0.5)
            print()
        
        # Summary
        print("=" * 60)
        print("🎉 ORDER SIMULATION COMPLETED!")
        print("=" * 60)
        print(f"✅ Successful orders: {successful_orders}")
        print(f"❌ Failed orders: {failed_orders}")
        print(f"📊 Success rate: {(successful_orders/num_orders)*100:.1f}%")
        
        if successful_orders > 0:
            print(f"\n🔍 You can now:")
            print(f"   • Login to any user account and view order history")
            print(f"   • Check the Orders table in DynamoDB")
            print(f"   • Test order management features")
        
        return successful_orders

def main():
    """Main function"""
    try:
        simulator = RealOrderSimulator()
        
        # Ask user how many orders to create
        print("🛒 Real Order Creation Simulator")
        print("This will create actual orders in the database using the customer portal")
        
        try:
            num_orders = int(input("\nHow many orders would you like to create? (default: 10): ") or "10")
        except ValueError:
            num_orders = 10
        
        if num_orders <= 0:
            print("Invalid number of orders")
            return
        
        print(f"\n🎯 Creating {num_orders} orders...")
        simulator.run_order_simulation(num_orders)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
