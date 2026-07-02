import { Player, PlayerRef } from "@remotion/player";
import { useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { SearchAnimation } from "./SearchAnimation";
import { cn } from "@/lib/utils";

/** Wrapper that auto-plays a Remotion Player.
 *  Retries play() until the composition is ready (Remotion v4 loads async). */
function AutoPlayer(props: React.ComponentProps<typeof Player>) {
  const ref = useRef<PlayerRef>(null);
  
  useEffect(() => {
    ref.current?.play();
  }, []);

  useEffect(() => {
    const handleFocus = () => {
      // Seek to frame 0, then play
      ref.current?.seekTo(0);
      ref.current?.play();
    };
    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, []);

  return <Player ref={ref} {...props} />;
}

// ── Icons ─────────────────────────────────────────────────────────────────────
function GithubIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden>
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
  );
}

function ArrowRight({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
      <path d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

// ── Data ──────────────────────────────────────────────────────────────────────
const CAPABILITIES = [
  {
    label: "Real-time web search",
    description:
      "Tavily performs advanced-depth crawls of the live web — not a cached knowledge base. Every answer is grounded in pages indexed minutes ago.",
    link: "How search works",
  },
  {
    label: "AI synthesis",
    description:
      "LangChain orchestrates Gemini 2.0 Flash to distill scattered sources into one coherent, readable answer. No hallucinations — only cited facts.",
    link: "About the model",
  },
  {
    label: "Inline citations",
    description:
      "Every claim carries a numbered source reference [1][2][3] linked back to the original page. Readers can verify and explore further.",
    link: "Citation format",
  },
];

const TECH_STACK = [
  {
    name: "Gemini 2.0 Flash",
    role: "Language Model",
    bullets: ["Multimodal reasoning", "128k context window", "Sub-second latency"],
    chip: "Google DeepMind",
  },
  {
    name: "Tavily",
    role: "Search API",
    bullets: ["Advanced crawl depth", "Live web index", "Structured extraction"],
    chip: "tavily.com",
  },
  {
    name: "LangChain",
    role: "Orchestration",
    bullets: ["Chain composition", "Memory management", "Tool integration"],
    chip: "Open source",
  },
];

const TRUST_NAMES = ["FastAPI", "Streamlit", "Python 3.11", "Bun", "React 19", "Tailwind CSS"];

// ── Component ─────────────────────────────────────────────────────────────────
export function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">

      {/* ══ ANNOUNCEMENT BAR ════════════════════════════════════════════════════ */}
      <div className="announcement-bar">
        <span>
          ✦ Now with{" "}
          <strong>Gemini 2.0 Flash</strong> — search faster, cite better.{" "}
          <a
            href="https://github.com/Shrikantlala24"
            target="_blank"
            rel="noreferrer"
            className="underline underline-offset-2 ml-1 hover:text-gray-300 transition-colors"
          >
            View on GitHub →
          </a>
        </span>
      </div>

      {/* ══ NAV ═════════════════════════════════════════════════════════════════ */}
      <header className="sticky top-0 z-50 border-b border-[#d9d9dd] bg-white/95 backdrop-blur-sm">
        <nav className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="size-7 rounded bg-[#17171c] flex items-center justify-center shrink-0">
              <svg viewBox="0 0 24 24" fill="white" className="size-4" aria-hidden>
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
              </svg>
            </div>
            <span className="font-display font-semibold text-base text-[#17171c] tracking-tight">
              Perplex AI
            </span>
          </div>

          {/* Center links */}
          <div className="hidden md:flex items-center gap-7 text-sm text-[#616161]">
            {["How it works", "Tech stack", "Docs", "Blog"].map((l) => (
              <a key={l} href="#" className="hover:text-[#17171c] transition-colors">
                {l}
              </a>
            ))}
          </div>

          {/* CTA */}
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/Shrikantlala24"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:flex items-center gap-1.5 text-sm text-[#616161] hover:text-[#17171c] transition-colors"
            >
              <GithubIcon className="size-4" />
              GitHub
            </a>
            <button className="btn-pill" style={{ padding: "8px 18px", fontSize: 13 }}>
              Get started
            </button>
          </div>
        </nav>
      </header>

      {/* ══ HERO ════════════════════════════════════════════════════════════════ */}
      <section className="bg-white pt-20 pb-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1fr_1.15fr] gap-12 items-start">

            {/* Left: headline + copy + CTAs */}
            <div className="flex flex-col gap-7 pt-4">
              {/* Coral chip */}
              <div className="inline-flex w-fit">
                <span className="chip-coral">
                  <span className="size-1.5 rounded-full bg-[#ff7759] inline-block" />
                  Alpha release
                </span>
              </div>

              {/* Headline */}
              <div>
                <h1
                  className="font-display font-normal leading-none text-[#17171c]"
                  style={{ fontSize: "clamp(52px, 6vw, 80px)", letterSpacing: "-0.03em" }}
                >
                  Search.{" "}
                  <span className="text-[#003c33]">Synthesize.</span>{" "}
                  Cite.
                </h1>
              </div>

              <p className="text-[#616161] text-lg leading-relaxed max-w-md">
                Ask anything. Get a cited, AI-synthesized answer drawn from live
                web sources — not guesses, not stale knowledge.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-5">
                <button className="btn-pill" style={{ padding: "12px 28px" }}>
                  Try it free
                  <ArrowRight className="size-4" />
                </button>
                <button className="btn-text-link flex items-center gap-1.5">
                  <GithubIcon className="size-4 opacity-60" />
                  View source
                </button>
              </div>

              {/* Mini trust signals */}
              <div className="flex flex-col gap-2 pt-2">
                {["Open source — MIT license", "Self-hostable in minutes", "No account required"].map((t) => (
                  <div key={t} className="flex items-center gap-2 text-sm text-[#93939f]">
                    <CheckIcon className="size-3.5 text-[#003c33] shrink-0" />
                    {t}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Remotion hero card */}
            <div className="flex flex-col gap-4">
              {/* Main: agent console animation */}
              <div className="hero-card border border-[#e5e7eb] overflow-hidden shadow-sm">
                <AutoPlayer
                  component={SearchAnimation}
                  durationInFrames={240}
                  fps={30}
                  compositionWidth={720}
                  compositionHeight={600}
                  style={{ width: "100%", display: "block" }}
                  loop
                  playbackRate={1}  // ← Ensure normal speed
                  initiallyShowControls={false}
                  controls={false}
                  clickToPlay={false}
                />
              </div>

              {/* Sub-card: "as featured in" style mini-card */}
              <div className="bg-[#eeece7] rounded-xl p-5 flex items-center justify-between">
                <div>
                  <p className="mono-label mb-1">Built with</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {["Gemini", "Tavily", "LangChain"].map((t) => (
                      <span
                        key={t}
                        className="text-xs font-medium px-3 py-1 rounded-full bg-white border border-[#d9d9dd] text-[#212121]"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-display text-3xl font-semibold text-[#003c33] leading-none">3</div>
                  <div className="text-xs text-[#93939f] mt-1">core APIs</div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ══ TRUST LOGO STRIP ════════════════════════════════════════════════════ */}
      <section className="bg-white border-y border-[#d9d9dd] py-10 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <p className="mono-label mb-8">Powered by open-source infrastructure</p>
          <div className="flex flex-wrap justify-center items-center gap-10 md:gap-16">
            {TRUST_NAMES.map((name) => (
              <span key={name} className="trust-logo">{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ══ DARK FEATURE BAND — HOW IT WORKS ═══════════════════════════════════ */}
      <section className="bg-cohere-green px-6 py-24">
        <div className="max-w-6xl mx-auto">
          {/* Heading */}
          <div className="mb-16">
            <p className="mono-label text-[rgba(255,255,255,0.45)] mb-4">How it works</p>
            <h2
              className="font-display font-normal text-white leading-tight"
              style={{ fontSize: "clamp(36px, 4vw, 52px)", letterSpacing: "-0.025em", maxWidth: 560 }}
            >
              Three steps.<br />One cited answer.
            </h2>
          </div>

          {/* Capabilities */}
          <div className="grid md:grid-cols-3 gap-2">
            {CAPABILITIES.map((cap, i) => (
              <div
                key={cap.label}
                className={cn(
                  "capability-card pr-8",
                  i < CAPABILITIES.length - 1 ? "md:border-r md:border-r-[rgba(255,255,255,0.1)]" : "",
                  i > 0 ? "md:pl-8 md:border-t-0" : ""
                )}
              >
                <div className="mono-label text-[rgba(255,255,255,0.4)] mb-4">
                  {String(i + 1).padStart(2, "0")}
                </div>
                <h3 className="text-white text-xl font-display font-normal leading-snug mb-3"
                  style={{ letterSpacing: "-0.01em" }}>
                  {cap.label}
                </h3>
                <p className="text-[rgba(255,255,255,0.6)] text-sm leading-relaxed mb-5">
                  {cap.description}
                </p>
                <a href="#" className="text-sm text-[rgba(255,255,255,0.5)] hover:text-white transition-colors underline underline-offset-3">
                  {cap.link} →
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ PRODUCT / TECH STACK GRID ═══════════════════════════════════════════ */}
      <section className="bg-white px-6 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="mb-14">
            <p className="mono-label mb-3">The stack</p>
            <h2
              className="font-display font-normal text-[#17171c] leading-tight"
              style={{ fontSize: "clamp(32px, 3.5vw, 48px)", letterSpacing: "-0.02em" }}
            >
              Engineered on best-in-class APIs.
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {TECH_STACK.map((tech) => (
              <div key={tech.name} className="product-card flex flex-col gap-5">
                {/* Top */}
                <div>
                  <div className="mono-label mb-2">{tech.role}</div>
                  <h3
                    className="font-display font-semibold text-[#17171c] leading-tight"
                    style={{ fontSize: 22, letterSpacing: "-0.01em" }}
                  >
                    {tech.name}
                  </h3>
                </div>

                {/* Divider */}
                <div className="border-t border-[#d9d9dd]" />

                {/* Bullets */}
                <ul className="flex flex-col gap-2">
                  {tech.bullets.map((b) => (
                    <li key={b} className="flex items-center gap-2.5 text-sm text-[#616161]">
                      <CheckIcon className="size-3.5 text-[#003c33] shrink-0" />
                      {b}
                    </li>
                  ))}
                </ul>

                {/* Chip */}
                <div className="mt-auto pt-2">
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border border-[#d9d9dd] text-[#93939f]">
                    {tech.chip}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ SECONDARY REMOTION FEATURE — "SEE IT LIVE" ══════════════════════════ */}
      <section className="bg-[#eeece7] px-6 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-[1fr_1fr] gap-16 items-center">
            {/* Left: copy */}
            <div>
              <p className="mono-label mb-4">Live demo</p>
              <h2
                className="font-display font-normal text-[#17171c] mb-5 leading-tight"
                style={{ fontSize: "clamp(30px, 3.5vw, 44px)", letterSpacing: "-0.02em" }}
              >
                Watch the AI reason in real time.
              </h2>
              <p className="text-[#616161] text-base leading-relaxed mb-8 max-w-sm">
                The agent console on the right shows a live Perplex AI session — query
                typed, web searched, answer synthesized, citations placed. This is the
                exact output format you get when you run it locally.
              </p>
              <div className="flex flex-col gap-3">
                {[
                  "Queries answered in under 3 seconds",
                  "Every claim linked to a source",
                  "Follow-up questions auto-suggested",
                ].map((feat) => (
                  <div key={feat} className="flex items-center gap-3 text-sm text-[#212121]">
                    <div className="size-1.5 rounded-full bg-[#003c33] shrink-0" />
                    {feat}
                  </div>
                ))}
              </div>
            </div>

            {/* Right: second Remotion Player, slightly different timing offset */}
            <div>
              <div
                className="rounded-[8px] overflow-hidden border border-[#d9d9dd] shadow-sm"
              >
                <AutoPlayer
                  component={SearchAnimation}
                  durationInFrames={240}
                  fps={30}
                  compositionWidth={720}
                  compositionHeight={600}
                  style={{ width: "100%", display: "block" }}
                  loop
                  playbackRate={1}  // ← Ensure normal speed
                  initiallyShowControls={false}
                  controls={false}
                  clickToPlay={false}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══ CTA BAND ════════════════════════════════════════════════════════════ */}
      <section className="bg-[#17171c] px-6 py-28">
        <div className="max-w-3xl mx-auto text-center">
          <p className="mono-label text-[rgba(255,255,255,0.35)] mb-5">Get started</p>
          <h2
            className="font-display font-normal text-white mb-5 leading-tight"
            style={{ fontSize: "clamp(36px, 4.5vw, 60px)", letterSpacing: "-0.03em" }}
          >
            Start searching smarter.
          </h2>
          <p className="text-[rgba(255,255,255,0.55)] text-lg mb-10 max-w-md mx-auto">
            Open source. Run locally in minutes. Bring your own Gemini and Tavily API keys.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="btn-pill btn-pill-white" style={{ padding: "13px 32px" }}>
              Run locally
              <ArrowRight className="size-4" />
            </button>
            <a
              href="https://github.com/Shrikantlala24"
              target="_blank"
              rel="noreferrer"
              className="btn-pill"
              style={{
                padding: "13px 28px",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.15)",
              }}
            >
              <GithubIcon className="size-4" />
              View source
            </a>
          </div>
        </div>
      </section>

      {/* ══ FOOTER ══════════════════════════════════════════════════════════════ */}
      <footer className="footer-dark px-6 pt-16 pb-10">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-[1fr_1fr_1fr_1fr] gap-10 pb-12 border-b border-[rgba(255,255,255,0.08)]">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="size-6 rounded bg-white/10 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="white" className="size-3.5" aria-hidden>
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
                  </svg>
                </div>
                <span className="font-display text-white font-semibold text-sm">Perplex AI</span>
              </div>
              <p className="text-[#93939f] text-xs leading-relaxed max-w-[180px]">
                Search. Synthesize. Cite. Powered by Gemini, Tavily, and LangChain.
              </p>
            </div>

            {/* Links */}
            {[
              { heading: "Product", links: ["How it works", "Tech stack", "API reference", "Changelog"] },
              { heading: "Developers", links: ["GitHub", "Documentation", "Run locally", "Contributing"] },
              { heading: "Company", links: ["About", "Blog", "Contact", "License"] },
            ].map((col) => (
              <div key={col.heading}>
                <p className="text-white text-xs font-medium mb-4 uppercase tracking-wider">{col.heading}</p>
                <ul className="flex flex-col gap-2.5">
                  {col.links.map((l) => (
                    <li key={l}>
                      <a href="#" className="text-[#93939f] text-xs hover:text-white transition-colors">{l}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-8 text-xs text-[#75758a]">
            <span>© 2025 Perplex AI. Open source under MIT License.</span>
            <span>Gemini · Tavily · LangChain · FastAPI · Streamlit</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
