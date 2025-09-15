#!/usr/bin/env python3
"""
Test runner for the multi-order simulation
Runs with predefined parameters for quick testing
"""

import sys
import os

# Add simulation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'simulation'))

from multi_order_fulfillment_simulator import MultiOrderFulfillmentSimulator

def test_multi_order_simulation():
    """Test the multi-order simulation with predefined parameters"""
    try:
        print("🧪 TESTING MULTI-ORDER SIMULATION")
        print("=" * 60)
        
        simulator = MultiOrderFulfillmentSimulator()
        
        # Override user input for automated testing
        def mock_get_input():
            return {
                'num_orders': 5,  # Test with 5 orders
                'speed': 'fast',
                'detailed_report': True
            }
        
        simulator.get_user_input_for_simulation = mock_get_input
        
        # Override wait_for_user to not wait
        simulator.wait_for_user = lambda msg="": print(f"⏭️ Auto-continuing: {msg}")
        
        print("🔄 Running automated test with 5 orders...")
        success = simulator.run_multi_order_simulation()
        
        if success:
            print("\n✅ MULTI-ORDER SIMULATION TEST PASSED!")
            return True
        else:
            print("\n❌ MULTI-ORDER SIMULATION TEST FAILED!")
            return False
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_multi_order_simulation()
    sys.exit(0 if success else 1)
