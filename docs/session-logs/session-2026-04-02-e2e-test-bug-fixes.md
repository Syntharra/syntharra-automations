# Session Log — 2026-04-02 — E2E Test & Bug Fixes

## Summary
Full end-to-end test of Standard pipeline from Jotform through to Retell agent provisioning.

## Test Results: 64/75 → All real bugs fixed (target 75/75 on next run)

## Bugs Found & Fixed

### BUG 1 — Notification fields not saved to Supabase
- Columns: notification_email_2, notification_email_3, notification_sms_2, notification_sms_3
- Root cause: n8n Parse JotForm Data node never mapped q64/q65/q66/q67 Jotform fields
- Fix: Added 4 field mappings to Parse JotForm Data node
- File: n8n workflow 4Hx7aRdzMl5N0uJP (HVAC AI Receptionist - JotForm Onboarding)

### BUG 2 — New client conversation flows missing callback + spam_robocall nodes (10 nodes, should be 12)
- Root cause: Build Retell Prompt node never included these nodes in the template
- Fix: Added node-callback + node-spam-robocall to the generated conversation flow
- Also added edges from identify_call to both new nodes
- New client flows: 12 nodes ✅

### BUG 3 (test script) — E2E assertion wrong: expected 13 nodes (none exist with 13)
- Fix: Updated assertion to 12 nodes
- Also fixed: agent_name assertion (expected company name, should be AI name)

## Architecture Clarification — Conversation Flows
| Node count | Flow type | Notes |
|---|---|---|
| 18 nodes | Premium (booking/calendar) | booking, availability, reschedule, cancel |
| 14 nodes | Arctic Breeze live | standard + emergency_fallback + spanish_routing |
| 12 nodes | New Standard clients ✅ | correct target |
| 10 nodes | Old/broken new clients | missing callback + spam |

## Files Changed
- n8n workflow 4Hx7aRdzMl5N0uJP — Parse JotForm Data + Build Retell Prompt nodes
- shared/e2e-test.py — node assertion 13→12, agent_name assertion fixed
- retell-agents/hvac-standard-MASTER-TEMPLATE.json — NEW master template reference
- docs/context/AGENTS.md — confirmed 12-node count
- docs/TASKS.md — updated
