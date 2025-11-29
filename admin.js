/* ================================
   ADMIN PANEL - ADMIN.JS
   ================================ */

class AdminApp extends TaxiApp {
    constructor() {
        this.adminLevel = 'super'; // super, manager, operator
        this.permissions = {};
        this.users = [];
        this.drivers = [];
        this.statistics = {};
        super();
        this.initAdmin();
    }

    initAdmin() {
        console.log('🔑 Admin App Initialized');
        this.loadAdminData();
        this.attachAdminListeners();
        this.updateDashboard();
    }

    // ================================
    // ADMIN AUTHENTICATION
    // ================================

    loginAdmin(phone, password) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const adminUsers = [
                    { phone: '+998901234567', password: 'admin123', name: 'Admin 1', id: 'admin_panel_1' },
                    { phone: '+998901234568', password: 'admin123', name: 'Admin 2', id: 'admin_panel_2' }
                ];

                const admin = adminUsers.find(a => a.phone === phone && a.password === password);
                
                if (admin) {
                    this.user = { ...admin, role: 'admin' };
                    this.adminLevel = 'super';
                    this.saveUser(this.user);
                    this.showNotification(`✅ Xush kelibsiz, ${admin.name}!`, 'success');
                    resolve(admin);
                } else {
                    this.showNotification('❌ Noto\'g\'ri telefon yoki parol', 'danger');
                    reject(new Error('Invalid credentials'));
                }
            }, 1000);
        });
    }

    // ================================
    // DRIVER MANAGEMENT
    // ================================

    registerDriver(driverData) {
        const driver = {
            id: this.generateId(),
            ...driverData,
            status: 'pending',
            registeredAt: new Date().toISOString(),
            verified: false
        };

        this.drivers.push(driver);
        this.setData('drivers', this.drivers);
        this.showNotification('✅ Haydovchi ro\'yxatdan o\'tkazildi', 'success');
        return driver;
    }

    verifyDriver(driverId) {
        const driver = this.drivers.find(d => d.id === driverId);
        if (driver) {
            driver.verified = true;
            driver.status = 'active';
            this.setData('drivers', this.drivers);
            this.showNotification('✅ Haydovchi tasdiqlandi', 'success');
            return driver;
        }
        return null;
    }

    rejectDriver(driverId, reason) {
        const driver = this.drivers.find(d => d.id === driverId);
        if (driver) {
            driver.status = 'rejected';
            driver.rejectionReason = reason;
            this.setData('drivers', this.drivers);
            this.showNotification('❌ Haydovchi rad qilindi', 'warning');
            return driver;
        }
        return null;
    }

    suspendDriver(driverId, reason) {
        const driver = this.drivers.find(d => d.id === driverId);
        if (driver) {
            driver.status = 'suspended';
            driver.suspensionReason = reason;
            driver.suspendedAt = new Date().toISOString();
            this.setData('drivers', this.drivers);
            this.showNotification('⏸️ Haydovchi to\'xtatildi', 'warning');
            return driver;
        }
        return null;
    }

    getDrivers(filter = 'all') {
        if (filter === 'all') return this.drivers;
        return this.drivers.filter(d => d.status === filter);
    }

    // ================================
    // COMMISSION MANAGEMENT
    // ================================

    setCommissionRate(rate) {
        if (rate < 0 || rate > 100) {
            this.showNotification('❌ Komissiya noto\'g\'ri', 'danger');
            return false;
        }

        this.setData('commissionRate', rate);
        this.showNotification(`✅ Komissiya ${rate}% ga o'rnatilingan`, 'success');
        return true;
    }

    getCommissionRate() {
        return this.getData('commissionRate') || 25; // Default 25%
    }

    calculateCommission(amount) {
        const rate = this.getCommissionRate();
        return (amount * rate) / 100;
    }

    // ================================
    // FINANCIAL MANAGEMENT
    // ================================

    getRevenue() {
        return this.orders
            .filter(o => o.status === 'completed')
            .reduce((sum, o) => sum + (o.fare || 0), 0);
    }

    getCommissionEarnings() {
        const revenue = this.getRevenue();
        return this.calculateCommission(revenue);
    }

    getDriverEarnings() {
        return this.orders
            .filter(o => o.status === 'completed')
            .reduce((sum, o) => sum + (o.driverEarning || 0), 0);
    }

    getFinancialSummary() {
        return {
            totalRevenue: this.getRevenue(),
            commissionEarnings: this.getCommissionEarnings(),
            driverEarnings: this.getDriverEarnings(),
            totalTrips: this.orders.filter(o => o.status === 'completed').length,
            pendingWithdrawals: this.getData('pendingWithdrawals') || []
        };
    }

    // ================================
    // SUPPORT MANAGEMENT
    // ================================

    getComplaints() {
        return this.getData('complaints') || [];
    }

    resolveComplaint(complaintId, resolution) {
        const complaints = this.getComplaints();
        const complaint = complaints.find(c => c.id === complaintId);
        
        if (complaint) {
            complaint.status = 'resolved';
            complaint.resolution = resolution;
            complaint.resolvedAt = new Date().toISOString();
            this.setData('complaints', complaints);
            this.showNotification('✅ Shikoyat hal qilindi', 'success');
        }

        return complaint;
    }

    // ================================
    // REPORTING
    // ================================

    generateDailyReport() {
        const today = new Date().toDateString();
        const todayOrders = this.orders.filter(o => {
            const createdDate = new Date(o.createdAt).toDateString();
            return createdDate === today;
        });

        return {
            date: today,
            totalTrips: todayOrders.length,
            completedTrips: todayOrders.filter(o => o.status === 'completed').length,
            cancelledTrips: todayOrders.filter(o => o.status === 'cancelled').length,
            totalRevenue: todayOrders
                .filter(o => o.status === 'completed')
                .reduce((sum, o) => sum + (o.fare || 0), 0)
        };
    }

    generateMonthlyReport(month = new Date().getMonth()) {
        const monthOrders = this.orders.filter(o => {
            const orderDate = new Date(o.createdAt);
            return orderDate.getMonth() === month;
        });

        return {
            month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month],
            totalTrips: monthOrders.length,
            completedTrips: monthOrders.filter(o => o.status === 'completed').length,
            totalRevenue: monthOrders
                .filter(o => o.status === 'completed')
                .reduce((sum, o) => sum + (o.fare || 0), 0),
            averageFare: monthOrders.length > 0 
                ? monthOrders.reduce((sum, o) => sum + (o.fare || 0), 0) / monthOrders.length 
                : 0
        };
    }

    // ================================
    // ANNOUNCEMENTS & MESSAGING
    // ================================

    sendAnnouncement(title, message, targetRole) {
        const announcement = {
            id: this.generateId(),
            title: title,
            message: message,
            targetRole: targetRole,
            sentAt: new Date().toISOString(),
            read: false
        };

        const announcements = this.getData('announcements') || [];
        announcements.push(announcement);
        this.setData('announcements', announcements);
        this.showNotification('✅ Xabar yuborildi', 'success');
        return announcement;
    }

    // ================================
    // SYSTEM SETTINGS
    // ================================

    updateSystemSettings(settings) {
        const currentSettings = this.getData('systemSettings') || {};
        const updatedSettings = { ...currentSettings, ...settings };
        this.setData('systemSettings', updatedSettings);
        this.showNotification('✅ Sozlamalar yangilandi', 'success');
        return updatedSettings;
    }

    getSystemSettings() {
        return this.getData('systemSettings') || {
            appVersion: '1.0.0',
            maintenanceMode: false,
            maxOrderDistance: 50,
            minRating: 4.0
        };
    }

    // ================================
    // DASHBOARD DATA
    // ================================

    loadAdminData() {
        this.drivers = this.getData('drivers') || [];
        this.users = this.orders.filter(o => o.passengerName)
            .map(o => ({ name: o.passengerName, orders: 1 }));
    }

    updateDashboard() {
        const financialSummary = this.getFinancialSummary();
        const dailyReport = this.generateDailyReport();
        const driverStats = {
            total: this.drivers.length,
            active: this.drivers.filter(d => d.status === 'active').length,
            pending: this.drivers.filter(d => d.status === 'pending').length,
            suspended: this.drivers.filter(d => d.status === 'suspended').length
        };

        this.statistics = {
            financial: financialSummary,
            daily: dailyReport,
            drivers: driverStats
        };

        return this.statistics;
    }

    // ================================
    // EVENT LISTENERS
    // ================================

    attachAdminListeners() {
        document.addEventListener('click', (e) => {
            // Verify driver button
            if (e.target.classList.contains('verify-driver-btn')) {
                const driverId = e.target.dataset.driverId;
                this.verifyDriver(driverId);
                this.renderDrivers();
            }

            // Reject driver button
            if (e.target.classList.contains('reject-driver-btn')) {
                const driverId = e.target.dataset.driverId;
                const reason = prompt('Rad qilish sababi:');
                if (reason) {
                    this.rejectDriver(driverId, reason);
                    this.renderDrivers();
                }
            }

            // Suspend driver button
            if (e.target.classList.contains('suspend-driver-btn')) {
                const driverId = e.target.dataset.driverId;
                const reason = prompt('To\'xtatish sababi:');
                if (reason) {
                    this.suspendDriver(driverId, reason);
                    this.renderDrivers();
                }
            }
        });
    }

    // ================================
    // UI RENDERING
    // ================================

    renderDrivers() {
        const container = document.getElementById('admin-drivers');
        if (!container) return;

        container.innerHTML = this.drivers.map(driver => `
            <tr>
                <td>${driver.id}</td>
                <td>${driver.name || 'Noma\'lum'}</td>
                <td>${driver.phone}</td>
                <td><span class="badge badge-${driver.status === 'active' ? 'success' : 'warning'}">${driver.status}</span></td>
                <td>${driver.verified ? '✅' : '❌'}</td>
                <td>
                    <button class="btn btn-success verify-driver-btn" data-driver-id="${driver.id}" ${driver.verified ? 'disabled' : ''}>
                        Tasdiqlash
                    </button>
                    <button class="btn btn-danger reject-driver-btn" data-driver-id="${driver.id}">
                        Rad qilish
                    </button>
                </td>
            </tr>
        `).join('');
    }

    renderFinancialDashboard() {
        const summary = this.getFinancialSummary();
        const container = document.getElementById('admin-financial');
        if (!container) return;

        container.innerHTML = `
            <div class="grid grid-3">
                <div class="card">
                    <div class="card-title">Umumiy Daromad</div>
                    <div style="font-size: 24px; font-weight: bold; color: var(--primary);" class="mt-2">
                        ${app.formatCurrency(summary.totalRevenue)}
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Komissiya</div>
                    <div style="font-size: 24px; font-weight: bold; color: var(--success);" class="mt-2">
                        ${app.formatCurrency(summary.commissionEarnings)}
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Haydovchining O'zbeki</div>
                    <div style="font-size: 24px; font-weight: bold; color: var(--warning);" class="mt-2">
                        ${app.formatCurrency(summary.driverEarnings)}
                    </div>
                </div>
            </div>
        `;
    }
}

// Initialize global admin app instance
const adminApp = new AdminApp();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminApp;
}
