import { clsx } from "clsx";
import { Spinner } from "@/components/ui/Spinner";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
  loading?: boolean;
};

export function Button({ className, variant = "primary", loading = false, disabled, children, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold shadow-sm transition disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary"
          ? "bg-accent text-white hover:bg-[#2A2A2A]"
          : "border border-line bg-white text-ink shadow-none hover:border-ink/30 hover:bg-[#F5F5F5]",
        className
      )}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </button>
  );
}
