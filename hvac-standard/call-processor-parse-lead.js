// HVAC Standard — Parse Lead Data node
// Synced from n8n workflow OyDCyiOjG0twguXq

const gptResponse = $input.first().json;
const clientData = $('Parse Client Data').first().json;

let leadData = {};
try {
  const text = gptResponse.message?.content || gptResponse.text || JSON.stringify(gptResponse);
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  leadData = jsonMatch ? JSON.parse(jsonMatch[0]) : {};
} catch (e) {
  leadData = { lead_score: 0, summary: 'Failed to parse GPT response', is_hot_lead: false };
}

return {
  ...clientData,
  ...leadData,
  lead_score: leadData.lead_score || 0,
  is_lead: (leadData.lead_score || 0) >= 6
};