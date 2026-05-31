import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentOps Governance Platform",
  description: "Insurance claims agent governance dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

