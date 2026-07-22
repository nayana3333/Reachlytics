"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiFetch } from "@/lib/api";
import { Video, Simulation } from "@/lib/types";

export function VideoUpload() {
  const router = useRouter();
  const [stage, setStage] = useState("Ready");
  const [error, setError] = useState("");
  const isSubmitting = stage !== "Ready";

  async function submit(formData: FormData) {
    setError("");
    setStage("Uploading demo video...");
    try {
      const videoData = new FormData();
      const file = formData.get("video");
      if (file) videoData.append("file", file);
      const video = await apiFetch<Video>("/api/videos/upload", { method: "POST", body: videoData });
      setStage("Creating persona population...");
      const simulation = await apiFetch<Simulation>("/api/simulations", {
        method: "POST",
        body: JSON.stringify({
          video_id: video.id,
          target_audience: formData.get("target_audience"),
          persona_count: Number(formData.get("persona_count")),
          round_count: Number(formData.get("round_count"))
        })
      });
      setStage("Opening report...");
      router.push(`/simulations/${simulation.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setStage("Ready");
    }
  }

  return (
    <form action={submit} className="border border-line bg-white p-6 shadow-instrument">
      <div className="grid gap-5 md:grid-cols-[1fr_1fr]">
        <label className="text-sm font-medium">
          Video
          <Input className="mt-2 pt-2" name="video" required type="file" accept="video/*" disabled={isSubmitting} />
        </label>
        <label className="text-sm font-medium">
          Target audience
          <Input className="mt-2" name="target_audience" required placeholder="Solo founders and small teams running tech businesses" disabled={isSubmitting} />
        </label>
        <label className="text-sm font-medium">
          Population
          <select className="mt-2 h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10" name="persona_count" defaultValue="100" disabled={isSubmitting}>
            <option value="50">50 agents</option>
            <option value="100">100 agents</option>
            <option value="200">200 agents</option>
            <option value="500">500 agents</option>
          </select>
        </label>
        <label className="text-sm font-medium">
          Rounds
          <select className="mt-2 h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/10" name="round_count" defaultValue="5" disabled={isSubmitting}>
            <option value="3">3 rounds</option>
            <option value="5">5 rounds</option>
            <option value="8">8 rounds</option>
            <option value="10">10 rounds</option>
          </select>
        </label>
      </div>
      <div className="mt-6 flex items-center justify-between border-t border-line pt-5">
        <p className="text-sm text-muted">{stage}</p>
        <Button loading={isSubmitting}>{isSubmitting ? "Running..." : "Run report"}</Button>
      </div>
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
    </form>
  );
}
