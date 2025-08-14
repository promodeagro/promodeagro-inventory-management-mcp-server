# Inventory Management System - Data Design Structure

## 📊 System Overview

The Inventory Management System uses a **multi-table DynamoDB architecture** with 23 specialized tables designed to handle comprehensive inventory operations, logistics, business workflows, **variants**, and **unit management**.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INVENTORY MANAGEMENT SYSTEM                             │
│                           (23 Tables)                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Products  │  │   Batches   │  │  Suppliers  │  │  Customers  │      │
│  │   (Core)    │  │   (Core)    │  │   (Core)    │  │   (Core)    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Riders    │  │   Orders    │  │ Deliveries  │  │StockLevels  │      │
│  │   (Core)    │  │   (Core)    │  │   (Core)    │  │   (Core)    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │PurchaseOrdrs│  │CashCollectns│  │  Discounts  │  │PricingRules │      │
│  │   (Core)    │  │   (Core)    │  │ (Business)  │  │ (Business)  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Categories  │  │  Locations  │  │    Users    │  │  AuditLogs  │      │
│  │ (Business)  │  │ (Business)  │  │ (Business)  │  │ (Business)  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │Notificatns  │  │   Reports   │  │  Settings   │  │  Journeys   │      │
│  │ (Business)  │  │ (Business)  │  │ (Business)  │  │   (Core)    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │
│  │ProductVarnts│  │ ProductUnits│  │ UnitConversn│                        │
│  │ (Variants)  │  │ (Variants)  │  │ (Variants)  │                        │
│  └─────────────┘  └─────────────┘  └─────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Table Structure Overview

### 🎯 **Core Inventory Tables (11)**
*Essential tables for basic inventory operations*

### 🎯 **Business Tables (9)**
*Advanced tables for business logic and system management*

### 🎯 **Variant & Unit Tables (3)**
*New tables for variant and unit management*

---

## 🗂️ Detailed Table Structure

