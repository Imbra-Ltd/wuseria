import { defineConfig } from "vitest/config";

export default defineConfig({
  esbuild: {
    jsx: "automatic",
    jsxImportSource: "react",
  },
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
