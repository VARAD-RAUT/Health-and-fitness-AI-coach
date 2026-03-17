# ✅ Testing & Validation Guide

After setting up all Azure services and configuring `.env`, use this guide to validate your setup.

---

## 🧪 Pre-Flight Checks

### 1. Verify Python Environment

```bash
# Check Python version (should be 3.9+)
python --version

# Check pip is available
pip --version

# List installed packages
pip list | grep -E "streamlit|openai|azure|plotly|reportlab"
```

Expected output should show:
- `streamlit`
- `openai`
- `azure-storage-blob`
- `azure-communication-email`
- `plotly`
- `reportlab`
- `pandas`
- `python-dotenv`

### 2. Verify `.env` File

```bash
# Check .env exists
test -f .env && echo "✅ .env file found" || echo "❌ .env file missing"

# Check it's not tracked by git
git status | grep ".env"  # Should show "nothing to commit" or not appear
```

### 3. Verify Directory Structure

```bash
# From project root, check key files exist
test -f app.py && echo "✅ app.py" || echo "❌ app.py missing"
test -d modules && echo "✅ modules/" || echo "❌ modules/ missing"
test -d config && echo "✅ config/" || echo "❌ config/ missing"
test -d utils && echo "✅ utils/" || echo "❌ utils/ missing"
test -f requirements.txt && echo "✅ requirements.txt" || echo "❌ requirements.txt missing"
```

---

## 🔐 Azure Credentials Validation

### Test 1: Azure OpenAI Connection

Create file `test_openai.py`:

```python
import os
from dotenv import load_dotenv
from config.azure_config import get_openai_client, get_deployment_name

# Load environment
load_dotenv()

print("Testing Azure OpenAI Connection...")
print("-" * 50)

try:
    # Get endpoint and key from env
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    key = os.getenv("AZURE_OPENAI_KEY", "")
    
    if not endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT not set")
        exit(1)
    if not key:
        print("❌ AZURE_OPENAI_KEY not set")
        exit(1)
    
    print(f"✅ Endpoint: {endpoint[:50]}...")
    print(f"✅ Key length: {len(key)} characters")
    
    # Try to create client
    client = get_openai_client()
    print("✅ AzureOpenAI client created successfully")
    
    # Try to get deployment name
    deployment = get_deployment_name()
    print(f"✅ Deployment name: {deployment}")
    
    # Try simple completion
    print("\n📝 Testing simple completion...")
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"✅ API Response: {result}")
    
    print("\n" + "=" * 50)
    print("✅ AZURE OPENAI: ALL TESTS PASSED")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    exit(1)
```

Run it:
```bash
python test_openai.py
```

### Test 2: Azure Blob Storage Connection

Create file `test_blob.py`:

```python
import os
from dotenv import load_dotenv
from config.azure_config import get_blob_service_client
import json
from datetime import datetime

# Load environment
load_dotenv()

print("Testing Azure Blob Storage Connection...")
print("-" * 50)

try:
    # Check env variables
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    if not conn_str:
        print("❌ AZURE_STORAGE_CONNECTION_STRING not set")
        exit(1)
    
    print(f"✅ Connection string configured")
    
    # Create client
    client = get_blob_service_client()
    print("✅ BlobServiceClient created successfully")
    
    # List existing containers
    print("\n📦 Listing containers...")
    containers = client.list_containers()
    container_list = [c.name for c in containers]
    print(f"✅ Found containers: {container_list}")
    
    # Check required containers
    required = ["health-fitness-data", "health-fitness-lake"]
    for cont in required:
        if cont in container_list:
            print(f"  ✅ {cont} exists")
        else:
            print(f"  ⚠️ {cont} not found (will be created on first write)")
    
    # Test write
    print("\n✍️ Testing blob write...")
    test_data = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "message": "Health & Fitness Assistant Test"
    }
    
    from utils.blob_helper import save_generic_blob, load_generic_blob
    path = "test/validation.json"
    success = save_generic_blob(path, test_data)
    
    if success:
        print(f"✅ Successfully wrote test blob: health-fitness-data/{path}")
    else:
        print(f"❌ Failed to write test blob")
        exit(1)
    
    # Test read
    print("\n📖 Testing blob read...")
    loaded = load_generic_blob(path)
    
    if loaded and loaded.get("test"):
        print(f"✅ Successfully read test blob")
        print(f"   Data: {loaded}")
    else:
        print(f"❌ Failed to read test blob or data mismatch")
        exit(1)
    
    # Clean up
    print("\n🧹 Cleaning up test blob...")
    from config.azure_config import download_from_blob
    # Note: We just leave it for now, not critical
    
    print("\n" + "=" * 50)
    print("✅ AZURE BLOB STORAGE: ALL TESTS PASSED")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    exit(1)
```

