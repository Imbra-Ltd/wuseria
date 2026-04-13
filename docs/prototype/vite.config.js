import { defineConfig } from "vite";

export default defineConfig({
  root: "docs/prototype",
  server: {
    port: 5555,
  },
  esbuild: {
    jsx: "automatic",
    jsxImportSource: "react",
  },
});
