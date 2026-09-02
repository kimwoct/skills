---
name: conductor-board
description: Drive work through the Conductor kanban board (localhost:8798) — submit
  routed task cards, read the state machine, work tickets TDD-first, honor the verify
  contract, and close with evidence. Use whenever the user mentions the conductor board,
  submitting/planning/retrying a conductor task or card (t-xxx ids), the G0–G5 loop,
  board routes/roles (implement, plan, cheap, reason, verify, claude, delegate), quota
  fallback or gate events, or wants a task run by conductor agents — even if they just
  paste a t- card id.
---

# Conductor board workflow

The board is a kanban of *runs* executed by CLI agents. You talk to it via the
`conductor` CLI (repo: `~/backlog`, config `~/.conductor/config.json`, dashboard
`:8798`). The board never runs git itself; agents working a card do.

## 1. Read the board before acting

```sh
python3 conductor.py list            # all cards with [state] and executor
python3 conductor.py show t-xxxx    # one card: history, attempts, verification
python3 conductor.py agents         # enabled agents → roles
python3 conductor.py config         # effective config incl. quota block
```

States: `queued → running → verifying → done`, side states `needs-info`
(agent asked questions), `awaiting-approval` (HITL gate), `retry-wait`
(transient), `failed`, `cancelled`. Never force a state by hand-editing
kanban.json — use `edit | ready | clarify | retry | cancel`.

## 2. Submit with an explicit route

```sh
python3 conductor.py submit "[plan] <task title and requirements>"
```

Routes map to executors: `implement`→codex, `plan`→omp, `cheap`→pi,
`reason`/`verify`→dsh, `claude`→ollama GLM, `delegate`→herdr. Unprefixed
titles auto-classify (why/explain→reason, plan/design→plan, default
implement). Quote the route prefix, keep tasks self-contained — the worker
sees only the card text plus answered grill questions.

## 3. Know the quota fallback (shipped 2026-09-02)

Before dispatch a quota gate consults live telemetry; on exhaustion the card
reroutes once automatically (model-swap, then role-swap) and the history shows
`quota gate: <role> exhausted, rerouting to <fb>` / `auto quota fallback: …`.
A `quota-blocked` attempt means the premium executor was skipped on purpose.
After one automatic recovery a second quota failure parks in the operator
gate (`awaiting_decision`) — that needs a human `conductor edit`/dashboard
decision, not a retry loop. See docs/quota-fallback-spec.md (decisions ①–⑬)
and ADR 0003 in the backlog repo.

## 4. Work a card like a ticket (TDD)

For implementation cards: write the failing test first, implement to green,
keep the full suite passing, one commit per logical slice on a
`conductor/<topic>` branch. Close by running the card's `verify_cmd` /
`test_cmd` when present and putting the evidence in the card
(`conductor followup t-xxxx "<result + evidence>"`). Follow `/implement`
(→ `/tdd`, `/code-review`) for the full per-ticket discipline.

## 5. HITL answers

`needs-info` cards carry grill questions (`conductor show` shows them);
answer with `conductor clarify t-xxxx "A1: …"` then `conductor ready t-xxxx`.
`awaiting_decision` on failed cards expects an operator fallback decision —
approve via dashboard or decide via CLI; do not auto-approve.

## 6. Hygiene

- The daemon self-restarts on conductor.py changes; the dashboard (:8798) may
  need a manual kickstart after UI changes.
- Cooldowns live in `~/.conductor/quota-state.json` (30-min TTL, self-expiring).
- Never read `~/.conductor/telegram-token`; secrets stay out of source.
- E2E checks on the live board: prefer a tiny `[plan]`/`[cheap]` probe card
  over mutating real cards; restore any temporary config (e.g.
  `quota.exhausted_pct`) immediately after.