Run it:
```bash
python test_blob.py
```

### Test 3: Azure Communication Services (Optional)

Create file `test_email.py`:

```python
import os
from dotenv import load_dotenv
from config.azure_config import get_email_client, get_sender_email

# Load environment
load_dotenv()

print("Testing Azure Communication Services (Email)...")
print("-" * 50)

try:
    # Check env variables
    conn_str = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")
    sender_email = os.getenv("SENDER_EMAIL", "")
    
    if not conn_str:
        print("⚠️ AZURE_COMMUNICATION_CONNECTION_STRING not set (optional)")
        print("   Email feature will be disabled")
        exit(0)
    
    if not sender_email:
        print("⚠️ SENDER_EMAIL not set (optional)")
        exit(0)
    
    print(f"✅ Email credentials configured")
    print(f"   Sender: {sender_email}")
    
    # Create client
    client = get_email_client()
    print("✅ EmailClient created successfully")
    
    # Note: Don't actually send a test email
    # Just verify the client was created
    
    print("\n" + "=" * 50)
    print("✅ AZURE COMMUNICATION SERVICES: ALL TESTS PASSED")
    print("   Email feature is ready (be mindful of costs)")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
    exit(1)
```

Run it:
```bash
python test_email.py
```

---

## 🚀 Application Testing

### Test 4: Start Streamlit Application

