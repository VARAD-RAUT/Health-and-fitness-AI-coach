# 💪 AI Health & Fitness Assistant

A comprehensive health and fitness application powered by **Azure OpenAI GPT-5**, **Azure Blob Storage**, and **Streamlit**.

## 🚀 Features

### 7 Core Modules

1. **👤 User Profile** - Create and manage your health profile with BMI calculation
2. **🥗 AI Diet Plan** - Generate 7-day personalized meal plans with macro tracking
3. **🏋️ AI Workout Plan** - Create 7-day workout routines tailored to your goals
4. **📸 Food Analyzer** - Upload food photos for instant nutrition analysis via GPT-5 Vision
5. **📓 Daily Log** - Track meals, workouts, water intake, and mood
6. **📊 Weekly Report** - Get AI-powered health insights and recommendations
7. **💬 Chat Assistant** - Ask questions about nutrition, fitness, and health

### Additional Features

- **Dark-themed glassmorphism UI** with modern design
- **Azure Blob Storage** for all data persistence
- **PDF generation** for plans and reports
- **Email delivery** via Azure Communication Services
- **Session state management** for seamless user experience

---

## 📋 Prerequisites

- **Python 3.9+**
- **Azure Account** with:
  - Azure OpenAI service (GPT-5 deployment)
  - Azure Blob Storage account
  - Azure Communication Services (optional, for email)
- **Streamlit** web framework

---

## 🔧 Setup Instructions

### 1. Clone/Download the Project

```bash
cd health-fitness-assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Azure Services

#### A. **Azure OpenAI**

1. Go to [Azure Portal](https://portal.azure.com)
2. Create or select your **Azure OpenAI** resource
3. Deploy a **GPT-5** model (or GPT-4)
4. Copy:
   - **Endpoint URL** (e.g., `https://your-resource.openai.azure.com/`)
   - **API Key**
   - **Deployment Name** (e.g., `gpt-5`)

#### B. **Azure Blob Storage**

1. Create a **Storage Account** in Azure Portal
2. In the storage account:
   - Create one container: `health-fitness-data`
3. Copy the **Connection String** from "Access Keys"

#### C. **Azure Communication Services** (Optional, for Email)

1. Create an **Email Communication Service** resource
2. Copy the **Connection String**
3. Add a verified sender email address
4. Get your **Sender Email** (typically in format: `donotreply@xxx.azurecomm.net`)

### 4. Create `.env` File

Create a `.env` file in the project root with your credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your-storage-account;AccountKey=your-key;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=health-fitness-data

# Azure Communication Services (Optional)
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://your-resource.communication.azure.com/;accesskey=your-access-key
SENDER_EMAIL=donotreply@your-domain.azurecomm.net
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 📁 Project Structure

```
health-fitness-assistant/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
│
├── config/
│   ├── __init__.py
│   └── azure_config.py             # Azure services configuration
│
├── modules/
│   ├── __init__.py
│   ├── profile.py                  # User profile management
│   ├── diet_plan.py                # 7-day meal planning
│   ├── workout_plan.py             # 7-day workout planning
│   ├── food_analyzer.py            # Food photo analysis
│   ├── daily_log.py                # Daily tracking
│   ├── weekly_report.py            # Weekly AI insights
│   └── email_sender.py             # Email delivery
│
├── utils/
│   ├── __init__.py
│   ├── blob_helper.py              # Blob Storage operations
│   ├── datalake_helper.py          # Data Lake zone management
│   └── pdf_generator.py            # PDF report generation
│
├── templates/
│   └── email_template.html         # Email HTML template
│
└── assets/                         # Images and static files
```

---

## 🔄 Data Flow

### User Profile
1. User fills form in Profile page
2. BMI calculated, daily calorie target estimated
3. Saved to Blob Storage: `users/{username}.json`

### Diet/Workout Plans
1. GPT-5 generates personalized plan based on profile
2. User can view, download as PDF, or email
3. Saved to Blob Storage: `diet-plans/{username}.json` or `workout-plans/{username}.json`

