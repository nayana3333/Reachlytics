-- Reachlytics analytics query pack
-- PostgreSQL examples for portfolio review, product analysis, and decision-science reporting.

-- 1. Simulation run overview: one row per completed run.
SELECT
    s.id AS simulation_id,
    s.created_at,
    s.target_audience,
    s.persona_count,
    s.round_count,
    s.status,
    s.final_verdict,
    s.virality_score,
    s.predicted_reach,
    s.like_rate,
    s.comment_rate,
    s.share_rate,
    s.cascade_depth,
    t.ai_source AS transcript_ai_source,
    ca.ai_source AS content_ai_source,
    s.personas_ai_source,
    s.reasons_ai_source
FROM simulations s
LEFT JOIN transcripts t ON t.video_id = s.video_id
LEFT JOIN content_analyses ca ON ca.video_id = s.video_id
WHERE s.status = 'completed'
ORDER BY s.created_at DESC;

-- 2. Verdict distribution: checks whether outcomes are balanced or concentrated.
SELECT
    s.final_verdict,
    COUNT(*) AS run_count,
    ROUND(AVG(s.virality_score)::numeric, 2) AS avg_virality_score,
    ROUND(AVG(s.predicted_reach)::numeric, 2) AS avg_reach,
    ROUND(AVG(s.share_rate)::numeric, 4) AS avg_share_rate
FROM simulations s
WHERE s.status = 'completed'
GROUP BY s.final_verdict
ORDER BY run_count DESC;

-- 3. Audience-level performance: compare target-audience choices.
SELECT
    s.target_audience,
    COUNT(*) AS runs,
    ROUND(AVG(s.virality_score)::numeric, 2) AS avg_virality_score,
    ROUND(AVG(s.predicted_reach)::numeric, 2) AS avg_reach,
    ROUND(AVG(s.like_rate)::numeric, 4) AS avg_like_rate,
    ROUND(AVG(s.share_rate)::numeric, 4) AS avg_share_rate,
    ROUND(AVG(s.cascade_depth)::numeric, 2) AS avg_cascade_depth
FROM simulations s
WHERE s.status = 'completed'
GROUP BY s.target_audience
HAVING COUNT(*) >= 1
ORDER BY avg_virality_score DESC;

-- 4. Round-by-round propagation funnel.
SELECT
    simulation_id,
    round_number,
    active_agents,
    new_reach,
    likes,
    comments,
    shares,
    ROUND((likes::numeric / NULLIF(new_reach, 0)), 4) AS like_per_new_reach_rate,
    ROUND((shares::numeric / NULLIF(new_reach, 0)), 4) AS share_per_new_reach_rate
FROM simulation_rounds
ORDER BY simulation_id, round_number;

-- 5. Persona behavior breakdown by target fit.
SELECT
    p.in_target,
    COUNT(*) AS reached_personas,
    SUM(CASE WHEN d.watched THEN 1 ELSE 0 END) AS watched,
    SUM(CASE WHEN d.liked THEN 1 ELSE 0 END) AS liked,
    SUM(CASE WHEN d.commented THEN 1 ELSE 0 END) AS commented,
    SUM(CASE WHEN d.shared THEN 1 ELSE 0 END) AS shared,
    ROUND(AVG(p.engagement_tendency)::numeric, 4) AS avg_engagement_tendency,
    ROUND(AVG(p.share_probability)::numeric, 4) AS avg_share_probability,
    ROUND(AVG(p.skepticism_level)::numeric, 4) AS avg_skepticism
FROM personas p
JOIN agent_decisions d ON d.persona_id = p.id
GROUP BY p.in_target
ORDER BY p.in_target DESC;

-- 6. AI-source audit: shows whether reports used live AI or fallback logic.
SELECT
    t.ai_source AS transcript_ai_source,
    ca.ai_source AS content_ai_source,
    s.personas_ai_source,
    s.reasons_ai_source,
    COUNT(*) AS run_count
FROM simulations s
LEFT JOIN transcripts t ON t.video_id = s.video_id
LEFT JOIN content_analyses ca ON ca.video_id = s.video_id
WHERE s.status = 'completed'
GROUP BY
    t.ai_source,
    ca.ai_source,
    s.personas_ai_source,
    s.reasons_ai_source
ORDER BY run_count DESC;

-- 7. Content-quality vs outcome: first-principles diagnostic view.
SELECT
    s.id AS simulation_id,
    ca.hook_score,
    ca.clarity_score,
    ca.emotional_appeal_score,
    ca.shareability_score,
    ca.audience_fit_score,
    s.final_verdict,
    s.virality_score,
    s.predicted_reach,
    s.share_rate
FROM simulations s
JOIN content_analyses ca ON ca.video_id = s.video_id
WHERE s.status = 'completed'
ORDER BY s.virality_score DESC;
