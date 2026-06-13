/**
 * Mock API client for testing without backend
 */

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

export class MockAPIClient {
  /**
   * Check a website URL for security issues
   */
  static async checkURL(url: string): Promise<CheckResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    const score = Math.floor(Math.random() * 30) + 70; // 70-100
    const risk_level = score >= 80 ? 'low' : score >= 60 ? 'medium' : 'high';

    return {
      id: `check_${Date.now()}`,
      input_type: 'url',
      input_value: url,
      score,
      risk_level,
      summary: `This website has a trust score of ${score}/100.`,
      red_flags: score < 80 ? [
        {
          severity: 'medium',
          category: 'security_headers',
          message: 'Missing security headers',
          evidence: 'HSTS header not found'
        }
      ] : [],
      ai_explanation: `Analysis complete. The website "${url}" has ${score >= 80 ? 'good' : 'moderate'} security indicators. SSL certificate is valid, domain age is acceptable, and no major red flags detected.`,
      safety_advice: score >= 80
        ? 'This site appears legitimate. Always verify you\'re on the correct URL before entering sensitive information.'
        : 'Exercise caution. Verify this is the legitimate website before sharing personal information.',
      created_at: new Date().toISOString(),
    };
  }

  /**
   * Verify a photo for AI generation
   */
  static async verifyPhoto(imageUrl?: string, imageBase64?: string): Promise<AIVerifyResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2500));

    const is_ai_generated = Math.random() > 0.8; // 20% chance AI-generated
    const authenticity_score = is_ai_generated ? Math.floor(Math.random() * 30) + 30 : Math.floor(Math.random() * 20) + 80;
    const confidence = is_ai_generated ? 0.85 : 0.92;

    return {
      id: `ver_photo_${Date.now()}`,
      verification_type: 'photo',
      is_ai_generated,
      confidence,
      authenticity_score,
      risk_level: authenticity_score >= 80 ? 'low' : authenticity_score >= 60 ? 'medium' : 'high',
      deepfake_detected: is_ai_generated,
      manipulation_detected: is_ai_generated,
      analysis: {
        metadata_analysis: {
          exif_present: !is_ai_generated,
          camera_model: !is_ai_generated ? 'Detected' : 'None',
          creation_date_consistent: !is_ai_generated,
        },
        pixel_analysis: {
          compression_artifacts: is_ai_generated ? 'Suspicious' : 'Normal',
          noise_patterns: is_ai_generated ? 'Synthetic' : 'Authentic',
        },
        gan_fingerprint: {
          detected: is_ai_generated,
          confidence: confidence,
        }
      },
      explanation: is_ai_generated
        ? 'This image shows signs of AI generation. Multiple indicators suggest synthetic content creation including GAN fingerprints and pixel-level artifacts.'
        : 'This image appears to be authentic based on metadata analysis, pixel examination, and deepfake detection. EXIF data is present and consistent.',
      safety_advice: is_ai_generated
        ? '⚠️ Exercise caution. This image may not be authentic. Verify the source before trusting.'
        : '✅ Image shows strong authenticity indicators. Safe to trust with normal verification practices.',
      processing_time_ms: 1850,
      created_at: new Date().toISOString(),
    };
  }

  /**
   * Verify a video for AI generation
   */
  static async verifyVideo(videoUrl?: string, videoBase64?: string): Promise<AIVerifyResponse> {
    // Simulate API delay (longer for video)
    await new Promise(resolve => setTimeout(resolve, 4000));

    const is_ai_generated = Math.random() > 0.85; // 15% chance AI-generated
    const authenticity_score = is_ai_generated ? Math.floor(Math.random() * 30) + 20 : Math.floor(Math.random() * 20) + 80;
    const confidence = is_ai_generated ? 0.88 : 0.91;

    return {
      id: `ver_video_${Date.now()}`,
      verification_type: 'video',
      is_ai_generated,
      confidence,
      authenticity_score,
      risk_level: authenticity_score >= 80 ? 'low' : authenticity_score >= 60 ? 'medium' : 'high',
      deepfake_detected: is_ai_generated,
      manipulation_detected: is_ai_generated,
      analysis: {
        temporal_analysis: {
          frame_consistency: is_ai_generated ? 'Poor' : 'Good',
          motion_patterns: is_ai_generated ? 'Synthetic' : 'Natural',
        },
        facial_analysis: {
          landmark_tracking: is_ai_generated ? 'Inconsistent' : 'Consistent',
          face_swap_indicators: is_ai_generated,
        },
        audio_visual_sync: {
          lip_sync_quality: is_ai_generated ? 'Poor' : 'Excellent',
          sync_anomalies: is_ai_generated,
        },
        frame_analysis: {
          total_frames_analyzed: 1200,
          suspicious_frames: is_ai_generated ? 145 : 0,
        }
      },
      explanation: is_ai_generated
        ? '🚨 This video shows signs of deepfake manipulation. Multiple temporal and facial inconsistencies detected including lip-sync anomalies and unnatural facial landmark tracking.'
        : '✅ Video analysis complete. No AI generation or deepfake manipulation detected. Facial tracking, audio-visual sync, and temporal consistency all indicate authentic content.',
      safety_advice: is_ai_generated
        ? '⛔ High risk of manipulation detected. Do not trust this video without independent verification from official sources.'
        : '✅ Video appears authentic based on comprehensive analysis. Normal verification practices recommended.',
      processing_time_ms: 4250,
      created_at: new Date().toISOString(),
    };
  }

  /**
   * Upload and verify a photo file
   */
  static async uploadPhoto(file: File): Promise<AIVerifyResponse> {
    return this.verifyPhoto(undefined, 'uploaded_file');
  }

  /**
   * Upload and verify a video file
   */
  static async uploadVideo(file: File): Promise<AIVerifyResponse> {
    return this.verifyVideo(undefined, 'uploaded_file');
  }
}
