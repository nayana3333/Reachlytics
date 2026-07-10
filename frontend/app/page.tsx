import Link from "next/link";
import { ArrowRight, LucideIcon, Network, ShieldCheck, Workflow } from "lucide-react";

const features: [string, string, LucideIcon][] = [
  ["Persona engine", "LLM-ready synthetic personas with interests, pain points, and behavior scores.", Network],
  ["Background jobs", "Video analysis and simulations run asynchronously with Redis and Celery.", Workflow],
  ["Production shape", "JWT auth, PostgreSQL persistence, typed APIs, tests, Docker, and Swagger docs.", ShieldCheck]
];

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <nav className="flex items-center justify-between border-b border-line px-6 py-4">
        <div className="text-lg font-extrabold tracking-tight">Reachlytics</div>
        <div className="flex items-center gap-3 text-sm">
          <Link className="font-medium text-muted hover:text-ink" href="/login">Login</Link>
          <Link className="rounded-md bg-accent px-4 py-2 font-semibold text-white shadow-sm hover:bg-[#2A2A2A]" href="/register">
            Start
          </Link>
        </div>
      </nav>
      <section className="mx-auto grid max-w-6xl gap-10 px-6 py-16 lg:grid-cols-[1fr_460px]">
        <div>
          <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-muted">AI + graph simulation</p>
          <h1 className="mt-4 max-w-3xl text-5xl font-extrabold leading-[1.04] tracking-tight">
            Predict how product demos spread across synthetic social audiences.
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-muted">
            Upload a demo, define your target audience, and run an agent-based virality
            simulation with personas, propagation rounds, graph analytics, and an explainable
            verdict.
          </p>
          <Link
            href="/register"
            className="mt-8 inline-flex items-center gap-2 rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white shadow-sm hover:bg-[#2A2A2A]"
          >
            Build a report <ArrowRight size={16} />
          </Link>
        </div>
        <div className="border border-line bg-white p-5 shadow-instrument">
          <div className="border-b border-line pb-4 text-sm font-bold">Simulation preview</div>
          <div className="graph-stage mt-5 h-64 border border-line p-6">
            <div className="relative h-full">
              {Array.from({ length: 32 }).map((_, index) => (
                <span
                  key={index}
                  className={`absolute h-3 w-3 rounded-full ${
                    index % 9 === 0 ? "bg-outside" : index % 3 === 0 ? "bg-target" : "bg-skipped"
                  }`}
                  style={{ left: `${(index * 29) % 92}%`, top: `${(index * 47) % 88}%` }}
                />
              ))}
            </div>
          </div>
          <div className="mt-5 grid grid-cols-3 gap-3 text-sm">
            <div><b className="tabular-nums text-accent">73%</b><br /><span className="text-muted">Audience fit</span></div>
            <div><b className="tabular-nums">2.8%</b><br /><span className="text-muted">Share rate</span></div>
            <div><b className="tabular-nums">3</b><br /><span className="text-muted">Rounds</span></div>
          </div>
        </div>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-6 pb-16 md:grid-cols-3">
        {features.map(([title, copy, Icon]) => (
          <div className="border border-line bg-white p-5 shadow-instrument" key={title}>
            <Icon className="text-accent" size={20} />
            <h2 className="mt-4 font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-muted">{copy}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
