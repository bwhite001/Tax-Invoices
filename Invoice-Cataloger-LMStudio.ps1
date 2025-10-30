<#
.SYNOPSIS
    Professional Invoice Cataloging System using LM Studio (Local LLM)
    For ATO-Compliant Work Expense Tracking - Software Developers

.DESCRIPTION
    Automated invoice discovery, AI-powered data extraction, and ATO-compliant
    deduction calculation with Excel export. Designed for software developers
    working from home 3/5 days per week.

.NOTES
    Requirements:
    - LM Studio installed and server running
    - Mistral 7B or compatible model loaded
    - Windows 10/11 with PowerShell 5.1+
    - Tesseract OCR (optional, for scanned documents)
    
    Author: Invoice Processing System
    ATO Compliance: 2024-25 Guidelines
    Date Created: 2025-10-30

.EXAMPLE
    .\Invoice-Cataloger-LMStudio.ps1 -InvoiceFolder "C:\Invoices\2024-25" -OutputFolder "C:\Invoices\Processed"

.EXAMPLE
    # Run with custom endpoint if LM Studio on different port
    $config.LMStudioEndpoint = "http://localhost:8080/v1/chat/completions"
    .\Invoice-Cataloger-LMStudio.ps1
#>

# ============================================
# CONFIGURATION SECTION
# ============================================
param(
    [switch]$CheckOnly,
    [switch]$RetryFailed,
    [string]$FinancialYear = "2024-2025"  # Format: YYYY-YYYY (e.g., "2024-2025", "2023-2024")
)

# Validate Financial Year format
if ($FinancialYear -notmatch '^\d{4}-\d{4}$') {
    Write-Host "ERROR: Invalid Financial Year format. Use YYYY-YYYY (e.g., '2024-2025')" -ForegroundColor Red
    exit 1
}

# Extract years and validate
$years = $FinancialYear -split '-'
$startYear = [int]$years[0]
$endYear = [int]$years[1]

if ($endYear -ne ($startYear + 1)) {
    Write-Host "ERROR: Financial Year must be consecutive years (e.g., 2024-2025)" -ForegroundColor Red
    exit 1
}

# Construct dynamic paths based on Financial Year
$BasePath = "G:\My Drive\Tax Invoices"
$FYFolder = "FY$FinancialYear"
$InvoiceFolderPath = Join-Path $BasePath $FYFolder
$OutputFolderPath = Join-Path $InvoiceFolderPath "Processed"
$LogFolderPath = Join-Path $OutputFolderPath "Logs"
$CachePath = Join-Path $OutputFolderPath "cache.json"
$FailedFilesPath = Join-Path $OutputFolderPath "failed_files.json"

$Config = @{
    # LM Studio Configuration
    LMStudioEndpoint = "http://192.168.0.100:1234/v1/chat/completions"
    LMStudioModelsEndpoint = "http://192.168.0.100:1234/v1/models"
    LMStudioModel = "local-model"  # LM Studio will use loaded model
    
    # OCR Configuration
    UseWindowsOCR = $true  # Built-in Windows 10+ OCR
    TesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
    TesseractLanguage = "eng"
    
    # Folder Configuration (Dynamic based on Financial Year parameter)
    InvoiceFolder = $InvoiceFolderPath
    OutputFolder = $OutputFolderPath
    LogFolder = $LogFolderPath
    CachePath = $CachePath
    FailedFilesPath = $FailedFilesPath
    
    # File Types to Process
    FileExtensions = @('pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml', 'msg')
    
    # ATO Configuration - Software Developer, 3 days WFH
    WorkFromHomeDays = 3
    TotalWorkDays = 5
    WorkUsePercentage = 60  # 3/5 = 60%
    FixedRateHourly = 0.70  # 2024-25 ATO rate
    FinancialYear = $FinancialYear
    Occupation = "Web / Software Developer"
    
    # LM Studio Parameters
    Temperature = 0.1  # Low temperature for consistent extraction
    MaxTokens = 3000
    TimeoutSeconds = 120
    RetryAttempts = 3
    RetryDelaySeconds = 2
    
    # Processing Options
    ProcessInBatches = $false
    BatchSize = 5
    DeleteProcessedFiles = $false  # Keep originals
    MoveProcessedFiles = $true  # Move to Processed folder
    MaxRetryAttempts = 3  # Maximum retry attempts for failed files
}

# ============================================
# LOGGING FUNCTIONS
# ============================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [switch]$NoConsole
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    if (-not $NoConsole) {
        $color = switch ($Level) {
            "ERROR"   { "Red" }
            "WARNING" { "Yellow" }
            "SUCCESS" { "Green" }
            "DEBUG"   { "Cyan" }
            default   { "White" }
        }
        Write-Host $logMessage -ForegroundColor $color
    }
    
    # Log file output
    $logPath = "$($Config.LogFolder)\processing_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $logPath -Value $logMessage -ErrorAction SilentlyContinue
}

function Get-ElapsedTime {
    param([datetime]$StartTime)
    $elapsed = (Get-Date) - $StartTime
    return "{0:d2}h:{1:d2}m:{2:d2}s" -f $elapsed.Hours, $elapsed.Minutes, $elapsed.Seconds
}

# ============================================
# CACHE AND FILE MANAGEMENT FUNCTIONS
# ============================================

function Get-FileHash-MD5 {
    param([string]$FilePath)
    
    try {
        $md5 = [System.Security.Cryptography.MD5]::Create()
        $stream = [System.IO.File]::OpenRead($FilePath)
        $hash = [System.BitConverter]::ToString($md5.ComputeHash($stream))
        $stream.Close()
        return $hash.Replace("-", "").ToLower()
    }
    catch {
        Write-Log "Error calculating file hash: $_" "ERROR"
        return $null
    }
}

function Load-Cache {
    if (Test-Path $Config.CachePath) {
        try {
            $cacheContent = Get-Content -Path $Config.CachePath -Raw -ErrorAction Stop
            $cache = $cacheContent | ConvertFrom-Json
            Write-Log "Loaded cache with $($cache.Count) entries" "DEBUG"
            return $cache
        }
        catch {
            Write-Log "Error loading cache, creating new: $_" "WARNING"
            return @()
        }
    }
    else {
        Write-Log "No cache file found, creating new cache" "DEBUG"
        return @()
    }
}

function Save-Cache {
    param([array]$Cache)
    
    try {
        $Cache | ConvertTo-Json -Depth 10 | Set-Content -Path $Config.CachePath -Encoding UTF8
        Write-Log "Cache saved with $($Cache.Count) entries" "DEBUG"
    }
    catch {
        Write-Log "Error saving cache: $_" "ERROR"
    }
}

function Find-InCache {
    param(
        [array]$Cache,
        [string]$FileHash
    )
    
    foreach ($entry in $Cache) {
        if ($entry.FileHash -eq $FileHash) {
            return $entry
        }
    }
    return $null
}

function Add-ToCache {
    param(
        [array]$Cache,
        [string]$FileName,
        [string]$FileHash,
        [PSCustomObject]$ExtractedData,
        [string]$Category,
        [PSCustomObject]$Deduction
    )
    
    $cacheEntry = [PSCustomObject]@{
        FileName = $FileName
        FileHash = $FileHash
        ProcessedDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        ExtractedData = $ExtractedData
        Category = $Category
        Deduction = $Deduction
    }
    
    return $Cache + $cacheEntry
}

function Load-FailedFiles {
    if (Test-Path $Config.FailedFilesPath) {
        try {
            $failedContent = Get-Content -Path $Config.FailedFilesPath -Raw -ErrorAction Stop
            $failed = $failedContent | ConvertFrom-Json
            Write-Log "Loaded failed files list with $($failed.Count) entries" "DEBUG"
            return $failed
        }
        catch {
            Write-Log "Error loading failed files, creating new: $_" "WARNING"
            return @()
        }
    }
    else {
        Write-Log "No failed files list found" "DEBUG"
        return @()
    }
}

function Save-FailedFiles {
    param([array]$FailedFiles)
    
    try {
        $FailedFiles | ConvertTo-Json -Depth 10 | Set-Content -Path $Config.FailedFilesPath -Encoding UTF8
        Write-Log "Failed files list saved with $($FailedFiles.Count) entries" "DEBUG"
    }
    catch {
        Write-Log "Error saving failed files list: $_" "ERROR"
    }
}

