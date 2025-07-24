# Custom global variables (common for all languages)
        st.subheader("🔧 Custom Variables")
        custom_vars_text = st.text_area(
            "Additional Variables (JSON format)",
            value='{"company": "Your Company", "background": "financial engineering"}',
            help="Enter custom variables in JSON format - these will be the same for all languages"
        )
        
        try:
            custom_vars = json.loads(custom_vars_text) if custom_vars_text.strip() else {}
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format for custom variables")
            custom_vars = {}
        
        # Add custom vars to global vars
        global_vars.update(custom_vars)
        
        # Store sender info mode for later use
        if 'sender_info_mode' not in st.session_state:
            st.session_state.sender_info_mode = sender_info_modeimport streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io
import zipfile
from email_campaign_bot import EmailCampaignBot  # Import our core module

# Page configuration
st.set_page_config(
    page_title="Email Campaign Manager",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'bot' not in st.session_state:
        st.session_state.bot = None
    if 'templates_loaded' not in st.session_state:
        st.session_state.templates_loaded = False
    if 'campaign_stats' not in st.session_state:
        st.session_state.campaign_stats = None
    if 'contacts_df' not in st.session_state:
        st.session_state.contacts_df = None

def validate_email_config(email, password, smtp_server, smtp_port):
    """Validate email configuration"""
    if not email or not password:
        return False, "Email and password are required"
    
    if '@' not in email:
        return False, "Invalid email format"
    
    if not smtp_server:
        return False, "SMTP server is required"
    
    try:
        int(smtp_port)
    except ValueError:
        return False, "SMTP port must be a number"
    
    return True, "Valid configuration"

def load_contacts_preview(uploaded_file):
    """Load and preview contacts file"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        return df, None
    except Exception as e:
        return None, str(e)

def create_sample_contacts():
    """Create sample contacts file"""
    sample_data = {
        'name': ['John Doe', 'Marie Martin', 'Alex Smith'],
        'email': ['john@example.com', 'marie@example.fr', 'alex@example.com'],
        'language': ['en', 'fr', 'en'],
        'company': ['TechCorp', 'InnovateFR', 'StartupXYZ'],
        'position': ['CTO', 'Directeur Innovation', 'Founder'],
        'source': ['LinkedIn', 'Conference', 'Website'],
        'custom_message': [
            'I am particularly interested in your work on AI applications.',
            'Votre expertise en innovation m\'intéresse beaucoup.',
            'I would love to learn about your entrepreneurship journey.'
        ]
    }
    return pd.DataFrame(sample_data)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📧 Email Campaign Manager</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Email configuration
        with st.expander("📧 Email Settings", expanded=True):
            email = st.text_input("Email Address", placeholder="your-email@gmail.com")
            password = st.text_input("Password", type="password", 
                                   help="Use App Password for Gmail")
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587, min_value=1, max_value=65535)
            
            if st.button("🔗 Connect Email"):
                is_valid, message = validate_email_config(email, password, smtp_server, smtp_port)
                if is_valid:
                    try:
                        st.session_state.bot = EmailCampaignBot(email, password, smtp_server, smtp_port)
                        st.success("✅ Email connected successfully!")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {e}")
                else:
                    st.error(f"❌ {message}")
        
        # Campaign settings
        with st.expander("🎯 Campaign Settings"):
            send_limit = st.number_input("Send Limit per Session", value=5, min_value=1, max_value=100)
            delay_min = st.number_input("Min Delay (seconds)", value=30, min_value=0)
            delay_max = st.number_input("Max Delay (seconds)", value=60, min_value=delay_min)
            test_mode = st.checkbox("🧪 Test Mode (don't send emails)", value=True)

    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Contacts", "📝 Templates", "📎 Attachments", "🚀 Campaign", "📊 Results"])
    
    with tab1:
        st.header("📋 Contact Management")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File upload
            uploaded_file = st.file_uploader(
                "Upload Contacts File",
                type=['csv', 'xlsx'],
                help="Upload a CSV or Excel file with contact information"
            )
            
            if uploaded_file:
                df, error = load_contacts_preview(uploaded_file)
                if error:
                    st.error(f"❌ Error loading file: {error}")
                else:
                    st.session_state.contacts_df = df
                    st.success(f"✅ Loaded {len(df)} contacts")
                    
                    # Preview
                    st.subheader("📊 Contacts Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Column validation
                    required_cols = ['name', 'email']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Missing required columns: {missing_cols}")
                    else:
                        st.success("✅ All required columns present")
                    
                    # Show available columns
                    st.info(f"Available columns: {', '.join(df.columns.tolist())}")
        
        with col2:
            st.subheader("📥 Sample File")
            sample_df = create_sample_contacts()
            
            # Download sample
            csv_buffer = io.StringIO()
            sample_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Sample CSV",
                data=csv_buffer.getvalue(),
                file_name="sample_contacts.csv",
                mime="text/csv"
            )
            
            # Show sample structure
            st.subheader("📋 Sample Structure")
            st.dataframe(sample_df, use_container_width=True)
    
    with tab2:
        st.header("📝 Email Templates")
        
        if not st.session_state.bot:
            st.warning("⚠️ Please connect your email first in the sidebar")
            return
        
        # Template type selection
        template_type = st.selectbox(
            "Select Template Type",
            ["networking", "job_application", "custom"],
            help="Choose a pre-built template or create custom templates"
        )
        
        if template_type in ["networking", "job_application"]:
            # Load default templates
            default_templates = st.session_state.bot.get_default_templates()
            if st.button(f"📥 Load {template_type.title()} Templates"):
                template_data = default_templates[template_type]
                st.session_state.bot.templates = template_data["templates"]
                st.session_state.bot.subject_templates = template_data["subjects"]
                st.session_state.templates_loaded = True
                st.success(f"✅ {template_type.title()} templates loaded!")
        
        # Template editor
        if st.session_state.templates_loaded or template_type == "custom":
            st.subheader("✏️ Template Editor")
            
            # Language selection
            languages = st.multiselect(
                "Select Languages",
                ["en", "fr", "es", "de", "it"],
                default=["en", "fr"] if not st.session_state.bot.templates else list(st.session_state.bot.templates.keys())
            )
            
            for lang in languages:
                st.subheader(f"🌐 {lang.upper()} Template")
                
                # Email template
                current_template = st.session_state.bot.templates.get(lang, "")
                template_content = st.text_area(
                    f"Email Template ({lang.upper()})",
                    value=current_template,
                    height=300,
                    key=f"template_{lang}",
                    help="Use {variable_name} for placeholders (e.g., {name}, {email}, {sender_name})"
                )
                
                # Subject templates
                current_subjects = st.session_state.bot.subject_templates.get(lang, [])
                subjects_text = "\n".join(current_subjects)
                subjects_content = st.text_area(
                    f"Subject Templates ({lang.upper()}) - One per line",
                    value=subjects_text,
                    height=100,
                    key=f"subjects_{lang}",
                    help="Enter multiple subject templates, one per line"
                )
                
                # Update templates
                st.session_state.bot.templates[lang] = template_content
                st.session_state.bot.subject_templates[lang] = [s.strip() for s in subjects_content.split('\n') if s.strip()]
            
            # Save/Load templates
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Templates"):
                    filename = f"templates_{template_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    st.session_state.bot.save_templates_to_file(filename, template_type)
                    st.success(f"Templates saved as {filename}")
            
            with col2:
                templates_file = st.file_uploader("📂 Load Templates JSON", type=['json'])
                if templates_file:
                    try:
                        # Save uploaded file temporarily
                        with open("temp_templates.json", "wb") as f:
                            f.write(templates_file.getbuffer())
                        st.session_state.bot.load_templates_from_file("temp_templates.json")
                        os.remove("temp_templates.json")
                        st.success("✅ Templates loaded successfully!")
                    except Exception as e:
                        st.error(f"❌ Error loading templates: {e}")
    
    with tab3:
        st.header("📎 Attachment Management")
        
        # Attachment configuration
        st.subheader("📋 Attachment Configuration")
        
        # Initialize attachment config in session state
        if 'attachment_config' not in st.session_state:
            st.session_state.attachment_config = {
                'common': [],
                'by_language': {}
            }
        
        # Common attachments
        st.subheader("📄 Common Attachments (All Languages)")
        common_files = st.file_uploader(
            "Upload common attachments",
            accept_multiple_files=True,
            key="common_attachments"
        )
        
        if common_files:
            # Save files and update config
            common_paths = []
            for file in common_files:
                file_path = f"attachments/common_{file.name}"
                os.makedirs("attachments", exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                common_paths.append(file_path)
            
            st.session_state.attachment_config['common'] = common_paths
            st.success(f"✅ {len(common_files)} common attachments uploaded")
        
        # Language-specific attachments
        st.subheader("🌐 Language-Specific Attachments")
        
        available_languages = list(st.session_state.bot.templates.keys()) if st.session_state.bot and st.session_state.bot.templates else ['en', 'fr']
        
        for lang in available_languages:
            st.write(f"**{lang.upper()} Attachments**")
            lang_files = st.file_uploader(
                f"Upload {lang.upper()} attachments",
                accept_multiple_files=True,
                key=f"lang_attachments_{lang}"
            )
            
            if lang_files:
                lang_paths = []
                for file in lang_files:
                    file_path = f"attachments/{lang}_{file.name}"
                    os.makedirs("attachments", exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    lang_paths.append(file_path)
                
                st.session_state.attachment_config['by_language'][lang] = lang_paths
                st.success(f"✅ {len(lang_files)} {lang.upper()} attachments uploaded")
        
        # Show current attachment configuration
        if st.session_state.attachment_config['common'] or st.session_state.attachment_config['by_language']:
            st.subheader("📊 Current Attachment Configuration")
            
            if st.session_state.attachment_config['common']:
                st.write("**Common Files:**")
                for file_path in st.session_state.attachment_config['common']:
                    st.write(f"- {os.path.basename(file_path)}")
            
            for lang, files in st.session_state.attachment_config['by_language'].items():
                if files:
                    st.write(f"**{lang.upper()} Files:**")
                    for file_path in files:
                        st.write(f"- {os.path.basename(file_path)}")
    
    with tab4:
        st.header("🚀 Campaign Launch")
        
        if not st.session_state.bot:
            st.warning("⚠️ Please connect your email first in the sidebar")
            return
        
        if not st.session_state.templates_loaded and not st.session_state.bot.templates:
            st.warning("⚠️ Please load email templates first")
            return
        
        if st.session_state.contacts_df is None:
            st.warning("⚠️ Please upload contacts file first")
            return
        
        # Language and Campaign Configuration
        st.subheader("🌐 Campaign Language Settings")
        
        # Get available languages from templates
        available_languages = list(st.session_state.bot.templates.keys()) if st.session_state.bot.templates else ['en']
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_mode = st.radio(
                "Campaign Mode",
                ["Single Language", "Multi-Language", "Auto-Detect"],
                help="Choose how to handle languages in your campaign"
            )
        
        with col2:
            if campaign_mode == "Single Language":
                selected_language = st.selectbox(
                    "Select Campaign Language",
                    available_languages,
                    help="All contacts will receive emails in this language"
                )
                st.info(f"All {len(st.session_state.contacts_df)} contacts will receive {selected_language.upper()} emails")
            
            elif campaign_mode == "Multi-Language":
                selected_languages = st.multiselect(
                    "Select Languages to Send",
                    available_languages,
                    default=available_languages,
                    help="Create separate campaigns for each selected language"
                )
                if selected_languages:
                    total_campaigns = len(selected_languages) * len(st.session_state.contacts_df)
                    st.warning(f"⚠️ This will create {len(selected_languages)} campaigns × {len(st.session_state.contacts_df)} contacts = {total_campaigns} total emails")
            
            else:  # Auto-Detect
                st.info("Will use 'language' column from contacts file, defaulting to English if not specified")
                # Check if language column exists
                if 'language' in st.session_state.contacts_df.columns:
                    lang_distribution = st.session_state.contacts_df['language'].value_counts()
                    st.write("**Language Distribution in Contacts:**")
                    for lang, count in lang_distribution.items():
                        if lang in available_languages:
                            st.write(f"- {lang.upper()}: {count} contacts ✅")
                        else:
                            st.write(f"- {lang.upper()}: {count} contacts ❌ (no template)")
                else:
                    st.warning("⚠️ No 'language' column found in contacts. Will default to English.")
        
        # Global variables configuration
        st.subheader("👤 Sender Information")
        
        # Language-specific sender info
        sender_info_mode = st.radio(
            "Sender Information Mode",
            ["Single (Same for all languages)", "Multi-Language (Different per language)"],
            help="Choose whether to use the same sender info for all languages or customize per language"
        )
        
        if sender_info_mode == "Single (Same for all languages)":
            col1, col2 = st.columns(2)
            
            with col1:
                sender_name = st.text_input("Sender Name", value="Reda Salhi")
                sender_title = st.text_input("Sender Title", value="Étudiant en Finance")
                sender_contact = st.text_area("Contact Information", value="Email: reda.salhi@email.com\nPhone: +33123456789")
            
            with col2:
                meeting_duration = st.text_input("Meeting Duration", value="15-20 minutes")
                call_to_action = st.text_area("Call to Action", 
                                            value="I'm actively exploring opportunities and would love any advice you might have.")
            
            # Create single global vars
            global_vars = {
                'sender_name': sender_name,
                'sender_title': sender_title,
                'sender_contact': sender_contact,
                'meeting_duration': meeting_duration,
                'call_to_action': call_to_action
            }
        
        else:  # Multi-Language sender info
            st.info("💡 Configure sender information for each language. This will automatically adapt based on the email language.")
            
            # Get available languages
            available_languages = list(st.session_state.bot.templates.keys()) if st.session_state.bot.templates else ['en', 'fr']
            
            # Create tabs for each language
            if len(available_languages) <= 4:
                lang_tabs = st.tabs([f"🌐 {lang.upper()}" for lang in available_languages])
            else:
                # Use selectbox for many languages
                selected_lang_for_config = st.selectbox("Select language to configure", available_languages)
                lang_tabs = [st.container()]
                available_languages = [selected_lang_for_config]
            
            global_vars = {}
            
            for i, lang in enumerate(available_languages):
                with lang_tabs[i]:
                    st.subheader(f"Sender Information - {lang.upper()}")
                    
                    # Default values based on language
                    if lang == 'fr':
                        default_title = "Étudiant en Ingénierie Financière"
                        default_duration = "15-20 minutes"
                        default_cta = "Je suis activement à la recherche d'opportunités et j'aimerais beaucoup avoir vos conseils."
                        default_contact = "Email: reda.salhi@email.com\nTéléphone: +33123456789"
                    elif lang == 'es':
                        default_title = "Estudiante de Ingeniería Financiera"
                        default_duration = "15-20 minutos"
                        default_cta = "Estoy explorando activamente oportunidades y me encantaría recibir cualquier consejo que puedas tener."
                        default_contact = "Email: reda.salhi@email.com\nTeléfono: +33123456789"
                    elif lang == 'de':
                        default_title = "Student der Finanzingenieurwissenschaften"
                        default_duration = "15-20 Minuten"
                        default_cta = "Ich erkunde aktiv neue Möglichkeiten und würde mich über jeden Rat freuen, den Sie haben könnten."
                        default_contact = "Email: reda.salhi@email.com\nTelefon: +33123456789"
                    else:  # English default
                        default_title = "Financial Engineering Student"
                        default_duration = "15-20 minutes"
                        default_cta = "I'm actively exploring opportunities and would love any advice you might have."
                        default_contact = "Email: reda.salhi@email.com\nPhone: +33123456789"
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sender_name = st.text_input(f"Sender Name ({lang.upper()})", value="Reda Salhi", key=f"name_{lang}")
                        sender_title = st.text_input(f"Sender Title ({lang.upper()})", value=default_title, key=f"title_{lang}")
                        sender_contact = st.text_area(f"Contact Information ({lang.upper()})", value=default_contact, key=f"contact_{lang}")
                    
                    with col2:
                        meeting_duration = st.text_input(f"Meeting Duration ({lang.upper()})", value=default_duration, key=f"duration_{lang}")
                        call_to_action = st.text_area(f"Call to Action ({lang.upper()})", value=default_cta, key=f"cta_{lang}")
                    
                    # Store language-specific variables
                    global_vars[f'sender_name_{lang}'] = sender_name
                    global_vars[f'sender_title_{lang}'] = sender_title
                    global_vars[f'sender_contact_{lang}'] = sender_contact
                    global_vars[f'meeting_duration_{lang}'] = meeting_duration
                    global_vars[f'call_to_action_{lang}'] = call_to_action
        
        # Campaign preview
        st.subheader("👀 Campaign Preview")
        
        # Language selection for preview
        if campaign_mode == "Single Language":
            preview_languages = [selected_language]
        elif campaign_mode == "Multi-Language":
            preview_languages = selected_languages if selected_languages else available_languages[:1]
        else:
            preview_languages = available_languages[:2]  # Show first 2 languages for auto-detect
        
        preview_cols = st.columns(len(preview_languages))
        
        for idx, lang in enumerate(preview_languages):
            with preview_cols[idx]:
                if st.button(f"🔍 Preview {lang.upper()}", key=f"preview_{lang}"):
                    if len(st.session_state.contacts_df) > 0:
                        first_contact = st.session_state.contacts_df.iloc[0].to_dict()
                        # Override language for preview
                        first_contact['language'] = lang
                        
                        if lang in st.session_state.bot.templates:
                            template = st.session_state.bot.templates[lang]
                            preview_message = st.session_state.bot.personalize_message(template, first_contact, global_vars)
                            preview_subject = st.session_state.bot.generate_subject(first_contact, lang, global_vars)
                            
                            st.success(f"**Subject ({lang.upper()}):** {preview_subject}")
                            st.info(f"**Email Content ({lang.upper()}):**")
                            with st.expander(f"View {lang.upper()} Email", expanded=True):
                                st.markdown(preview_message, unsafe_allow_html=True)
                            
                            # Show which sender info is being used
                            if sender_info_mode == "Multi-Language (Different per language)":
                                sender_name_used = global_vars.get(f'sender_name_{lang}', global_vars.get('sender_name', 'Not set'))
                                sender_title_used = global_vars.get(f'sender_title_{lang}', global_vars.get('sender_title', 'Not set'))
                                st.caption(f"📝 Using {lang.upper()} sender info: {sender_name_used}, {sender_title_used}")
                            else:
                                st.caption(f"📝 Using same sender info for all languages")
                        else:
                            st.error(f"❌ No template available for language: {lang}")
        
        # Launch campaign
        st.subheader("🚀 Launch Campaign")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if test_mode:
                st.info("🧪 **Test Mode Enabled** - No emails will actually be sent")
            else:
                st.warning("⚠️ **Live Mode** - Emails will be sent to recipients")
        
        with col2:
            launch_button = st.button(
                "🚀 Launch Campaign",
                type="primary",
                use_container_width=True
            )
        
        if launch_button:
            if not st.session_state.contacts_df.empty:
                # Prepare campaign data based on selected mode
                campaign_results = []
                
                if campaign_mode == "Single Language":
                    # Single language campaign
                    contacts_with_language = st.session_state.contacts_df.copy()
                    contacts_with_language['language'] = selected_language
                    
                    # Save contacts to temporary file
                    temp_contacts_file = f"temp_contacts_{selected_language}.xlsx"
                    contacts_with_language.to_excel(temp_contacts_file, index=False)
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text(f"🚀 Starting {selected_language.upper()} campaign...")
                    
                        try:
                            # For multi-language sender info, we need to modify global_vars for each contact
                            campaign_global_vars = global_vars.copy()
                            
                            # If using multi-language sender info, we need to process each contact individually
                            if sender_info_mode == "Multi-Language (Different per language)":
                                # Save original contacts to temporary file
                                temp_contacts_file = f"temp_contacts_{selected_language}.xlsx"
                                contacts_with_language.to_excel(temp_contacts_file, index=False)
                                
                                # Run campaign with language-specific processing
                                campaign_stats = st.session_state.bot.run_campaign(
                                    contacts_file=temp_contacts_file,
                                    global_vars=campaign_global_vars,
                                    attachments_config=st.session_state.attachment_config,
                                    send_limit=send_limit,
                                    delay_min=delay_min,
                                    delay_max=delay_max,
                                    test_mode=test_mode,
                                    default_language=selected_language
                                )
                            else:
                                # Use original logic for single sender info
                                temp_contacts_file = f"temp_contacts_{selected_language}.xlsx"
                                contacts_with_language.to_excel(temp_contacts_file, index=False)
                                
                                campaign_stats = st.session_state.bot.run_campaign(
                                    contacts_file=temp_contacts_file,
                                    global_vars=campaign_global_vars,
                                    attachments_config=st.session_state.attachment_config,
                                    send_limit=send_limit,
                                    delay_min=delay_min,
                                    delay_max=delay_max,
                                    test_mode=test_mode,
                                    default_language=selected_language
                                )
                        
                        campaign_stats['language'] = selected_language
                        campaign_results.append(campaign_stats)
                        
                    except Exception as e:
                        st.error(f"❌ Campaign failed: {str(e)}")
                    finally:
                        if os.path.exists(temp_contacts_file):
                            os.remove(temp_contacts_file)
                
                elif campaign_mode == "Multi-Language":
                    # Multi-language campaigns
                    if not selected_languages:
                        st.error("❌ Please select at least one language")
                        return
                    
                    total_languages = len(selected_languages)
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, lang in enumerate(selected_languages):
                        if lang not in st.session_state.bot.templates:
                            st.warning(f"⚠️ Skipping {lang.upper()} - no template available")
                            continue
                        
                        status_text.text(f"🚀 Starting {lang.upper()} campaign ({idx+1}/{total_languages})...")
                        progress_bar.progress((idx) / total_languages)
                        
                        # Prepare contacts for this language
                        contacts_with_language = st.session_state.contacts_df.copy()
                        contacts_with_language['language'] = lang
                        
                        # Save to temporary file
                        temp_contacts_file = f"temp_contacts_{lang}.xlsx"
                        contacts_with_language.to_excel(temp_contacts_file, index=False)
                        
                        try:
                            # For multi-language campaigns, each language gets its own sender info
                            campaign_global_vars = global_vars.copy()
                            
                            campaign_stats = st.session_state.bot.run_campaign(
                                contacts_file=temp_contacts_file,
                                global_vars=campaign_global_vars,
                                attachments_config=st.session_state.attachment_config,
                                send_limit=send_limit,
                                delay_min=delay_min,
                                delay_max=delay_max,
                                test_mode=test_mode,
                                default_language=lang
                            )
                            
                            campaign_stats['language'] = lang
                            campaign_results.append(campaign_stats)
                            
                        except Exception as e:
                            st.error(f"❌ {lang.upper()} campaign failed: {str(e)}")
                        finally:
                            if os.path.exists(temp_contacts_file):
                                os.remove(temp_contacts_file)
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / total_languages)
                
                else:  # Auto-Detect
                    # Auto-detect language from contacts
                    temp_contacts_file = "temp_contacts_auto.xlsx"
                    st.session_state.contacts_df.to_excel(temp_contacts_file, index=False)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("🚀 Starting auto-detect campaign...")
                    
                    try:
                        campaign_stats = st.session_state.bot.run_campaign(
                            contacts_file=temp_contacts_file,
                            global_vars=global_vars,
                            attachments_config=st.session_state.attachment_config,
                            send_limit=send_limit,
                            delay_min=delay_min,
                            delay_max=delay_max,
                            test_mode=test_mode,
                            default_language="en"  # For auto-detect, English is default
                        )
                        
                        campaign_stats['language'] = 'auto-detect'
                        campaign_results.append(campaign_stats)
                        
                    except Exception as e:
                        st.error(f"❌ Campaign failed: {str(e)}")
                    finally:
                        if os.path.exists(temp_contacts_file):
                            os.remove(temp_contacts_file)
                
                # Update progress and show results
                if campaign_results:
                    progress_bar.progress(100)
                    status_text.text("✅ All campaigns completed!")
                    
                    # Store results
                    st.session_state.campaign_stats = campaign_results
                    
                    # Show summary
                    total_successful = sum(stats.get('successful_sends', 0) for stats in campaign_results if 'error' not in stats)
                    total_failed = sum(stats.get('failed_sends', 0) for stats in campaign_results if 'error' not in stats)
                    
                    if total_successful > 0:
                        st.success(f"✅ All campaigns completed! {total_successful} emails sent successfully across {len(campaign_results)} campaign(s).")
                    if total_failed > 0:
                        st.warning(f"⚠️ {total_failed} emails failed to send.")
                    
                    # Show per-language results
                    for stats in campaign_results:
                        if 'error' not in stats:
                            lang_name = stats.get('language', 'Unknown').upper()
                            st.info(f"**{lang_name}**: {stats['successful_sends']} sent, {stats['failed_sends']} failed")
                else:
                    progress_bar.progress(0)
                    status_text.text("❌ No campaigns completed")
            else:
                st.error("❌ No contacts available")
    
    with tab5:
        st.header("📊 Campaign Results")
        
        if st.session_state.campaign_stats:
            # Handle both single campaign and multi-campaign results
            if isinstance(st.session_state.campaign_stats, list):
                # Multi-campaign results
                all_stats = st.session_state.campaign_stats
                
                # Overall summary
                st.subheader("📈 Overall Campaign Summary")
                
                total_contacts = sum(stats.get('total_contacts', 0) for stats in all_stats if 'error' not in stats)
                total_successful = sum(stats.get('successful_sends', 0) for stats in all_stats if 'error' not in stats)
                total_failed = sum(stats.get('failed_sends', 0) for stats in all_stats if 'error' not in stats)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Campaigns", len(all_stats))
                
                with col2:
                    st.metric("Total Emails Sent", total_successful)
                
                with col3:
                    st.metric("Total Failed", total_failed)
                
                with col4:
                    overall_success_rate = (total_successful / (total_successful + total_failed) * 100) if (total_successful + total_failed) > 0 else 0
                    st.metric("Overall Success Rate", f"{overall_success_rate:.1f}%")
                
                # Per-language breakdown
                st.subheader("🌐 Per-Language Results")
                
                language_data = []
                for stats in all_stats:
                    if 'error' not in stats:
                        language_data.append({
                            'Language': stats.get('language', 'Unknown').upper(),
                            'Contacts': stats.get('total_contacts', 0),
                            'Successful': stats.get('successful_sends', 0),
                            'Failed': stats.get('failed_sends', 0),
                            'Success Rate': f"{(stats.get('successful_sends', 0) / stats.get('total_contacts', 1) * 100):.1f}%",
                            'Completion Time': stats.get('completion_time', 'Unknown')
                        })
                
                if language_data:
                    lang_df = pd.DataFrame(language_data)
                    st.dataframe(lang_df, use_container_width=True)
                
                # Combined campaign log
                st.subheader("📋 Combined Campaign Log")
                
                all_logs = []
                for stats in all_stats:
                    if 'campaign_log' in stats and stats['campaign_log']:
                        # Add language info to each log entry
                        for log_entry in stats['campaign_log']:
                            log_entry['campaign_language'] = stats.get('language', 'Unknown')
                            all_logs.append(log_entry)
                
                if all_logs:
                    combined_log_df = pd.DataFrame(all_logs)
                    
                    # Add filters
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        status_filter = st.multiselect(
                            "Filter by Status",
                            options=combined_log_df['status'].unique(),
                            default=combined_log_df['status'].unique(),
                            key="multi_status_filter"
                        )
                    
                    with col2:
                        email_lang_filter = st.multiselect(
                            "Filter by Email Language",
                            options=combined_log_df['language'].unique(),
                            default=combined_log_df['language'].unique(),
                            key="multi_email_lang_filter"
                        )
                    
                    with col3:
                        campaign_lang_filter = st.multiselect(
                            "Filter by Campaign",
                            options=combined_log_df['campaign_language'].unique(),
                            default=combined_log_df['campaign_language'].unique(),
                            key="multi_campaign_filter"
                        )
                    
                    # Apply filters
                    filtered_df = combined_log_df[
                        (combined_log_df['status'].isin(status_filter)) &
                        (combined_log_df['language'].isin(email_lang_filter)) &
                        (combined_log_df['campaign_language'].isin(campaign_lang_filter))
                    ]
                    
                    # Display filtered results
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # Download combined results
                    csv_buffer = io.StringIO()
                    combined_log_df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="📥 Download Combined Campaign Log",
                        data=csv_buffer.getvalue(),
                        file_name=f"combined_campaign_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            else:
                # Single campaign results (backward compatibility)
                stats = st.session_state.campaign_stats
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Contacts", stats['total_contacts'])
                
                with col2:
                    st.metric("Successful Sends", stats['successful_sends'])
                
                with col3:
                    st.metric("Failed Sends", stats['failed_sends'])
                
                with col4:
                    success_rate = (stats['successful_sends'] / stats['total_contacts'] * 100) if stats['total_contacts'] > 0 else 0
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                # Campaign log
                if 'campaign_log' in stats and stats['campaign_log']:
                    st.subheader("📋 Detailed Log")
                    
                    log_df = pd.DataFrame(stats['campaign_log'])
                    
                    # Add filters
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        status_filter = st.multiselect(
                            "Filter by Status",
                            options=log_df['status'].unique(),
                            default=log_df['status'].unique(),
                            key="single_status_filter"
                        )
                    
                    with col2:
                        language_filter = st.multiselect(
                            "Filter by Language",
                            options=log_df['language'].unique(),
                            default=log_df['language'].unique(),
                            key="single_language_filter"
                        )
                    
                    # Apply filters
                    filtered_df = log_df[
                        (log_df['status'].isin(status_filter)) &
                        (log_df['language'].isin(language_filter))
                    ]
                    
                    # Display filtered results
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # Download results
                    csv_buffer = io.StringIO()
                    log_df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="📥 Download Campaign Log",
                        data=csv_buffer.getvalue(),
                        file_name=f"campaign_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Campaign summary
                st.subheader("📈 Campaign Summary")
                
                summary_data = {
                    'Metric': ['Total Contacts', 'Successful Sends', 'Failed Sends', 'Success Rate', 'Completion Time'],
                    'Value': [
                        stats['total_contacts'],
                        stats['successful_sends'],
                        stats['failed_sends'],
                        f"{success_rate:.1f}%",
                        stats['completion_time']
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                st.table(summary_df)
            
        else:
            st.info("📊 No campaign results yet. Launch a campaign to see results here.")
            
            # Show sample results structure
            st.subheader("📋 Sample Results Structure")
            sample_results = pd.DataFrame({
                'timestamp': ['2024-07-24T10:30:00', '2024-07-24T10:31:30', '2024-07-24T10:33:00'],
                'name': ['John Doe', 'Marie Martin', 'Hans Mueller'],
                'email': ['john@example.com', 'marie@example.fr', 'hans@example.de'],
                'language': ['en', 'fr', 'de'],
                'campaign_language': ['en', 'fr', 'de'],
                'status': ['success', 'success', 'failed'],
                'attachments_count': [2, 2, 2]
            })
            st.dataframe(sample_results, use_container_width=True)
            
        # Export all results
        if st.session_state.campaign_stats:
            st.subheader("📤 Export Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Summary Report"):
                    # Create comprehensive summary
                    if isinstance(st.session_state.campaign_stats, list):
                        # Multi-campaign report
                        report_data = []
                        for stats in st.session_state.campaign_stats:
                            if 'error' not in stats:
                                report_data.append({
                                    'Campaign Language': stats.get('language', 'Unknown').upper(),
                                    'Total Contacts': stats.get('total_contacts', 0),
                                    'Successful Sends': stats.get('successful_sends', 0),
                                    'Failed Sends': stats.get('failed_sends', 0),
                                    'Success Rate (%)': round((stats.get('successful_sends', 0) / max(stats.get('total_contacts', 1), 1) * 100), 2),
                                    'Test Mode': stats.get('test_mode', False),
                                    'Completion Time': stats.get('completion_time', 'Unknown')
                                })
                        
                        summary_df = pd.DataFrame(report_data)
                        
                        # Add totals row
                        totals = {
                            'Campaign Language': 'TOTAL',
                            'Total Contacts': summary_df['Total Contacts'].sum(),
                            'Successful Sends': summary_df['Successful Sends'].sum(),
                            'Failed Sends': summary_df['Failed Sends'].sum(),
                            'Success Rate (%)': round((summary_df['Successful Sends'].sum() / max(summary_df['Total Contacts'].sum(), 1) * 100), 2),
                            'Test Mode': 'Mixed' if len(set(stats.get('test_mode', False) for stats in st.session_state.campaign_stats)) > 1 else str(st.session_state.campaign_stats[0].get('test_mode', False)),
                            'Completion Time': f"{len(st.session_state.campaign_stats)} campaigns"
                        }
                        summary_df = pd.concat([summary_df, pd.DataFrame([totals])], ignore_index=True)
                        
                    else:
                        # Single campaign report
                        stats = st.session_state.campaign_stats
                        summary_df = pd.DataFrame([{
                            'Campaign Language': stats.get('language', 'auto-detect').upper(),
                            'Total Contacts': stats.get('total_contacts', 0),
                            'Successful Sends': stats.get('successful_sends', 0),
                            'Failed Sends': stats.get('failed_sends', 0),
                            'Success Rate (%)': round((stats.get('successful_sends', 0) / max(stats.get('total_contacts', 1), 1) * 100), 2),
                            'Test Mode': stats.get('test_mode', False),
                            'Completion Time': stats.get('completion_time', 'Unknown')
                        }])
                    
                    # Create downloadable CSV
                    csv_buffer = io.StringIO()
                    summary_df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="📥 Download Summary Report",
                        data=csv_buffer.getvalue(),
                        file_name=f"campaign_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📋 Export Detailed Logs"):
                    # Create detailed log export
                    if isinstance(st.session_state.campaign_stats, list):
                        # Combine all logs
                        all_logs = []
                        for stats in st.session_state.campaign_stats:
                            if 'campaign_log' in stats and stats['campaign_log']:
                                for log_entry in stats['campaign_log']:
                                    log_entry_copy = log_entry.copy()
                                    log_entry_copy['campaign_language'] = stats.get('language', 'Unknown')
                                    all_logs.append(log_entry_copy)
                        
                        if all_logs:
                            detailed_df = pd.DataFrame(all_logs)
                        else:
                            detailed_df = pd.DataFrame()
                    else:
                        # Single campaign log
                        stats = st.session_state.campaign_stats
                        if 'campaign_log' in stats and stats['campaign_log']:
                            detailed_df = pd.DataFrame(stats['campaign_log'])
                            detailed_df['campaign_language'] = stats.get('language', 'auto-detect')
                        else:
                            detailed_df = pd.DataFrame()
                    
                    if not detailed_df.empty:
                        csv_buffer = io.StringIO()
                        detailed_df.to_csv(csv_buffer, index=False)
                        
                        st.download_button(
                            label="📥 Download Detailed Logs",
                            data=csv_buffer.getvalue(),
                            file_name=f"campaign_detailed_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ No detailed logs available")

if __name__ == "__main__":
    main()
