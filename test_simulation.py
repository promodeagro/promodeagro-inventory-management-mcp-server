#!/usr/bin/env python3
"""
Test runner for the complete order fulfillment simulation
Runs without user interaction to identify issues
"""

import sys
import os
import traceback

# Add simulation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'simulation'))

from complete_order_fulfillment_simulator import CompleteOrderFulfillmentSimulator

def test_simulation():
    """Test the simulation and identify issues"""
    issues = []
    
    try:
        print("🧪 TESTING COMPLETE ORDER FULFILLMENT SIMULATION")
        print("=" * 60)
        
        simulator = CompleteOrderFulfillmentSimulator()
        
        # Override wait_for_user to not wait
        simulator.wait_for_user = lambda msg="": print(f"⏭️ Auto-continuing: {msg}")
        
        print("\n🔄 Starting automated simulation test...")
        
        # Test Phase 1: Customer Order Creation
        print("\n📋 Testing Phase 1: Customer Order Creation")
        try:
            success = simulator.simulate_customer_order_creation()
            if success:
                print("✅ Phase 1: Customer order creation - PASSED")
            else:
                print("❌ Phase 1: Customer order creation - FAILED")
                issues.append("Customer order creation failed")
        except Exception as e:
            print(f"❌ Phase 1: Customer order creation - ERROR: {str(e)}")
            issues.append(f"Customer order creation error: {str(e)}")
            traceback.print_exc()
        
        # Test Phase 2: Warehouse Operations
        print("\n📋 Testing Phase 2: Warehouse Operations")
        try:
            success = simulator.simulate_warehouse_operations()
            if success:
                print("✅ Phase 2: Warehouse operations - PASSED")
            else:
                print("❌ Phase 2: Warehouse operations - FAILED")
                issues.append("Warehouse operations failed")
        except Exception as e:
            print(f"❌ Phase 2: Warehouse operations - ERROR: {str(e)}")
            issues.append(f"Warehouse operations error: {str(e)}")
            traceback.print_exc()
        
        # Test Phase 3: Delivery Operations
        print("\n📋 Testing Phase 3: Delivery Operations")
        try:
            success = simulator.simulate_delivery_operations()
            if success:
                print("✅ Phase 3: Delivery operations - PASSED")
            else:
                print("❌ Phase 3: Delivery operations - FAILED")
                issues.append("Delivery operations failed")
        except Exception as e:
            print(f"❌ Phase 3: Delivery operations - ERROR: {str(e)}")
            issues.append(f"Delivery operations error: {str(e)}")
            traceback.print_exc()
        
        # Print results
        print("\n" + "=" * 60)
        print("🧪 SIMULATION TEST RESULTS")
        print("=" * 60)
        
        if not issues:
            print("✅ ALL TESTS PASSED!")
            print("🎉 The simulation is working correctly")
            
            # Print final summary
            if hasattr(simulator, 'order_id') and simulator.order_id:
                print(f"\n📦 Generated Order ID: {simulator.order_id}")
            if hasattr(simulator, 'route_id') and simulator.route_id:
                print(f"🗺️ Generated Route ID: {simulator.route_id}")
            if hasattr(simulator, 'assigned_rider') and simulator.assigned_rider:
                print(f"🚚 Assigned Rider: {simulator.assigned_rider}")
        else:
            print("❌ ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        return issues
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        issues.append(f"Critical simulation error: {str(e)}")
        return issues

if __name__ == "__main__":
    issues = test_simulation()
    
    if issues:
        print(f"\n📋 FOUND {len(issues)} ISSUES TO FIX")
        sys.exit(1)
    else:
        print("\n🎯 SIMULATION READY FOR PRODUCTION")
        sys.exit(0)
