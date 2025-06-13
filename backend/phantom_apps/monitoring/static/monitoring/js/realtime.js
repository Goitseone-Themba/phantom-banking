// Real-time updates and WebSocket functionality
let ws = null;
let reconnectInterval = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// Initialize WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/monitoring/`;
    
    try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            reconnectAttempts = 0;
            clearInterval(reconnectInterval);
            showNotification('Real-time updates connected', 'success');
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleRealtimeUpdate(data);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            attemptReconnect();
        };
        
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
    }
}

// Handle real-time updates
function handleRealtimeUpdate(data) {
    switch (data.type) {
        case 'system_metrics':
            updateSystemMetrics(data.data);
            updateSystemStatus();
            break;
            
        case 'transaction_created':
            handleNewTransaction(data.data);
            break;
            
        case 'customer_created':
            handleNewCustomer(data.data);
            break;
            
        case 'kyc_update':
            handleKycUpdate(data.data);
            break;
            
        case 'alert':
            showAlert(data.data);
            break;
            
        default:
            console.log('Unknown update type:', data.type);
    }
}

// Handle new transaction
function handleNewTransaction(transaction) {
    // Update transaction count
    const transactionStat = document.querySelector('.stat-card:nth-child(2) .stat-value');
    if (transactionStat) {
        const currentCount = parseInt(transactionStat.textContent) || 0;
        transactionStat.textContent = currentCount + 1;
        
        // Add animation
        transactionStat.classList.add('pulse');
        setTimeout(() => transactionStat.classList.remove('pulse'), 600);
    }
    
    // Update chart if visible
    if (transactionChart) {
        const lastDataPoint = transactionChart.data.datasets[0].data.length - 1;
        transactionChart.data.datasets[0].data[lastDataPoint] += transaction.amount;
        transactionChart.update('none');
    }
    
    // Show notification for large transactions
    if (transaction.amount > 10000) {
        showNotification(`Large transaction: BWP ${formatNumber(transaction.amount)}`, 'info');
    }
}

// Handle new customer
function handleNewCustomer(customer) {
    // Update customer count
    const customerStat = dashboardData.customer_stats?.total || 0;
    dashboardData.customer_stats.total = customerStat + 1;
    
    // Update UI if customer chart exists
    if (customerChart) {
        const today = customerChart.data.datasets[0].data.length - 1;
        customerChart.data.datasets[0].data[today] += 1;
        customerChart.update('none');
    }
    
    // Show notification
    showNotification('New customer registered', 'success');
}

// Handle KYC update
function handleKycUpdate(kycData) {
    // Update KYC stats
    if (dashboardData.kyc) {
        dashboardData.kyc = kycData;
    }
    
    // Update KYC chart
    if (kycChart) {
        kycChart.data.datasets[0].data = [
            kycData.pending || 0,
            kycData.approved || 0,
            kycData.rejected || 0
        ];
        kycChart.update('active');
    }
    
    // Update notification badge
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge) {
        notificationBadge.textContent = kycData.pending || 0;
    }
}

// Show alert
function showAlert(alert) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${alert.severity || 'info'}`;
    alertContainer.innerHTML = `
        <i class="fas fa-${getAlertIcon(alert.severity)}"></i>
        <div>
            <strong>${alert.title}</strong>
            <p>${alert.message}</p>
        </div>
    `;
    
    // Add to page
    const mainContent = document.querySelector('.dashboard-content');
    if (mainContent) {
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
        
        // Auto dismiss after 10 seconds
        setTimeout(() => {
            alertContainer.remove();
        }, 10000);
    }
}

// Get alert icon based on severity
function getAlertIcon(severity) {
    const icons = {
        success: 'check-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle',
        danger: 'times-circle'
    };
    return icons[severity] || 'info-circle';
}

// Attempt to reconnect WebSocket
function attemptReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        showNotification('Real-time updates disconnected', 'warning');
        return;
    }
    
    reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
    
    console.log(`Attempting to reconnect in ${delay}ms...`);
    
    reconnectInterval = setTimeout(() => {
        initWebSocket();
    }, delay);
}

// Send message through WebSocket
function sendWebSocketMessage(type, data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type, data }));
    }
}

// Subscribe to specific updates
function subscribeToUpdates(updateTypes) {
    sendWebSocketMessage('subscribe', { types: updateTypes });
}

// Unsubscribe from updates
function unsubscribeFromUpdates(updateTypes) {
    sendWebSocketMessage('unsubscribe', { types: updateTypes });
}

// Simulate real-time updates (for demo purposes)
function simulateRealtimeUpdates() {
    // Simulate system metrics update every 5 seconds
    setInterval(() => {
        const mockSystemData = {
            cpu_percent: Math.random() * 100,
            memory_percent: Math.random() * 100,
            disk_percent: Math.random() * 100
        };
        
        handleRealtimeUpdate({
            type: 'system_metrics',
            data: mockSystemData
        });
    }, 5000);
    
    // Simulate random transactions
    setInterval(() => {
        if (Math.random() > 0.7) {
            handleRealtimeUpdate({
                type: 'transaction_created',
                data: {
                    amount: Math.floor(Math.random() * 20000) + 1000,
                    type: 'payment'
                }
            });
        }
    }, 10000);
    
    // Simulate KYC updates
    setInterval(() => {
        if (Math.random() > 0.8) {
            const kycStats = dashboardData.kyc || {};
            const statuses = ['pending', 'approved', 'rejected'];
            const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
            
            kycStats[randomStatus] = (kycStats[randomStatus] || 0) + 1;
            
            handleRealtimeUpdate({
                type: 'kyc_update',
                data: kycStats
            });
        }
    }, 15000);
}

// Initialize real-time features
document.addEventListener('DOMContentLoaded', () => {
    // Try to initialize WebSocket
    // Comment out for now as it requires WebSocket server setup
    // initWebSocket();
    
    // Use simulation for demo
    simulateRealtimeUpdates();
    
    // Subscribe to relevant updates
    subscribeToUpdates(['system_metrics', 'transaction_created', 'customer_created', 'kyc_update']);
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (ws) {
        ws.close();
    }
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
    }
});

// Add pulse animation style
const pulseStyle = `
<style>
.pulse {
    animation: pulse-animation 0.6s ease-out;
}

@keyframes pulse-animation {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
    100% {
        transform: scale(1);
    }
}

.alert {
    margin-bottom: 1rem;
    animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', pulseStyle);