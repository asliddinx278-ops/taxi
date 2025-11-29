/* ================================
   DRIVER PRO APP - DRIVER.JS
   ================================ */

class DriverApp extends TaxiApp {
    constructor() {
        super();
        this.vehicle = null;
        this.currentLocation = null;
        this.ratings = 0;
        this.earnings = 0;
        this.acceptedOrders = [];
        this.initDriver();
    }

    initDriver() {
        console.log('🚗 Driver App Initialized');
        this.loadVehicleInfo();
        this.attachDriverListeners();
    }

    // ================================
    // DRIVER STATUS
    // ================================

    toggleOnline(status) {
        this.isOnline = status;
        if (status) {
            this.startLocationTracking();
            this.showNotification('🟢 Online holatiga o\'ttingiz', 'success');
        } else {
            this.stopLocationTracking();
            this.showNotification('🔴 Offline holatiga o\'ttingiz', 'warning');
        }
        this.saveUser(this.user);
    }

    // ================================
    // VEHICLE MANAGEMENT
    // ================================

    loadVehicleInfo() {
        this.vehicle = {
            model: 'Toyota Camry',
            color: 'Oq',
            plate: 'AA 777 AA',
            year: 2022,
            capacity: 4,
            status: 'active'
        };
    }

    updateVehicleInfo(vehicleData) {
        this.vehicle = { ...this.vehicle, ...vehicleData };
        this.setData('vehicle', this.vehicle);
        this.showNotification('✅ Mashina ma\'lumotlari yangilandi', 'success');
    }

    // ================================
    // LOCATION TRACKING
    // ================================

    startLocationTracking() {
        if (navigator.geolocation) {
            this.locationWatchId = navigator.geolocation.watchPosition(
                position => {
                    const { latitude, longitude, accuracy } = position.coords;
                    this.currentLocation = { latitude, longitude, accuracy };
                    this.updateLocationUI();
                    // Send to server in production
                },
                error => {
                    console.error('Location error:', error);
                    this.showNotification('❌ Lokatsiyani aniqlab bo\'lmadi', 'danger');
                },
                {
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: 5000
                }
            );
        }
    }

    stopLocationTracking() {
        if (this.locationWatchId) {
            navigator.geolocation.clearWatch(this.locationWatchId);
        }
    }

    getCurrentLocation() {
        return this.currentLocation;
    }

    updateLocationUI() {
        const locationElement = document.getElementById('driver-location');
        if (locationElement && this.currentLocation) {
            locationElement.textContent = `📍 ${this.currentLocation.latitude.toFixed(4)}, ${this.currentLocation.longitude.toFixed(4)}`;
        }
    }

    // ================================
    // ORDER MANAGEMENT
    // ================================

    getAvailableOrders() {
        return this.orders.filter(o => o.status === 'pending');
    }

    acceptOrder(orderId) {
        const order = this.updateOrder(orderId, {
            status: 'accepted',
            driverId: this.user.id,
            driverName: this.user.name,
            acceptedAt: new Date().toISOString()
        });

        if (order) {
            this.acceptedOrders.push(order);
            this.showNotification('✅ Buyurtmani qabul qildingiz!', 'success');
            this.playNotificationSound();
        }

        return order;
    }

    rejectOrder(orderId) {
        this.showNotification('❌ Buyurtmani rad qildingiz', 'warning');
    }

    startTrip(orderId) {
        return this.updateOrder(orderId, {
            status: 'started',
            startedAt: new Date().toISOString()
        });
    }

    completeTrip(orderId, rating = 5) {
        const order = this.updateOrder(orderId, {
            status: 'completed',
            completedAt: new Date().toISOString(),
            driverRating: rating
        });

        if (order) {
            this.acceptedOrders = this.acceptedOrders.filter(o => o.id !== orderId);
            this.updateEarnings(order);
            this.showNotification('🎉 Trip muvaffaqiyatli yakunlandi!', 'success');
        }

        return order;
    }

    // ================================
    // EARNINGS & STATISTICS
    // ================================

    updateEarnings(order) {
        const fare = order.fare || 50000;
        this.earnings += fare;
        this.setData('earnings', this.earnings);
        
        // Update UI
        const earningsElement = document.getElementById('driver-earnings');
        if (earningsElement) {
            earningsElement.textContent = app.formatCurrency(this.earnings);
        }
    }

    getEarningsToday() {
        const today = new Date().toDateString();
        return this.orders
            .filter(o => {
                const createdDate = new Date(o.createdAt).toDateString();
                return createdDate === today && o.status === 'completed';
            })
            .reduce((sum, o) => sum + (o.fare || 0), 0);
    }

