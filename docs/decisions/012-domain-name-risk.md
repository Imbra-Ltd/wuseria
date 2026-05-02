# ADR-012: Domain name trademark risk (fujime.app)

**Status:** Accepted
**Date:** 2026-04-15 (decided), 2026-04-09 (opened)

## Context

The project uses fujime.app as its domain. "Fuji" is a registered trademark
of FUJIFILM Holdings Corporation. The site includes affiliate links, making
it commercial in nature. This creates trademark risk.

## Risk assessment

**UDRP (domain dispute):** To take the domain, Fujifilm would need to prove:

1. Domain is confusingly similar to their trademark — likely yes
2. Registrant has no legitimate interest — debatable (informational site)
3. Registered in bad faith — weak argument (not cybersquatting)

Fan sites can win UDRP disputes if non-commercial. Affiliate links weaken
this defense.

**Trademark infringement:** Using brand names in affiliate site domains can
result in cease and desist letters, fines up to $10,000 per domain under the
Anticybersquatting Consumer Protection Act, affiliate program termination,
and lawsuits.

**Fujifilm policy:** Their terms state trademarks "must not be used in any
manner without the express prior written consent." Brand guidelines exist
for the X Series.

## Options

1. **Keep fujime.app** — accept risk, add disclaimers, hope for no enforcement
2. **Rename to a brand-neutral domain** — eliminates risk entirely
3. **Contact Fujifilm** — request explicit permission or a fan site license

## Domain name candidates

| Domain          | Pros                                                                                               | Cons                                              |
| --------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| fujime.app      | Memorable, direct                                                                                  | Trademark risk (contains "fuji")                  |
| **lenspip.me**  | Zero risk, unique, short, "pip" nods to scoring visualization, multi-system ready, fits me! series | Needs brand awareness from scratch                |
| **lensing.me**  | Zero risk, short, elegant, real cinematography term, fits me! series                               | Lens-specific — cameras/accessories are secondary |
| wisteria.me     | Zero risk, elegant, "fuji" = wisteria in Japanese                                                  | Subtle, doesn't scale to multi-system             |
| **wuseria.com** | Zero risk, short, playful twist on "wisteria", .com availability                                   | Invented word, no immediate meaning               |
| **wuseria.app** | Same as .com but signals web app, modern TLD                                                       | Invented word, .app forces HTTPS                  |
| **wuseria.io**  | Same base, developer/tech-forward TLD                                                              | .io trending but pricier                          |
| **wuseria.me**  | Zero risk, playful twist on "wisteria", fits me! series (.me TLD)                                  | Invented word, no immediate meaning               |
| lensgrade.me    | Clear, describes scoring, multi-system ready                                                       | Generic                                           |
| xmount.me       | Recognizable to Fuji shooters                                                                      | "X" prefix associations, Fuji-specific            |

## Decision

**wuseria.com** — rename from fujime.app before launch.

Rationale:

- Zero trademark risk — invented word, no existing brand conflicts
- `.com` is the strongest TLD for global reach, SEO, and user trust
- Short (7 letters), unique, fully ownable — will dominate search results
- "Wuseria" is a playful twist on "wisteria" (fuji = wisteria in Japanese) — an easter egg for those who know
- Rejected lenspip.com: too similar to LensTip (primary data source), risks confusion or damaging the relationship
- Rejected .me TLD: weaker for global audience despite fitting the me! series branding

## References

- [WIPO Guide to UDRP](https://www.wipo.int/amc/en/domains/guide/)
- [UDRP: When It Works and When It Doesn't](https://www.knobbe.com/blog/domain-name-disputes-when-udrp-works-and-when-it-doesnt/)
- [Avoiding Trademark Pitfalls in Affiliate Marketing](https://thepma.org/avoiding-trademark-pitfalls-in-affiliate-marketing/)
- [Avoid Trademark Infringement When Choosing a Domain Name](https://www.nolo.com/legal-encyclopedia/avoid-trademark-infringement-domain-name-29032.html)
- [Online Use of Third Party Trademarks](https://www.americanbar.org/groups/business_law/resources/business-law-today/2016-february/online-use-of-third-party-trademarks/)
- [Fujifilm Terms of Use](https://www.fujifilm.com/us/en/terms)
- [Fujifilm X Series Brand Guidelines](https://www.fujifilm-x.com/en-us/brand-guidelines/)

## Consequences

- Register wuseria.com immediately
- Update `astro.config.mjs` site URL, `public/CNAME`, CLAUDE.md, README, and all internal references
- Add "Not affiliated with FUJIFILM" disclaimer in footer (good practice regardless)
- fujime.app can redirect to wuseria.com temporarily if already registered, or be abandoned