### 📦 **1. Enhanced Products Table - Integrated Variant Support**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED PRODUCTS TABLE - WITH VARIANTS               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: groupId (String) - Your existing product group ID                     │
│ SK: category#subCategory (String)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields (Your Existing Structure):                                         │
│ • groupId, name, category, subCategory, description                       │
│ • image, images (List), tags (List)                                       │
│ • variations (List) - Your existing variant structure:                    │
│   [                                                                        │
│     {                                                                      │
│       "id": "9381385120",                                                  │
│       "name": "Bharta Brinjal (1 Kg)",                                    │
│       "unit": "Kg", "quantity": 1,                                        │
│       "mrp": 120, "price": 90,                                            │
│       "availability": true,                                                │
│       "sku": "BBR-1KG-001", "barcode": "8901234567890"                   │
│     }                                                                      │
│   ]                                                                        │
│ • productType, storageRequirements (Map)                                  │
│ • supplier (Map), inventory (Map)                                         │
│ • isActive, createdAt, updatedAt                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **2. Simplified StockLevels for Variants**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STOCKLEVELS TABLE - VARIANT SUPPORT                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: groupId (String) - Links to your product group                        │
│ SK: location#variantId (String) - Warehouse + specific variant            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • groupId, variantId, variantName                                         │
│ • location, unit, quantity (from your variant data)                       │
│ • totalStock, availableStock, reservedStock                               │
│ • damagedStock, expiredStock                                              │
│ • reorderPoint, maxStock                                                  │
│ • lastRestocked, lastUpdated                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **3. Simplified Units Reference Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCTUNITS TABLE - SIMPLIFIED                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: unitId (String) - "KG", "Gms", "Ltr", "ML", "Pcs"                    │
│ SK: unitType (String) - "WEIGHT", "VOLUME", "COUNT"                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields (Global Unit Definitions):                                         │
│ • unitId, unitName, unitType                                              │
│ • conversionFactor (Decimal) - To base unit                               │
│ • baseUnit (String) - "KG", "LTR", "PCS"                                 │
│ • isDefault (Boolean)                                                     │
│ • isActive (Boolean)                                                      │
│ Examples:                                                                  │
│ • {unitId: "KG", unitType: "WEIGHT", conversionFactor: 1.0}              │
│ • {unitId: "Gms", unitType: "WEIGHT", conversionFactor: 0.001}           │
│ • {unitId: "Ltr", unitType: "VOLUME", conversionFactor: 1.0}             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **4. UnitConversions Table (NEW)**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNITCONVERSIONS TABLE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: conversionId (String)                                                  │
│ SK: fromUnit#toUnit (String)                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • conversionId, fromUnit, toUnit                                          │
│ • conversionFactor (Decimal)                                              │
│ • unitType (String) - "WEIGHT", "VOLUME", "COUNT", "LENGTH"              │
│ • description (String) - "1 KG = 1000 GRAMS"                             │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **5. Enhanced Batches Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENHANCED BATCHES TABLE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: batchId (String)                                                       │
│ SK: productId (String)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • batchNumber, manufacturingDate, expiryDate                              │
│ • productId, variantId (String) - Link to variant                         │
│ • unitId (String) - Specific unit for this batch                          │
│ • initialQuantity, currentQuantity (Number)                               │
│ • unitQuantity (Decimal) - Quantity in base unit                          │
│ • supplierId, qualityStatus, location                                      │
│ • temperature (Decimal), createdAt, updatedAt (String)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **6. Enhanced StockLevels Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED STOCKLEVELS TABLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: productId (String)                                                     │
│ SK: location#variantId#unitId (String)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • productId, variantId, unitId                                            │
│ • location, totalStock, availableStock, reservedStock (Number)            │
│ • damagedStock, expiredStock (Number)                                     │
│ • baseUnitQuantity (Decimal) - Converted to base unit                     │
│ • lastUpdated (String)                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **7. Enhanced Orders Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENHANCED ORDERS TABLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: orderId (String)                                                       │
│ SK: customerId (String)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • customerName, customerPhone, deliveryAddress                            │
│ • status, paymentMethod, paymentStatus                                    │
│ • totalAmount, discountAmount, finalAmount (Decimal)                      │
│ • deliverySlot, riderId, createdAt, updatedAt (String)                   │
│ • variantSupport (Boolean) - Enable variant tracking                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **8. OrderItems Table (NEW)**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORDERITEMS TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: orderId (String)                                                       │
│ SK: productId#variantId#unitId (String)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • orderId, productId, variantId, unitId                                   │
│ • quantity (Number), unitPrice (Decimal)                                  │
│ • discountPercentage, discountAmount (Decimal)                            │
│ • finalPrice (Decimal), totalPrice (Decimal)                              │
│ • batchId (String) - Link to specific batch                               │
│ • createdAt, updatedAt (String)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **9. Enhanced PricingRules Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ENHANCED PRICINGRULES TABLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: pricingId (String)                                                     │
│ SK: ruleType (String)                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • productId, variantId (String) - Specific variant pricing                │
│ • unitId (String) - Specific unit pricing                                 │
│ • ruleType (String) - "DYNAMIC", "SEASONAL", "BULK"                      │
│ • basePrice, minPrice, maxPrice (Decimal)                                 │
│ • factors (Map), effectiveDate, expiryDate                               │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Core Inventory Tables (11) - Updated**

