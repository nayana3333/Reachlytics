CONTENT_ANALYSIS_PROMPT = """Analyze this product demo transcript for short-form virality.
Return strict JSON only. Do not include markdown or commentary.

JSON shape:
{{
  "hook_score": number from 0 to 1,
  "clarity_score": number from 0 to 1,
  "emotional_appeal_score": number from 0 to 1,
  "shareability_score": number from 0 to 1,
  "audience_fit_score": number from 0 to 1,
  "product_category": string,
  "strengths": array of strings,
  "weaknesses": array of strings,
  "summary": string
}}

Transcript:
{transcript}

Target audience:
{target_audience}
"""

MULTIMODAL_CONTENT_ANALYSIS_PROMPT = """Analyze this product demo for short-form virality.
Use BOTH the transcript and the attached representative video frames. The frames are sampled
from different points in the video, so infer what is actually shown on screen.

Return strict JSON only. Do not include markdown or commentary.

JSON shape:
{{
  "hook_score": number from 0 to 1,
  "clarity_score": number from 0 to 1,
  "emotional_appeal_score": number from 0 to 1,
  "shareability_score": number from 0 to 1,
  "audience_fit_score": number from 0 to 1,
  "product_category": string,
  "visual_description": string,
  "strengths": array of strings,
  "weaknesses": array of strings,
  "summary": string
}}

Transcript:
{transcript}

Target audience:
{target_audience}
"""

PERSONA_GENERATION_PROMPT = """Generate {count} realistic social media personas for:
{target_audience}

Mix approximately 70 percent in-target and 30 percent outside-target.
Return strict JSON only. Do not include markdown or commentary.

JSON shape:
[
  {{
    "name": string,
    "age": integer,
    "location": string,
    "profession": string,
    "interests": array of strings,
    "pain_points": array of strings,
    "content_preferences": array of strings,
    "engagement_tendency": number from 0 to 1,
    "share_probability": number from 0 to 1,
    "skepticism_level": number from 0 to 1,
    "in_target": boolean
  }}
]
"""
