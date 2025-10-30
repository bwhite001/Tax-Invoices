# Google Apps Scripts Documentation

This repository contains two powerful Google Apps Scripts designed to automate common tasks: invoice extraction from Gmail and work location tracking for remote workers.

---

## 📦 Available Scripts

### 1. Invoice Email Extractor
**Location:** `google_scripts/invoice_extract.gs`

Automatically extracts invoice and receipt attachments from Gmail, organizes them by Australian Financial Year, and maintains a detailed log.

**Key Features:**
- 🔍 Searches Gmail for invoice-related emails
- 📁 Organizes by Australian Financial Year (July-June)
- 💾 Saves to Google Drive with structured naming
- 📊 Logs everything to Google Sheets
- 🏷️ Applies Gmail labels and archives emails
- ⏰ Runs automatically daily

**Perfect For:**
- Tax preparation and record keeping
- Automatic invoice backup
- Financial year organization
- Audit trail maintenance

**[📖 Read Full Documentation →](google_scripts/Invoice-Email-Extractor-Guide.md)**

---

### 2. IP-Based Location Tracker
**Location:** `wfh/code.gs` + `wfh/IPLocationTracker.html`

Automatically tracks your work location (Home/Office) based on network IP address during business hours.

**Key Features:**
- 🌐 Automatic IP-based location detection
- 📊 Logs to Google Sheets with color coding
- ⏰ Automated checks every 3 hours (Mon-Fri, 9AM-5PM)
- 🌍 Uses free IP geolocation APIs
- 📈 Provides location statistics
- 🔒 Privacy-friendly (business hours only)

**Perfect For:**
- Work-from-home compliance tracking
- Tax deductions for home office
- Location-based reporting
- Remote work documentation

**[📖 Read Full Documentation →](wfh/IP-Location-Tracker-Guide.md)**

---

## 🚀 Quick Start

### Invoice Email Extractor

