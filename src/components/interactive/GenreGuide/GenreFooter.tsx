import type { ScoredGenre } from "../../../types/genre";
import styles from "./GenreGuide.module.css";

interface GenreFooterProps {
  genre: ScoredGenre;
}

function GenreFooter({ genre }: GenreFooterProps): React.JSX.Element {
  const text: Record<string, string> = {
    nightscape:
      " Primary: coma, astigmatism, aperture. Secondary: chromatic/spherical aberration, sharpness wide open, vignetting.",
    landscape:
      " Primary: corner + center sharpness stopped down. Secondary: distortion, CA, vignetting, flare, astigmatism, coma.",
    architecture:
      " Primary: corner + center sharpness, distortion. Secondary: lateral CA, vignetting, flare.",
    portrait:
      " Primary: bokeh, center sharpness wide open. Secondary: longitudinal CA, spherical aberration, vignetting.",
    street:
      " Primary: center sharpness stopped down, aperture. Secondary: center wide open, flare, longitudinal CA, coma.",
    travel:
      " Primary: center sharpness stopped down, weight. Secondary: aperture, flare, longitudinal CA.",
    sport:
      " Primary: center sharpness wide open. Secondary: aperture, longitudinal CA, lateral CA.",
    wildlife:
      " Primary: center sharpness wide open + stopped down. Secondary: aperture, longitudinal CA, lateral CA.",
    macro:
      " Primary: center sharpness stopped down, magnification. Secondary: distortion, CA, spherical aberration, bokeh.",
  };

  return (
    <div className={styles.footer}>
      FL is a creative choice, not a scoring input.{text[genre] ?? ""}
    </div>
  );
}

export { GenreFooter };
