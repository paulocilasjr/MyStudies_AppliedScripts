# Technical execution diagrams

Mode: built-in `image_gen`, one independent generation per asset. Selected PNGs copied unchanged from generated output. No programmatic drawing, pixel editing, or slide authoring.

Visual QA: each label was checked against the requested workflow. Runtime has seven directed arrows and a dotted conceptual stage separator; harness has eight directed arrows; joins has six directed arrows plus one plain missing-data invariant connector; tests has five sequential arrows, first three nodes green, last three navy. No claims of GPU acceptance or clinical results appear.

## runtime.png

```text
Use case: infographic-diagram. Asset type: technical presentation workflow, landscape 16:9 high-resolution raster.
Make one clean flat professional architecture diagram with a uniform off-white #F5F7F4 background, dark navy-green ink #12211C, green #76B900 emphasis and small teal #2A9D8F accents. Plain sans-serif, large readable labels approximately 44px in a 1672px wide final image. Generous clear whitespace. Exactly EIGHT nodes, comprising FIVE main nodes and THREE input nodes. No title, footer, UI cards, statuses, counts, icons, logos or watermarks.
The five main nodes are arranged evenly left-to-right in one central horizontal row, and are connected by four directed arrows:
'SLURM A30' -> 'Isolated env' -> 'GPU checks' -> 'Local snapshot' -> 'Offline run'.
Above the Isolated env node, add a simple input box 'Public packages', with one downward arrow into Isolated env.
Above the Local snapshot node, add a simple input box 'Public weights', with one downward arrow into Local snapshot.
Below the Offline run node, add a simple input box 'Patient records', with one upward arrow feeding Offline run ONLY.
Draw one subtle vertical dotted separator in the whitespace between Local snapshot and Offline run, without any label. It indicates conceptual preparation versus inference stages, not a firewall.
Exactly SEVEN arrows total. Patient records must have no line toward any preparation nodes. The first four main nodes have navy outlines and a pale neutral fill; Offline run is emphasized with green outline and pale green fill. The input boxes are understated and the patient input may use teal outline. Each main node has generous label space, using two-line labels if necessary while preserving exact wording. Exact text only: 'SLURM A30', 'Isolated env', 'GPU checks', 'Local snapshot', 'Offline run', 'Public packages', 'Public weights', 'Patient records'. No other text. The entire image must be a workflow diagram rather than a screenshot.
```

## harness.png

```text
Use case: infographic-diagram. Asset type: technical application harness diagram, landscape 16:9 high-resolution raster.
Clean flat professional architecture diagram on uniform off-white #F5F7F4, dark navy-green #12211C ink, green #76B900 and teal #2A9D8F accents. Large plain sans-serif labels approximately 44px in a 1672px final image. Generous whitespace. No title, footer, icons, screenshot, UI cards, metrics, statuses, logos or watermarks.
Exactly NINE node boxes: SEVEN sequential workflow nodes and TWO side-input nodes.
Use a tidy two-row snake layout so text stays large: the TOP main row from left to right contains 'Input contract', 'Evidence facts', 'Prompt + budget', 'Nemotron'. The BOTTOM main row from right to left contains 'JSON + screen', 'Result contract', 'Human review'. Connect the exact sequence using clear arrowheads:
Input contract -> Evidence facts -> Prompt + budget -> Nemotron -> JSON + screen -> Result contract -> Human review.
Thus the first three arrows point right along the top row; Nemotron points DOWN into JSON + screen below it; JSON + screen points LEFT into Result contract; Result contract points LEFT into Human review.
Two smaller input boxes at the top above Nemotron are labeled 'Run settings' and 'Local weights', each with a separate downward arrow feeding Nemotron only. Use two distinct input ports on the top of Nemotron. Avoid any crossing arrows or arrows through labels.
Exactly EIGHT arrows total. Nemotron is green with pale green fill; other main nodes have navy outlines and pale neutral fill. Input boxes may use teal outlines. No additional words or labels. Exact text: 'Input contract', 'Evidence facts', 'Prompt + budget', 'Nemotron', 'JSON + screen', 'Result contract', 'Human review', 'Run settings', 'Local weights'. Use two-line labels where needed without changing the exact wording. Do not combine or omit any nodes.
```

## joins.png

```text
Use case: infographic-diagram. Asset type: technical patient-ID data assembly workflow, landscape 16:9 high-resolution raster.
One clean flat professional diagram on uniform off-white #F5F7F4, dark navy-green #12211C ink, green #76B900 emphasis, teal #2A9D8F for mIF. Plain sans-serif labels approximately 44px in a 1672px-wide final image. Generous whitespace. No title, footer, icons, UI cards, counts, metrics, statuses, logos or watermarks.
Exactly EIGHT node boxes. On the far LEFT, vertically stack FOUR source boxes, with exact labels 'Clinical CSV', 'mIF CSV', 'Fusion CSV', 'Context JSONL'. Each of these four boxes has its own directed arrow feeding the SAME central-left box 'Join by patient ID'. Use four distinct input ports on the left of the join box and neatly spaced paths; no crossing arrows and no arrow passes through text. The join box label can wrap to two lines, but wording is verbatim.
From Join by patient ID, draw a rightward arrow to 'Validate records', then another rightward arrow to the final output box 'Patient JSONL'. The central row is Join by patient ID -> Validate records -> Patient JSONL.
Place a smaller note box below Validate records, exact label 'Missing stays missing', and connect it with a single subtle line from Validate records to the note (a plain connector without an arrowhead). It is an invariant note, not an additional data source or a substitute output.
Exactly SIX directed arrows and ONE plain note connector. Clinical/mIF/fusion/context all feed one shared join, never separate joins. No fabricated probabilities, mean, filled-in modalities or extra source boxes. Green outline on Patient JSONL; teal outline on mIF CSV; navy on other boxes. Exact text only: 'Clinical CSV', 'mIF CSV', 'Fusion CSV', 'Context JSONL', 'Join by patient ID', 'Validate records', 'Patient JSONL', 'Missing stays missing'.
```

## tests.png

```text
Use case: infographic-diagram. Asset type: technical verification gates diagram, wide landscape 16:9 high-resolution raster.
Create a clean flat professional workflow on a uniform off-white #F5F7F4 background with dark navy-green #12211C text and green #76B900 accents. Large plain sans-serif labels approximately 44px in a 1672px-wide final image, with generous whitespace. No title, footer, metrics, test counts, status words, icons, screenshot, UI cards, logos or watermarks.
Exactly SIX evenly spaced rectangular node boxes in ONE central horizontal row, connected sequentially by exactly FIVE right-pointing arrows:
'Contract tests' -> 'Adapter tests' -> 'Mock experiment' -> 'A30 smoke test' -> 'Human review' -> 'Demo acceptance'.
The FIRST THREE boxes have green outlines and very pale green fills. The LAST THREE have navy outlines and pale neutral fills. Text in all nodes is dark navy. Use large TWO-LINE labels in each box as needed: 'Contract' over 'tests', 'Adapter' over 'tests', 'Mock' over 'experiment', 'A30 smoke' over 'test', 'Human' over 'review', 'Demo' over 'acceptance'. Preserve the exact wording; no punctuation or added status labels.
Every arrow is a simple directed line from one node's right side to the next node's left side. No branching, no missing gates, no additional arrows. All boxes fit fully inside generous outer margins. Plain rigorous engineering diagram, not a decorative infographic.
```
