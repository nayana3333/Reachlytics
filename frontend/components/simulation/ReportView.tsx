import { AiSource, Report } from "@/lib/types";

type AiSourceBreakdown = {
  transcript: AiSource;
  contentAnalysis: AiSource;
  personas: AiSource;
  reasoning: AiSource;
};

function usedFallback(aiSources?: AiSourceBreakdown | null) {
  return Boolean(aiSources && Object.values(aiSources).some((source) => source === "fallback"));
}

export function ReportView({
  report,
  aiSources,
  ruleBasedVerdict
}: {
  report: Report;
  aiSources?: AiSourceBreakdown | null;
  ruleBasedVerdict?: string | null;
}) {
  return (
    <div className="border border-line bg-white p-6 shadow-instrument">
      <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-muted">03 Verdict</p>
      <p className="mt-3 text-lg font-medium leading-7">{report?.summary ?? "Report is still being generated."}</p>
      {report && (
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <div className="border border-line bg-canvas p-4">
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">
              Rule-based verdict (actual)
            </p>
            <p className="mt-2 text-base font-semibold">{ruleBasedVerdict ?? "Unavailable"}</p>
          </div>
          <div className="border border-line bg-canvas p-4">
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">
              ML-predicted verdict (estimated from inputs)
            </p>
            <p className="mt-2 text-base font-semibold">
              {report.ml_verdict_prediction ?? "No trained model available"}
            </p>
          </div>
        </div>
      )}
      {report?.visual_description && (
        <div className="mt-5 border border-line bg-canvas p-4">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">
            What the AI saw in your video
          </p>
          <p className="mt-2 text-sm leading-6 text-ink">{report.visual_description}</p>
        </div>
      )}
      {usedFallback(aiSources) && (
        <p className="mt-4 border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
          Analysis mode: AI-assisted estimate. Some stages used deterministic safeguards when live model output was unavailable.
        </p>
      )}
      <div className="mt-6 grid gap-5 md:grid-cols-3">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Improve</p>
          <ul className="mt-2 space-y-2 text-sm">
            {(report?.improvement_suggestions ?? []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Best segments</p>
          <ul className="mt-2 space-y-2 text-sm">
            {(report?.best_audience_segments ?? []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Risks</p>
          <ul className="mt-2 space-y-2 text-sm">
            {(report?.risk_factors ?? []).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}
