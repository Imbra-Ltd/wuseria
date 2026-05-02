# ADR-010: Gumroad for merchandise

**Status:** Accepted
**Date:** 2026-04-06

## Context

Merch (card decks) is one of 5 revenue streams. Expected volume is 10-15 orders/month. Need a storefront that handles payments without building e-commerce infrastructure.

## Decision

Use Gumroad.

## Alternatives considered

| Alternative              | Why rejected                                              |
| ------------------------ | --------------------------------------------------------- |
| Shopify                  | Full e-commerce platform; overkill for 10-15 orders/month |
| Custom checkout (Stripe) | Requires backend; maintenance overhead                    |

## Consequences

- Zero setup; handles payments, delivery, and tax
- No backend needed
- Gumroad takes a percentage per sale (acceptable at current volume)
