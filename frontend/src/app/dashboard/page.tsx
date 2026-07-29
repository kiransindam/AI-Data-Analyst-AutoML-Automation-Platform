// frontend/src/app/dashboard/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity, Database, Cpu, FileText, TrendingUp, AlertTriangle } from 'lucide-react';
import { api } from '@/services/api';
import { useStore } from '@/store/useStore';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function DashboardPage() {
  const { datasets, projects, user } = useStore();
  const [stats, setStats] = useState({
    totalDatasets: 0,
    totalProjects: 0,
    totalModels: 0,
    totalPredictions: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const { data: ds } = await api.listDatasets();
      setStats(prev => ({ ...prev, totalDatasets: ds.length }));
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back, {user?.username || 'Analyst'}!</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Database className="h-6 w-6" />}
            label="Datasets"
            value={stats.totalDatasets}
            color="blue"
            trend="+12%"
          />
          <StatCard
            icon={<Activity className="h-6 w-6" />}
            label="Projects"
            value={stats.totalProjects}
            color="green"
            trend="+8%"
          />
          <StatCard
            icon={<Cpu className="h-6 w-6" />}
            label="Models Trained"
            value={stats.totalModels}
            color="purple"
            trend="+23%"
          />
          <StatCard
            icon={<FileText className="h-6 w-6" />}
            label="Reports Generated"
            value={stats.totalPredictions}
            color="amber"
            trend="+5%"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Activity Chart */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Activity</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weeklyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="analyses" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predictions" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Model Performance */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Accuracy Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={modelTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis domain={[0.7, 1]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="accuracy" stroke="#3B82F6" strokeWidth={2} />
                <Line type="monotone" dataKey="f1_score" stroke="#10B981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Projects */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Projects</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Project</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Dataset</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Best Model</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Date</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((project) => (
                  <tr key={project.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{project.name}</td>
                    <td className="py-3 px-4 text-gray-600">—</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={project.status} />
                    </td>
                    <td className="py-3 px-4 text-gray-600">—</td>
                    <td className="py-3 px-4 text-gray-500 text-sm">—</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Mock data
const weeklyActivity = [
  { day: 'Mon', analyses: 4, predictions: 12 },
  { day: 'Tue', analyses: 6, predictions: 18 },
  { day: 'Wed', analyses: 3, predictions: 9 },
  { day: 'Thu', analyses: 8, predictions: 24 },
  { day: 'Fri', analyses: 5, predictions: 15 },
  { day: 'Sat', analyses: 2, predictions: 6 },
  { day: 'Sun', analyses: 1, predictions: 3 },
];

const modelTrend = [
  { week: 'W1', accuracy: 0.82, f1_score: 0.79 },
  { week: 'W2', accuracy: 0.85, f1_score: 0.83 },
  { week: 'W3', accuracy: 0.87, f1_score: 0.85 },
  { week: 'W4', accuracy: 0.89, f1_score: 0.87 },
  { week: 'W5', accuracy: 0.91, f1_score: 0.89 },
  { week: 'W6', accuracy: 0.92, f1_score: 0.90 },
];

function StatCard({ icon, label, value, color, trend }: any) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    amber: 'bg-amber-50 text-amber-600',
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>{icon}</div>
        <span className="text-sm text-green-600 font-medium flex items-center gap-1">
          <TrendingUp className="h-3 w-3" /> {trend}
        </span>
      </div>
      <p className="text-3xl font-bold text-gray-900 mt-4">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{label}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed: 'bg-green-100 text-green-700',
    analyzing: 'bg-blue-100 text-blue-700',
    training: 'bg-purple-100 text-purple-700',
    failed: 'bg-red-100 text-red-700',
    created: 'bg-gray-100 text-gray-700',
  };

  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${styles[status] || styles.created}`}>
      {status}
    </span>
  );
}
