import { Round } from "@/lib/types";

export function RoundTimeline({ rounds }: { rounds: Round[] }) {
  return (
    <div className="border border-line bg-white p-5 shadow-instrument">
      <p className="text-sm font-bold">Propagation rounds</p>
      <div className="mt-4 grid gap-3 md:grid-cols-5">
        {rounds.map((round) => (
          <div className="border border-line bg-[#fcfbf8] p-3 text-sm" key={round.id}>
            <p className="font-medium">Round {round.round_number}</p>
            <p className="mt-2 tabular-nums text-muted">Active: {round.active_agents}</p>
            <p className="tabular-nums text-muted">New reach: {round.new_reach}</p>
            <p className="tabular-nums text-muted">Shares: {round.shares}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
