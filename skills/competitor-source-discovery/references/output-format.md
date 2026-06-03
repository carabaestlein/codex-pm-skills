# Config Update Format

Default to updating `workflows/daily-intel-email/config.local.yaml` directly when the file exists.

If the user provided only a category and competitor names, still produce complete `competitors` entries. Use inferred `priority` values and note assumptions after updating the file.

Use this shape inside the config:

```yaml
competitors:
  - name: "Competitor A"
    priority: "high"
    sources:
      - label: "Blog"
        url: "https://example.com/blog"
      - label: "Changelog"
        url: "https://example.com/changelog"
      - label: "Docs"
        url: "https://docs.example.com/"
      - label: "Pricing"
        url: "https://example.com/pricing"
      - label: "Integrations"
        url: "https://example.com/integrations"
      - label: "Trust"
        url: "https://trust.example.com/"
      - label: "Press"
        url: "https://example.com/news"
```

## Label Conventions

Use these labels when possible:

- Blog
- Changelog
- Docs
- Pricing
- Integrations
- Trust
- Status
- Press
- Events
- Reviews
- Jobs

## Notes Format

After updating the config, include short notes in the response:

```markdown
Notes:
- Competitor A: No public changelog found.
- Competitor B: Pricing appears to be quote-only; used the plans/contact-sales page.
- Competitor C: Jobs page included as a weak secondary signal.
- Priorities were inferred because the user did not provide them.
```

Do not mix notes into the YAML unless the user asks for comments.
