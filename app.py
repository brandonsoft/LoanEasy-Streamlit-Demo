import streamlit as st
import json
import requests
import time
import base64

# Generate a unique session_id using the epoch timestamp
# Check if 'session_id' is not in the session state, then generate and store it
# Initialize session_id, uploaded_docs, and chat_history in session state if they don't already exist
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(int(time.time() * 1000))

if 'uploaded_docs' not in st.session_state:
    st.session_state['uploaded_docs'] = []

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Use the session_id from the session state for API calls
session_id = st.session_state['session_id']
# Define API base URL
BASE_URL = "http://backend:8501/api"

# Set page configuration to use a light theme
st.set_page_config(page_title="FinDoc Assistant", layout="wide", page_icon=":chart_with_upwards_trend:")

# Custom CSS for updated styling
st.markdown(
    """
    <style>
        .stTextInput>div>div>input, .stFileUploader {
            border-radius: 20px;
            border: 2px dashed #3333ff;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .report-column {
            background-color: #f0f2f6;
            height: 100%;
        }
        .chat-column {
            background-color: transparent;
        }
        .column-title {
            text-align: center;
            color: #000;  /* Changed to black */
            margin-bottom: 1rem;
        }
        .reset-btn {
            font-size: 16px;
            padding: 5px 10px;
            border-radius: 5px;
            background-color: #3333ff;
            color: white;
            border: none;
            cursor: pointer;
        }
        .reset-btn:hover {
            background-color: #5555ff;
        }
        .sidebar-section {
            margin-bottom: 1rem;
        }
        .app-details {
            position: absolute;
            bottom: 0;
            padding: 10px;
            width: -webkit-fill-available;
        }
        .sidebar .stButton>button {
            font-size: 16px;
            padding: 5px 10px;
            border-radius: 5px;
            background-color: #3333ff;
            color: white;
            border: none;
            cursor: pointer;
            display: block; /* Make the button wider */
            width: 100%; /* Use with display: block for full-width button */
            margin: 10px 0; /* Optional: Adds some space around the button */
        }
        .sidebar .stButton>button:hover {
            background-color: #5555ff;
        }
        .report-container {
            border: 1px solid #ECECEC;
            border-radius: 12px;
            margin: 15px 0;
        }
        .company-name-container {
            height: 104px;
            border-radius: 12px;
        }
        .company-logo {
            margin: 18px;
            height: 68px;
            width: 68px;
        }
        .company-name-title {
            font-size: 18px;
        }
        .company-location {
            font-size: 16px;
        }
        .report-title {
            padding: 18px;
            border-bottom: 1px solid #ECECEC
        }
        .report-title>span {
            font-color: #000000;
            font-weight: 600;
            font-size: 18px;
        }
        .report-content {
            padding: 20px;
            font-size: 16px;
        }
        .report-icon {
            width: 24px;
            height: 24px;
            margin-right: 10px;
        }
        .items-container {
            display: flex;
            flex-wrap: no-wrap;
            gap: 2%;
            overflow: auto;
            justify-content: flex-start;
        }
        .avatar-item {
            flex: 0 0 32%;
            min-width: 180px;
        }
        .avatar-container {
            display: flex;
            height: 84px;
            border: 1px solid #ECECEC;
            border-radius: 8px;
        }        
        .avatar-image {
            margin: 18px 16px;
            height: 48px;
            width: 48px;
        }
        .avatar-title {
            display: flex;
            justify-content: center;
            flex-direction: column;
        }
        .avatar-title .title {
            font-weight: 600;
            color: #ffffff;
            font-size: 14px;
            margin: 0;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .avatar-title .subtitle {
            font-weight: 600;
            margin: 0;
            color: #656F93;
            font-size: 12px;
        }
        .risk-item {
            flex: 1 1 32%;
            min-width: 200px;
        }
        .risk-content {
            padding: 20px 16px;
        }
        .risk-container {
            display: flex;
            flex-direction: column;
            border: 1px solid #ECECEC;
            border-radius: 8px;
            padding: 20px 16px;
        }
        .risk-level {
            font-size: 16px;
            margin-bottom: 12px;
        }
    </style>
    """, 
    unsafe_allow_html=True,
)



