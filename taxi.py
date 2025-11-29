# =====================================================
# 🚕 PROFESSIONAL TAXI MANAGEMENT SYSTEM
# Telegram Bot + Database + Web Apps
# =====================================================

import os
import logging
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

# Database
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Other
from dotenv import load_dotenv

# =====================================================
# 📋 LOGGING & CONFIGURATION
# =====================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    """Configuration settings"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///taxi_system.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'aB3#xY9@kL2$mN5&pQ7*rT4!vW6^zX8(')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7589919425:AAG9bMalFe7ZZi434bUrdKLy_gTEvtJFCxI')
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://asliddinx278-ops.github.io/taxi/')
    
    # Web App URLs
    ADMIN_APP_URL = f"{WEB_APP_URL}admin_login.html"
    CUSTOMER_APP_URL = f"{WEB_APP_URL}customer.html"
    DRIVER_APP_URL = f"{WEB_APP_URL}driver_pro.html"
    DISPATCHER_APP_URL = f"{WEB_APP_URL}admin_panel_driver_registration.html"

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
    telegram_id = Column(String, nullable=True, unique=True)
    telegram_username = Column(String, nullable=True)
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
    order_type = Column(String, default="standard")
    
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
    
    call_status = Column(String, default="received")
    received_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    dispatcher = relationship("User", back_populates="dispatcher_calls")

# =====================================================
# 🔌 DATABASE INITIALIZATION
# =====================================================

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

