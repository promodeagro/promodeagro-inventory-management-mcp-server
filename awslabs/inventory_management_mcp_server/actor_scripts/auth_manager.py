# auth_manager.py
import boto3
import sys
import getpass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any


class AuthManager:
    """Authentication and User Management for Actor-Based System"""
    
    def __init__(self, region_name: str = 'ap-south-1'):
        self.region_name = region_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.current_user = None
        self.current_role = None
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"🎭 {title}")
        print("=" * 60)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")
        
    def test_aws_connection(self) -> bool:
        """Test AWS connection and credentials"""
        try:
            sts = boto3.client('sts', region_name=self.region_name)
            identity = sts.get_caller_identity()
            print(f"🔐 AWS Identity: {identity['Arn']}")
            print(f"🏢 AWS Account: {identity['Account']}")
            print(f"🌍 AWS Region: {self.region_name}")
            return True
        except Exception as e:
            self.print_error(f"AWS connection failed: {str(e)}")
            return False
            
    def login(self) -> bool:
        """Authenticate user login"""
        self.print_header("ACTOR-BASED INVENTORY MANAGEMENT SYSTEM")
        
        # Test AWS connection
        if not self.test_aws_connection():
            return False
            
        print("\n🔐 Please enter your credentials:")
        
        # Get username and password
        username = input("👤 Username: ").strip()
        password = getpass.getpass("🔒 Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        # Authenticate user
        user = self.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Permissions: {', '.join(user.get('permissions', []))}")
            return True
        else:
            self.print_error("Invalid credentials. Please try again.")
            return False
            
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against DynamoDB Users table"""
        try:
            # Query user by username (assuming username is stored in userId field)
            response = self.users_table.query(
                KeyConditionExpression='userId = :username',
                FilterExpression='isActive = :active',
                ExpressionAttributeValues={
                    ':username': username,
                    ':active': True
                }
            )
            
            if response['Items']:
                user = response['Items'][0]
                # In a real system, you'd hash and compare passwords
                # For demo purposes, we'll use simple comparison
                if self.verify_password(password, user.get('password', '')):
                    return user
                    
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simplified for demo)"""
        # In production, use proper password hashing (bcrypt, etc.)
        return input_password == stored_password
        
    def get_user_permissions(self) -> list:
        """Get current user permissions"""
        if self.current_user:
            return self.current_user.get('permissions', [])
        return []
        
    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission"""
        permissions = self.get_user_permissions()
        return permission in permissions
        
    def require_permission(self, permission: str) -> bool:
        """Require specific permission for operation"""
        if not self.has_permission(permission):
            self.print_error(f"Access denied. Required permission: {permission}")
            return False
        return True
        
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.print_success(f"Goodbye, {self.current_user.get('name', 'User')}!")
            self.current_user = None
            self.current_role = None
        else:
            self.print_info("No user logged in")
            
    def get_current_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if self.current_user:
            return {
                'userId': self.current_user.get('userId'),
                'name': self.current_user.get('name'),
                'role': self.current_user.get('role'),
                'email': self.current_user.get('email'),
                'permissions': self.current_user.get('permissions', [])
            }
        return {}
        
    def create_demo_users(self):
        """Create demo users for testing"""
        demo_users = [
            {
                'userId': 'admin',
                'role': 'SUPER_ADMIN',
                'name': 'System Administrator',
                'email': 'admin@company.com',
                'phone': '+919876543210',
                'password': 'admin123',
                'permissions': [
                    'SYSTEM_CONFIG', 'USER_MANAGEMENT', 'INTEGRATION_MANAGEMENT',
                    'SYSTEM_MONITORING', 'BACKUP_RECOVERY', 'LICENSE_MANAGEMENT',
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'userId': 'warehouse_mgr',
                'role': 'WAREHOUSE_MANAGER',
                'name': 'Amit Patel',
                'email': 'amit@company.com',
                'phone': '+919876543211',
                'password': 'warehouse123',
                'permissions': [
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'ADJUSTMENT_APPROVE',
                    'WAREHOUSE_MANAGEMENT', 'QUALITY_CONTROL', 'RECEIVING_MANAGEMENT',
                    'EXPIRY_MANAGEMENT', 'SPACE_OPTIMIZATION'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'userId': 'inventory_staff',
                'role': 'INVENTORY_STAFF',
                'name': 'Priya Sharma',
                'email': 'priya@company.com',
                'phone': '+919876543212',
                'password': 'inventory123',
                'permissions': [
                    'INVENTORY_READ', 'INVENTORY_WRITE', 'STOCK_MOVEMENT',
                    'ORDER_FULFILLMENT', 'INVENTORY_COUNTING'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'userId': 'logistics_mgr',
                'role': 'LOGISTICS_MANAGER',
                'name': 'Rajesh Kumar',
                'email': 'rajesh@company.com',
                'phone': '+919876543213',
                'password': 'logistics123',
                'permissions': [
                    'ROUTE_PLANNING', 'DELIVERY_MANAGEMENT', 'RIDER_MANAGEMENT',
                    'RUNSHEET_MANAGEMENT', 'PERFORMANCE_MONITORING'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'userId': 'rider',
                'role': 'DELIVERY_PERSONNEL',
                'name': 'Amit Kumar',
                'email': 'amit.rider@company.com',
                'phone': '+919876543214',
                'password': 'rider123',
                'permissions': [
                    'RUNSHEET_VIEW', 'ORDER_DELIVERY', 'CASH_COLLECTION',
                    'STATUS_UPDATE', 'CUSTOMER_INTERACTION'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            {
                'userId': 'auditor',
                'role': 'AUDITOR',
                'name': 'Sneha Verma',
                'email': 'sneha@company.com',
                'phone': '+919876543215',
                'password': 'auditor123',
                'permissions': [
                    'TRANSACTION_VERIFICATION', 'COMPLIANCE_CHECKING',
                    'INVENTORY_VERIFICATION', 'REPORT_GENERATION', 'PROCESS_REVIEW'
                ],
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        ]
        
        try:
            with self.users_table.batch_writer() as batch:
                for user in demo_users:
                    batch.put_item(Item=user)
                    self.print_success(f"Created user: {user['name']} ({user['role']})")
                    
            self.print_success("Demo users created successfully!")
            self.print_info("You can now login with any of these credentials:")
            for user in demo_users:
                print(f"   👤 {user['userId']} / {user['password']} ({user['role']})")
                
        except Exception as e:
            self.print_error(f"Error creating demo users: {str(e)}")


if __name__ == '__main__':
    auth = AuthManager()
    auth.create_demo_users() 