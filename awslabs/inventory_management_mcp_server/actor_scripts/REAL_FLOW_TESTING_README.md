# Real End-to-End Order Flow Testing

## 🎯 Overview

This is a comprehensive testing framework that **actually calls and interacts with your actor scripts** to simulate complete order flows from customer login to delivery completion. Unlike simulation-only testing, this framework:

- ✅ **Actually starts script processes** using subprocess
- ✅ **Handles real authentication** with each actor script
- ✅ **Orchestrates multi-script interactions** for complete workflows
- ✅ **Tracks real order creation and delivery** through the entire system
- ✅ **Provides detailed execution reports** with timing and success metrics

## 📁 Files Created

### Core Framework Files
1. **`end_to_end_flow_simulator.py`** - Base simulation framework
2. **`script_caller_integration.py`** - Script process management and I/O handling
3. **`complete_flow_orchestrator.py`** - Main orchestrator for real script interactions
4. **`run_real_flow_test.py`** - Simple command-line runner

### Documentation
5. **`REAL_FLOW_TESTING_README.md`** - This comprehensive guide

## 🚀 Quick Start

### 1. Basic Real Flow Test
```bash
# Navigate to actor scripts directory
cd "C:\Users\Welcome\Desktop\promodeagro-inventory-management-mcp-server\awslabs\inventory_management_mcp_server\actor_scripts"

# Run a single real order flow
python run_real_flow_test.py --batch

# Run with demo explanations
python run_real_flow_test.py --demo --batch
```

### 2. Multiple Flow Testing
```bash
# Run 3 real order flows
python run_real_flow_test.py --batch --flows 3 --save

# Run with custom customer
python run_real_flow_test.py --batch --customer CUST005 --save
```

### 3. Interactive Mode
```bash
# Start interactive mode for detailed control
python run_real_flow_test.py
```

## 🔄 Complete Order Flow Process

The framework orchestrates this complete real workflow:

### Step 1: Customer Portal - Login & Order Creation
- ✅ Starts `customer_portal_standalone.py`
- ✅ Authenticates with customer credentials
- ✅ Navigates menus to create an order
- ✅ Extracts generated Order ID

### Step 2: Inventory Staff - Order Processing
- ✅ Starts `inventory_staff_standalone.py`
- ✅ Authenticates with staff credentials
- ✅ Processes the created order
- ✅ Updates inventory allocation

### Step 3: Warehouse Manager - Order Approval
- ✅ Starts `warehouse_manager_standalone.py`
- ✅ Authenticates with manager credentials
- ✅ Approves the processed order
- ✅ Authorizes picking and packing

### Step 4: Logistics Manager - Delivery Planning
- ✅ Starts `logistics_manager_standalone.py`
- ✅ Authenticates with logistics credentials
- ✅ Plans delivery route and schedule
- ✅ Generates Delivery ID

### Step 5: Delivery Personnel - Delivery Completion
- ✅ Starts `delivery_personnel_standalone.py`
- ✅ Authenticates with delivery credentials
- ✅ Accepts delivery assignment
- ✅ Completes delivery with payment collection

## 📊 What Gets Tested

### Real Script Interactions
- **Process Management**: Starting, monitoring, and terminating script processes
- **Authentication**: Real login flows with each actor type
- **Menu Navigation**: Actual menu selections and user input simulation
- **Data Flow**: Order IDs, delivery IDs, and other data passing between actors
- **Error Handling**: Real error detection and recovery

### Performance Metrics
- **Execution Times**: How long each step and the complete flow takes
- **Success Rates**: Percentage of successful completions
- **Failure Analysis**: Detailed error reporting for failed steps
- **Resource Usage**: Script startup times and cleanup efficiency

### Business Process Validation
- **Complete Order Journey**: End-to-end order lifecycle validation
- **Actor Coordination**: Multi-actor workflow orchestration
- **Data Consistency**: Order and delivery data integrity across actors
- **Exception Handling**: Real-world error scenarios and recovery

## 🎮 Usage Examples

### Command Line Options