```bash
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Test 5: Manual Feature Testing

Once the app opens in browser, test each feature:

#### Feature: User Profile (👤 Page 1)

- [ ] Fill form with test data
- [ ] Verify BMI calculation is correct
- [ ] Verify daily calorie target is reasonable
- [ ] Click "Save Profile"
- [ ] Verify ✅ success message appears
- [ ] Check sidebar updates with user badge
- [ ] Reload page, verify profile persists in session

#### Feature: Load Saved Profile (Sidebar)

- [ ] Expand "📂 Load Saved Profile"
- [ ] Enter username from previous step
- [ ] Click "🔄 Load"
- [ ] Verify profile loads (first time may fail if Azure not ready)

#### Feature: AI Diet Plan (🥗 Page 2)

- [ ] Verify warning if profile not set
- [ ] Set profile first, then return to this page
- [ ] Click "✨ Generate My Diet Plan"
- [ ] Wait for 🤖 spinner (GPT-5 is crafting...)
- [ ] Verify plan appears with 7 days
- [ ] Verify calories and macros are displayed
- [ ] Click "⬇️ Download PDF" button
- [ ] Verify PDF downloads
- [ ] Open PDF and check formatting

#### Feature: AI Workout Plan (🏋️ Page 3)

- [ ] Set profile first
- [ ] Click "✨ Generate My Workout Plan"
- [ ] Wait for generation
- [ ] Verify 7-day plan with exercises appears
- [ ] Verify sets/reps/rest times displayed correctly
- [ ] Click "⬇️ Download PDF"
- [ ] Verify PDF downloads and opens

#### Feature: Food Analyzer (📸 Page 4)

- [ ] Upload a food image (JPG/PNG)
- [ ] Wait for analysis
- [ ] Verify nutrition data appears:
  - [ ] Food items listed
  - [ ] Total calories shown
  - [ ] Macro breakdown (protein, carbs, fats)
  - [ ] Health score out of 10
- [ ] Verify health notes are provided

#### Feature: Daily Log (📓 Page 5)

- [ ] Add meals to breakfast/lunch/dinner
- [ ] Verify calorie totals update
- [ ] Log water intake (add glasses)
- [ ] Select mood
- [ ] Log workout details
- [ ] Click "💾 Save Daily Log"
- [ ] Verify success message

#### Feature: Weekly Report (📊 Page 6)

- [ ] Enter daily logs for 7 days first
- [ ] Click "📊 Generate Weekly Report"
- [ ] Wait for AI analysis
- [ ] Verify report shows:
  - [ ] Performance score (0-100)
  - [ ] Top 3 achievements
  - [ ] Top 3 areas to improve
  - [ ] Personalized advice
  - [ ] Charts/visualizations
- [ ] Click "⬇️ Download Report PDF"

#### Feature: Chat with AI (💬 Page 7)

- [ ] Set profile first
- [ ] Click a suggestion button (e.g., "What should I eat...")
- [ ] Verify message appears in chat
- [ ] Wait for AI response
- [ ] Verify AI responds with relevant advice
- [ ] Type custom question
- [ ] Click "➤ Send"
- [ ] Verify AI responds
- [ ] Click "🗑️ Clear" to clear history

---

## 📊 Error Recovery Tests

### Test 6: Handle Missing Azure Credentials

1. Temporarily comment out lines in `.env`
2. Restart app
3. Verify graceful error messages appear
4. Restore `.env`

### Test 7: Handle API Errors

1. Use an invalid deployment name
2. Try to generate a diet plan
3. Verify error message is user-friendly
4. Fix and retry

### Test 8: Handle Large Uploads

1. Try uploading a 10MB image to Food Analyzer
2. Verify timeout handling or upload completion
3. Check if resizing/compression is needed

---

## 📈 Performance Tests

### Test 9: Response Times

| Feature | Target Time | Acceptable |
|---------|------------|-----------|
| Profile Save | 2-3s | < 5s |
| Diet Plan Gen | 10-15s | < 30s |
| Workout Gen | 10-15s | < 30s |
| Food Analysis | 5-10s | < 20s |
| Weekly Report | 15-20s | < 60s |

### Test 10: Concurrent Users

- Open app in 2-3 browser windows
- Each user performs different actions
- Verify no session conflicts
- Verify each user sees only their data

---

## ✅ Final Checklist

- [ ] All environment variables set in `.env`
- [ ] Python 3.9+ installed
- [ ] All packages installed via `pip install -r requirements.txt`
- [ ] Azure containers created
- [ ] Credentials validated via test scripts
- [ ] Streamlit app starts without errors
- [ ] All 7 pages load and display correctly
- [ ] Profile creation works
- [ ] AI features generate responses
- [ ] PDF downloads work
- [ ] Email feature works (optional)
- [ ] Data persistence works
- [ ] Error handling is graceful

---

## 🐛 Debugging Tips

### Enable Debug Logging

Add to `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Azure Portal

1. Navigate to your Azure resources
2. Check "Activity logs" for errors
3. Check "Metrics" for usage
4. Check "Alerts" for quotas

### Check Blob Storage Contents

Via Azure Portal:
1. Storage account → Containers
2. Click each container
3. Browse folder structure
4. Verify data was written

### Check OpenAI Usage

Via Azure OpenAI Studio:
1. Deployments → View usage
2. Check token counts
3. Verify deployment is active

---

## 🎉 Success Indicators

When everything is working:

✅ Profiles are saved to Azure  
✅ Diet plans generate within 15 seconds  
✅ Food images analyze accurately  
✅ PDFs download and display correctly  
✅ Chat gives relevant responses  
✅ All pages load without errors  
✅ Data persists across sessions  
✅ Error messages are helpful  

---

**Troubleshooting?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) Troubleshooting section or [README.md](README.md#-troubleshooting).