function Add-ToFailedFiles {
    param(
        [array]$FailedFiles,
        [string]$FilePath,
        [string]$FileName,
        [string]$ErrorReason,
        [int]$AttemptCount = 1
    )
    
    # Check if file already in failed list
    $existing = $FailedFiles | Where-Object { $_.FilePath -eq $FilePath }
    
    if ($existing) {
        $existing.AttemptCount = $AttemptCount
        $existing.LastAttempt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        $existing.ErrorReason = $ErrorReason
        return $FailedFiles
    }
    else {
        $failedEntry = [PSCustomObject]@{
            FilePath = $FilePath
            FileName = $FileName
            ErrorReason = $ErrorReason
            AttemptCount = $AttemptCount
            FirstAttempt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            LastAttempt = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
        return $FailedFiles + $failedEntry
    }
}

function Remove-FromFailedFiles {
    param(
        [array]$FailedFiles,
        [string]$FilePath
    )
    
    return $FailedFiles | Where-Object { $_.FilePath -ne $FilePath }
}

function Move-ProcessedFile {
    param(
        [string]$SourcePath,
        [string]$Category,
        [string]$InvoiceDate
    )
    
    try {
        # Parse date for folder structure
        $yearMonth = "Unknown"
        if ($InvoiceDate -match '^\d{4}-\d{2}') {
            $yearMonth = $InvoiceDate.Substring(0, 7)  # YYYY-MM
        }
        
        # Create destination folder
        $destFolder = Join-Path $Config.OutputFolder "$Category\$yearMonth"
        if (-not (Test-Path $destFolder)) {
            New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
        }
        
        # Move file
        $fileName = Split-Path $SourcePath -Leaf
        $destPath = Join-Path $destFolder $fileName
        
        # Handle duplicate filenames
        $counter = 1
        while (Test-Path $destPath) {
            $fileNameWithoutExt = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
            $fileExt = [System.IO.Path]::GetExtension($fileName)
            $destPath = Join-Path $destFolder "$fileNameWithoutExt`_$counter$fileExt"
            $counter++
        }
        
        Move-Item -Path $SourcePath -Destination $destPath -Force
        Write-Log "Moved file to: $destPath" "DEBUG"
        return $destPath
    }
    catch {
        Write-Log "Error moving file: $_" "ERROR"
        return $SourcePath
    }
}

# ============================================
# ENVIRONMENT CHECK FUNCTION
# ============================================

function Test-Environment {
    Write-Log "Running environment checks..." "INFO"
    Write-Log "Financial Year: $FinancialYear" "INFO"
    $ok = $true

    # Invoice folder
    if (-not (Test-Path $Config.InvoiceFolder)) {
        Write-Log "Invoice folder not found: $($Config.InvoiceFolder)" "ERROR"
        Write-Log "Please create the folder: $($Config.InvoiceFolder)" "ERROR"
        $ok = $false
    }
    else {
        Write-Log "Invoice folder exists: $($Config.InvoiceFolder)" "SUCCESS"
    }

    # Output folder - auto-create if needed
    if (-not (Test-Path $Config.OutputFolder)) {
        Write-Log "Output folder not found: $($Config.OutputFolder) - attempting to create" "WARNING"
        try { 
            New-Item -ItemType Directory -Path $Config.OutputFolder -Force | Out-Null
            Write-Log "Created output folder: $($Config.OutputFolder)" "SUCCESS"
        } 
        catch { 
            Write-Log "Failed to create output folder: $_" "ERROR"
            $ok = $false 
        }
    }
    else { 
        Write-Log "Output folder exists: $($Config.OutputFolder)" "SUCCESS" 
    }

    # Log folder - auto-create if needed
    if (-not (Test-Path $Config.LogFolder)) {
        Write-Log "Log folder not found: $($Config.LogFolder) - attempting to create" "WARNING"
        try { 
            New-Item -ItemType Directory -Path $Config.LogFolder -Force | Out-Null
            Write-Log "Created log folder: $($Config.LogFolder)" "SUCCESS"
        } 
        catch { 
            Write-Log "Failed to create log folder: $_" "ERROR"
            $ok = $false 
        }
    }
    else { 
        Write-Log "Log folder exists: $($Config.LogFolder)" "SUCCESS" 
    }

    # LM Studio connectivity
    Write-Log "Checking LM Studio connectivity: $($Config.LMStudioModelsEndpoint)" "INFO"
    try {
        $resp = Invoke-RestMethod -Uri $Config.LMStudioModelsEndpoint -Method Get -TimeoutSec 5 -ErrorAction Stop
        if ($resp.data -and $resp.data.Count -gt 0) { Write-Log "LM Studio reachable. Loaded model: $($resp.data[0].id)" "SUCCESS" } else { Write-Log "LM Studio reachable but no models loaded" "WARNING"; $ok = $false }
    }
    catch { Write-Log "Cannot reach LM Studio: $_" "ERROR"; $ok = $false }

    # Tesseract
    if (Test-Path $Config.TesseractPath) { Write-Log "Tesseract found at: $($Config.TesseractPath)" "SUCCESS" } else { Write-Log "Tesseract NOT found at: $($Config.TesseractPath)" "WARNING" }

    # Excel COM
    try {
        $excel = New-Object -ComObject Excel.Application
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
        Write-Log "Excel COM available" "SUCCESS"
    }
    catch {
        Write-Log "Excel COM not available (Excel may be not installed): $_" "WARNING"
    }

    return $ok
}

# ============================================
# INITIALIZATION FUNCTIONS
# ============================================

function Test-Prerequisites {
    Write-Log "=== Checking Prerequisites ===" "INFO"
    Write-Log "Processing Financial Year: FY$FinancialYear" "INFO"
    
    # Check invoice folder exists
    if (-not (Test-Path $Config.InvoiceFolder)) {
        Write-Log "Invoice folder not found: $($Config.InvoiceFolder)" "ERROR"
        Write-Log "Please create the folder and add invoice files." "ERROR"
        Write-Log "Example: New-Item -ItemType Directory -Path '$($Config.InvoiceFolder)' -Force" "ERROR"
        return $false
    }
    
    # Auto-create output folder if needed
    if (-not (Test-Path $Config.OutputFolder)) {
        try {
            New-Item -ItemType Directory -Path $Config.OutputFolder -Force | Out-Null
            Write-Log "Created output folder: $($Config.OutputFolder)" "SUCCESS"
        }
        catch {
            Write-Log "Failed to create output folder: $_" "ERROR"
            return $false
        }
    }
    
    # Auto-create log folder if needed
    if (-not (Test-Path $Config.LogFolder)) {
        try {
            New-Item -ItemType Directory -Path $Config.LogFolder -Force | Out-Null
            Write-Log "Created log folder: $($Config.LogFolder)" "SUCCESS"
        }
        catch {
            Write-Log "Failed to create log folder: $_" "ERROR"
            return $false
        }
    }
    
    # Check LM Studio connectivity
    Write-Log "Testing LM Studio connection..." "INFO"
    
    try {
        $testResponse = Invoke-RestMethod -Uri $Config.LMStudioModelsEndpoint `
            -Method Get `
            -TimeoutSec 5 `
            -ErrorAction Stop
        
        Write-Log "LM Studio server is running" "SUCCESS"
        
        if ($testResponse.data -and $testResponse.data.Count -gt 0) {
            $modelName = $testResponse.data[0].id
            Write-Log "Loaded model: $modelName" "SUCCESS"
            $Config.LMStudioModel = $modelName
            return $true
        }
        else {
            Write-Log "No model loaded in LM Studio" "ERROR"
            Write-Log "Please load a model (Mistral 7B recommended) in LM Studio" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Cannot connect to LM Studio at $($Config.LMStudioEndpoint)" "ERROR"
        Write-Log "Error: $($_)" "ERROR"
        Write-Log "Please ensure:" "ERROR"
        Write-Log "  1. LM Studio is running (download from https://lmstudio.ai)" "ERROR"
        Write-Log "  2. A model is loaded (e.g., Mistral 7B)" "ERROR"
        Write-Log "  3. Developer Server is started (Status = Running)" "ERROR"
        Write-Log "  4. CORS is enabled in Settings" "ERROR"
        return $false
    }
}

function Get-InvoiceFiles {
    Write-Log "Scanning for invoice files in: $($Config.InvoiceFolder)" "INFO"
    
    $files = @()
    
    try {
        $allFiles = Get-ChildItem -Path $Config.InvoiceFolder -Recurse -File -ErrorAction SilentlyContinue
        foreach ($file in $allFiles) {
            $fileExt = [System.IO.Path]::GetExtension($file.Name).TrimStart('.').ToLower()
            if ($Config.FileExtensions -contains $fileExt) {
                $files += $file
            }
        }
        foreach ($ext in $Config.FileExtensions) {
            $count = ($files | Where-Object { [System.IO.Path]::GetExtension($_.Name).TrimStart('.').ToLower() -eq $ext }).Count
            if ($count -gt 0) {
                Write-Log "Found $count $ext files" "DEBUG"
            }
        }
    }
    catch {
        Write-Log "Error scanning files: $_" "ERROR"
        return @()
    }
    
    Write-Log "Total files found: $($files.Count)" "SUCCESS"
    return $files
}

# ============================================
# DOCUMENT EXTRACTION FUNCTIONS
# ============================================

function Extract-TextFromWord {
    param([string]$WordPath)
    
    try {
        Write-Log "Extracting text from Word document: $(Split-Path $WordPath -Leaf)" "DEBUG"
        
        # Try using Word COM object
        try {
            $word = New-Object -ComObject Word.Application
            $word.Visible = $false
            $word.DisplayAlerts = 0  # Disable alerts
            $doc = $word.Documents.Open($WordPath, $false, $true, $false)  # ReadOnly = true, AddToRecentFiles = false
            
            # Extract all text content
            $text = $doc.Content.Text
            
            # Clean up
            $doc.Close($false)
            $word.Quit()
            [System.Runtime.Interopservices.Marshal]::ReleaseComObject($doc) | Out-Null
            [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            
            if ($text -and $text.Trim().Length -gt 0) {
                Write-Log "Word extraction successful ($($text.Length) chars)" "DEBUG"
                return $text
            }
            else {
                Write-Log "Word document appears to be empty" "WARNING"
                return $null
            }
        }
        catch {
            Write-Log "Word COM extraction failed: $_" "WARNING"
            
            # Fallback: Try using .NET OpenXML for .docx files only
            if ($WordPath -match '\.docx$') {
                try {
                    Add-Type -AssemblyName DocumentFormat.OpenXml -ErrorAction Stop
                    Add-Type -AssemblyName System.IO.Packaging -ErrorAction Stop
                    
                    $package = [DocumentFormat.OpenXml.Packaging.WordprocessingDocument]::Open($WordPath, $false)
                    $body = $package.MainDocumentPart.Document.Body
                    $text = $body.InnerText
                    $package.Close()
                    
                    if ($text -and $text.Trim().Length -gt 0) {
                        Write-Log "OpenXML extraction successful ($($text.Length) chars)" "DEBUG"
                        return $text
                    }
                }
                catch {
                    Write-Log "OpenXML extraction also failed: $_" "WARNING"
                }
            }
        }
        
        Write-Log "Could not extract text from Word document" "WARNING"
        return $null
    }
    catch {
        Write-Log "Error extracting Word text: $_" "ERROR"
        return $null
    }
}

function Extract-TextFromExcel {
    param([string]$ExcelPath)
    
    try {
        Write-Log "Extracting text from Excel document: $(Split-Path $ExcelPath -Leaf)" "DEBUG"
        
        # Try using Excel COM object
        try {
            $excel = New-Object -ComObject Excel.Application
            $excel.Visible = $false
            $excel.DisplayAlerts = $false
            $workbook = $excel.Workbooks.Open($ExcelPath, 0, $true)  # ReadOnly = true
            
            $text = ""
            
            # Extract text from all worksheets
            foreach ($worksheet in $workbook.Worksheets) {
                $usedRange = $worksheet.UsedRange
                if ($usedRange) {
                    $rows = $usedRange.Rows.Count
                    $cols = $usedRange.Columns.Count
                    
                    for ($row = 1; $row -le $rows; $row++) {
                        for ($col = 1; $col -le $cols; $col++) {
                            $cellValue = $usedRange.Cells.Item($row, $col).Text
                            if ($cellValue) {
                                $text += "$cellValue "
                            }
                        }
                        $text += "`n"
                    }
                }
            }
            
            # Clean up
            $workbook.Close($false)
            $excel.Quit()
            [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
            [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            
            if ($text -and $text.Trim().Length -gt 0) {
                Write-Log "Excel extraction successful ($($text.Length) chars)" "DEBUG"
                return $text
            }
            else {
                Write-Log "Excel document appears to be empty" "WARNING"
                return $null
            }
        }
        catch {
            Write-Log "Excel COM extraction failed: $_" "WARNING"
            
            # Fallback: Try using .NET OpenXML for .xlsx files only
            if ($ExcelPath -match '\.xlsx$') {
                try {
                    Add-Type -AssemblyName DocumentFormat.OpenXml -ErrorAction Stop
                    Add-Type -AssemblyName System.IO.Packaging -ErrorAction Stop
                    
                    $package = [DocumentFormat.OpenXml.Packaging.SpreadsheetDocument]::Open($ExcelPath, $false)
                    $workbookPart = $package.WorkbookPart
                    $text = ""
                    
                    foreach ($worksheetPart in $workbookPart.WorksheetParts) {
                        $sheetData = $worksheetPart.Worksheet.Descendants() | Where-Object { $_ -is [DocumentFormat.OpenXml.Spreadsheet.SheetData] } | Select-Object -First 1
                        if ($sheetData) {
                            $rows = $sheetData.Descendants() | Where-Object { $_ -is [DocumentFormat.OpenXml.Spreadsheet.Row] }
                            foreach ($row in $rows) {
                                $cells = $row.Descendants() | Where-Object { $_ -is [DocumentFormat.OpenXml.Spreadsheet.Cell] }
                                foreach ($cell in $cells) {
                                    if ($cell.CellValue) {
                                        $text += "$($cell.CellValue.Text) "
                                    }
                                }
                                $text += "`n"
                            }
                        }
                    }
                    
                    $package.Close()
                    
                    if ($text -and $text.Trim().Length -gt 0) {
                        Write-Log "OpenXML Excel extraction successful ($($text.Length) chars)" "DEBUG"
                        return $text
                    }
                }
                catch {
                    Write-Log "OpenXML Excel extraction also failed: $_" "WARNING"
                }
            }
        }
        
        Write-Log "Could not extract text from Excel document" "WARNING"
        return $null
    }
    catch {
        Write-Log "Error extracting Excel text: $_" "ERROR"
        return $null
    }
}