### 📦 **10. Suppliers Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SUPPLIERS TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: supplierId (String)                                                    │
│ SK: status (String)                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, contactPerson, phone, email, address                              │
│ • paymentTerms, qualityStandards                                          │
│ • rating (Decimal), leadTime (Number)                                     │
│ • createdAt, updatedAt (String)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **11. Customers Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CUSTOMERS TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: customerId (String)                                                    │
│ SK: customerType (String)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, phone, email, address, pincode                                    │
│ • loyaltyPoints, totalOrders (Number)                                     │
│ • totalSpent (Decimal), preferredPaymentMethod                            │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **12. Riders Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RIDERS TABLE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: riderId (String)                                                       │
│ SK: status (String)                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, phone, email, vehicleNumber, vehicleType                          │
│ • currentLocation, assignedZone                                            │
│ • rating (Decimal), totalDeliveries, totalEarnings (Decimal)              │
│ • isAvailable (Boolean), createdAt, updatedAt (String)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **13. Deliveries Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DELIVERIES TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: deliveryId (String)                                                    │
│ SK: orderId (String)                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • riderId, status, pickupTime, estimatedDeliveryTime                      │
│ • actualDeliveryTime, signatureUrl, photoUrl                              │
│ • cashCollected (Decimal), createdAt, updatedAt (String)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **14. PurchaseOrders Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PURCHASEORDERS TABLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: poId (String)                                                          │
│ SK: supplierId (String)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • status, deliveryDate, createdBy, approvedBy                             │
│ • totalAmount (Decimal), createdAt, updatedAt (String)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **15. CashCollections Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CASHCOLLECTIONS TABLE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: collectionId (String)                                                  │
│ SK: riderId (String)                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • date, totalCollected, cashCollected, digitalCollected (Decimal)         │
│ • ordersDelivered (Number), status, settledAt                             │
│ • createdAt, updatedAt (String)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **16. Journeys Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          JOURNEYS TABLE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: PK (String) - JOURNEY#<journey_id>                                    │
│ SK: SK (String) - METADATA/STAGE/RULE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • EntityType, GSI1PK, GSI1SK                                              │
│ • CreatedAt, UpdatedAt (String)                                           │
│ • Data (Map) - Journey metadata, stages, rules                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Business Tables (9)**

### 📦 **17. Discounts Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DISCOUNTS TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: discountId (String)                                                    │
│ SK: discountType (String)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, description, discountValue (Number)                               │
│ • minOrderAmount, maxDiscountAmount (Decimal)                             │
│ • applicableProducts, applicableCategories, customerTypes (List)          │
│ • startDate, endDate, usageLimit, usedCount (Number)                     │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **18. Categories Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CATEGORIES TABLE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: categoryId (String)                                                    │
│ SK: parentCategory (String)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, description, icon, sortOrder (Number)                             │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **19. Locations Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCATIONS TABLE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: locationId (String)                                                    │
│ SK: locationType (String)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, pincodes (List), deliveryCharge, minOrderAmount (Decimal)         │
│ • deliverySlots (List), isActive (Boolean)                                │
│ • createdAt, updatedAt (String)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **20. Users Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USERS TABLE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: userId (String)                                                        │
│ SK: role (String)                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • name, email, phone, permissions (List)                                  │
│ • isActive (Boolean), createdAt, updatedAt (String)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **21. AuditLogs Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AUDITLOGS TABLE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: auditId (String)                                                       │
│ SK: timestamp (String)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • userId, action, entityId, details                                       │
│ • ipAddress, userAgent, createdAt (String)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **22. Notifications Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NOTIFICATIONS TABLE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: notificationId (String)                                                │
│ SK: recipientId (String)                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • type, title, message, priority                                          │
│ • isRead (Boolean), createdAt (String)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **23. Reports Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          REPORTS TABLE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: reportId (String)                                                      │
│ SK: reportType (String)                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • title, description, data (Map)                                          │
│ • generatedBy, createdAt (String)                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **24. Settings Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SETTINGS TABLE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: settingKey (String)                                                    │
│ SK: category (String)                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • value (Map), description, isActive (Boolean)                            │
│ • createdAt, updatedAt (String)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚚 **DELIVERY SLOTS SYSTEM**

