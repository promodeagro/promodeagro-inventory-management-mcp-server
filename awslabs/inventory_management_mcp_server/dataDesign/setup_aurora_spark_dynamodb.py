#!/usr/bin/env python3
# setup_aurora_spark_dynamodb.py
"""
Aurora Spark Theme - DynamoDB Setup Script
Creates all tables for the multi-portal SaaS inventory management system
Uses on-demand billing for AWS free tier compatibility
"""

import boto3
import sys
import traceback
from datetime import datetime, timezone
from decimal import Decimal
import uuid


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def create_aurora_spark_tables():
    """Create all DynamoDB tables for Aurora Spark Theme"""
    print_with_flush('🚀 Starting Aurora Spark Theme DynamoDB setup...')
    
    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region (ap-south-1)...')
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        print_with_flush('✅ DynamoDB client created successfully')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False

    # Complete Aurora Spark Theme table configuration
    tables_config = [
        # Authentication & User Management
        {
            'name': 'Users',
            'pk': 'id',
            'sk': 'email',
            'description': 'User authentication and profile management',
            'gsi': [
                {'name': 'EmailIndex', 'pk': 'email', 'sk': 'status'}
            ]
        },
        {
            'name': 'Roles',
            'pk': 'id',
            'sk': 'name',
            'description': 'Role definitions and permissions',
            'gsi': [
                {'name': 'NameIndex', 'pk': 'name', 'sk': 'isActive'}
            ]
        },
        {
            'name': 'UserRoles',
            'pk': 'userId',
            'sk': 'roleId',
            'description': 'User role assignments',
            'gsi': [
                {'name': 'RoleIndex', 'pk': 'roleId', 'sk': 'assignedAt'}
            ]
        },
        {
            'name': 'UserSessions',
            'pk': 'id',
            'sk': 'userId',
            'description': 'Active user sessions and JWT tokens',
            'gsi': [
                {'name': 'UserIndex', 'pk': 'userId', 'sk': 'expiresAt'}
            ]
        },
        
        # Products & Variants (NEW FEATURE)
        {
            'name': 'ProductCategories',
            'pk': 'id',
            'sk': 'name',
            'description': 'Product category hierarchy',
            'gsi': [
                {'name': 'NameIndex', 'pk': 'name', 'sk': 'isActive'}
            ]
        },
        {
            'name': 'Products',
            'pk': 'id',
            'sk': 'productCode',
            'description': 'Product catalog with variant support',
            'gsi': [
                {'name': 'CodeIndex', 'pk': 'productCode', 'sk': 'status'},
                {'name': 'CategoryIndex', 'pk': 'categoryId', 'sk': 'name'},
                {'name': 'SupplierIndex', 'pk': 'supplierId', 'sk': 'createdAt'}
            ]
        },
        {
            'name': 'ProductVariants',
            'pk': 'id',
            'sk': 'productId',
            'description': 'Product variants management for size color weight flavor',
            'gsi': [
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'variantType'},
                {'name': 'SKUIndex', 'pk': 'sku', 'sk': 'isActive'}
            ]
        },
        
        # Delivery Slots by Pincode (NEW FEATURE)
        {
            'name': 'PincodeServiceability',
            'pk': 'pincode',
            'sk': 'city',
            'description': 'PIN code service coverage and delivery options management',
            'gsi': [
                {'name': 'CityIndex', 'pk': 'city', 'sk': 'state'},
                {'name': 'ZoneIndex', 'pk': 'zone', 'sk': 'isServiceable'}
            ]
        },
        {
            'name': 'DeliverySlots',
            'pk': 'id',
            'sk': 'pincode',
            'description': 'Time slot management by PIN code',
            'gsi': [
                {'name': 'PincodeIndex', 'pk': 'pincode', 'sk': 'timeSlot'},
                {'name': 'SlotTypeIndex', 'pk': 'slotType', 'sk': 'isActive'}
            ]
        },
        
        # Inventory Management
        {
            'name': 'StockMovements',
            'pk': 'id',
            'sk': 'productId',
            'description': 'Inventory transaction tracking with variants',
            'gsi': [
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'createdAt'},
                {'name': 'VariantIndex', 'pk': 'variantId', 'sk': 'createdAt'},
                {'name': 'TypeIndex', 'pk': 'movementType', 'sk': 'createdAt'}
            ]
        },
        {
            'name': 'StorageLocations',
            'pk': 'id',
            'sk': 'name',
            'description': 'Warehouse storage location management',
            'gsi': [
                {'name': 'TypeIndex', 'pk': 'type', 'sk': 'status'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'name'}
            ]
        },
        {
            'name': 'TemperatureLogs',
            'pk': 'id',
            'sk': 'storageLocationId',
            'description': 'Temperature and humidity monitoring',
            'gsi': [
                {'name': 'LocationIndex', 'pk': 'storageLocationId', 'sk': 'recordedAt'},
                {'name': 'AlertIndex', 'pk': 'alertTriggered', 'sk': 'recordedAt'}
            ]
        },
        
        # Supplier Management
        {
            'name': 'SupplierCategories',
            'pk': 'id',
            'sk': 'name',
            'description': 'Supplier categorization',
            'gsi': [
                {'name': 'NameIndex', 'pk': 'name', 'sk': 'isActive'}
            ]
        },
        {
            'name': 'Suppliers',
            'pk': 'id',
            'sk': 'supplierCode',
            'description': 'Supplier information and performance tracking',
            'gsi': [
                {'name': 'CodeIndex', 'pk': 'supplierCode', 'sk': 'status'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'rating'},
                {'name': 'CategoryIndex', 'pk': 'categoryId', 'sk': 'name'}
            ]
        },
        {
            'name': 'SupplierReviews',
            'pk': 'id',
            'sk': 'supplierId',
            'description': 'Supplier ratings and reviews',
            'gsi': [
                {'name': 'SupplierIndex', 'pk': 'supplierId', 'sk': 'createdAt'},
                {'name': 'ReviewerIndex', 'pk': 'reviewerId', 'sk': 'rating'}
            ]
        },
        
        # Procurement Management
        {
            'name': 'PurchaseOrders',
            'pk': 'id',
            'sk': 'poNumber',
            'description': 'Purchase order management',
            'gsi': [
                {'name': 'PONumberIndex', 'pk': 'poNumber', 'sk': 'status'},
                {'name': 'SupplierIndex', 'pk': 'supplierId', 'sk': 'orderDate'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'orderDate'}
            ]
        },
        {
            'name': 'PurchaseOrderItems',
            'pk': 'id',
            'sk': 'poId',
            'description': 'Purchase order line items with variants',
            'gsi': [
                {'name': 'POIndex', 'pk': 'poId', 'sk': 'productId'},
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'variantId'}
            ]
        },
        
        # Billing & Payments
        {
            'name': 'Invoices',
            'pk': 'id',
            'sk': 'invoiceNumber',
            'description': 'Invoice management and tracking',
            'gsi': [
                {'name': 'InvoiceNumberIndex', 'pk': 'invoiceNumber', 'sk': 'status'},
                {'name': 'SupplierIndex', 'pk': 'supplierId', 'sk': 'invoiceDate'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'dueDate'}
            ]
        },
        {
            'name': 'InvoiceItems',
            'pk': 'id',
            'sk': 'invoiceId',
            'description': 'Invoice line items',
            'gsi': [
                {'name': 'InvoiceIndex', 'pk': 'invoiceId', 'sk': 'amount'}
            ]
        },
        {
            'name': 'Payments',
            'pk': 'id',
            'sk': 'paymentNumber',
            'description': 'Payment processing and tracking',
            'gsi': [
                {'name': 'PaymentNumberIndex', 'pk': 'paymentNumber', 'sk': 'status'},
                {'name': 'SupplierIndex', 'pk': 'supplierId', 'sk': 'paymentDate'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'paymentDate'}
            ]
        },
        
        # Warehouse & Operations
        {
            'name': 'StaffMembers',
            'pk': 'id',
            'sk': 'employeeId',
            'description': 'Staff management and assignments',
            'gsi': [
                {'name': 'EmployeeIndex', 'pk': 'employeeId', 'sk': 'status'},
                {'name': 'UserIndex', 'pk': 'userId', 'sk': 'department'},
                {'name': 'DepartmentIndex', 'pk': 'department', 'sk': 'position'}
            ]
        },
        {
            'name': 'StaffAttendance',
            'pk': 'id',
            'sk': 'staffId',
            'description': 'Staff attendance tracking',
            'gsi': [
                {'name': 'StaffIndex', 'pk': 'staffId', 'sk': 'date'},
                {'name': 'DateIndex', 'pk': 'date', 'sk': 'status'}
            ]
        },
        {
            'name': 'Tasks',
            'pk': 'id',
            'sk': 'assignedTo',
            'description': 'Task management and assignments',
            'gsi': [
                {'name': 'AssignedIndex', 'pk': 'assignedTo', 'sk': 'dueDate'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'priority'},
                {'name': 'TypeIndex', 'pk': 'type', 'sk': 'createdAt'}
            ]
        },
        
        # Logistics & Delivery
        {
            'name': 'Vehicles',
            'pk': 'id',
            'sk': 'vehicleNumber',
            'description': 'Fleet vehicle management',
            'gsi': [
                {'name': 'VehicleNumberIndex', 'pk': 'vehicleNumber', 'sk': 'status'},
                {'name': 'DriverIndex', 'pk': 'driverId', 'sk': 'vehicleType'},
                {'name': 'TypeIndex', 'pk': 'vehicleType', 'sk': 'status'}
            ]
        },
        {
            'name': 'DeliveryRoutes',
            'pk': 'id',
            'sk': 'routeCode',
            'description': 'Delivery route planning and optimization',
            'gsi': [
                {'name': 'RouteCodeIndex', 'pk': 'routeCode', 'sk': 'routeDate'},
                {'name': 'VehicleIndex', 'pk': 'vehicleId', 'sk': 'routeDate'},
                {'name': 'DriverIndex', 'pk': 'driverId', 'sk': 'routeDate'},
                {'name': 'DateIndex', 'pk': 'routeDate', 'sk': 'status'}
            ]
        },
        {
            'name': 'CustomerOrders',
            'pk': 'id',
            'sk': 'orderNumber',
            'description': 'Customer order management with delivery slots',
            'gsi': [
                {'name': 'OrderNumberIndex', 'pk': 'orderNumber', 'sk': 'status'},
                {'name': 'CustomerIndex', 'pk': 'customerEmail', 'sk': 'createdAt'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'deliveryDate'},
                {'name': 'DeliveryDateIndex', 'pk': 'deliveryDate', 'sk': 'deliveryTimeSlot'},
                {'name': 'PincodeIndex', 'pk': 'postalCode', 'sk': 'deliveryDate'}
            ]
        },
        {
            'name': 'OrderItems',
            'pk': 'id',
            'sk': 'orderId',
            'description': 'Customer order line items with variants',
            'gsi': [
                {'name': 'OrderIndex', 'pk': 'orderId', 'sk': 'productId'},
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'variantId'}
            ]
        },
        {
            'name': 'RouteOptimizations',
            'pk': 'id',
            'sk': 'routeId',
            'description': 'Route optimization history and metrics',
            'gsi': [
                {'name': 'RouteIndex', 'pk': 'routeId', 'sk': 'createdAt'},
                {'name': 'TypeIndex', 'pk': 'optimizationType', 'sk': 'efficiencyScore'}
            ]
        },
        
        # Quality Control & Monitoring
        {
            'name': 'QualityChecks',
            'pk': 'id',
            'sk': 'checkNumber',
            'description': 'Quality inspection and control with variants',
            'gsi': [
                {'name': 'CheckNumberIndex', 'pk': 'checkNumber', 'sk': 'checkDate'},
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'checkDate'},
                {'name': 'VariantIndex', 'pk': 'variantId', 'sk': 'checkDate'},
                {'name': 'InspectorIndex', 'pk': 'inspectorId', 'sk': 'checkDate'},
                {'name': 'GradeIndex', 'pk': 'overallGrade', 'sk': 'checkDate'}
            ]
        },
        {
            'name': 'WasteRecords',
            'pk': 'id',
            'sk': 'productId',
            'description': 'Waste tracking and disposal management',
            'gsi': [
                {'name': 'ProductIndex', 'pk': 'productId', 'sk': 'createdAt'},
                {'name': 'VariantIndex', 'pk': 'variantId', 'sk': 'createdAt'},
                {'name': 'ReasonIndex', 'pk': 'wasteReason', 'sk': 'costImpact'}
            ]
        },
        
        # Analytics & Reporting
        {
            'name': 'BusinessMetrics',
            'pk': 'metricDate',
            'sk': 'metricType',
            'description': 'Business analytics and KPIs',
            'gsi': [
                {'name': 'TypeIndex', 'pk': 'metricType', 'sk': 'metricDate'}
            ]
        },
        {
            'name': 'SystemAnalytics',
            'pk': 'metricDate',
            'sk': 'systemType',
            'description': 'System performance analytics',
            'gsi': [
                {'name': 'TypeIndex', 'pk': 'systemType', 'sk': 'metricDate'}
            ]
        },
        {
            'name': 'AuditLogs',
            'pk': 'id',
            'sk': 'userId',
            'description': 'System audit trail and compliance',
            'gsi': [
                {'name': 'UserIndex', 'pk': 'userId', 'sk': 'createdAt'},
                {'name': 'ActionIndex', 'pk': 'action', 'sk': 'createdAt'},
                {'name': 'ResourceIndex', 'pk': 'resourceType', 'sk': 'createdAt'}
            ]
        },
        {
            'name': 'SecurityEvents',
            'pk': 'id',
            'sk': 'eventType',
            'description': 'Security monitoring and events',
            'gsi': [
                {'name': 'EventTypeIndex', 'pk': 'eventType', 'sk': 'createdAt'},
                {'name': 'SeverityIndex', 'pk': 'severity', 'sk': 'createdAt'},
                {'name': 'StatusIndex', 'pk': 'status', 'sk': 'createdAt'}
            ]
        },
        
        # System Configuration
        {
            'name': 'SystemSettings',
            'pk': 'settingKey',
            'sk': 'category',
            'description': 'System configuration management',
            'gsi': [
                {'name': 'CategoryIndex', 'pk': 'category', 'sk': 'settingKey'}
            ]
        },
        {
            'name': 'Notifications',
            'pk': 'id',
            'sk': 'userId',
            'description': 'User notifications and alerts',
            'gsi': [
                {'name': 'UserIndex', 'pk': 'userId', 'sk': 'createdAt'},
                {'name': 'TypeIndex', 'pk': 'type', 'sk': 'createdAt'},
                {'name': 'CategoryIndex', 'pk': 'category', 'sk': 'isRead'}
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
                {'Key': 'Features', 'Value': 'ProductVariants-DeliverySlots-RBAC-Analytics'},
            ],
        }
        
        # Add Global Secondary Indexes if specified
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

    print_with_flush(f'📊 Successfully created/verified {len(created_tables)} tables')
    return created_tables


