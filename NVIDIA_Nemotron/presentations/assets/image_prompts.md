# Generated image asset prompts

Mode: built-in `image_gen` only. Generated PNGs were copied unchanged into this workspace; no programmatic illustration or pixel editing was used.

Selected outputs: `architecture.png` and `cover.png`, both 1672 × 941 pixels (approximately 16:9).

Visual QA: architecture has six correctly spelled node labels, three Future badges and exactly seven correct directed edges. Cover has an empty dark left title area with all visible dots, traces and computing surfaces concentrated on the right. No text, counts, patient data or logos appear in the cover.

## Selected architecture generation prompt

```text
Use case: infographic-diagram.
Asset type: a professional architecture-slide visual asset, landscape 16:9, high-resolution 2048x1152.
Create ONE precise clean flat architectural process diagram on uniform off-white #F5F7F4. Dark ink #12211C; restrained green #76B900; teal #2A9D8F for mIF. Modern plain sans-serif type, generous spacing, text at least 28px and easily readable on a projected slide. No title and no legend. No icons are necessary.
Exactly six rectangular rounded-corner node boxes. Two vertically separated, parallel source boxes on the left: 'Clinical model' at approximately x=14%, y=30%; 'mIF model' at x=14%, y=70%. 'Late fusion' at x=34%, y=50%. 'Patient contract' at x=55%, y=50%. 'Nemotron copilot' at x=76%, y=50%. 'Demo UI' at x=93%, y=50%. Make the Demo UI box narrower so it has a generous right page margin. First three boxes have a tiny secondary badge with exact word 'Future', marking integrations supplied by the other teams later. Patient contract, Nemotron copilot, and Demo UI form a single central horizontal output chain. Nemotron copilot has a pale green fill and green outline; mIF model teal outline; Clinical model and Late fusion gray-green outlines.
There must be EXACTLY SEVEN directed arrows with arrowheads on their destination, and no other arrows:
1 Clinical model -> Late fusion.
2 mIF model -> Late fusion.
3 Clinical model -> Patient contract.
4 mIF model -> Patient contract.
5 Late fusion -> Patient contract.
6 Patient contract -> Nemotron copilot.
7 Nemotron copilot -> Demo UI.
For arrow 3, use a clean orthogonal bypass route ABOVE the Late fusion box, from Clinical model right edge, rightward through open top whitespace and down into the upper boundary of Patient contract. For arrow 4, use a clean orthogonal bypass route BELOW Late fusion, from mIF model right edge, rightward through open bottom whitespace and up into the lower boundary of Patient contract. These bypass arrows must be distinct from the two diagonals into Late fusion. Do not merge arrows or let arrows cross any boxes or text. Late fusion right edge arrow 5 points straight into Patient contract left edge. All three predictions independently reach Patient contract, which is the sole input to Nemotron copilot. The model-training work is outside the copilot.
Keep labels verbatim and correctly spelled: 'Clinical model', 'mIF model', 'Late fusion', 'Patient contract', 'Nemotron copilot', 'Demo UI', and three 'Future' badges. No other labels, no patient counts, metrics, drug names, footer, logos, watermarks, decorations or screenshots. Diagram centered with abundant negative space.
```

## Selected cover generation prompt

```text
Use case: stylized-concept.
Asset type: professional architecture presentation cover background, very wide landscape 16:9.
Make an elegant abstract scientific-computing hero image with a STRICT blank-left composition. The left SIXTY PERCENT (60%) of the entire canvas is completely plain dark forest navy #12211C: no dots, no ribbons, no lines, no glow, no grid, no marks, all the way down to the bottom edge. This plain dark left area is essential text space. Confine every visible illustrative detail to the far RIGHT FORTY PERCENT (40%) of the canvas. On that right side only: a delicate green #76B900 and teal #2A9D8F abstract tissue-like point cloud in the upper-right corner with rare magenta accent dots, flowing down into thin orderly curved data traces, then a few beautiful translucent finely meshed computing surfaces in the lower-right corner. The flow is primarily VERTICAL within the rightmost 40%, not diagonal across the canvas. The lower-left and lower-center must remain empty dark background just like the upper-left. Restrained glowing details, premium quiet scientific aesthetic, deep subtle depth. The right-side illustration can fade softly into the plain dark backdrop within x=60–65% but may not extend further left. Clearly conceptual abstract art; no real microscopy or pathology. No text, numbers, letters, logos, watermark or labels.
```