# Sidebar for uploading documents and displaying uploaded document names
with st.sidebar:
    st.markdown("## FinDoc Assistant")
    st.markdown("**Welcome to FinDoc Assistant!** 🌟 Upload your financial documents and get instant insights.")
    
    uploaded_files = st.file_uploader("Upload Document", type=['pdf', 'docx', 'txt'], accept_multiple_files=True, key="file_uploader")
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state['uploaded_docs']:
                st.session_state['uploaded_docs'].append(uploaded_file.name)
                with st.spinner(f'Processing {uploaded_file.name}...'):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{BASE_URL}/report/{session_id}", files=files, timeout=60)
                    if response.ok:
                        try:
                            # Update the session state with the new report data
                            response_text = response.text
                            start_pos = response_text.find('{')
                            end_pos = response_text.rfind('}') + 1
                            explanation = response_text.split("Explanation:")[1].strip()
                            st.session_state['report_data'] = json.loads(response_text[start_pos:end_pos])
                            st.session_state['explanation'] = explanation
                            st.success(f"Document {uploaded_file.name} uploaded and processed successfully!")
                        except json.JSONDecodeError as e:
                            st.error(f"Failed to parse JSON response. Error: {str(e)}")
                    else:
                        st.error(f"Failed to upload {uploaded_file.name}. Error: " + response.text)
    
    st.markdown("### Uploaded Documents")
    for doc_name in st.session_state['uploaded_docs']:
        st.markdown(f"- {doc_name}")


    st.markdown("""
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    """, unsafe_allow_html=True)                
    st.markdown("---")  # This adds a horizontal line as a separator
    st.markdown("**App Version:** 1.0.0", unsafe_allow_html=True)
    st.markdown("© 2024 FinDoc Company", unsafe_allow_html=True)

    
# # If the reset button is pressed, clear specific session state keys
# if st.sidebar.button('Reset', key='reset', help='Reset the application to its initial state'):
#     keys_to_reset = ['report_data', 'uploaded_docs', 'chat_history']
#     for key in keys_to_reset:
#         if key in st.session_state:
#             del st.session_state[key]

# Layout for Chat and Report Output
col_chat, col_report = st.columns([1, 1], gap="medium")

# Chat Container
with col_chat:
    st.markdown("<h2 class='column-title'>💬 Chat with Assistant</h2>", unsafe_allow_html=True)

    # Capture user input from chat input widget
    user_input = st.chat_input("Message FinDoc...", key="new_chat_input")
    if user_input:
        # Construct user message dict and append to chat history
        user_message = {"text": user_input, "role": "user"}
        st.session_state['chat_history'].append(user_message)

        # Display the user's message immediately
        with st.chat_message("user"):
            st.markdown(user_message["text"])

        # Make backend call for bot response with a spinner
        with st.spinner('Waiting for a response...'):
            try:
                response = requests.get(f"{BASE_URL}/chat/", params={"query": user_input, "session_id": session_id})
                if response.ok:
                    chat_response = response.text
                    bot_message = {"text": chat_response, "role": "assistant"}
                    # Append bot response to chat history
                    st.session_state['chat_history'].append(bot_message)
                else:
                    st.error(f"Failed to get a response from the assistant. Error: {response.text}")
            except Exception as e:
                st.error(f"An error occurred while communicating with the assistant: {str(e)}")

        # Display chat history, including the new response
        for message in reversed(st.session_state['chat_history']):
            with st.chat_message(message["role"]):
                st.markdown(message["text"])

def get_image_base64(path):
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded

def generate_progress_bar(risk_level, percentage):
    color = {
      'Low': '#42B06F',  
      'Medium': '#FE734C',  
      'High': '#EB4646',  
    }.get(risk_level, '#ff6a6a')  

    progress_bar_html = f"""    
    <div class="progress-container" style="width: 100%; background-color: #e0e0e0; border-radius: 6px;">
        <div class="progress-bar" style="width: {percentage}%; height: 12px; background-color: {color}; border-radius: 7px; transition: width 0.4s ease;"></div>
    </div>
    """
    return progress_bar_html

