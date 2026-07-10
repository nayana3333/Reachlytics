"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { MetricCard } from "@/components/ui/MetricCard";
import { SimulationTable } from "@/components/dashboard/SimulationTable";
import { apiFetch } from "@/lib/api";
import { Simulation } from "@/lib/types";

type HealthStatus = {
  queue_backend: "celery" | "inline";
  queue_label?: string;
};

export default function DashboardPage() {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [queueLabel, setQueueLabel] = useState("Checking...");

  useEffect(() => {
    apiFetch<Simulation[]>("/api/simulations").then(setSimulations).catch(() => setSimulations([]));
    apiFetch<HealthStatus>("/health")
      .then((health) => {
        setQueueLabel(
          health.queue_backend === "celery" ? "Celery" : "Inline (Redis not connected)"
        );
      })
      .catch(() => setQueueLabel("Unknown"));
  }, []);

  const completed = simulations.filter((item) => item.status === "completed");
  const avgScore = completed.length
    ? Math.round(completed.reduce((sum, item) => sum + (item.virality_score ?? 0), 0) / completed.length)
    : 0;

  return (
    <main className="min-h-screen px-6 py-6">
      <header className="mx-auto flex max-w-6xl items-center justify-between border-b border-line pb-4">
        <Link href="/" className="font-extrabold tracking-tight">Reachlytics</Link>
        <Link href="/upload"><Button>New report</Button></Link>
      </header>
      <section className="mx-auto max-w-6xl py-8">
        <h1 className="text-3xl font-extrabold tracking-tight">Simulation dashboard</h1>
        <p className="mt-2 text-muted">Track virality reports, spread behavior, and explainable outcomes.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <MetricCard label="Reports" value={String(simulations.length)} />
          <MetricCard label="Completed" value={String(completed.length)} />
          <MetricCard label="Average score" value={String(avgScore)} />
          <MetricCard label="Queue model" value={queueLabel} />
        </div>
        <div className="mt-8">
          <SimulationTable simulations={simulations} />
        </div>
      </section>
    </main>
  );
}
