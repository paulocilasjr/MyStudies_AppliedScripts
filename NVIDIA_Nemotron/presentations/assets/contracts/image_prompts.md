# Contract/runtime diagram prompts

Mode: built-in ImageGen. Selected images were copied into this directory after visual review. No programmatic drawing or raster editing was used. All selected PNGs are 1672 × 941 pixels, approximately 16:9.

## prompt.png

Generation prompt used for the selected source image:

```text
Use case: infographic-diagram
Asset type: technical architecture image for a PowerPoint slide.
Canvas: exactly wide 16:9 landscape, high resolution, approximately 2048 by 1152 pixels. Keep large blank borders above and below the graph and do not crop tightly around nodes. Create a clean flat technical workflow diagram. Use a solid off-white background #F5F7F4, dark navy #12211C text and lines, green #76B900 accents, and restrained muted teal. Generous whitespace and tidy rounded rectangular nodes. No title, no footer, no icons, no textures, no gradients, no shadows, no decorative elements. All labels must be LARGE bold sans-serif, about 44 pixels if the image is 1672 pixels wide, easily readable on a slide. Multi-line labels within nodes are allowed.
Show exactly this main left-to-right pipeline centered horizontally: "Validated evidence" -> "JSON payload" -> "Chat template" -> "Token budget" -> "Nemotron" -> "Generated JSON".
Place a separate node labeled "System rules" above "Chat template", with one vertical arrow from "System rules" into "Chat template".
Place a separate node labeled "Ground truth" below "JSON payload". Show a dashed upward connector toward "JSON payload" ending with a prominent navy crossed blocking symbol and NO arrowhead entering the JSON payload. Put the exact short text "Withheld" beside the blocked connector. This is a deliberately BLOCKED connection: ground truth does not enter the prompt.
Render these exact labels verbatim: "Validated evidence", "JSON payload", "Chat template", "Token budget", "Nemotron", "Generated JSON", "System rules", "Ground truth", "Withheld".
There must be no other nodes, edges, arrows, text, titles or claims. Do not imply that prompt injection is impossible. Make the output polished, simple and technically precise.
```

Targeted built-in edit applied to that generated source:

```text
Use case: precise-object-edit
Edit target: the provided technical workflow diagram.
Change ONLY the blocked connection between "Ground truth" and "JSON payload". Remove the upward arrowhead that currently touches the bottom of "JSON payload", and remove the dashed segment ABOVE the large X blocking symbol. Keep the dashed segment from the "Ground truth" box upward to the blocking X. The large X and exact label "Withheld" remain. There must now be a clear blank gap between the X and the JSON payload box, with NO connector or arrowhead entering JSON payload from Ground truth.
Preserve everything else exactly: the 1672-by-941 wide canvas, all existing node positions, all exact labels, all main left-to-right pipeline arrows, System rules arrow, colors, large font sizes, whitespace, and style. No extra text or objects. This single change must make ground truth clearly withheld from the prompt.
```

Visual review: main evidence pipeline and System rules edge retained. Ground truth ends at a blocked X labeled Withheld, with a blank gap before JSON payload.

## quality.png

```text
Use case: infographic-diagram
Asset type: technical architecture image for a PowerPoint slide.
Canvas: exactly wide 16:9 landscape, high resolution, approximately 2048 by 1152 pixels. Keep a large blank border above, below, and beside the graph. Do not crop tightly to content.
Style: clean flat technical diagram, solid off-white background #F5F7F4, dark navy #12211C text and lines, green #76B900 accents, muted teal secondary accents. Large bold sans-serif text around 54 pixels at 2048 width (about 44 pixels at 1672 width). Neat rounded rectangular nodes and clear single-arrowhead connectors. Generous whitespace. No slide title, no footer, no icons, no gradients, no shadows, no decorations.
Show exactly this topology. Left-to-right: "Generated JSON" -> "Heuristic screen". From "Heuristic screen", split into TWO branches: the upper branch has a small connector label "Pass" and leads to a node "Model interpretation"; the lower branch has connector label "Reject" and leads to a node "Deterministic fallback". These two interpretation nodes each have a separate arrow converging into "Facts + review note", which then has one arrow to "Result".
On a separate lower row, show ONLY "Engine failure" -> "Stop run". This lower failure row has NO connection to "Heuristic screen", "Deterministic fallback", "Facts + review note", or "Result". An inference engine failure stops the run; it is not a narrative screen rejection.
Render exactly these labels verbatim: "Generated JSON", "Heuristic screen", "Pass", "Reject", "Model interpretation", "Deterministic fallback", "Facts + review note", "Result", "Engine failure", "Stop run". Line breaks inside node labels are allowed.
No additional nodes or edges. Do not claim that screening verifies medical correctness. Preserve large readable type.
```

