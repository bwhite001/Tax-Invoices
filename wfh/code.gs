/**
 * IP-Based Location Tracker for Work Hours
 * Automatically detects location based on network IP address
 * No manual clicking required - fully automated
 */

// ===== CONFIGURATION =====
const CONFIG = {
  // Your network IP addresses or IP ranges
  locations: {
    home: {
      name: 'Home',
      // Add your home IP address(es) or partial match
      // Example: ['203.123.45.67', '203.123.45'] for range matching
      ipAddresses: ['122.199.0.209'],  // Replace with actual home IP
      // Optional: Add home network ISP name for additional verification
      ispKeywords: ['SuperLoop']  // Common Australian ISPs
    },
    office: {
      name: 'Office',
      // Add your office IP address(es) or partial match
      ipAddresses: ['YOUR_OFFICE_IP_HERE'],  // Replace with actual office IP
      // Optional: Add office network ISP/Company name
      ispKeywords: ['CompanyName', 'Office']
    }
  },
  
  // Business hours configuration
  businessHours: {
    startHour: 9,    // 9 AM
    endHour: 17,     // 5 PM (checks at 9, 12, 15 = every 3 hours)
    daysOfWeek: [1, 2, 3, 4, 5]  // Monday to Friday
  },
  
  // Check interval in hours
  checkInterval: 3,
  
  // Sheet name for logging
  sheetName: 'Location Log',
  
  // Timezone
  timezone: 'Australia/Sydney',
  
  // IP Geolocation API (free tier available)
  // Options: 'ipapi', 'ipify', 'ip-api' (no key required)
  geoApiService: 'ip-api'  // Free, no API key required
};

/**
 * Setup spreadsheet with headers and formatting
 */
function setupSpreadsheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(CONFIG.sheetName);
  }
  
  if (sheet.getLastRow() === 0) {
    const headers = [
      'Timestamp', 
      'Date', 
      'Time', 
      'Day', 
      'Location', 
      'IP Address', 
      'ISP/Provider',
      'City',
      'Region',
      'Method',
      'Notes'
    ];
    
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.getRange(1, 1, 1, headers.length)
      .setFontWeight('bold')
      .setBackground('#4285f4')
      .setFontColor('#ffffff');
    sheet.setFrozenRows(1);
    
    // Set column widths
    sheet.setColumnWidth(1, 180);  // Timestamp
    sheet.setColumnWidth(2, 100);  // Date
    sheet.setColumnWidth(3, 80);   // Time
    sheet.setColumnWidth(4, 100);  // Day
    sheet.setColumnWidth(5, 100);  // Location
    sheet.setColumnWidth(6, 120);  // IP
    sheet.setColumnWidth(7, 150);  // ISP
  }
  
  Logger.log('Spreadsheet setup complete!');
}

/**
 * Check if current time is within business hours
 */
function isBusinessHours() {
  const now = new Date();
  const day = now.getDay();
  const hour = now.getHours();
  
  if (!CONFIG.businessHours.daysOfWeek.includes(day)) {
    return false;
  }
  
  if (hour >= CONFIG.businessHours.startHour && hour < CONFIG.businessHours.endHour) {
    return true;
  }
  
  return false;
}

/**
 * Get IP address and location information using external API
 * This runs from Google's servers and gets YOUR IP when you access the web app
 */
function getIPLocationInfo(clientIP) {
  try {
    let data = {};
    
    if (CONFIG.geoApiService === 'ip-api') {
      // Using ip-api.com (free, no API key required, 45 requests/minute)
      const url = clientIP 
        ? `http://ip-api.com/json/${clientIP}` 
        : 'http://ip-api.com/json/';
      
      const response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
      const jsonData = JSON.parse(response.getContentText());
      
      if (jsonData.status === 'success') {
        data = {
          ip: jsonData.query,
          city: jsonData.city,
          region: jsonData.regionName,
          country: jsonData.country,
          isp: jsonData.isp,
          org: jsonData.org,
          timezone: jsonData.timezone
        };
      }
    } else if (CONFIG.geoApiService === 'ipapi') {
      // Using ipapi.co (free tier: 1000 requests/day, no key required)
      const url = clientIP 
        ? `https://ipapi.co/${clientIP}/json/` 
        : 'https://ipapi.co/json/';
      
      const response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
      const jsonData = JSON.parse(response.getContentText());
      
      data = {
        ip: jsonData.ip,
        city: jsonData.city,
        region: jsonData.region,
        country: jsonData.country_name,
        isp: jsonData.org,
        org: jsonData.org,
        timezone: jsonData.timezone
      };
    }
    
    return data;
  } catch (error) {
    Logger.log('Error fetching IP location: ' + error);
    return null;
  }
}

