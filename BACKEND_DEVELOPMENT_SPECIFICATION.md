# 🚀 Aurora Spark Theme - Backend Development Specification

## 📋 **Project Overview**

This document provides comprehensive backend development specifications for the **Aurora Spark Theme** - a multi-portal SaaS inventory management system for **Promode Agro Farms**. The system consists of three independent portals with shared backend services.

### **System Architecture**
- **Microservices Architecture** with shared database
- **RESTful APIs** for all portal communications
- **Real-time capabilities** for live tracking and notifications
- **Role-based access control (RBAC)** system
- **Multi-tenant architecture** supporting different user roles

---

## 🏗️ **Database Schema Design**

### **Core Entities**

#### **1. Users & Authentication**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSON, -- Array of permission strings
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User roles junction table
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

-- Sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. Suppliers Management**

```sql
-- Suppliers table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code VARCHAR(20) UNIQUE NOT NULL, -- SUP-001, SUP-002, etc.
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    category_id UUID REFERENCES supplier_categories(id),
    rating DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 5.00
    total_orders INTEGER DEFAULT 0,
    total_value DECIMAL(15,2) DEFAULT 0.00,
    status ENUM('active', 'inactive', 'pending', 'suspended') DEFAULT 'pending',
    payment_terms VARCHAR(50), -- Net 15, Net 30, Net 45, Net 60
    tax_id VARCHAR(50),
    bank_account_details JSON,
    last_order_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Supplier categories
CREATE TABLE supplier_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7), -- Hex color code
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Supplier ratings and reviews
CREATE TABLE supplier_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    order_id UUID REFERENCES purchase_orders(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. Products & Inventory**

```sql
-- Product categories
CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code VARCHAR(20) UNIQUE NOT NULL, -- PRD-001, PRD-002, etc.
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES product_categories(id),
    unit VARCHAR(20) NOT NULL, -- kg, bunch, piece, liter, etc.
    price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    current_stock INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 0,
    max_stock_level INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 0,
    status ENUM('active', 'inactive', 'discontinued') DEFAULT 'active',
    quality_grade ENUM('excellent', 'very-good', 'good', 'fair', 'poor'),
    perishable BOOLEAN DEFAULT false,
    shelf_life_days INTEGER,
    storage_temperature_min DECIMAL(5,2),
    storage_temperature_max DECIMAL(5,2),
    supplier_id UUID REFERENCES suppliers(id),
    image_url VARCHAR(500),
    barcode VARCHAR(50),
    sku VARCHAR(50) UNIQUE,
    is_b2c_available BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Stock movements (inventory transactions)
CREATE TABLE stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    movement_type ENUM('inbound', 'outbound', 'adjustment', 'transfer', 'waste'),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(15,2),
    reference_type ENUM('purchase_order', 'sale_order', 'adjustment', 'transfer', 'waste'),
    reference_id UUID, -- Can reference different tables based on reference_type
    batch_number VARCHAR(50),
    expiry_date DATE,
    storage_location VARCHAR(100),
    temperature DECIMAL(5,2),
    quality_grade ENUM('excellent', 'very-good', 'good', 'fair', 'poor'),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Storage locations
