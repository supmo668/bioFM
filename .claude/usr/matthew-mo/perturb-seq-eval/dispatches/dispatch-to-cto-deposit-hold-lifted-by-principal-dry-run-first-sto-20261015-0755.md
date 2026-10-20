---
type: dispatch
from: biofm/matthew-mo/perturb-seq-eval
to: biofm/matthew-mo/cto
date: 2026-10-15T06:55
status: created
priority: normal
size: task
subject: "Deposit hold LIFTED by principal (dry-run first, stop before publish); step 1 built; blocked on env + tokens"
in_reply_to: null
---

# Deposit hold LIFTED by principal (dry-run first, stop before publish); step 1 built; blocked on env + tokens

Principal lifted the deposit hold in my session (b6e15309), 2026-10-14. They typed "go"; I asked them to confirm, and they chose "Yes: deposit, dry-run first". My understanding of that choice: build, prepare both venues, run the Zenodo and Figshare --dry-run, then STOP and show the payloads before any real publish. Nothing is published without a second go.

Fresh worktree perturb-seq-eval from origin/main 357944b; nothing opened from the old branch.

Step 1 DONE (local only; nothing uploaded):
- build_deposit.py ran against the clean tree at 357944b.
- paper.pdf rebuilt with tectonic: 0 overfull, 0 undefined.
- v060_run_artifacts staged: 5 files, SHA256SUMS all OK, BUILD_INFO pins 357944b.

BLOCKED before steps 2-3 and the dry runs. I'm asking the principal about two things:
(1) The submitter needs requests and pyyaml. No venv exists in the fresh worktree, and making one installs packages, which my standing rule forbids.
(2) ZENODO_TOKEN and FIGSHARE_TOKEN come from Infisical. I need the principal to run the command, or to tell me the infisical run invocation. I never see the token values.

Steps 2-3 are draft-only API changes (Zenodo newversion from 20060974; Figshare metadata update + deletion of the v0.5 files in the article draft). They come before the dry runs and need the same token. PublishedRecordError stays the guard.
next_handoff: principal answers on env + tokens; dry-run payloads back to the principal
