# Syntharra Subagent Component Library
> Generated: 2026-04-05 | Components: 19

| Component | ID | Content (chars) |
|---|---|---|
| Syntharra - booking_capture | `conversation_flow_component_ca04bba21560` | 4875 |
| Syntharra - call_style_detector | `conversation_flow_component_ff58734c21bb` | 3048 |
| Syntharra - callback | `conversation_flow_component_ab7909b654e2` | 679 |
| Syntharra - cancel_appointment | `conversation_flow_component_eb20b4cd1d8d` | 734 |
| Syntharra - check_availability | `conversation_flow_component_dfe7bd5017e5` | 918 |
| Syntharra - confirm_booking | `conversation_flow_component_20ac85a7954c` | 1021 |
| Syntharra - emergency_detection | `conversation_flow_component_24d9b49e1a30` | 330 |
| Syntharra - emergency_fallback | `conversation_flow_component_9d3c5c904347` | 916 |
| Syntharra - ending | `conversation_flow_component_801ba4098915` | 267 |
| Syntharra - existing_customer | `conversation_flow_component_d8eff9881e16` | 1126 |
| Syntharra - fallback_leadcapture | `conversation_flow_component_e6879f7849ab` | 1994 |
| Syntharra - general_questions | `conversation_flow_component_d46848148d1d` | 1602 |
| Syntharra - identify_call | `conversation_flow_component_ebac0db129f3` | 2223 |
| Syntharra - reschedule | `conversation_flow_component_4b3d107fd73a` | 1034 |
| Syntharra - spam_robocall | `conversation_flow_component_d23e204deb4f` | 66 |
| Syntharra - spanish_routing | `conversation_flow_component_731ee109f18a` | 611 |
| Syntharra - transfer_failed | `conversation_flow_component_183320e7b210` | 392 |
| Syntharra - validate_phone | `conversation_flow_component_3b788e86e755` | 426 |
| Syntharra - verify_emergency | `conversation_flow_component_174275fc7751` | 1351 |

## Usage
Components are shared across HVAC Standard and Premium agents.
Update a component → all agents using it inherit the change.

## Tier 1 (All Agents)
`identify_call`, `call_style_detector`, `verify_emergency`, `emergency_fallback`, `emergency_detection`, `callback`, `existing_customer`, `general_questions`, `spam_robocall`, `transfer_failed`, `spanish_routing`, `ending`, `validate_phone`, `fallback_leadcapture`

## Tier 2 (Premium Booking Only)
`booking_capture`, `check_availability`, `confirm_booking`, `reschedule`, `cancel_appointment`
