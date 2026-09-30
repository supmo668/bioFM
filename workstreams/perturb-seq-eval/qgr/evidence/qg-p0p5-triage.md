# Triage (disposition + rationale)
ACCEPT-FIX-NOW (implementation; does not change the measurand): C4, C5, C6(key+cache_hit), C9, C10, C11(text), C12, C14, C15, C16, C17, C18, C22, C23, C24, C27, OWN-1.
ACCEPT-FIX-AFTER-RULING (changes what the pre-registered experiment measures -> principal ruling + pre-registration amendment 2 BEFORE the sweep): C1, C2, C3, C7, C8, C13, C25, NEW-1, C6(prompt/cache-start), C20(wording).
REJECT (below threshold 80): C19 (bundle; its two confirmed items folded into C17/C18 fixes), C21 (unreachable: probe refuses a malformed key first — kept as hardening note), C26 (no duplicates in Adamson; unverified Norman — logged).
No finding deferred past this gate: the sweep cannot run until all ACCEPT items are fixed and re-reviewed.
