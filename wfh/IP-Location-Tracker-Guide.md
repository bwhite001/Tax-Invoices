# IP-Based Location Tracker - Setup & Usage Guide

## 📋 Overview

The **IP-Based Location Tracker** is a Google Apps Script that automatically tracks your work location (Home/Office) based on your network IP address. Perfect for work-from-home arrangements, it logs your location during business hours without requiring manual input.

### What It Does

- 🌐 **Detects Location** automatically using your network IP address
- 📊 **Logs to Google Sheets** with color-coded entries
- ⏰ **Automated Checks** every 3 hours during business hours (Mon-Fri, 9AM-5PM)
- 🌍 **IP Geolocation** using free APIs (no API key required)
- 📈 **Statistics** showing home vs office percentages
- 🎨 **Color Coding**: Green for Home, Blue for Office, Yellow for Unknown

### Why Use This?

- **WFH Compliance**: Automatic tracking for work-from-home policies
- **Tax Records**: Document home office usage for tax deductions
- **Time Tracking**: Prove where you worked for billing/compliance
- **No Manual Entry**: Set it and forget it
- **Privacy Friendly**: Only tracks during business hours

---

## ✨ Features

### Core Functionality
- Automatic IP address detection using geolocation APIs
- Matches IP addresses to configured locations (Home/Office)
- Fallback ISP keyword matching for additional verification
- Business hours filtering (Mon-Fri, 9AM-5PM configurable)
- Web app interface for manual location checks

### Smart Detection
- **Exact IP Match**: Matches your configured IP addresses
- **IP Range Match**: Supports partial IP matching (e.g., `203.123.45`)
- **ISP Keyword Match**: Falls back to ISP name matching
- **Confidence Levels**: High (IP match), Medium (ISP match), Low (unknown)

### Logging & Tracking
- Creates/updates "Location Log" spreadsheet
- Logs: timestamp, date, time, day, location, IP, ISP, city, region
- Color-coded rows: Green (Home), Blue (Office), Yellow (Unknown)
- Frozen header row for easy scrolling
- Automatic column width formatting

### Automation
- Triggers every 3 hours during business hours
- Sends email with link to check location
- Web app automatically detects and logs location
- Configurable check intervals and business hours

### Statistics & Reporting
- Calculate home vs office percentages
- Total check counts
- Location distribution analysis
- Easy export for reporting

---

## 📋 Prerequisites

Before setting up the script, ensure you have:

1. **Google Account** with Gmail and Google Sheets access
2. **Your IP Addresses**:
   - Home network IP address
   - Office network IP address (if applicable)
3. **Basic understanding** of Google Apps Script (helpful but not required)
4. **10-15 minutes** for initial setup

### Finding Your IP Address

