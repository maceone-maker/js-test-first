# Specification: cost-center-intelligence-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Data Dependencies

_No Data Product ORD IDs. All data access is via OData APIs through a generated MCP server._

---

## API Integration

| API Name | ORD ID | Spec File | Type |
|---|---|---|---|
| Cost Center - Read | `sap.s4:apiResource:CE_COSTCENTER_0001:v1` | `api-specs/CE_COSTCENTER_0001.edmx` | OData / EDMX |
| Cost Center Hierarchy | `sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1` | `api-specs/CE_COSTCENTERHIERARCHY_0001.edmx` | OData / EDMX |

**MCP tool scope (CE_COSTCENTER_0001):**
```
MCP API: sap.s4:apiResource:CE_COSTCENTER_0001:v1
MCP tool scope: read-only
Resources in scope: CostCenter, CostCenterText
```

**MCP tool scope (CE_COSTCENTERHIERARCHY_0001):**
```
MCP API: sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1
MCP tool scope: read-only
Resources in scope: CostCenterHierarchy, CostCenterHierarchyNode
```

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` before implementing any task
- [ ] Bootstrap agent code in `assets/cost-center-intelligence-agent/` using the `sap-agent-bootstrap` instructions from the agent skill (invoke from inside `assets/cost-center-intelligence-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## MCP Server Generation

- [ ] Invoke the `mcp-translation-file` skill for `CE_COSTCENTER_0001`:
  - Input spec: `specification/cost-center-intelligence-agent/api-specs/CE_COSTCENTER_0001.edmx`
  - API ORD ID: `sap.s4:apiResource:CE_COSTCENTER_0001:v1`
  - API type: `edmx`
  - MCP tool scope: read-only
  - Resources in scope: `CostCenter`, `CostCenterText`
  - The generated MCP asset will be registered in `solution.yaml`
- [ ] Invoke the `mcp-translation-file` skill for `CE_COSTCENTERHIERARCHY_0001`:
  - Input spec: `specification/cost-center-intelligence-agent/api-specs/CE_COSTCENTERHIERARCHY_0001.edmx`
  - API ORD ID: `sap.s4:apiResource:CE_COSTCENTERHIERARCHY_0001:v1`
  - API type: `edmx`
  - MCP tool scope: read-only
  - Resources in scope: `CostCenterHierarchy`, `CostCenterHierarchyNode`
  - The generated MCP asset will be registered in `solution.yaml`
- [ ] Invoke `setup-solution` skill to create/update `solution.yaml` and `asset.yaml` files covering both the agent and the two MCP server assets

---

## Project-Specific Tasks

### R1 — Natural Language Cost Center Count

- [ ] Implement the system prompt section in `app/agent.py` that instructs the agent to:
  - Answer questions about the total number of active cost centers
  - Use the `list_cost_centers` (or equivalent `$count`-capable) MCP tool to retrieve the count
  - Return a clear numeric answer with a plain-language sentence (e.g. "You currently have 342 active cost centers.")
  - Handle phrasing variations: "how many cost centers", "count of cost centers", "total cost centers", "number of cost centers"
- [ ] Implement the tool call logic in `agent.py` that maps the count intent to the correct MCP tool and returns the `$count` result
- [ ] Validate: ask "how many active cost centers do we have?" and confirm a numeric answer is returned

### R2 — Top 5 Cost Centers by Actual Spend

- [ ] Implement the system prompt section that instructs the agent to:
  - Answer questions about highest-spending cost centers
  - Use the MCP tool to retrieve cost centers ordered by actual costs descending, limited to 5
  - Return a ranked list with cost center ID, name, and actual cost amount for each entry
  - Handle phrasing: "top 5 cost centers", "highest spending cost centers", "cost centers with most spend", "where are costs highest"
- [ ] Implement the tool call logic that passes `$top=5&$orderby=ActualCosts desc` (or equivalent OData parameters) to the cost center MCP tool
- [ ] Validate: ask "which are the top 5 cost centers by spend?" and confirm a ranked list of 5 with ID, name, and cost is returned

### R3 — Cost Center Detail Drill-Down

- [ ] Implement the system prompt section that instructs the agent to:
  - Answer follow-up questions about a specific cost center referenced by ID or name
  - Use the MCP tool to retrieve a single cost center's details: name, responsible person, actual costs, and controlling area / hierarchy
  - Support follow-up references within the same conversation (e.g. "tell me more about the first one", "what about cost center 1000?")
  - Combine data from both `CE_COSTCENTER_0001` (name, responsible person, actual costs) and `CE_COSTCENTERHIERARCHY_0001` (hierarchy position) where available
- [ ] Implement tool call logic to:
  - Resolve cost center by ID or name from context
  - Call the cost center details MCP tool
  - Call the cost center hierarchy MCP tool to enrich the response with hierarchy position
- [ ] Validate: ask "tell me about cost center 1000" and confirm name, responsible person, actual costs, and hierarchy are returned

### R4 — Per-User Identity Propagation via IAS

- [ ] Confirm in `guidelines-agent-mcp.md` how principal propagation is configured for MCP tool calls in the agent gateway
- [ ] Ensure the agent does NOT use a shared service account credential — the MCP layer must forward the calling user's identity token to S/4HANA
- [ ] In `asset.yaml`, add the MCP server `requires` entries with the exact ORD IDs of both generated MCP assets; ensure the `requires` block does not include any hard-coded credential overrides
- [ ] Document in the agent's system prompt that identity context is propagated automatically — the agent must never include user credentials in tool call parameters
- [ ] Validate: confirm that when the agent gateway forwards requests to S/4HANA, the controller's identity token is used (verified by the IAS configuration, not the agent code itself)

