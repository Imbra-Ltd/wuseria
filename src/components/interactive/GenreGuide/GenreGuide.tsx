import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import type { Lens } from "../../../types/lens";
import type { ScoredGenre } from "../../../types/genre";
import {
  genreConfigs,
  evScenes,
  genreEvLabels,
  genreSceneFilter,
} from "../../../data/genres";
import { getGenreMark, isEditorialPick } from "../../../utils/scoring";
import { astroExposure, handheldExposure } from "./exposure";
import { ChipGroup } from "../shared/ChipGroup";
import styles from "./GenreGuide.module.css";

// =============================================================================
// PROPS
// =============================================================================

interface GenreGuideProps {
  lenses: Lens[];
  defaultGenre?: ScoredGenre;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const ND_OPTIONS = [
  { label: "ND2", factor: 2 },
  { label: "ND4", factor: 4 },
  { label: "ND8", factor: 8 },
  { label: "ND64", factor: 64 },
  { label: "ND1000", factor: 1000 },
];

const SCORED_GENRES: ScoredGenre[] = [
  "astro", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife", "macro",
];

const FL_CHIPS: Record<string, { label: string; fl: number }[]> = {
  default: [
    { label: "Ultra-wide", fl: 12 },
    { label: "Wide", fl: 24 },
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 135 },
    { label: "Super-tele", fl: 300 },
  ],
  portrait: [
    { label: "Group", fl: 15 },
    { label: "Indoor", fl: 33 },
    { label: "Outdoor", fl: 57 },
  ],
  sportWildlife: [
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 135 },
    { label: "Super-tele", fl: 300 },
  ],
  macro: [
    { label: "Standard", fl: 50 },
    { label: "Tele", fl: 90 },
    { label: "Long macro", fl: 200 },
  ],
};

// FL ranges for filtering — lens must overlap the range to show
const FL_RANGES: Record<number, [number, number]> = {
  6:   [6, 10],
  12:  [6, 18],
  15:  [12, 24],
  24:  [18, 40],
  33:  [24, 45],
  50:  [35, 70],
  57:  [40, 75],
  90:  [60, 120],
  135: [70, 200],
  200: [135, 300],
  300: [200, 600],
};

const GENRE_DEFAULTS: Record<ScoredGenre, { ev: number; iso: number; fl: number }> = {
  astro:        { ev: -7, iso: 1600, fl: 12 },
  landscape:    { ev: 9,  iso: 100,  fl: 24 },
  architecture: { ev: 7,  iso: 200,  fl: 12 },
  street:       { ev: 2,  iso: 6400, fl: 24 },
  travel:       { ev: 11, iso: 400,  fl: 24 },
  portrait:     { ev: 10, iso: 200,  fl: 57 },
  sport:        { ev: 13, iso: 800,  fl: 135 },
  wildlife:     { ev: 9,  iso: 3200, fl: 300 },
  macro:        { ev: 10, iso: 200,  fl: 90 },
};