/**
 * Determine location based on IP address
 */
function determineLocationFromIP(ipData) {
  if (!ipData || !ipData.ip) {
    return {
      location: 'Unknown',
      matchType: 'none',
      confidence: 'low'
    };
  }
  
  const ip = ipData.ip;
  const isp = (ipData.isp || '').toLowerCase();
  
  // Check home IP
  for (let homeIP of CONFIG.locations.home.ipAddresses) {
    if (ip === homeIP || ip.startsWith(homeIP)) {
      return {
        location: 'Home',
        matchType: 'IP Match',
        confidence: 'high'
      };
    }
  }
  
  // Check office IP
  for (let officeIP of CONFIG.locations.office.ipAddresses) {
    if (ip === officeIP || ip.startsWith(officeIP)) {
      return {
        location: 'Office',
        matchType: 'IP Match',
        confidence: 'high'
      };
    }
  }
  
  // Fallback: Check ISP keywords for home
  for (let keyword of CONFIG.locations.home.ispKeywords) {
    if (isp.includes(keyword.toLowerCase())) {
      return {
        location: 'Home (ISP Match)',
        matchType: 'ISP Keyword',
        confidence: 'medium'
      };
    }
  }
  
  // Fallback: Check ISP keywords for office
  for (let keyword of CONFIG.locations.office.ispKeywords) {
    if (isp.includes(keyword.toLowerCase())) {
      return {
        location: 'Office (ISP Match)',
        matchType: 'ISP Keyword',
        confidence: 'medium'
      };
    }
  }
  
  // Unknown location
  return {
    location: 'Other/Unknown',
    matchType: 'No Match',
    confidence: 'low'
  };
}

/**
 * Log location to spreadsheet
 */
function logLocationToSheet(ipData, locationInfo, notes = '') {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.sheetName);
  
  if (!sheet) {
    setupSpreadsheet();
    sheet = ss.getSheetByName(CONFIG.sheetName);
  }
  
  const now = new Date();
  
  const rowData = [
    now,
    Utilities.formatDate(now, CONFIG.timezone, 'yyyy-MM-dd'),
    Utilities.formatDate(now, CONFIG.timezone, 'HH:mm:ss'),
    Utilities.formatDate(now, CONFIG.timezone, 'EEEE'),
    locationInfo.location,
    ipData.ip || 'N/A',
    ipData.isp || 'N/A',
    ipData.city || 'N/A',
    ipData.region || 'N/A',
    locationInfo.matchType,
    notes
  ];
  
  sheet.appendRow(rowData);
  
  // Color code based on location
  const lastRow = sheet.getLastRow();
  const range = sheet.getRange(lastRow, 1, 1, 11);
  
  if (locationInfo.location.includes('Home')) {
    range.setBackground('#d9ead3');  // Green for home
  } else if (locationInfo.location.includes('Office')) {
    range.setBackground('#cfe2f3');  // Blue for office
  } else {
    range.setBackground('#fff2cc');  // Yellow for unknown
  }
  
  Logger.log(`Location logged: ${locationInfo.location} from IP: ${ipData.ip}`);
}

/**
 * Main function called by time trigger
 * This is what runs automatically every 3 hours
 */
function automaticLocationCheck() {
  // Only log during business hours
  if (!isBusinessHours()) {
    Logger.log('Outside business hours - skipping location check');
    return;
  }
  
  // Deploy the web app and visit it automatically
  // This function sends you an email with a link to click
  sendLocationCheckEmail();
}

/**
 * Send email with link to check location
 */
function sendLocationCheckEmail() {
  const webAppUrl = ScriptApp.getService().getUrl();
  const userEmail = Session.getActiveUser().getEmail();
  
  const subject = '📍 Location Check Required';
  const htmlBody = `
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Automatic Location Check</h2>
        <p>Please click the button below to log your current location:</p>
        <p style="margin: 20px 0;">
          <a href="${webAppUrl}" 
             style="background-color: #4285f4; color: white; padding: 12px 24px; 
                    text-decoration: none; border-radius: 4px; display: inline-block;">
            📍 Log My Location
          </a>
        </p>
        <p style="color: #666; font-size: 12px;">
          Or copy this URL: ${webAppUrl}
        </p>
        <p style="color: #666; font-size: 12px;">
          Tip: Bookmark this link for quick access in the future!
        </p>
      </body>
    </html>
  `;
  
  GmailApp.sendEmail(userEmail, subject, 'Click the link to log your location', {
    htmlBody: htmlBody
  });
  
  Logger.log('Location check email sent');
}