### R5 — Graceful Error Handling

- [ ] Implement error handling in `agent.py` for the following scenarios:
  - **Authorization error** (HTTP 403 / OData error code): agent responds with "You don't have access to this cost center data. Please contact your system administrator."
  - **Service unavailable** (HTTP 500 / 503 / network timeout): agent responds with "The SAP S/4HANA system is currently unavailable. Please try again shortly."
  - **No results found**: agent responds with "No cost centers matching your query were found. Please check your input and try again."
  - **Ambiguous intent** (agent cannot classify the question): agent asks one clarifying question, then falls back to listing supported queries if still unresolved
- [ ] Relay all MCP tool errors verbatim to the error handler — do NOT fabricate or soften error messages
- [ ] Validate: mock a 403 response and confirm the correct plain-language message is returned

### R6 (High-Want) — Controlling Area Awareness

- [ ] Extend the system prompt to recognize when a user specifies a controlling area in their question (e.g. "in controlling area A000")
- [ ] Pass the controlling area as a filter parameter (`$filter=ControllingArea eq 'A000'`) to the relevant MCP tools
- [ ] Validate: ask "how many cost centers are in controlling area A000?" and confirm the filter is applied

### R7 (High-Want) — Cost Center Hierarchy Context

- [ ] Ensure cost center hierarchy information is always included in drill-down responses (R3) by calling `CE_COSTCENTERHIERARCHY_0001` as a secondary enrichment call
- [ ] Format the hierarchy path clearly in the response (e.g. "Hierarchy: Corporate > Finance > Controlling > Cost Center 1000")
- [ ] Validate: confirm hierarchy path appears in all drill-down responses

---

## Agent System Prompt Requirements

- [ ] Scope the system prompt strictly to cost center queries — the agent must decline unrelated questions with: "I can only assist with cost center queries. Please ask about cost center counts, top spenders, or specific cost center details."
- [ ] Include explicit guardrails in the system prompt:
  - "Never modify, create, or delete cost center data."
  - "Never fabricate cost center figures — always use tool results."
  - "If a tool returns an error, relay the appropriate message to the user without guessing the correct answer."
- [ ] Define the supported query categories in the system prompt so the agent can guide users when their intent is unclear

---

## Business Instrumentation

- [ ] Implement structured logging and OpenTelemetry spans for all 5 milestones from the PRD. Extract business logic from `stream()` into a plain async helper to avoid `GeneratorExit` context errors (see `guidelines-agent-python.md`):

  | Milestone | Log on achievement | Log on miss |
  |---|---|---|
  | M1: S/4HANA connectivity | `M1.achieved: S/4HANA Cost Center API connection established with IAS principal propagation` | `M1.missed: S/4HANA Cost Center API connection failed — check IAS trust configuration and API availability` |
  | M2: Count query resolved | `M2.achieved: cost center count query resolved successfully — count returned to controller` | `M2.missed: cost center count query did not resolve — intent not classified or API call failed` |
  | M3: Top-5 by spend returned | `M3.achieved: top-5 cost centers by spend returned successfully` | `M3.missed: top-5 query did not complete — ranking logic failed or API returned insufficient records` |
  | M4: Drill-down answered | `M4.achieved: cost center detail drill-down completed — all attributes returned` | `M4.missed: cost center detail drill-down incomplete — one or more attributes missing or API call failed` |
  | M5: Agent live in production | `M5.achieved: agent live in production — controller identity propagation confirmed` | `M5.missed: production deployment incomplete or IAS trust not validated with real controller identity` |

- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [ ] After `mcp-translation-file` skill completes for both APIs, verify `solution.yaml` contains both MCP server assets
- [ ] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — see `guidelines-agent-python.md` for the canonical pattern
- [ ] Add both MCP server `requires` entries to `asset.yaml`:
  - One entry for the `CE_COSTCENTER_0001` MCP server (use the ORD ID from the generated asset)
  - One entry for the `CE_COSTCENTERHIERARCHY_0001` MCP server (use the ORD ID from the generated asset)
- [ ] Generate `mcp-mock.json` using the `mcp-mock-config` skill (required before tests can run)

---

## Testing

- [ ] `conftest.py` only sets `IBD_TESTING=true`
- [ ] Write unit tests in `assets/cost-center-intelligence-agent/tests/`, one per tool/intent handler:
  - `test_cost_center_count.py` — mock MCP returning a count; assert numeric answer returned
  - `test_top_cost_centers.py` — mock MCP returning 5 cost centers ordered by spend; assert ranked list returned
  - `test_cost_center_details.py` — mock MCP returning a single cost center; assert name, responsible person, costs, hierarchy in response
  - `test_error_handling.py` — mock 403 and 503 MCP responses; assert correct plain-language messages returned
  - `test_guardrails.py` — send an off-topic question; assert agent declines with the scoped refusal message
- [ ] Write one integration test in `tests/test_integration.py` executing end-to-end agent flow with mocked LLM and mocked MCP responses
- [ ] Run `pytest` from `assets/cost-center-intelligence-agent/` (no args); if coverage < 70%, add tests until threshold met
- [ ] Run `pytest` again to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/cost-center-intelligence-agent/`
