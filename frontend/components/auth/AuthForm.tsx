"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiFetch, setToken } from "@/lib/api";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(formData: FormData) {
    setLoading(true);
    setError("");
    try {
      if (mode === "register") {
        await apiFetch("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({
            name: formData.get("name"),
            email: formData.get("email"),
            password: formData.get("password")
          })
        });
      }
      const token = await apiFetch<{ access_token: string }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: formData.get("email"),
          password: formData.get("password")
        })
      });
      setToken(token.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form action={onSubmit} className="mx-auto mt-12 w-full max-w-sm border border-line bg-white p-6 shadow-instrument">
      <h1 className="text-2xl font-extrabold tracking-tight">{mode === "login" ? "Login" : "Create account"}</h1>
      <p className="mt-2 text-sm text-muted">Access your Reachlytics simulation workspace.</p>
      {mode === "register" && <Input className="mt-6" name="name" placeholder="Name" required />}
      <Input className="mt-4" name="email" placeholder="Email" required type="email" />
      <Input className="mt-4" name="password" placeholder="Password" required type="password" minLength={8} />
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      <Button className="mt-6 w-full" disabled={loading} loading={loading}>
        {loading ? "Working..." : mode === "login" ? "Login" : "Create account"}
      </Button>
      <p className="mt-5 text-center text-sm text-muted">
        {mode === "login" ? (
          <>New here? <a className="font-semibold text-accent hover:underline" href="/register">Create an account</a></>
        ) : (
          <>Already have an account? <a className="font-semibold text-accent hover:underline" href="/login">Login</a></>
        )}
      </p>
    </form>
  );
}
