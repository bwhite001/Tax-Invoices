/**
 * Invoice Email Extractor for Tax Purposes
 * Extracts emails with invoice-related attachments, organizes by Australian Financial Year,
 * and logs each extracted invoice to a Google Sheet.
 * MODIFIED: Now marks processed threads as read, applies FY-specific Gmail labels, and archives them.
 */

// ===== CONFIGURATION =====
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml'],
  spreadsheetName: 'Extracted Invoices Log',
  // Prefix for FY-specific Gmail labels (e.g., "Tax FY2024-2025")
  fyLabelPrefix: 'Tax FY'
};

/**
 * Main function to extract invoice attachments from Gmail
 */
function extractInvoiceAttachments() {
  try {
    Logger.log('Starting invoice extraction process...');

    const processedLabel = getOrCreateLabel(CONFIG.processedLabelName);
    const parentFolder = getOrCreateFolder(CONFIG.parentFolderName);

    const searchQuery = buildSearchQuery();
    Logger.log('Search query: ' + searchQuery);
    const threads = GmailApp.search(searchQuery, 0, CONFIG.maxEmailsPerRun);
    Logger.log('Found ' + threads.length + ' email threads to process');

    let totalAttachmentsSaved = 0;
    let totalEmailsProcessed = 0;

    for (let i = 0; i < threads.length; i++) {
      const thread = threads[i];
      const messages = thread.getMessages();
      let hasAttachments = false; // Track if thread has any attachments

      for (let j = 0; j < messages.length; j++) {
        const message = messages[j];
        const attachments = message.getAttachments();

        if (attachments.length > 0) {
          hasAttachments = true;
          const emailDate = message.getDate();
          // Subject/sender could be used for logging
          Logger.log('Processing email: ' + message.getSubject());
          const fyFolder = getOrCreateFYFolder(parentFolder, emailDate);

          for (let k = 0; k < attachments.length; k++) {
            const attachment = attachments[k];
            if (isAllowedFileType(attachment)) {
              saveAttachment(attachment, fyFolder, message, emailDate);
              totalAttachmentsSaved++;
            }
          }

          totalEmailsProcessed++;
        }
      }

      // Only apply labels, mark as read, and archive if the thread had attachments
      if (hasAttachments) {
        thread.addLabel(processedLabel);
        
        // Calculate FY from the first message's date and apply FY label
        const firstMessageDate = messages[0].getDate();
        const fyName = getFinancialYear(firstMessageDate);
        const fyLabel = getOrCreateFYLabel(fyName);
        thread.addLabel(fyLabel);
        
        // Mark the thread as read
        thread.markRead();
        
        // NEW: Archive the thread to remove it from the inbox
        thread.moveToArchive();
      }
    }

    Logger.log('Process completed!');
    Logger.log('Emails processed: ' + totalEmailsProcessed);
    Logger.log('Attachments saved: ' + totalAttachmentsSaved);

    sendSummaryEmail(totalEmailsProcessed, totalAttachmentsSaved);

  } catch (error) {
    Logger.log('Error: ' + error.toString());
    throw error;
  }
}

/**
 * Get or create Gmail label for a specific FY
 * NEW: Helper to create/retrieve FY-specific labels (e.g., "Tax FY2024-2025")
 */
function getOrCreateFYLabel(fyName) {
  const labelName = CONFIG.fyLabelPrefix + fyName;
  return getOrCreateLabel(labelName);
}

/**
 * Build Gmail search query based on keywords and tax period (last July 1)
 */
function buildSearchQuery() {
  let query = 'has:attachment ';

  // Add keyword search (subject or body)
  const keywordQuery = CONFIG.searchKeywords.map(keyword =>
    '(subject:"' + keyword + '" OR "' + keyword + '")'
  ).join(' OR ');

  query += '(' + keywordQuery + ') ';
  query += '-label:' + CONFIG.processedLabelName + ' ';

  // Only "after:" July 1 of last full tax period (could be current or previous)
  const afterDate = getTaxPeriodStart();
  const afterStr = Utilities.formatDate(afterDate, Session.getScriptTimeZone(), 'yyyy/MM/dd');
  query += 'after:' + afterStr;

  return query;
}

/**
 * Get start date of the most recent July 1 tax period (e.g. July 1, 2024 if today is after July 1, 2025)
 */
function getTaxPeriodStart() {
  const now = new Date();
  const year = now.getFullYear()-1;
  const month = now.getMonth(); // 0=Jan, 6=July

  // If we are after July (new FY has started this year), use this July
  // If not yet July, use July last year
  return (month >= 6)
    ? new Date(year, 6, 1)    // July 1st current year
    : new Date(year - 1, 6, 1); // July 1st last year
}

/**
 * Get or create Gmail label
 */
function getOrCreateLabel(labelName) {
  let label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    label = GmailApp.createLabel(labelName);
    Logger.log('Created new label: ' + labelName);
  }
  return label;
}

/**
 * Get or create folder in Google Drive
 */
