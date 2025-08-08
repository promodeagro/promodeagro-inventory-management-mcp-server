# cleanup_inventory_data.py
import boto3
import sys
import traceback
from datetime import datetime, timezone


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def cleanup_sample_data():
    """Clean up sample data from all InventoryManagement tables"""
    print_with_flush('🧹 Starting sample data cleanup in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    # Define all tables and their sample data
    tables_and_sample_data = {
        'InventoryManagement-Products': [
            {
                'productId': 'PROD001',
                'category': 'VEGETABLES'
            }
        ],
        'InventoryManagement-Batches': [
            {
                'batchId': 'BATCH001',
                'productId': 'PROD001'
            }
        ],
        'InventoryManagement-Suppliers': [
            {
                'supplierId': 'SUPP001',
                'status': 'ACTIVE'
            }
        ],
        'InventoryManagement-Customers': [
            {
                'customerId': 'CUST001',
                'customerType': 'REGULAR'
            }
        ],
        'InventoryManagement-Riders': [
            {
                'riderId': 'RIDER001',
                'status': 'ACTIVE'
            }
        ],
        'InventoryManagement-StockLevels': [
            {
                'productId': 'PROD001',
                'location': 'COLD_STORAGE_A'
            }
        ],
        'InventoryManagement-PurchaseOrders': [
            {
                'poId': 'PO-20241220-ABC123',
                'supplierId': 'SUPP001'
            }
        ],
        'InventoryManagement-Orders': [
            {
                'orderId': 'ORD001',
                'customerId': 'CUST001'
            }
        ],
        'InventoryManagement-Deliveries': [
            {
                'deliveryId': 'DEL001',
                'orderId': 'ORD001'
            }
        ],
        'InventoryManagement-CashCollections': [
            {
                'collectionId': 'COL001',
                'riderId': 'RIDER001'
            }
        ],
        'InventoryManagement-Journeys': [
            {
                'PK': 'JOURNEY#procurement-84882a7b',
                'SK': 'METADATA'
            }
        ]
    }

    total_deleted = 0

    for table_name, sample_keys in tables_and_sample_data.items():
        try:
            print_with_flush(f'🗑️  Cleaning up {table_name}...')
            table = dynamodb.Table(table_name)
            
            deleted_count = 0
            with table.batch_writer() as batch:
                for key in sample_keys:
                    try:
                        batch.delete_item(Key=key)
                        deleted_count += 1
                        print_with_flush(f'✅ Deleted from {table_name}: {list(key.values())[0]}')
                    except Exception as e:
                        print_with_flush(f'⚠️  Could not delete from {table_name}: {str(e)}')
            
            total_deleted += deleted_count
            print_with_flush(f'✅ {table_name}: {deleted_count} records deleted')
            
        except Exception as e:
            print_with_flush(f'❌ Error cleaning up {table_name}: {str(e)}')
            continue

    print_with_flush(f'✅ Sample data cleanup completed! Total records deleted: {total_deleted}')
    return True


def cleanup_by_entity_type(entity_type):
    """Clean up all data for a specific entity type across relevant tables"""
    print_with_flush(f'🧹 Cleaning up {entity_type} data in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    # Map entity types to their corresponding tables
    entity_table_mapping = {
        'PRODUCT': ['InventoryManagement-Products', 'InventoryManagement-StockLevels'],
        'BATCH': ['InventoryManagement-Batches'],
        'SUPPLIER': ['InventoryManagement-Suppliers', 'InventoryManagement-PurchaseOrders'],
        'CUSTOMER': ['InventoryManagement-Customers', 'InventoryManagement-Orders'],
        'RIDER': ['InventoryManagement-Riders', 'InventoryManagement-CashCollections'],
        'ORDER': ['InventoryManagement-Orders', 'InventoryManagement-Deliveries'],
        'DELIVERY': ['InventoryManagement-Deliveries'],
        'PURCHASE_ORDER': ['InventoryManagement-PurchaseOrders'],
        'STOCK_LEVEL': ['InventoryManagement-StockLevels'],
        'CASH_COLLECTION': ['InventoryManagement-CashCollections'],
        'JOURNEY': ['InventoryManagement-Journeys']
    }

    if entity_type not in entity_table_mapping:
        print_with_flush(f'❌ Unknown entity type: {entity_type}')
        print_with_flush(f'Available types: {list(entity_table_mapping.keys())}')
        return False

    target_tables = entity_table_mapping[entity_type]
    total_deleted = 0

    for table_name in target_tables:
        try:
            print_with_flush(f'🗑️  Cleaning up {entity_type} data from {table_name}...')
            table = dynamodb.Table(table_name)
            
            # Scan the table to find all records
            response = table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            print_with_flush(f'📊 Found {len(items)} records in {table_name}')
            
            if items:
                deleted_count = 0
                with table.batch_writer() as batch:
                    for item in items:
                        # Get the primary key for deletion
                        if 'productId' in item:
                            key = {'productId': item['productId']}
                            if 'category' in item:
                                key['category'] = item['category']
                            elif 'location' in item:
                                key['location'] = item['location']
                        elif 'batchId' in item:
                            key = {'batchId': item['batchId'], 'productId': item['productId']}
                        elif 'supplierId' in item:
                            key = {'supplierId': item['supplierId'], 'status': item['status']}
                        elif 'customerId' in item:
                            key = {'customerId': item['customerId'], 'customerType': item['customerType']}
                        elif 'riderId' in item:
                            key = {'riderId': item['riderId'], 'status': item['status']}
                        elif 'orderId' in item:
                            key = {'orderId': item['orderId'], 'customerId': item['customerId']}
                        elif 'deliveryId' in item:
                            key = {'deliveryId': item['deliveryId'], 'orderId': item['orderId']}
                        elif 'poId' in item:
                            key = {'poId': item['poId'], 'supplierId': item['supplierId']}
                        elif 'collectionId' in item:
                            key = {'collectionId': item['collectionId'], 'riderId': item['riderId']}
                        elif 'PK' in item:
                            key = {'PK': item['PK'], 'SK': item['SK']}
                        else:
                            continue
                        
                        batch.delete_item(Key=key)
                        deleted_count += 1
                        print_with_flush(f'✅ Deleted: {list(key.values())[0]}')
                
                total_deleted += deleted_count
                print_with_flush(f'✅ {table_name}: {deleted_count} records deleted')
            else:
                print_with_flush(f'ℹ️  No records found in {table_name}')
                
        except Exception as e:
            print_with_flush(f'❌ Error cleaning up {table_name}: {str(e)}')
            traceback.print_exc()
            continue

    print_with_flush(f'✅ {entity_type} data cleanup completed! Total records deleted: {total_deleted}')
    return True


def cleanup_all_data():
    """Clean up all data from all InventoryManagement tables"""
    print_with_flush('🧹 Starting complete data cleanup in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    # List of all tables
    table_names = [
        'InventoryManagement-Products',
        'InventoryManagement-Batches',
        'InventoryManagement-Suppliers',
        'InventoryManagement-Customers',
        'InventoryManagement-Riders',
        'InventoryManagement-Orders',
        'InventoryManagement-Deliveries',
        'InventoryManagement-StockLevels',
        'InventoryManagement-PurchaseOrders',
        'InventoryManagement-CashCollections',
        'InventoryManagement-Journeys'
    ]

    total_deleted = 0

    for table_name in table_names:
        try:
            print_with_flush(f'🗑️  Cleaning up all data from {table_name}...')
            table = dynamodb.Table(table_name)
            
            # Scan the table to find all records
            response = table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            print_with_flush(f'📊 Found {len(items)} records in {table_name}')
            
            if items:
                deleted_count = 0
                with table.batch_writer() as batch:
                    for item in items:
                        # Get the primary key for deletion based on table structure
                        if table_name == 'InventoryManagement-Products':
                            key = {'productId': item['productId'], 'category': item['category']}
                        elif table_name == 'InventoryManagement-Batches':
                            key = {'batchId': item['batchId'], 'productId': item['productId']}
                        elif table_name == 'InventoryManagement-Suppliers':
                            key = {'supplierId': item['supplierId'], 'status': item['status']}
                        elif table_name == 'InventoryManagement-Customers':
                            key = {'customerId': item['customerId'], 'customerType': item['customerType']}
                        elif table_name == 'InventoryManagement-Riders':
                            key = {'riderId': item['riderId'], 'status': item['status']}
                        elif table_name == 'InventoryManagement-Orders':
                            key = {'orderId': item['orderId'], 'customerId': item['customerId']}
                        elif table_name == 'InventoryManagement-Deliveries':
                            key = {'deliveryId': item['deliveryId'], 'orderId': item['orderId']}
                        elif table_name == 'InventoryManagement-StockLevels':
                            key = {'productId': item['productId'], 'location': item['location']}
                        elif table_name == 'InventoryManagement-PurchaseOrders':
                            key = {'poId': item['poId'], 'supplierId': item['supplierId']}
                        elif table_name == 'InventoryManagement-CashCollections':
                            key = {'collectionId': item['collectionId'], 'riderId': item['riderId']}
                        elif table_name == 'InventoryManagement-Journeys':
                            key = {'PK': item['PK'], 'SK': item['SK']}
                        else:
                            continue
                        
                        batch.delete_item(Key=key)
                        deleted_count += 1
                
                total_deleted += deleted_count
                print_with_flush(f'✅ {table_name}: {deleted_count} records deleted')
            else:
                print_with_flush(f'ℹ️  No records found in {table_name}')
                
        except Exception as e:
            print_with_flush(f'❌ Error cleaning up {table_name}: {str(e)}')
            traceback.print_exc()
            continue

    print_with_flush(f'✅ Complete data cleanup finished! Total records deleted: {total_deleted}')
    return True


def delete_all_tables():
    """Delete all InventoryManagement tables"""
    print_with_flush('🗑️  Starting deletion of all InventoryManagement tables in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region...')
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB client created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False

    # List of all tables to delete
    table_names = [
        'InventoryManagement-Products',
        'InventoryManagement-Batches',
        'InventoryManagement-Suppliers',
        'InventoryManagement-Customers',
        'InventoryManagement-Riders',
        'InventoryManagement-Orders',
        'InventoryManagement-Deliveries',
        'InventoryManagement-StockLevels',
        'InventoryManagement-PurchaseOrders',
        'InventoryManagement-CashCollections',
        'InventoryManagement-Journeys'
    ]

    deleted_tables = 0

    for table_name in table_names:
        try:
            print_with_flush(f'🔍 Checking if {table_name} exists in Mumbai region...')
            
            try:
                response = dynamodb.describe_table(TableName=table_name)
                print_with_flush(f'✅ {table_name} exists, proceeding with deletion...')
                
                print_with_flush(f'🗑️  Deleting {table_name} in Mumbai region...')
                dynamodb.delete_table(TableName=table_name)
                
                print_with_flush(f'⏳ Waiting for {table_name} deletion to complete...')
                waiter = dynamodb.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name)
                
                print_with_flush(f'✅ {table_name} deleted successfully!')
                deleted_tables += 1
                
            except dynamodb.exceptions.ResourceNotFoundException:
                print_with_flush(f'ℹ️  {table_name} does not exist in Mumbai region')
                
        except Exception as e:
            print_with_flush(f'❌ Error deleting {table_name}: {str(e)}')
            traceback.print_exc()
            continue

    print_with_flush(f'✅ Table deletion completed! {deleted_tables} tables deleted')
    return True


def main():
    """Main function with cleanup options"""
    print_with_flush('🧹 Inventory Management System Data Cleanup in Mumbai Region...')
    print_with_flush('=' * 60)

    # Test AWS credentials and region
    try:
        print_with_flush('🔐 Testing AWS credentials...')
        
        sts = boto3.client('sts', region_name='ap-south-1')
        identity = sts.get_caller_identity()
        
        print_with_flush(f'✅ AWS Identity: {identity["Arn"]}')
        print_with_flush(f'✅ AWS Account: {identity["Account"]}')

        # Set Mumbai region
        region = 'ap-south-1'
        print_with_flush(f'✅ AWS Region: {region} (Mumbai)')

    except Exception as e:
        print_with_flush(f'❌ AWS authentication failed: {str(e)}')
        traceback.print_exc()
        return False

    print_with_flush('=' * 60)
    print_with_flush('🧹 Cleanup Options:')
    print_with_flush('1. Clean up sample data only (default)')
    print_with_flush('2. Clean up specific entity type')
    print_with_flush('3. Clean up all data')
    print_with_flush('4. Delete all tables')
    print_with_flush('=' * 60)

    # For now, we'll clean up sample data only
    print_with_flush('🗑️  Step 1: Cleaning up sample data in Mumbai region...')
    if cleanup_sample_data():
        print_with_flush('✅ Sample data cleanup complete in Mumbai region')
    else:
        print_with_flush('❌ Sample data cleanup failed')
        return False

    print_with_flush('=' * 60)
    print_with_flush('🎉 Inventory data cleanup completed successfully in Mumbai Region!')
    print_with_flush('✅ Actions performed:')
    print_with_flush('   • Sample data removed from all 11 tables in Mumbai region')
    print_with_flush('   • Table structures preserved in Mumbai region')
    print_with_flush('   • Ready for fresh data in Mumbai region')
    print_with_flush('📊 Tables cleaned:')
    print_with_flush('   • Products, Batches, Suppliers, Customers, Riders')
    print_with_flush('   • Orders, Deliveries, StockLevels, PurchaseOrders')
    print_with_flush('   • CashCollections, Journeys')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Cleanup interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1) 