# Invoice Email Extractor - Setup & Usage Guide

## 📋 Overview

The **Invoice Email Extractor** is a Google Apps Script that automatically extracts invoice and receipt attachments from your Gmail account, organizes them by Australian Financial Year, and maintains a detailed log in Google Sheets.

### What It Does

- 🔍 **Searches Gmail** for emails containing invoice-related keywords
- 📁 **Organizes attachments** by Australian Financial Year (July 1 - June 30)
- 💾 **Saves files** to Google Drive with structured naming convention
- 📊 **Logs everything** to a Google Sheet for easy tracking
- 🏷️ **Labels emails** with "Invoices-Extracted" and FY-specific labels
- ✅ **Marks as read** and archives processed emails
- 📧 **Sends summary** email after each run

### Why Use This?

- **Tax Time Made Easy**: All invoices organized by financial year
- **Automatic Backup**: Never lose important receipts
- **Time Saver**: No manual downloading and organizing
- **Audit Trail**: Complete log of all extracted documents
- **Set and Forget**: Runs automatically daily

---

## ✨ Features

### Core Functionality
- Searches for emails with attachments containing invoice-related keywords
- Supports multiple file types (PDF, images, Office documents, EML)
- Creates organized folder structure: `Tax Invoices/FY2024-2025/`
- Renames files with date and sender: `2024-12-15_sender@email.com_invoice.pdf`
- Prevents duplicate file saves

### Smart Organization
- **Australian Financial Year**: Automatically calculates FY (July-June)
- **Gmail Labels**: Applies "Invoices-Extracted" and "Tax FY2024-2025" labels
- **Email Management**: Marks processed emails as read and archives them
- **Date Filtering**: Only processes emails from the most recent tax period

### Logging & Tracking
- Creates/updates "Extracted Invoices Log" spreadsheet
- Logs: timestamp, email date, sender, subject, attachment details
- Stores log in the same Tax Invoices folder
- Sends summary email after each extraction run

### Automation
- Can run automatically daily at 2 AM
- Processes up to 50 emails per run (configurable)
- Test mode available for safe testing with 5 emails

---

## 📋 Prerequisites

Before setting up the script, ensure you have:

1. **Google Account** with Gmail and Google Drive access
2. **Gmail emails** with invoice/receipt attachments
3. **Basic understanding** of Google Apps Script (helpful but not required)
4. **5-10 minutes** for initial setup

---

## 🚀 Setup Instructions

### Step 1: Create the Google Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **"New project"**
3. Name your project: `Invoice Email Extractor`
4. Delete the default `function myFunction() {}` code

### Step 2: Add the Script Code

1. Copy the entire contents of `invoice_extract.gs`
2. Paste it into the script editor
3. Click the **Save** icon (💾) or press `Ctrl+S` / `Cmd+S`

### Step 3: Configure Your Settings

Edit the `CONFIG` object at the top of the script:

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml'],
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

**Customization Options:**
- `searchKeywords`: Add/remove keywords to match your invoice emails
- `parentFolderName`: Change the main folder name in Google Drive
- `maxEmailsPerRun`: Increase/decrease batch size (max 500)
- `allowedFileTypes`: Add/remove file extensions

### Step 4: Grant Permissions

1. Click the **Run** button (▶️) or select `extractInvoiceAttachments` from the function dropdown
2. Click **Review permissions**
3. Choose your Google account
4. Click **Advanced** → **Go to Invoice Email Extractor (unsafe)**
5. Click **Allow**

**Permissions Required:**
- Read and modify Gmail messages
- Create and manage Google Drive files
- Create and edit Google Sheets
- Send emails as you

### Step 5: Test the Script

Run the test function first:

1. Select `testExtraction` from the function dropdown
2. Click **Run** (▶️)
3. Check the **Execution log** (View → Logs)
4. Verify files appear in Google Drive under "Tax Invoices"
5. Check the "Extracted Invoices Log" spreadsheet

### Step 6: Set Up Automation (Optional)

To run automatically every day:

1. Select `createAutomationTrigger` from the function dropdown
2. Click **Run** (▶️)
3. The script will now run daily at 2 AM

**To verify the trigger:**
1. Click the **Triggers** icon (⏰) in the left sidebar
2. You should see: `extractInvoiceAttachments` - Time-driven - Day timer - 2am to 3am

---

## ⚙️ Configuration Options Explained

### Search Keywords
```javascript
searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement']
```
- Searches email **subject** and **body** for these terms
- Case-insensitive matching
- Add industry-specific terms (e.g., 'purchase order', 'remittance')