### 📦 **25. DeliverySlots Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DELIVERY SLOTS TABLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: pincode (String) - Customer's pincode                                 │
│ SK: slotType#productType (String) - "STANDARD#PERISHABLE"                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • pincode, slotType, productType                                          │
│ • area, city, zone (String) - Geographic info                            │
│ • deliveryTypes (List) - ["same_day", "next_day", "scheduled"]           │
│ • timeSlots (List) - Available time slots:                               │
│   [                                                                        │
│     {                                                                      │
│       "slotId": "MORNING_1",                                               │
│       "name": "Morning Delivery",                                          │
│       "startTime": "06:00", "endTime": "10:00",                          │
│       "maxCapacity": 50, "deliveryCharge": 30.00,                        │
│       "daysAvailable": ["MON","TUE","WED","THU","FRI","SAT"]              │
│     }                                                                      │
│   ]                                                                        │
│ • specialRules (Map) - Product-specific delivery rules                    │
│ • isActive, createdAt, updatedAt                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **26. SlotAvailability Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SLOT AVAILABILITY TABLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: pincode#slotId#date (String) - "500086#MORNING_1#2024-01-15"         │
│ SK: deliveryType (String) - "same_day", "next_day", "scheduled"           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • pincode, slotId, date, deliveryType                                     │
│ • slotName, startTime, endTime                                            │
│ • maxCapacity, currentBookings, availableSlots                           │
│ • maxWeight, currentWeight, availableWeight                               │
│ • deliveryCharge, dynamicPricing (Boolean)                               │
│ • assignedRiders (List), status ("AVAILABLE", "FULL", "CLOSED")          │
│ • lastUpdated                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📦 **27. SlotBookings Table**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SLOT BOOKINGS TABLE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: bookingId (String) - Generated booking ID                             │
│ SK: orderId (String) - Links to customer order                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Fields:                                                                    │
│ • bookingId, orderId, customerId                                          │
│ • pincode, slotId, deliveryDate, deliveryType                            │
│ • slotDetails (Map):                                                       │
│   {                                                                        │
│     "slotName": "Morning Delivery",                                        │
│     "startTime": "06:00", "endTime": "10:00",                            │
│     "estimatedDelivery": "08:00"                                          │
│   }                                                                        │
│ • customerAddress, customerPhone                                          │
│ • productDetails (List) - Products in this booking                       │
│ • deliveryCharge, totalWeight                                             │
│ • riderId, status, confirmationCode                                       │
│ • bookedAt, deliveredAt                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Unit Management System**

### **📊 Unit Types & Conversions:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UNIT MANAGEMENT                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WEIGHT UNITS:                    VOLUME UNITS:                           │
│  • KG (Base)                     • LITERS (Base)                          │
│  • GRAMS (0.001)                 • ML (0.001)                             │
│  • POUNDS (0.453592)             • GALLONS (3.78541)                     │
│  • OUNCES (0.0283495)            • CUPS (0.236588)                       │
│                                                                             │
│  COUNT UNITS:                     LENGTH UNITS:                           │
│  • PCS (Base)                    • METERS (Base)                          │
│  • DOZEN (12)                    • CM (0.01)                              │
│  • GROSS (144)                   • INCHES (0.0254)                        │
│  • BOX (24)                      • FEET (0.3048)                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **📦 Unit Conversion Logic:**
```python
def convert_units(quantity, from_unit, to_unit, conversion_factors):
    """
    Convert quantity between units using conversion factors
    """
    if from_unit == to_unit:
        return quantity
    
    # Get conversion factors
    from_factor = conversion_factors.get(from_unit, 1.0)
    to_factor = conversion_factors.get(to_unit, 1.0)
    
    # Convert to base unit first, then to target unit
    base_quantity = quantity * from_factor
    target_quantity = base_quantity / to_factor
    
    return target_quantity
```

---