```bash
# Basic usage
python run_real_flow_test.py --batch

# Multiple flows with custom settings
python run_real_flow_test.py --batch --flows 5 --timeout 60 --delay 2.0

# Specific customer testing
python run_real_flow_test.py --batch --customer CUST999 --save

# Demo mode with explanations
python run_real_flow_test.py --demo --batch

# Interactive mode for detailed control
python run_real_flow_test.py
```

### Interactive Mode Features

When you run without `--batch`, you get an interactive menu:

```
🎯 COMPLETE REAL FLOW ORCHESTRATOR
============================================================
1. 🚀 Run Single Real Order Flow
2. 🔄 Run Multiple Real Order Flows  
3. 📊 View Last Results
4. 💾 Save Results to File
5. 🧹 Cleanup All Scripts
6. 📋 List Active Scripts
0. 🚪 Exit
```

This allows you to:
- Run flows with custom parameters
- Monitor active script processes
- View detailed execution reports
- Clean up resources manually
- Save results for analysis

## 📈 Sample Output

### Successful Flow Execution
```
🚀 Starting Complete Real Order Flow
📋 Session ID: REAL-E2E-20240115-143022
👤 Customer ID: CUST001

📍 Real Step 1/10: 01_start_customer_portal
🎭 Actor: Customer
🎬 Action: start_and_authenticate
🚀 Starting script instance: customer_portal_standalone.py
✅ Script customer_portal_standalone.py started with ID customer_portal_standalone.py_1705334622
✅ Real Step 01_start_customer_portal completed successfully (8.45s)

📍 Real Step 2/10: 02_create_order
🎭 Actor: Customer
🎬 Action: create_order
📋 Extracted Order ID: ORD-20240115-143035
✅ Real Step 02_create_order completed successfully (12.23s)

[... continues for all 10 steps ...]

🏁 Real Order Flow Completed!
📊 Status: COMPLETED
⏱️ Total Duration: 125.67s
📋 Order ID: ORD-20240115-143035
🚚 Delivery ID: DEL-20240115-143142
```

### Comprehensive Report
```
🎯 REAL END-TO-END ORDER FLOW EXECUTION REPORT
================================================================================
🔧 Execution Type: REAL_SCRIPT_EXECUTION
📱 Script Instances Used: 5

📊 Overall Results:
  Total Flows: 1
  ✅ Completed: 1
  ❌ Failed: 0
  📈 Success Rate: 100.0%
  ⏱️ Total Duration: 125.67s
  ⏱️ Average Flow Duration: 125.67s

📋 Step Performance Analysis:
--------------------------------------------------------------------------------
Step ID              Actor              Success Rate  Avg Time   Total
--------------------------------------------------------------------------------
01_start_customer_portal Customer        100.0%      8.45s      1
02_create_order      Customer           100.0%     12.23s      1
03_start_inventory_staff Inventory Staff 100.0%      7.89s      1
04_process_order     Inventory Staff    100.0%     15.67s      1
05_start_warehouse_manager Warehouse Manager 100.0%   8.12s      1
06_approve_order     Warehouse Manager  100.0%     11.34s      1
07_start_logistics_manager Logistics Manager 100.0%   7.98s      1
08_plan_delivery     Logistics Manager  100.0%     13.45s      1
09_start_delivery_personnel Delivery Personnel 100.0% 8.23s      1
10_complete_delivery Delivery Personnel 100.0%     18.91s      1
--------------------------------------------------------------------------------
```

## ⚙️ Configuration

### Timeout Settings
```python
# In complete_flow_orchestrator.py
self.step_timeout = 30          # seconds per step
self.inter_step_delay = 3       # seconds between steps  
self.script_startup_delay = 5   # seconds for script startup
```

### Authentication Credentials
```python
# In script_caller_integration.py
"demo_credentials": {
    "customer_id": "CUST001", 
    "password": "customer123"
}
```

### Script Interaction Patterns
The framework knows how to interact with each script type:
- Customer Portal: Handles product browsing, order creation
- Inventory Staff: Manages order processing, stock allocation
- Warehouse Manager: Handles approvals, picking authorization
- Logistics Manager: Plans routes, schedules deliveries
- Delivery Personnel: Manages delivery execution, payment collection

