// ============================================================
// Syntharra Premium — Integration Dispatcher
// ============================================================
// 
// This n8n workflow receives custom function calls from Retell 
// conversation flow agents during live calls. It routes to the 
// correct calendar/CRM platform based on the client's config.
//
// WEBHOOK: POST /webhook/retell-integration-dispatch
//
// Retell sends:
// {
//   "call": { "agent_id": "...", "call_id": "...", ... },
//   "args": { "date": "2026-04-01", "time_window": "morning", ... }
// }
//
// Plus the function name comes from which custom function node 
// triggered this — we differentiate by the args or by using 
// separate webhook paths per function.
//
// ARCHITECTURE:
//   Webhook → Look up client → Route by platform → Call API → Return result
//
// PLATFORMS SUPPORTED:
//   Calendars: Google Calendar, Calendly, Cal.com, Outlook, Jobber, HCP, ServiceTitan
//   CRMs: Jobber, HCP, ServiceTitan, GoHighLevel, HubSpot
//
// FUNCTIONS:
//   check_availability → checks calendar for open slots
//   create_booking → creates appointment in calendar + contact in CRM
//   reschedule_booking → updates existing appointment
//   cancel_booking → removes appointment
//
// ============================================================

// This file documents the workflow design. The actual n8n workflow
// is built via the n8n API and deployed programmatically.

const WORKFLOW_DESIGN = {
  name: "Premium Integration Dispatcher",
  webhook_path: "/webhook/retell-integration-dispatch",
  
  nodes: [
    // 1. WEBHOOK TRIGGER
    // Receives POST from Retell custom function during live call
    // Must respond within 2 minutes (Retell timeout)
    {
      name: "Retell Function Webhook",
      type: "webhook",
      method: "POST",
      path: "retell-integration-dispatch",
      response_mode: "responseNode" // We need to return data to Retell
    },
    
    // 2. EXTRACT FUNCTION DATA
    // Parse the Retell payload to get agent_id, call_id, function args
    {
      name: "Extract Function Data",
      type: "code",
      logic: `
        const body = $input.first().json.body;
        const agentId = body.call?.agent_id || '';
        const callId = body.call?.call_id || '';
        const args = body.args || {};
        
        // Determine which function was called based on args or webhook path
        let functionName = 'unknown';
        if (args.action) {
          functionName = args.action; // check_availability, create_booking, etc
        } else if (args.date && !args.booking_id) {
          functionName = 'check_availability';
        } else if (args.booking_id && args.new_date) {
          functionName = 'reschedule_booking';
        } else if (args.booking_id && args.cancel) {
          functionName = 'cancel_booking';
        } else if (args.date && args.caller_name) {
          functionName = 'create_booking';
        }
        
        return {
          agent_id: agentId,
          call_id: callId,
          function_name: functionName,
          args: args
        };
      `
    },
    
    // 3. LOOK UP CLIENT
    // Get the client's calendar_platform, crm_platform, and credentials from Supabase
    {
      name: "Look Up Client",
      type: "httpRequest",
      method: "GET",
      url: "https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/hvac_premium_agent",
      query: "agent_id=eq.{{ $json.agent_id }}&select=*",
      // Returns: calendar_platform, crm_platform, calendar_access_token, crm_access_token, etc
    },
    
    // 4. ROUTE BY FUNCTION
    // Switch node that routes to the correct handler
    {
      name: "Route by Function",
      type: "switch",
      routes: [
        { value: "check_availability", output: 0 },
        { value: "create_booking", output: 1 },
        { value: "reschedule_booking", output: 2 },
        { value: "cancel_booking", output: 3 }
      ]
    },
    
    // 5a. CHECK AVAILABILITY HANDLER
    // Routes to correct calendar platform
    {
      name: "Check Availability",
      type: "code",
      logic: `
        const client = $input.first().json;
        const platform = client.calendar_platform || '';
        const args = client.args || {};
        
        // Normalize date and time
        const date = args.date; // YYYY-MM-DD
        const timeWindow = args.time_window || 'morning'; // morning or afternoon
        const duration = client.default_appointment_duration || 60;
        
        // Calculate time range
        let startHour, endHour;
        if (timeWindow === 'morning') { startHour = 8; endHour = 12; }
        else { startHour = 12; endHour = 17; }
        
        // Build platform-specific request
        switch (platform) {
          case 'Google Calendar':
            // Google Calendar API: list events in time range
            return {
              platform: 'google_calendar',
              api_url: 'https://www.googleapis.com/calendar/v3/calendars/primary/events',
              params: {
                timeMin: date + 'T' + String(startHour).padStart(2,'0') + ':00:00Z',
                timeMax: date + 'T' + String(endHour).padStart(2,'0') + ':00:00Z',
                singleEvents: true,
                orderBy: 'startTime'
              },
              access_token: client.calendar_access_token,
              date, timeWindow, duration
            };
            
          case 'Calendly':
            return {
              platform: 'calendly',
              // Calendly API: check event type availability
              date, timeWindow, duration,
              access_token: client.calendar_access_token
            };
            
          case 'Jobber Calendar':
          case 'Jobber':
            return {
              platform: 'jobber',
              date, timeWindow, duration,
              api_key: client.crm_api_key || client.calendar_api_key
            };
            
          default:
            // No calendar connected — always say available (fallback)
            return {
              platform: 'none',
              result: { available: true, message: 'Slot is available' },
              date, timeWindow
            };
        }
      `
    },
    
    // 5b. CREATE BOOKING HANDLER
    {
      name: "Create Booking",
      type: "code",
      logic: `
        // Creates appointment in calendar AND contact in CRM
        // Returns confirmation to Retell agent
      `
    },
    
    // 5c. RESCHEDULE HANDLER
    {
      name: "Reschedule Booking",
      type: "code"
    },
    
    // 5d. CANCEL HANDLER
    {
      name: "Cancel Booking",
      type: "code"
    },
    
    // 6. PLATFORM API CALLS
    // Sub-workflows or httpRequest nodes for each platform
    // Google Calendar, Calendly, Jobber, HCP, ServiceTitan, etc.
    
    // 7. FORMAT RESPONSE
    // Formats the result into a string that Retell can use
    {
      name: "Format Response",
      type: "code",
      logic: `
        const result = $input.first().json;
        
        if (result.available) {
          return { result: 'The ' + result.timeWindow + ' slot on ' + result.date + ' is available.' };
        } else {
          return { result: 'That slot is taken. The next available slots are: ' + result.alternatives.join(', ') };
        }
      `
    },
    
    // 8. RESPOND TO RETELL
    // Returns the result to the Retell agent
    {
      name: "Respond to Webhook",
      type: "respondToWebhook",
      response: "{{ $json.result }}"
    }
  ]
};

module.exports = WORKFLOW_DESIGN;
