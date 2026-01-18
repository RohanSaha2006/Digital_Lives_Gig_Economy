import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="The Gig Economy That Isn't",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DATA
# -----------------------------------------------------------------------------
WORKERS = {
    'zanzibar': {
        'title': 'Zanzibar Informal Worker',
        'Experience': '13+ years',
        'Structure': 'Bus driver + Wakala shop',
        'Schedule': '8am-5:30pm, 7 days/week',
        'Income': 'Variable, covers basic needs',
        'Autonomy': "Self-employed but can't decide when to rest",
        'Gig Score': '9/10 (90%)'
    },
    'supplemental': {
        'title': 'Supplemental Gig Worker',
        'Experience': 'Few months to 2 years',
        'Structure': 'Platform + stable main job',
        'Schedule': 'Flexible by choice',
        'Income': 'Extra/discretionary',
        'Autonomy': 'High - can reject tasks',
        'Gig Score': '5/10 (50%)'
    },
    'dependent': {
        'title': 'Dependent Gig Worker',
        'Experience': 'Varies',
        'Structure': 'Platform as sole income',
        'Schedule': 'Must work long hours',
        'Income': 'Below poverty despite long hours',
        'Autonomy': 'Illusory - must accept all work',
        'Gig Score': '10/10 (100%)'
    }
}

dimensions = ['Income Uncertainty', 'Contractual Security', 'Income Dependency', 'Autonomy Over Time', 'Digital Mediation']

scores = {
    'Zanzibar': [2, 2, 2, 2, 1],
    'Supplemental': [1, 2, 0, 0, 2],
    'Dependent': [2, 2, 2, 2, 2]
}

# -----------------------------------------------------------------------------
# THEME CONFIGURATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎨 Appearance")
    theme = st.radio("Select View Mode:", ["Clear Dark Mode", "High Visibility Light Mode"], index=0)

if theme == "Clear Dark Mode":
    bg_color = "#0e1117"
    text_color = "#ffffff"
    secondary_bg = "#1f2937"
    card_shadow = "rgba(0,0,0,0.6)"
    chart_grid = "#374151"
    border_color = "#374151"
    finding_bg = "linear-gradient(135deg, #1f2937 0%, #111827 100%)"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    secondary_bg = "#f3f4f6"
    card_shadow = "rgba(0,0,0,0.1)"
    chart_grid = "#e5e7eb"
    border_color = "#d1d5db"
    finding_bg = "linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)"

