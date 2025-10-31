# wfh - Parameters Reference

Complete parameter documentation for the Work-From-Home Location Tracking module.

---

## 📋 Table of Contents

- [Configuration Object](#configuration-object)
- [Location Parameters](#location-parameters)
- [Business Hours Parameters](#business-hours-parameters)
- [Tracking Parameters](#tracking-parameters)
- [API Parameters](#api-parameters)
- [Functions](#functions)
- [Examples](#examples)

---

## ⚙️ Configuration Object

**Location**: `wfh/code.gs`

All parameters are defined in the `CONFIG` object at the top of the script.

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['YOUR_HOME_IP_HERE'],
      ispKeywords: ['SuperLoop', 'Telstra', 'Optus']
    },
    office: {
      name: 'Office',
      ipAddresses: ['YOUR_OFFICE_IP_HERE'],
      ispKeywords: ['CompanyName', 'Office']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

---

## 📍 Location Parameters

### locations.home

#### name

```javascript
name: 'Home'
```

- **Type**: String
- **Default**: `'Home'`
- **Description**: Display name for home location
- **Required**: Yes

**When to change**:
- Different naming preference
- Multiple home locations

**Examples**:
```javascript
name: 'Home'
name: 'Home Office'
name: 'Remote'
```

#### ipAddresses

```javascript
ipAddresses: ['YOUR_HOME_IP_HERE']
```

- **Type**: Array of strings (IP addresses)
- **Default**: `['YOUR_HOME_IP_HERE']` (MUST CONFIGURE)
- **Description**: Home IP addresses for matching
- **Required**: Yes
- **Format**: IPv4 addresses (exact or partial)

**When to change**:
- **CRITICAL**: Must set your actual home IP
- IP address changes
- Multiple home IPs
- IP range matching

**Examples**:
```javascript
// Exact IP match
ipAddresses: ['203.123.45.67']

// IP range match (matches 203.123.45.*)
ipAddresses: ['203.123.45']

// Multiple IPs
ipAddresses: ['203.123.45.67', '203.123.45.68']

// Multiple ranges
ipAddresses: ['203.123.45', '203.123.46']
```

**Finding Your IP**:
1. Visit [whatismyipaddress.com](https://whatismyipaddress.com)
2. Note your IPv4 address
3. Or run `testGetMyIP()` function

**IP Matching Logic**:
- **Exact match**: `'203.123.45.67'` matches only `203.123.45.67`
- **Range match**: `'203.123.45'` matches any IP starting with `203.123.45`
- **First match wins**: Checks in order

#### ispKeywords

```javascript
ispKeywords: ['SuperLoop', 'Telstra', 'Optus']
```

- **Type**: Array of strings
- **Default**: `['SuperLoop', 'Telstra', 'Optus']`
- **Description**: ISP keywords for fallback matching
- **Required**: No (but recommended)
- **Case-insensitive**: Yes

**When to change**:
- Add your actual ISP
- Multiple ISPs
- Improve accuracy

**Examples**:
```javascript
// Australian ISPs
ispKeywords: ['SuperLoop', 'Telstra', 'Optus', 'TPG', 'Aussie Broadband']

// Single ISP
ispKeywords: ['SuperLoop']

// Company ISP
ispKeywords: ['NBN Co', 'Telstra Business']
```

**ISP Matching**:
- Used if IP doesn't match
- Checks ISP/organization name from geolocation API
- Lower confidence than IP match

### locations.office

Same parameters as `locations.home`:

```javascript
office: {
  name: 'Office',
  ipAddresses: ['YOUR_OFFICE_IP_HERE'],  // MUST CONFIGURE
  ispKeywords: ['CompanyName', 'Office']
}
```

**When to configure**:
- **CRITICAL**: Must set your actual office IP
- If you work from office
- If tracking office days

**Examples**:
```javascript
// Standard office
office: {
  name: 'Office',
  ipAddresses: ['192.168.1.100'],
  ispKeywords: ['CompanyName', 'Corporate']
}

// Co-working space
office: {
  name: 'Co-working',
  ipAddresses: ['203.45.67.89'],
  ispKeywords: ['WeWork', 'Spaces']
}

// No office (full remote)
office: {
  name: 'Office',
  ipAddresses: [],  // Empty
  ispKeywords: []
}
```

---

## ⏰ Business Hours Parameters

### startHour

```javascript
startHour: 9
```

- **Type**: Integer (0-23)
- **Default**: `9` (9 AM)
- **Description**: Business hours start time (24-hour format)
- **Range**: 0-23
- **Required**: Yes

**When to change**:
- Different work schedule
- Flexible hours
- Shift work

**Examples**:
```javascript
// Standard (9 AM - 5 PM)
startHour: 9

// Early start (7 AM)
startHour: 7

// Late start (10 AM)
startHour: 10

// Night shift (6 PM)
startHour: 18
```

### endHour

```javascript
endHour: 17
```

- **Type**: Integer (0-23)
- **Default**: `17` (5 PM)
- **Description**: Business hours end time (24-hour format)
- **Range**: 0-23
- **Required**: Yes

**When to change**:
- Different work schedule
- Extended hours
- Shift work

**Examples**:
```javascript
// Standard (9 AM - 5 PM)
endHour: 17

// Extended (9 AM - 6 PM)
endHour: 18

// Early finish (9 AM - 3 PM)
endHour: 15

// Night shift (6 PM - 2 AM)
endHour: 26  // Use 24+ for next day
```

**Note**: For shifts crossing midnight, use 24+ for next day hours.

### daysOfWeek

```javascript
daysOfWeek: [1, 2, 3, 4, 5]
```

- **Type**: Array of integers (0-6)
- **Default**: `[1, 2, 3, 4, 5]` (Monday-Friday)
- **Description**: Working days of the week
- **Range**: 0=Sunday, 1=Monday, ..., 6=Saturday
- **Required**: Yes

**When to change**:
- Part-time schedule
- Weekend work
- Compressed work week

**Examples**:
```javascript
// Standard (Mon-Fri)
daysOfWeek: [1, 2, 3, 4, 5]

// 4-day week (Mon-Thu)
daysOfWeek: [1, 2, 3, 4]

// Part-time (Mon, Wed, Fri)
daysOfWeek: [1, 3, 5]

// Weekend work (Sat-Sun)
daysOfWeek: [0, 6]

// 6-day week (Mon-Sat)
daysOfWeek: [1, 2, 3, 4, 5, 6]

// Every day
daysOfWeek: [0, 1, 2, 3, 4, 5, 6]
```

**Day Numbers**:
- 0 = Sunday
- 1 = Monday
- 2 = Tuesday
- 3 = Wednesday
- 4 = Thursday
- 5 = Friday
- 6 = Saturday

---

## 📊 Tracking Parameters

### checkInterval

```javascript
checkInterval: 3
```

- **Type**: Integer (hours)
- **Default**: `3`
- **Description**: Hours between automated checks
- **Range**: 1-8
- **Required**: Yes

**When to change**:
- More frequent tracking
- Less frequent tracking
- Battery/data concerns

**Examples**:
```javascript
// Every hour
checkInterval: 1
// Checks: 9 AM, 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM, 4 PM, 5 PM

// Every 2 hours
checkInterval: 2
// Checks: 9 AM, 11 AM, 1 PM, 3 PM, 5 PM

// Every 3 hours (default)
checkInterval: 3
// Checks: 9 AM, 12 PM, 3 PM

// Every 4 hours
checkInterval: 4
// Checks: 9 AM, 1 PM, 5 PM
```

**Considerations**:
- More frequent = more accurate
- Less frequent = less intrusive
- Triggers created based on this interval

### sheetName

```javascript
sheetName: 'Location Log'
```

- **Type**: String
- **Default**: `'Location Log'`
- **Description**: Name of Google Sheets log
- **Required**: Yes
- **Auto-created**: Yes

**When to change**:
- Different sheet name
- Multiple tracking sheets
- Organization preference

**Examples**:
```javascript
sheetName: 'Location Log'
sheetName: 'WFH Tracker'
sheetName: 'Work Location'
sheetName: 'Attendance Log'
```

---

## 🌍 API Parameters

### timezone

```javascript
timezone: 'Australia/Sydney'
```

- **Type**: String
- **Default**: `'Australia/Sydney'`
- **Description**: Timezone for logging
- **Required**: Yes
- **Format**: IANA timezone identifier

**When to change**:
- Different location
- Different state
- Traveling

**Australian Timezones**:
```javascript
// NSW, VIC, TAS, ACT
timezone: 'Australia/Sydney'

// QLD
timezone: 'Australia/Brisbane'

// SA
timezone: 'Australia/Adelaide'

// WA
timezone: 'Australia/Perth'

// NT
timezone: 'Australia/Darwin'

// Lord Howe Island
timezone: 'Australia/Lord_Howe'
```

**Other Timezones**:
```javascript
// New Zealand
timezone: 'Pacific/Auckland'

// Singapore
timezone: 'Asia/Singapore'

// UK
timezone: 'Europe/London'

// US Eastern
timezone: 'America/New_York'
```

**Finding Your Timezone**:
- [List of IANA timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- Use your city/region

### geoApiService

```javascript
geoApiService: 'ip-api'
```

- **Type**: String
- **Default**: `'ip-api'`
- **Description**: Geolocation API service to use
- **Options**: `'ip-api'` or `'ipapi'`
- **Required**: Yes

**When to change**:
- API rate limits
- Service issues
- Preference

**Options**:

#### ip-api (Default)
```javascript
geoApiService: 'ip-api'
```
- **URL**: http://ip-api.com/json/
- **Rate Limit**: 45 requests/minute
- **API Key**: Not required
- **Free**: Yes
- **Data**: IP, city, region, country, ISP, timezone

#### ipapi
```javascript
geoApiService: 'ipapi'
```
- **URL**: https://ipapi.co/json/
- **Rate Limit**: 1000 requests/day (free tier)
- **API Key**: Not required (free tier)
- **Free**: Yes (with limits)
- **Data**: IP, city, region, country, ISP, timezone

**Comparison**:
| Feature | ip-api | ipapi |
|---------|--------|-------|
| Rate Limit | 45/min | 1000/day |
| API Key | No | No (free) |
| HTTPS | No | Yes |
| Accuracy | Good | Good |

---

## 🔧 Functions

### Setup Functions

#### setupSpreadsheet()

```javascript
function setupSpreadsheet()
```

- **Description**: Create location log spreadsheet
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual (once)

**When to run**:
- Initial setup
- Recreate sheet
- Reset logging

#### testGetMyIP()

```javascript
function testGetMyIP()
```

- **Description**: Test IP detection and display current IP info
- **Parameters**: None
- **Returns**: Void (logs to console)
- **Execution**: Manual

**When to run**:
- Find your IP address
- Test geolocation API
- Verify configuration

### Tracking Functions

#### handleAutomaticLocationCheck()

```javascript
function handleAutomaticLocationCheck()
```

- **Description**: Manual location check and log
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual or automated

**When to run**:
- Manual check
- Testing
- Automated via triggers

### Automation Functions

#### createAutomaticTriggers()

```javascript
function createAutomaticTriggers()
```

- **Description**: Set up automated location checks
- **Parameters**: None
- **Returns**: Void
- **Execution**: Manual (once)

**When to run**:
- Enable automation
- After configuration

**Triggers Created**:
Based on `checkInterval` and `businessHours`:
- Checks at intervals during business hours
- Only on specified days

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

### Statistics Functions

#### getLocationStatistics()

```javascript
function getLocationStatistics()
```

- **Description**: Calculate location statistics
- **Parameters**: None
- **Returns**: Void (logs to console)
- **Execution**: Manual

**When to run**:
- View statistics
- Generate reports
- End of period

**Output**:
```
Location Statistics:
Total checks: 45
Home: 30 (66.7%)
Office: 12 (26.7%)
Other: 3 (6.7%)
```

---

## 📝 Examples

### Example 1: Standard Configuration

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['203.123.45.67'],
      ispKeywords: ['SuperLoop']
    },
    office: {
      name: 'Office',
      ipAddresses: ['192.168.1.100'],
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

**Use case**: Standard 9-5, Mon-Fri, 3-hour checks

### Example 2: Full-Time Remote

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['203.123.45.67'],
      ispKeywords: ['SuperLoop']
    },
    office: {
      name: 'Office',
      ipAddresses: [],  // No office
      ispKeywords: []
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

**Use case**: 100% remote work

### Example 3: Flexible Hours

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['203.123.45.67'],
      ispKeywords: ['SuperLoop']
    },
    office: {
      name: 'Office',
      ipAddresses: ['192.168.1.100'],
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 7,   // 7 AM
    endHour: 19,    // 7 PM
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 2,  // Every 2 hours
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

**Use case**: Flexible hours, 7 AM - 7 PM

### Example 4: Part-Time (3 days)

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['203.123.45.67'],
      ispKeywords: ['SuperLoop']
    },
    office: {
      name: 'Office',
      ipAddresses: ['192.168.1.100'],
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 3, 5]  // Mon, Wed, Fri
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

**Use case**: Part-time, Mon/Wed/Fri

### Example 5: IP Range Matching

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['203.123.45'],  // Matches 203.123.45.*
      ispKeywords: ['SuperLoop', 'Telstra']
    },
    office: {
      name: 'Office',
      ipAddresses: ['192.168.1'],  // Matches 192.168.1.*
      ispKeywords: ['CompanyName']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

**Use case**: Dynamic IPs, range matching

---

## 🔧 Parameter Validation

### IP Addresses

```javascript
// Valid
['203.123.45.67']  ✓
['203.123.45']     ✓ (range)
['203.123.45.67', '203.123.45.68']  ✓ (multiple)

// Invalid
[]  ⚠️ Empty, no matching
['YOUR_HOME_IP_HERE']  ✗ Must configure
['203.123.45.67.89']  ✗ Invalid format
```

### Business Hours

```javascript
// Valid
startHour: 9, endHour: 17  ✓
startHour: 0, endHour: 23  ✓

// Invalid
startHour: 25  ✗ Out of range
startHour: 17, endHour: 9  ⚠️ End before start
```

### Days of Week

```javascript
// Valid
[1, 2, 3, 4, 5]  ✓
[1, 3, 5]        ✓
[0, 6]           ✓

// Invalid
[]  ⚠️ No days selected
[7]  ✗ Invalid day number
```

---

## 💡 Tips & Best Practices

### IP Configuration

**Best practices**:
- Use exact IP if static
- Use range if dynamic
- Add multiple IPs if needed
- Test with `testGetMyIP()`

### ISP Keywords

**Best practices**:
- Add your actual ISP
- Use multiple keywords
- Check ISP name in test
- Case doesn't matter

### Business Hours

**Best practices**:
- Match actual work hours
- Include buffer time
- Consider time zones
- Test during work hours

### Check Interval

**Recommendations**:
- Start with 3 hours
- Adjust based on needs
- Consider battery/data
- More frequent = more accurate

---

## ⚠️ Common Issues

### Issue: "Wrong location detected"

**Solution**:
```javascript
// Run testGetMyIP() to see current IP
// Update ipAddresses with actual IP
ipAddresses: ['YOUR_ACTUAL_IP']
```

### Issue: "Location shows as Unknown"

**Solution**:
```javascript
// Add IP to config
ipAddresses: ['203.123.45.67']

// Or add ISP keywords
ispKeywords: ['YourISP', 'YourProvider']
```

### Issue: "No checks happening"

**Solution**:
- Verify triggers created (Triggers icon ⏰)
- Check business hours configuration
- Verify current day/time is within business hours
- Run `createAutomaticTriggers()` again

### Issue: "Too many checks"

**Solution**:
```javascript
// Increase interval
checkInterval: 4  // From 3
```

---

## 📚 Related Documentation

- **[IP-Location-Tracker-Guide.md](IP-Location-Tracker-Guide.md)** - Complete setup guide
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick start
- **[../MODULE_INDEX.md](../MODULE_INDEX.md)** - All modules

---

*Last Updated: December 2024*  
*Version: 1.0*
