// Dashboard initialization and main functionality
let dashboardData = {};
let autoRefreshInterval = null;
let isAutoRefreshing = false;

// Initialize dashboard
function initializeDashboard(data) {
    console.log('Initializing dashboard with data:', data);
    dashboardData = data;
    
    // Initialize charts
    initializeCharts();
    
    // Load business table data
    loadBusinessesTable();
    
    // Update system status
    updateSystemStatus();
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('Dashboard initialization complete');
}

// Load businesses table
function loadBusinessesTable() {
    const tableBody = document.getElementById('businessesTableBody');
    if (!tableBody) return;
    
    // Use real business data from server if available
    let businesses = [];
    
    if (dashboardData.recent_merchants && Array.isArray(dashboardData.recent_merchants)) {
        businesses = dashboardData.recent_merchants.map(merchant => ({
            name: merchant.name,
            industry: merchant.industry,
            wallets: merchant.wallets,
            value: merchant.total_value,
            status: merchant.status
        }));
    }
    
    // Fallback to sample data if no real data available
    if (businesses.length === 0) {
        businesses = [
            {
                name: 'Acme Corp',
                industry: 'Technology',
                wallets: 15,
                value: 500000,
                status: 'active'
            },
            {
                name: 'Global Foods Inc.',
                industry: 'Food & Beverage',
                wallets: 20,
                value: 750000,
                status: 'active'
            },
            {
                name: 'Sunrise Retail',
                industry: 'Retail',
                wallets: 10,
                value: 250000,
                status: 'active'
            },
            {
                name: 'Innovate Solutions',
                industry: 'Consulting',
                wallets: 5,
                value: 100000,
                status: 'active'
            },
            {
                name: 'Pinnacle Investments',
                industry: 'Finance',
                wallets: 25,
                value: 700000,
                status: 'active'
            }
        ];
    }
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add rows
    businesses.forEach((business, index) => {
        const row = createBusinessRow(business);
        tableBody.appendChild(row);
        
        // Animate row appearance
        setTimeout(() => {
            row.classList.add('fade-in');
        }, index * 50);
    });
}

// Create business table row
function createBusinessRow(business) {
    const row = document.createElement('tr');
    row.className = 'table-row';
    
    row.innerHTML = `
        <td>
            <div class="business-name">
                <i class="fas fa-building"></i>
                <span>${business.name}</span>
            </div>
        </td>
        <td>
            <span class="industry-tag">${business.industry}</span>
        </td>
        <td>${business.wallets}</td>
        <td>BWP ${formatNumber(business.value)}</td>
        <td>
            <span class="status-badge ${business.status}">
                ${business.status.charAt(0).toUpperCase() + business.status.slice(1)}
            </span>
        </td>
    `;
    
    return row;
}

// Update system status indicator
function updateSystemStatus() {
    const statusIndicator = document.getElementById('systemStatus');
    if (!statusIndicator) return;
    
    const cpu = dashboardData.system?.cpu_percent || 0;
    const memory = dashboardData.system?.memory_percent || 0;
    const disk = dashboardData.system?.disk_percent || 0;
    
    // Calculate overall system health
    const avgUsage = (cpu + memory + disk) / 3;
    
    if (avgUsage < 70) {
        statusIndicator.style.backgroundColor = 'var(--success)';
    } else if (avgUsage < 85) {
        statusIndicator.style.backgroundColor = 'var(--warning)';
    } else {
        statusIndicator.style.backgroundColor = 'var(--danger)';
    }
}

// Toggle auto refresh
function toggleAutoRefresh() {
    const refreshButton = document.querySelector('.icon-button .fa-sync-alt').parentElement;
    
    if (isAutoRefreshing) {
        // Stop auto refresh
        clearInterval(autoRefreshInterval);
        isAutoRefreshing = false;
        refreshButton.classList.remove('active');
        showNotification('Auto refresh disabled', 'info');
    } else {
        // Start auto refresh
        autoRefreshInterval = setInterval(refreshDashboard, 30000); // 30 seconds
        isAutoRefreshing = true;
        refreshButton.classList.add('active');
        showNotification('Auto refresh enabled (30s)', 'success');
    }
}

// Refresh dashboard data
function refreshDashboard() {
    // Show loading state
    showLoadingState();
    
    // Fetch updated data
    fetch('/monitoring/api/dashboard-data/')
        .then(response => response.json())
        .then(data => {
            // Update dashboard data
            dashboardData = data;
            
            // Update all components
            updateCharts(data);
            updateStats(data);
            updateSystemMetrics(data.system_stats);
            updateSystemStatus();
            
            // Hide loading state
            hideLoadingState();
            
            showNotification('Dashboard updated', 'success');
        })
        .catch(error => {
            console.error('Error refreshing dashboard:', error);
            hideLoadingState();
            showNotification('Failed to refresh dashboard', 'danger');
        });
}

