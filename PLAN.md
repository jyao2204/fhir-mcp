# fhir-mcp build plan

A read-only MCP server that exposes a FHIR R4 clinical record to AI agents, against synthetic data.
Built by hand, in Python, over about three weeks from 12 October 2026.

## Rules

- You write every line in `src/` and `tests/`.
  AI is for reading docs, explaining an error, and reviewing a file you have already finished.
  Never for writing the file.
- If you could not walk an interviewer through a function, rewrite it.
- Small commits with real messages.
  The commit history is part of the evidence.
- Every working day ends with something that runs.
- v1 scope is fixed.
  Stretch items only after `v0.1.0` is tagged.

## Stack

- Python 3.13, `uv`, `ruff`, `pytest`.
- `mcp` 2.x (the official SDK): `from mcp.server import MCPServer`, tools via `@server.tool()`, plain `def` functions are fine.
  End `server.py` with `if __name__ == "__main__": server.run()` so `python -m fhir_mcp.server` starts it over stdio.
  For local testing, `uv run mcp dev src/fhir_mcp/server.py` opens the MCP Inspector (needs `npx`).
- `httpx` for HTTP, sync client.
- Test data: the public HAPI FHIR R4 server, `https://hapi.fhir.org/baseR4`.
  It is synthetic, public, and gets reset, so never depend on a specific patient ID in a test.

## Layout

```
src/fhir_mcp/
  server.py     MCP tools, thin: validate, call client, shape, return
  client.py     FHIR HTTP: get, search, pagination, error mapping
  shape.py      raw FHIR resources -> compact summaries
  config.py     env vars (base URL, timeout, page cap)
tests/
  fixtures/     real responses saved once, used offline
  test_client.py
  test_shape.py
  test_server.py
```

## v1 tools

| Tool | Does |
|---|---|
| `search_patients` | by name, birthdate or identifier; returns a compact patient list |
| `get_patient_summary` | demographics, active conditions, active medications, allergies, last few observations, in one compact object |
| `get_observations` | vitals and labs for a patient; filter by code and date; limit |
| `get_medications` | medication requests for a patient; filter by status |
| `get_encounters` | visits for a patient since a date |

The code that proves you can program lives under the tools:

- Pagination: FHIR returns Bundles with `next` links; follow them with a hard cap on pages.
- Shaping: raw FHIR is verbose; turn it into small, consistent, LLM-friendly summaries.
- Errors: 404s, `OperationOutcome` responses, timeouts, retries; map them to messages an agent can act on.
- Validation: IDs, dates, limits; bad input never reaches the network.
- Config: base URL, timeout, page cap from environment variables.
- Read-only by design, with one README paragraph on why.

## Days 1-3: setup and learning

- [x] Repo created with `uv`, `ruff`, `pytest`, CI, licence, this plan (scaffold).
- [ ] Read the SDK quickstart: https://py.sdk.modelcontextprotocol.io/v2/
- [ ] Write `src/fhir_mcp/server.py` with one hello-world tool (for example `ping` returning a string).
- [ ] Register it with Claude Code and see a tool call succeed:
      `claude mcp add fhir -- uv --directory /Users/jerwynyao/Documents/jerwyn-personal/fhir-mcp run python -m fhir_mcp.server`
- [ ] Read enough FHIR R4 to know: Patient, Observation, Condition, MedicationRequest, Encounter, AllergyIntolerance, Bundle, and search parameters.
      Start at https://hl7.org/fhir/R4/resourcelist.html and https://hl7.org/fhir/R4/search.html
- [ ] Write a scratch script (not committed) that fetches one Patient and one Observation search from HAPI with `httpx` and prints the raw JSON.
      Look hard at how verbose it is.

Done when: a hello-world server answers Claude, and you have seen real FHIR JSON.

## Week 1: the client and two tools

- [ ] `config.py`: base URL, timeout, max pages, from env with defaults.
- [ ] `client.py`: get a resource by type and ID; search with parameters; follow `next` links with a cap; map HTTP and `OperationOutcome` errors to one exception type.
- [ ] Save a few real responses into `tests/fixtures/` and write `test_client.py` against them (no network in tests).
- [ ] `shape.py`: Patient and the pieces `get_patient_summary` needs.
- [ ] `server.py`: `search_patients` and `get_patient_summary`.

Done when: both tools work in Claude and the tests pass offline.

## Week 2: the rest, usable by a stranger

- [ ] `get_observations`, `get_medications`, `get_encounters`.
- [ ] Every summary has the same structure; `test_shape.py` proves it.
- [ ] Validation, timeouts, caps; `test_server.py`.
- [ ] One live integration test, marked and skipped by default.
- [ ] CI green on every push.
- [ ] README: what it is; why you built it (one paragraph on mpdAI, nothing confidential); install snippet for Claude Code and Claude Desktop; a reference for each tool; design notes; limitations.

Done when: someone who has never spoken to you can install and use it from the README alone.

## Week 3: polish and publish

- [ ] Edge cases: no results, a huge record, the server down.
- [ ] Demo: a short transcript or GIF of Claude summarising a patient.
- [ ] Final README pass.
- [ ] Tag `v0.1.0`.
- [ ] Link on the CV and LinkedIn; one post.
- [ ] Article: what you learned shipping an LLM interface to clinicians, failures included.
      No MPD code, no patient data, nothing about the founder.
      May slip into week 4.

Done when: `v0.1.0` is tagged, the link is on the CV, and the article is drafted.

## Stretch (after v0.1.0 only)

- Remote deployment: `server.run("streamable-http")` (or `server.streamable_http_app()` under uvicorn), a Dockerfile, and a CDK stack that runs it on ECS Fargate behind an ALB with TLS, with a bearer token or OAuth in front.
  This is the AWS CDK and Fargate claim on the CV, in public.
- `docker-compose` for a local HAPI server loaded with Synthea data.
- TTL cache on patient summaries.
- Token-budget-aware summaries that say what they left out.
- Write tools (for example create an Appointment) behind an explicit flag.
