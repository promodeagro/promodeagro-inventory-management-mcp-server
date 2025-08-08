# setup_dynamodb.py
import boto3
import sys
import traceback
from datetime import datetime, timezone
from decimal import Decimal


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def create_inventory_tables():
    """Create multiple DynamoDB tables for Inventory Management System with Variants & Units"""
    print_with_flush('🔧 Starting DynamoDB tables creation for Inventory Management System...')

    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region...')
        
        # Use Mumbai region (ap-south-1) for free tier
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB client created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False

    # Define all tables to create - Complete multi-table structure with Variants & Units
    tables_config = [
        # Core Inventory Tables (Enhanced)
        {
            'name': 'Products',
            'pk': 'productId',
            'sk': 'category',
            'description': 'Product catalog and information with variant support'
        },
        {
            'name': 'Batches',
            'pk': 'batchId',
            'sk': 'productId',
            'description': 'Batch tracking and expiry management with variants'
        },
        {
            'name': 'Suppliers',
            'pk': 'supplierId',
            'sk': 'status',
            'description': 'Supplier information and performance'
        },
        {
            'name': 'Customers',
            'pk': 'customerId',
            'sk': 'customerType',
            'description': 'Customer information and preferences'
        },
        {
            'name': 'Riders',
            'pk': 'riderId',
            'sk': 'status',
            'description': 'Delivery personnel management'
        },
        {
            'name': 'Orders',
            'pk': 'orderId',
            'sk': 'customerId',
            'description': 'Customer orders and fulfillment with variant support'
        },
        {
            'name': 'Deliveries',
            'pk': 'deliveryId',
            'sk': 'orderId',
            'description': 'Delivery management and tracking'
        },
        {
            'name': 'StockLevels',
            'pk': 'productId',
            'sk': 'location',
            'description': 'Real-time stock level monitoring with variants and units'
        },
        {
            'name': 'PurchaseOrders',
            'pk': 'poId',
            'sk': 'supplierId',
            'description': 'Procurement workflow management'
        },
        {
            'name': 'CashCollections',
            'pk': 'collectionId',
            'sk': 'riderId',
            'description': 'Payment tracking and reconciliation'
        },
        {
            'name': 'Journeys',
            'pk': 'PK',
            'sk': 'SK',
            'description': 'Workflow journey management and tracking'
        },
        # Variant & Unit Tables (NEW)
        {
            'name': 'ProductVariants',
            'pk': 'variantId',
            'sk': 'productId',
            'description': 'Product variants management size color weight'
        },
        {
            'name': 'ProductUnits',
            'pk': 'unitId',
            'sk': 'productId',
            'description': 'Product units management with conversion factors'
        },
        {
            'name': 'UnitConversions',
            'pk': 'conversionId',
            'sk': 'fromUnit#toUnit',
            'description': 'Unit conversion factors and relationships'
        },
        {
            'name': 'OrderItems',
            'pk': 'orderId',
            'sk': 'productId#variantId#unitId',
            'description': 'Order items with variants and units tracking'
        },
        # Business Tables
        {
            'name': 'Discounts',
            'pk': 'discountId',
            'sk': 'discountType',
            'description': 'Discount and promotion management'
        },
        {
            'name': 'PricingRules',
            'pk': 'pricingId',
            'sk': 'ruleType',
            'description': 'Dynamic pricing and cost management with variants'
        },
        {
            'name': 'Categories',
            'pk': 'categoryId',
            'sk': 'parentCategory',
            'description': 'Product categorization and hierarchy'
        },
        {
            'name': 'Locations',
            'pk': 'locationId',
            'sk': 'locationType',
            'description': 'Warehouse and delivery zone management'
        },
        {
            'name': 'Users',
            'pk': 'userId',
            'sk': 'role',
            'description': 'User management and authentication'
        },
        {
            'name': 'AuditLogs',
            'pk': 'auditId',
            'sk': 'timestamp',
            'description': 'System audit trails and compliance'
        },
        {
            'name': 'Notifications',
            'pk': 'notificationId',
            'sk': 'recipientId',
            'description': 'System notifications and alerts'
        },
        {
            'name': 'Reports',
            'pk': 'reportId',
            'sk': 'reportType',
            'description': 'Analytics and reporting data'
        },
        {
            'name': 'Settings',
            'pk': 'settingKey',
            'sk': 'category',
            'description': 'System configuration and settings'
        }
    ]

    created_tables = []

    for table_config in tables_config:
        table_name = f'InventoryManagement-{table_config["name"]}'
        
        try:
            print_with_flush(f'🔍 Checking if {table_name} table exists in Mumbai region...')
            response = dynamodb.describe_table(TableName=table_name)
            print_with_flush(f'✅ Table {table_name} already exists and is ready!')
            print_with_flush(f'🕐 Table Status: {response["Table"]["TableStatus"]}')
            created_tables.append(table_name)
            continue
            
        except dynamodb.exceptions.ResourceNotFoundException:
            print_with_flush(f'📋 Table {table_name} does not exist, creating new table in Mumbai region...')
            pass
        except Exception as e:
            print_with_flush(f'❌ Error checking table existence: {str(e)}')
            traceback.print_exc()
            continue

        table_definition = {
            'TableName': table_name,
            'AttributeDefinitions': [
                {'AttributeName': table_config['pk'], 'AttributeType': 'S'},
                {'AttributeName': table_config['sk'], 'AttributeType': 'S'},
            ],
            'KeySchema': [
                {'AttributeName': table_config['pk'], 'KeyType': 'HASH'},
                {'AttributeName': table_config['sk'], 'KeyType': 'RANGE'},
            ],
            'BillingMode': 'PAY_PER_REQUEST',  # Free tier - no provisioned capacity
            'Tags': [
                {'Key': 'Service', 'Value': 'Inventory-Management'},
                {'Key': 'Component', 'Value': 'DataStore'},
                {'Key': 'Purpose', 'Value': table_config['description']},
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'BillingMode', 'Value': 'PAY_PER_REQUEST'},
                {'Key': 'Region', 'Value': 'ap-south-1'},
                {'Key': 'TableType', 'Value': table_config['name']},
                {'Key': 'Features', 'Value': 'ProductManagement-StockTracking-OrderProcessing-Variants-Units'},
            ],
        }

        try:
            print_with_flush(f'📋 Creating {table_name} with {table_config["description"]}...')
            response = dynamodb.create_table(**table_definition)
            print_with_flush(f'✅ Table creation initiated: {response["TableDescription"]["TableName"]}')
            print_with_flush(f'🕐 Table Status: {response["TableDescription"]["TableStatus"]}')

            # Wait for table to be active
            print_with_flush(f'⏳ Waiting for {table_name} to become active in Mumbai region...')
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print_with_flush(f'✅ {table_name} is now active in Mumbai region!')
            created_tables.append(table_name)

        except dynamodb.exceptions.ResourceInUseException:
            print_with_flush(f'⚠️  Table {table_name} already exists (from creation attempt)')
            created_tables.append(table_name)
        except Exception as e:
            print_with_flush(f'❌ Error creating table {table_name}: {str(e)}')
            traceback.print_exc()

    print_with_flush(f'📊 Successfully created/verified {len(created_tables)} tables')
    return created_tables