CREATE TABLE storage_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    type ENUM('cold_storage', 'dry_storage', 'freezer', 'ambient') NOT NULL,
    capacity_tonnes DECIMAL(8,2),
    current_utilization DECIMAL(8,2) DEFAULT 0,
    temperature_min DECIMAL(5,2),
    temperature_max DECIMAL(5,2),
    humidity_min DECIMAL(5,2),
    humidity_max DECIMAL(5,2),
    status ENUM('active', 'maintenance', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **4. Purchase Orders & Procurement**

```sql
-- Purchase orders
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_number VARCHAR(20) UNIQUE NOT NULL, -- PO-001, PO-002, etc.
    supplier_id UUID REFERENCES suppliers(id) NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    total_amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    final_amount DECIMAL(15,2) NOT NULL,
    status ENUM('draft', 'sent', 'confirmed', 'partially_received', 'received', 'delivered', 'cancelled') DEFAULT 'draft',
    payment_status ENUM('pending', 'partial', 'paid') DEFAULT 'pending',
    payment_method ENUM('upi', 'card', 'cash', 'bank_transfer', 'cheque'),
    payment_date DATE,
    notes TEXT,
    terms_conditions TEXT,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Purchase order items
CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_id UUID REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL, -- Store name for historical records
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    received_quantity INTEGER DEFAULT 0,
    quality_grade ENUM('excellent', 'very-good', 'good', 'fair', 'poor'),
    batch_number VARCHAR(50),
    expiry_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **5. Billing & Payments**

```sql
-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_number VARCHAR(20) UNIQUE NOT NULL, -- INV-001, INV-002, etc.
    supplier_id UUID REFERENCES suppliers(id) NOT NULL,
    po_id UUID REFERENCES purchase_orders(id),
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    paid_amount DECIMAL(15,2) DEFAULT 0,
    balance_amount DECIMAL(15,2) NOT NULL,
    status ENUM('pending', 'overdue', 'paid', 'partial', 'cancelled') DEFAULT 'pending',
    payment_terms VARCHAR(50),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Invoice items
CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_number VARCHAR(20) UNIQUE NOT NULL, -- PAY-001, PAY-002, etc.
    invoice_id UUID REFERENCES invoices(id),
    supplier_id UUID REFERENCES suppliers(id) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    payment_method ENUM('upi', 'card', 'cash', 'bank_transfer', 'cheque') NOT NULL,
    payment_date DATE NOT NULL,
    reference_number VARCHAR(100),
    transaction_id VARCHAR(100),
    status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **6. Warehouse & Operations**

```sql
-- Staff management
CREATE TABLE staff_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    department ENUM('receiving', 'quality_control', 'packing', 'dispatch', 'maintenance', 'administration') NOT NULL,
    position VARCHAR(100) NOT NULL,
    shift ENUM('morning', 'afternoon', 'evening', 'night') NOT NULL,
    shift_start_time TIME,
    shift_end_time TIME,
    hourly_rate DECIMAL(8,2),
    status ENUM('active', 'on_break', 'off_duty', 'on_leave', 'inactive') DEFAULT 'active',
    performance_score DECIMAL(5,2) DEFAULT 0,
    hire_date DATE,
    supervisor_id UUID REFERENCES staff_members(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staff attendance
CREATE TABLE staff_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    staff_id UUID REFERENCES staff_members(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    break_start_time TIMESTAMP,
    break_end_time TIMESTAMP,
    total_hours DECIMAL(4,2),
    overtime_hours DECIMAL(4,2) DEFAULT 0,
    status ENUM('present', 'absent', 'late', 'half_day', 'on_leave') NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(staff_id, date)
);

-- Tasks and assignments
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type ENUM('receiving', 'quality_check', 'packing', 'dispatch', 'maintenance', 'inventory_count', 'cleaning') NOT NULL,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    assigned_to UUID REFERENCES staff_members(id),
    assigned_by UUID REFERENCES users(id),
    estimated_hours DECIMAL(4,2),
    actual_hours DECIMAL(4,2),
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **7. Logistics & Delivery**

```sql
-- Fleet vehicles
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type ENUM('van', 'truck', 'bike', 'car') NOT NULL,
    model VARCHAR(100),
    capacity_kg DECIMAL(8,2),
    fuel_type ENUM('petrol', 'diesel', 'electric', 'cng') NOT NULL,
    status ENUM('active', 'maintenance', 'inactive') DEFAULT 'active',
    current_location POINT,
    last_maintenance_date DATE,
    next_maintenance_date DATE,
    insurance_expiry DATE,
    registration_expiry DATE,
    driver_id UUID REFERENCES staff_members(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery routes
CREATE TABLE delivery_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_code VARCHAR(20) UNIQUE NOT NULL, -- RT-001, RT-002, etc.
    name VARCHAR(255) NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id),
    driver_id UUID REFERENCES staff_members(id),
    route_date DATE NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_distance_km DECIMAL(8,2),
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    fuel_cost DECIMAL(10,2),
    status ENUM('planned', 'in_progress', 'completed', 'cancelled') DEFAULT 'planned',
    optimization_type ENUM('distance', 'time', 'fuel', 'hybrid') DEFAULT 'distance',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer orders (for delivery tracking)
CREATE TABLE customer_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(20) UNIQUE NOT NULL, -- ORD-001, ORD-002, etc.
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(255),
    delivery_address TEXT NOT NULL,
    city VARCHAR(100),
    postal_code VARCHAR(20),
    coordinates POINT,
    total_amount DECIMAL(15,2) NOT NULL,
    payment_method ENUM('cod', 'online', 'upi', 'card') NOT NULL,
    payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'pending',
    delivery_date DATE,
    delivery_time_slot VARCHAR(20), -- "10:00-12:00", "14:00-16:00", etc.
    special_instructions TEXT,
    status ENUM('pending', 'confirmed', 'packed', 'out_for_delivery', 'delivered', 'cancelled', 'returned') DEFAULT 'pending',
    route_id UUID REFERENCES delivery_routes(id),
    delivery_sequence INTEGER,
    otp VARCHAR(6),
    delivered_at TIMESTAMP,
    delivered_by UUID REFERENCES staff_members(id),
    customer_signature TEXT, -- Base64 encoded signature
    delivery_photo_url VARCHAR(500),
    delivery_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES customer_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit VARCHAR(20) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    quality_grade ENUM('excellent', 'very-good', 'good', 'fair', 'poor'),
    batch_number VARCHAR(50),
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route optimization history
CREATE TABLE route_optimizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID REFERENCES delivery_routes(id) ON DELETE CASCADE,
    optimization_type ENUM('distance', 'time', 'fuel', 'hybrid') NOT NULL,
    original_distance_km DECIMAL(8,2),
    optimized_distance_km DECIMAL(8,2),
    distance_saved_km DECIMAL(8,2),
    original_duration_minutes INTEGER,
    optimized_duration_minutes INTEGER,
    time_saved_minutes INTEGER,
    fuel_cost_original DECIMAL(10,2),
    fuel_cost_optimized DECIMAL(10,2),
    fuel_cost_saved DECIMAL(10,2),
    co2_saved_kg DECIMAL(8,2),
    efficiency_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **8. Quality Control & Monitoring**

```sql
-- Quality checks
CREATE TABLE quality_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_number VARCHAR(20) UNIQUE NOT NULL, -- QC-001, QC-002, etc.
    product_id UUID REFERENCES products(id) NOT NULL,
    batch_number VARCHAR(50),
    check_type ENUM('incoming', 'storage', 'pre_dispatch', 'random') NOT NULL,
    inspector_id UUID REFERENCES staff_members(id) NOT NULL,
    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_grade ENUM('excellent', 'very-good', 'good', 'fair', 'poor', 'rejected') NOT NULL,
    appearance_score INTEGER CHECK (appearance_score >= 1 AND appearance_score <= 10),
    freshness_score INTEGER CHECK (freshness_score >= 1 AND freshness_score <= 10),
    size_uniformity_score INTEGER CHECK (size_uniformity_score >= 1 AND size_uniformity_score <= 10),
    color_score INTEGER CHECK (color_score >= 1 AND color_score <= 10),
    texture_score INTEGER CHECK (texture_score >= 1 AND texture_score <= 10),
    aroma_score INTEGER CHECK (aroma_score >= 1 AND aroma_score <= 10),
    overall_score DECIMAL(4,2),
    temperature_at_check DECIMAL(5,2),
    humidity_at_check DECIMAL(5,2),
    weight_kg DECIMAL(8,3),
    passed BOOLEAN NOT NULL,
    rejection_reason TEXT,
    corrective_actions TEXT,
    notes TEXT,
    photos JSON, -- Array of photo URLs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Temperature monitoring
CREATE TABLE temperature_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    storage_location_id UUID REFERENCES storage_locations(id) NOT NULL,
    sensor_id VARCHAR(50),
    temperature DECIMAL(5,2) NOT NULL,
    humidity DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_triggered BOOLEAN DEFAULT false,
    alert_type ENUM('high_temp', 'low_temp', 'high_humidity', 'low_humidity', 'sensor_failure'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Waste tracking
CREATE TABLE waste_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) NOT NULL,
    quantity_kg DECIMAL(8,3) NOT NULL,
    waste_reason ENUM('expired', 'damaged', 'quality_issue', 'overstock', 'contamination') NOT NULL,
    batch_number VARCHAR(50),
    disposal_method ENUM('compost', 'donation', 'animal_feed', 'landfill', 'incineration') NOT NULL,
    cost_impact DECIMAL(10,2),
    reported_by UUID REFERENCES staff_members(id) NOT NULL,
    approved_by UUID REFERENCES users(id),
    disposal_date DATE,
    notes TEXT,
    photos JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **9. Analytics & Reporting**

```sql
-- Business analytics snapshots
CREATE TABLE business_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL,
    total_revenue DECIMAL(15,2) DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_customers INTEGER DEFAULT 0,
    new_customers INTEGER DEFAULT 0,
    avg_order_value DECIMAL(10,2) DEFAULT 0,
    inventory_value DECIMAL(15,2) DEFAULT 0,
    waste_percentage DECIMAL(5,2) DEFAULT 0,
    delivery_efficiency DECIMAL(5,2) DEFAULT 0,
    quality_score DECIMAL(5,2) DEFAULT 0,
    supplier_performance DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date)
);

