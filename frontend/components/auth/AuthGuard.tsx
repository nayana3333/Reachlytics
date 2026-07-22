"use client";

import { useAuthGuard } from "@/hooks/useAuthGuard";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const ready = useAuthGuard();

  if (!ready) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-muted">Checking session...</p>
      </main>
    );
  }

  return <>{children}</>;
}
