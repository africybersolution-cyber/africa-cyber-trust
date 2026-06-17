"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Filters
  const [emailFilter, setEmailFilter] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const router = useRouter();

  useEffect(() => {
    loadUsers();
  }, [emailFilter, roleFilter, statusFilter, page]);

  const loadUsers = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: String(page * pageSize),
        limit: String(pageSize),
      });

      if (emailFilter) params.append("email", emailFilter);
      if (roleFilter) params.append("role", roleFilter);
      if (statusFilter !== "") params.append("is_active", statusFilter);

      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/users/?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setTotal(data.total || 0);
      }
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserDetails = async (userId: string) => {
    const token = localStorage.getItem("admin_token");
    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/users/${userId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSelectedUser(data);
        setShowDetails(true);
      }
    } catch (error) {
      console.error("Failed to load user details:", error);
    }
  };

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    const token = localStorage.getItem("admin_token");
    const reason = prompt(
      `${currentStatus ? "Suspend" : "Activate"} user?\n\nEnter reason:`
    );

    if (!reason) return;

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/users/${userId}/status`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            is_active: !currentStatus,
            reason: reason,
          }),
        }
      );

      if (response.ok) {
        alert(`User ${currentStatus ? "suspended" : "activated"} successfully`);
        loadUsers();
        if (selectedUser?.id === userId) {
          setShowDetails(false);
          setSelectedUser(null);
        }
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error updating user status");
    }
  };

  const grantPlan = async (userId: string) => {
    const token = localStorage.getItem("admin_token");
    const plan = prompt("Enter plan name (starter/professional/enterprise):");
    if (!plan) return;

    const days = prompt("Duration in days:", "30");
    if (!days) return;

    const reason = prompt("Reason for granting plan:");
    if (!reason) return;

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/users/${userId}/grant-plan`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            plan_name: plan,
            duration_days: parseInt(days),
            reason: reason,
          }),
        }
      );

      if (response.ok) {
        alert("Plan granted successfully!");
        loadUserDetails(userId);
      } else {
        const error = await response.json();
        alert(`Failed: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error granting plan");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">👥 User Management</h1>
          <p className="text-gray-500 text-sm mt-1">
            Manage all platform users
          </p>
        </div>
      </div>

      <div className="px-6 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Email
              </label>
              <input
                type="text"
                value={emailFilter}
                onChange={(e) => {
                  setEmailFilter(e.target.value);
                  setPage(0);
                }}
                placeholder="user@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <select
                value={roleFilter}
                onChange={(e) => {
                  setRoleFilter(e.target.value);
                  setPage(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Roles</option>
                <option value="normal_user">Customer</option>
                <option value="agent">Agent</option>
                <option value="support_admin">Support Admin</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value="true">Active</option>
                <option value="false">Suspended</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => {
                  setEmailFilter("");
                  setRoleFilter("");
                  setStatusFilter("");
                  setPage(0);
                }}
                className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="text-sm text-gray-600">
            Showing <span className="font-semibold">{users.length}</span> of{" "}
            <span className="font-semibold">{total}</span> users
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No users found</div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Account Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.name}
                        </div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_agent ? (
                        <div className="flex flex-col gap-1">
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800 w-fit">
                            Agent
                            {user.agent?.tier ? ` · ${user.agent.tier}` : ""}
                          </span>
                          {user.agent?.referral_code && (
                            <span className="text-xs text-gray-500">
                              {user.agent.referral_code}
                              {user.agent?.country
                                ? ` · ${user.agent.country}`
                                : ""}
                              {user.agent?.status &&
                              user.agent.status !== "approved"
                                ? ` · ${user.agent.status}`
                                : ""}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                          {user.role}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.account_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${
                          user.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {user.is_active ? "Active" : "Suspended"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                      <button
                        onClick={() => loadUserDetails(user.id)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        View
                      </button>
                      <button
                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                        className={
                          user.is_active
                            ? "text-red-600 hover:text-red-800"
                            : "text-green-600 hover:text-green-800"
                        }
                      >
                        {user.is_active ? "Suspend" : "Activate"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {total > pageSize && (
          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">
              Page {page + 1} of {Math.ceil(total / pageSize)}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {showDetails && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900">User Details</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">
                  Basic Information
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Name:</span>
                    <p className="font-medium">{selectedUser.name}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Email:</span>
                    <p className="font-medium">{selectedUser.email}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Role:</span>
                    <p className="font-medium">{selectedUser.role}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Account Type:</span>
                    <p className="font-medium">{selectedUser.account_type}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <p
                      className={`font-medium ${
                        selectedUser.is_active
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {selectedUser.is_active ? "Active" : "Suspended"}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Email Verified:</span>
                    <p className="font-medium">
                      {selectedUser.email_verified ? "Yes" : "No"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Subscription Info */}
              {selectedUser.subscription && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">
                    Subscription
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Plan:</span>
                      <p className="font-medium">
                        {selectedUser.subscription.plan_name}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Status:</span>
                      <p className="font-medium">
                        {selectedUser.subscription.status}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Ends At:</span>
                      <p className="font-medium">
                        {new Date(
                          selectedUser.subscription.ends_at
                        ).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Company Info */}
              {selectedUser.company && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Company</h3>
                  <div className="text-sm">
                    <span className="text-gray-500">Name:</span>
                    <p className="font-medium">{selectedUser.company.name}</p>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => grantPlan(selectedUser.id)}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg"
                >
                  Grant Plan
                </button>
                <button
                  onClick={() => {
                    toggleUserStatus(selectedUser.id, selectedUser.is_active);
                  }}
                  className={`flex-1 px-4 py-2 rounded-lg text-white ${
                    selectedUser.is_active
                      ? "bg-red-600 hover:bg-red-700"
                      : "bg-green-600 hover:bg-green-700"
                  }`}
                >
                  {selectedUser.is_active ? "Suspend User" : "Activate User"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
