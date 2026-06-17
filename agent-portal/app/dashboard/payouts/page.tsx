"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function PayoutsPage() {
  const [payouts, setPayouts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showRequestForm, setShowRequestForm] = useState(false);

  // Request form
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState("mobile_money");
  const [destination, setDestination] = useState("");
  const [requesting, setRequesting] = useState(false);

  const router = useRouter();

  useEffect(() => {
    loadPayouts();
    loadStats();
  }, []);

  const loadPayouts = async () => {
    const token = localStorage.getItem("agent_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agents/payouts",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPayouts(data.payouts || []);
      }
    } catch (error) {
      console.error("Failed to load payouts:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agents/me",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data.stats);
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const requestPayout = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem("agent_token");
    setRequesting(true);

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agents/payouts/request",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            amount: parseFloat(amount),
            method,
            destination,
            currency: "USD",
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(data.message);
        setShowRequestForm(false);
        setAmount("");
        setDestination("");
        loadPayouts();
        loadStats();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to request payout");
      }
    } catch (error) {
      alert("Error requesting payout");
    } finally {
      setRequesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">💳 Payouts</h1>
              <p className="text-gray-500 text-sm mt-1">
                Request payouts and view history
              </p>
            </div>
            <button
              onClick={() => setShowRequestForm(true)}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium"
            >
              Request Payout
            </button>
          </div>
        </div>
      </div>

      <div className="px-6 py-8">
        {/* Balance Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Available Balance</p>
              <p className="text-3xl font-bold text-green-600 mt-1">
                ${stats.pending_commissions?.toFixed(2) || "0.00"}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Minimum payout: $50.00
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Total Paid Out</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">
                ${stats.paid_commissions?.toFixed(2) || "0.00"}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <p className="text-sm text-gray-500">Pending Requests</p>
              <p className="text-3xl font-bold text-yellow-600 mt-1">
                {payouts.filter((p) => p.status === "pending").length}
              </p>
            </div>
          </div>
        )}

        {/* Payouts Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="font-semibold text-gray-900">Payout History</h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-gray-500">
              Loading payouts...
            </div>
          ) : payouts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No payout requests yet
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Requested
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Destination
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Processed
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {payouts.map((payout) => (
                  <tr key={payout.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(payout.requested_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                      ${payout.amount.toFixed(2)} {payout.currency}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {payout.method.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-mono">
                      {payout.destination}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          payout.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : payout.status === "pending"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {payout.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {payout.processed_at
                        ? new Date(payout.processed_at).toLocaleDateString()
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Request Payout Modal */}
      {showRequestForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">
                  Request Payout
                </h2>
                <button
                  onClick={() => setShowRequestForm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <form onSubmit={requestPayout} className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount (USD)
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                  min="50"
                  step="0.01"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="50.00"
                />
                <p className="text-xs text-gray-500 mt-1">Minimum: $50.00</p>
                {stats && (
                  <p className="text-xs text-green-600 mt-1">
                    Available: ${stats.pending_commissions?.toFixed(2) || "0.00"}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Method
                </label>
                <select
                  value={method}
                  onChange={(e) => setMethod(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="mobile_money">Mobile Money</option>
                  <option value="crypto">Cryptocurrency</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {method === "mobile_money" ? "Phone Number" : "Wallet Address"}
                </label>
                <input
                  type="text"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder={
                    method === "mobile_money"
                      ? "+250788123456"
                      : "0x..."
                  }
                />
              </div>

              <button
                type="submit"
                disabled={requesting}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {requesting ? "Requesting..." : "Submit Request"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