### Food Analysis
1. User uploads food photo
2. GPT-5 Vision analyzes image
3. Nutrition data extracted and saved to Blob Storage: `food-analysis/{username}/{datetime}.json`
4. Photo stored in Blob Storage: `food-images/{username}/{datetime}.jpg`

### Daily Logs
1. User logs meals, workouts, water, mood
2. Saved to Blob Storage: `daily-logs/{username}/{date}.json`

### Weekly Report
1. Last 7 days of logs retrieved from Blob Storage
2. GPT-5 analyzes logs and generates insights
3. Report saved to Blob Storage: `reports/{username}.json`

---

## 🛠️ Error Handling

The application includes comprehensive error handling:

- **Azure Service Failures**: Gracefully degrades with user-friendly messages
- **Missing Environment Variables**: Detailed error messages pointing to `.env` setup
- **API Rate Limits**: Displays error and suggests retry
- **Invalid Inputs**: Form validation with clear error messages
- **Storage Failures**: Session data preserved, users can retry

---

## 📊 Blob Storage Structure

All data is stored in a single container: `health-fitness-data`

```
health-fitness-data/
├── users/
│   └── {username}.json              # User profiles
├── diet-plans/
│   └── {username}.json              # Generated diet plans
├── workout-plans/
│   └── {username}.json              # Generated workout plans
├── daily-logs/
│   └── {username}/
│       └── {date}.json              # Daily meal & activity logs
├── food-images/
│   └── {username}/
│       └── {datetime}.jpg           # Food photos
├── food-analysis/
│   └── {username}/
│       └── {datetime}.json          # Nutrition analysis results
└── reports/
    └── {username}.json              # Weekly health reports
```

---

## 🔐 Security Notes

- ⚠️ **Never commit `.env` file** to version control
- Store sensitive credentials in Azure Key Vault for production
- Use environment-specific `.env` files (`.env.local`, `.env.prod`)
- Regularly rotate Azure API keys
- Use service principals for CI/CD pipelines

---

## 🚨 Troubleshooting

### "AZURE_OPENAI_ENDPOINT is not set"
**Fix**: Ensure `.env` file exists in project root with all required variables

### "BlobServiceClient creation failed"
**Fix**: Verify `AZURE_STORAGE_CONNECTION_STRING` is correct and account exists

### "Module not found" errors
**Fix**: Install dependencies: `pip install -r requirements.txt`

### Streamlit not found
**Fix**: `pip install streamlit` or reinstall: `pip install -r requirements.txt`

### GPT-5 returns empty responses
**Fix**: Check deployment name matches your Azure OpenAI deployment

---

## 📈 Performance Tips

1. **Cache AI responses**: Store generated plans in session state to avoid re-generation
2. **Batch Data Lake writes**: Combine multiple writes when possible
3. **Optimize images**: Compress food photos before upload (~2MB max)
4. **Monitor API usage**: Check Azure OpenAI usage in portal

---

## 🔄 Session State Features

The app maintains session state for:
- Current user profile
- Generated diet/workout plans
- Chat history
- Daily meal logs
- Daily water intake
- Current UI page

**Note**: Session state resets on browser refresh. Use "Load Saved Profile" feature to restore previous session.

---

## 📚 API Endpoints Used

### Azure OpenAI
- `POST /deployments/{deployment}/chat/completions` - Text & vision analysis
- API Version: `2024-02-15-preview`

### Azure Blob Storage
- `PUT /container/blob` - Upload
- `GET /container/blob` - Download
- `POST /containers` - Create container

### Azure Communication Services
- `POST /emails:send` - Send email

---

## 🎯 Future Enhancements

- [ ] User authentication & login system
- [ ] Social sharing of achievements
- [ ] Integration with fitness trackers (Fitbit, Apple Health)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Community challenges
- [ ] Real-time workout coaching via video

---

## 📄 License

MIT License - See LICENSE file for details

---

## 💬 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Azure service logs in Portal
3. Verify `.env` configuration
4. Check Streamlit documentation: https://docs.streamlit.io

---

## 🙏 Acknowledgments

- **Azure OpenAI** for GPT-5 & vision capabilities
- **Streamlit** for the web framework
- **ReportLab** for PDF generation
- **Plotly** for interactive charts

---

**Happy coding! 💚 Stay healthy!**
