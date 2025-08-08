#!/usr/bin/env python3
"""
Reset Rider Status

This script resets all riders to available status for testing purposes.
"""

import boto3
import sys
import traceback
from datetime import datetime, timezone


def print_with_flush(message):
    """Print message and flush stdout immediately"""
    print(message)
    sys.stdout.flush()


def reset_rider_status():
    """Reset all riders to available status"""
    print_with_flush('🔄 Resetting rider status in Mumbai region...')

    try:
        print_with_flush('🔗 Creating DynamoDB resource for Mumbai region...')
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        riders_table = dynamodb.Table('InventoryManagement-Riders')
        
        print_with_flush('✅ DynamoDB resource created successfully for Mumbai region')
    except Exception as e:
        print_with_flush(f'❌ Failed to create DynamoDB resource: {str(e)}')
        traceback.print_exc()
        return False

    try:
        print_with_flush('🔍 Scanning all riders...')
        response = riders_table.scan()
        riders = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = riders_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            riders.extend(response.get('Items', []))
        
        print_with_flush(f'📊 Found {len(riders)} riders')
        
        if riders:
            updated_count = 0
            for rider in riders:
                try:
                    # Update rider to available status
                    riders_table.update_item(
                        Key={'riderId': rider['riderId'], 'status': rider['status']},
                        UpdateExpression='SET isAvailable = :available, lastUpdated = :timestamp',
                        ExpressionAttributeValues={
                            ':available': True,
                            ':timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                    )
                    print_with_flush(f'✅ Reset rider: {rider["name"]} (ID: {rider["riderId"]})')
                    updated_count += 1
                except Exception as e:
                    print_with_flush(f'❌ Error updating rider {rider["riderId"]}: {str(e)}')
                    continue
            
            print_with_flush(f'✅ Successfully reset {updated_count} riders to available status')
        else:
            print_with_flush('ℹ️  No riders found to reset')
        
        return True
        
    except Exception as e:
        print_with_flush(f'❌ Error resetting rider status: {str(e)}')
        traceback.print_exc()
        return False


def main():
    """Main function to reset rider status"""
    print_with_flush('🔄 Rider Status Reset Tool')
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
    
    # Reset rider status
    print_with_flush('🔄 Resetting rider status...')
    if reset_rider_status():
        print_with_flush('✅ Rider status reset completed successfully')
    else:
        print_with_flush('❌ Failed to reset rider status')
        return False
    
    print_with_flush('=' * 60)
    print_with_flush('🎉 Rider Status Reset Complete!')
    print_with_flush('✅ All riders are now available for assignment')
    print_with_flush('🌍 Region: ap-south-1 (Mumbai)')
    print_with_flush('=' * 60)
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_with_flush('\n⚠️  Reset interrupted by user')
        sys.exit(1)
    except Exception as e:
        print_with_flush(f'\n❌ Unexpected error: {str(e)}')
        traceback.print_exc()
        sys.exit(1) 