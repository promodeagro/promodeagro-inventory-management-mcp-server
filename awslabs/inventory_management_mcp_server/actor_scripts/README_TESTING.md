# Actor Scripts Testing Suite

A comprehensive testing framework for simulating and validating all actor scripts in the inventory management system.

## Overview

This testing suite provides automated testing capabilities for all actor scripts including:
- Customer Portal
- Inventory Staff
- Super Admin
- Warehouse Manager
- Delivery Personnel
- Logistics Manager
- Supplier Portal
- Auditor
- Authentication Manager
- API Services

## Features

- **Comprehensive Testing**: Tests all major functionalities of each actor script
- **Simulated Interactions**: Simulates real-world usage scenarios without requiring actual AWS resources
- **Parallel Execution**: Runs tests in parallel for faster execution
- **Detailed Reporting**: Generates comprehensive reports with metrics and error details
- **Result Persistence**: Saves test results to JSON files for historical analysis
- **Interactive Mode**: Provides an interactive menu for selective testing
- **Batch Mode**: Supports automated batch execution for CI/CD pipelines

## Files

- `actor_testing_simulator.py` - Main testing framework
- `run_actor_tests.py` - Simple batch runner script
- `README_TESTING.md` - This documentation file

## Quick Start

### Basic Usage

```bash
# Run all tests interactively
python run_actor_tests.py

# Run all tests in batch mode
python run_actor_tests.py --batch

# Run tests and save results
python run_actor_tests.py --batch --save
```

### Advanced Usage

```bash
# Run quick tests only (skip long-running tests)
python run_actor_tests.py --quick

# Test specific script
python run_actor_tests.py --script customer

# Run tests sequentially (not parallel)
python run_actor_tests.py --no-parallel

# Set custom timeout
python run_actor_tests.py --timeout 60

# Custom output directory
python run_actor_tests.py --batch --save --output-dir ./my_results
```

## Test Categories

### 1. Connection Tests
- AWS connectivity validation
- DynamoDB table access verification
- Service availability checks

### 2. Authentication Tests
- User login simulation
- Role-based access validation
- Session management testing

### 3. Functional Tests
- Core functionality simulation
- Business logic validation
- Error handling verification

### 4. Integration Tests
- Inter-service communication
- Data flow validation
- API endpoint testing

### 5. Performance Tests
- Execution time measurement
- Resource usage monitoring
- Scalability assessment

## Test Results

### Result Structure

Each test result contains:
- Script name and test case
- Execution status (PASS/FAIL/SKIP/ERROR)
- Execution time
- Error messages (if any)
- Output details
- Timestamp

### Result Files

Test results are saved in JSON format in the `test_results/` directory:

```json
{
  "session_info": {
    "session_id": "TEST-20240115-143022",
    "timestamp": "2024-01-15T14:30:22Z",
    "scripts_directory": "/path/to/scripts",
    "aws_available": true
  },
  "summary": {
    "total_tests": 75,
    "passed": 68,
    "failed": 5,
    "skipped": 2,
    "success_rate": 90.7
  },
  "detailed_results": [...]
}
```

## Interactive Mode

The interactive mode provides a menu-driven interface:

```
🧪 ACTOR SCRIPTS TESTING SIMULATOR
============================================================
1. 🚀 Run All Tests
2. 🎯 Run Specific Script Tests
3. 📊 View Last Results Summary
4. 💾 Save Results to File
5. 📁 View Test History
6. ⚙️ Configuration
0. 🚪 Exit
```

### Features:
- Selective script testing
- Real-time result viewing
- Historical result analysis
- Configuration management
- Result export options

## Configuration

### Test Timeout
Default: 30 seconds per test
Can be configured via command line or interactive mode.

### AWS Dependency
Tests automatically detect AWS availability and skip AWS-dependent tests if not available.

### Parallel Execution
Default: Enabled (4 concurrent workers)
Can be disabled for sequential execution.

## Test Cases by Script

### Customer Portal (`customer_portal_standalone.py`)
- AWS connection test
- Customer authentication
- Demo customer creation
- Product browsing simulation
- Order placement simulation
- Order history retrieval
- Profile management test

### Inventory Staff (`inventory_staff_standalone.py`)
- AWS connection test
- Staff authentication
- Inventory tracking
- Stock level management
- Product management
- Order processing
- Report generation

### Super Admin (`super_admin_standalone.py`)
- AWS connection test
- Admin authentication
- User management
- System configuration
- Audit log review
- System health check
- Backup/restore operations

### Warehouse Manager (`warehouse_manager_standalone.py`)
- AWS connection test
- Manager authentication
- Warehouse operations
- Inventory optimization
- Supplier coordination
- Staff management
- Performance analytics

### Delivery Personnel (`delivery_personnel_standalone.py`)
- AWS connection test
- Personnel authentication
- Delivery assignment
- Route optimization
- Delivery status updates
- Cash collection
- Feedback submission

### Logistics Manager (`logistics_manager_standalone.py`)
- AWS connection test
- Logistics authentication
- Route planning
- Delivery scheduling
- Fleet management
- Performance tracking
- Cost optimization

### Supplier Portal (`supplier_portal_standalone.py`)
- AWS connection test
- Supplier authentication
- Product catalog management
- Order fulfillment
- Inventory updates
- Payment tracking
- Communication systems

### Auditor (`auditor_standalone.py`)
- AWS connection test
- Auditor authentication
- Audit trail analysis
- Compliance checking
- Financial auditing
- Security auditing
- Report generation

### Authentication Manager (`auth_manager.py`)
- AWS connection test
- User creation
- Authentication validation
- Role management
- Permission validation
- Session management

### API Services
- API initialization
- Endpoint testing
- Data validation
- Error handling
- Performance testing

## Troubleshooting

### Common Issues

1. **AWS Connection Failed**
   - Ensure AWS credentials are configured
   - Check internet connectivity
   - Verify region settings

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify file permissions

3. **Test Timeouts**
   - Increase timeout value
   - Check system performance
   - Run tests sequentially

### Debug Mode

For detailed debugging, check the log files in `test_logs/` directory:
- `actor_tests_[SESSION_ID].log`

### Error Analysis

Failed tests include detailed error messages and stack traces in the results file.

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Actor Scripts Testing
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run Actor Tests
      run: |
        cd awslabs/inventory_management_mcp_server/actor_scripts
        python run_actor_tests.py --batch --save --quick
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: awslabs/inventory_management_mcp_server/actor_scripts/test_results/
```

## Performance Metrics

The testing suite tracks:
- Individual test execution times
- Total suite execution time
- Success/failure rates
- Resource usage patterns
- Historical performance trends

## Future Enhancements

- Load testing capabilities
- Integration with monitoring systems
- Automated performance regression detection
- Custom test case definitions
- Real-time result streaming
- Integration with external reporting tools

## Support

For issues or questions:
1. Check the log files for detailed error information
2. Review the test results JSON for specific failure details
3. Use the interactive mode for step-by-step debugging
4. Examine individual script implementations for context

## License

This testing suite is part of the ProModeAgro Inventory Management System.