def get_user_by_telegram(telegram_id: str):
    """Get user by Telegram ID"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    db.close()
    return user

def create_or_update_user(telegram_id: str, telegram_username: str, role: UserRole = UserRole.CUSTOMER):
    """Create or update user from Telegram"""
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    
    if user:
        user.telegram_username = telegram_username
        user.updated_at = datetime.utcnow()
    else:
        user = User(
            phone=f"tg_{telegram_id}",
            name=telegram_username or f"User_{telegram_id}",
            telegram_id=str(telegram_id),
            telegram_username=telegram_username,
            role=role,
            is_active=True
        )
        db.add(user)
    
    db.commit()
    db.close()
    return user

# =====================================================
# 🤖 TELEGRAM BOT HANDLERS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - Show role selection"""
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username or update.effective_user.first_name
    
    # Get or create user
    user = get_user_by_telegram(telegram_id)
    
    if user:
        await show_role_menu(update, context, user)
    else:
        # Show welcome message and role selection
        keyboard = [
            [
                InlineKeyboardButton("👤 Mijoz", callback_data="role_customer"),
                InlineKeyboardButton("🚗 Haydovchi", callback_data="role_driver"),
            ],
            [
                InlineKeyboardButton("📞 Dispatcher", callback_data="role_dispatcher"),
                InlineKeyboardButton("🔑 Admin", callback_data="role_admin"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🎉 *Xush Kelibsiz Taxi Sistemasiga!*

Iltimos, siz kim ekanligingizni tanlang:

👤 *Mijoz* - Taksi buyurtma qilish
🚗 *Haydovchi* - Taksi bilan pulga raqib
📞 *Dispatcher* - Taksi qo'ng'iroqlarni boshqarish
🔑 *Admin* - Tizimni boshqarish
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def show_role_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
    """Show menu based on user role"""
    keyboard = []
    
    if user.role == UserRole.ADMIN:
        keyboard = [
            [InlineKeyboardButton("📊 Admin Panel", url=Config.ADMIN_APP_URL)],
            [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton("💰 Moliya", callback_data="admin_money")],
            [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="admin_settings")],
        ]
        title = "🔑 Admin Panel"
        message = "Admin paneliga xush kelibsiz!"
        
    elif user.role == UserRole.DRIVER:
        keyboard = [
            [InlineKeyboardButton("🚗 Haydovchi Applikatsiyasi", url=Config.DRIVER_APP_URL)],
            [InlineKeyboardButton("💰 Daromadim", callback_data="driver_earnings")],
            [InlineKeyboardButton("⭐ Reyting", callback_data="driver_rating")],
            [InlineKeyboardButton("🆘 Yordam", callback_data="driver_support")],
        ]
        title = "🚗 Haydovchi Applikatsiyasi"
        message = "Haydovchi applikatsiyasiga xush kelibsiz!"
        
    elif user.role == UserRole.DISPATCHER:
        keyboard = [
            [InlineKeyboardButton("📞 Dispatcher Panel", url=Config.DISPATCHER_APP_URL)],
            [InlineKeyboardButton("📋 Buyurtmalar", callback_data="dispatcher_orders")],
            [InlineKeyboardButton("👥 Haydovchilar", callback_data="dispatcher_drivers")],
            [InlineKeyboardButton("🆘 Yordam", callback_data="dispatcher_support")],
        ]
        title = "📞 Dispatcher Panel"
        message = "Dispatcher paneliga xush kelibsiz!"
        
    else:  # CUSTOMER
        keyboard = [
            [InlineKeyboardButton("👤 Mijoz Applikatsiyasi", url=Config.CUSTOMER_APP_URL)],
            [InlineKeyboardButton("🚕 Taksi Buyurtma Qilish", callback_data="customer_order")],
            [InlineKeyboardButton("📋 Tarixim", callback_data="customer_history")],
            [InlineKeyboardButton("🆘 Yordam", callback_data="customer_support")],
        ]
        title = "👤 Mijoz Applikatsiyasi"
        message = "Mijoz applikatsiyasiga xush kelibsiz!"
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = f"""
{title}

{message}

*Sizning roli:* {user.role.value.upper()}
*Telefon:* {user.phone}
*Yaratilgan:* {user.created_at.strftime('%Y-%m-%d %H:%M')}
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = update.effective_user.id
    telegram_username = update.effective_user.username or update.effective_user.first_name
    
    # Handle role selection
    if query.data.startswith("role_"):
        role_map = {
            "role_customer": UserRole.CUSTOMER,
            "role_driver": UserRole.DRIVER,
            "role_dispatcher": UserRole.DISPATCHER,
            "role_admin": UserRole.ADMIN,
        }
        
        selected_role = role_map[query.data]
        user = create_or_update_user(telegram_id, telegram_username, selected_role)
        
        await show_role_menu(update, context, user)
    
    # Handle other callbacks
    elif query.data == "customer_order":
        text = "🚕 *Taksi Buyurtma Qilish*\n\nTaksi buyurtmasini qilish uchun mijoz applikatsiyasini oching:"
        keyboard = [[InlineKeyboardButton("👤 Mijoz Applikatsiyasi", url=Config.CUSTOMER_APP_URL)]]
        
    elif query.data == "driver_earnings":
        text = "💰 *Mening Daromadim*\n\nSizning daromadingizni ko'rish uchun haydovchi applikatsiyasini oching:"
        keyboard = [[InlineKeyboardButton("🚗 Haydovchi Applikatsiyasi", url=Config.DRIVER_APP_URL)]]
        
    elif query.data == "admin_users":
        text = "👥 *Foydalanuvchilar*\n\nFoydalanuvchilarni boshqarish uchun admin panelini oching:"
        keyboard = [[InlineKeyboardButton("🔑 Admin Panel", url=Config.ADMIN_APP_URL)]]
        
    elif query.data == "dispatcher_orders":
        text = "📋 *Buyurtmalar*\n\nBuyurtmalarni boshqarish uchun dispatcher panelini oching:"
        keyboard = [[InlineKeyboardButton("📞 Dispatcher Panel", url=Config.DISPATCHER_APP_URL)]]
        
    elif query.data in ["customer_history", "customer_support", "driver_rating", "driver_support", 
                        "dispatcher_drivers", "dispatcher_support", "admin_money", "admin_settings"]:
        text = "📱 *Applikatsiyani Oching*\n\nBu funksiyani ishlatish uchun applikatsiyani oching:"
        keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data="back_to_menu")]]
    
    else:
        text = "❌ Noma'lum buyruq"
        keyboard = [[InlineKeyboardButton("◀️ Orqaga", callback_data="back_to_menu")]]
    
    if query.data == "back_to_menu":
        user = get_user_by_telegram(telegram_id)
        if user:
            await show_role_menu(update, context, user)
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
🆘 *Yordam va Buyruqlar*

*Asosiy Buyruqlar:*
/start - Boshlanish
/help - Yordam
/profile - Mening Profilim
/role - Roli o'zgartirish

*Mijoz Buyruqlari:*
/order - Taksi Buyurtma Qilish
/history - Tarixim
/support - Yordam So'rash

*Haydovchi Buyruqlari:*
/online - Online Bo'lish
/offline - Offline Bo'lish
/earnings - Daromadim
/rating - Reyting

*Admin Buyruqlari:*
/dashboard - Dashboard
/users - Foydalanuvchilar
/settings - Sozlamalar

*Dispatcher Buyruqlari:*
/calls - Qo'ng'iroqlar
/drivers - Haydovchilar
/orders - Buyurtmalar
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /profile command"""
    telegram_id = update.effective_user.id
    user = get_user_by_telegram(telegram_id)
    
    if not user:
        await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'isini yuboring.")
        return
    
    profile_text = f"""
👤 *Mening Profilim*

*Ism:* {user.name}
*Telefon:* {user.phone}
*Roli:* {user.role.value.upper()}
*Status:* {'✅ Faol' if user.is_active else '❌ Nofaol'}
*Yaratilgan:* {user.created_at.strftime('%Y-%m-%d %H:%M')}

*Telegram:* @{user.telegram_username if user.telegram_username else 'Noma\'lum'}
    """
    
    keyboard = [[InlineKeyboardButton("🔄 Roli O'zgartirish", callback_data="role_customer")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages"""
    message_text = update.message.text.lower()
    
    if message_text in ["salom", "hi", "hello", "assalom"]:
        await start(update, context)
    else:
        await update.message.reply_text("🤔 Men bu buyruqni tushunmasdim. /help buyrug'isini yuboring.")

# =====================================================
# 💾 DATABASE INITIALIZATION
# =====================================================

def init_system():
    """Initialize system with test data"""
    db = SessionLocal()
    
    if db.query(User).count() > 0:
        db.close()
        return
    
    try:
        # Create admins
        admin1 = User(
            phone="+998901234567",
            name="Admin Panel 1",
            role=UserRole.ADMIN,
            telegram_id="admin_panel_1",
            is_active=True
        )
        admin2 = User(
            phone="+998901234568",
            name="Admin Panel 2",
            role=UserRole.ADMIN,
            telegram_id="admin_panel_2",
            is_active=True
        )
        db.add(admin1)
        db.add(admin2)
        
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
        for i in range(5):
            driver = User(
                phone=f"+99890234567{i+1}",
                name=f"Driver {i+1}",
                role=UserRole.DRIVER,
                is_active=True
            )
            db.add(driver)
        
        # Create customers
        for i in range(3):
            customer = User(
                phone=f"+99890334567{i+1}",
                name=f"Customer {i+1}",
                role=UserRole.CUSTOMER,
                is_active=True
            )
            db.add(customer)
        
        db.commit()
        logger.info("✅ System initialized with test data")
        
    except Exception as e:
        logger.error(f"❌ Error initializing system: {e}")
        db.rollback()
    finally:
        db.close()

# =====================================================
# 🚀 BOT STARTUP
# =====================================================

async def main():
    """Start the bot"""
    # Initialize database
    init_system()
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("role", start))  # Alias for /start
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Regex(r"^(salom|hi|hello|assalom)$"), start))
    
    # Callback handler for buttons
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("🤖 Telegram Bot started!")
    logger.info(f"📱 Admin App: {Config.ADMIN_APP_URL}")
    logger.info(f"👤 Customer App: {Config.CUSTOMER_APP_URL}")
    logger.info(f"🚗 Driver App: {Config.DRIVER_APP_URL}")
    logger.info(f"📞 Dispatcher App: {Config.DISPATCHER_APP_URL}")
    
    # Start bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
