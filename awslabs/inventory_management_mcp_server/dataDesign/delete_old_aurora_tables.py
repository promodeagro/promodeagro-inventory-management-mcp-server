#!/usr/bin/env python3
# delete_old_aurora_tables.py
"""
Aurora Spark Theme - Delete Old DynamoDB Tables Script
Cleans up previously created tables to prepare for optimized design
"""

import boto3
import sys
import traceback
import time


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def list_aurora_tables():
    """List all Aurora Spark Theme tables"""
    try:
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        # List all tables
        response = dynamodb.list_tables()
        all_tables = response.get('TableNames', [])
        
        # Filter Aurora Spark Theme tables
        aurora_tables = [table for table in all_tables if table.startswith('AuroraSparkTheme-')]
        
        return aurora_tables, dynamodb
        
    except Exception as e:
        print_with_flush(f'❌ Failed to list tables: {str(e)}')
        return [], None


def delete_aurora_tables():
    """Delete all Aurora Spark Theme DynamoDB tables"""
    print_with_flush('🗑️  Starting Aurora Spark Theme table cleanup...')
    
    aurora_tables, dynamodb = list_aurora_tables()
    
    if not aurora_tables:
        print_with_flush('ℹ️  No Aurora Spark Theme tables found to delete')
        return True
    
    if not dynamodb:
        print_with_flush('❌ Failed to connect to DynamoDB')
        return False
    
    print_with_flush(f'📋 Found {len(aurora_tables)} Aurora Spark Theme tables:')
    for table in aurora_tables:
        print_with_flush(f'   • {table}')
    
    # Confirm deletion
    print_with_flush('')
    print_with_flush('⚠️  WARNING: This will permanently delete all Aurora Spark Theme tables!')
    print_with_flush('⚠️  All data in these tables will be lost!')
    print_with_flush('')
    
    confirm = input('Are you sure you want to delete all tables? Type "DELETE" to confirm: ').strip()
    
    if confirm != 'DELETE':
        print_with_flush('❌ Deletion cancelled - confirmation not received')
        return False
    
    print_with_flush('')
    print_with_flush('🗑️  Starting table deletion process...')
    
    deleted_tables = []
    failed_deletions = []
    
    for table_name in aurora_tables:
        try:
            print_with_flush(f'🗑️  Deleting {table_name}...')
            
            # Delete the table
            response = dynamodb.delete_table(TableName=table_name)
            print_with_flush(f'✅ {table_name} deletion initiated')
            print_with_flush(f'   Status: {response["TableDescription"]["TableStatus"]}')
            
            # Wait for table to be deleted
            print_with_flush(f'⏳ Waiting for {table_name} to be deleted...')
            waiter = dynamodb.get_waiter('table_not_exists')
            waiter.wait(TableName=table_name)
            print_with_flush(f'✅ {table_name} deleted successfully!')
            
            deleted_tables.append(table_name)
            
            # Small delay to avoid throttling
            time.sleep(1)
            
        except dynamodb.exceptions.ResourceNotFoundException:
            print_with_flush(f'⚠️  Table {table_name} does not exist (already deleted)')
            deleted_tables.append(table_name)
        except Exception as e:
            print_with_flush(f'❌ Failed to delete {table_name}: {str(e)}')
            failed_deletions.append(table_name)
            traceback.print_exc()
    
    # Summary
    print_with_flush('')
    print_with_flush('=' * 80)
    print_with_flush('📊 DELETION SUMMARY:')
    print_with_flush(f'   ✅ Successfully deleted: {len(deleted_tables)} tables')
    print_with_flush(f'   ❌ Failed to delete: {len(failed_deletions)} tables')
    
    if deleted_tables:
        print_with_flush('')
        print_with_flush('✅ DELETED TABLES:')
        for table in deleted_tables:
            print_with_flush(f'   • {table}')
    
    if failed_deletions:
        print_with_flush('')
        print_with_flush('❌ FAILED DELETIONS:')
        for table in failed_deletions:
            print_with_flush(f'   • {table}')
    
    print_with_flush('')
    if len(failed_deletions) == 0:
        print_with_flush('🎉 All Aurora Spark Theme tables deleted successfully!')
        print_with_flush('✅ System is ready for optimized table creation')
    else:
        print_with_flush('⚠️  Some tables failed to delete - please check manually')
    
    print_with_flush('=' * 80)
    
    return len(failed_deletions) == 0


def verify_cleanup():
    """Verify that all tables have been cleaned up"""
    print_with_flush('🔍 Verifying table cleanup...')
    
    aurora_tables, _ = list_aurora_tables()
    
    if not aurora_tables:
        print_with_flush('✅ Cleanup verified - No Aurora Spark Theme tables found')
        return True
    else:
        print_with_flush(f'⚠️  Cleanup incomplete - {len(aurora_tables)} tables still exist:')
        for table in aurora_tables:
            print_with_flush(f'   • {table}')
        return False


def main():
    """Main function for table cleanup"""
    print_with_flush('🗑️  Aurora Spark Theme - Table Cleanup Script')
    print_with_flush('=' * 80)
    print_with_flush('This script will delete all existing Aurora Spark Theme tables')
    print_with_flush('to prepare for the new optimized 12-table design')
    print_with_flush('=' * 80)
    
    # Test AWS credentials
    try:
        print_with_flush('🔐 Testing AWS credentials...')
        sts = boto3.client('sts', region_name='ap-south-1')
        identity = sts.get_caller_identity()
        print_with_flush(f'✅ AWS Account: {identity["Account"]}')
        print_with_flush(f'✅ AWS Region: ap-south-1 (Mumbai)')
    except Exception as e:
        print_with_flush(f'❌ AWS authentication failed: {str(e)}')
        return False
    
    print_with_flush('=' * 80)
    
    # List existing tables first
    aurora_tables, _ = list_aurora_tables()
    
    if not aurora_tables:
        print_with_flush('ℹ️  No Aurora Spark Theme tables found - nothing to delete')
        return True
    
    # Delete tables
    if delete_aurora_tables():
        print_with_flush('')
        print_with_flush('🎯 NEXT STEPS:')
        print_with_flush('   1. Run setup_optimized_aurora_spark_dynamodb.py')
        print_with_flush('   2. Create 12 optimized tables')
        print_with_flush('   3. Seed with sample data')
        print_with_flush('   4. Start building portal applications')
        
        # Verify cleanup
        time.sleep(2)  # Wait a bit before verification
        verify_cleanup()
        
        return True
    else:
        print_with_flush('❌ Table deletion failed - please check errors above')
        return False


if __name__ == '__main__':
    try:
        success = main()
        print_with_flush(f'\n{"✅ Cleanup completed successfully!" if success else "❌ Cleanup failed!"}')
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Cleanup interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1)
