"""OpenRouter backend — thin HTTP client for chat completions.

Usage:
    backend = OpenRouterBackend.from_env()   # reads .env / process env
    text = backend.complete(system="...", user="...", max_tokens=32)

The backend is deliberately stdlib-only (``urllib``) so the project keeps its
small dependency surface. Retry-with-backoff handles transient 429/503s.

Configuration is entirely via environment variables — load ``.env`` at
process start (``python-dotenv``) or export the variables manually.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class OpenRouterError(RuntimeError):
    pass


@dataclass
class OpenRouterBackend:
    """Minimal OpenRouter chat-completions client."""

    api_key: str
    model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    base_url: str = "https://openrouter.ai/api/v1"
    referer: str = "https://example.invalid"
    app_title: str = "perturb-seq-eval"
    timeout_seconds: float = 30.0
    max_retries: int = 3
    backoff_initial: float = 1.0

    # Let tests inject a fake transport without monkey-patching urllib.
    transport: Any = None  # set to a callable(req)->dict to stub

    # ---- constructors --------------------------------------------------
    @classmethod
    def from_env(cls) -> "OpenRouterBackend":
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not set — copy .env.example to .env "
                "and fill in your key, or export it in the shell."
            )
        return cls(
            api_key=key,
            model=os.environ.get("OPENROUTER_MODEL", cls.model),
            base_url=os.environ.get("OPENROUTER_BASE_URL", cls.base_url),
            referer=os.environ.get("OPENROUTER_REFERER", cls.referer),
            app_title=os.environ.get("OPENROUTER_APP_TITLE", cls.app_title),
        )

    # ---- public API ----------------------------------------------------
    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 64,
        temperature: float = 0.0,
    ) -> str:
        """Run one chat-completion turn and return the assistant string."""
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if self.transport is not None:
            resp = self.transport(body)
        else:
            resp = self._post("/chat/completions", body)

        try:
            return resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise OpenRouterError(f"unexpected response shape: {resp}") from e

    # ---- low-level transport ------------------------------------------
    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + path
        data = json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.referer,
            "X-Title": self.app_title,
        }
        req = urllib.request.Request(url, data=data, method="POST", headers=headers)

        backoff = self.backoff_initial
        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as r:
                    raw = r.read()
                return json.loads(raw.decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in {429, 500, 502, 503, 504} and attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    last_err = e
                    continue
                # Try to surface the server's error body
                try:
                    payload = json.loads(e.read().decode("utf-8"))
                except Exception:
                    payload = {"error": str(e)}
                raise OpenRouterError(
                    f"HTTP {e.code} from OpenRouter: {payload}"
                ) from e
            except urllib.error.URLError as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise OpenRouterError(f"network error: {e}") from e
        raise OpenRouterError(f"retries exhausted: {last_err}")


def make_severity_rater(backend: OpenRouterBackend, prompt_template: str):
    """Return a callable ``rater(prompt_text) -> float`` suitable for
    ``massgen_skill_draft.extractors.severity.project_severity``.

    The prompt_template is the severity rater prompt; we split it into system
    and user sections by the '## User' marker.
    """
    parts = prompt_template.split("## User", 1)
    system = parts[0].replace("## System", "").strip()
    user_tmpl = parts[1].strip() if len(parts) == 2 else "{reason_text}"

    def _rate(rendered_prompt: str) -> float:
        # The template parameter has already been formatted upstream, so we
        # pass it straight through as the user turn.
        out = backend.complete(system=system, user=rendered_prompt, max_tokens=8)
        # Pull the first float-parseable token.
        for tok in out.replace(",", " ").split():
            try:
                v = float(tok)
                return max(0.0, min(1.0, v))
            except ValueError:
                continue
        return 0.2  # safe fallback

    # Avoid unused-var warning on user_tmpl; we keep it for documentation.
    _ = user_tmpl
    return _rate
