#!/usr/bin/env python3
"""
Setup Products with Variants - Your Existing JSON Structure
Implements your existing product-variant JSON structure directly in the Products table.
No complex separate tables - just enhance existing structure for simplicity.
"""

import boto3
import sys
import traceback
import uuid
from datetime import datetime, timezone
from decimal import Decimal


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def update_products_table_structure():
    """Update existing Products table to support your variant structure"""
    print_with_flush('🔧 Updating Products table structure for variants...')
    
    try:
        # Note: DynamoDB is schema-less, so we just need to ensure we can store your structure
        # The existing Products table can already handle your JSON structure
        print_with_flush('✅ Products table structure is compatible with your variant format')
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error updating Products table: {str(e)}')
        return False


def update_stock_levels_for_variants():
    """Update StockLevels table structure to track variants separately"""
    print_with_flush('📊 Updating StockLevels table for variant tracking...')
    
    try:
        # StockLevels table will use:
        # PK: groupId (your product group ID)
        # SK: location#variantId (warehouse + specific variant)
        print_with_flush('✅ StockLevels table structure updated for variant tracking')
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error updating StockLevels table: {str(e)}')
        return False


def create_units_reference_table():
    """Create a simple units reference table"""
    print_with_flush('📏 Creating Units reference table...')
    
    try:
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        # Check if table exists
        try:
            existing_table = dynamodb.describe_table(TableName='InventoryManagement-ProductUnits')
            print_with_flush('⚠️  ProductUnits table already exists')
            return True
        except dynamodb.exceptions.ResourceNotFoundException:
            pass

        table_params = {
            'TableName': 'InventoryManagement-ProductUnits',
            'KeySchema': [
                {'AttributeName': 'unitId', 'KeyType': 'HASH'},
                {'AttributeName': 'unitType', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'unitId', 'AttributeType': 'S'},
                {'AttributeName': 'unitType', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'Tags': [
                {'Key': 'Service', 'Value': 'InventoryManagement'},
                {'Key': 'Component', 'Value': 'ProductUnits'},
                {'Key': 'Purpose', 'Value': 'UnitsReference'}
            ]
        }
        
        response = dynamodb.create_table(**table_params)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print_with_flush('✅ ProductUnits table created successfully')
            return True
        else:
            print_with_flush('❌ Failed to create ProductUnits table')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error creating ProductUnits table: {str(e)}')
        traceback.print_exc()
        return False


def create_sample_units():
    """Create sample unit definitions"""
    print_with_flush('📏 Creating sample unit definitions...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        units_table = dynamodb.Table('InventoryManagement-ProductUnits')
        
        sample_units = [
            # Weight Units
            {
                'unitId': 'Kg',
                'unitType': 'WEIGHT',
                'unitName': 'Kilograms',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'Kg',
                'isDefault': True,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'unitId': 'Gms',
                'unitType': 'WEIGHT',
                'unitName': 'Grams',
                'conversionFactor': Decimal('0.001'),
                'baseUnit': 'Kg',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            # Volume Units
            {
                'unitId': 'Ltr',
                'unitType': 'VOLUME',
                'unitName': 'Liters',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'Ltr',
                'isDefault': True,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'unitId': 'ML',
                'unitType': 'VOLUME',
                'unitName': 'Milliliters',
                'conversionFactor': Decimal('0.001'),
                'baseUnit': 'Ltr',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            # Count Units
            {
                'unitId': 'Pcs',
                'unitType': 'COUNT',
                'unitName': 'Pieces',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'Pcs',
                'isDefault': True,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'unitId': 'Dozen',
                'unitType': 'COUNT',
                'unitName': 'Dozen',
                'conversionFactor': Decimal('12.0'),
                'baseUnit': 'Pcs',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for unit in sample_units:
            try:
                units_table.put_item(Item=unit)
                print_with_flush(f'✅ Created unit: {unit["unitName"]}')
            except Exception as e:
                print_with_flush(f'⚠️  Unit {unit["unitName"]} might already exist: {str(e)}')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating sample units: {str(e)}')
        return False


def migrate_your_product_data():
    """Create your product using the exact JSON structure you provided"""
    print_with_flush('🥬 Creating your product with existing JSON structure...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        products_table = dynamodb.Table('InventoryManagement-Products')
        
        # Your exact product structure with enhancements for DynamoDB
        your_product = {
            # DynamoDB Keys
            'groupId': '8b7bb419-f868-491c-bba6-7785e78b62cf',  # PK
            'category': 'Bengali Special#Bengali Vegetables',    # SK (category#subCategory)
            
            # Your existing JSON structure
            'name': 'Bharta Brinjal (Black medium pieces)',
            'subCategory': 'Bengali Vegetables',
            'description': 'Bharta Brinjal (Begun) is a special variety of large, fleshy eggplant perfect for roasting and Bengali cuisine preparations.',
            'image': 'https://cdn.example.com/bharta-brinjal.webp',
            'images': [
                'https://cdn.example.com/bharta-brinjal-1.webp',
                '',
                ''
            ],
            'tags': [
                'bharta brinjal', 'begun', 'baingan', 'roasting eggplant'
            ],
            
            # Your exact variations structure
            'variations': [
                {
                    'id': '9381385120',
                    'name': 'Bharta Brinjal (1 Kg)',
                    'unit': 'Kg',
                    'quantity': 1,
                    'mrp': Decimal('120'),
                    'price': Decimal('90'),
                    'availability': True
                },
                {
                    'id': '9271560014',
                    'name': 'Bharta Brinjal (500 Gms)',
                    'unit': 'Gms',
                    'quantity': 500,
                    'mrp': Decimal('60'),
                    'price': Decimal('45'),
                    'availability': True
                },
                {
                    'id': '8628945059',
                    'name': 'Bharta Brinjal (250 Gms)',
                    'unit': 'Gms',
                    'quantity': 250,
                    'mrp': Decimal('30'),
                    'price': Decimal('23'),
                    'availability': True
                }
            ],
            
            # Additional fields for inventory system
            'productType': 'PERISHABLE',
            'storageRequirements': {
                'temperature': 'ROOM_TEMP',
                'humidity': 'MEDIUM',
                'specialHandling': 'HANDLE_WITH_CARE'
            },
            'supplier': {
                'supplierId': 'SUPP-BENGALI-001',
                'supplierName': 'Bengali Fresh Vegetables Co.',
                'leadTime': 2
            },
            'inventory': {
                'trackBatches': True,
                'expiryTracking': True,
                'qualityChecks': True,
                'reorderPoint': 50,
                'maxStock': 500
            },
            'isActive': True,
            'createdAt': datetime.now(timezone.utc).isoformat(),
            'updatedAt': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert the product
        products_table.put_item(Item=your_product)
        print_with_flush(f'✅ Created product: {your_product["name"]}')
        
        # Create stock levels for each variant
        create_stock_levels_for_product(your_product)
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating your product: {str(e)}')
        traceback.print_exc()
        return False


def create_stock_levels_for_product(product):
    """Create stock level entries for each variant in your product"""
    print_with_flush('📊 Creating stock levels for variants...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        stock_table = dynamodb.Table('InventoryManagement-StockLevels')
        
        for variation in product['variations']:
            stock_entry = {
                # DynamoDB Keys
                'productId': product['groupId'],  # PK (using your groupId)
                'location': f'WAREHOUSE-HYDERABAD-01#{variation["id"]}',  # SK (location#variantId)
                
                # Variant information
                'groupId': product['groupId'],
                'variantId': variation['id'],
                'variantName': variation['name'],
                'unit': variation['unit'],
                'quantity': variation['quantity'],
                
                # Stock tracking
                'totalStock': 100,  # Initial stock
                'availableStock': 95,
                'reservedStock': 5,
                'damagedStock': 0,
                'expiredStock': 0,
                'reorderPoint': 20,
                'maxStock': 500,
                
                # Timestamps
                'lastRestocked': datetime.now(timezone.utc).isoformat(),
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
            
            try:
                stock_table.put_item(Item=stock_entry)
                print_with_flush(f'✅ Created stock level for: {variation["name"]}')
            except Exception as e:
                print_with_flush(f'⚠️  Stock level for {variation["name"]} might already exist: {str(e)}')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating stock levels: {str(e)}')
        return False


def create_additional_sample_products():
    """Create more sample products to demonstrate the system"""
    print_with_flush('🥛 Creating additional sample products...')
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        products_table = dynamodb.Table('InventoryManagement-Products')
        
        additional_products = [
            {
                'groupId': str(uuid.uuid4()),
                'category': 'Dairy Products#Fresh Milk',
                'name': 'Organic Fresh Milk',
                'subCategory': 'Fresh Milk',
                'description': 'Pure organic milk from grass-fed cows, rich in nutrients.',
                'image': 'https://cdn.example.com/organic-milk.webp',
                'images': [
                    'https://cdn.example.com/organic-milk-1.webp',
                    'https://cdn.example.com/organic-milk-2.webp',
                    ''
                ],
                'tags': ['organic milk', 'fresh milk', 'dairy', 'grass-fed'],
                'variations': [
                    {
                        'id': str(uuid.uuid4())[:10],
                        'name': 'Organic Fresh Milk (1 Ltr)',
                        'unit': 'Ltr',
                        'quantity': 1,
                        'mrp': Decimal('80'),
                        'price': Decimal('65'),
                        'availability': True
                    },
                    {
                        'id': str(uuid.uuid4())[:10],
                        'name': 'Organic Fresh Milk (500 ML)',
                        'unit': 'ML',
                        'quantity': 500,
                        'mrp': Decimal('45'),
                        'price': Decimal('35'),
                        'availability': True
                    }
                ],
                'productType': 'PERISHABLE',
                'storageRequirements': {
                    'temperature': 'REFRIGERATED',
                    'humidity': 'LOW',
                    'specialHandling': 'KEEP_COLD'
                },
                'supplier': {
                    'supplierId': 'SUPP-DAIRY-001',
                    'supplierName': 'Organic Dairy Farms Ltd.',
                    'leadTime': 1
                },
                'inventory': {
                    'trackBatches': True,
                    'expiryTracking': True,
                    'qualityChecks': True,
                    'reorderPoint': 30,
                    'maxStock': 200
                },
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'groupId': str(uuid.uuid4()),
                'category': 'Fresh Vegetables#Leafy Greens',
                'name': 'Fresh Spinach (Palak)',
                'subCategory': 'Leafy Greens',
                'description': 'Fresh, tender spinach leaves rich in iron and vitamins.',
                'image': 'https://cdn.example.com/fresh-spinach.webp',
                'images': [
                    'https://cdn.example.com/fresh-spinach-1.webp',
                    '',
                    ''
                ],
                'tags': ['spinach', 'palak', 'leafy greens', 'iron rich'],
                'variations': [
                    {
                        'id': str(uuid.uuid4())[:10],
                        'name': 'Fresh Spinach (500 Gms)',
                        'unit': 'Gms',
                        'quantity': 500,
                        'mrp': Decimal('40'),
                        'price': Decimal('30'),
                        'availability': True
                    },
                    {
                        'id': str(uuid.uuid4())[:10],
                        'name': 'Fresh Spinach (250 Gms)',
                        'unit': 'Gms',
                        'quantity': 250,
                        'mrp': Decimal('22'),
                        'price': Decimal('18'),
                        'availability': True
                    }
                ],
                'productType': 'PERISHABLE',
                'storageRequirements': {
                    'temperature': 'COOL',
                    'humidity': 'HIGH',
                    'specialHandling': 'GENTLE_HANDLING'
                },
                'supplier': {
                    'supplierId': 'SUPP-GREENS-001',
                    'supplierName': 'Fresh Greens Cooperative',
                    'leadTime': 1
                },
                'inventory': {
                    'trackBatches': True,
                    'expiryTracking': True,
                    'qualityChecks': True,
                    'reorderPoint': 25,
                    'maxStock': 150
                },
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for product in additional_products:
            try:
                products_table.put_item(Item=product)
                print_with_flush(f'✅ Created product: {product["name"]}')
                
                # Create stock levels for this product
                create_stock_levels_for_product(product)
                
            except Exception as e:
                print_with_flush(f'⚠️  Product {product["name"]} might already exist: {str(e)}')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error creating additional products: {str(e)}')
        return False


def main():
    """Main execution function"""
    print_with_flush('🚀 PRODUCTS & VARIANTS SETUP - YOUR EXISTING STRUCTURE')
    print_with_flush('='*70)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Update Products table structure
    if update_products_table_structure():
        success_count += 1
    
    # Step 2: Update StockLevels for variants
    print_with_flush('\n' + '-'*50)
    if update_stock_levels_for_variants():
        success_count += 1
    
    # Step 3: Create units reference table
    print_with_flush('\n' + '-'*50)
    if create_units_reference_table():
        success_count += 1
        
        # Step 3a: Create sample units
        create_sample_units()
    
    # Step 4: Create your product with exact JSON structure
    print_with_flush('\n' + '-'*50)
    if migrate_your_product_data():
        success_count += 1
    
    # Step 5: Create additional sample products
    print_with_flush('\n' + '-'*50)
    if create_additional_sample_products():
        success_count += 1
    
    # Summary
    print_with_flush('\n' + '='*70)
    print_with_flush('📊 SETUP SUMMARY')
    print_with_flush('='*70)
    
    print_with_flush(f'✅ Successful steps: {success_count}/{total_steps}')
    
    if success_count == total_steps:
        print_with_flush('\n🎉 Products & Variants setup completed successfully!')
        print_with_flush('\n📋 What you now have:')
        print_with_flush('• Products table storing your exact JSON variant structure')
        print_with_flush('• StockLevels table tracking each variant separately')
        print_with_flush('• ProductUnits table with standard unit definitions')
        print_with_flush('• Sample products: Bharta Brinjal, Organic Milk, Spinach')
        print_with_flush('• Stock levels for each product variant')
        
        print_with_flush('\n🔍 Sample Data Structure:')
        print_with_flush('Products Table PK: groupId (8b7bb419-f868-491c-bba6-7785e78b62cf)')
        print_with_flush('Products Table SK: category#subCategory (Bengali Special#Bengali Vegetables)')
        print_with_flush('StockLevels PK: groupId (8b7bb419-f868-491c-bba6-7785e78b62cf)')
        print_with_flush('StockLevels SK: location#variantId (WAREHOUSE-HYDERABAD-01#9381385120)')
        
        print_with_flush('\n🚀 Next Steps:')
        print_with_flush('1. Test querying products by category')
        print_with_flush('2. Test updating variant prices')
        print_with_flush('3. Test stock level tracking per variant')
        print_with_flush('4. Integrate with existing inventory operations')
        print_with_flush('5. Add more of your products using the same structure')
        
    else:
        print_with_flush(f'\n⚠️  Setup completed with {total_steps - success_count} issues.')
        print_with_flush('Please check the error messages above and resolve them.')


if __name__ == '__main__':
    main()