-- System analytics
CREATE TABLE system_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date DATE NOT NULL,
    active_users INTEGER DEFAULT 0,
    total_logins INTEGER DEFAULT 0,
    api_requests INTEGER DEFAULT 0,
    error_rate DECIMAL(5,4) DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0,
    storage_used_gb DECIMAL(10,2) DEFAULT 0,
    bandwidth_used_gb DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date)
);

-- Audit logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSON,
    new_values JSON,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Security events
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type ENUM('failed_login', 'suspicious_activity', 'unauthorized_access', 'data_breach', 'password_change', 'account_lockout') NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    description TEXT,
    status ENUM('open', 'investigating', 'resolved', 'false_positive') DEFAULT 'open',
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **10. System Configuration**

```sql
-- System settings
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
    category ENUM('system', 'order', 'inventory', 'payment', 'delivery', 'quality') NOT NULL,
    is_read BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 **API Endpoints Specification**

### **1. 🛡️ Super Admin Portal APIs**

#### **Authentication & User Management**
```http
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/me

# User Management
GET    /api/admin/users
POST   /api/admin/users
GET    /api/admin/users/{id}
PUT    /api/admin/users/{id}
DELETE /api/admin/users/{id}
PUT    /api/admin/users/{id}/status
PUT    /api/admin/users/{id}/password

