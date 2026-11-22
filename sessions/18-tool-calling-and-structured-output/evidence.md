# Evidence — session 18

- Both application versions exercised the six tools through an authenticated
  loopback API and a ticketing mock seeded with 60 tickets. The Mac VPN search
  returned `KB-1017`. The employee profile, assigned devices, and regional
  printing incident agreed with the directory seed.
- A valid draft with a foreign asset returned `403`. An invalid category
  returned `422`, a missing idempotency key returned `400`, and an employee
  update returned `403`. The allowed create replayed the same ticket, and an
  analyst changed that ticket to `Awaiting User`.
- The inherited Session 17 password-reset request created its own ticket.
- GPT-6 Luna selected all 10 expected tools and returned 20 valid drafts on the
  first attempt. The run recorded 30 provider requests and an upper cost
  estimate of `$0.002270750`, using the cache-write rate for all input tokens.
- The unit fixture verified one successful repair, escalation after a second
  invalid draft, and escalation after a provider refusal.
- The completion gate records both HTTP checks and the live model report in
  `verification/runtime-gate.json`.