**Method 1: Quick Check**
1. Visit [whatismyipaddress.com](https://whatismyipaddress.com)
2. Note your IPv4 address (e.g., `203.123.45.67`)

**Method 2: Using the Script**
1. Set up the script (follow setup instructions)
2. Run the `testGetMyIP` function
3. Check the execution log for your IP details

---

## 🚀 Setup Instructions

### Step 1: Create the Google Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **"New project"**
3. Name your project: `IP Location Tracker`
4. Delete the default `function myFunction() {}` code

### Step 2: Add the Script Code

1. Copy the entire contents of `code.gs`
2. Paste it into the script editor
3. Click the **Save** icon (💾) or press `Ctrl+S` / `Cmd+S`

### Step 3: Add the HTML File

1. Click the **+** icon next to "Files"
2. Select **HTML**
3. Name it: `IPLocationTracker`
4. Copy the HTML code (see HTML section below)
5. Paste and save

### Step 4: Configure Your IP Addresses

Edit the `CONFIG` object at the top of `code.gs`:

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['YOUR_HOME_IP_HERE'],  // Replace with your actual home IP
      ispKeywords: ['SuperLoop', 'Telstra', 'Optus']  // Your home ISP
    },
    office: {
      name: 'Office',
      ipAddresses: ['YOUR_OFFICE_IP_HERE'],  // Replace with your actual office IP
      ispKeywords: ['CompanyName', 'Office']  // Your office ISP/company name
    }
  },
  
  businessHours: {
    startHour: 9,    // 9 AM
    endHour: 17,     // 5 PM
    daysOfWeek: [1, 2, 3, 4, 5]  // Monday to Friday
  },
  
  checkInterval: 3,  // Check every 3 hours
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'  // Free, no API key required
};
```

**Important**: Replace `YOUR_HOME_IP_HERE` and `YOUR_OFFICE_IP_HERE` with your actual IP addresses!

### Step 5: Set Up the Spreadsheet

1. Select `setupSpreadsheet` from the function dropdown
2. Click **Run** (▶️)
3. Grant permissions when prompted
4. A new sheet called "Location Log" will be created

### Step 6: Test IP Detection

1. Select `testGetMyIP` from the function dropdown
2. Click **Run** (▶️)
3. Check **View** → **Logs** to see your current IP info
4. Verify it matches your expected location

### Step 7: Deploy the Web App

1. Click **Deploy** → **New deployment**
2. Click the gear icon ⚙️ next to "Select type"
3. Choose **Web app**
4. Configure:
   - **Description**: IP Location Tracker
   - **Execute as**: Me
   - **Who has access**: Only myself
5. Click **Deploy**
6. Copy the **Web app URL** (you'll need this!)
7. Click **Done**

### Step 8: Test the Web App

1. Open the Web app URL in your browser
2. Click **"Check My Location Now"**
3. Verify the detected location is correct
4. Check the "Location Log" sheet for the entry

### Step 9: Set Up Automation

1. Select `createAutomaticTriggers` from the function dropdown
2. Click **Run** (▶️)
3. The script will create triggers for automated checks

**Triggers Created:**
- Checks at 9 AM, 12 PM, 3 PM on weekdays
- Sends email with link to check location
- You click the link, location is automatically logged

---

## ⚙️ Configuration Options Explained

### Location Configuration

```javascript
locations: {
  home: {
    name: 'Home',
    ipAddresses: ['203.123.45.67', '203.123.45'],  // Exact or partial match
    ispKeywords: ['SuperLoop', 'Telstra']  // ISP name fallback
  }
}
```

**IP Address Matching:**
- **Exact Match**: `'203.123.45.67'` - matches only this IP
- **Range Match**: `'203.123.45'` - matches any IP starting with this
- **Multiple IPs**: Add multiple addresses if your IP changes

**ISP Keywords:**
- Used as fallback if IP doesn't match
- Matches against ISP/organization name from geolocation API
- Case-insensitive matching

### Business Hours Configuration

```javascript
businessHours: {
  startHour: 9,    // Start checking at 9 AM
  endHour: 17,     // Stop checking at 5 PM
  daysOfWeek: [1, 2, 3, 4, 5]  // 0=Sunday, 1=Monday, ..., 6=Saturday
}
```

**Customization Examples:**
- **4-day work week**: `daysOfWeek: [1, 2, 3, 4]` (Mon-Thu)
- **Weekend work**: `daysOfWeek: [0, 6]` (Sat-Sun)
- **Extended hours**: `startHour: 8, endHour: 18` (8AM-6PM)

### Check Interval

```javascript
checkInterval: 3  // Check every 3 hours
```

**Options:**
- `1` = Every hour (9AM, 10AM, 11AM, ...)
- `2` = Every 2 hours (9AM, 11AM, 1PM, ...)
- `3` = Every 3 hours (9AM, 12PM, 3PM)
- `4` = Every 4 hours (9AM, 1PM, 5PM)

### Geolocation API Service

```javascript
geoApiService: 'ip-api'  // or 'ipapi'
```

**Available Services:**
- **`ip-api`**: Free, 45 requests/minute, no API key required
- **`ipapi`**: Free tier 1000 requests/day, no API key required

Both services provide: IP address, city, region, country, ISP, timezone

### Timezone

```javascript
timezone: 'Australia/Sydney'
```

**Common Australian Timezones:**
- `'Australia/Sydney'` - NSW, VIC, TAS, ACT
- `'Australia/Brisbane'` - QLD
- `'Australia/Adelaide'` - SA
- `'Australia/Perth'` - WA
- `'Australia/Darwin'` - NT

---

## 📖 Usage Guide

### Automated Location Tracking

Once set up, the system works automatically:

1. **Trigger Fires**: At 9 AM, 12 PM, 3 PM on weekdays
2. **Email Sent**: You receive an email with a link
3. **Click Link**: Opens the web app
4. **Auto-Detect**: Location is automatically detected and logged
5. **Confirmation**: You see the result on screen

**Email Example:**
```
Subject: 📍 Location Check Required

