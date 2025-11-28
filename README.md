# 🚕 Professional Taxi Management System

A complete, production-ready taxi management system built with Flask, SQLAlchemy, and modern web technologies.

## ✨ Features

### 🚗 Driver Pro App (iOS-26 Design)
- Real-time order notifications
- Professional iOS-26 interface
- Live GPS map integration (Leaflet.js)
- **Real-time meter calculation** (3000 som/km, 15 km/h)
- Pause button to stop meter
- Money split: 20% admin, 80% driver
- Beautiful animations and gradients

### 👥 Admin Panel
- Driver registration and management
- Financial dashboard with statistics
- Money tracking (revenue, commissions)
- Driver performance analytics
- Orders analysis

### 👤 Customer App
- Easy order booking
- Real-time order tracking
- Order history
- Price estimates

### 📡 Backend API
- 20+ REST endpoints
- JWT authentication
- Phone-based login
- SQLAlchemy ORM
- SQLite / PostgreSQL support

## 🚀 Quick Start

### 1. Initialize System
```bash
python taxi_system.py --init
```

### 2. Start Web Server
```bash
python taxi_system.py --start-web
```

### 3. Open in Browser
```
http://localhost:5000/index.html
```

## 🔐 Test Accounts

| Role | Phone | App |
|------|-------|-----|
| Admin | +998901234567 | admin_login.html |
| Driver | +998902345671 | driver_login.html |
| Customer | +998903345671 | customer.html |

## 📁 Project Structure

```
d:\python\
├── taxi_system.py                  (Backend - 1400+ lines)
├── driver_pro.html                 (Driver App - 600+ lines)
├── admin_login.html                (Admin Login)
├── admin_panel_driver_registration.html (Driver Management)
├── admin_dashboard_money.html      (Financial Dashboard)
├── driver_login.html               (Driver Login)
├── customer.html                   (Customer App)
├── index.html                      (Landing Page)
├── COMPLETE_GUIDE.md               (Comprehensive Guide)
├── requirements.txt                (Python Dependencies)
├── .env.example                    (Environment Template)
├── start.bat / start.sh            (Startup Scripts)
└── venv/                           (Python Virtual Environment)
```

## 💻 Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLAlchemy 2.0.31 + SQLite/PostgreSQL
- **Authentication**: JWT (Flask-JWT-Extended)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Maps**: Leaflet.js
- **Python**: 3.13+

## 💰 Real-Time Meter Algorithm

```
Distance = (elapsed_seconds × 15 km/h) / 3600
Total Price = Distance × 3000 som/km
Admin Commission = Total Price × 0.20
Driver Earnings = Total Price × 0.80
Updates every 1 second
```

## 📚 Documentation

- `COMPLETE_GUIDE.md` - Comprehensive guide with all features
- `README_UZ.md` - Uzbek language documentation
- See `COMPLETE_GUIDE.md` for API endpoints, database schema, and more

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with phone

### Driver
- `GET /api/driver/available-orders` - Get available orders
- `POST /api/driver/accept-order/<id>` - Accept order
- `POST /api/driver/complete-order/<id>` - Complete order

### Customer
- `POST /api/orders` - Create order
- `GET /api/orders` - Get orders
- `POST /api/orders/<id>/cancel` - Cancel order

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `GET /api/admin/users` - All users

## 🎨 Design System

- **Color Palette**: Purple (#667eea→#764ba2), Pink (#f093fb→#f5576c)
- **Animations**: Smooth 0.3s transitions with keyframe effects
- **Typography**: Apple system fonts
- **Responsive**: Mobile-first design (works on all devices)

## 📦 Installation

```bash
# Clone or download
cd d:\python

# Install dependencies
pip install -r requirements.txt

# Initialize database
python taxi_system.py --init

# Start server
python taxi_system.py --start-web
```

## 🌐 Deployment

The system is ready for production deployment on:
- Heroku
- Railway.app
- DigitalOcean
- AWS
- Google Cloud
- Azure

See `COMPLETE_GUIDE.md` for deployment instructions.

## 👨‍💻 Development

To understand the codebase:
1. Read `COMPLETE_GUIDE.md` for comprehensive documentation
2. See `taxi_system.py` for backend implementation
3. See `driver_pro.html` for the main driver app
4. See `admin_dashboard_money.html` for financial dashboard

## 📄 License

MIT License - feel free to use and modify

## 🔗 Links

- **GitHub**: https://github.com/asliddinx278-ops/taxi
- **Guide**: See `COMPLETE_GUIDE.md`
- **Contact**: asliddinx278-ops@github.com

---

**Status**: ✅ Production Ready | **Version**: 1.0 | **Updated**: 2025-11-28
