# Failed Patterns

## logical_counter_only

Symptom:
Hit/miss/eviction counters improve, often dramatically.

Rejection:
`mib_per_token`, `decode_core_upload_mib`, `decode_req_mat_writes`, and total
service do not move consistently.

Harness rule:
Do not accept transfer/residency patches on logical counters alone.

## latency_shift

Symptom:
`decode_req_page_touch_ms` drops.

Rejection:
`decode_req_mat_enqueue_ms` or finish/wait time absorbs the cost, so total
service and primary throughput do not improve.

Harness rule:
For service patches, require total service and primary metric support.

## scheduling_only

Symptom:
Async submit/complete, prewarm, or queue counters move.

Rejection:
Physical upload volume is unchanged. This may still be a scheduling win, but it
must not be reported as transfer elimination.

Harness rule:
Classify scheduling improvements separately from transfer/residency wins.

## inactive_control_surface

Symptom:
A plausible default, flag, helper, or branch is changed.

Rejection:
Diagnostics show the path was already inactive or not used by the fixed
benchmark.

Harness rule:
The bounded task must name the active read/write/action sites before patching.
