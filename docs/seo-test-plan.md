# SEO Manual Test Plan

Periodic checklist for monitoring indexing, discoverability, and technical SEO health.

## 1. Google Search Console (GSC)

### 1.1 Sitemap

- [ ] Sitemap submitted at `sitemap-index.xml`
- [ ] Status shows "Success" (no errors)
- [ ] Discovered URLs match expected page count (~458)
- [ ] No sitemap warnings or errors

### 1.2 Coverage / Indexing

- [ ] Check **Pages > Indexed** count — trending upward
- [ ] Review **Pages > Not indexed** — check reasons:
  - "Discovered - currently not indexed" — crawl budget issue
  - "Crawled - currently not indexed" — thin content signal
  - "Excluded by noindex tag" — should be zero
  - "Blocked by robots.txt" — should be zero
  - "Redirect" — check for unexpected redirects
  - "Duplicate without user-selected canonical" — investigate
- [ ] No pages stuck in "Discovered" for >2 weeks

### 1.3 Enhancements

- [ ] **Structured data** — no errors on Product or Article types
- [ ] No "unparsable structured data" warnings
- [ ] Check rich result eligibility for Product pages

### 1.4 Experience

- [ ] Core Web Vitals — no "Poor" URLs
- [ ] Mobile usability — no errors
- [ ] HTTPS — all pages served over HTTPS

### 1.5 Links

- [ ] Review **Links > Top linked pages** — confirm section hubs rank high
- [ ] Review **Links > External links** — track backlink growth

### 1.6 Search performance

- [ ] Check **Performance > Search results** for impressions trend
- [ ] Note top queries and pages — identify content gaps
- [ ] Compare impressions vs clicks — low CTR pages may need better titles/descriptions

## 2. Umami Analytics

### 2.1 Traffic

- [ ] Verify tracking script fires on page load (check network tab)
- [ ] Compare Umami pageviews with GSC impressions — large discrepancy means tracking gaps
- [ ] Check bounce rate on key landing pages (homepage, /lenses/, /genre/)

### 2.2 Navigation patterns

- [ ] Review top pages — do users reach individual lens/camera pages?
- [ ] Check referrers — any organic search traffic appearing?
- [ ] Review device split — confirm mobile vs desktop ratio

### 2.3 Engagement

- [ ] Average visit duration — is it increasing?
- [ ] Pages per visit — are users exploring beyond landing page?
- [ ] Check exit pages — identify where users leave

## 3. Technical SEO (manual spot checks)

### 3.1 Meta tags

Pick 1 page from each section (homepage, lens, camera, accessory, genre, wiki):

- [ ] `<title>` is unique and descriptive (50-60 chars)
- [ ] `<meta name="description">` is unique (120-160 chars)
- [ ] `<link rel="canonical">` points to correct URL with trailing slash
- [ ] `og:title`, `og:description`, `og:url`, `og:image` present
- [ ] `twitter:card`, `twitter:title`, `twitter:description` present
- [ ] `twitter:image` present (currently missing — see #507)

### 3.2 Structured data

Validate with [Google Rich Results Test](https://search.google.com/test/rich-results):

- [ ] `/lenses/fujifilm-xf-23mm-f1-4-r-lm-wr/` — valid Product schema
- [ ] `/cameras/x-t5/` — valid Product schema
- [ ] `/accessories/fujifilm-np-w235/` — valid Product schema
- [ ] `/wiki/aperture/` — valid Article schema
- [ ] No errors or warnings

### 3.3 Trailing slashes

- [ ] `https://wuseria.com/lenses` redirects to `/lenses/` (301, not 302)
- [ ] No double-slash URLs (e.g., `/lenses//xf-23mm/`)
- [ ] Internal links in HTML output all end with `/`

### 3.4 Canonical consistency

- [ ] Canonical URL matches the actual page URL
- [ ] No `www` vs non-`www` conflicts
- [ ] HTTP requests redirect to HTTPS

### 3.5 robots.txt and sitemap

- [ ] `https://wuseria.com/robots.txt` is accessible
- [ ] `https://wuseria.com/sitemap-index.xml` is accessible
- [ ] `https://wuseria.com/sitemap-0.xml` is accessible
- [ ] Sitemap URL count matches build output
- [ ] All sitemap URLs use trailing slashes
- [ ] All sitemap URLs use HTTPS

### 3.6 404 handling

- [ ] Non-existent URL (e.g., `/lenses/does-not-exist/`) returns 404 status
- [ ] Custom 404 page renders with back-to-home link

## 4. Lighthouse

Run against production (`https://wuseria.com`):

```bash
npx @lhci/cli@latest autorun
```

- [ ] Performance >= 80
- [ ] Accessibility >= 90
- [ ] SEO >= 90
- [ ] Best Practices >= 90

Spot-check these pages:

| Page            | URL                                      |
| --------------- | ---------------------------------------- |
| Homepage        | `/`                                      |
| Lenses index    | `/lenses/`                               |
| Individual lens | `/lenses/fujifilm-xf-23mm-f1-4-r-lm-wr/` |
| Cameras index   | `/cameras/`                              |
| Genre index     | `/genre/`                                |
| Genre page      | `/genre/landscape/`                      |
| Wiki index      | `/wiki/`                                 |
| Wiki article    | `/wiki/aperture/`                        |

## 5. External tools (periodic)

### 5.1 Google "site:" search

- [ ] Search `site:wuseria.com` — count matches expected indexed pages
- [ ] Search `site:wuseria.com/lenses/` — lens pages appearing
- [ ] Search `site:wuseria.com/wiki/` — wiki pages appearing

### 5.2 Social card preview

Test with [OpenGraph.xyz](https://www.opengraph.xyz/):

- [ ] Homepage renders card correctly
- [ ] Individual lens page renders card correctly
- [ ] OG image loads (not broken)

## 6. Frequency

| Check                       | Frequency                               |
| --------------------------- | --------------------------------------- |
| GSC coverage & indexing     | Weekly until 400+ indexed, then monthly |
| GSC search performance      | Weekly                                  |
| Umami traffic review        | Weekly                                  |
| Lighthouse scores           | After each deploy                       |
| Structured data validation  | After schema changes                    |
| Technical spot checks (3.x) | After deploy or SEO-related changes     |
| External tools (5.x)        | Monthly                                 |