function getOrCreateFolder(folderName, parentFolder) {
  const parent = parentFolder || DriveApp.getRootFolder();
  const folders = parent.getFoldersByName(folderName);

  if (folders.hasNext()) {
    return folders.next();
  } else {
    const newFolder = parent.createFolder(folderName);
    Logger.log('Created new folder: ' + folderName);
    return newFolder;
  }
}

/**
 * Calculate Australian Financial Year from date
 */
function getFinancialYear(date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  if (month >= 6) {
    return 'FY' + year + '-' + (year + 1);
  } else {
    return 'FY' + (year - 1) + '-' + year;
  }
}

function getOrCreateFYFolder(parentFolder, emailDate) {
  const fyName = getFinancialYear(emailDate);
  return getOrCreateFolder(fyName, parentFolder);
}

function isAllowedFileType(attachment) {
  if (CONFIG.allowedFileTypes.length === 0) {
    return true;
  }
  const fileName = attachment.getName().toLowerCase();
  const fileExtension = fileName.substring(fileName.lastIndexOf('.') + 1);
  return CONFIG.allowedFileTypes.includes(fileExtension);
}

// ===== Logging Section (unchanged) =====

function getOrCreateLogSheet() {
  const files = DriveApp.getFilesByName(CONFIG.spreadsheetName);
  let ss;
  if (files.hasNext()) {
    const file = files.next();
    ss = SpreadsheetApp.open(file);
  } else {
    ss = SpreadsheetApp.create(CONFIG.spreadsheetName);
    try {
      const parentFolder = getOrCreateFolder(CONFIG.parentFolderName);
      const file = DriveApp.getFileById(ss.getId());
      parentFolder.addFile(file);
      DriveApp.getRootFolder().removeFile(file);
    } catch (err) {
      Logger.log('Could not move sheet: ' + err.toString());
    }
    const sheet = ss.getActiveSheet();
    sheet.appendRow(['Log Timestamp', 'Email Date', 'Sender', 'Subject', 'Attachment Name', 'Attachment Type', 'Saved File Name']);
  }
  return ss.getActiveSheet();
}

function logExtractedInvoice(emailDate, sender, subject, attachmentName, fileType, savedFileName) {
  const sheet = getOrCreateLogSheet();
  sheet.appendRow([
    Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss'),
    Utilities.formatDate(emailDate, Session.getScriptTimeZone(), 'yyyy-MM-dd'),
    sender,
    subject,
    attachmentName,
    fileType,
    savedFileName
  ]);
}

function saveAttachment(attachment, folder, message, emailDate) {
  try {
    const originalName = attachment.getName();
    const sender = extractEmailAddress(message.getFrom());
    const dateStr = Utilities.formatDate(emailDate, Session.getScriptTimeZone(), 'yyyy-MM-dd');
    const newFileName = dateStr + '_' + sender + '_' + originalName;
    const fileType = originalName.substring(originalName.lastIndexOf('.') + 1).toLowerCase();

    const existingFiles = folder.getFilesByName(newFileName);
    if (existingFiles.hasNext()) {
      Logger.log('File already exists, skipping: ' + newFileName);
      return;
    }

    const file = folder.createFile(attachment.copyBlob());
    file.setName(newFileName);
    file.setDescription('From: ' + message.getFrom() + '\nSubject: ' + message.getSubject() + '\nDate: ' + emailDate);

    logExtractedInvoice(emailDate, sender, message.getSubject(), originalName, fileType, newFileName);

    Logger.log('Saved: ' + newFileName);
  } catch (error) {
    Logger.log('Error saving attachment: ' + error.toString());
  }
}

function extractEmailAddress(fromField) {
  const emailMatch = fromField.match(/<(.+?)>/);
  if (emailMatch) {
    return emailMatch[1].replace(/[^a-zA-Z0-9@.-]/g, '_');
  }
  return fromField.replace(/[^a-zA-Z0-9@.-]/g, '_').substring(0, 30);
}

function sendSummaryEmail(emailsProcessed, attachmentsSaved) {
  const userEmail = Session.getActiveUser().getEmail();
  const subject = 'Invoice Extraction Complete - ' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const body = 'Invoice extraction process completed.\n\n' +
    'Emails processed: ' + emailsProcessed + '\n' +
    'Attachments saved: ' + attachmentsSaved + '\n\n' +
    'Check your Google Drive folder: ' + CONFIG.parentFolderName + '\n' +
    'Extraction Log: ' + CONFIG.spreadsheetName;
  GmailApp.sendEmail(userEmail, subject, body);
}

function createAutomationTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  ScriptApp.newTrigger('extractInvoiceAttachments')
    .timeBased()
    .atHour(2)
    .everyDays(1)
    .create();
  Logger.log('Automation trigger created - will run daily at 2 AM');
}

function testExtraction() {
  const originalMax = CONFIG.maxEmailsPerRun;
  CONFIG.maxEmailsPerRun = 5;
  extractInvoiceAttachments();
  CONFIG.maxEmailsPerRun = originalMax;
}