## 🔗 Enhanced Data Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENHANCED DATA RELATIONSHIPS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRODUCTS ──────────┐                                                      │
│         │           │                                                      │
│         ▼           ▼                                                      │
│  PRODUCTVARIANTS ───┼─── PRODUCTUNITS                                      │
│         │           │           │                                          │
│         ▼           │           ▼                                          │
│  BATCHES ───────────┼─── UNITCONVERSIONS                                   │
│         │           │                                                      │
│         ▼           │                                                      │
│  STOCKLEVELS ───────┼───────────────── PURCHASEORDERS                      │
│         │           │                                                      │
│         ▼           │                                                      │
│  SUPPLIERS ─────────┼───────────────── ORDERS ─────── ORDERITEMS           │
│         │           │                      │              │                │
│         ▼           │                      ▼              ▼                │
│  CUSTOMERS ─────────┼───────────────── DELIVERIES                          │
│         │           │                                                      │
│         ▼           │                                                      │
│  RIDERS ────────────┼───────────────── CASHCOLLECTIONS                     │
│         │           │                                                      │
│         ▼           │                                                      │
│  USERS ─────────────┼───────────────── AUDITLOGS                           │
│         │           │                                                      │
│         ▼           │                                                      │
│  CATEGORIES ────────┼───────────────── DISCOUNTS                           │
│         │           │                                                      │
│         ▼           │                                                      │
│  LOCATIONS ─────────┼───────────────── PRICINGRULES                        │
│         │           │                                                      │
│         ▼           │                                                      │
│  SETTINGS ──────────┼───────────────── NOTIFICATIONS                       │
│         │           │                                                      │
│         ▼           │                                                      │
│  REPORTS ───────────┼───────────────── JOURNEYS                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Enhanced Key Relationships

### **Primary Relationships:**
- **Products** ↔ **ProductVariants** (One-to-Many)
- **Products** ↔ **ProductUnits** (One-to-Many)
- **ProductUnits** ↔ **UnitConversions** (Many-to-Many)
- **Products** ↔ **Batches** (One-to-Many)
- **Products** ↔ **StockLevels** (One-to-Many)
- **Products** ↔ **OrderItems** (One-to-Many)
- **Variants** ↔ **Batches** (One-to-Many)
- **Units** ↔ **Batches** (One-to-Many)
- **Orders** ↔ **OrderItems** (One-to-Many)

### **Business Logic Relationships:**
- **Categories** ↔ **Products** (One-to-Many)
- **Locations** ↔ **Deliveries** (One-to-Many)
- **Discounts** ↔ **Orders** (Many-to-Many)
- **PricingRules** ↔ **Products** (One-to-Many)
- **Settings** ↔ **All Tables** (Configuration)

---

## 📊 Variant & Unit Management Examples

### **📦 Example 1: Tomatoes with Size Variants**
```json
// Products Table
{
  "productId": "PROD001",
  "category": "VEGETABLES",
  "name": "Fresh Tomatoes",
  "hasVariants": true,
  "variantTypes": ["SIZE"],
  "baseUnit": "KG",
  "defaultUnit": "KG",
  "costPrice": 45.00,
  "sellingPrice": 60.00
}

// ProductVariants Table
[
  {
    "variantId": "VAR001",
    "productId": "PROD001",
    "variantType": "SIZE",
    "variantValue": "SMALL",
    "sku": "PROD001-SMALL",
    "dimensions": {"weight": "0.1"}
  },
  {
    "variantId": "VAR002",
    "productId": "PROD001",
    "variantType": "SIZE",
    "variantValue": "MEDIUM",
    "sku": "PROD001-MEDIUM",
    "dimensions": {"weight": "0.2"}
  },
  {
    "variantId": "VAR003",
    "productId": "PROD001",
    "variantType": "SIZE",
    "variantValue": "LARGE",
    "sku": "PROD001-LARGE",
    "dimensions": {"weight": "0.3"}
  }
]

// ProductUnits Table
[
  {
    "unitId": "KG",
    "productId": "PROD001",
    "unitName": "Kilograms",
    "unitType": "WEIGHT",
    "conversionFactor": 1.0,
    "baseUnit": "KG",
    "isDefault": true
  },
  {
    "unitId": "GRAMS",
    "productId": "PROD001",
    "unitName": "Grams",
    "unitType": "WEIGHT",
    "conversionFactor": 0.001,
    "baseUnit": "KG",
    "isDefault": false
  },
  {
    "unitId": "PCS",
    "productId": "PROD001",
    "unitName": "Pieces",
    "unitType": "COUNT",
    "conversionFactor": 1.0,
    "baseUnit": "PCS",
    "isDefault": false
  }
]
```

