# Codex PM Skills

A collection of Codex skills and workflow starters for product managers working on B2B SaaS products.

The repo is organized around two related ideas:

- **Skills** teach Codex how to perform a PM task with the right judgment, structure, and quality bar.
- **Workflows** show how to run a skill as a repeatable operating rhythm, such as a daily market intel digest.

## Current Skills

### Competitor Source Discovery

Path: `skills/competitor-source-discovery`

Use this skill to find the best public URLs to monitor for each competitor and update the daily intel email config.

Good starting prompt:

```text
Use $competitor-source-discovery to build monitoring sources for <category>. Competitors: <names>.
```

Minimum useful input:

```text
Category: <product category>
Competitors: <competitor names>
```

### Competitive Market Intel

Path: `skills/competitive-market-intel`

Use this skill to monitor competitors and market signals, classify what changed, separate facts from interpretation, and produce a concise morning digest for a B2B SaaS PM.

Good starting prompt:

```text
Use $competitive-market-intel to create a morning market intel digest for my B2B SaaS product.
```

## Repo Structure

```text
skills/
  competitor-source-discovery/
    SKILL.md
    agents/openai.yaml
    references/
  competitive-market-intel/
    SKILL.md
    agents/openai.yaml
    references/
workflows/
  daily-intel-email/
    automation-prompt.md
    config.example.yaml
    requirements.txt
    run.py
examples/
  daily-intel-email-digest.md
```

## Getting Started

1. Copy `workflows/daily-intel-email/config.example.yaml` to a private ignored config such as `workflows/daily-intel-email/config.local.yaml`.
2. In the private config, provide the product category, competitor names, and delivery details. Source URLs can be left empty.
3. Ask Codex to use `$competitor-source-discovery` to fill in missing source URLs in the private config.
4. Run the daily intel email workflow locally:

```bash
python3 -m pip install -r workflows/daily-intel-email/requirements.txt
python3 workflows/daily-intel-email/run.py \
  --config workflows/daily-intel-email/config.local.yaml \
  --output outputs/daily-intel-email.md
```

5. Use `workflows/daily-intel-email/automation-prompt.md` as the prompt for a Codex automation.
6. Once the digest shape feels useful, add real delivery credentials and run with `--send-email`.

Private company context, API keys, inbox details, and non-public competitor lists should live in a private config or automation environment, not in a public Git repo.
