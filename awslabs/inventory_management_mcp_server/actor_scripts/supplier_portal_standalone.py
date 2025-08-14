#!/usr/bin/env python3
# supplier_portal_standalone.py
"""
Supplier/Vendor Portal Standalone Script
Run this script in a separate terminal window for Supplier/Vendor operations.
Simulates external supplier portal interactions.
"""

import boto3
import sys
import getpass
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional


class SupplierPortalStandalone:
    """Standalone Supplier Portal with External Operations"""
    
    def __init__(self):
        self.region_name = 'ap-south-1'
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
        self.suppliers_table = self.dynamodb.Table('InventoryManagement-Suppliers')
        self.purchase_orders_table = self.dynamodb.Table('InventoryManagement-PurchaseOrders')
        self.products_table = self.dynamodb.Table('InventoryManagement-Products')
        self.audit_logs_table = self.dynamodb.Table('InventoryManagement-AuditLogs')
        self.notifications_table = self.dynamodb.Table('InventoryManagement-Notifications')
        
        self.current_supplier = None
        self.supplier_id = None
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"[SUPPLIER] {title}")
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
            
    def authenticate_supplier(self) -> bool:
        """Authenticate supplier login"""
        self.clear_screen()
        self.print_header("SUPPLIER PORTAL - LOGIN")
        
        if not self.test_aws_connection():
            return False
            
        print("\n[SECURE] Please enter your supplier credentials:")
        print("[NOTE] Demo credentials: supplier1 / supplier123")
        
        supplier_id = input("\n[SUPPLIER] Supplier ID: ").strip()
        password = getpass.getpass("[PASSWORD] Password: ").strip()
        
        if not supplier_id or not password:
            self.print_error("Supplier ID and password are required")
            return False
            
        supplier = self.authenticate_supplier_db(supplier_id, password)
        if supplier:
            self.current_supplier = supplier
            self.supplier_id = supplier_id
            self.print_success(f"Welcome, {supplier.get('name', supplier_id)}!")
            self.print_info(f"Supplier ID: {supplier_id}")
            self.print_info(f"Status: {supplier.get('status', 'Unknown')}")
            return True
        else:
            self.print_error("Invalid credentials or supplier not found.")
            return False
            
    def authenticate_supplier_db(self, supplier_id: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate supplier against DynamoDB Suppliers table"""
        try:
            # First try to find the supplier by scanning (since we don't know the exact key structure)
            response = self.suppliers_table.scan(
                FilterExpression='supplierId = :supplierId AND #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':supplierId': supplier_id,
                    ':status': 'ACTIVE'
                }
            )
            
            if response['Items']:
                supplier = response['Items'][0]
                # For demo purposes, check if password matches (in real system, this would be hashed)
                if self.verify_password(password, supplier.get('password', 'supplier123')):
                    return supplier
            return None
            
        except Exception as e:
            self.print_error(f"Authentication error: {str(e)}")
            return None
            
    def verify_password(self, input_password: str, stored_password: str) -> bool:
        """Verify password (simplified for demo)"""
        return input_password == stored_password
        
    def create_demo_supplier(self):
        """Create demo supplier if not exists"""
        try:
            demo_supplier = {
                'supplierId': 'supplier1',
                'status': 'ACTIVE',
                'name': 'ABC Suppliers Pvt Ltd',
                'email': 'orders@abcsuppliers.com',
                'phone': '+919876543216',
                'address': '123 Industrial Area, Mumbai, Maharashtra',
                'password': 'supplier123',
                'contactPerson': 'Rajesh Kumar',
                'contactPhone': '+919876543217',
                'paymentTerms': 'NET30',
                'rating': Decimal('4.5'),
                'specialization': 'Electronics and Gadgets',
                'deliveryTime': '2-3 business days',
                'minimumOrder': 1000,
                'isActive': True,
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'updatedAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            # Check if supplier already exists
            response = self.suppliers_table.scan(
                FilterExpression='supplierId = :supplierId',
                ExpressionAttributeValues={':supplierId': 'supplier1'}
            )
            
            if not response['Items']:
                self.suppliers_table.put_item(Item=demo_supplier)
                self.print_success("Demo Supplier created!")
                self.print_info("Supplier ID: supplier1")
                self.print_info("Password: supplier123")
            else:
                self.print_info("Demo supplier already exists.")
                
        except Exception as e:
            self.print_error(f"Error creating demo supplier: {str(e)}")
            
    def show_main_menu(self):
        """Show Supplier Portal main menu"""
        while True:
            self.clear_screen()
            self.print_header("SUPPLIER PORTAL DASHBOARD")
            
            if self.current_supplier:
                print(f"[SUPPLIER] Supplier: {self.current_supplier.get('name', 'Unknown')}")
                print(f"[ID] Supplier ID: {self.supplier_id}")
                print(f"[EMAIL] Email: {self.current_supplier.get('email', 'Unknown')}")
                print(f"[DATE] Login Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n[CLIPBOARD] Available Operations:")
            print("1. [CLIPBOARD] Order Management")
            print("2. [ORDER] Inventory Updates")
            print("3. [DELIVERY] Delivery Coordination")
            print("4. [PRICE] Invoice Management")
            print("5. [TRACK] Performance Review")
            print("6. [SECURE] Logout")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select operation (0-6): ").strip()
            
            if choice == '1':
                self.order_management_menu()
            elif choice == '2':
                self.inventory_updates_menu()
            elif choice == '3':
                self.delivery_coordination_menu()
            elif choice == '4':
                self.invoice_management_menu()
            elif choice == '5':
                self.performance_review_menu()
            elif choice == '6':
                self.logout()
                break
            elif choice == '0':
                self.print_success("Thank you for using the Supplier Portal!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def order_management_menu(self):
        """Order Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("ORDER MANAGEMENT")
            print("1. [CLIPBOARD] View Purchase Orders")
            print("2. [SUCCESS] Confirm Order Acceptance")
            print("3. [GENERATE] Update Order Status")
            print("4. [TRACK] Order History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.view_purchase_orders()
            elif choice == '2':
                self.confirm_order_acceptance()
            elif choice == '3':
                self.update_order_status()
            elif choice == '4':
                self.order_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def view_purchase_orders(self):
        """View purchase orders for this supplier"""
        self.clear_screen()
        self.print_header("VIEW PURCHASE ORDERS")
        
        try:
            # Get purchase orders for this supplier
            response = self.purchase_orders_table.scan()
            purchase_orders = response.get('Items', [])
            
            supplier_orders = [po for po in purchase_orders if po.get('supplierId') == self.supplier_id]
            
            if not supplier_orders:
                self.print_info("No purchase orders found for your supplier.")
                input("Press Enter to continue...")
                return
                
            print(f"[CLIPBOARD] Your Purchase Orders ({len(supplier_orders)} orders):")
            print("-" * 100)
            print(f"{'PO ID':<20} {'Order Date':<15} {'Total Amount':<15} {'Status':<15} {'Delivery Date':<15}")
            print("-" * 100)
            
            for po in supplier_orders:
                print(f"{po.get('poId', 'N/A'):<20} "
                      f"{po.get('orderDate', 'N/A')[:10]:<15} "
                      f"{po.get('totalAmount', 0):<15} "
                      f"{po.get('status', 'N/A'):<15} "
                      f"{po.get('expectedDeliveryDate', 'N/A')[:10]:<15}")
                      
            print("-" * 100)
            
            # Status breakdown
            status_counts = {}
            for po in supplier_orders:
                status = po.get('status', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
                
            print(f"\n[TRACK] Order Status Breakdown:")
            for status, count in status_counts.items():
                print(f"  • {status}: {count} orders")
                
            # Show pending orders
            pending_orders = [po for po in supplier_orders if po.get('status') == 'PENDING']
            if pending_orders:
                print(f"\n[INTERRUPTED] Pending Orders Requiring Action:")
                for po in pending_orders:
                    print(f"  • {po.get('poId')} - Amount: {po.get('totalAmount')}")
                    
        except Exception as e:
            self.print_error(f"Error viewing purchase orders: {str(e)}")
            
        input("Press Enter to continue...")
        
    def confirm_order_acceptance(self):
        """Confirm order acceptance"""
        self.clear_screen()
        self.print_header("CONFIRM ORDER ACCEPTANCE")
        
        try:
            # Get pending orders for this supplier
            response = self.purchase_orders_table.scan()
            purchase_orders = response.get('Items', [])
            
            pending_orders = [po for po in purchase_orders 
                            if po.get('supplierId') == self.supplier_id 
                            and po.get('status') == 'PENDING']
            
            if not pending_orders:
                self.print_info("No pending orders found for acceptance.")
                input("Press Enter to continue...")
                return
                
            print("[CLIPBOARD] Pending Orders for Acceptance:")
            for i, po in enumerate(pending_orders, 1):
                print(f"{i}. {po.get('poId')} - Amount: {po.get('totalAmount')} - Date: {po.get('orderDate', 'N/A')[:10]}")
                
            order_choice = input("\n[TARGET] Select order number to accept: ").strip()
            
            try:
                order_index = int(order_choice) - 1
                if 0 <= order_index < len(pending_orders):
                    selected_po = pending_orders[order_index]
                    po_id = selected_po['poId']
                    
                    print(f"\n[CLIPBOARD] Order Details:")
                    print(f"  • PO ID: {po_id}")
                    print(f"  • Amount: {selected_po.get('totalAmount')}")
                    print(f"  • Order Date: {selected_po.get('orderDate', 'N/A')[:10]}")
                    print(f"  • Expected Delivery: {selected_po.get('expectedDeliveryDate', 'N/A')[:10]}")
                    
                    # Confirm acceptance
                    confirm = input("\n[CONFIRM] Confirm acceptance of this order? (yes/no): ").strip().lower()
                    
                    if confirm == 'yes':
                        # Update order status
                        self.purchase_orders_table.update_item(
                            Key={'poId': po_id, 'supplierId': self.supplier_id},
                            UpdateExpression='SET #status = :status, acceptedAt = :accepted, updatedAt = :updated',
                            ExpressionAttributeNames={
                                '#status': 'status'
                            },
                            ExpressionAttributeValues={
                                ':status': 'ACCEPTED',
                                ':accepted': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                                ':updated': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                            }
                        )
                        
                        # Log audit
                        self.log_audit('PO_ACCEPTED', po_id, f"Purchase order {po_id} accepted by supplier {self.supplier_id}")
                        
                        self.print_success(f"Purchase order {po_id} accepted successfully!")
                        self.print_info("Status updated to ACCEPTED")
                        
                    else:
                        self.print_info("Order acceptance cancelled.")
                else:
                    self.print_error("Invalid order selection.")
            except ValueError:
                self.print_error("Invalid order number.")
                
        except Exception as e:
            self.print_error(f"Error accepting order: {str(e)}")
            
        input("Press Enter to continue...")
        
    def inventory_updates_menu(self):
        """Inventory Updates Operations"""
        while True:
            self.clear_screen()
            self.print_header("INVENTORY UPDATES")
            print("1. [ORDER] Update Stock Availability")
            print("2. [CATEGORY] Update Product Catalog")
            print("3. [PRICE] Update Pricing")
            print("4. [TRACK] Inventory Reports")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.update_stock_availability()
            elif choice == '2':
                self.update_product_catalog()
            elif choice == '3':
                self.update_pricing()
            elif choice == '4':
                self.inventory_reports()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def delivery_coordination_menu(self):
        """Delivery Coordination Operations"""
        while True:
            self.clear_screen()
            self.print_header("DELIVERY COORDINATION")
            print("1. [DATE] Schedule Deliveries")
            print("2. [ADDRESS] Provide Tracking Information")
            print("3. [TRACK] Update Delivery Status")
            print("4. [CLIPBOARD] Delivery History")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.schedule_deliveries()
            elif choice == '2':
                self.provide_tracking_information()
            elif choice == '3':
                self.update_delivery_status()
            elif choice == '4':
                self.delivery_history()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def invoice_management_menu(self):
        """Invoice Management Operations"""
        while True:
            self.clear_screen()
            self.print_header("INVOICE MANAGEMENT")
            print("1. 📄 Submit Invoices")
            print("2. [PRICE] Track Payment Status")
            print("3. [TRACK] Payment History")
            print("4. [CLIPBOARD] Credit Management")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.submit_invoices()
            elif choice == '2':
                self.track_payment_status()
            elif choice == '3':
                self.payment_history()
            elif choice == '4':
                self.credit_management()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def performance_review_menu(self):
        """Performance Review Operations"""
        while True:
            self.clear_screen()
            self.print_header("PERFORMANCE REVIEW")
            print("1. [TRACK] View Performance Metrics")
            print("2. [GENERATE] Respond to Feedback")
            print("3. [CLIPBOARD] Update Compliance Documents")
            print("4. [REPORT] Performance Analytics")
            print("5. [BACK] Back to Main Menu")
            
            choice = input("\n[TARGET] Select operation (1-5): ").strip()
            
            if choice == '1':
                self.view_performance_metrics()
            elif choice == '2':
                self.respond_to_feedback()
            elif choice == '3':
                self.update_compliance_documents()
            elif choice == '4':
                self.performance_analytics()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice. Please try again.")
                input("Press Enter to continue...")
                
    # Placeholder methods for other operations
    def update_order_status(self):
        self.clear_screen()
        self.print_header("UPDATE ORDER STATUS")
        self.print_info("Order status update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def order_history(self):
        self.clear_screen()
        self.print_header("ORDER HISTORY")
        self.print_info("Order history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_stock_availability(self):
        self.clear_screen()
        self.print_header("UPDATE STOCK AVAILABILITY")
        self.print_info("Stock availability update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_product_catalog(self):
        self.clear_screen()
        self.print_header("UPDATE PRODUCT CATALOG")
        self.print_info("Product catalog update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_pricing(self):
        self.clear_screen()
        self.print_header("UPDATE PRICING")
        self.print_info("Pricing update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def inventory_reports(self):
        self.clear_screen()
        self.print_header("INVENTORY REPORTS")
        self.print_info("Inventory report generation functionality will be implemented.")
        input("Press Enter to continue...")
        
    def schedule_deliveries(self):
        self.clear_screen()
        self.print_header("SCHEDULE DELIVERIES")
        self.print_info("Delivery scheduling functionality will be implemented.")
        input("Press Enter to continue...")
        
    def provide_tracking_information(self):
        self.clear_screen()
        self.print_header("PROVIDE TRACKING INFORMATION")
        self.print_info("Tracking information provision functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_delivery_status(self):
        self.clear_screen()
        self.print_header("UPDATE DELIVERY STATUS")
        self.print_info("Delivery status update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def delivery_history(self):
        self.clear_screen()
        self.print_header("DELIVERY HISTORY")
        self.print_info("Delivery history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def submit_invoices(self):
        self.clear_screen()
        self.print_header("SUBMIT INVOICES")
        self.print_info("Invoice submission functionality will be implemented.")
        input("Press Enter to continue...")
        
    def track_payment_status(self):
        self.clear_screen()
        self.print_header("TRACK PAYMENT STATUS")
        self.print_info("Payment status tracking functionality will be implemented.")
        input("Press Enter to continue...")
        
    def payment_history(self):
        self.clear_screen()
        self.print_header("PAYMENT HISTORY")
        self.print_info("Payment history viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def credit_management(self):
        self.clear_screen()
        self.print_header("CREDIT MANAGEMENT")
        self.print_info("Credit management functionality will be implemented.")
        input("Press Enter to continue...")
        
    def view_performance_metrics(self):
        self.clear_screen()
        self.print_header("VIEW PERFORMANCE METRICS")
        self.print_info("Performance metrics viewing functionality will be implemented.")
        input("Press Enter to continue...")
        
    def respond_to_feedback(self):
        self.clear_screen()
        self.print_header("RESPOND TO FEEDBACK")
        self.print_info("Feedback response functionality will be implemented.")
        input("Press Enter to continue...")
        
    def update_compliance_documents(self):
        self.clear_screen()
        self.print_header("UPDATE COMPLIANCE DOCUMENTS")
        self.print_info("Compliance document update functionality will be implemented.")
        input("Press Enter to continue...")
        
    def performance_analytics(self):
        self.clear_screen()
        self.print_header("PERFORMANCE ANALYTICS")
        self.print_info("Performance analytics functionality will be implemented.")
        input("Press Enter to continue...")
        
    def logout(self):
        """Logout current supplier"""
        if self.current_supplier:
            self.print_success(f"Goodbye, {self.current_supplier.get('name', 'Supplier')}!")
            self.current_supplier = None
            self.supplier_id = None
        else:
            self.print_info("No supplier logged in")
            
    def log_audit(self, action: str, entity_id: str, details: str):
        """Log audit trail"""
        try:
            audit_item = {
                'auditId': f'AUDIT-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'userId': f'SUPPLIER_{self.supplier_id}',
                'action': action,
                'entityId': entity_id,
                'details': details,
                'ipAddress': '127.0.0.1',
                'userAgent': 'SupplierPortal-Standalone',
                'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            self.audit_logs_table.put_item(Item=audit_item)
            
        except Exception as e:
            self.print_error(f"Error logging audit: {str(e)}")
            
    def run(self):
        """Main run method"""
        try:
            # Create demo supplier if needed
            self.create_demo_supplier()
            
            # Authenticate supplier
            if not self.authenticate_supplier():
                self.print_error("Authentication failed. Exiting.")
                sys.exit(1)
                
            # Show main menu
            self.show_main_menu()
            
        except KeyboardInterrupt:
            self.print_info("\n[INTERRUPTED]  System interrupted by user")
        except Exception as e:
            self.print_error(f"Unexpected error: {str(e)}")
        finally:
            self.print_success("Thank you for using the Supplier Portal!")


def main():
    """Main entry point"""
    supplier_portal = SupplierPortalStandalone()
    supplier_portal.run()


if __name__ == '__main__':
    main() 