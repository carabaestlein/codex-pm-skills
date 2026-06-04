# Codex PM Skills

A collection of Codex skills and workflow starters for product managers working on B2B SaaS products.

The repo is organized around two related ideas:

- **Skills** teach Codex how to perform a PM task with the right judgment, structure, and quality bar.
- **Workflows** show how to run a skill as a repeatable operating rhythm, such as a daily market intel digest.

## Current Skills

### Competitive Market Intel

Path: `skills/competitive-market-intel`

Use this skill to monitor competitors and market signals, classify what changed, separate facts from interpretation, and produce a concise morning digest for a B2B SaaS PM.

Good starting prompt:

```text
Use $competitive-market-intel to create a morning market intel digest for my B2B SaaS product.
```

Supporting setup skill:

`competitor-source-discovery` helps the competitive market intel workflow fill in missing competitor monitoring URLs. It is primarily used to update `workflows/daily-intel-email/config.local.yaml` before the daily digest runs, so PMs only need to provide product category and competitor names.

Example setup prompt:

```text
Use $competitor-source-discovery to fill missing source URLs for the daily intel email config.
```

### Release Notes And Social

Path: `skills/release-notes-and-social`

Use this skill to turn technical feature documentation into release notes and social posts using product, ICP, audience, tone, and channel context from a config.

Good starting prompt:

```text
Use $release-notes-and-social to draft launch copy from <technical doc path> using <config path>.
```

### Customer Call Mining

Path: `skills/customer-call-mining`

Use this skill to analyze customer, sales, CS, or research call transcripts for themes, use cases, requirements, and concrete product feedback, with impact and confidence attributes.

Good starting prompt:

```text
Use $customer-call-mining to analyze transcripts in <path> using config.local.yaml and workflows/call-mining/config.local.yaml.
```

## Repo Structure

```text
config.example.yaml
skills/
  competitive-market-intel/
    SKILL.md
    agents/openai.yaml
    references/
  competitor-source-discovery/
    SKILL.md
    agents/openai.yaml
    references/
  release-notes-and-social/
    SKILL.md
    agents/openai.yaml
    references/
  customer-call-mining/
    SKILL.md
    agents/openai.yaml
    references/
workflows/
  daily-intel-email/
    automation-prompt.md
    config.example.yaml
    requirements.txt
    run.py
  launch-comms/
    config.example.yaml
  call-mining/
    config.example.yaml
examples/
  daily-intel-email-digest.md
  release-notes-and-social-output.md
  customer-call-mining-output.md
```

## Global PM Context

Shared product, market, ICP, positioning, terminology, and voice settings live in the root config:

```text
config.local.yaml
```

Create it by copying:

```text
config.example.yaml
```

Workflow-specific configs should only contain the extra inputs for that workflow.

## Daily Intel Email

1. Create the root `config.local.yaml` if it does not already exist.
2. Copy `workflows/daily-intel-email/config.example.yaml` to a private ignored config such as `workflows/daily-intel-email/config.local.yaml`.
3. In the daily intel config, provide competitor names and delivery details. Source URLs can be left empty.
4. Ask Codex to use `$competitor-source-discovery` to fill in missing source URLs in the private config.
5. Run the daily intel email workflow locally:

```bash
python3 -m pip install -r workflows/daily-intel-email/requirements.txt
python3 workflows/daily-intel-email/run.py \
  --config workflows/daily-intel-email/config.local.yaml \
  --output outputs/daily-intel-email.md
```

6. Use `workflows/daily-intel-email/automation-prompt.md` as the prompt for a Codex automation.
7. Once the digest shape feels useful, add real delivery credentials and run with `--send-email`.

## Launch Comms Drafting

1. Create the root `config.local.yaml` if it does not already exist.
2. Copy `workflows/launch-comms/config.example.yaml` to a private ignored config such as `workflows/launch-comms/config.local.yaml`.
3. In the launch comms config, choose output channels and add links if useful.
4. Ask Codex to use `$release-notes-and-social` with the technical feature documentation, the root config, and the launch comms config.

Example prompt:

```text
Use $release-notes-and-social to draft launch copy from docs/feature-spec.md using config.local.yaml and workflows/launch-comms/config.local.yaml.
```

## Customer Call Mining

1. Create the root `config.local.yaml` if it does not already exist.
2. Copy `workflows/call-mining/config.example.yaml` to a private ignored config such as `workflows/call-mining/config.local.yaml`.
3. Ask Codex to use `$customer-call-mining` with one transcript or a folder of transcripts.

Example prompt:

```text
Use $customer-call-mining to analyze transcripts in calls/ using config.local.yaml and workflows/call-mining/config.local.yaml.
```

Private company context, API keys, inbox details, and non-public competitor lists should live in a private config or automation environment, not in a public Git repo.