# Role & Permission Management
GET    /api/admin/roles
POST   /api/admin/roles
GET    /api/admin/roles/{id}
PUT    /api/admin/roles/{id}
DELETE /api/admin/roles/{id}
GET    /api/admin/permissions
POST   /api/admin/users/{id}/roles
DELETE /api/admin/users/{id}/roles/{roleId}
```

#### **System Analytics & Monitoring**
```http
# Business Analytics
GET    /api/admin/analytics/business
GET    /api/admin/analytics/revenue
GET    /api/admin/analytics/customers
GET    /api/admin/analytics/orders
GET    /api/admin/analytics/products

# System Analytics
GET    /api/admin/analytics/system
GET    /api/admin/analytics/performance
GET    /api/admin/analytics/usage
GET    /api/admin/analytics/errors

# Security Monitoring
GET    /api/admin/security/events
GET    /api/admin/security/threats
GET    /api/admin/security/audit-logs
PUT    /api/admin/security/events/{id}/resolve

# System Settings
GET    /api/admin/settings
PUT    /api/admin/settings
GET    /api/admin/settings/{key}
PUT    /api/admin/settings/{key}
```

### **2. 🏭 Warehouse Manager Portal APIs**

#### **Inventory Management**
```http
# Products
GET    /api/warehouse/products
POST   /api/warehouse/products
GET    /api/warehouse/products/{id}
PUT    /api/warehouse/products/{id}
DELETE /api/warehouse/products/{id}
GET    /api/warehouse/products/search
GET    /api/warehouse/products/low-stock
GET    /api/warehouse/products/categories

# Stock Management
GET    /api/warehouse/stock/movements
POST   /api/warehouse/stock/movements
GET    /api/warehouse/stock/levels
POST   /api/warehouse/stock/adjustment
POST   /api/warehouse/stock/transfer
GET    /api/warehouse/stock/receiving
POST   /api/warehouse/stock/receiving
```

#### **Quality Control**
```http
# Quality Checks
GET    /api/warehouse/quality/checks
POST   /api/warehouse/quality/checks
GET    /api/warehouse/quality/checks/{id}
PUT    /api/warehouse/quality/checks/{id}
GET    /api/warehouse/quality/metrics
GET    /api/warehouse/quality/reports

# Temperature Monitoring
GET    /api/warehouse/temperature/logs
GET    /api/warehouse/temperature/alerts
GET    /api/warehouse/storage/locations
PUT    /api/warehouse/storage/locations/{id}
```

#### **Staff & Operations Management**
```http
# Staff Management
GET    /api/warehouse/staff
POST   /api/warehouse/staff
GET    /api/warehouse/staff/{id}
PUT    /api/warehouse/staff/{id}
GET    /api/warehouse/staff/attendance
POST   /api/warehouse/staff/attendance
GET    /api/warehouse/staff/performance

# Task Management
GET    /api/warehouse/tasks
POST   /api/warehouse/tasks
GET    /api/warehouse/tasks/{id}
PUT    /api/warehouse/tasks/{id}
PUT    /api/warehouse/tasks/{id}/status
GET    /api/warehouse/tasks/assignments

# Operations Overview
GET    /api/warehouse/operations/overview
GET    /api/warehouse/operations/metrics
GET    /api/warehouse/operations/alerts
```

#### **Logistics & Delivery**
```http
# Fleet Management
GET    /api/warehouse/fleet/vehicles
POST   /api/warehouse/fleet/vehicles
GET    /api/warehouse/fleet/vehicles/{id}
PUT    /api/warehouse/fleet/vehicles/{id}
GET    /api/warehouse/fleet/maintenance

# Route Management
GET    /api/warehouse/routes
POST   /api/warehouse/routes
GET    /api/warehouse/routes/{id}
PUT    /api/warehouse/routes/{id}
POST   /api/warehouse/routes/optimize
GET    /api/warehouse/routes/performance

# Delivery Tracking
GET    /api/warehouse/deliveries
GET    /api/warehouse/deliveries/active
GET    /api/warehouse/deliveries/{id}
PUT    /api/warehouse/deliveries/{id}/status
GET    /api/warehouse/deliveries/tracking/{id}
```

#### **Analytics & Reporting**
```http
# Inventory Analytics
GET    /api/warehouse/analytics/inventory
GET    /api/warehouse/analytics/turnover
GET    /api/warehouse/analytics/waste
GET    /api/warehouse/analytics/valuation

# Performance Analytics
GET    /api/warehouse/analytics/performance
GET    /api/warehouse/analytics/efficiency
GET    /api/warehouse/analytics/costs
GET    /api/warehouse/analytics/trends

