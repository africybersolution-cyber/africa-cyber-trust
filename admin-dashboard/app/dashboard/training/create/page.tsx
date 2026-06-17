"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateCoursePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "onboarding",
    difficulty: "beginner",
    content_type: "video",
    video_url: "",
    document_url: "",
    content_html: "",
    duration_minutes: 30,
    is_required: false,
    is_published: false,
    pass_score: null,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem("admin_token");
    if (!token) {
      router.push("/");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        "https://africa-cyber-trust.onrender.com/api/admin/training/courses",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...formData,
            duration_minutes: formData.duration_minutes || null,
            pass_score: formData.pass_score || null,
          }),
        }
      );

      if (response.ok) {
        alert("Course created successfully!");
        router.push("/dashboard/training");
      } else {
        const error = await response.json();
        alert(`Failed to create course: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error creating course");
      console.error(error);
    } finally {
      setLoading(false);
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
                Create Training Course
              </h1>
              <p className="text-gray-500 text-sm mt-1">
                Add a new course for agent training
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard/training")}
              className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
            >
              ← Cancel
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-6">
          {/* Title */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Course Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Introduction to Agent Sales"
            />
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Brief description of what this course covers..."
            />
          </div>

          {/* Category & Difficulty */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                required
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="onboarding">Onboarding</option>
                <option value="sales">Sales</option>
                <option value="compliance">Compliance</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Difficulty *
              </label>
              <select
                required
                value={formData.difficulty}
                onChange={(e) =>
                  setFormData({ ...formData, difficulty: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="beginner">🌱 Beginner</option>
                <option value="intermediate">🌿 Intermediate</option>
                <option value="advanced">🌳 Advanced</option>
              </select>
            </div>
          </div>

          {/* Content Type */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type *
            </label>
            <select
              required
              value={formData.content_type}
              onChange={(e) =>
                setFormData({ ...formData, content_type: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="video">Video</option>
              <option value="document">Document</option>
              <option value="quiz">Quiz</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>

          {/* Video URL (if video content) */}
          {(formData.content_type === "video" ||
            formData.content_type === "mixed") && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Video URL
              </label>
              <input
                type="url"
                value={formData.video_url}
                onChange={(e) =>
                  setFormData({ ...formData, video_url: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="https://youtube.com/watch?v=..."
              />
              <p className="text-xs text-gray-500 mt-1">
                YouTube, Vimeo, or direct video link
              </p>
            </div>
          )}

          {/* Document URL (if document content) */}
          {(formData.content_type === "document" ||
            formData.content_type === "mixed") && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Document URL
              </label>
              <input
                type="url"
                value={formData.document_url}
                onChange={(e) =>
                  setFormData({ ...formData, document_url: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com/document.pdf"
              />
              <p className="text-xs text-gray-500 mt-1">
                Link to PDF, Google Doc, or other document
              </p>
            </div>
          )}

          {/* Content HTML */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Content (HTML)
            </label>
            <textarea
              value={formData.content_html}
              onChange={(e) =>
                setFormData({ ...formData, content_html: e.target.value })
              }
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              placeholder="<p>Additional instructions or content...</p>"
            />
          </div>

          {/* Duration */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (minutes)
            </label>
            <input
              type="number"
              min="1"
              value={formData.duration_minutes}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  duration_minutes: parseInt(e.target.value),
                })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Checkboxes */}
          <div className="mb-6 space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_required}
                onChange={(e) =>
                  setFormData({ ...formData, is_required: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Required course (all agents must complete)
              </span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_published}
                onChange={(e) =>
                  setFormData({ ...formData, is_published: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Publish immediately (make visible to agents)
              </span>
            </label>
          </div>

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Course"}
            </button>
            <button
              type="button"
              onClick={() => router.push("/dashboard/training")}
              className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
