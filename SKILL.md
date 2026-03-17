---
name: location-scout-ultimate
description: Use for commercial site selection, multi-location comparison, district exploration, and reverse招商 workflows that must combine AMap-backed data, local Python scripts, and the bundled HTML report templates.
---

# Location Scout Ultimate

Use this skill when the user wants a commercial real-estate style site-selection assessment, competitor scan, multi-location comparison, vague district exploration, or reverse招商 recommendation.

The value of this skill is not generic analysis. It is a strict workflow:

1. Route the request into the correct scenario.
2. Use real local scripts when keys and inputs are available.
3. Follow the bundled HTML templates instead of inventing a new layout.
4. Clearly separate confirmed API facts from model inference.

## First Response

Before doing analysis, check whether `AMAP_WEB_KEY` is available.

- If the key is missing, tell the user that real AMap-backed analysis is unavailable and offer two paths:
  - provide the key so the skill can fetch real location data
  - continue in demo mode with clearly labeled mock data
- If the user chooses demo mode, do not run the scripts. Make it explicit that all numeric results are illustrative.
- If the key exists, continue with real-data mode.

## Route The Request

Classify the request into one of these four scenarios before generating a report:

- `single-defense`: one concrete address or coordinate plus business type
- `multi-compare`: multiple candidate locations to compare
- `fuzzy-explore`: no exact location yet, only budget / city / business intent
- `reverse-leasing`: an idle storefront that needs a recommended business type

See [references/routing-and-output.md](references/routing-and-output.md) for the detailed routing rules, required follow-up questions, and expected deliverable shape for each scenario.

## Real Data Workflow

When working in real-data mode and the location has been identified, do not invent numeric facts. Run the local scripts in this order:

1. `python scripts/fetch_location_context.py "<lng,lat>"`
2. `python scripts/fetch_amap_poi.py "<lng,lat>" "<business_keyword>"`

If a script fails, a path is wrong, or the API returns insufficient data, explain the limitation to the user instead of fabricating numbers.

See [references/data-contracts.md](references/data-contracts.md) for:

- which output fields must be quoted directly
- which conclusions are allowed only as inference
- how to handle uncertainty in the report

## Report Generation Rules

Every full assessment should end in an HTML report, not just a plain Markdown summary.

Before generating any HTML, read the relevant local template:

- single-location report: `resources/report_template.html`
- multi-location comparison: `resources/location_report_comparison.html`

If the template cannot be read, warn the user that the report will be a degraded fallback HTML version.

Do not casually redesign the UI. Prefer filling the existing template structure and reserved containers.

See [references/template-rules.md](references/template-rules.md) for:

- required template-reading behavior
- single-report injection rules
- strict multi-location `locationData` replacement rules
- map data injection requirements
- final reminder text about JSAPI key / security code

## Output Standard

Preferred delivery order:

1. write an HTML file locally and return the absolute path
2. if file writing is blocked, output complete HTML source

Do not return meaningless `localhost` links.

Before final output, run through the quality checks in [references/report-checklist.md](references/report-checklist.md).

## Style

Maintain a professional commercial real-estate tone. Be concise, specific, and numerically grounded. Avoid hype when presenting conclusions; the strength of the report should come from the data, the structure, and the template fidelity.
