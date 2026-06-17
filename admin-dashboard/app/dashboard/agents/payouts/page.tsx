"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Payout {
  id: string;
  agent: {
    id: string;
    referral_code: string;
    user: { email: string; name: string };
  };
  amount: number;
  currency: string;
  method: string;
  destination: string;
  requested_at: string;
}

export default function PayoutsPage() {
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadPayouts();
  }, []);

  const loadPayouts = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/agents/payouts/pending",
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

  const processPayout = async (payoutId: string, action: "approve" | "reject") => {
    const token = localStorage.getItem("admin_token");

    let txRef = "";
    let reason = "";

    if (action === "approve") {
      txRef = prompt("Transaction reference (from PawaPay/crypto wallet):") || "";
      if (!txRef) {
        alert("Transaction reference is required to approve payout");
        return;
      }
    } else {
      reason = prompt("Reason for rejection:") || "";
      if (!reason) return;
    }

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/agents/payouts/${payoutId}/process`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action,
            transaction_reference: txRef || undefined,
            rejection_reason: reason || undefined,
          }),
        }
      );

      if (response.ok) {
        alert(`Payout ${action}d successfully!`);
        loadPayouts();
      } else {
        alert("Failed to process payout");
      }
    } catch (error) {
      alert("Error processing payout");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading payouts...</div>
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
                Payout Requests
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Process agent commission payouts
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
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <p className="text-sm text-gray-500">Pending Requests</p>
            <p className="text-2xl font-bold text-yellow-600 mt-1">
              {payouts.length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <p className="text-sm text-gray-500">Total Amount (MoMo)</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              $
              {payouts
                .filter((p) => p.method === "mobile_money")
                .reduce((sum, p) => sum + p.amount, 0)
                .toFixed(0)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <p className="text-sm text-gray-500">Total Amount (Crypto)</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              $
              {payouts
                .filter((p) => p.method === "crypto")
                .reduce((sum, p) => sum + p.amount, 0)
                .toFixed(0)}
            </p>
          </div>
        </div>

        {/* Payouts Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Agent
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
                    Requested
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {payouts.map((payout) => (
                  <tr key={payout.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {payout.agent?.user?.name || "Unknown"}
                        </div>
                        <div className="text-sm text-gray-500">
                          {payout.agent?.user?.email || ""}
                        </div>
                        <div className="text-xs text-blue-600 font-mono">
                          {payout.agent?.referral_code}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-gray-900">
                        ${payout.amount.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-500">{payout.currency}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          payout.method === "mobile_money"
                            ? "bg-green-100 text-green-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {payout.method === "mobile_money"
                          ? "Mobile Money"
                          : "Crypto"}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {payout.destination}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(payout.requested_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => processPayout(payout.id, "approve")}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs"
                        >
                          ✓ Pay
                        </button>
                        <button
                          onClick={() => processPayout(payout.id, "reject")}
                          className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-xs"
                        >
                          ✗ Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {payouts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No pending payout requests</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
