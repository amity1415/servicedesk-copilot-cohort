# Evidence — session 19

- The standalone and integrated APIs diagnosed “My laptop is slow” for the
  synthetic employee `E1166`. Three typed reads found Windows laptop
  `LH-L-00166`, active SecureTunnel incident `1` in APAC, and article `KB-1054`.
  The earlier authenticated Session 18 asset route also passed.
- A repeated asset decision escalated at the two-step limit after two reads.
  The seeded ticket count stayed at 60. Unit checks also verified an invalid
  decision, a disallowed ticket action, and an elapsed deadline before dispatch.
- GPT-6 Luna completed the same diagnostic trajectory in four calls, including
  the final troubleshooting answer. Estimated cost was `$0.000301125` using
  the cache-write price as an upper estimate for input tokens.
- `verification/runtime-gate.json` records the local and live trajectories,
  provider usage, and the completion check results.
