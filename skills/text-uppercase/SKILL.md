---
name: text-uppercase
description: Use when the user wants provided text converted to UPPERCASE. Handles inline text, multi-line blocks, and uploaded text files; leaves numbers, punctuation, and layout intact.
---

# Text Uppercase

## Workflow

1. Take the text the user provides (inline, pasted block, or an uploaded .txt/.md file).
2. Convert every alphabetic character to its uppercase form.
3. Preserve all line breaks, spacing, numbers, punctuation, and symbols exactly as-is.
4. Return the converted text in a code block so it is easy to copy.
5. If the source was an uploaded file, also offer to save the result as a new file.

## Notes

- Apply locale-aware uppercasing where relevant (e.g. accented characters: é → É).
- Do not alter the meaning, word order, or content — this is a pure case transformation.
- If the input is empty, ask the user for the text to convert.
