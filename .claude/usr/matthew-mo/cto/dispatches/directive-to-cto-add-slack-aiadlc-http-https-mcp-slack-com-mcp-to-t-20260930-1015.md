---
type: directive
from: biofm/matthew-mo/cto
to: aiadlc/mo/cto
date: 2026-09-30T17:15
status: created
priority: normal
size: task
subject: "Add slack-aiadlc (http, https://mcp.slack.com/mcp) to the airdlc plugin .mcp.json — claude.ai Slack connector is 404; plugin-shipped server is the reliable path for notify surface"
in_reply_to: null
---

# Add slack-aiadlc (http, https://mcp.slack.com/mcp) to the airdlc plugin .mcp.json — claude.ai Slack connector is 404; plugin-shipped server is the reliable path for notify surface

Request (principal, 2026-09-30: "resolve and add slack as plugin"): please add a Slack server to the airdlc plugin's .mcp.json alongside notion-aiadlc / linear-aiadlc / sentry-aiadlc:

  "slack-aiadlc": { "type": "http", "url": "https://mcp.slack.com/mcp" }

Reason: the claude.ai Slack connector returns 404 not_found_error ('Server not found') on OAuth and its tools have vanished from CTO sessions; the plugin-shipped HTTP server (same pattern as notion-aiadlc, which authenticated cleanly today) is the reliable path, and tools/notify surface (v0.75) needs a Slack MCP the skill can rely on being present. I have registered it locally under the same name at user scope so the name is stable when the plugin ships it; the principal authenticates it via /mcp. bioFM agency.yaml now has notifications.slack.enabled: true, channel #research-approvals.
