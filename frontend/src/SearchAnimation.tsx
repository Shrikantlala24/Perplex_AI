/**
 * SearchAnimation — Remotion composition embedded in the hero.
 * Shows: query typed → web search → AI answer with [1][2][3] citations → sources.
 * No CSS transitions or Tailwind animation classes (forbidden in Remotion).
 * All animation via useCurrentFrame() + interpolate().
 */
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";

// ── Answer segments (alternating text / citation) ─────────────────────────────
const SEGMENTS: Array<{ type: "text" | "cite"; content: string }> = [
  { type: "text", content: "LangChain is an open-source framework for building applications powered by large language models " },
  { type: "cite", content: "1" },
  { type: "text", content: ". It provides a standardized interface for chaining prompts, models, memory, and tools into coherent workflows " },
  { type: "cite", content: "2" },
  { type: "text", content: ". Developers use it to build chatbots, document Q&A systems, and autonomous agents " },
  { type: "cite", content: "3" },
  { type: "text", content: "." },
];

const FULL_TEXT = SEGMENTS.map((s) => (s.type === "text" ? s.content : `[${s.content}]`)).join("");
const TOTAL_CHARS = FULL_TEXT.length;

const QUERY = "What is LangChain?";
const SOURCES = [
  { label: "1", domain: "docs.langchain.com", title: "LangChain Documentation" },
  { label: "2", domain: "github.com/langchain-ai", title: "langchain-ai/langchain" },
  { label: "3", domain: "blog.langchain.dev", title: "Building LLM Apps" },
];

// ── Timing constants (frames at 30 fps) ───────────────────────────────────────
const T = {
  QUERY_START: 5,
  QUERY_END: 50,
  DOTS_START: 58,
  DOTS_END: 95,
  ANSWER_START: 100,
  ANSWER_END: 185,
  SOURCES_START: 175,
  SOURCES_END: 210,
  TOTAL: 240, // loopable
} as const;

// ── Helper: clamp interpolate ─────────────────────────────────────────────────
function lerp(frame: number, from: number, to: number, inMin: number, inMax: number) {
  return interpolate(frame, [inMin, inMax], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
}

// ── Render answer segments up to charCount characters ─────────────────────────
function AnswerSegments({ charCount }: { charCount: number }) {
  let rendered = 0;
  const nodes: React.ReactNode[] = [];

  for (let i = 0; i < SEGMENTS.length; i++) {
    const seg = SEGMENTS[i];
    const citeMark = seg.type === "cite" ? `[${seg.content}]` : seg.content;
    const segLen = citeMark.length;
    const visible = Math.max(0, Math.min(segLen, charCount - rendered));
    rendered += segLen;

    if (visible === 0) break;

    if (seg.type === "cite" && visible === segLen) {
      nodes.push(
        <span
          key={i}
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: 18,
            height: 18,
            borderRadius: 4,
            background: "rgba(108, 111, 255, 0.2)",
            border: "1px solid rgba(108, 111, 255, 0.4)",
            color: "#a5a8ff",
            fontSize: 11,
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: 700,
            margin: "0 2px",
            verticalAlign: "middle",
            lineHeight: 1,
          }}
        >
          {seg.content}
        </span>
      );
    } else if (seg.type === "text") {
      nodes.push(<span key={i}>{seg.content.slice(0, visible)}</span>);
    }

    if (rendered >= charCount) break;
  }

  return <>{nodes}</>;
}

