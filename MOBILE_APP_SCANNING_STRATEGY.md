# 📱 Mobile App Security Scanning - Complete Strategy

## 🎯 THE CHALLENGE

Mobile apps require different scanning techniques than websites:
- Not accessible via URL
- Compiled binaries (APK for Android, IPA for iOS)
- Need to analyze code, permissions, libraries
- Must check for malware, vulnerabilities, data leaks

---

## 📋 IMPLEMENTATION APPROACHES

### Option 1: File Upload + Static Analysis ⭐ RECOMMENDED

**How it works:**
1. User uploads APK (Android) or IPA (iOS) file
2. Backend extracts and analyzes:
   - Permissions requested
   - API keys & secrets in code
   - Libraries & dependencies
   - Code vulnerabilities
   - SSL pinning
   - Data storage practices
   - Network security config

**Pros:**
- Works for any app (public or private)
- Deep analysis possible
- No Play Store API needed
- Works offline

**Cons:**
- Users must have APK/IPA file
- Storage space needed (~50-200MB per app)
- Processing time (~2-5 minutes)

**Tools to use:**
- **Android:** APKTool, jadx, MobSF, Androguard
- **iOS:** ipautil, class-dump, MobSF
- **Both:** OWASP MASVS checks

---

### Option 2: Play Store / App Store Link

**How it works:**
1. User provides app URL (e.g., play.google.com/store/apps/details?id=com.example)
2. Backend downloads APK using:
   - Google Play API (unofficial)
   - APK downloader services
3. Analyze downloaded file

**Pros:**
- Easier for users (just paste link)
- Always get latest version
- Can track updates automatically

**Cons:**
- Requires third-party services
- May violate Play Store TOS
- Can't analyze private/unreleased apps
- Rate limits

**Services:**
- APKPure API
- APKMirror scraping
- evozi.com API (APK Downloader)

---

### Option 3: SDK Integration (Advanced)

**How it works:**
1. User adds SDK to their app
2. SDK reports to your platform:
   - Runtime security events
   - API calls
   - Network requests
   - Crash reports

**Pros:**
- Real-time monitoring
- Production app insights
- User behavior data

**Cons:**
- Requires code integration
- Only for apps user owns
- Privacy concerns
- Complex implementation

---

## 🔍 WHAT TO SCAN FOR

### Android APK Analysis

#### 1. Permissions Analysis ⚠️
```java
// Extract from AndroidManifest.xml
<uses-permission android:name="android.permission.READ_CONTACTS"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>

// Risk scoring:
HIGH RISK:
- READ_CONTACTS, READ_SMS, RECORD_AUDIO
- ACCESS_FINE_LOCATION
- READ_CALL_LOG

MEDIUM RISK:
- CAMERA, WRITE_EXTERNAL_STORAGE
- ACCESS_COARSE_LOCATION

LOW RISK:
- INTERNET, VIBRATE
- ACCESS_NETWORK_STATE
```

**Security Issues:**
- ❌ Excessive permissions (asking for more than needed)
- ❌ Dangerous permissions without justification
- ❌ Location tracking in non-location apps

#### 2. Hardcoded Secrets 🔑
```bash
# Scan decompiled code for:
- API keys: "AIzaSy...", "sk_live_..."
- Passwords: "password", "admin123"
- URLs: "https://api.internal.company.com"
- Private keys: "-----BEGIN PRIVATE KEY-----"
- Database credentials
- Firebase config
- AWS keys
```

**Tools:**
```bash
# Use regex patterns
grep -r "AIzaSy" decompiled/
grep -r "sk_live_" decompiled/
grep -r "api_key" decompiled/
grep -r "password.*=" decompiled/
```

#### 3. Insecure Data Storage 💾
```java
// Check for:
SharedPreferences.MODE_WORLD_READABLE  // BAD - accessible by all apps
SQLite databases without encryption
Files in /sdcard/ with sensitive data
Log statements with sensitive info
```

#### 4. Insecure Communication 🌐
```xml
<!-- Check AndroidManifest.xml -->
<application android:usesCleartextTraffic="true">  <!-- BAD -->

<!-- Check network_security_config.xml -->
<domain-config cleartextTrafficPermitted="true">   <!-- BAD -->
```

