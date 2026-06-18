"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userData = localStorage.getItem("agent_user");
    const token = localStorage.getItem("agent_token");

    if (!userData || !token) {
      router.push("/");
      return;
    }

    setUser(JSON.parse(userData));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("agent_token");
    localStorage.removeItem("agent_user");
    router.push("/");
  };

  const menuItems = [
    {
      label: "Dashboard",
      icon: "📊",
      path: "/dashboard",
      exact: true,
    },
    {
      label: "Training",
      icon: "🎓",
      path: "/dashboard/training",
    },
    {
      label: "Commissions",
      icon: "💰",
      path: "/dashboard/commissions",
    },
    {
      label: "Payouts",
      icon: "💳",
      path: "/dashboard/payouts",
    },
  ];

  const isActive = (path: string, exact = false) => {
    if (exact) {
      return pathname === path;
    }
    return pathname.startsWith(path);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-gradient-to-b from-blue-900 to-indigo-900 text-white flex flex-col">
        {/* Logo/Header */}
        <div className="p-6 border-b border-blue-800">
          <h1 className="text-xl font-bold">🛡️ ACT Portal</h1>
          {user && (
            <div className="mt-3">
              <p className="text-blue-200 text-sm">{user.name}</p>
              <p className="text-blue-300 text-xs">{user.email}</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-2">
            {menuItems.map((item, idx) => (
              <li key={idx}>
                <a
                  href={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive(item.path, item.exact)
                      ? "bg-white text-blue-900"
                      : "text-blue-100 hover:bg-blue-800"
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-blue-800">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            <span>🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">{children}</div>
    </div>
  );
}
