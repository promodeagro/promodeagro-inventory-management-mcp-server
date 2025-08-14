#!/usr/bin/env python3
"""
Demo Script for Actor Testing Suite
Shows the testing framework in action with sample execution.
"""

import os
import sys
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from actor_testing_simulator import ActorTestingSimulator
except ImportError as e:
    print(f"❌ Error importing ActorTestingSimulator: {e}")
    sys.exit(1)


def demo_quick_test():
    """Demonstrate quick testing functionality"""
    print("🎬 DEMO: Quick Actor Scripts Testing")
    print("=" * 60)
    
    # Initialize simulator
    simulator = ActorTestingSimulator(current_dir)
    
    # Configure for demo (shorter timeout, fewer tests)
    simulator.test_timeout = 5
    
    # Select a few scripts for demo
    demo_scripts = [
        'customer_portal_standalone.py',
        'auth_manager.py',
        'delivery_slots_api.py'
    ]
    
    # Filter test suites for demo
    demo_suites = [
        suite for suite in simulator.test_suites 
        if suite.script_name in demo_scripts
    ]
    
    # Limit test cases for demo
    for suite in demo_suites:
        suite.test_cases = suite.test_cases[:3]  # Only first 3 test cases
    
    simulator.test_suites = demo_suites
    
    print(f"🎯 Running demo tests for {len(demo_suites)} scripts...")
    print(f"📊 Total test cases: {sum(len(suite.test_cases) for suite in demo_suites)}")
    
    # Run tests
    start_time = time.time()
    results = simulator.run_all_tests(parallel=True)
    end_time = time.time()
    
    print(f"\n⏱️ Demo completed in {end_time - start_time:.2f} seconds")
    
    # Show results
    simulator.print_summary_report()
    
    return simulator


def demo_interactive_features():
    """Demonstrate interactive features"""
    print("\n🎮 DEMO: Interactive Features")
    print("=" * 60)
    
    simulator = demo_quick_test()
    
    print("\n📋 Available Interactive Features:")
    print("1. 📊 Summary Report - ✅ Demonstrated above")
    print("2. 💾 Save Results - Let's try this...")
    
    # Save results
    filepath = simulator.save_results_to_file()
    print(f"✅ Demo results saved to: {filepath}")
    
    print("\n3. 📈 Results Analysis:")
    summary = simulator.generate_summary_report()
    
    if summary:
        print(f"   • Success Rate: {summary['summary']['success_rate']:.1f}%")
        print(f"   • Average Test Time: {summary['summary']['average_execution_time']:.2f}s")
        print(f"   • Scripts Tested: {len(summary['script_results'])}")
        
        # Show script performance
        print("\n   📊 Script Performance:")
        for script_name, results in summary['script_results'].items():
            success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            print(f"   • {script_name[:30]:<30}: {success_rate:5.1f}% ({results['execution_time']:.2f}s)")
    
    return simulator


def demo_error_handling():
    """Demonstrate error handling and reporting"""
    print("\n🚨 DEMO: Error Handling")
    print("=" * 60)
    
    # Create a simulator with intentional issues for demo
    simulator = ActorTestingSimulator(current_dir)
    
    # Simulate some test failures
    print("🎭 Simulating test scenarios with different outcomes...")
    
    # Create mock results for demonstration
    from actor_testing_simulator import TestResult
    
    mock_results = [
        TestResult("demo_script.py", "successful_test", "PASS", 0.5, None, "Test completed successfully"),
        TestResult("demo_script.py", "failed_test", "FAIL", 1.2, "Connection timeout", "Failed to connect to service"),
        TestResult("demo_script.py", "skipped_test", "SKIP", 0.0, "AWS not available", None),
        TestResult("demo_script.py", "error_test", "ERROR", 0.8, "ImportError: module not found", "Stack trace here...")
    ]
    
    simulator.results = mock_results
    
    print("\n📊 Demo Results with Various Outcomes:")
    simulator.print_summary_report()
    
    return simulator


def demo_batch_mode():
    """Demonstrate batch mode execution"""
    print("\n🚀 DEMO: Batch Mode Execution")
    print("=" * 60)
    
    print("💡 In real usage, you would run:")
    print("   python run_actor_tests.py --batch --save")
    print("\n📋 This would:")
    print("   • Run all tests automatically")
    print("   • Generate comprehensive reports")
    print("   • Save results to JSON files")
    print("   • Exit without user interaction")
    
    print("\n🎯 Other useful batch commands:")
    print("   python run_actor_tests.py --quick          # Fast tests only")
    print("   python run_actor_tests.py --script customer # Specific script")
    print("   python run_actor_tests.py --no-parallel    # Sequential execution")


def main():
    """Main demo function"""
    print("🎬 Actor Scripts Testing Suite - DEMONSTRATION")
    print("=" * 70)
    print("This demo shows the capabilities of the testing framework.")
    print("=" * 70)
    
    try:
        # Demo 1: Quick test execution
        simulator1 = demo_quick_test()
        
        input("\n⏸️ Press Enter to continue to interactive features demo...")
        
        # Demo 2: Interactive features
        simulator2 = demo_interactive_features()
        
        input("\n⏸️ Press Enter to continue to error handling demo...")
        
        # Demo 3: Error handling
        simulator3 = demo_error_handling()
        
        input("\n⏸️ Press Enter to continue to batch mode demo...")
        
        # Demo 4: Batch mode
        demo_batch_mode()
        
        print("\n" + "=" * 70)
        print("🎉 DEMO COMPLETED!")
        print("=" * 70)
        print("✅ You've seen:")
        print("   • Quick test execution")
        print("   • Result reporting and analysis")
        print("   • Error handling and different test outcomes")
        print("   • File saving and result persistence")
        print("   • Batch mode capabilities")
        
        print("\n🚀 Ready to use the testing suite!")
        print("Run 'python run_actor_tests.py' to get started.")
        
        # Offer to run interactive mode
        choice = input("\n❓ Would you like to try the interactive mode now? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n🎮 Starting interactive mode...")
            simulator = ActorTestingSimulator(current_dir)
            simulator.run_interactive_mode()
        else:
            print("👋 Demo finished. Thank you!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
