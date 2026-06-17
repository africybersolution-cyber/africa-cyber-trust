"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AnalyticsPage() {
  const [revenue, setRevenue] = useState<any>(null);
  const [growth, setGrowth] = useState<any>(null);
  const [topCustomers, setTopCustomers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      // Load all analytics in parallel
      const [revenueRes, growthRes, customersRes] = await Promise.all([
        fetch("https://africa-cyber-trust.onrender.com/api/admin/analytics/revenue", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("https://africa-cyber-trust.onrender.com/api/admin/analytics/user-growth", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("https://africa-cyber-trust.onrender.com/api/admin/analytics/top-customers?limit=10", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (revenueRes.ok) {
        const data = await revenueRes.json();
        setRevenue(data);
      }

      if (growthRes.ok) {
        const data = await growthRes.json();
        setGrowth(data);
      }

      if (customersRes.ok) {
        const data = await customersRes.json();
        setTopCustomers(data.customers || []);
      }
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            📈 Analytics & Insights
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Revenue, growth, and customer analytics
          </p>
        </div>
      </div>

      <div className="px-6 py-8 space-y-8">
        {/* Revenue Analytics */}
        {revenue && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Revenue Breakdown
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  ${revenue.total_all_time?.toLocaleString() || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">This Month</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  ${revenue.this_month?.toLocaleString() || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Last Month</p>
                <p className="text-2xl font-bold text-gray-700 mt-1">
                  ${revenue.last_month?.toLocaleString() || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">MRR</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  ${revenue.mrr?.toLocaleString() || 0}
                </p>
              </div>
            </div>

            {/* Payment Methods */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">
                Payment Methods
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Mobile Money</p>
                  <p className="text-xl font-bold text-gray-900">
                    {revenue.by_method?.mobile_money || 0} payments
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Cryptocurrency</p>
                  <p className="text-xl font-bold text-gray-900">
                    {revenue.by_method?.crypto || 0} payments
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* User Growth */}
        {growth && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              User Growth
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Total Users</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {growth.total_users || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Last 7 Days</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  +{growth.last_7_days || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Last 30 Days</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  +{growth.last_30_days || 0}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Last 90 Days</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  +{growth.last_90_days || 0}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Top Customers */}
        {topCustomers.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Top Customers
            </h2>
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rank
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Total Spent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Payments
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Plan
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {topCustomers.map((customer, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-lg font-bold text-gray-700">
                          #{idx + 1}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {customer.name || "Unknown"}
                          </div>
                          <div className="text-sm text-gray-500">
                            {customer.email}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-bold text-green-600">
                          ${customer.total_spent?.toFixed(2) || "0.00"}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {customer.payment_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                          {customer.plan_name || "N/A"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