// ── Main composition ──────────────────────────────────────────────────────────
export const SearchAnimation: React.FC = () => {
  const frame = useCurrentFrame();

  // Query typing
  const queryChars = Math.round(
    lerp(frame, 0, QUERY.length, T.QUERY_START, T.QUERY_END)
  );
  const queryText = QUERY.slice(0, queryChars);
  const cursorVisible = frame >= T.QUERY_START && frame < T.ANSWER_START
    ? Math.floor(frame / 14) % 2 === 0 ? 1 : 0
    : 0;

  // Loading dots
  const dotsOpacity = interpolate(
    frame,
    [T.DOTS_START, T.DOTS_START + 6, T.DOTS_END - 6, T.DOTS_END],
    [0, 1, 1, 0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );
  const dot1 = lerp(frame, 0, 1, T.DOTS_START + 5, T.DOTS_START + 18);
  const dot2 = lerp(frame, 0, 1, T.DOTS_START + 18, T.DOTS_START + 31);
  const dot3 = lerp(frame, 0, 1, T.DOTS_START + 31, T.DOTS_START + 44);

  // Answer reveal (by character count)
  const charCount = frame >= T.ANSWER_START
    ? Math.round(lerp(frame, 0, TOTAL_CHARS, T.ANSWER_START, T.ANSWER_END))
    : 0;

  // Sources slide in
  const sourcesY = lerp(frame, 12, 0, T.SOURCES_START, T.SOURCES_END);
  const sourcesOpacity = lerp(frame, 0, 1, T.SOURCES_START, T.SOURCES_END);

  // Global fade-in (starts visible — dark bg shows immediately)
  const globalOpacity = 1;

  return (
    <AbsoluteFill
      style={{
        background: "#17171c",
        fontFamily: "'Inter', 'Space Grotesk', sans-serif",
        padding: 28,
        opacity: globalOpacity,
        boxSizing: "border-box",
      }}
    >
      {/* ── Top bar: status chip ── */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            background: "rgba(0, 212, 100, 0.12)",
            border: "1px solid rgba(0, 212, 100, 0.25)",
            borderRadius: 20,
            padding: "3px 10px",
            fontSize: 11,
            color: "#4ade80",
            fontFamily: "'JetBrains Mono', monospace",
            letterSpacing: "0.04em",
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#4ade80", display: "inline-block" }} />
          LIVE
        </div>
        <span style={{ color: "#75758a", fontSize: 12 }}>Perplex AI — Agent Console</span>
      </div>

      {/* ── Search bar ── */}
      <div
        style={{
          background: "rgba(255,255,255,0.06)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 8,
          padding: "10px 14px",
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 20,
        }}
      >
        {/* search icon SVG */}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#93939f" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <span style={{ color: "#f5f5f5", fontSize: 14, flex: 1 }}>
          {queryText}
          <span style={{ opacity: cursorVisible, color: "#a5a8ff" }}>|</span>
        </span>
      </div>

      {/* ── Loading dots ── */}
      {frame >= T.DOTS_START && frame < T.ANSWER_START + 10 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            marginBottom: 16,
            opacity: dotsOpacity,
          }}
        >
          <span style={{ color: "#75758a", fontSize: 12 }}>Searching the web</span>
          {[dot1, dot2, dot3].map((d, i) => (
            <span
              key={i}
              style={{
                width: 5,
                height: 5,
                borderRadius: "50%",
                background: "#a5a8ff",
                display: "inline-block",
                opacity: d,
              }}
            />
          ))}
        </div>
      )}

      {/* ── Answer ── */}
      {frame >= T.ANSWER_START && (
        <div
          style={{
            color: "#e8eaf6",
            fontSize: 13.5,
            lineHeight: 1.75,
            marginBottom: 18,
            opacity: lerp(frame, 0, 1, T.ANSWER_START, T.ANSWER_START + 8),
          }}
        >
          <AnswerSegments charCount={charCount} />
        </div>
      )}

      {/* ── Sources ── */}
      {frame >= T.SOURCES_START && (
        <div
          style={{
            opacity: sourcesOpacity,
            translate: `0px ${sourcesY}px`,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              marginBottom: 10,
            }}
          >
            {/* globe icon */}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#75758a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
              <path d="M2 12h20" />
            </svg>
            <span style={{ color: "#75758a", fontSize: 11, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.06em", textTransform: "uppercase" }}>
              Sources
            </span>
          </div>
          {SOURCES.map((src, i) => {
            const delay = T.SOURCES_START + i * 8;
            const srcOpacity = lerp(frame, 0, 1, delay, delay + 12);
            const srcY = lerp(frame, 6, 0, delay, delay + 12);
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "7px 10px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.07)",
                  borderRadius: 6,
                  marginBottom: 5,
                  opacity: srcOpacity,
                  translate: `0px ${srcY}px`,
                }}
              >
                <span
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: 4,
                    background: "rgba(108, 111, 255, 0.18)",
                    border: "1px solid rgba(108, 111, 255, 0.3)",
                    color: "#a5a8ff",
                    fontSize: 10,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontWeight: 700,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {src.label}
                </span>
                <div>
                  <div style={{ color: "#e8eaf6", fontSize: 12, fontWeight: 500, lineHeight: 1.3 }}>{src.title}</div>
                  <div style={{ color: "#75758a", fontSize: 11 }}>{src.domain}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};