# -----------------------------------------------------------------------------
# CUSTOM CSS
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    /* Theme-aware variables */
    :root {{
        --bg-color: {bg_color};
        --text-color: {text_color};
        --secondary-bg: {secondary_bg};
        --border-color: {border_color};
    }}

    .stApp {{ background-color: var(--bg-color); color: var(--text-color); }}
    
    /* Global Text Styling */
    h1, h2, h3, p, span, li, label, .stMetric div {{
        color: var(--text-color) !important;
    }}

    /* Worker Cards - Always high contrast */
    .worker-card-zanzibar {{ 
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
        border: 3px solid #60a5fa; 
    }}
    .worker-card-supplemental {{ 
        background: linear-gradient(135deg, #065f46 0%, #10b981 100%); 
        border: 3px solid #34d399; 
    }}
    .worker-card-dependent {{ 
        background: linear-gradient(135deg, #991b1b 0%, #ef4444 100%); 
        border: 3px solid #f87171; 
    }}
    .worker-card {{ 
        padding: 1.5rem; 
        border-radius: 12px; 
        color: #ffffff !important; 
        box-shadow: 0 8px 16px {card_shadow}; 
        margin-bottom: 1rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }}
    .worker-card h3 {{ font-size: 1.25rem; margin-bottom: 0.5rem; }}
    .worker-card p {{ font-size: 0.85rem; margin-bottom: 0.25rem; line-height: 1.2; }}
    .worker-card strong {{ font-weight: 700; }}
    .worker-card h3, .worker-card p, .worker-card strong {{ 
        color: #ffffff !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    
    /* Findings Box */
    .finding-box {{
        background: {finding_bg};
        border-left: 6px solid #3b82f6;
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px {card_shadow};
    }}
    .finding-box h4 {{ color: #3b82f6 !important; margin: 0 0 0.5rem 0; }}
    .finding-box p {{ color: var(--text-color) !important; margin: 0; }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: var(--secondary-bg);
        border-radius: 4px;
        color: var(--text-color);
        padding: 10px 20px;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #3b82f6;
        color: #ffffff !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: #3b82f6;
        color: #ffffff !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--secondary-bg);
    }}
    
    /* Expander Styling */
    .streamlit-expanderHeader {{
        background-color: var(--secondary-bg) !important;
        border-radius: 8px !important;
    }}

    /* Interactive Explorer Diagram */
    .explorer-container {{
        display: grid;
        grid-template-columns: 1fr 0.8fr 1fr;
        grid-template-rows: auto auto;
        gap: 2rem;
        align-items: center;
        padding: 2rem;
        background: var(--bg-color);
        border-radius: 12px;
        position: relative;
    }}
    
    .phone-center {{
        grid-column: 2;
        grid-row: 1 / span 2;
        justify-self: center;
        padding: 1rem;
        background: #6d5dfc;
        border: 8px solid #332d4a;
        border-radius: 40px;
        width: 180px;
        height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        color: white !important;
        text-align: center;
    }}
    
    .phone-screen {{
        background: white;
        width: 140px;
        height: 240px;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #332d4a !important;
    }}
    
    .satellite-card {{
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px {card_shadow};
        transition: transform 0.3s ease;
        height: 100%;
        min-height: 200px;
    }}
    .satellite-card:hover {{
        transform: translateY(-5px);
        border-color: #3b82f6;
    }}
    .satellite-card h4 {{ margin: 0.5rem 0; font-size: 1.2rem; }}
    .satellite-card ul {{ padding-left: 1.2rem; margin: 0; }}
    .satellite-card li {{ font-size: 0.9rem; margin-bottom: 0.3rem; }}
    
    .satellite-icon {{
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}

    .insight-card {{
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        border-left: 5px solid;
    }}

    @media (max-width: 768px) {{
        .explorer-container {{
            grid-template-columns: 1fr;
            grid-template-rows: auto;
        }}
        .phone-center {{
            grid-row: 1;
            grid-column: 1;
        }}
    }}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR CONTENT
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📚 Research Info")
    st.write("**Authors:** Rohan Saha, Shambhavi Srivastava")
    st.write("**Institution:** IIT Madras Zanzibar")
    st.write("**Course:** Z2106 Digital Lives")
    st.write("**Date:** Dec 2025 - Jan 2026")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Zanzibar Score", "9/10", "90% Gig-ness")
    st.metric("Workers Interviewed", "6")
    st.metric("Index Dimensions", "5")
    
    st.markdown("---")
    st.info("Use the **Explorer** tab for the interactive conceptual model.")

# -----------------------------------------------------------------------------
# MAIN LAYOUT
# -----------------------------------------------------------------------------
st.title("The Gig Economy That Isn't")
st.markdown("### Ethnographic Research on Gig Work in Zanzibar")

tabs = st.tabs([
    "Overview", 
    "Gig-ness Index", 
    "Autonomy & Control", 
    "Economic Security", 
    "Digital Mediation", 
    "Key Findings", 
    "Interactive Explorer"
])

# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW
# -----------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### Worker Profiles")
    st.write("Comparison of Zanzibar informal workers with platform gig workers.")
    
    col1, col2, col3 = st.columns(3)
    
    def worker_card(col, w_type, w_class):
        w_data = WORKERS[w_type]
        with col:
            st.markdown(f"""
            <div class="worker-card {w_class}">
                <h3>{w_data['title']}</h3>
                <p><strong>Gig Score:</strong> {w_data['Gig Score']}</p>
                <hr style="margin: 10px 0; border-color: rgba(255,255,255,0.2);">
                <p><strong>Experience:</strong> {w_data['Experience']}</p>
                <p><strong>Structure:</strong> {w_data['Structure']}</p>
                <p><strong>Schedule:</strong> {w_data['Schedule']}</p>
                <p><strong>Income:</strong> {w_data['Income']}</p>
                <p><strong>Autonomy:</strong> {w_data['Autonomy']}</p>
            </div>
            """, unsafe_allow_html=True)
            
    worker_card(col1, 'zanzibar', 'worker-card-zanzibar')
    worker_card(col2, 'supplemental', 'worker-card-supplemental')
    worker_card(col3, 'dependent', 'worker-card-dependent')

# -----------------------------------------------------------------------------
# TAB 2: GIG-NESS INDEX
# -----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("### The Gig-ness Index Comparison")
    
    # --- INPUT SECTION ---
    with st.expander("🧮 Interactive: Calculate Custom Gig-ness Score", expanded=True):
        st.markdown("#### Input Your Dimensions")
        st.write("Adjust the sliders below to see how different factors affect the Gig-ness Index.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            u_inc = st.slider("Income Uncertainty", 0, 2, 1, help="0: Stable, 2: High Volatility")
            c_sec = st.slider("Contractual Security", 0, 2, 1, help="0: Strong Contract, 2: No Contract")
        with c2:
            i_dep = st.slider("Income Dependency", 0, 2, 1, help="0: Supplementary, 2: Sole Source")
            a_time = st.slider("Autonomy Over Time", 0, 2, 1, help="0: High Control, 2: Algorithmic/Market Control")
        with c3:
            d_med = st.slider("Digital Mediation", 0, 2, 0, help="0: Low/Tool-only, 2: Managed by App")
        
        user_scores = [u_inc, c_sec, i_dep, a_time, d_med]
        total_score = sum(user_scores)
        percent_score = (total_score / 10) * 100
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # --- OUTPUT SECTION (CHART) ---
        fig = go.Figure()
        # Pre-defined profiles
        fig.add_trace(go.Scatterpolar(r=scores['Zanzibar'], theta=dimensions, name='Zanzibar (9/10)', line=dict(color='#3b82f6', width=2, dash='dot')))
        fig.add_trace(go.Scatterpolar(r=scores['Supplemental'], theta=dimensions, name='Supplemental (5/10)', line=dict(color='#10b981', width=2, dash='dot')))
        fig.add_trace(go.Scatterpolar(r=scores['Dependent'], theta=dimensions, name='Dependent (10/10)', line=dict(color='#ef4444', width=2, dash='dot')))
        
        # User dynamic profile
        fig.add_trace(go.Scatterpolar(r=user_scores, theta=dimensions, name='Your Calculation', fill='toself', line=dict(color='#fbbf24', width=4)))
        
        fig.update_layout(
            polar=dict(
                bgcolor=secondary_bg, 
                radialaxis=dict(gridcolor=chart_grid, tickfont=dict(color=text_color), range=[0, 2.5]),
                angularaxis=dict(gridcolor=chart_grid, tickfont=dict(color=text_color))
            ), 
            paper_bgcolor=bg_color,
            font=dict(color=text_color),
            legend=dict(font=dict(color=text_color)),
            margin=dict(t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # --- OUTPUT SECTION (METRICS) ---
        st.markdown("#### Your Result")
        st.metric("Total Gig-ness Score", f"{total_score}/10", f"{percent_score}%", delta_color="inverse")
        
        if percent_score >= 80:
            st.error("Classification: **Extreme Precarity** (High Gig-ness)")
        elif percent_score >= 50:
            st.warning("Classification: **Moderate Gig-ness**")
        else:
            st.success("Classification: **Low Precariousness**")
            
        st.markdown("#### Research Benchmarks")
        st.info("The Zanzibar average (9/10) closely tracks the Dependent Gig Worker pattern, despite the absence of digital platforms.")

# -----------------------------------------------------------------------------
# TAB 3: AUTONOMY & CONTROL
# -----------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### Autonomy & Control Analysis")
    st.write("Comparative analysis of perceived vs. actual autonomy.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Comparison of Control")
        comparison_data = {
            'Dimension': ['Task Refusal', 'Schedule Control', 'Rest Days', 'Price Setting'],
            'Zanzibar': ['High (Can close shop)', 'Moderate (Customer demand)', 'Low (7 days/week)', 'Moderate (Negotiable)'],
            'Dependent Gig': ['None (Penalty)', 'None (Algo enforced)', 'None (Income loss)', 'None (Algo set)']
        }
        df_autonomy = pd.DataFrame(comparison_data)
        st.table(df_autonomy)
    
    with col2:
        st.markdown("#### Autonomy Perception Score")
        # Creating a bar chart for autonomy comparison
        categories = ['Task Choice', 'Time Control', 'Place Flexibility', 'Price Power']
        fig_bar = go.Figure(data=[
            go.Bar(name='Zanzibar', x=categories, y=[0.8, 0.4, 0.9, 0.6], marker_color='#3b82f6'),
            go.Bar(name='Dependent Gig', x=categories, y=[0.1, 0.1, 0.2, 0.0], marker_color='#ef4444')
        ])
        fig_bar.update_layout(
            barmode='group',
            paper_bgcolor=bg_color,
            plot_bgcolor=secondary_bg,
            font=dict(color=text_color),
            xaxis=dict(gridcolor=chart_grid),
            yaxis=dict(gridcolor=chart_grid, title="Autonomy Index (0-1)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("#### Key Insight")
    st.info("**Finding:** While Zanzibar informal workers technically own their means of production (shop/bus), market pressures and high competition enforce a schedule just as rigid as the algorithmic control in dependent gig work.")

# -----------------------------------------------------------------------------
# TAB 4: ECONOMIC SECURITY
# -----------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### Economic Security & Vulnerability")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Income Consistency Patterns")
        # Refining the line chart
        x = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        fig_inc = go.Figure()
        fig_inc.add_trace(go.Scatter(x=x, y=[80, 82, 81, 83], name='Formal Job (Stable)', line=dict(color='#10b981', dash='dot', width=2)))
        fig_inc.add_trace(go.Scatter(x=x, y=[40, 95, 30, 85], name='Zanzibar Informal (Volatile)', line=dict(color='#3b82f6', width=4)))
        fig_inc.add_trace(go.Scatter(x=x, y=[50, 45, 55, 48], name='Dependent Gig (Stagnant)', line=dict(color='#ef4444', width=4)))
        
        fig_inc.update_layout(
            title="Daily/Weekly Income Variance",
            paper_bgcolor=bg_color,
            plot_bgcolor=secondary_bg,
            font=dict(color=text_color),
            xaxis=dict(gridcolor=chart_grid),
            yaxis=dict(gridcolor=chart_grid, title="Daily Earnings (Local Normalization)")
        )
        st.plotly_chart(fig_inc, use_container_width=True)
        
    with col2:
        st.markdown("#### Structural Vulnerabilities")
        st.markdown("""
        - **No Institutional Safety Nets**: All three profiles rely on personal savings for health emergencies.
        - **Equipment Risks**: Small-scale operators (bus/shop) face catastrophic income loss if tools break.
        - **Platform Dependency**: Gig workers face "Algo-precarity"—sudden changes in incentives or deactivation.
        """)
        st.error("Conclusion: 100% of interviewed Zanzibar informal workers had zero insurance cover.")

# -----------------------------------------------------------------------------
# TAB 5: DIGITAL MEDIATION
# -----------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### Digital Mediation & Technology")
    st.write("How technology shapes the workflow and management of labor.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Platform Gig Work")
        st.write("Algorithm as Manager: Tasks, pay, and behavior are controlled via the app.")
        st.progress(1.0)
        st.caption("100% Algorithmic Management")
        
    with col2:
        st.markdown("#### Zanzibar Informal Work")
        st.write("Digital as Tool: WhatsApp/Mobile Money used for communication and payments only.")
        st.progress(0.35)
        st.caption("35% Digital Tool Usage (Non-Managerial)")

# -----------------------------------------------------------------------------
# TAB 6: KEY FINDINGS
# -----------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### Major Research Findings")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""
        <div class="finding-box">
            <h4>Finding 1: Gig-ness Without Platforms</h4>
            <p>Zanzibar workers score 90% on Gig-ness Index despite zero platform involvement. This proves precarity is structural, not just technological.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="finding-box" style="border-left-color: #fbbf24;">
            <h4 style="color: #fbbf24 !important;">Finding 2: The Time-Poverty Trap</h4>
            <p>High autonomy in theory but zero autonomy in practice. Workers must work 14+ hours to meet basic survival costs.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="finding-box" style="border-left-color: #10b981;">
            <h4 style="color: #34d399 !important;">Finding 3: Digital Tools != Digital Management</h4>
            <p>Zanzibar workers use WhatsApp and Mobile Money extensively, yet remain outside the "platform economy" management structures.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="finding-box" style="border-left-color: #a855f7;">
            <h4 style="color: #a855f7 !important;">Finding 4: Invisiblized Skills</h4>
            <p>Informal workers manage complex logistics, customer relations, and financial risks without the branding or support of platforms.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="finding-box" style="border-left-color: #ef4444; background: rgba(153, 27, 27, 0.1);">
        <h4 style="color: #f87171 !important;">⚠️ Policy Implication</h4>
        <p>Labor protections must focus on the <b>vulnerability of the condition</b> (the "gig-ness") rather than the <b>method of work</b> (the app). Regulating the gig economy requires a post-platform perspective.</p>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 7: INTERACTIVE EXPLORER
# -----------------------------------------------------------------------------
with tabs[6]:
    st.markdown("""
### The Mobile Phone as a Primary Workplace
A conceptual analysis of platform-free gig labor in Zanzibar.

<div class="explorer-container">
<div class="satellite-card">
<div class="satellite-icon">📞</div>
<h4>Phone Calls</h4>
<p><strong>CUSTOMER ACCESS</strong></p>
<ul>
<li>Direct voice communication</li>
<li>Immediate coordination</li>
<li>Personal relationships</li>
</ul>
</div>

<div class="phone-center">
<div class="phone-screen">
<span style="font-size: 3rem;">📱</span>
</div>
<p style="font-weight: bold; margin:0;">THE MOBILE PHONE</p>
<p style="font-size: 0.7rem;">DECENTRALIZED WORKPLACE</p>
</div>

<div class="satellite-card">
<div class="satellite-icon">💬</div>
<h4>WhatsApp</h4>
<p><strong>WORK COORDINATION</strong></p>
<ul>
<li>Order management</li>
<li>Schedule negotiation</li>
<li>Customer messaging</li>
</ul>
</div>

<div class="satellite-card">
<div class="satellite-icon">💰</div>
<h4>Mobile Money</h4>
<p><strong>PAYMENT SYSTEM</strong></p>
<ul>
<li>Instant wage receipt</li>
<li>No bank required</li>
<li>Digital transactions</li>
</ul>
</div>

<div class="satellite-card">
<div class="satellite-icon">✅</div>
<h4>No Algorithm</h4>
<p><strong>AUTONOMY RETAINED</strong></p>
<ul>
<li>Worker sets terms</li>
<li>No ratings surveillance</li>
<li>Direct negotiation</li>
</ul>
</div>
</div>

<div style="display: flex; gap: 20px; justify-content: center; margin-top: 1rem; font-size: 0.8rem;">
<span><span style="color: #10b981;">●</span> <b>Enabling Functions:</b> Tools workers control</span>
<span><span style="color: #ef4444;">●</span> <b>Structural Risk:</b> Precarity remains</span>
</div>

<div class="insight-card" style="background: rgba(59, 130, 246, 0.1); border-color: #3b82f6;">
<h5 style="color: #3b82f6 !important; margin: 0 0 0.5rem 0;">📊 CONCEPTUAL INSIGHT</h5>
<p style="font-size: 0.95rem;">This figure conceptualizes the phone <b>not as a platform, but as a decentralized workplace</b>. Unlike platform gig work where proprietary apps mediate all interactions and enable algorithmic control, Zanzibar's informal workers use general-purpose communication tools (calls, WhatsApp, mobile money) that <b>they control</b>. The phone enables coordination without <i>controlling</i> the worker.</p>
</div>

<div class="insight-card" style="background: rgba(251, 191, 36, 0.1); border-color: #fbbf24;">
<h5 style="color: #fbbf24 !important; margin: 0 0 0.5rem 0;">🔑 KEY THEORETICAL CONTRIBUTION</h5>
<p style="font-size: 0.95rem;">This diagram visually demonstrates that <b>digital mediation ≠ platform control</b>. Workers can adopt mobile technology for efficiency gains without surrendering autonomy to algorithms. This challenges the assumption that "going digital" necessarily requires platform intermediaries.</p>
</div>

<div style="margin-top: 2rem; padding: 1rem; background: var(--secondary-bg); border-radius: 8px; text-align: center; font-size: 0.8rem;">
<p><b>Data Source:</b> Deep ethnographic interviews with informal workers in Zanzibar (Dec 2025 - Jan 2026)</p>
<p><b>Research Team:</b> Shambhavi & Rohan | Indian Institute of Technology Madras - Zanzibar (IITMZ)</p>
</div>
""", unsafe_allow_html=True)
