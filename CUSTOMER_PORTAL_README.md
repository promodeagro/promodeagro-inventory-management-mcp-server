# 🛒 Aurora Spark Customer Portal

## 📋 Overview

The Aurora Spark Customer Portal is a comprehensive e-commerce solution that provides customers with a complete shopping experience. It includes product browsing, cart management, address management, delivery slot selection, and order placement functionality.

## 🚀 Features

### 🛍️ Product Management
- **Browse Categories**: View all available product categories
- **Product Catalog**: Browse all products with filtering options
- **Product Search**: Search products by name or description
- **Product Details**: View detailed product information including variants
- **Product Variants**: Support for size, color, weight, and flavor variants

### 🛒 Shopping Cart
- **Add to Cart**: Add products with specified quantities and variants
- **View Cart**: Display cart contents with totals
- **Update Quantities**: Modify item quantities in cart
- **Remove Items**: Remove individual items or clear entire cart
- **Stock Validation**: Real-time stock checking

### 📍 Address Management
- **Multiple Addresses**: Support for home, work, and other address types
- **Address CRUD**: Create, read, update, and delete addresses
- **Default Address**: Set and manage default delivery address
- **Address Validation**: Pincode format validation
- **Address Selection**: Choose delivery address during checkout

### 🚚 Delivery Management
- **Slot Selection**: Choose from available delivery time slots
- **Pincode-based Slots**: Delivery slots filtered by pincode
- **Capacity Management**: Real-time slot availability checking
- **Delivery Charges**: Dynamic delivery charge calculation

### 📦 Order Management
- **Order Placement**: Complete checkout process with confirmation
- **Order History**: View past orders with detailed information
- **Order Tracking**: Track order status and delivery information
- **Order Totals**: Automatic calculation of cart total, delivery charges, and final amount

### 👤 User Account
- **Customer Registration**: New customer account creation
- **Secure Authentication**: Login with email and password
- **Profile Management**: Update name, phone, and password
- **Role-based Access**: Customer-specific permissions
- **Session Management**: Secure user session handling

## 🏗️ Architecture

### Database Integration
- **DynamoDB Tables**: Integrates with Aurora Spark Theme DynamoDB tables
- **Optimized Queries**: Efficient data retrieval using GSIs
- **Data Consistency**: Maintains data integrity across operations

### Security Features
- **Password Hashing**: SHA-256 password encryption
- **Role Validation**: Customer role verification
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Robust error management

## 📁 File Structure

```
awslabs/inventory_management_mcp_server/actors/
├── customer_portal.py          # Main customer portal implementation
└── ...

simulation/
├── customer_portal_simulator.py # Testing and simulation script
└── ...
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- AWS Account with DynamoDB access
- Configured AWS credentials
- Aurora Spark Theme DynamoDB tables

### Installation
1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Ensure DynamoDB tables are set up:
   ```bash
   python awslabs/inventory_management_mcp_server/dataDesign/setup_optimized_aurora_spark_dynamodb.py
   ```

### Running the Customer Portal
```bash
python awslabs/inventory_management_mcp_server/actors/customer_portal.py
```

### Running the Simulation
```bash
python simulation/customer_portal_simulator.py
```

## 🎯 Usage Guide

### 1. Customer Registration
```python
# New customers can register with:
# - First Name, Last Name
# - Email (unique identifier)
# - Phone number
# - Password (securely hashed)
```

### 2. Product Browsing
```python
# Browse products by:
# - Category filtering
# - Search functionality
# - View all products
# - Product detail viewing
```

### 3. Shopping Cart Management
```python
# Cart operations:
portal.add_to_cart(product_id, quantity, variant_id)
portal.view_cart()
portal.update_cart_quantity(item_index, new_quantity)
portal.remove_from_cart(item_index)
```

### 4. Address Management
```python
# Address operations:
portal.add_address()
portal.view_addresses()
portal.edit_address()
portal.delete_address()
portal.set_default_address()
```

### 5. Order Placement
```python
# Complete checkout process:
# 1. Select delivery address
# 2. Choose delivery slot
# 3. Review order summary
# 4. Confirm and place order
```

## 🔧 Configuration

### DynamoDB Tables Used
- `AuroraSparkTheme-Users`: User authentication and profiles
- `AuroraSparkTheme-Products`: Product catalog and variants
- `AuroraSparkTheme-Inventory`: Stock levels and availability
- `AuroraSparkTheme-Orders`: Customer orders and history
- `AuroraSparkTheme-Delivery`: Delivery slots and scheduling
- `AuroraSparkTheme-System`: System settings and configurations

### Environment Variables
```bash
AWS_REGION=ap-south-1  # Default region
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🧪 Testing

