#!/usr/bin/env python3
"""
Complete Flow Orchestrator
Orchestrates the complete end-to-end order flow by actually calling actor scripts.
Manages the entire process from customer login to delivery completion with real script interactions.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import our custom modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from script_caller_integration import ActorScriptController
    from end_to_end_flow_simulator import FlowStep, OrderFlowSession
except ImportError as e:
    print(f"[ERROR] Error importing modules: {e}")
    print("Make sure script_caller_integration.py and end_to_end_flow_simulator.py are in the same directory.")
    sys.exit(1)


@dataclass
class RealFlowExecution:
    """Represents a real flow execution with actual script calls"""
    session_id: str
    customer_id: str
    order_id: Optional[str] = None
    delivery_id: Optional[str] = None
    status: str = "INITIATED"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration: float = 0.0
    steps: List[FlowStep] = None
    script_instances: Dict[str, str] = None  # script_name -> script_id mapping
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.script_instances is None:
            self.script_instances = {}


class CompleteFlowOrchestrator:
    """Orchestrates complete order flows with real script interactions"""
    
    def __init__(self, scripts_directory: str = None):
        self.scripts_directory = scripts_directory or current_dir
        self.controller = ActorScriptController(self.scripts_directory)
        self.session_id = f"REAL-E2E-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.setup_logging()
        
        # Configuration
        self.step_timeout = 30  # seconds per step
        self.inter_step_delay = 3  # seconds between steps
        self.script_startup_delay = 15  # seconds for script startup
        
        # Current execution
        self.current_execution: Optional[RealFlowExecution] = None
        self.completed_executions: List[RealFlowExecution] = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.join(self.scripts_directory, 'orchestrator_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'orchestrator_{self.session_id}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_real_flow_steps(self, customer_id: str) -> List[FlowStep]:
        """Create flow steps for real script execution"""
        return [
            FlowStep(
                step_id="01_start_customer_portal",
                actor="Customer",
                script_name="customer_portal_standalone.py",
                action="start_and_authenticate",
                data={"customer_id": customer_id, "password": "customer123"}
            ),
            FlowStep(
                step_id="02_create_order",
                actor="Customer",
                script_name="customer_portal_standalone.py",
                action="create_order",
                data={"product_selection": "auto", "quantity": 2}
            ),
            FlowStep(
                step_id="03_start_inventory_staff",
                actor="Inventory Staff",
                script_name="inventory_staff_standalone.py",
                action="start_and_authenticate",
                data={"staff_id": "STAFF001", "password": "staff123"}
            ),
            FlowStep(
                step_id="04_process_order",
                actor="Inventory Staff",
                script_name="inventory_staff_standalone.py",
                action="process_order",
                data={"order_id": None}  # Will be filled from previous step
            ),
            FlowStep(
                step_id="05_start_warehouse_manager",
                actor="Warehouse Manager",
                script_name="warehouse_manager_standalone.py",
                action="start_and_authenticate",
                data={"manager_id": "MGR001", "password": "manager123"}
            ),
            FlowStep(
                step_id="06_approve_order",
                actor="Warehouse Manager",
                script_name="warehouse_manager_standalone.py",
                action="approve_order",
                data={"order_id": None}  # Will be filled from previous step
            ),
            FlowStep(
                step_id="07_start_logistics_manager",
                actor="Logistics Manager",
                script_name="logistics_manager_standalone.py",
                action="start_and_authenticate",
                data={"manager_id": "LOG001", "password": "logistics123"}
            ),
            FlowStep(
                step_id="08_plan_delivery",
                actor="Logistics Manager",
                script_name="logistics_manager_standalone.py",
                action="plan_delivery",
                data={"order_id": None}  # Will be filled from previous step
            ),
            FlowStep(
                step_id="09_start_delivery_personnel",
                actor="Delivery Personnel",
                script_name="delivery_personnel_standalone.py",
                action="start_and_authenticate",
                data={"personnel_id": "DEL001", "password": "delivery123"}
            ),
            FlowStep(
                step_id="10_complete_delivery",
                actor="Delivery Personnel",
                script_name="delivery_personnel_standalone.py",
                action="complete_delivery",
                data={"delivery_id": None, "payment_method": "cash", "amount": 150.00}
            )
        ]
    
    def execute_real_flow_step(self, step: FlowStep, execution: RealFlowExecution) -> bool:
        """Execute a real flow step with actual script interaction"""
        step.status = "RUNNING"
        step.start_time = datetime.now(timezone.utc).isoformat()
        
        self.logger.info(f"[DEMO] Executing Real Step {step.step_id}: {step.actor} - {step.action}")
        
        try:
            script_name = step.script_name
            action = step.action
            
            # Check if we need to start a new script instance
            if action.startswith("start_and_"):
                script_id = self._start_script_instance(script_name, execution)
                if not script_id:
                    step.status = "FAILED"
                    step.error = f"Failed to start script {script_name}"
                    return False
                
                # Handle authentication after starting
                auth_success = self._handle_authentication(script_id, step.data)
                if not auth_success:
                    step.status = "FAILED"
                    step.error = "Authentication failed"
                    return False
                
                step.output = f"Script {script_name} started and authenticated successfully"
                
                # Extract data from script output during startup
                try:
                    script_output = self.controller.caller.get_output(script_id, timeout=2.0)
                    if script_output:
                        # Create a result-like structure for data extraction
                        startup_result = {"output": script_output, "success": True}
                        self._extract_flow_data(startup_result, execution, step)
                except Exception as e:
                    self.logger.debug(f"[DEBUG] Could not get script output for data extraction: {e}")
                
            else:
                # Use existing script instance
                script_id = execution.script_instances.get(script_name)
                if not script_id:
                    step.status = "FAILED"
                    step.error = f"No active instance of {script_name}"
                    return False
                
                # Perform the action
                result = self.controller.perform_actor_action(script_id, action, step.data)
                
                if result["success"]:
                    step.output = f"Action {action} completed successfully"
                    
                    # Extract important data (like order_id, delivery_id)
                    self._extract_flow_data(result, execution, step)
                    
                    # Also try to get fresh script output for additional data extraction
                    try:
                        fresh_output = self.controller.caller.get_output(script_id, timeout=2.0)
                        if fresh_output:
                            fresh_result = {"output": fresh_output, "success": True}
                            self._extract_flow_data(fresh_result, execution, step)
                    except Exception as e:
                        self.logger.debug(f"[DEBUG] Could not get fresh script output: {e}")
                else:
                    step.status = "FAILED"
                    step.error = f"Action failed: {result.get('errors', [])}"
                    return False
            
            step.status = "COMPLETED"
            step.end_time = datetime.now(timezone.utc).isoformat()
            step.duration = (datetime.fromisoformat(step.end_time.replace('Z', '+00:00')) - 
                           datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))).total_seconds()
            
            self.logger.info(f"[SUCCESS] Real Step {step.step_id} completed successfully ({step.duration:.2f}s)")
            return True
            
        except Exception as e:
            step.end_time = datetime.now(timezone.utc).isoformat()
            step.duration = (datetime.fromisoformat(step.end_time.replace('Z', '+00:00')) - 
                           datetime.fromisoformat(step.start_time.replace('Z', '+00:00'))).total_seconds()
            step.status = "FAILED"
            step.error = str(e)
            self.logger.error(f"[ERROR] Real Step {step.step_id} failed: {str(e)}")
            return False
    
    def _start_script_instance(self, script_name: str, execution: RealFlowExecution) -> Optional[str]:
        """Start a new script instance"""
        try:
            self.logger.info(f"[START] Starting script instance: {script_name}")
            script_id = self.controller.start_actor_script(script_name)
            
            # Wait for script to fully start with progressive checking
            max_wait_time = self.script_startup_delay
            check_interval = 1.0
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                time.sleep(check_interval)
                elapsed_time += check_interval
                
                is_running = self.controller.caller.is_script_running(script_id)
                self.logger.info(f"[DEBUG] Script {script_name} running check at {elapsed_time}s: {is_running}")
                
                if is_running:
                    execution.script_instances[script_name] = script_id
                    self.logger.info(f"[SUCCESS] Script {script_name} started with ID {script_id}")
                    return script_id
            
            # Final check after max wait time
            if self.controller.caller.is_script_running(script_id):
                execution.script_instances[script_name] = script_id
                self.logger.info(f"[SUCCESS] Script {script_name} started with ID {script_id}")
                return script_id
            else:
                # Get error details for debugging
                try:
                    output = self.controller.caller.get_output(script_id, timeout=1.0)
                    error_output = self.controller.caller.get_error_output(script_id, timeout=1.0)
                    self.logger.error(f"[ERROR] Script {script_name} failed to start properly")
                    if output:
                        self.logger.error(f"[OUTPUT] {output}")
                    if error_output:
                        self.logger.error(f"[ERROR] {error_output}")
                except:
                    pass
                
                # Cleanup failed script
                try:
                    self.controller.caller.terminate_script(script_id)
                except:
                    pass
                    
                return None
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to start script {script_name}: {str(e)}")
            return None
    
    def _handle_authentication(self, script_id: str, auth_data: Dict[str, Any]) -> bool:
        """Handle authentication for a script"""
        try:
            # The ActorScriptController should handle authentication automatically
            # during script startup, but we can add additional verification here
            
            # Wait for authentication to complete
            time.sleep(2)
            
            # Get output to verify authentication
            output = self.controller.caller.get_output(script_id, timeout=3.0)
            errors = self.controller.caller.get_errors(script_id)
            
            # Check for authentication success indicators
            auth_success = any("Welcome" in line or "authenticated" in line.lower() 
                             for line in output)
            
            if errors:
                self.logger.warning(f"Authentication warnings: {errors}")
            
            return auth_success or len(errors) == 0  # Consider success if no errors
            
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _extract_flow_data(self, result: Dict[str, Any], execution: RealFlowExecution, step: FlowStep):
        """Extract important data from step results"""
        import re
        
        # Handle both list and string outputs
        output_data = result.get("output", [])
        if isinstance(output_data, list):
            output_text = " ".join(output_data)
        else:
            output_text = str(output_data)
        
        # Extract order ID - look for various patterns
        if not execution.order_id:
            # Look for ORD- pattern
            order_patterns = [
                r'ORD-\d{8}-\d{6}',  # ORD-20250814-223045
                r'Order ID[:\s]+([A-Z0-9-]+)',  # Order ID: ORD-20250814-223045
                r'order[:\s]+([A-Z0-9-]+)',     # order: ORD-20250814-223045
            ]
            
            for pattern in order_patterns:
                order_match = re.search(pattern, output_text, re.IGNORECASE)
                if order_match:
                    if pattern.startswith('ORD-'):
                        execution.order_id = order_match.group()
                    else:
                        execution.order_id = order_match.group(1)
                    self.logger.info(f"[ORDER] Extracted Order ID: {execution.order_id}")
                    break
        
        # Extract delivery ID - look for various patterns
        if not execution.delivery_id:
            delivery_patterns = [
                r'DEL-\d{8}-\d{6}',  # DEL-20250814-223045
                r'DELIVERY-\d{8}-\d{6}',  # DELIVERY-20250814-223045
                r'Delivery ID[:\s]+([A-Z0-9-]+)',  # Delivery ID: DEL-20250814-223045
                r'delivery[:\s]+([A-Z0-9-]+)',     # delivery: DEL-20250814-223045
            ]
            
            for pattern in delivery_patterns:
                delivery_match = re.search(pattern, output_text, re.IGNORECASE)
                if delivery_match:
                    if pattern.startswith(('DEL-', 'DELIVERY-')):
                        execution.delivery_id = delivery_match.group()
                    else:
                        execution.delivery_id = delivery_match.group(1)
                    self.logger.info(f"[DELIVERY] Extracted Delivery ID: {execution.delivery_id}")
                    break
    
    def run_complete_real_flow(self, customer_id: str = "CUST001") -> RealFlowExecution:
        """Run complete end-to-end flow with real script interactions"""
        self.logger.info(f"[START] Starting Complete Real Order Flow")
        self.logger.info(f"[CLIPBOARD] Session ID: {self.session_id}")
        self.logger.info(f"[USER] Customer ID: {customer_id}")
        
        # Create execution instance
        execution = RealFlowExecution(
            session_id=self.session_id,
            customer_id=customer_id,
            start_time=datetime.now(timezone.utc).isoformat(),
            steps=self.create_real_flow_steps(customer_id)
        )
        
        self.current_execution = execution
        execution.status = "RUNNING"
        
        try:
            # Execute each step
            for i, step in enumerate(execution.steps, 1):
                self.logger.info(f"\n[ADDRESS] Real Step {i}/{len(execution.steps)}: {step.step_id}")
                self.logger.info(f"[ORCHESTRATE] Actor: {step.actor}")
                self.logger.info(f"[DEMO] Action: {step.action}")
                
                # Update step data with extracted information
                if step.data and execution.order_id:
                    if step.data.get("order_id") is None:
                        step.data["order_id"] = execution.order_id
                
                if step.data and execution.delivery_id:
                    if step.data.get("delivery_id") is None:
                        step.data["delivery_id"] = execution.delivery_id
                
                # Execute the step
                success = self.execute_real_flow_step(step, execution)
                
                if not success:
                    self.logger.error(f"[ERROR] Real Step {step.step_id} failed - stopping flow")
                    execution.status = "FAILED"
                    break
                
                # Add delay between steps (except for the last step)
                if i < len(execution.steps):
                    self.logger.info(f"[WAIT] Waiting {self.inter_step_delay}s before next step...")
                    time.sleep(self.inter_step_delay)
            
            # Complete the execution
            execution.end_time = datetime.now(timezone.utc).isoformat()
            execution.total_duration = (datetime.fromisoformat(execution.end_time.replace('Z', '+00:00')) - 
                                      datetime.fromisoformat(execution.start_time.replace('Z', '+00:00'))).total_seconds()
            
            # Determine final status
            if execution.status != "FAILED":
                completed_steps = len([s for s in execution.steps if s.status == "COMPLETED"])
                if completed_steps == len(execution.steps):
                    execution.status = "COMPLETED"
                else:
                    execution.status = "PARTIAL"
            
            self.logger.info(f"\n[COMPLETE] Real Order Flow Completed!")
            self.logger.info(f"[TRACK] Status: {execution.status}")
            self.logger.info(f"[TIME] Total Duration: {execution.total_duration:.2f}s")
            self.logger.info(f"[CLIPBOARD] Order ID: {execution.order_id}")
            self.logger.info(f"[DELIVERY] Delivery ID: {execution.delivery_id}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Flow execution failed: {str(e)}")
            execution.status = "FAILED"
            execution.end_time = datetime.now(timezone.utc).isoformat()
            execution.total_duration = (datetime.fromisoformat(execution.end_time.replace('Z', '+00:00')) - 
                                      datetime.fromisoformat(execution.start_time.replace('Z', '+00:00'))).total_seconds()
        
        finally:
            # Clean up script instances
            self._cleanup_execution(execution)
        
        self.completed_executions.append(execution)
        self.current_execution = None
        
        return execution
    
    def _cleanup_execution(self, execution: RealFlowExecution):
        """Clean up script instances for an execution"""
        self.logger.info("[CLEANUP] Cleaning up script instances...")
        
        for script_name, script_id in execution.script_instances.items():
            try:
                self.controller.caller.terminate_script(script_id)
                self.controller.caller.cleanup_script(script_id)
                self.logger.info(f"[SUCCESS] Cleaned up {script_name} (ID: {script_id})")
            except Exception as e:
                self.logger.warning(f"[INTERRUPTED] Error cleaning up {script_name}: {str(e)}")
    
    def run_multiple_real_flows(self, num_flows: int = 2, customer_base: List[str] = None) -> List[RealFlowExecution]:
        """Run multiple real flows sequentially"""
        if customer_base is None:
            customer_base = [f"CUST{i:03d}" for i in range(1, num_flows + 1)]
        
        self.logger.info(f"[FLOW] Running {num_flows} sequential real order flows")
        
        executions = []
        for i, customer_id in enumerate(customer_base[:num_flows], 1):
            self.logger.info(f"\n[TARGET] Starting Real Flow {i}/{num_flows} for Customer {customer_id}")
            
            # Create new session ID for each flow
            self.session_id = f"REAL-E2E-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{i:02d}"
            
            execution = self.run_complete_real_flow(customer_id)
            executions.append(execution)
            
            # Brief pause between flows
            if i < num_flows:
                self.logger.info(f"⏸️ Pausing 10s between flows...")
                time.sleep(10)
        
        return executions
    
    def generate_real_flow_report(self, executions: List[RealFlowExecution] = None) -> Dict[str, Any]:
        """Generate report for real flow executions"""
        if executions is None:
            executions = self.completed_executions
        
        if not executions:
            return {}
        
        # Convert to OrderFlowSession format for compatibility
        sessions = []
        for execution in executions:
            session = OrderFlowSession(
                session_id=execution.session_id,
                customer_id=execution.customer_id,
                order_id=execution.order_id,
                delivery_id=execution.delivery_id,
                status=execution.status,
                start_time=execution.start_time,
                end_time=execution.end_time,
                total_duration=execution.total_duration,
                steps=execution.steps
            )
            sessions.append(session)
        
        # Use the existing report generation logic
        from end_to_end_flow_simulator import EndToEndFlowSimulator
        temp_simulator = EndToEndFlowSimulator()
        temp_simulator.completed_sessions = sessions
        
        report = temp_simulator.generate_flow_report()
        
        # Add real flow specific information
        report['execution_type'] = 'REAL_SCRIPT_EXECUTION'
        report['script_instances_used'] = sum(len(ex.script_instances) for ex in executions)
        
        return report
    
    def print_real_flow_report(self, executions: List[RealFlowExecution] = None):
        """Print formatted real flow report"""
        report = self.generate_real_flow_report(executions)
        
        if not report:
            print("No real flow data available for reporting.")
            return
        
        print("\n" + "=" * 80)
        print("[TARGET] REAL END-TO-END ORDER FLOW EXECUTION REPORT")
        print("=" * 80)
        print(f"[TOOL] Execution Type: {report.get('execution_type', 'Unknown')}")
        print(f"[MOBILE] Script Instances Used: {report.get('script_instances_used', 0)}")
        
        # Use existing report printing logic
        from end_to_end_flow_simulator import EndToEndFlowSimulator
        temp_simulator = EndToEndFlowSimulator()
        temp_simulator.completed_sessions = [
            OrderFlowSession(
                session_id=ex.session_id,
                customer_id=ex.customer_id,
                order_id=ex.order_id,
                delivery_id=ex.delivery_id,
                status=ex.status,
                start_time=ex.start_time,
                end_time=ex.end_time,
                total_duration=ex.total_duration,
                steps=ex.steps
            ) for ex in (executions or self.completed_executions)
        ]
        
        temp_simulator.print_flow_report()
    
    def save_real_flow_results(self, filename: str = None) -> str:
        """Save real flow results to JSON file"""
        if not filename:
            filename = f"real_e2e_flow_results_{self.session_id}.json"
        
        results_dir = os.path.join(self.scripts_directory, 'real_e2e_results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        
        report_data = self.generate_real_flow_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"Real flow results saved to: {filepath}")
        return filepath
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        while True:
            print("\n" + "=" * 60)
            print("[TARGET] COMPLETE REAL FLOW ORCHESTRATOR")
            print("=" * 60)
            print("1. [START] Run Single Real Order Flow")
            print("2. [FLOW] Run Multiple Real Order Flows")
            print("3. [TRACK] View Last Results")
            print("4. [SAVE] Save Results to File")
            print("5. [CLEANUP] Cleanup All Scripts")
            print("6. [CLIPBOARD] List Active Scripts")
            print("0. [EXIT] Exit")
            
            choice = input("\n[TARGET] Select option (0-6): ").strip()
            
            if choice == '1':
                customer_id = input("[USER] Enter Customer ID (default: CUST001): ").strip() or "CUST001"
                print(f"\n[START] Running real order flow for {customer_id}...")
                execution = self.run_complete_real_flow(customer_id)
                self.print_real_flow_report([execution])
                
            elif choice == '2':
                try:
                    num_flows = int(input("[NUMBER] Number of flows to run (default: 2): ").strip() or "2")
                    print(f"\n[FLOW] Running {num_flows} real order flows...")
                    executions = self.run_multiple_real_flows(num_flows)
                    self.print_real_flow_report(executions)
                except ValueError:
                    print("[ERROR] Invalid number of flows")
                    
            elif choice == '3':
                if self.completed_executions:
                    self.print_real_flow_report()
                else:
                    print("[ERROR] No real flow results available. Run flows first.")
                    
            elif choice == '4':
                if self.completed_executions:
                    filepath = self.save_real_flow_results()
                    print(f"[SUCCESS] Results saved to: {filepath}")
                else:
                    print("[ERROR] No real flow results to save. Run flows first.")
                    
            elif choice == '5':
                print("[CLEANUP] Cleaning up all active scripts...")
                self.controller.cleanup()
                print("[SUCCESS] Cleanup completed")
                
            elif choice == '6':
                active_scripts = self.controller.caller.list_active_scripts()
                if active_scripts:
                    print("\n[CLIPBOARD] Active Scripts:")
                    for script_id, status in active_scripts.items():
                        print(f"  {script_id}: {status['script_name']} - {status['status']}")
                else:
                    print("[CLIPBOARD] No active scripts")
                    
            elif choice == '0':
                print("[CLEANUP] Cleaning up before exit...")
                self.controller.cleanup()
                print("[GOODBYE] Goodbye!")
                break
                
            else:
                print("[ERROR] Invalid choice. Please try again.")


def main():
    """Main entry point"""
    print("[TARGET] Complete Real Flow Orchestrator")
    print("=" * 50)
    
    # Get scripts directory from command line or use current directory
    scripts_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize orchestrator
    orchestrator = CompleteFlowOrchestrator(scripts_dir)
    
    try:
        # Check if running in batch mode
        if '--batch' in sys.argv:
            print("[START] Running in batch mode...")
            
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
                execution = orchestrator.run_complete_real_flow()
                orchestrator.print_real_flow_report([execution])
            else:
                executions = orchestrator.run_multiple_real_flows(num_flows)
                orchestrator.print_real_flow_report(executions)
            
            # Save results if requested
            if '--save' in sys.argv:
                filepath = orchestrator.save_real_flow_results()
                print(f"[SUCCESS] Results saved to: {filepath}")
        else:
            # Run in interactive mode
            orchestrator.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Interrupted by user")
        orchestrator.controller.cleanup()
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        orchestrator.controller.cleanup()
        raise


if __name__ == '__main__':
    main()
