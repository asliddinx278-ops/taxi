# =====================================================
# 🚕 PROFESSIONAL TAXI MANAGEMENT SYSTEM
# All Backend Code Combined - Complete System
# =====================================================

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
from enum import Enum
import json

# Flask & Extensions
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Database
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

# Other
from dotenv import load_dotenv
import requests
from functools import wraps
import telebot
from telebot import types

# =====================================================
# 📋 CONFIGURATION MANAGEMENT
# =====================================================

load_dotenv()

class Config:
    """Configuration settings"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///taxi_system.db')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
    ORDER_TIMEOUT_MINUTES = int(os.getenv('ORDER_TIMEOUT_MINUTES', 5))
    AUTO_ASSIGN_RADIUS_KM = float(os.getenv('AUTO_ASSIGN_RADIUS_KM', 5.0))

# =====================================================
# 🗄️ DATABASE MODELS
# =====================================================

Base = declarative_base()

class UserRole(Enum):
    CUSTOMER = "customer"
    DRIVER = "driver"
    DISPATCHER = "dispatcher"
    ADMIN = "admin"

class OrderStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    telegram_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders_as_customer = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    orders_as_driver = relationship("Order", foreign_keys="Order.driver_id", back_populates="driver")
    dispatcher_calls = relationship("DispatcherCall", back_populates="dispatcher")
    driver_locations = relationship("DriverLocation", back_populates="driver")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    dispatcher_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    pickup_location = Column(String, nullable=False)
    destination_location = Column(String, nullable=False)
    passengers_count = Column(Integer, default=1)
    order_type = Column(String, default="standard")  # standard, shared, premium
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    
    customer_phone = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_comment = Column(String, nullable=True)
    
    pickup_lat = Column(Float, nullable=True)
    pickup_lng = Column(Float, nullable=True)
    destination_lat = Column(Float, nullable=True)
    destination_lng = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    scheduled_time = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders_as_customer")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="orders_as_driver")

class DriverLocation(Base):
    __tablename__ = "driver_locations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    driver_id = Column(String, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    driver = relationship("User", back_populates="driver_locations")

class DispatcherCall(Base):
    __tablename__ = "dispatcher_calls"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dispatcher_id = Column(String, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=True)
    
    customer_phone = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_location = Column(String, nullable=True)
    passenger_count = Column(Integer, default=1)
    call_notes = Column(String, nullable=True)
    
    call_status = Column(String, default="received")  # received, processing, completed
    received_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    dispatcher = relationship("User", back_populates="dispatcher_calls")

# =====================================================
# 🔌 DATABASE INITIALIZATION
# =====================================================

# Create database engine
if 'sqlite' in Config.DATABASE_URL:
    engine = create_engine(
        Config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(Config.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

# =====================================================
# 🌐 FLASK APP & API ENDPOINTS
# =====================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET

CORS(app)
jwt = JWTManager(app)

# =====================================================
# 🔐 AUTHENTICATION ENDPOINTS
# =====================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        phone = data.get('phone')
        name = data.get('name', 'Unknown')
        role = data.get('role', 'customer')
        
        if not phone:
            return jsonify({'error': 'Phone required'}), 400
        
        db = SessionLocal()
        
        # Check if user exists
        existing = db.query(User).filter(User.phone == phone).first()
        if existing:
            db.close()
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user = User(
            phone=phone,
            name=name,
            role=UserRole[role.upper()] if role.upper() in UserRole.__members__ else UserRole.CUSTOMER
        )
        db.add(user)
        db.commit()
        
        # Generate token
        access_token = create_access_token(identity=user.id)
        db.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'access_token': access_token
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with phone"""
    try:
        data = request.json
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'error': 'Phone required'}), 400
        
        db = SessionLocal()
        user = db.query(User).filter(User.phone == phone).first()
        
        if not user or not user.is_active:
            db.close()
            return jsonify({'error': 'User not found or inactive'}), 401
        
        access_token = create_access_token(identity=user.id)
        
        result = {
            'message': 'Login successful',
            'user_id': user.id,
            'phone': user.phone,
            'name': user.name,
            'role': user.role.value,
            'access_token': access_token
        }
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# 👤 CUSTOMER ENDPOINTS
# =====================================================

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    """Create new order"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        order = Order(
            customer_id=user_id,
            pickup_location=data.get('pickup_location', ''),
            destination_location=data.get('destination_location', ''),
            passengers_count=data.get('passengers_count', 1),
            customer_phone=user.phone,
            customer_name=user.name,
            customer_comment=data.get('comment', ''),
            estimated_price=data.get('estimated_price', 0),
            pickup_lat=data.get('pickup_lat'),
            pickup_lng=data.get('pickup_lng'),
            destination_lat=data.get('destination_lat'),
            destination_lng=data.get('destination_lng')
        )
        
        db.add(order)
        db.commit()
        order_id = order.id
        db.close()
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Get user's orders"""
    try:
        user_id = get_jwt_identity()
        db = SessionLocal()
        
        orders = db.query(Order).filter(Order.customer_id == user_id).all()
        result = []
        
        for order in orders:
            result.append({
                'id': order.id,
                'pickup': order.pickup_location,
                'destination': order.destination_location,
                'status': order.status.value,
                'passengers': order.passengers_count,
                'estimated_price': order.estimated_price,
                'final_price': order.final_price,
                'driver_name': order.driver.name if order.driver else None,
                'driver_phone': order.driver.phone if order.driver else None,
                'created_at': order.created_at.isoformat(),
                'completed_at': order.completed_at.isoformat() if order.completed_at else None
            })
        
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """Cancel order"""
    try:
        user_id = get_jwt_identity()
        db = SessionLocal()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order or order.customer_id != user_id:
            db.close()
            return jsonify({'error': 'Order not found'}), 404
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.ASSIGNED]:
            db.close()
            return jsonify({'error': 'Cannot cancel order in current status'}), 400
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.close()
        
        return jsonify({'message': 'Order cancelled'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# 👨‍✈️ DRIVER ENDPOINTS
# =====================================================

@app.route('/api/driver/update-location', methods=['POST'])
@jwt_required()
def update_location():
    """Update driver location"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        db = SessionLocal()
        
        location = db.query(DriverLocation).filter(DriverLocation.driver_id == user_id).first()
        
        if location:
            location.latitude = data.get('latitude')
            location.longitude = data.get('longitude')
            location.is_available = data.get('is_available', True)
            location.updated_at = datetime.utcnow()
        else:
            location = DriverLocation(
                driver_id=user_id,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                is_available=data.get('is_available', True)
            )
            db.add(location)
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Location updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver/available-orders', methods=['GET'])
@jwt_required()
def get_available_orders():
    """Get available orders for driver"""
    try:
        user_id = get_jwt_identity()
        db = SessionLocal()
        
        # Get pending and assigned orders
        orders = db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.ASSIGNED]),
            Order.driver_id == None
        ).all()
        
        result = []
        for order in orders:
            result.append({
                'id': order.id,
                'pickup': order.pickup_location,
                'destination': order.destination_location,
                'passengers': order.passengers_count,
                'estimated_price': order.estimated_price,
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'customer_comment': order.customer_comment,
                'created_at': order.created_at.isoformat()
            })
        
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver/accept-order/<order_id>', methods=['POST'])
@jwt_required()
def accept_order(order_id):
    """Accept order"""
    try:
        user_id = get_jwt_identity()
        db = SessionLocal()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order or order.status != OrderStatus.PENDING:
            db.close()
            return jsonify({'error': 'Order not available'}), 404
        
        order.driver_id = user_id
        order.status = OrderStatus.ACCEPTED
        order.assigned_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Order accepted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver/start-order/<order_id>', methods=['POST'])
@jwt_required()
def start_order(order_id):
    """Start delivery"""
    try:
        user_id = get_jwt_identity()
        db = SessionLocal()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order or order.driver_id != user_id:
            db.close()
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = OrderStatus.STARTED
        order.started_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Order started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver/complete-order/<order_id>', methods=['POST'])
@jwt_required()
def complete_order(order_id):
    """Complete delivery"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        db = SessionLocal()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order or order.driver_id != user_id:
            db.close()
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = OrderStatus.COMPLETED
        order.final_price = data.get('final_price', order.estimated_price)
        order.completed_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Order completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# 📞 DISPATCHER ENDPOINTS
# =====================================================

@app.route('/api/dispatcher/create-order-from-call', methods=['POST'])
@jwt_required()
def create_order_from_call():
    """Create order from phone call"""
    try:
        dispatcher_id = get_jwt_identity()
        data = request.json
        
        db = SessionLocal()
        
        # Create order
        order = Order(
            customer_phone=data.get('customer_phone'),
            customer_name=data.get('customer_name'),
            pickup_location=data.get('pickup_location', ''),
            destination_location=data.get('destination_location', ''),
            passengers_count=data.get('passengers_count', 1),
            customer_comment=data.get('notes', ''),
            dispatcher_id=dispatcher_id
        )
        
        db.add(order)
        db.flush()
        
        # Create call record
        call = DispatcherCall(
            dispatcher_id=dispatcher_id,
            order_id=order.id,
            customer_phone=data.get('customer_phone'),
            customer_name=data.get('customer_name'),
            customer_location=data.get('customer_location', ''),
            passenger_count=data.get('passengers_count', 1),
            call_notes=data.get('notes', '')
        )
        
        db.add(call)
        db.commit()
        
        result = {'message': 'Order created', 'order_id': order.id}
        db.close()
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dispatcher/pending-orders', methods=['GET'])
@jwt_required()
def get_pending_orders():
    """Get pending orders"""
    try:
        db = SessionLocal()
        
        orders = db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.ASSIGNED])
        ).all()
        
        result = []
        for order in orders:
            result.append({
                'id': order.id,
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'pickup': order.pickup_location,
                'destination': order.destination_location,
                'passengers': order.passengers_count,
                'status': order.status.value,
                'driver': order.driver.name if order.driver else None,
                'created_at': order.created_at.isoformat()
            })
        
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dispatcher/available-drivers', methods=['GET'])
@jwt_required()
def get_available_drivers():
    """Get available drivers"""
    try:
        db = SessionLocal()
        
        drivers = db.query(User).filter(
            User.role == UserRole.DRIVER,
            User.is_active == True
        ).all()
        
        result = []
        for driver in drivers:
            location = db.query(DriverLocation).filter(DriverLocation.driver_id == driver.id).first()
            active_orders = db.query(Order).filter(
                Order.driver_id == driver.id,
                Order.status.in_([OrderStatus.ACCEPTED, OrderStatus.STARTED])
            ).count()
            
            result.append({
                'id': driver.id,
                'name': driver.name,
                'phone': driver.phone,
                'is_available': location.is_available if location else False,
                'latitude': location.latitude if location else None,
                'longitude': location.longitude if location else None,
                'active_orders': active_orders
            })
        
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dispatcher/assign-driver/<order_id>/<driver_id>', methods=['POST'])
@jwt_required()
def assign_driver(order_id, driver_id):
    """Assign driver to order"""
    try:
        db = SessionLocal()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        driver = db.query(User).filter(User.id == driver_id).first()
        
        if not order or not driver:
            db.close()
            return jsonify({'error': 'Order or driver not found'}), 404
        
        order.driver_id = driver_id
        order.status = OrderStatus.ASSIGNED
        order.assigned_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Driver assigned'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# 🔐 ADMIN ENDPOINTS
