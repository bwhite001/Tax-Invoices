## Purpose

Short, actionable guidance for AI coding assistants working in this repo (Tax Invoices / LM Studio invoice cataloger).

## Quick overview (big picture)
- This repository is primarily a set of documentation and a PowerShell automation script (`Invoice-Cataloger-LMStudio.ps1`) that:
  - Scans an invoice folder (year-based `FYYYYY-YYYY` directories).
  - Extracts text from PDFs / images (Windows OCR or Tesseract).
  - Sends invoice text to a local LM Studio endpoint to extract structured JSON.
  - Categorises expenses using keyword maps and computes ATO-style deductions.
  - Exports results to CSV and (optionally) Excel in the configured `OutputFolder`.

## Key files and places to look
- `Invoice-Cataloger-LMStudio.ps1` — single authoritative script. See the `$Config` block at top for runtime settings (endpoints, folders, OCR path, feature toggles).
- `Quick-Start-Guide.md` and `Setup-Guide-LM-Studio.md` — user-facing runbook; contains exact PowerShell commands and LM Studio setup notes.
- `Extracted Invoices Log.gsheet` and `Invoice Summary.gsheet` — canonical spreadsheets used by users; treat them as authoritative data outputs.
- Year folders (`FY2021-2022/` …) — invoice source organization. Processed files are moved to `Proccessed` (note: directory name contains a misspelling; preserve it unless intentionally renaming and updating configs).

## Things an AI assistant should do first (high-value reads)
1. Open `Invoice-Cataloger-LMStudio.ps1` and read the `$Config` section to understand hard-coded defaults and paths.
2. Read `Quick-Start-Guide.md` for the exact commands users run (examples are the canonical run examples we should preserve).
3. Inspect `Get-ExpenseCategory` and `Calculate-ATODeduction` functions in the PS1 file — these show category keyword maps and calculation rules (use them when suggesting new categories or refactors).

## Developer workflows (explicit commands and examples)
- Run the script (PowerShell 5.1+ on Windows):
  - Open PowerShell as Administrator, cd to script directory, then: `.\\Invoice-Cataloger-LMStudio.ps1`
- If execution policy blocks the script: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- LM Studio connectivity check: browse or GET `http://localhost:1234/v1/models` (configured endpoint may differ — check `$Config.LMStudioEndpoint`).
- Output artifacts: `Invoice_Catalog_YYYYMMDD_HHMMSS.csv` and `Deduction_Summary_YYYYMMDD_HHMMSS.csv` appear in `$Config.OutputFolder`; Excel `.xlsx` created if Excel COM is available.

## Project-specific conventions and patterns
- Single-script orchestration: the PS1 script contains discovery, OCR, LLM extraction, categorisation and export in one file. Prefer small, conservative edits when changing behavior.
- Config-first edits: change behavior primarily via the `$Config` hashtable rather than sprinkling new hard-coded paths.
- Output stability: scripts preserve originals by default (`DeleteProcessedFiles = $false`). Do not enable deletion without verifying workflow.
- Keyword-driven categorisation: `Get-ExpenseCategory` uses simple keyword matching (lowercase, substring). When adding keywords, follow existing style (small arrays of common vendor/keyword tokens).

## Integration points and external dependencies
- Local LM Studio server (HTTP API). The script expects an OpenAI-like chat completions endpoint (see `$Config.LMStudioEndpoint`).
- Optional OCR: Tesseract (`C:\Program Files\Tesseract-OCR\tesseract.exe`) or Windows built-in OCR. If adding OCR logic, follow current helper functions (`Extract-TextWithTesseract`, `Extract-TextFromImage`).
- Excel COM: `Export-ToExcel` uses the Excel COM object; ensure Excel is installed on Windows if required.

## When editing or extending behavior — concrete rules
1. If you change folder names (e.g., `Proccessed`), update `$Config` and the Quick Start/Setup guides. Preserve the current folder name unless migrating deliberately.
2. Keep LM Studio prompt instructions strict about returning valid JSON. The script strips markdown fences and parses JSON — avoid changing response shape unintentionally.
3. When adding new categories, update both `Get-ExpenseCategory` and any unit tests/docs; prefer conservative mapping.
4. For any network calls to LM Studio, follow existing retry pattern (RetryAttempts/RetryDelaySeconds) rather than adding new ad-hoc retries.

## Example snippets to reference (do not change verbatim unless intentionally updating examples)
- `$Config` default endpoint example: `LMStudioEndpoint = "http://192.168.0.100:1234/v1/chat/completions"`
- Run example from Quick-Start: `cd C:\Scripts; .\Invoice-Cataloger-LMStudio.ps1`

## Testing and validation guidance
- Manual test: place 1–3 known invoice PDFs into the configured `InvoiceFolder` and run the script. Confirm CSV and Summary files are created and contain expected vendor/amount values.
- LM Studio test: confirm `GET $Config.LMStudioModelsEndpoint` returns at least one model; script uses the first model id when available.

## Notes & gotchas (non-obvious, discovered in repo)
- The `Proccessed` folder name is misspelled and referenced in `$Config.OutputFolder` — changing it breaks automatic exports unless synced across docs/config.
- The script expects Windows PowerShell 5.1 APIs for Windows OCR and Excel COM; Linux/macOS are not supported targets for the PS1 workflow.

## If something is missing
- Ask the repo owner for sample invoice files or sample LM Studio responses (they help reproduce parsing edge-cases). When in doubt, reference the Quick-Start and Setup guides before proposing behavioural changes.

---
If this draft misses any repository-specific workflows or files you'd like me to call out, tell me what to add and I'll iterate.
