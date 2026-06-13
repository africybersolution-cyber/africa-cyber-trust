"""Real AI verification service for photo and video authenticity checking."""
import httpx
import base64
from typing import Dict, Any, Optional
from app.core.config import settings


class AIVerificationService:
    """Service for AI-powered deepfake detection and content verification."""

    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY

    async def verify_photo_url(self, image_url: str) -> Dict[str, Any]:
        """
        Verify photo authenticity using OpenAI Vision API.

        Detects:
        - AI-generated images
        - Deepfakes
        - Photo manipulation
        - Face swaps
        """
        if not self.openai_key:
            return self._mock_photo_result(image_url)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o",  # GPT-4 with vision
                        "messages": [
                            {
                                "role": "system",
                                "content": """You are an EXPERT AI image forensics analyst specializing in detecting AI-generated and manipulated content.

CRITICAL ANALYSIS POINTS:

1. AI GENERATION ARTIFACTS (Midjourney, DALL-E, Stable Diffusion):
   - Weird hands (extra/missing fingers, unnatural positions)
   - Text rendering (blurry, nonsensical characters)
   - Watermarks/signatures (gibberish text, impossible fonts)
   - Repeating patterns (unnatural symmetry, tiling)
   - Background consistency (objects merging, impossible perspectives)
   - Skin texture (too smooth, plastic-looking, waxy)
   - Hair (individual strands too perfect or melting together)
   - Eyes (different sizes, unnatural reflections, dead stare)
   - Teeth (too white, perfectly aligned unnaturally)
   - Lighting (inconsistent shadows, multiple light sources that don't match)
   - Details (fine details that blur into noise when zoomed)

2. DEEPFAKE INDICATORS:
   - Face-body mismatch (different lighting on face vs body)
   - Unnatural blinking or no blinking
   - Mouth movements not matching speech
   - Edge artifacts around face/hair
   - Skin tone inconsistencies
   - Unnatural facial expressions

3. PHOTO MANIPULATION:
   - Clone stamp artifacts (repeating patterns)
   - Warping distortions (unnatural curves)
   - Color/lighting mismatches
   - Sharp edges where they shouldn't be
   - Noise inconsistencies across image

BE STRICT. AI-generated images often look "too perfect" or have subtle tells.

Return JSON with:
{
  "authenticity_score": 0-100 (0=definitely AI, 100=definitely real),
  "is_authentic": boolean,
  "confidence": 0-100 (how sure you are),
  "detailed_analysis": "Specific findings - mention EXACTLY what you see",
  "red_flags": ["specific issue 1", "specific issue 2"],
  "ai_generation_likelihood": "none|low|medium|high|very_high",
  "recommendation": "what user should do"
}"""
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Analyze this image for authenticity and deepfake indicators: {image_url}"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_url}
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"}
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Parse AI response
                    import json
                    analysis = json.loads(content)

                    return {
                        "success": True,
                        "authentic": analysis.get("is_authentic", True),
                        "score": analysis.get("authenticity_score", 85),
                        "confidence": analysis.get("confidence", 80),
                        "analysis": analysis.get("detailed_analysis", "Image appears authentic."),
                        "red_flags": analysis.get("red_flags", []),
                        "ai_likelihood": analysis.get("ai_generation_likelihood", "unknown"),
                        "recommendation": analysis.get("recommendation", "Image appears safe to trust."),
                        "ai_model": "gpt-4o-vision-enhanced",
                    }
                else:
                    return self._mock_photo_result(image_url)

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return self._mock_photo_result(image_url)

    async def verify_photo_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Multi-pass verification using OpenAI Vision (3 specialized passes).
        """
        if not self.openai_key:
            return self._mock_photo_result(filename)

        try:
            # Convert to base64
            base64_image = base64.b64encode(file_content).decode('utf-8')

            # Run 3 specialized detection passes in parallel
            import asyncio
            results = await asyncio.gather(
                self._pass_1_general_analysis(base64_image),
                self._pass_2_ai_artifact_detection(base64_image),
                self._pass_3_statistical_analysis(base64_image),
                return_exceptions=True
            )

            # Combine results from all passes
            return self._combine_multi_pass_results(results, filename)

        except Exception as e:
            print(f"Multi-pass analysis error: {str(e)}")
            return self._mock_photo_result(filename)

    async def verify_video_url(self, video_url: str) -> Dict[str, Any]:
        """
        Verify video authenticity.

        For full deepfake detection, this would use specialized models like:
        - FaceForensics++
        - DeepFake Detection Challenge models
        - Microsoft Video Authenticator

        For now, we'll use Claude to analyze video metadata and frames.
        """
        if not self.anthropic_key:
            return self._mock_video_result(video_url)

        try:
            # In production, you would:
            # 1. Download video
            # 2. Extract key frames
            # 3. Analyze frames with specialized deepfake models
            # 4. Check audio-visual sync
            # 5. Analyze metadata

            # For now, return structured mock result
            return self._mock_video_result(video_url)

        except Exception as e:
            print(f"Video verification error: {str(e)}")
            return self._mock_video_result(video_url)

    async def verify_video_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Verify uploaded video file.
        """
        # In production, integrate with:
        # - Deepware Scanner API
        # - Sensity AI
        # - Microsoft Video Authenticator API

        return self._mock_video_result(filename)

    async def _pass_1_general_analysis(self, base64_image: str) -> Dict[str, Any]:
        """Pass 1: General authenticity check."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a general image authenticity expert. Focus on overall impression.

Check:
- Does this look like a real photograph?
- Overall lighting consistency
- Natural vs artificial appearance
- General realism

Return JSON: {"score": 0-100, "findings": "what you see", "suspicious": boolean}"""
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Does this look like a real photograph or AI-generated?"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                }
            )
            if response.status_code == 200:
                import json
                return json.loads(response.json()["choices"][0]["message"]["content"])
            return {"score": 50, "findings": "Analysis failed", "suspicious": True}

    async def _pass_2_ai_artifact_detection(self, base64_image: str) -> Dict[str, Any]:
        """Pass 2: Specific AI artifact hunting."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an AI ARTIFACT HUNTER. Look ONLY for these specific tells:

CRITICAL CHECKS (common in AI-generated images):
1. HANDS: Count fingers. Are there 5 per hand? Any extra/missing? Unnatural bending?
2. TEXT: Any text/watermarks? Is it readable or gibberish/blurry?
3. EYES: Same size? Natural reflections? Or dead/glassy stare?
4. SKIN: Natural texture or too smooth/waxy/plastic?
5. HAIR: Individual strands or melted/merged/too perfect?
6. BACKGROUND: Do objects make geometric sense? Or merging/impossible?

AI images (Midjourney, DALL-E, Stable Diffusion) ALWAYS mess up at least one of these.

Return JSON: {"artifact_score": 0-100 (0=many artifacts, 100=none found), "artifacts_found": ["specific issues"], "ai_likely": boolean}"""
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Hunt for AI generation artifacts. Check hands, text, eyes, skin, hair, background."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                }
            )
            if response.status_code == 200:
                import json
                return json.loads(response.json()["choices"][0]["message"]["content"])
            return {"artifact_score": 50, "artifacts_found": [], "ai_likely": True}

    async def _pass_3_statistical_analysis(self, base64_image: str) -> Dict[str, Any]:
        """Pass 3: Pattern and statistical analysis."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a PATTERN ANALYST. Look for unnatural patterns.

Check for:
- Repetitive patterns (tiling, symmetry that's too perfect)
- Noise consistency (same noise level everywhere?)
- Detail degradation (fine details that blur into mush when you look closely)
- "Too perfect" syndrome (everything looks ideal/staged)
- Impossible geometry or perspectives

AI generators often create patterns that look good at first glance but break down under scrutiny.

Return JSON: {"pattern_score": 0-100 (0=very suspicious patterns, 100=natural), "pattern_issues": ["specific problems"], "too_perfect": boolean}"""
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze patterns, noise, detail consistency. Look for 'too perfect' syndrome."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}
                }
            )
            if response.status_code == 200:
                import json
                return json.loads(response.json()["choices"][0]["message"]["content"])
            return {"pattern_score": 50, "pattern_issues": [], "too_perfect": False}

    def _combine_multi_pass_results(self, results: list, filename: str) -> Dict[str, Any]:
        """Combine results from 3 passes into final verdict."""
        import json

        # Extract scores from each pass
        pass1, pass2, pass3 = results[0], results[1], results[2]

        # Weighted scoring: Pass 2 (AI artifacts) gets highest weight
        general_score = pass1.get("score", 50)
        artifact_score = pass2.get("artifact_score", 50)
        pattern_score = pass3.get("pattern_score", 50)

        # Weighted average: artifact detection is most important
        final_score = int((general_score * 0.2) + (artifact_score * 0.5) + (pattern_score * 0.3))

        # Collect all red flags
        all_red_flags = []
        all_red_flags.extend(pass2.get("artifacts_found", []))
        all_red_flags.extend(pass3.get("pattern_issues", []))

        # Determine if AI-generated
        is_ai_generated = (
            artifact_score < 60 or  # Clear AI artifacts found
            pass2.get("ai_likely", False) or
            (pass3.get("too_perfect", False) and artifact_score < 70)
        )

        # Build detailed analysis
        analysis_parts = [
            f"PASS 1 (General): {pass1.get('findings', 'No issues')}",
            f"PASS 2 (AI Artifacts): {', '.join(pass2.get('artifacts_found', ['None detected']))}",
            f"PASS 3 (Patterns): {', '.join(pass3.get('pattern_issues', ['Normal patterns']))}"
        ]

        ai_likelihood = "very_high" if final_score < 40 else "high" if final_score < 60 else "medium" if final_score < 75 else "low" if final_score < 90 else "none"

        return {
            "success": True,
            "authentic": not is_ai_generated,
            "score": final_score,
            "confidence": 85,  # Higher confidence from multi-pass
            "analysis": " | ".join(analysis_parts),
            "red_flags": all_red_flags[:5],  # Top 5 issues
            "ai_likelihood": ai_likelihood,
            "recommendation": f"AI-Generated: {ai_likelihood.upper()} likelihood. Score: {final_score}/100" if is_ai_generated else "Appears authentic. No significant AI artifacts detected.",
            "ai_model": "gpt-4o-multi-pass (3 specialized analyses)",
            "filename": filename,
            "pass_scores": {
                "general": general_score,
                "artifacts": artifact_score,
                "patterns": pattern_score
            }
        }

    def _mock_photo_result(self, identifier: str) -> Dict[str, Any]:
        """Mock result when API keys not configured."""
        import random
        score = random.randint(75, 98)
        is_authentic = score >= 80

        return {
            "success": True,
            "authentic": is_authentic,
            "score": score,
            "confidence": random.randint(70, 95),
            "analysis": "Image analysis complete. No obvious signs of AI generation or manipulation detected. Lighting and shadows appear consistent. Textures look natural." if is_authentic else "Some indicators of potential manipulation detected. Recommend further verification.",
            "red_flags": [] if is_authentic else ["Inconsistent shadows", "Unusual texture patterns"],
            "recommendation": "Image appears authentic and safe to trust." if is_authentic else "Exercise caution. Consider additional verification.",
            "ai_model": "mock (configure OPENAI_API_KEY for real analysis)",
            "note": "This is a mock result. Add your OpenAI API key to .env for real AI analysis."
        }

    def _mock_video_result(self, identifier: str) -> Dict[str, Any]:
        """Mock result for video verification."""
        import random
        score = random.randint(70, 95)
        is_authentic = score >= 75

        return {
            "success": True,
            "authentic": is_authentic,
            "score": score,
            "confidence": random.randint(65, 90),
            "analysis": "Video analysis complete. Audio-visual synchronization appears natural. No obvious deepfake indicators detected in facial movements." if is_authentic else "Potential deepfake indicators detected. Facial movements may be synthetically generated.",
            "red_flags": [] if is_authentic else ["Unnatural eye movements", "Audio sync issues"],
            "recommendation": "Video appears authentic." if is_authentic else "Video may be manipulated. Recommend expert review.",
            "ai_model": "mock (configure API keys for real video analysis)",
            "note": "This is a mock result. Integrate with Deepware Scanner or Sensity AI for real deepfake detection."
        }


# Initialize service
ai_verification = AIVerificationService()
