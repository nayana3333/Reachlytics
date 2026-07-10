"use client";

import Link from "next/link";
import { Simulation } from "@/lib/types";

export function SimulationTable({ simulations }: { simulations: Simulation[] }) {
  return (
    <div className="overflow-x-auto border border-line bg-white shadow-instrument">
      <div className="grid min-w-[760px] grid-cols-[1fr_140px_140px_180px] border-b border-line px-4 py-3 text-[11px] font-bold uppercase tracking-[0.16em] text-muted">
        <span>Audience</span>
        <span>Status</span>
        <span>Score</span>
        <span>Verdict</span>
      </div>
      {simulations.length === 0 ? (
        <p className="p-6 text-sm text-muted">No simulations yet. Upload a demo to create your first report.</p>
      ) : (
        simulations.map((simulation) => (
          <Link
            href={`/simulations/${simulation.id}`}
            className="grid min-w-[760px] grid-cols-[1fr_140px_140px_180px] border-b border-line px-4 py-4 text-sm transition hover:bg-[#f6f5f1]"
            key={simulation.id}
          >
            <span className="truncate pr-4">{simulation.target_audience}</span>
            <span className="capitalize">{simulation.status}</span>
            <span className="tabular-nums font-semibold">{simulation.virality_score ?? "-"}</span>
            <span className="truncate">{simulation.final_verdict ?? "-"}</span>
          </Link>
        ))
      )}
    </div>
  );
}
