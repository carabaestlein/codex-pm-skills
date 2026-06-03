Use $competitive-market-intel to run the daily intel email workflow for this repo.

Run `python3 workflows/daily-intel-email/run.py --config workflows/daily-intel-email/config.example.yaml --output outputs/daily-intel-email.md`.

Then summarize the resulting digest in this Codex thread with:

- The subject line
- The top 3 signals
- Any follow-ups that need a PM decision
- Whether email delivery was skipped or completed

Do not send email unless the workflow has been explicitly configured with real delivery credentials and the run command includes `--send-email`.