1. Go to [script.google.com](https://script.google.com)
2. Create new project: "Invoice Email Extractor"
3. Copy code from `google_scripts/invoice_extract.gs`
4. Configure your settings (keywords, folder names)
5. Run `testExtraction` to test with 5 emails
6. Set up daily automation with `createAutomationTrigger`

**[Full Setup Guide →](google_scripts/Invoice-Email-Extractor-Guide.md#-setup-instructions)**

### IP Location Tracker

1. Go to [script.google.com](https://script.google.com)
2. Create new project: "IP Location Tracker"
3. Copy code from `wfh/code.gs`
4. Add HTML file from `wfh/IPLocationTracker.html`
5. Configure your IP addresses
6. Deploy as web app
7. Set up automation with `createAutomaticTriggers`

**[Full Setup Guide →](wfh/IP-Location-Tracker-Guide.md#-setup-instructions)**

---

## 📋 Prerequisites

Both scripts require:
- Google Account (Gmail, Drive, Sheets access)
- Basic understanding of Google Apps Script (helpful but not required)
- 10-15 minutes for initial setup

### Additional Requirements

**Invoice Extractor:**
- Gmail emails with invoice attachments
- Google Drive storage space

**Location Tracker:**
- Your home/office IP addresses
- Web browser for location checks

---

## 🔧 Configuration

### Invoice Email Extractor Configuration

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'],
  spreadsheetName: 'Extracted Invoices Log'
};
```

### Location Tracker Configuration

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['YOUR_HOME_IP'],
      ispKeywords: ['YourISP']
    },
    office: {
      name: 'Office',
      ipAddresses: ['YOUR_OFFICE_IP'],
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]  // Mon-Fri
  },
  checkInterval: 3  // Every 3 hours
};
```

---

## 📊 Features Comparison

| Feature | Invoice Extractor | Location Tracker |
|---------|------------------|------------------|
| **Automation** | Daily at 2 AM | Every 3 hours (business hours) |
| **Google Drive** | ✅ Saves files | ❌ No files |
| **Google Sheets** | ✅ Extraction log | ✅ Location log |
| **Gmail Integration** | ✅ Reads & labels | ✅ Sends notifications |
| **Web Interface** | ❌ No | ✅ Yes |
| **External APIs** | ❌ No | ✅ IP geolocation |
| **Privacy Impact** | Low (email only) | Low (IP only, business hours) |

---

## 🔒 Privacy & Security

### Invoice Email Extractor
- Only accesses your Gmail and Drive
- No external services used
- All data stays in your Google account
- Processes only invoice-related emails

### Location Tracker
- Only tracks during business hours
- Uses public IP address (not GPS)
- No continuous tracking
- All data stored in your Google Sheets
- Free geolocation APIs (no account needed)

---

## 🐛 Troubleshooting

### Common Issues for Both Scripts

**"Authorization required"**
- Run the script manually once
- Follow authorization prompts
- Grant all requested permissions

**"Execution timeout"**
- Reduce batch sizes in configuration
- Run more frequently
- Check execution logs for specific errors

**"Script not running automatically"**
- Verify triggers are created (click Triggers icon ⏰)
- Check trigger execution history
- Recreate triggers if needed

### Script-Specific Issues

**Invoice Extractor:**
- [Troubleshooting Guide](google_scripts/Invoice-Email-Extractor-Guide.md#-troubleshooting)

**Location Tracker:**
- [Troubleshooting Guide](wfh/IP-Location-Tracker-Guide.md#-troubleshooting)

---

## 📖 Documentation Structure

Each script has comprehensive documentation including:

1. **Overview** - What it does and why it's useful
2. **Features** - Detailed feature list
3. **Prerequisites** - Requirements before setup
4. **Setup Instructions** - Step-by-step guide
5. **Configuration Options** - All settings explained
6. **Usage Guide** - How to use the script
7. **How It Works** - Technical explanation
8. **Troubleshooting** - Common issues and solutions
9. **Customization Tips** - How to adapt for your needs

---

## 🎯 Use Cases

### Invoice Email Extractor

**Tax Preparation:**
- Automatically collect all invoices for the financial year
- Organized folder structure ready for accountant
- Complete log for audit trail

**Business Expense Tracking:**
- Backup all receipts automatically
- Easy retrieval by date or sender
- Never lose important documents

**Compliance & Auditing:**
- Maintain complete records
- Timestamped extraction log
- Searchable spreadsheet database

### Location Tracker

**Work-From-Home Compliance:**
- Automatic tracking for WFH policies
- Proof of location for employer
- No manual entry required

**Tax Deductions:**
- Document home office usage
- Calculate home vs office percentages
- Export data for tax returns

**Billing & Timesheets:**
- Verify location for client billing
- Support for location-based rates
- Automatic record keeping

---

## 🔄 Updates & Maintenance

### Recommended Maintenance Schedule

**Weekly:**
- Review execution logs for errors
- Check spreadsheet logs for accuracy
- Verify automation is running

**Monthly:**
- Update IP addresses if changed (Location Tracker)
- Review and adjust keywords (Invoice Extractor)
- Export logs for backup

**Quarterly:**
- Review configuration settings
- Update customizations as needed
- Check Google Drive storage usage

**Annually:**
- Archive old financial year data
- Update for new tax year
- Review and optimize settings

---

## 💡 Tips & Best Practices

### General Tips

1. **Start with Testing**: Always use test functions before full automation
2. **Monitor Initially**: Check logs daily for the first week
3. **Backup Data**: Export spreadsheets regularly
4. **Document Changes**: Keep notes on configuration changes
5. **Review Permissions**: Understand what access scripts have

### Invoice Extractor Tips

1. **Customize Keywords**: Add industry-specific terms
2. **Adjust Batch Size**: Start small, increase gradually
3. **Check Labels**: Verify Gmail labels are applied correctly
4. **Review Log Sheet**: Use for tax preparation
5. **Archive Old Data**: Move old FY folders to archive

### Location Tracker Tips

1. **Update IPs Regularly**: Home IPs can change
2. **Use IP Ranges**: More reliable than exact IPs
3. **Add ISP Keywords**: Provides fallback matching
4. **Monitor Accuracy**: Check first week of logs
5. **Bookmark Web App**: Quick access for manual checks

---

## 🤝 Contributing

These scripts are designed to be customizable. Feel free to:

- Modify configuration for your needs
- Add new features
- Improve error handling
- Enhance logging
- Create additional integrations

---

## 📞 Support Resources

### Documentation
- [Invoice Extractor Full Guide](google_scripts/Invoice-Email-Extractor-Guide.md)
- [Location Tracker Full Guide](wfh/IP-Location-Tracker-Guide.md)

### Google Resources
- [Google Apps Script Documentation](https://developers.google.com/apps-script)
- [Gmail Service Reference](https://developers.google.com/apps-script/reference/gmail)
- [Drive Service Reference](https://developers.google.com/apps-script/reference/drive)
- [Spreadsheet Service Reference](https://developers.google.com/apps-script/reference/spreadsheet)

### Testing Functions

**Invoice Extractor:**
```javascript
testExtraction()  // Test with 5 emails
```

**Location Tracker:**
```javascript
testGetMyIP()              // See your current IP
testLocationDetection()    // Test location matching
getLocationStatistics()    // View statistics
```

---

## 📝 Version History

**Version 1.0** (December 2024)
- Initial release
- Invoice Email Extractor with FY organization
- IP-Based Location Tracker with automation
- Comprehensive documentation
- HTML web interface for location tracker

---

## 📄 License

These scripts are provided as-is for personal and commercial use. Feel free to modify and adapt to your needs.

---

## 🎉 Getting Started

Ready to automate your workflow? Choose a script and follow its setup guide:

1. **[Invoice Email Extractor Setup →](google_scripts/Invoice-Email-Extractor-Guide.md#-setup-instructions)**
2. **[IP Location Tracker Setup →](wfh/IP-Location-Tracker-Guide.md#-setup-instructions)**

Both scripts can be set up in 10-15 minutes and will save you hours of manual work!

---

**Last Updated:** December 2024  
**Maintained By:** Tax Invoices Project  
**Compatible With:** Google Apps Script, Gmail, Google Drive, Google Sheets