### Folder Structure
```javascript
parentFolderName: 'Tax Invoices'
```
- Creates this folder in your Google Drive root
- Financial year subfolders created automatically: `FY2024-2025`

### Processing Limits
```javascript
maxEmailsPerRun: 50
```
- Prevents timeout errors on large mailboxes
- Increase for faster initial processing (max 500)
- Decrease if experiencing timeouts

### File Types
```javascript
allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml']
```
- Only these file types will be saved
- Remove types you don't need
- Add others like `'txt'`, `'csv'`, `'zip'`

### Gmail Labels
```javascript
processedLabelName: 'Invoices-Extracted'
fyLabelPrefix: 'Tax FY'
```
- Creates labels: `Invoices-Extracted` and `Tax FY2024-2025`
- Prevents reprocessing the same emails
- Helps organize your Gmail

---

## 📖 Usage Guide

### Running Manually

1. Open your script at [script.google.com](https://script.google.com)
2. Select `extractInvoiceAttachments` from the function dropdown
3. Click **Run** (▶️)
4. Check execution log for results
5. Check your email for summary

### Testing with Limited Emails

Use the `testExtraction` function to process only 5 emails:

1. Select `testExtraction` from dropdown
2. Click **Run**
3. Review results before full processing

### Monitoring the Log Sheet

The "Extracted Invoices Log" spreadsheet contains:

| Column | Description |
|--------|-------------|
| Log Timestamp | When the file was extracted |
| Email Date | Original email date |
| Sender | Email address of sender |
| Subject | Email subject line |
| Attachment Name | Original filename |
| Attachment Type | File extension |
| Saved File Name | New filename in Drive |

**Tips:**
- Sort by date to find recent extractions
- Filter by sender to find specific vendors
- Use for tax preparation and audits

### Checking Your Google Drive

Files are organized as:
```
📁 Tax Invoices/
  📁 FY2024-2025/
    📄 2024-12-15_vendor@email.com_invoice.pdf
    📄 2024-12-20_supplier@company.com_receipt.pdf
  📁 FY2023-2024/
    📄 2023-08-10_shop@store.com_bill.pdf
  📊 Extracted Invoices Log
```

### Managing Gmail Labels

The script creates these labels:
- **Invoices-Extracted**: All processed emails
- **Tax FY2024-2025**: Current financial year emails
- **Tax FY2023-2024**: Previous financial year emails

**To view labeled emails:**
1. Open Gmail
2. Look for labels in the left sidebar
3. Click to view all emails with that label

---

## 🔧 How It Works

### Workflow Overview

1. **Search Gmail**: Builds query with keywords and date filter
2. **Filter Emails**: Excludes already processed (labeled) emails
3. **Process Threads**: Iterates through email threads
4. **Extract Attachments**: Gets all attachments from messages
5. **Determine FY**: Calculates Australian Financial Year from email date
6. **Save Files**: Creates folders and saves with structured naming
7. **Log Details**: Records extraction in Google Sheet
8. **Apply Labels**: Adds "Invoices-Extracted" and FY-specific labels
9. **Archive**: Marks as read and moves to archive
10. **Send Summary**: Emails you the results

### Date Filtering Logic

The script only processes emails from the most recent tax period:

```javascript
// If today is after July 1, 2024: searches from July 1, 2024
// If today is before July 1, 2024: searches from July 1, 2023
```

This prevents reprocessing old emails while catching all current FY invoices.

### File Naming Convention

Files are renamed to: `YYYY-MM-DD_sender@email.com_originalname.ext`

**Example:**
- Original: `invoice.pdf`
- Renamed: `2024-12-15_accounts@vendor.com_invoice.pdf`

**Benefits:**
- Chronological sorting
- Easy sender identification
- Prevents filename conflicts
- Maintains original name for reference

### Duplicate Prevention

The script checks if a file already exists before saving:
- Same filename in same folder = skipped
- Prevents duplicate processing
- Logged as "File already exists, skipping"

---

## 🐛 Troubleshooting

### Common Issues

#### "Authorization required"
**Problem**: Script needs permissions
**Solution**: 
1. Run the script manually once
2. Follow the authorization prompts
3. Grant all requested permissions

#### "No emails found"
**Problem**: Search query returns no results
**Solution**:
1. Check your `searchKeywords` - are they too specific?
2. Verify emails exist with attachments
3. Check date range - emails might be too old
4. Look for the "Invoices-Extracted" label - emails might already be processed

#### "Execution timeout"
**Problem**: Script runs too long (6-minute limit)
**Solution**:
1. Reduce `maxEmailsPerRun` to 25 or less
2. Run multiple times to process all emails
3. Consider running more frequently (twice daily)

#### "Files not appearing in Drive"
**Problem**: Files saved but can't find them
**Solution**:
1. Check the "Tax Invoices" folder in Drive
2. Look in the correct FY subfolder
3. Search Drive for the filename
4. Check execution log for errors

#### "Duplicate files being created"
**Problem**: Same file saved multiple times
**Solution**:
1. Check if emails are being relabeled
2. Verify the "Invoices-Extracted" label is applied
3. Look for errors in the log

#### "Wrong Financial Year folder"
**Problem**: Files in incorrect FY folder
**Solution**:
1. Check the email date (not extraction date)
2. Verify Australian FY logic (July-June)
3. Manually move files if needed

### Checking Execution Logs

1. Open your script
2. Click **View** → **Logs** or **Executions**
3. Look for error messages in red
4. Check "Emails processed" and "Attachments saved" counts

### Getting Help

If issues persist:
1. Check the execution log for specific error messages
2. Verify all permissions are granted
3. Test with `testExtraction` function first
4. Review the CONFIG settings for typos

---

## 🎨 Customization Tips

### Adding More Keywords

```javascript
searchKeywords: [
  'invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement',
  'purchase order', 'PO', 'remittance', 'credit note', 'quote'
]
```

### Excluding Specific Senders

Add to the search query in `buildSearchQuery()`:

```javascript
query += '-from:spam@example.com ';
```

### Changing the Trigger Time

Modify `createAutomationTrigger()`:

```javascript
ScriptApp.newTrigger('extractInvoiceAttachments')
  .timeBased()
  .atHour(9)  // Change to 9 AM
  .everyDays(1)
  .create();
```

### Processing Older Emails

Modify `getTaxPeriodStart()` to go back further:

```javascript
// Go back 2 years instead of 1
return new Date(year - 2, 6, 1);
```

### Adding Custom Metadata

Modify `saveAttachment()` to add more file description:

```javascript
file.setDescription(
  'From: ' + message.getFrom() + 
  '\nSubject: ' + message.getSubject() + 
  '\nDate: ' + emailDate +
  '\nExtracted: ' + new Date()
);
```

### Creating Multiple Folder Structures

Organize by sender instead of FY:

```javascript
function getOrCreateSenderFolder(parentFolder, sender) {
  const cleanSender = sender.replace(/[^a-zA-Z0-9]/g, '_');
  return getOrCreateFolder(cleanSender, parentFolder);
}
```

### Running Multiple Times Daily

Create additional triggers:

```javascript
// Morning run at 9 AM
ScriptApp.newTrigger('extractInvoiceAttachments')
  .timeBased()
  .atHour(9)
  .everyDays(1)
  .create();

// Evening run at 6 PM
ScriptApp.newTrigger('extractInvoiceAttachments')
  .timeBased()
  .atHour(18)
  .everyDays(1)
  .create();
```

---

## 📊 Best Practices

### Initial Setup
1. Start with `testExtraction` to process 5 emails
2. Verify folder structure and file naming
3. Check the log sheet for accuracy
4. Then run full extraction manually
5. Finally, set up automation

### Regular Maintenance
- Review the log sheet monthly
- Check for any failed extractions
- Verify all invoices are captured
- Update keywords as needed

### Tax Time Preparation
- Run manually before tax deadline
- Export log sheet to CSV for accountant
- Verify all FY folders are complete
- Share Drive folder with tax professional

### Privacy & Security
- Script only accesses your own Gmail and Drive
- No data sent to external services
- Files remain in your Google Drive
- Consider using a dedicated tax email

---

## 📝 Summary

The Invoice Email Extractor automates the tedious task of downloading and organizing invoice attachments from Gmail. With automatic Financial Year organization, comprehensive logging, and set-and-forget automation, it's an essential tool for tax preparation and record keeping.

**Key Benefits:**
- ⏱️ Saves hours of manual work
- 📁 Perfect organization by FY
- 📊 Complete audit trail
- 🔄 Fully automated
- 🇦🇺 Australian tax year compliant

**Next Steps:**
1. Complete the setup following this guide
2. Run a test extraction
3. Review the results
4. Set up daily automation
5. Enjoy automated invoice management!

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review execution logs for errors
3. Test with the `testExtraction` function
4. Verify all configuration settings

**Script Version**: 1.0  
**Last Updated**: December 2024  
**Compatible With**: Google Apps Script, Gmail, Google Drive