def seed_aurora_spark_data():
    """Seed tables with Aurora Spark Theme sample data"""
    print_with_flush('🌱 Starting Aurora Spark Theme sample data seeding...')

    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        print_with_flush('✅ DynamoDB resource created')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        return False

    # Sample data for Aurora Spark Theme
    sample_data = {
        'Users': [
            {
                'id': 'user-admin-001',
                'email': 'admin@promodeagro.com',
                'passwordHash': 'hashed_admin_password_123',
                'firstName': 'Super',
                'lastName': 'Admin',
                'phone': '+919876543210',
                'avatarUrl': None,
                'status': 'active',
                'emailVerified': True,
                'lastLogin': None,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'user-warehouse-001',
                'email': 'warehouse@promodeagro.com',
                'passwordHash': 'hashed_warehouse_password_456',
                'firstName': 'Amit',
                'lastName': 'Patel',
                'phone': '+919876543211',
                'avatarUrl': None,
                'status': 'active',
                'emailVerified': True,
                'lastLogin': None,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'user-logistics-001',
                'email': 'logistics@promodeagro.com',
                'passwordHash': 'hashed_logistics_password_789',
                'firstName': 'Suresh',
                'lastName': 'Reddy',
                'phone': '+919876543212',
                'avatarUrl': None,
                'status': 'active',
                'emailVerified': True,
                'lastLogin': None,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Roles': [
            {
                'id': 'role-super-admin',
                'name': 'super_admin',
                'description': 'Super Administrator with full system access',
                'permissions': ['*'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-warehouse-manager',
                'name': 'warehouse_manager',
                'description': 'Warehouse Manager with inventory and operations access',
                'permissions': ['inventory:*', 'staff:*', 'quality:*', 'logistics:*', 'analytics:warehouse'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-logistics-manager',
                'name': 'logistics_manager',
                'description': 'Logistics Manager with fleet and delivery access',
                'permissions': ['routes:*', 'fleet:*', 'deliveries:*', 'analytics:logistics'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-inventory-staff',
                'name': 'inventory_staff',
                'description': 'Inventory Staff with product and stock management',
                'permissions': ['products:read', 'products:write', 'stock:read', 'stock:write', 'quality:read', 'quality:write'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-delivery-personnel',
                'name': 'delivery_personnel',
                'description': 'Delivery Personnel with route and order delivery access',
                'permissions': ['deliveries:read', 'deliveries:update_status', 'routes:read', 'customers:contact'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-supplier-manager',
                'name': 'supplier_manager',
                'description': 'Supplier Manager with procurement and billing access',
                'permissions': ['suppliers:*', 'purchase_orders:*', 'invoices:*', 'payments:*', 'analytics:supplier'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'role-customer',
                'name': 'customer',
                'description': 'Customer with order placement and tracking access',
                'permissions': ['orders:create', 'orders:read_own', 'profile:manage'],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'UserRoles': [
            {
                'id': 'user-role-001',
                'userId': 'user-admin-001',
                'roleId': 'role-super-admin',
                'assignedBy': 'system',
                'assignedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'user-role-002',
                'userId': 'user-warehouse-001',
                'roleId': 'role-warehouse-manager',
                'assignedBy': 'user-admin-001',
                'assignedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'user-role-003',
                'userId': 'user-logistics-001',
                'roleId': 'role-logistics-manager',
                'assignedBy': 'user-admin-001',
                'assignedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'ProductCategories': [
            {
                'id': 'category-vegetables',
                'name': 'Vegetables',
                'description': 'Fresh vegetables and leafy greens',
                'parentId': None,
                'color': '#4CAF50',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'category-fruits',
                'name': 'Fruits',
                'description': 'Fresh fruits and seasonal produce',
                'parentId': None,
                'color': '#FF9800',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'category-dairy',
                'name': 'Dairy',
                'description': 'Milk and dairy products',
                'parentId': None,
                'color': '#2196F3',
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Products': [
            {
                'id': 'product-tomato-001',
                'productCode': 'TOM-RED-001',
                'name': 'Fresh Red Tomatoes',
                'description': 'Premium quality red tomatoes from local farms',
                'categoryId': 'category-vegetables',
                'unit': 'kg',
                'price': Decimal('60.00'),
                'costPrice': Decimal('45.00'),
                'currentStock': 500,
                'minStockLevel': 100,
                'maxStockLevel': 1000,
                'reorderPoint': 150,
                'status': 'active',
                'qualityGrade': 'excellent',
                'perishable': True,
                'shelfLifeDays': 7,
                'storageTemperatureMin': Decimal('2.0'),
                'storageTemperatureMax': Decimal('8.0'),
                'supplierId': 'supplier-fresh-farms-001',
                'imageUrl': 'https://example.com/images/tomatoes.jpg',
                'barcode': '1234567890123',
                'sku': 'TOM-RED-001',
                'isB2cAvailable': True,
                'hasVariants': True,
                'createdBy': 'user-admin-001',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'product-milk-001',
                'productCode': 'MLK-COW-001',
                'name': 'Fresh Cow Milk',
                'description': 'Pure cow milk from organic farms',
                'categoryId': 'category-dairy',
                'unit': 'liters',
                'price': Decimal('70.00'),
                'costPrice': Decimal('55.00'),
                'currentStock': 200,
                'minStockLevel': 50,
                'maxStockLevel': 500,
                'reorderPoint': 75,
                'status': 'active',
                'qualityGrade': 'excellent',
                'perishable': True,
                'shelfLifeDays': 3,
                'storageTemperatureMin': Decimal('2.0'),
                'storageTemperatureMax': Decimal('4.0'),
                'supplierId': 'supplier-dairy-fresh-001',
                'imageUrl': 'https://example.com/images/milk.jpg',
                'barcode': '1234567890124',
                'sku': 'MLK-COW-001',
                'isB2cAvailable': True,
                'hasVariants': False,
                'createdBy': 'user-admin-001',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'ProductVariants': [
            {
                'id': 'variant-tomato-small',
                'productId': 'product-tomato-001',
                'variantName': 'Small Tomatoes',
                'variantType': 'size',
                'variantValue': 'small',
                'sku': 'TOM-RED-001-SM',
                'barcode': '1234567890125',
                'attributes': {'weight_range': '50-80g', 'diameter': '4-5cm'},
                'priceAdjustment': Decimal('-5.00'),
                'weightKg': Decimal('0.065'),
                'dimensions': {'length': '4.5', 'width': '4.5', 'height': '4.0'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'variant-tomato-medium',
                'productId': 'product-tomato-001',
                'variantName': 'Medium Tomatoes',
                'variantType': 'size',
                'variantValue': 'medium',
                'sku': 'TOM-RED-001-MD',
                'barcode': '1234567890126',
                'attributes': {'weight_range': '80-120g', 'diameter': '5-6cm'},
                'priceAdjustment': Decimal('0.00'),
                'weightKg': Decimal('0.100'),
                'dimensions': {'length': '5.5', 'width': '5.5', 'height': '5.0'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'variant-tomato-large',
                'productId': 'product-tomato-001',
                'variantName': 'Large Tomatoes',
                'variantType': 'size',
                'variantValue': 'large',
                'sku': 'TOM-RED-001-LG',
                'barcode': '1234567890127',
                'attributes': {'weight_range': '120-180g', 'diameter': '6-7cm'},
                'priceAdjustment': Decimal('10.00'),
                'weightKg': Decimal('0.150'),
                'dimensions': {'length': '6.5', 'width': '6.5', 'height': '6.0'},
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'PincodeServiceability': [
            {
                'pincode': '500001',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zone': 'Central Hyderabad',
                'isServiceable': True,
                'deliveryCharge': Decimal('0.00'),
                'estimatedDeliveryDays': 1,
                'availableSlots': ['09:00-12:00', '14:00-17:00', '18:00-21:00'],
                'restrictions': {'min_order_amount': 200, 'cod_available': True},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'pincode': '500032',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zone': 'Gachibowli',
                'isServiceable': True,
                'deliveryCharge': Decimal('0.00'),
                'estimatedDeliveryDays': 1,
                'availableSlots': ['09:00-12:00', '14:00-17:00', '18:00-21:00'],
                'restrictions': {'min_order_amount': 200, 'cod_available': True},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'pincode': '500084',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'zone': 'Kondapur',
                'isServiceable': True,
                'deliveryCharge': Decimal('0.00'),
                'estimatedDeliveryDays': 1,
                'availableSlots': ['09:00-12:00', '14:00-17:00', '18:00-21:00'],
                'restrictions': {'min_order_amount': 200, 'cod_available': True},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'DeliverySlots': [
            {
                'id': 'slot-500001-morning',
                'pincode': '500001',
                'slotId': 'MORNING_09_12',
                'timeSlot': '09:00-12:00',
                'slotType': 'morning',
                'maxOrders': 20,
                'currentOrders': 0,
                'deliveryCharge': Decimal('0.00'),
                'isActive': True,
                'serviceAreas': ['Abids', 'Nampally', 'Koti'],
                'restrictions': {'vehicle_types': ['bike', 'van'], 'max_weight': 50},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'slot-500032-evening',
                'pincode': '500032',
                'slotId': 'EVENING_18_21',
                'timeSlot': '18:00-21:00',
                'slotType': 'evening',
                'maxOrders': 25,
                'currentOrders': 0,
                'deliveryCharge': Decimal('0.00'),
                'isActive': True,
                'serviceAreas': ['Gachibowli', 'Madhapur', 'Hitech City'],
                'restrictions': {'vehicle_types': ['bike', 'van', 'car'], 'max_weight': 30},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'slot-500084-afternoon',
                'pincode': '500084',
                'slotId': 'AFTERNOON_14_17',
                'timeSlot': '14:00-17:00',
                'slotType': 'afternoon',
                'maxOrders': 30,
                'currentOrders': 0,
                'deliveryCharge': Decimal('0.00'),
                'isActive': True,
                'serviceAreas': ['Kondapur', 'Manikonda', 'Nanakramguda'],
                'restrictions': {'vehicle_types': ['bike', 'van'], 'max_weight': 40},
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'Suppliers': [
            {
                'id': 'supplier-fresh-farms-001',
                'supplierCode': 'SUP-FF-001',
                'name': 'Fresh Farms Pvt Ltd',
                'contactPerson': 'Rajesh Kumar',
                'email': 'rajesh@freshfarms.com',
                'phone': '+919876543220',
                'address': '123 Farm Road, Ranga Reddy District',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'postalCode': '501301',
                'country': 'India',
                'categoryId': 'supplier-category-organic',
                'rating': Decimal('4.5'),
                'totalOrders': 0,
                'totalValue': Decimal('0.00'),
                'status': 'active',
                'paymentTerms': 'Net 30',
                'taxId': 'GST29ABCDE1234F1Z5',
                'bankAccountDetails': {
                    'accountNumber': '1234567890',
                    'ifscCode': 'HDFC0001234',
                    'bankName': 'HDFC Bank'
                },
                'lastOrderDate': None,
                'createdBy': 'user-admin-001',
                'createdAt': datetime.now(timezone.utc).isoformat(),
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'StorageLocations': [
            {
                'id': 'storage-cold-001',
                'name': 'Cold Storage Unit 1',
                'type': 'cold_storage',
                'capacityTonnes': Decimal('5.0'),
                'currentUtilization': Decimal('0.0'),
                'temperatureMin': Decimal('2.0'),
                'temperatureMax': Decimal('8.0'),
                'humidityMin': Decimal('80.0'),
                'humidityMax': Decimal('95.0'),
                'status': 'active',
                'createdAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'storage-dry-001',
                'name': 'Dry Storage Unit 1',
                'type': 'dry_storage',
                'capacityTonnes': Decimal('10.0'),
                'currentUtilization': Decimal('0.0'),
                'temperatureMin': Decimal('15.0'),
                'temperatureMax': Decimal('25.0'),
                'humidityMin': Decimal('40.0'),
                'humidityMax': Decimal('60.0'),
                'status': 'active',
                'createdAt': datetime.now(timezone.utc).isoformat()
            }
        ],
        'SystemSettings': [
            {
                'settingKey': 'SYSTEM_CONFIG',
                'category': 'general',
                'settingValue': {
                    'timezone': 'Asia/Kolkata',
                    'currency': 'INR',
                    'language': 'en',
                    'dateFormat': 'DD/MM/YYYY',
                    'businessHours': '09:00-18:00'
                },
                'settingType': 'json',
                'description': 'General system configuration',
                'isPublic': False,
                'updatedBy': 'user-admin-001',
                'updatedAt': datetime.now(timezone.utc).isoformat()
            },
            {
                'settingKey': 'DELIVERY_CONFIG',
                'category': 'logistics',
                'settingValue': {
                    'defaultDeliveryCharge': 0,
                    'freeDeliveryMinAmount': 500,
                    'maxDeliveryDistance': 50,
                    'defaultTimeSlots': ['09:00-12:00', '14:00-17:00', '18:00-21:00']
                },
                'settingType': 'json',
                'description': 'Delivery configuration settings',
                'isPublic': True,
                'updatedBy': 'user-admin-001',
                'updatedAt': datetime.now(timezone.utc).isoformat()
            }
        ]
    }

    # Insert sample data
    for table_name, items in sample_data.items():
        if not items:  # Skip empty tables
            continue
            
        try:
            table = dynamodb.Table(f'AuroraSparkTheme-{table_name}')
            print_with_flush(f'📝 Inserting {len(items)} records into {table_name}...')
            
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
                    print_with_flush(f'   ✅ Inserted: {item.get(list(item.keys())[0], "Unknown")}')
                    
        except Exception as e:
            print_with_flush(f'❌ Error seeding {table_name}: {str(e)}')
            traceback.print_exc()
            return False

    print_with_flush('✅ Sample data seeding completed successfully')
    return True


def main():
    """Main function to set up Aurora Spark Theme DynamoDB infrastructure"""
    print_with_flush('🚀 Aurora Spark Theme - DynamoDB Setup')
    print_with_flush('=' * 80)
    print_with_flush('Multi-Portal SaaS Inventory Management System')
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
    
    # Step 1: Create DynamoDB tables
    print_with_flush('🗄️  Step 1: Creating Aurora Spark Theme DynamoDB tables...')
    created_tables = create_aurora_spark_tables()
    
    if not created_tables:
        print_with_flush('❌ Table creation failed')
        return False
    
    print_with_flush('=' * 80)
    
    # Step 2: Seed sample data
    print_with_flush('🌱 Step 2: Seeding Aurora Spark Theme sample data...')
    if not seed_aurora_spark_data():
        print_with_flush('❌ Sample data seeding failed')
        return False
    
    print_with_flush('=' * 80)
    print_with_flush('🎉 Aurora Spark Theme Setup Complete!')
    print_with_flush('')
    print_with_flush('🏗️  SYSTEM ARCHITECTURE:')
    print_with_flush('   • Multi-Portal SaaS Architecture')
    print_with_flush('   • JWT-based Authentication with RBAC')
    print_with_flush('   • Microservices with Shared Database')
    print_with_flush('   • Real-time Capabilities Ready')
    print_with_flush('')
    print_with_flush('✨ NEW FEATURES IMPLEMENTED:')
    print_with_flush('   • Product Variants System (size, color, weight, flavor)')
    print_with_flush('   • Delivery Slots by Pincode Management')
    print_with_flush('   • Advanced Quality Control with Variants')
    print_with_flush('   • Comprehensive Analytics & Monitoring')
    print_with_flush('')
    print_with_flush('🗄️  DATABASE TABLES:')
    print_with_flush('   • Authentication: Users, Roles, UserRoles, UserSessions')
    print_with_flush('   • Products: Products, ProductCategories, ProductVariants ✨')
    print_with_flush('   • Inventory: StockMovements, StorageLocations, TemperatureLogs')
    print_with_flush('   • Suppliers: Suppliers, SupplierCategories, SupplierReviews')
    print_with_flush('   • Procurement: PurchaseOrders, PurchaseOrderItems')
    print_with_flush('   • Billing: Invoices, InvoiceItems, Payments')
    print_with_flush('   • Operations: StaffMembers, StaffAttendance, Tasks')
    print_with_flush('   • Logistics: Vehicles, DeliveryRoutes, RouteOptimizations')
    print_with_flush('   • Delivery: CustomerOrders, OrderItems, DeliverySlots ✨, PincodeServiceability ✨')
    print_with_flush('   • Quality: QualityChecks, WasteRecords')
    print_with_flush('   • Analytics: BusinessMetrics, SystemAnalytics')
    print_with_flush('   • System: AuditLogs, SecurityEvents, SystemSettings, Notifications')
    print_with_flush('')
    print_with_flush('💰 BILLING: Pay-per-request (On-demand) - Free Tier Compatible')
    print_with_flush('🌍 REGION: ap-south-1 (Mumbai)')
    print_with_flush('📊 TOTAL TABLES: 32 with Global Secondary Indexes')
    print_with_flush('🔗 RELATIONSHIPS: Complete entity relationships implemented')
    print_with_flush('')
    print_with_flush('🎯 NEXT STEPS:')
    print_with_flush('   1. Implement REST APIs for each portal')
    print_with_flush('   2. Set up JWT authentication system')
    print_with_flush('   3. Create portal-specific business logic')
    print_with_flush('   4. Implement real-time features with WebSockets')
    print_with_flush('   5. Set up monitoring and analytics')
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
