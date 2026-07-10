import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Reachlytics",
  description: "Agent-based virality prediction simulator for product demo videos"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
