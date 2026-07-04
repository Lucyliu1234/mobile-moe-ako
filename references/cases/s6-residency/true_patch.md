# Useful Patch Mechanism

The original useful S6 patch targeted a state-relation issue rather than a raw
counter issue.

Mechanism:

```text
physical packed payload upload
    covers multiple logical projection accesses
        but runtime residency state may record only the triggering projection
            later sibling projection access can miss logically
                and may cause repeated service or misleading miss/churn signals
```

Harness lesson:

The agent must prove which logical state controls the physical skip. A patch
that only changes logical hit/miss accounting is insufficient unless physical
bytes, write count, or total service move consistently.

Generalized control rule:

```text
For repeated-work bottlenecks, first map:
logical request -> physical action -> coverage -> lifetime -> invalidation -> skip decision.
Then patch the state read/write that controls the physical action.
```
