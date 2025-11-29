/* ================================
   PREMIUM TAXI SYSTEM - CORE APP.JS
   ================================ */

class TaxiApp {
    constructor() {
        this.isOnline = false;
        this.currentOrder = null;
        this.user = null;
        this.orders = [];
        this.init();
    }

    init() {
        console.log('🚕 Taxi App Initialized');
        this.loadUser();
        this.attachEventListeners();
        this.startPeriodicUpdates();
    }

    // ================================
    // USER MANAGEMENT
    // ================================

    loadUser() {
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            this.user = JSON.parse(savedUser);
        }
    }

    saveUser(user) {
        this.user = user;
        localStorage.setItem('user', JSON.stringify(user));
    }

    login(phone, password) {
        return new Promise((resolve, reject) => {
            // Simulate API call
            setTimeout(() => {
                const user = {
                    id: Math.random().toString(36).substr(2, 9),
                    phone: phone,
                    name: 'Test User',
                    role: 'driver',
                    avatar: '👨‍💼'
                };
                this.saveUser(user);
                this.showNotification('✅ Muvaffaqiyatli kirdi!', 'success');
                resolve(user);
            }, 1000);
        });
    }

    logout() {
        this.user = null;
        localStorage.removeItem('user');
        this.showNotification('🚪 Chiqdiing', 'info');
    }

    // ================================
    // ORDERS MANAGEMENT
    // ================================

    getOrders() {
        const savedOrders = localStorage.getItem('orders');
        return savedOrders ? JSON.parse(savedOrders) : [];
    }

    saveOrders(orders) {
        this.orders = orders;
        localStorage.setItem('orders', JSON.stringify(orders));
    }

    createOrder(data) {
        const order = {
            id: 'ORD-' + Date.now(),
            ...data,
            status: 'pending',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        this.orders.push(order);
        this.saveOrders(this.orders);
        return order;
    }

    updateOrder(orderId, updates) {
        const order = this.orders.find(o => o.id === orderId);
        if (order) {
            Object.assign(order, updates);
            order.updatedAt = new Date().toISOString();
            this.saveOrders(this.orders);
            return order;
        }
        return null;
    }

    deleteOrder(orderId) {
        this.orders = this.orders.filter(o => o.id !== orderId);
        this.saveOrders(this.orders);
    }

    // ================================
    // NOTIFICATIONS (PREMIUM)
    // ================================

    showNotification(message, type = 'info', duration = 3000) {
        const container = document.getElementById('notifications') || this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="close-btn" onclick="this.parentElement.remove()">✕</button>
        `;
        
        container.appendChild(notification);
        
        if (duration > 0) {
            setTimeout(() => notification.remove(), duration);
        }

        return notification;
    }

    createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notifications';
        container.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    // ================================
    // VALIDATION (PREMIUM)
    // ================================

    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    validatePhone(phone) {
        const regex = /^(\+998|0)?[0-9]{9,12}$/;
        return regex.test(phone);
    }

    validateForm(formData, rules) {
        const errors = {};

        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];

            if (rule.required && (!value || value.trim() === '')) {
                errors[field] = `${field} majburiy`;
            }

            if (rule.minLength && value && value.length < rule.minLength) {
                errors[field] = `${field} kamida ${rule.minLength} belgisdan ko'p bo'lishi kerak`;
            }

            if (rule.maxLength && value && value.length > rule.maxLength) {
                errors[field] = `${field} ${rule.maxLength} belgisdan ko'p bo'lishi kerak`;
            }

            if (rule.type === 'email' && value && !this.validateEmail(value)) {
                errors[field] = `${field} noto'g'ri`;
            }

            if (rule.type === 'phone' && value && !this.validatePhone(value)) {
                errors[field] = `${field} noto'g'ri`;
            }
        }

        return errors;
    }

    // ================================
    // FORMATTING (PREMIUM)
    // ================================

    formatCurrency(amount) {
        return new Intl.NumberFormat('uz-UZ', {
            style: 'currency',
            currency: 'UZS'
        }).format(amount);
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('uz-UZ', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    formatTime(date) {
        return new Date(date).toLocaleTimeString('uz-UZ', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatDateTime(date) {
        return `${this.formatDate(date)} ${this.formatTime(date)}`;
    }

    // ================================
    // STORAGE (PREMIUM)
    // ================================

    setData(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    getData(key) {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    }

    removeData(key) {
        localStorage.removeItem(key);
    }

    clearAllData() {
        localStorage.clear();
    }

    // ================================
    // EVENTS
    // ================================

    attachEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM Loaded');
        });
    }

    // ================================
    // PERIODIC UPDATES
    // ================================

    startPeriodicUpdates() {
        // Update every 5 seconds
        setInterval(() => {
            this.updateLocation();
            this.checkOrderUpdates();
        }, 5000);
    }

    updateLocation() {
        if (this.isOnline && navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                const { latitude, longitude } = position.coords;
                this.user.location = { latitude, longitude };
                this.saveUser(this.user);
            });
        }
    }

    checkOrderUpdates() {
        // Simulate checking for new orders
        // In production, this would be an API call
    }

    // ================================
    // UTILITIES (PREMIUM)
    // ================================

    generateId() {
        return 'ID-' + Math.random().toString(36).substr(2, 9).toUpperCase();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async fetchJSON(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    debounce(func, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func(...args), delay);
        };
    }

    throttle(func, delay) {
        let lastCall = 0;
        return (...args) => {
            const now = Date.now();
            if (now - lastCall >= delay) {
                lastCall = now;
                func(...args);
            }
        };
    }
}

// Initialize global app instance
const app = new TaxiApp();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaxiApp;
}
