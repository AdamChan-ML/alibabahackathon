# 🇲🇾 Taxy: Make Your Tax Journey Easier

Taxy is an intelligent Malaysian tax relief assistant powered by AI and Alibaba Cloud technologies. It helps users manage their tax deductions, process receipts, and provides personalized tax advice using advanced AI models.

## 🌟 Features

- **Profile Management**: Personalized user profiles for tailored tax recommendations
- **Receipt Processing**: Automated receipt scanning and categorization
- **Interactive Dashboard**: Visual representation of tax-related data using QuickBI
- **Tax Deduction Suggestions**: AI-powered recommendations for maximizing tax relief
- **Tax Readiness Assessment**: Evaluate your tax preparation status
- **Knowledge Base Integration**: Built-in LHDN criteria for accurate tax guidance

## 🛠️ Tech Stack

- **App Deployment**
  - Alibaba Elastic Compute Service (ECS)
  - Production-grade hosting with scalability

- **AI/ML Components**
  - Qwen-VL: Vision-Language model for receipt processing
  - Qwen-Max: Advanced language model for tax advice
  - ModelStudio: AI model deployment and management

- **Data Storage & Processing**
  - Alibaba Object Storage Service (OSS)
  - Efficient storage for user data and documents

- **Analytics & Visualization**
  - QuickBI: Interactive business intelligence dashboard
  - Real-time tax insights and analytics

- **Frontend Interface**
  - Gradio: User-friendly web interface
  - Responsive and intuitive design

- **Knowledge Base**
  - ModelStudio-powered LHDN criteria database
  - Up-to-date tax regulations and guidelines

## 🚀 Getting Started

### Prerequisites

1. Python 3.x
2. Virtual Environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd devkaki-alibaba
```

2. Create and activate virtual environment (optional but recommended):
```bash
python -m venv alibabaenv
source alibabaenv/bin/activate  # On Windows: alibabaenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Set up your Alibaba Cloud credentials
- Configure ModelStudio API access
- Set up OSS bucket information

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:7860`

## 📁 Project Structure

- `app.py`: Main application entry point
- `Dashboard.py`: QuickBI dashboard integration
- `Profile.py`: User profile management
- `UploadReceipt.py`: Receipt processing functionality
- `TaxDeduction.py`: Tax deduction calculation and suggestions
- `TaxReadiness.py`: Tax preparation assessment
- `receipt_parser.py`: Receipt data extraction utilities
- `tax_relief_advisor.py`: AI-powered tax relief recommendations

## 🔐 Security

- Secure data storage in Alibaba OSS
- Encrypted user data transmission
- Compliance with data protection regulations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the terms included in the LICENSE file.

## 🙏 Acknowledgments

- Alibaba Cloud for infrastructure and AI services
- LHDN for tax regulation guidelines
- Contributors and maintainers

---

For support or inquiries, please open an issue in the repository. 