def display_report_section(data, explanation=""):
    # Display the company name
    st.markdown(
        f"""
        <div class="report-container avatar-container company-name-container">
            <img class="avatar-image company-logo" src="https://ui-avatars.com/api/?length=2&rounded=true&bold=true&name={data.get('CompanyName', 'Company Name')}" />
            <div class="avatar-title">
                <p class="title company-name-title">{data.get('CompanyName', 'Company Name')}</p>
                <p class="subtitle company-location">Location</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display the description
    st.markdown(
        f"""
        <div class="report-container">
            <div class="report-title">
                <img class="report-icon" src="data:image/png;base64,{get_image_base64('static/book_icon.png')}" />
                <span>Description :</span>
            </div>
            <div class="report-content">
                {data.get('CompanyDescription', 'No description provided.')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display the directors
    html_content = f"""
    <div class="report-container">
        <div class="report-title">
            <img class="report-icon" src="data:image/png;base64,{get_image_base64('static/medal_icon.png')}" />
            <span>Company Director :</span>
        </div>
        <div class="report-content items-container">
    """
    for director in data.get('Directors', []):
        prefix, name = director.split(' ', 1)
        html_content += f"""<div class="avatar-container avatar-item"><img class="avatar-image" src="https://ui-avatars.com/api/?length=2&rounded=true&bold=true&name={name}" /><div class="avatar-title"><p class="title">{name}</p><p class="subtitle">Grhoud,</p></div></div>"""

    html_content += "</div></div>"
    st.markdown(html_content, unsafe_allow_html=True,)


    # Display the shareholders
    html_content = f"""
    <div class="report-container">
        <div class="report-title">
            <img class="report-icon" src="data:image/png;base64,{get_image_base64('static/cube_icon.png')}" />
            <span>Company Shareholder :</span>
        </div>
        <div class="report-content items-container">
    """
    for shareholder in data.get('Shareholders', []):
        origin_name, percentage = shareholder.rsplit(' ', 1)
        prefix, name = origin_name.split(' ', 1)
        percentage = percentage.strip("()")
        html_content += f"""<div class="avatar-container avatar-item"><img class="avatar-image" src="https://ui-avatars.com/api/?length=2&rounded=true&bold=true&name={name}" /><div class="avatar-title"><p class="title">{name}</p><p class="subtitle">{percentage}</p></div></div>"""

    html_content += "</div></div>"
    st.markdown(html_content, unsafe_allow_html=True,)


    # Display the risk assessments
    report_content = f"""
    <div class="report-container">
        <div class="report-title">
            <img class="report-icon" src="data:image/png;base64,{get_image_base64('static/warn_icon.png')}" />
            <span>AI-Suggested Risk Management Details :</span>
        </div>
        <div class="report-content items-container">
            <div class="report-container risk-item">
                <div class="report-title">
                    <span>Company Risk :</span>
                </div>
                <div class="risk-content">
                    <div class="risk-container">
                        <p class="risk-level">{data.get('CompanyRisk', 'Undefined')} Risk</p>
    """
    report_content += generate_progress_bar(data.get('CompanyRisk', 'Not provided'), 70)
    report_content += f"""
    </div>
                </div>
            </div>
            <div class="report-container risk-item">
                <div class="report-title">
                    <span>Director Risk :</span>
                </div>
                <div class="report-content">
                    <div class="risk-container">
                        <p class="risk-level">{data.get('DirectorsRisk', 'Undefined')} Risk</p>
    """
    report_content += generate_progress_bar(data.get('DirectorsRisk', 'Not provided'), 50)
    report_content += f"""    
    </div>
                </div>
            </div>
            <div class="report-container risk-item">
                <div class="report-title">
                    <span>Shareholder Risk :</span>
                </div>
                <div class="report-content">
                    <div class="risk-container">
                        <p class="risk-level">{data.get('ShareholdersRisk', 'Undefined')} Risk</p>
    """
    report_content += generate_progress_bar(data.get('ShareholdersRisk', 'Not provided'), 70)
    report_content += f"""  
    </div>
                </div>
            </div>
        </div>
    </div>
    """

    st.markdown(
        report_content,
        unsafe_allow_html=True,
    )

    # display explanation
    st.markdown(
        f"""
        <div class="report-container">
            <div class="report-title">
                <img class="report-icon" src="data:image/png;base64,{get_image_base64('static/book_icon.png')}" />
                <span>Explanation :</span>
            </div>
            <div class="report-content">
                {explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display action buttons
    st.markdown("""
    <br>
    """, unsafe_allow_html=True)      
    col1, col2 = st.columns([1, 1], gap="medium")
    with col1:
        st.button("Reject Applications", type="secondary", use_container_width=True,)
    with col2:
        st.button("Approve Applications", type="primary", use_container_width=True,)

# example_data = """json{
#     "DocumentType": ["Memorandum of Association (MoA)"],
#     "CompanyName": "SMART SENSE DRONE SERVICES L.L.C",
#     "CompanyDescription": "SMART SENSE DRONE SERVICES L.L.C is a Limited Liability Company that operates in the drone services industry. The company's primary operations involve the use of drones for various services, potentially including surveillance, delivery, and other applications. The company's unique selling proposition lies in its innovative use of drone technology, potentially leveraging AI and other advanced technologies to provide superior services.",
#     "Directors": ["Mr. NAVANEETHA BABU CHELLATHURAI CHELLATHURAI", "Mr. HENDRIK OSKAR SCHOUTEN", "Mr. LUCA ROMANINI"],
#     "Shareholders": ["Mr. NAVANEETHA BABU CHELLATHURAI CHELLATHURAI (50%)", "Mr. HENDRIK OSKAR SCHOUTEN (50%)"],
#     "NewsArticles": "The company's industry is experiencing significant advancements, with companies like XTEND securing substantial funding to redefine robotics with AI-powered common sense. This development indicates a growing interest and investment in the drone and robotics industry, potentially presenting opportunities for SMART SENSE DRONE SERVICES L.L.C to secure funding or partnerships for growth and expansion.",
#     "CompanyRisk": "Medium",
#     "ShareholdersRisk": "Medium",
#     "DirectorsRisk": "Low"
# }

# Explanation:

# The company, SMART SENSE DRONE SERVICES L.L.C, is a Limited Liability Company that specializes in drone services. The company's directors are Mr. NAVANEETHA BABU CHELLATHURAI CHELLATHURAI, Mr. HENDRIK OSKAR SCHOUTEN, and Mr. LUCA ROMANINI. The shareholders are Mr. NAVANEETHA BABU CHELLATHURAI CHELLATHURAI and Mr. HENDRIK OSKAR SCHOUTEN, each holding a 50% stake in the company.

# The company risk is assessed as Medium, considering the inherent risks associated with the drone services industry, including regulatory changes, technological advancements, and market competition. The shareholders' risk is also Medium, given the equal distribution of shares between two shareholders, which could lead to potential conflicts in decision-making. The directors' risk is assessed as Low, as the directors have a clear strategic direction and are experienced in their roles.

# No news articles were found using the API, indicating a lack of recent public exposure or significant events involving the company.

# Uploaded Documents
# SMARTSENSE AMENDED MOA.pdf
# """

# Report Container - Displaying only the latest report
with col_report:
    st.markdown("<h2 class='column-title'>Report</h2>", unsafe_allow_html=True)
    if 'report_data' in st.session_state and st.session_state['report_data']:
        display_report_section(st.session_state['report_data'], st.session_state['explanation'])
    else:
        st.info("Please upload a document to generate the report.")

# with col_report:
#     start_pos = example_data.find('{')
#     end_pos = example_data.find('}') + 1
#     explanation = example_data.split("Explanation:")[1].strip()
#     display_report_section(json.loads(example_data[start_pos:end_pos]), explanation)