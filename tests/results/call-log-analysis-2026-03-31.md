# Syntharra Call Log Analysis Report
**Generated:** 2026-03-31 04:40
**Calls analysed:** 9
**Calls with issues:** 8 (89%)
**Total issues found:** 10

## Severity Breakdown
- CRITICAL: 0
- HIGH: 8
- MEDIUM: 2
- LOW: 0

## Issues by Type (sorted by severity × frequency)

### [HIGH] call_failed — 5 occurrence(s)
- Call marked unsuccessful. Summary: The user called to cancel an appointment scheduled for later that day. The agent attempted to transfer the call to the appropriate department but was unable to do so due to technical limitations. The agent then offered to take the user's contact information for a callback, but the call ended before this was completed.
  Call: The user called to cancel an appointment scheduled for later that day. The agent attempted to transfer the call to the appropriate department but was 
- Call marked unsuccessful. Summary: The user called back after missing a call from Arctic Breeze HVAC. The agent asked for the user's name and contact number to have someone follow up, but the user did not provide the information before hanging up.
  Call: The user called back after missing a call from Arctic Breeze HVAC. The agent asked for the user's name and contact number to have someone follow up, b
- Call marked unsuccessful. Summary: The user called Arctic Breeze HVAC reporting an emergency with their AC not working and requested urgent service. The agent collected the user's name, address, and phone number but was unable to transfer the call to the service team. The agent apologized and assured the user that someone would call back as soon as possible.
  Call: The user called Arctic Breeze HVAC reporting an emergency with their AC not working and requested urgent service. The agent collected the user's name,
- ...and 2 more

### [HIGH] negative_sentiment — 3 occurrence(s)
- User sentiment: Negative
  Call: The user called Arctic Breeze HVAC reporting an emergency with their AC not working and requested urgent service. The agent collected the user's name,
- User sentiment: Negative
  Call: The user, Declan Joanna, called Arctic Breeze HVAC to report that their AC is not cooling at all. The agent collected the user's contact information a
- User sentiment: Negative
  Call: The user called Arctic Breeze HVAC because their heater stopped working and it was very cold. The agent attempted to transfer the call for urgent serv

### [MEDIUM] abnormal_disconnect — 2 occurrence(s)
- Disconnection reason: agent_hangup
  Call: The user called Arctic Breeze HVAC to inquire about the price for servicing their AC system. The agent collected the user's name, phone number, and se
- Disconnection reason: agent_hangup
  Call: The user called Arctic Breeze HVAC to inquire about AC installations and requested a quote. The agent collected the user's full name, phone number, an

## Call Quality Stats
- Average call duration: 1.6 minutes
- Sentiment distribution: {"Neutral": 3, "Positive": 2, "Negative": 3, "Unknown": 1}
- Successful calls: 4/9 (44%)
- Average tokens per turn: 4442