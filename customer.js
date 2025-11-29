/* ================================
   CUSTOMER APP - CUSTOMER.JS
   ================================ */

class CustomerApp extends TaxiApp {
    constructor() {
        super();
        this.savedLocations = [];
        this.favoriteDrivers = [];
        this.activeOrder = null;
        this.orderHistory = [];
        this.initCustomer();
    }

    initCustomer() {
        console.log('👤 Customer App Initialized');
        this.loadCustomerData();
        this.attachCustomerListeners();
    }

    // ================================
    // LOCATION MANAGEMENT
    // ================================

    addSavedLocation(name, address, latitude, longitude) {
        const location = {
            id: this.generateId(),
            name: name,
            address: address,
            latitude: latitude,
            longitude: longitude,
            type: 'saved'
        };

        this.savedLocations.push(location);
        this.setData('savedLocations', this.savedLocations);
        this.showNotification(`✅ "${name}" saqlandi`, 'success');
        return location;
    }

    getSavedLocations() {
        return this.savedLocations;
    }

    removeSavedLocation(locationId) {
        this.savedLocations = this.savedLocations.filter(l => l.id !== locationId);
        this.setData('savedLocations', this.savedLocations);
        this.showNotification('✅ Joylashuv o\'chirildi', 'success');
    }

    // ================================
    // ORDER BOOKING
    // ================================

    bookRide(pickupLocation, dropoffLocation, rideType = 'standard') {
        const order = {
            id: 'ORD-' + Date.now(),
            customerId: this.user.id,
            passengerName: this.user.name,
            passengerPhone: this.user.phone,
            from: pickupLocation.address,
            fromLatitude: pickupLocation.latitude,
            fromLongitude: pickupLocation.longitude,
            to: dropoffLocation.address,
            toLatitude: dropoffLocation.latitude,
            toLongitude: dropoffLocation.longitude,
            rideType: rideType,
            fare: this.calculateFare(rideType),
            status: 'searching',
            createdAt: new Date().toISOString()
        };

        this.activeOrder = order;
        this.orders.push(order);
        this.saveOrders(this.orders);
        
        this.showNotification('🔍 Haydovchini qidiryapman...', 'info');
        this.simulateDriverSearch(order);
        
        return order;
    }

    calculateFare(rideType) {
        const baseFare = 50000; // UZS
        const multipliers = {
            'standard': 1,
            'premium': 1.5,
            'shared': 0.7
        };

        const randomDistance = Math.random() * 10 + 5; // 5-15 km
        const baseCost = baseFare * (multipliers[rideType] || 1);
        return Math.round(baseCost + (randomDistance * 5000));
    }

    simulateDriverSearch(order) {
        // Simulate finding a driver after 3-8 seconds
        const searchTime = Math.random() * 5000 + 3000;
        
        setTimeout(() => {
            if (this.activeOrder && this.activeOrder.id === order.id) {
                order.status = 'assigned';
                order.driverId = this.generateId();
                order.driverName = '🚗 Haydovchi Ism';
                order.driverRating = 4.8;
                order.vehicleModel = 'Toyota Camry';
                order.vehiclePlate = 'AA 777 AA';
                order.assignedAt = new Date().toISOString();
                
                this.saveOrders(this.orders);
                this.showNotification('✅ Haydovchi topildi!', 'success');
                this.playNotificationSound();
            }
        }, searchTime);
    }

    cancelOrder(orderId) {
        const order = this.updateOrder(orderId, {
            status: 'cancelled',
            cancelledAt: new Date().toISOString()
        });

        if (order) {
            this.activeOrder = null;
            this.showNotification('❌ Buyurtma bekor qilindi', 'warning');
        }

        return order;
    }

    // ================================
    // RIDE TRACKING
    // ================================

