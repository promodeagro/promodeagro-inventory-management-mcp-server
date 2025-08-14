#!/usr/bin/env python3
"""
Real Flow Test Runner
Simple script to run end-to-end order flow tests with actual script interactions.
"""

import os
import sys
import argparse

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from complete_flow_orchestrator import CompleteFlowOrchestrator
except ImportError as e:
    print(f"❌ Error importing CompleteFlowOrchestrator: {e}")
    print("Make sure complete_flow_orchestrator.py is in the same directory.")
    sys.exit(1)


def main():
    """Main entry point for real flow testing"""
    parser = argparse.ArgumentParser(
        description="Run Real End-to-End Order Flow Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_real_flow_test.py                     # Interactive mode
  python run_real_flow_test.py --batch             # Single flow in batch mode
  python run_real_flow_test.py --batch --flows 3   # Multiple flows in batch mode
  python run_real_flow_test.py --customer CUST005  # Specific customer
  python run_real_flow_test.py --demo              # Demo mode with explanations
        """
    )
    
    parser.add_argument(
        '--batch', 
        action='store_true',
        help='Run in batch mode (non-interactive)'
    )
    
    parser.add_argument(
        '--flows', 
        type=int,
        default=1,
        help='Number of flows to run (default: 1)'
    )
    
    parser.add_argument(
        '--customer', 
        type=str,
        default='CUST001',
        help='Customer ID to use (default: CUST001)'
    )
    
    parser.add_argument(
        '--save', 
        action='store_true',
        help='Save results to file'
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run in demo mode with explanations'
    )
    
    parser.add_argument(
        '--timeout', 
        type=int,
        default=30,
        help='Step timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--delay', 
        type=float,
        default=3.0,
        help='Delay between steps in seconds (default: 3.0)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🎯 Real End-to-End Order Flow Test Runner")
    print("=" * 60)
    
    if args.demo:
        print_demo_explanation()
    
    try:
        # Initialize orchestrator
        orchestrator = CompleteFlowOrchestrator(current_dir)
        
        # Configure timeouts
        orchestrator.step_timeout = args.timeout
        orchestrator.inter_step_delay = args.delay
        
        if args.batch:
            print("🚀 Running in batch mode...")
            print(f"📊 Configuration:")
            print(f"  • Flows: {args.flows}")
            print(f"  • Customer: {args.customer}")
            print(f"  • Step Timeout: {args.timeout}s")
            print(f"  • Inter-step Delay: {args.delay}s")
            
            # Run flows
            if args.flows == 1:
                print(f"\n🎬 Starting single real flow for {args.customer}...")
                execution = orchestrator.run_complete_real_flow(args.customer)
                orchestrator.print_real_flow_report([execution])
                
                if execution.status == "COMPLETED":
                    print("\n🎉 SUCCESS: Complete order flow executed successfully!")
                    print(f"📋 Order ID: {execution.order_id}")
                    print(f"🚚 Delivery ID: {execution.delivery_id}")
                    print(f"⏱️ Total Time: {execution.total_duration:.2f}s")
                else:
                    print(f"\n❌ FAILED: Flow completed with status: {execution.status}")
                    failed_steps = [s for s in execution.steps if s.status == "FAILED"]
                    if failed_steps:
                        print("Failed steps:")
                        for step in failed_steps:
                            print(f"  • {step.step_id}: {step.error}")
                
            else:
                print(f"\n🔄 Starting {args.flows} real flows...")
                customer_base = [f"CUST{i:03d}" for i in range(1, args.flows + 1)]
                executions = orchestrator.run_multiple_real_flows(args.flows, customer_base)
                orchestrator.print_real_flow_report(executions)
                
                # Summary
                completed = len([e for e in executions if e.status == "COMPLETED"])
                print(f"\n📊 Batch Summary:")
                print(f"  • Total Flows: {len(executions)}")
                print(f"  • Completed: {completed}")
                print(f"  • Success Rate: {completed/len(executions)*100:.1f}%")
            
            # Save results if requested
            if args.save:
                filepath = orchestrator.save_real_flow_results()
                print(f"\n💾 Results saved to: {filepath}")
            
        else:
            # Interactive mode
            print("🎮 Starting interactive mode...")
            print("You can run flows, view results, and manage script instances.")
            input("Press Enter to continue...")
            orchestrator.run_interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running real flow tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def print_demo_explanation():
    """Print demo mode explanation"""
    print("\n🎓 DEMO MODE: Real End-to-End Order Flow Testing")
    print("=" * 60)
    print("This tool will:")
    print("1. 🚀 Actually start actor script processes")
    print("2. 🔐 Handle authentication for each actor")
    print("3. 🎭 Orchestrate interactions between scripts")
    print("4. 📊 Track the complete order journey")
    print("5. 📝 Generate comprehensive reports")
    print()
    print("🔄 Complete Flow Steps:")
    print("  1. Customer Portal - Login & Create Order")
    print("  2. Inventory Staff - Process Order")
    print("  3. Warehouse Manager - Approve Order")
    print("  4. Logistics Manager - Plan Delivery")
    print("  5. Delivery Personnel - Complete Delivery")
    print()
    print("⚠️  Note: This requires actual script files and may take several minutes.")
    print("=" * 60)
    
    input("Press Enter to continue with the demo...")


if __name__ == '__main__':
    sys.exit(main())