#### 5. Code Vulnerabilities 🐛
```java
// SQL Injection
db.rawQuery("SELECT * FROM users WHERE id=" + userId);  // BAD

// WebView vulnerabilities
webView.setJavaScriptEnabled(true);  // Risky
webView.getSettings().setAllowFileAccess(true);  // Risky

// Insecure crypto
Cipher.getInstance("DES");  // BAD - use AES
MessageDigest.getInstance("MD5");  // BAD - use SHA-256
```

#### 6. Third-Party Libraries 📚
```
// Check for vulnerable versions:
okhttp < 4.9.3  → Vulnerability CVE-2021-0341
gson < 2.8.9    → DoS vulnerability
retrofit < 2.9.0 → Security issue
```

#### 7. Code Obfuscation
```java
// Check if ProGuard/R8 enabled
- Minification: Classes renamed (a.b.c instead of com.example.Utils)
- Obfuscation: Method names scrambled
- Missing: Easy to reverse engineer
```

---

### iOS IPA Analysis

#### 1. Binary Analysis
```bash
# Extract Info.plist
unzip app.ipa
plutil -convert xml1 Payload/*.app/Info.plist

# Check:
- Bundle ID
- Permissions (NSLocationWhenInUseUsageDescription, etc.)
- URL schemes
- App Transport Security settings
```

#### 2. Network Security
```xml
<!-- Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>  <!-- BAD - allows HTTP -->
</dict>
```

#### 3. Jailbreak Detection
```objective-c
// Check if app has jailbreak detection
// Good security practice
```

#### 4. Certificate Pinning
```swift
// Check for SSL pinning implementation
// Good: App validates server certificate
// Bad: No pinning - vulnerable to MITM
```

---

## 🛠️ IMPLEMENTATION PLAN

### Phase 1: Basic APK Scanner (Week 1)

**Step 1: Add Mobile App Asset Type**

```sql
-- Update Asset type enum
ALTER TYPE asset_type ADD VALUE 'mobile_app_android';
ALTER TYPE asset_type ADD VALUE 'mobile_app_ios';

-- Add mobile app specific columns
ALTER TABLE assets ADD COLUMN app_file_path VARCHAR(500);
ALTER TABLE assets ADD COLUMN app_package_name VARCHAR(255);
ALTER TABLE assets ADD COLUMN app_version VARCHAR(50);
ALTER TABLE assets ADD COLUMN app_size_mb FLOAT;
```

**Step 2: File Upload Endpoint**

```python
# app/api/assets.py

@router.post("/mobile-app/upload")
async def upload_mobile_app(
    file: UploadFile,
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload APK or IPA file for scanning."""
    
    # Validate file type
    if not file.filename.endswith(('.apk', '.ipa')):
        raise HTTPException(400, "Only APK or IPA files allowed")
    
    # Check file size (max 500MB)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    if file_size > 500 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 500MB)")
    
    file.file.seek(0)
    
    # Save to storage
    file_path = f"uploads/apps/{uuid.uuid4()}/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create asset
    asset_type = 'mobile_app_android' if file.filename.endswith('.apk') else 'mobile_app_ios'
    
    asset = Asset(
        company_id=current_user.company_id,
        name=name,
        type=asset_type,
        value=file.filename,
        app_file_path=file_path,
        app_size_mb=file_size / (1024 * 1024)
    )
    
    db.add(asset)
    db.commit()
    
    # Trigger scan
    from app.services.mobile_scan_service import mobile_scanner
    mobile_scanner.scan_apk(asset.id)
    
    return {"asset_id": str(asset.id), "message": "Upload successful"}
```

**Step 3: Mobile Scan Service**

