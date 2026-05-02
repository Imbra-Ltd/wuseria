import type { GenreState } from "./useGenreState";
import type { EnrichedLens } from "./types";
import {
  FilterSelect,
  MIN_THRESHOLDS,
  APERTURE_THRESHOLDS,
  MARK_THRESHOLDS,
  WEIGHT_THRESHOLDS,
  PRICE_THRESHOLDS,
} from "./FilterSelect";
import styles from "./GenreGuide.module.css";

interface GenreFilterPanelProps {
  state: GenreState;
  enrichedLenses: EnrichedLens[];
}

function GenreFilterPanel({ state, enrichedLenses }: GenreFilterPanelProps) {
  const {
    isNightscape,
    isLandscape,
    isArchitecture,
    isPortrait,
    isStreet,
    markFilter,
    setMarkFilter,
    typeFilter,
    setTypeFilter,
    brandFilter,
    setBrandFilter,
    apertureFilter,
    setApertureFilter,
    comaFilter,
    setComaFilter,
    astigFilter,
    setAstigFilter,
    cornerFilter,
    setCornerFilter,
    distFilter,
    setDistFilter,
    latcaFilter,
    setLatcaFilter,
    flareFilter,
    setFlareFilter,
    bokehFilter,
    setBokehFilter,
    locaFilter,
    setLocaFilter,
    weightFilter,
    setWeightFilter,
    wrFilter,
    setWrFilter,
    priceFilter,
    setPriceFilter,
    hasFilters,
    clearFilters,
  } = state;

  const brandOptions = [...new Set(enrichedLenses.map((el) => el.lens.brand))]
    .sort()
    .map((b) => ({ label: b, value: b }));

  return (
    <div className={styles.filterPanel}>
      <FilterSelect
        label="Mark"
        value={markFilter}
        onChange={setMarkFilter}
        allLabel="All"
        options={MARK_THRESHOLDS}
      />
      <FilterSelect
        label="Type"
        value={typeFilter}
        onChange={setTypeFilter}
        allLabel="All"
        options={[
          { label: "Prime", value: "prime" },
          { label: "Zoom", value: "zoom" },
        ]}
      />
      <FilterSelect
        label="Brand"
        value={brandFilter}
        onChange={setBrandFilter}
        allLabel="All"
        options={brandOptions}
      />

      {isNightscape && (
        <FilterSelect
          label="f/"
          value={apertureFilter}
          onChange={setApertureFilter}
          options={APERTURE_THRESHOLDS}
        />
      )}
      {isNightscape && (
        <FilterSelect
          label="Coma"
          value={comaFilter}
          onChange={setComaFilter}
          options={MIN_THRESHOLDS}
        />
      )}
      {isNightscape && (
        <FilterSelect
          label="Astig"
          value={astigFilter}
          onChange={setAstigFilter}
          options={MIN_THRESHOLDS}
        />
      )}

      {(isLandscape || isArchitecture) && (
        <FilterSelect
          label="CornerS"
          value={cornerFilter}
          onChange={setCornerFilter}
          options={MIN_THRESHOLDS}
        />
      )}
      {(isLandscape || isArchitecture) && (
        <FilterSelect
          label="Dist"
          value={distFilter}
          onChange={setDistFilter}
          options={MIN_THRESHOLDS}
        />
      )}
      {isArchitecture && (
        <FilterSelect
          label="LatCA"
          value={latcaFilter}
          onChange={setLatcaFilter}
          options={MIN_THRESHOLDS}
        />
      )}
      {(isLandscape || isStreet) && (
        <FilterSelect
          label="Flare"
          value={flareFilter}
          onChange={setFlareFilter}
          options={MIN_THRESHOLDS}
        />
      )}

      {isPortrait && (
        <FilterSelect
          label="Bokeh"
          value={bokehFilter}
          onChange={setBokehFilter}
          options={MIN_THRESHOLDS}
        />
      )}
      {isPortrait && (
        <FilterSelect
          label="LoCA"
          value={locaFilter}
          onChange={setLocaFilter}
          options={MIN_THRESHOLDS}
        />
      )}

      {isStreet && (
        <FilterSelect
          label="f/"
          value={apertureFilter}
          onChange={setApertureFilter}
          options={APERTURE_THRESHOLDS}
        />
      )}
      {isStreet && (
        <FilterSelect
          label="Coma"
          value={comaFilter}
          onChange={setComaFilter}
          options={MIN_THRESHOLDS}
        />
      )}

      {!isNightscape && !isLandscape && !isArchitecture && !isPortrait && (
        <FilterSelect
          label="Wt"
          value={weightFilter}
          onChange={setWeightFilter}
          options={WEIGHT_THRESHOLDS}
        />
      )}
      {(isNightscape || isLandscape || isArchitecture) && (
        <FilterSelect
          label="WR"
          value={wrFilter}
          onChange={setWrFilter}
          allLabel="All"
          options={[
            { label: "Yes", value: "yes" },
            { label: "No", value: "no" },
          ]}
        />
      )}

      <FilterSelect
        label="Price"
        value={priceFilter}
        onChange={setPriceFilter}
        options={PRICE_THRESHOLDS}
      />

      {hasFilters && (
        <button
          type="button"
          className={styles.clearBtn}
          onClick={clearFilters}
        >
          &#x2715; clear
        </button>
      )}
    </div>
  );
}

export { GenreFilterPanel };
