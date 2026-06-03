---
name: competitive-market-intel
description: Use this skill to monitor competitors and market signals for a B2B SaaS product manager, synthesize source-backed insights, and produce a concise market intel digest with PM implications, confidence, and follow-ups.
---

# Competitive Market Intel

## Goal

Create a concise, source-backed competitive and market intelligence digest for a B2B SaaS PM.

The digest should help a PM notice meaningful changes early, understand why they matter, and decide whether to investigate, respond, or ignore.

## Inputs To Request Or Infer

Use the information available in the user's request, repo, or config. If critical context is missing, ask for only the smallest missing set.

- Company and product category
- ICP and buyer/user personas
- Competitors and adjacent products
- Strategic themes to watch
- Source list or source constraints
- Digest cadence and audience

## Core Workflow

1. Identify the market, product surface, ICP, and priority themes.
2. Collect recent source-backed signals from approved sources.
3. Deduplicate repeated coverage of the same underlying change.
4. Classify each signal using `references/signal-taxonomy.md`.
5. Prioritize by novelty, relevance to PM decisions, source quality, and potential impact.
6. Separate observed facts from interpretation.
7. Write a digest using `references/digest-format.md`.
8. Include dates, links, confidence, and recommended follow-ups.

## Source Guidance

Prefer primary sources over commentary. Use `references/source-priorities.md` when deciding what to trust and how to label confidence.

Do not overstate weak signals. A pricing page change, release note, job posting, and customer quote can all matter, but they imply different levels of certainty.

## Quality Bar

- Lead with what changed, not with general market commentary.
- Keep the summary short enough to read over coffee.
- Name the PM implication for each important item.
- Cite sources directly.
- Mark confidence as High, Medium, or Low.
- Include follow-ups only when they are specific and actionable.
- Avoid creating false urgency around routine marketing content.

## Output

Default to a morning digest with:

- Subject line
- Executive summary
- Top signals
- PM implications
- Watchlist
- Suggested follow-ups
- Sources

If the user asks for a different format, keep the same reasoning discipline while adapting the output.