```python
# app/services/mobile_scan_service.py

import subprocess
import json
import os
from typing import List, Dict

class MobileScanService:
    """Mobile app security scanner."""
    
    def scan_apk(self, asset_id: str):
        """Scan Android APK file."""
        
        # Get asset
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        apk_path = asset.app_file_path
        
        # Extract APK
        extract_dir = f"temp/extracted/{asset_id}"
        os.makedirs(extract_dir, exist_ok=True)
        
        subprocess.run([
            "apktool", "d", apk_path, 
            "-o", extract_dir, 
            "-f"
        ])
        
        # Analyze
        findings = []
        
        # 1. Check permissions
        findings.extend(self._check_permissions(extract_dir))
        
        # 2. Scan for secrets
        findings.extend(self._scan_secrets(extract_dir))
        
        # 3. Check network security
        findings.extend(self._check_network_security(extract_dir))
        
        # 4. Analyze libraries
        findings.extend(self._check_libraries(extract_dir))
        
        # Calculate score
        score = self._calculate_mobile_score(findings)
        
        # Save results
        scan = Scan(
            asset_id=asset_id,
            status="completed",
            score=score,
            findings_count=len(findings)
        )
        db.add(scan)
        
        for finding in findings:
            db.add(Finding(
                scan_id=scan.id,
                asset_id=asset_id,
                **finding
            ))
        
        db.commit()
        
        # Cleanup
        shutil.rmtree(extract_dir)
    
    def _check_permissions(self, extract_dir: str) -> List[Dict]:
        """Check AndroidManifest.xml for dangerous permissions."""
        findings = []
        
        manifest_path = f"{extract_dir}/AndroidManifest.xml"
        
        # Parse manifest
        import xml.etree.ElementTree as ET
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        dangerous_perms = {
            'READ_CONTACTS': 'high',
            'READ_SMS': 'critical',
            'RECORD_AUDIO': 'high',
            'ACCESS_FINE_LOCATION': 'high',
            'READ_CALL_LOG': 'high',
            'CAMERA': 'medium'
        }
        
        for perm in root.findall('.//uses-permission'):
            perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
            
            for dangerous, severity in dangerous_perms.items():
                if dangerous in perm_name:
                    findings.append({
                        'severity': severity,
                        'category': 'Permissions',
                        'title': f'Dangerous Permission: {dangerous}',
                        'description': f'App requests {perm_name}',
                        'recommendation': 'Ensure this permission is necessary and justified'
                    })
        
        return findings
    
    def _scan_secrets(self, extract_dir: str) -> List[Dict]:
        """Scan for hardcoded secrets."""
        findings = []
        
        # Regex patterns
        patterns = {
            'API Key': r'api[_-]?key["\s]*[:=]["\s]*([A-Za-z0-9_-]{20,})',
            'AWS Key': r'AKIA[0-9A-Z]{16}',
            'Firebase': r'AIzaSy[A-Za-z0-9_-]{33}',
            'Private Key': r'-----BEGIN (RSA |DSA )?PRIVATE KEY-----'
        }
        
        # Scan all files
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(('.java', '.xml', '.smali')):
                    file_path = os.path.join(root, file)
                    
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        
                        for secret_type, pattern in patterns.items():
                            import re
                            if re.search(pattern, content):
                                findings.append({
                                    'severity': 'critical',
                                    'category': 'Hardcoded Secrets',
                                    'title': f'{secret_type} Found in Code',
                                    'description': f'Hardcoded {secret_type} detected in {file}',
                                    'recommendation': 'Remove hardcoded secrets, use secure storage'
                                })
        
        return findings
    
    def _check_network_security(self, extract_dir: str) -> List[Dict]:
        """Check for insecure network configuration."""
        findings = []
        
        manifest_path = f"{extract_dir}/AndroidManifest.xml"
        
        import xml.etree.ElementTree as ET
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        # Check cleartext traffic
        app = root.find('.//application')
        if app is not None:
            cleartext = app.get('{http://schemas.android.com/apk/res/android}usesCleartextTraffic')
            if cleartext == 'true':
                findings.append({
                    'severity': 'high',
                    'category': 'Network Security',
                    'title': 'Cleartext Traffic Allowed',
                    'description': 'App allows unencrypted HTTP traffic',
                    'recommendation': 'Disable cleartext traffic, use HTTPS only'
                })
        
        return findings

mobile_scanner = MobileScanService()
```

---

### Phase 2: Frontend UI (Week 2)

**Add Mobile App Upload**

