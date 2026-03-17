# 🚀 Quick Reference Card

Keep this handy while setting up Azure services!

---

## 🔑 Environment Variables `.env` Template

```env
# ════════════════════════════════════════════
# Azure OpenAI (REQUIRED)
# ════════════════════════════════════════════
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_KEY=YOUR_API_KEY_HERE
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5

# ════════════════════════════════════════════
# Azure Blob Storage (REQUIRED)
# ════════════════════════════════════════════
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=health-fitness-data

# ════════════════════════════════════════════
# Azure Communication Services (OPTIONAL)
# ════════════════════════════════════════════
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://YOUR_RESOURCE.communication.azure.com/;accesskey=YOUR_KEY
SENDER_EMAIL=donotreply@noreply.azurecomm.net
```

---

## 📝 Azure Portal Checklist

### Azure OpenAI
- [ ] Resource created
- [ ] GPT-5 model deployed
- [ ] Endpoint URL copied: `________________________________`
- [ ] API Key copied: `________________________________`
- [ ] Deployment name: `________________________________`

### Blob Storage
- [ ] Storage account created
- [ ] Container `health-fitness-data` created
- [ ] Connection string copied: `________________________________`

### Communication Services (Optional)
- [ ] Service created
- [ ] Email domain configured
- [ ] Connection string copied: `________________________________`
- [ ] Sender email: `________________________________`

---

## 🔄 Setup Flow

```
1. Azure Portal → Create OpenAI Service
               → Deploy GPT-5 Model
               → Copy Endpoint & Key
                ↓
2. Azure Portal → Create Storage Account
               → Create 2 Containers
               → Copy Connection String
                ↓
3. Create .env → Paste all credentials
                ↓
4. pip install -r requirements.txt
                ↓
5. streamlit run app.py
                ↓
6. Test in browser http://localhost:8501
```

---

## 💻 Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Test connections
python test_openai.py
python test_blob.py
python test_email.py

# Check Python version
python --version

# Check if .env exists
test -f .env && echo "OK" || echo "Missing"

# List pip packages
pip list | grep azure
```

---

## 🎯 Key Azure Portal Paths

| What | Where |
|------|-------|
| OpenAI Endpoint | OpenAI Resource → Keys and Endpoint |
| OpenAI Key | OpenAI Resource → Keys and Endpoint |
| Deployments | Azure OpenAI Studio → Deployments |
| Storage Connection String | Storage Account → Access keys |
| Create Container | Storage Account → Containers → + Container |
| Email Connection String | Communication Services → Keys |
| Sender Email | Communication Services → Emails → Domains |

---

## 🚨 Common Values

**Default Region**: `East US` or `UK South`

**Container Name**:
- `health-fitness-data` (for all app storage)

**Deployment Name**: `gpt-5` (unless you named it differently)

**API Version**: `2024-02-15-preview` (built-in)

---

## ✅ Validation Commands

```bash
# Check OpenAI works
python << 'EOF'
from dotenv import load_dotenv
from config.azure_config import get_openai_client
load_dotenv()
client = get_openai_client()
print("✅ OpenAI OK")
EOF

# Check Blob works
python << 'EOF'
from dotenv import load_dotenv
from config.azure_config import get_blob_service_client
load_dotenv()
client = get_blob_service_client()
containers = [c.name for c in client.list_containers()]
print(f"✅ Blob OK: {containers}")
EOF
```

---

## 📊 Cost Quick Reference

| Service | Price | Notes |
|---------|-------|-------|
| Azure OpenAI (GPT-5) | $0.05 per 1K input tokens | Can use GPT-4 to save money |
| Blob Storage | $0.02-0.05/GB | 5GB free tier |
| Communication Services | $0.0004 per email | Optional feature |
| **Monthly (est.)** | **$1-10** | Very affordable |

---

## 🔗 Useful Links

- [Azure Portal](https://portal.azure.com)
- [Azure OpenAI Studio](https://oai.azure.com) - After creating OpenAI resource
- [Streamlit Docs](https://docs.streamlit.io)
- [OpenAI API Reference](https://platform.openai.com/docs/reference)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)

---

## ⏱️ Estimated Times

| Task | Time |
|------|------|
| Create OpenAI Resource | 5 min |
| Deploy GPT-5 Model | 5 min |
| Create Storage Account | 5 min |
| Create Containers | 2 min |
| Create Email Service | 10 min |
| Get All Credentials | 5 min |
| Create `.env` file | 2 min |
| Install Dependencies | 5 min |
| **TOTAL** | **~40 min** |

---

## 🎯 Success Indicators

When set up is done, you should see:

✅ No errors when running `streamlit run app.py`  
✅ App opens in browser at http://localhost:8501  
✅ Sidebar shows "👤 User Profile" as first page  
✅ Can create a profile and save it  
✅ Chat with AI returns responses  
✅ Downloads generate PDFs without errors  

---

## 🆘 Quick Troubleshooting

**Problem**: Module not found  
**Fix**: `pip install -r requirements.txt`

**Problem**: AZURE_OPENAI_ENDPOINT is not set  
**Fix**: Check `.env` file exists and has correct variable name

**Problem**: InvalidAuthentication error  
**Fix**: Check API key is correct (copy-paste from Azure Portal)

**Problem**: Container not found  
**Fix**: Check containers exist in Storage Account → Containers

**Problem**: App won't start  
**Fix**: Check Python version: `python --version` (need 3.9+)

---

## 📞 Getting Help

1. **Check docs**: [README.md](README.md) → Troubleshooting
2. **Check guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md) → Troubleshooting  
3. **Check tests**: Run `python test_openai.py` etc.
4. **Check Azure Portal**: Look at service logs/alerts
5. **Check `.env`**: Verify all credentials are correct

---

**Bookmark this page! You'll reference it during setup. Good luck! 💪**
