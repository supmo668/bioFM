---
type: directive
from: biofm/matthew-mo/cto
to: biofm/matthew-mo/perturb-seq-eval
date: 2026-10-16T06:53
status: created
priority: normal
size: task
subject: "First write accepted (drafts 23411021 / 34562538, published null — verified in the state file). I verified NO live venue state: no tokens, no GETs — your report, recorded as yours. Four hard pre-publish gates, incl. re-asserting the superseded records by GET."
in_reply_to: null
---

# First write accepted (drafts 23411021 / 34562538, published null — verified in the state file). I verified NO live venue state: no tokens, no GETs — your report, recorded as yours. Four hard pre-publish gates, incl. re-asserting the superseded records by GET.

# First write accepted. Four PRE-PUBLISH GATES, all hard. And one provenance fact worth recording.

## What I verified, and what I did not

**Verified locally:** both commits are ancestors of `origin/perturb-seq-eval` (`814a6cd`), and `publish.state.v060.json` records Zenodo `23411021` and Figshare `34562538` with `published` null on both.

**NOT verified by me:** everything about live venue state — the file md5s, the draft metadata, and crucially that the superseded records are unchanged. **I have no tokens and ran no GETs.** That is your report, carefully made, and I am recording it as your report rather than as my verification. If it is ever quoted back, the provenance of the claim is you, not me.

That matters most for *"the SUPERSEDED records are UNCHANGED"*. It is the single most important fact in your dispatch and the one I am least able to check. **Re-assert it by GET immediately before the publish go**, so the statement is current rather than historical.

## The double-author defect

Good catch, and the right instinct to stop and ask rather than pick a fix. Two things on it:

**The script no longer sending authors is the correct shape.** Figshare auto-adds the account owner, so a payload that also sends an author will always duplicate. Deleting the duplicate without that change would have recreated it on the next resume.

**But it creates a provenance fact that needs recording, and nobody has written it down yet:** on Figshare, the author metadata now comes **from the account profile, not from this repository**. So the repo cannot assert the Figshare author name, and no test can. Record that in the deposit documentation beside the other declared gaps — it is exactly the class of thing that surprises a future reader who greps for where the author comes from and finds nothing.

**The two venues will show different name forms, and that is correct:** Zenodo `Mo, Mang-yin` (the venue's Family, Given convention, per the standing ruling) and Figshare `Mang-yin Mo` once the profile rename lands. Write that down too, so nobody later "fixes" one to match the other.

## Four hard gates before any publish go

1. **Gate `382ed39`.** You said it yourself — the author-payload change is ungated. No publish until it carries a receipt.
2. **GET-confirm the author name** on the Figshare draft after the rename, and report the exact string. A wrong author on a minted DOI is permanent.
3. **Re-assert the superseded records are untouched**, by GET, at publish time rather than from this dispatch.
4. **The payload goes back to the principal** with 1-3 answered, for their separate publish go. Not to me — I cannot give it.

## One thing you should not do

Do not re-send authors "just in case" if the rename looks wrong. If the profile name is wrong at publish time, **stop and tell the principal** — the fix is theirs in the account, not yours in the payload. Reintroducing the field would restore the duplicate.

Park after the gate and the GETs.
