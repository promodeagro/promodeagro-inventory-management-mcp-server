#!/usr/bin/env python3
"""
Create Pricing & Promotion Flow Journey

This script creates and executes a comprehensive pricing and promotion journey that simulates
dynamic pricing strategy changes and their impact on the inventory system.

Pricing & Promotion Flow:
1. Strategy Change Initiation
2. Product Category Analysis
3. Pricing Rules Application
4. Discount Strategy Implementation
5. Order Pricing Updates
6. Market Impact Assessment
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


def get_pricing_promotion_rules_for_stage(stage_id, journey_id):
    """Get AI rules for pricing and promotion journey stages"""
    
    base_rules = {
        'strategy_initiation': [
            {
                'ruleId': f'rule-{stage_id}-strategy-validation-001',
                'title': 'Validate pricing strategy changes',
                'description': 'Verify strategy changes are within acceptable business parameters',
                'type': 'strategy_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['products', 'pricing_strategies'],
                    'conditions': [
                        {
                            'field': 'marginThreshold',
                            'operator': 'greater_than',
                            'value': 'minimumMargin'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Ensure pricing changes maintain minimum profit margins and comply with business rules.',
                    'jsonRule': {
                        'conditions': {
                            'min_margin': '>= 15%',
                            'max_increase': '<= 25%',
                            'competitive_analysis': 'required'
                        },
                        'actions': {
                            'validate_strategy': True,
                            'check_margins': True,
                            'approve_changes': True
                        }
                    }
                }
            }
        ],
        'product_analysis': [
            {
                'ruleId': f'rule-{stage_id}-category-impact-001',
                'title': 'Analyze product category impact',
                'description': 'Identify products affected by pricing strategy changes',
                'type': 'analysis_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['products', 'categories'],
                    'conditions': [
                        {
                            'field': 'category',
                            'operator': 'in',
                            'value': ['VEGETABLES', 'FRUITS', 'DAIRY']
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Analyze which product categories will be impacted by the pricing strategy change.',
                    'jsonRule': {
                        'conditions': {
                            'affected_categories': ['VEGETABLES', 'FRUITS', 'DAIRY'],
                            'volume_analysis': 'required',
                            'profit_impact': 'calculated'
                        },
                        'actions': {
                            'identify_products': True,
                            'calculate_impact': True,
                            'prioritize_changes': True
                        }
                    }
                }
            }
        ],
        'pricing_rules': [
            {
                'ruleId': f'rule-{stage_id}-dynamic-pricing-001',
                'title': 'Apply dynamic pricing rules',
                'description': 'Implement cost-based and demand-based pricing strategies',
                'type': 'pricing_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['products', 'pricing_rules'],
                    'conditions': [
                        {
                            'field': 'pricingType',
                            'operator': 'in',
                            'value': ['COST_BASED', 'DEMAND_BASED', 'COMPETITIVE']
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Apply dynamic pricing based on cost fluctuations, demand patterns, and competitive analysis.',
                    'jsonRule': {
                        'conditions': {
                            'cost_increase': '> 5%',
                            'demand_high': True,
                            'competitive_advantage': 'maintained'
                        },
                        'actions': {
                            'adjust_cost_price': True,
                            'update_selling_price': True,
                            'maintain_margins': True
                        }
                    }
                }
            }
        ],
        'discount_strategy': [
            {
                'ruleId': f'rule-{stage_id}-discount-application-001',
                'title': 'Apply strategic discount strategies',
                'description': 'Implement time-based, customer-specific, and quantity-based discounts',
                'type': 'discount_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['products', 'customers', 'discounts'],
                    'conditions': [
                        {
                            'field': 'discountType',
                            'operator': 'in',
                            'value': ['TIME_BASED', 'CUSTOMER_SPECIFIC', 'QUANTITY_BASED']
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Apply strategic discounts to boost sales, clear inventory, and reward loyal customers.',
                    'jsonRule': {
                        'conditions': {
                            'seasonal_promotion': True,
                            'customer_tier': 'REGULAR|PREMIUM|VIP',
                            'quantity_threshold': 'met'
                        },
                        'actions': {
                            'apply_time_discount': True,
                            'apply_customer_discount': True,
                            'apply_quantity_discount': True
                        }
                    }
                }
            }
        ],
        'order_updates': [
            {
                'ruleId': f'rule-{stage_id}-order-pricing-001',
                'title': 'Update order pricing with new rates',
                'description': 'Apply new pricing to existing and future orders',
                'type': 'order_rule',
                'priority': 'critical',
                'scope': 'global',
                'context': {
                    'appliesTo': ['orders', 'products'],
                    'conditions': [
                        {
                            'field': 'orderStatus',
                            'operator': 'in',
                            'value': ['PENDING', 'VALIDATED']
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Update pricing for pending orders and ensure new orders reflect current pricing strategy.',
                    'jsonRule': {
                        'conditions': {
                            'order_not_shipped': True,
                            'pricing_effective_date': 'reached',
                            'customer_notified': True
                        },
                        'actions': {
                            'recalculate_order_total': True,
                            'notify_customer': True,
                            'update_payment_amount': True
                        }
                    }
                }
            }
        ],
        'market_assessment': [
            {
                'ruleId': f'rule-{stage_id}-market-impact-001',
                'title': 'Assess market impact of pricing changes',
                'description': 'Analyze customer response and competitive positioning',
                'type': 'assessment_rule',
                'priority': 'high',
                'scope': 'global',
                'context': {
                    'appliesTo': ['orders', 'customers', 'market_data'],
                    'conditions': [
                        {
                            'field': 'assessmentPeriod',
                            'operator': 'greater_than',
                            'value': '7days'
                        }
                    ]
                },
                'content': {
                    'naturalLanguage': 'Monitor customer response, order volume changes, and competitive positioning after pricing updates.',
                    'jsonRule': {
                        'conditions': {
                            'monitoring_period': '7_days',
                            'key_metrics_tracked': True,
                            'feedback_collected': True
                        },
                        'actions': {
                            'track_order_volume': True,
                            'monitor_customer_feedback': True,
                            'analyze_competitive_position': True,
                            'adjust_strategy_if_needed': True
                        }
                    }
                }
            }
        ]
    }
    
    return base_rules.get(stage_id, [])


def create_pricing_promotion_journey(journey_name="Pricing & Promotion Flow", journey_id=None):
    """Create a complete pricing and promotion journey with all stages"""
    print_with_flush('🚀 Starting pricing and promotion journey creation...')
    
    if journey_id is None:
        journey_id = f'pricing-promotion-{uuid.uuid4().hex[:8]}'
    
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    print_with_flush(f'📝 Creating pricing and promotion journey with ID: {journey_id}')
    
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
            'description': 'Complete pricing and promotion strategy workflow from strategy change to market impact',
            'status': 'pending',
            'createdBy': 'system',
            'priority': 'high',
            'journeyType': 'pricing_promotion',
            'source': {
                'type': 'strategy-change',
                'triggerType': 'marketing_decision',
                'triggerSource': 'marketing_team',
                'version': '1.0.0',
            },
            'configuration': {
                'timeout': 2400,  # 40 minutes for complete strategy
                'maxRetries': 3,
                'enableNotifications': True,
                'enableDetailedLogging': True,
                'validateAtEachStage': True,
                'aiAssisted': True,
                'ruleEngineVersion': 'v1.0',
            },
            'currentStageIndex': 0,
            'currentStageId': 'strategy_initiation',
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
                'strategy_initiation': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'product_analysis': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'pricing_rules': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'discount_strategy': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'order_updates': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
                'market_assessment': {'totalExecutions': 0, 'lastStatus': 'pending', 'rulesCount': 0},
            },
            'aiConfig': {
                'enabled': True,
                'ruleTypes': ['strategy_rule', 'analysis_rule', 'pricing_rule', 'discount_rule', 'order_rule', 'assessment_rule'],
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
        # Stage 0: Strategy Initiation
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#00#strategy_initiation',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '00',
            'Data': {
                'stageId': 'strategy_initiation',
                'name': 'Strategy Initiation',
                'description': 'Initiate pricing strategy change based on market conditions',
                'order': 0,
                'canSkip': False,
                'estimatedDuration': '8m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['strategy_rule'],
                'steps': [
                    {
                        'id': 'market_analysis',
                        'name': 'Market Analysis',
                        'description': 'Analyze current market conditions and competitive landscape',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['strategy_rule'],
                    },
                    {
                        'id': 'strategy_validation',
                        'name': 'Strategy Validation',
                        'description': 'Validate proposed pricing strategy against business rules',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['strategy_rule'],
                    },
                    {
                        'id': 'strategy_approval',
                        'name': 'Strategy Approval',
                        'description': 'Approve and activate new pricing strategy',
                        'order': 2,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['strategy_rule'],
                    },
                ],
            },
        },
        # Stage 1: Product Analysis
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#01#product_analysis',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '01',
            'Data': {
                'stageId': 'product_analysis',
                'name': 'Product Analysis',
                'description': 'Identify products affected by pricing strategy changes',
                'order': 1,
                'canSkip': False,
                'estimatedDuration': '10m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['analysis_rule'],
                'steps': [
                    {
                        'id': 'category_identification',
                        'name': 'Category Identification',
                        'description': 'Identify product categories impacted by strategy',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['analysis_rule'],
                    },
                    {
                        'id': 'product_impact_analysis',
                        'name': 'Product Impact Analysis',
                        'description': 'Analyze individual product impact and profitability',
                        'order': 1,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['analysis_rule'],
                    },
                    {
                        'id': 'priority_ranking',
                        'name': 'Priority Ranking',
                        'description': 'Rank products by impact and implementation priority',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['analysis_rule'],
                    },
                ],
            },
        },
        # Stage 2: Pricing Rules
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#02#pricing_rules',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '02',
            'Data': {
                'stageId': 'pricing_rules',
                'name': 'Pricing Rules',
                'description': 'Apply dynamic pricing rules based on cost and demand',
                'order': 2,
                'canSkip': False,
                'estimatedDuration': '12m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['pricing_rule'],
                'steps': [
                    {
                        'id': 'cost_analysis',
                        'name': 'Cost Analysis',
                        'description': 'Analyze cost fluctuations and supplier pricing',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'demand_analysis',
                        'name': 'Demand Analysis',
                        'description': 'Analyze demand patterns and seasonal trends',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'price_calculation',
                        'name': 'Price Calculation',
                        'description': 'Calculate new prices based on cost and demand',
                        'order': 2,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                    {
                        'id': 'margin_validation',
                        'name': 'Margin Validation',
                        'description': 'Validate profit margins meet business requirements',
                        'order': 3,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['pricing_rule'],
                    },
                ],
            },
        },
        # Stage 3: Discount Strategy
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#03#discount_strategy',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '03',
            'Data': {
                'stageId': 'discount_strategy',
                'name': 'Discount Strategy',
                'description': 'Implement strategic discounts and promotions',
                'order': 3,
                'canSkip': False,
                'estimatedDuration': '15m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['discount_rule'],
                'steps': [
                    {
                        'id': 'time_based_discounts',
                        'name': 'Time-Based Discounts',
                        'description': 'Apply seasonal and promotional time-based discounts',
                        'order': 0,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['discount_rule'],
                    },
                    {
                        'id': 'customer_discounts',
                        'name': 'Customer Discounts',
                        'description': 'Apply customer-specific loyalty and tier discounts',
                        'order': 1,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['discount_rule'],
                    },
                    {
                        'id': 'quantity_discounts',
                        'name': 'Quantity Discounts',
                        'description': 'Apply bulk and quantity-based discount tiers',
                        'order': 2,
                        'estimatedDuration': '4m',
                        'aiAssisted': True,
                        'applicableRules': ['discount_rule'],
                    },
                    {
                        'id': 'promotion_activation',
                        'name': 'Promotion Activation',
                        'description': 'Activate promotional campaigns and discounts',
                        'order': 3,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['discount_rule'],
                    },
                ],
            },
        },
        # Stage 4: Order Updates
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#04#order_updates',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '04',
            'Data': {
                'stageId': 'order_updates',
                'name': 'Order Updates',
                'description': 'Update existing orders and ensure new orders reflect new pricing',
                'order': 4,
                'canSkip': False,
                'estimatedDuration': '10m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['order_rule'],
                'steps': [
                    {
                        'id': 'pending_order_analysis',
                        'name': 'Pending Order Analysis',
                        'description': 'Identify orders that need pricing updates',
                        'order': 0,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['order_rule'],
                    },
                    {
                        'id': 'price_recalculation',
                        'name': 'Price Recalculation',
                        'description': 'Recalculate order totals with new pricing',
                        'order': 1,
                        'estimatedDuration': '3m',
                        'aiAssisted': True,
                        'applicableRules': ['order_rule'],
                    },
                    {
                        'id': 'customer_notification',
                        'name': 'Customer Notification',
                        'description': 'Notify customers of pricing changes',
                        'order': 2,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['order_rule'],
                    },
                    {
                        'id': 'order_confirmation',
                        'name': 'Order Confirmation',
                        'description': 'Confirm updated orders with customers',
                        'order': 3,
                        'estimatedDuration': '2m',
                        'aiAssisted': True,
                        'applicableRules': ['order_rule'],
                    },
                ],
            },
        },
        # Stage 5: Market Assessment
        {
            'PK': f'JOURNEY#{journey_id}',
            'SK': 'STAGE#05#market_assessment',
            'EntityType': 'StageDefinition',
            'GSI1PK': f'JOURNEY#{journey_id}#STAGES',
            'GSI1SK': '05',
            'Data': {
                'stageId': 'market_assessment',
                'name': 'Market Assessment',
                'description': 'Assess market impact and customer response to pricing changes',
                'order': 5,
                'canSkip': False,
                'estimatedDuration': '20m',
                'status': 'pending',
                'aiAssisted': True,
                'ruleTypes': ['assessment_rule'],
                'steps': [
                    {
                        'id': 'order_volume_tracking',
                        'name': 'Order Volume Tracking',
                        'description': 'Monitor changes in order volume and patterns',
                        'order': 0,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['assessment_rule'],
                    },
                    {
                        'id': 'customer_feedback_analysis',
                        'name': 'Customer Feedback Analysis',
                        'description': 'Analyze customer feedback and satisfaction levels',
                        'order': 1,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['assessment_rule'],
                    },
                    {
                        'id': 'competitive_analysis',
                        'name': 'Competitive Analysis',
                        'description': 'Analyze competitive positioning and market share',
                        'order': 2,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['assessment_rule'],
                    },
                    {
                        'id': 'strategy_adjustment',
                        'name': 'Strategy Adjustment',
                        'description': 'Recommend strategy adjustments based on market response',
                        'order': 3,
                        'estimatedDuration': '5m',
                        'aiAssisted': True,
                        'applicableRules': ['assessment_rule'],
                    },
                ],
            },
        },
    ]
    
    # 3. Create Rules for each stage
    all_rules = []
    for stage in stages:
        stage_id = stage['Data']['stageId']
        stage_rules = get_pricing_promotion_rules_for_stage(stage_id, journey_id)
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


def execute_pricing_promotion_journey(journey_id):
    """Execute a realistic pricing and promotion journey by populating data step by step"""
    print_with_flush('🚀 Executing Realistic Pricing & Promotion Journey...')
    print_with_flush('=' * 60)
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        # Get table references
        products_table = dynamodb.Table('InventoryManagement-Products')
        orders_table = dynamodb.Table('InventoryManagement-Orders')
        customers_table = dynamodb.Table('InventoryManagement-Customers')
        
        print_with_flush('✅ DynamoDB tables connected successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Failed to connect to DynamoDB: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 1: Strategy Initiation (User Action: Marketing team initiates strategy change)
    print_with_flush('📊 Step 1: Strategy Initiation...')
    try:
        # Simulate market analysis and strategy decision
        strategy_id = f'STRATEGY-{datetime.now().strftime("%Y%m%d")}-{uuid.uuid4().hex[:6].upper()}'
        
        print_with_flush(f'📈 Strategy ID: {strategy_id}')
        print_with_flush('🎯 Strategy Type: Cost-Based Price Increase')
        print_with_flush('📊 Market Analysis: Supplier costs increased by 15%')
        print_with_flush('💰 Impact: Vegetables category affected')
        print_with_flush('✅ Strategy validation successful')
        
    except Exception as e:
        print_with_flush(f'❌ Error in strategy initiation: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 2: Product Analysis (User Action: Analyze affected products)
    print_with_flush('\n📦 Step 2: Product Analysis...')
    try:
        # Analyze products in VEGETABLES category
        products_response = products_table.scan(
            FilterExpression='#category = :category',
            ExpressionAttributeNames={'#category': 'category'},
            ExpressionAttributeValues={':category': 'VEGETABLES'}
        )
        
        affected_products = products_response.get('Items', [])
        print_with_flush(f'📊 Found {len(affected_products)} products in VEGETABLES category')
        
        for product in affected_products:
            print_with_flush(f'📦 Product: {product["name"]} (ID: {product["productId"]})')
            print_with_flush(f'💰 Current Price: ₹{product["sellingPrice"]}')
            print_with_flush(f'📊 Current Cost: ₹{product["costPrice"]}')
            
            # Calculate new pricing
            cost_increase = Decimal('0.15')  # 15% cost increase
            new_cost = product['costPrice'] * (1 + cost_increase)
            new_selling = new_cost * Decimal('1.25')  # 25% margin
            
            print_with_flush(f'📈 New Cost: ₹{new_cost}')
            print_with_flush(f'💰 New Price: ₹{new_selling}')
            print_with_flush(f'📊 Price Increase: ₹{new_selling - product["sellingPrice"]}')
            print_with_flush('---')
        
        print_with_flush('✅ Product analysis completed')
        
    except Exception as e:
        print_with_flush(f'❌ Error in product analysis: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 3: Pricing Rules Application (User Action: Apply new pricing)
    print_with_flush('\n💰 Step 3: Pricing Rules Application...')
    try:
        # Update product pricing
        for product in affected_products:
            cost_increase = Decimal('0.15')
            new_cost = product['costPrice'] * (1 + cost_increase)
            new_selling = new_cost * Decimal('1.25')
            
            # Update product with new pricing
            products_table.update_item(
                Key={'productId': product['productId'], 'category': product['category']},
                UpdateExpression='SET costPrice = :cost, sellingPrice = :selling, updatedAt = :timestamp, pricingStrategy = :strategy',
                ExpressionAttributeValues={
                    ':cost': new_cost,
                    ':selling': new_selling,
                    ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    ':strategy': 'COST_BASED_INCREASE'
                }
            )
            
            print_with_flush(f'✅ Updated pricing for {product["name"]}')
            print_with_flush(f'   📈 Cost: ₹{product["costPrice"]} → ₹{new_cost}')
            print_with_flush(f'   💰 Selling: ₹{product["sellingPrice"]} → ₹{new_selling}')
        
        print_with_flush('✅ Pricing rules applied successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Error in pricing rules: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 4: Discount Strategy Implementation (User Action: Apply strategic discounts)
    print_with_flush('\n🎫 Step 4: Discount Strategy Implementation...')
    try:
        # Apply time-based discount (10% off for first week)
        time_discount = Decimal('0.10')
        
        for product in affected_products:
            discounted_price = product['sellingPrice'] * (1 - time_discount)
            
            # Update product with promotional pricing
            products_table.update_item(
                Key={'productId': product['productId'], 'category': product['category']},
                UpdateExpression='SET promotionalPrice = :promo, discountPercentage = :discount, promotionEndDate = :end_date',
                ExpressionAttributeValues={
                    ':promo': discounted_price,
                    ':discount': time_discount,
                    ':end_date': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat().replace('+00:00', 'Z')
                }
            )
            
            print_with_flush(f'🎫 Applied promotional pricing for {product["name"]}')
            print_with_flush(f'   💰 Regular Price: ₹{product["sellingPrice"]}')
            print_with_flush(f'   🎫 Promotional Price: ₹{discounted_price}')
            print_with_flush(f'   📅 Valid until: {(datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d")}')
        
        print_with_flush('✅ Discount strategy implemented successfully')
        
    except Exception as e:
        print_with_flush(f'❌ Error in discount strategy: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 5: Order Updates (User Action: Update existing orders)
    print_with_flush('\n📋 Step 5: Order Updates...')
    try:
        # Find pending orders that need price updates
        orders_response = orders_table.scan(
            FilterExpression='#status IN (:pending, :validated)',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':pending': 'PENDING', ':validated': 'VALIDATED'}
        )
        
        pending_orders = orders_response.get('Items', [])
        print_with_flush(f'📊 Found {len(pending_orders)} pending orders to update')
        
        updated_orders = 0
        for order in pending_orders:
            try:
                # Get updated product pricing
                product_response = products_table.get_item(
                    Key={'productId': order['productId'], 'category': 'VEGETABLES'}
                )
                
                if 'Item' in product_response:
                    updated_product = product_response['Item']
                    new_unit_price = updated_product.get('promotionalPrice', updated_product['sellingPrice'])
                    new_total = new_unit_price * order['quantity']
                    
                    # Update order with new pricing
                    orders_table.update_item(
                        Key={'orderId': order['orderId'], 'customerId': order['customerId']},
                        UpdateExpression='SET unitPrice = :price, totalAmount = :total, finalAmount = :final, updatedAt = :timestamp',
                        ExpressionAttributeValues={
                            ':price': new_unit_price,
                            ':total': new_total,
                            ':final': new_total,
                            ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    
                    print_with_flush(f'✅ Updated Order: {order["orderId"]}')
                    print_with_flush(f'   📦 Product: {order["productId"]}')
                    print_with_flush(f'   💰 Old Total: ₹{order["totalAmount"]}')
                    print_with_flush(f'   💰 New Total: ₹{new_total}')
                    updated_orders += 1
                    
            except Exception as e:
                print_with_flush(f'⚠️  Could not update order {order["orderId"]}: {str(e)}')
                continue
        
        print_with_flush(f'✅ Successfully updated {updated_orders} orders')
        
    except Exception as e:
        print_with_flush(f'❌ Error in order updates: {str(e)}')
        traceback.print_exc()
        return False
    
    # Step 6: Market Impact Assessment (User Action: Monitor market response)
    print_with_flush('\n📊 Step 6: Market Impact Assessment...')
    try:
        # Simulate market impact analysis
        print_with_flush('📈 Market Impact Analysis:')
        print_with_flush('   📊 Order Volume: +12% increase in first 24 hours')
        print_with_flush('   💰 Revenue Impact: +8% increase due to higher prices')
        print_with_flush('   🎫 Discount Effectiveness: 85% of customers used promotional pricing')
        print_with_flush('   ⭐ Customer Satisfaction: 4.2/5 (slight decrease due to price increase)')
        print_with_flush('   📈 Competitive Position: Maintained market share')
        
        # Calculate key metrics
        total_revenue_impact = Decimal('0.08')  # 8% increase
        customer_satisfaction = Decimal('4.2')
        discount_usage = Decimal('0.85')  # 85%
        
        print_with_flush('\n📊 Key Metrics:')
        print_with_flush(f'   💰 Revenue Impact: +{total_revenue_impact * 100}%')
        print_with_flush(f'   ⭐ Customer Satisfaction: {customer_satisfaction}/5')
        print_with_flush(f'   🎫 Discount Usage: {discount_usage * 100}%')
        print_with_flush('   📈 Strategy Success: POSITIVE')
        
        print_with_flush('✅ Market impact assessment completed')
        
    except Exception as e:
        print_with_flush(f'❌ Error in market assessment: {str(e)}')
        traceback.print_exc()
        return False
    
    print_with_flush('\n🎉 Pricing & Promotion Journey Completed Successfully!')
    print_with_flush('=' * 60)
    print_with_flush('📋 Journey Summary:')
    print_with_flush(f'   📊 Strategy Initiation: ✅ {strategy_id} created')
    print_with_flush(f'   📦 Product Analysis: ✅ {len(affected_products)} products analyzed')
    print_with_flush(f'   💰 Pricing Rules: ✅ Applied cost-based pricing')
    print_with_flush(f'   🎫 Discount Strategy: ✅ Promotional pricing implemented')
    print_with_flush(f'   📋 Order Updates: ✅ {updated_orders} orders updated')
    print_with_flush(f'   📊 Market Assessment: ✅ Impact analyzed')
    print_with_flush(f'💰 Revenue Impact: +8%')
    print_with_flush(f'⭐ Customer Satisfaction: 4.2/5')
    print_with_flush(f'🎫 Discount Usage: 85%')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)
    
    return True


def main():
    """Main function to create and execute pricing and promotion journey"""
    print_with_flush('🚀 Creating and Executing Pricing & Promotion Flow Journey...')
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
    
    # Create pricing and promotion journey metadata
    print_with_flush('📋 Creating pricing and promotion journey metadata...')
    journey_item, stages, rules = create_pricing_promotion_journey()
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
    
    # Execute the realistic pricing and promotion journey
    print_with_flush('🔄 Executing Realistic Pricing & Promotion Journey...')
    journey_id = journey_item['Data']['journeyId']
    if execute_pricing_promotion_journey(journey_id):
        print_with_flush('✅ Pricing and promotion journey executed successfully')
    else:
        print_with_flush('❌ Failed to execute pricing and promotion journey')
        return False
    
    print_with_flush('=' * 60)
    print_with_flush('🎉 Complete Pricing & Promotion Journey Successfully Created and Executed!')
    print_with_flush('📦 Journey Features:')
    print_with_flush('   • Market analysis and strategy validation')
    print_with_flush('   • Product category impact analysis')
    print_with_flush('   • Dynamic pricing rule application')
    print_with_flush('   • Strategic discount implementation')
    print_with_flush('   • Order pricing updates and notifications')
    print_with_flush('   • Market impact assessment and monitoring')
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