Visual review: screen pass/reject paths merge into facts plus review note; the engine failure path terminates separately at Stop run.

## publication.png

```text
Use case: infographic-diagram
Asset type: technical architecture image for a PowerPoint slide.
Canvas: exactly wide 16:9 landscape, high resolution, approximately 2048 by 1152 pixels. Keep a large blank border above, below, and beside the graph. Do not crop tightly to content.
Style: clean flat technical diagram, solid off-white background #F5F7F4, dark navy #12211C text and lines, green #76B900 accents, muted teal secondary accents. Large bold sans-serif text around 54 pixels at 2048 width (about 44 pixels at 1672 width). Neat rounded rectangular nodes and clear single-arrowhead connectors. Generous whitespace. No slide title, no footer, no icons, no gradients, no shadows, no decorations.
Show exactly this successful artifact-publication graph. The main left-to-right row is "Input snapshot" -> "SHA256 + manifest" -> "Stage artifacts" -> "Atomic run directory" -> "Demo reader".
Place a separate node "Narratives + metrics" above "Stage artifacts", with one downward arrow into "Stage artifacts".
Place a completely separate lower-row failure graph "Inference failure" -> "No partial results". This failure row must have NO arrows into "Stage artifacts", "Atomic run directory", or "Demo reader".
Render exactly these labels verbatim: "Input snapshot", "SHA256 + manifest", "Stage artifacts", "Atomic run directory", "Demo reader", "Narratives + metrics", "Inference failure", "No partial results". Line breaks inside node labels are allowed.
This is a simplified success publication pipeline. No additional nodes, edges or text. Preserve very large readable labels and whitespace.
```

Visual review: successful artifact staging/publication and inference-failure paths remain separate.

## api.png

```text
Use case: infographic-diagram
Asset type: technical architecture image for a PowerPoint slide.
Canvas: exactly wide 16:9 landscape, high resolution, approximately 2048 by 1152 pixels. Keep a large blank border above, below, and beside the graph. Do not crop tightly to content.
Style: clean flat technical diagram, solid off-white background #F5F7F4, dark navy #12211C text and lines, green #76B900 accents, muted teal secondary accents. Large bold sans-serif text around 54 pixels at 2048 width (about 44 pixels at 1672 width). Neat rounded rectangular nodes and clear single-arrowhead connectors. Generous whitespace. No slide title, no footer, no icons, no gradients, no shadows, no decorations.
Show exactly this local service request/response diagram. Main top row reads left-to-right: "UI backend" -> "Validate request" -> "Copilot lock" -> "GPU engine" -> "Result JSON".
Draw a clear long return connector BELOW the main row, starting from "Result JSON" and pointing LEFT back into "UI backend". Label the return connector "Response". Its arrowhead must point at "UI backend"; this return path is not a new node.
Draw one large thin rounded rectangular GROUP OUTLINE labeled "Local service" containing exactly "Validate request", "Copilot lock", "GPU engine", and "Result JSON". "UI backend" stays outside this group.
On a separate lower row, show "Health check" -> "Service state", positioned separately from the GPU request row. This health-check arrow must have NO connection to "GPU engine", "Copilot lock", or "Result JSON". A health check reports service state and does not load the model or promise model readiness.
Render exactly these labels verbatim: "UI backend", "Validate request", "Copilot lock", "GPU engine", "Result JSON", "Response", "Local service", "Health check", "Service state". Line breaks inside nodes allowed.
No extra nodes, no extra arrows, no title/footer. No claims of authentication or deadline enforcement. Keep the group outline, return path, and isolated health branch unambiguous.
```

Visual review: Local service contains exactly four request nodes; response arrow returns to UI backend; Health check only leads to Service state.

## quality_v2.png

Mode: built-in ImageGen edit of quality.png. Original quality.png is preserved.

```text
Use case: text-localization
Edit target: the provided technical workflow diagram.
Make exactly ONE text change. In the bottom-row rectangle currently labeled "Stop run", replace that label with the exact two-line label:
Fail
operation
Use the same dark navy bold sans-serif type, same approximate font size, centered in the same existing rectangle. The exact resulting wording is "Fail operation".
Preserve all other content as closely as possible: canvas dimensions 1672 by 941, node positions and sizes, every other label, all colors, whitespace, arrows and arrowhead directions, the full screen Pass/Reject branching topology, and the isolated bottom Engine failure branch. Keep "Engine failure" unchanged. Do not move, add, remove, redraw or relabel any other element. No title, caption, footer or extra text.
```

Visual review: exact two-line Fail operation label is legible. All other node labels, layout, and arrow topology are preserved; the Engine failure branch stays separate from screening fallback.
