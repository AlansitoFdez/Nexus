import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

/* IBM Plex replaces Geist for the Fase 6 redesign. Both are static (not
   variable) fonts, so every weight the design actually uses has to be listed
   explicitly — anything not listed here silently falls back to a synthesized
   bold, which looks wrong at the small sizes the mono labels use. */
const plexSans = IBM_Plex_Sans({
  variable: "--font-plex-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Nexus",
  description: "Orquestador multi-agente con LangGraph y MCP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${plexSans.variable} ${plexMono.variable} h-full antialiased`}
    >
      <body className="bg-canvas text-ink flex min-h-full flex-col font-sans text-sm">
        {children}
      </body>
    </html>
  );
}
