---
name: pdf-summarizer
description: Use this skill when the user wants to summarize a PDF document. Triggers on mentions of "summarize this PDF", "what does this paper say", or any uploaded .pdf file the user wants condensed.
---

# PDF Summarizer

## When to use

Use whenever the user has a PDF and wants its contents condensed. Not for filling forms, extracting tables, or OCR on scanned PDFs — use the `pdf` skill for those.

## Workflow

1. Run `python scripts/extract.py <path-to-pdf>` to get the raw text.
2. Identify the document type (paper, contract, report, etc.) from the first page.
3. Produce a summary with:
   - 2–3 sentence overview
   - Key bullet points (5–10)
   - Important entities (people, organizations, dates)
   - Open questions or things the user should verify

## Output format

Keep the summary under 400 words unless the user asks for more detail.