    trackRide(orderId) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) return null;

        return {
            orderId: order.id,
            status: order.status,
            driverName: order.driverName,
            driverRating: order.driverRating,
            vehicleModel: order.vehicleModel,
            vehiclePlate: order.vehiclePlate,
            estimatedTime: this.estimateTime(order),
            distance: this.estimateDistance(order),
            fare: order.fare
        };
    }

    estimateTime(order) {
        // Rough estimate: 3 minutes per km
        const distance = this.estimateDistance(order);
        return Math.round(distance * 3);
    }

    estimateDistance(order) {
        // Rough calculation
        if (order.fromLatitude && order.toLatitude) {
            const R = 6371; // Earth's radius in km
            const dLat = (order.toLatitude - order.fromLatitude) * Math.PI / 180;
            const dLon = (order.toLongitude - order.fromLongitude) * Math.PI / 180;
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(order.fromLatitude * Math.PI / 180) * Math.cos(order.toLatitude * Math.PI / 180) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return (R * c).toFixed(1);
        }
        return 5; // Default
    }

    // ================================
    // RATING & FEEDBACK
    // ================================

    rateRide(orderId, rating, comment) {
        const order = this.updateOrder(orderId, {
            customerRating: rating,
            customerComment: comment,
            ratedAt: new Date().toISOString()
        });

        if (order) {
            this.orderHistory.push(order);
            this.showNotification(`✅ ${rating} ⭐ baholadi`, 'success');
        }

        return order;
    }

    reportIssue(orderId, issueType, description) {
        const report = {
            id: this.generateId(),
            orderId: orderId,
            type: issueType,
            description: description,
            reportedAt: new Date().toISOString(),
            status: 'pending'
        };

        const reports = this.getData('issues') || [];
        reports.push(report);
        this.setData('issues', reports);
        
        this.showNotification('✅ Muammo hisobotlandi', 'success');
        return report;
    }

    // ================================
    // FAVORITE DRIVERS
    // ================================

    addFavoriteDriver(driverId) {
        if (!this.favoriteDrivers.includes(driverId)) {
            this.favoriteDrivers.push(driverId);
            this.setData('favoriteDrivers', this.favoriteDrivers);
            this.showNotification('⭐ Sevimli haydovchiga qo\'shildi', 'success');
        }
    }

    removeFavoriteDriver(driverId) {
        this.favoriteDrivers = this.favoriteDrivers.filter(d => d !== driverId);
        this.setData('favoriteDrivers', this.favoriteDrivers);
        this.showNotification('⭐ Sevimli haydovchidan olib tashlandi', 'info');
    }

    getFavoriteDrivers() {
        return this.favoriteDrivers;
    }

    // ================================
    // RIDE HISTORY
    // ================================

    getOrderHistory() {
        return this.orders.filter(o => o.status === 'completed' || o.status === 'cancelled');
    }

    getCompletedRides() {
        return this.orders.filter(o => o.status === 'completed');
    }

    getStats() {
        const completed = this.getCompletedRides();
        const totalRides = completed.length;
        const totalSpent = completed.reduce((sum, o) => sum + (o.fare || 0), 0);
        const avgRating = totalRides > 0 
            ? (completed.reduce((sum, o) => sum + (o.driverRating || 0), 0) / totalRides).toFixed(1)
            : 0;

        return {
            totalRides: totalRides,
            totalSpent: totalSpent,
            avgDriverRating: avgRating,
            favoriteDrivers: this.favoriteDrivers.length
        };
    }

    // ================================
    // PAYMENT & WALLET
    // ================================

    addToWallet(amount) {
        const wallet = this.getData('wallet') || { balance: 0 };
        wallet.balance += amount;
        this.setData('wallet', wallet);
        this.showNotification(`✅ ${app.formatCurrency(amount)} o\'tkazildi`, 'success');
        return wallet;
    }

    getWalletBalance() {
        const wallet = this.getData('wallet') || { balance: 0 };
        return wallet.balance;
    }

    useWalletBalance(amount) {
        const wallet = this.getData('wallet') || { balance: 0 };
        if (wallet.balance >= amount) {
            wallet.balance -= amount;
            this.setData('wallet', wallet);
            return true;
        }
        this.showNotification('❌ Yetarli mablag\' yo\'q', 'danger');
        return false;
    }

    // ================================
    // PROMO CODES
    // ================================

    applyPromoCode(code) {
        const promoCodes = {
            'WELCOME': 50000,  // 50,000 UZS discount
            'FRIEND': 75000,   // 75,000 UZS discount
            'SUMMER': 100000   // 100,000 UZS discount
        };

        if (promoCodes[code]) {
            const discount = promoCodes[code];
            this.addToWallet(discount);
            this.showNotification(`🎉 ${app.formatCurrency(discount)} skidka qo\'shildi!`, 'success');
            return discount;
        }

        this.showNotification('❌ Noto\'g\'ri promo kod', 'danger');
        return 0;
    }

    // ================================
    // SUPPORT
    // ================================

    contactSupport(subject, message) {
        const support = {
            id: this.generateId(),
            customerId: this.user.id,
            subject: subject,
            message: message,
            sentAt: new Date().toISOString(),
            status: 'pending'
        };

        const supports = this.getData('support') || [];
        supports.push(support);
        this.setData('support', supports);
        
        this.showNotification('✅ Xabar yuborildi', 'success');
        return support;
    }

    // ================================
    // NOTIFICATIONS & SOUNDS
    // ================================

    playNotificationSound() {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 1000;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }

    // ================================
    // EVENT LISTENERS
    // ================================

    attachCustomerListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('book-ride-btn')) {
                const pickup = { address: 'Toshkent', latitude: 41.2995, longitude: 69.2401 };
                const dropoff = { address: 'Chust', latitude: 41.1, longitude: 69.5 };
                this.bookRide(pickup, dropoff, 'standard');
            }

            if (e.target.classList.contains('cancel-order-btn')) {
                const orderId = e.target.dataset.orderId;
                this.cancelOrder(orderId);
            }

            if (e.target.classList.contains('rate-ride-btn')) {
                const orderId = e.target.dataset.orderId;
                const rating = prompt('Haydovchini baholang (1-5):', '5');
                if (rating) {
                    this.rateRide(orderId, parseInt(rating), 'Yaxshi xizmat');
                }
            }
        });
    }

    loadCustomerData() {
        this.savedLocations = this.getData('savedLocations') || [];
        this.favoriteDrivers = this.getData('favoriteDrivers') || [];
        this.orderHistory = this.getOrderHistory();
    }

    // ================================
    // UI RENDERING
    // ================================

    renderOrderHistory() {
        const container = document.getElementById('customer-history');
        if (!container) return;

        const history = this.getOrderHistory();
        container.innerHTML = history.map(order => `
            <div class="card mt-2">
                <div class="card-header">
                    <div>
                        <div class="card-title">${order.from} → ${order.to}</div>
                        <div class="card-subtitle">${app.formatDateTime(order.createdAt)}</div>
                    </div>
                    <span class="badge badge-${order.status === 'completed' ? 'success' : 'warning'}">
                        ${order.status}
                    </span>
                </div>
                <div class="p-2">
                    <p><strong>Narx:</strong> ${app.formatCurrency(order.fare || 50000)}</p>
                    <p><strong>Haydovchi:</strong> ${order.driverName || 'Noma\'lum'}</p>
                    ${order.customerRating ? `<p><strong>Baholash:</strong> ${order.customerRating} ⭐</p>` : ''}
                </div>
            </div>
        `).join('');

        if (history.length === 0) {
            container.innerHTML = '<p class="text-center text-gray mt-4">Chiptalar yo\'q</p>';
        }
    }

    renderStats() {
        const stats = this.getStats();
        const container = document.getElementById('customer-stats');
        if (!container) return;

        container.innerHTML = `
            <div class="grid grid-2">
                <div class="card text-center">
                    <div style="font-size: 24px;">🚗</div>
                    <div style="font-size: 28px; font-weight: bold; color: var(--primary);" class="mt-2">
                        ${stats.totalRides}
                    </div>
                    <div class="text-gray mt-1">Umumiy sayohatlar</div>
                </div>
                <div class="card text-center">
                    <div style="font-size: 24px;">💰</div>
                    <div style="font-size: 28px; font-weight: bold; color: var(--success);" class="mt-2">
                        ${app.formatCurrency(stats.totalSpent)}
                    </div>
                    <div class="text-gray mt-1">Umumiy xarajat</div>
                </div>
            </div>
        `;
    }
}

// Initialize global customer app instance
const customerApp = new CustomerApp();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CustomerApp;
}
