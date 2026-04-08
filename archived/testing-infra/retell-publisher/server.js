const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;
const RETELL_EMAIL = process.env.RETELL_EMAIL;
const RETELL_PASSWORD = process.env.RETELL_PASSWORD;
const API_SECRET = process.env.API_SECRET; // simple auth token

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.post('/publish-agent', async (req, res) => {
  // Auth check
  const authHeader = req.headers.authorization;
  if (!authHeader || authHeader !== `Bearer ${API_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const { agent_id } = req.body;
  if (!agent_id) return res.status(400).json({ error: 'agent_id required' });

  let browser;
  try {
    console.log(`Publishing agent: ${agent_id}`);

    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // Go to Retell login
    await page.goto('https://app.retellai.com', { waitUntil: 'networkidle2', timeout: 30000 });

    // Wait for login form
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });

    // Fill login
    await page.type('input[type="email"]', RETELL_EMAIL);
    await page.type('input[type="password"]', RETELL_PASSWORD);
    await page.keyboard.press('Enter');

    // Wait for dashboard
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
    console.log('Logged in, navigating to agent...');

    // Navigate directly to agent
    await page.goto(`https://app.retellai.com/agents/${agent_id}`, { 
      waitUntil: 'networkidle2', timeout: 30000 
    });

    // Wait for Publish button
    await page.waitForSelector('button:has-text("Publish"), button[data-testid="publish-btn"]', { 
      timeout: 15000 
    }).catch(() => null);

    // Find and click publish button
    const published = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const publishBtn = buttons.find(b => b.textContent.trim() === 'Publish');
      if (publishBtn && !publishBtn.disabled) {
        publishBtn.click();
        return true;
      }
      return false;
    });

    if (!published) {
      // Try alternate selector
      const btn = await page.$('button.publish-button, [data-action="publish"]');
      if (btn) {
        await btn.click();
      }
    }

    // Wait a moment for publish to complete
    await new Promise(r => setTimeout(r, 3000));

    console.log(`Agent ${agent_id} published successfully`);
    res.json({ success: true, agent_id, message: 'Agent published' });

  } catch (err) {
    console.error('Publish error:', err.message);
    res.status(500).json({ error: err.message });
  } finally {
    if (browser) await browser.close();
  }
});

app.listen(PORT, () => console.log(`Retell Publisher running on port ${PORT}`));
