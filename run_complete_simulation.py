#!/usr/bin/env python3
"""
Quick runner for the complete order fulfillment simulation
"""

import sys
import os

# Add simulation directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'simulation'))

from complete_order_fulfillment_simulator import main

if __name__ == "__main__":
    print("🚀 Starting Aurora Spark Complete Order Fulfillment Simulation...")
    main()
