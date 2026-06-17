"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  content_type: string;
  duration_minutes: number;
  is_required: boolean;
  is_published: boolean;
  created_at: string;
}

export default function TrainingPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState("all");
  const router = useRouter();

  useEffect(() => {
    loadCourses();
    loadStats();
  }, [categoryFilter]);

  const loadCourses = async () => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const params = new URLSearchParams();
      if (categoryFilter !== "all") {
        params.append("category", categoryFilter);
      }

      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/training/courses?${params}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setCourses(data.courses || []);
      }
    } catch (error) {
      console.error("Failed to load courses:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    const token = localStorage.getItem("admin_token");

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/training/stats",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const deleteCourse = async (courseId: string) => {
    if (!confirm("Delete this course? This action cannot be undone.")) return;

    const token = localStorage.getItem("admin_token");

    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/admin/training/courses/${courseId}`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        alert("Course deleted");
        loadCourses();
        loadStats();
      } else {
        alert("Failed to delete course");
      }
    } catch (error) {
      alert("Error deleting course");
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      onboarding: "bg-blue-100 text-blue-800",
      sales: "bg-green-100 text-green-800",
      compliance: "bg-red-100 text-red-800",
      advanced: "bg-purple-100 text-purple-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  const getDifficultyBadge = (difficulty: string) => {
    const badges: Record<string, string> = {
      beginner: "🌱",
      intermediate: "🌿",
      advanced: "🌳",
    };
    return badges[difficulty] || "🌱";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading courses...</div>
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
                📚 Training Courses
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Manage agent training content
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push("/dashboard/training/create")}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium"
              >
                + Create Course
              </button>
              <button
                onClick={() => router.push("/dashboard")}
                className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Total Courses</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {stats.total_courses}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Published</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {stats.published_courses}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Required</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {stats.required_courses}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Completions</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {stats.total_completions}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">In Progress</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">
                {stats.in_progress}
              </p>
            </div>
          </div>
        )}

        {/* Category Filters */}
        <div className="mb-6 flex gap-2">
          {["all", "onboarding", "sales", "compliance", "advanced"].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                categoryFilter === cat
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {/* Courses Grid */}
        {courses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">
                          {getDifficultyBadge(course.difficulty)}
                        </span>
                        <h3 className="font-bold text-gray-900 text-lg">
                          {course.title}
                        </h3>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {course.description}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap mb-4">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(
                        course.category
                      )}`}
                    >
                      {course.category}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                      {course.content_type}
                    </span>
                    {course.duration_minutes && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                        ⏱️ {course.duration_minutes}min
                      </span>
                    )}
                    {course.is_required && (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                        Required
                      </span>
                    )}
                    {course.is_published ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        ✓ Published
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800">
                        Draft
                      </span>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() =>
                        router.push(`/dashboard/training/${course.id}`)
                      }
                      className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteCourse(course.id)}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              No Courses Yet
            </h2>
            <p className="text-gray-500 mb-6">
              Create your first training course for agents
            </p>
            <button
              onClick={() => router.push("/dashboard/training/create")}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium text-lg"
            >
              + Create Course
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
