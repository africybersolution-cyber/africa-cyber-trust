/**
 * API client for Africa Cyber Trust Infrastructure
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CheckResponse {
  id: string;
  input_type: string;
  input_value: string;
  score: number;
  risk_level: string;
  summary: string;
  red_flags: any[];
  ai_explanation: string;
  safety_advice: string;
  created_at: string;
}

interface AIVerifyResponse {
  id: string;
  verification_type: string;
  is_ai_generated: boolean;
  confidence: number;
  authenticity_score: number;
  risk_level: string;
  deepfake_detected: boolean;
  manipulation_detected: boolean;
  analysis: any;
  explanation: string;
  safety_advice: string;
  processing_time_ms: number;
  created_at: string;
}

export class APIClient {
  /**
   * Check a website URL for security issues
   */
  static async checkURL(url: string): Promise<CheckResponse> {
    const response = await fetch(`${API_BASE_URL}/api/public-check/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      throw new Error(`Check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Verify a photo for AI generation
   */
  static async verifyPhoto(imageUrl?: string, imageBase64?: string): Promise<AIVerifyResponse> {
    const response = await fetch(`${API_BASE_URL}/api/ai-verify/photo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: imageUrl,
        image_base64: imageBase64,
      }),
    });

    if (!response.ok) {
      throw new Error(`Photo verification failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Verify a video for AI generation
   */
  static async verifyVideo(videoUrl?: string, videoBase64?: string): Promise<AIVerifyResponse> {
    const response = await fetch(`${API_BASE_URL}/api/ai-verify/video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_url: videoUrl,
        video_base64: videoBase64,
      }),
    });

    if (!response.ok) {
      throw new Error(`Video verification failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Upload and verify a photo file
   */
  static async uploadPhoto(file: File): Promise<AIVerifyResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/ai-verify/photo/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Photo upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Upload and verify a video file
   */
  static async uploadVideo(file: File): Promise<AIVerifyResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/ai-verify/video/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Video upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check a company for legitimacy
   */
  static async checkCompany(companyName: string): Promise<CheckResponse> {
    const response = await fetch(`${API_BASE_URL}/api/public-check/company`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_name: companyName }),
    });

    if (!response.ok) {
      throw new Error(`Company check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check a mobile app
   */
  static async checkApp(appIdentifier: string): Promise<CheckResponse> {
    const response = await fetch(`${API_BASE_URL}/api/public-check/app`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ app_identifier: appIdentifier }),
    });

    if (!response.ok) {
      throw new Error(`App check failed: ${response.statusText}`);
    }

    return response.json();
  }
}