# =====================================================

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Get dashboard statistics"""
    try:
        db = SessionLocal()
        
        total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        total_drivers = db.query(User).filter(User.role == UserRole.DRIVER).count()
        total_orders = db.query(Order).count()
        completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()
        
        db.close()
        
        return jsonify({
            'total_customers': total_customers,
            'total_drivers': total_drivers,
            'total_orders': total_orders,
            'completed_orders': completed_orders
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def admin_get_users():
    """Get all users"""
    try:
        db = SessionLocal()
        
        users = db.query(User).all()
        result = []
        
        for user in users:
            result.append({
                'id': user.id,
                'phone': user.phone,
                'name': user.name,
                'role': user.role.value,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            })
        
        db.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = not user.is_active
        db.commit()
        db.close()
        
        return jsonify({'message': f'User status changed to {user.is_active}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# ✅ HEALTH CHECK
# =====================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'timestamp': datetime.utcnow().isoformat()}), 200

# =====================================================
# 💾 INITIALIZATION FUNCTIONS
# =====================================================

def init_system():
    """Initialize system with test data"""
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).count() > 0:
        db.close()
        return
    
    try:
        # Create admin
        admin = User(
            phone="+998901234567",
            name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        # Create dispatchers
        dispatcher1 = User(
            phone="+998902345678",
            name="Dispatcher 1",
            role=UserRole.DISPATCHER,
            is_active=True
        )
        dispatcher2 = User(
            phone="+998903345678",
            name="Dispatcher 2",
            role=UserRole.DISPATCHER,
            is_active=True
        )
        db.add(dispatcher1)
        db.add(dispatcher2)
        
        # Create drivers
        drivers = []
        for i in range(5):
            driver = User(
                phone=f"+99890234567{i+1}",
                name=f"Driver {i+1}",
                role=UserRole.DRIVER,
                is_active=True
            )
            drivers.append(driver)
            db.add(driver)
        
        # Create customers
        customers = []
        for i in range(3):
            customer = User(
                phone=f"+99890334567{i+1}",
                name=f"Customer {i+1}",
                role=UserRole.CUSTOMER,
                is_active=True
            )
            customers.append(customer)
            db.add(customer)
        
        db.commit()
        
        # Create sample orders
        for i, customer in enumerate(customers):
            order = Order(
                customer_id=customer.id,
                customer_phone=customer.phone,
                customer_name=customer.name,
                pickup_location=f"Location {i+1}",
                destination_location=f"Destination {i+1}",
                passengers_count=1 + i,
                status=OrderStatus.PENDING
            )
            db.add(order)
        
        # Create driver locations
        for i, driver in enumerate(drivers):
            location = DriverLocation(
                driver_id=driver.id,
                latitude=41.2995 + (i * 0.01),
                longitude=69.2401 + (i * 0.01),
                is_available=True
            )
            db.add(location)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
    finally:
        db.close()

# =====================================================
# 🚀 MAIN EXECUTION
# =====================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Taxi Management System')
    parser.add_argument('--init', action='store_true', help='Initialize system')
    parser.add_argument('--start-web', action='store_true', help='Start web server')
    parser.add_argument('--port', type=int, default=Config.PORT, help='Port number')
    
    args = parser.parse_args()
    
    if args.init:
        init_system()
    elif args.start_web:
        app.run(host='0.0.0.0', port=args.port, debug=Config.DEBUG)
    else:
        # Default: start web server
        app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
