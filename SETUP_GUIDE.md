# 🔧 Azure Setup Guide

Complete step-by-step instructions to set up all Azure services for the AI Health & Fitness Assistant.

---

## ✅ Checklist

- [ ] Azure Account created
- [ ] Azure OpenAI service deployed
- [ ] GPT-4 model deployed
- [ ] Azure Blob Storage account created
- [ ] Storage containers created
- [ ] `.env` file configured
- [ ] Application tested

---

## 📝 Step 1: Azure OpenAI Setup

### 1.1 Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource**
3. Search for **"OpenAI"** → Select **"Azure OpenAI"**
4. Click **Create**
5. Fill in details:
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or select existing (e.g., `rg-health-fitness`)
   - **Region**: Select closest region (e.g., `East US`, `UK South`)
   - **Name**: e.g., `openai-health-fitness`
   - **Pricing Tier**: Standard (`STD`) is fine for development
6. Click **Review + create** → **Create**
7. Wait for deployment to complete

### 1.2 Deploy GPT-5 Model

1. In Azure Portal, go to your **Azure OpenAI** resource
2. Click **Go to Azure OpenAI Studio**
3. In Azure OpenAI Studio:
   - Click **Deployments** (left sidebar)
   - Click **Create new deployment**
   - **Model**: Select `gpt-5` or `gpt-4`
   - **Deployment name**: `gpt-5` (or your preference)
   - **Model version**: `4` (latest)
   - Click **Create**
4. Wait for deployment to complete

### 1.3 Get Credentials

1. In Azure Portal → Your OpenAI resource
2. Go to **Keys and Endpoint**
3. Copy:
   - **Endpoint URL**: Looks like `https://your-resource.openai.azure.com/`
   - **Key 1** or **Key 2**: Random string
4. Save these in a temporary note

**⚠️ Important**: Keep keys secret, never share or commit to GitHub!

---

## 💾 Step 2: Azure Blob Storage Setup

### 2.1 Create Storage Account

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource**
3. Search for **"Storage account"** → Click **Create**
4. Fill in details:
   - **Subscription**: Same as OpenAI
   - **Resource Group**: Same as OpenAI (e.g., `rg-health-fitness`)
   - **Storage account name**: Must be globally unique, lowercase (e.g., `healthfitnessstore123`)
   - **Region**: Same as OpenAI
   - **Performance**: Standard
   - **Redundancy**: Locally-redundant storage (LRS) for dev/test
5. Click **Review + create** → **Create**
6. Wait for deployment

### 2.2 Create Container

1. In Azure Portal → Your Storage account
2. Click **Containers** (left sidebar under "Data storage")
3. Click **+ Container**
4. Create container:
   - **Name**: `health-fitness-data`
   - **Public access level**: Private
   - Click **Create**

### 2.3 Get Connection String

1. In your Storage account → **Access keys** (left sidebar)
2. Under "Default connection string", click **Copy**
3. Save this in a temporary note

Format looks like:
```
DefaultEndpointsProtocol=https;AccountName=xxx;AccountKey=xxx;EndpointSuffix=core.windows.net
```

---

## 📧 Step 3: Azure Communication Services (Optional)

**Skip if you don't need email functionality.**

### 3.1 Create Communication Services Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **+ Create a resource**
3. Search for **"Communication Services"** → Click **Create**
4. Fill in details:
   - **Subscription**: Same as others
   - **Resource Group**: Same (e.g., `rg-health-fitness`)
   - **Name**: e.g., `communication-health`
   - **Data location**: Select region
5. Click **Create**
6. Wait for deployment

### 3.2 Add Email Channel

1. In Azure Portal → Your Communication Services resource
2. Click **Emails** (left sidebar)
3. Click **Domains**
4. Click **Connect domain** or **Create Azure managed domain**
5. For testing, select **Create Azure managed domain**:
   - **Subdomain**: e.g., `noreply`
   - Azure will create: `noreply@xxx.azurecomm.net`
6. Click **Create**
7. Wait for verification (can take a few minutes)

### 3.3 Get Connection String

1. In Communication Services → **Keys** (left sidebar)
2. Under "Connection string", click **Copy**
3. Also copy the **Primary key**

Looks like:
```
endpoint=https://your-resource.communication.azure.com/;accesskey=xxx
```

### 3.4 Get Sender Email

1. In Communication Services → **Emails** → **Domains**
2. Find your managed domain
3. Copy the **Mail From address** (e.g., `donotreply@noreply.azurecomm.net`)

**⚠️ Note**: You must use the exact sender email provided; you cannot change it to a custom domain without additional verification.

---

## 📄 Step 4: Create `.env` File

In the project root directory, create a file named `.env` with:

```env
# ════════════════════════════════════════════
# REQUIRED: Azure OpenAI Configuration
# ════════════════════════════════════════════
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-from-step-1
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5

# ════════════════════════════════════════════
# REQUIRED: Azure Storage Configuration
# ════════════════════════════════════════════
AZURE_STORAGE_CONNECTION_STRING=your-connection-string-from-step-2
BLOB_CONTAINER_NAME=health-fitness-data

# ════════════════════════════════════════════
# OPTIONAL: Azure Communication Services (Email)
# ════════════════════════════════════════════
AZURE_COMMUNICATION_CONNECTION_STRING=your-connection-string-from-step-3
SENDER_EMAIL=donotreply@noreply.azurecomm.net
```