// Update stats cards
function updateStats(data) {
    // Update business stats
    const businessValue = document.querySelector('.stat-card:nth-child(1) .stat-value');
    if (businessValue) {
        businessValue.textContent = data.merchant_stats?.total || 0;
    }
    
    // Update wallet stats
    const walletValue = document.querySelector('.stat-card:nth-child(2) .stat-value');
    if (walletValue) {
        walletValue.textContent = data.wallet_stats?.total || 0;
    }
    
    // Update balance stats
    const balanceValue = document.querySelector('.stat-card:nth-child(3) .stat-value');
    if (balanceValue) {
        const balance = data.wallet_stats?.total_balance || 0;
        balanceValue.textContent = `BWP ${formatNumber(balance)}`;
    }
}

// Update system metrics
function updateSystemMetrics(systemStats) {
    if (!systemStats) return;
    
    // Update CPU progress
    const cpuProgress = document.querySelector('.metric-row:nth-child(1) .progress-fill');
    const cpuValue = document.querySelector('.metric-row:nth-child(1) .metric-value');
    if (cpuProgress && cpuValue) {
        cpuProgress.style.width = `${systemStats.cpu_percent}%`;
        cpuValue.textContent = `${systemStats.cpu_percent.toFixed(1)}%`;
    }
    
    // Update Memory progress
    const memoryProgress = document.querySelector('.metric-row:nth-child(2) .progress-fill');
    const memoryValue = document.querySelector('.metric-row:nth-child(2) .metric-value');
    if (memoryProgress && memoryValue) {
        memoryProgress.style.width = `${systemStats.memory_percent}%`;
        memoryValue.textContent = `${systemStats.memory_percent.toFixed(1)}%`;
    }
    
    // Update Disk progress
    const diskProgress = document.querySelector('.metric-row:nth-child(3) .progress-fill');
    const diskValue = document.querySelector('.metric-row:nth-child(3) .metric-value');
    if (diskProgress && diskValue) {
        diskProgress.style.width = `${systemStats.disk_percent}%`;
        diskValue.textContent = `${systemStats.disk_percent.toFixed(1)}%`;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle',
        danger: 'times-circle'
    };
    return icons[type] || 'info-circle';
}

// Show loading state
function showLoadingState() {
    const cards = document.querySelectorAll('.stat-card, .chart-card, .metric-card');
    cards.forEach(card => {
        card.classList.add('loading');
    });
}

// Hide loading state
function hideLoadingState() {
    const cards = document.querySelectorAll('.stat-card, .chart-card, .metric-card');
    cards.forEach(card => {
        card.classList.remove('loading');
    });
}

// Format number with commas
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Setup event listeners
function setupEventListeners() {
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
    
    // Dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (toggle) {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });
        }
    });
    
    // Close dropdowns on outside click
    document.addEventListener('click', () => {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    });
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + R: Refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshDashboard();
        }
        
        // Ctrl/Cmd + A: Toggle auto refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
            e.preventDefault();
            toggleAutoRefresh();
        }
    });
}

// Add notification styles
const notificationStyles = `
<style>
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: var(--surface);
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    z-index: 9999;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    border-left: 4px solid var(--success);
    color: var(--success);
}

.notification-info {
    border-left: 4px solid var(--primary-color);
    color: var(--primary-color);
}

.notification-warning {
    border-left: 4px solid var(--warning);
    color: var(--warning);
}

.notification-danger {
    border-left: 4px solid var(--danger);
    color: var(--danger);
}

.table-row {
    opacity: 0;
    transform: translateY(10px);
}

.table-row.fade-in {
    opacity: 1;
    transform: translateY(0);
    transition: all 0.3s ease;
}

.business-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.business-name i {
    color: var(--primary-color);
}

.industry-tag {
    padding: 0.25rem 0.75rem;
    background-color: var(--background);
    border-radius: 20px;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.stat-card.loading,
.chart-card.loading,
.metric-card.loading {
    position: relative;
    overflow: hidden;
}

.stat-card.loading::after,
.chart-card.loading::after,
.metric-card.loading::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    animation: loading 1.5s infinite;
}

@keyframes loading {
    to {
        left: 100%;
    }
}

.icon-button.active {
    background-color: var(--primary-color);
    color: white;
    animation: rotate 2s linear infinite;
}

@keyframes rotate {
    to {
        transform: rotate(360deg);
    }
}
</style>
`;

// Add styles to document
document.head.insertAdjacentHTML('beforeend', notificationStyles);