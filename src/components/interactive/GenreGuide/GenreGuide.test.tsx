import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GenreGuide from "./GenreGuide";
import type { Lens } from "../../../types/lens";
import { makeLens } from "../../../test/factories";

const testLenses: Lens[] = [
  makeLens({
    brand: "Fujifilm",
    model: "XF 23mm f/1.4",
    focalLengthMin: 23,
    focalLengthMax: 23,
    maxAperture: 1.4,
    weight: 300,
    price: 950,
    genreMarks: { nightscape: 4, street: 4, portrait: 3, landscape: 3.5 },
    editorialPicks: ["street"],
    cornerStopped: 1.5,
    centerStopped: 2.0,
    distortion: 1.5,
    flareResistance: 1.0,
  }),
  makeLens({
    brand: "Fujifilm",
    model: "XF 16mm f/1.4",
    focalLengthMin: 16,
    focalLengthMax: 16,
    maxAperture: 1.4,
    weight: 375,
    price: 1000,
    genreMarks: { nightscape: 4, street: 4, portrait: 3, landscape: 4 },
    editorialPicks: ["nightscape", "street", "landscape"],
    cornerStopped: 1.5,
    centerStopped: 2.0,
    distortion: 1.0,
    flareResistance: 1.5,
    isWeatherSealed: true,
  }),
  makeLens({
    brand: "Fujifilm",
    model: "XF 90mm f/2.0",
    focalLengthMin: 90,
    focalLengthMax: 90,
    maxAperture: 2.0,
    weight: 540,
    price: 800,
    genreMarks: { portrait: 5, sport: 3 },
    editorialPicks: ["portrait"],
  }),
  makeLens({
    brand: "Samyang",
    model: "12mm f/2",
    focalLengthMin: 12,
    focalLengthMax: 12,
    maxAperture: 2.0,
    weight: 260,
    price: 410,
    genreMarks: { nightscape: 4, street: 4 },
    editorialPicks: ["nightscape"],
  }),
];

// =============================================================================
// TESTS
// =============================================================================

describe("GenreGuide", () => {
  it("renders with default genre (street)", () => {
    render(<GenreGuide lenses={testLenses} />);
    expect(screen.getByRole("tab", { name: /street/i, selected: true })).toBeInTheDocument();
  });

  it("renders with a specified default genre", () => {
    render(<GenreGuide lenses={testLenses} defaultGenre="nightscape" />);
    expect(screen.getByRole("tab", { name: /nightscape/i, selected: true })).toBeInTheDocument();
  });

  it("shows genre tabs for all 9 genres", () => {
    render(<GenreGuide lenses={testLenses} />);
    const tablist = screen.getByRole("tablist");
    const tabs = within(tablist).getAllByRole("tab");
    expect(tabs).toHaveLength(9);
  });

  it("switches genre when tab is clicked", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} />);

    await user.click(screen.getByRole("tab", { name: /portrait/i }));
    expect(screen.getByRole("tab", { name: /portrait/i, selected: true })).toBeInTheDocument();
  });

  it("shows mark pips for scored lenses", () => {
    render(<GenreGuide lenses={testLenses} defaultGenre="nightscape" />);
    const pips = screen.getAllByLabelText(/Mark \d of 5/);
    expect(pips.length).toBeGreaterThan(0);
  });

  it("shows filter panel with dropdowns", () => {
    render(<GenreGuide lenses={testLenses} defaultGenre="portrait" />);
    expect(screen.getAllByText("Mark").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Price")).toBeInTheDocument();
  });

  it("displays footnote about scoring methodology", () => {
    render(<GenreGuide lenses={testLenses} />);
    expect(
      screen.getByText(/FL is a creative choice/),
    ).toBeInTheDocument();
  });

  it("shows mount toggle (X-Mount / GFX)", () => {
    render(<GenreGuide lenses={testLenses} />);
    expect(screen.getByText("X-Mount")).toBeInTheDocument();
    expect(screen.getByText("GFX")).toBeInTheDocument();
  });

  it("shows ISO chips", () => {
    render(<GenreGuide lenses={testLenses} />);
    expect(screen.getByText("ISO")).toBeInTheDocument();
    expect(screen.getByText("1600")).toBeInTheDocument();
  });

  it("shows scene list", () => {
    render(<GenreGuide lenses={testLenses} />);
    expect(screen.getByText(/Scene/)).toBeInTheDocument();
  });

  it("switches to landscape and shows landscape-specific columns", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} />);

    await user.click(screen.getByRole("tab", { name: /landscape/i }));
    expect(screen.getByRole("tab", { name: /landscape/i, selected: true })).toBeInTheDocument();
  });

  it("shows landscape scoring explanation when landscape is selected", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} />);

    await user.click(screen.getByRole("tab", { name: /landscape/i }));
    expect(
      screen.getByText(/corner \+ center sharpness stopped down/),
    ).toBeInTheDocument();
  });

  it("shows landscape-specific filters when landscape is selected", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} />);

    await user.click(screen.getByRole("tab", { name: /landscape/i }));
    expect(screen.getAllByText("CornerS").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Dist").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Flare").length).toBeGreaterThanOrEqual(1);
  });

  it("shows shutter speed matrix for landscape", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} />);

    await user.click(screen.getByRole("tab", { name: /landscape/i }));
    expect(screen.getByText(/EV Matrix.*Tripod/)).toBeInTheDocument();
  });
});
