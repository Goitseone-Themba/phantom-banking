import React from 'react';

const Dashboard: React.FC = () => {
  const userName = 'John Doe';

  const stats = [
    { label: 'Balance', value: 'P12,480.50', color: 'bg-indigo-500' },
    { label: 'Income', value: 'P4,200.00', color: 'bg-green-500' },
    { label: 'Expenses', value: 'P1,820.00', color: 'bg-red-500' },
  ];

  const transactions = [
    { id: 1, name: 'Amazon Purchase', amount: '-P120.00', date: '2024-05-20' },
    { id: 2, name: 'Salary', amount: '+P3,500.00', date: '2024-05-18' },
    { id: 3, name: 'Netflix', amount: '-P15.00', date: '2024-05-17' },
    { id: 4, name: 'Transfer to Alice', amount: '-P500.00', date: '2024-05-15' },
  ];

  const actions = [
    { label: 'Send Money', icon: '💸' },
    { label: 'Request', icon: '📩' },
    { label: 'Top-Up', icon: '💳' },
    { label: 'Pay Bills', icon: '🧾' },
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Welcome back, {userName} 👋</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {stats.map((stat) => (
          <div key={stat.label} className={`rounded-xl p-4 shadow-md text-white ${stat.color}`}>
            <p className="text-sm uppercase">{stat.label}</p>
            <h2 className="text-xl font-semibold">{stat.value}</h2>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Recent Transactions */}
        <div className="md:col-span-2 bg-white rounded-xl shadow-md p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Recent Transactions</h2>
          <ul>
            {transactions.map((tx) => (
              <li key={tx.id} className="flex justify-between py-2 border-b border-gray-200">
                <div>
                  <p className="text-gray-700 font-medium">{tx.name}</p>
                  <p className="text-sm text-gray-400">{tx.date}</p>
                </div>
                <p
                  className={`font-medium ${
                    tx.amount.startsWith('-') ? 'text-red-500' : 'text-green-500'
                  }`}
                >
                  {tx.amount}
                </p>
              </li>
            ))}
          </ul>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-md p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            {actions.map((action) => (
              <button
                key={action.label}
                className="bg-indigo-100 hover:bg-indigo-200 text-indigo-700 font-medium py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition"
              >
                <span>{action.icon}</span>
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
