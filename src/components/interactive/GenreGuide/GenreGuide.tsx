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

const MARK_PALETTE = ["", "#2a2520", "#4a4540", "#7a7060", "#c08830", "#e8a045"];
const ISO_OPTIONS = [100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600];
const ND_OPTIONS = [
  { label: "ND2", factor: 2 },
  { label: "ND4", factor: 4 },
  { label: "ND8", factor: 8 },
  { label: "ND64", factor: 64 },
  { label: "ND1000", factor: 1000 },
];

const SCORED_GENRES: ScoredGenre[] = [
  "astro", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife",
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
};

type SortKey = "mark" | "pick" | "brand" | "idealIso" | "weight" | "price" | "fl";

// =============================================================================
// ENRICHED LENS — lens + computed fields for display
// =============================================================================

interface EnrichedLens {
  lens: Lens;
  mark: number;
  isPick: boolean;
  idealIso: number | null;
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

function MarkPips({ mark }: { mark: number | null }) {
  if (mark == null) return <span className={styles.markDash}>&ndash;</span>;
  const color = MARK_PALETTE[mark] || "#8a8070";
  return (
    <span className={styles.markDots} style={{ color }} aria-label={`Mark ${mark} of 5`}>
      {"●".repeat(mark)}
    </span>
  );
}

function PickStar({ isPick }: { isPick: boolean }) {
  if (!isPick) return null;
  return <span className={styles.topStar} aria-label="Editor pick">★</span>;
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
        return crop === 0.79 ? l.mount === "GFX" : l.mount === "X";
      })
      .map((l) => {
        const mark = getGenreMark(l, genre)!;
        const isPick = isEditorialPick(l, genre);
        const idealIso = isAstro
          ? astroExposure(l, ev, iso, crop).idealIso
          : handheldExposure(l, genre, ev, crop, mp).idealIso;

        return { lens: l, mark, isPick, idealIso };
      });

    // Sort
    enriched.sort((a, b) => {
      let v = 0;
      switch (sortBy) {
        case "mark":
          v = b.mark - a.mark;
          if (v === 0) v = (b.isPick ? 1 : 0) - (a.isPick ? 1 : 0);
          break;
        case "pick":
          v = (b.isPick ? 1 : 0) - (a.isPick ? 1 : 0);
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
      }
      return sortAsc ? v : -v;
    });

    return enriched;
  }, [lenses, genre, crop, ev, iso, mp, sortBy, sortAsc, isAstro]);

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
            {genreConfigs[g].name.replace(" Photography", "")}
          </button>
        ))}
      </div>

      {/* Genre header */}
      <div className={styles.genreHeader}>
        <h2 className={styles.genreName}>{config.name}</h2>
        <p className={styles.genreLabel}>{config.tagline}</p>
        <p className={styles.genreDesc}>{config.description}</p>
      </div>

      {/* Controls panel */}
      <div className={styles.controls}>
        {/* Scene selector */}
        <div className={styles.controlGroup}>
          <label className={styles.controlLabel}>Scene (EV {ev})</label>
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

        {/* ISO */}
        <div className={styles.controlGroup}>
          <label className={styles.controlLabel} htmlFor="iso-select">ISO</label>
          <select
            id="iso-select"
            className={styles.controlSelect}
            value={iso}
            onChange={(e) => setIso(Number(e.target.value))}
          >
            {ISO_OPTIONS.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>

        {/* ND filters */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>ND Filter</span>
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

        {/* FL chips */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Focal Length</span>
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
      </div>

      {/* Results count */}
      <p className={styles.resultCount}>
        {enrichedLenses.length} lens{enrichedLenses.length !== 1 ? "es" : ""}
      </p>

      {enrichedLenses.length === 0 ? (
        <p className={styles.emptyState}>No lenses match the current settings.</p>
      ) : (
        <>
          {/* Desktop table */}
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  {([
                    ["mark", "Mark"],
                    ["pick", ""],
                    ["brand", "Brand"],
                    ["fl", "Model"],
                    ["idealIso", "Ideal ISO"],
                    ["weight", "Weight"],
                    ["price", "Price"],
                  ] as [SortKey, string][]).map(([key, label]) => (
                    <th
                      key={key}
                      className={
                        key === "weight" || key === "price" || key === "idealIso"
                          ? styles.cellRight
                          : key === "mark" || key === "pick"
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
                    <td className={styles.cellCenter}><MarkPips mark={el.mark} /></td>
                    <td className={styles.cellCenter}><PickStar isPick={el.isPick} /></td>
                    <td>{el.lens.brand}</td>
                    <td>
                      {el.lens.model}
                      {el.lens.sweetSpotAperture && (
                        <span className={styles.sweetSpot}> f/{el.lens.sweetSpotAperture}</span>
                      )}
                    </td>
                    <td className={styles.cellRight}>{fmtIso(el.idealIso)}</td>
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
                  {el.lens.sweetSpotAperture && <span>f/{el.lens.sweetSpotAperture}</span>}
                  {el.idealIso != null && <span>ISO {fmtIso(el.idealIso)}</span>}
                  <span>{el.lens.weight}g</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <p className={styles.footnote}>
        Marks represent optical suitability (sharpness, coma, bokeh). OIS, WR, AF,
        and weight are display attributes and do not affect the mark. Focal length is a
        creative choice, not a scoring criterion. All prices are approximate USD estimates.
      </p>
    </div>
  );
}

export default GenreGuide;
