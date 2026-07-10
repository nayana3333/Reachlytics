import { clsx } from "clsx";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-semibold shadow-sm transition disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary"
          ? "bg-accent text-white hover:bg-[#2A2A2A]"
          : "border border-line bg-white text-ink shadow-none hover:border-ink/30 hover:bg-[#F5F5F5]",
        className
      )}
      {...props}
    />
  );
}
