"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { GraphView } from "@/components/simulation/GraphView";
import { MetricsPanel } from "@/components/simulation/MetricsPanel";
import { ReportView } from "@/components/simulation/ReportView";
import { RoundTimeline } from "@/components/simulation/RoundTimeline";
import { Button } from "@/components/ui/Button";
import { apiFetch } from "@/lib/api";
import { GraphEdge, GraphNode, PersonaDetail, Simulation } from "@/lib/types";

type Round = {
  id: string;
  round_number: number;
  active_agents: number;
  new_reach: number;
  likes: number;
  comments: number;
  shares: number;
};

type Report = {
  summary: string;
  improvement_suggestions: string[];
  best_audience_segments: string[];
  risk_factors: string[];
  ml_verdict_prediction: string | null;
  visual_description: string | null;
} | null;

const stageMessages: Record<string, string> = {
  queued: "Waiting to start...",
  starting: "Preparing simulation...",
  transcribing: "Transcribing video audio...",
  analyzing_content: "Analyzing video content...",
  generating_personas: "Creating persona population...",
  simulating_spread: "Running propagation rounds...",
  generating_reasons: "Generating agent explanations...",
  saving_results: "Saving analytics report...",
  generating_report: "Generating final report...",
  completed: "Simulation completed",
  failed: "Simulation failed"
};

function getAiSources(simulation: Simulation | null) {
  if (!simulation) return null;
  return {
    transcript: simulation.transcript_ai_source,
    contentAnalysis: simulation.content_analysis_ai_source,
    personas: simulation.personas_ai_source,
    reasoning: simulation.reasons_ai_source
  };
}

function sourceIsReal(source: string) {
  return source !== "fallback";
}

function providerLabel(values: string[]) {
  const hasGemini = values.some((source) => source.includes("gemini"));
  const hasAnthropic = values.some((source) => source.includes("anthropic"));
  const hasOpenRouter = values.some((source) => source.includes("openrouter"));
  const providerCount = [hasGemini, hasAnthropic, hasOpenRouter].filter(Boolean).length;
  if (providerCount > 1) return "Mixed providers";
  if (hasOpenRouter) return "OpenRouter";
  if (hasGemini) return "Gemini";
  if (hasAnthropic) return "Anthropic/OpenAI";
  return "";
}

function hasVisualInspection(source: string) {
  return source === "real_multimodal" || source.endsWith("_mm");
}

function AiSourceBadge({ simulation }: { simulation: Simulation | null }) {
  const sources = getAiSources(simulation);
  if (!sources) return null;

  const values = Object.values(sources);
  const realCount = values.filter(sourceIsReal).length;
  const provider = providerLabel(values);
  const withVision = hasVisualInspection(sources.contentAnalysis);
  const label =
    withVision && realCount === values.length
      ? `Real AI analysis (${provider ? `${provider} + ` : ""}visual inspection)`
      : realCount === values.length && provider
      ? `Real AI analysis (${provider})`
      : realCount === values.length
      ? "Real AI analysis"
      : realCount === 0
      ? "Fallback estimate"
      : "Partial AI / Fallback estimate";
  const className =
    realCount === values.length
      ? "border-accent/25 bg-accent/10 text-accent"
      : realCount === 0
      ? "border-warning/30 bg-warning/10 text-warning"
      : "border-warning/30 bg-warning/10 text-warning";

  return (
    <details className="group relative">
      <summary className={`cursor-pointer list-none rounded-full border px-3 py-1 text-sm ${className}`}>
        {label}
      </summary>
      <div className="absolute right-0 z-20 mt-2 w-80 border border-line bg-white p-3 text-sm shadow-instrument">
        <p>Transcript: {sources.transcript}</p>
        <p>Content analysis: {sources.contentAnalysis}</p>
        <p>Personas: {sources.personas}</p>
        <p>Reasoning: {sources.reasoning}</p>
      </div>
    </details>
  );
}

export default function SimulationPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [simulation, setSimulation] = useState<Simulation | null>(null);
  const [graph, setGraph] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] }>({ nodes: [], edges: [] });
  const [rounds, setRounds] = useState<Round[]>([]);
  const [report, setReport] = useState<Report>(null);
  const [personas, setPersonas] = useState<PersonaDetail[]>([]);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!id) return;
    async function load() {
      const nextSimulation = await apiFetch<Simulation>(`/api/simulations/${id}`);
      setSimulation(nextSimulation);
      if (nextSimulation.status === "completed") {
        const [nextGraph, nextRounds, nextPersonas, nextReport] = await Promise.all([
          apiFetch<{ nodes: GraphNode[]; edges: GraphEdge[] }>(`/api/simulations/${id}/graph`),
          apiFetch<Round[]>(`/api/simulations/${id}/rounds`),
          apiFetch<PersonaDetail[]>(`/api/simulations/${id}/personas`),
          apiFetch<Report>(`/api/simulations/${id}/report`)
        ]);
        setGraph(nextGraph);
        setRounds(nextRounds);
        setPersonas(nextPersonas);
        setReport(nextReport);
        const artifactsReady =
          Boolean(nextReport) &&
          nextGraph.nodes.length > 0 &&
          nextPersonas.length > 0 &&
          nextRounds.length > 0;
        if (artifactsReady && intervalRef.current !== null) {
          window.clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
      if (nextSimulation.status === "failed") {
        if (intervalRef.current !== null) {
          window.clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    }
    load();
    intervalRef.current = window.setInterval(load, 5000);
    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [id]);

  return (
    <AuthGuard>
    <main className="min-h-screen px-6 py-6">
      <header className="mx-auto flex max-w-7xl items-center justify-between border-b border-line pb-4">
        <Link href="/dashboard" className="font-extrabold tracking-tight">Reachlytics</Link>
        <div className="flex items-center gap-2">
          <Link href="/upload"><Button>New report</Button></Link>
          <LogoutButton />
        </div>
      </header>
      <section className="mx-auto max-w-7xl py-8">
        <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-muted">Run report</p>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">{simulation?.final_verdict ?? "Simulation running"}</h1>
            <p className="mt-2 max-w-3xl text-muted">{simulation?.target_audience}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {simulation?.status === "completed" && <AiSourceBadge simulation={simulation} />}
            <span className="rounded-full border border-accent/25 bg-accent/10 px-3 py-1 text-sm font-medium text-accent">
              {simulation
                ? stageMessages[simulation.progress_stage] ?? simulation.status
                : "Loading..."}
            </span>
          </div>
        </div>
        {simulation?.status === "failed" && simulation.error_message && (
          <div className="mt-4 border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {simulation.error_message}
          </div>
        )}
        {simulation && <div className="mt-6"><MetricsPanel simulation={simulation} /></div>}
        <div className="mt-6">
          <GraphView nodes={graph.nodes} edges={graph.edges} personas={personas} />
        </div>
        <div className="mt-6">
          <RoundTimeline rounds={rounds} />
        </div>
        <div className="mt-6">
          <ReportView
            report={report}
            aiSources={getAiSources(simulation)}
            ruleBasedVerdict={simulation?.final_verdict ?? null}
          />
        </div>
      </section>
    </main>
    </AuthGuard>
  );
}
