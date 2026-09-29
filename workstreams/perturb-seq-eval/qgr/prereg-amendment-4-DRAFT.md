# Pre-registration AMENDMENT 4 — DRAFT (locks after CTO approval of the costed plan; before any data)

`prereg_version` -> `v0.6.0-a4` (fresh, empty LLM cache namespace per A2-8). Ruled by the principal 2026-09-29 (via AskUserQuestion and via the
CTO, #473/#476): the LLM provider moves from OpenRouter to the Anthropic API, total spend under $30, cheapest models where they pass the role probe.

### A4-1: LLM condition (replaces Convention 5's provider and pins the roster)
"A rotating pool of Anthropic Claude models called through the Anthropic Messages API, with failover; the roster is pinned by model id and
recorded in provenance with each model's preflight liveness per role: `claude-haiku-4-5-20251001` for DataCurator, Literature, Architect and Trainer;
`claude-sonnet-5-5` for the Validator; each role fails over to the other. Every reply is constrained to the role's JSON schema by structured outputs;
`model_id` is recorded per call. Thinking is off (none on Haiku 4.5; `between_tools` at low effort on Sonnet 5.5). max_tokens per role is the dry run's observed output x 1.5."
Rationale: 6/8 free OpenRouter models had disappeared and the rest rate-limited into fallbacks (fatal under A2-1); the paid OpenRouter roster
(ruling of 2026-09-28) was superseded by the principal's Anthropic ruling. Roster = cheapest model passing each role's strict schema probe,
with the Validator on a different tier from the roles it judges.

**Implementation notes in A4-1 (CTO #480/#482):** every call records `stop_reason`, `stop_details.category` (on refusal), the requested and the
served model id (asserted equal), `usage` and the per-role `max_tokens` ceiling (4x the dry run's observed maximum, minimum 256: DataCurator 256, Literature 1316, Architect 256, Trainer 256, Validator 1192);
`refusal` and a served-model mismatch are fallback-class events (run invalid); `max_tokens` gets one retry at 2x, both billed, a second is a fallback-class event;
the request never carries a `fallbacks` parameter. Sampling: Haiku 4.5 at temperature 0.3 (raw body; the same value the OpenRouter runs used), Sonnet 5.5 at API
defaults (non-default rejected); thinking off on both (`between_tools` + effort low on Sonnet 5.5). Wire schema: structured outputs omit numeric ranges and express
the two free-form maps as key/value pair arrays converted before parsing; ranges are enforced by the role schema after parsing (out of range = schema failure).

### A4-2: spend
Total ceiling $30 (principal). The pre-registered lines stay: $12 stop-and-report and $28 kill, on TOTAL spend = GPU wall-clock + LLM usage
(API-reported input/output/cache tokens x the pinned list prices: Haiku 4.5 $1/$5 per MTok, Sonnet 5.5 $2/$10; source: Anthropic first-party
pricing as tabulated in the claude-api skill, cached 2026-09-25) + $1.3 carried in from the aborted run 20260928T220916Z-291efad.
Dry run 2026-09-29 (35 calls in three authorised passes, $0.0548). Grid: 123 runs x 3 rounds = 1845 calls. Measured-usage projection $7.19 (LLM 2.93, GPU 2.90 incl. LLM latency on the held A100, prior 1.3, dry run); worst case at the output caps $13.96. Lines unchanged: $12 stop-and-report, $28 kill, $30 ceiling. Earlier estimate at the upper bound: $9.30 (costed plan, measured input tokens).

### A4-3: caveats stated in the methods
Single model family (no cross-family generality claim; H3's entropy may be lower than under a multi-family pool). Same-family judge: the Validator
is a different tier (Sonnet 5.5) from the four Haiku 4.5 proposer roles; residual same-family bias is acknowledged.

### Unchanged
Everything else in amendments 1-3 (A2-1 fallback = run invalid; A2-8 empty namespace + replay detection; A3-3 required Validator threshold; A3-4
count = 7). Text it changes in `PREREGISTRATION.md`: Convention 5; "Run record" (LLM cost components); the Amendments preamble.
