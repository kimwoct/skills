---
name: pstack-benchmark-checklist
description: Validate a runtime performance measurement before reporting a speedup, regression, or technology choice. Check the limiter, comparable tuning, errors, completed work, physical limits, repetitions, and end-to-end relevance; not a replacement for agent reliability evals.
license: MIT
metadata:
  source: cursor/plugins/pstack/skills/benchmark-checklist
  upstream-commit: d0ef80d86795816da932a153458c5dbe192d294e
---

# Validate the performance number

A plausible number can measure fast rejection, cached or skipped work, an untuned configuration, a saturated load generator, or noise. Establish what it means before acting on it.

## Define the claim

Write the sentence the result is meant to support, with units, workload/data size, concurrency, and the part of the user path being measured. Read the measurement script: what is timed, counted, awaited, and ignored? Record versions, hardware, build flags, cache conditions, and competing load using tools available on the host. Do not require Linux-only commands on another OS.

For an explicitly requested rough ballpark, one run is acceptable if correctness and completed-work checks pass and the report labels it a single-run estimate. A choice between implementations or a claimed speedup needs the fuller comparison below.

## Check the measurement against execution

1. **Name the limiter.** Ask why throughput is not twice as good or latency half as large. Use a separate profiling/counter run so profiler overhead does not contaminate the reported timings; map the observed hot path or resource limit to source. Check the load generator too. Source-reading alone is not a measured limiter.
2. **Make each side comparable.** Use production-intended release builds, versions, data, batching, transactions, pools, and appropriate warm/cold cache conditions. Tune every option for its intended use before recommending one. If one remains untuned, do not present that comparison as intrinsic implementation superiority or choose an adoption winner from it.
3. **Check physical and arithmetic limits.** Compare throughput with CPU, disk, network, and per-operation cost. Under a fixed serial workload, eliminating a component responsible for 10% of elapsed time saves at most 10% of the time, or raises throughput by about 11.1%. Distinguish time reduction from throughput gain. A result beyond a relevant ceiling suggests different work, caching, overlap, or a harness error that must be explained.
4. **Count errors and validate results.** Capture failures, non-success responses, timeouts, and retries alongside successes. Assert output correctness, not just presence. A fast failed request is not successful throughput; include all requested work in the denominator.
5. **Confirm the work completed inside the timed region.** Observe the requests reaching the service, bytes consumed, rows or files persisted, and results used. Await promises, consume lazy iterators, and prevent dead-result elimination where applicable. State whether the metric is enqueue/ack latency or durable completion; do not confuse them.
6. **Test repeatability.** For a comparative claim, start with at least five runs per side, interleaving A/B so load drift and warmup do not favor one. Report the per-side median, range, and any relevant request percentiles separately. Treat differences within observed variation as no measurable difference; use the harness's appropriate statistics for close calls rather than chasing a preferred result.
7. **Check user relevance.** Measure the end-to-end path with realistic data sizes and concurrency beside a microbenchmark. State the measured component's share of total time; a tiny component's improvement cannot justify an unsupported whole-system claim.

Keep these checks read-only or within an owned disposable benchmark environment. The measurement task does not authorize stopping someone else's workload, production load generation, configuration changes, or deployments. Preserve existing harness isolation and approval requirements.

## Report and stop

Lead with faster, slower, no measurable difference, or inconclusive. Give the primary metric and unit, before/after values, run count, spread, workload/configuration, limiter evidence, error counts, completed-work checks, and end-to-end result. Keep the raw runs with the claim in a named artifact.

Call a comparative claim inconclusive if it lacks a measured limiter, an adequately tuned side, correctness/completed-work evidence, or enough repetition to distinguish the gap from noise. Report the missing check rather than filling it with a guess. Stop once the stated claim is supported or its evidence gap is explicit; optimization is a separate task.

Adapted from pstack `benchmark-checklist` and `principle-explain-the-number` at the commit above. Copyright (c) 2026 Lauren Tan; see [LICENSE](LICENSE).
