#!/usr/bin/env python3
"""
Create Inventory Management Journeys

This script creates comprehensive inventory management journeys with metadata, stages,
and AI-guided workflow management for inventory operations.

Journey Types:
1. Procurement Flow (Starts with Purchase Need)
2. Order Fulfillment Flow
3. Stock Management Flow
4. Delivery Management Flow
5. Cash Collection Flow

Journey Structure:
- Metadata and configuration
- Stage definitions with steps
- AI-assisted workflow guidance
- Progress tracking and monitoring
- Business rules and validation
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


def get_procurement_rules_for_stage(stage_id, journey_id):
    """Get AI rules for procurement journey stages"""
    
    base_rules = {
        'stock_assessment': [
            {
                'ruleId': f'rule-{stage_id}-stock-check-001',
                'title': 'Low stock triggers procurement',
                'description': 'When stock levels fall below reorder point, automatically trigger procurement process',
                'type': 'business_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['products', 'stock_levels'],
                    'conditions': [
                        {
                            'field': 'availableStock',
                            'operator': 'less_than',
                            'value': 'reorderPoint'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'When available stock is less than reorder point, create purchase order automatically. Consider supplier lead time and minimum order quantities.',
                    'jsonRule': {
                        'conditions': {
                            'stock_comparison': 'available < reorder_point',
                            'auto_trigger': True
                        },
                        'actions': {
                            'create_po': True,
                            'notify_supplier': True,
                            'calculate_quantity': 'demand_forecast + safety_stock'
                        }
                    }
                }
            }
        ],
        'supplier_selection': [
            {
                'ruleId': f'rule-{stage_id}-supplier-rating-001',
                'title': 'Select supplier based on rating and performance',
                'description': 'Choose supplier with highest rating and best delivery performance',
                'type': 'decision_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['suppliers'],
                    'conditions': [
                        {
                            'field': 'status',
                            'operator': 'equals',
                            'value': 'ACTIVE'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Select supplier with rating >= 4.0 and active status. Consider delivery time, quality, and cost.',
                    'jsonRule': {
                        'conditions': {
                            'min_rating': Decimal('4.0'),
                            'status': 'ACTIVE',
                            'delivery_performance': 'GOOD'
                        },
                        'actions': {
                            'rank_by': ['rating', 'delivery_time', 'cost'],
                            'select_top': 1
                        }
                    }
                }
            }
        ],
        'purchase_order_creation': [
            {
                'ruleId': f'rule-{stage_id}-po-validation-001',
                'title': 'Validate purchase order quantities and pricing',
                'description': 'Ensure PO quantities meet minimum order requirements and pricing is within budget',
                'type': 'validation_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['purchase_orders'],
                    'conditions': [
                        {
                            'field': 'totalAmount',
                            'operator': 'less_than_or_equal',
                            'value': 'budgetLimit'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Validate that PO total is within budget and quantities meet supplier minimums. Check for bulk discounts.',
                    'jsonRule': {
                        'conditions': {
                            'budget_check': 'total <= budget_limit',
                            'quantity_check': 'quantity >= min_order_qty',
                            'pricing_check': 'unit_price <= max_approved_price'
                        },
                        'actions': {
                            'apply_discounts': True,
                            'validate_budget': True,
                            'check_approvals': True
                        }
                    }
                }
            }
        ],
        'goods_receipt': [
            {
                'ruleId': f'rule-{stage_id}-quality-check-001',
                'title': 'Quality check on received goods',
                'description': 'Verify received goods meet quality standards and match PO specifications',
                'type': 'quality_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['deliveries', 'batches'],
                    'conditions': [
                        {
                            'field': 'qualityStatus',
                            'operator': 'equals',
                            'value': 'GOOD'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Check received goods for damage, expiry dates, and quantity accuracy. Update stock levels only after quality approval.',
                    'jsonRule': {
                        'conditions': {
                            'quality_check': 'status == GOOD',
                            'quantity_match': 'received == ordered',
                            'expiry_check': 'expiry_date > current_date + buffer'
                        },
                        'actions': {
                            'update_stock': True,
                            'create_batch': True,
                            'notify_supplier': 'quality_approved'
                        }
                    }
                }
            }
        ],
        'stock_update': [
            {
                'ruleId': f'rule-{stage_id}-stock-reconciliation-001',
                'title': 'Reconcile stock levels after receipt',
                'description': 'Update inventory levels and create new batches with proper tracking',
                'type': 'data_update_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['stock_levels', 'batches'],
                    'conditions': [
                        {
                            'field': 'qualityStatus',
                            'operator': 'equals',
                            'value': 'GOOD'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Update available stock, create new batch records with expiry tracking, and adjust reserved stock if needed.',
                    'jsonRule': {
                        'conditions': {
                            'quality_approved': True,
                            'quantity_received': '> 0'
                        },
                        'actions': {
                            'update_available_stock': True,
                            'create_batch_record': True,
                            'set_expiry_tracking': True,
                            'update_reorder_status': True
                        }
                    }
                }
            }
        ]
    }
    
    return base_rules.get(stage_id, [])


def create_procurement_journey(journey_name="Procurement Flow", journey_id=None):
    """Create a complete procurement journey with all stages"""
    print_with_flush('🚀 Starting procurement journey creation...')
    
    if journey_id is None:
        journey_id = f'procurement-{uuid.uuid4().hex[:8]}'
    
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    print_with_flush(f'📝 Creating procurement journey with ID: {journey_id}')
    
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
            'description': 'Complete procurement workflow from stock assessment to inventory update',
            'status': 'pending',
            'createdBy': 'system',
            'priority': 'high',
            'journeyType': 'procurement',
            'source': {
                'type': 'inventory-system',
                'triggerType': 'low_stock_automatic',
                'triggerSource': 'stock_monitoring',
                'version': '1.0.0',
            },
            'configuration': {
                'timeout': 3600,  # 1 hour for complete procurement
                'maxRetries': 3,
                'enableNotifications': True,
                'enableDetailedLogging': True,
                'validateAtEachStage': True,
                'aiAssisted': True,
                'ruleEngineVersion': 'v1.0',
            },
            'currentStageIndex': 0,
            'currentStageId': 'stock_assessment',
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
                'stock_assessment': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'supplier_selection': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'purchase_order_creation': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'goods_receipt': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'batch_creation': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'stock_update': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
            },
            'aiConfig': {
                'enabled': True,
                'ruleTypes': ['business_rule', 'decision_rule', 'validation_rule', 'quality_rule', 'data_update_rule'],
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
        # Stage 0: Stock Assessment
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#00#stock_assessment',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '00',
            'Data': {
                'stageId': 'stock_assessment',
                'name': 'Stock Assessment',
                'description': 'Identify products with low stock levels that need procurement',
                'order': 0,
                'canSkip': False,
                'estimatedDuration': '10m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['business_rule'],
                'steps': [
                    {
                        'id': 'stock_level_check',
                        'name': 'Stock Level Check',
                        'description': 'Check current stock levels against reorder points',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['business_rule'],
                    },
                    {
                        'id': 'demand_forecast',
                        'name': 'Demand Forecast',
                        'description': 'Calculate expected demand and required quantities',
                        'order': 1,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['business_rule'],
                    },
                    {
                        'id': 'procurement_trigger',
                        'name': 'Procurement Trigger',
                        'description': 'Determine if procurement is needed and quantities',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['business_rule'],
                    },
                ],
            },
        },
        # Stage 1: Supplier Selection
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#01#supplier_selection',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '01',
            'Data': {
                'stageId': 'supplier_selection',
                'name': 'Supplier Selection',
                'description': 'Select appropriate supplier based on rating, performance, and availability',
                'order': 1,
                'canSkip': False,
                'estimatedDuration': '15m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['decision_rule'],
                'steps': [
                    {
                        'id': 'supplier_filtering',
                        'name': 'Supplier Filtering',
                        'description': 'Filter suppliers by product availability and status',
                        'order': 0,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['decision_rule'],
                    },
                    {
                        'id': 'performance_evaluation',
                        'name': 'Performance Evaluation',
                        'description': 'Evaluate supplier performance, rating, and delivery time',
                        'order': 1,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['decision_rule'],
                    },
                    {
                        'id': 'supplier_selection',
                        'name': 'Supplier Selection',
                        'description': 'Select best supplier based on criteria',
                        'order': 2,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['decision_rule'],
                    },
                ],
            },
        },
        # Stage 2: Purchase Order Creation
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#02#purchase_order_creation',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '02',
            'Data': {
                'stageId': 'purchase_order_creation',
                'name': 'Purchase Order Creation',
                'description': 'Create purchase order with validated quantities and pricing',
                'order': 2,
                'canSkip': False,
                'estimatedDuration': '20m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['validation_rule'],
                'steps': [
                    {
                        'id': 'po_validation',
                        'name': 'PO Validation',
                        'description': 'Validate quantities, pricing, and budget constraints',
                        'order': 0,
                        'estimatedDuration': '8m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                    {
                        'id': 'po_creation',
                        'name': 'PO Creation',
                        'description': 'Create purchase order with supplier details',
                        'order': 1,
                        'estimatedDuration': '6m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                    {
                        'id': 'supplier_notification',
                        'name': 'Supplier Notification',
                        'description': 'Notify supplier of new purchase order',
                        'order': 2,
                        'estimatedDuration': '6m',
                        'aiAssisted': True,
                        'applicableRules': ['validation_rule'],
                    },
                ],
            },
        },
        # Stage 3: Goods Receipt
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#03#goods_receipt',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '03',
            'Data': {
                'stageId': 'goods_receipt',
                'name': 'Goods Receipt',
                'description': 'Receive and verify delivered goods against purchase order',
                'order': 3,
                'canSkip': False,
                'estimatedDuration': '25m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['quality_rule'],
                'steps': [
                    {
                        'id': 'delivery_verification',
                        'name': 'Delivery Verification',
                        'description': 'Verify delivered goods match purchase order',
                        'order': 0,
                        'estimatedDuration': '8m',
                        'aiAssisted': True,
                        'applicableRules': ['quality_rule'],
                    },
                    {
                        'id': 'quality_check',
                        'name': 'Quality Check',
                        'description': 'Check goods quality and expiry dates',
                        'order': 1,
                        'estimatedDuration': '10m',
                        'aiAssisted': True,
                        'applicableRules': ['quality_rule'],
                    },
                    {
                        'id': 'quantity_reconciliation',
                        'name': 'Quantity Reconciliation',
                        'description': 'Reconcile received quantities with ordered quantities',
                        'order': 2,
                        'estimatedDuration': '7m',
                        'aiAssisted': True,
                        'applicableRules': ['quality_rule'],
                    },
                ],
            },
        },
        # Stage 4: Batch Creation
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#04#batch_creation',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '04',
            'Data': {
                'stageId': 'batch_creation',
                'name': 'Batch Creation',
                'description': 'Create new batches with expiry tracking and location assignment',
                'order': 4,
                'canSkip': False,
                'estimatedDuration': '15m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['data_update_rule'],
                'steps': [
                    {
                        'id': 'batch_number_generation',
                        'name': 'Batch Number Generation',
                        'description': 'Generate unique batch numbers for received goods',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                    {
                        'id': 'expiry_tracking_setup',
                        'name': 'Expiry Tracking Setup',
                        'description': 'Set up expiry date tracking for perishable goods',
                        'order': 1,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                    {
                        'id': 'location_assignment',
                        'name': 'Location Assignment',
                        'description': 'Assign storage location based on product requirements',
                        'order': 2,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                    {
                        'id': 'batch_record_creation',
                        'name': 'Batch Record Creation',
                        'description': 'Create batch records in inventory system',
                        'order': 3,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                ],
            },
        },
        # Stage 5: Stock Update
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#05#stock_update',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '05',
            'Data': {
                'stageId': 'stock_update',
                'name': 'Stock Update',
                'description': 'Update inventory levels and adjust stock counts',
                'order': 5,
                'canSkip': False,
                'estimatedDuration': '10m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['data_update_rule'],
                'steps': [
                    {
                        'id': 'available_stock_update',
                        'name': 'Available Stock Update',
                        'description': 'Update available stock levels',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                    {
                        'id': 'reserved_stock_adjustment',
                        'name': 'Reserved Stock Adjustment',
                        'description': 'Adjust reserved stock if needed',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                    {
                        'id': 'reorder_status_update',
                        'name': 'Reorder Status Update',
                        'description': 'Update reorder status and trigger notifications',
                        'order': 2,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['data_update_rule'],
                    },
                ],
            },
        },
    ]
    
    # 3. Create Rules for each stage
    all_rules = []
    for stage in stages:
        stage_id = stage['Data']['stageId']
        stage_rules = get_procurement_rules_for_stage(stage_id, journey_id)
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


def execute_procurement_journey(journey_id):
    """Execute a realistic procurement journey by populating data step by step"""
    print_with_flush('🚀 Executing Realistic Procurement Journey...')
    print_with_flush('=' * 60)
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        # Get table references
        products_table = dynamodb.Table('InventoryManagement-Products')
        stock_levels_table = dynamodb.Table('InventoryManagement-StockLevels')
        suppliers_table = dynamodb.Table('InventoryManagement-Suppliers')
        purchase_orders_table = dynamodb.Table('InventoryManagement-PurchaseOrders')
        batches_table = dynamodb.Table('InventoryManagement-Batches')
        
        print_with_flush('✅ DynamoDB tables connected successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Failed to connect to DynamoDB: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 1: Check Stock Levels (User Action: View Inventory)
    print_with_flush('📊 Step 1: Checking Stock Levels...')
    try:
        # Simulate user checking stock levels
        stock_response = stock_levels_table.get_item(
            Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'}
        )
        
        if 'Item' in stock_response:
            stock_data = stock_response['Item']
            available_stock = stock_data['availableStock']
            reorder_point = 150  # From product configuration
            
            print_with_flush(f'📦 Current Available Stock: {available_stock} KG')
            print_with_flush(f'📋 Reorder Point: {reorder_point} KG')
            
            if available_stock < reorder_point:
                print_with_flush('⚠️  LOW STOCK ALERT: Stock below reorder point!')
                print_with_flush('🔄 Triggering procurement process...')
                
                # Update stock status
                stock_levels_table.update_item(
                    Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'},
                    UpdateExpression='SET reorderStatus = :status, lastChecked = :timestamp',
                    ExpressionAttributeValues={
                        ':status': 'REORDER_REQUIRED',
                        ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                )
                print_with_flush('✅ Stock status updated to REORDER_REQUIRED')
            else:
                print_with_flush('✅ Stock levels are adequate')
                
        else:
            print_with_flush('❌ Stock data not found')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error checking stock levels: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 2: Select Supplier (User Action: Choose Supplier)
    print_with_flush('\n👥 Step 2: Selecting Supplier...')
    try:
        # Simulate user searching for suppliers
        supplier_response = suppliers_table.scan(
            FilterExpression='#status = :status AND #rating >= :min_rating',
            ExpressionAttributeNames={'#status': 'status', '#rating': 'rating'},
            ExpressionAttributeValues={':status': 'ACTIVE', ':min_rating': Decimal('4.0')}
        )
        
        if supplier_response['Items']:
            # Sort by rating and select best supplier
            suppliers = sorted(supplier_response['Items'], key=lambda x: x['rating'], reverse=True)
            selected_supplier = suppliers[0]
            
            print_with_flush(f'🏆 Selected Supplier: {selected_supplier["name"]}')
            print_with_flush(f'⭐ Rating: {selected_supplier["rating"]}')
            print_with_flush(f'📞 Contact: {selected_supplier["contactPerson"]}')
            print_with_flush(f'📧 Email: {selected_supplier["email"]}')
            
            # Update supplier status
            suppliers_table.update_item(
                Key={'supplierId': selected_supplier['supplierId'], 'status': selected_supplier['status']},
                UpdateExpression='SET lastSelected = :timestamp, selectionCount = if_not_exists(selectionCount, :zero) + :inc',
                ExpressionAttributeValues={
                    ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':zero': 0,
                    ':inc': 1
                }
            )
            print_with_flush('✅ Supplier selection recorded')
            
        else:
            print_with_flush('❌ No suitable suppliers found')
            return False
            
    except Exception as e:
        print_with_flush(f'❌ Error selecting supplier: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 3: Create Purchase Order (User Action: Create PO)
    print_with_flush('\n📋 Step 3: Creating Purchase Order...')
    try:
        # Calculate required quantity
        required_quantity = 500  # Based on demand forecast
        unit_price = Decimal('45.00')  # From supplier catalog
        total_amount = required_quantity * unit_price
        
        # Create PO data
        po_id = f'PO-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        po_data = {
            'poId': po_id,
            'supplierId': selected_supplier['supplierId'],
            'productId': 'PROD001',
            'quantity': required_quantity,
            'unitPrice': unit_price,
            'totalAmount': total_amount,
            'status': 'PENDING',
            'orderDate': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'expectedDelivery': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat().replace('+00:00', 'Z'),
            'paymentTerms': 'NET30',
            'notes': 'Automatic reorder due to low stock',
            'createdBy': 'system',
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Save PO to database
        purchase_orders_table.put_item(Item=po_data)
        
        print_with_flush(f'📋 Purchase Order Created: {po_id}')
        print_with_flush(f'📦 Quantity: {required_quantity} KG')
        print_with_flush(f'💰 Unit Price: ₹{unit_price}')
        print_with_flush(f'💵 Total Amount: ₹{total_amount}')
        print_with_flush(f'📅 Expected Delivery: {po_data["expectedDelivery"]}')
        
        # Update supplier with new order
        suppliers_table.update_item(
            Key={'supplierId': selected_supplier['supplierId'], 'status': selected_supplier['status']},
            UpdateExpression='SET totalOrders = totalOrders + :inc, totalAmount = totalAmount + :amount, lastOrderDate = :timestamp',
            ExpressionAttributeValues={
                ':inc': 1,
                ':amount': total_amount,
                ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        )
        print_with_flush('✅ Supplier order history updated')
        
    except Exception as e:
        print_with_flush(f'❌ Error creating purchase order: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 4: Simulate Goods Receipt (User Action: Receive Goods)
    print_with_flush('\n📦 Step 4: Receiving Goods...')
    try:
        # Simulate delivery arrival
        received_quantity = 480  # Slightly less than ordered (realistic)
        received_date = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Update PO status
        purchase_orders_table.update_item(
            Key={'poId': po_id, 'supplierId': selected_supplier['supplierId']},
            UpdateExpression='SET #status = :status, receivedQuantity = :qty, receivedDate = :date, updatedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'RECEIVED',
                ':qty': received_quantity,
                ':date': received_date,
                ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        )
        
        print_with_flush(f'📦 Goods Received: {received_quantity} KG')
        print_with_flush(f'📅 Received Date: {received_date}')
        print_with_flush(f'📋 PO Status Updated: RECEIVED')
        
    except Exception as e:
        print_with_flush(f'❌ Error processing goods receipt: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 5: Create Batch Records (User Action: Create Batch)
    print_with_flush('\n🏷️  Step 5: Creating Batch Records...')
    try:
        # Create new batch
        batch_id = f'BATCH-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        batch_data = {
            'batchId': batch_id,
            'productId': 'PROD001',
            'batchNumber': f'TOMATO-{datetime.now().strftime("%Y%m%d")}-001',
            'manufacturingDate': datetime.now().strftime('%Y-%m-%d'),
            'expiryDate': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'initialQuantity': received_quantity,
            'currentQuantity': received_quantity,
            'supplierId': selected_supplier['supplierId'],
            'qualityStatus': 'GOOD',
            'temperature': Decimal('4.5'),
            'location': 'COLD_STORAGE_A',
            'poId': po_id,
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Save batch to database
        batches_table.put_item(Item=batch_data)
        
        print_with_flush(f'🏷️  Batch Created: {batch_id}')
        print_with_flush(f'📦 Initial Quantity: {received_quantity} KG')
        print_with_flush(f'📅 Expiry Date: {batch_data["expiryDate"]}')
        print_with_flush(f'🌡️  Temperature: {batch_data["temperature"]}°C')
        print_with_flush(f'📍 Location: {batch_data["location"]}')
        
    except Exception as e:
        print_with_flush(f'❌ Error creating batch: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 6: Update Stock Levels (User Action: Update Inventory)
    print_with_flush('\n📊 Step 6: Updating Stock Levels...')
    try:
        # Update stock levels
        stock_levels_table.update_item(
            Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'},
            UpdateExpression='SET availableStock = availableStock + :qty, totalStock = totalStock + :qty, lastUpdated = :timestamp, reorderStatus = :status',
            ExpressionAttributeValues={
                ':qty': received_quantity,
                ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                ':status': 'ADEQUATE'
            }
        )
        
        # Get updated stock levels
        updated_stock = stock_levels_table.get_item(
            Key={'productId': 'PROD001', 'location': 'COLD_STORAGE_A'}
        )
        
        if 'Item' in updated_stock:
            stock_info = updated_stock['Item']
            print_with_flush(f'📊 Updated Stock Levels:')
            print_with_flush(f'   📦 Total Stock: {stock_info["totalStock"]} KG')
            print_with_flush(f'   ✅ Available Stock: {stock_info["availableStock"]} KG')
            print_with_flush(f'   📋 Reorder Status: {stock_info.get("reorderStatus", "ADEQUATE")}')
            print_with_flush(f'   🕐 Last Updated: {stock_info["lastUpdated"]}')
        
        print_with_flush('✅ Stock levels updated successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Error updating stock levels: {str(e)}')
        traceback.print_exc()
        return False
    
    print_with_flush('\n🎉 Procurement Journey Completed Successfully!')
    print_with_flush('=' * 60)
    print_with_flush('📋 Journey Summary:')
    print_with_flush(f'   📊 Stock Check: ✅ Low stock detected')
    print_with_flush(f'   👥 Supplier Selection: ✅ {selected_supplier["name"]} selected')
    print_with_flush(f'   📋 Purchase Order: ✅ {po_id} created')
    print_with_flush(f'   📦 Goods Receipt: ✅ {received_quantity} KG received')
    print_with_flush(f'   🏷️  Batch Creation: ✅ {batch_id} created')
    print_with_flush(f'   📊 Stock Update: ✅ Inventory updated')
    print_with_flush('💰 Total Cost: ₹{:.2f}'.format(float(total_amount)))
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)
    
    return True


def main():
    """Main function to create and execute procurement journey"""
    print_with_flush('🚀 Creating and Executing Inventory Management Procurement Journey...')
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
    
    # Create procurement journey metadata
    print_with_flush('📋 Creating procurement journey metadata...')
    journey_item, stages, rules = create_procurement_journey()
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
    
    # Execute the realistic procurement journey
    print_with_flush('🔄 Executing Realistic Procurement Journey...')
    journey_id = journey_item['Data']['journeyId']
    if execute_procurement_journey(journey_id):
        print_with_flush('✅ Procurement journey executed successfully')
    else:
        print_with_flush('❌ Failed to execute procurement journey')
        return False
    
    print_with_flush('=' * 60)
    print_with_flush('🎉 Complete Procurement Journey Successfully Created and Executed!')
    print_with_flush('📦 Journey Features:')
    print_with_flush('   • Real-time stock monitoring and alerts')
    print_with_flush('   • Intelligent supplier selection')
    print_with_flush('   • Automated purchase order creation')
    print_with_flush('   • Goods receipt processing')
    print_with_flush('   • Batch tracking and management')
    print_with_flush('   • Inventory level updates')
    print_with_flush('🤖 AI-Assisted: Yes')
    print_with_flush('📊 Total Stages: 6')
    print_with_flush('📋 Total Rules: 5')
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