# Google Apps Scripts - Quick Reference Guide

Quick reference for the Invoice Email Extractor and IP Location Tracker scripts.

---

## 📦 Invoice Email Extractor

### Quick Setup
```bash
1. script.google.com → New project
2. Paste code from google_scripts/invoice_extract.gs
3. Update CONFIG (keywords, folder name)
4. Run testExtraction()
5. Run createAutomationTrigger()
```

### Key Functions
| Function | Purpose |
|----------|---------|
| `extractInvoiceAttachments()` | Main extraction function |
| `testExtraction()` | Test with 5 emails |
| `createAutomationTrigger()` | Set up daily automation |

### Configuration Quick Edit
```javascript
searchKeywords: ['invoice', 'receipt', 'bill']  // Add your keywords
parentFolderName: 'Tax Invoices'                // Change folder name
maxEmailsPerRun: 50                             // Adjust batch size
```

### File Organization
```
📁 Tax Invoices/
  📁 FY2024-2025/
    📄 2024-12-15_sender@email.com_invoice.pdf
  📊 Extracted Invoices Log
```

### Gmail Labels Created
- `Invoices-Extracted` - All processed emails
- `Tax FY2024-2025` - Current financial year

### Common Commands
```javascript
// Test with 5 emails
testExtraction()

// Run full extraction
extractInvoiceAttachments()

// Set up daily automation (2 AM)
createAutomationTrigger()
```

---

## 📍 IP Location Tracker

### Quick Setup
```bash
1. script.google.com → New project
2. Paste code from wfh/code.gs
3. Add HTML file: wfh/IPLocationTracker.html
4. Update CONFIG (IP addresses)
5. Run setupSpreadsheet()
6. Deploy → New deployment → Web app
7. Run createAutomaticTriggers()
```

### Key Functions
| Function | Purpose |
|----------|---------|
| `setupSpreadsheet()` | Create log sheet |
| `testGetMyIP()` | See your current IP |
| `testLocationDetection()` | Test location matching |
| `createAutomaticTriggers()` | Set up automation |
| `getLocationStatistics()` | View statistics |
| `deleteAllTriggers()` | Remove all triggers |

### Configuration Quick Edit
```javascript
// Your IP addresses
home: {
  ipAddresses: ['203.123.45.67'],      // Your home IP
  ispKeywords: ['SuperLoop', 'Telstra'] // Your ISP
}

// Business hours (Mon-Fri, 9AM-5PM)
businessHours: {
  startHour: 9,
  endHour: 17,
  daysOfWeek: [1, 2, 3, 4, 5]
}

// Check every 3 hours
checkInterval: 3
```

### Finding Your IP
```javascript
// Method 1: Visit whatismyipaddress.com
// Method 2: Run this function
testGetMyIP()
```

### Spreadsheet Structure
| Column | Description |
|--------|-------------|
| Timestamp | When logged |
| Location | Home/Office/Unknown |
| IP Address | Your IP |
| ISP/Provider | Internet provider |
| Match Method | How detected |

### Color Coding
- 🟢 Green = Home
- 🔵 Blue = Office
- 🟡 Yellow = Unknown

### Common Commands
```javascript
// See your current IP
testGetMyIP()

// Test location detection
testLocationDetection()

// Set up automation
createAutomaticTriggers()

// View statistics
getLocationStatistics()

// Remove all triggers
deleteAllTriggers()
```

---

## 🔧 Troubleshooting Quick Fixes

### Both Scripts

**Authorization Error:**
```javascript
// Run manually once, grant permissions
extractInvoiceAttachments()  // or
handleAutomaticLocationCheck()
```

**Trigger Not Working:**
```javascript
// Check triggers
// Click Triggers icon (⏰) in left sidebar

// Recreate triggers
createAutomationTrigger()  // Invoice Extractor
createAutomaticTriggers()  // Location Tracker
```

**Execution Timeout:**
```javascript
// Reduce batch size
maxEmailsPerRun: 25  // Invoice Extractor
checkInterval: 4     // Location Tracker
```

### Invoice Extractor

**No Emails Found:**
```javascript
// Check keywords are correct
searchKeywords: ['invoice', 'receipt']

// Check date range (searches from last July 1)
// Manually adjust in getTaxPeriodStart()
```

**Files Not Saving:**
```javascript
// Check execution log (View → Logs)
// Verify folder name exists
// Check file type is allowed
```

### Location Tracker

**Wrong Location:**
```javascript
// Check your current IP
testGetMyIP()

// Update config with correct IP
ipAddresses: ['YOUR_ACTUAL_IP']

// Test detection
testLocationDetection()
```

**No Email Received:**
```javascript
// Check spam folder
// Verify triggers exist (⏰ icon)
// Check execution history
```

---

## 📊 Quick Statistics

### Invoice Extractor
```javascript
// Check execution log after running
Logger.log('Emails processed: ' + totalEmailsProcessed);
Logger.log('Attachments saved: ' + totalAttachmentsSaved);

// View log spreadsheet
// Open "Extracted Invoices Log" in Drive
```

