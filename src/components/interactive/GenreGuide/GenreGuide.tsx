import { useState, useMemo, useRef, useEffect, useCallback } from "react";
import type { Lens } from "../../../types/lens";
import type { ScoredGenre } from "../../../types/genre";
import {
  genreConfigs,
  evScenes,
  genreEvLabels,
  genreSceneFilter,
  ND_OPTIONS,
  FL_CHIPS_X,
  FL_CHIPS_GFX,
  FL_RANGES_X,
  FL_RANGES_GFX,
  GENRE_DEFAULTS,
  GENRE_EQUIPMENT,
  NIGHTSCAPE_ISO_BY_EV,
} from "../../../data/genres";
import { getGenreMark, isEditorialPick } from "../../../utils/scoring";
import { astroExposure, handheldExposure } from "./exposure";
import { ChipGroup } from "../shared/ChipGroup";
import { MarkPips, PickStar, FieldVal } from "../shared/MarkPips";
import { ExposureMatrix } from "./ExposureMatrix";
import { LandscapeMatrix } from "./LandscapeMatrix";
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

const SCORED_GENRES: ScoredGenre[] = [
  "nightscape", "landscape", "architecture", "street",
  "travel", "portrait", "sport", "wildlife", "macro",
];

type SortKey = "mark" | "pick" | "brand" | "idealIso" | "weight" | "price" | "fl" | "aperture" | "rule500" | "coma" | "astigmatism" | "wr" | "cornerStopped" | "centerStopped" | "distortion" | "flareResistance";

// =============================================================================
// ENRICHED LENS — lens + computed fields for display
// =============================================================================

