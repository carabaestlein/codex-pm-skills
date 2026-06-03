# Digest Format

Use this default format unless the user requests otherwise.

Only include competitors or market actors that have a noteworthy signal in the configured lookback window, usually the last 24 hours. Do not include a competitor just because they are listed in the config.

```markdown
Subject: Morning Market Intel: <3-5 word summary>

## Executive Summary

<1-3 bullets summarizing the most important changes.>

## Top Signals

### 1. <Competitor or market actor>: <what changed>

- **Signal type:** <taxonomy label>
- **What happened:** <factual summary>
- **Confidence:** <High | Medium | Low>
- **Sources:** <dated links>

## Watchlist

- <Lower-confidence signal or thing to monitor next.>

## Recommended Actions

- <Specific this-week action, decision, or research question. Omit this section if there is no action worth taking.>

## Sources

- <Source title> - <URL>
```

If no configured competitor has a noteworthy signal in the lookback window, use this shorter format:

```markdown
Subject: Morning Market Intel: No noteworthy competitor updates

## Executive Summary

- No noteworthy competitor or market signals were found in the last 24 hours.
- Sources checked: <brief count or list of source groups checked>.

## Watchlist

- <Optional low-confidence item to keep monitoring. Omit if there is nothing useful to watch.>

## Sources

- <Source title> - <URL>
```

## Style

- Direct and concise.
- Favor a short, useful email over a complete memo.
- No hype.
- No long preamble.
- Use bullets for scanability.
- Keep each top signal to roughly 40-80 words unless the user asks for a deeper memo.
- Exclude competitors with no noteworthy activity.
- Include recommended actions only when they are specific, useful, and plausibly worth doing this week.
- Do not create generic homework just to fill the section.
- Do not include separate "why it matters" or "PM implication" fields; a seasoned PM should be able to infer those from a crisp fact pattern.