Please click the button below to log your current location:
[📍 Log My Location]

Or copy this URL: https://script.google.com/...
```

### Manual Location Check

To check your location manually:

1. Open the Web app URL (bookmark it!)
2. Click **"Check My Location Now"**
3. View the detected location
4. Check the spreadsheet for the log entry

### Viewing the Location Log

Open your Google Sheets and find "Location Log":

| Timestamp | Date | Time | Day | Location | IP Address | ISP/Provider | City | Region | Method | Notes |
|-----------|------|------|-----|----------|------------|--------------|------|--------|--------|-------|
| 2024-12-15 09:00:00 | 2024-12-15 | 09:00:00 | Monday | Home | 203.123.45.67 | SuperLoop | Sydney | NSW | IP Match | Automatic check |

**Color Coding:**
- 🟢 **Green Background**: Home location
- 🔵 **Blue Background**: Office location
- 🟡 **Yellow Background**: Unknown/Other location

### Getting Location Statistics

1. Select `getLocationStatistics` from the function dropdown
2. Click **Run** (▶️)
3. Check **View** → **Logs** for results

**Example Output:**
```
Location Statistics:
Total checks: 45
Home: 30 (66.7%)
Office: 12 (26.7%)
Other: 3 (6.7%)
```

### Exporting Data

To export for reporting:

1. Open the "Location Log" spreadsheet
2. Click **File** → **Download** → **CSV** or **Excel**
3. Use for tax records, compliance, or billing

---

## 🔧 How It Works

### Workflow Overview

1. **Trigger Fires**: Time-based trigger activates during business hours
2. **Email Sent**: Script sends you an email with web app link
3. **User Clicks**: You click the link (can be automated with email filters)
4. **Web App Opens**: HTML interface loads in browser
5. **IP Detection**: JavaScript calls geolocation API
6. **Data Sent**: IP info sent back to Google Apps Script
7. **Location Match**: Script compares IP to configured locations
8. **Log Entry**: Creates spreadsheet row with color coding
9. **Confirmation**: Shows result to user

### IP Detection Process

```
1. Get Public IP → 2. Query Geolocation API → 3. Receive IP Data
                                                    ↓
                                            (IP, ISP, City, Region)
                                                    ↓
4. Match Against Config ← 5. Check IP Addresses ← 6. Check ISP Keywords
                                                    ↓
                                            7. Determine Location
                                                    ↓
                                            8. Assign Confidence Level
                                                    ↓
                                            9. Log to Spreadsheet
```

### Location Matching Logic

**Priority Order:**
1. **Exact IP Match** → High confidence
2. **IP Range Match** → High confidence
3. **ISP Keyword Match** → Medium confidence
4. **No Match** → Low confidence (logged as "Other/Unknown")

**Example:**
```javascript
Your IP: 203.123.45.67
Your ISP: SuperLoop

Config Home IP: ['203.123.45.67']
Result: ✅ Home (IP Match) - High Confidence

Config Home IP: ['203.123.45']
Result: ✅ Home (IP Match) - High Confidence

Config Home IP: ['192.168.1.1']
Config Home ISP: ['SuperLoop']
Result: ✅ Home (ISP Match) - Medium Confidence

