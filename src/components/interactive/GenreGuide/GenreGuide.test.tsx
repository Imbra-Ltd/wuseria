import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GenreGuide from "./GenreGuide";
import type { GenreLens } from "./types";
import { makeLens } from "../../../test/factories";

const testLenses: GenreLens[] = [
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
    expect(
      screen.getByRole("tab", { name: /street/i, selected: true }),
    ).toBeInTheDocument();
  });

  it("renders with a specified default genre", () => {
    render(<GenreGuide lenses={testLenses} defaultGenre="nightscape" />);
    expect(
      screen.getByRole("tab", { name: /nightscape/i, selected: true }),
    ).toBeInTheDocument();
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
    expect(
      screen.getByRole("tab", { name: /portrait/i, selected: true }),
    ).toBeInTheDocument();
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
    expect(screen.getByText(/FL is a creative choice/)).toBeInTheDocument();
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
    expect(
      screen.getByRole("tab", { name: /landscape/i, selected: true }),
    ).toBeInTheDocument();
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

  it("filters by mark threshold", async () => {
    const user = userEvent.setup();
    // Street default FL=24, range [16,27] → XF 23mm (mark 4) + XF 16mm (mark 4) visible
    // Filter mark >= 5 should exclude both (marks are 4)
    render(<GenreGuide lenses={testLenses} defaultGenre="street" />);

    // Verify lenses render before filtering
    expect(screen.getAllByText("XF 23mm f/1.4").length).toBeGreaterThan(0);

    const selects = screen.getAllByRole("combobox");
    const markSelect = selects.find(
      (s) => s.querySelector("option[value='4.5']") !== null,
    );
    expect(markSelect).toBeDefined();
    await user.selectOptions(markSelect!, "5");

    // Both have mark=4, so neither passes >= 5
    expect(screen.queryByText("XF 23mm f/1.4")).not.toBeInTheDocument();
    expect(screen.queryByText("XF 16mm f/1.4")).not.toBeInTheDocument();
  });

  it("filters by price threshold", async () => {
    const user = userEvent.setup();
    // Street default FL=24, range [16,27] → XF 23mm ($950) + XF 16mm ($1000)
    render(<GenreGuide lenses={testLenses} defaultGenre="street" />);

    // Verify lenses render before filtering
    expect(screen.getAllByText("XF 23mm f/1.4").length).toBeGreaterThan(0);

    // Price filter "≤ ~$500" should exclude both ($950 and $1000)
    // Use value='4000' to identify the price select (unique to PRICE_THRESHOLDS)
    const selects = screen.getAllByRole("combobox");
    const priceSelect = selects.find(
      (s) => s.querySelector("option[value='4000']") !== null,
    );
    expect(priceSelect).toBeDefined();
    await user.selectOptions(priceSelect!, "500");

    expect(screen.queryByText("XF 23mm f/1.4")).not.toBeInTheDocument();
    expect(screen.queryByText("XF 16mm f/1.4")).not.toBeInTheDocument();
  });

  it("filters by type (prime/zoom)", async () => {
    const user = userEvent.setup();
    render(<GenreGuide lenses={testLenses} defaultGenre="street" />);

    // All test lenses are primes — filter for zoom should show empty
    const selects = screen.getAllByRole("combobox");
    const typeSelect = selects.find(
      (s) => s.querySelector("option[value='zoom']") !== null,
    );
    expect(typeSelect).toBeDefined();
    await user.selectOptions(typeSelect!, "zoom");

    // No lenses match — cards/table should be empty
    expect(screen.queryByText("XF 23mm f/1.4")).not.toBeInTheDocument();
    expect(screen.queryByText("XF 16mm f/1.4")).not.toBeInTheDocument();
  });
});
