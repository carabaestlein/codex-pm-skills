---
name: competitor-source-discovery
description: Use this skill to find public source URLs for monitoring B2B SaaS competitors, including blogs, changelogs, docs, pricing pages, integrations, trust pages, press pages, and secondary sources, then update the daily intel email config.
---

# Competitor Source Discovery

## Goal

Find reliable public URLs to monitor for competitive and market intelligence, then update the daily intel email config in place.

This skill is for source assembly, not signal interpretation. Use `competitive-market-intel` after sources are configured.

## Inputs To Request Or Infer

Minimize the user's input. The minimum useful input is:

- Product category
- Competitor names

Infer everything else when possible:

- Competitor homepages
- Source URLs
- Priority for each competitor
- Common market sources
- Whether secondary sources are useful

Optional inputs, when the user already has them:

- Company/product name
- ICP or buyer segment
- Geographic or segment constraints
- Known competitor homepages
- Sources to exclude

## Workflow

1. Accept a short competitor list without asking for URLs.
2. For each competitor, find or verify the official homepage.
3. Search for official source URLs first.
4. Prefer stable pages that are likely to update over time.
5. Collect source types using `references/source-types.md`.
6. Verify that each URL belongs to the expected company or a credible secondary source.
7. Infer priority as `high` when the user gives no priority, unless the request clearly distinguishes primary and secondary competitors.
8. Avoid adding duplicate pages or generic homepages unless no better source exists.
9. Label weak/secondary sources clearly.
10. Update the target config file using `references/output-format.md`.
11. If no target config file is available, return YAML as a fallback instead of stopping.

## Quality Bar

- Prefer official primary sources.
- Include only URLs that can plausibly produce useful monitoring signals.
- Do not guess URLs from memory.
- Do not include a source if the URL cannot be found or verified.
- Ask follow-up questions only when missing context would materially change the source list.
- Keep labels short and consistent.
- Return notes for missing high-value sources, such as "No public changelog found."

## Output

Default to:

- Updated config file, usually `workflows/daily-intel-email/config.local.yaml`
- Notes on missing or weak sources
- YAML only when file editing is unavailable or the user explicitly asks for copyable output

When browsing/search is unavailable, ask the user to provide either competitor homepages or permission to search the web.

## Minimal Prompt Pattern

The user should be able to start with:

```text
Use $competitor-source-discovery for B2B SaaS customer support tools.
Competitors: Intercom, Zendesk, Front.
```

Do not ask for each source URL. Find them.

## Config Update Behavior

When a config file exists:

- Preserve existing company, digest, delivery, and theme settings.
- Preserve global product, audience, positioning, and voice settings in root `config.local.yaml`.
- Preserve user-provided competitor names and priorities.
- Add or replace missing `sources` arrays for each competitor.
- Do not overwrite user-provided source URLs unless they are broken, duplicated, or clearly point to the wrong company.
- Add short notes outside the config in the response, not as YAML comments, unless the user asks for comments.