### Location Tracker
```javascript
// Get statistics
getLocationStatistics()

// Output example:
// Total checks: 45
// Home: 30 (66.7%)
// Office: 12 (26.7%)
// Other: 3 (6.7%)
```

---

## ⚙️ Configuration Templates

### Invoice Extractor - Minimal Config
```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50
};
```

### Invoice Extractor - Extended Config
```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement', 'purchase order'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 100,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml', 'txt'],
  spreadsheetName: 'Extracted Invoices Log'
};
```

### Location Tracker - Home Only
```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['YOUR_HOME_IP'],
      ispKeywords: ['YourISP']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3
};
```

### Location Tracker - Home + Office
```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['HOME_IP'],
      ispKeywords: ['HomeISP']
    },
    office: {
      name: 'Office',
      ipAddresses: ['OFFICE_IP'],
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3
};
```

---

## 🚀 Automation Setup

### Invoice Extractor - Daily at 2 AM
```javascript
createAutomationTrigger()
// Creates: Daily trigger at 2 AM
```

### Location Tracker - Every 3 Hours (Business Hours)
```javascript
createAutomaticTriggers()
// Creates: Triggers at 9 AM, 12 PM, 3 PM on weekdays
```

### Custom Trigger Times
```javascript
// Invoice Extractor - Run at 9 AM
ScriptApp.newTrigger('extractInvoiceAttachments')
  .timeBased()
  .atHour(9)
  .everyDays(1)
  .create();

// Location Tracker - Check every hour
CONFIG.checkInterval = 1;
createAutomaticTriggers();
```

---

## 📱 Quick Access URLs

### After Setup, Bookmark These:

**Invoice Extractor:**
- Script: `https://script.google.com/home/projects/YOUR_PROJECT_ID`
- Log Sheet: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID`
- Drive Folder: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`

**Location Tracker:**
- Script: `https://script.google.com/home/projects/YOUR_PROJECT_ID`
- Web App: `https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec`
- Log Sheet: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID`

---

## 🔑 Permissions Required

### Invoice Extractor
- ✅ Read Gmail messages
- ✅ Modify Gmail messages (add labels)
- ✅ Create/modify Google Drive files
- ✅ Create/edit Google Sheets
- ✅ Send emails

### Location Tracker
- ✅ Create/edit Google Sheets
- ✅ Send emails
- ✅ Access external web services (IP APIs)
- ✅ Run as web app

---

## 📋 Checklists

### Invoice Extractor Setup Checklist
- [ ] Create new Google Apps Script project
- [ ] Copy code from `invoice_extract.gs`
- [ ] Update `searchKeywords` in CONFIG
- [ ] Update `parentFolderName` if needed
- [ ] Run `testExtraction()` with 5 emails
- [ ] Verify files in Google Drive
- [ ] Check "Extracted Invoices Log" sheet
- [ ] Run `createAutomationTrigger()` for daily automation
- [ ] Verify trigger created (⏰ icon)

### Location Tracker Setup Checklist
- [ ] Create new Google Apps Script project
- [ ] Copy code from `code.gs`
- [ ] Add HTML file `IPLocationTracker.html`
- [ ] Run `testGetMyIP()` to find your IP
- [ ] Update `ipAddresses` in CONFIG
- [ ] Update `ispKeywords` in CONFIG
- [ ] Run `setupSpreadsheet()`
- [ ] Deploy as Web App
- [ ] Copy Web App URL
- [ ] Test Web App manually
- [ ] Run `createAutomaticTriggers()`
- [ ] Verify triggers created (⏰ icon)

---

## 💡 Pro Tips

### Invoice Extractor
1. Start with `testExtraction()` - always test first
2. Add sender-specific keywords for better matching
3. Export log sheet monthly for backup
4. Use Gmail search to verify processed emails
5. Archive old FY folders annually

### Location Tracker
1. Use IP range matching for dynamic IPs
2. Bookmark the Web App URL for quick access
3. Check logs weekly for accuracy
4. Update IPs when changing networks
5. Export data monthly for tax records

---

## 📞 Quick Help

### Need More Details?
- [Invoice Extractor Full Guide](google_scripts/Invoice-Email-Extractor-Guide.md)
- [Location Tracker Full Guide](wfh/IP-Location-Tracker-Guide.md)
- [Main Documentation](Google-Scripts-Documentation.md)

### Common Questions

**Q: How do I stop automation?**
```javascript
// Delete all triggers
ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
```

**Q: How do I change trigger time?**
```javascript
// Delete old trigger, create new one
deleteAllTriggers()
// Then create new trigger with desired time
```

**Q: How do I export data?**
```
Open spreadsheet → File → Download → CSV/Excel
```

**Q: How do I find my IP?**
```
Visit: whatismyipaddress.com
Or run: testGetMyIP()
```

---

**Last Updated:** December 2024  
**For detailed documentation, see the full guides linked above.**
