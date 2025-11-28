# =====================================================
# 🚕 PROFESSIONAL TAXI MANAGEMENT SYSTEM
# Database Models & Core Backend
# =====================================================

import os
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

# Database
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

# Other
from dotenv import load_dotenv

# =====================================================
# 📋 CONFIGURATION MANAGEMENT
# =====================================================

load_dotenv()

class Config:
    """Configuration settings"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///taxi_system.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2025')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'http://localhost:5000')

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
# 🚀 UTILITY FUNCTIONS
# =====================================================

def create_test_data():
    """Create test data for development"""
    init_system()

if __name__ == '__main__':
    init_system()
