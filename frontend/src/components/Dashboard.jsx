import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';
import ocrService from '../services/ocrService';

/**
 * Admin Dashboard Component
 * Displays analytics and statistics for OCR processing
 */
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange, fetchStats]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await ocrService.getStatus();
      console.log('Service status:', response);
      // In production, this would fetch actual analytics data
      const mockStats = generateMockStats();
      setStats(mockStats);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateMockStats = () => ({
    overview: {
      totalDocuments: 1247,
      successRate: 94.3,
      averageProcessingTime: 2.4,
      activeProcessing: 3,
    },
    languages: {
      English: 523,
      Hindi: 412,
      Urdu: 312,
    },
    processingTimes: {
      preprocessing: 0.5,
      ocr: 1.2,
      language_detection: 0.2,
      cleaning: 0.3,
      transliteration: 0.2,
    },
    recentProcessing: [
      { time: '14:30', count: 12 },
      { time: '14:45', count: 15 },
      { time: '15:00', count: 18 },
      { time: '15:15', count: 14 },
      { time: '15:30', count: 20 },
    ],
    confidenceDistribution: {
      'A (90-100%)': 742,
      'B (80-89%)': 315,
      'C (70-79%)': 142,
      'D (60-69%)': 32,
      'F (<60%)': 16,
    },
  });

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">OCR Analytics Dashboard</h1>
        <div className="flex gap-2">
          {['1h', '24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Documents"
          value={stats.overview.totalDocuments.toLocaleString()}
          icon="📄"
          color="blue"
        />
        <StatCard
          title="Success Rate"
          value={`${stats.overview.successRate}%`}
          icon="✅"
          color="green"
        />
        <StatCard
          title="Avg Processing Time"
          value={`${stats.overview.averageProcessingTime}s`}
          icon="⚡"
          color="yellow"
        />
        <StatCard
          title="Active Processing"
          value={stats.overview.activeProcessing}
          icon="🔄"
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Language Distribution */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Language Distribution</h2>
          <div className="h-64">
            <PieChart data={stats.languages} />
          </div>
        </div>

        {/* Processing Times */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Processing Stage Times</h2>
          <div className="h-64">
            <BarChart data={stats.processingTimes} />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Activity</h2>
          <div className="h-64">
            <LineChart data={stats.recentProcessing} />
          </div>
        </div>

        {/* Confidence Distribution */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Quality Distribution</h2>
          <div className="h-64">
            <HorizontalBarChart data={stats.confidenceDistribution} />
          </div>
        </div>
      </div>

      {/* Detailed Stats Table */}
      <div className="card">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Processing Breakdown</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Time (s)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  % of Total
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Object.entries(stats.processingTimes).map(([stage, time]) => {
                const total = Object.values(stats.processingTimes).reduce((a, b) => a + b, 0);
                const percentage = ((time / total) * 100).toFixed(1);
                return (
                  <tr key={stage}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {stage.replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {time.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {percentage}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`text-4xl ${colorClasses[color]} w-16 h-16 flex items-center justify-center rounded-full`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

// Simplified chart components (you'd use actual Chart.js with react-chartjs-2)
const PieChart = ({ data }) => (
  <div className="flex items-center justify-center h-full">
    <div className="space-y-2">
      {Object.entries(data).map(([lang, count]) => (
        <div key={lang} className="flex items-center gap-2">
          <div className="w-4 h-4 rounded bg-primary-500"></div>
          <span className="text-sm">{lang}: {count}</span>
        </div>
      ))}
    </div>
  </div>
);

const BarChart = ({ data }) => (
  <div className="flex items-end justify-around h-full p-4">
    {Object.entries(data).map(([stage, time]) => (
      <div key={stage} className="flex flex-col items-center gap-2">
        <div
          className="w-12 bg-primary-500 rounded-t"
          style={{ height: `${(time / 2) * 100}%` }}
        ></div>
        <span className="text-xs">{stage.slice(0, 3)}</span>
      </div>
    ))}
  </div>
);

const LineChart = ({ data }) => (
  <div className="flex items-end justify-around h-full p-4">
    {data.map((point, i) => (
      <div key={i} className="flex flex-col items-center gap-2">
        <div
          className="w-8 bg-green-500 rounded-t"
          style={{ height: `${(point.count / 20) * 100}%` }}
        ></div>
        <span className="text-xs">{point.time}</span>
      </div>
    ))}
  </div>
);

const HorizontalBarChart = ({ data }) => (
  <div className="space-y-3 p-4">
    {Object.entries(data).map(([grade, count]) => {
      const maxCount = Math.max(...Object.values(data));
      const width = (count / maxCount) * 100;
      return (
        <div key={grade}>
          <div className="flex items-center justify-between text-sm mb-1">
            <span>{grade}</span>
            <span className="font-semibold">{count}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-primary-600 h-4 rounded-full"
              style={{ width: `${width}%` }}
            ></div>
          </div>
        </div>
      );
    })}
  </div>
);

export default Dashboard;
