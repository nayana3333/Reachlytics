import { MetricCard } from "@/components/ui/MetricCard";
import { Simulation } from "@/lib/types";

function percent(value: number | null) {
  return value === null ? "-" : `${Math.round(value * 100)}%`;
}

function viralityTone(verdict: string | null): "accent" | "warning" | "default" {
  if (verdict === "Viral candidate" || verdict === "Niche hit") return "accent";
  if (verdict === "Low signal" || verdict === "Out-of-target breakout") return "warning";
  return "default";
}

export function MetricsPanel({ simulation }: { simulation: Simulation }) {
  return (
    <div className="grid gap-4 md:grid-cols-5">
      <MetricCard
        label="Virality score"
        value={simulation.virality_score?.toString() ?? "-"}
        tone={viralityTone(simulation.final_verdict)}
      />
      <MetricCard label="Reach" value={simulation.predicted_reach?.toString() ?? "-"} />
      <MetricCard label="Like rate" value={percent(simulation.like_rate)} />
      <MetricCard label="Share rate" value={percent(simulation.share_rate)} />
      <MetricCard label="Cascade depth" value={simulation.cascade_depth?.toString() ?? "-"} />
    </div>
  );
}
