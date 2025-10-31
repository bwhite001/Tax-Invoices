# google_scripts - Parameters Reference

Complete parameter documentation for the Gmail Invoice Extraction module.

---

## 📋 Table of Contents

- [Configuration Object](#configuration-object)
- [Search Parameters](#search-parameters)
- [Folder Parameters](#folder-parameters)
- [Processing Parameters](#processing-parameters)
- [Label Parameters](#label-parameters)
- [File Type Parameters](#file-type-parameters)
- [Functions](#functions)
- [Examples](#examples)

---

## ⚙️ Configuration Object

**Location**: `google_scripts/invoice_extract.gs`

All parameters are defined in the `CONFIG` object at the top of the script.

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

---

## 🔍 Search Parameters

### searchKeywords

```javascript
searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement']
```

- **Type**: Array of strings
- **Default**: `['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement']`
- **Description**: Keywords to search in email subject and body
- **Required**: Yes
- **Case-insensitive**: Yes

**When to change**:
- Add industry-specific terms
- Add vendor-specific terms
- Remove irrelevant keywords

**Examples**:
```javascript
// Standard
searchKeywords: ['invoice', 'receipt', 'tax invoice']

// Extended
searchKeywords: [
  'invoice', 'receipt', 'tax invoice',
  'purchase order', 'PO', 'remittance',
  'credit note', 'quote', 'estimate'
]

// Minimal
searchKeywords: ['invoice']

// Vendor-specific
searchKeywords: [
  'invoice', 'receipt',
  'amazon order', 'ebay purchase',
  'paypal receipt'
]
```

**Search Behavior**:
- Searches email subject AND body
- Case-insensitive matching
- OR logic (matches any keyword)
- Requires attachment

**Gmail Query Built**:
```
has:attachment (invoice OR receipt OR "tax invoice" OR bill OR payment OR statement)
```

---

## 📁 Folder Parameters

### parentFolderName

```javascript
parentFolderName: 'Tax Invoices'
```

- **Type**: String
- **Default**: `'Tax Invoices'`
- **Description**: Main folder name in Google Drive
- **Required**: Yes
- **Location**: Google Drive root

**When to change**:
- Different folder name preference
- Multiple tax folders
- Organization requirements

**Examples**:
```javascript
// Standard
parentFolderName: 'Tax Invoices'

// Alternative
parentFolderName: 'Business Expenses'
parentFolderName: 'Tax Documents'
parentFolderName: 'Receipts'
```

**Folder Structure Created**:
```
Google Drive/
└── Tax Invoices/              ← parentFolderName
    ├── FY2024-2025/           ← Auto-created
    │   ├── file1.pdf
    │   └── file2.pdf
    ├── FY2023-2024/
    └── Extracted Invoices Log ← Spreadsheet
```

---

## ⚙️ Processing Parameters

### maxEmailsPerRun

```javascript
maxEmailsPerRun: 50
```

- **Type**: Integer
- **Default**: `50`
- **Description**: Maximum emails to process per execution
- **Range**: 1-500
- **Required**: Yes

**When to change**:
- Initial processing (increase for faster)
- Timeout issues (decrease)
- Daily automation (keep moderate)

**Examples**:
```javascript
// Conservative (avoid timeouts)
maxEmailsPerRun: 25

// Standard
maxEmailsPerRun: 50

// Aggressive (initial processing)
maxEmailsPerRun: 100

// Maximum (may timeout)
maxEmailsPerRun: 500
```

**Considerations**:
- Google Apps Script timeout: 6 minutes
- More emails = longer processing
- Attachments increase processing time
- Can run multiple times

**Timeout Prevention**:
```javascript
// If processing times out
maxEmailsPerRun: 25  // Reduce

// If processing is fast
maxEmailsPerRun: 100  // Increase
```

---

## 🏷️ Label Parameters

### processedLabelName

```javascript
processedLabelName: 'Invoices-Extracted'
```

- **Type**: String
- **Default**: `'Invoices-Extracted'`
- **Description**: Gmail label for processed emails
- **Required**: Yes
- **Auto-created**: Yes

**When to change**:
- Different label preference
- Multiple extraction scripts
- Organization requirements

**Examples**:
```javascript
// Standard
processedLabelName: 'Invoices-Extracted'

// Alternative
processedLabelName: 'Processed'
processedLabelName: 'Tax-Processed'
processedLabelName: 'Archived-Invoices'
```

**Label Behavior**:
- Created automatically if doesn't exist
- Applied to processed emails
- Prevents reprocessing
- Visible in Gmail sidebar

### fyLabelPrefix

```javascript
fyLabelPrefix: 'Tax FY'
```

- **Type**: String
- **Default**: `'Tax FY'`
- **Description**: Prefix for financial year labels
- **Required**: Yes
- **Auto-created**: Yes

**When to change**:
- Different label naming
- Organization requirements

**Examples**:
```javascript
// Standard
fyLabelPrefix: 'Tax FY'
// Creates: "Tax FY2024-2025"

// Alternative
fyLabelPrefix: 'FY'
// Creates: "FY2024-2025"

fyLabelPrefix: 'Financial Year'
// Creates: "Financial Year2024-2025"
```

**Labels Created**:
- `Invoices-Extracted` (all processed)
- `Tax FY2024-2025` (current FY)
- `Tax FY2023-2024` (previous FY)
- etc.

---

## 📄 File Type Parameters

### allowedFileTypes

```javascript
allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml']
```

- **Type**: Array of strings (file extensions)
- **Default**: 10 file types
- **Description**: File extensions to extract
- **Required**: Yes
- **Case-insensitive**: Yes

**When to change**:
- Add new file types
- Remove unwanted types
- Optimize storage

**Examples**:
```javascript
// Standard (all types)
allowedFileTypes: [
  'pdf', 'png', 'jpg', 'jpeg', 'gif',
  'doc', 'docx', 'xls', 'xlsx', 'eml'
]

// PDF only
allowedFileTypes: ['pdf']

// Documents only
allowedFileTypes: ['pdf', 'doc', 'docx']

// Images only
allowedFileTypes: ['png', 'jpg', 'jpeg', 'gif']

// Extended
allowedFileTypes: [
  'pdf', 'png', 'jpg', 'jpeg', 'gif',
  'doc', 'docx', 'xls', 'xlsx', 'eml',
  'txt', 'csv', 'zip'  // Added
]
```

**File Type Details**:

| Extension | Type | Common Use |
|-----------|------|------------|
| **pdf** | Document | Invoices, receipts |
| **png, jpg, jpeg, gif** | Image | Scanned receipts, screenshots |
| **doc, docx** | Word | Invoice documents |
| **xls, xlsx** | Excel | Itemized invoices |
| **eml** | Email | Forwarded invoices |
| **txt** | Text | Plain text invoices |
| **csv** | Data | Transaction exports |
| **zip** | Archive | Multiple files |

---

## 📊 Spreadsheet Parameters

### spreadsheetName

```javascript
spreadsheetName: 'Extracted Invoices Log'
```

- **Type**: String
- **Default**: `'Extracted Invoices Log'`
- **Description**: Name of log spreadsheet
- **Required**: Yes
- **Auto-created**: Yes
- **Location**: Same folder as parentFolderName

**When to change**:
- Different spreadsheet name
- Multiple log sheets
- Organization requirements

**Examples**:
```javascript
// Standard
spreadsheetName: 'Extracted Invoices Log'

// Alternative
spreadsheetName: 'Invoice Extraction Log'
spreadsheetName: 'Tax Document Log'
spreadsheetName: 'Receipt Tracker'
```

**Spreadsheet Structure**:

| Column | Description |
|--------|-------------|
| Log Timestamp | When extracted |
| Email Date | Original email date |
| Sender | Email sender |
| Subject | Email subject |
| Attachment Name | Original filename |
| Attachment Type | File extension |
| Saved File Name | New filename in Drive |

---

## 🔧 Functions

### Main Functions

#### extractInvoiceAttachments()

```javascript
function extractInvoiceAttachments()
```

- **Description**: Main extraction function
- **Parameters**: None (uses CONFIG)
- **Returns**: Void
- **Execution**: Manual or automated

**When to run**:
- Manual processing
- Automated daily run
- Initial setup

#### testExtraction()

```javascript
function testExtraction()
```

- **Description**: Test with 5 emails only
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual only

**When to run**:
- Initial setup
- Testing changes
- Verifying configuration

#### createAutomationTrigger()

```javascript
function createAutomationTrigger()
```

- **Description**: Set up daily automation at 2 AM
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual (once)

**When to run**:
- After initial setup
- To enable automation

#### deleteAllTriggers()

```javascript
function deleteAllTriggers()
```

- **Description**: Remove all triggers
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual

**When to run**:
- Disable automation
- Reset triggers
- Troubleshooting

---

## 📝 Examples

### Example 1: Standard Configuration

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg'],
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

**Use case**: Standard setup, common file types

### Example 2: Conservative (Avoid Timeouts)

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 25,  // Reduced
  allowedFileTypes: ['pdf'],  // PDF only
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

**Use case**: Slow connection, many attachments

### Example 3: Aggressive (Initial Processing)

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 100,  // Increased
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'],
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

**Use case**: Initial processing, fast connection

### Example 4: Extended Keywords

```javascript
const CONFIG = {
  searchKeywords: [
    'invoice', 'receipt', 'tax invoice',
    'purchase order', 'PO', 'remittance',
    'credit note', 'quote', 'estimate',
    'statement', 'bill'
  ],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml'],
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

**Use case**: Comprehensive extraction

### Example 5: Custom Organization

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt'],
  parentFolderName: 'Business Expenses',  // Custom
  processedLabelName: 'Processed',  // Custom
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg'],
  spreadsheetName: 'Expense Log',  // Custom
  fyLabelPrefix: 'FY'  // Custom
};
```

**Use case**: Custom naming convention

---

## 🔧 Parameter Validation

### Search Keywords

```javascript
// Valid
['invoice', 'receipt']  ✓

// Warning
[]  ⚠️ Empty array, no matches
['']  ⚠️ Empty string, no matches
```

### Max Emails

```javascript
// Valid
maxEmailsPerRun: 50  ✓
maxEmailsPerRun: 1   ✓

// Warning
maxEmailsPerRun: 0   ⚠️ No processing
maxEmailsPerRun: 1000  ⚠️ May timeout
```

### File Types

```javascript
// Valid
['pdf', 'png', 'jpg']  ✓

// Warning
[]  ⚠️ No files extracted
['PDF', 'PNG']  ⚠️ Use lowercase
```

---

## 💡 Tips & Best Practices

### Search Keywords

**Best practices**:
- Start with common terms
- Add specific terms gradually
- Test with small batches
- Review unmatched emails

**Avoid**:
- Too generic (e.g., "email", "message")
- Too specific (e.g., "Invoice #12345")
- Special characters

### Max Emails Per Run

**Guidelines**:
- Initial processing: 50-100
- Daily automation: 25-50
- Slow connection: 10-25
- Fast connection: 50-100

**Monitoring**:
- Check execution logs
- Watch for timeouts
- Adjust as needed

### File Types

**Recommendations**:
- Include PDF (most common)
- Include images (scanned receipts)
- Include documents (Word, Excel)
- Exclude unnecessary types

### Folder Organization

**Best practices**:
- Use clear folder names
- Keep consistent naming
- Don't nest too deep
- Regular cleanup

---

## ⚠️ Common Issues

### Issue: "No emails found"

**Solution**:
```javascript
// Check keywords
searchKeywords: ['invoice', 'receipt']

// Verify emails exist with attachments
// Check Gmail manually
```

### Issue: "Script timeout"

**Solution**:
```javascript
// Reduce max emails
maxEmailsPerRun: 25  // From 50

// Reduce file types
allowedFileTypes: ['pdf']  // From all types
```

### Issue: "Duplicate files"

**Solution**:
- Check if emails are being relabeled
- Verify processedLabelName is applied
- Check for errors in logs

### Issue: "Wrong folder"

**Solution**:
```javascript
// Check folder name
parentFolderName: 'Tax Invoices'

// Verify folder exists in Drive
// Check permissions
```

---

## 📚 Related Documentation

- **[Invoice-Email-Extractor-Guide.md](Invoice-Email-Extractor-Guide.md)** - Complete setup guide
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick start
- **[../MODULE_INDEX.md](../MODULE_INDEX.md)** - All modules

---

## 🔄 Automation Configuration

### Daily Trigger

Created by `createAutomationTrigger()`:

```javascript
ScriptApp.newTrigger('extractInvoiceAttachments')
  .timeBased()
  .atHour(2)  // 2 AM
  .everyDays(1)
  .create();
```

**Customization**:
```javascript
// Different time
.atHour(9)  // 9 AM

// Different frequency
.everyDays(7)  // Weekly

// Specific days
.onWeekDay(ScriptApp.WeekDay.MONDAY)
```

---

*Last Updated: December 2024*  
*Version: 1.0*
