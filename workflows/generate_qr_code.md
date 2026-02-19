# Generate QR Code

## Objective
Generate a QR code from user-provided content and save it as PNG + PDF
to the archive folder. Push to GitHub for permanent backup.

## When to Use
User asks to create/make/generate a QR code for any content type:
URLs, text, email addresses, phone numbers, WiFi credentials, etc.

## Required Inputs
- **Content**: The data to encode (URL, text, email, phone, WiFi info)

## Optional Inputs
- **Label**: A human-friendly name (defaults to the content itself)
- **Type**: url, text, email, phone, wifi, other (auto-detected if omitted)

## Tool
`tools/generate_qr.py`

## How to Run

### Basic URL
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "https://example.com"
```

### With custom label
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "https://example.com" --label "Example Website"
```

### Email
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "paul@example.com"
```

### Phone
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "+1-555-123-4567" --label "Office Phone"
```

### WiFi
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;" --label "Home WiFi"
```

### Plain text
```
python "C:/Users/Paul/Desktop/Claude Projects/qr-generator/tools/generate_qr.py" --content "Hello World" --type text
```

## WiFi Format Reference
`WIFI:T:{security};S:{network_name};P:{password};;`
- Security: WPA, WEP, or nopass
- Example: `WIFI:T:WPA;S:Coffee Shop WiFi;P:guest2026;;`

When Paul says "make a QR for my WiFi", ask for:
1. Network name (SSID)
2. Password
3. Security type (assume WPA if not specified — it's the most common)

Then construct: `--content "WIFI:T:WPA;S:{name};P:{password};;"`

## Expected Output
- PNG saved to `archive/{label}_{date}.png`
- PDF saved to `archive/{label}_{date}.pdf`

## After Generation
Push the new files to GitHub:
```
cd "C:/Users/Paul/Desktop/Claude Projects/qr-generator" && git add archive/ && git commit -m "Add QR code: {label}" && git push
```

## Edge Cases
- If content is a bare domain like "example.com", the tool auto-prepends https://
- Duplicate filenames on same day get -2, -3 suffixes automatically
- If pip install fails, check internet connection
