const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        LevelFormat, PageBreak } = require("docx");

const accent = "6C63FF";
const accentDark = "4F46E5";
const gray = "6B7280";
const lightPurple = "F3F0FF";
const darkText = "111827";

const border = { style: BorderStyle.SINGLE, size: 1, color: "E5E7EB" };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const cellMargins = { top: 100, bottom: 100, left: 140, right: 140 };

const spacer = (pts = 200) => new Paragraph({ spacing: { before: pts } });

const heading = (text, level = HeadingLevel.HEADING_1) =>
  new Paragraph({ heading: level, children: [new TextRun({ text, font: "Georgia", bold: true, color: darkText })] });

const body = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: 120, line: 276 },
    children: [new TextRun({ text, font: "Calibri", size: 22, color: opts.color || "374151", ...opts })]
  });

const boldBody = (label, value) =>
  new Paragraph({
    spacing: { after: 80 },
    children: [
      new TextRun({ text: label, font: "Calibri", size: 22, bold: true, color: darkText }),
      new TextRun({ text: value, font: "Calibri", size: 22, color: "374151" })
    ]
  });

const featureRow = (icon, title, desc) =>
  new TableRow({
    children: [
      new TableCell({
        borders: noBorders, width: { size: 600, type: WidthType.DXA }, margins: cellMargins,
        verticalAlign: "center",
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: icon, font: "Calibri", size: 28 })] })]
      }),
      new TableCell({
        borders: noBorders, width: { size: 8760, type: WidthType.DXA }, margins: cellMargins,
        children: [
          new Paragraph({ children: [new TextRun({ text: title, font: "Calibri", size: 22, bold: true, color: darkText })] }),
          new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: desc, font: "Calibri", size: 20, color: gray })] })
        ]
      })
    ]
  });