    getStatistics() {
        const completed = this.orders.filter(o => o.status === 'completed').length;
        const cancelled = this.orders.filter(o => o.status === 'cancelled').length;
        const rating = this.calculateRating();

        return {
            totalTrips: completed,
            cancelledTrips: cancelled,
            avgRating: rating,
            totalEarnings: this.earnings,
            earningsToday: this.getEarningsToday()
        };
    }

    calculateRating() {
        if (this.orders.length === 0) return 0;
        const sumRatings = this.orders
            .filter(o => o.driverRating)
            .reduce((sum, o) => sum + o.driverRating, 0);
        const ratedTrips = this.orders.filter(o => o.driverRating).length;
        return ratedTrips > 0 ? (sumRatings / ratedTrips).toFixed(1) : 0;
    }

    // ================================
    // PAYMENT & SETTLEMENTS
    // ================================

    requestWithdrawal(amount) {
        if (amount > this.earnings) {
            this.showNotification('❌ Yetarli hisob qolmadi', 'danger');
            return false;
        }

        const withdrawal = {
            id: this.generateId(),
            amount: amount,
            status: 'pending',
            requestedAt: new Date().toISOString()
        };

        this.earnings -= amount;
        this.setData('earnings', this.earnings);
        this.showNotification('✅ Pul yechish so\'rovi yuborildi', 'success');
        return true;
    }

    // ================================
    // NOTIFICATIONS & SOUNDS
    // ================================

    playNotificationSound() {
        // Create audio context for notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    }

    // ================================
    // DOCUMENTS & VERIFICATION
    // ================================

    uploadDocument(type, file) {
        const documents = this.getData('documents') || {};
        documents[type] = {
            fileName: file.name,
            size: file.size,
            uploadedAt: new Date().toISOString(),
            status: 'pending'
        };
        this.setData('documents', documents);
        this.showNotification('✅ Hujjat yuklandi', 'success');
    }

    getDocumentStatus() {
        return this.getData('documents') || {};
    }

    // ================================
    // SUPPORT & HELP
    // ================================

    openSupportChat() {
        this.showNotification('💬 Support chati ochildi', 'info');
    }

    submitComplaint(complaint) {
        const complaints = this.getData('complaints') || [];
        complaints.push({
            id: this.generateId(),
            complaint: complaint,
            submittedAt: new Date().toISOString(),
            status: 'pending'
        });
        this.setData('complaints', complaints);
        this.showNotification('✅ Shikoyat yuborildi', 'success');
    }

    // ================================
    // EVENT LISTENERS
    // ================================

    attachDriverListeners() {
        // Online/Offline toggle
        const onlineToggle = document.getElementById('driver-online-toggle');
        if (onlineToggle) {
            onlineToggle.addEventListener('change', (e) => {
                this.toggleOnline(e.target.checked);
            });
        }

        // Accept order buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('accept-order-btn')) {
                const orderId = e.target.dataset.orderId;
                this.acceptOrder(orderId);
                this.renderOrders();
            }

            if (e.target.classList.contains('start-trip-btn')) {
                const orderId = e.target.dataset.orderId;
                this.startTrip(orderId);
                this.renderOrders();
            }

            if (e.target.classList.contains('complete-trip-btn')) {
                const orderId = e.target.dataset.orderId;
                const rating = prompt('Baholang (1-5):', '5');
                if (rating) {
                    this.completeTrip(orderId, parseInt(rating));
                    this.renderOrders();
                }
            }
        });
    }

    // ================================
    // UI RENDERING
    // ================================

    renderOrders() {
        const container = document.getElementById('driver-orders');
        if (!container) return;

        const orders = this.getAvailableOrders();
        container.innerHTML = orders.map(order => `
            <div class="card mt-2">
                <div class="card-header">
                    <div>
                        <div class="card-title">Buyurtma #{order.id}</div>
                        <div class="card-subtitle">${app.formatDateTime(order.createdAt)}</div>
                    </div>
                    <span class="badge badge-warning">Kutish</span>
                </div>
                <div class="p-2">
                    <p><strong>📍 From:</strong> ${order.from}</p>
                    <p><strong>📍 To:</strong> ${order.to}</p>
                    <p><strong>💰 Narx:</strong> ${app.formatCurrency(order.fare || 50000)}</p>
                    <p><strong>👤 Mijoz:</strong> ${order.passengerName || 'Noma\'lum'}</p>
                </div>
                <div class="flex gap-2">
                    <button class="btn btn-success accept-order-btn" data-order-id="${order.id}">
                        ✅ Qabul qilish
                    </button>
                    <button class="btn btn-danger" onclick="app.rejectOrder('${order.id}')">
                        ❌ Rad qilish
                    </button>
                </div>
            </div>
        `).join('');

        if (orders.length === 0) {
            container.innerHTML = '<p class="text-center text-gray mt-4">Buyurtmalar yo\'q</p>';
        }
    }
}

// Initialize global driver app instance
const driverApp = new DriverApp();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DriverApp;
}
