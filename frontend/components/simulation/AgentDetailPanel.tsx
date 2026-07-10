import { PersonaDetail } from "@/lib/types";

function score(value: number) {
  return `${Math.round(value * 100)}%`;
}

const profileSeparator = " \u00B7 ";

export function AgentDetailPanel({
  persona,
  onClose
}: {
  persona: PersonaDetail | null;
  onClose: () => void;
}) {
  if (!persona) {
    return (
      <aside className="border border-line bg-white p-5 shadow-instrument">
        <p className="text-sm font-bold">Agent detail</p>
        <p className="mt-3 text-sm text-muted">Click a node to inspect the persona and reaction.</p>
      </aside>
    );
  }

  return (
    <aside className="border border-line bg-white p-5 shadow-instrument">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-bold">{persona.name}</p>
          <p className="mt-1 text-xs text-muted">
            {[persona.age, persona.location, persona.profession].join(profileSeparator)}
          </p>
        </div>
        <button className="text-xs text-muted hover:text-ink" onClick={onClose} type="button">
          Close
        </button>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <div className="border border-line bg-[#fcfbf8] p-2">
          <p className="text-muted">Engage</p>
          <p className="font-semibold tabular-nums">{score(persona.engagement_tendency)}</p>
        </div>
        <div className="border border-line bg-[#fcfbf8] p-2">
          <p className="text-muted">Share</p>
          <p className="font-semibold tabular-nums">{score(persona.share_probability)}</p>
        </div>
        <div className="border border-line bg-[#fcfbf8] p-2">
          <p className="text-muted">Skeptic</p>
          <p className="font-semibold tabular-nums">{score(persona.skepticism_level)}</p>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Action</p>
        <p className="mt-1 text-sm font-semibold capitalize">{persona.action.replace("_", " ")}</p>
      </div>

      <div className="mt-4">
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Reason</p>
        <p className="mt-1 text-sm leading-6">{persona.reason}</p>
      </div>

      <div className="mt-4">
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Interests</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {persona.interests.map((item) => (
            <span className="border border-line bg-[#fcfbf8] px-2 py-1 text-xs" key={item}>{item}</span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">Pain points</p>
        <ul className="mt-2 space-y-1 text-sm text-muted">
          {persona.pain_points.map((item) => <li key={item}>{item}</li>)}
        </ul>
      </div>
    </aside>
  );
}