```tsx
// frontend/app/dashboard/assets/page.tsx

const [showMobileUpload, setShowMobileUpload] = useState(false);
const [uploadFile, setUploadFile] = useState<File | null>(null);

// Add button
<button onClick={() => setShowMobileUpload(true)}>
  📱 Add Mobile App
</button>

// Modal
{showMobileUpload && (
  <div className="modal">
    <h2>Upload Mobile App</h2>
    <input
      type="file"
      accept=".apk,.ipa"
      onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
    />
    <button onClick={handleMobileAppUpload}>
      Upload & Scan
    </button>
  </div>
)}

const handleMobileAppUpload = async () => {
  const formData = new FormData();
  formData.append('file', uploadFile!);
  formData.append('name', assetName);
  
  const res = await fetch('/api/assets/mobile-app/upload', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  if (res.ok) {
    alert('App uploaded! Scanning in progress...');
    loadAssets();
  }
};
```

---

### Phase 3: Advanced Features (Month 2)

**1. App Store Integration**
```python
# Download from Play Store
from gpapi.googleplay import GooglePlayAPI

def download_from_play_store(package_name: str):
    api = GooglePlayAPI()
    api.login()
    
    # Download APK
    data = api.download(package_name)
    
    with open(f'{package_name}.apk', 'wb') as f:
        for chunk in data.get('file').get('data'):
            f.write(chunk)
```

**2. Automated Updates**
```python
# Check for app updates
def check_app_updates():
    apps = db.query(Asset).filter(
        Asset.type == 'mobile_app_android',
        Asset.app_package_name != None
    ).all()
    
    for app in apps:
        latest_version = get_play_store_version(app.app_package_name)
        if latest_version != app.app_version:
            # Download and scan new version
            download_and_scan(app.app_package_name)
```

**3. Dynamic Analysis (Advanced)**
```python
# Run app in emulator and monitor
def dynamic_analysis(apk_path: str):
    # Start Android emulator
    emulator = AndroidEmulator()
    emulator.start()
    
    # Install app
    emulator.install(apk_path)
    
    # Monitor:
    # - Network requests
    # - File system access
    # - API calls
    # - Permissions usage
    
    findings = emulator.monitor(duration=300)  # 5 minutes
    
    return findings
```

---

## 📊 MOBILE APP FINDINGS EXAMPLES

### Critical Issues:
- ❌ Hardcoded API keys in code
- ❌ Private keys in APK
- ❌ SQL injection vulnerabilities
- ❌ Unencrypted sensitive data storage

### High Issues:
- ⚠️ Excessive permissions (READ_SMS in calculator app)
- ⚠️ Cleartext traffic allowed
- ⚠️ No certificate pinning
- ⚠️ Weak encryption (DES, MD5)

### Medium Issues:
- ⚙️ Outdated vulnerable libraries
- ⚙️ Missing obfuscation
- ⚙️ Debug mode enabled
- ⚙️ Exported activities without protection

### Low Issues:
- ℹ️ Missing backup rules
- ℹ️ Large app size
- ℹ️ Too many permissions
- ℹ️ No jailbreak detection

---

## 🎯 RECOMMENDED IMPLEMENTATION

### Start Simple (Week 1-2):

**Phase 1: APK Upload & Basic Analysis**
1. Add file upload endpoint
2. Use APKTool to extract
3. Check 5 key things:
   - Permissions
   - Hardcoded secrets
   - Network security
   - Cleartext traffic
   - Dangerous code patterns
4. Generate report

**Tools needed:**
```bash
pip install androguard
pip install apktool
pip install pycrypto
```

**Cost:** ~$0 (all open source)
**Time:** 2-3 hours implementation

### Phase 2: Advanced Analysis (Month 2)
- Play Store integration
- iOS support
- Library vulnerability database
- Dynamic analysis

---

## 💰 BUSINESS MODEL

### Pricing:
- **Free:** 1 app, monthly scans
- **Starter ($29/mo):** 5 apps, weekly scans
- **Professional ($99/mo):** 25 apps, daily scans
- **Enterprise:** Unlimited, API access

### Market:
- African fintech apps (M-Pesa, etc.)
- E-commerce apps
- Government apps
- Banking apps
- Healthcare apps

---

## 🚀 QUICK START

Want me to implement Phase 1 (APK Upload & Basic Analysis)?

It will include:
1. File upload endpoint
2. APK extraction
3. Permission analysis
4. Secret scanning
5. Network security check
6. Report generation

**Time: 2-3 hours**

Should I build it now? 🛠️
