import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LensExplorer from "./LensExplorer";
import { makeExplorerLens } from "../../../test/factories";

const lenses = [
  makeExplorerLens({
    brand: "Fujifilm",
    model: "XF 23mm f/1.4 R",
    focalLengthMin: 23,
    focalLengthMax: 23,
    maxAperture: 1.4,
    weight: 300,
    price: 950,
  }),
  makeExplorerLens({
    brand: "Fujifilm",
    model: "XF 56mm f/1.2 R",
    focalLengthMin: 56,
    focalLengthMax: 56,
    maxAperture: 1.2,
    weight: 405,
    price: 1000,
  }),
  makeExplorerLens({
    brand: "Fujifilm",
    model: "XF 16-55mm f/2.8 R LM WR",
    type: "zoom",
    focalLengthMin: 16,
    focalLengthMax: 55,
    maxAperture: 2.8,
    weight: 655,
    price: 1200,
    isWeatherSealed: true,
  }),
];

describe("LensExplorer", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", window.location.pathname);
  });

  it("renders all lenses", () => {
    render(<LensExplorer lenses={lenses} />);
    expect(screen.getAllByText("XF 23mm f/1.4 R").length).toBeGreaterThan(0);
    expect(screen.getAllByText("XF 56mm f/1.2 R").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText("XF 16-55mm f/2.8 R LM WR").length,
    ).toBeGreaterThan(0);
  });

  it("shows lens count", () => {
    render(<LensExplorer lenses={lenses} />);
    expect(
      screen.getByText("3 / 3 Fujifilm-compatible lenses"),
    ).toBeInTheDocument();
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
    expect(
      screen.getAllByText("XF 16-55mm f/2.8 R LM WR").length,
    ).toBeGreaterThan(0);
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
    await user.type(
      screen.getByRole("textbox", { name: /search/i }),
      "nonexistent",
    );
    expect(
      screen.getByText("No lenses match the current filters."),
    ).toBeInTheDocument();
  });

  it("OIS filter works after sorting", async () => {
    const user = userEvent.setup();
    const testLenses = [
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 16mm f/1.4 R WR",
        hasOis: false,
        isWeatherSealed: true,
        price: 1000,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 18-120mm f/4 LM PZ WR",
        type: "zoom",
        focalLengthMin: 18,
        focalLengthMax: 120,
        hasOis: true,
        isWeatherSealed: true,
        price: 900,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 50mm f/2 R WR",
        hasOis: false,
        isWeatherSealed: true,
        price: 450,
      }),
    ];
    render(<LensExplorer lenses={testLenses} />);

    // Sort by price first
    const table = screen.getAllByRole("table")[0];
    const priceButton = within(table).getByRole("button", { name: /price/i });
    await user.click(priceButton);

    // Now filter by OIS — first "Yes" button is OIS (before WR in markup)
    const yesButtons = screen.getAllByRole("button", { name: "Yes" });
    await user.click(yesButtons[0]);

    // Only the OIS lens should remain
    expect(
      screen.getAllByText("XF 18-120mm f/4 LM PZ WR").length,
    ).toBeGreaterThan(0);
    expect(screen.queryByText("XF 16mm f/1.4 R WR")).not.toBeInTheDocument();
    expect(screen.queryByText("XF 50mm f/2 R WR")).not.toBeInTheDocument();
  });

  it("OIS column sort toggles between asc and desc", async () => {
    const user = userEvent.setup();
    const testLenses = [
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 16mm f/1.4 R WR",
        hasOis: false,
        price: 1000,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 18-120mm f/4 LM PZ WR",
        type: "zoom",
        focalLengthMin: 18,
        focalLengthMax: 120,
        hasOis: true,
        price: 900,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 50mm f/2 R WR",
        hasOis: false,
        price: 450,
      }),
    ];
    render(<LensExplorer lenses={testLenses} />);

    const table = screen.getAllByRole("table")[0];
    const oisButton = within(table).getByRole("button", { name: /OIS/i });

    // First click → descending (true/green before false)
    await user.click(oisButton);
    const rowsDesc = within(table).getAllByRole("row").slice(1);
    const modelsDesc = rowsDesc.map(
      (row) => within(row).getByRole("link").textContent,
    );
    expect(modelsDesc[0]).toBe("XF 18-120mm f/4 LM PZ WR");

    // Second click → ascending (false before true)
    await user.click(oisButton);
    const rowsAsc = within(table).getAllByRole("row").slice(1);
    const modelsAsc = rowsAsc.map(
      (row) => within(row).getByRole("link").textContent,
    );
    expect(modelsAsc).not.toEqual(modelsDesc);
  });

  it("filters by mount chip", async () => {
    const user = userEvent.setup();
    const testLenses = [
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 23mm f/1.4 R",
        mount: "X",
        price: 950,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "GF 63mm f/2.8 R WR",
        mount: "GFX",
        price: 1500,
      }),
    ];
    render(<LensExplorer lenses={testLenses} />);
    // Mount chips: "All", "X", "GFX"
    const gfxButtons = screen.getAllByRole("button", { name: "GFX" });
    await user.click(gfxButtons[0]);
    expect(screen.getAllByText("GF 63mm f/2.8 R WR").length).toBeGreaterThan(0);
    expect(screen.queryByText("XF 23mm f/1.4 R")).not.toBeInTheDocument();
  });

  it("filters by focal length select", async () => {
    const user = userEvent.setup();
    const testLenses = [
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 14mm f/2.8 R",
        focalLengthMin: 14,
        focalLengthMax: 14,
        price: 800,
      }),
      makeExplorerLens({
        brand: "Fujifilm",
        model: "XF 90mm f/2 R LM WR",
        focalLengthMin: 90,
        focalLengthMax: 90,
        price: 800,
      }),
    ];
    render(<LensExplorer lenses={testLenses} />);
    const flSelect = screen.getByRole("combobox", {
      name: /focal length/i,
    });
    await user.selectOptions(flSelect, "36-100");
    expect(screen.getAllByText("XF 90mm f/2 R LM WR").length).toBeGreaterThan(
      0,
    );
    expect(screen.queryByText("XF 14mm f/2.8 R")).not.toBeInTheDocument();
  });

  it("sorts by price when Price header is clicked", async () => {
    const user = userEvent.setup();
    render(<LensExplorer lenses={lenses} />);

    const table = screen.getAllByRole("table")[0];
    const priceButton = within(table).getByRole("button", { name: /price/i });

    // Click once — ascending
    await user.click(priceButton);
    const rowsAsc = within(table).getAllByRole("row").slice(1); // skip thead row
    const modelsAsc = rowsAsc.map(
      (row) => within(row).getByRole("link").textContent,
    );
    expect(modelsAsc).toEqual([
      "XF 23mm f/1.4 R",
      "XF 56mm f/1.2 R",
      "XF 16-55mm f/2.8 R LM WR",
    ]);

    // Click again — descending
    await user.click(priceButton);
    const rowsDesc = within(table).getAllByRole("row").slice(1);
    const modelsDesc = rowsDesc.map(
      (row) => within(row).getByRole("link").textContent,
    );
    expect(modelsDesc).toEqual([
      "XF 16-55mm f/2.8 R LM WR",
      "XF 56mm f/1.2 R",
      "XF 23mm f/1.4 R",
    ]);
  });
});
