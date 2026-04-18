import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CameraExplorer from "./CameraExplorer";
import { makeCamera } from "../../../test/factories";

const cameras = [
  makeCamera({ model: "X-T5", year: 2022, megapixels: 40, weight: 557, price: 1500, hasIbis: true, isWeatherSealed: true }),
  makeCamera({ model: "X-T4", year: 2020, megapixels: 26, weight: 607, price: 1000, hasIbis: true, isWeatherSealed: true, isDiscontinued: true }),
  makeCamera({ model: "X-S10", year: 2020, megapixels: 26, weight: 465, price: 750, hasIbis: true, series: "X-S" }),
];

describe("CameraExplorer", () => {
  it("renders all cameras", () => {
    render(<CameraExplorer cameras={cameras} />);
    expect(screen.getAllByText("X-T5").length).toBeGreaterThan(0);
    expect(screen.getAllByText("X-T4").length).toBeGreaterThan(0);
    expect(screen.getAllByText("X-S10").length).toBeGreaterThan(0);
  });

  it("shows camera count", () => {
    render(<CameraExplorer cameras={cameras} />);
    expect(screen.getByText("3 / 3 Fujifilm cameras")).toBeInTheDocument();
  });

  it("filters by search", async () => {
    const user = userEvent.setup();
    render(<CameraExplorer cameras={cameras} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "X-T5");
    expect(screen.getAllByText("X-T5").length).toBeGreaterThan(0);
    expect(screen.queryByText("X-S10")).not.toBeInTheDocument();
  });

  it("clears filters", async () => {
    const user = userEvent.setup();
    render(<CameraExplorer cameras={cameras} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "X-T5");
    expect(screen.queryByText("X-S10")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /clear/i }));
    expect(screen.getAllByText("X-S10").length).toBeGreaterThan(0);
  });

  it("shows empty state when no matches", async () => {
    const user = userEvent.setup();
    render(<CameraExplorer cameras={cameras} />);
    await user.type(screen.getByRole("textbox", { name: /search/i }), "nonexistent");
    expect(screen.getByText("No cameras match the current filters.")).toBeInTheDocument();
  });

  it("shows price footnote", () => {
    render(<CameraExplorer cameras={cameras} />);
    expect(screen.getByText(/approximate USD estimates/)).toBeInTheDocument();
  });
});