/**
 * Web App - HTML interface that automatically detects IP
 */
function doGet() {
  return HtmlService.createHtmlOutputFromFile('IPLocationTracker.html')
    .setTitle('IP Location Tracker')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Handle automatic location detection from web app
 */
function handleAutomaticLocationCheck(clientIPData) {
  if (!isBusinessHours()) {
    return {
      success: false,
      message: 'Outside business hours (Mon-Fri, 9AM-5PM)',
      businessHours: false
    };
  }
  
  const ipData = clientIPData || getIPLocationInfo();
  const locationInfo = determineLocationFromIP(ipData);
  
  logLocationToSheet(ipData, locationInfo, 'Automatic check');
  
  return {
    success: true,
    message: 'Location logged successfully!',
    location: locationInfo.location,
    ip: ipData.ip,
    isp: ipData.isp,
    city: ipData.city,
    matchType: locationInfo.matchType,
    confidence: locationInfo.confidence,
    timestamp: new Date().toString(),
    businessHours: true
  };
}

/**
 * Create time-based triggers for automatic checks every 3 hours
 */
function createAutomaticTriggers() {
  // Delete existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'automaticLocationCheck') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Calculate check times (every 3 hours during business hours)
  const checkHours = [];
  for (let hour = CONFIG.businessHours.startHour; 
       hour < CONFIG.businessHours.endHour; 
       hour += CONFIG.checkInterval) {
    checkHours.push(hour);
  }
  
  Logger.log('Creating triggers for hours: ' + checkHours.join(', '));
  
  // Create triggers for each check time on weekdays
  checkHours.forEach(hour => {
    CONFIG.businessHours.daysOfWeek.forEach(day => {
      ScriptApp.newTrigger('automaticLocationCheck')
        .timeBased()
        .onWeekDay(getDayEnum(day))
        .atHour(hour)
        .create();
    });
  });
  
  const totalTriggers = checkHours.length * CONFIG.businessHours.daysOfWeek.length;
  Logger.log(`Created ${totalTriggers} automatic location check triggers`);
  Logger.log(`Will check at: ${checkHours.join(', ')} on weekdays`);
}

/**
 * Convert day number to enum
 */
function getDayEnum(dayNum) {
  const days = [
    ScriptApp.WeekDay.SUNDAY,
    ScriptApp.WeekDay.MONDAY,
    ScriptApp.WeekDay.TUESDAY,
    ScriptApp.WeekDay.WEDNESDAY,
    ScriptApp.WeekDay.THURSDAY,
    ScriptApp.WeekDay.FRIDAY,
    ScriptApp.WeekDay.SATURDAY
  ];
  return days[dayNum];
}

/**
 * Get current IP information (for testing)
 */
function testGetMyIP() {
  const ipData = getIPLocationInfo();
  Logger.log('Your current IP info:');
  Logger.log(JSON.stringify(ipData, null, 2));
  return ipData;
}

/**
 * Test location determination
 */
function testLocationDetection() {
  const ipData = getIPLocationInfo();
  const locationInfo = determineLocationFromIP(ipData);
  
  Logger.log('IP Data: ' + JSON.stringify(ipData, null, 2));
  Logger.log('Location: ' + locationInfo.location);
  Logger.log('Match Type: ' + locationInfo.matchType);
  Logger.log('Confidence: ' + locationInfo.confidence);
}

/**
 * Delete all triggers
 */
function deleteAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  Logger.log('All triggers deleted');
}

/**
 * Get location statistics
 */
function getLocationStatistics() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.sheetName);
  
  if (!sheet || sheet.getLastRow() <= 1) {
    Logger.log('No data available');
    return;
  }
  
  const data = sheet.getRange(2, 5, sheet.getLastRow() - 1, 1).getValues();
  
  let stats = {
    home: 0,
    office: 0,
    other: 0,
    total: 0
  };
  
  data.forEach(row => {
    const location = row[0].toString().toLowerCase();
    stats.total++;
    
    if (location.includes('home')) {
      stats.home++;
    } else if (location.includes('office')) {
      stats.office++;
    } else {
      stats.other++;
    }
  });
  
  stats.homePercentage = ((stats.home / stats.total) * 100).toFixed(1);
  stats.officePercentage = ((stats.office / stats.total) * 100).toFixed(1);
  
  Logger.log('Location Statistics:');
  Logger.log(`Total checks: ${stats.total}`);
  Logger.log(`Home: ${stats.home} (${stats.homePercentage}%)`);
  Logger.log(`Office: ${stats.office} (${stats.officePercentage}%)`);
  Logger.log(`Other: ${stats.other}`);
  
  return stats;
}
