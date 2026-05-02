# ADR-009: Buttondown for newsletter

**Status:** Accepted
**Date:** 2026-04-06

## Context

Newsletter is one of 5 revenue streams (sponsorship). Need a low-cost, low-friction email platform.

## Decision

Use Buttondown.

## Alternatives considered

| Alternative | Why rejected                                     |
| ----------- | ------------------------------------------------ |
| Substack    | Opinionated platform; less control over branding |
| ConvertKit  | More expensive; features beyond current needs    |
| Mailchimp   | Complex UI; expensive at scale                   |

## Consequences

- Free under 100 subscribers; EUR 9/month after
- Minimal UI, no lock-in
- No backend integration needed — standalone service
