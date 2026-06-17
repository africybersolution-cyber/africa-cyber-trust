"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

export default function AgentDetailPage() {
  const [agent, setAgent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const router = useRouter();
  const params = useParams();
  const agentId = params.id;

  useEffect(() => {
    loadAgent();
  }, [agentId]);

  const loadAgent = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/agents/${agentId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAgent(data);
      }
    } catch (error) {
      console.error("Failed to load agent:", error);
    } finally {
      setLoading(false);
    }
  };

  const approveAgent = async () => {
    const token = localStorage.getItem("admin_token");
    setActionLoading(true);

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/agents/${agentId}/approve`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ grant_demo_scans: 5 }),
        }
      );

      if (response.ok) {
        alert("Agent approved successfully!");
        loadAgent();
      } else {
        alert("Failed to approve agent");
      }
    } catch (error) {
      alert("Error approving agent");
    } finally {
      setActionLoading(false);
    }
  };

  const rejectAgent = async () => {
    const reason = prompt("Reason for rejection:");
    if (!reason) return;

    const token = localStorage.getItem("admin_token");
    setActionLoading(true);

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/agents/${agentId}/reject`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ reason }),
        }
      );

      if (response.ok) {
        alert("Agent rejected");
        loadAgent();
      } else {
        alert("Failed to reject agent");
      }
    } catch (error) {
      alert("Error rejecting agent");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !agent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  const stats = agent.stats || {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {agent.user?.name || "Agent Details"}
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                {agent.user?.email} • {agent.agent.referral_code}
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard/agents")}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
            >
              ← Back to Agents
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Action Buttons */}
        {agent.agent.status === "pending" && (
          <div className="mb-6 flex gap-4">
            <button
              onClick={approveAgent}
              disabled={actionLoading}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              ✓ Approve Agent
            </button>
            <button
              onClick={rejectAgent}
              disabled={actionLoading}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              ✗ Reject Agent
            </button>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Total Sales", value: `$${stats.total_sales?.toFixed(0) || 0}` },
            { label: "Monthly Sales", value: `$${stats.monthly_sales?.toFixed(0) || 0}` },
            { label: "Total Commissions", value: `$${stats.total_commissions?.toFixed(0) || 0}` },
            { label: "Tier", value: agent.agent.tier?.toUpperCase() || "BRONZE" },
          ].map((stat, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">{stat.label}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Agent Info */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Agent Information</h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-500">Status</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {agent.agent.status}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Country</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {agent.agent.country}
                  {agent.agent.is_country_manager && (
                    <span className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                      Country Manager
                    </span>
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Demo Scans</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {agent.agent.demo_scans_remaining} remaining
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Customers Referred</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {stats.total_customers || 0}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Sub-Agents</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {stats.sub_agents || 0}
                </dd>
              </div>
            </dl>
          </div>

          {/* Commission Breakdown */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Commission Breakdown
            </h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-500">Pending</dt>
                <dd className="text-sm font-medium text-yellow-600 mt-1">
                  ${stats.pending_commissions?.toFixed(2) || "0.00"}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Paid</dt>
                <dd className="text-sm font-medium text-green-600 mt-1">
                  ${stats.paid_commissions?.toFixed(2) || "0.00"}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Commission Rate</dt>
                <dd className="text-sm font-medium text-gray-900 mt-1">
                  {(stats.commission_rate * 100).toFixed(0)}%
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Recent Commissions */}
        <div className="mt-6 bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Commissions
          </h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Amount
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Type
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {agent.recent_commissions?.map((commission: any) => (
                  <tr key={commission.id}>
                    <td className="px-4 py-2 text-sm text-gray-900">
                      ${commission.amount.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {commission.type}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          commission.status === "paid"
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {commission.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-600">
                      {new Date(commission.created_at).toLocaleDateString()}
                    </td>
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
