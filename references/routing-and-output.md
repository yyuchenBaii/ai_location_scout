# Routing And Output

Route every request into exactly one of the following scenarios before starting report generation.

## 1. `single-defense`

Trigger when the user gives one specific address or coordinate and one business type.

Action:

1. Confirm the business keyword if needed.
2. Run location context first.
3. Run competitor scan second.
4. Produce a single-location HTML report.

Deliverable:

- clear risk conclusion
- named nearest competitor and distance
- explicit final grade / risk level
- single-location HTML report using `resources/report_template.html`

## 2. `multi-compare`

Trigger when the user provides multiple candidate addresses and asks which is better.

Action:

1. Normalize each candidate location.
2. Run both scripts for each location.
3. Compare all candidates in one result set.
4. Produce one combined HTML comparison report.

Deliverable:

- concise comparison summary
- exactly one recommended option
- one combined HTML report using `resources/location_report_comparison.html`

Important:

- Do not create one HTML file per site.
- The comparison template is driven by JavaScript data. Follow the template injection rules strictly.

## 3. `fuzzy-explore`

Trigger when the user has a business intent and budget but no exact address.

You must ask for the missing core dimensions before selecting locations:

- budget
- target customer segment
- space / area requirement
- rent tolerance

After the user answers, infer three concrete districts / streets / business areas worth evaluating, then run the normal real-data workflow for those three candidates.

Deliverable:

- three recommended candidate areas
- one combined comparison HTML report

## 4. `reverse-leasing`

Trigger when the user gives an idle storefront and asks what business type fits it.

Action:

1. Identify the storefront location.
2. Scan the surrounding POI structure.
3. Recommend suitable and unsuitable business types.
4. Choose the best-fit business type and produce the final HTML report for that scenario.

Deliverable:

- matched business-type recommendation
- explicit no-go business types
- final HTML report grounded in the selected business type

## Universal Rule

No matter which scenario the user starts from, the end state for a full evaluation is an HTML report with map content, not only a conversational answer.