function Extract-TextFromEmail {
    param([string]$EmailPath)
    
    try {
        Write-Log "Extracting text from email: $(Split-Path $EmailPath -Leaf)" "DEBUG"
        
        # Try using Outlook COM object for .msg files
        if ($EmailPath -match '\.msg$') {
            try {
                $outlook = New-Object -ComObject Outlook.Application
                $mail = $outlook.Session.OpenSharedItem($EmailPath)
                
                $text = "From: $($mail.SenderName) <$($mail.SenderEmailAddress)>`n"
                $text += "To: $($mail.To)`n"
                $text += "Subject: $($mail.Subject)`n"
                $text += "Date: $($mail.ReceivedTime)`n`n"
                $text += $mail.Body
                
                # Check for attachments
                if ($mail.Attachments.Count -gt 0) {
                    $text += "`n`nAttachments:`n"
                    foreach ($attachment in $mail.Attachments) {
                        $text += "- $($attachment.FileName)`n"
                    }
                }
                
                [System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null
                [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
                [System.GC]::Collect()
                [System.GC]::WaitForPendingFinalizers()
                
                if ($text -and $text.Trim().Length -gt 0) {
                    Write-Log "Email extraction successful ($($text.Length) chars)" "DEBUG"
                    return $text
                }
            }
            catch {
                Write-Log "Outlook COM extraction failed: $_" "WARNING"
            }
        }
        
        # Fallback: Try reading as plain text for .eml files
        if ($EmailPath -match '\.eml$') {
            try {
                $text = Get-Content -Path $EmailPath -Raw -Encoding UTF8
                if ($text -and $text.Trim().Length -gt 0) {
                    Write-Log "EML text extraction successful ($($text.Length) chars)" "DEBUG"
                    return $text
                }
            }
            catch {
                Write-Log "EML text extraction failed: $_" "WARNING"
            }
        }
        
        Write-Log "Could not extract text from email" "WARNING"
        return $null
    }
    catch {
        Write-Log "Error extracting email text: $_" "ERROR"
        return $null
    }
}

function Extract-TextFromPDF {
    param([string]$PdfPath)
    
    try {
        Write-Log "Extracting text from PDF: $(Split-Path $PdfPath -Leaf)" "DEBUG"
        
        # Use Windows built-in PDF text extraction via Windows Search Index
        # Or use Tesseract for better results
        
        if (Test-Path $Config.TesseractPath) {
            return Extract-TextWithTesseract -ImagePath $PdfPath
        }
        
        # Fallback: Use System.Diagnostics with pdftotext
        $tempText = [System.IO.Path]::GetTempFileName()
        
        try {
            $pdftotext = "C:\Program Files\poppler\Library\bin\pdftotext.exe"
            if (Test-Path $pdftotext) {
                & $pdftotext $PdfPath $tempText 2>$null
                $text = Get-Content $tempText -Raw -ErrorAction SilentlyContinue
                Remove-Item $tempText -ErrorAction SilentlyContinue
                
                if ($text -and $text.Length -gt 10) {
                    return $text
                }
            }
        }
        catch {}
        
        Write-Log "PDF extraction requires Tesseract or Poppler tools" "WARNING"
        return $null
    }
    catch {
        Write-Log "Error extracting PDF text: $_" "ERROR"
        return $null
    }
}

function Extract-TextFromImage {
    param([string]$ImagePath)
    
    $extension = [System.IO.Path]::GetExtension($ImagePath).ToLower()
    
    Write-Log "Extracting text from image: $(Split-Path $ImagePath -Leaf)" "DEBUG"
    
    # Try Tesseract first
    if (Test-Path $Config.TesseractPath) {
        return Extract-TextWithTesseract -ImagePath $ImagePath
    }
    
    # Try Windows built-in OCR (PowerShell 5.1, Windows 10+)
    if ($Config.UseWindowsOCR) {
        try {
            Add-Type -AssemblyName System.Runtime.WindowsRuntime
            $null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
            $null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
            
            $file = [Windows.Storage.StorageFile]::GetFileFromPathAsync($ImagePath).GetAwaiter().GetResult()
            $stream = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read).GetAwaiter().GetResult()
            
            $decoder = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream).GetAwaiter().GetResult()
            $bitmap = $decoder.GetSoftwareBitmapAsync().GetAwaiter().GetResult()
            
            $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new($Config.TesseractLanguage))
            $result = $engine.RecognizeAsync($bitmap).GetAwaiter().GetResult()
            
            $stream.Dispose()
            
            return $result.Text
        }
        catch {
            Write-Log "Windows OCR failed, falling back to Tesseract" "WARNING"
        }
    }
    
    Write-Log "No OCR engine available for image processing" "WARNING"
    return $null
}

