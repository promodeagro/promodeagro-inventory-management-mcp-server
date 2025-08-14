#!/usr/bin/env python3
"""
Delivery Slots API - Pincode-based Automatic Slot Selection
Automatically checks available delivery slots based on customer pincode and product type.
Integrates with your existing products and variants system.
"""

import boto3
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional


class DeliverySlotsAPI:
    """API for managing delivery slots with automatic pincode-based selection"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.delivery_slots_table = self.dynamodb.Table('InventoryManagement-DeliverySlots')
        self.slot_availability_table = self.dynamodb.Table('InventoryManagement-SlotAvailability')
        self.slot_bookings_table = self.dynamodb.Table('InventoryManagement-SlotBookings')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
    
    def get_available_slots(self, pincode: str, product_types: List[str], delivery_date: str = None, delivery_type: str = 'next_day') -> Dict[str, Any]:
        """
        Get available delivery slots for a pincode and product types
        
        Args:
            pincode: Customer's pincode
            product_types: List of product types ['PERISHABLE', 'GENERAL']
            delivery_date: Target delivery date (YYYY-MM-DD), defaults to tomorrow
            delivery_type: 'same_day', 'next_day', or 'scheduled'
            
        Returns:
            Dictionary with available slots
        """
        try:
            # Default to tomorrow if no date specified
            if not delivery_date:
                tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
                delivery_date = tomorrow.strftime('%Y-%m-%d')
            
            # Determine primary product type (prioritize PERISHABLE)
            primary_product_type = 'PERISHABLE' if 'PERISHABLE' in product_types else product_types[0]
            
            # Get slot configuration for the pincode and product type
            slot_config = self._get_slot_configuration(pincode, primary_product_type)
            if not slot_config:
                return {
                    'success': False,
                    'error': f'No delivery slots available for pincode {pincode}',
                    'availableSlots': []
                }
            
            # Get current day of week
            target_date = datetime.strptime(delivery_date, '%Y-%m-%d')
            day_of_week = target_date.strftime('%a').upper()[:3]  # MON, TUE, etc.
            
            available_slots = []
            
            # Check each time slot for availability
            for time_slot in slot_config['timeSlots']:
                # Check if slot is available on this day
                if day_of_week not in time_slot['daysAvailable']:
                    continue
                
                # Check if delivery type is supported
                if delivery_type not in slot_config['deliveryTypes']:
                    continue
                
                # Get real-time availability
                availability = self._get_slot_availability(pincode, time_slot['slotId'], delivery_date, delivery_type)
                
                if availability and availability['status'] == 'AVAILABLE' and availability['availableSlots'] > 0:
                    slot_info = {
                        'slotId': time_slot['slotId'],
                        'slotName': time_slot['name'],
                        'startTime': time_slot['startTime'],
                        'endTime': time_slot['endTime'],
                        'deliveryCharge': float(time_slot['deliveryCharge']),
                        'availableCapacity': availability['availableSlots'],
                        'maxCapacity': availability['maxCapacity'],
                        'estimatedDeliveryTime': self._calculate_estimated_delivery_time(time_slot),
                        'specialRules': slot_config.get('specialRules', {}),
                        'area': slot_config.get('area', ''),
                        'city': slot_config.get('city', '')
                    }
                    available_slots.append(slot_info)
            
            # Sort slots by start time
            available_slots.sort(key=lambda x: x['startTime'])
            
            return {
                'success': True,
                'pincode': pincode,
                'deliveryDate': delivery_date,
                'deliveryType': delivery_type,
                'productType': primary_product_type,
                'availableSlots': available_slots,
                'totalSlotsAvailable': len(available_slots)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def auto_select_best_slot(self, pincode: str, product_types: List[str], delivery_preference: str = 'fastest') -> Dict[str, Any]:
        """
        Automatically select the best available slot based on preferences
        
        Args:
            pincode: Customer's pincode
            product_types: List of product types
            delivery_preference: 'fastest', 'cheapest', or 'morning'
            
        Returns:
            Dictionary with selected slot information
        """
        try:
            # Try next day first, then day after
            for days_ahead in range(1, 4):
                target_date = datetime.now(timezone.utc).date() + timedelta(days=days_ahead)
                delivery_date = target_date.strftime('%Y-%m-%d')
                
                # Try different delivery types
                delivery_types = ['next_day', 'scheduled'] if days_ahead > 1 else ['same_day', 'next_day']
                
                for delivery_type in delivery_types:
                    slots_result = self.get_available_slots(pincode, product_types, delivery_date, delivery_type)
                    
                    if slots_result['success'] and slots_result['availableSlots']:
                        available_slots = slots_result['availableSlots']
                        
                        # Select slot based on preference
                        selected_slot = None
                        
                        if delivery_preference == 'fastest':
                            # Select earliest available slot
                            selected_slot = available_slots[0]
                        elif delivery_preference == 'cheapest':
                            # Select slot with lowest delivery charge
                            selected_slot = min(available_slots, key=lambda x: x['deliveryCharge'])
                        elif delivery_preference == 'morning':
                            # Prefer morning slots
                            morning_slots = [slot for slot in available_slots if slot['startTime'] < '12:00']
                            selected_slot = morning_slots[0] if morning_slots else available_slots[0]
                        else:
                            selected_slot = available_slots[0]
                        
                        return {
                            'success': True,
                            'selectedSlot': selected_slot,
                            'deliveryDate': delivery_date,
                            'deliveryType': delivery_type,
                            'selectionReason': delivery_preference,
                            'alternativeSlots': available_slots[1:5]  # Show up to 4 alternatives
                        }
            
            return {
                'success': False,
                'error': f'No delivery slots available for pincode {pincode} in the next 3 days'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def book_delivery_slot(self, order_data: Dict[str, Any], selected_slot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Book a delivery slot for an order
        
        Args:
            order_data: Order information including customer details
            selected_slot: Selected slot information
            
        Returns:
            Dictionary with booking confirmation
        """
        try:
            booking_id = str(uuid.uuid4())
            confirmation_code = f"SLOT-{booking_id[:8].upper()}"
            
            # Calculate total weight from products
            total_weight = self._calculate_order_weight(order_data.get('products', []))
            
            # Create booking record
            booking_record = {
                'bookingId': booking_id,
                'orderId': order_data['orderId'],
                'customerId': order_data['customerId'],
                'pincode': order_data['customerAddress']['pincode'],
                'slotId': selected_slot['slotId'],
                'deliveryDate': selected_slot['deliveryDate'],
                'deliveryType': selected_slot['deliveryType'],
                'slotDetails': {
                    'slotName': selected_slot['slotName'],
                    'startTime': selected_slot['startTime'],
                    'endTime': selected_slot['endTime'],
                    'estimatedDelivery': selected_slot['estimatedDeliveryTime']
                },
                'customerAddress': order_data['customerAddress'],
                'customerPhone': order_data['customerPhone'],
                'productDetails': order_data.get('products', []),
                'deliveryCharge': Decimal(str(selected_slot['deliveryCharge'])),
                'totalWeight': Decimal(str(total_weight)),
                'riderId': None,  # Will be assigned later
                'status': 'CONFIRMED',
                'confirmationCode': confirmation_code,
                'bookedAt': datetime.now(timezone.utc).isoformat(),
                'deliveredAt': None
            }
            
            # Save booking
            self.slot_bookings_table.put_item(Item=booking_record)
            
            # Update slot availability
            self._update_slot_availability(
                order_data['customerAddress']['pincode'],
                selected_slot['slotId'],
                selected_slot['deliveryDate'],
                selected_slot['deliveryType'],
                total_weight
            )
            
            return {
                'success': True,
                'bookingId': booking_id,
                'confirmationCode': confirmation_code,
                'deliveryDetails': {
                    'slotName': selected_slot['slotName'],
                    'deliveryDate': selected_slot['deliveryDate'],
                    'timeRange': f"{selected_slot['startTime']} - {selected_slot['endTime']}",
                    'estimatedDelivery': selected_slot['estimatedDeliveryTime'],
                    'deliveryCharge': selected_slot['deliveryCharge'],
                    'area': selected_slot.get('area', ''),
                    'city': selected_slot.get('city', '')
                },
                'message': f'Delivery slot booked successfully. Confirmation code: {confirmation_code}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_pincode_serviceability(self, pincode: str) -> Dict[str, Any]:
        """
        Check if a pincode is serviceable and return available service types
        
        Args:
            pincode: Customer's pincode
            
        Returns:
            Dictionary with serviceability information
        """
        try:
            # Query delivery slots for this pincode
            response = self.delivery_slots_table.query(
                KeyConditionExpression='pincode = :pincode',
                ExpressionAttributeValues={':pincode': pincode}
            )
            
            if not response['Items']:
                return {
                    'success': False,
                    'serviceable': False,
                    'pincode': pincode,
                    'message': f'Sorry, we do not deliver to pincode {pincode} yet.'
                }
            
            # Extract service information
            service_info = {
                'serviceable': True,
                'pincode': pincode,
                'area': response['Items'][0].get('area', ''),
                'city': response['Items'][0].get('city', ''),
                'zone': response['Items'][0].get('zone', ''),
                'deliveryTypes': [],
                'productTypes': [],
                'minimumCharges': {},
                'specialServices': []
            }
            
            for slot_config in response['Items']:
                # Collect delivery types
                for delivery_type in slot_config.get('deliveryTypes', []):
                    if delivery_type not in service_info['deliveryTypes']:
                        service_info['deliveryTypes'].append(delivery_type)
                
                # Collect product types
                product_type = slot_config.get('productType', 'GENERAL')
                if product_type not in service_info['productTypes']:
                    service_info['productTypes'].append(product_type)
                
                # Find minimum delivery charges
                time_slots = slot_config.get('timeSlots', [])
                if time_slots:
                    min_charge = min(float(slot['deliveryCharge']) for slot in time_slots)
                    service_info['minimumCharges'][product_type] = min_charge
                
                # Special services
                special_rules = slot_config.get('specialRules', {})
                if special_rules.get('temperatureControl'):
                    service_info['specialServices'].append('Temperature Controlled Delivery')
                if special_rules.get('qualityChecks'):
                    service_info['specialServices'].append('Quality Assured Delivery')
            
            return {
                'success': True,
                **service_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_booking_details(self, booking_id: str = None, order_id: str = None) -> Dict[str, Any]:
        """
        Get booking details by booking ID or order ID
        
        Args:
            booking_id: Booking ID
            order_id: Order ID
            
        Returns:
            Dictionary with booking details
        """
        try:
            if booking_id:
                response = self.slot_bookings_table.query(
                    KeyConditionExpression='bookingId = :bookingId',
                    ExpressionAttributeValues={':bookingId': booking_id}
                )
            elif order_id:
                response = self.slot_bookings_table.query(
                    IndexName='OrderIndex',
                    KeyConditionExpression='orderId = :orderId',
                    ExpressionAttributeValues={':orderId': order_id}
                )
            else:
                return {
                    'success': False,
                    'error': 'Either booking_id or order_id is required'
                }
            
            if not response['Items']:
                return {
                    'success': False,
                    'error': 'Booking not found'
                }
            
            booking = response['Items'][0]
            
            return {
                'success': True,
                'booking': booking
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_slot_configuration(self, pincode: str, product_type: str) -> Optional[Dict[str, Any]]:
        """Get slot configuration for pincode and product type"""
        try:
            response = self.delivery_slots_table.get_item(
                Key={
                    'pincode': pincode,
                    'slotType_productType': f'STANDARD#{product_type}'
                }
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error getting slot configuration: {str(e)}")
            return None
    
    def _get_slot_availability(self, pincode: str, slot_id: str, date: str, delivery_type: str) -> Optional[Dict[str, Any]]:
        """Get real-time slot availability"""
        try:
            response = self.slot_availability_table.get_item(
                Key={
                    'pincode_slotId_date': f'{pincode}#{slot_id}#{date}',
                    'deliveryType': delivery_type
                }
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error getting slot availability: {str(e)}")
            return None
    
    def _calculate_estimated_delivery_time(self, time_slot: Dict[str, Any]) -> str:
        """Calculate estimated delivery time within the slot"""
        start_time = time_slot['startTime']
        end_time = time_slot['endTime']
        
        # Calculate midpoint for estimation
        start_hour = int(start_time.split(':')[0])
        start_min = int(start_time.split(':')[1])
        end_hour = int(end_time.split(':')[0])
        end_min = int(end_time.split(':')[1])
        
        mid_hour = (start_hour + end_hour) // 2
        mid_min = (start_min + end_min) // 2
        
        return f"{mid_hour:02d}:{mid_min:02d}"
    
    def _calculate_order_weight(self, products: List[Dict[str, Any]]) -> float:
        """Calculate total weight of products in order"""
        total_weight = 0.0
        
        for product in products:
            quantity = product.get('quantity', 1)
            
            # Get variant weight from product data
            variant_weight = product.get('weight', 1.0)  # Default 1kg
            unit = product.get('unit', 'Kg')
            
            # Convert to kg if needed
            if unit.lower() in ['gms', 'g', 'grams']:
                variant_weight = variant_weight / 1000
            elif unit.lower() in ['ltr', 'litre', 'ml']:
                # Assume 1 liter = 1 kg for liquids
                if unit.lower() == 'ml':
                    variant_weight = variant_weight / 1000
            
            total_weight += quantity * variant_weight
        
        return total_weight
    
    def _update_slot_availability(self, pincode: str, slot_id: str, date: str, delivery_type: str, weight_used: float):
        """Update slot availability after booking"""
        try:
            self.slot_availability_table.update_item(
                Key={
                    'pincode_slotId_date': f'{pincode}#{slot_id}#{date}',
                    'deliveryType': delivery_type
                },
                UpdateExpression='SET currentBookings = currentBookings + :inc, availableSlots = availableSlots - :inc, currentWeight = currentWeight + :weight, availableWeight = availableWeight - :weight, lastUpdated = :timestamp',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':weight': Decimal(str(weight_used)),
                    ':timestamp': datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            print(f"Warning: Could not update slot availability: {str(e)}")


# Example usage and testing
def example_usage():
    """Example of how to use the DeliverySlotsAPI"""
    
    api = DeliverySlotsAPI()
    
    # Check if pincode is serviceable
    serviceability = api.check_pincode_serviceability('500086')
    print(f"Serviceability check: {serviceability}")
    
    # Get available slots for a pincode
    available_slots = api.get_available_slots(
        pincode='500086',
        product_types=['PERISHABLE'],
        delivery_type='next_day'
    )
    print(f"Available slots: {available_slots}")
    
    # Auto-select best slot
    best_slot = api.auto_select_best_slot(
        pincode='500086',
        product_types=['PERISHABLE'],
        delivery_preference='fastest'
    )
    print(f"Best slot selection: {best_slot}")
    
    # Book a delivery slot
    if best_slot['success']:
        order_data = {
            'orderId': 'ORD-20241220-001',
            'customerId': 'CUST001',
            'customerAddress': {
                'pincode': '500086',
                'address': '123 Main Street, Secunderabad'
            },
            'customerPhone': '+919876543210',
            'products': [
                {
                    'groupId': '8b7bb419-f868-491c-bba6-7785e78b62cf',
                    'variantId': '9381385120',
                    'quantity': 2,
                    'weight': 1.0,
                    'unit': 'Kg'
                }
            ]
        }
        
        # Add delivery details to selected slot
        selected_slot = best_slot['selectedSlot']
        selected_slot['deliveryDate'] = best_slot['deliveryDate']
        selected_slot['deliveryType'] = best_slot['deliveryType']
        
        booking_result = api.book_delivery_slot(order_data, selected_slot)
        print(f"Booking result: {booking_result}")


if __name__ == '__main__':
    example_usage()