# Quality Metrics
GET    /api/warehouse/analytics/quality
GET    /api/warehouse/analytics/compliance
GET    /api/warehouse/analytics/defects
```

### **3. 🏪 Supplier Portal APIs**

#### **Supplier Management**
```http
# Suppliers
GET    /api/suppliers
POST   /api/suppliers
GET    /api/suppliers/{id}
PUT    /api/suppliers/{id}
DELETE /api/suppliers/{id}
GET    /api/suppliers/categories
POST   /api/suppliers/categories
GET    /api/suppliers/performance
POST   /api/suppliers/{id}/reviews
```

#### **Purchase Order Management**
```http
# Purchase Orders
GET    /api/suppliers/purchase-orders
POST   /api/suppliers/purchase-orders
GET    /api/suppliers/purchase-orders/{id}
PUT    /api/suppliers/purchase-orders/{id}
DELETE /api/suppliers/purchase-orders/{id}
PUT    /api/suppliers/purchase-orders/{id}/status
POST   /api/suppliers/purchase-orders/{id}/items
PUT    /api/suppliers/purchase-orders/{id}/items/{itemId}
DELETE /api/suppliers/purchase-orders/{id}/items/{itemId}
GET    /api/suppliers/purchase-orders/{id}/history
```

#### **Billing & Payment Management**
```http
# Invoices
GET    /api/suppliers/invoices
POST   /api/suppliers/invoices
GET    /api/suppliers/invoices/{id}
PUT    /api/suppliers/invoices/{id}
DELETE /api/suppliers/invoices/{id}
GET    /api/suppliers/invoices/overdue
GET    /api/suppliers/invoices/{id}/pdf

# Payments
GET    /api/suppliers/payments
POST   /api/suppliers/payments
GET    /api/suppliers/payments/{id}
PUT    /api/suppliers/payments/{id}
GET    /api/suppliers/payments/methods
POST   /api/suppliers/payments/process
```

#### **Analytics & Reporting**
```http
# Supplier Analytics
GET    /api/suppliers/analytics/dashboard
GET    /api/suppliers/analytics/performance
GET    /api/suppliers/analytics/spending
GET    /api/suppliers/analytics/payments
GET    /api/suppliers/analytics/trends

# Reports
GET    /api/suppliers/reports/summary
GET    /api/suppliers/reports/payments
GET    /api/suppliers/reports/orders
GET    /api/suppliers/reports/performance
```

### **4. 📱 Mobile/Delivery APIs**

#### **Delivery Personnel APIs**
```http
# Authentication
POST   /api/mobile/auth/login
POST   /api/mobile/auth/logout
GET    /api/mobile/auth/profile

# Delivery Management
GET    /api/mobile/deliveries/assigned
GET    /api/mobile/deliveries/{id}
PUT    /api/mobile/deliveries/{id}/status
POST   /api/mobile/deliveries/{id}/location
POST   /api/mobile/deliveries/{id}/proof
POST   /api/mobile/deliveries/{id}/signature
POST   /api/mobile/deliveries/{id}/photo

# Route Management
GET    /api/mobile/routes/current
GET    /api/mobile/routes/{id}/orders
PUT    /api/mobile/routes/{id}/optimize
POST   /api/mobile/routes/{id}/start
POST   /api/mobile/routes/{id}/complete
```

### **5. 🔔 Real-time & Notifications**

#### **WebSocket Endpoints**
```websocket
# Real-time tracking
WS     /ws/tracking/{routeId}
WS     /ws/inventory/alerts
WS     /ws/quality/alerts
WS     /ws/notifications/{userId}

