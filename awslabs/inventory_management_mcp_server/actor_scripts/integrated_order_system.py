#!/usr/bin/env python3
"""
Integrated Order System with Automatic Slot Selection
Combines your products/variants system with automatic delivery slot selection.
When customer provides pincode, automatically finds and assigns best delivery slot.
"""

import boto3
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List

from products_variants_api import ProductsVariantsAPI
from delivery_slots_api import DeliverySlotsAPI


class IntegratedOrderSystem:
    """Complete order processing with automatic slot selection"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        
        # Initialize APIs
        self.products_api = ProductsVariantsAPI()
        self.slots_api = DeliverySlotsAPI()
    
    def create_order_with_auto_slot_selection(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create order with automatic delivery slot selection based on pincode
        
        Args:
            order_data: Complete order information including customer address with pincode
            
        Returns:
            Dictionary with order creation result and selected delivery slot
        """
        try:
            # Step 1: Validate customer address has pincode
            customer_address = order_data.get('customerAddress', {})
            pincode = customer_address.get('pincode')
            
            if not pincode:
                return {
                    'success': False,
                    'error': 'Customer pincode is required for delivery slot selection'
                }
            
            # Step 2: Check pincode serviceability
            serviceability = self.slots_api.check_pincode_serviceability(pincode)
            if not serviceability['success'] or not serviceability['serviceable']:
                return {
                    'success': False,
                    'error': f'Sorry, we do not deliver to pincode {pincode} yet.',
                    'serviceability': serviceability
                }
            
            # Step 3: Analyze products to determine delivery requirements
            product_analysis = self._analyze_order_products(order_data['products'])
            if not product_analysis['success']:
                return product_analysis
            
            # Step 4: Auto-select best delivery slot
            slot_selection = self.slots_api.auto_select_best_slot(
                pincode=pincode,
                product_types=product_analysis['productTypes'],
                delivery_preference=order_data.get('deliveryPreference', 'fastest')
            )
            
            if not slot_selection['success']:
                return {
                    'success': False,
                    'error': 'No delivery slots available for your location',
                    'slotSelection': slot_selection
                }
            
            # Step 5: Calculate order totals including delivery charges
            order_totals = self._calculate_order_totals(
                order_data['products'],
                slot_selection['selectedSlot']['deliveryCharge']
            )
            
            # Step 6: Create order record
            order_id = f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            order_record = {
                'orderId': order_id,
                'customerId': order_data['customerId'],
                'customerName': order_data['customerName'],
                'customerPhone': order_data['customerPhone'],
                'customerEmail': order_data.get('customerEmail', ''),
                'deliveryAddress': customer_address,
                'pincode': pincode,
                'products': order_data['products'],
                'productAnalysis': product_analysis,
                'orderTotals': order_totals,
                'deliverySlot': {
                    'slotId': slot_selection['selectedSlot']['slotId'],
                    'slotName': slot_selection['selectedSlot']['slotName'],
                    'deliveryDate': slot_selection['deliveryDate'],
                    'deliveryType': slot_selection['deliveryType'],
                    'timeRange': f"{slot_selection['selectedSlot']['startTime']} - {slot_selection['selectedSlot']['endTime']}",
                    'estimatedDelivery': slot_selection['selectedSlot']['estimatedDeliveryTime'],
                    'deliveryCharge': slot_selection['selectedSlot']['deliveryCharge'],
                    'area': slot_selection['selectedSlot'].get('area', ''),
                    'city': slot_selection['selectedSlot'].get('city', '')
                },
                'paymentMethod': order_data.get('paymentMethod', 'CASH_ON_DELIVERY'),
                'paymentStatus': 'PENDING',
                'status': 'CONFIRMED',
                'specialInstructions': order_data.get('specialInstructions', ''),
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
            
            # Step 7: Save order to database
            # Using groupId as PK and customerId as SK for Orders table
            order_for_db = {
                'orderId': order_id,  # PK
                'customerId': order_data['customerId'],  # SK
                **order_record
            }
            
            self.orders_table.put_item(Item=order_for_db)
            
            # Step 8: Book the delivery slot
            slot_booking = self.slots_api.book_delivery_slot(
                {
                    'orderId': order_id,
                    'customerId': order_data['customerId'],
                    'customerAddress': customer_address,
                    'customerPhone': order_data['customerPhone'],
                    'products': order_data['products']
                },
                {
                    **slot_selection['selectedSlot'],
                    'deliveryDate': slot_selection['deliveryDate'],
                    'deliveryType': slot_selection['deliveryType']
                }
            )
            
            if not slot_booking['success']:
                return {
                    'success': False,
                    'error': 'Order created but slot booking failed',
                    'orderId': order_id,
                    'slotBookingError': slot_booking
                }
            
            # Step 9: Update stock levels for reserved items
            stock_updates = self._reserve_stock_for_order(order_data['products'])
            
            return {
                'success': True,
                'orderId': order_id,
                'orderDetails': order_record,
                'deliverySlot': slot_booking['deliveryDetails'],
                'slotBooking': {
                    'bookingId': slot_booking['bookingId'],
                    'confirmationCode': slot_booking['confirmationCode']
                },
                'stockUpdates': stock_updates,
                'serviceability': serviceability,
                'alternativeSlots': slot_selection.get('alternativeSlots', []),
                'message': f'Order {order_id} created successfully with delivery slot booked!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_delivery_options_for_address(self, pincode: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get all delivery options for a given address and products (before placing order)
        
        Args:
            pincode: Customer's pincode
            products: List of products in cart
            
        Returns:
            Dictionary with all available delivery options
        """
        try:
            # Check serviceability
            serviceability = self.slots_api.check_pincode_serviceability(pincode)
            if not serviceability['success'] or not serviceability['serviceable']:
                return {
                    'success': False,
                    'serviceable': False,
                    'pincode': pincode,
                    'message': serviceability.get('message', 'Area not serviceable')
                }
            
            # Analyze products
            product_analysis = self._analyze_order_products(products)
            if not product_analysis['success']:
                return product_analysis
            
            delivery_options = []
            
            # Get options for next 3 days
            for days_ahead in range(1, 4):
                for delivery_type in ['same_day', 'next_day', 'scheduled']:
                    # Skip same_day for future dates
                    if delivery_type == 'same_day' and days_ahead > 1:
                        continue
                    
                    target_date = (datetime.now(timezone.utc).date() + 
                                 timezone.timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                    
                    slots_result = self.slots_api.get_available_slots(
                        pincode=pincode,
                        product_types=product_analysis['productTypes'],
                        delivery_date=target_date,
                        delivery_type=delivery_type
                    )
                    
                    if slots_result['success'] and slots_result['availableSlots']:
                        delivery_options.append({
                            'date': target_date,
                            'deliveryType': delivery_type,
                            'dayName': (datetime.now(timezone.utc).date() + 
                                      timezone.timedelta(days=days_ahead)).strftime('%A'),
                            'slotsAvailable': len(slots_result['availableSlots']),
                            'slots': slots_result['availableSlots']
                        })
            
            return {
                'success': True,
                'serviceable': True,
                'pincode': pincode,
                'serviceability': serviceability,
                'productAnalysis': product_analysis,
                'deliveryOptions': delivery_options,
                'recommendedOption': delivery_options[0] if delivery_options else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_order_delivery_slot(self, order_id: str, new_slot_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update delivery slot for an existing order
        
        Args:
            order_id: Order ID
            new_slot_details: New slot information
            
        Returns:
            Dictionary with update result
        """
        try:
            # Get current order
            response = self.orders_table.query(
                KeyConditionExpression='orderId = :orderId',
                ExpressionAttributeValues={':orderId': order_id}
            )
            
            if not response['Items']:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            order = response['Items'][0]
            
            # Cancel current slot booking
            current_booking = self.slots_api.get_booking_details(order_id=order_id)
            if current_booking['success']:
                # Logic to cancel current booking would go here
                pass
            
            # Book new slot
            slot_booking = self.slots_api.book_delivery_slot(
                {
                    'orderId': order_id,
                    'customerId': order['customerId'],
                    'customerAddress': order['deliveryAddress'],
                    'customerPhone': order['customerPhone'],
                    'products': order['products']
                },
                new_slot_details
            )
            
            if not slot_booking['success']:
                return {
                    'success': False,
                    'error': 'Failed to book new delivery slot',
                    'details': slot_booking
                }
            
            # Update order record
            self.orders_table.update_item(
                Key={
                    'orderId': order_id,
                    'customerId': order['customerId']
                },
                UpdateExpression='SET deliverySlot = :newSlot, updatedAt = :timestamp',
                ExpressionAttributeValues={
                    ':newSlot': slot_booking['deliveryDetails'],
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
            
            return {
                'success': True,
                'message': 'Delivery slot updated successfully',
                'newSlotDetails': slot_booking['deliveryDetails'],
                'newBookingId': slot_booking['bookingId'],
                'newConfirmationCode': slot_booking['confirmationCode']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_order_products(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze products to determine delivery requirements"""
        try:
            product_types = set()
            total_weight = 0.0
            requires_temperature_control = False
            
            for product_item in products:
                group_id = product_item['groupId']
                variant_id = product_item['variantId']
                quantity = product_item['quantity']
                
                # Get product details
                product_result = self.products_api.get_product_by_group_id(group_id)
                if not product_result['success']:
                    return {
                        'success': False,
                        'error': f'Product {group_id} not found'
                    }
                
                product = product_result['data']
                
                # Determine product type
                product_type = product.get('productType', 'GENERAL')
                product_types.add(product_type)
                
                # Check for special requirements
                storage_req = product.get('storageRequirements', {})
                if storage_req.get('temperature') in ['REFRIGERATED', 'COOL']:
                    requires_temperature_control = True
                
                # Calculate weight for this product variant
                variant_weight = 1.0  # Default weight
                for variation in product.get('variations', []):
                    if variation['id'] == variant_id:
                        unit = variation['unit']
                        unit_quantity = variation['quantity']
                        
                        if unit.lower() == 'kg':
                            variant_weight = unit_quantity
                        elif unit.lower() in ['gms', 'g', 'grams']:
                            variant_weight = unit_quantity / 1000
                        elif unit.lower() in ['ltr', 'litre']:
                            variant_weight = unit_quantity  # Assume 1L = 1kg
                        elif unit.lower() == 'ml':
                            variant_weight = unit_quantity / 1000
                        else:
                            variant_weight = 1.0
                        break
                
                total_weight += quantity * variant_weight
            
            return {
                'success': True,
                'productTypes': list(product_types),
                'totalWeight': total_weight,
                'requiresTemperatureControl': requires_temperature_control,
                'totalItems': len(products),
                'deliveryComplexity': 'HIGH' if requires_temperature_control else 'STANDARD'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_order_totals(self, products: List[Dict[str, Any]], delivery_charge: float) -> Dict[str, Any]:
        """Calculate order totals including delivery charges"""
        try:
            subtotal = Decimal('0.00')
            total_discount = Decimal('0.00')
            
            for product_item in products:
                group_id = product_item['groupId']
                variant_id = product_item['variantId']
                quantity = product_item['quantity']
                
                # Get product details
                product_result = self.products_api.get_product_by_group_id(group_id)
                if product_result['success']:
                    product = product_result['data']
                    
                    # Find variant price
                    for variation in product.get('variations', []):
                        if variation['id'] == variant_id:
                            item_price = variation['price']
                            item_mrp = variation['mrp']
                            item_total = Decimal(str(item_price)) * quantity
                            item_discount = (Decimal(str(item_mrp)) - Decimal(str(item_price))) * quantity
                            
                            subtotal += item_total
                            total_discount += item_discount
                            break
            
            delivery_charge_decimal = Decimal(str(delivery_charge))
            total_amount = subtotal + delivery_charge_decimal
            
            return {
                'subtotal': float(subtotal),
                'totalDiscount': float(total_discount),
                'deliveryCharge': float(delivery_charge_decimal),
                'totalAmount': float(total_amount),
                'currency': 'INR'
            }
            
        except Exception as e:
            return {
                'subtotal': 0.0,
                'totalDiscount': 0.0,
                'deliveryCharge': delivery_charge,
                'totalAmount': delivery_charge,
                'currency': 'INR',
                'error': str(e)
            }
    
    def _reserve_stock_for_order(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Reserve stock for order items"""
        stock_updates = []
        
        for product_item in products:
            try:
                update_result = self.products_api.update_stock_level(
                    group_id=product_item['groupId'],
                    variant_id=product_item['variantId'],
                    stock_change=-product_item['quantity']  # Negative for reservation
                )
                stock_updates.append({
                    'groupId': product_item['groupId'],
                    'variantId': product_item['variantId'],
                    'quantityReserved': product_item['quantity'],
                    'success': update_result['success']
                })
            except Exception as e:
                stock_updates.append({
                    'groupId': product_item['groupId'],
                    'variantId': product_item['variantId'],
                    'quantityReserved': 0,
                    'success': False,
                    'error': str(e)
                })
        
        return stock_updates


# Example usage
def example_usage():
    """Example of complete order flow with automatic slot selection"""
    
    order_system = IntegratedOrderSystem()
    
    # Sample order data
    order_data = {
        'customerId': 'CUST001',
        'customerName': 'Rajesh Kumar',
        'customerPhone': '+919876543210',
        'customerEmail': 'rajesh@example.com',
        'customerAddress': {
            'address': '123 Main Street, Secunderabad',
            'pincode': '500086',
            'landmark': 'Near Metro Station',
            'city': 'Hyderabad',
            'state': 'Telangana'
        },
        'products': [
            {
                'groupId': '8b7bb419-f868-491c-bba6-7785e78b62cf',
                'variantId': '9381385120',
                'quantity': 2
            },
            {
                'groupId': '8b7bb419-f868-491c-bba6-7785e78b62cf',
                'variantId': '8628945059',
                'quantity': 1
            }
        ],
        'deliveryPreference': 'fastest',
        'paymentMethod': 'CASH_ON_DELIVERY',
        'specialInstructions': 'Please call before delivery'
    }
    
    # Check delivery options first
    delivery_options = order_system.get_delivery_options_for_address(
        pincode='500086',
        products=order_data['products']
    )
    print(f"Delivery options: {delivery_options}")
    
    # Create order with automatic slot selection
    order_result = order_system.create_order_with_auto_slot_selection(order_data)
    print(f"Order creation result: {order_result}")


if __name__ == '__main__':
    example_usage()
