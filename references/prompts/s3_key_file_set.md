# S3 Key-File-Set Prompt

Use S2 instructions, but start from a supplied candidate key-file set. The agent must still choose which file to edit and justify the choice.

Before editing:

- map each candidate file to the runtime behavior it controls
- identify the most likely policy bottleneck
- state the expected metric movement
- choose one file or tightly coupled file group for one coherent change

After benchmarking:

- decide whether the file localization was correct
- record needed expert knowledge if the code mapping was wrong or incomplete
- archive wrong-file or no-signal attempts instead of silently dropping them