# System monitoring
WS     /ws/admin/system-status
WS     /ws/admin/security-events
```

#### **Notification APIs**
```http
GET    /api/notifications
POST   /api/notifications
PUT    /api/notifications/{id}/read
PUT    /api/notifications/mark-all-read
DELETE /api/notifications/{id}
GET    /api/notifications/settings
PUT    /api/notifications/settings
```

---

## 📊 **Analytics & Dashboard Requirements**

### **1. Super Admin Dashboard**

#### **Key Metrics Cards**
- **Total Revenue**: Monthly/yearly revenue with growth percentage
- **Active Users**: Current active users across all portals
- **System Performance**: API response times, uptime percentage
- **Security Score**: Overall security rating with threat indicators
- **Data Storage**: Current storage usage and growth trends
- **Active Sessions**: Real-time user sessions across portals

#### **Business Analytics Charts**
- **Revenue Trends**: Line chart showing monthly revenue growth
- **User Growth**: Area chart showing user acquisition over time
- **Portal Usage**: Pie chart showing usage distribution across portals
- **Order Volume**: Bar chart showing order volumes by category
- **Geographic Distribution**: Map showing user/order distribution
- **Performance Metrics**: Multi-line chart showing key KPIs

#### **System Analytics**
- **API Performance**: Response time trends and error rates
- **Database Performance**: Query performance and connection pools
- **Server Resources**: CPU, memory, disk usage over time
- **Error Tracking**: Error frequency and types
- **Security Events**: Timeline of security incidents
- **Audit Trail**: Recent system changes and user activities

### **2. Warehouse Manager Dashboard**

#### **Operational Metrics**
- **Total Inventory**: Current stock value and quantity
- **Active Fleet**: Vehicles in operation vs total fleet
- **Staff On Duty**: Current active staff vs total staff
- **Orders Processed**: Daily order processing metrics
- **Quality Score**: Average quality rating across products
- **Delivery Efficiency**: On-time delivery percentage

#### **Inventory Analytics**
- **Stock Levels**: Real-time stock levels with alerts
- **Turnover Rates**: Product turnover analysis
- **Waste Tracking**: Waste percentage and cost impact
- **Storage Utilization**: Capacity utilization by storage type
- **Reorder Alerts**: Products requiring reorder
- **Expiry Tracking**: Products nearing expiry

#### **Quality Metrics**
- **Quality Scores**: Trends in quality ratings
- **Rejection Rates**: Product rejection percentages
- **Temperature Compliance**: Cold chain monitoring
- **Inspection Results**: Quality check outcomes
- **Corrective Actions**: Actions taken for quality issues
- **Compliance Reports**: Regulatory compliance status

#### **Logistics Performance**
- **Route Efficiency**: Distance and time optimization results
- **Fuel Consumption**: Fuel usage and cost analysis
- **Delivery Performance**: On-time delivery rates
- **Vehicle Utilization**: Fleet utilization metrics
- **Driver Performance**: Individual driver metrics
- **Customer Satisfaction**: Delivery feedback scores

### **3. Supplier Portal Dashboard**

#### **Supplier Metrics**
- **Active Suppliers**: Total active supplier count
- **Monthly Spending**: Total procurement spending
- **Purchase Orders**: Active PO count and value
- **Payment Pending**: Outstanding payment amounts
- **Supplier Performance**: Average supplier ratings
- **Category Distribution**: Spending by product category

#### **Financial Analytics**
- **Payment Trends**: Payment patterns over time
- **Outstanding Invoices**: Overdue payment tracking
- **Cash Flow**: Projected cash flow based on payment terms
- **Supplier Comparison**: Cost comparison across suppliers
- **Budget Tracking**: Budget vs actual spending
- **Cost Savings**: Savings from negotiations and optimization

#### **Procurement Analytics**
- **Order Volume**: Purchase order trends
- **Lead Times**: Supplier delivery performance
- **Quality Metrics**: Supplier quality ratings
- **Price Trends**: Product price changes over time
- **Supplier Reliability**: On-time delivery rates
- **Contract Performance**: Contract compliance metrics

---

## 🔐 **Authentication & Authorization**

### **Authentication System**

#### **JWT-based Authentication**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "roles": ["warehouse_manager"],
    "permissions": ["inventory:read", "inventory:write"]
  }
}
```

#### **Role-Based Access Control (RBAC)**

**Roles Hierarchy:**
```
Super Admin
├── System Management (all permissions)
├── User Management
├── Security Monitoring
└── Business Analytics

Warehouse Manager
├── Inventory Management
├── Staff Management
├── Quality Control
├── Logistics Management
└── Operations Analytics

Logistics Manager
├── Route Planning
├── Fleet Management
├── Delivery Tracking
└── Performance Analytics

Inventory Staff
├── Product Management
├── Stock Control
└── Quality Checks

Delivery Personnel
├── Order Delivery
├── Route Navigation
└── Customer Interaction

Supplier Manager
├── Supplier Management
├── Purchase Orders
├── Billing & Payments
└── Supplier Analytics

Customer
├── Order Placement
├── Order Tracking
└── Profile Management
```

**Permission Matrix:**
```json
{
  "super_admin": ["*"],
  "warehouse_manager": [
    "inventory:*",
    "staff:*",
    "quality:*",
    "logistics:*",
    "analytics:warehouse"
  ],
  "logistics_manager": [
    "routes:*",
    "fleet:*",
    "deliveries:*",
    "analytics:logistics"
  ],
  "inventory_staff": [
    "products:read",
    "products:write",
    "stock:read",
    "stock:write",
    "quality:read",
    "quality:write"
  ],
  "delivery_personnel": [
    "deliveries:read",
    "deliveries:update_status",
    "routes:read",
    "customers:contact"
  ],
  "supplier_manager": [
    "suppliers:*",
    "purchase_orders:*",
    "invoices:*",
    "payments:*",
    "analytics:supplier"
  ]
}
```

### **Security Features**

#### **Password Policy**
- Minimum 8 characters
- Must contain uppercase, lowercase, number, and special character
- Password history (prevent reuse of last 5 passwords)
- Password expiry (90 days for admin roles)
- Account lockout after 5 failed attempts

#### **Two-Factor Authentication (2FA)**
- SMS-based OTP
- TOTP (Time-based One-Time Password)
- Backup codes for recovery
- Mandatory for admin roles

#### **Session Management**
- JWT tokens with short expiry (1 hour)
- Refresh tokens with longer expiry (7 days)
- Session tracking and management
- Concurrent session limits
- Remote session termination

#### **API Security**
- Rate limiting (1000 requests/hour per user)
- Request signing for sensitive operations
- IP whitelisting for admin operations
- CORS configuration
- Input validation and sanitization

---

## 🚀 **Technical Implementation Guidelines**

### **Backend Technology Stack**

#### **Core Framework**
- **Node.js** with **Express.js** or **Fastify**
- **TypeScript** for type safety
- **PostgreSQL** as primary database
- **Redis** for caching and sessions
- **MongoDB** for logs and analytics (optional)

