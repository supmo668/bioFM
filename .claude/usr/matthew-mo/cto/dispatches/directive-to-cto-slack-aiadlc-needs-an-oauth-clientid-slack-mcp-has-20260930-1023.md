---
type: directive
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-09-30T17:23
status: created
priority: normal
size: task
subject: "slack-aiadlc needs an oauth.clientId — Slack MCP has no dynamic client registration (plugin .mcp.json shape attached)"
in_reply_to: null
---

# slack-aiadlc needs an oauth.clientId — Slack MCP has no dynamic client registration (plugin .mcp.json shape attached)

Follow-up to the slack-aiadlc request: a bare {type: http, url: https://mcp.slack.com/mcp} entry FAILS — 'Incompatible auth server: does not support dynamic client registration'. Slack's MCP needs a pre-registered OAuth client, the same shape the official engineering plugin ships:

  "slack-aiadlc": { "type": "http", "url": "https://mcp.slack.com/mcp", "oauth": { "clientId": "<Slack app client id>", "callbackPort": 3118 } }

The clientId is a public OAuth identifier (not a secret); the official engineering plugin's .mcp.json carries one you can reuse, or register an airdlc Slack app. tools/notify surface (0.77.0) works standalone and produced the five payloads in bioFM workstreams/_adhoc/2026-09-30-slack-hacp-surface.md — the send half still needs the MCP.
