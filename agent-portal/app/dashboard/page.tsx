"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const [agent, setAgent] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    const token = localStorage.getItem("agent_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agents/me",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAgent(data.agent);
        setStats(data.stats);
      } else {
        // Not an agent yet
        alert("You are not approved as an agent yet. Please wait for admin approval.");
        router.push("/");
      }
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back! 👋
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Your agent dashboard
          </p>
        </div>
      </div>

      <div className="px-6 py-8">
        {/* Agent Info */}
        {agent && (
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-sm p-6 mb-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Agent Profile</h2>
                <div className="mt-3 space-y-1">
                  <p className="text-blue-100">
                    <span className="font-medium">Referral Code:</span>{" "}
                    {agent.referral_code}
                  </p>
                  <p className="text-blue-100">
                    <span className="font-medium">Country:</span> {agent.country}
                  </p>
                  <p className="text-blue-100">
                    <span className="font-medium">Tier:</span>{" "}
                    <span className="uppercase">{agent.tier}</span>
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    agent.status === "approved"
                      ? "bg-green-500 text-white"
                      : "bg-yellow-500 text-white"
                  }`}
                >
                  {agent.status}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Total Sales</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${stats.total_sales?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Total Commissions</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                ${stats.total_commissions?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">
                ${stats.pending_commissions?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Paid Out</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                ${stats.paid_commissions?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        )}

        {/* Quick Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Total Customers</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {stats.total_customers || 0}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">This Month Sales</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                ${stats.monthly_sales?.toLocaleString() || 0}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Sub-Agents</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {stats.sub_agents_count || 0}
              </p>
            </div>
          </div>
        )}

        {/* Referral Link */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4">
            📎 Your Referral Link
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={`https://africa-cyber-trust.vercel.app/signup?ref=${agent?.referral_code}`}
              readOnly
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
            />
            <button
              onClick={() => {
                navigator.clipboard.writeText(
                  `https://africa-cyber-trust.vercel.app/signup?ref=${agent?.referral_code}`
                );
                alert("Copied to clipboard!");
              }}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
            >
              Copy
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