## 🔧 Technical Details

### Process Management
- Uses Python `subprocess` to start actual script processes
- Manages stdin/stdout/stderr communication with scripts
- Handles process termination and cleanup
- Monitors script health and status

### I/O Handling
- Threaded I/O for non-blocking communication
- Queue-based input/output management
- Real-time output capture and parsing
- Error stream monitoring and reporting

### Data Extraction
- Parses script output to extract Order IDs, Delivery IDs
- Tracks data flow between different actors
- Maintains state consistency across the workflow
- Handles data validation and error detection

### Error Recovery
- Graceful handling of script failures
- Process cleanup on errors or interruption
- Detailed error reporting and logging
- Partial flow completion tracking

## 🚨 Troubleshooting

### Common Issues

1. **Script Not Found**
   ```
   ❌ Script not found: customer_portal_standalone.py
   ```
   - Ensure all actor scripts are in the same directory
   - Check file permissions and paths

2. **Authentication Failed**
   ```
   ❌ Authentication failed for customer_portal_standalone.py
   ```
   - Verify demo credentials in the scripts
   - Check if scripts expect different authentication flow

3. **Process Timeout**
   ```
   ❌ Step timeout after 30 seconds
   ```
   - Increase timeout with `--timeout 60`
   - Check if scripts are waiting for input

4. **Script Startup Issues**
   ```
   ❌ Script failed to start properly
   ```
   - Ensure Python dependencies are installed
   - Check if AWS credentials are configured (if required)

### Debug Mode

For detailed debugging:
1. Check log files in `orchestrator_logs/`
2. Use interactive mode to monitor step-by-step
3. List active scripts to see process status
4. Review saved results for detailed error information

### Performance Optimization

- Reduce `inter_step_delay` for faster execution
- Increase `script_timeout` for complex operations
- Use batch mode for automated testing
- Run single flows first to validate setup

## 🎯 Use Cases

### Development Testing
- Validate complete order workflows
- Test actor script integration
- Verify business process flows
- Performance benchmarking

### Quality Assurance
- End-to-end regression testing
- Multi-actor coordination validation
- Error handling verification
- Load testing with multiple flows

### Production Readiness
- System integration validation
- Performance baseline establishment
- Failure scenario testing
- Deployment verification

## 🔮 Future Enhancements

### Planned Features
- **Parallel Flow Execution**: Run multiple flows simultaneously
- **Custom Scenario Scripts**: Define custom test scenarios
- **Performance Monitoring**: Real-time performance dashboards
- **Integration Testing**: Test with external systems
- **Automated Scheduling**: Scheduled test execution

### Advanced Capabilities
- **Load Testing**: High-volume flow simulation
- **Chaos Engineering**: Failure injection testing
- **Monitoring Integration**: Connect with monitoring systems
- **CI/CD Integration**: Automated pipeline testing
- **Custom Assertions**: Business rule validation

## 📞 Support

### Getting Help
1. **Check Logs**: Review `orchestrator_logs/` for detailed execution logs
2. **Interactive Mode**: Use interactive mode for step-by-step debugging
3. **Saved Results**: Analyze JSON results files for detailed metrics
4. **Script Status**: Monitor active script processes

### Best Practices
1. **Start Simple**: Begin with single flows before multiple flows
2. **Monitor Resources**: Watch for script process accumulation
3. **Clean Up**: Always clean up scripts after testing
4. **Save Results**: Keep results for trend analysis
5. **Validate Setup**: Ensure all scripts work individually first

---

## 🎉 Summary

You now have a complete **real script interaction testing framework** that:

✅ **Actually calls your actor scripts** - No simulation, real processes
✅ **Handles complete order workflows** - From login to delivery completion  
✅ **Provides comprehensive reporting** - Detailed metrics and analysis
✅ **Supports multiple execution modes** - Batch, interactive, demo
✅ **Manages script processes** - Startup, monitoring, cleanup
✅ **Tracks real data flow** - Order IDs, delivery IDs, timing
✅ **Handles errors gracefully** - Recovery, reporting, cleanup

This framework will help you validate that your complete inventory management system works end-to-end with real actor interactions!