const GENRE_EQUIPMENT: Record<string, string[]> = {
  astro:        ["Star tracker", "Sturdy tripod", "Lens heater", "Dew shield", "Light pollution filter", "External power bank", "Remote intervalometer", "Bahtinov mask", "Spare batteries", "Red light headlamp"],
  landscape:    ["Sturdy tripod", "Ball head", "L-bracket", "Remote shutter", "Filter set (CPL & ND)", "Graduated ND filter", "Rain cover", "Spare batteries", "Fast memory cards", "Outdoor camera backpack"],
  architecture: ["Sturdy tripod", "Geared tripod head", "L-bracket", "Remote shutter", "Tethering cable", "Field monitor", "Filter set (CPL & Graduated ND)", "Anti-reflective lens cover", "Color checker", "Power bank"],
  street:       ["Thumb grip", "Compact bag", "Quick-adjust sling strap", "Mini travel tripod", "Flash (Compact)", "Filter set (ND, CPL & Black Mist)", "Fast memory cards", "Spare batteries", "Soft shutter release button", "Rain cover"],
  travel:       ["Travel tripod", "Adjustable sling strap", "Travel camera backpack", "L-bracket", "Filter set (ND & Polarizer)", "Anti-reflection hood", "Remote shutter", "Fast memory cards", "Spare batteries", "Portable SSD"],
  portrait:     ["Tripod", "Speedlight", "Flash trigger", "Light stand", "Constant light", "Light modifiers", "Reflector", "Tethering cable", "Color checker", "Remote shutter"],
  sport:        ["Monopod", "Battery grip", "Dual harness", "Teleconverter", "Remote trigger", "Fast memory cards", "Spare batteries", "Rain cover", "Power bank", "Camera gear bag"],
  wildlife:     ["Gimbal head", "Tripod/Monopod", "Teleconverter", "Beanbag", "Shoulder sling strap", "Lens covers", "Fast memory cards", "Spare batteries", "Power bank", "Wildlife backpack"],
  macro:        ["Sturdy tripod", "Macro rail", "Ring flash", "Diffuser", "Extension tubes", "Remote shutter", "Reflector", "Focus stacking software", "Spare batteries", "Macro shooting tent"],
};

type SortKey = "mark" | "pick" | "brand" | "idealIso" | "weight" | "price" | "fl" | "aperture" | "rule500" | "coma" | "astigmatism";

// =============================================================================
// ENRICHED LENS — lens + computed fields for display
// =============================================================================

interface EnrichedLens {
  lens: Lens;
  mark: number;
  isPick: boolean;
  idealIso: number | null;
  rule500: number | null;
}

// =============================================================================
// FIELD VALUE DISPLAY — 0-2 scale with color
// =============================================================================