### **📦 Example 2: Milk with Volume Units**
```json
// Products Table
{
  "productId": "PROD002",
  "category": "DAIRY",
  "name": "Fresh Milk",
  "hasVariants": false,
  "baseUnit": "LITERS",
  "defaultUnit": "LITERS",
  "costPrice": 50.00,
  "sellingPrice": 70.00
}

// ProductUnits Table
[
  {
    "unitId": "LITERS",
    "productId": "PROD002",
    "unitName": "Liters",
    "unitType": "VOLUME",
    "conversionFactor": 1.0,
    "baseUnit": "LITERS",
    "isDefault": true
  },
  {
    "unitId": "ML",
    "productId": "PROD002",
    "unitName": "Milliliters",
    "unitType": "VOLUME",
    "conversionFactor": 0.001,
    "baseUnit": "LITERS",
    "isDefault": false
  },
  {
    "unitId": "GALLONS",
    "productId": "PROD002",
    "unitName": "Gallons",
    "unitType": "VOLUME",
    "conversionFactor": 3.78541,
    "baseUnit": "LITERS",
    "isDefault": false
  }
]
```

### **📦 Example 3: OrderItems with Variants & Units**
```json
// OrderItems Table
[
  {
    "orderId": "ORD-20241220-001",
    "productId": "PROD001",
    "variantId": "VAR002",
    "unitId": "KG",
    "quantity": 2,
    "unitPrice": 60.00,
    "discountPercentage": 10,
    "discountAmount": 12.00,
    "finalPrice": 48.00,
    "totalPrice": 96.00,
    "batchId": "BATCH001"
  },
  {
    "orderId": "ORD-20241220-001",
    "productId": "PROD002",
    "variantId": null,
    "unitId": "LITERS",
    "quantity": 1,
    "unitPrice": 70.00,
    "discountPercentage": 0,
    "discountAmount": 0.00,
    "finalPrice": 70.00,
    "totalPrice": 70.00,
    "batchId": "BATCH002"
  }
]
```

---

## 🔧 Technical Specifications

### **DynamoDB Configuration:**
- **Billing Mode**: PAY_PER_REQUEST (Free tier)
- **Region**: ap-south-1 (Mumbai)
- **Encryption**: AES-256 (Default)
- **Point-in-time Recovery**: Enabled
- **Tags**: Service, Component, Purpose, Environment

### **Data Types:**
- **String**: IDs, names, descriptions, statuses
- **Number**: Quantities, counts, ratings
- **Decimal**: Monetary values, prices, amounts
- **Boolean**: Flags, status indicators
- **List**: Arrays of values
- **Map**: Complex objects, configurations
- **Null**: Optional fields

### **Indexing Strategy:**
- **Primary Keys**: Optimized for access patterns
- **Sort Keys**: Time-based sorting, categorization
- **GSI**: Future expansion for complex queries

---

## 📊 Performance Considerations

### **Read Optimization:**
- Partition key distribution for even load
- Sort key design for range queries
- Batch operations for multiple items

### **Write Optimization:**
- Atomic updates for critical operations
- Conditional writes for data integrity
- Batch writes for bulk operations

### **Storage Optimization:**
- Efficient data types (Decimal vs Float)
- Compressed text fields
- Archived historical data

---

## 🔒 Security & Compliance

### **Access Control:**
- IAM roles and policies
- Resource-based permissions
- Encryption at rest and in transit

### **Audit Trail:**
- Comprehensive logging
- User action tracking
- Compliance reporting

### **Data Protection:**
- Backup and recovery
- Point-in-time restore
- Cross-region replication

---

## 🚀 Implementation Status

### **✅ Completed:**
- 24 DynamoDB tables designed
- Variant and unit management structure
- Multi-table architecture implemented
- Mumbai region configuration
- Free tier billing mode

### **🔄 In Progress:**
- Journey workflows
- Actor-based operations
- Business logic implementation

### **📋 Planned:**
- GSI optimization
- Advanced analytics
- Real-time monitoring
- Performance tuning

---

*This enhanced data design structure provides comprehensive support for variants and unit management while maintaining the scalability and performance of the Inventory Management System.* 