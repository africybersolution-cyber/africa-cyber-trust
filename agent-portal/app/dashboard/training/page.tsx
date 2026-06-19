"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import DOMPurify from "isomorphic-dompurify";

export default function TrainingPage() {
  const [courses, setCourses] = useState<any[]>([]);
  const [progress, setProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<any>(null);
  const [showCourse, setShowCourse] = useState(false);

  const router = useRouter();

  useEffect(() => {
    loadCourses();
    loadProgress();
  }, []);

  const loadCourses = async () => {
    const token = localStorage.getItem("agent_token");
    if (!token) {
      router.push("/");
      return;
    }

    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agent/training/courses",
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

  const loadProgress = async () => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/agent/training/my-progress",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setProgress(data);
      }
    } catch (error) {
      console.error("Failed to load progress:", error);
    }
  };

  const openCourse = async (courseId: string) => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/agent/training/courses/${courseId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSelectedCourse(data);
        setShowCourse(true);
      }
    } catch (error) {
      console.error("Failed to load course details:", error);
    }
  };

  const startCourse = async (courseId: string) => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/agent/training/courses/${courseId}/start`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        alert("Course started!");
        loadCourses();
        openCourse(courseId);
      }
    } catch (error) {
      console.error("Failed to start course:", error);
    }
  };

  const completeCourse = async (courseId: string) => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(
        `https://africa-cyber-trust.onrender.com/api/agent/training/courses/${courseId}/complete`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(data.message);
        loadCourses();
        loadProgress();
        setShowCourse(false);
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to complete course");
      }
    } catch (error) {
      alert("Error completing course");
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      onboarding: "bg-blue-100 text-blue-800",
      sales: "bg-green-100 text-green-800",
      compliance: "bg-purple-100 text-purple-800",
      advanced: "bg-red-100 text-red-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "bg-green-100 text-green-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      not_started: "bg-gray-100 text-gray-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
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
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">🎓 Training Center</h1>
          <p className="text-gray-500 text-sm mt-1">
            Complete courses to improve your skills
          </p>
        </div>
      </div>

      <div className="px-6 py-8">
        {/* Progress Stats */}
        {progress && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Total Courses</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {progress.total_courses}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {progress.completed}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">In Progress</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">
                {progress.in_progress}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Not Started</p>
              <p className="text-2xl font-bold text-gray-600 mt-1">
                {progress.not_started}
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-4">
              <p className="text-sm text-gray-500">Completion Rate</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {progress.completion_rate}%
              </p>
            </div>
          </div>
        )}

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 text-lg">
                    {course.title}
                  </h3>
                  {course.is_required && (
                    <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                      Required
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {course.description}
                </p>

                <div className="flex items-center gap-2 mb-4">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${getCategoryColor(
                      course.category
                    )}`}
                  >
                    {course.category}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                    {course.difficulty}
                  </span>
                  {course.duration_minutes && (
                    <span className="text-xs text-gray-500">
                      {course.duration_minutes} min
                    </span>
                  )}
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium">
                      {course.completion.progress_percent}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${course.completion.progress_percent}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(
                      course.completion.status
                    )}`}
                  >
                    {course.completion.status.replace("_", " ")}
                  </span>
                  <button
                    onClick={() => openCourse(course.id)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg"
                  >
                    {course.completion.status === "completed"
                      ? "Review"
                      : course.completion.status === "in_progress"
                      ? "Continue"
                      : "Start"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Course Detail Modal */}
      {showCourse && selectedCourse && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedCourse.title}
                </h2>
                <button
                  onClick={() => setShowCourse(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-600 mt-2">{selectedCourse.description}</p>
            </div>

            <div className="p-6">
              {/* Video */}
              {selectedCourse.video_url && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">
                    📹 Video Content
                  </h3>
                  <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                    <a
                      href={selectedCourse.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
                    >
                      Open Video
                    </a>
                  </div>
                </div>
              )}

              {/* Document */}
              {selectedCourse.document_url && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">
                    📄 Document
                  </h3>
                  <a
                    href={selectedCourse.document_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg"
                  >
                    Download Document
                  </a>
                </div>
              )}

              {/* HTML Content */}
              {selectedCourse.content_html && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Content</h3>
                  <div
                    className="prose max-w-none"
                    dangerouslySetInnerHTML={{
                      __html: DOMPurify.sanitize(selectedCourse.content_html),
                    }}
                  />
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                {selectedCourse.completion.status === "not_started" && (
                  <button
                    onClick={() => startCourse(selectedCourse.id)}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg"
                  >
                    Start Course
                  </button>
                )}
                {selectedCourse.completion.status === "in_progress" && (
                  <button
                    onClick={() => completeCourse(selectedCourse.id)}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white rounded-lg"
                  >
                    Mark as Complete
                  </button>
                )}
                {selectedCourse.completion.status === "completed" && (
                  <div className="flex-1 px-6 py-3 bg-green-100 text-green-800 rounded-lg text-center font-medium">
                    ✓ Completed on{" "}
                    {new Date(
                      selectedCourse.completion.completed_at
                    ).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
