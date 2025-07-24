# Email Campaign Manager

A comprehensive email campaign management tool with Streamlit frontend for networking, job applications, and custom email campaigns.

## Features

- 🎯 **Multi-language Support**: English, French, Spanish, German, Italian
- 📧 **Multiple Campaign Types**: Networking, Job Applications, Custom
- 📎 **Attachment Management**: Common and language-specific attachments
- 🔄 **Template System**: Customizable email templates with variable substitution
- 📊 **Campaign Analytics**: Detailed reporting and logging
- 🧪 **Test Mode**: Preview campaigns without sending emails
- 🛡️ **Safe Sending**: Configurable delays and send limits

## Installation

### 1. Clone or Download Files

Create a new directory and save the following files:
- `email_campaign_bot.py` (Core module)
- `streamlit_app.py` (Frontend)
- `requirements.txt`
- `templates_networking.json` (Sample templates)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Gmail Setup (Recommended)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account Settings → Security
   - Select "2-Step Verification" → "App passwords"
   - Generate a new app password for "Mail"
   - Use this 16-character password in the application

### 4. Prepare Your Data

Create a contacts file (CSV or Excel) with the following columns:

**Required Columns:**
- `name`: Contact's full name
- `email`: Contact's email address

**Optional Columns:**
- `language`: Language code (en, fr, es, de, it)
- `company`: Company name
- `position`: Job title
- `source`: Where you found this contact
- `custom_message`: Personalized message for this contact
- `attachment`: Path to contact-specific attachment

**Sample CSV:**
```csv
name,email,language,company,position,source,custom_message
John Doe,john@example.com,en,TechCorp,CTO,LinkedIn,I'm interested in your AI work
Marie Martin,marie@example.fr,fr,InnovateFR,Director,Conference,Votre expertise m'intéresse
```

## Usage

### 1. Start the Application

```bash
streamlit run streamlit_app.py
```

### 2. Configure Email Settings

1. Go to the sidebar "Email Settings"
2. Enter your email credentials
3. Test the connection

### 3. Upload Contacts

1. Go to "Contacts" tab
2. Upload your CSV/Excel file
3. Verify the data preview

### 4. Setup Templates

1. Go to "Templates" tab
2. Choose a template type or create custom
3. Customize templates for each language
4. Save templates for future use

### 5. Add Attachments

1. Go to "Attachments" tab
2. Upload common files (sent with all emails)
3. Upload language-specific files (CV in different languages)

### 6. Launch Campaign

1. Go to "Campaign" tab
2. Fill in sender information
3. Preview your emails
4. Enable test mode for first run
5. Launch campaign

### 7. Review Results

1. Go to "Results" tab
2. View campaign statistics
3. Download detailed logs

## Template Variables

Use these variables in your email templates:

### Contact Variables
- `{name}`: Contact's name
- `{email}`: Contact's email
- `{company}`: Contact's company
- `{position}`: Contact's position
- `{source}`: Where you found them (`{source_info}` adds "on " prefix)
- `{custom_message}`: Personalized message

### Sender Variables
- `{sender_name}`: Your name
- `{sender_title}`: Your title
- `{sender_contact}`: Your contact information
- `{meeting_duration}`: Requested meeting length
- `{call_to_action}`: Your call to action

### Custom Variables
Add any custom variables in JSON format in the campaign settings.

## File Structure

```
email-campaign/
├── email_campaign_bot.py      # Core functionality
├── streamlit_app.py           # Streamlit frontend
├── requirements.txt           # Dependencies
├── templates_networking.json  # Sample templates
├── attachments/              # Attachment storage
│   ├── common_file.pdf
│   ├── en_resume.pdf
│   └── fr_cv.pdf
└── contacts_sample.csv       # Sample contacts
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use app passwords** instead of your main Gmail password
3. **Start with test mode** to verify your setup
4. **Limit send rates** to avoid being flagged as spam
5. **Review templates** to ensure professional content

## Troubleshooting

### Email Connection Issues
- Verify app password is correct (16 characters)
- Check SMTP settings (Gmail: smtp.gmail.com:587)
- Ensure 2FA is enabled on Gmail

### Template Issues
- Check for unclosed `{variables}`
- Verify JSON format for custom variables
- Test with preview function

### File Upload Issues
- Ensure CSV/Excel files have required columns
- Check file encoding (UTF-8 recommended)
- Verify attachment file paths exist

## Advanced Usage

### Custom SMTP Servers

The application supports other email providers:

- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom**: Enter your provider's SMTP settings

### Batch Processing

For large campaigns:
1. Split contacts into smaller batches
2. Use appropriate delays between sends
3. Monitor sending quotas
4. Save campaign logs for tracking

### Template Development

Create sophisticated templates:
1. Use HTML for rich formatting
2. Add conditional content based on variables
3. Test across different email clients
4. Maintain professional appearance

## License

This project is open source. Use responsibly and in compliance with email regulations and anti-spam laws.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review your email provider's documentation
3. Test with small batches first
4. Ensure compliance with relevant regulations