### Manual Testing
Run the customer portal and test each feature:
```bash
python awslabs/inventory_management_mcp_server/actors/customer_portal.py
```

### Automated Simulation
Run the simulation script to test all features:
```bash
python simulation/customer_portal_simulator.py
```

### Test Scenarios
1. **Registration Flow**: New customer registration
2. **Authentication**: Login/logout functionality
3. **Product Browsing**: Category and search operations
4. **Cart Management**: Add, update, remove operations
5. **Address Management**: CRUD operations
6. **Order Placement**: Complete checkout flow
7. **Profile Management**: User account updates

## 🔍 API Reference

### Core Classes

#### CustomerPortal
Main class providing all customer functionality.

**Key Methods:**
- `authenticate_user(email, password)`: User authentication
- `register_customer()`: New customer registration
- `list_products(category, search_term)`: Product listing
- `add_to_cart(product_id, quantity, variant_id)`: Cart management
- `manage_addresses()`: Address operations
- `place_order()`: Order placement

### Data Models

#### User Profile
```python
{
    'userID': str,
    'email': str,
    'firstName': str,
    'lastName': str,
    'phone': str,
    'addresses': [Address],
    'roles': [Role]
}
```

#### Cart Item
```python
{
    'product_id': str,
    'variant_id': str,
    'name': str,
    'price': Decimal,
    'quantity': int,
    'total': Decimal
}
```

#### Address
```python
{
    'id': str,
    'type': str,
    'addressLine1': str,
    'addressLine2': str,
    'city': str,
    'state': str,
    'pincode': str,
    'isDefault': bool
}
```

## 🚨 Error Handling

### Common Errors
- **Authentication Failed**: Invalid credentials or inactive account
- **Product Not Found**: Invalid product ID
- **Insufficient Stock**: Requested quantity exceeds available stock
- **Invalid Address**: Missing required address fields
- **No Delivery Slots**: No available slots for selected pincode

### Error Messages
All errors are displayed with descriptive messages and appropriate error codes.

## 🔒 Security Considerations

### Password Security
- Passwords are hashed using SHA-256
- No plain text password storage
- Password confirmation during registration

### Access Control
- Role-based access (customer role required)
- User session validation
- Input sanitization and validation

### Data Protection
- Secure DynamoDB operations
- Error message sanitization
- User data privacy protection

## 📈 Performance Optimization

### Database Optimization
- Efficient DynamoDB queries using GSIs
- Batch operations where applicable
- Connection pooling and reuse

### Caching Strategy
- In-memory cart storage
- Session-based user data caching
- Product catalog caching

## 🛠️ Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```
   Solution: Configure AWS credentials using `aws configure`
   ```

2. **DynamoDB Table Not Found**
   ```
   Solution: Run the table setup script first
   ```

3. **Permission Denied**
   ```
   Solution: Ensure IAM user has DynamoDB permissions
   ```

4. **Connection Timeout**
   ```
   Solution: Check internet connection and AWS region
   ```

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=true
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include error handling
- Write unit tests for new features

## 📄 License

This project is part of the Aurora Spark Theme inventory management system.

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review the simulation output
- Verify AWS configuration
- Ensure all dependencies are installed

---

**Aurora Spark Theme - Customer Portal**  
*Complete E-commerce Customer Experience*
