Use $competitor-source-discovery and $competitive-market-intel to run the daily intel email workflow for this repo.

Use `workflows/daily-intel-email/config.local.yaml` when it exists. Otherwise, create it from `workflows/daily-intel-email/config.example.yaml` and treat it as the private working config.

Before running the digest:

1. Inspect the private config.
2. If any competitor has no `sources`, an empty `sources` list, or placeholder `example.com` URLs, use $competitor-source-discovery to find public monitoring URLs.
3. Update the private config in place with the discovered URLs.
4. Preserve existing company, digest, delivery, theme, competitor, and user-provided source settings.

Then run `python3 workflows/daily-intel-email/run.py --config workflows/daily-intel-email/config.local.yaml --output outputs/daily-intel-email.md`.

Then summarize the resulting digest in this Codex thread with:

- The subject line
- The top 3 signals
- Any recommended actions that need a PM decision
- A clear note if no configured competitors had noteworthy activity in the last 24 hours
- Whether email delivery was skipped or completed

Do not send email unless the workflow has been explicitly configured with real delivery credentials and the run command includes `--send-email`.