Config Home IP: ['192.168.1.1']
Config Home ISP: ['Telstra']
Result: ❌ Other/Unknown - Low Confidence
```

### Business Hours Filtering

The script only logs during configured business hours:

```javascript
// Example: Mon-Fri, 9AM-5PM
if (day is Monday-Friday AND hour is 9-16) {
  → Log location
} else {
  → Skip (outside business hours)
}
```

This ensures:
- No tracking outside work hours
- Privacy during personal time
- Accurate work location records

---

## 🔒 Privacy & Security

### What Data Is Collected

- **IP Address**: Your public IP address
- **Location Data**: City, region, country (from IP)
- **ISP Information**: Internet service provider name
- **Timestamp**: When the check occurred
- **Match Method**: How location was determined

### What Is NOT Collected

- ❌ Precise GPS coordinates
- ❌ Device information
- ❌ Browsing history
- ❌ Personal files or data
- ❌ Continuous tracking

### Data Storage

- All data stored in YOUR Google Sheets
- No external databases
- No third-party data sharing
- You control all data

### Privacy Best Practices

1. **Limit Business Hours**: Only track during work hours
2. **Review Logs**: Regularly check what's being logged
3. **Secure Spreadsheet**: Don't share the log sheet publicly
4. **Use Work Account**: Consider using work Google account
5. **Disable When Not Needed**: Delete triggers when not working

### IP Address Privacy

**Important Notes:**
- IP addresses can change (especially home connections)
- Dynamic IPs may require periodic config updates
- VPNs will show VPN server location, not your actual location
- Mobile hotspots will show mobile carrier location

---

## 🐛 Troubleshooting

### Common Issues

#### "Wrong location detected"
**Problem**: Script shows Office when you're at Home (or vice versa)
**Solution**:
1. Run `testGetMyIP` to see your current IP
2. Verify the IP matches your config
3. Update `ipAddresses` in CONFIG if your IP changed
4. Check ISP keywords are correct

#### "Location shows as Unknown"
**Problem**: Neither Home nor Office is detected
**Solution**:
1. Check your current IP with `testGetMyIP`
2. Add the IP to your config
3. Verify ISP keywords match your provider
4. Consider using IP range matching (partial IP)

#### "No email received"
**Problem**: Trigger fires but no email arrives
**Solution**:
1. Check Gmail spam folder
2. Verify trigger is created (click Triggers icon ⏰)
3. Check execution log for errors
4. Ensure `automaticLocationCheck` function exists

#### "Web app shows error"
**Problem**: Clicking link shows error page
**Solution**:
1. Redeploy the web app
2. Ensure HTML file is named `IPLocationTracker`
3. Check deployment settings (Execute as: Me)
4. Try opening in incognito mode

#### "Geolocation API fails"
**Problem**: Can't detect IP or location
**Solution**:
1. Try switching API service (`ip-api` ↔ `ipapi`)
2. Check internet connection
3. Verify API rate limits not exceeded
4. Wait a few minutes and try again

#### "Spreadsheet not created"
**Problem**: Can't find "Location Log" sheet
**Solution**:
1. Run `setupSpreadsheet` function manually
2. Check for errors in execution log
3. Verify permissions granted
4. Look in all your Google Sheets

#### "Triggers not working"
**Problem**: Automated checks not happening
**Solution**:
1. Click Triggers icon (⏰) to verify triggers exist
2. Check trigger execution history for errors
3. Delete and recreate triggers with `createAutomaticTriggers`
4. Ensure business hours config is correct

### Checking Execution History

1. Open your script
2. Click **Executions** icon (📋) in left sidebar
3. Review recent executions
4. Click on any execution to see detailed logs
5. Look for errors in red

### Testing Functions

**Test IP Detection:**
```javascript
testGetMyIP()  // Shows your current IP info
```

**Test Location Matching:**
```javascript
testLocationDetection()  // Shows how your IP is matched
```

**Test Manual Check:**
```javascript
handleAutomaticLocationCheck()  // Simulates a location check
```

---

## 🎨 Customization Tips

### Adding More Locations

Add a third location (e.g., Co-working space):

```javascript
locations: {
  home: { /* ... */ },
  office: { /* ... */ },
  coworking: {
    name: 'Co-working Space',
    ipAddresses: ['COWORKING_IP_HERE'],
    ispKeywords: ['CoworkingISP']
  }
}
```

Then update `determineLocationFromIP()` to check this location.

### Custom Business Hours

**Part-time schedule (Mon/Wed/Fri):**
```javascript
businessHours: {
  startHour: 9,
  endHour: 17,
  daysOfWeek: [1, 3, 5]  // Monday, Wednesday, Friday
}
```

**Night shift (6PM-2AM):**
```javascript
businessHours: {
  startHour: 18,  // 6 PM
  endHour: 26,    // 2 AM next day (use 24+ for next day)
  daysOfWeek: [1, 2, 3, 4, 5]
}
```

### More Frequent Checks

Check every hour instead of every 3 hours:

```javascript
checkInterval: 1  // Every hour
```

Then recreate triggers:
```javascript
deleteAllTriggers()
createAutomaticTriggers()
```

### Custom Email Template

Modify `sendLocationCheckEmail()`:

```javascript
const subject = '🏠 Time to Log Your Location!';
const htmlBody = `
  <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
      <div style="background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4285f4;">📍 Location Check</h2>
        <p>Hi there! It's time for your automated location check.</p>
        <p style="margin: 30px 0;">
          <a href="${webAppUrl}" 
             style="background-color: #34a853; color: white; padding: 15px 30px; 
                    text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
            Check My Location
          </a>
        </p>
        <p style="color: #666; font-size: 14px;">
          This automated check helps track your work location for compliance and tax purposes.
        </p>
      </div>
    </body>
  </html>
`;
```

### Adding Notes/Comments

Modify `logLocationToSheet()` to add custom notes:

```javascript
const notes = isBusinessHours() ? 'Automatic check' : 'Manual check';
// Or add more context:
const notes = `Checked via ${locationInfo.matchType} at ${new Date().toLocaleTimeString()}`;
```

### Slack/Teams Integration

Send notifications to Slack instead of email:

```javascript
function sendSlackNotification(location, ip) {
  const webhookUrl = 'YOUR_SLACK_WEBHOOK_URL';
  const payload = {
    text: `📍 Location logged: ${location} from IP ${ip}`
  };
  
  UrlFetchApp.fetch(webhookUrl, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  });
}
```

### Automatic Email Click

Use Gmail filters to automatically open the link:
1. Create filter for subject "Location Check Required"
2. Forward to a service like IFTTT or Zapier
3. Configure to automatically visit the URL

---

## 📊 Best Practices

### Initial Setup
1. Test IP detection with `testGetMyIP` first
2. Verify location matching with `testLocationDetection`
3. Do a manual web app check before automation
4. Monitor first few automated checks
5. Adjust config as needed

### Regular Maintenance
- Update IP addresses when they change
- Review logs weekly for accuracy
- Check trigger execution history monthly
- Update ISP keywords if provider changes

### For Tax/Compliance
- Keep logs for entire financial year
- Export to CSV monthly for backup
- Document any manual corrections
- Include in tax records with other WFH evidence

### Accuracy Tips
- Use IP range matching for dynamic IPs
- Add multiple ISP keywords for reliability
- Check logs regularly for "Unknown" entries
- Update config when changing networks

### Privacy Considerations
- Only enable during work hours
- Disable triggers when on leave
- Don't share spreadsheet publicly
- Review what data is being logged

---

## 📝 Summary

The IP-Based Location Tracker provides automated, privacy-friendly work location tracking using network IP addresses. Perfect for work-from-home arrangements, tax documentation, and compliance requirements.

**Key Benefits:**
- 🤖 Fully automated tracking
- 🏠 Accurate home/office detection
- 📊 Easy reporting and statistics
- 🔒 Privacy-focused (business hours only)
- 💰 Free to use (no API costs)

**Perfect For:**
- Remote workers tracking WFH days
- Tax deductions for home office
- Compliance with WFH policies
- Billing/timesheet verification
- Location-based reporting

**Next Steps:**
1. Complete setup following this guide
2. Configure your IP addresses
3. Test detection accuracy
4. Deploy web app
5. Set up automation
6. Monitor first week of logs
7. Adjust config as needed

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Run test functions to diagnose
3. Review execution logs for errors
4. Verify configuration settings
5. Test with manual web app check

**Common Test Functions:**
- `testGetMyIP()` - See your current IP
- `testLocationDetection()` - Test location matching
- `getLocationStatistics()` - View statistics
- `setupSpreadsheet()` - Recreate log sheet

**Script Version**: 1.0  
**Last Updated**: December 2024  
**Compatible With**: Google Apps Script, Google Sheets  
**API Services**: ip-api.com, ipapi.co (free tiers)
