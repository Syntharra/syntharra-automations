#!/usr/bin/env python3
"""
Hook: PreToolUse → bash
Blocks any bash command that attempts to write to a MASTER Retell agent.
Reads stdin JSON: {"tool_name": "bash", "tool_input": {"command": "..."}}
Exit 2 = block the tool call and show message.
Exit 0 = allow.
"""
import sys, json

MASTER_AGENTS = {
    "agent_4afbfdb3fcb1ba9569353af28d": "HVAC Standard MASTER",
    "agent_9822f440f5c3a13bc4d283ea90": "HVAC Premium MASTER",
    "agent_b9d169e5290c609a8734e0bb45": "Demo Male MASTER",
    "agent_2723c07c83f65c71afd06e1d50": "Demo Female MASTER",
}

WRITE_SIGNALS = [
    "update-agent", "PATCH", "patch",
    "/update-conversation-flow", "/create-conversation-flow",
    "requests.patch", "requests.put", "requests.post",
]

try:
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")

    for agent_id, label in MASTER_AGENTS.items():
        if agent_id in command:
            for signal in WRITE_SIGNALS:
                if signal in command:
                    print(f"\n🚫 HOOK BLOCKED: Attempted write to {label} ({agent_id})")
                    print("   MASTER agents are read-only. Use TESTING agents only:")
                    print("   Standard TESTING: agent_731f6f4d59b749a0aa11c26929")
                    print("   Premium TESTING:  agent_2cffe3d86d7e1990d08bea068f")
                    sys.exit(2)
except Exception as e:
    # Never block on hook error — fail open
    sys.exit(0)

sys.exit(0)