**⚠️ Security Warning**:
- ✅ Add `.env` to `.gitignore` to prevent accidental commits
- ✅ Never share your `.env` file
- ✅ Use different keys for dev/staging/production
- ✅ Rotate keys periodically

---

## 🔑 Verify Credentials

### Test Azure OpenAI Connection

```bash
python -c "
from config.azure_config import get_openai_client, get_deployment_name
try:
    client = get_openai_client()
    print('✅ Azure OpenAI connected successfully')
    print(f'Deployment: {get_deployment_name()}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Test Blob Storage Connection

```bash
python -c "
from config.azure_config import get_blob_service_client
try:
    client = get_blob_service_client()
    containers = client.list_containers()
    print('✅ Blob Storage connected successfully')
    for container in containers:
        print(f'  - {container.name}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Test Email Connection (if configured)

```bash
python -c "
from config.azure_config import get_email_client, get_sender_email
try:
    client = get_email_client()
    print('✅ Communication Services connected successfully')
    print(f'Sender: {get_sender_email()}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

---

## 🚀 Run Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🆘 Troubleshooting

### Issue: "AZURE_OPENAI_ENDPOINT is not set"

**Solution**:
1. Check `.env` file exists in project root
2. Check for typos in environment variable names (exact case matters)
3. Run: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('AZURE_OPENAI_ENDPOINT'))"`

### Issue: "Invalid API key"

**Solution**:
1. Go to Azure Portal → OpenAI resource → Keys and Endpoint
2. Copy the correct key (Key 1 or Key 2, both work)
3. Update `.env` and save
4. Restart the Streamlit app

### Issue: "Container not found"

**Solution**:
1. Go to Azure Portal → Storage account → Containers
2. Verify the container exists: `health-fitness-data`
3. If missing, create it following Step 2.2

### Issue: "BlobServiceClient creation failed"

**Solution**:
1. Go to Azure Portal → Storage account → Access keys
2. Copy the entire "Default connection string"
3. Paste into `.env` under `AZURE_STORAGE_CONNECTION_STRING`
4. Ensure no extra spaces or line breaks

### Issue: Email not sending

**Solution**:
1. Check Communication Services resource was created
2. Check Email/Domains are properly configured
3. Verify `AZURE_COMMUNICATION_CONNECTION_STRING` is in `.env`
4. Verify `SENDER_EMAIL` matches your managed domain exactly
5. Try sending to a valid email (not .test domain)

### Issue: "GPT-5 model not found"

**Solution**:
1. Go to Azure Portal → OpenAI Studio → Deployments
2. Check that your deployment exists and is named `gpt-5` (or whatever you specified)
3. Update `AZURE_OPENAI_DEPLOYMENT_NAME` in `.env` to match
4. Click on the deployment to see its status (should be "Succeeded")

### Issue: Application runs but features fail

**Solution**:
1. Run verification scripts above to test each service
2. Check Azure Portal for quotas/limits
3. Look at Streamlit error messages for specific service errors
4. Check `requirements.txt` has all packages installed: `pip install -r requirements.txt`

---

## 📊 Azure Quotas & Limits

### Azure OpenAI

- **Default limit**: 200,000 TPM (tokens per minute)
- **Adjust in**: Azure Portal → Your OpenAI resource → Quotas
- For development, 200K TPM should be sufficient

### Blob Storage

- **Default limit**: 100 TB
- **Cost**: ~$20/month for 1TB

### Communication Services

- **Email**: Pay per email sent (~$0.0004 per email)
- **Free tier**: 25 free emails/month

---

## 💰 Cost Estimates (Monthly)

| Service | Free? | Cost/Month | Notes |
|---------|-------|-----------|-------|
| Azure OpenAI | No | $0.05-0.10/1K tokens | GPT-5 is more expensive than GPT-4 |
| Blob Storage | 5GB free | ~$0.02-0.05 | Cheap for most use cases |
| Communication Services | 25 emails | ~$1-5 | Only if using email feature |
| **Total** | | **~$1-10** | Very affordable for development |

To lower costs:
- Use GPT-4 instead of GPT-5
- Disable email feature if not needed
- Monitor usage in Azure Portal

---

## ✨ Best Practices

1. **Separate Dev & Prod**:
   - Use different Azure subscriptions or resource groups
   - Use different `.env` files (e.g., `.env.dev`, `.env.prod`)

2. **Key Rotation**:
   - Rotate API keys every 90 days
   - Use Azure Key Vault in production

3. **Monitoring**:
   - Check Azure Portal dashboards regularly
   - Set up cost alerts
   - Monitor API usage and errors

4. **Backup**:
   - Set blob storage redundancy to GRS for production
   - Enable versioning for important containers

5. **Security**:
   - Use managed identities instead of keys (production)
   - Enable Azure AD authentication
   - Restrict storage account access via firewalls

---

**Next Steps**: Return to [README.md](README.md) and run the application!
