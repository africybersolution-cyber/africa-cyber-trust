"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function WhatsAppPage() {
  const [config, setConfig] = useState<any>(null);
  const [testPhone, setTestPhone] = useState("");
  const [testMessage, setTestMessage] = useState(
    "Hello! This is a test message from Africa Cyber Trust admin."
  );
  const [sending, setSending] = useState(false);
  const [bulkSending, setBulkSending] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/whatsapp/config",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error("Failed to load config:", error);
    }
  };

  const sendTest = async () => {
    if (!testPhone || !testMessage) {
      alert("Please enter phone number and message");
      return;
    }

    const token = localStorage.getItem("admin_token");
    setSending(true);

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/whatsapp/test",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            to_number: testPhone,
            message: testMessage,
          }),
        }
      );

      if (response.ok) {
        alert("WhatsApp message sent successfully!");
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error sending message");
    } finally {
      setSending(false);
    }
  };

  const sendBulkNotification = async (type: "monthly" | "training") => {
    if (
      !confirm(
        `Send ${type === "monthly" ? "monthly summaries" : "training reminders"} to all agents? This will send WhatsApp messages to all eligible agents.`
      )
    ) {
      return;
    }

    const token = localStorage.getItem("admin_token");
    setBulkSending(type);

    try {
      const endpoint =
        type === "monthly"
          ? "/api/admin/whatsapp/send-monthly-summaries"
          : "/api/admin/whatsapp/send-training-reminders";

      const response = await fetch(
        `https://africa-cyber-trust.onrender.com${endpoint}`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(`Success! ${data.message}\nSent: ${data.sent}\nFailed: ${data.failed || 0}\nSkipped: ${data.skipped || 0}`);
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error sending bulk notifications");
    } finally {
      setBulkSending(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                📱 WhatsApp Notifications
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Test and manage agent notifications
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Configuration Status */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Configuration Status
          </h2>
          {config ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Provider:</span>
                <span className="text-sm font-medium text-gray-900">
                  {config.provider || "Not configured"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status:</span>
                <span
                  className={`text-sm font-medium ${
                    config.configured ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {config.configured ? "✓ Configured" : "✗ Not Configured"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">From Number:</span>
                <span className="text-sm font-mono text-gray-900">
                  {config.from_number || "N/A"}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Loading...</p>
          )}

          {config && !config.configured && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>WhatsApp not configured.</strong> Set these environment
                variables on Render:
              </p>
              <ul className="text-xs text-yellow-700 mt-2 space-y-1">
                <li>• TWILIO_ACCOUNT_SID</li>
                <li>• TWILIO_AUTH_TOKEN</li>
                <li>• TWILIO_WHATSAPP_NUMBER (optional)</li>
              </ul>
            </div>
          )}
        </div>

        {/* Test Send */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Send Test Message
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                value={testPhone}
                onChange={(e) => setTestPhone(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="+250788123456"
              />
              <p className="text-xs text-gray-500 mt-1">
                Include country code (e.g., +250 for Rwanda)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Message
              </label>
              <textarea
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={sendTest}
              disabled={sending || !config?.configured}
              className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {sending ? "Sending..." : "📤 Send Test Message"}
            </button>
          </div>
        </div>

        {/* Bulk Notifications */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Bulk Notifications
          </h2>
          <p className="text-sm text-gray-600 mb-4">
            Send automated notifications to all eligible agents
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => sendBulkNotification("monthly")}
              disabled={bulkSending !== null || !config?.configured}
              className="px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg font-medium disabled:opacity-50 text-left"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">📊</span>
                <div>
                  <div className="font-semibold">
                    {bulkSending === "monthly"
                      ? "Sending..."
                      : "Send Monthly Summaries"}
                  </div>
                  <div className="text-xs opacity-90">
                    Performance reports to all agents
                  </div>
                </div>
              </div>
            </button>

            <button
              onClick={() => sendBulkNotification("training")}
              disabled={bulkSending !== null || !config?.configured}
              className="px-6 py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white rounded-lg font-medium disabled:opacity-50 text-left"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">📚</span>
                <div>
                  <div className="font-semibold">
                    {bulkSending === "training"
                      ? "Sending..."
                      : "Send Training Reminders"}
                  </div>
                  <div className="text-xs opacity-90">
                    Remind agents of incomplete courses
                  </div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Message Templates */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Available Templates
          </h2>
          {config?.templates && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {config.templates.map((template: string) => (
                <div
                  key={template}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                >
                  <h3 className="font-medium text-gray-900 mb-1">
                    {template.replace(/_/g, " ").toUpperCase()}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {getTemplateDescription(template)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Usage Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">📖 How to Use</h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>
              <strong>1. Test Message:</strong> Enter a phone number and send a
              test message above
            </li>
            <li>
              <strong>2. Automatic Notifications:</strong> Agents receive
              WhatsApp messages automatically when:
              <ul className="ml-6 mt-1 space-y-1">
                <li>• Application approved</li>
                <li>• Commission earned</li>
                <li>• Payout processed</li>
                <li>• Account flagged for fraud</li>
              </ul>
            </li>
            <li>
              <strong>3. Twilio Setup:</strong> If not configured, add
              credentials in Render environment variables
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function getTemplateDescription(template: string): string {
  const descriptions: Record<string, string> = {
    approved: "Sent when agent application is approved",
    commission: "Sent when agent earns a commission",
    payout: "Sent when payout is processed",
    fraud_alert: "Sent when account is flagged",
    monthly_summary: "Sent at end of month with stats",
    training_reminder: "Sent for incomplete required courses",
  };
  return descriptions[template] || "Automated notification";
}
