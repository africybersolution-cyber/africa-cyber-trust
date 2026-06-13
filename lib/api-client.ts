/**
 * Real API Client for Africa Cyber Trust Infrastructure
 * Connects to Python FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

export class APIClient {
  /**
   * Verify a photo for deepfakes and AI generation
   */
  static async verifyPhoto(imageUrl: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/ai-verify/photo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: imageUrl,
      }),
    });

    if (!response.ok) {
      throw new Error(`Photo verification failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Determine if AI-generated or authentic
    const isAIGenerated = !data.authentic;
    const score = data.confidence;

    // Build red flags
    const redFlags = [];
    if (isAIGenerated) {
      redFlags.push({
        severity: 'high',
        category: 'AI-Generated',
        message: 'This photo appears to be AI-generated',
        evidence: data.analysis || 'AI generation patterns detected'
      });
    }
    if (data.red_flags && data.red_flags.length > 0) {
      data.red_flags.forEach((flag: string) => {
        redFlags.push({
          severity: 'medium',
          category: 'Suspicious Pattern',
          message: flag,
          evidence: 'Detected by AI analysis'
        });
      });
    }

    // Transform to results page format
    return {
      id: `photo-${Date.now()}`,
      input_type: 'photo',
      input_value: imageUrl,
      score: score,
      risk_level: isAIGenerated ? 'high' : 'low',
      summary: isAIGenerated
        ? `🤖 AI-Generated Photo Detected (Confidence: ${score}%)`
        : `✅ Authentic Photo - Created by Human (Confidence: ${score}%)`,
      red_flags: redFlags,
      ai_explanation: data.analysis || 'Photo analysis completed using OpenAI GPT-4 Vision',
      safety_advice: data.recommendation || (isAIGenerated
        ? 'This image appears to be AI-generated. Verify source before trusting.'
        : 'Image appears authentic. Still verify source for important decisions.'),
      created_at: new Date().toISOString(),
      ai_model: data.ai_model,
    };
  }

  /**
   * Verify a video for deepfakes
   */
  static async verifyVideo(videoUrl: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/ai-verify/video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_url: videoUrl,
      }),
    });

    if (!response.ok) {
      throw new Error(`Video verification failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Determine if AI-generated, deepfake, or authentic
    const isAIGenerated = !data.authentic;
    const score = data.confidence;

    // Build red flags
    const redFlags = [];
    if (isAIGenerated) {
      redFlags.push({
        severity: 'critical',
        category: 'AI-Generated / Deepfake',
        message: 'This video appears to be AI-generated or manipulated',
        evidence: data.analysis || 'Deepfake patterns or AI generation detected'
      });
    }
    if (data.red_flags && data.red_flags.length > 0) {
      data.red_flags.forEach((flag: string) => {
        redFlags.push({
          severity: 'high',
          category: 'Manipulation Detected',
          message: flag,
          evidence: 'Detected by AI analysis'
        });
      });
    }

    // Transform to results page format
    return {
      id: `video-${Date.now()}`,
      input_type: 'video',
      input_value: videoUrl,
      score: score,
      risk_level: isAIGenerated ? 'critical' : 'low',
      summary: isAIGenerated
        ? `⚠️ DEEPFAKE / AI-Generated Video Detected (Confidence: ${score}%)`
        : `✅ Authentic Video - Real Human Content (Confidence: ${score}%)`,
      red_flags: redFlags,
      ai_explanation: data.analysis || 'Video analysis completed using OpenAI GPT-4 Vision',
      safety_advice: data.recommendation || (isAIGenerated
        ? '🚨 WARNING: This video may be fake or manipulated. Do not trust without verification from original source.'
        : 'Video appears authentic. However, always verify source for critical decisions.'),
      created_at: new Date().toISOString(),
      ai_model: data.ai_model,
    };
  }

  /**
   * Upload and verify a photo file
   */
  static async uploadPhoto(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/ai-verify/photo/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Photo upload failed: ${response.statusText}`);
    }

    const data = await response.json();

    const isAIGenerated = !data.authentic;
    const score = data.confidence;

    const redFlags = [];
    if (isAIGenerated) {
      redFlags.push({
        severity: 'high',
        category: 'AI-Generated',
        message: 'This photo appears to be AI-generated',
        evidence: data.analysis || 'AI generation patterns detected'
      });
    }

    return {
      id: `photo-${Date.now()}`,
      input_type: 'photo',
      input_value: file.name,
      score: score,
      risk_level: isAIGenerated ? 'high' : 'low',
      summary: isAIGenerated
        ? `🤖 AI-Generated Photo Detected (Confidence: ${score}%)`
        : `✅ Authentic Photo - Created by Human (Confidence: ${score}%)`,
      red_flags: redFlags,
      ai_explanation: data.analysis || 'Photo analysis completed using OpenAI GPT-4 Vision',
      safety_advice: data.recommendation || (isAIGenerated
        ? 'This image appears to be AI-generated. Verify source before trusting.'
        : 'Image appears authentic. Still verify source for important decisions.'),
      created_at: new Date().toISOString(),
      ai_model: data.ai_model,
    };
  }

  /**
   * Upload and verify a video file
   */
  static async uploadVideo(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/ai-verify/video/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Video upload failed: ${response.statusText}`);
    }

    const data = await response.json();

    const isAIGenerated = !data.authentic;
    const score = data.confidence;

    const redFlags = [];
    if (isAIGenerated) {
      redFlags.push({
        severity: 'critical',
        category: 'AI-Generated / Deepfake',
        message: 'This video appears to be AI-generated or manipulated',
        evidence: data.analysis || 'Deepfake patterns detected'
      });
    }

    return {
      id: `video-${Date.now()}`,
      input_type: 'video',
      input_value: file.name,
      score: score,
      risk_level: isAIGenerated ? 'critical' : 'low',
      summary: isAIGenerated
        ? `⚠️ DEEPFAKE / AI-Generated Video Detected (Confidence: ${score}%)`
        : `✅ Authentic Video - Real Human Content (Confidence: ${score}%)`,
      red_flags: redFlags,
      ai_explanation: data.analysis || 'Video analysis completed using OpenAI GPT-4 Vision',
      safety_advice: data.recommendation || (isAIGenerated
        ? '🚨 WARNING: This video may be fake or manipulated. Do not trust without verification.'
        : 'Video appears authentic. However, always verify source for critical decisions.'),
      created_at: new Date().toISOString(),
      ai_model: data.ai_model,
    };
  }

  /**
   * Check a website/URL for security issues
   */
  static async checkURL(url: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/public-check/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: url,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`URL check failed: ${errorData.detail || response.statusText}`);
    }

    const data = await response.json();

    // Return in the format expected by the results page
    return {
      id: data.id || `url-${Date.now()}`,
      input_type: data.input_type || 'website',
      input_value: data.input_value || url,
      score: data.score || 0,
      risk_level: data.risk_level || 'unknown',
      summary: data.summary || 'Security scan complete',
      red_flags: data.red_flags || [],
      ai_explanation: data.ai_explanation || 'Analysis completed',
      safety_advice: data.safety_advice || 'Exercise normal caution',
      created_at: data.created_at || new Date().toISOString(),
    };
  }

  /**
   * Check backend health
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/`, {
        method: 'GET',
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}
