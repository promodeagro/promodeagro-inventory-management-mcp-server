#!/usr/bin/env python3
"""
Create Customer Order Flow Journey

This script creates and executes a comprehensive customer order journey that simulates
the complete order-to-delivery process with realistic data flow.

Customer Order Flow:
1. Customer Order Initiation
2. Order Processing & Validation
3. Pricing & Discount Application
4. Stock Reservation & Adjustment
5. Rider Assignment & Delivery Planning
6. Cash Collection & Reconciliation
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


def get_customer_order_rules_for_stage(stage_id, journey_id):
    """Get AI rules for customer order journey stages"""
    
    base_rules = {
        'order_initiation': [
            {
                'ruleId': f'rule-{stage_id}-customer-validation-001',
                'title': 'Validate customer information and credit',
                'description': 'Verify customer exists, is active, and has good payment history',
                'type': 'validation_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['customers'],
                    'conditions': [
                        {
                            'field': 'isActive',
                            'operator': 'equals',
                            'value': True
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Check if customer is active and has good payment history before processing order.',
                    'jsonRule': {
                        'conditions': {
                            'customer_active': True,
                            'payment_history': 'GOOD',
                            'credit_limit': 'sufficient'
                        },
                        'actions': {
                            'validate_customer': True,
                            'check_credit_limit': True,
                            'apply_payment_terms': True
                        }
                    }
                }
            }
        ],
        'order_processing': [
            {
                'ruleId': f'rule-{stage_id}-order-validation-001',
                'title': 'Validate order quantities and product availability',
                'description': 'Check if requested products are available in sufficient quantities',
                'type': 'validation_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['orders', 'stock_levels'],
                    'conditions': [
                        {
                            'field': 'availableStock',
                            'operator': 'greater_than_or_equal',
                            'value': 'orderQuantity'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Verify that requested quantities are available in stock before confirming order.',
                    'jsonRule': {
                        'conditions': {
                            'stock_available': 'quantity <= available_stock',
                            'product_active': True,
                            'delivery_possible': True
                        },
                        'actions': {
                            'reserve_stock': True,
                            'calculate_delivery_time': True,
                            'validate_order': True
                        }
                    }
                }
            }
        ],
        'pricing_discounts': [
            {
                'ruleId': f'rule-{stage_id}-pricing-rules-001',
                'title': 'Apply pricing rules and customer discounts',
                'description': 'Calculate final pricing based on customer tier, bulk discounts, and promotions',
                'type': 'pricing_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['orders', 'customers'],
                    'conditions': [
                        {
                            'field': 'customerType',
                            'operator': 'in',
                            'value': ['REGULAR', 'PREMIUM', 'VIP']
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Apply customer-specific pricing, bulk discounts, and promotional offers.',
                    'jsonRule': {
                        'conditions': {
                            'customer_tier': 'REGULAR|PREMIUM|VIP',
                            'order_value': '> minimum_for_discount',
                            'promotion_active': True
                        },
                        'actions': {
                            'apply_customer_discount': True,
                            'apply_bulk_discount': True,
                            'apply_promotion': True,
                            'calculate_final_price': True
                        }
                    }
                }
            }
        ],
        'stock_reservation': [
            {
                'ruleId': f'rule-{stage_id}-stock-reservation-001',
                'title': 'Reserve stock for customer order',
                'description': 'Reserve available stock and update inventory levels',
                'type': 'inventory_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['stock_levels', 'orders'],
                    'conditions': [
                        {
                            'field': 'availableStock',
                            'operator': 'greater_than',
                            'value': 0
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Reserve stock for customer order and update available quantities.',
                    'jsonRule': {
                        'conditions': {
                            'stock_sufficient': True,
                            'order_confirmed': True
                        },
                        'actions': {
                            'reserve_stock': True,
                            'update_available_stock': True,
                            'update_reserved_stock': True,
                            'notify_fulfillment': True
                        }
                    }
                }
            }
        ],
        'rider_assignment': [
            {
                'ruleId': f'rule-{stage_id}-rider-selection-001',
                'title': 'Assign best available rider for delivery',
                'description': 'Select rider based on location, availability, and performance rating',
                'type': 'assignment_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['riders', 'deliveries'],
                    'conditions': [
                        {
                            'field': 'isAvailable',
                            'operator': 'equals',
                            'value': True
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Select available rider with best rating and proximity to delivery location.',
                    'jsonRule': {
                        'conditions': {
                            'rider_available': True,
                            'rating_minimum': Decimal('4.0'),
                            'location_proximity': 'optimal'
                        },
                        'actions': {
                            'assign_rider': True,
                            'calculate_route': True,
                            'estimate_delivery_time': True,
                            'notify_rider': True
                        }
                    }
                }
            }
        ],
        'cash_collection': [
            {
                'ruleId': f'rule-{stage_id}-payment-processing-001',
                'title': 'Process payment and update collection records',
                'description': 'Record payment method, amount, and update cash collection tracking',
                'type': 'payment_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['cash_collections', 'orders'],
                    'conditions': [
                        {
                            'field': 'paymentStatus',
                            'operator': 'equals',
                            'value': 'PENDING'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Process payment, update collection records, and reconcile with order.',
                    'jsonRule': {
                        'conditions': {
                            'payment_received': True,
                            'amount_matches': True,
                            'delivery_completed': True
                        },
                        'actions': {
                            'record_payment': True,
                            'update_collection_status': True,
                            'update_rider_earnings': True,
                            'send_receipt': True
                        }
                    }
                }
            }
        ]
    }
    
    return base_rules.get(stage_id, [])


def create_customer_order_journey(journey_name="Customer Order Flow", journey_id=None):
    """Create a complete customer order journey with all stages"""
    print_with_flush('🚀 Starting customer order journey creation...')
    
    if journey_id is None:
        journey_id = f'customer-order-{uuid.uuid4().hex[:8]}'
    
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    print_with_flush(f'📝 Creating customer order journey with ID: {journey_id}')
    
    # 1. Journey Metadata
    journey_item = {
        'PK': f'JOURNEY#{journey_id}',
        'SK': 'METADATA',
        'EntityType': 'Journey',
        'GSI1PK': 'JOURNEYS',
        'GSI1SK': timestamp,
        'CreatedAt': timestamp,
        'UpdatedAt': timestamp,
        'Data': {
            'journeyId': journey_id,
            'name': journey_name,
            'description': 'Complete customer order workflow from order placement to cash collection',
            'status': 'pending',
            'createdBy': 'system',
            'priority': 'high',
            'journeyType': 'customer_order',
            'source': {
                'type': 'customer-order',
                'triggerType': 'customer_initiated',
                'triggerSource': 'customer_portal',
                'version': '1.0.0',
            },
            'configuration': {
                'timeout': 1800,  # 30 minutes for complete order
                'maxRetries': 3,
                'enableNotifications': True,
                'enableDetailedLogging': True,
                'validateAtEachStage': True,
                'aiAssisted': True,
                'ruleEngineVersion': 'v1.0',
            },
            'currentStageIndex': 0,
            'currentStageId': 'order_initiation',
            'overallProgress': 0,
            'currentJobs': {},
            'aggregates': {
                'totalJobs': 0,
                'completedJobs': 0,
                'failedJobs': 0,
                'totalExecutionTime': '0m',
                'totalLogs': 0,
                'totalErrors': 0,
                'totalWarnings': 0,
                'totalRules': 0,
                'activeRules': 0,
            },
            'stageSummary': {
                'order_initiation': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'order_processing': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'pricing_discounts': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'stock_reservation': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'rider_assignment': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'cash_collection': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
            },
            'aiConfig': {
                'enabled': True,
                'ruleTypes': ['validation_rule', 'pricing_rule', 'inventory_rule', 'assignment_rule', 'payment_rule'],
                'priorityLevels': ['low', 'medium', 'high', 'critical'],
                'scopes': ['global', 'project', 'stage'],
                'defaultScope': 'global',
                'autoApplyRules': True,
                'customRulesEnabled': True,
            },
        },
    }
    
    # 2. Complete Stage Definitions
    stages = [
        # Stage 0: Order Initiation
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#00#order_initiation',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '00',
            'Data': {
                'stageId': 'order_initiation',
                'name': 'Order Initiation',
                'description': 'Customer places order and system validates customer information',
                'order': 0,
                'canSkip': False,
                'estimatedDuration': '5m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['validation_rule'],
                'steps': [
                    {
                        'id': 'customer_validation',
                        'name': 'Customer Validation',
                        'description': 'Verify customer exists and is active',
                        'order': 0,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                    {
                        'id': 'order_creation',
                        'name': 'Order Creation',
                        'description': 'Create initial order record',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                ],
            },
        },
        # Stage 1: Order Processing
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#01#order_processing',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '01',
            'Data': {
                'stageId': 'order_processing',
                'name': 'Order Processing',
                'description': 'Validate order details and product availability',
                'order': 1,
                'canSkip': False,
                'estimatedDuration': '8m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['validation_rule'],
                'steps': [
                    {
                        'id': 'product_validation',
                        'name': 'Product Validation',
                        'description': 'Check if products are available and active',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                    {
                        'id': 'quantity_validation',
                        'name': 'Quantity Validation',
                        'description': 'Verify requested quantities are available',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                    {
                        'id': 'order_confirmation',
                        'name': 'Order Confirmation',
                        'description': 'Confirm order and calculate initial pricing',
                        'order': 2,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                ],
            },
        },
        # Stage 2: Pricing & Discounts
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#02#pricing_discounts',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '02',
            'Data': {
                'stageId': 'pricing_discounts',
                'name': 'Pricing & Discounts',
                'description': 'Apply pricing rules, customer discounts, and promotions',
                'order': 2,
                'canSkip': False,
                'estimatedDuration': '10m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['pricing_rule'],
                'steps': [
                    {
                        'id': 'base_pricing',
                        'name': 'Base Pricing',
                        'description': 'Calculate base pricing for all items',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'customer_discounts',
                        'name': 'Customer Discounts',
                        'description': 'Apply customer-specific discounts and loyalty benefits',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'bulk_discounts',
                        'name': 'Bulk Discounts',
                        'description': 'Apply quantity-based bulk discounts',
                        'order': 2,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'promotional_offers',
                        'name': 'Promotional Offers',
                        'description': 'Apply active promotional offers and coupons',
                        'order': 3,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                ],
            },
        },
        # Stage 3: Stock Reservation
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#03#stock_reservation',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '03',
            'Data': {
                'stageId': 'stock_reservation',
                'name': 'Stock Reservation',
                'description': 'Reserve inventory and update stock levels',
                'order': 3,
                'canSkip': False,
                'estimatedDuration': '8m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['inventory_rule'],
                'steps': [
                    {
                        'id': 'stock_check',
                        'name': 'Stock Check',
                        'description': 'Verify final stock availability',
                        'order': 0,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['inventory_rule'],
                    },
                    {
                        'id': 'stock_reservation',
                        'name': 'Stock Reservation',
                        'description': 'Reserve stock for customer order',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['inventory_rule'],
                    },
                    {
                        'id': 'inventory_update',
                        'name': 'Inventory Update',
                        'description': 'Update available and reserved stock levels',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['inventory_rule'],
                    },
                ],
            },
        },
        # Stage 4: Rider Assignment
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#04#rider_assignment',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '04',
            'Data': {
                'stageId': 'rider_assignment',
                'name': 'Rider Assignment',
                'description': 'Assign best available rider and plan delivery',
                'order': 4,
                'canSkip': False,
                'estimatedDuration': '12m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['assignment_rule'],
                'steps': [
                    {
                        'id': 'rider_search',
                        'name': 'Rider Search',
                        'description': 'Find available riders in delivery area',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['assignment_rule'],
                    },
                    {
                        'id': 'rider_selection',
                        'name': 'Rider Selection',
                        'description': 'Select best rider based on rating and proximity',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['assignment_rule'],
                    },
                    {
                        'id': 'delivery_planning',
                        'name': 'Delivery Planning',
                        'description': 'Plan delivery route and estimate time',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['assignment_rule'],
                    },
                    {
                        'id': 'rider_notification',
                        'name': 'Rider Notification',
                        'description': 'Notify assigned rider of new delivery',
                        'order': 3,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['assignment_rule'],
                    },
                ],
            },
        },
        # Stage 5: Cash Collection
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#05#cash_collection',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '05',
            'Data': {
                'stageId': 'cash_collection',
                'name': 'Cash Collection',
                'description': 'Process payment and update collection records',
                'order': 5,
                'canSkip': False,
                'estimatedDuration': '15m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['payment_rule'],
                'steps': [
                    {
                        'id': 'payment_processing',
                        'name': 'Payment Processing',
                        'description': 'Process customer payment method',
                        'order': 0,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['payment_rule'],
                    },
                    {
                        'id': 'collection_recording',
                        'name': 'Collection Recording',
                        'description': 'Record payment in collection system',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['payment_rule'],
                    },
                    {
                        'id': 'rider_earnings',
                        'name': 'Rider Earnings',
                        'description': 'Update rider earnings and commission',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['payment_rule'],
                    },
                    {
                        'id': 'receipt_generation',
                        'name': 'Receipt Generation',
                        'description': 'Generate and send payment receipt',
                        'order': 3,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['payment_rule'],
                    },
                ],
            },
        },
    ]
    
    # 3. Create Rules for each stage
    all_rules = []
    for stage in stages:
        stage_id = stage['Data']['stageId']
        stage_rules = get_customer_order_rules_for_stage(stage_id, journey_id)
        all_rules.extend(stage_rules)
    
    return journey_item, stages, all_rules


def save_journey_to_dynamodb(journey_item, stages, rules):
    """Save journey data to DynamoDB using multi-table design"""
    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB client created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False
    
    try:
        # Save journey metadata to Journeys table
        print_with_flush('📝 Saving journey metadata...')
        journeys_table = dynamodb.Table('InventoryManagement-Journeys')
        journeys_table.put_item(Item=journey_item)
        print_with_flush('✅ Journey metadata saved successfully')
        
        # Save stages to Journeys table
        print_with_flush('📝 Saving journey stages...')
        for stage in stages:
            journeys_table.put_item(Item=stage)
        print_with_flush(f'✅ {len(stages)} stages saved successfully')
        
        # Save rules to Journeys table
        print_with_flush('📝 Saving journey rules...')
        for rule in rules:
            rule_item = {
                'PK': f'JOURNEY#{journey_item["Data"]["journeyId"]}',
                'SK': f'RULE#{rule["ruleId"]}',
                'EntityType': 'JourneyRule',
                'GSI1PK': f'JOURNEY#{journey_item["Data"]["journeyId"]}#RULES',
                'GSI1SK': rule['ruleId'],
                'CreatedAt': journey_item['CreatedAt'],
                'UpdatedAt': journey_item['UpdatedAt'],
                'Data': rule
            }
            journeys_table.put_item(Item=rule_item)
        print_with_flush(f'✅ {len(rules)} rules saved successfully')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error saving journey data: {str(e)}')
        traceback.print_exc()
        return False


def execute_customer_order_journey(journey_id):
    """Execute a realistic customer order journey by populating data step by step"""
    print_with_flush('🚀 Executing Realistic Customer Order Journey...')
    print_with_flush('=' * 60)
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        # Get table references
        customers_table = dynamodb.Table('InventoryManagement-Customers')
        orders_table = dynamodb.Table('InventoryManagement-Orders')
        products_table = dynamodb.Table('InventoryManagement-Products')
        stock_levels_table = dynamodb.Table('InventoryManagement-StockLevels')
        riders_table = dynamodb.Table('InventoryManagement-Riders')
        deliveries_table = dynamodb.Table('InventoryManagement-Deliveries')
        cash_collections_table = dynamodb.Table('InventoryManagement-CashCollections')
        
        print_with_flush('✅ DynamoDB tables connected successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Failed to connect to DynamoDB: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 1: Customer Order Initiation (User Action: Customer places order)
    print_with_flush('👤 Step 1: Customer Order Initiation...')
    try:
        # Simulate customer placing order
        customer_id = 'CUST001'
        order_id = f'ORD-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        
        # Check customer status
        customer_response = customers_table.get_item(
            Key={'customerId': customer_id, 'customerType': 'REGULAR'}
        )
        
        if 'Item' in customer_response:
            customer_data = customer_response['Item']
            print_with_flush(f'👤 Customer: {customer_data["name"]}')
            print_with_flush(f'📞 Phone: {customer_data["phone"]}')
            print_with_flush(f'📧 Email: {customer_data["email"]}')
            print_with_flush(f'⭐ Status: {"Active" if customer_data["isActive"] else "Inactive"}')
            
            if customer_data['isActive']:
                print_with_flush('✅ Customer validation successful')
                
                # Create order
                order_data = {
                    'orderId': order_id,
                    'customerId': customer_id,
                    'productId': 'PROD001',
                    'quantity': 50,
                    'unitPrice': Decimal('60.00'),
                    'totalAmount': Decimal('3000.00'),
                    'status': 'PENDING',
                    'orderDate': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'deliveryAddress': '123 Main St, Mumbai',
                    'paymentMethod': 'CASH_ON_DELIVERY',
                    'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
                
                orders_table.put_item(Item=order_data)
                print_with_flush(f'📋 Order Created: {order_id}')
                print_with_flush(f'📦 Product: Fresh Tomatoes')
                print_with_flush(f'📊 Quantity: 50 KG')
                print_with_flush(f'💰 Total: ₹3,000.00')
                
            else:
                print_with_flush('❌ Customer is inactive')
                return False
        else:
            print_with_flush('❌ Customer not found')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error in order initiation: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 2: Order Processing & Validation (User Action: System validates order)
    print_with_flush('\n📋 Step 2: Order Processing & Validation...')
    try:
        # Check product availability
        product_response = products_table.get_item(
            Key={'productId': 'PROD001', 'category': 'VEGETABLES'}
        )
        
        if 'Item' in product_response:
            product_data = product_response['Item']
            print_with_flush(f'📦 Product: {product_data["name"]}')
            print_with_flush(f'🏷️  Brand: {product_data["brand"]}')
            print_with_flush(f'💰 Unit Price: ₹{product_data["sellingPrice"]}')
            
            # Check stock availability
            stock_response = stock_levels_table.get_item(
                Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'}
            )
            
            if 'Item' in stock_response:
                stock_data = stock_response['Item']
                available_stock = stock_data['availableStock']
                requested_quantity = 50
                
                print_with_flush(f'📊 Available Stock: {available_stock} KG')
                print_with_flush(f'📋 Requested Quantity: {requested_quantity} KG')
                
                if available_stock >= requested_quantity:
                    print_with_flush('✅ Stock validation successful')
                    
                    # Update order status
                    orders_table.update_item(
                        Key={'orderId': order_id, 'customerId': customer_id},
                        UpdateExpression='SET #status = :status, validatedAt = :timestamp',
                        ExpressionAttributeNames={'#status': 'status'},
                        ExpressionAttributeValues={
                            ':status': 'VALIDATED',
                            ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    print_with_flush('✅ Order validated successfully')
                    
                else:
                    print_with_flush('❌ Insufficient stock available')
                    return False
            else:
                print_with_flush('❌ Stock data not found')
                return False
        else:
            print_with_flush('❌ Product not found')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error in order processing: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 3: Pricing & Discounts (User Action: Apply pricing rules)
    print_with_flush('\n💰 Step 3: Pricing & Discounts...')
    try:
        # Apply customer discount (10% for regular customers)
        base_amount = Decimal('3000.00')
        customer_discount = Decimal('0.10')  # 10%
        discount_amount = base_amount * customer_discount
        final_amount = base_amount - discount_amount
        
        # Apply bulk discount (5% for orders > 25 KG)
        bulk_discount = Decimal('0.05')  # 5%
        bulk_discount_amount = final_amount * bulk_discount
        final_amount = final_amount - bulk_discount_amount
        
        # Update order with final pricing
        orders_table.update_item(
            Key={'orderId': order_id, 'customerId': customer_id},
            UpdateExpression='SET finalAmount = :amount, customerDiscount = :cust_disc, bulkDiscount = :bulk_disc, discountAmount = :disc_amount, #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':amount': final_amount,
                ':cust_disc': customer_discount,
                ':bulk_disc': bulk_discount,
                ':disc_amount': discount_amount + bulk_discount_amount,
                ':status': 'PRICED'
            }
        )
        
        print_with_flush(f'💰 Base Amount: ₹{base_amount}')
        print_with_flush(f'🎫 Customer Discount: ₹{discount_amount} (10%)')
        print_with_flush(f'📦 Bulk Discount: ₹{bulk_discount_amount} (5%)')
        print_with_flush(f'💵 Final Amount: ₹{final_amount}')
        print_with_flush('✅ Pricing applied successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Error in pricing: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 4: Stock Reservation (User Action: Reserve inventory)
    print_with_flush('\n📦 Step 4: Stock Reservation...')
    try:
        # Reserve stock for the order
        reserved_quantity = 50
        
        stock_levels_table.update_item(
            Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'},
            UpdateExpression='SET availableStock = availableStock - :qty, reservedStock = reservedStock + :qty, lastUpdated = :timestamp',
            ExpressionAttributeValues={
                ':qty': reserved_quantity,
                ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        )
        
        # Update order status
        orders_table.update_item(
            Key={'orderId': order_id, 'customerId': customer_id},
            UpdateExpression='SET #status = :status, reservedQuantity = :qty, reservedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'RESERVED',
                ':qty': reserved_quantity,
                ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        )
        
        print_with_flush(f'📦 Reserved Quantity: {reserved_quantity} KG')
        print_with_flush('✅ Stock reserved successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Error in stock reservation: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 5: Rider Assignment (User Action: Assign delivery rider)
    print_with_flush('\n🚚 Step 5: Rider Assignment...')
    try:
        # Find available rider
        rider_response = riders_table.scan(
            FilterExpression='#status = :status AND #isAvailable = :available AND #rating >= :min_rating',
            ExpressionAttributeNames={'#status': 'status', '#isAvailable': 'isAvailable', '#rating': 'rating'},
            ExpressionAttributeValues={':status': 'ACTIVE', ':available': True, ':min_rating': Decimal('4.0')}
        )
        
        if rider_response['Items']:
            # Select best rider by rating
            riders = sorted(rider_response['Items'], key=lambda x: x['rating'], reverse=True)
            selected_rider = riders[0]
            
            print_with_flush(f'🚚 Selected Rider: {selected_rider["name"]}')
            print_with_flush(f'⭐ Rating: {selected_rider["rating"]}')
            print_with_flush(f'📞 Phone: {selected_rider["phone"]}')
            print_with_flush(f'🏍️  Vehicle: {selected_rider["vehicleNumber"]}')
            
            # Create delivery record
            delivery_id = f'DEL-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
            delivery_data = {
                'deliveryId': delivery_id,
                'orderId': order_id,
                'riderId': selected_rider['riderId'],
                'status': 'ASSIGNED',
                'pickupLocation': 'COLD_STORAGE_A',
                'deliveryAddress': '123 Main St, Mumbai',
                'estimatedPickupTime': (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat().replace('+00:00', 'Z'),
                'estimatedDeliveryTime': (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat().replace('+00:00', 'Z'),
                'assignedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            deliveries_table.put_item(Item=delivery_data)
            
            # Update rider status
            riders_table.update_item(
                Key={'riderId': selected_rider['riderId'], 'status': selected_rider['status']},
                UpdateExpression='SET isAvailable = :available, lastAssigned = :timestamp',
                ExpressionAttributeValues={
                    ':available': False,
                    ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                }
            )
            
            print_with_flush(f'📦 Delivery Created: {delivery_id}')
            print_with_flush('✅ Rider assigned successfully')
            
        else:
            print_with_flush('❌ No available riders found')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error in rider assignment: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 6: Cash Collection (User Action: Process payment)
    print_with_flush('\n💵 Step 6: Cash Collection...')
    try:
        # Process payment
        collection_id = f'COL-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        collection_data = {
            'collectionId': collection_id,
            'riderId': selected_rider['riderId'],
            'orderId': order_id,
            'amount': final_amount,
            'paymentMethod': 'CASH_ON_DELIVERY',
            'status': 'PENDING',
            'collectionDate': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'riderCommission': final_amount * Decimal('0.05'),  # 5% commission
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        cash_collections_table.put_item(Item=collection_data)
        
        # Update order status
        orders_table.update_item(
            Key={'orderId': order_id, 'customerId': customer_id},
            UpdateExpression='SET #status = :status, paymentStatus = :payment_status, collectionId = :col_id',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'READY_FOR_DELIVERY',
                ':payment_status': 'PENDING',
                ':col_id': collection_id
            }
        )
        
        print_with_flush(f'💵 Collection Created: {collection_id}')
        print_with_flush(f'💰 Amount: ₹{final_amount}')
        print_with_flush(f'💳 Payment Method: Cash on Delivery')
        print_with_flush(f'👤 Rider Commission: ₹{collection_data["riderCommission"]}')
        print_with_flush('✅ Payment processing initiated')
        
    except Exception as e:
        print_with_flush(f'❌ Error in cash collection: {str(e)}')
        traceback.print_exc()
        return False
    
    print_with_flush('\n🎉 Customer Order Journey Completed Successfully!')
    print_with_flush('=' * 60)
    print_with_flush('📋 Journey Summary:')
    print_with_flush(f'   👤 Customer Validation: ✅ {customer_data["name"]} verified')
    print_with_flush(f'   📋 Order Creation: ✅ {order_id} created')
    print_with_flush(f'   📦 Product Validation: ✅ Fresh Tomatoes confirmed')
    print_with_flush(f'   💰 Pricing Applied: ✅ ₹{final_amount} (with discounts)')
    print_with_flush(f'   📦 Stock Reserved: ✅ {reserved_quantity} KG reserved')
    print_with_flush(f'   🚚 Rider Assigned: ✅ {selected_rider["name"]} assigned')
    print_with_flush(f'   💵 Payment Setup: ✅ Cash collection initiated')
    print_with_flush(f'💰 Total Order Value: ₹{final_amount}')
    print_with_flush(f'🚚 Delivery ID: {delivery_id}')
    print_with_flush(f'💵 Collection ID: {collection_id}')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)
    
    return True


def main():
    """Main function to create and execute customer order journey"""
    print_with_flush('🚀 Creating and Executing Customer Order Flow Journey...')
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
    
    # Create customer order journey metadata
    print_with_flush('📋 Creating customer order journey metadata...')
    journey_item, stages, rules = create_customer_order_journey()
    print_with_flush(f'✅ Journey metadata created with {len(stages)} stages and {len(rules)} rules')
    
    print_with_flush('=' * 60)
    
    # Save journey metadata to DynamoDB
    print_with_flush('💾 Saving journey metadata to DynamoDB...')
    if save_journey_to_dynamodb(journey_item, stages, rules):
        print_with_flush('✅ Journey metadata saved successfully to DynamoDB')
    else:
        print_with_flush('❌ Failed to save journey metadata to DynamoDB')
        return False
    
    print_with_flush('=' * 60)
    
    # Execute the realistic customer order journey
    print_with_flush('🔄 Executing Realistic Customer Order Journey...')
    journey_id = journey_item['Data']['journeyId']
    if execute_customer_order_journey(journey_id):
        print_with_flush('✅ Customer order journey executed successfully')
    else:
        print_with_flush('❌ Failed to execute customer order journey')
        return False
    
    print_with_flush('=' * 60)
    print_with_flush('🎉 Complete Customer Order Journey Successfully Created and Executed!')
    print_with_flush('📦 Journey Features:')
    print_with_flush('   • Customer validation and order initiation')
    print_with_flush('   • Product availability and order processing')
    print_with_flush('   • Intelligent pricing and discount application')
    print_with_flush('   • Stock reservation and inventory management')
    print_with_flush('   • Smart rider assignment and delivery planning')
    print_with_flush('   • Payment processing and cash collection')
    print_with_flush('🤖 AI-Assisted: Yes')
    print_with_flush('📊 Total Stages: 6')
    print_with_flush('📋 Total Rules: 6')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('💾 Multi-Table Design: Yes')
    print_with_flush('=' * 60)
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Journey creation interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1) 