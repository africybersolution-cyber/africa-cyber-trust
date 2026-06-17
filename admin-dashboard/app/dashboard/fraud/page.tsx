"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface FraudFlag {
  type: string;
  severity: string;
  details: string;
}

interface FlaggedAgent {
  agent_id: string;
  referral_code: string;
  user: { email: string; name: string };
  flags: FraudFlag[];
  flag_count: number;
  highest_severity: string;
}

export default function FraudDetectionPage() {
  const [scanResult, setScanResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const router = useRouter();

  const runScan = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    setScanning(true);
    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/fraud/scan",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setScanResult(data);
      }
    } catch (error) {
      console.error("Failed to run scan:", error);
    } finally {
      setScanning(false);
    }
  };

  const suspendAgent = async (agentId: string) => {
    const reason = prompt("Reason for suspension:");
    if (!reason) return;

    const token = localStorage.getItem("admin_token");

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/fraud/agent/${agentId}/suspend`,
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
        alert("Agent suspended for fraud");
        runScan(); // Re-scan
      } else {
        alert("Failed to suspend agent");
      }
    } catch (error) {
      alert("Error suspending agent");
    }
  };

  const clearFlags = async (agentId: string) => {
    if (!confirm("Clear fraud flags? This marks the agent as legitimate."))
      return;

    const token = localStorage.getItem("admin_token");

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/fraud/agent/${agentId}/clear`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        alert("Fraud flags cleared");
        runScan(); // Re-scan
      } else {
        alert("Failed to clear flags");
      }
    } catch (error) {
      alert("Error clearing flags");
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: "bg-red-100 text-red-800 border-red-300",
      high: "bg-orange-100 text-orange-800 border-orange-300",
      medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
      low: "bg-blue-100 text-blue-800 border-blue-300",
    };
    return colors[severity] || colors.low;
  };

  const getSeverityBadge = (severity: string) => {
    const badges: Record<string, string> = {
      critical: "🚨",
      high: "⚠️",
      medium: "⚡",
      low: "ℹ️",
    };
    return badges[severity] || "ℹ️";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                🛡️ Fraud Detection
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Scan agents for suspicious activity
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={runScan}
                disabled={scanning}
                className="px-6 py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {scanning ? "Scanning..." : "🔍 Run Scan"}
              </button>
              <button
                onClick={() => router.push("/dashboard/agents")}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                ← Back to Agents
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {!scanResult && !scanning && (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🛡️</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Ready to Scan
            </h2>
            <p className="text-gray-500 mb-6">
              Click "Run Scan" to check all agents for fraudulent activity
            </p>
            <button
              onClick={runScan}
              className="px-8 py-4 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white rounded-lg font-medium text-lg"
            >
              🔍 Start Fraud Scan
            </button>
          </div>
        )}

        {scanning && (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="text-6xl mb-4 animate-pulse">🔍</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Scanning Agents...
            </h2>
            <p className="text-gray-500">
              Checking for duplicate accounts, self-referrals, and suspicious patterns
            </p>
          </div>
        )}

        {scanResult && !scanning && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Agents Scanned</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {scanResult.total_agents_scanned}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Flagged Agents</p>
                <p className="text-2xl font-bold text-red-600 mt-1">
                  {scanResult.flagged_agents}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Total Flags</p>
                <p className="text-2xl font-bold text-orange-600 mt-1">
                  {scanResult.total_flags}
                </p>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-4">
                <p className="text-sm text-gray-500">Clean Agents</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {scanResult.total_agents_scanned - scanResult.flagged_agents}
                </p>
              </div>
            </div>

            {/* Flagged Agents */}
            {scanResult.agents.length > 0 ? (
              <div className="space-y-4">
                {scanResult.agents.map((agent: FlaggedAgent) => (
                  <div
                    key={agent.agent_id}
                    className={`bg-white rounded-xl shadow-sm border-2 ${getSeverityColor(
                      agent.highest_severity
                    )} overflow-hidden`}
                  >
                    {/* Agent Header */}
                    <div className="p-6 border-b border-gray-200">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-3xl">
                              {getSeverityBadge(agent.highest_severity)}
                            </span>
                            <div>
                              <h3 className="text-lg font-bold text-gray-900">
                                {agent.user.name}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {agent.user.email}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <span className="font-mono text-blue-600">
                              {agent.referral_code}
                            </span>
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(
                                agent.highest_severity
                              )}`}
                            >
                              {agent.highest_severity.toUpperCase()} RISK
                            </span>
                            <span className="text-gray-500">
                              {agent.flag_count} flag{agent.flag_count !== 1 ? "s" : ""}
                            </span>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => suspendAgent(agent.agent_id)}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg"
                          >
                            🚫 Suspend
                          </button>
                          <button
                            onClick={() => clearFlags(agent.agent_id)}
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg"
                          >
                            ✓ Clear
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Fraud Flags */}
                    <div className="p-6 bg-gray-50">
                      <h4 className="text-sm font-semibold text-gray-700 mb-3">
                        Fraud Indicators:
                      </h4>
                      <div className="space-y-2">
                        {agent.flags.map((flag, idx) => (
                          <div
                            key={idx}
                            className="bg-white rounded-lg p-4 border border-gray-200"
                          >
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-lg">
                                    {getSeverityBadge(flag.severity)}
                                  </span>
                                  <span className="font-medium text-gray-900">
                                    {flag.type.replace(/_/g, " ").toUpperCase()}
                                  </span>
                                  <span
                                    className={`px-2 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(
                                      flag.severity
                                    )}`}
                                  >
                                    {flag.severity}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600">
                                  {flag.details}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <div className="text-6xl mb-4">✅</div>
                <h2 className="text-xl font-semibold text-green-900 mb-2">
                  All Clear!
                </h2>
                <p className="text-gray-500">
                  No fraudulent activity detected. All {scanResult.total_agents_scanned} agents passed the scan.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
