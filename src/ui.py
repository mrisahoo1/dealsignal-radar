from html import escape
import streamlit as st


def html(content: str):
    st.markdown(content, unsafe_allow_html=True)


def esc(value) -> str:
    return escape(str(value))


def style():
    html('''<style>
    .stApp {background: #F7F8FA;}
    .block-container {padding: 1.35rem 2.4rem 2rem; max-width: 1560px;}
    header[data-testid="stHeader"] {background: transparent; height: 1rem;}
    [data-testid="stToolbar"], [data-testid="stAppDeployButton"] {display: none !important;}
    h1,h2,h3,p {color: #172C3A;}
    h1 {font-size: 2rem !important; letter-spacing: -.055rem; padding: 0 !important;}
    h3 {font-size: 1.15rem !important; padding: .15rem 0 !important;}
    [data-testid="stVerticalBlock"] {gap: .65rem;}
    .brand,.demo-note,.kpis,.brief,.section-row {font-family:'Segoe UI',sans-serif;}
    .brand {display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;}
    .eyebrow {font: 600 11px 'Segoe UI',sans-serif; letter-spacing: 1.8px; color:#5D727D; text-transform:uppercase;}
    .brand-title {font: 600 30px Georgia,serif; letter-spacing: -.6px; margin: 4px 0 3px;}
    .subtitle {font-size:13px; color:#536873;}
    .badge {font-size:11px; font-weight:650; border:1px solid #C9DDDA; color:#086C62; background:#EAF5F2; border-radius:4px; padding:5px 9px; display:inline-block;}
    .demo-note {background:#EDF1F4; border-left:3px solid #9AAEB8; padding:8px 12px; font-size:12px; color:#465D69; margin:2px 0 8px;}
    .kpis {display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:5px;}
    .kpi {background:white; border:1px solid #DFE6EA; border-radius:6px; padding:12px 17px;}
    .kpi-label {font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#647986;}
    .kpi-value {font-size:27px; font-weight:600; line-height:1.3; letter-spacing:-.8px;}
    .kpi-foot {font-size:11px; color:#6D7F89;}
    .section-row {display:flex; align-items:center; justify-content:space-between; margin:3px 0 5px;}
    .section-title {font-size:18px; font-weight:650;}
    .small {font-size:12px; color:#627782;}
    .brief {background:white; border:1px solid #DBE4E8; border-top:3px solid #138578; border-radius:6px; padding:15px 19px;}
    .brief-grid {display:grid;grid-template-columns: 1.2fr 2.2fr 1.1fr;gap:23px;}
    .company-title {font:600 22px Georgia,serif; margin:5px 0 6px;}
    .why {font-size:12.5px;line-height:1.6; margin-top:7px;}
    .score-pair {display:flex;gap:22px;margin-top:12px;}
    .score {font-size:26px;font-weight:650;line-height:1;}
    .score span {font-size:12px;font-weight:400;color:#70828B;}
    .teal {color:#087F74;}.blue {color:#426486;}
    .mini-label {font-size:11px;color:#667C87;margin-top:5px;}
    .ledger {border-left:2px solid #C2D9D5;padding:0 0 3px 14px;margin:8px 0;}
    .stTabs [data-baseweb="tab-list"] {gap:28px;border-bottom:1px solid #DEE6EB;}
    .stTabs [data-baseweb="tab"] {height:39px;font-size:13px;}
    [data-testid="stWidgetLabel"] p {font-size:12px;}
    [data-testid="stCaptionContainer"] p {font-size:11.5px;}
    @media(max-width:900px) {.block-container{padding:1rem}.brief-grid{grid-template-columns:1fr}.kpis{gap:6px}.kpi{padding:8px}.brand-title{font-size:25px}}
    </style>''')

