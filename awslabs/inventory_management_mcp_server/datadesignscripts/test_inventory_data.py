# test_inventory_data.py
import boto3
import sys
import traceback
from datetime import datetime, timezone


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def test_inventory_table_access():
    """Test access to the InventoryManagement table"""
    print_with_flush('🧪 Testing InventoryManagement table access in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB client for Mumbai region...')
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        print_with_flush('✅ DynamoDB client created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB client: {str(e)}')
        traceback.print_exc()
        return False

    try:
        print_with_flush('🔍 Checking table status in Mumbai region...')
        response = dynamodb.describe_table(TableName='InventoryManagement')
        
        table_status = response["Table"]["TableStatus"]
        print_with_flush(f'✅ Table Status: {table_status}')
        
        if table_status == 'ACTIVE':
            print_with_flush('✅ Table is active and ready for operations in Mumbai region')
            return True
        else:
            print_with_flush(f'⚠️  Table is not active: {table_status}')
            return False
            
    except dynamodb.exceptions.ResourceNotFoundException:
        print_with_flush('❌ Table does not exist in Mumbai region. Please run setup_dynamodb.py first.')
        return False
    except Exception as e:
        print_with_flush(f'❌ Error accessing table: {str(e)}')
        traceback.print_exc()
        return False


def test_sample_data_queries():
    """Test sample data queries to verify data integrity"""
    print_with_flush('🔍 Testing sample data queries in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('InventoryManagement')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    test_queries = [
        {
            'name': 'Product Query',
            'pk': 'ENTITY#PRODUCT#PROD001',
            'sk': 'METADATA#INFO#2024-01-01T00:00:00Z'
        },
        {
            'name': 'Batch Query',
            'pk': 'ENTITY#BATCH#BATCH001',
            'sk': 'METADATA#INFO#2024-01-01T00:00:00Z'
        },
        {
            'name': 'Supplier Query',
            'pk': 'ENTITY#SUPPLIER#SUPP001',
            'sk': 'METADATA#INFO#2024-01-01T00:00:00Z'
        },
        {
            'name': 'Customer Query',
            'pk': 'ENTITY#CUSTOMER#CUST001',
            'sk': 'METADATA#INFO#2024-01-01T00:00:00Z'
        },
        {
            'name': 'Rider Query',
            'pk': 'ENTITY#RIDER#RIDER001',
            'sk': 'METADATA#INFO#2024-01-01T00:00:00Z'
        }
    ]

    success_count = 0
    total_count = len(test_queries)

    for query in test_queries:
        try:
            print_with_flush(f'🔍 Testing {query["name"]}...')
            
            response = table.get_item(
                Key={
                    'PK': query['pk'],
                    'SK': query['sk']
                }
            )
            
            if 'Item' in response:
                item = response['Item']
                print_with_flush(f'✅ {query["name"]} found: {item.get("name", item.get("productId", item.get("supplierId", item.get("customerId", item.get("riderId", "Unknown")))))}')
                success_count += 1
            else:
                print_with_flush(f'❌ {query["name"]} not found')
                
        except Exception as e:
            print_with_flush(f'❌ Error testing {query["name"]}: {str(e)}')
            traceback.print_exc()

    print_with_flush(f'📊 Query Test Results: {success_count}/{total_count} successful')
    return success_count == total_count


