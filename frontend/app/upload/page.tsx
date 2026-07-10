import Link from "next/link";
import { VideoUpload } from "@/components/upload/VideoUpload";

export default function UploadPage() {
  return (
    <main className="min-h-screen px-6 py-6">
      <header className="mx-auto flex max-w-6xl items-center justify-between border-b border-line pb-4">
        <Link href="/dashboard" className="font-extrabold tracking-tight">Reachlytics</Link>
      </header>
      <section className="mx-auto max-w-6xl py-8">
        <p className="text-[11px] font-extrabold uppercase tracking-[0.18em] text-muted">01 Input</p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Upload a product demo</h1>
        <p className="mb-6 mt-2 max-w-2xl text-muted">
          Reachlytics will analyze the demo, generate a synthetic audience, run propagation rounds,
          and create an explainable virality report.
        </p>
        <VideoUpload />
      </section>
    </main>
  );
}
