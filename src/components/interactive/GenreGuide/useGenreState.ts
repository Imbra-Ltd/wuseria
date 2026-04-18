import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import type { ScoredGenre } from "../../../types/genre";
import {
  evScenes,
  genreSceneFilter,
  FL_CHIPS_X,
  FL_CHIPS_GFX,
  FL_RANGES_X,
  FL_RANGES_GFX,
  GENRE_DEFAULTS,
  NIGHTSCAPE_ISO_BY_EV,
} from "../../../data/genres";
import type { SortKey } from "./types";

function useGenreState(defaultGenre: ScoredGenre) {
  const [genre, setGenre] = useState<ScoredGenre>(defaultGenre);
  const defaults = GENRE_DEFAULTS[genre];
  const [ev, setEv] = useState(defaults.ev);
  const [iso, setIso] = useState(defaults.iso);
  const [nd, setNd] = useState<number[]>([]);
  const [cropFactor, setCropFactor] = useState(1.5);
  const [selectedFl, setSelectedFl] = useState(defaults.fl);
  const [magnification, setMagnification] = useState(1.0);
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
  const [bokehFilter, setBokehFilter] = useState("");
  const [locaFilter, setLocaFilter] = useState("");
  const [latcaFilter, setLatcaFilter] = useState("");
  const sceneListRef = useRef<HTMLDivElement>(null);

  const isNightscape = genre === "nightscape";
  const isLandscape = genre === "landscape";
  const isArchitecture = genre === "architecture";
  const isPortrait = genre === "portrait";
  const isStreet = genre === "street";
  const isSport = genre === "sport";
  const isWildlife = genre === "wildlife";
  const isTravel = genre === "travel";
  const FL_CHIPS = cropFactor === 0.79 ? FL_CHIPS_GFX : FL_CHIPS_X;
  const FL_RANGES = cropFactor === 0.79 ? FL_RANGES_GFX : FL_RANGES_X;

  function handleGenreChange(g: ScoredGenre): void {
    setGenre(g);
    const d = GENRE_DEFAULTS[g];
    setEv(d.ev);
    setIso(d.iso);
    setSelectedFl(d.fl);
    setNd([]);
    setMagnification(1.0);
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
    setBokehFilter("");
    setLocaFilter("");
    setLatcaFilter("");
  }

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

  const visibleScenes = useMemo(
    () => evScenes.filter((s) => genreSceneFilter[genre](s.ev)),
    [genre],
  );

  function handleSort(key: SortKey): void {
    if (sortBy === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(key);
      setSortAsc(key === "brand" || key === "fl" || key === "price" || key === "weight" || key === "idealIso");
    }
  }

  function toggleNd(factor: number): void {
    setNd((prev) =>
      prev.includes(factor) ? prev.filter((f) => f !== factor) : [...prev, factor],
    );
  }

  function clearFilters(): void {
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
    setBokehFilter("");
    setLocaFilter("");
    setLatcaFilter("");
  }

  const hasFilters = !!(brandFilter || markFilter || priceFilter || weightFilter || apertureFilter || comaFilter || astigFilter || typeFilter || wrFilter || cornerFilter || distFilter || flareFilter || bokehFilter || locaFilter || latcaFilter);

  const flChips = FL_CHIPS.default;

  return {
    genre, ev, setEv, iso, setIso, nd, cropFactor, setCropFactor,
    selectedFl, setSelectedFl, magnification, setMagnification,
    sortBy, sortAsc,
    brandFilter, setBrandFilter, markFilter, setMarkFilter,
    priceFilter, setPriceFilter, weightFilter, setWeightFilter,
    apertureFilter, setApertureFilter, comaFilter, setComaFilter,
    astigFilter, setAstigFilter, typeFilter, setTypeFilter,
    wrFilter, setWrFilter, cornerFilter, setCornerFilter,
    distFilter, setDistFilter, flareFilter, setFlareFilter,
    bokehFilter, setBokehFilter, locaFilter, setLocaFilter,
    latcaFilter, setLatcaFilter,
    sceneListRef, visibleScenes, flChips,
    isNightscape, isLandscape, isArchitecture, isPortrait,
    isStreet, isSport, isWildlife, isTravel,
    FL_CHIPS, FL_RANGES,
    handleGenreChange, handleSort, toggleNd, clearFilters, hasFilters,
    NIGHTSCAPE_ISO_BY_EV,
  };
}

type GenreState = ReturnType<typeof useGenreState>;

export { useGenreState };
export type { GenreState };
