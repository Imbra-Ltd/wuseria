import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// vite 8 bundles Rolldown (oxc transforms), so the legacy `esbuild.jsx`
// shorthand is ignored and `.tsx` tests fail to parse ("Unexpected JSX
// expression"). `@vitejs/plugin-react` applies the React JSX transform
// independent of the underlying bundler. See #1358 (astro 6->7).
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    coverage: {
      provider: "v8",
      include: ["src/utils/**", "src/hooks/**"],
      reportsDirectory: "reports/coverage",
      reporter: ["text", "lcov", "html"],
      thresholds: {
        statements: 85,
        branches: 80,
        functions: 90,
        lines: 85,
      },
    },
  },
});
