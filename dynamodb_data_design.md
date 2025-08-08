# DynamoDB Data Design - Inventory Management System

## Table of Contents
1. [Data Model Overview](#data-model-overview)
2. [Core Tables](#core-tables)
3. [Additional Business Tables](#additional-business-tables)
4. [Access Patterns](#access-patterns)
5. [GSI (Global Secondary Index) Design](#gsi-design)
6. [Data Relationships](#data-relationships)
7. [Partition Key Strategy](#partition-key-strategy)
8. [Implementation Guidelines](#implementation-guidelines)

---

## Data Model Overview

### Design Principles
- **Single Table Design**: Leverage DynamoDB's single table design for efficient queries
- **Composite Keys**: Use composite partition keys for better data distribution
- **GSI Optimization**: Strategic use of GSIs for different access patterns
- **Time-based Sorting**: Use sort keys for time-based queries and FIFO/LIFO operations
- **Batch Operations**: Optimize for batch reads/writes for inventory operations

### Core Entities
1. **Products** - Product catalog and inventory
2. **Batches** - Batch tracking and expiry management
3. **Suppliers** - Supplier information and performance
4. **Purchase Orders** - Procurement workflow
5. **Orders** - Customer orders and fulfillment
6. **Deliveries** - Delivery management and tracking
7. **Stock Adjustments** - Inventory modifications
8. **Cash Collections** - Payment tracking and reconciliation
9. **Customers** - Customer information and preferences
10. **Riders** - Delivery personnel management
11. **Discounts** - Discount and promotion management
12. **Pricing Rules** - Dynamic pricing and cost management
13. **Categories** - Product categorization
14. **Locations** - Warehouse and delivery zone management

---

## Core Tables

### 1. Main Inventory Table (InventoryTable)

**Table Name:** `InventoryTable`

**Primary Key Structure:**
- **Partition Key (PK):** `ENTITY#<entity_type>#<entity_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

**Entity Types:**
- `PRODUCT` - Product information
- `BATCH` - Batch information
- `SUPPLIER` - Supplier information
- `PO` - Purchase Order
- `ORDER` - Customer Order
- `DELIVERY` - Delivery information
- `ADJUSTMENT` - Stock adjustments
- `COLLECTION` - Cash collections
- `CUSTOMER` - Customer information
- `RIDER` - Rider information
- `DISCOUNT` - Discount and promotion rules
- `PRICING` - Pricing rules and cost management
- `CATEGORY` - Product categories
- `LOCATION` - Warehouse and delivery zones

**Sample Records:**

```json
// Product Record
{
  "PK": "ENTITY#PRODUCT#PROD001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "productId": "PROD001",
  "name": "Fresh Tomatoes",
  "description": "Organic red tomatoes",
  "category": "VEGETABLES",
  "brand": "Organic Farms",
  "unit": "KG",
  "costPrice": 45.00,
  "sellingPrice": 60.00,
  "minStock": 100,
  "reorderPoint": 150,
  "supplierId": "SUPP001",
  "expiryTracking": true,
  "batchRequired": true,
  "storageLocation": "COLD_STORAGE_A",
  "specialHandling": "TEMPERATURE_CONTROLLED",
  "images": ["url1", "url2"],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Batch Record
{
  "PK": "ENTITY#BATCH#BATCH001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "batchId": "BATCH001",
  "productId": "PROD001",
  "batchNumber": "TOMATO-2024-001",
  "manufacturingDate": "2024-01-01",
  "expiryDate": "2024-01-15",
  "initialQuantity": 500,
  "currentQuantity": 450,
  "supplierId": "SUPP001",
  "qualityStatus": "GOOD",
  "temperature": 4.5,
  "location": "COLD_STORAGE_A",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Stock Level Record
{
  "PK": "ENTITY#PRODUCT#PROD001",
  "SK": "METADATA#STOCK#2024-01-01T00:00:00Z",
  "productId": "PROD001",
  "totalStock": 1200,
  "availableStock": 1100,
  "reservedStock": 100,
  "damagedStock": 50,
  "expiredStock": 0,
  "lastUpdated": "2024-01-01T00:00:00Z"
}

// Purchase Order Record
{
  "PK": "ENTITY#PO#PO001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "poId": "PO001",
  "supplierId": "SUPP001",
  "status": "APPROVED",
  "totalAmount": 50000.00,
  "deliveryDate": "2024-01-05",
  "createdBy": "USER001",
  "approvedBy": "USER002",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// PO Item Record
{
  "PK": "ENTITY#PO#PO001",
  "SK": "METADATA#ITEM#PROD001",
  "poId": "PO001",
  "productId": "PROD001",
  "quantity": 1000,
  "unitPrice": 45.00,
  "totalPrice": 45000.00,
  "receivedQuantity": 0,
  "status": "PENDING"
}

// Customer Order Record
{
  "PK": "ENTITY#ORDER#ORD001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "orderId": "ORD001",
  "customerId": "CUST001",
  "customerName": "John Doe",
  "customerPhone": "+919876543210",
  "deliveryAddress": "123 Main St, Mumbai",
  "status": "PICKING",
  "totalAmount": 1200.00,
  "discountAmount": 100.00,
  "finalAmount": 1100.00,
  "paymentMethod": "CASH_ON_DELIVERY",
  "paymentStatus": "PENDING",
  "deliverySlot": "2024-01-02T10:00:00Z",
  "riderId": "RIDER001",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Order Item Record
{
  "PK": "ENTITY#ORDER#ORD001",
  "SK": "METADATA#ITEM#PROD001",
  "orderId": "ORD001",
  "productId": "PROD001",
  "quantity": 2,
  "unitPrice": 60.00,
  "discountPercentage": 10,
  "discountAmount": 12.00,
  "finalPrice": 48.00,
  "totalPrice": 96.00,
  "batchId": "BATCH001"
}

// Stock Adjustment Record
{
  "PK": "ENTITY#ADJUSTMENT#ADJ001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "adjustmentId": "ADJ001",
  "productId": "PROD001",
  "batchId": "BATCH001",
  "adjustmentType": "DAMAGE",
  "quantity": -50,
  "reason": "Damaged during handling",
  "approvedBy": "USER001",
  "photoUrl": "url_to_photo",
  "createdAt": "2024-01-01T00:00:00Z"
}

// Delivery Record
{
  "PK": "ENTITY#DELIVERY#DEL001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "deliveryId": "DEL001",
  "orderId": "ORD001",
  "riderId": "RIDER001",
  "status": "IN_TRANSIT",
  "pickupTime": "2024-01-02T09:00:00Z",
  "estimatedDeliveryTime": "2024-01-02T10:00:00Z",
  "actualDeliveryTime": null,
  "signatureUrl": null,
  "photoUrl": null,
  "cashCollected": 0,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Cash Collection Record
{
  "PK": "ENTITY#COLLECTION#COL001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "collectionId": "COL001",
  "riderId": "RIDER001",
  "date": "2024-01-01",
  "totalCollected": 5000.00,
  "cashCollected": 3000.00,
  "digitalCollected": 2000.00,
  "ordersDelivered": 25,
  "status": "PENDING_SETTLEMENT",
  "settledAt": null,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Customer Record
{
  "PK": "ENTITY#CUSTOMER#CUST001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "customerId": "CUST001",
  "name": "John Doe",
  "phone": "+919876543210",
  "email": "john.doe@email.com",
  "address": "123 Main St, Mumbai",
  "pincode": "400001",
  "customerType": "REGULAR",
  "loyaltyPoints": 150,
  "totalOrders": 25,
  "totalSpent": 15000.00,
  "preferredPaymentMethod": "CASH_ON_DELIVERY",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Rider Record
{
  "PK": "ENTITY#RIDER#RIDER001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "riderId": "RIDER001",
  "name": "Amit Kumar",
  "phone": "+919876543213",
  "email": "amit.kumar@company.com",
  "vehicleNumber": "MH01AB1234",
  "vehicleType": "BIKE",
  "status": "ACTIVE",
  "currentLocation": "19.0760,72.8777",
  "assignedZone": "MUMBAI_CENTRAL",
  "rating": 4.5,
  "totalDeliveries": 150,
  "totalEarnings": 25000.00,
  "isAvailable": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Discount Record
{
  "PK": "ENTITY#DISCOUNT#DISC001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "discountId": "DISC001",
  "name": "New Customer Discount",
  "description": "10% off for first order",
  "discountType": "PERCENTAGE",
  "discountValue": 10,
  "minOrderAmount": 500,
  "maxDiscountAmount": 200,
  "applicableProducts": ["ALL"],
  "applicableCategories": ["VEGETABLES", "FRUITS"],
  "customerTypes": ["NEW"],
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "usageLimit": 1,
  "usedCount": 0,
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Pricing Rule Record
{
  "PK": "ENTITY#PRICING#PRICE001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "pricingId": "PRICE001",
  "productId": "PROD001",
  "ruleType": "DYNAMIC_PRICING",
  "basePrice": 60.00,
  "minPrice": 45.00,
  "maxPrice": 80.00,
  "factors": {
    "demand": "HIGH",
    "season": "PEAK",
    "competition": "MEDIUM"
  },
  "effectiveDate": "2024-01-01",
  "expiryDate": "2024-12-31",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Category Record
{
  "PK": "ENTITY#CATEGORY#VEGETABLES",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "categoryId": "VEGETABLES",
  "name": "Vegetables",
  "description": "Fresh vegetables",
  "parentCategory": null,
  "icon": "vegetables-icon",
  "sortOrder": 1,
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Location Record
{
  "PK": "ENTITY#LOCATION#MUMBAI_CENTRAL",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "locationId": "MUMBAI_CENTRAL",
  "name": "Mumbai Central",
  "type": "DELIVERY_ZONE",
  "pincodes": ["400001", "400002", "400003"],
  "deliveryCharge": 50.00,
  "minOrderAmount": 200.00,
  "deliverySlots": ["09:00-12:00", "14:00-17:00", "18:00-21:00"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 2. Supplier Table (SupplierTable)

**Table Name:** `SupplierTable`

**Primary Key Structure:**
- **Partition Key (PK):** `SUPPLIER#<supplier_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// Supplier Info
{
  "PK": "SUPPLIER#SUPP001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "supplierId": "SUPP001",
  "name": "Fresh Produce Co.",
  "contactPerson": "Rajesh Kumar",
  "phone": "+919876543210",
  "email": "rajesh@freshproduce.com",
  "address": "123 Farm Road, Pune",
  "paymentTerms": "NET_30",
  "rating": 4.5,
  "leadTime": 2,
  "qualityStandards": "ORGANIC_CERTIFIED",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Supplier Performance
{
  "PK": "SUPPLIER#SUPP001",
  "SK": "METADATA#PERFORMANCE#2024-01-01T00:00:00Z",
  "supplierId": "SUPP001",
  "month": "2024-01",
  "ordersDelivered": 15,
  "onTimeDelivery": 14,
  "qualityScore": 4.8,
  "costSavings": 5000.00,
  "totalSpend": 50000.00
}
```

### 3. User Table (UserTable)

**Table Name:** `UserTable`

**Primary Key Structure:**
- **Partition Key (PK):** `USER#<user_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// User Info
{
  "PK": "USER#USER001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "userId": "USER001",
  "name": "Amit Patel",
  "email": "amit@company.com",
  "phone": "+919876543210",
  "role": "WAREHOUSE_MANAGER",
  "permissions": ["INVENTORY_READ", "INVENTORY_WRITE", "ADJUSTMENT_APPROVE"],
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// User Activity
{
  "PK": "USER#USER001",
  "SK": "METADATA#ACTIVITY#2024-01-01T10:30:00Z",
  "userId": "USER001",
  "action": "STOCK_ADJUSTMENT",
  "entityId": "ADJ001",
  "details": "Created stock adjustment for damaged tomatoes",
  "timestamp": "2024-01-01T10:30:00Z"
}
```

---

## Additional Business Tables

### 4. Discount Management Table (DiscountTable)

**Table Name:** `DiscountTable`

**Primary Key Structure:**
- **Partition Key (PK):** `DISCOUNT#<discount_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// Discount Rules
{
  "PK": "DISCOUNT#DISC001",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "discountId": "DISC001",
  "name": "New Customer Discount",
  "description": "10% off for first order",
  "discountType": "PERCENTAGE",
  "discountValue": 10,
  "minOrderAmount": 500,
  "maxDiscountAmount": 200,
  "applicableProducts": ["ALL"],
  "applicableCategories": ["VEGETABLES", "FRUITS"],
  "customerTypes": ["NEW"],
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "usageLimit": 1,
  "usedCount": 0,
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Discount Usage
{
  "PK": "DISCOUNT#DISC001",
  "SK": "METADATA#USAGE#CUST001#2024-01-01T10:30:00Z",
  "discountId": "DISC001",
  "customerId": "CUST001",
  "orderId": "ORD001",
  "discountAmount": 100.00,
  "usedAt": "2024-01-01T10:30:00Z"
}

// Bulk Discount
{
  "PK": "DISCOUNT#DISC002",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "discountId": "DISC002",
  "name": "Bulk Purchase Discount",
  "description": "15% off on orders above 1000",
  "discountType": "PERCENTAGE",
  "discountValue": 15,
  "minOrderAmount": 1000,
  "maxDiscountAmount": 500,
  "applicableProducts": ["ALL"],
  "applicableCategories": ["ALL"],
  "customerTypes": ["ALL"],
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "usageLimit": -1,
  "usedCount": 0,
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Product Specific Discount
{
  "PK": "DISCOUNT#DISC003",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "discountId": "DISC003",
  "name": "Tomato Special",
  "description": "20% off on tomatoes",
  "discountType": "PERCENTAGE",
  "discountValue": 20,
  "minOrderAmount": 0,
  "maxDiscountAmount": 100,
  "applicableProducts": ["PROD001"],
  "applicableCategories": ["VEGETABLES"],
  "customerTypes": ["ALL"],
  "startDate": "2024-01-01",
  "endDate": "2024-01-15",
  "usageLimit": -1,
  "usedCount": 0,
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 5. Pricing Rules Table (PricingTable)

**Table Name:** `PricingTable`

**Primary Key Structure:**
- **Partition Key (PK):** `PRICING#<pricing_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// Dynamic Pricing Rule
{
  "PK": "PRICING#PRICE001",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "pricingId": "PRICE001",
  "productId": "PROD001",
  "ruleType": "DYNAMIC_PRICING",
  "basePrice": 60.00,
  "minPrice": 45.00,
  "maxPrice": 80.00,
  "factors": {
    "demand": "HIGH",
    "season": "PEAK",
    "competition": "MEDIUM"
  },
  "effectiveDate": "2024-01-01",
  "expiryDate": "2024-12-31",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Seasonal Pricing
{
  "PK": "PRICING#PRICE002",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "pricingId": "PRICE002",
  "productId": "PROD002",
  "ruleType": "SEASONAL_PRICING",
  "basePrice": 50.00,
  "seasonalMultiplier": 1.2,
  "season": "SUMMER",
  "effectiveDate": "2024-03-01",
  "expiryDate": "2024-08-31",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Bulk Pricing
{
  "PK": "PRICING#PRICE003",
  "SK": "METADATA#RULE#2024-01-01T00:00:00Z",
  "pricingId": "PRICE003",
  "productId": "PROD003",
  "ruleType": "BULK_PRICING",
  "basePrice": 40.00,
  "tiers": [
    {"minQty": 1, "maxQty": 5, "price": 40.00},
    {"minQty": 6, "maxQty": 10, "price": 35.00},
    {"minQty": 11, "maxQty": 999, "price": 30.00}
  ],
  "effectiveDate": "2024-01-01",
  "expiryDate": "2024-12-31",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}
```

### 6. Customer Management Table (CustomerTable)

**Table Name:** `CustomerTable`

**Primary Key Structure:**
- **Partition Key (PK):** `CUSTOMER#<customer_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// Customer Info
{
  "PK": "CUSTOMER#CUST001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "customerId": "CUST001",
  "name": "John Doe",
  "phone": "+919876543210",
  "email": "john.doe@email.com",
  "address": "123 Main St, Mumbai",
  "pincode": "400001",
  "customerType": "REGULAR",
  "loyaltyPoints": 150,
  "totalOrders": 25,
  "totalSpent": 15000.00,
  "preferredPaymentMethod": "CASH_ON_DELIVERY",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Customer Preferences
{
  "PK": "CUSTOMER#CUST001",
  "SK": "METADATA#PREFERENCES#2024-01-01T00:00:00Z",
  "customerId": "CUST001",
  "preferredCategories": ["VEGETABLES", "FRUITS"],
  "preferredDeliveryTime": "MORNING",
  "preferredPaymentMethod": "CASH_ON_DELIVERY",
  "communicationPreferences": ["SMS", "EMAIL"],
  "dietaryRestrictions": ["VEGETARIAN"],
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Customer Loyalty
{
  "PK": "CUSTOMER#CUST001",
  "SK": "METADATA#LOYALTY#2024-01-01T00:00:00Z",
  "customerId": "CUST001",
  "loyaltyPoints": 150,
  "pointsEarned": 200,
  "pointsRedeemed": 50,
  "tier": "SILVER",
  "nextTier": "GOLD",
  "pointsToNextTier": 350,
  "lastUpdated": "2024-01-01T00:00:00Z"
}
```

### 7. Rider Management Table (RiderTable)

**Table Name:** `RiderTable`

**Primary Key Structure:**
- **Partition Key (PK):** `RIDER#<rider_id>`
- **Sort Key (SK):** `METADATA#<metadata_type>#<timestamp>`

```json
// Rider Info
{
  "PK": "RIDER#RIDER001",
  "SK": "METADATA#INFO#2024-01-01T00:00:00Z",
  "riderId": "RIDER001",
  "name": "Amit Kumar",
  "phone": "+919876543213",
  "email": "amit.kumar@company.com",
  "vehicleNumber": "MH01AB1234",
  "vehicleType": "BIKE",
  "status": "ACTIVE",
  "currentLocation": "19.0760,72.8777",
  "assignedZone": "MUMBAI_CENTRAL",
  "rating": 4.5,
  "totalDeliveries": 150,
  "totalEarnings": 25000.00,
  "isAvailable": true,
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z"
}

// Rider Performance
{
  "PK": "RIDER#RIDER001",
  "SK": "METADATA#PERFORMANCE#2024-01-01T00:00:00Z",
  "riderId": "RIDER001",
  "month": "2024-01",
  "deliveriesCompleted": 45,
  "onTimeDeliveries": 42,
  "averageRating": 4.5,
  "totalEarnings": 5000.00,
  "incentivesEarned": 500.00,
  "createdAt": "2024-01-01T00:00:00Z"
}

// Rider Schedule
{
  "PK": "RIDER#RIDER001",
  "SK": "METADATA#SCHEDULE#2024-01-01T00:00:00Z",
  "riderId": "RIDER001",
  "date": "2024-01-01",
  "shiftStart": "09:00",
  "shiftEnd": "18:00",
  "assignedZone": "MUMBAI_CENTRAL",
  "isAvailable": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
```

---

## GSI (Global Secondary Index) Design

### GSI1: Product Category Index
**Index Name:** `ProductCategoryIndex`
- **Partition Key:** `category`
- **Sort Key:** `updatedAt`

**Use Cases:**
- List products by category
- Find recently updated products in a category

### GSI2: Batch Expiry Index
**Index Name:** `BatchExpiryIndex`
- **Partition Key:** `expiryDate`
- **Sort Key:** `productId`

**Use Cases:**
- Find batches expiring soon
- FIFO/LIFO batch selection

### GSI3: Order Status Index
**Index Name:** `OrderStatusIndex`
- **Partition Key:** `status`
- **Sort Key:** `createdAt`

**Use Cases:**
- Find orders by status (PENDING, PICKING, PACKED, etc.)
- Track order processing

### GSI4: Delivery Date Index
**Index Name:** `DeliveryDateIndex`
- **Partition Key:** `deliveryDate`
- **Sort Key:** `orderId`

**Use Cases:**
- Find deliveries for a specific date
- Route planning

### GSI5: Supplier Performance Index
**Index Name:** `SupplierPerformanceIndex`
- **Partition Key:** `supplierId`
- **Sort Key:** `month`

**Use Cases:**
- Track supplier performance over time
- Supplier evaluation

### GSI6: Discount Active Index
**Index Name:** `DiscountActiveIndex`
- **Partition Key:** `isActive`
- **Sort Key:** `endDate`

**Use Cases:**
- Find active discounts
- Expired discount cleanup

### GSI7: Customer Type Index
**Index Name:** `CustomerTypeIndex`
- **Partition Key:** `customerType`
- **Sort Key:** `totalSpent`

**Use Cases:**
- Find customers by type (NEW, REGULAR, PREMIUM)
- Customer segmentation

### GSI8: Rider Zone Index
**Index Name:** `RiderZoneIndex`
- **Partition Key:** `assignedZone`
- **Sort Key:** `isAvailable`

**Use Cases:**
- Find available riders in a zone
- Rider assignment

---

## Access Patterns

### 1. Product Management
```javascript
// Get product details
const product = await dynamodb.get({
  TableName: 'InventoryTable',
  Key: {
    PK: 'ENTITY#PRODUCT#PROD001',
    SK: 'METADATA#INFO#2024-01-01T00:00:00Z'
  }
});

// Get products by category
const products = await dynamodb.query({
  TableName: 'InventoryTable',
  IndexName: 'ProductCategoryIndex',
  KeyConditionExpression: 'category = :category',
  ExpressionAttributeValues: {
    ':category': 'VEGETABLES'
  }
});

// Get product stock levels
const stockLevels = await dynamodb.query({
  TableName: 'InventoryTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'ENTITY#PRODUCT#PROD001',
    ':sk': 'METADATA#STOCK#'
  }
});
```

### 2. Inventory Operations
```javascript
// Get batches expiring soon
const expiringBatches = await dynamodb.query({
  TableName: 'InventoryTable',
  IndexName: 'BatchExpiryIndex',
  KeyConditionExpression: 'expiryDate BETWEEN :start AND :end',
  ExpressionAttributeValues: {
    ':start': '2024-01-01',
    ':end': '2024-01-15'
  }
});

// Get stock adjustments for a product
const adjustments = await dynamodb.query({
  TableName: 'InventoryTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'ENTITY#PRODUCT#PROD001',
    ':sk': 'METADATA#ADJUSTMENT#'
  }
});
```

### 3. Procurement Operations
```javascript
// Get purchase orders by status
const pendingPOs = await dynamodb.query({
  TableName: 'InventoryTable',
  IndexName: 'OrderStatusIndex',
  KeyConditionExpression: 'status = :status',
  ExpressionAttributeValues: {
    ':status': 'PENDING'
  }
});

// Get PO items
const poItems = await dynamodb.query({
  TableName: 'InventoryTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'ENTITY#PO#PO001',
    ':sk': 'METADATA#ITEM#'
  }
});
```

### 4. Order Fulfillment
```javascript
// Get orders by status
const pickingOrders = await dynamodb.query({
  TableName: 'InventoryTable',
  IndexName: 'OrderStatusIndex',
  KeyConditionExpression: 'status = :status',
  ExpressionAttributeValues: {
    ':status': 'PICKING'
  }
});

// Get deliveries for today
const todayDeliveries = await dynamodb.query({
  TableName: 'InventoryTable',
  IndexName: 'DeliveryDateIndex',
  KeyConditionExpression: 'deliveryDate = :date',
  ExpressionAttributeValues: {
    ':date': '2024-01-02'
  }
});
```

### 5. Discount Management
```javascript
// Get active discounts
const activeDiscounts = await dynamodb.query({
  TableName: 'DiscountTable',
  IndexName: 'DiscountActiveIndex',
  KeyConditionExpression: 'isActive = :active',
  ExpressionAttributeValues: {
    ':active': true
  }
});

// Get applicable discounts for customer
const applicableDiscounts = await dynamodb.query({
  TableName: 'DiscountTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  FilterExpression: 'customerTypes = :customerType AND :currentDate BETWEEN startDate AND endDate',
  ExpressionAttributeValues: {
    ':pk': 'DISCOUNT#DISC001',
    ':sk': 'METADATA#RULE#',
    ':customerType': 'NEW',
    ':currentDate': '2024-01-01'
  }
});
```

### 6. Customer Management
```javascript
// Get customers by type
const regularCustomers = await dynamodb.query({
  TableName: 'CustomerTable',
  IndexName: 'CustomerTypeIndex',
  KeyConditionExpression: 'customerType = :type',
  ExpressionAttributeValues: {
    ':type': 'REGULAR'
  }
});

// Get customer loyalty info
const customerLoyalty = await dynamodb.query({
  TableName: 'CustomerTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'CUSTOMER#CUST001',
    ':sk': 'METADATA#LOYALTY#'
  }
});
```

### 7. Rider Management
```javascript
// Get available riders in zone
const availableRiders = await dynamodb.query({
  TableName: 'RiderTable',
  IndexName: 'RiderZoneIndex',
  KeyConditionExpression: 'assignedZone = :zone AND isAvailable = :available',
  ExpressionAttributeValues: {
    ':zone': 'MUMBAI_CENTRAL',
    ':available': true
  }
});

// Get rider performance
const riderPerformance = await dynamodb.query({
  TableName: 'RiderTable',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'RIDER#RIDER001',
    ':sk': 'METADATA#PERFORMANCE#'
  }
});
```

---

## Data Relationships

### 1. Product → Batch Relationship
- Product PK: `ENTITY#PRODUCT#PROD001`
- Batch PK: `ENTITY#BATCH#BATCH001`
- Batch contains `productId` reference

### 2. Product → Supplier Relationship
- Product contains `supplierId`
- Supplier info stored in separate table

### 3. Order → Order Items Relationship
- Order PK: `ENTITY#ORDER#ORD001`
- Order Items SK: `METADATA#ITEM#PROD001`

### 4. PO → PO Items Relationship
- PO PK: `ENTITY#PO#PO001`
- PO Items SK: `METADATA#ITEM#PROD001`

### 5. Customer → Order Relationship
- Customer PK: `CUSTOMER#CUST001`
- Order contains `customerId` reference

### 6. Rider → Delivery Relationship
- Rider PK: `RIDER#RIDER001`
- Delivery contains `riderId` reference

### 7. Discount → Order Relationship
- Discount PK: `DISCOUNT#DISC001`
- Order contains discount information

---

## Partition Key Strategy

### 1. Entity-based Partitioning
- Use `ENTITY#<entity_type>#<entity_id>` for main entities
- Ensures even distribution across partitions
- Supports efficient queries by entity type

### 2. Time-based Sorting
- Use timestamps in sort keys for time-based queries
- Supports FIFO/LIFO operations for batches
- Enables efficient range queries

### 3. Composite Keys
- Combine multiple attributes in partition keys
- Example: `SUPPLIER#SUPP001` for supplier-specific data
- Reduces hot partition issues

---

## Implementation Guidelines

### 1. Batch Operations
```javascript
// Batch write for stock adjustments
const batchWriteParams = {
  RequestItems: {
    'InventoryTable': [
      {
        PutRequest: {
          Item: {
            PK: 'ENTITY#ADJUSTMENT#ADJ001',
            SK: 'METADATA#INFO#2024-01-01T00:00:00Z',
            // ... adjustment data
          }
        }
      },
      {
        PutRequest: {
          Item: {
            PK: 'ENTITY#PRODUCT#PROD001',
            SK: 'METADATA#STOCK#2024-01-01T00:00:00Z',
            // ... updated stock data
          }
        }
      }
    ]
  }
};
```

### 2. Conditional Updates
```javascript
// Update stock only if sufficient quantity
const updateParams = {
  TableName: 'InventoryTable',
  Key: {
    PK: 'ENTITY#PRODUCT#PROD001',
    SK: 'METADATA#STOCK#2024-01-01T00:00:00Z'
  },
  UpdateExpression: 'SET availableStock = availableStock - :quantity',
  ConditionExpression: 'availableStock >= :quantity',
  ExpressionAttributeValues: {
    ':quantity': 10
  }
};
```

### 3. Transaction Support
```javascript
// Use DynamoDB transactions for complex operations
const transactionParams = {
  TransactItems: [
    {
      Put: {
        TableName: 'InventoryTable',
        Item: {
          // ... adjustment record
        }
      }
    },
    {
      Update: {
        TableName: 'InventoryTable',
        Key: {
          // ... stock update
        },
        UpdateExpression: 'SET availableStock = availableStock - :quantity'
      }
    }
  ]
};
```

### 4. Error Handling
```javascript
// Handle conditional check failures
try {
  await dynamodb.update(updateParams).promise();
} catch (error) {
  if (error.code === 'ConditionalCheckFailedException') {
    // Handle insufficient stock
    throw new Error('Insufficient stock available');
  }
  throw error;
}
```

---

## Performance Optimization

### 1. Read Capacity Optimization
- Use GSIs for different access patterns
- Implement caching for frequently accessed data
- Use batch operations for multiple reads

### 2. Write Capacity Optimization
- Use batch writes for multiple items
- Implement optimistic locking for concurrent updates
- Use transactions for data consistency

### 3. Storage Optimization
- Compress large text fields
- Use efficient data types
- Archive old data to S3

### 4. Query Optimization
- Design indexes based on access patterns
- Use filter expressions sparingly
- Implement pagination for large result sets

This comprehensive DynamoDB data design provides a scalable, performant foundation for the inventory management system, supporting all the core business flows while maintaining data consistency and enabling efficient queries. 