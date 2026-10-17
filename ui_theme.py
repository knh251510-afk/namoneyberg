"""NAMONEYBERG 공통 디자인. 단일 스타일 정의로 레이아웃 충돌 방지."""
import streamlit as st
import altair as alt
PALETTE=['#245b78','#b46a43','#3c8278','#8e6c91','#b39845','#647c9a','#b45e70','#667a57']
def apply():
    st.markdown("""<style>
@font-face{font-family:Pretendard;src:url('/app/static/PretendardVariable.woff2') format('woff2');font-weight:100 900;font-display:swap}
:root{
 --nb-primary:#152d43;--nb-accent:#806751;--nb-bg:#ffffff;--nb-surface:#fff;
 --nb-text:#242424;--nb-muted:#686868;--nb-border:#e6e6e6;--nb-soft:#f6f6f6;
 --nb-radius:4px;--nb-font-body:0.875rem;--nb-leading-body:1.1875rem;--nb-font-title:1.625rem;--nb-leading-title:2.1875rem;--nb-space-1:4px;--nb-space-2:8px;--nb-space-3:16px;--nb-space-4:24px;--nb-space-5:32px;
}
*{box-sizing:border-box}
html,body,.stApp{font-family:Pretendard,-apple-system,BlinkMacSystemFont,sans-serif;color:var(--nb-text);background:var(--nb-bg)}
.stApp p,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp button,.stApp label,.stApp input,.stApp a,.stApp table{font-family:Pretendard,-apple-system,sans-serif!important}
.stApp p{font-size:15px;line-height:1.75;font-weight:400}.stApp{font-synthesis:none;text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased}.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-weight:600}.stApp table,.stApp [data-testid="stMetricValue"]{font-variant-numeric:tabular-nums}
.stApp h1{font-size:26px;line-height:35px;letter-spacing:-.6px}
.stApp h2{font-size:22px;line-height:1.4;letter-spacing:-.4px}
.stApp h3{font-size:18px;line-height:1.5;letter-spacing:-.3px}
.stApp h4{font-size:16px;line-height:1.5}
[data-testid="stAppDeployButton"]{display:none}
[data-testid="stMainBlockContainer"]{max-width:1240px;padding:24px 32px}
.stApp [data-testid="stVerticalBlock"]{gap:16px}
.st-key-site_header{border-bottom:1px solid var(--nb-border);padding:8px 0 12px;margin-bottom:0}
.brand-head{display:flex;align-items:center;padding:0;min-height:48px}
.brand-name,.brand-name b{font-size:21px;font-weight:700;color:var(--nb-primary);letter-spacing:-.6px;white-space:nowrap}
.st-key-main_navigation{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;gap:0 22px!important;padding:0!important;background:#fff;border:0;margin:0!important}
.st-key-main_navigation [data-testid="stElementContainer"]{width:auto!important;flex:0 0 auto!important}
.st-key-main_navigation a{border-radius:0!important;white-space:nowrap;padding:12px 0!important;background:transparent!important;border:0!important;border-bottom:2px solid transparent!important;color:#333!important;text-decoration:none!important}
.st-key-main_navigation a p{font-size:14px;line-height:24px;font-weight:500;margin:0}
.st-key-main_navigation a:hover{color:var(--nb-accent)!important}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #8bafdb!important;outline-offset:3px}
.st-key-page_body{padding:12px 0 32px}
.quote-ticker{overflow:hidden;border-bottom:1px solid var(--nb-border);background:#fff;border-radius:0;margin:0 0 24px}
.quote-ticker .quote-item{flex-direction:row;align-items:center;gap:12px;min-width:260px;padding:14px 24px;border-right:0}
.quote-ticker .quote-item>span{font-size:12px;font-weight:500;color:#555}
.quote-ticker .quote-item>b{font-size:16px;font-weight:600}
.quote-ticker .quote-item>strong{font-size:12px;font-weight:500;white-space:nowrap}
.quote-ticker .quote-item>small{display:none}
.quote-track{display:flex;width:max-content;animation:market-scroll 100s linear infinite}
.quote-group{display:flex;flex-shrink:0}
.quote-ticker:hover .quote-track,.quote-ticker:focus-within .quote-track{animation-play-state:paused}
@keyframes market-scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.quote-item{display:flex;flex-direction:column;gap:8px;min-width:168px;padding:16px 24px;border-right:1px solid var(--nb-border);font-variant-numeric:tabular-nums}
.quote-item>span{font-size:12px;color:var(--nb-muted);font-weight:600}
.quote-item>b{font-size:24px;font-weight:700;line-height:1.2;color:var(--nb-text)}
.quote-item>strong{font-size:12px}.quote-item>small{font-size:11px;color:var(--nb-muted)}
.rise{color:#c23838!important}.fall{color:#2463b3!important}.flat{color:#64748b!important}
.market-strip{display:flex;overflow-x:auto;background:#fafafa;border-block:1px solid var(--nb-border);border-radius:0;padding:16px 0;margin:0 0 32px}
.ticker-item{flex:1;min-width:164px;padding:0 16px;border-right:1px solid var(--nb-border);white-space:nowrap}
.ticker-item:last-child{border:0}.ticker-item span{font-size:12px;color:var(--nb-muted)}
.ticker-item strong{font-size:22px;color:var(--nb-primary);margin-left:8px}
.ticker-item small{display:block;font-size:11px;color:var(--nb-muted);margin-top:8px}
.ticker-item .rate-change{font-size:11px}.ticker-item .rate-change span{font-size:10px;margin-left:4px}
.edition-line{display:flex;justify-content:space-between;color:var(--nb-muted);font-size:11px;letter-spacing:1px;padding:8px 0}
.section-heading{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;padding:0 0 16px;margin:24px 0 16px}
.section-kicker{display:none}
.section-heading h2{font-size:26px!important;font-weight:600;margin:4px 0 0;padding:0;color:var(--nb-text)}
.section-heading>a{font-size:12px;color:var(--nb-accent)!important;text-decoration:none}
.page-heading{padding:12px 0 20px;margin-bottom:24px;border-bottom:1px solid #333}
.breadcrumb{font-size:12px;color:var(--nb-muted);margin-bottom:8px}
.page-heading h1{font-size:28px!important;margin:0;padding:0;color:var(--nb-text)}
.research-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-bottom:24px}
.research-card{display:flex;flex-direction:column;min-width:0;padding:24px;border:1px solid var(--nb-border);border-radius:var(--nb-radius);background:var(--nb-surface);color:var(--nb-text)!important;text-decoration:none!important;overflow:hidden;transition:border-color .15s}
.research-card:hover{border-color:var(--nb-accent)}
.brief-image{display:block;width:calc(100% + 48px);max-width:none!important;height:160px;object-fit:cover;margin:-24px -24px 16px}
.card-category{align-self:flex-start;font-size:11px;color:var(--nb-accent);background:#f4eee7;padding:4px 8px;border-radius:4px;margin-bottom:8px}
.research-card h3{font-size:16px!important;line-height:1.6!important;margin:0 0 8px;word-break:keep-all}
.research-card p{font-size:13px!important;color:var(--nb-muted);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card-more{font-size:12px;color:var(--nb-accent);margin-top:auto;padding-top:16px}
.comparison-wrap,.calendar-table-wrap{overflow-x:auto;background:var(--nb-surface);border:1px solid var(--nb-border);border-radius:var(--nb-radius);margin:8px 0 16px}
.comparison-table,.calendar-table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
.comparison-table{min-width:560px}.calendar-table{min-width:650px}
.comparison-table th,.comparison-table td{padding:12px 16px;text-align:right;border-bottom:1px solid var(--nb-border);vertical-align:middle}
.comparison-table th:first-child{text-align:left}
.comparison-table thead th,.calendar-table th{background:var(--nb-soft);color:var(--nb-muted);font-weight:600;font-size:12px}
.comparison-table tbody th{color:var(--nb-primary);font-weight:600;white-space:nowrap}
.comparison-table small{display:block;font-size:11px;line-height:1.5;color:var(--nb-muted);margin-top:4px}
.comparison-table .value{font-size:18px;font-weight:600;color:var(--nb-text);line-height:1.2}
.comparison-table .observation{white-space:nowrap}
.comparison-table tr:last-child td,.comparison-table tr:last-child th{border-bottom:0}
.comparison-table tbody tr:hover,.calendar-table tbody tr:hover{background:#f8fafc}
.quote-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:24px}
.quote-grid .quote-item{min-width:0;border:1px solid var(--nb-border);border-radius:var(--nb-radius);background:var(--nb-surface)}
.calendar-day{display:flex;gap:16px;align-items:center;background:#f1ece6;padding:12px 16px;margin-top:24px;color:#6e503b;font-size:15px;font-weight:700;border-radius:6px 6px 0 0}
.calendar-day span{font-size:12px;font-weight:400}
.calendar-table th{padding:12px 16px;text-align:right;border-bottom:1px solid var(--nb-border)}
.calendar-table th:nth-child(-n+2){text-align:left}
.calendar-table td{padding:16px;border-bottom:1px solid var(--nb-border)}
.calendar-table small{display:block;font-size:11px;color:var(--nb-muted);margin-top:4px}
.cal-time{color:var(--nb-muted);white-space:nowrap}.cal-title{color:var(--nb-text);min-width:180px}.cal-number{text-align:right;white-space:nowrap}
.glossary-item{border:0;border-bottom:1px solid var(--nb-border);border-radius:0;background:#fff;padding:24px 0;margin-bottom:8px}
.glossary-title{display:flex;justify-content:space-between;gap:16px}.glossary-title b{font-size:16px;color:var(--nb-primary)}
.glossary-title span{white-space:nowrap;color:#947144;font-size:13px}
.glossary-item p{font-size:14px;color:var(--nb-text);margin:12px 0}
.glossary-item dl{display:grid;grid-template-columns:72px 1fr;gap:8px 16px;margin:0;font-size:13px;line-height:1.8}
.glossary-item dt{color:var(--nb-accent);font-weight:600}.glossary-item dd{margin:0;color:var(--nb-muted)}
.news-headline{display:flex;gap:16px;align-items:baseline;padding:12px 0;border-bottom:1px solid var(--nb-border);font-size:14px}
.news-headline span{color:var(--nb-muted);font-size:12px;min-width:48px}
.news-list-item{padding:16px 0;border-bottom:1px solid var(--nb-border)}
.news-list-item small{display:block;font-size:12px;color:var(--nb-muted);margin-top:8px}
.news-headline a,.news-list-item a{color:var(--nb-primary)!important;text-decoration:none}
.news-headline a:hover,.news-list-item a:hover{text-decoration:underline}
.terminal-footer{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;margin-top:32px;padding:24px 16px;border-top:1px solid var(--nb-border)}
.terminal-footer b{color:var(--nb-primary);font-size:14px}.terminal-footer nav{display:flex;gap:24px}.terminal-footer a{font-size:12px;color:var(--nb-muted)!important;text-decoration:none}
.st-key-comparison_tray{background:var(--nb-surface);border:1px solid var(--nb-border);padding:16px!important;border-radius:8px;margin:8px 0 24px}.st-key-comparison_tray [data-testid="stCaptionContainer"] p{font-size:12px;line-height:16px}
/* Preserve BaseWeb geometry: never style anonymous inner divs globally. */
[data-testid="stSelectbox"] label,[data-testid="stMultiSelect"] label,[data-testid="stTextInput"] label{font-size:13px!important;color:var(--nb-muted)!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div,[data-testid="stTextInput"] [data-baseweb="input"]{background:var(--nb-surface)!important;border:1px solid var(--nb-border)!important;border-radius:var(--nb-radius)!important;min-height:40px;box-shadow:none}
[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within>div,[data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within>div,[data-testid="stTextInput"] [data-baseweb="input"]:focus-within{border-color:#7395bf!important;box-shadow:0 0 0 3px #dfe8f4!important}
[data-testid="stExpander"]{background:var(--nb-surface);border:1px solid var(--nb-border);border-radius:var(--nb-radius)}
[data-testid="stExpander"] summary{font-size:13px;color:var(--nb-muted);padding:12px 16px}
[data-testid="stButton"] button,[data-testid="stDownloadButton"] button{min-height:40px;padding:8px 16px;background:var(--nb-surface);border:1px solid var(--nb-border);border-radius:var(--nb-radius);color:var(--nb-primary);font-size:14px}
[data-testid="stButton"] button:hover,[data-testid="stDownloadButton"] button:hover{background:var(--nb-soft);border-color:#a5b1bf}
[data-testid="stButton"] button[kind="primary"]{background:var(--nb-accent);color:#fff;border-color:var(--nb-accent)}
[data-testid="stButton"] button:disabled{opacity:.5;cursor:not-allowed}
[data-testid="stMetric"]{padding:24px;background:var(--nb-surface);border:1px solid var(--nb-border);border-radius:var(--nb-radius)}
[data-testid="stMetricValue"]{font-size:28px;color:var(--nb-primary)}
[data-testid="stTabs"] [role="tablist"]{gap:0;border-bottom:1px solid var(--nb-border)}
[data-testid="stTabs"] [role="tab"]{height:48px;padding:8px 24px;background:transparent;color:var(--nb-muted)}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--nb-accent)!important;font-weight:700}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--nb-accent)}
[data-testid="stButtonGroup"] button[kind="segmented_controlActive"],[data-testid="stButtonGroup"] button[aria-pressed="true"]{background:#806751!important;color:#fff!important;border-color:#806751!important}
[data-testid="stSegmentedControl"] [role="radiogroup"]{gap:4px;flex-wrap:wrap}
[data-testid="stSegmentedControl"] button{border-radius:4px;padding:8px 16px;background:var(--nb-surface);border-color:var(--nb-border);color:var(--nb-muted)}
[data-testid="stSegmentedControl"] button[aria-checked="true"],[data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:var(--nb-primary)!important;color:#fff!important}
.st-key-global_brief_panel{background:#fff;border:0;border-radius:0;padding:0!important;margin:8px 0 24px;box-shadow:none}
.st-key-global_brief_panel .section-heading{margin:0 0 16px;padding-bottom:16px;border-bottom:1px solid var(--nb-border)}
.brief-lead{padding:28px 32px;margin:8px 0 24px;background:#f8f6f3;border-top:2px solid var(--nb-accent);border-bottom:0}
.brief-lead h3{font-size:22px!important;font-weight:600!important;line-height:1.5!important;margin:0 0 12px;padding:0;color:var(--nb-primary)}
.brief-lead p{font-size:15px!important;line-height:1.85!important;color:var(--nb-text);margin:0}
.brief-topic{padding:24px 0 28px;margin:0 0 16px;border-bottom:1px solid var(--nb-border)}
.brief-topic:last-child{margin-bottom:0;border-bottom:0}
.brief-topic h4{font-size:18px!important;font-weight:600!important;line-height:1.6!important;margin:0 0 16px;padding:0;color:var(--nb-primary)}
.brief-topic dl{display:grid;grid-template-columns:80px 1fr;gap:12px 16px;margin:0;font-size:15px;line-height:1.85}
.brief-topic dt{font-size:12px;font-weight:600;color:var(--nb-accent);padding-top:2px}.brief-topic dd{margin:0;color:var(--nb-text);word-break:keep-all;overflow-wrap:anywhere}
.brief-sources{margin-top:16px;font-size:12px;color:var(--nb-muted)}.brief-sources summary{cursor:pointer;padding:4px 0}
.brief-sources a{display:block;font-size:12px;color:var(--nb-muted)!important;line-height:1.7;margin:8px 0}
.brief-layout{display:grid;grid-template-columns:180px minmax(0,1fr);gap:24px;align-items:start;margin-top:16px}
.brief-art{border:1px solid var(--nb-border);border-radius:var(--nb-radius);overflow:hidden;background:#f7f3ee}
.brief-art img{display:block;width:100%;height:auto}.brief-art span{display:block;padding:12px 16px;color:var(--nb-accent);font-size:12px}
.brief-category-banner{display:block;width:180px;max-width:100%;height:auto;margin:16px 0}
@media(max-width:900px){.quote-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.research-grid{gap:16px}}
@media(max-width:800px){.st-key-site_header [data-testid="stHorizontalBlock"]{flex-wrap:wrap}.st-key-site_header [data-testid="stColumn"]{width:100%!important;flex:1 1 100%!important}.brand-head{min-height:36px}.st-key-main_navigation{gap:0 18px!important}.quote-ticker .quote-item{padding:12px 16px;min-width:240px}.brief-lead{padding:20px}.brief-lead h3{font-size:19px!important}[data-testid="stMainBlockContainer"]{padding:24px 16px}.st-key-main_navigation{gap:0 16px!important}.st-key-main_navigation a p{font-size:13px}.st-key-page_body{padding:8px 8px 16px}.brand-name,.brand-name b{font-size:24px}.brief-topic dl{grid-template-columns:1fr;gap:4px}.brief-topic dd{margin-bottom:12px}.research-grid{grid-template-columns:1fr}.brief-layout{grid-template-columns:1fr}.brief-art{width:180px}}
@media(max-width:480px){[data-testid="stMainBlockContainer"]{padding:16px 12px}.st-key-page_body{padding:8px 0 16px}.st-key-global_brief_panel{padding:16px!important}.quote-grid{grid-template-columns:1fr}.glossary-item{padding:16px}.glossary-title{flex-wrap:wrap}.section-heading h2{font-size:20px!important}}
@media(prefers-reduced-motion:reduce){.quote-track{animation:none}.quote-ticker{overflow-x:auto}}
</style>""",unsafe_allow_html=True)
    def portal():
        return {'config':{'background':'#fff','font':'Pretendard','view':{'stroke':None},'range':{'category':PALETTE},'axis':{'labelColor':'#596469','titleColor':'#234657','gridColor':'#ecece6','domainColor':'#ccd6e3','labelFont':'Pretendard','titleFont':'Pretendard'},'legend':{'labelColor':'#596469','labelFont':'Pretendard','titleFont':'Pretendard'},'title':{'color':'#345780','font':'Pretendard'}}}
    alt.themes.register('macro_portal',portal)
    alt.themes.enable('macro_portal')
