# Slack summary — aviary-biosim completion walkthrough (drafted 2026-09-28; superseded by the five surface messages sent 2026-09-30, see 2026-09-30-slack-hacp-surface.md)

*aviary-biosim — where the workstream ends* (CTO, 2026-09-28)

*What was delivered.* A build loop whose worker cannot grade its own work (an independent test, re-run by a small tool with no model inside, is the only thing that can close a task), and `BioSimEnv`, an aviary environment that runs ESM-2 over real sequences under a budget the agent cannot forge.

*State.*
• Branch `aviary-biosim` @ `ab8f6f5`: gated, receipt `4217902` CTO-verified, 445 tests green (328 science / 42 register / 75 sealed), 48/48 live mutants killed + 1 retired. *Waiting on the principal's land* (`/airdlc:pr-cto-land aviary-biosim --no-release`).
• Branch `whitepaper` @ `b366667`: plan #272 signed r2 (`4a8bb59`); Tasks 0–12 done; Task 13 boundary gate owed by the agent, then the CTO's claims review, then the deposit.

*HACP breakdown* (six sections at `ab8f6f5`): §vision current (2 docs) · §design current, 1 correction · §build 2 in flight · §eval last gate green 2026-09-26 · §risk 6 open, one shape (a mechanism looked right while its property was absent) · §decision 4 open.

*Decisions waiting.* Run the land · lessons-pin fix (A/B/C) · second pass, before or after the paper · token price · keep or withdraw R5 · F31 hold through publication.

*Not claimed.* Known-constraint recovery, not new biology; no wet experiment; attribution, not reproduction; self-improvement unmeasured.

Full walkthrough + one-screen product cut: https://app.notion.com/p/3eb749bd250d810abd55ffd606eae42b (HACP index row, §build). Result review for perturb-seq-eval v0.6.0: https://app.notion.com/p/3eb749bd250d8112a6aeca8ae015149c (§eval).
