// Chart configurations and initialization
let transactionChart, customerChart, kycChart;

// Chart default configuration
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.plugins.legend.display = false;
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleFont.size = 14;
Chart.defaults.plugins.tooltip.bodyFont.size = 12;

// Initialize all charts
function initializeCharts() {
    initTransactionChart();
    initCustomerChart();
    initKycChart();
}

// Initialize transaction volume chart
function initTransactionChart() {
    const ctx = document.getElementById('transactionChart');
    if (!ctx) return;
    
    // Generate sample data for last 7 days
    const labels = generateDateLabels(7);
    const data = generateRandomData(7, 50000, 150000);
    
    transactionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Transaction Volume',
                data: data,
                borderColor: '#667eea',
                backgroundColor: createGradient(ctx, '#667eea'),
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'BWP ' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        callback: function(value) {
                            return 'BWP ' + formatNumber(value / 1000) + 'k';
                        }
                    }
                }
            }
        }
    });
}

// Initialize customer growth chart
function initCustomerChart() {
    const ctx = document.getElementById('customerChart');
    if (!ctx) return;
    
    // Generate sample data for last 30 days
    const labels = generateDateLabels(30);
    const newCustomers = generateRandomData(30, 10, 50);
    const totalCustomers = generateCumulativeData(newCustomers, dashboardData.customer_stats?.total || 100);
    
    customerChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'New Customers',
                data: newCustomers,
                backgroundColor: '#48bb78',
                borderRadius: 4,
                barPercentage: 0.7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'New Customers: ' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 7
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    border: {
                        display: false
                    }
                }
            }
        }
    });
}

// Initialize KYC status chart
function initKycChart() {
    const ctx = document.getElementById('kycChart');
    if (!ctx) return;
    
    const kycData = dashboardData.kyc_stats || {};
    const data = [
        kycData.pending || 0,
        kycData.approved || 0,
        kycData.rejected || 0
    ];
    
    kycChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'Approved', 'Rejected'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#ed8936',
                    '#48bb78',
                    '#f56565'
                ],
                borderWidth: 0,
                spacing: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(data) {
    // Update transaction chart
    if (transactionChart) {
        const newData = generateRandomData(7, 50000, 150000);
        transactionChart.data.datasets[0].data = newData;
        transactionChart.update('active');
    }
    
    // Update customer chart
    if (customerChart) {
        const newData = generateRandomData(30, 10, 50);
        customerChart.data.datasets[0].data = newData;
        customerChart.update('active');
    }
    
    // Update KYC chart
    if (kycChart && data.kyc_stats) {
        kycChart.data.datasets[0].data = [
            data.kyc_stats.pending || 0,
            data.kyc_stats.approved || 0,
            data.kyc_stats.rejected || 0
        ];
        kycChart.update('active');
    }
}

// Helper functions
function createGradient(ctx, color) {
    const chart = ctx.getContext('2d');
    const gradient = chart.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, color + '40');
    gradient.addColorStop(1, color + '00');
    return gradient;
}

function generateDateLabels(days) {
    const labels = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        if (days <= 7) {
            labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        } else {
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
    }
    
    return labels;
}

function generateRandomData(count, min, max) {
    const data = [];
    for (let i = 0; i < count; i++) {
        data.push(Math.floor(Math.random() * (max - min + 1)) + min);
    }
    return data;
}

function generateCumulativeData(baseData, startValue) {
    const data = [];
    let cumulative = startValue;
    
    for (let i = 0; i < baseData.length; i++) {
        cumulative += baseData[i];
        data.push(cumulative);
    }
    
    return data;
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}