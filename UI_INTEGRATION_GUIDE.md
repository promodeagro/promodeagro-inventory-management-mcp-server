# 📊 JSON Data Examples - Products, Variants & Delivery Slots

## 📋 Overview

This document provides sample JSON data structures for:
1. **Products & Variants System** - Product data with variants
2. **Delivery Slots System** - Pincode-based slot data
3. **Order Flow** - Complete order and booking data

---

## 📦 **PRODUCTS & VARIANTS JSON EXAMPLES**

### **1. Product Listing Response**

**API Endpoint:** `GET /api/products/category/Bengali%20Special/Bengali%20Vegetables`

#### **Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
      "category": "Bengali Special#Bengali Vegetables",
      "name": "Bharta Brinjal (Black medium pieces)",
      "subCategory": "Bengali Vegetables",
      "description": "Bharta Brinjal (Begun) is a special variety of large, fleshy eggplant perfect for roasting and Bengali cuisine preparations.",
      "image": "https://cdn.example.com/bharta-brinjal.webp",
      "images": [
        "https://cdn.example.com/bharta-brinjal-1.webp",
        "https://cdn.example.com/bharta-brinjal-2.webp",
        ""
      ],
      "tags": [
        "bharta brinjal", "begun", "baingan", "roasting eggplant", "bengali vegetables"
      ],
      "variations": [
        {
          "id": "9381385120",
          "name": "Bharta Brinjal (1 Kg)",
          "unit": "Kg",
          "quantity": 1,
          "mrp": 120,
          "price": 90,
          "availability": true
        },
        {
          "id": "9271560014",
          "name": "Bharta Brinjal (500 Gms)",
          "unit": "Gms",
          "quantity": 500,
          "mrp": 60,
          "price": 45,
          "availability": true
        },
        {
          "id": "8628945059",
          "name": "Bharta Brinjal (250 Gms)",
          "unit": "Gms",
          "quantity": 250,
          "mrp": 30,
          "price": 23,
          "availability": true
        }
      ],
      "productType": "PERISHABLE",
      "storageRequirements": {
        "temperature": "ROOM_TEMP",
        "humidity": "MEDIUM",
        "specialHandling": "HANDLE_WITH_CARE"
      },
      "stockLevels": [
        {
          "variantId": "9381385120",
          "availableStock": 95,
          "totalStock": 100
        },
        {
          "variantId": "9271560014",
          "availableStock": 45,
          "totalStock": 50
        },
        {
          "variantId": "8628945059",
          "availableStock": 28,
          "totalStock": 30
        }
      ]
    }
  ],
  "count": 1
}
```

### **2. Product Detail Response**

**API Endpoint:** `GET /api/products/8b7bb419-f868-491c-bba6-7785e78b62cf`

**Response:**
```json
{
  "success": true,
  "data": {
    "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
    "category": "Bengali Special#Bengali Vegetables",
    "name": "Bharta Brinjal (Black medium pieces)",
    "subCategory": "Bengali Vegetables",
    "description": "Bharta Brinjal (Begun) is a special variety of large, fleshy eggplant perfect for roasting and Bengali cuisine preparations.",
    "image": "https://cdn.example.com/bharta-brinjal.webp",
    "images": [
      "https://cdn.example.com/bharta-brinjal-1.webp",
      "https://cdn.example.com/bharta-brinjal-2.webp",
      "https://cdn.example.com/bharta-brinjal-3.webp"
    ],
    "tags": [
      "bharta brinjal", "begun", "baingan", "roasting eggplant", "bengali vegetables"
    ],
    "variations": [
      {
        "id": "9381385120",
        "name": "Bharta Brinjal (1 Kg)",
        "unit": "Kg",
        "quantity": 1,
        "mrp": 120,
        "price": 90,
        "availability": true,
        "sku": "BBR-1KG-001",
        "barcode": "8901234567890"
      },
      {
        "id": "9271560014",
        "name": "Bharta Brinjal (500 Gms)",
        "unit": "Gms",
        "quantity": 500,
        "mrp": 60,
        "price": 45,
        "availability": true,
        "sku": "BBR-500G-001",
        "barcode": "8901234567891"
      },
      {
        "id": "8628945059",
        "name": "Bharta Brinjal (250 Gms)",
        "unit": "Gms",
        "quantity": 250,
        "mrp": 30,
        "price": 23,
        "availability": true,
        "sku": "BBR-250G-001",
        "barcode": "8901234567892"
      }
    ],
    "productType": "PERISHABLE",
    "storageRequirements": {
      "temperature": "ROOM_TEMP",
      "humidity": "MEDIUM",
      "specialHandling": "HANDLE_WITH_CARE"
    },
    "supplier": {
      "supplierId": "SUP001",
      "supplierName": "Bengal Fresh Farms",
      "contactPhone": "+91-9876543210"
    },
    "inventory": {
      "totalStock": 180,
      "availableStock": 168,
      "reservedStock": 12,
      "damagedStock": 0
    },
    "stockLevels": [
      {
        "variantId": "9381385120",
        "location": "WH001",
        "totalStock": 100,
        "availableStock": 95,
        "reservedStock": 5,
        "reorderPoint": 20
      },
      {
        "variantId": "9271560014",
        "location": "WH001",
        "totalStock": 50,
        "availableStock": 45,
        "reservedStock": 5,
        "reorderPoint": 15
      },
      {
        "variantId": "8628945059",
        "location": "WH001",
        "totalStock": 30,
        "availableStock": 28,
        "reservedStock": 2,
        "reorderPoint": 10
      }
    ],
    "isActive": true,
    "createdAt": "2024-01-15T06:30:00Z",
    "updatedAt": "2024-01-15T08:45:00Z"
  }
}
```

### **3. Cart Item Structure**

**Add to Cart Payload:**
```json
{
  "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
  "variantId": "9381385120",
  "productName": "Bharta Brinjal (Black medium pieces)",
  "variantName": "Bharta Brinjal (1 Kg)",
  "price": 90,
  "mrp": 120,
  "quantity": 2,
  "unit": "Kg",
  "image": "https://cdn.example.com/bharta-brinjal.webp",
  "productType": "PERISHABLE",
  "sku": "BBR-1KG-001"
}
```
### **4. Product Search Response**

**API Endpoint:** `GET /api/products/search?q=brinjal&category=Bengali Special`

**Response:**
```json
{
  "success": true,
  "query": "brinjal",
  "category": "Bengali Special",
  "results": [
    {
      "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
      "name": "Bharta Brinjal (Black medium pieces)",
      "category": "Bengali Special",
      "subCategory": "Bengali Vegetables",
      "image": "https://cdn.example.com/bharta-brinjal.webp",
      "productType": "PERISHABLE",
      "minPrice": 23,
      "maxPrice": 90,
      "variations": [
        {
          "id": "9381385120",
          "name": "Bharta Brinjal (1 Kg)",
          "price": 90,
          "mrp": 120,
          "availability": true
        },
        {
          "id": "9271560014", 
          "name": "Bharta Brinjal (500 Gms)",
          "price": 45,
          "mrp": 60,
          "availability": true
        }
      ],
      "totalStock": 168,
      "isActive": true
    }
  ],
  "totalResults": 1,
  "page": 1,
  "limit": 20
}
```

### **5. Stock Level Response**

**API Endpoint:** `GET /api/products/8b7bb419-f868-491c-bba6-7785e78b62cf/stock`

**Response:**
```json
{
  "success": true,
  "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
  "productName": "Bharta Brinjal (Black medium pieces)",
  "stockLevels": [
    {
      "variantId": "9381385120",
      "variantName": "Bharta Brinjal (1 Kg)",
      "location": "WH001",
      "locationName": "Main Warehouse",
      "totalStock": 100,
      "availableStock": 95,
      "reservedStock": 5,
      "damagedStock": 0,
      "expiredStock": 0,
      "reorderPoint": 20,
      "maxStock": 200,
      "lastRestocked": "2024-01-14T10:30:00Z",
      "lastUpdated": "2024-01-15T08:45:00Z"
    },
    {
      "variantId": "9271560014",
      "variantName": "Bharta Brinjal (500 Gms)",
      "location": "WH001",
      "locationName": "Main Warehouse",
      "totalStock": 50,
      "availableStock": 45,
      "reservedStock": 5,
      "damagedStock": 0,
      "expiredStock": 0,
      "reorderPoint": 15,
      "maxStock": 100,
      "lastRestocked": "2024-01-14T10:30:00Z",
      "lastUpdated": "2024-01-15T08:45:00Z"
    }
  ],
  "totalProductStock": {
    "totalStock": 180,
    "availableStock": 168,
    "reservedStock": 12,
    "reorderRequired": false
  }
}
```

---

## 🚚 **DELIVERY SLOTS JSON EXAMPLES**

### **1. Pincode Serviceability Check**

**API Endpoint:** `GET /api/delivery/check-pincode/500086`

**Response:**
```json
{
  "success": true,
  "serviceable": true,
  "pincode": "500086",
  "area": "Secunderabad",
  "city": "Hyderabad",
  "zone": "Central",
  "deliveryTypes": ["same_day", "next_day", "scheduled"],
  "productTypes": ["PERISHABLE", "GENERAL"],
  "minimumCharges": {
    "PERISHABLE": 25.00,
    "GENERAL": 20.00
  },
  "specialServices": [
    "Temperature Controlled Delivery",
    "Quality Assured Delivery"
  ]
}
```

### **2. Delivery Options Request**

**API Endpoint:** `POST /api/delivery/options`

**Request Body:**
```json
{
  "pincode": "500086",
  "products": [
    {
      "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
      "variantId": "9381385120",
      "quantity": 2,
      "productType": "PERISHABLE"
    },
    {
      "groupId": "7a6bb319-e758-381b-aba5-6785d67a51ce",
      "variantId": "8271460013",
      "quantity": 1,
      "productType": "PERISHABLE"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "serviceable": true,
  "pincode": "500086",
  "productAnalysis": {
    "productTypes": ["PERISHABLE"],
    "totalWeight": 1.75,
    "requiresTemperatureControl": true,
    "deliveryComplexity": "HIGH"
  },
  "deliveryOptions": [
    {
      "date": "2024-01-16",
      "deliveryType": "next_day",
      "dayName": "Tuesday",
      "slotsAvailable": 3,
      "slots": [
        {
          "slotId": "MORNING_1",
          "slotName": "Early Morning Delivery",
          "startTime": "06:00",
          "endTime": "10:00",
          "deliveryCharge": 30.00,
          "availableCapacity": 27,
          "maxCapacity": 50,
          "estimatedDeliveryTime": "08:00",
          "specialRules": {
            "temperatureControl": true,
            "maxDeliveryTime": 4,
            "qualityChecks": true
          },
          "area": "Secunderabad",
          "city": "Hyderabad"
        },
        {
          "slotId": "MORNING_2",
          "slotName": "Late Morning Delivery",
          "startTime": "10:00",
          "endTime": "14:00",
          "deliveryCharge": 25.00,
          "availableCapacity": 52,
          "maxCapacity": 75,
          "estimatedDeliveryTime": "12:00"
        },
        {
          "slotId": "EVENING_1",
          "slotName": "Evening Delivery",
          "startTime": "17:00",
          "endTime": "21:00",
          "deliveryCharge": 35.00,
          "availableCapacity": 35,
          "maxCapacity": 60,
          "estimatedDeliveryTime": "19:00"
        }
      ]
    },
    {
      "date": "2024-01-17",
      "deliveryType": "scheduled",
      "dayName": "Wednesday",
      "slotsAvailable": 3,
      "slots": [...]
    }
  ],
  "recommendedOption": {
    "date": "2024-01-16",
    "deliveryType": "next_day",
    "slot": {...}
  }
}
```

### **3. Slot Booking Request**

**API Endpoint:** `POST /api/delivery/slots/book`

**Request Body:**
```json
{
  "pincode": "500086",
  "slotId": "MORNING_1",
  "deliveryDate": "2024-01-16",
  "customerId": "CUST001",
  "customerName": "John Doe",
  "customerPhone": "+91-9876543210",
  "customerAddress": {
    "address": "Flat 301, Green Valley Apartments, Road No. 12",
    "pincode": "500086",
    "landmark": "Near City Mall",
    "city": "Hyderabad",
    "state": "Telangana"
  },
  "orderDetails": {
    "orderId": "ORD-20240116-001",
    "totalAmount": 315.00,
    "deliveryCharge": 30.00,
    "productTypes": ["PERISHABLE"]
  },
  "specialInstructions": "Handle with care, temperature sensitive items"
}
```

**Response:**
```json
{
  "success": true,
  "bookingId": "SLOT-BOOK-20240116-001",
  "confirmationCode": "SB24011601",
  "message": "Delivery slot booked successfully",
  "slotDetails": {
    "slotId": "MORNING_1",
    "slotName": "Early Morning Delivery",
    "deliveryDate": "2024-01-16",
    "timeRange": "06:00 - 10:00",
    "estimatedDelivery": "08:00",
    "deliveryCharge": 30.00,
    "area": "Secunderabad",
    "city": "Hyderabad",
    "specialRules": {
      "temperatureControl": true,
      "maxDeliveryTime": 4,
      "qualityChecks": true
    }
  },
  "capacityInfo": {
    "remainingCapacity": 26,
    "maxCapacity": 50
  }
}
```

### **4. Booking Details Response**

**API Endpoint:** `GET /api/delivery/booking/SLOT-BOOK-20240116-001`

**Response:**
```json
{
  "success": true,
  "bookingDetails": {
    "bookingId": "SLOT-BOOK-20240116-001",
    "confirmationCode": "SB24011601",
    "status": "CONFIRMED",
    "pincode": "500086",
    "slotId": "MORNING_1",
    "deliveryDate": "2024-01-16",
    "bookedAt": "2024-01-15T14:30:00Z",
    "customerInfo": {
      "customerId": "CUST001",
      "customerName": "John Doe",
      "customerPhone": "+91-9876543210",
      "customerAddress": {
        "address": "Flat 301, Green Valley Apartments, Road No. 12",
        "pincode": "500086",
        "landmark": "Near City Mall",
        "city": "Hyderabad",
        "state": "Telangana"
      }
    },
    "slotDetails": {
      "slotName": "Early Morning Delivery",
      "timeRange": "06:00 - 10:00",
      "estimatedDelivery": "08:00",
      "deliveryCharge": 30.00,
      "area": "Secunderabad",
      "city": "Hyderabad"
    },
    "orderInfo": {
      "orderId": "ORD-20240116-001",
      "totalAmount": 315.00,
      "deliveryCharge": 30.00,
      "productTypes": ["PERISHABLE"],
      "specialInstructions": "Handle with care, temperature sensitive items"
    },
    "trackingInfo": {
      "status": "SLOT_BOOKED",
      "nextUpdate": "Order will be prepared for delivery on 2024-01-16 at 06:00",
      "canModify": true,
      "canCancel": true
    }
  }
}
```

---

## 🛒 **ORDER FLOW JSON EXAMPLES**

### **1. Create Order with Auto Slot Selection**

**API Endpoint:** `POST /api/orders/create-with-slot-selection`

**Request Body:**
```json
{
  "customerId": "CUST001",
  "customerName": "John Doe",
  "customerPhone": "+91-9876543210",
  "customerEmail": "john.doe@example.com",
  "customerAddress": {
    "address": "Flat 301, Green Valley Apartments, Road No. 12",
    "pincode": "500086",
    "landmark": "Near City Mall",
    "city": "Hyderabad",
    "state": "Telangana"
  },
  "products": [
    {
      "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
      "variantId": "9381385120",
      "quantity": 2
    },
    {
      "groupId": "7a6bb319-e758-381b-aba5-6785d67a51ce",
      "variantId": "8271460013",
      "quantity": 1
    }
  ],
  "deliveryPreference": "fastest",
  "paymentMethod": "CASH_ON_DELIVERY",
  "specialInstructions": "Handle with care, temperature sensitive items"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Order created and delivery slot auto-selected successfully",
  "orderDetails": {
    "orderId": "ORD-20240116-001",
    "customerId": "CUST001",
    "orderStatus": "CONFIRMED",
    "orderDate": "2024-01-15T14:30:00Z",
    "orderItems": [
      {
        "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
        "variantId": "9381385120",
        "productName": "Bharta Brinjal (Black medium pieces)",
        "variantName": "Bharta Brinjal (1 Kg)",
        "quantity": 2,
        "unitPrice": 90,
        "totalPrice": 180
      },
      {
        "groupId": "7a6bb319-e758-381b-aba5-6785d67a51ce",
        "variantId": "8271460013",
        "productName": "Organic Milk",
        "variantName": "Organic Milk (1 Ltr)",
        "quantity": 1,
        "unitPrice": 105,
        "totalPrice": 105
      }
    ],
    "orderTotals": {
      "subtotal": 285,
      "deliveryCharge": 30,
      "taxes": 0,
      "totalAmount": 315
    },
    "customerInfo": {
      "customerId": "CUST001",
      "customerName": "John Doe",
      "customerPhone": "+91-9876543210",
      "customerEmail": "john.doe@example.com",
      "customerAddress": {
        "address": "Flat 301, Green Valley Apartments, Road No. 12",
        "pincode": "500086",
        "landmark": "Near City Mall",
        "city": "Hyderabad",
        "state": "Telangana"
      }
    },
    "paymentInfo": {
      "paymentMethod": "CASH_ON_DELIVERY",
      "paymentStatus": "PENDING",
      "amountToPay": 315
    }
  },
  "deliverySlot": {
    "slotId": "MORNING_1",
    "slotName": "Early Morning Delivery",
    "deliveryDate": "2024-01-16",
    "timeRange": "06:00 - 10:00",
    "estimatedDelivery": "08:00",
    "deliveryCharge": 30,
    "area": "Secunderabad",
    "city": "Hyderabad",
    "specialRules": {
      "temperatureControl": true,
      "maxDeliveryTime": 4,
      "qualityChecks": true
    }
  },
  "slotBooking": {
    "bookingId": "SLOT-BOOK-20240116-001",
    "confirmationCode": "SB24011601",
    "status": "CONFIRMED",
    "bookedAt": "2024-01-15T14:30:00Z"
  },
  "tracking": {
    "currentStatus": "ORDER_CONFIRMED",
    "statusHistory": [
      {
        "status": "ORDER_PLACED",
        "timestamp": "2024-01-15T14:30:00Z",
        "description": "Order received and confirmed"
      },
      {
        "status": "SLOT_BOOKED",
        "timestamp": "2024-01-15T14:30:05Z",
        "description": "Delivery slot automatically selected and booked"
      }
    ],
    "nextUpdate": "Order will be prepared for delivery on 2024-01-16 at 06:00",
    "estimatedDelivery": "2024-01-16T08:00:00Z"
  }
}
```

### **2. Order Details Response**

**API Endpoint:** `GET /api/orders/ORD-20240116-001`

**Response:**
```json
{
  "success": true,
  "order": {
    "orderId": "ORD-20240116-001",
    "customerId": "CUST001",
    "orderStatus": "IN_PREPARATION",
    "orderDate": "2024-01-15T14:30:00Z",
    "lastUpdated": "2024-01-16T06:15:00Z",
    "orderItems": [
      {
        "groupId": "8b7bb419-f868-491c-bba6-7785e78b62cf",
        "variantId": "9381385120",
        "productName": "Bharta Brinjal (Black medium pieces)",
        "variantName": "Bharta Brinjal (1 Kg)",
        "quantity": 2,
        "unitPrice": 90,
        "totalPrice": 180,
        "sku": "BBR-1KG-001",
        "productType": "PERISHABLE"
      },
      {
        "groupId": "7a6bb319-e758-381b-aba5-6785d67a51ce",
        "variantId": "8271460013",
        "productName": "Organic Milk",
        "variantName": "Organic Milk (1 Ltr)",
        "quantity": 1,
        "unitPrice": 105,
        "totalPrice": 105,
        "sku": "OM-1LTR-001",
        "productType": "PERISHABLE"
      }
    ],
    "orderTotals": {
      "subtotal": 285,
      "deliveryCharge": 30,
      "taxes": 0,
      "discount": 0,
      "totalAmount": 315
    },
    "deliveryInfo": {
      "slotId": "MORNING_1",
      "slotName": "Early Morning Delivery",
      "deliveryDate": "2024-01-16",
      "timeRange": "06:00 - 10:00",
      "estimatedDelivery": "08:00",
      "deliveryCharge": 30,
      "deliveryAddress": {
        "address": "Flat 301, Green Valley Apartments, Road No. 12",
        "pincode": "500086",
        "landmark": "Near City Mall",
        "city": "Hyderabad",
        "state": "Telangana"
      },
      "deliveryInstructions": "Handle with care, temperature sensitive items",
      "bookingConfirmationCode": "SB24011601"
    },
    "tracking": {
      "currentStatus": "IN_PREPARATION",
      "statusHistory": [
        {
          "status": "ORDER_PLACED",
          "timestamp": "2024-01-15T14:30:00Z",
          "description": "Order received and confirmed"
        },
        {
          "status": "SLOT_BOOKED",
          "timestamp": "2024-01-15T14:30:05Z",
          "description": "Delivery slot automatically selected and booked"
        },
        {
          "status": "IN_PREPARATION",
          "timestamp": "2024-01-16T06:15:00Z",
          "description": "Order is being prepared for delivery"
        }
      ],
      "nextUpdate": "Order will be out for delivery by 07:30",
      "estimatedDelivery": "2024-01-16T08:00:00Z",
      "canModify": false,
      "canCancel": false
    }
  }
}
```

---

## 📱 **API ENDPOINTS SUMMARY**

### **Products & Variants APIs:**
```
GET  /api/products/category/{category}/{subCategory}  - Get products by category
GET  /api/products/{groupId}                          - Get specific product details
GET  /api/products/search?q={searchTerm}              - Search products
GET  /api/products/{groupId}/stock                    - Get stock levels for variants
POST /api/products/{groupId}/variants/{variantId}/price - Update variant price
```

### **Delivery Slots APIs:**
```
GET  /api/delivery/check-pincode/{pincode}            - Check pincode serviceability
POST /api/delivery/options                            - Get delivery slot options
POST /api/delivery/slots/book                         - Book delivery slot
GET  /api/delivery/booking/{bookingId}                - Get booking details
```

### **Order Management APIs:**
```
POST /api/orders/create-with-slot-selection           - Create order with auto slot selection
GET  /api/orders/{orderId}                            - Get order details
PUT  /api/orders/{orderId}/delivery-slot              - Update delivery slot
```

---

## 🎯 **Key Data Structures**

### **Product with Variants**
- `groupId` links all variants under one product
- Each variant has its own pricing, stock, and availability
- Stock tracking per `groupId` + `variantId` combination

### **Delivery Slots System**
- Pincode-based serviceability checking
- Product-type aware slot availability (PERISHABLE vs GENERAL)
- Real-time capacity management with booking confirmations

### **Integrated Order Flow**
- Automatic slot selection based on delivery preferences
- Real-time inventory and slot booking
- Complete order tracking with status updates

This comprehensive JSON reference provides everything needed to integrate both the products/variants system and delivery slots system into your frontend! 🚀
