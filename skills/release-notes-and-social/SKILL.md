---
name: release-notes-and-social
description: Use this skill to turn technical feature documentation into customer-facing B2B SaaS release notes, changelog entries, launch announcements, and social posts using product, ICP, audience, tone, and channel context from a config.
---

# Release Notes And Social

## Goal

Transform technical feature documentation into accurate, useful launch communications for B2B SaaS audiences.

The output should preserve technical truth while making the feature understandable, relevant, and ready for the intended channel.

## Inputs To Request Or Infer

Minimize user input. The minimum useful input is:

- Technical documentation, PRD, engineering notes, or implementation summary
- Config path, usually `workflows/launch-comms/config.local.yaml`

Infer from the config when possible:

- Product and category
- ICP, buyer, and user personas
- Voice and terminology
- Channels to draft for
- Claims to avoid
- Required links or CTAs

Ask follow-up questions only when missing context would create risky or inaccurate copy.

## Workflow

1. Read the technical source material.
2. Read the launch comms config if provided.
3. Extract the factual feature change, user-visible behavior, limits, prerequisites, and rollout status.
4. Separate confirmed facts from assumptions.
5. Choose output formats using `references/output-formats.md`.
6. Apply audience and tone guidance from `references/audience-and-tone.md`.
7. Draft concise release notes and social posts.
8. Flag open questions, risky claims, or missing launch details.

## Quality Bar

- Do not invent benefits, metrics, customer names, integrations, security claims, AI capabilities, or availability.
- Avoid internal implementation details unless the audience is technical and the detail matters.
- Prefer specific user-visible changes over generic value statements.
- Keep copy crisp; do not turn release notes into a marketing essay.
- Include prerequisites, plan availability, beta status, or rollout constraints when relevant.
- Use the user's product terminology from the config.
- If the technical docs are ambiguous, include an `Open Questions` section rather than guessing.

## Output

Default to:

- Release note
- Changelog entry
- LinkedIn post
- Short social post
- Internal enablement blurb
- Open questions

If the config asks for only some channels, output only those channels.