function Extract-TextWithTesseract {
    param([string]$ImagePath)
    
    if (-not (Test-Path $Config.TesseractPath)) {
        Write-Log "Tesseract not installed at: $($Config.TesseractPath)" "WARNING"
        return $null
    }
    
    try {
        $outputFile = [System.IO.Path]::GetTempFileName()
        $outputBase = $outputFile -replace '\.tmp$', ''
        
        # Run Tesseract
        & $Config.TesseractPath $ImagePath $outputBase -l $Config.TesseractLanguage 2>&1 | Out-Null
        
        $textFile = "$outputBase.txt"
        if (Test-Path $textFile) {
            $text = Get-Content $textFile -Raw -ErrorAction SilentlyContinue
            Remove-Item $textFile -ErrorAction SilentlyContinue
            Remove-Item $outputFile -ErrorAction SilentlyContinue
            
            # Check if text was actually extracted
            if ($text -and $text.Trim().Length -gt 0) {
                Write-Log "Tesseract extraction successful ($($text.Length) chars)" "DEBUG"
                return $text
            }
            else {
                Write-Log "Tesseract extracted empty text" "WARNING"
                return $null
            }
        }
        else {
            Write-Log "Tesseract output file not created" "WARNING"
            return $null
        }
    }
    catch {
        Write-Log "Tesseract error: $_" "ERROR"
    }
    
    return $null
}

# ============================================
# LM STUDIO EXTRACTION FUNCTIONS
# ============================================

