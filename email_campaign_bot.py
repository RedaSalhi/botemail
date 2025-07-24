import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import time
import random
import os
import mimetypes
from datetime import datetime
import json
import re
from typing import Dict, List, Optional


class EmailCampaignBot:
    def __init__(self, email: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Initialize the Email Campaign Bot
        
        Args:
            email: Sender email address
            password: Email password (app password for Gmail)
            smtp_server: SMTP server address
            smtp_port: SMTP server port
        """
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.templates = {}
        self.subject_templates = {}

    def load_templates_from_file(self, templates_file: str):
        """Load email templates from JSON file"""
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.subject_templates = data.get('subjects', {})
            print(f"✅ Templates loaded from {templates_file}")
        except Exception as e:
            print(f"❌ Error loading templates: {e}")

    def add_template(self, language: str, template: str, subjects: List[str]):
        """Add a template for a specific language"""
        self.templates[language] = template
        self.subject_templates[language] = subjects

    def get_default_templates(self) -> Dict:
        """Get default templates for common use cases"""
        return {
            "networking": {
                "templates": {
                    "en": """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <p>Hi {name},</p>
                        
                        <p>I hope you're doing well! I'm {sender_name}, {sender_title}, and I recently came across your profile{source_info}. Your work and background really stood out to me.</p>
                        
                        <p>{custom_message}</p>
                        
                        <p>If you happen to be open to a brief {meeting_duration} chat, I'd be incredibly grateful. {call_to_action}</p>
                        
                        <p>Thanks so much for your time, and I hope we get a chance to connect!</p>
                        
                        <p>Warm regards,<br>
                        <strong>{sender_name}</strong><br>
                        {sender_contact}</p>
                    </body>
                    </html>
                    """,
                    "fr": """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <p>Bonjour {name},</p>
                        
                        <p>J'espère que vous allez bien. Je m'appelle {sender_name}, {sender_title}, et j'ai découvert votre profil{source_info}. J'ai été particulièrement intéressé par votre parcours.</p>
                        
                        <p>{custom_message}</p>
                        
                        <p>Si jamais vous avez {meeting_duration} à me consacrer pour un rapide échange, ce serait avec grand plaisir. {call_to_action}</p>
                        
                        <p>Un grand merci pour votre temps et votre attention.</p>
                        
                        <p>Bien cordialement,<br>
                        <strong>{sender_name}</strong><br>
                        {sender_contact}</p>
                    </body>
                    </html>
                    """
                },
                "subjects": {
                    "en": [
                        "Looking to Connect – {sender_name}",
                        "Seeking your insights – {sender_name}",
                        "Brief connection request – {sender_name}"
                    ],
                    "fr": [
                        "Demande d'échange – {sender_name}",
                        "Demande de connexion – {sender_name}",
                        "Échange professionnel – {sender_name}"
                    ]
                }
            },
            "job_application": {
                "templates": {
                    "en": """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <p>Dear {name},</p>
                        
                        <p>I am writing to express my interest in the {position} role at {company}. With my background in {background}, I believe I would be a strong fit for this position.</p>
                        
                        <p>{custom_message}</p>
                        
                        <p>I have attached my resume and would welcome the opportunity to discuss how my skills align with your team's needs.</p>
                        
                        <p>Thank you for your consideration.</p>
                        
                        <p>Best regards,<br>
                        <strong>{sender_name}</strong><br>
                        {sender_contact}</p>
                    </body>
                    </html>
                    """,
                    "fr": """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <p>Madame, Monsieur {name},</p>
                        
                        <p>Je me permets de vous contacter concernant le poste de {position} au sein de {company}. Fort de mon expérience en {background}, je pense correspondre au profil recherché.</p>
                        
                        <p>{custom_message}</p>
                        
                        <p>Vous trouverez ci-joint mon CV et je serais ravi de pouvoir échanger avec vous sur cette opportunité.</p>
                        
                        <p>Dans l'attente de votre retour.</p>
                        
                        <p>Cordialement,<br>
                        <strong>{sender_name}</strong><br>
                        {sender_contact}</p>
                    </body>
                    </html>
                    """
                },
                "subjects": {
                    "en": [
                        "Application for {position} - {sender_name}",
                        "{position} Position - {sender_name}",
                        "Interest in {position} Role - {sender_name}"
                    ],
                    "fr": [
                        "Candidature {position} - {sender_name}",
                        "Poste de {position} - {sender_name}",
                        "Intérêt pour le poste {position} - {sender_name}"
                    ]
                }
            }
        }

    def personalize_message(self, template: str, contact_data: Dict, global_vars: Dict = None) -> str:
        """
        Personalize message with contact data and global variables
        
        Args:
            template: Email template string
            contact_data: Individual contact information
            global_vars: Global variables (sender info, etc.)
        """
        message = template
        
        # Merge contact data with global variables
        all_vars = {}
        if global_vars:
            all_vars.update(global_vars)
        all_vars.update(contact_data)
        
        # Handle language-specific sender information
        email_language = contact_data.get('language', 'en')
        
        # Check if we have language-specific sender info
        if global_vars:
            # Look for language-specific variables first
            for key in ['sender_name', 'sender_title', 'sender_contact', 'meeting_duration', 'call_to_action']:
                lang_specific_key = f"{key}_{email_language}"
                if lang_specific_key in global_vars:
                    all_vars[key] = global_vars[lang_specific_key]
                elif key not in all_vars and key in global_vars:
                    # Fallback to general version if no language-specific version exists
                    all_vars[key] = global_vars[key]
        
        # Replace placeholders
        for key, value in all_vars.items():
            if pd.notna(value) and value is not None:
                placeholder = f"{{{key}}}"
                message = message.replace(placeholder, str(value))
        
        # Handle source info specially
        source_info = ""
        if 'source' in contact_data and pd.notna(contact_data['source']):
            source_info = f" on {contact_data['source']}"
        message = message.replace("{source_info}", source_info)
        
        # Clean up any remaining unfilled placeholders
        message = re.sub(r'\{[^}]*\}', '', message)
        
        return message

    def generate_subject(self, contact_data: Dict, language: str = "en", global_vars: Dict = None) -> str:
        """Generate personalized subject line"""
        if language not in self.subject_templates:
            language = "en"  # fallback
            
        subjects = self.subject_templates.get(language, ["Contact from {sender_name}"])
        subject_template = random.choice(subjects)
        
        # Merge variables for subject personalization
        all_vars = {}
        if global_vars:
            all_vars.update(global_vars)
        all_vars.update(contact_data)
        
        # Handle language-specific sender information for subject
        # Look for language-specific variables first
        if global_vars:
            for key in ['sender_name', 'sender_title', 'sender_contact', 'meeting_duration', 'call_to_action']:
                lang_specific_key = f"{key}_{language}"
                if lang_specific_key in global_vars:
                    all_vars[key] = global_vars[lang_specific_key]
                elif key not in all_vars and key in global_vars:
                    # Fallback to general version if no language-specific version exists
                    all_vars[key] = global_vars[key]
        
        # Replace placeholders in subject
        for key, value in all_vars.items():
            if pd.notna(value) and value is not None:
                placeholder = f"{{{key}}}"
                subject_template = subject_template.replace(placeholder, str(value))
        
        return subject_template

    def send_email(self, recipient: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send individual email with attachments"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'html'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._add_attachment(msg, file_path)
                    else:
                        print(f"⚠️ Attachment not found: {file_path}")

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()

            print(f"✅ Email sent successfully to {recipient}")
            return True

        except Exception as e:
            print(f"❌ Error sending email to {recipient}: {e}")
            return False

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add attachment to email message"""
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        main_type, sub_type = content_type.split('/', 1)
        filename = os.path.basename(file_path)

        if main_type == 'text':
            with open(file_path, 'r', encoding='utf-8') as fp:
                attachment = MIMEText(fp.read(), _subtype=sub_type)
        else:
            with open(file_path, 'rb') as fp:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(fp.read())
                encoders.encode_base64(attachment)

        attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(attachment)

    def run_campaign(self, 
                    contacts_file: str,
                    global_vars: Dict,
                    attachments_config: Dict = None,
                    send_limit: int = 5,
                    delay_min: int = 30,
                    delay_max: int = 60,
                    test_mode: bool = False,
                    default_language: str = "en") -> Dict:
        """
        Run email campaign
        
        Args:
            contacts_file: Path to contacts CSV/Excel file
            global_vars: Global variables (sender info, etc.)
            attachments_config: Configuration for attachments
            send_limit: Maximum emails to send per session
            delay_min/max: Delay between emails (seconds)
            test_mode: If True, don't actually send emails
            default_language: Default language if not specified in contact data
            
        Returns:
            Campaign statistics
        """
        
        # Load contacts
        try:
            if contacts_file.endswith('.xlsx'):
                df = pd.read_excel(contacts_file)
            else:
                df = pd.read_csv(contacts_file)
        except Exception as e:
            print(f"❌ Error loading contacts: {e}")
            return {"error": str(e)}

        print(f"📋 {len(df)} contacts loaded from {contacts_file}")

        # Validate required columns
        required_columns = ['name', 'email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

        # Check available templates
        available_languages = list(self.templates.keys())
        if not available_languages:
            error_msg = "No email templates loaded"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

        print(f"📝 Available templates: {', '.join(available_languages)}")

        successful_sends = 0
        failed_sends = 0
        campaign_log = []
        language_stats = {}

        for index, contact in df.iterrows():
            if successful_sends >= send_limit:
                print(f"🛑 Send limit of {send_limit} reached")
                break

            # Determine language with fallback logic
            contact_dict = contact.to_dict()
            
            # Priority: contact language > default language > first available template
            language = contact_dict.get('language', default_language)
            
            if language not in self.templates:
                # Try default language
                if default_language in self.templates:
                    language = default_language
                    print(f"⚠️ Language '{contact_dict.get('language', 'None')}' not available for {contact_dict.get('name', 'Unknown')}, using {default_language}")
                else:
                    # Use first available template
                    language = available_languages[0]
                    print(f"⚠️ Neither specified nor default language available for {contact_dict.get('name', 'Unknown')}, using {language}")
            
            # Track language usage
            if language not in language_stats:
                language_stats[language] = {'attempted': 0, 'successful': 0, 'failed': 0}
            language_stats[language]['attempted'] += 1
            
            template = self.templates[language]
            
            # Personalize message
            message = self.personalize_message(template, contact_dict, global_vars)
            
            # Generate subject
            subject = self.generate_subject(contact_dict, language, global_vars)
            
            # Prepare attachments
            attachments = []
            
            # Add language-specific attachments
            if attachments_config and 'by_language' in attachments_config:
                lang_attachments = attachments_config['by_language'].get(language, [])
                attachments.extend(lang_attachments)
            
            # Add common attachments
            if attachments_config and 'common' in attachments_config:
                attachments.extend(attachments_config['common'])
            
            # Add contact-specific attachments
            if 'attachment' in contact_dict and pd.notna(contact_dict['attachment']):
                attachments.append(contact_dict['attachment'])

            # Log campaign entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'name': contact_dict.get('name', 'Unknown'),
                'email': contact_dict.get('email', 'Unknown'),
                'language': language,
                'original_language': contact_dict.get('language', 'Not specified'),
                'subject': subject,
                'attachments_count': len(attachments),
                'template_used': language in self.templates
            }

            print(f"\n📤 Sending to {contact_dict.get('name', 'Unknown')} ({contact_dict.get('email', 'Unknown')}) - Language: {language.upper()}")
            
            if test_mode:
                print(f"🧪 TEST MODE: Email would be sent")
                print(f"   Subject: {subject}")
                print(f"   Attachments: {len(attachments)}")
                print(f"   Template language: {language}")
                log_entry['status'] = 'test_success'
                successful_sends += 1
                language_stats[language]['successful'] += 1
            else:
                if self.send_email(contact_dict['email'], subject, message, attachments):
                    successful_sends += 1
                    language_stats[language]['successful'] += 1
                    log_entry['status'] = 'success'
                    
                    # Random delay between sends
                    if index < len(df) - 1:
                        delay = random.randint(delay_min, delay_max)
                        print(f"⏳ Waiting {delay} seconds...")
                        time.sleep(delay)
                else:
                    failed_sends += 1
                    language_stats[language]['failed'] += 1
                    log_entry['status'] = 'failed'
            
            campaign_log.append(log_entry)

        # Campaign summary
        stats = {
            'total_contacts': len(df),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'completion_time': datetime.now().isoformat(),
            'test_mode': test_mode,
            'campaign_log': campaign_log,
            'language_statistics': language_stats,
            'available_templates': available_languages,
            'default_language_used': default_language
        }
        
        print(f"\n📊 CAMPAIGN SUMMARY")
        print(f"✅ Successful sends: {successful_sends}")
        print(f"❌ Failed sends: {failed_sends}")
        print(f"🌐 Languages used: {', '.join(language_stats.keys())}")
        for lang, lang_stats in language_stats.items():
            print(f"   {lang.upper()}: {lang_stats['successful']}/{lang_stats['attempted']} successful")
        print(f"📅 Completed at: {stats['completion_time']}")
        
        return stats

    def save_templates_to_file(self, filename: str, campaign_type: str = "custom"):
        """Save current templates to JSON file"""
        data = {
            'campaign_type': campaign_type,
            'templates': self.templates,
            'subjects': self.subject_templates
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Templates saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving templates: {e}")
