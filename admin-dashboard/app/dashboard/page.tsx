"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface LiveMetrics {
  users: {
    total: number;
    active: number;
    trial: number;
    recent_signups_7d: number;
  };
  revenue: {
    total_all_time: number;
    this_month: number;
    mrr: number;
    currency: string;
  };
  subscriptions: {
    active: number;
    starter: number;
    professional: number;
    enterprise: number;
  };
  platform: {
    total_assets: number;
    total_scans: number;
    total_findings: number;
    critical_findings: number;
  };
  payments: {
    mobile_money: number;
    crypto: number;
    total: number;
  };
}

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<LiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem("admin_token");
    const userData = localStorage.getItem("admin_user");

    if (!token || !userData) {
      router.push("/");
      return;
    }

    setUser(JSON.parse(userData));

    // Load metrics
    loadMetrics(token);

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => loadMetrics(token), 30000);
    return () => clearInterval(interval);
  }, [router]);

  const loadMetrics = async (token: string) => {
    setError(null);
    try {
      // Add cache-busting timestamp
      const cacheBust = `?_t=${Date.now()}`;
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/analytics/live-metrics${cacheBust}`,
        {
          headers: {
            "Authorization": `Bearer ${token}`,
          },
          cache: "no-store", // Force no cache
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } else if (response.status === 401) {
        // Token expired
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_user");
        router.push("/");
      } else {
        const errorText = await response.text();
        const errorMsg = `API Error ${response.status}: ${errorText}`;
        console.error(errorMsg);
        setError(errorMsg);
        // Set empty metrics
        setMetrics({
          users: { total: 0, active: 0, trial: 0, recent_signups_7d: 0 },
          revenue: { total_all_time: 0, this_month: 0, mrr: 0, currency: "USD" },
          subscriptions: { active: 0, starter: 0, professional: 0, enterprise: 0 },
          platform: { total_assets: 0, total_scans: 0, total_findings: 0, critical_findings: 0 },
          payments: { mobile_money: 0, crypto: 0, total: 0 }
        });
      }
    } catch (error: any) {
      const errorMsg = error?.message || "Network error - check CORS/connection";
      console.error("Failed to load metrics:", error);
      setError(`Connection Failed: ${errorMsg}. Clear browser cache or use Incognito mode.`);
      // Set empty metrics
      setMetrics({
        users: { total: 0, active: 0, trial: 0, recent_signups_7d: 0 },
        revenue: { total_all_time: 0, this_month: 0, mrr: 0, currency: "USD" },
        subscriptions: { active: 0, starter: 0, professional: 0, enterprise: 0 },
        platform: { total_assets: 0, total_scans: 0, total_findings: 0, critical_findings: 0 },
        payments: { mobile_money: 0, crypto: 0, total: 0 }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    router.push("/");
  };

  if (loading || !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  const StatCard = ({ title, value, subtitle, icon, color = "blue" }: any) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg bg-${color}-50`}>
          {icon}
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-sm text-gray-500 font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        {subtitle && <p className="text-sm text-gray-400">{subtitle}</p>}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-500 text-sm mt-1">Real-time platform metrics</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.role}</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-red-900 mb-1">
                  Failed to Load Metrics
                </h3>
                <p className="text-sm text-red-700 mb-3">{error}</p>
                <div className="text-xs text-red-600 space-y-1">
                  <p><strong>Fix:</strong> Clear browser cache (Ctrl+Shift+Delete) and refresh, or use Incognito mode (Ctrl+Shift+N)</p>
                  <p><strong>Alternative:</strong> Agent pages work fine - click "Manage Agents" below</p>
                </div>
              </div>
              <button
                onClick={() => loadMetrics(localStorage.getItem("admin_token") || "")}
                className="px-3 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-800 rounded"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Quick Actions (if error) */}
        {error && (
          <div className="mb-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Can't load metrics? Agent management works fine!
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              The agent pages are new routes with no CORS cache issues. Start here:
            </p>
            <div className="flex gap-3">
              <a
                href="/dashboard/agents"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                → Manage Agents
              </a>
              <a
                href="/dashboard/agents/payouts"
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
              >
                → Process Payouts
              </a>
            </div>
          </div>
        )}

        {/* Revenue Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Revenue"
            value={`$${metrics.revenue.total_all_time.toLocaleString()}`}
            subtitle="All time"
            icon={<svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="green"
          />
          <StatCard
            title="This Month"
            value={`$${metrics.revenue.this_month.toLocaleString()}`}
            subtitle={new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            icon={<svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
            color="blue"
          />
          <StatCard
            title="MRR"
            value={`$${metrics.revenue.mrr.toLocaleString()}`}
            subtitle="Monthly recurring revenue"
            icon={<svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
            color="purple"
          />
        </div>

        {/* User Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={metrics.users.total.toLocaleString()}
            icon={<svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>}
          />
          <StatCard
            title="Active Users"
            value={metrics.users.active.toLocaleString()}
            icon={<svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="green"
          />
          <StatCard
            title="Trial Users"
            value={metrics.users.trial.toLocaleString()}
            icon={<svg className="w-6 h-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
            color="yellow"
          />
          <StatCard
            title="New (7 days)"
            value={metrics.users.recent_signups_7d.toLocaleString()}
            icon={<svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>}
            color="indigo"
          />
        </div>

        {/* Subscriptions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Active Subscriptions</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{metrics.subscriptions.active}</p>
              <p className="text-sm text-gray-500">Total Active</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{metrics.subscriptions.starter}</p>
              <p className="text-sm text-gray-600">Starter ($15/mo)</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{metrics.subscriptions.professional}</p>
              <p className="text-sm text-gray-600">Professional ($79/mo)</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{metrics.subscriptions.enterprise}</p>
              <p className="text-sm text-gray-600">Enterprise ($299/mo)</p>
            </div>
          </div>
        </div>

        {/* Platform Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Activity</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Assets</span>
                <span className="text-xl font-bold text-gray-900">{metrics.platform.total_assets}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Scans</span>
                <span className="text-xl font-bold text-gray-900">{metrics.platform.total_scans}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Findings</span>
                <span className="text-xl font-bold text-gray-900">{metrics.platform.total_findings}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-red-600 font-medium">Critical Findings</span>
                <span className="text-xl font-bold text-red-600">{metrics.platform.critical_findings}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Methods</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Mobile Money</span>
                <span className="text-xl font-bold text-blue-600">{metrics.payments.mobile_money}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Cryptocurrency</span>
                <span className="text-xl font-bold text-purple-600">{metrics.payments.crypto}</span>
              </div>
              <div className="flex justify-between items-center border-t pt-4">
                <span className="text-gray-900 font-medium">Total Payments</span>
                <span className="text-xl font-bold text-gray-900">{metrics.payments.total}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation - Admin */}
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Admin Management
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/dashboard/users" className="bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-4 transition-colors">
              <h3 className="font-semibold text-gray-900">Manage Users</h3>
              <p className="text-sm text-gray-500 mt-1">Create, suspend, grant plans</p>
            </a>
            <a href="/dashboard/analytics" className="bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-4 transition-colors">
              <h3 className="font-semibold text-gray-900">Analytics</h3>
              <p className="text-sm text-gray-500 mt-1">Revenue, growth, top customers</p>
            </a>
            <a href="/dashboard/audit" className="bg-white hover:bg-gray-50 border border-gray-200 rounded-lg p-4 transition-colors">
              <h3 className="font-semibold text-gray-900">Audit Logs</h3>
              <p className="text-sm text-gray-500 mt-1">View all admin actions</p>
            </a>
          </div>
        </div>

        {/* Navigation - Agents */}
        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Agent Management
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/dashboard/agents" className="bg-white hover:bg-blue-50 border border-blue-200 rounded-lg p-4 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">Manage Agents</h3>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">New</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">Approve, reject, assign country managers</p>
            </a>
            <a href="/dashboard/agents/payouts" className="bg-white hover:bg-green-50 border border-green-200 rounded-lg p-4 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">Payout Requests</h3>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">New</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">Process commission payouts</p>
            </a>
            <a href="/dashboard/fraud" className="bg-white hover:bg-red-50 border border-red-200 rounded-lg p-4 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">Fraud Detection</h3>
                <span className="text-xs bg-red-100 text-red-800 px-2 py-0.5 rounded-full">New</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">Scan for suspicious activity</p>
            </a>
          </div>

          {/* Navigation - Training & WhatsApp */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a href="/dashboard/training" className="bg-white hover:bg-indigo-50 border border-indigo-200 rounded-lg p-4 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">📚 Training Courses</h3>
                <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full">New</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">Create and manage agent training</p>
            </a>
            <a href="/dashboard/whatsapp" className="bg-white hover:bg-green-50 border border-green-200 rounded-lg p-4 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-semibold text-gray-900">📱 WhatsApp Notifications</h3>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">New</span>
              </div>
              <p className="text-sm text-gray-500 mt-1">Test and manage agent notifications</p>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
