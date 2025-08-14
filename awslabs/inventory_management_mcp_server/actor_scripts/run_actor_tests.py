#!/usr/bin/env python3
"""
Simple batch runner for Actor Scripts Testing
Quick execution script for running all actor tests and generating reports.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from actor_testing_simulator import ActorTestingSimulator
except ImportError as e:
    print(f"❌ Error importing ActorTestingSimulator: {e}")
    print("Make sure actor_testing_simulator.py is in the same directory.")
    sys.exit(1)


def main():
    """Main entry point for batch testing"""
    parser = argparse.ArgumentParser(
        description="Run Actor Scripts Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_actor_tests.py                    # Run all tests interactively
  python run_actor_tests.py --batch            # Run all tests in batch mode
  python run_actor_tests.py --batch --save     # Run tests and save results
  python run_actor_tests.py --quick            # Run quick tests only
  python run_actor_tests.py --script customer  # Test specific script
        """
    )
    
    parser.add_argument(
        '--batch', 
        action='store_true',
        help='Run in batch mode (non-interactive)'
    )
    
    parser.add_argument(
        '--save', 
        action='store_true',
        help='Save results to file'
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Run only quick tests (skip optimization and long-running tests)'
    )
    
    parser.add_argument(
        '--script', 
        type=str,
        help='Run tests for specific script (partial name matching)'
    )
    
    parser.add_argument(
        '--parallel', 
        action='store_true',
        default=True,
        help='Run tests in parallel (default: True)'
    )
    
    parser.add_argument(
        '--no-parallel', 
        action='store_true',
        help='Run tests sequentially'
    )
    
    parser.add_argument(
        '--timeout', 
        type=int,
        default=30,
        help='Test timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str,
        help='Output directory for results (default: test_results/)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🧪 Actor Scripts Testing Suite")
    print("=" * 50)
    
    try:
        # Initialize simulator
        simulator = ActorTestingSimulator(current_dir)
        
        # Configure timeout
        simulator.test_timeout = args.timeout
        
        # Handle specific script testing
        if args.script:
            matching_suites = [
                suite for suite in simulator.test_suites 
                if args.script.lower() in suite.script_name.lower()
            ]
            
            if not matching_suites:
                print(f"❌ No scripts found matching '{args.script}'")
                print("Available scripts:")
                for suite in simulator.test_suites:
                    print(f"  - {suite.script_name}")
                return 1
            
            print(f"🎯 Running tests for {len(matching_suites)} matching script(s):")
            for suite in matching_suites:
                print(f"  - {suite.script_name}")
            
            all_results = []
            for suite in matching_suites:
                suite_results = simulator.run_suite_tests(suite)
                all_results.extend(suite_results)
            
            simulator.results = all_results
            
        else:
            # Run all tests
            parallel = args.parallel and not args.no_parallel
            print(f"🚀 Running all tests ({'parallel' if parallel else 'sequential'} mode)...")
            
            if args.quick:
                # Filter out long-running tests
                for suite in simulator.test_suites:
                    suite.test_cases = [
                        tc for tc in suite.test_cases 
                        if not any(keyword in tc.lower() for keyword in ['optimization', 'analytics', 'backup'])
                    ]
                print("⚡ Quick mode: Skipping optimization and long-running tests")
            
            simulator.run_all_tests(parallel=parallel)
        
        # Print results
        simulator.print_summary_report()
        
        # Save results if requested
        if args.save or args.batch:
            output_dir = args.output_dir
            if output_dir:
                # Create custom output directory
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.join(output_dir, f"actor_test_results_{simulator.test_session_id}.json")
            else:
                filename = None
            
            filepath = simulator.save_results_to_file(filename)
            print(f"💾 Results saved to: {filepath}")
        
        # Interactive mode if not batch
        if not args.batch:
            print("\n" + "=" * 50)
            print("🎮 Entering interactive mode...")
            print("You can now view detailed results, run specific tests, or configure settings.")
            input("Press Enter to continue to interactive mode...")
            simulator.run_interactive_mode()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
