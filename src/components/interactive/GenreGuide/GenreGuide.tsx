import { genreConfigs, GENRE_EQUIPMENT, NIGHTSCAPE_ISO_BY_EV } from "../../../data/genres";
import { ExposureMatrix } from "./ExposureMatrix";
import { LandscapeMatrix } from "./LandscapeMatrix";
import { ArchitectureMatrix } from "./ArchitectureMatrix";
import { HandheldMatrix } from "./HandheldMatrix";
import { SportMatrix } from "./SportMatrix";
import { GenreControls } from "./GenreControls";
import { GenreFilterPanel } from "./GenreFilterPanel";
import { GenreTable } from "./GenreTable";
import { GenreCards } from "./GenreCards";
import { GenreFooter } from "./GenreFooter";
import type { GenreGuideProps } from "./types";
import { SCORED_GENRES } from "./types";
import { sceneLabel, evHeaderLabel } from "./helpers";
import { useGenreState } from "./useGenreState";
import { useEnrichedLenses } from "./useEnrichedLenses";
import styles from "./GenreGuide.module.css";

function GenreGuide({ lenses, defaultGenre = "street" }: GenreGuideProps) {
  const state = useGenreState(defaultGenre);
  const enrichedLenses = useEnrichedLenses(lenses, state);
  const {
    genre, ev, setEv, iso, setIso, nd, cropFactor, selectedFl,
    magnification, sceneListRef, visibleScenes,
    isNightscape, isLandscape, isArchitecture, isPortrait,
    isStreet, isTravel, isSport, isWildlife,
    handleGenreChange,
  } = state;

  return (
    <div className={styles.guide}>
      <div className={styles.hero}>
        <h1 className={styles.heroTitle}>{genreConfigs[genre].name} Screener</h1>
      </div>
      <div className={styles.genreTabs} role="tablist" aria-label="Photography genres">
        {SCORED_GENRES.map((g) => (
          <button
            key={g} type="button" role="tab" aria-selected={genre === g}
            className={`${styles.genreTab} ${genre === g ? styles.genreTabActive : ""}`}
            onClick={() => handleGenreChange(g)}
          >
            {genreConfigs[g].name.replace("Astrophotography", "Astronomy").replace(" Photography", "")}
          </button>
        ))}
      </div>

      <div className={styles.layout}>
        <div className={styles.sidebar}>
          <div className={styles.sidebarPanel}>
            <div className={styles.sidebarTitle}>EV / Scene</div>
            <div className={styles.sceneList} ref={sceneListRef}>
              {visibleScenes.map((s) => (
                <button
                  key={s.ev} type="button" data-ev={s.ev}
                  className={`${styles.sceneItem} ${ev === s.ev ? styles.sceneItemActive : ""}`}
                  onClick={() => {
                    setEv(s.ev);
                    if (isNightscape && NIGHTSCAPE_ISO_BY_EV[s.ev] != null) setIso(NIGHTSCAPE_ISO_BY_EV[s.ev]);
                  }}
                >
                  <span className={styles.sceneEv}>{s.ev}</span>
                  <span className={styles.sceneText}>{sceneLabel(genre, s.ev)}</span>
                </button>
              ))}
            </div>
          </div>
          <div className={`${styles.sidebarPanel} ${styles.sidebarBottom}`}>
            <div className={styles.sidebarTitle}>Equipment</div>
            <div className={styles.equipmentList}>{GENRE_EQUIPMENT[genre]?.join(" \u00B7 ")}</div>
          </div>
        </div>

        <div className={styles.main}>
          <div className={styles.controlPanel}>
            <div className={styles.evHeader}>
              <span className={styles.evLabel}>EV {ev} — {evHeaderLabel(genre, ev)}</span>
            </div>
            <GenreControls state={state} />
          </div>

          {isNightscape && <div className={styles.matrixPanel}><ExposureMatrix cropFactor={cropFactor} iso={iso} ev={ev} selectedFl={selectedFl} /></div>}
          {isLandscape && <div className={styles.matrixPanel}><LandscapeMatrix cropFactor={cropFactor} iso={iso} ev={ev} nd={nd} selectedFl={selectedFl} /></div>}
          {isArchitecture && <div className={styles.matrixPanel}><ArchitectureMatrix cropFactor={cropFactor} iso={iso} ev={ev} nd={nd} selectedFl={selectedFl} /></div>}
          {(isPortrait || isStreet || isTravel) && <div className={styles.matrixPanel}><HandheldMatrix cropFactor={cropFactor} iso={iso} ev={ev} selectedFl={selectedFl} genre={genre as "street" | "travel" | "portrait"} /></div>}
          {(isSport || isWildlife) && <div className={styles.matrixPanel}><SportMatrix cropFactor={cropFactor} iso={iso} ev={ev} selectedFl={selectedFl} genre={genre as "sport" | "wildlife"} /></div>}
          {genre === "macro" && <div className={styles.matrixPanel}><HandheldMatrix cropFactor={cropFactor} iso={iso} ev={ev} selectedFl={selectedFl} genre="macro" magnification={magnification} /></div>}

          <div className={styles.learnMoreLinks}>
            <a href="/wiki/optical-scoring" className={styles.learnMoreBtn}>How marks work</a>
            <a href={`/wiki/${genre}-photography`} className={styles.learnMoreBtn}>{genreConfigs[genre].name.replace(" Photography", "")} guide</a>
            {isNightscape && <a href="https://www.lightpollutionmap.info" target="_blank" rel="noopener noreferrer" className={styles.learnMoreBtn}>Find dark skies</a>}
          </div>
        </div>
      </div>

      <GenreFilterPanel state={state} enrichedLenses={enrichedLenses} />

      {enrichedLenses.length === 0 ? (
        <p className={styles.emptyState}>No lenses match the current settings.</p>
      ) : (
        <>
          <GenreTable state={state} enrichedLenses={enrichedLenses} />
          <GenreCards state={state} enrichedLenses={enrichedLenses} />
        </>
      )}

      <GenreFooter genre={genre} />
    </div>
  );
}

export default GenreGuide;
