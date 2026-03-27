# Jotform Fields Reference — HVAC Standard

## Form: Standard Onboarding (260795139953066)

### Section 1: Business Information
| QID | Name | Type | Required | Conditional |
|-----|------|------|----------|-------------|
| q4 | HVAC Company Name | textbox | Yes | - |
| q54 | Owner/Manager Name | textbox | No | - |
| q6 | Main Company Phone | phone | Yes | - |
| q5 | Client Email | email | Yes | - |
| q7 | Company Website | textbox | No | - |
| q8 | Years in Business | number | Yes | - |
| q34 | Timezone | dropdown | Yes | - |
| q13 | Services Offered | checkbox | No | - |
| q14 | Brands/Equipment Serviced | checkbox | No | - |
| q16 | Primary Service Area | textbox | Yes | - |
| q40 | Service Area Radius | dropdown | No | - |
| q29 | Certifications | checkbox | Yes | - |
| q28 | Licensed and Insured | dropdown | Yes | - |

### Section 2: AI Receptionist Configuration
| QID | Name | Type | Required | Conditional |
|-----|------|------|----------|-------------|
| q10 | AI Receptionist Name | textbox | Yes | - |
| q11 | AI Voice Gender | dropdown | Yes | - |
| q38 | Custom Greeting | textbox | No | - |
| q39 | Company Tagline | textbox | No | - |

### Section 3: Call Handling & Pricing
| QID | Name | Type | Required | Conditional |
|-----|------|------|----------|-------------|
| q17 | Business Hours | textbox | Yes | - |
| q18 | Typical Response Time | textbox | Yes | - |
| q20 | 24/7 Emergency Service | dropdown (Yes/No) | Yes | - |
| q21 | Emergency After-Hours Phone | phone | No | Show if q20=Yes |
| q22 | After-Hours Behavior | dropdown | No | Show if q20=Yes |
| q68 | After-Hours Transfer Behavior | dropdown | No | Show if q20=Yes |
| q42 | Pricing Policy | dropdown | No | - |
| q41 | Diagnostic Fee | textbox | No | - |
| q43 | Standard Fees | textarea | No | - |
| q24 | Free Estimates | dropdown | Yes | - |
| q25 | Financing Available | dropdown (Yes/No) | Yes | - |
| q44 | Financing Details | textbox | No | Show if q25=Yes |
| q26 | Warranties | dropdown (Yes/No) | Yes | - |
| q27 | Warranty Details | textbox | No | Show if q26=Yes |
| q45 | Payment Methods | checkbox | No | - |
| q46 | Maintenance Plans | dropdown | No | - |
| q58 | Membership Program Name | textbox | No | Show if q46 contains "Yes" |

### Section 4: Lead Capture & Notifications
| QID | Name | Type | Required | Conditional |
|-----|------|------|----------|-------------|
| q31 | Lead Contact Method | dropdown | Yes | - |
| q32 | Lead Notification Phone | phone | Yes | - |
| q33 | Lead Notification Email | email | Yes | - |
| q64 | Additional Notification SMS 2 | phone | No | - |
| q65 | Additional Notification SMS 3 | phone | No | - |
| q66 | Additional Notification Email 2 | email | No | - |
| q67 | Additional Notification Email 3 | email | No | - |
| q48 | Transfer Phone Number | phone | No | - |
| q49 | Transfer Triggers | checkbox | No | - |
| q50 | Transfer Behavior | dropdown | No | - |

### Section 5: Branding, Promotions & Extras
| QID | Name | Type | Required | Conditional |
|-----|------|------|----------|-------------|
| q55 | Google Review Rating | dropdown | No | - |
| q56 | Google Review Count | dropdown | No | - |
| q51 | Unique Selling Points | textarea | No | - |
| q52 | Current Promotion | textarea | No | - |
| q53 | Seasonal Services | textarea | No | - |
| q57 | Do Not Service List | textarea | No | - |
| q37 | Additional Info | textarea | No | - |

### Conditional Logic Rules
1. **Emergency fields** (q21, q22, q68) → only visible when q20 = "Yes"
2. **Warranty Details** (q27) → only visible when q26 = "Yes"
3. **Financing Details** (q44) → only visible when q25 = "Yes"
4. **Membership Name** (q58) → only visible when q46 contains "Yes"

### After-Hours Transfer Values (q68)
| Jotform Option | Stored Value | Behavior |
|----------------|-------------|----------|
| Transfer all calls 24/7 (default) | all | Transfers all calls regardless of time |
| Only transfer emergency calls after hours | emergency_only | Regular calls → take details, emergencies → transfer |
| Never transfer calls after hours | never | All calls → take details, no transfers |

### NOTE: Conditional Logic
Jotform conditional visibility needs to be configured in the Jotform UI (Form Builder → Settings → Conditions) for card-style forms. The API-set conditions may not render in card view. Set them manually:
- q20 = "Yes" → Show q21, q22, q68
- q26 = "Yes" → Show q27
- q25 = "Yes" → Show q44
- q46 contains "Yes" → Show q58