interface EnrichedLens {
  lens: Lens;
  mark: number;
  isPick: boolean;
  idealIso: number | null;
  rule500: number | null;
  effectiveFl: number;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

function GenreGuide({ lenses, defaultGenre = "street" }: GenreGuideProps) {
  // -- State ----------------------------------------------------------------
  const [genre, setGenre] = useState<ScoredGenre>(defaultGenre);
  const defaults = GENRE_DEFAULTS[genre];
  const [ev, setEv] = useState(defaults.ev);
  const [iso, setIso] = useState(defaults.iso);
  const [nd, setNd] = useState<number[]>([]);
  const [cropFactor, setCropFactor] = useState(1.5);
  const [sensorMp, setSensorMp] = useState(26);
  const [selectedFl, setSelectedFl] = useState(defaults.fl);
  const [sortBy, setSortBy] = useState<SortKey>("mark");
  const [sortAsc, setSortAsc] = useState(false);
  const [brandFilter, setBrandFilter] = useState("");
  const [markFilter, setMarkFilter] = useState("");
  const [priceFilter, setPriceFilter] = useState("");
  const [weightFilter, setWeightFilter] = useState("");
  const [apertureFilter, setApertureFilter] = useState("");
  const [comaFilter, setComaFilter] = useState("");
  const [astigFilter, setAstigFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [wrFilter, setWrFilter] = useState("");
  const [cornerFilter, setCornerFilter] = useState("");
  const [distFilter, setDistFilter] = useState("");
  const [flareFilter, setFlareFilter] = useState("");
  const sceneListRef = useRef<HTMLDivElement>(null);

  const isNightscape = genre === "nightscape";
  const isLandscape = genre === "landscape";
  const isArchitecture = genre === "architecture";
  const FL_CHIPS = cropFactor === 0.79 ? FL_CHIPS_GFX : FL_CHIPS_X;
  const FL_RANGES = cropFactor === 0.79 ? FL_RANGES_GFX : FL_RANGES_X;

  // -- Genre change -> reset all --------------------------------------------
  function handleGenreChange(g: ScoredGenre): void {
    setGenre(g);
    const d = GENRE_DEFAULTS[g];
    setEv(d.ev);
    setIso(d.iso);
    setSelectedFl(d.fl);
    setNd([]);
    setSortBy("mark");
    setSortAsc(false);
    setBrandFilter("");
    setMarkFilter("");
    setPriceFilter("");
    setWeightFilter("");
    setApertureFilter("");
    setComaFilter("");
    setAstigFilter("");
    setTypeFilter("");
    setWrFilter("");
    setCornerFilter("");
    setDistFilter("");
    setFlareFilter("");
  }

  // -- Scene scroll ---------------------------------------------------------
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

  // -- Filtered scenes ------------------------------------------------------
  const visibleScenes = useMemo(
    () => evScenes.filter((s) => genreSceneFilter[genre](s.ev)),
    [genre],
  );

  // -- Filter + enrich + sort lenses ----------------------------------------
  const enrichedLenses = useMemo(() => {
    const enriched: EnrichedLens[] = lenses
      .filter((l) => {
        const mark = getGenreMark(l, genre);
        if (mark == null) return false;
        if (l.isDiscontinued) return false;
        if (cropFactor === 0.79 ? l.mount !== "GFX" : l.mount !== "X") return false;
        const range = FL_RANGES[selectedFl];
        if (range) {
          if (l.focalLengthMax < range[0] || l.focalLengthMin > range[1]) return false;
        }
        return true;
      })
      .map((l) => {
        const mark = getGenreMark(l, genre)!;
        const isPick = isEditorialPick(l, genre);
        const range = FL_RANGES[selectedFl];
        let effectiveFl = l.focalLengthMin;
        if (range && l.type === "zoom") {
          effectiveFl = Math.max(l.focalLengthMin, range[0]);
        }
        const idealIso = isNightscape
          ? astroExposure({ ...l, focalLengthMin: effectiveFl } as Lens, ev, iso, cropFactor).idealIso
          : handheldExposure(l, genre, ev, cropFactor, sensorMp).idealIso;
        const rule500 = isNightscape
          ? Math.round(500 / (cropFactor * effectiveFl))
          : null;

        return { lens: l, mark, isPick, idealIso, rule500, effectiveFl };
      });

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
        case "wr":
          v = (a.lens.isWeatherSealed ? 1 : 0) - (b.lens.isWeatherSealed ? 1 : 0);
          break;
        case "cornerStopped":
          v = (a.lens.cornerStopped ?? -1) - (b.lens.cornerStopped ?? -1);
          break;
        case "centerStopped":
          v = (a.lens.centerStopped ?? -1) - (b.lens.centerStopped ?? -1);
          break;
        case "distortion":
          v = (a.lens.distortion ?? -1) - (b.lens.distortion ?? -1);
          break;
        case "flareResistance":
          v = (a.lens.flareResistance ?? -1) - (b.lens.flareResistance ?? -1);
          break;
      }
      return sortAsc ? v : -v;
    });

    return enriched.filter((el) => {
      if (brandFilter && el.lens.brand !== brandFilter) return false;
      if (markFilter && el.mark < Number(markFilter)) return false;
      if (priceFilter && el.lens.price > Number(priceFilter)) return false;
      if (weightFilter && el.lens.weight > Number(weightFilter)) return false;
      if (apertureFilter && el.lens.maxAperture > Number(apertureFilter)) return false;
      if (comaFilter && (el.lens.coma == null || el.lens.coma < Number(comaFilter))) return false;
      if (astigFilter && (el.lens.astigmatism == null || el.lens.astigmatism < Number(astigFilter))) return false;
      if (typeFilter && el.lens.type !== typeFilter) return false;
      if (wrFilter === "yes" && !el.lens.isWeatherSealed) return false;
      if (wrFilter === "no" && el.lens.isWeatherSealed) return false;
      if (cornerFilter && (el.lens.cornerStopped == null || el.lens.cornerStopped < Number(cornerFilter))) return false;
      if (distFilter && (el.lens.distortion == null || el.lens.distortion < Number(distFilter))) return false;
      if (flareFilter && (el.lens.flareResistance == null || el.lens.flareResistance < Number(flareFilter))) return false;
      return true;
    });
  }, [lenses, genre, cropFactor, ev, iso, sensorMp, selectedFl, sortBy, sortAsc, isNightscape, brandFilter, markFilter, priceFilter, weightFilter, apertureFilter, comaFilter, astigFilter, typeFilter, wrFilter, cornerFilter, distFilter, flareFilter]);

  // -- Sort handler ---------------------------------------------------------
  function handleSort(key: SortKey): void {
    if (sortBy === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(key);
      setSortAsc(key === "brand" || key === "fl" || key === "price" || key === "weight" || key === "idealIso");
    }
  }

  // -- ND factor ------------------------------------------------------------
  function toggleNd(factor: number): void {
    setNd((prev) =>
      prev.includes(factor) ? prev.filter((f) => f !== factor) : [...prev, factor],
    );
  }

  // -- FL chips ----------------------------------------------------------------
  const flChips =
    genre === "portrait"
      ? FL_CHIPS.portrait
      : genre === "sport" || genre === "wildlife"
        ? FL_CHIPS.sportWildlife
        : genre === "macro"
          ? FL_CHIPS.macro
          : FL_CHIPS.default;

  // -- Scene label ----------------------------------------------------------
  function sceneLabel(sceneEv: number): string {
    // Nightscape sidebar uses short labels; Bortle labels only in EV header
    if (isNightscape) {
      return evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
    }
    return genreEvLabels[genre]?.[sceneEv] ?? evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
  }

  function evHeaderLabel(sceneEv: number): string {
    return genreEvLabels[genre]?.[sceneEv] ?? evScenes.find((s) => s.ev === sceneEv)?.short ?? "";
  }

  // -- Format helpers -------------------------------------------------------
  function fmtIso(v: number | null): string {
    if (v == null) return "\u2013";
    if (v > 99999) return ">100K";
    return v.toLocaleString();
  }

  const sortIndicator = (key: SortKey) =>
    sortBy === key ? (sortAsc ? "\u2191" : "\u2193") : "\u2195";

  // -- Render ---------------------------------------------------------------
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
                  onClick={() => {
                    setEv(s.ev);
                    if (isNightscape && NIGHTSCAPE_ISO_BY_EV[s.ev] != null) {
                      setIso(NIGHTSCAPE_ISO_BY_EV[s.ev]);
                    }
                  }}
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
            <span className={styles.evLabel}>EV {ev} — {evHeaderLabel(ev)}</span>
          </div>

          {/* Controls — matching prototype order: Mount -> FL -> ISO -> ND -> MP */}
          <div className={styles.controls}>
            {/* Mount */}
            <div className={styles.controlGroup}>
              <ChipGroup
                label="Mount"
                value={cropFactor === 1.5 ? "X" : "GFX"}
                onChange={(v) => {
                  const c = v === "GFX" ? 0.79 : 1.5;
                  setCropFactor(c);
                  setSensorMp(c === 0.79 ? 102 : 26);
                  if (isNightscape) setIso(c === 0.79 ? 3200 : 1600);
                  const chips = c === 0.79 ? FL_CHIPS_GFX : FL_CHIPS_X;
                  setSelectedFl(chips.default[0].fl);
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
                    className={`${styles.chip} ${selectedFl === chip.fl ? styles.chipOn : ""}`}
                    onClick={() => setSelectedFl(chip.fl)}
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
                {(cropFactor === 0.79
                  ? [100, 200, 400, 800, 1600, 3200, 6400]
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
          {isNightscape && (
            <div className={styles.matrixPanel}>
              <ExposureMatrix cropFactor={cropFactor} iso={iso} ev={ev} selectedFl={selectedFl} />
            </div>
          )}
          {(isLandscape || isArchitecture) && (
            <div className={styles.matrixPanel}>
              <LandscapeMatrix cropFactor={cropFactor} iso={iso} ev={ev} nd={nd} selectedFl={selectedFl} />
            </div>
          )}
        </div>{/* end main */}
      </div>{/* end layout */}

      {/* Filter panel — ordered to match columns */}
      <div className={styles.filterPanel}>
        {/* Mark */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Mark</span>
          <select className={styles.controlSelect} value={markFilter} onChange={(e) => setMarkFilter(e.target.value)}>
            <option value="">All</option>
            {[5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1].map((v) => (
              <option key={v} value={v}>≥ {v}</option>
            ))}
          </select>
        </div>
        {/* Type */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Type</span>
          <select className={styles.controlSelect} value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="">All</option>
            <option value="prime">Prime</option>
            <option value="zoom">Zoom</option>
          </select>
        </div>
        {/* Brand */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Brand</span>
          <select className={styles.controlSelect} value={brandFilter} onChange={(e) => setBrandFilter(e.target.value)}>
            <option value="">All</option>
            {[...new Set(enrichedLenses.map((el) => el.lens.brand))].sort().map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
        {/* Aperture — astro */}
        {isNightscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>f/</span>
            <select className={styles.controlSelect} value={apertureFilter} onChange={(e) => setApertureFilter(e.target.value)}>
              <option value="">Any</option>
              {[1.4, 2.0, 2.8, 4.0].map((v) => (
                <option key={v} value={v}>≤ f/{v}</option>
              ))}
            </select>
          </div>
        )}
        {/* Coma — astro */}
        {isNightscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Coma</span>
            <select className={styles.controlSelect} value={comaFilter} onChange={(e) => setComaFilter(e.target.value)}>
              <option value="">Any</option>
              {[2.0, 1.5, 1.0].map((v) => (
                <option key={v} value={v}>≥ {v}</option>
              ))}
            </select>
          </div>
        )}
        {/* Astigmatism — astro */}
        {isNightscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Astig</span>
            <select className={styles.controlSelect} value={astigFilter} onChange={(e) => setAstigFilter(e.target.value)}>
              <option value="">Any</option>
              {[2.0, 1.5, 1.0].map((v) => (
                <option key={v} value={v}>≥ {v}</option>
              ))}
            </select>
          </div>
        )}
        {/* CornerS — landscape */}
        {isLandscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>CornerS</span>
            <select className={styles.controlSelect} value={cornerFilter} onChange={(e) => setCornerFilter(e.target.value)}>
              <option value="">Any</option>
              {[2.0, 1.5, 1.0].map((v) => (
                <option key={v} value={v}>≥ {v}</option>
              ))}
            </select>
          </div>
        )}
        {/* Dist — landscape */}
        {isLandscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Dist</span>
            <select className={styles.controlSelect} value={distFilter} onChange={(e) => setDistFilter(e.target.value)}>
              <option value="">Any</option>
              {[2.0, 1.5, 1.0].map((v) => (
                <option key={v} value={v}>≥ {v}</option>
              ))}
            </select>
          </div>
        )}
        {/* Flare — landscape */}
        {isLandscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Flare</span>
            <select className={styles.controlSelect} value={flareFilter} onChange={(e) => setFlareFilter(e.target.value)}>
              <option value="">Any</option>
              {[2.0, 1.5, 1.0].map((v) => (
                <option key={v} value={v}>≥ {v}</option>
              ))}
            </select>
          </div>
        )}
        {/* Weight — non-astro, non-landscape */}
        {!isNightscape && !isLandscape && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>Wt</span>
            <select className={styles.controlSelect} value={weightFilter} onChange={(e) => setWeightFilter(e.target.value)}>
              <option value="">Any</option>
              {[200, 300, 500, 800, 1500].map((v) => (
                <option key={v} value={v}>≤ {v}g</option>
              ))}
            </select>
          </div>
        )}
        {/* WR — astro + landscape */}
        {(isNightscape || isLandscape) && (
          <div className={styles.controlGroup}>
            <span className={styles.controlLabel}>WR</span>
            <select className={styles.controlSelect} value={wrFilter} onChange={(e) => setWrFilter(e.target.value)}>
              <option value="">All</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
        )}
        {/* Price */}
        <div className={styles.controlGroup}>
          <span className={styles.controlLabel}>Price</span>
          <select className={styles.controlSelect} value={priceFilter} onChange={(e) => setPriceFilter(e.target.value)}>
            <option value="">Any</option>
            {[500, 1000, 1500, 2000, 4000].map((v) => (
              <option key={v} value={v}>≤ ~${v}</option>
            ))}
          </select>
        </div>
        {/* Clear */}
        {(brandFilter || markFilter || priceFilter || weightFilter || apertureFilter || comaFilter || astigFilter || typeFilter || wrFilter || cornerFilter || distFilter || flareFilter) && (
          <button
            type="button"
            className={styles.clearBtn}
            onClick={() => { setBrandFilter(""); setMarkFilter(""); setPriceFilter(""); setWeightFilter(""); setApertureFilter(""); setComaFilter(""); setAstigFilter(""); setTypeFilter(""); setWrFilter(""); setCornerFilter(""); setDistFilter(""); setFlareFilter(""); }}
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
                  {(isNightscape ? ([
                    ["mark", "Mark"],
                    ["pick", ""],
                    ["brand", "Brand"],
                    ["fl", "Model"],
                    ["fl", "FL"],
                    ["aperture", "f/"],
                    ["coma", "Coma"],
                    ["astigmatism", "Astig"],
                    ["rule500", "Rule 500"],
                    ["idealIso", "Ideal ISO"],
                    ["wr", "WR"],
                    ["price", "Price"],
                  ] as [SortKey, string][]) : isLandscape ? ([
                    ["mark", "Mark"],
                    ["pick", ""],
                    ["brand", "Brand"],
                    ["fl", "Model"],
                    ["fl", "FL"],
                    ["aperture", "f/"],
                    ["aperture", "Sweet"],
                    ["cornerStopped", "CornerS"],
                    ["centerStopped", "CenterS"],
                    ["distortion", "Dist"],
                    ["flareResistance", "Flare"],
                    ["wr", "WR"],
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
                      className={key === "pick" ? styles.cellCenter : undefined}
                      onClick={key === "wr" ? undefined : () => handleSort(key)}
                      style={key === "wr" ? { cursor: "default" } : undefined}
                    >
                      {label}
                      {key !== "wr" && (
                        <span className={styles.sortIndicator}>{sortIndicator(key)}</span>
                      )}
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
                    {isNightscape && (
                      <>
                        <td>{el.effectiveFl}mm</td>
                        <td>f/{el.lens.maxAperture}</td>
                        <td><FieldVal value={el.lens.coma} /></td>
                        <td><FieldVal value={el.lens.astigmatism} /></td>
                        <td>{el.rule500}s</td>
                        <td>{fmtIso(el.idealIso)}</td>
                      </>
                    )}
                    {isLandscape && (
                      <>
                        <td>{el.effectiveFl}mm</td>
                        <td>f/{el.lens.maxAperture}</td>
                        <td>{el.lens.sweetSpotAperture ? `f/${el.lens.sweetSpotAperture}` : "\u2013"}</td>
                        <td><FieldVal value={el.lens.cornerStopped} /></td>
                        <td><FieldVal value={el.lens.centerStopped} /></td>
                        <td><FieldVal value={el.lens.distortion} /></td>
                        <td><FieldVal value={el.lens.flareResistance} /></td>
                      </>
                    )}
                    {!isNightscape && !isLandscape && (
                      <>
                        <td>{fmtIso(el.idealIso)}</td>
                        <td>{el.lens.weight}g</td>
                      </>
                    )}
                    {(isNightscape || isLandscape) && (
                      <td><span className={el.lens.isWeatherSealed ? styles.dotOn : styles.dotOff} /></td>
                    )}
                    <td>~${el.lens.price}</td>
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
                  {isNightscape && el.rule500 != null && <span>{el.rule500}s</span>}
                  {el.idealIso != null && <span>ISO {fmtIso(el.idealIso)}</span>}
                  {isNightscape && <><span>Coma <FieldVal value={el.lens.coma} /></span><span>Astig <FieldVal value={el.lens.astigmatism} /></span></>}
                  {isLandscape && <><span>CornerS <FieldVal value={el.lens.cornerStopped} /></span><span>CenterS <FieldVal value={el.lens.centerStopped} /></span></>}
                  <span>{el.lens.weight}g</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <div className={styles.footer}>
        <a href="/wiki/optical-scoring" className={styles.footerLink}>How are marks calculated?</a>
        {isNightscape && (
          <>{" · "}<a href="https://www.lightpollutionmap.info" target="_blank" rel="noopener noreferrer" className={styles.footerLink}>Find dark skies</a></>
        )}
        {isLandscape && (
          <>{" · "}<a href="/wiki/landscape-photography" className={styles.footerLink}>Landscape guide</a></>
        )}
        {" · "}FL is a creative choice, not a scoring input.
      </div>
    </div>
  );
}

export default GenreGuide;
