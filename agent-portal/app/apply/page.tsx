"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ApplyAgentPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [country, setCountry] = useState("");
  const [referralCode, setReferralCode] = useState("");
  const [step, setStep] = useState<"login" | "signup" | "apply">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [token, setToken] = useState("");

  const router = useRouter();

  const africanCountries = [
    { code: "DZ", name: "Algeria" },
    { code: "AO", name: "Angola" },
    { code: "BJ", name: "Benin" },
    { code: "BW", name: "Botswana" },
    { code: "BF", name: "Burkina Faso" },
    { code: "BI", name: "Burundi" },
    { code: "CM", name: "Cameroon" },
    { code: "CV", name: "Cape Verde" },
    { code: "CF", name: "Central African Republic" },
    { code: "TD", name: "Chad" },
    { code: "KM", name: "Comoros" },
    { code: "CG", name: "Congo" },
    { code: "CD", name: "Democratic Republic of Congo" },
    { code: "CI", name: "Côte d'Ivoire" },
    { code: "DJ", name: "Djibouti" },
    { code: "EG", name: "Egypt" },
    { code: "GQ", name: "Equatorial Guinea" },
    { code: "ER", name: "Eritrea" },
    { code: "SZ", name: "Eswatini" },
    { code: "ET", name: "Ethiopia" },
    { code: "GA", name: "Gabon" },
    { code: "GM", name: "Gambia" },
    { code: "GH", name: "Ghana" },
    { code: "GN", name: "Guinea" },
    { code: "GW", name: "Guinea-Bissau" },
    { code: "KE", name: "Kenya" },
    { code: "LS", name: "Lesotho" },
    { code: "LR", name: "Liberia" },
    { code: "LY", name: "Libya" },
    { code: "MG", name: "Madagascar" },
    { code: "MW", name: "Malawi" },
    { code: "ML", name: "Mali" },
    { code: "MR", name: "Mauritania" },
    { code: "MU", name: "Mauritius" },
    { code: "MA", name: "Morocco" },
    { code: "MZ", name: "Mozambique" },
    { code: "NA", name: "Namibia" },
    { code: "NE", name: "Niger" },
    { code: "NG", name: "Nigeria" },
    { code: "RW", name: "Rwanda" },
    { code: "ST", name: "São Tomé and Príncipe" },
    { code: "SN", name: "Senegal" },
    { code: "SC", name: "Seychelles" },
    { code: "SL", name: "Sierra Leone" },
    { code: "SO", name: "Somalia" },
    { code: "ZA", name: "South Africa" },
    { code: "SS", name: "South Sudan" },
    { code: "SD", name: "Sudan" },
    { code: "TZ", name: "Tanzania" },
    { code: "TG", name: "Togo" },
    { code: "TN", name: "Tunisia" },
    { code: "UG", name: "Uganda" },
    { code: "ZM", name: "Zambia" },
    { code: "ZW", name: "Zimbabwe" },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/auth/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setStep("apply");
      } else {
        const error = await response.json();
        setError(error.detail || "Login failed");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/auth/signup",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            password,
            name,
            phone_number: phoneNumber,
          }),
        }
      );

      if (response.ok) {
        alert("Account created successfully! Now complete your agent application.");

        // Auto-login after signup
        const loginResponse = await fetch(
          "https://africa-cyber-trust.onrender.com/api/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          }
        );

        if (loginResponse.ok) {
          const data = await loginResponse.json();
          setToken(data.access_token);
          setStep("apply");
        }
      } else {
        const error = await response.json();
        setError(error.detail || "Signup failed");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agents/apply",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            country,
            parent_referral_code: referralCode || null,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(
          `Application submitted successfully! Your referral code: ${data.referral_code}\n\nAdmin will review and approve your application. You'll receive a WhatsApp notification once approved.`
        );
        router.push("/");
      } else {
        const error = await response.json();
        setError(error.detail || "Application failed");
      }
    } catch (error) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🛡️ Become an Agent
          </h1>
          <p className="text-gray-600">
            Join our network and earn commissions
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {(step === "login" || step === "signup") && (
          <>
            {/* Login/Signup Tabs */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setStep("login")}
                className={`flex-1 py-2 px-4 rounded-lg font-medium ${
                  step === "login"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Login
              </button>
              <button
                onClick={() => setStep("signup")}
                className={`flex-1 py-2 px-4 rounded-lg font-medium ${
                  step === "signup"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Sign Up
              </button>
            </div>

            {step === "login" ? (
              <form onSubmit={handleLogin} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium disabled:opacity-50 transition-all"
                >
                  {loading ? "Logging in..." : "Continue"}
                </button>
              </form>
            ) : (
              <form onSubmit={handleSignup} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number (WhatsApp)
                  </label>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="+250788123456"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Include country code for WhatsApp notifications
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium disabled:opacity-50 transition-all"
                >
                  {loading ? "Creating account..." : "Create Account & Continue"}
                </button>
              </form>
            )}
          </>
        )}

        {step === "apply" && (
          <form onSubmit={handleApply} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Country *
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select your country</option>
                {africanCountries.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Choose the country where you'll operate as an agent
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Referral Code (Optional)
              </label>
              <input
                type="text"
                value={referralCode}
                onChange={(e) => setReferralCode(e.target.value.toUpperCase())}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="AGENT123"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the code of the agent who referred you (for MLM structure)
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg font-medium disabled:opacity-50 transition-all"
            >
              {loading ? "Submitting..." : "Submit Application"}
            </button>
          </form>
        )}

        {/* Footer */}
        <div className="mt-6 text-center">
          <a
            href="/"
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Already an agent? Sign in
          </a>
        </div>
      </div>
    </div>
  );
}
