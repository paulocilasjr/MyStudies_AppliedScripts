https://www.nature.com/articles/s41592-025-02707-1
https://www.nature.com/articles/s41587-025-02852-0
https://www.nature.com/articles/s41587-026-03135-y
https://www.nature.com/articles/s41467-026-76277-x
https://www.nature.com/articles/s41746-026-03423-6
https://www.cell.com/cell-systems/abstract/S2405-4712(26)00240-1?_returnURL=https%3A%2F%2Flinkinghub.elsevier.com%2Fretrieve%2Fpii%2FS2405471226002401%3Fshowall%3Dtrue
https://www.nature.com/articles/s41587-024-02534-3


1. What ours does and why we built it
Agents working through the Galaxy API used far more tokens than agents writing local code on the same tasks. The traces showed two causes:

many more model round trips: polling running jobs, retrying payloads after guessing the schema, re-checking jobs that had already finished;
long API responses (tool lists, full schemas, job details) that stay in the context and are resent with every later call.


Our MCP is built to cut both:

One call per job: it checks the inputs, submits once, waits until the job finishes and returns the result, so the agent doesn’t poll or resubmit.
Short replies: tool search returns a short list of candidates. A tool schema shows only the fields and conditional branch the agent asked for, with a fill-in template that uses the real parameter paths. History listings and dataset previews are capped. A finished run returns the job state, check results, output IDs and small text outputs.
No repeats: outputs, unchanged results and schemas already shown in the session are shortened.
Full details kept outside the conversation: the complete request, reply and job record go to a file, and the reply points to it. The agent reads only what it needs, and we use these files for scoring.
Fewer failed submissions: equivalent parameter formats are not flagged as mismatches, and user-defined tool definitions are checked before the tool is created.


Tools (9):
Find and set up a tool

search_galaxy_tools: top matches among installed tools (current versions) by package, tool family, operation or metric
inspect_galaxy_tool: the tool’s live input schema, limited to the fields and branch the agent asks for
Run

run_galaxy_tool_and_wait: check inputs, submit once, wait, return the outputs or the error
run_galaxy_udt_and_wait: create and run a user-defined tool (a command in a container), then wait
wait_for_galaxy_jobs: keep waiting on jobs that were already submitted, without resubmitting
stage_workspace_file: upload a local file and wait until it’s ready
Check data

inspect_galaxy_history: datasets in the history, filtered by name or type
peek_galaxy_dataset: preview and column info for one dataset
inspect_archive_inventory: files inside an archive


2. Difference from galaxy-mcp

galaxy-mcp is general-purpose and covers most of the Galaxy API: histories, uploads, collections, tools, user tools, jobs, workflows, IWC search/import/invoke and pages. Ours only covers finding, running and checking tools on the data in one history.
galaxy-mcp’s run_tool returns as soon as the job is submitted, and the agent checks the status afterwards. Ours returns when the job is done.
Ours is tuned for token cost in an agent loop: short replies, no repeated content, and full records saved to files.
Feature-wise, ours is basically a subset of galaxy-mcp. We contribute what we learn back to galaxy-mcp as PRs.
