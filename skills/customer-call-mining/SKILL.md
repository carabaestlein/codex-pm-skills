---
name: customer-call-mining
description: Use this skill to mine customer, sales, CS, research, or support call transcripts for theme maps, customer use cases, key requirements, and concrete product feedback, with impact, confidence, evidence, and single-call emphasis or multi-call frequency.
---

# Customer Call Mining

## Goal

Analyze customer and sales call transcripts to extract PM-useful insights:

- General themes
- Customer use cases
- Key requirements
- Concrete product feedback

Each insight should include impact and confidence. Use emphasis for individual transcripts and frequency for multi-transcript batches.

## Inputs To Request Or Infer

Minimize user input. The minimum useful input is:

- One transcript or a folder of transcripts
- Global config path, usually `config.local.yaml`

Optional:

- Call-mining config path, usually `workflows/call-mining/config.local.yaml`
- Account metadata, if not already in transcript filenames or headers
- Specific product areas to focus on

Infer from the global config when possible:

- Product category
- ICP and personas
- Strategic themes
- Terminology

## Workflow

1. Read the global config if provided.
2. Read the call-mining config if provided.
3. Determine analysis mode:
   - One transcript: use `Emphasis`.
   - Multiple transcripts: use `Frequency`.
4. Extract evidence-backed insights.
5. Organize output in this order:
   - Theme Map
   - Use Cases
   - Requirements
   - Product Feedback
6. Score impact and confidence using `references/scoring.md`.
7. Format the output using `references/output-format.md`.
8. Include open questions only when they are needed to avoid overclaiming.

## Quality Bar

- Ground every insight in transcript evidence.
- Separate what the customer said from sales interpretation.
- Do not treat a single transcript as broad market proof.
- Preserve customer language when it is useful, but avoid long quotes.
- Prefer concrete product feedback over vague sentiment.
- Do not invent account metadata, revenue impact, deal status, or urgency.
- Deduplicate repeated wording inside the same transcript.
- Sort each section by impact, then confidence.

## Output

Default to:

- Theme Map
- Use Cases
- Requirements
- Product Feedback
- Open Questions, only if needed
- Source Coverage

If the user asks for a brief version, keep the same sections but limit each section to the highest-impact rows.
