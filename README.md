# Email_Marketing_Campaign_Automation
This is an automation to web scrape prospects' emails to carry out an email marketing campaign.

An end-to-end Python automation pipeline designed to streamline lead generation and cold outreach. This project scrapes prospect data from the web, cleans and analyzes it, and automatically sends personalized bulk emails using a free Gmail account.

## 🌟 Key Features

* **Automated Lead Generation:** Utilizes a custom web scraper built with Selenium and BeautifulSoup to extract contact information and data from potential prospects.
* **Data Processing & Cleaning:** Leverages Pandas to clean, format, and structure the scraped data into an easy-to-use CSV file.
* **Dynamic Email Templating:** Injects personalized data (like First Name, Company, etc.) from the CSV directly into a custom HTML email template.
* **Zero-Cost Bulk Emailing:** Bypasses expensive email marketing software by utilizing the official Gmail API to send emails directly from a standard, free Gmail account.
* **Google API Integration:** Uses the Google Drive API and Gmail API for seamless file handling and email delivery.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Data Scraping:** Selenium, BeautifulSoup4
* **Data Manipulation:** Pandas
* **APIs:** Google Gmail API, Google Drive API
* **Templating:** HTML/CSS with Python String Formatting

## 📋 Prerequisites

Before running this project, you will need:
1. Python 3.7+ installed on your machine.
2. A Google Cloud Console account.
3. A Google Cloud Project with the **Gmail API** and **Google Drive API** enabled.
4. OAuth 2.0 Client ID credentials downloaded as `credentials.json`.

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/email-marketing-automation.git
   cd email-marketing-automation