function Invoke-LMStudioExtraction {
    param(
        [string]$InvoiceText,
        [string]$FileName,
        [int]$Attempt = 1
    )
    
    if ([string]::IsNullOrWhiteSpace($InvoiceText)) {
        Write-Log "No text to extract from $FileName" "WARNING"
        return $null
    }
    
    # Truncate very long texts
    if ($InvoiceText.Length -gt 10000) {
        Write-Log "Truncating invoice text (was $($InvoiceText.Length) chars)" "DEBUG"
        $InvoiceText = $InvoiceText.Substring(0, 10000)
    }
    
    $prompt = @"
You are an invoice data extraction specialist. Extract invoice information from the text below and return ONLY valid JSON with no additional text or markdown.

TEXT TO EXTRACT FROM:
$InvoiceText

RETURN THIS JSON STRUCTURE (use empty string "" for missing fields, 0.00 for amounts):
{
  "vendor_name": "",
  "vendor_abn": "",
  "invoice_number": "",
  "invoice_date": "",
  "due_date": "",
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00,
  "currency": "AUD",
  "description": "",
  "line_items": [{"description": "", "quantity": 1, "unit_price": 0.00, "amount": 0.00}]
}

INSTRUCTIONS:
1. Extract vendor ABN if visible
2. Extract invoice number/ID
3. Extract invoice date and due date in YYYY-MM-DD format
4. Extract all monetary amounts
5. Extract line item descriptions and amounts
6. Return ONLY the JSON object, no explanation
"@

    try {
        # Combine system message with user prompt since some models don't support system role
        $fullPrompt = "You are a JSON extraction assistant. Always respond with ONLY valid JSON, no markdown, no explanations.`n`n$prompt"
        
        $requestBody = @{
            model = $Config.LMStudioModel
            messages = @(
                @{
                    role = "user"
                    content = $fullPrompt
                }
            )
            temperature = $Config.Temperature
            max_tokens = $Config.MaxTokens
        } | ConvertTo-Json -Depth 10 -Compress
        
        Write-Log "Sending to LM Studio for extraction (attempt $Attempt)..." "DEBUG"
        
        $response = Invoke-RestMethod -Uri $Config.LMStudioEndpoint `
            -Method Post `
            -Body $requestBody `
            -ContentType "application/json" `
            -TimeoutSec $Config.TimeoutSeconds `
            -ErrorAction Stop
        
        if ($response.choices -and $response.choices[0].message) {
            $jsonResponse = $response.choices[0].message.content
            
            # Clean up response
            $jsonResponse = $jsonResponse -replace '```json\s*', '' -replace '```\s*', '' -replace '^[\s\n]*', '' -replace '[\s\n]*$', ''
            
            # Parse and validate JSON
            $extractedData = $jsonResponse | ConvertFrom-Json -ErrorAction Stop
            
            Write-Log "Successfully extracted data from $FileName" "DEBUG"
            return $extractedData
        }
    }
    catch {
        Write-Log "LM Studio extraction error: $_" "ERROR"
        if ($response -and $response.choices -and $response.choices[0].message) {
            Write-Log "Response was: $($response.choices[0].message.content)" "DEBUG"
        }
        
        if ($Attempt -lt $Config.RetryAttempts) {
            Write-Log "Retrying in $($Config.RetryDelaySeconds) seconds..." "WARNING"
            Start-Sleep -Seconds $Config.RetryDelaySeconds
            return Invoke-LMStudioExtraction -InvoiceText $InvoiceText -FileName $FileName -Attempt ($Attempt + 1)
        }
    }
    
    return $null
}

# ============================================
# DATA PROCESSING FUNCTIONS
# ============================================

function Get-ExpenseCategory {
    param(
        [string]$Description,
        [string]$VendorName,
        [string]$LineItemText
    )
    
    $searchText = "$Description $VendorName $LineItemText".ToLower()
    
    # Enhanced categories with more context-based keywords
    $categories = @{
        "Food & Groceries" = @("food", "grocery", "groceries", "supermarket", "woolworths", "coles", "aldi", "iga", "restaurant", "cafe", "coffee", "lunch", "dinner", "breakfast", "meal", "catering", "uber eats", "menulog", "deliveroo", "doordash")
        "Electronics" = @("electronics", "electronic", "jb hi-fi", "jb hifi", "harvey norman", "good guys", "bing lee", "appliance", "tv", "television", "camera", "headphones", "speaker", "audio", "video", "gaming", "console", "playstation", "xbox", "nintendo")
        "Software & Subscriptions" = @("software", "license", "subscription", "saas", "ide", "github", "azure", "aws", "jetbrains", "microsoft", "adobe", "npm", "python", "annual", "monthly", "cloud", "hosting", "domain", "ssl", "api", "dropbox", "google workspace", "office 365", "slack", "zoom", "notion", "figma", "canva")
        "Computer Equipment" = @("computer", "laptop", "monitor", "keyboard", "mouse", "hardware", "dell", "hp", "lenovo", "macbook", "ipad", "tablet", "printer", "scanner", "webcam", "microphone", "usb", "cable", "adapter", "dock", "ssd", "hard drive", "ram", "memory")
        "Electricity" = @("electricity", "energy", "power", "electric", "eora", "ergon", "ausgrid", "energex", "agl", "origin", "red energy", "simply energy", "alinta")
        "Internet" = @("internet", "isp", "broadband", "nbn", "telstra", "optus", "vodafone", "data", "tpg", "aussie broadband", "superloop", "belong", "wifi", "modem", "router")
        "Phone & Mobile" = @("phone", "mobile", "telco", "mobile plan", "sim", "smartphone", "iphone", "samsung", "android", "prepaid", "postpaid", "amaysim", "boost", "kogan mobile")
        "Professional Development" = @("training", "course", "udemy", "pluralsight", "education", "conference", "seminar", "masterclass", "workshop", "certification", "exam", "learning", "tutorial", "bootcamp", "coursera", "linkedin learning", "skillshare")
        "Professional Membership" = @("association", "membership", "professional", "society", "aca", "ieee", "acm", "annual fee", "registration", "accreditation")
        "Office Supplies" = @("office", "stationery", "supplies", "paper", "pen", "desk", "chair", "filing", "officeworks", "staples", "notebook", "folder", "binder", "whiteboard", "marker")
        "Communication Tools" = @("communication", "voip", "skype", "teams", "zoom", "slack", "discord", "webex", "gotomeeting", "conferencing", "video call")
        "Transportation" = @("transport", "uber", "taxi", "lyft", "didi", "ola", "petrol", "fuel", "gas", "parking", "toll", "car", "vehicle", "automotive", "service", "maintenance", "registration", "insurance")
        "Clothing & Apparel" = @("clothing", "clothes", "apparel", "shirt", "pants", "shoes", "jacket", "dress", "fashion", "wear", "footwear", "uniqlo", "zara", "h&m", "target", "kmart", "big w")
        "Health & Medical" = @("health", "medical", "doctor", "pharmacy", "chemist", "medicine", "prescription", "dental", "dentist", "optometry", "glasses", "physiotherapy", "physio", "hospital", "clinic")
        "Home & Garden" = @("home", "garden", "bunnings", "mitre 10", "hardware", "tools", "paint", "furniture", "ikea", "fantastic furniture", "homeware", "decor", "renovation", "repair")
        "Entertainment & Media" = @("entertainment", "netflix", "spotify", "disney", "amazon prime", "stan", "binge", "kayo", "foxtel", "streaming", "music", "movie", "cinema", "theatre", "event", "ticket", "concert")
        "Books & Publications" = @("book", "books", "publication", "magazine", "journal", "kindle", "ebook", "audiobook", "audible", "bookstore", "dymocks", "booktopia", "amazon books")
        "Insurance" = @("insurance", "policy", "premium", "cover", "coverage", "life insurance", "health insurance", "car insurance", "home insurance", "contents insurance")
        "Banking & Finance" = @("bank", "banking", "fee", "account fee", "transaction fee", "atm", "interest", "loan", "credit card", "debit card", "financial", "investment")
        "Utilities & Services" = @("utility", "utilities", "water", "gas", "sewerage", "council", "rates", "waste", "garbage", "bin", "service fee")
    }
    
    foreach ($category in $categories.Keys) {
        $keywords = $categories[$category]
        foreach ($keyword in $keywords) {
            if ($searchText -match $keyword) {
                return $category
            }
        }
    }
    
    return "Other"
}

function Calculate-ATODeduction {
    param(
        [PSCustomObject]$InvoiceData,
        [string]$Category,
        [string]$FilePath
    )
    
    $total = if ($InvoiceData.total) { [decimal]$InvoiceData.total } else { 0 }
    $workUse = $Config.WorkUsePercentage / 100
    
    $deduction = [PSCustomObject]@{
        Category = $Category
        TotalAmount = $total
        WorkUsePercentage = $Config.WorkUsePercentage
        DeductibleAmount = 0
        ClaimMethod = ""
        ClaimNotes = ""
        AtoReference = ""
        RequiresDocumentation = @()
    }
    
    switch ($Category) {
        "Electricity" {
            $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
            $deduction.ClaimMethod = "Actual Cost Method (60% work use)"
            $deduction.ClaimNotes = "Alternative: Fixed Rate Method at $($Config.FixedRateHourly)/hour requires time records"
            $deduction.AtoReference = "Working from Home Expenses"
            $deduction.RequiresDocumentation = @("Original invoice", "Usage records")
        }
        "Internet" {
            $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
            $deduction.ClaimMethod = "Actual Cost Method (60% work use)"
            $deduction.ClaimNotes = "NOT claimable if using Fixed Rate Method"
            $deduction.AtoReference = "Home Phone and Internet Expenses"
            $deduction.RequiresDocumentation = @("Invoice with breakdown", "Evidence of work use")
        }
        "Phone" {
            $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
            $deduction.ClaimMethod = "Actual Cost Method (60% work use)"
            $deduction.ClaimNotes = "Must have itemized bills showing work calls"
            $deduction.AtoReference = "Home Phone and Internet Expenses"
            $deduction.RequiresDocumentation = @("Itemized phone bill", "Call log analysis")
        }
        "Software & Subscriptions" {
            if ($total -le 300) {
                $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
                $deduction.ClaimMethod = "Immediate Deduction (Under $300)"
                $deduction.ClaimNotes = "Verify work-related purpose in vendor name/description"
                $deduction.AtoReference = "Computers, Laptops and Software"
            }
            else {
                $deduction.DeductibleAmount = [Math]::Round($total * $workUse / 2, 2)  # Conservative estimate
                $deduction.ClaimMethod = "Decline in Value (Over $300 - Depreciation Required)"
                $deduction.ClaimNotes = "Use ATO Depreciation Tool to calculate. Typical: 2-3 years"
                $deduction.AtoReference = "Depreciation - Assets over \$300"
            }
            $deduction.RequiresDocumentation = @("Invoice", "Evidence of work-related use")
        }
        "Computer Equipment" {
            if ($total -le 300) {
                $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
                $deduction.ClaimMethod = "Immediate Deduction (Under $300)"
                $deduction.ClaimNotes = "Work-related portion only (60%)"
            }
            else {
                $deduction.DeductibleAmount = [Math]::Round($total * $workUse / 3, 2)  # Conservative 3-year depreciation
                $deduction.ClaimMethod = "Decline in Value (Over $300 - Depreciation)"
                $deduction.ClaimNotes = "Typical effective life for computers: 2-4 years. Use ATO tool"
                $deduction.AtoReference = "Depreciation - Assets over \$300"
            }
            $deduction.RequiresDocumentation = @("Invoice", "Purchase receipt", "Depreciation calculation")
        }
        "Professional Development" {
            $deduction.DeductibleAmount = $total
            $deduction.WorkUsePercentage = 100
            $deduction.ClaimMethod = "Full Deduction (100%)"
            $deduction.ClaimNotes = "Must directly relate to current employment and improve current skills"
            $deduction.AtoReference = "Training and Education"
            $deduction.RequiresDocumentation = @("Course invoice", "Evidence of course content", "Relevance to role")
        }
        "Professional Membership" {
            $deduction.DeductibleAmount = $total
            $deduction.WorkUsePercentage = 100
            $deduction.ClaimMethod = "Full Deduction (100%)"
            $deduction.ClaimNotes = "Must be relevant to your IT profession"
            $deduction.AtoReference = "Professional Memberships and Accreditations"
            $deduction.RequiresDocumentation = @("Invoice", "Membership certificate")
        }
        "Office Supplies" {
            $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
            $deduction.ClaimMethod = "Actual Cost Method (60%) OR included in Fixed Rate"
            $deduction.ClaimNotes = "Covered by Fixed Rate Method if using that approach"
            $deduction.AtoReference = "Home Office Expenses"
            $deduction.RequiresDocumentation = @("Invoice", "Usage records")
        }
        "Mobile/Communication" {
            $deduction.DeductibleAmount = [Math]::Round($total * $workUse, 2)
            $deduction.ClaimMethod = "Actual Cost Method (60% work use)"
            $deduction.AtoReference = "Home Phone and Internet Expenses"
            $deduction.RequiresDocumentation = @("Invoice", "Usage analysis")
        }
        default {
            $deduction.DeductibleAmount = 0
            $deduction.ClaimMethod = "Manual Review Required"
            $deduction.ClaimNotes = "Consult tax professional to determine deductibility"
            $deduction.AtoReference = "Other Operating Expenses"
            $deduction.RequiresDocumentation = @("Full documentation", "Professional advice")
        }
    }
    
    return $deduction
}

# ============================================
# EXPORT FUNCTIONS
# ============================================

function Export-ToCSV {
    param([array]$ProcessedInvoices)
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $csvPath = "$($Config.OutputFolder)\Invoice_Catalog_$timestamp.csv"
    
    Write-Log "Exporting catalog to CSV: $csvPath" "INFO"
    
    $catalogEntries = @()
    
    foreach ($invoice in $ProcessedInvoices) {
        $entry = [PSCustomObject]@{
            ProcessDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            ProcessingStatus = if ($invoice.ProcessingStatus) { $invoice.ProcessingStatus } else { "Success" }
            FileName = $invoice.FileName
            FileType = $invoice.FileType
            FileHash = if ($invoice.FileHash) { $invoice.FileHash } else { "N/A" }
            VendorName = $invoice.Data.vendor_name
            VendorABN = $invoice.Data.vendor_abn
            InvoiceNumber = $invoice.Data.invoice_number
            InvoiceDate = $invoice.Data.invoice_date
            DueDate = $invoice.Data.due_date
            Category = $invoice.Category
            Currency = $invoice.Data.currency
            SubTotal = $invoice.Data.subtotal
            Tax = $invoice.Data.tax
            InvoiceTotal = $invoice.Data.total
            WorkUsePercentage = $invoice.Deduction.WorkUsePercentage
            DeductibleAmount = $invoice.Deduction.DeductibleAmount
            ClaimMethod = $invoice.Deduction.ClaimMethod
            ClaimNotes = $invoice.Deduction.ClaimNotes
            ATOReference = $invoice.Deduction.AtoReference
            RequiredDocumentation = $invoice.Deduction.RequiresDocumentation -join "; "
            OriginalPath = $invoice.FilePath
            MovedTo = if ($invoice.MovedTo) { $invoice.MovedTo } else { "N/A" }
        }
        $catalogEntries += $entry
    }
    
    $catalogEntries | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    
    Write-Log "CSV catalog saved: $csvPath" "SUCCESS"
    
    # Create summary report
    $summaryPath = "$($Config.OutputFolder)\Deduction_Summary_$timestamp.csv"
    
    $summary = $catalogEntries | Group-Object -Property Category | ForEach-Object {
        [PSCustomObject]@{
            Category = $_.Name
            InvoiceCount = $_.Count
            TotalInvoiced = [Math]::Round(($_.Group | Measure-Object -Property InvoiceTotal -Sum).Sum, 2)
            TotalDeductible = [Math]::Round(($_.Group | Measure-Object -Property DeductibleAmount -Sum).Sum, 2)
            AverageDeduction = [Math]::Round(($_.Group | Measure-Object -Property DeductibleAmount -Average).Average, 2)
        }
    } | Sort-Object -Property TotalDeductible -Descending
    
    $summary | Export-Csv -Path $summaryPath -NoTypeInformation -Encoding UTF8
    
    Write-Log "Summary report saved: $summaryPath" "SUCCESS"
    
    # Display summary
    Write-Log "" "INFO"
    Write-Log "=== PROCESSING SUMMARY ===" "INFO"
    Write-Log "Total invoices processed: $($catalogEntries.Count)" "SUCCESS"
    $totalInvoiced = [Math]::Round(($catalogEntries | Measure-Object -Property InvoiceTotal -Sum).Sum, 2)
    $totalDeductible = [Math]::Round(($catalogEntries | Measure-Object -Property DeductibleAmount -Sum).Sum, 2)
    Write-Log ("Total invoiced amount: $" + $totalInvoiced) "SUCCESS"
    Write-Log ("Total deductible amount: $" + $totalDeductible) "SUCCESS"
    Write-Log "" "INFO"
    Write-Log "Breakdown by Category:" "INFO"
    $summary | ForEach-Object {
        Write-Log ([string]::Format("  {0}: {1} invoices = ${2} deductible", $_.Category, $_.InvoiceCount, $_.TotalDeductible)) "INFO"
    }
    
    return @{
        CatalogPath = $csvPath
        SummaryPath = $summaryPath
        CatalogEntries = $catalogEntries
        Summary = $summary
    }
}

function Export-ToExcel {
    param(
        [array]$ProcessedInvoices,
        [PSCustomObject]$ExportData
    )
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $excelPath = "$($Config.OutputFolder)\Invoice_Catalog_$timestamp.xlsx"
    
    Write-Log "Exporting to Excel: $excelPath" "INFO"
    
    try {
        # Create Excel COM object
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        
        $workbook = $excel.Workbooks.Add()
        
        # Add summary sheet
        $summarySheet = $workbook.Sheets.Item(1)
        $summarySheet.Name = "Summary"
        
        $row = 1
        $summarySheet.Cells.Item($row, 1) = "ATO WORK EXPENSE DEDUCTION SUMMARY"
        $summarySheet.Cells.Item($row, 1).Font.Bold = $true
        $summarySheet.Cells.Item($row, 1).Font.Size = 14
        
        $row = 3
        $summarySheet.Cells.Item($row, 1) = "Employee: $($Config.Occupation)"
        $summarySheet.Cells.Item($row, 2) = "Work Days WFH: $($Config.WorkFromHomeDays)/$($Config.TotalWorkDays)"
        
        $row++
        $summarySheet.Cells.Item($row, 1) = "Financial Year: $($Config.FinancialYear)"
        $summarySheet.Cells.Item($row, 2) = "Work Use %: $($Config.WorkUsePercentage)%"
        
        $row = 6
        $summarySheet.Cells.Item($row, 1) = "Category"
        $summarySheet.Cells.Item($row, 2) = "Invoices"
        $summarySheet.Cells.Item($row, 3) = "Total Invoiced"
        $summarySheet.Cells.Item($row, 4) = "Total Deductible"
        
        for ($i = 1; $i -le 4; $i++) {
            $summarySheet.Cells.Item($row, $i).Font.Bold = $true
            $summarySheet.Cells.Item($row, $i).Interior.ColorIndex = 15
        }
        
        $row = 7
        foreach ($item in $ExportData.Summary) {
            $summarySheet.Cells.Item($row, 1) = $item.Category
            $summarySheet.Cells.Item($row, 2) = $item.InvoiceCount
            $summarySheet.Cells.Item($row, 3) = $item.TotalInvoiced
            $summarySheet.Cells.Item($row, 4) = $item.TotalDeductible
            $summarySheet.Cells.Item($row, 3).NumberFormat = "$#,##0.00"
            $summarySheet.Cells.Item($row, 4).NumberFormat = "$#,##0.00"
            $row++
        }
        
        $row++
        $summarySheet.Cells.Item($row, 1) = "TOTAL"
        $summarySheet.Cells.Item($row, 1).Font.Bold = $true
        $summarySheet.Cells.Item($row, 2) = $ExportData.CatalogEntries.Count
        $summarySheet.Cells.Item($row, 3) = [Math]::Round(($ExportData.CatalogEntries | Measure-Object -Property InvoiceTotal -Sum).Sum, 2)
        $summarySheet.Cells.Item($row, 4) = [Math]::Round(($ExportData.CatalogEntries | Measure-Object -Property DeductibleAmount -Sum).Sum, 2)
        $summarySheet.Cells.Item($row, 3).NumberFormat = "$#,##0.00"
        $summarySheet.Cells.Item($row, 4).NumberFormat = "$#,##0.00"
        
        # Auto-fit columns
        for ($i = 1; $i -le 4; $i++) {
            $summarySheet.Columns.Item($i).AutoFit() | Out-Null
        }
        
        # Add detailed sheet
        $detailSheet = $workbook.Sheets.Add()
        $detailSheet.Name = "Invoices"
        
        # Headers
        $headers = @("Status", "File", "Date", "Vendor", "Category", "Amount", "Deductible", "Method", "Moved To")
        for ($i = 0; $i -lt $headers.Count; $i++) {
            $detailSheet.Cells.Item(1, $i + 1) = $headers[$i]
            $detailSheet.Cells.Item(1, $i + 1).Font.Bold = $true
            $detailSheet.Cells.Item(1, $i + 1).Interior.ColorIndex = 15
        }
        
        # Data
        $row = 2
        foreach ($entry in $ExportData.CatalogEntries) {
            $detailSheet.Cells.Item($row, 1) = $entry.ProcessingStatus
            $detailSheet.Cells.Item($row, 2) = $entry.FileName
            $detailSheet.Cells.Item($row, 3) = $entry.InvoiceDate
            $detailSheet.Cells.Item($row, 4) = $entry.VendorName
            $detailSheet.Cells.Item($row, 5) = $entry.Category
            $detailSheet.Cells.Item($row, 6) = $entry.InvoiceTotal
            $detailSheet.Cells.Item($row, 7) = $entry.DeductibleAmount
            $detailSheet.Cells.Item($row, 8) = $entry.ClaimMethod
            $detailSheet.Cells.Item($row, 9) = $entry.MovedTo
            
            $detailSheet.Cells.Item($row, 6).NumberFormat = "$#,##0.00"
            $detailSheet.Cells.Item($row, 7).NumberFormat = "$#,##0.00"
            
            # Color code by status
            if ($entry.ProcessingStatus -match "Failed|Skipped") {
                $detailSheet.Rows.Item($row).Interior.ColorIndex = 46  # Orange
            }
            elseif ($entry.ProcessingStatus -match "Cached") {
                $detailSheet.Rows.Item($row).Interior.ColorIndex = 34  # Light Blue
            }
            
            $row++
        }
        
        # Auto-fit columns
        for ($i = 1; $i -le $headers.Count; $i++) {
            $detailSheet.Columns.Item($i).AutoFit() | Out-Null
        }
        
        # Add Failed Files sheet if there are any
        $failedEntries = $ExportData.CatalogEntries | Where-Object { $_.ProcessingStatus -match "Failed|Skipped" }
        if ($failedEntries.Count -gt 0) {
            $failedSheet = $workbook.Sheets.Add()
            $failedSheet.Name = "Failed Files"
            
            # Headers
            $failedHeaders = @("Status", "File", "Category", "Error/Reason", "File Hash", "Original Path")
            for ($i = 0; $i -lt $failedHeaders.Count; $i++) {
                $failedSheet.Cells.Item(1, $i + 1) = $failedHeaders[$i]
                $failedSheet.Cells.Item(1, $i + 1).Font.Bold = $true
                $failedSheet.Cells.Item(1, $i + 1).Interior.ColorIndex = 15
            }
            
            # Data
            $row = 2
            foreach ($entry in $failedEntries) {
                $failedSheet.Cells.Item($row, 1) = $entry.ProcessingStatus
                $failedSheet.Cells.Item($row, 2) = $entry.FileName
                $failedSheet.Cells.Item($row, 3) = $entry.Category
                $failedSheet.Cells.Item($row, 4) = $entry.ClaimNotes
                $failedSheet.Cells.Item($row, 5) = $entry.FileHash
                $failedSheet.Cells.Item($row, 6) = $entry.OriginalPath
                $row++
            }
            
            # Auto-fit columns
            for ($i = 1; $i -le $failedHeaders.Count; $i++) {
                $failedSheet.Columns.Item($i).AutoFit() | Out-Null
            }
        }
        
        # Save workbook
        $workbook.SaveAs($excelPath)
        $workbook.Close()
        $excel.Quit()
        
        Write-Log "Excel file created: $excelPath" "SUCCESS"
        return $excelPath
    }
    catch {
        Write-Log "Excel export error: $_" "ERROR"
        Write-Log "CSV files have been created instead" "WARNING"
        return $null
    }
}

# ============================================
# MAIN PROCESSING
# ============================================

function Start-InvoiceProcessing {
    $startTime = Get-Date
    
    Write-Log "========================================" "INFO"
    Write-Log "LM STUDIO INVOICE CATALOGING SYSTEM" "INFO"
    Write-Log "Financial Year: FY$FinancialYear" "INFO"
    Write-Log "ATO Work Expense Deductions" "INFO"
    Write-Log "========================================" "INFO"
    Write-Log "" "INFO"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites check failed. Exiting." "ERROR"
        return
    }
    
    Write-Log "" "INFO"
    
    # Load cache and failed files list
    $cache = Load-Cache
    $failedFiles = Load-FailedFiles
    
    Write-Log "Cache loaded: $($cache.Count) entries" "INFO"
    Write-Log "Failed files tracked: $($failedFiles.Count) entries" "INFO"
    Write-Log "" "INFO"
    
    # Get invoice files
    $files = Get-InvoiceFiles
    
    if ($files.Count -eq 0) {
        Write-Log "No invoice files found to process" "WARNING"
        Write-Log "Checked folder: $($Config.InvoiceFolder)" "INFO"
        Write-Log "Supported formats: $($Config.FileExtensions -join ', ')" "INFO"
        return
    }
    
    # Filter files based on retry mode
    if ($RetryFailed) {
        Write-Log "RETRY MODE: Processing only failed files" "INFO"
        $filesToProcess = @()
        foreach ($failedEntry in $failedFiles) {
            $file = $files | Where-Object { $_.FullName -eq $failedEntry.FilePath }
            if ($file) {
                $filesToProcess += $file
            }
        }
        $files = $filesToProcess
        Write-Log "Found $($files.Count) failed files to retry" "INFO"
    }
    
    Write-Log "" "INFO"
    
    $processedInvoices = @()
    $successCount = 0
    $failCount = 0
    $cachedCount = 0
    $skippedCount = 0
    $fileIndex = 0
    
    # Process files
    foreach ($file in $files) {
        $fileIndex++
        Write-Log "[$fileIndex/$($files.Count)] Processing: $($file.Name)" "INFO"
        
        # Calculate file hash for duplicate detection
        $fileHash = Get-FileHash-MD5 -FilePath $file.FullName
        
        if (-not $fileHash) {
            Write-Log "Could not calculate file hash, skipping file" "ERROR"
            $failCount++
            continue
        }
        
        # Check if file is in cache (already processed)
        $cachedEntry = Find-InCache -Cache $cache -FileHash $fileHash
        if ($cachedEntry) {
            Write-Log "DUPLICATE FOUND: File already processed (cached)" "WARNING"
            Write-Log "Original: $($cachedEntry.FileName) | Processed: $($cachedEntry.ProcessedDate)" "INFO"
            
            # Use cached data
            $processedInvoices += [PSCustomObject]@{
                FileName = $file.Name
                FileType = $file.Extension.ToLower()
                FilePath = $file.FullName
                ProcessedDateTime = Get-Date
                Data = $cachedEntry.ExtractedData
                Category = $cachedEntry.Category
                Deduction = $cachedEntry.Deduction
                ProcessingStatus = "Cached (Duplicate)"
                FileHash = $fileHash
                MovedTo = "N/A - Duplicate"
            }
            
            $cachedCount++
            continue
        }
        
        # Check if file has failed too many times
        $failedEntry = $failedFiles | Where-Object { $_.FilePath -eq $file.FullName }
        if ($failedEntry -and $failedEntry.AttemptCount -ge $Config.MaxRetryAttempts) {
            Write-Log "SKIPPED: File has failed $($failedEntry.AttemptCount) times (max: $($Config.MaxRetryAttempts))" "WARNING"
            
            # Add to processed list as skipped
            $processedInvoices += [PSCustomObject]@{
                FileName = $file.Name
                FileType = $file.Extension.ToLower()
                FilePath = $file.FullName
                ProcessedDateTime = Get-Date
                Data = [PSCustomObject]@{
                    vendor_name = "N/A"
                    vendor_abn = ""
                    invoice_number = ""
                    invoice_date = ""
                    due_date = ""
                    subtotal = 0.00
                    tax = 0.00
                    total = 0.00
                    currency = "AUD"
                    description = "Skipped - Too many failures"
                    line_items = @()
                }
                Category = "Failed/Skipped"
                Deduction = [PSCustomObject]@{
                    Category = "Failed/Skipped"
                    TotalAmount = 0.00
                    WorkUsePercentage = 0
                    DeductibleAmount = 0.00
                    ClaimMethod = "Not Applicable"
                    ClaimNotes = "File skipped after $($failedEntry.AttemptCount) failed attempts"
                    AtoReference = "N/A"
                    RequiresDocumentation = @("Manual review required")
                }
                ProcessingStatus = "Skipped (Max retries exceeded)"
                FileHash = $fileHash
                MovedTo = "N/A - Not moved"
            }
            
            $skippedCount++
            continue
        }

        try {
            switch ($file.Extension.ToLower()) {
                ".pdf" { $invoiceText = Extract-TextFromPDF -PdfPath $file.FullName }
                ".png" { $invoiceText = Extract-TextFromImage -ImagePath $file.FullName }
                ".jpg" { $invoiceText = Extract-TextFromImage -ImagePath $file.FullName }
                ".jpeg" { $invoiceText = Extract-TextFromImage -ImagePath $file.FullName }
                ".gif" { $invoiceText = Extract-TextFromImage -ImagePath $file.FullName }
                ".doc" { $invoiceText = Extract-TextFromWord -WordPath $file.FullName }
                ".docx" { $invoiceText = Extract-TextFromWord -WordPath $file.FullName }
                ".xls" { $invoiceText = Extract-TextFromExcel -ExcelPath $file.FullName }
                ".xlsx" { $invoiceText = Extract-TextFromExcel -ExcelPath $file.FullName }
                ".eml" { $invoiceText = Extract-TextFromEmail -EmailPath $file.FullName }
                ".msg" { $invoiceText = Extract-TextFromEmail -EmailPath $file.FullName }
                default {
                    Write-Log "Unsupported file type: $($file.Extension) - filing as Non-Invoice" "WARNING"
                    $invoiceText = $null
                }
            }

            # Handle files with no extractable text
            if ([string]::IsNullOrWhiteSpace($invoiceText)) {
                Write-Log "No text extracted - filing as Non-Invoice" "WARNING"
                
                $attemptCount = if ($failedEntry) { $failedEntry.AttemptCount + 1 } else { 1 }
                $failedFiles = Add-ToFailedFiles -FailedFiles $failedFiles -FilePath $file.FullName `
                    -FileName $file.Name -ErrorReason "No text content extracted" -AttemptCount $attemptCount
                
                # Create a placeholder entry for non-invoice files
                $processedInvoices += [PSCustomObject]@{
                    FileName = $file.Name
                    FileType = $file.Extension.ToLower()
                    FilePath = $file.FullName
                    ProcessedDateTime = Get-Date
                    Data = [PSCustomObject]@{
                        vendor_name = "N/A"
                        vendor_abn = ""
                        invoice_number = ""
                        invoice_date = ""
                        due_date = ""
                        subtotal = 0.00
                        tax = 0.00
                        total = 0.00
                        currency = "AUD"
                        description = "No text content extracted"
                        line_items = @()
                    }
                    Category = "Non-Invoice/Other"
                    Deduction = [PSCustomObject]@{
                        Category = "Non-Invoice/Other"
                        TotalAmount = 0.00
                        WorkUsePercentage = 0
                        DeductibleAmount = 0.00
                        ClaimMethod = "Not Applicable"
                        ClaimNotes = "File contains no extractable invoice data"
                        AtoReference = "N/A"
                        RequiresDocumentation = @("Manual review required")
                    }
                    ProcessingStatus = "Failed (No text)"
                    FileHash = $fileHash
                    MovedTo = "N/A - Not moved"
                }
                
                $failCount++
                continue
            }

            # Extract data using LM Studio
            $extractedData = Invoke-LMStudioExtraction -InvoiceText $invoiceText -FileName $file.Name

            if ($extractedData) {
                # Categorize expense
                $description = if ($extractedData.line_items -and $extractedData.line_items[0]) {
                    $extractedData.line_items[0].description
                } else {
                    ""
                }

                $category = Get-ExpenseCategory -Description $description `
                    -VendorName $extractedData.vendor_name `
                    -LineItemText ($extractedData.description)

                # Calculate deduction
                $deduction = Calculate-ATODeduction -InvoiceData $extractedData `
                    -Category $category `
                    -FilePath $file.FullName

                # Move file to processed folder
                $movedPath = $file.FullName
                if ($Config.MoveProcessedFiles) {
                    $movedPath = Move-ProcessedFile -SourcePath $file.FullName `
                        -Category $category `
                        -InvoiceDate $extractedData.invoice_date
                }

                $processedInvoices += [PSCustomObject]@{
                    FileName = $file.Name
                    FileType = $file.Extension.ToLower()
                    FilePath = $movedPath
                    ProcessedDateTime = Get-Date
                    Data = $extractedData
                    Category = $category
                    Deduction = $deduction
                    ProcessingStatus = "Success"
                    FileHash = $fileHash
                    MovedTo = $movedPath
                }

                # Add to cache
                $cache = Add-ToCache -Cache $cache -FileName $file.Name -FileHash $fileHash `
                    -ExtractedData $extractedData -Category $category -Deduction $deduction

                # Remove from failed files if it was there
                if ($failedEntry) {
                    $failedFiles = Remove-FromFailedFiles -FailedFiles $failedFiles -FilePath $file.FullName
                    Write-Log "Removed from failed files list (successful retry)" "INFO"
                }

                Write-Log ([string]::Format("Extracted: {0} - {1} - ${2}", $extractedData.vendor_name, $category, $extractedData.total)) "SUCCESS"
                $successCount++
            }
            else {
                Write-Log "Failed to extract data - adding to failed files" "WARNING"
                
                $attemptCount = if ($failedEntry) { $failedEntry.AttemptCount + 1 } else { 1 }
                $failedFiles = Add-ToFailedFiles -FailedFiles $failedFiles -FilePath $file.FullName `
                    -FileName $file.Name -ErrorReason "AI extraction failed" -AttemptCount $attemptCount
                
                # Create a placeholder entry for failed extractions
                $processedInvoices += [PSCustomObject]@{
                    FileName = $file.Name
                    FileType = $file.Extension.ToLower()
                    FilePath = $file.FullName
                    ProcessedDateTime = Get-Date
                    Data = [PSCustomObject]@{
                        vendor_name = "N/A"
                        vendor_abn = ""
                        invoice_number = ""
                        invoice_date = ""
                        due_date = ""
                        subtotal = 0.00
                        tax = 0.00
                        total = 0.00
                        currency = "AUD"
                        description = "AI extraction failed"
                        line_items = @()
                    }
                    Category = "Non-Invoice/Other"
                    Deduction = [PSCustomObject]@{
                        Category = "Non-Invoice/Other"
                        TotalAmount = 0.00
                        WorkUsePercentage = 0
                        DeductibleAmount = 0.00
                        ClaimMethod = "Not Applicable"
                        ClaimNotes = "Could not extract invoice data from file"
                        AtoReference = "N/A"
                        RequiresDocumentation = @("Manual review required")
                    }
                    ProcessingStatus = "Failed (AI extraction)"
                    FileHash = $fileHash
                    MovedTo = "N/A - Not moved"
                }
                
                $failCount++
            }
        }
        catch {
            Write-Log ("Error processing file: " + $_) "ERROR"
            
            $attemptCount = if ($failedEntry) { $failedEntry.AttemptCount + 1 } else { 1 }
            $failedFiles = Add-ToFailedFiles -FailedFiles $failedFiles -FilePath $file.FullName `
                -FileName $file.Name -ErrorReason "Processing error: $_" -AttemptCount $attemptCount
            
            # Create a placeholder entry for error cases
            $processedInvoices += [PSCustomObject]@{
                FileName = $file.Name
                FileType = $file.Extension.ToLower()
                FilePath = $file.FullName
                ProcessedDateTime = Get-Date
                Data = [PSCustomObject]@{
                    vendor_name = "N/A"
                    vendor_abn = ""
                    invoice_number = ""
                    invoice_date = ""
                    due_date = ""
                    subtotal = 0.00
                    tax = 0.00
                    total = 0.00
                    currency = "AUD"
                    description = "Processing error: $_"
                    line_items = @()
                }
                Category = "Non-Invoice/Other"
                Deduction = [PSCustomObject]@{
                    Category = "Non-Invoice/Other"
                    TotalAmount = 0.00
                    WorkUsePercentage = 0
                    DeductibleAmount = 0.00
                    ClaimMethod = "Not Applicable"
                    ClaimNotes = "Error during processing"
                    AtoReference = "N/A"
                    RequiresDocumentation = @("Manual review required")
                }
                ProcessingStatus = "Failed (Error)"
                FileHash = $fileHash
                MovedTo = "N/A - Not moved"
            }
            
            $failCount++
        }
    }
    
    Write-Log "" "INFO"
    
    # Save cache and failed files
    Save-Cache -Cache $cache
    Save-FailedFiles -FailedFiles $failedFiles
    
    Write-Log "Cache saved with $($cache.Count) entries" "SUCCESS"
    Write-Log "Failed files list saved with $($failedFiles.Count) entries" "SUCCESS"
    Write-Log "" "INFO"
    
    # Export results
    if ($processedInvoices.Count -gt 0) {
        $exportData = Export-ToCSV -ProcessedInvoices $processedInvoices
        $excelPath = Export-ToExcel -ProcessedInvoices $processedInvoices -ExportData $exportData
        
        Write-Log "" "INFO"
        Write-Log "Files created:" "SUCCESS"
        Write-Log "  - $($exportData.CatalogPath)" "SUCCESS"
        Write-Log "  - $($exportData.SummaryPath)" "SUCCESS"
        
        if ($excelPath) {
            Write-Log "  - $excelPath" "SUCCESS"
            Write-Log "Opening Excel file..." "INFO"
            Start-Process $excelPath
        }
        else {
            Write-Log "Opening CSV files..." "INFO"
            Start-Process $($exportData.CatalogPath)
        }
    }
    
    # Final summary
    Write-Log "" "INFO"
    Write-Log "=== PROCESSING COMPLETE ===" "INFO"
    Write-Log "Successful: $successCount files" "SUCCESS"
    Write-Log "Failed: $failCount files" $(if ($failCount -eq 0) { "SUCCESS" } else { "WARNING" })
    Write-Log "Cached (Duplicates): $cachedCount files" "INFO"
    Write-Log "Skipped (Max retries): $skippedCount files" $(if ($skippedCount -eq 0) { "SUCCESS" } else { "WARNING" })
    Write-Log "Total processed: $($processedInvoices.Count) invoices" "SUCCESS"
    Write-Log "Time elapsed: $(Get-ElapsedTime $startTime)" "INFO"
    Write-Log "" "INFO"
    
    if ($failCount -gt 0) {
        Write-Log "TIP: Run with -RetryFailed switch to retry failed files" "INFO"
    }
}

# ============================================
# SCRIPT EXECUTION
# ============================================

# Create log folder if doesn't exist
if (-not (Test-Path $Config.LogFolder)) {
    New-Item -ItemType Directory -Path $Config.LogFolder -Force | Out-Null
}

# If script was called with -CheckOnly, run the environment checks and exit
if ($CheckOnly) {
    $envOk = Test-Environment
    if ($envOk) { Write-Log "Environment check passed" "SUCCESS"; exit 0 } else { Write-Log "Environment check failed" "ERROR"; exit 1 }
}

# Run with error handling
try {
    Start-InvoiceProcessing
}
catch {
    Write-Log "Fatal error: $_" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "DEBUG"
}

Write-Log 'Press any key to exit...' 'INFO'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