function FieldVal({ value }: { value: number | undefined }) {
  if (value == null) return <span className={styles.markDash}>&ndash;</span>;
  const color = value >= 1.5 ? "#6aaa70" : value >= 1.0 ? "#b09040" : "#905030";
  return <span style={{ color, fontFamily: "var(--font-mono)" }}>{value}</span>;
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

function MarkPips({ mark }: { mark: number | null }) {
  if (mark == null) return <span className={styles.markDash}>&ndash;</span>;
  const full = Math.floor(mark);
  const half = mark % 1 >= 0.5;
  const pips: React.ReactNode[] = [];
  for (let i = 0; i < full; i++) {
    pips.push(<span key={i} className={`${styles.pip} ${styles.pipFull}`} />);
  }
  if (half) {
    pips.push(<span key="half" className={`${styles.pip} ${styles.pipHalf}`} />);
  }
  return (
    <span className={styles.markDots} aria-label={`Mark ${mark} of 5`}>
      {pips}
    </span>
  );
}

function PickStar({ isPick }: { isPick: boolean }) {
  if (!isPick) return null;
  return <span className={styles.topStar} aria-label="Editor pick">★</span>;
}

// =============================================================================
// EXPOSURE MATRIX — astro rule-of-500 grid
// =============================================================================

const MATRIX_FL_COLS: Record<number, number[]> = {
  12:  [6, 8, 10, 12, 14, 16],
  24:  [18, 21, 24, 28, 35],
  50:  [35, 40, 50, 56],
  135: [75, 85, 100, 135],
  300: [200, 300, 400],
};

const MATRIX_APERTURES = [1.0, 1.2, 1.4, 1.8, 2.0, 2.8, 4.0];

function ExposureMatrix({ crop, iso, ev, aoV }: { crop: number; iso: number; ev: number; aoV: number }) {
  const cols = MATRIX_FL_COLS[aoV] || MATRIX_FL_COLS[12];

  return (
    <div className={styles.matrix}>
      <div className={styles.matrixTitle}>
        EV Matrix · Rule of 500 · untracked · ISO {iso}
      </div>
      <div className={styles.matrixScroll}>
        <table className={styles.matrixTable}>
          <thead>
            <tr>
              <th className={styles.matrixCorner}>f/</th>
              {cols.map((fl) => (
                <th key={fl} className={styles.matrixColHead}>{fl}mm</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MATRIX_APERTURES.map((ap) => (
              <tr key={ap}>
                <td className={styles.matrixRowHead}>{ap}</td>
                {cols.map((fl) => {
                  const maxT = Math.round(500 / (crop * fl));
                  const needed = Math.round((ap * ap * 100) / (maxT * Math.pow(2, ev)));
                  const viable = needed <= iso;
                  const marginal = !viable && needed <= iso * 1.5;
                  const label = maxT >= 60 ? `${Math.round(maxT / 60)}m` : `${maxT}s`;
                  const cls = viable
                    ? styles.matrixViable
                    : marginal
                      ? styles.matrixMarginal
                      : styles.matrixOver;
                  return (
                    <td key={fl} className={`${styles.matrixCell} ${cls}`}>
                      {label}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className={styles.matrixLegend}>
        <span className={styles.matrixViableText}>●</span> within ISO{" "}
        <span className={styles.matrixMarginalText}>●</span> within 1 stop{" "}
        <span className={styles.matrixOverText}>●</span> needs more ISO
      </div>
      <p className={styles.matrixExplain}>
        Max exposure before star trails = 500 / (crop x FL). Each cell shows
        the longest untracked exposure at that aperture and focal length.
        Green means your selected ISO is enough. Amber means you are within
        one stop — recoverable in post processing with some noise. Red means
        the exposure does not gather enough light at this ISO.
      </p>
    </div>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

function GenreGuide({ lenses, defaultGenre = "street" }: GenreGuideProps) {
  // ── State ──────────────────────────────────────────────────────────────
  const [genre, setGenre] = useState<ScoredGenre>(defaultGenre);
  const defaults = GENRE_DEFAULTS[genre];
  const [ev, setEv] = useState(defaults.ev);
  const [iso, setIso] = useState(defaults.iso);
  const [nd, setNd] = useState<number[]>([]);
  const [crop, setCrop] = useState(1.5);
  const [mp, setMp] = useState(26);
  const [aoV, setAoV] = useState(defaults.fl);
  const [sortBy, setSortBy] = useState<SortKey>("mark");
  const [sortAsc, setSortAsc] = useState(false);
  const [brandFilter, setBrandFilter] = useState("");
  const [markFilter, setMarkFilter] = useState("");
  const [priceFilter, setPriceFilter] = useState("");
  const [weightFilter, setWeightFilter] = useState("");
  const [apertureFilter, setApertureFilter] = useState("");
  const sceneListRef = useRef<HTMLDivElement>(null);

  const config = genreConfigs[genre];
  const isAstro = genre === "astro";

  // ── Genre change → reset all ───────────────────────────────────────────
  function handleGenreChange(g: ScoredGenre): void {
    setGenre(g);
    const d = GENRE_DEFAULTS[g];
    setEv(d.ev);
    setIso(d.iso);
    setAoV(d.fl);
    setNd([]);
    setSortBy("mark");
    setSortAsc(false);
    setBrandFilter("");
    setMarkFilter("");
    setPriceFilter("");
    setWeightFilter("");
    setApertureFilter("");
  }

  // ── Scene scroll ───────────────────────────────────────────────────────
  const scrollToEv = useCallback(() => {
    const container = sceneListRef.current;
    if (!container) return;
    const el = container.querySelector(`[data-ev="${ev}"]`);
    if (!el) return;
    const cRect = container.getBoundingClientRect();
    const eRect = el.getBoundingClientRect();
    const offset = eRect.top - cRect.top + container.scrollTop - cRect.height / 2 + eRect.height / 2;
    container.scrollTop = Math.max(0, offset);
  }, [ev]);

  useEffect(() => { scrollToEv(); }, [ev, genre, scrollToEv]);

  // ── Filtered scenes ────────────────────────────────────────────────────
  const visibleScenes = useMemo(
    () => evScenes.filter((s) => genreSceneFilter[genre](s.ev)),
    [genre],
  );

  // ── Filter + enrich + sort lenses ──────────────────────────────────────
  const enrichedLenses = useMemo(() => {
    const enriched: EnrichedLens[] = lenses
      .filter((l) => {
        // Must have a mark for this genre
        const mark = getGenreMark(l, genre);
        if (mark == null) return false;
        // Filter by mount
        if (crop === 0.79 ? l.mount !== "GFX" : l.mount !== "X") return false;
        // Filter by FL range
        const range = FL_RANGES[aoV];
        if (range) {
          if (l.focalLengthMax < range[0] || l.focalLengthMin > range[1]) return false;
        }
        return true;
      })
      .map((l) => {
        const mark = getGenreMark(l, genre)!;
        const isPick = isEditorialPick(l, genre);
        const idealIso = isAstro
          ? astroExposure(l, ev, iso, crop).idealIso
          : handheldExposure(l, genre, ev, crop, mp).idealIso;
        const rule500 = isAstro
          ? Math.round(500 / (crop * l.focalLengthMin))
          : null;

        return { lens: l, mark, isPick, idealIso, rule500 };
      });

    // Sort — v is always ascending (a < b → negative)
    enriched.sort((a, b) => {
      let v = 0;
      switch (sortBy) {
        case "mark":
          v = a.mark - b.mark;
          if (v === 0) v = (a.isPick ? 1 : 0) - (b.isPick ? 1 : 0);
          break;
        case "pick":
          v = (a.isPick ? 1 : 0) - (b.isPick ? 1 : 0);
          break;
        case "brand":
          v = a.lens.brand.localeCompare(b.lens.brand);
          break;
        case "idealIso":
          v = (a.idealIso ?? 99999) - (b.idealIso ?? 99999);
          break;
        case "weight":
          v = a.lens.weight - b.lens.weight;
          break;
        case "price":
          v = a.lens.price - b.lens.price;
          break;
        case "fl":
          v = a.lens.focalLengthMin - b.lens.focalLengthMin;
          break;
        case "aperture":
          v = a.lens.maxAperture - b.lens.maxAperture;
          break;
        case "rule500":
          v = (a.rule500 ?? 0) - (b.rule500 ?? 0);
          break;
        case "coma":
          v = (a.lens.coma ?? -1) - (b.lens.coma ?? -1);
          break;
        case "astigmatism":
          v = (a.lens.astigmatism ?? -1) - (b.lens.astigmatism ?? -1);
          break;
      }
      return sortAsc ? v : -v;
    });

    // Apply filters
    return enriched.filter((el) => {
      if (brandFilter && el.lens.brand !== brandFilter) return false;
      if (markFilter && el.mark < Number(markFilter)) return false;
      if (priceFilter && el.lens.price > Number(priceFilter)) return false;
      if (weightFilter && el.lens.weight > Number(weightFilter)) return false;
      if (apertureFilter && el.lens.maxAperture > Number(apertureFilter)) return false;
      return true;
    });
  }, [lenses, genre, crop, ev, iso, mp, aoV, sortBy, sortAsc, isAstro, brandFilter, markFilter, priceFilter, weightFilter, apertureFilter]);

  // ── Sort handler ───────────────────────────────────────────────────────
  function handleSort(key: SortKey): void {
    if (sortBy === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(key);
      setSortAsc(key === "brand" || key === "fl" || key === "price" || key === "weight" || key === "idealIso");
    }
  }

  // ── ND factor ──────────────────────────────────────────────────────────
  function toggleNd(factor: number): void {
    setNd((prev) =>
      prev.includes(factor) ? prev.filter((f) => f !== factor) : [...prev, factor],
    );
  }

  // ── FL chips ───────────────────────────────────────────────────────────
  const flChips =
    genre === "portrait"
      ? FL_CHIPS.portrait
      : genre === "sport" || genre === "wildlife"
        ? FL_CHIPS.sportWildlife
        : genre === "macro"
          ? FL_CHIPS.macro
          : FL_CHIPS.default;

  // ── Scene label ────────────────────────────────────────────────────────
  function sceneLabel(sceneEv: number): string {
    return genreEvLabels[genre]?.[sceneEv] ?? evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
  }

  // ── Format helpers ─────────────────────────────────────────────────────
  function fmtIso(v: number | null): string {
    if (v == null) return "\u2013";
    if (v > 99999) return ">100K";
    return v.toLocaleString();
  }

  const sortIndicator = (key: SortKey) =>
    sortBy === key ? (sortAsc ? "\u2191" : "\u2193") : "\u2195";

  // ── Render ─────────────────────────────────────────────────────────────
  return (
    <div className={styles.guide}>
      {/* Genre tabs */}
      <div className={styles.genreTabs} role="tablist" aria-label="Photography genres">
        {SCORED_GENRES.map((g) => (
          <button
            key={g}
            type="button"
            role="tab"
            aria-selected={genre === g}
            className={`${styles.genreTab} ${genre === g ? styles.genreTabActive : ""}`}
            onClick={() => handleGenreChange(g)}
          >
            {genreConfigs[g].name.replace("Astrophotography", "Astronomy").replace(" Photography", "")}
          </button>
        ))}
      </div>

      {/* Two-column layout: sidebar + main */}
      <div className={styles.layout}>

        {/* Left sidebar: scene list + equipment */}
        <div className={styles.sidebar}>
          {/* Scene selector */}
          <div className={styles.sidebarPanel}>
            <div className={styles.sidebarTitle}>EV / Scene</div>
            <div className={styles.sceneList} ref={sceneListRef}>
              {visibleScenes.map((s) => (
                <button
                  key={s.ev}
                  type="button"
                  data-ev={s.ev}
                  className={`${styles.sceneItem} ${ev === s.ev ? styles.sceneItemActive : ""}`}
                  onClick={() => setEv(s.ev)}
                >
                  <span className={styles.sceneEv}>{s.ev}</span>
                  <span className={styles.sceneText}>{sceneLabel(s.ev)}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Equipment panel */}
          <div className={styles.sidebarPanel}>
            <div className={styles.sidebarTitle}>Equipment</div>
            <div className={styles.equipmentList}>
              {GENRE_EQUIPMENT[genre]?.join(" · ")}
            </div>
          </div>
        </div>

        {/* Right: controls + matrix + results */}
        <div className={styles.main}>
          <div className={styles.controlPanel}>
          {/* EV header */}
          <div className={styles.evHeader}>
            <span className={styles.evLabel}>EV {ev} — {sceneLabel(ev)}</span>
          </div>

          {/* Controls — matching prototype order: Mount → FL → ISO → ND → MP */}
          <div className={styles.controls}>
            {/* Mount */}
            <div className={styles.controlGroup}>
              <ChipGroup
                label="Mount"
                value={crop === 1.5 ? "X" : "GFX"}
                onChange={(v) => {
                  const c = v === "GFX" ? 0.79 : 1.5;
                  setCrop(c);
                  setMp(c === 0.79 ? 102 : 26);
                  if (isAstro) setIso(c === 0.79 ? 3200 : 1600);
                }}
                styles={styles}
                options={[
                  { label: "X-Mount", value: "X" },
                  { label: "GFX", value: "GFX" },
                ]}
              />
            </div>

            {/* FL chips */}
            <div className={styles.controlGroup}>
              <span className={styles.controlLabel}>FL</span>
              <div className={styles.flRow}>
                {flChips.map((chip) => (
                  <button
                    key={chip.fl}
                    type="button"
                    className={`${styles.chip} ${aoV === chip.fl ? styles.chipOn : ""}`}
                    onClick={() => setAoV(chip.fl)}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>
            </div>

            {/* ISO — chips matching prototype */}
            <div className={styles.controlGroup}>
              <span className={styles.controlLabel}>ISO</span>
              <div className={styles.flRow}>
                {(crop === 0.79
                  ? [100, 200, 400, 800, 1600, 3200, 6400, 12800]
                  : [100, 200, 400, 800, 1600, 3200, 6400]
                ).map((v) => (
                  <button
                    key={v}
                    type="button"
                    className={`${styles.chip} ${iso === v ? styles.chipOn : ""}`}
                    onClick={() => setIso(v)}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>

            {/* ND — only for landscape + architecture */}
            {(genre === "landscape" || genre === "architecture") && (
              <div className={styles.controlGroup}>
                <span className={styles.controlLabel}>ND</span>
                <div className={styles.ndRow}>
                  {ND_OPTIONS.map((opt) => (
                    <button
                      key={opt.factor}
                      type="button"
                      className={`${styles.chip} ${nd.includes(opt.factor) ? styles.chipOn : ""}`}
                      onClick={() => toggleNd(opt.factor)}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          </div>{/* end controlPanel */}

          {/* Exposure matrix — separate panel */}
          {isAstro && (
            <div className={styles.matrixPanel}>
              <ExposureMatrix crop={crop} iso={iso} ev={ev} aoV={aoV} />
            </div>
          )}
        </div>{/* end main */}
      </div>{/* end layout */}

      {/* Filter panel — full width */}
      <div className={styles.filterPanel}>
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Brand</span>
          <select
            className={styles.controlSelect}
            value={brandFilter}
            onChange={(e) => setBrandFilter(e.target.value)}
          >
            <option value="">All</option>
            {[...new Set(enrichedLenses.map((el) => el.lens.brand))].sort().map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Mark</span>
          <select
            className={styles.controlSelect}
            value={markFilter}
            onChange={(e) => setMarkFilter(e.target.value)}
          >
            <option value="">All</option>
            {[5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1].map((v) => (
              <option key={v} value={v}>≥ {v}</option>
            ))}
          </select>
        </div>
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Price</span>
          <select
            className={styles.controlSelect}
            value={priceFilter}
            onChange={(e) => setPriceFilter(e.target.value)}
          >
            <option value="">Any</option>
            {[500, 1000, 1500, 2000, 4000].map((v) => (
              <option key={v} value={v}>≤ ~${v}</option>
            ))}
          </select>
        </div>
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Weight</span>
          <select
            className={styles.controlSelect}
            value={weightFilter}
            onChange={(e) => setWeightFilter(e.target.value)}
          >
            <option value="">Any</option>
            {[200, 300, 500, 800, 1500].map((v) => (
              <option key={v} value={v}>≤ {v}g</option>
            ))}
          </select>
        </div>
        {isAstro && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Aperture</span>
            <select
              className={styles.controlSelect}
              value={apertureFilter}
              onChange={(e) => setApertureFilter(e.target.value)}
            >
              <option value="">Any</option>
              {[1.4, 2.0, 2.8, 4.0].map((v) => (
                <option key={v} value={v}>≤ f/{v}</option>
              ))}
            </select>
          </div>
        )}
        {(brandFilter || markFilter || priceFilter || weightFilter || apertureFilter) && (
          <button
            type="button"
            className={styles.clearBtn}
            onClick={() => { setBrandFilter(""); setMarkFilter(""); setPriceFilter(""); setWeightFilter(""); setApertureFilter(""); }}
          >
            ✕ clear
          </button>
        )}
      </div>

      {enrichedLenses.length === 0 ? (
        <p className={styles.emptyState}>No lenses match the current settings.</p>
      ) : (
        <>
          {/* Desktop table */}
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  {(isAstro ? ([
                    ["mark", "Mark"],
                    ["pick", ""],
                    ["brand", "Brand"],
                    ["fl", "Model"],
                    ["aperture", "f/"],
                    ["fl", "FL"],
                    ["rule500", "Rule 500"],
                    ["idealIso", "Ideal ISO"],
                    ["coma", "Coma"],
                    ["astigmatism", "Astig"],
                    ["weight", "Wt"],
                    ["price", "Price"],
                  ] as [SortKey, string][]) : ([
                    ["mark", "Mark"],
                    ["pick", ""],
                    ["brand", "Brand"],
                    ["fl", "Model"],
                    ["idealIso", "Ideal ISO"],
                    ["weight", "Wt"],
                    ["price", "Price"],
                  ] as [SortKey, string][])).map(([key, label]) => (
                    <th
                      key={`${key}-${label}`}
                      className={
                        key === "weight" || key === "price" || key === "idealIso" || key === "rule500" || key === "aperture" || key === "coma" || key === "astigmatism"
                          ? styles.cellRight
                          : key === "pick"
                            ? styles.cellCenter
                            : undefined
                      }
                      onClick={() => handleSort(key)}
                    >
                      {label}
                      <span className={styles.sortIndicator}>{sortIndicator(key)}</span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {enrichedLenses.map((el) => (
                  <tr key={`${el.lens.brand}-${el.lens.model}`}>
                    <td><MarkPips mark={el.mark} /></td>
                    <td className={styles.cellCenter}><PickStar isPick={el.isPick} /></td>
                    <td>{el.lens.brand}</td>
                    <td>{el.lens.model}</td>
                    {isAstro && (
                      <>
                        <td className={styles.cellRight}>f/{el.lens.maxAperture}</td>
                        <td className={styles.cellRight}>{el.lens.focalLengthMin}mm</td>
                        <td className={styles.cellRight}>{el.rule500}s</td>
                        <td className={styles.cellRight}>{fmtIso(el.idealIso)}</td>
                        <td className={styles.cellRight}><FieldVal value={el.lens.coma} /></td>
                        <td className={styles.cellRight}><FieldVal value={el.lens.astigmatism} /></td>
                      </>
                    )}
                    {!isAstro && (
                      <td className={styles.cellRight}>{fmtIso(el.idealIso)}</td>
                    )}
                    <td className={styles.cellRight}>{el.lens.weight}g</td>
                    <td className={styles.cellRight}>~${el.lens.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile cards */}
          <div className={styles.cards}>
            {enrichedLenses.map((el) => (
              <div key={`${el.lens.brand}-${el.lens.model}`} className={styles.card}>
                <div className={styles.cardTop}>
                  <MarkPips mark={el.mark} />
                  <PickStar isPick={el.isPick} />
                  <span className={styles.cardPrice}>~${el.lens.price}</span>
                </div>
                <div className={styles.cardName}>
                  {el.lens.brand} {el.lens.model}
                </div>
                <div className={styles.cardSpecs}>
                  <span>f/{el.lens.maxAperture}</span>
                  <span>
                    {el.lens.focalLengthMin === el.lens.focalLengthMax
                      ? `${el.lens.focalLengthMin}mm`
                      : `${el.lens.focalLengthMin}-${el.lens.focalLengthMax}mm`}
                  </span>
                  {isAstro && el.rule500 != null && <span>{el.rule500}s</span>}
                  {el.idealIso != null && <span>ISO {fmtIso(el.idealIso)}</span>}
                  {isAstro && <><span>Coma <FieldVal value={el.lens.coma} /></span><span>Astig <FieldVal value={el.lens.astigmatism} /></span></>}
                  <span>{el.lens.weight}g</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <p className={styles.footnote}>
        Marks score optical suitability only — resolution, aberrations, bokeh quality —
        from lab measurements and trusted field reviews. OIS, autofocus, weather sealing,
        and build quality do not affect the mark. Focal length is a creative choice shown
        as a filter, not a scoring input. Prices are approximate USD estimates.
      </p>
    </div>
  );
}

export default GenreGuide;
