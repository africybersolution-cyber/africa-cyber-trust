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
    const userData = localStorage.getItem("admin_user");
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
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
      label: "Agent Management",
      icon: "👥",
      children: [
        { label: "Manage Agents", path: "/dashboard/agents" },
        { label: "Leaderboard", path: "/dashboard/agents/leaderboard" },
        { label: "Payout Requests", path: "/dashboard/agents/payouts" },
      ],
    },
    {
      label: "Security",
      icon: "🛡️",
      children: [
        { label: "Fraud Detection", path: "/dashboard/fraud" },
      ],
    },
    {
      label: "Training",
      icon: "📚",
      children: [
        { label: "Training Courses", path: "/dashboard/training" },
      ],
    },
    {
      label: "Communications",
      icon: "📱",
      children: [
        { label: "WhatsApp Notifications", path: "/dashboard/whatsapp" },
      ],
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
      <div className="w-64 bg-gray-900 text-white flex flex-col">
        {/* Logo/Header */}
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">Admin Dashboard</h1>
          {user && (
            <div className="mt-3 text-xs">
              <p className="text-gray-400">{user.name}</p>
              <p className="text-gray-500 text-xs">{user.role}</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-2">
            {menuItems.map((item, idx) => (
              <li key={idx}>
                {item.path ? (
                  // Single menu item
                  <a
                    href={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive(item.path, item.exact)
                        ? "bg-blue-600 text-white"
                        : "text-gray-300 hover:bg-gray-800 hover:text-white"
                    }`}
                  >
                    <span className="text-xl">{item.icon}</span>
                    <span className="font-medium">{item.label}</span>
                  </a>
                ) : (
                  // Menu group with children
                  <div>
                    <div className="flex items-center gap-3 px-4 py-2 text-gray-400 text-xs font-semibold uppercase tracking-wider">
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </div>
                    <ul className="mt-1 space-y-1">
                      {item.children?.map((child, childIdx) => (
                        <li key={childIdx}>
                          <a
                            href={child.path}
                            className={`flex items-center px-4 py-2 ml-4 rounded-lg text-sm transition-colors ${
                              isActive(child.path)
                                ? "bg-blue-600 text-white"
                                : "text-gray-300 hover:bg-gray-800 hover:text-white"
                            }`}
                          >
                            {child.label}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-gray-800">
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
      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
    </div>
  );
}
