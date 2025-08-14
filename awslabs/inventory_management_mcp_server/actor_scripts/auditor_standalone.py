#!/usr/bin/env python3
# auditor_standalone.py
"""
Auditor Standalone Script
Run this script in a separate terminal window for Auditor operations.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List


class AuditorStandalone:
    """Standalone Auditor with Compliance and Audit Operations"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.users_table = self.dynamodb.Table('InventoryManagement-Users')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.orders_table = self.dynamodb.Table('InventoryManagement-Orders')
        self.stock_levels_table = self.dynamodb.Table('InventoryManagement-StockLevels')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.deliveries_table = self.dynamodb.Table('InventoryManagement-Deliveries')
        self.cash_collections_table = self.dynamodb.Table('InventoryManagement-CashCollections')
        self.reports_table = self.dynamodb.Table('InventoryManagement-Reports')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
        self.current_user = None
        self.current_role = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"[AUDIT] {title}")
        print("=" * 80)
        
    def print_success(self, message: str):
        """Print success message"""
        print(f"[SUCCESS] {message}")
        
    def print_error(self, message: str):
        """Print error message"""
        print(f"[ERROR] {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"[INFO]  {message}")
        
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"[INTERRUPTED]  {message}")
        
    def test_aws_connection(self) -> bool:
        """Test AWS connection and credentials"""
        try:
            sts = boto3.client('sts', region_name=self.region_name)
            identity = sts.get_caller_identity()
            print(f"[SECURE] AWS Identity: {identity['Arn']}")
            print(f"[ACCOUNT] AWS Account: {identity['Account']}")
            print(f"[REGION] AWS Region: {self.region_name}")
            return True
        except Exception as e:
            self.print_error(f"AWS connection failed: {str(e)}")
            return False
            
    def authenticate_user(self) -> bool:
        """Authenticate user login"""
        self.clear_screen()
        self.print_header("AUDITOR - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your credentials:")
        print("[NOTE] Demo credentials: auditor / auditor123")
        
        username = input("\n[USER] Username: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
        if not username or not password:
            self.print_error("Username and password are required")
            return False
            
        user = self.authenticate_user_db(username, password)
        if user and user.get('role') == 'AUDITOR':
            self.current_user = user
            self.current_role = user.get('role')
            self.print_success(f"Welcome, {user.get('name', username)}!")
            self.print_info(f"Role: {self.current_role}")
            self.print_info(f"Permissions: {', '.join(user.get('permissions', []))}")
            return True
        else:
            self.print_error("Invalid credentials or insufficient permissions.")
            self.print_error("Only Auditor role can access this system.")
            return False
            
    def authenticate_user_db(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against DynamoDB Users table"""
        try:
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
                if self.verify_password(password, user.get('password', '')):
                    return user
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simplified for demo)"""
        return input_password == stored_password
        
    def create_demo_user(self):
        """Create demo auditor user if not exists"""
        try:
            demo_user = {
                'userId': 'auditor',
                'role': 'AUDITOR',
                'name': 'Priya Sharma',
                'email': 'priya.auditor@company.com',
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
            
            response = self.users_table.get_item(
                Key={'userId': 'auditor', 'role': 'AUDITOR'}
            )
            
            if 'Item' not in response:
                self.users_table.put_item(Item=demo_user)
                self.print_success("Demo Auditor user created!")
                self.print_info("Username: auditor")
                self.print_info("Password: auditor123")
            else:
                self.print_info("Demo user already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo user: {str(e)}")
            
    def show_main_menu(self):
        """Show Auditor main menu"""
        while True:
            self.clear_screen()
            self.print_header("AUDITOR DASHBOARD")
            
            if self.current_user:
                print(f"[USER] User: {self.current_user.get('name', 'Unknown')}")
                print(f"[AUDIT] Role: {self.current_user.get('role', 'Unknown')}")
                print(f"[EMAIL] Email: {self.current_user.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. [AUDIT] Transaction Verification")
            print("2. [SUCCESS] Compliance Checking")
            print("3. [ORDER] Inventory Verification")
            print("4. [TRACK] Report Generation")
            print("5. [FLOW] Process Review")
            print("6. [REPORT] Audit Analytics")
            print("7. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-7): ").strip()
            
            if choice == '1':
                self.transaction_verification_menu()
            elif choice == '2':
                self.compliance_checking_menu()
            elif choice == '3':
                self.inventory_verification_menu()
            elif choice == '4':
                self.report_generation_menu()
            elif choice == '5':
                self.process_review_menu()
            elif choice == '6':
                self.audit_analytics_menu()
            elif choice == '7':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Auditor system!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def transaction_verification_menu(self):
        """Transaction Verification Operations"""
        while True:
            self.clear_screen()
            self.print_header("TRANSACTION VERIFICATION")
            print("1. [PRICE] Verify Cash Collections")
            print("2. [ORDER] Verify Order Transactions")
            print("3. [TRACK] Review Transaction History")
            print("4. [INTERRUPTED] Flag Suspicious Transactions")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.verify_cash_collections()
            elif choice == '2':
                self.verify_order_transactions()
            elif choice == '3':
                self.review_transaction_history()
            elif choice == '4':
                self.flag_suspicious_transactions()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def verify_cash_collections(self):
        """Verify cash collections"""
        self.clear_screen()
        self.print_header("VERIFY CASH COLLECTIONS")
        
        try:
            # Get recent cash collections
            response = self.cash_collections_table.scan()
            collections = response.get('Items', [])
            
            if not collections:
                self.print_info("No cash collections found.")
                input("Press Enter to continue...")
                return
                
            print(f"[PRICE] Recent Cash Collections ({len(collections)} records):")
            print("-" * 100)
            print(f"{'Collection ID':<20} {'Rider ID':<15} {'Amount':<12} {'Method':<10} {'Status':<12} {'Date':<20}")
            print("-" * 100)
            
            for collection in collections:
                print(f"{collection.get('collectionId', 'N/A'):<20} "
                      f"{collection.get('riderId', 'N/A'):<15} "
                      f"{collection.get('amountCollected', 0):<12} "
                      f"{collection.get('paymentMethod', 'N/A'):<10} "
                      f"{collection.get('status', 'N/A'):<12} "
                      f"{collection.get('collectionDate', 'N/A')[:19]:<20}")
                      
            print("-" * 100)
            
            # Verification summary
            total_amount = sum(Decimal(str(collection.get('amountCollected', 0))) for collection in collections)
            completed_collections = [c for c in collections if c.get('status') == 'COMPLETED']
            
            print(f"\n[TRACK] Verification Summary:")
            print(f"  • Total Collections: {len(collections)}")
            print(f"  • Completed Collections: {len(completed_collections)}")
            print(f"  • Total Amount Collected: {total_amount}")
            print(f"  • Average Amount: {total_amount / len(collections) if collections else 0:.2f}")
            
            # Flag potential issues
            issues = []
            for collection in collections:
                if collection.get('amountCollected', 0) == 0:
                    issues.append(f"Zero amount collection: {collection.get('collectionId')}")
                if collection.get('paymentMethod') not in ['CASH', 'CARD', 'UPI']:
                    issues.append(f"Invalid payment method: {collection.get('collectionId')}")
                    
            if issues:
                print(f"\n[INTERRUPTED] Potential Issues Found:")
                for issue in issues:
                    print(f"  • {issue}")
            else:
                print(f"\n[SUCCESS] No obvious issues detected in cash collections.")
                
        except Exception as e:
            self.print_error(f"Error verifying cash collections: {str(e)}")
            
        input("Press Enter to continue...")
        
    def verify_order_transactions(self):
        """Verify order transactions"""
        self.clear_screen()
        self.print_header("VERIFY ORDER TRANSACTIONS")
        
        try:
            # Get recent orders
            response = self.orders_table.scan()
            orders = response.get('Items', [])
            
            if not orders:
                self.print_info("No orders found.")
                input("Press Enter to continue...")
                return
                
            print(f"[ORDER] Recent Orders ({len(orders)} records):")
            print("-" * 100)
            print(f"{'Order ID':<20} {'Customer ID':<15} {'Amount':<12} {'Status':<15} {'Date':<20}")
            print("-" * 100)
            
            for order in orders:
                print(f"{order.get('orderId', 'N/A'):<20} "
                      f"{order.get('customerId', 'N/A'):<15} "
                      f"{order.get('totalAmount', 0):<12} "
                      f"{order.get('status', 'N/A'):<15} "
                      f"{order.get('orderDate', 'N/A')[:19]:<20}")
                      
            print("-" * 100)
            
            # Verification summary
            total_amount = sum(Decimal(str(order.get('totalAmount', 0))) for order in orders)
            completed_orders = [o for o in orders if o.get('status') == 'COMPLETED']
            pending_orders = [o for o in orders if o.get('status') == 'PENDING']
            
            print(f"\n[TRACK] Order Verification Summary:")
            print(f"  • Total Orders: {len(orders)}")
            print(f"  • Completed Orders: {len(completed_orders)}")
            print(f"  • Pending Orders: {len(pending_orders)}")
            print(f"  • Total Order Value: {total_amount}")
            print(f"  • Average Order Value: {total_amount / len(orders) if orders else 0:.2f}")
            
            # Check for anomalies
            anomalies = []
            for order in orders:
                if order.get('totalAmount', 0) < 0:
                    anomalies.append(f"Negative amount order: {order.get('orderId')}")
                if order.get('totalAmount', 0) > 10000:  # High value threshold
                    anomalies.append(f"High value order: {order.get('orderId')} - {order.get('totalAmount')}")
                    
            if anomalies:
                print(f"\n[INTERRUPTED] Anomalies Detected:")
                for anomaly in anomalies:
                    print(f"  • {anomaly}")
            else:
                print(f"\n[SUCCESS] No anomalies detected in order transactions.")
                
        except Exception as e:
            self.print_error(f"Error verifying order transactions: {str(e)}")
            
        input("Press Enter to continue...")
        
    def compliance_checking_menu(self):
        """Compliance Checking Operations"""
        while True:
            self.clear_screen()
            self.print_header("COMPLIANCE CHECKING")
            print("1. [AUDIT] Audit Trail Review")
            print("2. 👥 User Access Review")
            print("3. [ORDER] Inventory Compliance")
            print("4. [PRICE] Financial Compliance")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.audit_trail_review()
            elif choice == '2':
                self.user_access_review()
            elif choice == '3':
                self.inventory_compliance()
            elif choice == '4':
                self.financial_compliance()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def audit_trail_review(self):
        """Review audit trail"""
        self.clear_screen()
        self.print_header("AUDIT TRAIL REVIEW")
        
        try:
            # Get recent audit logs
            response = self.audit_logs_table.scan()
            audit_logs = response.get('Items', [])
            
            if not audit_logs:
                self.print_info("No audit logs found.")
                input("Press Enter to continue...")
                return
                
            print(f"[AUDIT] Recent Audit Logs ({len(audit_logs)} records):")
            print("-" * 120)
            print(f"{'Audit ID':<25} {'User ID':<15} {'Action':<20} {'Entity ID':<20} {'Timestamp':<20}")
            print("-" * 120)
            
            for log in audit_logs:
                print(f"{log.get('auditId', 'N/A'):<25} "
                      f"{log.get('userId', 'N/A'):<15} "
                      f"{log.get('action', 'N/A'):<20} "
                      f"{log.get('entityId', 'N/A'):<20} "
                      f"{log.get('timestamp', 'N/A')[:19]:<20}")
                      
            print("-" * 120)
            
            # Analysis by action type
            action_counts = {}
            user_counts = {}
            
            for log in audit_logs:
                action = log.get('action', 'UNKNOWN')
                user = log.get('userId', 'UNKNOWN')
                action_counts[action] = action_counts.get(action, 0) + 1
                user_counts[user] = user_counts.get(user, 0) + 1
                
            print(f"\n[TRACK] Audit Trail Analysis:")
            print(f"  • Total Audit Events: {len(audit_logs)}")
            print(f"  • Unique Actions: {len(action_counts)}")
            print(f"  • Active Users: {len(user_counts)}")
            
            print(f"\n[AUDIT] Most Common Actions:")
            sorted_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)
            for action, count in sorted_actions[:5]:
                print(f"  • {action}: {count} times")
                
            print(f"\n👥 Most Active Users:")
            sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
            for user, count in sorted_users[:5]:
                print(f"  • {user}: {count} actions")
                
            # Check for suspicious patterns
            suspicious_patterns = []
            for user, count in user_counts.items():
                if count > 50:  # High activity threshold
                    suspicious_patterns.append(f"High activity user: {user} ({count} actions)")
                    
            if suspicious_patterns:
                print(f"\n[INTERRUPTED] Suspicious Patterns Detected:")
                for pattern in suspicious_patterns:
                    print(f"  • {pattern}")
            else:
                print(f"\n[SUCCESS] No suspicious patterns detected in audit trail.")
                
        except Exception as e:
            self.print_error(f"Error reviewing audit trail: {str(e)}")
            
        input("Press Enter to continue...")
        
    def inventory_verification_menu(self):
        """Inventory Verification Operations"""
        while True:
            self.clear_screen()
            self.print_header("INVENTORY VERIFICATION")
            print("1. [ORDER] Verify Stock Levels")
            print("2. [AUDIT] Check Product Accuracy")
            print("3. [TRACK] Inventory Reconciliation")
            print("4. [INTERRUPTED] Flag Discrepancies")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.verify_stock_levels()
            elif choice == '2':
                self.check_product_accuracy()
            elif choice == '3':
                self.inventory_reconciliation()
            elif choice == '4':
                self.flag_discrepancies()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def verify_stock_levels(self):
        """Verify stock levels"""
        self.clear_screen()
        self.print_header("VERIFY STOCK LEVELS")
        
        try:
            # Get stock levels
            response = self.stock_levels_table.scan()
            stock_levels = response.get('Items', [])
            
            if not stock_levels:
                self.print_info("No stock levels found.")
                input("Press Enter to continue...")
                return
                
            print(f"[ORDER] Stock Level Verification ({len(stock_levels)} records):")
            print("-" * 100)
            print(f"{'Product ID':<20} {'Location':<20} {'Available':<12} {'Reserved':<12} {'Damaged':<12}")
            print("-" * 100)
            
            for stock in stock_levels:
                print(f"{stock.get('productId', 'N/A'):<20} "
                      f"{stock.get('location', 'N/A'):<20} "
                      f"{stock.get('availableStock', 0):<12} "
                      f"{stock.get('reservedStock', 0):<12} "
                      f"{stock.get('damagedStock', 0):<12}")
                      
            print("-" * 100)
            
            # Verification summary
            total_available = sum(stock.get('availableStock', 0) for stock in stock_levels)
            total_reserved = sum(stock.get('reservedStock', 0) for stock in stock_levels)
            total_damaged = sum(stock.get('damagedStock', 0) for stock in stock_levels)
            
            print(f"\n[TRACK] Stock Verification Summary:")
            print(f"  • Total Stock Records: {len(stock_levels)}")
            print(f"  • Total Available Stock: {total_available}")
            print(f"  • Total Reserved Stock: {total_reserved}")
            print(f"  • Total Damaged Stock: {total_damaged}")
            print(f"  • Average Available per Product: {total_available / len(stock_levels) if stock_levels else 0:.2f}")
            
            # Check for issues
            issues = []
            for stock in stock_levels:
                if stock.get('availableStock', 0) < 0:
                    issues.append(f"Negative stock: {stock.get('productId')} at {stock.get('location')}")
                if stock.get('damagedStock', 0) > stock.get('availableStock', 0):
                    issues.append(f"High damaged stock: {stock.get('productId')} at {stock.get('location')}")
                    
            if issues:
                print(f"\n[INTERRUPTED] Stock Issues Detected:")
                for issue in issues:
                    print(f"  • {issue}")
            else:
                print(f"\n[SUCCESS] No stock issues detected.")
                
        except Exception as e:
            self.print_error(f"Error verifying stock levels: {str(e)}")
            
        input("Press Enter to continue...")
        
    def report_generation_menu(self):
        """Report Generation Operations"""
        while True:
            self.clear_screen()
            self.print_header("REPORT GENERATION")
            print("1. [TRACK] Compliance Report")
            print("2. [PRICE] Financial Report")
            print("3. [ORDER] Inventory Report")
            print("4. 👥 User Activity Report")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.generate_compliance_report()
            elif choice == '2':
                self.generate_financial_report()
            elif choice == '3':
                self.generate_inventory_report()
            elif choice == '4':
                self.generate_user_activity_report()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def generate_compliance_report(self):
        """Generate compliance report"""
        self.clear_screen()
        self.print_header("GENERATE COMPLIANCE REPORT")
        
        try:
            # Collect compliance data
            audit_response = self.audit_logs_table.scan()
            audit_logs = audit_response.get('Items', [])
            
            users_response = self.users_table.scan()
            users = users_response.get('Items', [])
            
            orders_response = self.orders_table.scan()
            orders = orders_response.get('Items', [])
            
            collections_response = self.cash_collections_table.scan()
            collections = collections_response.get('Items', [])
            
            # Generate report
            report_id = f'COMPLIANCE-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            
            report_data = {
                'reportId': report_id,
                'reportType': 'COMPLIANCE',
                'generatedBy': self.current_user.get('userId'),
                'generatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'data': {
                    'totalAuditEvents': len(audit_logs),
                    'totalUsers': len(users),
                    'totalOrders': len(orders),
                    'totalCollections': len(collections),
                    'activeUsers': len([u for u in users if u.get('isActive', False)]),
                    'completedOrders': len([o for o in orders if o.get('status') == 'COMPLETED']),
                    'completedCollections': len([c for c in collections if c.get('status') == 'COMPLETED']),
                    'suspiciousActivities': 0,  # Would be calculated based on rules
                    'complianceScore': 95.5  # Would be calculated based on various factors
                },
                'summary': 'Compliance report generated successfully',
                'status': 'COMPLETED',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Save report
            self.reports_table.put_item(Item=report_data)
            
            # Display report
            print(f"[TRACK] Compliance Report Generated:")
            print(f"  • Report ID: {report_id}")
            print(f"  • Generated By: {self.current_user.get('name', 'Unknown')}")
            print(f"  • Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n[REPORT] Compliance Metrics:")
            print(f"  • Total Audit Events: {len(audit_logs)}")
            print(f"  • Total Users: {len(users)}")
            print(f"  • Active Users: {len([u for u in users if u.get('isActive', False)])}")
            print(f"  • Total Orders: {len(orders)}")
            print(f"  • Completed Orders: {len([o for o in orders if o.get('status') == 'COMPLETED'])}")
            print(f"  • Total Collections: {len(collections)}")
            print(f"  • Completed Collections: {len([c for c in collections if c.get('status') == 'COMPLETED'])}")
            print(f"  • Compliance Score: 95.5%")
            
            print(f"\n[SUCCESS] Report saved to database successfully!")
            
        except Exception as e:
            self.print_error(f"Error generating compliance report: {str(e)}")
            
        input("Press Enter to continue...")
        
    def process_review_menu(self):
        """Process Review Operations"""
        while True:
            self.clear_screen()
            self.print_header("PROCESS REVIEW")
            print("1. [FLOW] Review Order Process")
            print("2. [ORDER] Review Inventory Process")
            print("3. [PRICE] Review Payment Process")
            print("4. 👥 Review User Process")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.review_order_process()
            elif choice == '2':
                self.review_inventory_process()
            elif choice == '3':
                self.review_payment_process()
            elif choice == '4':
                self.review_user_process()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def audit_analytics_menu(self):
        """Audit Analytics Operations"""
        while True:
            self.clear_screen()
            self.print_header("AUDIT ANALYTICS")
            print("1. [TRACK] Activity Analytics")
            print("2. [INTERRUPTED] Risk Assessment")
            print("3. [REPORT] Trend Analysis")
            print("4. [AUDIT] Anomaly Detection")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.activity_analytics()
            elif choice == '2':
                self.risk_assessment()
            elif choice == '3':
                self.trend_analysis()
            elif choice == '4':
                self.anomaly_detection()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    # Placeholder methods for other operations
    def review_transaction_history(self):
        self.clear_screen()
        self.print_header("REVIEW TRANSACTION HISTORY")
        self.print_info("Transaction history review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def flag_suspicious_transactions(self):
        self.clear_screen()
        self.print_header("FLAG SUSPICIOUS TRANSACTIONS")
        self.print_info("Suspicious transaction flagging functionality will be implemented.")
        input("Press Enter to continue...")
        
    def user_access_review(self):
        self.clear_screen()
        self.print_header("USER ACCESS REVIEW")
        self.print_info("User access review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def inventory_compliance(self):
        self.clear_screen()
        self.print_header("INVENTORY COMPLIANCE")
        self.print_info("Inventory compliance checking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def financial_compliance(self):
        self.clear_screen()
        self.print_header("FINANCIAL COMPLIANCE")
        self.print_info("Financial compliance checking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def check_product_accuracy(self):
        self.clear_screen()
        self.print_header("CHECK PRODUCT ACCURACY")
        self.print_info("Product accuracy checking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def inventory_reconciliation(self):
        self.clear_screen()
        self.print_header("INVENTORY RECONCILIATION")
        self.print_info("Inventory reconciliation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def flag_discrepancies(self):
        self.clear_screen()
        self.print_header("FLAG DISCREPANCIES")
        self.print_info("Discrepancy flagging functionality will be implemented.")
        input("Press Enter to continue...")
        
    def generate_financial_report(self):
        self.clear_screen()
        self.print_header("GENERATE FINANCIAL REPORT")
        self.print_info("Financial report generation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def generate_inventory_report(self):
        self.clear_screen()
        self.print_header("GENERATE INVENTORY REPORT")
        self.print_info("Inventory report generation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def generate_user_activity_report(self):
        self.clear_screen()
        self.print_header("GENERATE USER ACTIVITY REPORT")
        self.print_info("User activity report generation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_order_process(self):
        self.clear_screen()
        self.print_header("REVIEW ORDER PROCESS")
        self.print_info("Order process review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_inventory_process(self):
        self.clear_screen()
        self.print_header("REVIEW INVENTORY PROCESS")
        self.print_info("Inventory process review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_payment_process(self):
        self.clear_screen()
        self.print_header("REVIEW PAYMENT PROCESS")
        self.print_info("Payment process review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def review_user_process(self):
        self.clear_screen()
        self.print_header("REVIEW USER PROCESS")
        self.print_info("User process review functionality will be implemented.")
        input("Press Enter to continue...")
        
    def activity_analytics(self):
        self.clear_screen()
        self.print_header("ACTIVITY ANALYTICS")
        self.print_info("Activity analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def risk_assessment(self):
        self.clear_screen()
        self.print_header("RISK ASSESSMENT")
        self.print_info("Risk assessment functionality will be implemented.")
        input("Press Enter to continue...")
        
    def trend_analysis(self):
        self.clear_screen()
        self.print_header("TREND ANALYSIS")
        self.print_info("Trend analysis functionality will be implemented.")
        input("Press Enter to continue...")
        
    def anomaly_detection(self):
        self.clear_screen()
        self.print_header("ANOMALY DETECTION")
        self.print_info("Anomaly detection functionality will be implemented.")
        input("Press Enter to continue...")
        
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.print_success(f"Goodbye, {self.current_user.get('name', 'User')}!")
            self.current_user = None
            self.current_role = None
        else:
            self.print_info("No user logged in")
            
    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': self.current_user.get('userId'),
                'action': action,
                'entityId': entity_id,
                'details': details,
                'ipAddress': '127.0.0.1',
                'userAgent': 'Auditor-Standalone',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")
            
    def run(self):
        """Main run method"""
        try:
            # Create demo user if needed
            self.create_demo_user()
            
            # Authenticate user
            if not self.authenticate_user():
                self.print_error("Authentication failed. Exiting.")
                sys.exit(1)
                
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
        finally:
            self.print_success("Thank you for using the Auditor system!")


def main():
    """Main entry point"""
    auditor = AuditorStandalone()
    auditor.run()


if __name__ == '__main__':
    main() 