"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface LeaderboardEntry {
  rank: number;
  agent: {
    id: string;
    referral_code: string;
    user: { id: string; name: string; email: string };
    country: string;
    tier: string;
    is_country_manager: boolean;
  };
  metric_value: number;
  total_sales: number;
  total_commissions: number;
  total_customers: number;
  sub_agents: number;
}

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState("this_month");
  const [metric, setMetric] = useState("sales");
  const router = useRouter();

  useEffect(() => {
    loadLeaderboard();
  }, [period, metric]);

  const loadLeaderboard = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/agents/leaderboard?period=${period}&metric=${metric}&limit=20`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error("Failed to load leaderboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const getTierBadge = (tier: string) => {
    const badges: Record<string, { color: string; emoji: string }> = {
      bronze: { color: "bg-orange-100 text-orange-800", emoji: "🥉" },
      silver: { color: "bg-gray-100 text-gray-800", emoji: "🥈" },
      gold: { color: "bg-yellow-100 text-yellow-800", emoji: "🥇" },
    };
    return badges[tier] || badges.bronze;
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return `#${rank}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading leaderboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🏆 Agent Leaderboard
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Top performing agents by {metric === "sales" ? "sales" : "commissions earned"}
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
        {/* Filters */}
        <div className="mb-6 flex gap-4">
          {/* Period Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-2">
              TIME PERIOD
            </label>
            <div className="flex gap-2">
              {[
                { value: "this_week", label: "This Week" },
                { value: "this_month", label: "This Month" },
                { value: "all_time", label: "All Time" },
              ].map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPeriod(p.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    period === p.value
                      ? "bg-blue-600 text-white"
                      : "bg-white text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Metric Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-2">
              METRIC
            </label>
            <div className="flex gap-2">
              {[
                { value: "sales", label: "Sales" },
                { value: "commissions", label: "Commissions" },
              ].map((m) => (
                <button
                  key={m.value}
                  onClick={() => setMetric(m.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    metric === m.value
                      ? "bg-purple-600 text-white"
                      : "bg-white text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Top 3 Podium */}
        {leaderboard.length >= 3 && (
          <div className="mb-8 grid grid-cols-3 gap-4">
            {/* 2nd Place */}
            <div className="bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl p-6 text-center transform translate-y-4">
              <div className="text-4xl mb-2">🥈</div>
              <div className="text-sm text-gray-600 mb-1">2nd Place</div>
              <div className="font-bold text-gray-900 text-lg mb-1">
                {leaderboard[1].agent.user.name}
              </div>
              <div className="text-2xl font-bold text-gray-700">
                ${leaderboard[1].metric_value.toFixed(0)}
              </div>
              <div className="text-xs text-gray-500 mt-2">
                {leaderboard[1].total_customers} customers
              </div>
            </div>

            {/* 1st Place */}
            <div className="bg-gradient-to-br from-yellow-100 to-yellow-300 rounded-xl p-6 text-center transform -translate-y-2">
              <div className="text-5xl mb-2">🥇</div>
              <div className="text-sm text-yellow-800 mb-1">1st Place</div>
              <div className="font-bold text-gray-900 text-xl mb-1">
                {leaderboard[0].agent.user.name}
              </div>
              <div className="text-3xl font-bold text-yellow-900">
                ${leaderboard[0].metric_value.toFixed(0)}
              </div>
              <div className="text-xs text-yellow-800 mt-2">
                {leaderboard[0].total_customers} customers
              </div>
              {leaderboard[0].agent.is_country_manager && (
                <div className="mt-2 text-xs bg-yellow-200 text-yellow-900 px-2 py-1 rounded">
                  👑 Country Manager
                </div>
              )}
            </div>

            {/* 3rd Place */}
            <div className="bg-gradient-to-br from-orange-100 to-orange-200 rounded-xl p-6 text-center transform translate-y-4">
              <div className="text-4xl mb-2">🥉</div>
              <div className="text-sm text-orange-700 mb-1">3rd Place</div>
              <div className="font-bold text-gray-900 text-lg mb-1">
                {leaderboard[2].agent.user.name}
              </div>
              <div className="text-2xl font-bold text-orange-700">
                ${leaderboard[2].metric_value.toFixed(0)}
              </div>
              <div className="text-xs text-orange-600 mt-2">
                {leaderboard[2].total_customers} customers
              </div>
            </div>
          </div>
        )}

        {/* Full Leaderboard Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Agent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Country
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Tier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    {metric === "sales" ? "Sales" : "Commissions"}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Customers
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Sub-Agents
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leaderboard.map((entry) => {
                  const tierBadge = getTierBadge(entry.agent.tier);
                  const isTopThree = entry.rank <= 3;

                  return (
                    <tr
                      key={entry.rank}
                      className={`hover:bg-gray-50 ${
                        isTopThree ? "bg-blue-50" : ""
                      }`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-2xl font-bold text-gray-700">
                          {getRankBadge(entry.rank)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                            {entry.agent.user.name}
                            {entry.agent.is_country_manager && (
                              <span className="text-xs">👑</span>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">
                            {entry.agent.user.email}
                          </div>
                          <div className="text-xs text-blue-600 font-mono">
                            {entry.agent.referral_code}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.agent.country}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${tierBadge.color}`}
                        >
                          {tierBadge.emoji} {entry.agent.tier}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-bold text-gray-900">
                          ${entry.metric_value.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-500">
                          Total: ${entry.total_sales.toFixed(0)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.total_customers}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.sub_agents}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {leaderboard.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No agents to display</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
