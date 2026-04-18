import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LensExplorer from "./LensExplorer";
import { makeLens } from "../../../test/factories";

const lenses = [
  makeLens({ brand: "Fujifilm", model: "XF 23mm f/1.4 R", focalLengthMin: 23, focalLengthMax: 23, maxAperture: 1.4, weight: 300, price: 950, mount: "X", hasOis: false, isWeatherSealed: false }),
  makeLens({ brand: "Fujifilm", model: "XF 56mm f/1.2 R", focalLengthMin: 56, focalLengthMax: 56, maxAperture: 1.2, weight: 405, price: 1000, mount: "X", hasOis: false, isWeatherSealed: false }),
  makeLens({ brand: "Fujifilm", model: "XF 16-55mm f/2.8 R LM WR", type: "zoom", focalLengthMin: 16, focalLengthMax: 55, maxAperture: 2.8, weight: 655, price: 1200, mount: "X", hasOis: false, isWeatherSealed: true }),
];

describe("LensExplorer", () => {
  it("renders all lenses", () => {
    render(<LensExplorer lenses={lenses} />);
    expect(screen.getAllByText("XF 23mm f/1.4 R").length).toBeGreaterThan(0);
    expect(screen.getAllByText("XF 56mm f/1.2 R").length).toBeGreaterThan(0);
    expect(screen.getAllByText("XF 16-55mm f/2.8 R LM WR").length).toBeGreaterThan(0);
  });

  it("shows lens count", () => {
    render(<LensExplorer lenses={lenses} />);
    expect(screen.getByText("3 / 3 Fujifilm-compatible lenses")).toBeInTheDocument();
  });

  it("filters by search", async () => {
    const user = userEvent.setup();
    render(<LensExplorer lenses={lenses} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "56mm");
    expect(screen.getAllByText("XF 56mm f/1.2 R").length).toBeGreaterThan(0);
    expect(screen.queryByText("XF 23mm f/1.4 R")).not.toBeInTheDocument();
  });

  it("filters by type chip", async () => {
    const user = userEvent.setup();
    render(<LensExplorer lenses={lenses} />);
    await user.click(screen.getByRole("button", { name: "Zoom" }));
    expect(screen.getAllByText("XF 16-55mm f/2.8 R LM WR").length).toBeGreaterThan(0);
    expect(screen.queryByText("XF 23mm f/1.4 R")).not.toBeInTheDocument();
  });

  it("clears filters", async () => {
    const user = userEvent.setup();
    render(<LensExplorer lenses={lenses} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "56mm");
    expect(screen.queryByText("XF 23mm f/1.4 R")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /clear/i }));
    expect(screen.getAllByText("XF 23mm f/1.4 R").length).toBeGreaterThan(0);
  });

  it("shows empty state when no matches", async () => {
    const user = userEvent.setup();
    render(<LensExplorer lenses={lenses} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "nonexistent");
    expect(screen.getByText("No lenses match the current filters.")).toBeInTheDocument();
  });

  it("shows price footnote", () => {
    render(<LensExplorer lenses={lenses} />);
    expect(screen.getByText(/approximate USD estimates/)).toBeInTheDocument();
  });
});