def seed_sample_data():
    """Seed the tables with sample inventory data including variants and units"""
    print_with_flush('🌱 Starting sample data seeding in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    # Sample data for each table
    sample_data = {
        'Products': [
            {
                'productId': 'PROD001',
                'category': 'VEGETABLES',
                'name': 'Fresh Tomatoes',
                'description': 'Organic red tomatoes with variant support',
                'brand': 'Organic Farms',
                'baseUnit': 'KG',
                'defaultUnit': 'KG',
                'hasVariants': True,
                'variantTypes': ['SIZE'],
                'costPrice': Decimal('45.00'),
                'sellingPrice': Decimal('60.00'),
                'minStock': 100,
                'reorderPoint': 150,
                'supplierId': 'SUPP001',
                'expiryTracking': True,
                'batchRequired': True,
                'storageLocation': 'COLD_STORAGE_A',
                'specialHandling': 'TEMPERATURE_CONTROLLED',
                'images': ['url1', 'url2'],
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'productId': 'PROD002',
                'category': 'DAIRY',
                'name': 'Fresh Milk',
                'description': 'Pure cow milk with volume units',
                'brand': 'Dairy Fresh',
                'baseUnit': 'LITERS',
                'defaultUnit': 'LITERS',
                'hasVariants': False,
                'variantTypes': [],
                'costPrice': Decimal('50.00'),
                'sellingPrice': Decimal('70.00'),
                'minStock': 50,
                'reorderPoint': 75,
                'supplierId': 'SUPP002',
                'expiryTracking': True,
                'batchRequired': True,
                'storageLocation': 'COLD_STORAGE_B',
                'specialHandling': 'REFRIGERATED',
                'images': ['url3', 'url4'],
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'ProductVariants': [
            {
                'variantId': 'VAR001',
                'productId': 'PROD001',
                'variantName': 'Small Tomatoes',
                'variantType': 'SIZE',
                'variantValue': 'SMALL',
                'sku': 'PROD001-SMALL',
                'barcode': '123456789001',
                'dimensions': {'weight': '0.1', 'length': '5', 'width': '4'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'variantId': 'VAR002',
                'productId': 'PROD001',
                'variantName': 'Medium Tomatoes',
                'variantType': 'SIZE',
                'variantValue': 'MEDIUM',
                'sku': 'PROD001-MEDIUM',
                'barcode': '123456789002',
                'dimensions': {'weight': '0.2', 'length': '6', 'width': '5'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'variantId': 'VAR003',
                'productId': 'PROD001',
                'variantName': 'Large Tomatoes',
                'variantType': 'SIZE',
                'variantValue': 'LARGE',
                'sku': 'PROD001-LARGE',
                'barcode': '123456789003',
                'dimensions': {'weight': '0.3', 'length': '7', 'width': '6'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'ProductUnits': [
            {
                'unitId': 'KG',
                'productId': 'PROD001',
                'unitName': 'Kilograms',
                'unitType': 'WEIGHT',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'KG',
                'isDefault': True,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'unitId': 'GRAMS',
                'productId': 'PROD001',
                'unitName': 'Grams',
                'unitType': 'WEIGHT',
                'conversionFactor': Decimal('0.001'),
                'baseUnit': 'KG',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'unitId': 'PCS',
                'productId': 'PROD001',
                'unitName': 'Pieces',
                'unitType': 'COUNT',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'PCS',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'unitId': 'LITERS',
                'productId': 'PROD002',
                'unitName': 'Liters',
                'unitType': 'VOLUME',
                'conversionFactor': Decimal('1.0'),
                'baseUnit': 'LITERS',
                'isDefault': True,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'unitId': 'ML',
                'productId': 'PROD002',
                'unitName': 'Milliliters',
                'unitType': 'VOLUME',
                'conversionFactor': Decimal('0.001'),
                'baseUnit': 'LITERS',
                'isDefault': False,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'UnitConversions': [
            {
                'conversionId': 'CONV001',
                'fromUnit#toUnit': 'KG#GRAMS',
                'fromUnit': 'KG',
                'toUnit': 'GRAMS',
                'conversionFactor': Decimal('1000.0'),
                'unitType': 'WEIGHT',
                'description': '1 KG = 1000 GRAMS',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'conversionId': 'CONV002',
                'fromUnit#toUnit': 'LITERS#ML',
                'fromUnit': 'LITERS',
                'toUnit': 'ML',
                'conversionFactor': Decimal('1000.0'),
                'unitType': 'VOLUME',
                'description': '1 LITER = 1000 ML',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Batches': [
            {
                'batchId': 'BATCH001',
                'productId': 'PROD001',
                'variantId': 'VAR002',
                'unitId': 'KG',
                'batchNumber': 'TOMATO-MEDIUM-2024-001',
                'manufacturingDate': '2024-01-01',
                'expiryDate': '2024-01-15',
                'initialQuantity': 500,
                'currentQuantity': 450,
                'unitQuantity': Decimal('500.0'),
                'supplierId': 'SUPP001',
                'qualityStatus': 'GOOD',
                'temperature': Decimal('4.5'),
                'location': 'COLD_STORAGE_A',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'batchId': 'BATCH002',
                'productId': 'PROD002',
                'variantId': None,
                'unitId': 'LITERS',
                'batchNumber': 'MILK-2024-001',
                'manufacturingDate': '2024-01-01',
                'expiryDate': '2024-01-07',
                'initialQuantity': 200,
                'currentQuantity': 180,
                'unitQuantity': Decimal('200.0'),
                'supplierId': 'SUPP002',
                'qualityStatus': 'GOOD',
                'temperature': Decimal('2.0'),
                'location': 'COLD_STORAGE_B',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Suppliers': [
            {
                'supplierId': 'SUPP001',
                'status': 'ACTIVE',
                'name': 'Fresh Produce Co.',
                'contactPerson': 'Rajesh Kumar',
                'phone': '+919876543210',
                'email': 'rajesh@freshproduce.com',
                'address': '123 Farm Road, Pune',
                'paymentTerms': 'NET_30',
                'rating': Decimal('4.5'),
                'leadTime': 2,
                'qualityStandards': 'ORGANIC_CERTIFIED',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'supplierId': 'SUPP002',
                'status': 'ACTIVE',
                'name': 'Dairy Fresh Ltd.',
                'contactPerson': 'Priya Sharma',
                'phone': '+919876543211',
                'email': 'priya@dairyfresh.com',
                'address': '456 Dairy Farm, Nashik',
                'paymentTerms': 'NET_15',
                'rating': Decimal('4.8'),
                'leadTime': 1,
                'qualityStandards': 'PASTEURIZED',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Customers': [
            {
                'customerId': 'CUST001',
                'customerType': 'REGULAR',
                'name': 'John Doe',
                'phone': '+919876543210',
                'email': 'john.doe@email.com',
                'address': '123 Main St, Mumbai',
                'pincode': '400001',
                'loyaltyPoints': 150,
                'totalOrders': 25,
                'totalSpent': Decimal('15000.00'),
                'preferredPaymentMethod': 'CASH_ON_DELIVERY',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Riders': [
            {
                'riderId': 'RIDER001',
                'status': 'ACTIVE',
                'name': 'Amit Kumar',
                'phone': '+919876543213',
                'email': 'amit.kumar@company.com',
                'vehicleNumber': 'MH01AB1234',
                'vehicleType': 'BIKE',
                'currentLocation': '19.0760,72.8777',
                'assignedZone': 'MUMBAI_CENTRAL',
                'rating': Decimal('4.5'),
                'totalDeliveries': 150,
                'totalEarnings': Decimal('25000.00'),
                'isAvailable': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Orders': [
            {
                'orderId': 'ORD-20241220-68034D',
                'customerId': 'CUST001',
                'customerName': 'John Doe',
                'customerPhone': '+919876543210',
                'deliveryAddress': '123 Main St, Mumbai',
                'status': 'PENDING',
                'totalAmount': Decimal('3000.00'),
                'discountAmount': Decimal('100.00'),
                'finalAmount': Decimal('2900.00'),
                'paymentMethod': 'CASH_ON_DELIVERY',
                'paymentStatus': 'PENDING',
                'deliverySlot': '2024-12-21T10:00:00Z',
                'riderId': 'RIDER001',
                'variantSupport': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'OrderItems': [
            {
                'orderId': 'ORD-20241220-68034D',
                'productId#variantId#unitId': 'PROD001#VAR002#KG',
                'productId': 'PROD001',
                'variantId': 'VAR002',
                'unitId': 'KG',
                'quantity': 2,
                'unitPrice': Decimal('60.00'),
                'discountPercentage': 10,
                'discountAmount': Decimal('12.00'),
                'finalPrice': Decimal('48.00'),
                'totalPrice': Decimal('96.00'),
                'batchId': 'BATCH001',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'orderId': 'ORD-20241220-68034D',
                'productId#variantId#unitId': 'PROD002#null#LITERS',
                'productId': 'PROD002',
                'variantId': None,
                'unitId': 'LITERS',
                'quantity': 1,
                'unitPrice': Decimal('70.00'),
                'discountPercentage': 0,
                'discountAmount': Decimal('0.00'),
                'finalPrice': Decimal('70.00'),
                'totalPrice': Decimal('70.00'),
                'batchId': 'BATCH002',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Deliveries': [
            {
                'deliveryId': 'DEL-20241220-001',
                'orderId': 'ORD-20241220-68034D',
                'riderId': 'RIDER001',
                'status': 'PENDING',
                'pickupTime': None,
                'estimatedDeliveryTime': '2024-12-21T10:00:00Z',
                'actualDeliveryTime': None,
                'signatureUrl': None,
                'photoUrl': None,
                'cashCollected': Decimal('0.00'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'StockLevels': [
            {
                'productId': 'PROD001',
                'location': 'COLD_STORAGE_A#VAR002#KG',
                'variantId': 'VAR002',
                'unitId': 'KG',
                'totalStock': 1200,
                'availableStock': 1100,
                'reservedStock': 100,
                'damagedStock': 50,
                'expiredStock': 0,
                'baseUnitQuantity': Decimal('1200.0'),
                'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'productId': 'PROD002',
                'location': 'COLD_STORAGE_B#null#LITERS',
                'variantId': None,
                'unitId': 'LITERS',
                'totalStock': 500,
                'availableStock': 480,
                'reservedStock': 20,
                'damagedStock': 0,
                'expiredStock': 0,
                'baseUnitQuantity': Decimal('500.0'),
                'lastUpdated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'PurchaseOrders': [
            {
                'poId': 'PO-20241220-001',
                'supplierId': 'SUPP001',
                'status': 'APPROVED',
                'totalAmount': Decimal('50000.00'),
                'deliveryDate': '2024-12-25',
                'createdBy': 'USER001',
                'approvedBy': 'USER002',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'CashCollections': [
            {
                'collectionId': 'COL-20241220-001',
                'riderId': 'RIDER001',
                'date': '2024-12-20',
                'totalCollected': Decimal('5000.00'),
                'cashCollected': Decimal('3000.00'),
                'digitalCollected': Decimal('2000.00'),
                'ordersDelivered': 25,
                'status': 'PENDING_SETTLEMENT',
                'settledAt': None,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Discounts': [
            {
                'discountId': 'DISC001',
                'discountType': 'PERCENTAGE',
                'name': 'New Customer Discount',
                'description': '10% off for first order',
                'discountValue': 10,
                'minOrderAmount': Decimal('500.00'),
                'maxDiscountAmount': Decimal('200.00'),
                'applicableProducts': ['ALL'],
                'applicableCategories': ['VEGETABLES', 'FRUITS'],
                'customerTypes': ['NEW'],
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'usageLimit': 1,
                'usedCount': 0,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'PricingRules': [
            {
                'pricingId': 'PRICE001',
                'ruleType': 'DYNAMIC_PRICING',
                'productId': 'PROD001',
                'variantId': 'VAR002',
                'unitId': 'KG',
                'basePrice': Decimal('60.00'),
                'minPrice': Decimal('45.00'),
                'maxPrice': Decimal('80.00'),
                'factors': {
                    'demand': 'HIGH',
                    'season': 'PEAK',
                    'competition': 'MEDIUM'
                },
                'effectiveDate': '2024-01-01',
                'expiryDate': '2024-12-31',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Categories': [
            {
                'categoryId': 'VEGETABLES',
                'parentCategory': None,
                'name': 'Vegetables',
                'description': 'Fresh vegetables',
                'icon': 'vegetables-icon',
                'sortOrder': 1,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'categoryId': 'DAIRY',
                'parentCategory': None,
                'name': 'Dairy Products',
                'description': 'Fresh dairy products',
                'icon': 'dairy-icon',
                'sortOrder': 2,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Locations': [
            {
                'locationId': 'MUMBAI_CENTRAL',
                'locationType': 'DELIVERY_ZONE',
                'name': 'Mumbai Central',
                'pincodes': ['400001', '400002', '400003'],
                'deliveryCharge': Decimal('50.00'),
                'minOrderAmount': Decimal('200.00'),
                'deliverySlots': ['09:00-12:00', '14:00-17:00', '18:00-21:00'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Users': [
            {
                'userId': 'USER001',
                'role': 'WAREHOUSE_MANAGER',
                'name': 'Amit Patel',
                'email': 'amit@company.com',
                'phone': '+919876543210',
                'permissions': ['INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'AuditLogs': [
            {
                'auditId': 'AUDIT-20241220-001',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': 'USER001',
                'action': 'STOCK_ADJUSTMENT',
                'entityId': 'ADJ001',
                'details': 'Created stock adjustment for damaged tomatoes',
                'ipAddress': '192.168.1.100',
                'userAgent': 'Mozilla/5.0',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Notifications': [
            {
                'notificationId': 'NOTIF-20241220-001',
                'recipientId': 'USER001',
                'type': 'STOCK_ALERT',
                'title': 'Low Stock Alert',
                'message': 'Product PROD001 is below reorder point',
                'priority': 'HIGH',
                'isRead': False,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Reports': [
            {
                'reportId': 'REPORT-20241220-001',
                'reportType': 'DAILY_SALES',
                'title': 'Daily Sales Report',
                'description': 'Sales summary for 2024-12-20',
                'data': {
                    'totalOrders': 25,
                    'totalRevenue': Decimal('75000.00'),
                    'averageOrderValue': Decimal('3000.00')
                },
                'generatedBy': 'SYSTEM',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Settings': [
            {
                'settingKey': 'SYSTEM_CONFIG',
                'category': 'GENERAL',
                'value': {
                    'timezone': 'Asia/Kolkata',
                    'currency': 'INR',
                    'language': 'en',
                    'dateFormat': 'DD/MM/YYYY'
                },
                'description': 'System configuration settings',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ],
        'Journeys': [
            {
                'PK': 'JOURNEY#procurement-84882a7b',
                'SK': 'METADATA',
                'EntityType': 'Journey',
                'GSI1PK': 'JOURNEYS',
                'GSI1SK': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'CreatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'UpdatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'Data': {
                    'journeyId': 'procurement-84882a7b',
                    'name': 'Procurement Flow',
                    'description': 'Complete procurement workflow with variants',
                    'status': 'pending',
                    'variantSupport': True
                }
            }
        ]
    }

    # Insert sample data into each table
    for table_name, items in sample_data.items():
        try:
            table = dynamodb.Table(f'InventoryManagement-{table_name}')
            print_with_flush(f'📝 Inserting {len(items)} sample records in {table_name} table...')
            
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
                    print_with_flush(f'✅ Inserted: {item.get(list(item.keys())[0], "Unknown")}')
                    
        except Exception as e:
            print_with_flush(f'❌ Error seeding sample data: {str(e)}')
            traceback.print_exc()
            return False

    print_with_flush('✅ Sample data seeding completed successfully')
    return True


def main():
    """Main function to set up DynamoDB infrastructure with Variants & Units"""
    print_with_flush('🚀 Setting up Inventory Management System Infrastructure with Variants & Units in Mumbai Region...')
    print_with_flush('=' * 60)
    
    # Test AWS credentials
    try:
        print_with_flush('🔐 Testing AWS credentials...')
        sts = boto3.client('sts', region_name='ap-south-1')
        identity = sts.get_caller_identity()
        print_with_flush(f'✅ AWS Identity: {identity["Arn"]}')
        print_with_flush(f'✅ AWS Account: {identity["Account"]}')
        print_with_flush(f'✅ AWS Region: ap-south-1 (Mumbai)')
    except Exception as e:
        print_with_flush(f'❌ AWS authentication failed: {str(e)}')
        traceback.print_exc()
        return False
    
    print_with_flush('=' * 60)
    
    # Step 1: Create DynamoDB tables
    print_with_flush('🗄️ Step 1: Creating DynamoDB tables in Mumbai region...')
    created_tables = create_inventory_tables()
    
    if not created_tables:
        print_with_flush('❌ DynamoDB table setup failed')
        return False
    
    print_with_flush('=' * 60)
    
    # Step 2: Seed sample data
    print_with_flush('🌱 Step 2: Seeding sample data in Mumbai region...')
    if not seed_sample_data():
        print_with_flush('❌ Sample data seeding failed')
        return False
    
    print_with_flush('=' * 60)
    print_with_flush('🎉 Inventory Management System Setup Complete with Variants & Units!')
    print_with_flush('📦 System Features:')
    print_with_flush('   • Products table - Product catalog with variant support')
    print_with_flush('   • ProductVariants table - Variant management (size, color, weight)')
    print_with_flush('   • ProductUnits table - Unit management with conversion factors')
    print_with_flush('   • UnitConversions table - Unit conversion relationships')
    print_with_flush('   • Batches table - Batch tracking with variants and units')
    print_with_flush('   • StockLevels table - Stock monitoring with variants and units')
    print_with_flush('   • Orders table - Order processing with variant support')
    print_with_flush('   • OrderItems table - Order items with variants and units')
    print_with_flush('   • Suppliers table - Supplier information and performance')
    print_with_flush('   • Customers table - Customer information and preferences')
    print_with_flush('   • Riders table - Delivery personnel management')
    print_with_flush('   • Deliveries table - Delivery management and tracking')
    print_with_flush('   • PurchaseOrders table - Procurement workflow management')
    print_with_flush('   • CashCollections table - Payment tracking and reconciliation')
    print_with_flush('   • Discounts table - Discount and promotion management')
    print_with_flush('   • PricingRules table - Dynamic pricing with variants')
    print_with_flush('   • Categories table - Product categorization and hierarchy')
    print_with_flush('   • Locations table - Warehouse and delivery zone management')
    print_with_flush('   • Users table - User management and authentication')
    print_with_flush('   • AuditLogs table - System audit trails and compliance')
    print_with_flush('   • Notifications table - System notifications and alerts')
    print_with_flush('   • Reports table - Analytics and reporting data')
    print_with_flush('   • Settings table - System configuration and settings')
    print_with_flush('   • Journeys table - Workflow journey management and tracking')
    print_with_flush('💰 Billing Mode: PAY_PER_REQUEST (Free tier)')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('📊 Total Tables: 24')
    print_with_flush('🎨 Variant Support: Size, Color, Weight')
    print_with_flush('📏 Unit Support: Weight, Volume, Count, Length')
    print_with_flush('🔄 Unit Conversion: Automatic conversion factors')
    print_with_flush('=' * 60)
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Setup interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1) 