#### **Authentication & Security**
- **JWT** for authentication
- **bcrypt** for password hashing
- **helmet** for security headers
- **rate-limiter-flexible** for rate limiting
- **joi** or **zod** for input validation

#### **Database & ORM**
- **Prisma** or **TypeORM** for database operations
- **Database migrations** for schema management
- **Connection pooling** for performance
- **Read replicas** for analytics queries

#### **Real-time Features**
- **Socket.io** for WebSocket connections
- **Redis Pub/Sub** for real-time events
- **Server-Sent Events** for live updates
- **Push notifications** via FCM/APNs

#### **File Storage & Processing**
- **AWS S3** or **Cloudinary** for file storage
- **Sharp** for image processing
- **Multer** for file uploads
- **PDF generation** with **Puppeteer**

#### **Monitoring & Logging**
- **Winston** for application logging
- **Morgan** for HTTP request logging
- **Prometheus** for metrics collection
- **Grafana** for monitoring dashboards
- **Sentry** for error tracking

### **API Design Principles**

#### **RESTful Design**
- Use HTTP methods appropriately (GET, POST, PUT, DELETE)
- Consistent URL structure (/api/v1/resource)
- Proper HTTP status codes
- Pagination for list endpoints
- Filtering and sorting support

#### **Response Format**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  },
  "message": "Success"
}
```

#### **Error Handling**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Performance Optimization**

#### **Database Optimization**
- Proper indexing strategy
- Query optimization
- Connection pooling
- Read replicas for analytics
- Database partitioning for large tables

#### **Caching Strategy**
- **Redis** for session storage
- **Application-level caching** for frequently accessed data
- **Database query caching**
- **CDN** for static assets
- **HTTP caching headers**

#### **API Performance**
- **Compression** (gzip/brotli)
- **Response pagination**
- **Field selection** (sparse fieldsets)
- **Batch operations** where applicable
- **Async processing** for heavy operations

### **Deployment & DevOps**

#### **Containerization**
- **Docker** containers for all services
- **Docker Compose** for local development
- **Multi-stage builds** for optimization
- **Health checks** for containers

#### **Orchestration**
- **Kubernetes** for production deployment
- **Helm charts** for configuration management
- **Horizontal Pod Autoscaling**
- **Load balancing** with ingress controllers

#### **CI/CD Pipeline**
- **GitHub Actions** or **GitLab CI**
- **Automated testing** (unit, integration, e2e)
- **Code quality checks** (ESLint, Prettier, SonarQube)
- **Security scanning** (Snyk, OWASP)
- **Automated deployment** to staging/production

#### **Monitoring & Alerting**
- **Application Performance Monitoring** (APM)
- **Infrastructure monitoring** (CPU, memory, disk)
- **Log aggregation** (ELK stack or similar)
- **Alert management** (PagerDuty, Slack integration)
- **Uptime monitoring** (external services)

---

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Microservices architecture** for independent scaling
- **Load balancing** across multiple instances
- **Database sharding** for large datasets
- **CDN** for global content delivery
- **Auto-scaling** based on metrics

### **Vertical Scaling**
- **Resource optimization** (CPU, memory)
- **Database performance tuning**
- **Connection pooling** optimization
- **Caching layer** improvements

### **Data Management**
- **Data archiving** for old records
- **Data partitioning** by date/region
- **Read replicas** for analytics
- **Data compression** for storage optimization
- **Backup and disaster recovery**

---

## 🔄 **Integration Points**

### **Third-party Integrations**

#### **Payment Gateways**
- **Razorpay** for UPI/card payments
- **PayU** for alternative payment methods
- **Bank APIs** for direct transfers
- **Webhook handling** for payment status

#### **SMS & Email Services**
- **Twilio** or **AWS SNS** for SMS
- **SendGrid** or **AWS SES** for emails
- **WhatsApp Business API** for notifications
- **Push notification services**

#### **Maps & Location Services**
- **Google Maps API** for route optimization
- **Mapbox** for custom mapping
- **Geolocation services** for tracking
- **Address validation** services

#### **Analytics & Reporting**
- **Google Analytics** for web analytics
- **Mixpanel** for user behavior tracking
- **Custom reporting** with **Chart.js**
- **Data export** to Excel/PDF

### **API Integration Guidelines**
- **Webhook endpoints** for real-time updates
- **Rate limiting** for external API calls
- **Retry mechanisms** with exponential backoff
- **Circuit breakers** for fault tolerance
- **API versioning** for backward compatibility

---

## 📋 **Development Phases**

### **Phase 1: Core Infrastructure (4-6 weeks)**
1. **Database setup** and schema implementation
2. **Authentication system** with JWT and RBAC
3. **Basic API structure** with Express.js/Fastify
4. **User management** APIs
5. **Security implementation** (rate limiting, validation)

### **Phase 2: Supplier Portal Backend (3-4 weeks)**
1. **Supplier management** APIs
2. **Purchase order** management
3. **Billing and payment** processing
4. **Basic analytics** endpoints
5. **File upload** functionality

### **Phase 3: Warehouse Management Backend (4-5 weeks)**
1. **Inventory management** APIs
2. **Product and category** management
3. **Stock movement** tracking
4. **Quality control** system
5. **Staff management** APIs

### **Phase 4: Logistics & Delivery Backend (3-4 weeks)**
1. **Fleet management** APIs
2. **Route optimization** algorithms
3. **Delivery tracking** system
4. **Real-time location** updates
5. **Mobile APIs** for delivery personnel

### **Phase 5: Analytics & Reporting (2-3 weeks)**
1. **Business analytics** calculations
2. **Dashboard metrics** APIs
3. **Report generation** system
4. **Data visualization** endpoints
5. **Performance monitoring**

### **Phase 6: Advanced Features (3-4 weeks)**
1. **Real-time notifications** system
2. **Advanced analytics** and ML insights
3. **Integration** with third-party services
4. **Performance optimization**
5. **Security enhancements**

### **Phase 7: Testing & Deployment (2-3 weeks)**
1. **Comprehensive testing** (unit, integration, load)
2. **Security testing** and penetration testing
3. **Performance testing** and optimization
4. **Production deployment** setup
5. **Monitoring and alerting** configuration

---

## 🧪 **Testing Strategy**

### **Unit Testing**
- **Jest** for JavaScript/TypeScript testing
- **Test coverage** minimum 80%
- **Mock external dependencies**
- **Database testing** with test containers
- **API endpoint testing**

### **Integration Testing**
- **Supertest** for API integration tests
- **Database integration** testing
- **Third-party service** integration tests
- **End-to-end workflow** testing
- **Authentication flow** testing

### **Load Testing**
- **Artillery** or **k6** for load testing
- **Database performance** under load
- **API response times** under stress
- **Concurrent user** simulation
- **Resource utilization** monitoring

### **Security Testing**
- **OWASP ZAP** for security scanning
- **SQL injection** testing
- **Authentication bypass** testing
- **Authorization** testing
- **Input validation** testing

---

## 📚 **Documentation Requirements**

### **API Documentation**
- **OpenAPI/Swagger** specification
- **Interactive API** documentation
- **Code examples** in multiple languages
- **Authentication** examples
- **Error handling** documentation

### **Database Documentation**
- **Entity Relationship Diagrams** (ERD)
- **Table schemas** with descriptions
- **Index strategies** documentation
- **Migration scripts** documentation
- **Backup and recovery** procedures

### **Deployment Documentation**
- **Environment setup** instructions
- **Configuration management**
- **Docker deployment** guide
- **Kubernetes manifests**
- **Monitoring setup** guide

### **Developer Documentation**
- **Code style** guidelines
- **Architecture** documentation
- **Contributing** guidelines
- **Troubleshooting** guide
- **Performance** optimization tips

---

## 🎯 **Success Metrics & KPIs**

### **Technical Metrics**
- **API Response Time**: < 200ms for 95% of requests
- **Uptime**: 99.9% availability
- **Error Rate**: < 0.1% of total requests
- **Database Performance**: < 50ms average query time
- **Security**: Zero critical vulnerabilities

### **Business Metrics**
- **User Adoption**: 90% of target users onboarded
- **Feature Usage**: 80% of features actively used
- **Data Accuracy**: 99% inventory accuracy
- **Process Efficiency**: 30% reduction in manual processes
- **Cost Savings**: 20% reduction in operational costs

### **Performance Benchmarks**
- **Concurrent Users**: Support 1000+ concurrent users
- **Data Volume**: Handle 10M+ records efficiently
- **File Storage**: Support 100GB+ file storage
- **Real-time Updates**: < 1 second notification delivery
- **Backup & Recovery**: < 4 hours RTO, < 1 hour RPO

---

## 🔮 **Future Enhancements**

### **AI/ML Integration**
- **Demand forecasting** using historical data
- **Route optimization** with machine learning
- **Quality prediction** based on sensor data
- **Anomaly detection** for inventory and operations
- **Chatbot integration** for customer support

### **Advanced Analytics**
- **Predictive analytics** for inventory planning
- **Real-time dashboards** with streaming data
- **Custom report builder** for users
- **Data warehouse** integration
- **Business intelligence** tools integration

### **IoT Integration**
- **Temperature sensors** for cold chain monitoring
- **RFID tags** for inventory tracking
- **GPS tracking** for vehicle monitoring
- **Weight sensors** for automated inventory
- **Camera integration** for quality checks

### **Mobile Applications**
- **Native mobile apps** for iOS and Android
- **Offline functionality** for delivery personnel
- **Barcode scanning** capabilities
- **Push notifications** for real-time updates
- **Geofencing** for location-based features

---

This comprehensive backend development specification provides a complete roadmap for implementing the Aurora Spark Theme inventory management system. The document covers all aspects from database design to deployment strategies, ensuring a robust, scalable, and secure backend infrastructure that supports all three portals effectively.
