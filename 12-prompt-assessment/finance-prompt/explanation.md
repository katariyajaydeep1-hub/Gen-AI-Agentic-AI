# Explanation — Stock Insights Engine Prompt

## Design Philosophy

The prompt is structured in clearly-labeled blocks rather than free
prose. Modern LLMs follow labeled, rule-numbered instructions far more
reliably than narrative descriptions of desired behavior. Each block
addresses one concern:

| Block | Purpose |
|---|---|
| SYSTEM ROLE | Identity and scope boundary (non-advisor, non-predictor) |
| PRIMARY DIRECTIVE | The single most important rule: CONTEXT is truth |
| INPUT BLOCKS | Clean delimitation of trusted-output vs untrusted-input |
| RULES OF GROUNDING (R1-R5) | RAG hygiene + prompt-injection defense |
| RULES OF SAFETY (S1-S4) | Hard prohibitions on advisory language |
| RULES OF DETERMINISM (D1-D3) | Output stability for downstream parsers |
| OUTPUT SCHEMA | Machine-readable contract |
| CONFIDENCE RUBRIC | Turns a vague signal into a 3-level decision |
| SILENT REASONING POLICY | Prevents CoT leakage into structured output |
| PRE-OUTPUT VALIDATION | Self-check before emission, reduces failures |
| FEW-SHOT EXAMPLE | Shows ideal format for the model to imitate |

## How Each Assessment Constraint Is Enforced

**"No financial advice (no Buy/Sell)"**
Enforced in three places: explicit role denial in SYSTEM ROLE, hard
prohibition in S1, refusal protocol in S4 for direct asks, and a
required non-advisory contract in the `recommendation` field
description.

**"No prediction of prices"**
Enforced in S2 and reinforced in the SYSTEM ROLE ("NOT a price
predictor"). The schema offers no field that could carry a price
target, removing the temptation.

**"Use only provided context"**
The PRIMARY DIRECTIVE states this as the top-level rule. R1 repeats
it as an enumerated rule. R4 prevents number paraphrasing (which can
introduce subtle errors). PRE-OUTPUT VALIDATION makes the model
re-check this before emitting.

**"No hallucination"**
Addressed via the same grounding rules above, plus the confidence
rubric — the model is instructed to lower confidence and use sentinels
rather than fabricate.

**"If insufficient → say 'Insufficient data'"**
R2 defines the sentinel explicitly. The schema's
`valuation_comment` description names the sentinel inline so the model
knows when to use it. Array fields default to `[]` for missing data.

**"Structured output required"**
D1, D2, D3 together enforce strict JSON. The few-shot example shows
exactly what good output looks like. In the calling code we additionally
pair this with `response_format={"type": "json_object"}` on the API
call for belt-and-suspenders enforcement.

## Advanced Techniques Used

1. **Few-shot exemplar** — the EXAMPLE block teaches format by
   demonstration. Far more effective than describing format in prose.
2. **Numbered rule groups** — R1-R5, S1-S4, D1-D3 — let the model
   reference rules internally and let humans audit them.
3. **Prompt injection defense** — R3 explicitly tells the model to
   treat embedded instructions in CONTEXT and USER_QUERY as data,
   not commands. This is critical because in a RAG system the
   retrieved documents are untrusted text.
4. **Sentinel values** — "Insufficient data" gives the model an
   explicit "way out" so it doesn't feel pressure to invent.
5. **Pre-output self-validation** — the model is asked to silently
   audit its own draft before emitting. This reduces malformed
   outputs significantly in our testing.
6. **Confidence rubric** — three discrete levels (high / medium /
   low) instead of a vague "be confident". Discrete labels are
   far more stable than free-form confidence language.
7. **Silent CoT** — the model is permitted (encouraged) to reason
   internally but forbidden from exposing scratchpad in the JSON
   output.

## Edge Cases Considered

| Edge case | How the prompt handles it |
|---|---|
| User asks "just Buy or Sell, one word" | S4 + recommendation contract — refuses directive, still populates other fields |
| CONTEXT is sparse or empty | R2 sentinel; confidence drops to "low" |
| CONTEXT contains a prompt injection ("ignore previous instructions") | R3 treats it as data |
| Query about Company A, CONTEXT about Company B | R5 — populate from CONTEXT, flag mismatch in notes |
| User asks for price target | S2 + missing field in schema = nothing to populate |
| Model wants to add "as of 2024..." external context | R1 + R4 + PRE-OUTPUT VALIDATION |

## Why This Will Pass The Trainer's Common Mistakes Filter

The assessment lists these common mistakes. Here's how each is prevented:

- **Giving Buy/Sell advice** → S1, S3, S4
- **Adding external knowledge** → R1, R4, PRE-OUTPUT VALIDATION
- **Missing structure** → strict schema + few-shot example + D3
- **Ignoring risks** → mandatory `risks` field + market-risk language required in `recommendation`

## Configuration Recommendations

| Setting | Value | Why |
|---|---|---|
| Model | `gpt-4o-mini` or `gpt-4.1-mini` | Cheap, strong JSON adherence |
| `temperature` | `0` | Determinism — same input always gives same output |
| `response_format` | `{"type": "json_object"}` | Forces parseable JSON at the API level |
| `max_tokens` | `800` | Comfortable headroom for a fully-populated schema |
| Retry policy | 2 retries with `json.loads` validation | Catches the rare invalid-JSON case |
