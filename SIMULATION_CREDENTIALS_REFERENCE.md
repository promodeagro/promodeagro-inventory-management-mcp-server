# 🔐 Aurora Spark Simulation - Complete Credentials Reference

## 📋 **Overview**

This document provides all the credentials needed to run the complete Aurora Spark order fulfillment simulation across all three portals.

---

## 🎯 **Portal Credentials**

### 1️⃣ **Customer Portal**
**Purpose**: Place orders, manage cart, select delivery slots

| Field | Value |
|-------|-------|
| 📧 **Email** | `john.doe@example.com` |
| 🔒 **Password** | `password123` |
| 👤 **Name** | John Doe |
| 📱 **Phone** | +919876543001 |
| 📍 **Address** | 123 MG Road, Banjara Hills, Hyderabad - 500034 |
| 🎯 **Access** | Product browsing, cart management, order placement |

---

### 2️⃣ **Warehouse Manager Portal**
**Purpose**: Pack orders, create routes, assign riders

| Field | Value |
|-------|-------|
| 📧 **Email** | `warehouse@promodeagro.com` |
| 🔒 **Password** | `password123` |
| 👤 **Name** | Amit Patel (from database) |
| 🏭 **Role** | Warehouse Manager |
| 🎯 **Access** | Warehouse + Logistics + Inventory Operations |
| 📋 **Functions** | Order packing, quality verification, route creation, rider assignment |

---

### 3️⃣ **Delivery Personnel Portal**
**Purpose**: Accept routes, deliver orders, collect delivery proof

| Field | Value |
|-------|-------|
| 🆔 **Employee ID** | `EMP-001` |
| 🔒 **Password** | `password123` |
| 👤 **Name** | Ravi Kumar |
| 🚚 **Role** | Delivery Personnel |
| 🚛 **Vehicle** | MH12AB1234 (Bike) |
| 🎯 **Access** | Route Management + Order Delivery + GPS Tracking |
| 📋 **Functions** | Route acceptance, order delivery, proof collection, status updates |

---

## 🔄 **Complete Workflow**

### **Step-by-Step Process:**

1. **Customer Portal** (`john.doe@example.com`)
   - Login with email and password
   - Add products to cart
   - Select delivery address and slot
   - Place order → Generates **Order ID**

2. **Warehouse Manager Portal** (`warehouse@promodeagro.com`)
   - Login with email and password
   - Pack the customer order
   - Perform quality verification
   - Create delivery route → Generates **Route ID**
   - Assign rider (Ravi Kumar/EMP-001)

3. **Delivery Personnel Portal** (`EMP-001`)
   - Login with Employee ID and password
   - Accept assigned route
   - Navigate to customer location
   - Deliver order with proof collection
   - Complete delivery

---

## 🎬 **How to Use These Credentials**

### **Interactive Simulation:**
```bash
python simulation/complete_order_fulfillment_simulator.py
```
- Shows credentials at the beginning
- Displays credentials before each authentication
- Pauses between steps for review

### **Automated Testing:**
```bash
python test_simulation.py
```
- Uses credentials automatically
- Shows credentials during authentication
- Runs complete workflow without pauses

---

## 📊 **Sample Output with Credentials**

```
🔑 CUSTOMER PORTAL CREDENTIALS:
   📧 Email: john.doe@example.com
   🔒 Password: password123
   👤 Name: John Doe
   📱 Phone: +919876543001

✅ Customer authenticated: John

🔑 WAREHOUSE MANAGER PORTAL CREDENTIALS:
   📧 Email: warehouse@promodeagro.com
   🔒 Password: password123
   🏭 Role: Warehouse Manager
   🎯 Access: Warehouse + Logistics + Inventory Operations

✅ Warehouse manager authenticated: Amit Patel

🔑 DELIVERY PERSONNEL PORTAL CREDENTIALS:
   🆔 Employee ID: EMP-001
   🔒 Password: password123
   👤 Name: Ravi Kumar
   🚚 Role: Delivery Personnel
   🚛 Vehicle: MH12AB1234 (Bike)

✅ Delivery personnel authenticated: Ravi Kumar
```

---

## ⚠️ **Important Security Notes**

### **Demo Environment:**
- ✅ All passwords are `password123` for simplicity
- ✅ Customer portal uses email-based authentication
- ✅ Warehouse portal uses email-based authentication  
- ✅ Delivery portal uses Employee ID-based authentication

### **Production Environment:**
- 🔒 **Change all default passwords**
- 🔒 **Implement strong password policies**
- 🔒 **Enable two-factor authentication**
- 🔒 **Use environment variables for credentials**
- 🔒 **Implement role-based access controls**
- 🔒 **Regular credential rotation**

---

## 🎯 **Alternative Test Users**

### **Additional Customer Accounts:**
| Email | Password | Name |
|-------|----------|------|
| `jane.smith@example.com` | `password123` | Jane Smith |
| `rajesh.sharma@example.com` | `password123` | Rajesh Sharma |
| `priya.patel@example.com` | `password123` | Priya Patel |

### **Additional Staff Accounts:**
| Employee ID | Password | Name | Role |
|-------------|----------|------|------|
| `EMP-002` | `password123` | Suresh Reddy | Delivery Personnel |
| `EMP-003` | `password123` | Amit Singh | Delivery Personnel |

---

## 🚀 **Quick Reference**

### **Copy-Paste Ready Credentials:**

**Customer Login:**
```
Email: john.doe@example.com
Password: password123
```

**Warehouse Manager Login:**
```
Email: warehouse@promodeagro.com
Password: password123
```

**Delivery Personnel Login:**
```
Employee ID: EMP-001
Password: password123
```

---

## 🎉 **Success Indicators**

When using these credentials correctly, you should see:

- ✅ **Order ID Generated**: `ORD-YYYYMMDD-XXXX`
- ✅ **Route ID Generated**: `RT-YYYYMMDD-XXX`
- ✅ **Rider Assigned**: Ravi Kumar
- ✅ **Database Operations**: All successful
- ✅ **Complete Workflow**: Customer → Warehouse → Delivery

**The simulation demonstrates the complete Aurora Spark system with real database integration!** 🚚✨
