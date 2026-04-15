import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const wiki = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/wiki" }),
  schema: z.object({
    title: z.string(),
    fullTitle: z.string().optional(),
    category: z.enum([
      "Camera",
      "Composition",
      "Exposure",
      "Focus",
      "Geometry",
      "Lenses",
      "Lighting",
      "Optics",
      "Sensor",
    ]),
    summary: z.string(),
    related: z.array(z.string()).optional(),
  }),
});

export const collections = { wiki };
