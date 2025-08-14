#!/usr/bin/env python3
"""
Script Caller Integration
Provides integration to actually call and interact with actor scripts using subprocess.
Handles input/output communication and process management.
"""

import os
import sys
import subprocess
import threading
import queue
import time
import json
import signal
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class ScriptExecution:
    """Represents a script execution instance"""
    script_name: str
    process: subprocess.Popen
    input_queue: queue.Queue
    output_queue: queue.Queue
    error_queue: queue.Queue
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED, TIMEOUT
    start_time: float = 0.0
    end_time: float = 0.0
    exit_code: Optional[int] = None


class ScriptCallerIntegration:
    """Handles calling and interacting with actor scripts"""
    
    def __init__(self, scripts_directory: str = None):
        self.scripts_directory = scripts_directory or os.path.dirname(os.path.abspath(__file__))
        self.active_scripts: Dict[str, ScriptExecution] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.script_timeout = 60  # seconds
        self.python_executable = sys.executable
        
    def start_script(self, script_name: str, script_id: str = None) -> str:
        """Start an actor script and return execution ID"""
        if script_id is None:
            script_id = f"{script_name}_{int(time.time())}"
        
        script_path = os.path.join(self.scripts_directory, script_name)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        try:
            # Start the script process
            process = subprocess.Popen(
                [self.python_executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=self.scripts_directory
            )
            
            # Create execution instance
            execution = ScriptExecution(
                script_name=script_name,
                process=process,
                input_queue=queue.Queue(),
                output_queue=queue.Queue(),
                error_queue=queue.Queue(),
                start_time=time.time()
            )
            
            # Start I/O threads
            self._start_io_threads(execution)
            
            self.active_scripts[script_id] = execution
            self.logger.info(f"Started script {script_name} with ID {script_id}")
            
            return script_id
            
        except Exception as e:
            self.logger.error(f"Failed to start script {script_name}: {str(e)}")
            raise
    
    def _start_io_threads(self, execution: ScriptExecution):
        """Start input/output handling threads for a script"""
        
        def output_reader():
            """Read stdout from the script"""
            try:
                while execution.process.poll() is None:
                    line = execution.process.stdout.readline()
                    if line:
                        execution.output_queue.put(line.strip())
                    time.sleep(0.01)
                
                # Read any remaining output
                remaining = execution.process.stdout.read()
                if remaining:
                    for line in remaining.split('\n'):
                        if line.strip():
                            execution.output_queue.put(line.strip())
                            
            except Exception as e:
                execution.error_queue.put(f"Output reader error: {str(e)}")
        
        def error_reader():
            """Read stderr from the script"""
            try:
                while execution.process.poll() is None:
                    line = execution.process.stderr.readline()
                    if line:
                        execution.error_queue.put(line.strip())
                    time.sleep(0.01)
                
                # Read any remaining errors
                remaining = execution.process.stderr.read()
                if remaining:
                    for line in remaining.split('\n'):
                        if line.strip():
                            execution.error_queue.put(line.strip())
                            
            except Exception as e:
                execution.error_queue.put(f"Error reader error: {str(e)}")
        
        def input_writer():
            """Write stdin to the script"""
            try:
                while execution.process.poll() is None:
                    try:
                        input_data = execution.input_queue.get(timeout=0.1)
                        if input_data is not None:
                            execution.process.stdin.write(input_data + '\n')
                            execution.process.stdin.flush()
                    except queue.Empty:
                        continue
                    except Exception as e:
                        execution.error_queue.put(f"Input writer error: {str(e)}")
                        break
                        
            except Exception as e:
                execution.error_queue.put(f"Input writer error: {str(e)}")
        
        # Start threads
        threading.Thread(target=output_reader, daemon=True).start()
        threading.Thread(target=error_reader, daemon=True).start()
        threading.Thread(target=input_writer, daemon=True).start()
    
    def send_input(self, script_id: str, input_data: str) -> bool:
        """Send input to a running script"""
        if script_id not in self.active_scripts:
            self.logger.error(f"Script ID {script_id} not found")
            return False
        
        execution = self.active_scripts[script_id]
        
        if execution.status != "RUNNING":
            self.logger.error(f"Script {script_id} is not running (status: {execution.status})")
            return False
        
        try:
            execution.input_queue.put(input_data)
            self.logger.debug(f"Sent input to {script_id}: {input_data}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send input to {script_id}: {str(e)}")
            return False
    
    def get_output(self, script_id: str, timeout: float = 1.0) -> List[str]:
        """Get output from a running script"""
        if script_id not in self.active_scripts:
            return []
        
        execution = self.active_scripts[script_id]
        output_lines = []
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                line = execution.output_queue.get(timeout=0.1)
                output_lines.append(line)
            except queue.Empty:
                if execution.process.poll() is not None:
                    # Process has ended, get any remaining output
                    break
                continue
        
        return output_lines
    
    def get_errors(self, script_id: str) -> List[str]:
        """Get error output from a running script"""
        if script_id not in self.active_scripts:
            return []
        
        execution = self.active_scripts[script_id]
        error_lines = []
        
        while not execution.error_queue.empty():
            try:
                line = execution.error_queue.get_nowait()
                error_lines.append(line)
            except queue.Empty:
                break
        
        return error_lines
    
    def is_script_running(self, script_id: str) -> bool:
        """Check if a script is still running"""
        if script_id not in self.active_scripts:
            return False
        
        execution = self.active_scripts[script_id]
        
        if execution.process.poll() is None:
            return True
        else:
            # Process has ended, update status
            execution.status = "COMPLETED" if execution.process.returncode == 0 else "FAILED"
            execution.end_time = time.time()
            execution.exit_code = execution.process.returncode
            return False
    
    def wait_for_script(self, script_id: str, timeout: float = None) -> bool:
        """Wait for a script to complete"""
        if script_id not in self.active_scripts:
            return False
        
        execution = self.active_scripts[script_id]
        
        try:
            if timeout:
                execution.process.wait(timeout=timeout)
            else:
                execution.process.wait()
            
            execution.status = "COMPLETED" if execution.process.returncode == 0 else "FAILED"
            execution.end_time = time.time()
            execution.exit_code = execution.process.returncode
            
            return execution.status == "COMPLETED"
            
        except subprocess.TimeoutExpired:
            execution.status = "TIMEOUT"
            execution.end_time = time.time()
            self.terminate_script(script_id)
            return False
    
    def terminate_script(self, script_id: str) -> bool:
        """Terminate a running script"""
        if script_id not in self.active_scripts:
            return False
        
        execution = self.active_scripts[script_id]
        
        try:
            if execution.process.poll() is None:
                execution.process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    execution.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    execution.process.kill()
                    execution.process.wait()
            
            execution.status = "TERMINATED"
            execution.end_time = time.time()
            execution.exit_code = execution.process.returncode
            
            self.logger.info(f"Terminated script {script_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate script {script_id}: {str(e)}")
            return False
    
    def cleanup_script(self, script_id: str):
        """Clean up resources for a script"""
        if script_id in self.active_scripts:
            execution = self.active_scripts[script_id]
            
            # Ensure process is terminated
            if execution.process.poll() is None:
                self.terminate_script(script_id)
            
            # Remove from active scripts
            del self.active_scripts[script_id]
            self.logger.debug(f"Cleaned up script {script_id}")
    
    def cleanup_all(self):
        """Clean up all active scripts"""
        script_ids = list(self.active_scripts.keys())
        for script_id in script_ids:
            self.cleanup_script(script_id)
    
    def get_script_status(self, script_id: str) -> Dict[str, Any]:
        """Get detailed status of a script"""
        if script_id not in self.active_scripts:
            return {"error": "Script not found"}
        
        execution = self.active_scripts[script_id]
        
        # Update status if process has ended
        if execution.status == "RUNNING" and execution.process.poll() is not None:
            execution.status = "COMPLETED" if execution.process.returncode == 0 else "FAILED"
            execution.end_time = time.time()
            execution.exit_code = execution.process.returncode
        
        return {
            "script_name": execution.script_name,
            "status": execution.status,
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "duration": (execution.end_time or time.time()) - execution.start_time,
            "exit_code": execution.exit_code,
            "pid": execution.process.pid if execution.process.poll() is None else None
        }
    
    def list_active_scripts(self) -> Dict[str, Dict[str, Any]]:
        """List all active scripts"""
        return {script_id: self.get_script_status(script_id) 
                for script_id in self.active_scripts.keys()}


class ActorScriptController:
    """High-level controller for managing actor script interactions"""
    
    def __init__(self, scripts_directory: str = None):
        self.caller = ScriptCallerIntegration(scripts_directory)
        self.logger = logging.getLogger(__name__)
        
        # Script-specific interaction patterns
        self.interaction_patterns = {
            "customer_portal_standalone.py": {
                "login_prompts": ["Customer ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"customer_id": "CUST001", "password": "customer123"}
            },
            "inventory_staff_standalone.py": {
                "login_prompts": ["Staff ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"staff_id": "STAFF001", "password": "staff123"}
            },
            "warehouse_manager_standalone.py": {
                "login_prompts": ["Manager ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"manager_id": "MGR001", "password": "manager123"}
            },
            "delivery_personnel_standalone.py": {
                "login_prompts": ["Personnel ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"personnel_id": "DEL001", "password": "delivery123"}
            },
            "logistics_manager_standalone.py": {
                "login_prompts": ["Manager ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"manager_id": "LOG001", "password": "logistics123"}
            },
            "supplier_portal_standalone.py": {
                "login_prompts": ["Supplier ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"supplier_id": "SUP001", "password": "supplier123"}
            },
            "auditor_standalone.py": {
                "login_prompts": ["Auditor ID:", "Password:"],
                "menu_prompts": ["Select operation"],
                "demo_credentials": {"auditor_id": "AUD001", "password": "auditor123"}
            }
        }
    
    def start_actor_script(self, script_name: str) -> str:
        """Start an actor script and handle initial setup"""
        script_id = self.caller.start_script(script_name)
        
        # Wait for script to start
        time.sleep(2)
        
        # Handle initial interactions if needed
        if script_name in self.interaction_patterns:
            self._handle_initial_interaction(script_id, script_name)
        
        return script_id
    
    def _handle_initial_interaction(self, script_id: str, script_name: str):
        """Handle initial interaction with a script (like login)"""
        pattern = self.interaction_patterns[script_name]
        
        # Get initial output
        output = self.caller.get_output(script_id, timeout=3.0)
        
        # Look for login prompts
        for line in output:
            if any(prompt in line for prompt in pattern["login_prompts"]):
                # Send demo credentials
                credentials = pattern["demo_credentials"]
                
                if "Customer ID:" in line or "customer_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("customer_id", ""))
                elif "Staff ID:" in line or "staff_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("staff_id", ""))
                elif "Manager ID:" in line or "manager_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("manager_id", ""))
                elif "Personnel ID:" in line or "personnel_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("personnel_id", ""))
                elif "Supplier ID:" in line or "supplier_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("supplier_id", ""))
                elif "Auditor ID:" in line or "auditor_id" in credentials:
                    self.caller.send_input(script_id, credentials.get("auditor_id", ""))
                elif "Password:" in line:
                    # Send the appropriate password
                    for key, value in credentials.items():
                        if "password" in key:
                            self.caller.send_input(script_id, value)
                            break
    
    def perform_actor_action(self, script_id: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform a specific action with an actor script"""
        if parameters is None:
            parameters = {}
        
        result = {
            "action": action,
            "success": False,
            "output": [],
            "errors": [],
            "duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Send action-specific inputs based on the action type
            if action == "create_order":
                self._handle_create_order_action(script_id, parameters)
            elif action == "process_order":
                self._handle_process_order_action(script_id, parameters)
            elif action == "approve_order":
                self._handle_approve_order_action(script_id, parameters)
            elif action == "plan_delivery":
                self._handle_plan_delivery_action(script_id, parameters)
            elif action == "complete_delivery":
                self._handle_complete_delivery_action(script_id, parameters)
            else:
                # Generic action handling
                self._handle_generic_action(script_id, action, parameters)
            
            # Wait for output
            time.sleep(2)
            
            # Collect results
            result["output"] = self.caller.get_output(script_id, timeout=2.0)
            result["errors"] = self.caller.get_errors(script_id)
            result["success"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(str(e))
            result["success"] = False
        
        result["duration"] = time.time() - start_time
        return result
    
    def _handle_create_order_action(self, script_id: str, parameters: Dict[str, Any]):
        """Handle order creation action"""
        # Navigate to order creation menu
        self.caller.send_input(script_id, "1")  # Order Management
        time.sleep(1)
        self.caller.send_input(script_id, "2")  # Place New Order
        time.sleep(1)
        
        # Select products (simplified)
        self.caller.send_input(script_id, "3")  # View All Products
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Select first product
        time.sleep(1)
        self.caller.send_input(script_id, str(parameters.get("quantity", 1)))  # Quantity
        time.sleep(1)
        self.caller.send_input(script_id, "yes")  # Add to cart
        time.sleep(1)
        self.caller.send_input(script_id, "5")  # Proceed to checkout
    
    def _handle_process_order_action(self, script_id: str, parameters: Dict[str, Any]):
        """Handle order processing action"""
        # Navigate to order processing menu
        self.caller.send_input(script_id, "2")  # Order Processing
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Process Pending Orders
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Select first order
        time.sleep(1)
        self.caller.send_input(script_id, "yes")  # Confirm processing
    
    def _handle_approve_order_action(self, script_id: str, parameters: Dict[str, Any]):
        """Handle order approval action"""
        # Navigate to approval menu
        self.caller.send_input(script_id, "3")  # Order Management
        time.sleep(1)
        self.caller.send_input(script_id, "2")  # Approve Orders
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Select first order
        time.sleep(1)
        self.caller.send_input(script_id, "yes")  # Approve
    
    def _handle_plan_delivery_action(self, script_id: str, parameters: Dict[str, Any]):
        """Handle delivery planning action"""
        # Navigate to delivery planning
        self.caller.send_input(script_id, "2")  # Delivery Management
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Plan Deliveries
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Auto-plan
    
    def _handle_complete_delivery_action(self, script_id: str, parameters: Dict[str, Any]):
        """Handle delivery completion action"""
        # Navigate to delivery completion
        self.caller.send_input(script_id, "1")  # Delivery Operations
        time.sleep(1)
        self.caller.send_input(script_id, "3")  # Complete Delivery
        time.sleep(1)
        self.caller.send_input(script_id, "1")  # Select delivery
        time.sleep(1)
        self.caller.send_input(script_id, "yes")  # Confirm completion
    
    def _handle_generic_action(self, script_id: str, action: str, parameters: Dict[str, Any]):
        """Handle generic actions"""
        # Send basic menu navigation
        self.caller.send_input(script_id, "1")  # First menu option
        time.sleep(1)
    
    def cleanup(self):
        """Clean up all resources"""
        self.caller.cleanup_all()


# Example usage and testing functions
def test_script_integration():
    """Test the script integration functionality"""
    controller = ActorScriptController()
    
    try:
        print("🧪 Testing Script Integration")
        
        # Test starting a customer portal script
        print("📱 Starting Customer Portal...")
        customer_script_id = controller.start_actor_script("customer_portal_standalone.py")
        
        # Wait and check status
        time.sleep(3)
        status = controller.caller.get_script_status(customer_script_id)
        print(f"Status: {status}")
        
        # Get output
        output = controller.caller.get_output(customer_script_id, timeout=2.0)
        print(f"Output: {output}")
        
        # Perform an action
        print("🛒 Creating order...")
        result = controller.perform_actor_action(customer_script_id, "create_order", {"quantity": 2})
        print(f"Action result: {result}")
        
        # Clean up
        controller.cleanup()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        controller.cleanup()


if __name__ == "__main__":
    # Run test if executed directly
    test_script_integration()
