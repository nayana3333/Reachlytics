import Link from "next/link";
import { AuthForm } from "@/components/auth/AuthForm";

export default function LoginPage() {
  return (
    <main className="min-h-screen px-6 py-8">
      <Link href="/" className="text-sm font-extrabold tracking-tight">Reachlytics</Link>
      <AuthForm mode="login" />
    </main>
  );
}
