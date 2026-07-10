import { clsx } from "clsx";

export function MetricCard({
  label,
  value,
  tone = "default"
}: {
  label: string;
  value: string;
  tone?: "default" | "accent" | "warning";
}) {
  return (
    <div className="border border-line bg-white p-5 shadow-instrument">
      <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-muted">{label}</p>
      <p
        className={clsx(
          "mt-3 text-3xl font-extrabold tabular-nums tracking-tight",
          tone === "accent" && "text-accent",
          tone === "warning" && "text-warning"
        )}
      >
        {value}
      </p>
    </div>
  );
}
