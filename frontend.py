import streamlit as st
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
        
        # Global variables configuration
        st.subheader("👤 Sender Information")
        col1, col2 = st.columns(2)
        
        with col1:
            sender_name = st.text_input("Sender Name", value="Your Name")
            sender_title = st.text_input("Sender Title", value="Your Title")
            sender_contact = st.text_area("Contact Information", value="Email: your@email.com\nPhone: +1234567890")
        
        with col2:
            meeting_duration = st.text_input("Meeting Duration", value="15-20 minutes")
            call_to_action = st.text_area("Call to Action", 
                                        value="I'm actively exploring opportunities and would love any advice you might have.")
        
        # Custom global variables
        st.subheader("🔧 Custom Variables")
        custom_vars_text = st.text_area(
            "Additional Variables (JSON format)",
            value='{"company": "Your Company", "background": "your background"}',
            help="Enter custom variables in JSON format"
        )
        
        try:
            custom_vars = json.loads(custom_vars_text) if custom_vars_text.strip() else {}
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format for custom variables")
            custom_vars = {}
        
        # Combine all global variables
        global_vars = {
            'sender_name': sender_name,
            'sender_title': sender_title,
            'sender_contact': sender_contact,
            'meeting_duration': meeting_duration,
            'call_to_action': call_to_action,
            **custom_vars
        }
        
        # Campaign preview
        st.subheader("👀 Campaign Preview")
        
        if st.button("🔍 Preview First Email"):
            if len(st.session_state.contacts_df) > 0:
                first_contact = st.session_state.contacts_df.iloc[0].to_dict()
                language = first_contact.get('language', 'en')
                
                if language in st.session_state.bot.templates:
                    template = st.session_state.bot.templates[language]
                    preview_message = st.session_state.bot.personalize_message(template, first_contact, global_vars)
                    preview_subject = st.session_state.bot.generate_subject(first_contact, language, global_vars)
                    
                    st.success(f"**Subject:** {preview_subject}")
                    st.info("**Email Content:**")
                    st.markdown(preview_message, unsafe_allow_html=True)
                else:
                    st.error(f"❌ No template available for language: {language}")
        
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
                # Save contacts to temporary file
                temp_contacts_file = "temp_contacts.xlsx"
                st.session_state.contacts_df.to_excel(temp_contacts_file, index=False)
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🚀 Starting campaign...")
                
                try:
                    # Run campaign
                    campaign_stats = st.session_state.bot.run_campaign(
                        contacts_file=temp_contacts_file,
                        global_vars=global_vars,
                        attachments_config=st.session_state.attachment_config,
                        send_limit=send_limit,
                        delay_min=delay_min,
                        delay_max=delay_max,
                        test_mode=test_mode
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Campaign completed!")
                    
                    # Store results
                    st.session_state.campaign_stats = campaign_stats
                    
                    # Clean up
                    if os.path.exists(temp_contacts_file):
                        os.remove(temp_contacts_file)
                    
                    # Show immediate results
                    if "error" not in campaign_stats:
                        st.success(f"✅ Campaign completed! {campaign_stats['successful_sends']} emails sent successfully.")
                        if campaign_stats['failed_sends'] > 0:
                            st.warning(f"⚠️ {campaign_stats['failed_sends']} emails failed to send.")
                    else:
                        st.error(f"❌ Campaign failed: {campaign_stats['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Campaign failed: {str(e)}")
                    progress_bar.progress(0)
                    status_text.text("❌ Campaign failed")
            else:
                st.error("❌ No contacts available")
    
    with tab5:
        st.header("📊 Campaign Results")
        
        if st.session_state.campaign_stats:
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
                        default=log_df['status'].unique()
                    )
                
                with col2:
                    language_filter = st.multiselect(
                        "Filter by Language",
                        options=log_df['language'].unique(),
                        default=log_df['language'].unique()
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
                'timestamp': ['2024-07-24T10:30:00', '2024-07-24T10:31:30'],
                'name': ['John Doe', 'Marie Martin'],
                'email': ['john@example.com', 'marie@example.fr'],
                'language': ['en', 'fr'],
                'status': ['success', 'success'],
                'attachments_count': [2, 2]
            })
            st.dataframe(sample_results, use_container_width=True)

if __name__ == "__main__":
    main()
