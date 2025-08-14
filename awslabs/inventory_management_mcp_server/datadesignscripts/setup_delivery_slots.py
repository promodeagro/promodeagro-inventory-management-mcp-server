#!/usr/bin/env python3
"""
Setup Delivery Slots System
Creates pincode-based delivery slot management with automatic slot selection.
Integrates with your existing products and variants system.
"""

import boto3
import sys
import traceback
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def create_delivery_slots_tables():
    """Create delivery slots management tables"""
    print_with_flush('🚚 Creating Delivery Slots tables...')

    try:
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        tables_config = [
            {
                'name': 'DeliverySlots',
                'pk': 'pincode',
                'sk': 'slotType_productType',
                'description': 'Pincode-based delivery slot configurations'
            },
            {
                'name': 'SlotAvailability',
                'pk': 'pincode_slotId_date',
                'sk': 'deliveryType',
                'description': 'Real-time slot availability tracking'
            },
            {
                'name': 'SlotBookings',
                'pk': 'bookingId',
                'sk': 'orderId',
                'description': 'Customer slot bookings and reservations'
            }
        ]

        created_tables = []
        
        for table_config in tables_config:
            table_name = f"InventoryManagement-{table_config['name']}"
            
            try:
                # Check if table exists
                existing_table = dynamodb.describe_table(TableName=table_name)
                print_with_flush(f'⚠️  {table_name} already exists, skipping...')
                continue
            except dynamodb.exceptions.ResourceNotFoundException:
                pass

            table_params = {
                'TableName': table_name,
                'KeySchema': [
                    {'AttributeName': table_config['pk'], 'KeyType': 'HASH'},
                    {'AttributeName': table_config['sk'], 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': table_config['pk'], 'AttributeType': 'S'},
                    {'AttributeName': table_config['sk'], 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [
                    {'Key': 'Service', 'Value': 'InventoryManagement'},
                    {'Key': 'Component', 'Value': 'DeliverySlots'},
                    {'Key': 'Purpose', 'Value': table_config['name']}
                ]
            }

            # Add GSI for specific tables
            if table_config['name'] == 'SlotAvailability':
                table_params['GlobalSecondaryIndexes'] = [
                    {
                        'IndexName': 'DateSlotIndex',
                        'KeySchema': [
                            {'AttributeName': 'pincode_slotId_date', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ]
            elif table_config['name'] == 'SlotBookings':
                table_params['GlobalSecondaryIndexes'] = [
                    {
                        'IndexName': 'OrderIndex',
                        'KeySchema': [
                            {'AttributeName': 'orderId', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ]

            response = dynamodb.create_table(**table_params)
            
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print_with_flush(f'✅ Created table: {table_name}')
                created_tables.append(table_name)
            else:
                print_with_flush(f'❌ Failed to create table: {table_name}')

        return len(created_tables) > 0
        
    except Exception as e:
        print_with_flush(f'❌ Error creating delivery slots tables: {str(e)}')
        traceback.print_exc()
        return False


def create_sample_delivery_slots():
    """Create sample delivery slot configurations for different pincodes"""
    print_with_flush('📍 Creating sample delivery slot configurations...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        slots_table = dynamodb.Table('InventoryManagement-DeliverySlots')
        
        sample_slots = [
            # Hyderabad pincodes - Perishable products
            {
                'pincode': '500086',
                'slotType_productType': 'STANDARD#PERISHABLE',
                'slotType': 'STANDARD',
                'productType': 'PERISHABLE',
                'area': 'Secunderabad',
                'city': 'Hyderabad',
                'zone': 'Central',
                'deliveryTypes': ['same_day', 'next_day', 'scheduled'],
                'timeSlots': [
                    {
                        'slotId': 'MORNING_1',
                        'name': 'Early Morning Delivery',
                        'startTime': '06:00',
                        'endTime': '10:00',
                        'maxCapacity': 50,
                        'deliveryCharge': Decimal('30.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'MORNING_2',
                        'name': 'Late Morning Delivery',
                        'startTime': '10:00',
                        'endTime': '14:00',
                        'maxCapacity': 75,
                        'deliveryCharge': Decimal('25.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'EVENING_1',
                        'name': 'Evening Delivery',
                        'startTime': '17:00',
                        'endTime': '21:00',
                        'maxCapacity': 60,
                        'deliveryCharge': Decimal('35.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                    }
                ],
                'specialRules': {
                    'temperatureControl': True,
                    'maxDeliveryTime': 4,
                    'qualityChecks': True,
                    'sameDayCutoff': '14:00'
                },
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            # Same pincode - General products
            {
                'pincode': '500086',
                'slotType_productType': 'STANDARD#GENERAL',
                'slotType': 'STANDARD',
                'productType': 'GENERAL',
                'area': 'Secunderabad',
                'city': 'Hyderabad',
                'zone': 'Central',
                'deliveryTypes': ['same_day', 'next_day', 'scheduled'],
                'timeSlots': [
                    {
                        'slotId': 'MORNING_1',
                        'name': 'Morning Delivery',
                        'startTime': '08:00',
                        'endTime': '12:00',
                        'maxCapacity': 100,
                        'deliveryCharge': Decimal('20.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'AFTERNOON_1',
                        'name': 'Afternoon Delivery',
                        'startTime': '14:00',
                        'endTime': '18:00',
                        'maxCapacity': 80,
                        'deliveryCharge': Decimal('20.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'EVENING_1',
                        'name': 'Evening Delivery',
                        'startTime': '18:00',
                        'endTime': '22:00',
                        'maxCapacity': 60,
                        'deliveryCharge': Decimal('25.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                    }
                ],
                'specialRules': {
                    'temperatureControl': False,
                    'maxDeliveryTime': 8,
                    'qualityChecks': False,
                    'sameDayCutoff': '16:00'
                },
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            # Mumbai pincode - Perishable products
            {
                'pincode': '400001',
                'slotType_productType': 'STANDARD#PERISHABLE',
                'slotType': 'STANDARD',
                'productType': 'PERISHABLE',
                'area': 'Fort',
                'city': 'Mumbai',
                'zone': 'South',
                'deliveryTypes': ['same_day', 'next_day', 'scheduled'],
                'timeSlots': [
                    {
                        'slotId': 'MORNING_1',
                        'name': 'Early Morning Delivery',
                        'startTime': '06:00',
                        'endTime': '09:00',
                        'maxCapacity': 40,
                        'deliveryCharge': Decimal('40.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'MORNING_2',
                        'name': 'Morning Delivery',
                        'startTime': '09:00',
                        'endTime': '13:00',
                        'maxCapacity': 60,
                        'deliveryCharge': Decimal('35.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                    },
                    {
                        'slotId': 'EVENING_1',
                        'name': 'Evening Delivery',
                        'startTime': '18:00',
                        'endTime': '22:00',
                        'maxCapacity': 50,
                        'deliveryCharge': Decimal('45.00'),
                        'daysAvailable': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                    }
                ],
                'specialRules': {
                    'temperatureControl': True,
                    'maxDeliveryTime': 3,
                    'qualityChecks': True,
                    'sameDayCutoff': '13:00'
                },
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for slot_config in sample_slots:
            try:
                slots_table.put_item(Item=slot_config)
                print_with_flush(f'✅ Created slot config for {slot_config["pincode"]} - {slot_config["productType"]}')
            except Exception as e:
                print_with_flush(f'⚠️  Slot config might already exist: {str(e)}')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating sample delivery slots: {str(e)}')
        return False


def create_sample_slot_availability():
    """Create sample slot availability for the next 7 days"""
    print_with_flush('📅 Creating sample slot availability...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        availability_table = dynamodb.Table('InventoryManagement-SlotAvailability')
        
        # Create availability for next 7 days
        base_date = datetime.now(timezone.utc).date()
        pincodes = ['500086', '400001']
        slot_ids = ['MORNING_1', 'MORNING_2', 'EVENING_1']
        delivery_types = ['same_day', 'next_day', 'scheduled']
        
        for days_ahead in range(7):
            target_date = base_date + timedelta(days=days_ahead)
            date_str = target_date.strftime('%Y-%m-%d')
            
            for pincode in pincodes:
                for slot_id in slot_ids:
                    for delivery_type in delivery_types:
                        # Skip same_day for past dates
                        if delivery_type == 'same_day' and days_ahead > 0:
                            continue
                        
                        # Determine capacity based on slot
                        if slot_id == 'MORNING_1':
                            max_capacity = 50
                            delivery_charge = Decimal('30.00')
                            start_time = '06:00'
                            end_time = '10:00'
                        elif slot_id == 'MORNING_2':
                            max_capacity = 75
                            delivery_charge = Decimal('25.00')
                            start_time = '10:00'
                            end_time = '14:00'
                        else:  # EVENING_1
                            max_capacity = 60
                            delivery_charge = Decimal('35.00')
                            start_time = '17:00'
                            end_time = '21:00'
                        
                        # Simulate some bookings
                        current_bookings = min(max_capacity - 10, max(0, (max_capacity // 3) + (days_ahead * 2)))
                        
                        availability_entry = {
                            'pincode_slotId_date': f'{pincode}#{slot_id}#{date_str}',
                            'deliveryType': delivery_type,
                            'pincode': pincode,
                            'slotId': slot_id,
                            'date': date_str,
                            'slotName': f'{slot_id.replace("_", " ").title()} Delivery',
                            'startTime': start_time,
                            'endTime': end_time,
                            'maxCapacity': max_capacity,
                            'currentBookings': current_bookings,
                            'availableSlots': max_capacity - current_bookings,
                            'maxWeight': Decimal('1000.0'),
                            'currentWeight': Decimal(str(current_bookings * 5.5)),
                            'availableWeight': Decimal(str((max_capacity - current_bookings) * 5.5)),
                            'deliveryCharge': delivery_charge,
                            'dynamicPricing': False,
                            'assignedRiders': [],
                            'status': 'AVAILABLE' if current_bookings < max_capacity else 'FULL',
                            'lastUpdated': datetime.now(timezone.utc).isoformat()
                        }
                        
                        try:
                            availability_table.put_item(Item=availability_entry)
                        except Exception as e:
                            print_with_flush(f'⚠️  Availability entry might already exist: {str(e)}')
        
        print_with_flush(f'✅ Created slot availability for next 7 days')
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating slot availability: {str(e)}')
        return False


def main():
    """Main execution function"""
    print_with_flush('🚚 DELIVERY SLOTS SYSTEM SETUP')
    print_with_flush('='*60)
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Create delivery slots tables
    if create_delivery_slots_tables():
        success_count += 1
    
    # Step 2: Create sample delivery slot configurations
    print_with_flush('\n' + '-'*50)
    if create_sample_delivery_slots():
        success_count += 1
    
    # Step 3: Create sample slot availability
    print_with_flush('\n' + '-'*50)
    if create_sample_slot_availability():
        success_count += 1
    
    # Summary
    print_with_flush('\n' + '='*60)
    print_with_flush('📊 DELIVERY SLOTS SETUP SUMMARY')
    print_with_flush('='*60)
    
    print_with_flush(f'✅ Successful steps: {success_count}/{total_steps}')
    
    if success_count == total_steps:
        print_with_flush('\n🎉 Delivery Slots system setup completed successfully!')
        print_with_flush('\n📋 What you now have:')
        print_with_flush('• DeliverySlots table with pincode-based slot configurations')
        print_with_flush('• SlotAvailability table for real-time slot tracking')
        print_with_flush('• SlotBookings table for customer reservations')
        print_with_flush('• Sample slots for Hyderabad (500086) and Mumbai (400001)')
        print_with_flush('• Different slot types for PERISHABLE vs GENERAL products')
        print_with_flush('• 7 days of sample availability data')
        
        print_with_flush('\n🔍 Sample Data:')
        print_with_flush('Pincode 500086 (Hyderabad):')
        print_with_flush('  • PERISHABLE: 6:00-10:00, 10:00-14:00, 17:00-21:00')
        print_with_flush('  • GENERAL: 8:00-12:00, 14:00-18:00, 18:00-22:00')
        print_with_flush('Pincode 400001 (Mumbai):')
        print_with_flush('  • PERISHABLE: 6:00-9:00, 9:00-13:00, 18:00-22:00')
        
        print_with_flush('\n🚀 Next Steps:')
        print_with_flush('1. Test the delivery slot API')
        print_with_flush('2. Add more pincodes and slot configurations')
        print_with_flush('3. Integrate with order placement system')
        print_with_flush('4. Set up automatic slot availability generation')
        print_with_flush('5. Add dynamic pricing based on demand')
        
    else:
        print_with_flush(f'\n⚠️  Setup completed with {total_steps - success_count} issues.')
        print_with_flush('Please check the error messages above and resolve them.')


if __name__ == '__main__':
    main()
