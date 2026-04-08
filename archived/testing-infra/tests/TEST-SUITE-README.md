# Syntharra Agent Test Suite

**Total scenarios: 95**

Use these with Retell's AI Simulated Chat batch testing.
Each scenario includes a user persona prompt and evaluation metrics.

## Coverage

### Core Flow Paths (15 scenarios)
Tests every node in the conversation flow is reachable and handles correctly.

1. 1. Standard AC repair request - cooperative caller
2. 2. Heating repair request
3. 3. New AC installation inquiry
4. 4. Maintenance tune-up request
5. 5. Duct cleaning request
6. 6. Emergency - complete AC failure in extreme heat
7. 7. Emergency - gas smell
8. 8. Emergency - carbon monoxide detector alarm
9. 9. Returning a missed call
10. 10. Existing customer - appointment status
11. 11. Existing customer - invoice dispute
12. 12. General question - service area
13. 13. Spam robocall
14. 14. Caller wants to speak to a real person
15. 15. Transfer fails - agent handles gracefully

### Service Variations (10 scenarios)
Different HVAC problems and service types.

16. 16. AC making strange noise
17. 17. AC leaking water inside house
18. 18. Thermostat not working
19. 19. Heat pump not heating in winter
20. 20. Pilot light keeps going out
21. 21. AC running but not cooling - tenant calling for landlord
22. 22. Multiple issues in one call
23. 23. Pre-purchase home inspection HVAC check
24. 24. Seasonal service - fall heating check-up
25. 25. Warranty question on previous work

### Caller Personalities (15 scenarios)
Same scenarios with wildly different caller behaviours.

26. 26. Elderly caller - slow and hard of hearing
27. 27. Extremely impatient caller
28. 28. Suspicious caller - reluctant to share info
29. 29. Chatty caller who goes off topic
30. 30. Caller who doesn't know HVAC terminology
31. 31. Caller who gives one-word answers
32. 32. Caller who overshares medical information
33. 33. Caller who frequently changes their mind
34. 34. Angry caller threatening bad review
35. 35. Caller threatening legal action
36. 36. Caller who interrupts constantly
37. 37. Non-native English speaker
38. 38. Caller on speaker phone with background noise
39. 39. Two people talking - caller with spouse
40. 40. Very polite but asks many questions before committing

### Information Collection (15 scenarios)
Edge cases in name, phone, address, email collection.

41. 41. Hyphenated last name
42. 42. Caller only gives first name repeatedly
43. 43. Phone number given too fast
44. 44. Wrong phone number - caller corrects
45. 45. Complex email address
46. 46. PO Box instead of service address
47. 47. Rural route address
48. 48. Caller refuses to give address
49. 49. Apartment with complex unit number
50. 50. Caller gives city but no street address
51. 51. Caller spells name wrong then corrects
52. 52. Caller has two phone numbers - which to use?
53. 53. Very long street name
54. 54. Caller provides info before being asked
55. 55. Caller gives email with unusual domain

### Edge Cases & Anomalies (25 scenarios)
Unusual situations, third-party callers, wrong numbers, mid-flow changes.

56. 56. Caller asks question mid-information-collection
57. 57. Caller changes what service they need mid-call
58. 58. Caller asks about a service we don't provide mid-flow
59. 59. Caller is calling for someone else
60. 60. Caller dialled the wrong number
61. 61. Caller asks if the agent is AI/robot
62. 62. Caller asks to be called back at specific time
63. 63. Caller explicitly asks for same-day service
64. 64. Repeat caller - already called earlier today
65. 65. Contractor/vendor calling - not a customer
66. 66. Caller mentions insurance claim
67. 67. Caller asks about commercial service
68. 68. Caller asks for a specific technician by name
69. 69. Caller wants to cancel an existing appointment
70. 70. Caller wants to reschedule
71. 71. Caller asks about financing in detail
72. 72. Caller compares with a competitor's quote
73. 73. Caller asks about senior discount
74. 74. Caller asks 'are you open right now?' after hours
75. 75. Caller on a Sunday
76. 76. Caller mentions current promotion unprompted
77. 77. Caller asks about COVID/health protocols
78. 78. Caller is a real estate agent with multiple properties
79. 79. Caller puts agent on hold
80. 80. Caller asks the agent to repeat everything at the end

### Pricing Traps (8 scenarios)
Every angle a caller might use to extract pricing.

81. 81. 'Just give me a ballpark'
82. 82. 'What do most people pay?'
83. 83. 'Is the diagnostic fee refundable?'
84. 84. 'Can you match the other company's price?'
85. 85. 'What's your hourly rate?'
86. 86. Asks about cancellation fee
87. 87. Tries to negotiate the diagnostic fee
88. 88. Asks about payment plans for repair (not installation)

### Boundary & Safety (7 scenarios)
Abuse, minors, privacy, DIY requests, diagnosis requests.

89. 89. Caller asks agent to diagnose the problem
90. 90. Caller asks for DIY advice
91. 91. Caller uses profanity
92. 92. Caller directs abuse at the agent personally
93. 93. Caller mentions BBB complaint
94. 94. Caller asks about data privacy
95. 95. Minor/child calling

## Usage

1. Go to Retell Dashboard → Agent → Test tab → AI Simulated Chat
2. Create a new test case
3. Paste the `user_prompt` from the scenario
4. Run the simulation
5. Add the `metrics` as evaluation criteria
6. Save and add to batch
7. Use Batch Test to run all scenarios at once
