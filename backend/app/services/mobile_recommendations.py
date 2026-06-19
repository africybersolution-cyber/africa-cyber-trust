"""
Mobile App Security Recommendations

Provides detailed, code-level remediation guidance with OWASP MASVS mapping.
"""
from typing import Dict


class MobileRecommendations:
    """Detailed recommendations for mobile app security findings."""

    @staticmethod
    def get_debuggable_fix() -> Dict[str, str]:
        """Fix for debuggable flag in production."""
        return {
            "title": "Remove Debuggable Flag from Production Build",
            "severity": "critical",
            "owasp_masvs": "MSTG-CODE-2, MSTG-RESILIENCE-2",
            "description": """The android:debuggable="true" flag allows attackers to:
- Attach debuggers to your running app
- Dump memory contents (extract secrets, tokens, keys)
- Modify app behavior at runtime
- Bypass security checks
- Extract business logic""",
            "fix": """
**STEP 1: Remove from AndroidManifest.xml**

In `app/src/main/AndroidManifest.xml`, ensure debuggable is NOT set to true:

```xml
<!-- ❌ NEVER DO THIS IN PRODUCTION -->
<application
    android:debuggable="true"
    ...>
</application>

<!-- ✅ CORRECT: Remove the line entirely or set to false -->
<application
    android:debuggable="false"
    ...>
</application>
```

**STEP 2: Use Build Variants in build.gradle**

In `app/build.gradle`:

```gradle
android {
    buildTypes {
        debug {
            debuggable true  // ✅ OK for debug builds
            applicationIdSuffix ".debug"
        }
        release {
            debuggable false  // ✅ REQUIRED for production
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.release
        }
    }
}
```

**STEP 3: Verify in APK**

```bash
# Check if APK is debuggable
aapt dump badging app-release.apk | grep debuggable
# Should return nothing or "debuggable='false'"
```

**VERIFICATION:**
- Build release APK: `./gradlew assembleRelease`
- Check APK: `aapt dump badging` should show no debuggable flag
- Install and test: App should work normally

**TIME:** 5 minutes | **DIFFICULTY:** Easy | **COST:** Free""",
            "references": [
                "https://developer.android.com/studio/publish/preparing",
                "https://owasp.org/www-project-mobile-app-security/",
                "https://mobile-security.gitbook.io/masvs/security-requirements/0x07-v2-data_storage_and_privacy_requirements"
            ]
        }

    @staticmethod
    def get_cleartext_traffic_fix() -> Dict[str, str]:
        """Fix for cleartext (HTTP) traffic."""
        return {
            "title": "Disable Cleartext HTTP Traffic",
            "severity": "critical",
            "owasp_masvs": "MSTG-NETWORK-1, MSTG-NETWORK-2",
            "description": """Allowing cleartext (HTTP) traffic exposes:
- User credentials transmitted in plain text
- Session tokens intercepted by attackers
- API keys visible on network
- Man-in-the-middle attacks
- Data tampering""",
            "fix": """
**STEP 1: Disable in AndroidManifest.xml**

In `app/src/main/AndroidManifest.xml`:

```xml
<application
    android:usesCleartextTraffic="false"
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

**STEP 2: Create Network Security Config**

Create `app/src/main/res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Enforce HTTPS for all domains -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Optional: Allow localhost for debug builds only -->
    <debug-overrides>
        <domain-config cleartextTrafficPermitted="true">
            <domain includeSubdomains="true">localhost</domain>
            <domain includeSubdomains="true">10.0.2.2</domain>
        </domain-config>
    </debug-overrides>
</network-security-config>
```

**STEP 3: Update All API Calls to HTTPS**

In your network code (Retrofit, OkHttp, etc.):

```kotlin
// ❌ NEVER DO THIS
const val BASE_URL = "http://api.example.com"

// ✅ ALWAYS USE HTTPS
const val BASE_URL = "https://api.example.com"
```

**VERIFICATION:**
- Build and run app
- Try making network requests
- HTTP requests should fail with SecurityException
- HTTPS requests should work normally

**TIME:** 15 minutes | **DIFFICULTY:** Easy | **COST:** Free (Let's Encrypt)""",
            "references": [
                "https://developer.android.com/training/articles/security-config",
                "https://owasp.org/www-project-mobile-app-security/",
                "https://letsencrypt.org/"
            ]
        }

    @staticmethod
    def get_ssl_pinning_fix() -> Dict[str, str]:
        """Implement SSL certificate pinning."""
        return {
            "title": "Implement SSL Certificate Pinning",
            "severity": "high",
            "owasp_masvs": "MSTG-NETWORK-3, MSTG-NETWORK-4",
            "description": """Without SSL pinning, attackers can:
- Intercept HTTPS traffic with fake certificates
- Steal credentials, tokens, API keys
- Modify API responses
- Inject malicious content
- Perform man-in-the-middle attacks""",
            "fix": """
**OPTION 1: Network Security Config (Easy)**

In `res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.yourapp.com</domain>
        <pin-set expiration="2027-01-01">
            <!-- Get SHA-256 hash: openssl x509 -in cert.pem -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64 -->
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <!-- Backup pin (different CA or future cert) -->
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

**OPTION 2: OkHttp CertificatePinner (Advanced)**

In your network module:

```kotlin
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient

val certificatePinner = CertificatePinner.Builder()
    .add("api.yourapp.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.yourapp.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")  // Backup
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**OPTION 3: TrustKit (Most Flexible)**

Add dependency in `build.gradle`:
```gradle
implementation 'com.datatheorem.android.trustkit:trustkit:1.1.5'
```

In `res/xml/network_security_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">api.yourapp.com</domain>
        <trustkit-config
            enforcePinning="true"
            includeSubdomains="true">
            <pin digest="sha256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="sha256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </trustkit-config>
    </domain-config>
</network-security-config>
```

**GET YOUR CERTIFICATE PINS:**

```bash
# Method 1: From live server
openssl s_client -connect api.yourapp.com:443 -servername api.yourapp.com < /dev/null | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64

# Method 2: From certificate file
openssl x509 -in certificate.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64
```

**VERIFICATION:**
- Build and run app
- Make API calls (should work)
- Use Charles Proxy or Burp Suite to intercept
- Should fail with SSL pinning error
- Check logs for "CertificateException" or "SSLHandshakeException"

**IMPORTANT:**
- Always have 2+ pins (backup in case primary expires)
- Set expiration date (prevents app breaking if cert changes)
- Test thoroughly before production release

**TIME:** 30-60 minutes | **DIFFICULTY:** Medium | **COST:** Free""",
            "references": [
                "https://developer.android.com/training/articles/security-config#CertificatePinning",
                "https://square.github.io/okhttp/4.x/okhttp/okhttp3/-certificate-pinner/",
                "https://github.com/datatheorem/TrustKit-Android"
            ]
        }

    @staticmethod
    def get_backup_flag_fix() -> Dict[str, str]:
        """Fix for backup flag."""
        return {
            "title": "Disable App Backup or Protect Sensitive Data",
            "severity": "high",
            "owasp_masvs": "MSTG-STORAGE-8",
            "description": """The allowBackup flag allows:
- Full app data backup via `adb backup`
- Restore on attacker's device
- Access to databases, SharedPreferences, files
- Extraction of tokens, keys, user data""",
            "fix": """
**OPTION 1: Disable Backup Completely (Most Secure)**

In `AndroidManifest.xml`:

```xml
<application
    android:allowBackup="false"
    android:fullBackupContent="false"
    ...>
</application>
```

**OPTION 2: Exclude Sensitive Data (Recommended)**

**Step 1:** In `AndroidManifest.xml`:

```xml
<application
    android:allowBackup="true"
    android:fullBackupContent="@xml/backup_rules"
    android:dataExtractionRules="@xml/data_extraction_rules"
    ...>
</application>
```

**Step 2:** Create `res/xml/backup_rules.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <!-- Exclude sensitive data -->
    <exclude domain="sharedpref" path="auth_prefs.xml"/>
    <exclude domain="sharedpref" path="user_tokens.xml"/>
    <exclude domain="database" path="sensitive_data.db"/>
    <exclude domain="file" path="encryption_keys/"/>

    <!-- Include everything else -->
    <include domain="sharedpref" path="."/>
    <include domain="database" path="."/>
    <include domain="file" path="."/>
</full-backup-content>
```

**Step 3:** For Android 12+ (API 31+), create `res/xml/data_extraction_rules.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="sharedpref" path="auth_prefs.xml"/>
        <exclude domain="database" path="sensitive_data.db"/>
    </cloud-backup>

    <device-transfer>
        <exclude domain="sharedpref" path="auth_prefs.xml"/>
        <exclude domain="database" path="sensitive_data.db"/>
    </device-transfer>
</data-extraction-rules>
```

**VERIFICATION:**

```bash
# Test backup
adb backup -f backup.ab -apk com.yourapp.package

# Extract backup (on Linux/Mac)
dd if=backup.ab bs=1 skip=24 | openssl zlib -d > backup.tar
tar -xvf backup.tar

# Check if sensitive files are present
# Should NOT see: auth_prefs.xml, user_tokens.xml, etc.
```

**BEST PRACTICES:**
- Never store sensitive data in SharedPreferences
- Use Android Keystore for keys/tokens
- Encrypt databases with SQLCipher
- Encrypt files with Android EncryptedFile API

**TIME:** 20 minutes | **DIFFICULTY:** Easy | **COST:** Free""",
            "references": [
                "https://developer.android.com/guide/topics/data/autobackup",
                "https://developer.android.com/guide/topics/data/backup",
                "https://owasp.org/www-project-mobile-app-security/"
            ]
        }

    @staticmethod
    def get_obfuscation_fix() -> Dict[str, str]:
        """Enable code obfuscation."""
        return {
            "title": "Enable Code Obfuscation with ProGuard/R8",
            "severity": "medium",
            "owasp_masvs": "MSTG-RESILIENCE-9",
            "description": """Without obfuscation:
- Class/method names reveal business logic
- Easy to decompile and understand code
- Competitors can steal algorithms
- Attackers can find vulnerabilities faster
- API endpoints and keys easier to find""",
            "fix": """
**STEP 1: Enable R8/ProGuard in build.gradle**

In `app/build.gradle`:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true  // ✅ Enable R8 shrinking
            shrinkResources true  // ✅ Remove unused resources
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

**STEP 2: Configure ProGuard Rules**

In `app/proguard-rules.pro`:

```proguard
# Keep your app's main classes
-keep public class com.yourapp.MainActivity
-keep public class com.yourapp.Application

# Keep Retrofit/OkHttp (if using)
-dontwarn okhttp3.**
-dontwarn retrofit2.**
-keepattributes Signature
-keepattributes Exceptions

# Keep Gson models (if using)
-keep class com.yourapp.models.** { *; }

# Keep Android components
-keep class * extends android.app.Activity
-keep class * extends android.app.Service
-keep class * extends android.content.BroadcastReceiver

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}

# Aggressive obfuscation
-optimizationpasses 5
-allowaccessmodification
-repackageclasses ''
```

**STEP 3: Test Thoroughly**

```bash
# Build release APK
./gradlew assembleRelease

# Check obfuscation
# 1. Decompile APK with jadx
jadx app-release.apk

# 2. Check class names
# Should see: a.class, b.class, c.class (obfuscated!)
# NOT: LoginActivity.class, UserRepository.class (readable)

# 3. Check mapping file
cat app/build/outputs/mapping/release/mapping.txt
# Shows original → obfuscated name mapping
```

**STEP 4: Save Mapping File**

Store `mapping.txt` for each release to deobfuscate crash reports:

```bash
# Upload to Firebase/Play Console
# Location: app/build/outputs/mapping/release/mapping.txt
```

**VERIFICATION:**
- App builds successfully
- All features work (test thoroughly!)
- Decompiled code shows single-letter class names
- Crash reports can be deobfuscated with mapping file

**COMMON ISSUES:**
- App crashes after obfuscation → Add `-keep` rules for affected classes
- Reflection breaks → Keep classes accessed via reflection
- Serialization issues → Keep model classes

**TIME:** 1-2 hours (including testing) | **DIFFICULTY:** Medium | **COST:** Free""",
            "references": [
                "https://developer.android.com/studio/build/shrink-code",
                "https://www.guardsquare.com/manual/configuration/usage",
                "https://github.com/krschultz/android-proguard-snippets"
            ]
        }

    @staticmethod
    def get_hardcoded_secrets_fix() -> Dict[str, str]:
        """Fix for hardcoded secrets."""
        return {
            "title": "Remove Hardcoded Secrets and Use Secure Storage",
            "severity": "critical",
            "owasp_masvs": "MSTG-STORAGE-14, MSTG-CRYPTO-1",
            "description": """Hardcoded secrets expose:
- API keys visible in decompiled code
- Backend access credentials
- Database connection strings
- Third-party service keys
- Cryptographic keys""",
            "fix": """
**STEP 1: Remove Hardcoded Secrets from Code**

```kotlin
// ❌ NEVER DO THIS
class ApiService {
    companion object {
        const val API_KEY = "sk_live_abc123xyz789"  // Visible in APK!
        const val AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
}

// ✅ DO THIS INSTEAD
class ApiService {
    private val apiKey: String by lazy {
        SecureStorage.getApiKey()  // Fetch from secure storage
    }
}
```

**STEP 2: Use BuildConfig for API Keys (Better)**

In `app/build.gradle`:

```gradle
android {
    defaultConfig {
        // Read from local.properties (NOT committed to Git)
        def localProperties = new Properties()
        localProperties.load(new FileInputStream(rootProject.file("local.properties")))

        buildConfigField "String", "API_KEY", "\"${localProperties.getProperty('api.key')}\""
        buildConfigField "String", "BASE_URL", "\"${localProperties.getProperty('api.url')}\""
    }
}
```

In `local.properties` (add to `.gitignore`):
```properties
api.key=sk_live_abc123xyz789
api.url=https://api.example.com
```

In code:
```kotlin
val apiKey = BuildConfig.API_KEY  // Still in APK, but not in Git
```

**STEP 3: Use Android Keystore (Most Secure)**

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

object SecureStorage {
    private const val KEYSTORE_ALIAS = "MyAppKeystore"
    private const val ANDROID_KEYSTORE = "AndroidKeyStore"

    fun storeApiKey(apiKey: String) {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }

        // Generate key if not exists
        if (!keyStore.containsAlias(KEYSTORE_ALIAS)) {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            )
            keyGenerator.init(
                KeyGenParameterSpec.Builder(
                    KEYSTORE_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(false)
                .build()
            )
            keyGenerator.generateKey()
        }

        // Encrypt and store
        val secretKey = keyStore.getKey(KEYSTORE_ALIAS, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        val encrypted = cipher.doFinal(apiKey.toByteArray())
        // Save encrypted bytes to SharedPreferences or file
    }

    fun getApiKey(): String {
        // Decrypt and return
        // ... (reverse of storeApiKey)
    }
}
```

**STEP 4: Use Environment Variables (Backend)**

For backend keys, fetch at runtime:

```kotlin
class ApiClient {
    suspend fun getApiKey(): String {
        // Fetch from your backend
        return api.fetchConfig().apiKey
    }
}
```

**STEP 5: Remove Secrets from Git History**

```bash
# If you already committed secrets
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secrets.kt' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (⚠️ WARNING: Destructive!)
git push --force --all
```

**VERIFICATION:**

```bash
# Decompile APK and search for secrets
jadx app-release.apk
grep -r "api_key\|secret\|password" jadx-output/

# Should find nothing or only encrypted values
```

**BEST PRACTICES:**
- ✅ Use Android Keystore for encryption keys
- ✅ Use BuildConfig for non-critical keys
- ✅ Fetch sensitive keys from backend at runtime
- ✅ Add `local.properties` to `.gitignore`
- ❌ Never commit secrets to Git
- ❌ Never log secrets (even in debug builds)

**TIME:** 1-3 hours | **DIFFICULTY:** Medium-Hard | **COST:** Free""",
            "references": [
                "https://developer.android.com/training/articles/keystore",
                "https://owasp.org/www-project-mobile-app-security/",
                "https://github.com/scottyab/secure-preferences"
            ]
        }

    @staticmethod
    def get_dangerous_permissions_fix(permissions: list) -> Dict[str, str]:
        """Fix for dangerous permissions."""
        perm_list = "\n".join([f"- {p}" for p in permissions])

        return {
            "title": f"Review and Minimize Dangerous Permissions ({len(permissions)} found)",
            "severity": "high" if len(permissions) > 10 else "medium",
            "owasp_masvs": "MSTG-PLATFORM-1",
            "description": f"""Your app requests {len(permissions)} dangerous permissions:

{perm_list}

Each permission:
- Increases attack surface
- Raises privacy concerns
- May trigger Play Store warnings
- Reduces user trust""",
            "fix": """
**STEP 1: Review Each Permission**

For each permission, ask:
1. Is it essential for core functionality?
2. Can we achieve the same goal without it?
3. When is it actually used?
4. Can we delay requesting it until needed?

**STEP 2: Remove Unused Permissions**

In `AndroidManifest.xml`:

```xml
<!-- ❌ Remove if not needed -->
<uses-permission android:name="android.permission.READ_CONTACTS"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.CAMERA"/>
```

**STEP 3: Request at Runtime (Not Install Time)**

```kotlin
// ❌ OLD: Requested at install time
// (All permissions in manifest)

// ✅ NEW: Request when needed
class MainActivity : AppCompatActivity() {
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            // Permission granted, proceed
            accessCamera()
        } else {
            // Explain why you need it
            showPermissionRationale()
        }
    }

    fun takePicture() {
        when {
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Already granted
                accessCamera()
            }
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                // Show explanation
                showPermissionRationale()
            }
            else -> {
                // Request permission
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }
}
```

**STEP 4: Use Alternatives Where Possible**

```kotlin
// Instead of READ_CONTACTS
// Use Contact Picker (no permission needed)
val pickContact = registerForActivityResult(ActivityResultContracts.PickContact()) { uri: Uri? ->
    // Handle selected contact
}

// Instead of CAMERA
// Use camera intent (no permission needed)
val takePicture = registerForActivityResult(ActivityResultContracts.TakePicture()) { success: Boolean ->
    // Handle picture
}

// Instead of ACCESS_FINE_LOCATION
// Use approximate location (less sensitive)
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
```

**STEP 5: Explain Why You Need Each Permission**

In your privacy policy and app description:
- Camera: "To scan QR codes"
- Location: "To find nearby stores"
- Contacts: "To invite friends"

**VERIFICATION:**

```bash
# Check permissions in APK
aapt dump permissions app-release.apk

# Should only show essential permissions
```

**PERMISSION ALTERNATIVES:**

| Permission | Alternative |
|-----------|-------------|
| READ_CONTACTS | Contact Picker API |
| CAMERA | Camera Intent |
| READ_EXTERNAL_STORAGE | Scoped Storage (Android 10+) |
| ACCESS_FINE_LOCATION | ACCESS_COARSE_LOCATION |
| READ_PHONE_STATE | Not needed in most cases |

**TIME:** 1-2 hours | **DIFFICULTY:** Medium | **COST:** Free""",
            "references": [
                "https://developer.android.com/training/permissions/requesting",
                "https://developer.android.com/about/versions/11/privacy/permissions",
                "https://owasp.org/www-project-mobile-app-security/"
            ]
        }


def get_recommendation(finding_type: str, **kwargs) -> Dict[str, str]:
    """Get detailed recommendation for a finding type."""

    recommendations_map = {
        "debuggable": MobileRecommendations.get_debuggable_fix,
        "cleartext_traffic": MobileRecommendations.get_cleartext_traffic_fix,
        "ssl_pinning": MobileRecommendations.get_ssl_pinning_fix,
        "backup_flag": MobileRecommendations.get_backup_flag_fix,
        "obfuscation": MobileRecommendations.get_obfuscation_fix,
        "hardcoded_secrets": MobileRecommendations.get_hardcoded_secrets_fix,
        "dangerous_permissions": lambda: MobileRecommendations.get_dangerous_permissions_fix(kwargs.get('permissions', []))
    }

    if finding_type in recommendations_map:
        return recommendations_map[finding_type]()

    return {
        "title": "Security Issue Detected",
        "severity": "medium",
        "owasp_masvs": "N/A",
        "description": "A security issue was detected in your mobile app.",
        "fix": "Please review the finding details and consult security best practices.",
        "references": ["https://owasp.org/www-project-mobile-app-security/"]
    }