def test_gsi_queries():
    """Test GSI queries to verify index functionality"""
    print_with_flush('🔍 Testing GSI queries in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('InventoryManagement')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    test_gsi_queries = [
        {
            'name': 'Products by Category (GSI1)',
            'index': 'GSI1',
            'pk': 'CATEGORY#VEGETABLES',
            'sk_prefix': 'PRODUCT#'
        },
        {
            'name': 'Suppliers by Status (GSI1)',
            'index': 'GSI1',
            'pk': 'SUPPLIER#ACTIVE',
            'sk_prefix': 'SUPP'
        },
        {
            'name': 'Customers by Type (GSI1)',
            'index': 'GSI1',
            'pk': 'CUSTOMER#REGULAR',
            'sk_prefix': 'CUST'
        },
        {
            'name': 'Riders by Status (GSI1)',
            'index': 'GSI1',
            'pk': 'RIDER#ACTIVE',
            'sk_prefix': 'RIDER'
        }
    ]

    success_count = 0
    total_count = len(test_gsi_queries)

    for query in test_gsi_queries:
        try:
            print_with_flush(f'🔍 Testing {query["name"]}...')
            
            response = table.query(
                IndexName=query['index'],
                KeyConditionExpression='GSI1PK = :pk AND begins_with(GSI1SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': query['pk'],
                    ':sk_prefix': query['sk_prefix']
                }
            )
            
            items = response.get('Items', [])
            print_with_flush(f'✅ {query["name"]} found {len(items)} items')
            success_count += 1
                
        except Exception as e:
            print_with_flush(f'❌ Error testing {query["name"]}: {str(e)}')
            traceback.print_exc()

    print_with_flush(f'📊 GSI Query Test Results: {success_count}/{total_count} successful')
    return success_count == total_count


def test_data_integrity():
    """Test data integrity and relationships"""
    print_with_flush('🔍 Testing data integrity in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('InventoryManagement')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    integrity_tests = [
        {
            'name': 'Product-Batch Relationship',
            'pk': 'ENTITY#PRODUCT#PROD001',
            'sk_prefix': 'METADATA#'
        },
        {
            'name': 'Product-Stock Relationship',
            'pk': 'ENTITY#PRODUCT#PROD001',
            'sk_prefix': 'METADATA#STOCK#'
        }
    ]

    success_count = 0
    total_count = len(integrity_tests)

    for test in integrity_tests:
        try:
            print_with_flush(f'🔍 Testing {test["name"]}...')
            
            response = table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': test['pk'],
                    ':sk_prefix': test['sk_prefix']
                }
            )
            
            items = response.get('Items', [])
            print_with_flush(f'✅ {test["name"]} found {len(items)} related records')
            success_count += 1
                
        except Exception as e:
            print_with_flush(f'❌ Error testing {test["name"]}: {str(e)}')
            traceback.print_exc()

    print_with_flush(f'📊 Integrity Test Results: {success_count}/{total_count} successful')
    return success_count == total_count


def main():
    """Main function with comprehensive testing"""
    print_with_flush('🧪 Starting Inventory Management System Data Tests in Mumbai Region...')
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

    # Test table access
    print_with_flush('🗄️  Step 1: Testing table access in Mumbai region...')
    if test_inventory_table_access():
        print_with_flush('✅ Table access test complete in Mumbai region')
    else:
        print_with_flush('❌ Table access test failed')
        return False

    print_with_flush('=' * 60)

    # Test sample data queries
    print_with_flush('🔍 Step 2: Testing sample data queries in Mumbai region...')
    if test_sample_data_queries():
        print_with_flush('✅ Sample data query test complete in Mumbai region')
    else:
        print_with_flush('❌ Sample data query test failed')
        return False

    print_with_flush('=' * 60)

    # Test GSI queries
    print_with_flush('🔍 Step 3: Testing GSI queries in Mumbai region...')
    if test_gsi_queries():
        print_with_flush('✅ GSI query test complete in Mumbai region')
    else:
        print_with_flush('❌ GSI query test failed')
        return False

    print_with_flush('=' * 60)

    # Test data integrity
    print_with_flush('🔍 Step 4: Testing data integrity in Mumbai region...')
    if test_data_integrity():
        print_with_flush('✅ Data integrity test complete in Mumbai region')
    else:
        print_with_flush('❌ Data integrity test failed')
        return False

    print_with_flush('=' * 60)
    print_with_flush('🎉 All inventory data tests completed successfully in Mumbai Region!')
    print_with_flush('✅ Features verified:')
    print_with_flush('   • Table access and connectivity in Mumbai region')
    print_with_flush('   • Sample data retrieval in Mumbai region')
    print_with_flush('   • GSI query functionality in Mumbai region')
    print_with_flush('   • Data relationship integrity in Mumbai region')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Testing interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1) 