#!/usr/bin/env python3
# setup_optimized_aurora_spark_dynamodb.py
"""
Aurora Spark Theme - Optimized DynamoDB Setup Script
Reduced from 36 tables to 12 tables using efficient multi-table design
Uses on-demand billing for AWS free tier compatibility
"""

import boto3
import sys
import traceback
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
import uuid


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def convert_floats_to_decimal(obj):
    """Recursively convert all float values to Decimal and handle DynamoDB type compatibility"""
    if isinstance(obj, dict):
        converted = {}
        for key, value in obj.items():
            # Special handling for GSI boolean fields that need to be strings
            if key == 'isServiceable' and isinstance(value, bool):
                converted[key] = 'true' if value else 'false'
            elif key == 'isActive' and isinstance(value, bool):
                converted[key] = 'true' if value else 'false'
            else:
                converted[key] = convert_floats_to_decimal(value)
        return converted
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def create_optimized_aurora_tables():
    """Create optimized DynamoDB tables for Aurora Spark Theme"""
    print_with_flush('🚀 Starting Aurora Spark Theme Optimized DynamoDB setup...')
    print_with_flush('📊 Reducing from 36 tables to 12 efficient tables')
    
    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region (ap-south-1)...')
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        print_with_flush('✅ DynamoDB client created successfully')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False

    # Optimized Aurora Spark Theme table configuration - 12 tables only
    tables_config = [
        # 1. Authentication & Users (Combined: Users + Roles + Sessions)
        {
            'name': 'Users',
            'pk': 'userID',
            'sk': 'email',
            'description': 'User authentication with embedded roles and session management',
            'gsi': [
                {'name': 'EmailIndex', 'pk': 'email', 'sk': 'status'},
                {'name': 'RoleIndex', 'pk': 'primaryRole', 'sk': 'createdAt'}
            ]
        },
        
        # 2. Products (Combined: Products + Categories + Variants)
        {
            'name': 'Products',
            'pk': 'productID',
            'sk': 'category',
            'description': 'Product catalog with embedded variants and categories',
            'gsi': [
                {'name': 'CategoryIndex', 'pk': 'category', 'sk': 'name'},
                {'name': 'CodeIndex', 'pk': 'productCode', 'sk': 'status'},
                {'name': 'SupplierIndex', 'pk': 'supplierID', 'sk': 'createdAt'}
            ]
        },
        
        # 3. Inventory (Combined: Stock + Movements + Storage + Temperature)
        {
            'name': 'Inventory',
            'pk': 'productID',
            'sk': 'location#batch',
            'description': 'Inventory management with stock movements and storage data',
            'gsi': [
                {'name': 'LocationIndex', 'pk': 'storageLocation', 'sk': 'lastUpdated'},
                {'name': 'MovementIndex', 'pk': 'movementType', 'sk': 'createdAt'},
                {'name': 'BatchIndex', 'pk': 'batchNumber', 'sk': 'expiryDate'}
            ]
        },
        
        # 4. Orders (Combined: Customer Orders + Items + Delivery Slots)
        {
            'name': 'Orders',
            'pk': 'orderID',
            'sk': 'customerEmail',
            'description': 'Customer orders with embedded items and delivery slot management',
            'gsi': [
                {'name': 'CustomerIndex', 'pk': 'customerEmail', 'sk': 'createdAt'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'deliveryDate'},
                {'name': 'PincodeIndex', 'pk': 'deliveryPincode', 'sk': 'deliveryTimeSlot'},
                {'name': 'DeliveryDateIndex', 'pk': 'deliveryDate', 'sk': 'deliveryTimeSlot'}
            ]
        },
        
        # 5. Suppliers (Combined: Suppliers + Categories + Reviews + Performance)
        {
            'name': 'Suppliers',
            'pk': 'supplierID',
            'sk': 'supplierCode',
            'description': 'Supplier management with embedded categories and performance data',
            'gsi': [
                {'name': 'CodeIndex', 'pk': 'supplierCode', 'sk': 'status'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'rating'},
                {'name': 'CategoryIndex', 'pk': 'category', 'sk': 'name'}
            ]
        },
        
        # 6. Procurement (Combined: POs + Items + Invoices + Payments)
        {
            'name': 'Procurement',
            'pk': 'documentID',
            'sk': 'documentType',
            'description': 'Purchase orders invoices and payments management',
            'gsi': [
                {'name': 'SupplierIndex', 'pk': 'supplierID', 'sk': 'documentDate'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'documentDate'},
                {'name': 'TypeIndex', 'pk': 'documentType', 'sk': 'documentDate'}
            ]
        },
        
        # 7. Logistics (Combined: Routes + Vehicles + Optimization + Fleet)
        {
            'name': 'Logistics',
            'pk': 'entityID',
            'sk': 'entityType',
            'description': 'Logistics management with routes vehicles and optimization',
            'gsi': [
                {'name': 'TypeIndex', 'pk': 'entityType', 'sk': 'createdAt'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'entityType'},
                {'name': 'DateIndex', 'pk': 'operationDate', 'sk': 'entityType'}
            ]
        },
        
        # 8. Staff (Combined: Staff + Attendance + Tasks + Performance)
        {
            'name': 'Staff',
            'pk': 'staffID',
            'sk': 'employeeID',
            'description': 'Staff management with embedded attendance and task data',
            'gsi': [
                {'name': 'EmployeeIndex', 'pk': 'employeeID', 'sk': 'status'},
                {'name': 'DepartmentIndex', 'pk': 'department', 'sk': 'position'},
                {'name': 'UserIndex', 'pk': 'userID', 'sk': 'department'}
            ]
        },
        
        # 9. Quality (Combined: Quality Checks + Temperature + Waste + Compliance)
        {
            'name': 'Quality',
            'pk': 'checkID',
            'sk': 'productID#variantID',
            'description': 'Quality control with temperature monitoring and waste tracking',
            'gsi': [
                {'name': 'ProductIndex', 'pk': 'productID', 'sk': 'checkDate'},
                {'name': 'InspectorIndex', 'pk': 'inspectorID', 'sk': 'checkDate'},
                {'name': 'GradeIndex', 'pk': 'overallGrade', 'sk': 'checkDate'}
            ]
        },
        
        # 10. Delivery (Combined: Delivery Slots + Pincode Serviceability + Area Management)
        {
            'name': 'Delivery',
            'pk': 'pincodeID',
            'sk': 'slotID',
            'description': 'Delivery slot management by pincode with serviceability data',
            'gsi': [
                {'name': 'CityIndex', 'pk': 'city', 'sk': 'state'},
                {'name': 'SlotTypeIndex', 'pk': 'slotType', 'sk': 'timeSlot'},
                {'name': 'ServiceableIndex', 'pk': 'isServiceable', 'sk': 'deliveryCharge'}
            ]
        },
        
        # 11. Analytics (Combined: Business + System + Performance Metrics)
        {
            'name': 'Analytics',
            'pk': 'metricDate',
            'sk': 'metricType',
            'description': 'Business and system analytics with performance metrics',
            'gsi': [
                {'name': 'TypeIndex', 'pk': 'metricType', 'sk': 'metricDate'},
                {'name': 'CategoryIndex', 'pk': 'metricCategory', 'sk': 'metricDate'}
            ]
        },
        
        # 12. System (Combined: Settings + Notifications + Audit + Security)
        {
            'name': 'System',
            'pk': 'entityType',
            'sk': 'entityID',
            'description': 'System configuration notifications audit logs and security events',
            'gsi': [
                {'name': 'UserIndex', 'pk': 'userID', 'sk': 'createdAt'},
                {'name': 'TypeIndex', 'pk': 'eventType', 'sk': 'createdAt'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'priority'}
            ]
        }
    ]

    created_tables = []
    
    for table_config in tables_config:
        table_name = f'AuroraSparkTheme-{table_config["name"]}'
        
        try:
            print_with_flush(f'🔍 Checking if {table_name} exists...')
            response = dynamodb.describe_table(TableName=table_name)
            print_with_flush(f'✅ Table {table_name} already exists')
            print_with_flush(f'   Status: {response["Table"]["TableStatus"]}')
            created_tables.append(table_name)
            continue
            
        except dynamodb.exceptions.ResourceNotFoundException:
            print_with_flush(f'📋 Creating {table_name}...')
            pass
        except Exception as e:
            print_with_flush(f'❌ Error checking table: {str(e)}')
            continue

        # Base table definition
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
            'BillingMode': 'PAY_PER_REQUEST',  # On-demand for free tier
            'Tags': [
                {'Key': 'Project', 'Value': 'Aurora-Spark-Theme'},
                {'Key': 'Environment', 'Value': 'Development'},
                {'Key': 'BillingMode', 'Value': 'ON_DEMAND'},
                {'Key': 'Region', 'Value': 'ap-south-1'},
                {'Key': 'Purpose', 'Value': table_config['description']},
                {'Key': 'TableType', 'Value': table_config['name']},
                {'Key': 'OptimizedDesign', 'Value': '12-Tables-Multi-Entity'},
            ],
        }
        
        # Add Global Secondary Indexes
        if 'gsi' in table_config:
            gsi_list = []
            for gsi in table_config['gsi']:
                # Add GSI attributes to AttributeDefinitions if not already present
                gsi_pk_attr = {'AttributeName': gsi['pk'], 'AttributeType': 'S'}
                gsi_sk_attr = {'AttributeName': gsi['sk'], 'AttributeType': 'S'}
                
                if gsi_pk_attr not in table_definition['AttributeDefinitions']:
                    table_definition['AttributeDefinitions'].append(gsi_pk_attr)
                if gsi_sk_attr not in table_definition['AttributeDefinitions']:
                    table_definition['AttributeDefinitions'].append(gsi_sk_attr)
                
                gsi_definition = {
                    'IndexName': gsi['name'],
                    'KeySchema': [
                        {'AttributeName': gsi['pk'], 'KeyType': 'HASH'},
                        {'AttributeName': gsi['sk'], 'KeyType': 'RANGE'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
                gsi_list.append(gsi_definition)
            
            table_definition['GlobalSecondaryIndexes'] = gsi_list

        try:
            print_with_flush(f'   Creating table with {len(table_config.get("gsi", []))} GSIs...')
            response = dynamodb.create_table(**table_definition)
            print_with_flush(f'✅ {table_name} creation initiated')
            print_with_flush(f'   Status: {response["TableDescription"]["TableStatus"]}')

            # Wait for table to be active
            print_with_flush(f'⏳ Waiting for {table_name} to become active...')
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print_with_flush(f'✅ {table_name} is now active!')
            created_tables.append(table_name)

        except dynamodb.exceptions.ResourceInUseException:
            print_with_flush(f'⚠️  Table {table_name} already exists')
            created_tables.append(table_name)
        except Exception as e:
            print_with_flush(f'❌ Error creating {table_name}: {str(e)}')
            traceback.print_exc()

    print_with_flush(f'📊 Successfully created/verified {len(created_tables)} optimized tables')
    return created_tables


def seed_optimized_sample_data():
    """Seed optimized tables with sample data"""
    print_with_flush('🌱 Starting optimized sample data seeding...')

    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        print_with_flush('✅ DynamoDB resource created')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        return False

    # Optimized sample data structure
    sample_data = {
        'Users': [
            {
                'userID': 'user-admin-001',
                'email': 'admin@promodeagro.com',
                'passwordHash': hashlib.sha256('password123'.encode()).hexdigest(),
                'firstName': 'Super',
                'lastName': 'Admin',
                'phone': '+919876543210',
                'status': 'active',
                'emailVerified': True,
                'primaryRole': 'super_admin',
                'roles': ['super_admin'],
                'permissions': ['*'],
                'profile': {
                    'avatarUrl': None,
                    'department': 'administration',
                    'lastLogin': None
                },
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'userID': 'user-warehouse-001',
                'email': 'warehouse@promodeagro.com',
                'passwordHash': hashlib.sha256('password123'.encode()).hexdigest(),
                'firstName': 'Amit',
                'lastName': 'Patel',
                'phone': '+919876543211',
                'status': 'active',
                'emailVerified': True,
                'primaryRole': 'warehouse_manager',
                'roles': ['warehouse_manager'],
                'permissions': ['inventory:*', 'staff:*', 'quality:*', 'logistics:*', 'analytics:warehouse'],
                'profile': {
                    'avatarUrl': None,
                    'department': 'warehouse',
                    'lastLogin': None
                },
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'userID': 'user-logistics-001',
                'email': 'logistics@promodeagro.com',
                'passwordHash': hashlib.sha256('password123'.encode()).hexdigest(),
                'firstName': 'Suresh',
                'lastName': 'Reddy',
                'phone': '+919876543212',
                'status': 'active',
                'emailVerified': True,
                'primaryRole': 'logistics_manager',
                'roles': ['logistics_manager'],
                'permissions': ['routes:*', 'fleet:*', 'deliveries:*', 'analytics:logistics'],
                'profile': {
                    'avatarUrl': None,
                    'department': 'logistics',
                    'lastLogin': None
                },
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'userID': 'user-supplier-001',
                'email': 'supplier@promodeagro.com',
                'passwordHash': hashlib.sha256('password123'.encode()).hexdigest(),
                'firstName': 'Priya',
                'lastName': 'Sharma',
                'phone': '+919876543213',
                'status': 'active',
                'emailVerified': True,
                'primaryRole': 'supplier_manager',
                'roles': ['supplier_manager'],
                'permissions': ['suppliers:*', 'purchase_orders:*', 'invoices:*', 'payments:*', 'analytics:supplier'],
                'profile': {
                    'avatarUrl': None,
                    'department': 'procurement',
                    'lastLogin': None,
                    'loginCount': 0,
                    'passwordChangedAt': datetime.now(timezone.utc).isoformat()
                },
                'security': {
                    'failedLoginAttempts': 0,
                    'accountLockedUntil': None,
                    'passwordHistory': [hashlib.sha256('password123'.encode()).hexdigest()],
                    'twoFactorEnabled': False
                },
                'createdBy': 'user-admin-001',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Products': [
            {
                'productID': 'product-tomato-001',
                'category': 'vegetables',
                'productCode': 'TOM-RED-001',
                'name': 'Fresh Red Tomatoes',
                'description': 'Premium quality red tomatoes from local farms',
                'unit': 'kg',
                'price': Decimal('60.00'),
                'costPrice': Decimal('45.00'),
                'status': 'active',
                'qualityGrade': 'excellent',
                'perishable': True,
                'shelfLifeDays': 7,
                'storageRequirements': {
                    'temperatureMin': Decimal('2.0'),
                    'temperatureMax': Decimal('8.0'),
                    'humidityMin': Decimal('80.0'),
                    'humidityMax': Decimal('95.0'),
                    'storageType': 'cold_storage'
                },
                'supplierID': 'supplier-fresh-farms-001',
                'hasVariants': True,
                'variants': [
                    {
                        'variantID': 'variant-tomato-small',
                        'variantName': 'Small Tomatoes',
                        'variantType': 'size',
                        'variantValue': 'small',
                        'sku': 'TOM-RED-001-SM',
                        'barcode': '1234567890125',
                        'priceAdjustment': Decimal('-5.00'),
                        'attributes': {'weight_range': '50-80g', 'diameter': '4-5cm'},
                        'isActive': True
                    },
                    {
                        'variantID': 'variant-tomato-medium',
                        'variantName': 'Medium Tomatoes',
                        'variantType': 'size',
                        'variantValue': 'medium',
                        'sku': 'TOM-RED-001-MD',
                        'barcode': '1234567890126',
                        'priceAdjustment': Decimal('0.00'),
                        'attributes': {'weight_range': '80-120g', 'diameter': '5-6cm'},
                        'isActive': True
                    },
                    {
                        'variantID': 'variant-tomato-large',
                        'variantName': 'Large Tomatoes',
                        'variantType': 'size',
                        'variantValue': 'large',
                        'sku': 'TOM-RED-001-LG',
                        'barcode': '1234567890127',
                        'priceAdjustment': Decimal('10.00'),
                        'attributes': {'weight_range': '120-180g', 'diameter': '6-7cm'},
                        'isActive': True
                    }
                ],
                'categoryInfo': {
                    'categoryID': 'cat-vegetables',
                    'categoryName': 'Vegetables',
                    'categoryColor': '#4CAF50'
                },
                'isB2cAvailable': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Inventory': [
            {
                'productID': 'product-tomato-001',
                'location#batch': 'cold-storage-1#BATCH-TOM-001',
                'storageLocation': 'cold-storage-1',
                'batchNumber': 'BATCH-TOM-001',
                'currentStock': 500,
                'availableStock': 450,
                'reservedStock': 50,
                'variantStocks': {
                    'variant-tomato-small': {'stock': 150, 'reserved': 10},
                    'variant-tomato-medium': {'stock': 200, 'reserved': 25},
                    'variant-tomato-large': {'stock': 150, 'reserved': 15}
                },
                'movementHistory': [
                    {
                        'movementID': 'mov-001',
                        'movementType': 'inbound',
                        'quantity': 500,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'createdBy': 'user-warehouse-001'
                    }
                ],
                'storageInfo': {
                    'locationName': 'Cold Storage Unit 1',
                    'locationType': 'cold_storage',
                    'currentTemperature': Decimal('4.2'),
                    'currentHumidity': Decimal('85.5'),
                    'capacityUtilization': Decimal('0.75')
                },
                'expiryDate': '2024-01-27',
                'receivedDate': '2024-01-20',
                'qualityGrade': 'excellent',
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Orders': [
            {
                'orderID': 'order-001',
                'customerEmail': 'customer@example.com',
                'orderNumber': 'ORD-20240120-001',
                'customerInfo': {
                    'name': 'John Doe',
                    'phone': '+919876543220',
                    'email': 'customer@example.com'
                },
                'deliveryInfo': {
                    'address': '123 Green Valley Apartments, Kondapur',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'pincode': '500084'
                },
                'deliveryPincode': '500084',
                'deliveryDate': '2024-01-21',
                'deliveryTimeSlot': '09:00-12:00',
                'deliverySlotInfo': {
                    'slotID': 'slot-500084-morning',
                    'slotType': 'morning',
                    'deliveryCharge': Decimal('0.00'),
                    'maxOrders': 30,
                    'currentBookings': 15
                },
                'items': [
                    {
                        'itemID': 'item-001',
                        'productID': 'product-tomato-001',
                        'variantID': 'variant-tomato-medium',
                        'productName': 'Fresh Red Tomatoes',
                        'variantName': 'Medium Tomatoes',
                        'quantity': 2,
                        'unit': 'kg',
                        'unitPrice': Decimal('60.00'),
                        'totalPrice': Decimal('120.00'),
                        'qualityGrade': 'excellent'
                    }
                ],
                'orderSummary': {
                    'subtotal': Decimal('120.00'),
                    'deliveryCharge': Decimal('0.00'),
                    'totalAmount': Decimal('120.00')
                },
                'paymentInfo': {
                    'method': 'cod',
                    'status': 'pending'
                },
                'status': 'confirmed',
                'specialInstructions': None,
                'routeID': None,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Suppliers': [
            {
                'supplierID': 'supplier-fresh-farms-001',
                'supplierCode': 'SUP-FF-001',
                'name': 'Fresh Farms Pvt Ltd',
                'contactInfo': {
                    'contactPerson': 'Rajesh Kumar',
                    'email': 'rajesh@freshfarms.com',
                    'phone': '+919876543220'
                },
                'address': {
                    'street': '123 Farm Road, Ranga Reddy District',
                    'city': 'Hyderabad',
                    'state': 'Telangana',
                    'postalCode': '501301',
                    'country': 'India'
                },
                'category': 'organic_farms',
                'categoryInfo': {
                    'categoryName': 'Organic Farms',
                    'categoryColor': '#4CAF50'
                },
                'performance': {
                    'rating': Decimal('4.5'),
                    'totalOrders': 25,
                    'totalValue': Decimal('125000.00'),
                    'onTimeDeliveryRate': Decimal('95.5'),
                    'qualityScore': Decimal('4.8')
                },
                'businessTerms': {
                    'paymentTerms': 'Net 30',
                    'creditLimit': Decimal('100000.00'),
                    'discountRate': Decimal('2.5')
                },
                'compliance': {
                    'taxID': 'GST29ABCDE1234F1Z5',
                    'certifications': ['Organic', 'ISO9001'],
                    'bankDetails': {
                        'accountNumber': '1234567890',
                        'ifscCode': 'HDFC0001234',
                        'bankName': 'HDFC Bank'
                    }
                },
                'status': 'active',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Delivery': [
            {
                'pincodeID': '500084',
                'slotID': 'morning-09-12',
                'pincode': '500084',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zone': 'Kondapur',
                'isServiceable': 'true',
                'serviceInfo': {
                    'deliveryCharge': Decimal('0.00'),
                    'estimatedDeliveryDays': 1,
                    'serviceAreas': ['Kondapur', 'Manikonda', 'Nanakramguda'],
                    'restrictions': {
                        'minOrderAmount': 200,
                        'maxWeight': 50,
                        'codAvailable': True
                    }
                },
                'slotInfo': {
                    'timeSlot': '09:00-12:00',
                    'slotType': 'morning',
                    'maxOrders': 30,
                    'currentOrders': 15,
                    'deliveryCharge': Decimal('0.00'),
                    'isActive': True
                },
                'availableSlots': [
                    {'slot': '09:00-12:00', 'type': 'morning', 'capacity': 30},
                    {'slot': '14:00-17:00', 'type': 'afternoon', 'capacity': 25},
                    {'slot': '18:00-21:00', 'type': 'evening', 'capacity': 20}
                ],
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'pincodeID': '500032',
                'slotID': 'evening-18-21',
                'pincode': '500032',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zone': 'Gachibowli',
                'isServiceable': 'true',
                'serviceInfo': {
                    'deliveryCharge': Decimal('0.00'),
                    'estimatedDeliveryDays': 1,
                    'serviceAreas': ['Gachibowli', 'Madhapur', 'Hitech City'],
                    'restrictions': {
                        'minOrderAmount': 200,
                        'maxWeight': 40,
                        'codAvailable': True
                    }
                },
                'slotInfo': {
                    'timeSlot': '18:00-21:00',
                    'slotType': 'evening',
                    'maxOrders': 20,
                    'currentOrders': 8,
                    'deliveryCharge': Decimal('0.00'),
                    'isActive': True
                },
                'availableSlots': [
                    {'slot': '09:00-12:00', 'type': 'morning', 'capacity': 25},
                    {'slot': '14:00-17:00', 'type': 'afternoon', 'capacity': 22},
                    {'slot': '18:00-21:00', 'type': 'evening', 'capacity': 20}
                ],
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Staff': [
            {
                'staffID': 'staff-001',
                'employeeID': 'EMP-001',
                'userID': 'user-warehouse-001',
                'personalInfo': {
                    'firstName': 'Amit',
                    'lastName': 'Patel',
                    'phone': '+919876543211',
                    'email': 'warehouse@promodeagro.com'
                },
                'jobInfo': {
                    'department': 'warehouse',
                    'position': 'Warehouse Manager',
                    'shift': 'morning',
                    'shiftTiming': {
                        'startTime': '06:00',
                        'endTime': '14:00'
                    },
                    'hourlyRate': Decimal('300.00')
                },
                'performance': {
                    'score': Decimal('4.5'),
                    'totalTasksCompleted': 150,
                    'avgTaskCompletionTime': 45,
                    'qualityScore': Decimal('4.8')
                },
                'attendance': {
                    'totalDays': 25,
                    'presentDays': 24,
                    'lateDays': 1,
                    'attendanceRate': Decimal('96.0')
                },
                'currentTasks': [
                    {
                        'taskID': 'task-001',
                        'title': 'Quality check incoming tomatoes',
                        'type': 'quality_check',
                        'priority': 'high',
                        'status': 'pending',
                        'dueDate': '2024-01-21'
                    }
                ],
                'status': 'active',
                'hireDate': '2023-01-15',
                'supervisorID': None,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Logistics': [
            {
                'entityID': 'vehicle-001',
                'entityType': 'vehicle',
                'vehicleInfo': {
                    'vehicleNumber': 'TS07EA1234',
                    'vehicleType': 'van',
                    'model': 'Tata Ace',
                    'capacityKg': Decimal('1000.0'),
                    'fuelType': 'diesel'
                },
                'assignmentInfo': {
                    'driverID': 'staff-delivery-001',
                    'currentRoute': None,
                    'homeBase': 'warehouse-main'
                },
                'maintenance': {
                    'lastMaintenanceDate': '2024-01-15',
                    'nextMaintenanceDate': '2024-04-15',
                    'maintenanceCost': Decimal('5000.00')
                },
                'compliance': {
                    'insuranceExpiry': '2024-12-31',
                    'registrationExpiry': '2024-12-31',
                    'pollutionCertExpiry': '2024-06-30'
                },
                'status': 'active',
                'operationDate': '2024-01-20',
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'entityID': 'route-001',
                'entityType': 'route',
                'routeInfo': {
                    'routeCode': 'RT-HYD-KP-001',
                    'routeName': 'Kondapur-Gachibowli Route',
                    'coverageAreas': ['Kondapur', 'Gachibowli', 'Madhapur']
                },
                'assignments': {
                    'vehicleID': 'vehicle-001',
                    'driverID': 'staff-delivery-001',
                    'routeDate': '2024-01-21'
                },
                'optimization': {
                    'totalDistanceKm': Decimal('45.5'),
                    'estimatedDurationMinutes': 240,
                    'fuelCostEstimate': Decimal('850.00'),
                    'optimizationType': 'hybrid'
                },
                'orders': ['order-001'],
                'performance': {
                    'actualDistance': None,
                    'actualDuration': None,
                    'fuelCostActual': None,
                    'onTimeDeliveryRate': None
                },
                'status': 'planned',
                'operationDate': '2024-01-21',
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Analytics': [
            {
                'metricDate': '2024-01-20',
                'metricType': 'business_daily',
                'metricCategory': 'business',
                'metrics': {
                    'totalRevenue': Decimal('15000.00'),
                    'totalOrders': 25,
                    'totalCustomers': 20,
                    'newCustomers': 3,
                    'avgOrderValue': Decimal('600.00'),
                    'inventoryValue': Decimal('250000.00'),
                    'wastePercentage': Decimal('2.1'),
                    'deliveryEfficiency': Decimal('95.5'),
                    'qualityScore': Decimal('4.7'),
                    'supplierPerformance': 4.5
                },
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'System': [
            {
                'entityType': 'setting',
                'entityID': 'system-config',
                'settingKey': 'SYSTEM_CONFIG',
                'category': 'general',
                'value': {
                    'timezone': 'Asia/Kolkata',
                    'currency': 'INR',
                    'language': 'en',
                    'dateFormat': 'DD/MM/YYYY',
                    'businessHours': '09:00-18:00'
                },
                'isPublic': False,
                'description': 'General system configuration',
                'updatedBy': 'user-admin-001',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'entityType': 'notification',
                'entityID': 'notif-001',
                'userID': 'user-warehouse-001',
                'title': 'Low Stock Alert',
                'message': 'Tomatoes stock is below reorder point',
                'type': 'warning',
                'category': 'inventory',
                'isRead': False,
                'priority': 'high',
                'actionUrl': '/inventory/products/product-tomato-001',
                'metadata': {
                    'productID': 'product-tomato-001',
                    'currentStock': 150,
                    'reorderPoint': 200
                },
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ]
    }

    # Insert sample data
    for table_name, items in sample_data.items():
        if not items:
            continue
            
        try:
            table = dynamodb.Table(f'AuroraSparkTheme-{table_name}')
            print_with_flush(f'📝 Inserting {len(items)} records into {table_name}...')
            
            with table.batch_writer() as batch:
                for item in items:
                    # Convert all floats to Decimal before inserting
                    clean_item = convert_floats_to_decimal(item)
                    batch.put_item(Item=clean_item)
                    identifier = item.get(list(item.keys())[0], "Unknown")
                    print_with_flush(f'   ✅ Inserted: {identifier}')
                    
        except Exception as e:
            print_with_flush(f'❌ Error seeding {table_name}: {str(e)}')
            traceback.print_exc()
            return False

    print_with_flush('✅ Optimized sample data seeding completed')
    return True


def main():
    """Main function for optimized Aurora Spark Theme setup"""
    print_with_flush('🚀 Aurora Spark Theme - Optimized DynamoDB Setup')
    print_with_flush('=' * 80)
    print_with_flush('Multi-Portal SaaS Inventory Management System')
    print_with_flush('Optimized Design: 12 Tables (vs 36 original)')
    print_with_flush('Features: Product Variants + Delivery Slots by Pincode')
    print_with_flush('=' * 80)
    
    # Test AWS credentials
    try:
        print_with_flush('🔐 Testing AWS credentials...')
        sts = boto3.client('sts', region_name='ap-south-1')
        identity = sts.get_caller_identity()
        print_with_flush(f'✅ AWS Account: {identity["Account"]}')
        print_with_flush(f'✅ AWS Region: ap-south-1 (Mumbai - Free Tier)')
        print_with_flush(f'✅ User ARN: {identity["Arn"]}')
    except Exception as e:
        print_with_flush(f'❌ AWS authentication failed: {str(e)}')
        return False
    
    print_with_flush('=' * 80)
    
    # Step 1: Create optimized tables
    print_with_flush('🗄️  Step 1: Creating 12 optimized Aurora Spark Theme tables...')
    created_tables = create_optimized_aurora_tables()
    
    if not created_tables:
        print_with_flush('❌ Table creation failed')
        return False
    
    print_with_flush('=' * 80)
    
    # Step 2: Seed optimized sample data
    print_with_flush('🌱 Step 2: Seeding optimized sample data...')
    if not seed_optimized_sample_data():
        print_with_flush('❌ Sample data seeding failed')
        return False
    
    print_with_flush('=' * 80)
    print_with_flush('🎉 Aurora Spark Theme Optimized Setup Complete!')
    print_with_flush('')
    print_with_flush('🏗️  OPTIMIZED ARCHITECTURE:')
    print_with_flush('   • 12 Tables (vs 36 original) - 66% reduction!')
    print_with_flush('   • Multi-entity tables with JSON embedding')
    print_with_flush('   • Efficient GSI design for complex queries')
    print_with_flush('   • Maintained data integrity and relationships')
    print_with_flush('')
    print_with_flush('📊 OPTIMIZED TABLE STRUCTURE:')
    print_with_flush('   1. Users - Authentication + roles + sessions')
    print_with_flush('   2. Products - Catalog + variants + categories')
    print_with_flush('   3. Inventory - Stock + movements + storage + temperature')
    print_with_flush('   4. Orders - Customer orders + items + delivery slots')
    print_with_flush('   5. Suppliers - Suppliers + categories + reviews + performance')
    print_with_flush('   6. Procurement - POs + items + invoices + payments')
    print_with_flush('   7. Logistics - Routes + vehicles + drivers + optimization')
    print_with_flush('   8. Staff - Staff + attendance + tasks + performance')
    print_with_flush('   9. Quality - Quality checks + temperature + waste')
    print_with_flush('  10. Delivery - Delivery slots + pincode serviceability')
    print_with_flush('  11. Analytics - Business + system + performance metrics')
    print_with_flush('  12. System - Settings + notifications + audit + security')
    print_with_flush('')
    print_with_flush('✨ KEY FEATURES:')
    print_with_flush('   • Product Variants embedded in Products table')
    print_with_flush('   • Delivery Slots by Pincode in Delivery table')
    print_with_flush('   • JSON embedding for related data')
    print_with_flush('   • Optimized GSIs for efficient querying')
    print_with_flush('   • Reduced DynamoDB costs and complexity')
    print_with_flush('')
    print_with_flush('💰 BILLING: Pay-per-request (On-demand) - Free Tier Optimized')
    print_with_flush('🌍 REGION: ap-south-1 (Mumbai)')
    print_with_flush('📊 TOTAL TABLES: 12 (Optimized from 36)')
    print_with_flush('🎯 DESIGN: Multi-table with JSON embedding')
    print_with_flush('=' * 80)
    
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
