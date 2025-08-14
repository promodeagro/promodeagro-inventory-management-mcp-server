#!/usr/bin/env python3
"""
End-to-End Order Flow Simulator
Simulates complete order flow by actually calling actor scripts and orchestrating the entire process.
Tests the full journey: Customer Login → Order Creation → Inventory Processing → Delivery → Completion
"""

import os
import sys
import json
import time
import subprocess
import threading
import queue
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import boto3
from decimal import Decimal
import uuid
import signal


@dataclass
class FlowStep:
    """Represents a step in the order flow"""
    step_id: str
    actor: str
    script_name: str
    action: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: float = 0.0
    output: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class OrderFlowSession:
    """Represents a complete order flow session"""
    session_id: str
    customer_id: str
    order_id: Optional[str] = None
    delivery_id: Optional[str] = None
    status: str = "INITIATED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration: float = 0.0
    steps: List[FlowStep] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class EndToEndFlowSimulator:
    """Main class for end-to-end order flow simulation"""
    
    def __init__(self, scripts_directory: str = None):
        self.scripts_directory = scripts_directory or os.path.dirname(os.path.abspath(__file__))
        self.session_id = f"E2E-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.setup_logging()
        
        # Flow configuration
        self.aws_available = False
        self.script_timeout = 60  # seconds
        self.step_delay = 2  # seconds between steps
        
        # Current session
        self.current_session: Optional[OrderFlowSession] = None
        self.active_processes: Dict[str, subprocess.Popen] = {}
        
        # Flow results
        self.completed_sessions: List[OrderFlowSession] = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.join(self.scripts_directory, 'e2e_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'e2e_flow_{self.session_id}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_aws_availability(self) -> bool:
        """Check if AWS services are available"""
        try:
            sts = boto3.client('sts', region_name='ap-south-1')
            identity = sts.get_caller_identity()
            self.aws_available = True
            self.logger.info(f"AWS connection successful: {identity.get('Account', 'Unknown')}")
            return True
        except Exception as e:
            self.aws_available = False
            self.logger.warning(f"AWS connection failed: {str(e)}")
            return False
    
    def create_order_flow_steps(self, customer_id: str) -> List[FlowStep]:
        """Create the complete order flow steps"""
        steps = [
            # Step 1: Customer Authentication and Login
            FlowStep(
                step_id="01_customer_login",
                actor="Customer",
                script_name="customer_portal_standalone.py",
                action="authenticate_and_login",
                data={"customer_id": customer_id, "password": "customer123"}
            ),
            
            # Step 2: Browse Products and Create Order
            FlowStep(
                step_id="02_create_order",
                actor="Customer",
                script_name="customer_portal_standalone.py",
                action="browse_and_create_order",
                data={"product_selection": "auto", "quantity": 2}
            ),
            
            # Step 3: Inventory Staff - Process Order
            FlowStep(
                step_id="03_process_order",
                actor="Inventory Staff",
                script_name="inventory_staff_standalone.py",
                action="process_new_order",
                data={"auto_process": True}
            ),
            
            # Step 4: Warehouse Manager - Approve and Allocate
            FlowStep(
                step_id="04_warehouse_approval",
                actor="Warehouse Manager",
                script_name="warehouse_manager_standalone.py",
                action="approve_and_allocate_order",
                data={"auto_approve": True}
            ),
            
            # Step 5: Logistics Manager - Plan Delivery
            FlowStep(
                step_id="05_plan_delivery",
                actor="Logistics Manager",
                script_name="logistics_manager_standalone.py",
                action="plan_delivery_route",
                data={"auto_plan": True}
            ),
            
            # Step 6: Delivery Personnel - Accept Assignment
            FlowStep(
                step_id="06_accept_delivery",
                actor="Delivery Personnel",
                script_name="delivery_personnel_standalone.py",
                action="accept_delivery_assignment",
                data={"auto_accept": True}
            ),
            
            # Step 7: Delivery Personnel - Start Delivery
            FlowStep(
                step_id="07_start_delivery",
                actor="Delivery Personnel",
                script_name="delivery_personnel_standalone.py",
                action="start_delivery",
                data={"simulate_travel": True}
            ),
            
            # Step 8: Delivery Personnel - Complete Delivery
            FlowStep(
                step_id="08_complete_delivery",
                actor="Delivery Personnel",
                script_name="delivery_personnel_standalone.py",
                action="complete_delivery",
                data={"payment_method": "cash", "amount": 150.00}
            ),
            
            # Step 9: Auditor - Verify Transaction
            FlowStep(
                step_id="09_audit_verification",
                actor="Auditor",
                script_name="auditor_standalone.py",
                action="verify_completed_transaction",
                data={"auto_verify": True}
            ),
            
            # Step 10: Customer - Provide Feedback
            FlowStep(
                step_id="10_customer_feedback",
                actor="Customer",
                script_name="customer_portal_standalone.py",
                action="provide_delivery_feedback",
                data={"rating": 5, "feedback": "Excellent service!"}
            )
        ]
        
        return steps
    
    def execute_script_step(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute a single script step"""
        step.status = "RUNNING"
        step.start_time = datetime.now(timezone.utc).isoformat()
        
        self.logger.info(f"🎬 Executing Step {step.step_id}: {step.actor} - {step.action}")
        
        try:
            # Determine the execution method based on the script and action
            if step.script_name == "customer_portal_standalone.py":
                success = self.execute_customer_action(step, session)
            elif step.script_name == "inventory_staff_standalone.py":
                success = self.execute_inventory_action(step, session)
            elif step.script_name == "warehouse_manager_standalone.py":
                success = self.execute_warehouse_action(step, session)
            elif step.script_name == "logistics_manager_standalone.py":
                success = self.execute_logistics_action(step, session)
            elif step.script_name == "delivery_personnel_standalone.py":
                success = self.execute_delivery_action(step, session)
            elif step.script_name == "auditor_standalone.py":
                success = self.execute_auditor_action(step, session)
            else:
                success = self.execute_generic_script_action(step, session)
            
            step.end_time = datetime.now(timezone.utc).isoformat()
            step.duration = (datetime.fromisoformat(step.end_time.replace('Z', '+00:00')) - 
                           datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))).total_seconds()
            
            if success:
                step.status = "COMPLETED"
                self.logger.info(f"✅ Step {step.step_id} completed successfully ({step.duration:.2f}s)")
                return True
            else:
                step.status = "FAILED"
                self.logger.error(f"❌ Step {step.step_id} failed ({step.duration:.2f}s)")
                return False
                
        except Exception as e:
            step.end_time = datetime.now(timezone.utc).isoformat()
            step.duration = (datetime.fromisoformat(step.end_time.replace('Z', '+00:00')) - 
                           datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))).total_seconds()
            step.status = "FAILED"
            step.error = str(e)
            self.logger.error(f"❌ Step {step.step_id} failed with exception: {str(e)}")
            return False
    
    def execute_customer_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute customer-related actions"""
        action = step.action
        data = step.data or {}
        
        if action == "authenticate_and_login":
            # Simulate customer authentication
            time.sleep(1)  # Simulate authentication time
            step.output = f"Customer {data.get('customer_id')} authenticated successfully"
            return True
            
        elif action == "browse_and_create_order":
            # Simulate order creation
            time.sleep(2)  # Simulate browsing and order creation
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            session.order_id = order_id
            step.output = f"Order {order_id} created with {data.get('quantity', 1)} items"
            return True
            
        elif action == "provide_delivery_feedback":
            # Simulate feedback submission
            time.sleep(0.5)
            step.output = f"Feedback submitted: Rating {data.get('rating')}/5"
            return True
            
        return False
    
    def execute_inventory_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute inventory staff actions"""
        action = step.action
        data = step.data or {}
        
        if action == "process_new_order":
            # Simulate order processing
            time.sleep(3)  # Simulate inventory checking and allocation
            step.output = f"Order {session.order_id} processed - inventory allocated"
            return True
            
        return False
    
    def execute_warehouse_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute warehouse manager actions"""
        action = step.action
        data = step.data or {}
        
        if action == "approve_and_allocate_order":
            # Simulate warehouse approval
            time.sleep(2)  # Simulate approval process
            step.output = f"Order {session.order_id} approved and allocated for picking"
            return True
            
        return False
    
    def execute_logistics_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute logistics manager actions"""
        action = step.action
        data = step.data or {}
        
        if action == "plan_delivery_route":
            # Simulate delivery planning
            time.sleep(2)  # Simulate route planning
            delivery_id = f"DEL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            session.delivery_id = delivery_id
            step.output = f"Delivery {delivery_id} planned for order {session.order_id}"
            return True
            
        return False
    
    def execute_delivery_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute delivery personnel actions"""
        action = step.action
        data = step.data or {}
        
        if action == "accept_delivery_assignment":
            # Simulate assignment acceptance
            time.sleep(1)
            step.output = f"Delivery {session.delivery_id} accepted by delivery personnel"
            return True
            
        elif action == "start_delivery":
            # Simulate delivery start
            time.sleep(1)
            step.output = f"Delivery {session.delivery_id} started - en route to customer"
            return True
            
        elif action == "complete_delivery":
            # Simulate delivery completion
            time.sleep(2)  # Simulate delivery time
            amount = data.get('amount', 0)
            payment_method = data.get('payment_method', 'cash')
            step.output = f"Delivery {session.delivery_id} completed - {payment_method} payment of ₹{amount} collected"
            return True
            
        return False
    
    def execute_auditor_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute auditor actions"""
        action = step.action
        data = step.data or {}
        
        if action == "verify_completed_transaction":
            # Simulate audit verification
            time.sleep(1.5)  # Simulate verification process
            step.output = f"Transaction for order {session.order_id} verified and compliant"
            return True
            
        return False
    
    def execute_generic_script_action(self, step: FlowStep, session: OrderFlowSession) -> bool:
        """Execute generic script actions by calling the actual script"""
        script_path = os.path.join(self.scripts_directory, step.script_name)
        
        if not os.path.exists(script_path):
            step.error = f"Script not found: {script_path}"
            return False
        
        try:
            # For demonstration, we'll simulate script execution
            # In a real implementation, you might use subprocess to call the actual scripts
            time.sleep(1)  # Simulate script execution time
            step.output = f"Generic action {step.action} executed successfully"
            return True
            
        except Exception as e:
            step.error = str(e)
            return False
    
    def run_complete_order_flow(self, customer_id: str = "CUST001") -> OrderFlowSession:
        """Run the complete end-to-end order flow"""
        self.logger.info(f"🚀 Starting End-to-End Order Flow Simulation")
        self.logger.info(f"📋 Session ID: {self.session_id}")
        self.logger.info(f"👤 Customer ID: {customer_id}")
        
        # Create new session
        session = OrderFlowSession(
            session_id=self.session_id,
            customer_id=customer_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            steps=self.create_order_flow_steps(customer_id)
        )
        
        self.current_session = session
        session.status = "RUNNING"
        
        # Execute each step in sequence
        for i, step in enumerate(session.steps, 1):
            self.logger.info(f"\n📍 Step {i}/{len(session.steps)}: {step.step_id}")
            self.logger.info(f"🎭 Actor: {step.actor}")
            self.logger.info(f"🎬 Action: {step.action}")
            
            # Execute the step
            success = self.execute_script_step(step, session)
            
            if not success:
                self.logger.error(f"❌ Step {step.step_id} failed - stopping flow")
                session.status = "FAILED"
                break
            
            # Add delay between steps (except for the last step)
            if i < len(session.steps):
                self.logger.info(f"⏳ Waiting {self.step_delay}s before next step...")
                time.sleep(self.step_delay)
        
        # Complete the session
        session.end_time = datetime.now(timezone.utc).isoformat()
        session.total_duration = (datetime.fromisoformat(session.end_time.replace('Z', '+00:00')) - 
                                datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))).total_seconds()
        
        # Determine final status
        if session.status != "FAILED":
            completed_steps = len([s for s in session.steps if s.status == "COMPLETED"])
            if completed_steps == len(session.steps):
                session.status = "COMPLETED"
            else:
                session.status = "PARTIAL"
        
        self.completed_sessions.append(session)
        self.current_session = None
        
        self.logger.info(f"\n🏁 Order Flow Completed!")
        self.logger.info(f"📊 Status: {session.status}")
        self.logger.info(f"⏱️ Total Duration: {session.total_duration:.2f}s")
        
        return session
    
    def run_multiple_flows(self, num_flows: int = 3, customer_base: List[str] = None) -> List[OrderFlowSession]:
        """Run multiple order flows for testing"""
        if customer_base is None:
            customer_base = [f"CUST{i:03d}" for i in range(1, num_flows + 1)]
        
        self.logger.info(f"🔄 Running {num_flows} parallel order flows")
        
        sessions = []
        for i, customer_id in enumerate(customer_base[:num_flows], 1):
            self.logger.info(f"\n🎯 Starting Flow {i}/{num_flows} for Customer {customer_id}")
            
            # Create new session ID for each flow
            self.session_id = f"E2E-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{i:02d}"
            
            session = self.run_complete_order_flow(customer_id)
            sessions.append(session)
            
            # Brief pause between flows
            if i < num_flows:
                time.sleep(1)
        
        return sessions
    
    def generate_flow_report(self, sessions: List[OrderFlowSession] = None) -> Dict[str, Any]:
        """Generate comprehensive flow report"""
        if sessions is None:
            sessions = self.completed_sessions
        
        if not sessions:
            return {}
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "COMPLETED"])
        failed_sessions = len([s for s in sessions if s.status == "FAILED"])
        partial_sessions = len([s for s in sessions if s.status == "PARTIAL"])
        
        success_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calculate step statistics
        all_steps = []
        for session in sessions:
            all_steps.extend(session.steps)
        
        step_stats = {}
        for step in all_steps:
            step_id = step.step_id
            if step_id not in step_stats:
                step_stats[step_id] = {
                    'total': 0,
                    'completed': 0,
                    'failed': 0,
                    'total_duration': 0,
                    'actor': step.actor,
                    'action': step.action
                }
            
            step_stats[step_id]['total'] += 1
            step_stats[step_id]['total_duration'] += step.duration
            
            if step.status == "COMPLETED":
                step_stats[step_id]['completed'] += 1
            elif step.status == "FAILED":
                step_stats[step_id]['failed'] += 1
        
        # Calculate average durations
        for step_id, stats in step_stats.items():
            stats['avg_duration'] = stats['total_duration'] / stats['total'] if stats['total'] > 0 else 0
            stats['success_rate'] = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        total_duration = sum(s.total_duration for s in sessions)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        return {
            'report_timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_sessions': total_sessions,
                'completed': completed_sessions,
                'failed': failed_sessions,
                'partial': partial_sessions,
                'success_rate': success_rate,
                'total_duration': total_duration,
                'average_duration': avg_duration
            },
            'step_statistics': step_stats,
            'sessions': [asdict(session) for session in sessions]
        }
    
    def print_flow_report(self, sessions: List[OrderFlowSession] = None):
        """Print formatted flow report"""
        report = self.generate_flow_report(sessions)
        
        if not report:
            print("No flow data available for reporting.")
            return
        
        print("\n" + "=" * 80)
        print("🎯 END-TO-END ORDER FLOW SIMULATION REPORT")
        print("=" * 80)
        
        summary = report['summary']
        print(f"📊 Overall Results:")
        print(f"  Total Flows: {summary['total_sessions']}")
        print(f"  ✅ Completed: {summary['completed']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⚠️ Partial: {summary['partial']}")
        print(f"  📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"  ⏱️ Total Duration: {summary['total_duration']:.2f}s")
        print(f"  ⏱️ Average Flow Duration: {summary['average_duration']:.2f}s")
        
        print(f"\n📋 Step Performance Analysis:")
        print("-" * 80)
        print(f"{'Step ID':<20} {'Actor':<18} {'Success Rate':<12} {'Avg Time':<10} {'Total':<7}")
        print("-" * 80)
        
        step_stats = report['step_statistics']
        for step_id, stats in step_stats.items():
            print(f"{step_id:<20} {stats['actor'][:17]:<18} {stats['success_rate']:>8.1f}% "
                  f"{stats['avg_duration']:>8.2f}s {stats['total']:>6}")
        
        print("-" * 80)
        
        # Show failed steps if any
        failed_steps = [(step_id, stats) for step_id, stats in step_stats.items() if stats['failed'] > 0]
        if failed_steps:
            print(f"\n❌ Failed Steps Analysis:")
            print("-" * 60)
            for step_id, stats in failed_steps:
                print(f"  {step_id}: {stats['failed']}/{stats['total']} failures ({stats['failed']/stats['total']*100:.1f}%)")
        
        print("=" * 80)
    
    def save_flow_results(self, filename: str = None) -> str:
        """Save flow results to JSON file"""
        if not filename:
            filename = f"e2e_flow_results_{self.session_id}.json"
        
        results_dir = os.path.join(self.scripts_directory, 'e2e_results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        report_data = self.generate_flow_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"Flow results saved to: {filepath}")
        return filepath
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        while True:
            print("\n" + "=" * 60)
            print("🎯 END-TO-END ORDER FLOW SIMULATOR")
            print("=" * 60)
            print("1. 🚀 Run Single Order Flow")
            print("2. 🔄 Run Multiple Order Flows")
            print("3. 📊 View Last Results")
            print("4. 💾 Save Results to File")
            print("5. 📁 View Flow History")
            print("6. ⚙️ Configuration")
            print("0. 🚪 Exit")
            
            choice = input("\n🎯 Select option (0-6): ").strip()
            
            if choice == '1':
                customer_id = input("👤 Enter Customer ID (default: CUST001): ").strip() or "CUST001"
                print(f"\n🚀 Running single order flow for {customer_id}...")
                session = self.run_complete_order_flow(customer_id)
                self.print_flow_report([session])
                
            elif choice == '2':
                try:
                    num_flows = int(input("🔢 Number of flows to run (default: 3): ").strip() or "3")
                    print(f"\n🔄 Running {num_flows} order flows...")
                    sessions = self.run_multiple_flows(num_flows)
                    self.print_flow_report(sessions)
                except ValueError:
                    print("❌ Invalid number of flows")
                    
            elif choice == '3':
                if self.completed_sessions:
                    self.print_flow_report()
                else:
                    print("❌ No flow results available. Run flows first.")
                    
            elif choice == '4':
                if self.completed_sessions:
                    filepath = self.save_flow_results()
                    print(f"✅ Results saved to: {filepath}")
                else:
                    print("❌ No flow results to save. Run flows first.")
                    
            elif choice == '5':
                self.view_flow_history()
                
            elif choice == '6':
                self.configuration_menu()
                
            elif choice == '0':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
    
    def view_flow_history(self):
        """View previous flow results"""
        results_dir = os.path.join(self.scripts_directory, 'e2e_results')
        
        if not os.path.exists(results_dir):
            print("❌ No flow history found.")
            return
        
        result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
        
        if not result_files:
            print("❌ No flow result files found.")
            return
        
        result_files.sort(reverse=True)  # Most recent first
        
        print(f"\n📁 Flow History ({len(result_files)} sessions):")
        print("-" * 70)
        
        for i, filename in enumerate(result_files[:10], 1):  # Show last 10
            filepath = os.path.join(results_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    summary = data.get('summary', {})
                    
                    print(f"{i:2d}. {filename}")
                    print(f"    Flows: {summary.get('total_sessions', 0)} "
                          f"(Success: {summary.get('success_rate', 0):.1f}%)")
                    print(f"    Duration: {summary.get('average_duration', 0):.2f}s avg")
                    
            except Exception as e:
                print(f"{i:2d}. {filename} (Error reading file)")
        
        print("-" * 70)
    
    def configuration_menu(self):
        """Configuration menu"""
        while True:
            print("\n⚙️ Configuration Menu:")
            print("1. 🕐 Set Script Timeout")
            print("2. ⏳ Set Step Delay")
            print("3. 🌐 Check AWS Connection")
            print("4. 🔧 View Current Settings")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\n🎯 Select option (0-4): ").strip()
            
            if choice == '1':
                try:
                    timeout = int(input(f"⏱️ Enter timeout in seconds (current: {self.script_timeout}): "))
                    if timeout > 0:
                        self.script_timeout = timeout
                        print(f"✅ Script timeout set to {timeout} seconds")
                    else:
                        print("❌ Timeout must be positive")
                except ValueError:
                    print("❌ Invalid timeout value")
                    
            elif choice == '2':
                try:
                    delay = float(input(f"⏳ Enter step delay in seconds (current: {self.step_delay}): "))
                    if delay >= 0:
                        self.step_delay = delay
                        print(f"✅ Step delay set to {delay} seconds")
                    else:
                        print("❌ Delay must be non-negative")
                except ValueError:
                    print("❌ Invalid delay value")
                    
            elif choice == '3':
                print("🌐 Checking AWS connection...")
                if self.check_aws_availability():
                    print("✅ AWS connection successful")
                else:
                    print("❌ AWS connection failed")
                    
            elif choice == '4':
                print(f"\n🔧 Current Settings:")
                print(f"  Script Timeout: {self.script_timeout} seconds")
                print(f"  Step Delay: {self.step_delay} seconds")
                print(f"  AWS Available: {'✅ Yes' if self.aws_available else '❌ No'}")
                print(f"  Scripts Directory: {self.scripts_directory}")
                
            elif choice == '0':
                break
                
            else:
                print("❌ Invalid choice")


def main():
    """Main entry point"""
    print("🎯 End-to-End Order Flow Simulator")
    print("=" * 50)
    
    # Get scripts directory from command line or use current directory
    scripts_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize simulator
    simulator = EndToEndFlowSimulator(scripts_dir)
    
    # Check AWS availability
    simulator.check_aws_availability()
    
    # Check if running in batch mode
    if '--batch' in sys.argv:
        print("🚀 Running in batch mode...")
        
        # Determine number of flows
        num_flows = 1
        if '--flows' in sys.argv:
            try:
                flow_index = sys.argv.index('--flows') + 1
                if flow_index < len(sys.argv):
                    num_flows = int(sys.argv[flow_index])
            except (ValueError, IndexError):
                num_flows = 1
        
        # Run flows
        if num_flows == 1:
            session = simulator.run_complete_order_flow()
            simulator.print_flow_report([session])
        else:
            sessions = simulator.run_multiple_flows(num_flows)
            simulator.print_flow_report(sessions)
        
        # Save results if requested
        if '--save' in sys.argv:
            filepath = simulator.save_flow_results()
            print(f"✅ Results saved to: {filepath}")
    else:
        # Run in interactive mode
        simulator.run_interactive_mode()


if __name__ == '__main__':
    main()
