# ui/theme.py
import streamlit as st

# Palette (user-provided)
ACCENT_LIGHT = "#CAE9F5"
ACCENT_BLUE = "#113382"
TEXT_DARK = "#181818"
CARD_BG = "#EDEDED"
PAGE_BG = "#FFFFFF"

def render_css(pin_sidebar: bool = True):
    """
    Render CSS. If pin_sidebar=False the login screen stays centered.
    When pinned the sidebar is visible but content no longer gets a huge gap.
    """
    # small left offset to avoid content overlapping sidebar, but not double-reserving
    margin_left = "80px" if pin_sidebar else "0"

    sidebar_css = ""
    if pin_sidebar:
        sidebar_css = """
        section[data-testid="stSidebar"] {
          position: fixed;
          left: 0;
          top: 0;
          width: 220px;             /* sidebar width */
          height: 100vh;
          padding: 18px;
          overflow: auto;
          border-right: 1px solid rgba(17,51,130,0.03);
          background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
          z-index: 999;
        }
        /* hide the built-in toggle so UI is stable for demo */
        button[title="Toggle sidebar"] { display:none !important; }
        """

    css = f"""
    <style>
    :root {{
      --accent-blue: {ACCENT_BLUE};
      --accent-light: {ACCENT_LIGHT};
      --text-dark: {TEXT_DARK};
      --card-bg: {CARD_BG};
      --page-bg: {PAGE_BG};
    }}

    /* page container & margin */
    .reportview-container .main {{ background: var(--page-bg); }}
    .block-container {{
        padding: 1rem 1.2rem !important;
        max-width: calc(100% - {margin_left}) !important;
        margin-left: {margin_left};
    }}

    /* optional pinned sidebar */
    {sidebar_css}

    /* headings */
    h1,h2,h3 {{ color: var(--accent-blue) !important; font-weight:800; margin:0; }}
    .sidebar-header {{ font-weight:800; color:var(--accent-blue); margin-bottom:6px; font-size:15px; }}
    .sidebar-sub {{ color:var(--text-dark); font-size:14px; margin-bottom:12px; }}

    /* cards & micro UI */
    .card {{ background: var(--card-bg); padding: 12px; border-radius: 12px; border: 1px solid rgba(17,51,130,0.06); box-shadow: 0 6px 18px rgba(17,51,130,0.03); margin-bottom: 12px; }}
    .micro-card {{ background: #ffffff; padding:10px; border-radius:10px; border:1px solid rgba(17,51,130,0.04); margin-bottom:12px; }}

    /* chat */
    .chat-window {{ background: #ffffff; border: 1px solid rgba(17,51,130,0.03); padding: 14px; border-radius: 16px; min-height: 260px; max-height: 52vh; overflow:auto; }}
    .msg-row {{ display:flex; gap:12px; margin:8px 0; align-items:flex-end; }}
    .avatar {{ width:36px; height:36px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:700; color:white; font-size:13px; flex:0 0 36px; }}
    .avatar-bot {{ background:var(--accent-blue); }}
    .avatar-user {{ background:var(--text-dark); }}

    /* bubble styling - responsive and wrap text */
    .bubble-bot {{
      display:inline-block;
      background:#F6FAFF;
      padding:12px 16px;
      border-radius:18px;
      max-width:78%;
      white-space:normal;
      word-break:break-word;
      color:var(--accent-blue);
      font-size:15px;
      line-height:1.36;
    }}
    .bubble-user {{
      display:inline-block;
      background:#E8F6EA;
      padding:12px 16px;
      border-radius:18px;
      max-width:78%;
      white-space:normal;
      word-break:break-word;
      color:#063020;
      font-size:15px;
      line-height:1.36;
    }}

    /* inputs/buttons */
    .stButton>button {{ border-radius: 8px; padding: 8px 12px; background: var(--accent-blue); color: #ffffff !important; font-weight:600; border:none; }}
    .stTextInput>div>input, .stNumberInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div {{
      border-radius: 8px; padding: 10px 12px; border: 1px solid rgba(17,51,130,0.06); background:#fff; font-size:15px;
    }}

    /* responsive small screens */
    @media (max-width: 900px) {{
      .block-container {{ margin-left: 0 !important; max-width: 100% !important; padding: 0.6rem !important; }}
      section[data-testid="stSidebar"] {{ position: relative; width: auto; height: auto; border-right:none; }}
      button[title="Toggle sidebar"] {{ display:block !important; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