const pricingCell = (plan, price, annual, setup, minutes, features) =>
  new TableCell({
    borders, width: { size: 4680, type: WidthType.DXA }, margins: { top: 200, bottom: 200, left: 200, right: 200 },
    shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: plan, font: "Georgia", size: 28, bold: true, color: accent })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 }, children: [
        new TextRun({ text: price, font: "Calibri", size: 40, bold: true, color: darkText }),
        new TextRun({ text: "/mo", font: "Calibri", size: 20, color: gray })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [
        new TextRun({ text: `${annual}/mo annual (2 months free)`, font: "Calibri", size: 18, color: gray })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
        new TextRun({ text: `${setup} one-time setup`, font: "Calibri", size: 18, color: gray })
      ]}),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
        new TextRun({ text: `${minutes} minutes/month`, font: "Calibri", size: 22, bold: true, color: accentDark })
      ]}),
      ...features.map(f => new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun({ text: `  \u2713  ${f}`, font: "Calibri", size: 20, color: "374151" })]
      }))
    ]
  });

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Georgia", color: darkText },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Georgia", color: accentDark },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // ═══════════════════════════════════════════════════════
    // COVER PAGE
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 2880, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        spacer(2000),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "SYNTHARRA", font: "Georgia", size: 18, bold: true, color: accent, characterSpacing: 400 })
        ]}),
        spacer(200),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "AI Receptionist", font: "Georgia", size: 56, bold: true, color: darkText })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
          new TextRun({ text: "for the Trade Industry", font: "Georgia", size: 40, color: accentDark })
        ]}),
        spacer(200),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "Never miss a call. Capture every lead. 24/7.", font: "Calibri", size: 24, color: gray })
        ]}),
        spacer(600),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "Sales & Product Overview", font: "Calibri", size: 20, color: gray })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "www.syntharra.com  |  daniel@syntharra.com", font: "Calibri", size: 20, color: accent })
        ]}),
      ]
    },
    // ═══════════════════════════════════════════════════════
    // THE PROBLEM
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        heading("The Problem Every Trade Business Faces"),
        body("Your phone rings. You're on a roof, under a sink, or elbow-deep in a furnace. The call goes to voicemail. That caller? They're already dialling your competitor."),
        spacer(100),
        body("Research shows that 85% of callers who reach voicemail never call back. For an HVAC company handling 200+ calls per month, that's potentially dozens of lost jobs — tens of thousands in missed revenue every single month."),
        spacer(100),
        body("Hiring a full-time receptionist costs $35,000-$50,000/year. An answering service gives you a script-reading human who can't answer questions about your business. Neither solution scales."),
        spacer(200),
        heading("The Syntharra Solution"),
        body("An AI receptionist that sounds like a real member of your team. It knows your services, your prices, your hours, your promotions. It captures every lead, handles emergencies, transfers urgent calls, and sends you instant notifications — all for a fraction of the cost of a human receptionist."),
        spacer(100),
        body("Your AI receptionist is custom-built for your business. It greets callers by name, answers questions from your company information, captures detailed lead data, and hands off calls when human attention is needed."),
        spacer(100),
        body("It works 24/7. It never calls in sick. It never puts someone on hold. And it gets smarter with every call."),
      ]
    },
    // ═══════════════════════════════════════════════════════
    // FEATURES
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        heading("What's Included"),
        spacer(100),
        new Table({
          width: { size: 9360, type: WidthType.DXA }, columnWidths: [600, 8760],
          rows: [
            featureRow("\uD83D\uDCDE", "Custom AI Voice Agent", "Trained on your business. Answers questions about your services, hours, pricing policy, and service areas using your company's actual information."),
            featureRow("\uD83D\uDCCB", "Intelligent Lead Capture", "Collects caller name, phone, address, and service description. Every lead scored 1-10 for priority. Hot leads flagged instantly."),
            featureRow("\uD83D\uDEA8", "Emergency Call Routing", "Detects true emergencies (no heat in freezing conditions, gas leaks, flooding) and warm-transfers directly to your emergency line with a spoken briefing."),
            featureRow("\uD83D\uDD04", "Warm Transfer with Whisper", "When the AI transfers a call, it briefly tells your team member who's calling and what it's about — so they pick up prepared, not cold."),
            featureRow("\uD83D\uDCF5", "Missed Transfer Alerts", "If a transfer doesn't connect, the AI takes the caller's details and sends you an instant email and SMS marked as a missed transfer needing callback."),
            featureRow("\uD83D\uDCCA", "Live Call Dashboard", "Real-time dashboard showing all calls, lead scores, emergencies, and summaries. Filter by date, type, and priority. Clickable phone numbers."),
            featureRow("\uD83D\uDCE7", "Multi-Channel Notifications", "Lead alerts via email and SMS — up to 3 email addresses and 3 phone numbers. Dispatchers, managers, and owners all stay informed."),
            featureRow("\uD83D\uDCCD", "Address Verification", "Every service address is geocoded and verified with Google Maps. View Map links included in every lead notification."),
            featureRow("\uD83D\uDCC5", "Weekly Performance Reports", "Automated weekly email showing total calls, leads captured, hot leads, service breakdown, and top leads — sent in the client's timezone."),
            featureRow("\u23F0", "After-Hours Intelligence", "Configurable behavior: transfer all calls 24/7, only emergencies after hours, or never transfer after hours. The client chooses."),
            featureRow("\uD83D\uDEE1\uFE0F", "Spam & Robocall Filter", "Automatically detects and ends spam calls. No wasted time, no false leads."),
            featureRow("\uD83C\uDF10", "Multilingual Support", "Built-in multilingual capability — handles callers in multiple languages naturally."),
            featureRow("\uD83D\uDD12", "Dead Letter Queue", "If any part of the system encounters an error, the call data is safely captured in a failover queue. No lead is ever silently lost."),
          ]
        }),
      ]
    },
    // ═══════════════════════════════════════════════════════
    // HOW IT WORKS
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        heading("How It Works"),
        spacer(100),
        boldBody("1. Onboard in 10 Minutes  ", "Fill out a simple online form with your company details, services, hours, and preferences. The form adapts — only showing questions relevant to your setup."),
        spacer(60),
        boldBody("2. AI Agent Built Automatically  ", "Your custom AI receptionist is created instantly with your greeting, your voice preference, your company information, and your call handling rules."),
        spacer(60),
        boldBody("3. Phone Number Assigned  ", "A dedicated phone number is purchased and linked to your AI agent. You simply forward your existing business number to it."),
        spacer(60),
        boldBody("4. Go Live  ", "Calls are answered instantly. Leads flow to your inbox and phone. Your dashboard shows everything in real-time. You focus on the work."),
        spacer(300),
        heading("Onboarding is Fully Automated"),
        body("From the moment a client submits their onboarding form, the entire setup is automated:"),
        spacer(60),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "Form data is parsed and validated", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "AI voice agent is created with custom prompts", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "13-node conversation flow is deployed to Retell AI", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "Client data stored in Supabase", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "Phone number purchased and assigned", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "Welcome email sent with call forwarding instructions and QR codes", font: "Calibri", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: "Internal notification sent to Syntharra team", font: "Calibri", size: 22 })] }),
        spacer(60),
        body("Total time from form submission to live agent: under 60 seconds.", { bold: true, color: accent }),
      ]
    },
    // ═══════════════════════════════════════════════════════
    // PRICING
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        heading("Pricing"),
        spacer(100),
        new Table({
          width: { size: 9360, type: WidthType.DXA }, columnWidths: [4680, 4680],
          rows: [
            new TableRow({
              children: [
                pricingCell("Standard", "$497", "$414", "$1,499", "475", [
                  "Custom AI voice agent",
                  "13-node conversation flow",
                  "Lead capture + scoring",
                  "Emergency call routing",
                  "Warm transfer with whisper",
                  "Email + SMS notifications (3 each)",
                  "Live call dashboard",
                  "Weekly performance reports",
                  "Spam/robocall filtering",
                  "Address geocoding + map links",
                ]),
                pricingCell("Premium", "$997", "$831", "$2,499", "1,000", [
                  "Everything in Standard, plus:",
                  "Double the minutes",
                  "Priority support",
                  "Custom integrations",
                  "Advanced analytics",
                  "Multi-location support",
                  "Dedicated account manager",
                ]),
              ]
            })
          ]
        }),
        spacer(200),
        body("Annual billing saves 2 months (pay for 10, get 12). Setup fee covers custom agent build, conversation flow design, phone number provisioning, and onboarding."),
      ]
    },
    // ═══════════════════════════════════════════════════════
    // ROI
    // ═══════════════════════════════════════════════════════
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        heading("Return on Investment"),
        spacer(100),
        body("The average HVAC service call generates $300-$800 in revenue. A new system installation is $5,000-$15,000. Missing even a handful of calls per month costs more than Syntharra's annual subscription."),
        spacer(100),
        new Table({
          width: { size: 9360, type: WidthType.DXA }, columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, shading: { fill: lightPurple, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "Without Syntharra", font: "Calibri", size: 22, bold: true, color: "DC2626" })] })] }),
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, shading: { fill: lightPurple, type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "With Syntharra", font: "Calibri", size: 22, bold: true, color: "16A34A" })] })] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("15-30 missed calls/month go to voicemail")] }),
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("0 missed calls — every call answered instantly")] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("85% of voicemail callers never call back")] }),
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("100% of callers engaged and details captured")] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("$4,500-$24,000/year in lost jobs")] }),
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("$5,964/year for Standard plan")] }),
            ]}),
            new TableRow({ children: [
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("$35,000-$50,000/year for a human receptionist")] }),
              new TableCell({ borders, width: { size: 4680, type: WidthType.DXA }, margins: cellMargins, children: [body("AI receptionist works 24/7/365 for $497/mo")] }),
            ]}),
          ]
        }),
        spacer(200),
        heading("Ready to Stop Missing Calls?", HeadingLevel.HEADING_2),
        spacer(100),
        body("Contact us today to get started. Your AI receptionist can be live within the hour."),
        spacer(100),
        boldBody("Email:  ", "daniel@syntharra.com"),
        boldBody("Website:  ", "www.syntharra.com"),
        spacer(200),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "SYNTHARRA", font: "Georgia", size: 18, bold: true, color: accent, characterSpacing: 300 })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: "AI Receptionists for the Trade Industry", font: "Calibri", size: 20, color: gray })
        ]}),
      ]
    },
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/syntharra-sales-pitch.docx", buffer);
  console.log("Sales pitch document created: syntharra-sales-pitch.docx");
});
