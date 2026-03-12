"""
PokerGuys - Texas Hold'em Session Tracker
MVP: Record sessions, track buy-ins/final stacks, validate table balance
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path
import json
import uuid

# Database
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from dateutil import parser

# Supabase (optional - for community features)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Config
st.set_page_config(
    page_title="PokerGuys",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== COMMUNITY / LOGIN SYSTEM ==============
COMMUNITY_INFO = """
## 🏆 What is a Community?

A **Community** is your poker group — friends, regular players, or club members who play together.

### Features:
- **Shared Session History** — All members see the same sessions
- **Player Statistics** — Track performance across all sessions
- **Community Leaderboard** — See who's winning the most

### How it works:
1. One person creates a community (becomes the owner)
2. Gets a **6-character code** (e.g., "DHILLL")
3. Shares the code with members
4. Everyone enters the code to join and see the same data
"""

# Supabase config - can be set via environment or use demo
SUPABASE_URL = "https://oycwgywdddjfkmvxgaij.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im95Y3dneXdkZGprZm1teGdhaWoiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY0OTM5OTIwMCwiZXhwIjoxOTY0OTc1MjAwfQ.Uu4hH6fN17L8dK2zD3qZ9h5vY6xR2tW8kM4pL1qN3sM"

def get_supabase_client() -> Optional[Client]:
    """Get Supabase client if available"""
    if not SUPABASE_AVAILABLE:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return None

def init_community_state():
    """Initialize community-related session state"""
    if 'community_logged_in' not in st.session_state:
        st.session_state.community_logged_in = False
    if 'community_code' not in st.session_state:
        st.session_state.community_code = None
    if 'community_name' not in st.session_state:
        st.session_state.community_name = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True

def render_welcome_modal():
    """Render the welcome/login modal"""
    if st.session_state.get('community_logged_in', False):
        return True
    
    # Custom CSS for modal
    modal_css = """
    <style>
    /* Centered login container */
    .login-container {
        max-width: 500px;
        margin: 50px auto;
        padding: 40px;
        background: linear-gradient(145deg, #1e2329, #2a2e39);
        border-radius: 16px;
        border: 1px solid #3a3f4a;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        text-align: center;
    }
    
    .login-logo {
        font-size: 60px;
        margin-bottom: 20px;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: bold;
        color: #f0b90b;
        margin-bottom: 10px;
    }
    
    .login-subtitle {
        color: #888;
        margin-bottom: 30px;
        font-size: 14px;
    }
    
    .community-info-box {
        background: #0b0e11;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        text-align: left;
    }
    
    .community-info-box h3 {
        color: #f0b90b !important;
        font-size: 16px;
        margin-bottom: 12px;
    }
    
    .community-info-box ul {
        color: #aaa;
        font-size: 13px;
        padding-left: 20px;
        line-height: 1.8;
    }
    
    .divider {
        display: flex;
        align-items: center;
        margin: 25px 0;
        color: #555;
        font-size: 12px;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #333;
    }
    
    .divider span {
        padding: 0 15px;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #f0b90b, #d49a0a);
        color: #000;
        border: none;
        padding: 14px 28px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 15px;
        cursor: pointer;
        width: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(240, 185, 11, 0.3);
    }
    
    .btn-secondary {
        background: transparent;
        color: #f0b90b;
        border: 2px solid #f0b90b;
        padding: 12px 26px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        width: 100%;
        transition: all 0.2s;
    }
    
    .btn-secondary:hover {
        background: rgba(240, 185, 11, 0.1);
    }
    
    .input-group {
        margin-bottom: 15px;
    }
    
    .input-group label {
        display: block;
        text-align: left;
        color: #aaa;
        font-size: 12px;
        margin-bottom: 6px;
    }
    
    .input-group input {
        width: 100%;
        padding: 12px 16px;
        background: #0b0e11;
        border: 1px solid #333;
        border-radius: 8px;
        color: #fff;
        font-size: 16px;
        box-sizing: border-box;
    }
    
    .input-group input:focus {
        outline: none;
        border-color: #f0b90b;
    }
    
    .error-msg {
        background: rgba(246, 70, 93, 0.1);
        border: 1px solid #f6465d;
        color: #f6465d;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 13px;
    }
    
    .success-msg {
        background: rgba(11, 138, 78, 0.1);
        border: 1px solid #0b8a4e;
        color: #0b8a4e;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 13px;
    }
    
    .back-link {
        color: #666;
        font-size: 13px;
        cursor: pointer;
        margin-top: 15px;
        display: inline-block;
    }
    
    .back-link:hover {
        color: #f0b90b;
    }
    
    /* Hide Streamlit elements in modal */
    .login-container + div {
        display: none;
    }
    </style>
    """
    
    st.markdown(modal_css, unsafe_allow_html=True)
    
    # Initialize login step
    if 'login_step' not in st.session_state:
        st.session_state.login_step = 'initial'  # initial, join, create, enter_name
    
    # Container for the login UI
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Step 1: Initial choice
    if st.session_state.login_step == 'initial':
        st.markdown('<div class="login-logo">🃏</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Welcome to PokerGuys</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Track your poker sessions with friends</div>', unsafe_allow_html=True)
        
        # Community info (collapsible)
        with st.expander("ℹ️ What is a Community?"):
            st.markdown(COMMUNITY_INFO)
        
        st.markdown('<div class="divider"><span>GET STARTED</span></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 I Have a Code", use_container_width=True, type="primary"):
                st.session_state.login_step = 'join'
                st.rerun()
        with col2:
            if st.button("✨ Create New Community", use_container_width=True):
                st.session_state.login_step = 'create'
                st.rerun()
    
    # Step 2: Join existing community
    elif st.session_state.login_step == 'join':
        st.markdown('<div class="login-logo">🔗</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Join a Community</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Enter the 6-character code shared by your community</div>', unsafe_allow_html=True)
        
        community_code = st.text_input("Community Code", placeholder="e.g., DHILLL", max_chars=10).upper()
        user_name = st.text_input("Your Name", placeholder="Your nickname").strip()
        
        if st.button("Join Community", type="primary", use_container_width=True):
            if not community_code:
                st.error("Please enter a community code")
            elif not user_name:
                st.error("Please enter your name")
            else:
                # Try to join
                sb = get_supabase_client()
                if sb:
                    try:
                        # Find community by code
                        result = sb.table('communities').select('*').ilike('code', community_code).execute()
                        if result.data:
                            community = result.data[0]
                            # Add member
                            try:
                                sb.table('community_members').insert({
                                    'community_id': community['id'],
                                    'user_name': user_name,
                                    'role': 'member'
                                }).execute()
                            except:
                                pass  # May already be a member
                            
                            # Success
                            st.session_state.community_logged_in = True
                            st.session_state.community_code = community_code
                            st.session_state.community_name = community['name']
                            st.session_state.user_name = user_name
                            st.session_state.show_login = False
                            st.rerun()
                        else:
                            st.error("❌ Community not found. Check the code and try again.")
                    except Exception as e:
                        st.error(f"Error joining community: {e}")
                else:
                    st.error("Supabase not available. Please try again later.")
        
        st.markdown('<span class="back-link" onclick="history.back()">← Back</span>', unsafe_allow_html=True)
        if st.button("← Back", key="back_join"):
            st.session_state.login_step = 'initial'
            st.rerun()
    
    # Step 3: Create new community
    elif st.session_state.login_step == 'create':
        st.markdown('<div class="login-logo">🚀</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Create a Community</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Start a new poker group and invite your friends</div>', unsafe_allow_html=True)
        
        community_name = st.text_input("Community Name", placeholder="e.g., Friday Night Poker").strip()
        your_name = st.text_input("Your Name (as owner)", placeholder="Your nickname").strip()
        
        if st.button("Create Community", type="primary", use_container_width=True):
            if not community_name:
                st.error("Please enter a community name")
            elif not your_name:
                st.error("Please enter your name")
            else:
                # Generate a simple code
                import random
                import string
                code = ''.join(random.choices(string.ascii_uppercase, k=6))
                
                sb = get_supabase_client()
                if sb:
                    try:
                        # Create community
                        result = sb.table('communities').insert({
                            'name': community_name,
                            'code': code,
                            'owner_name': your_name
                        }).execute()
                        
                        if result.data:
                            community = result.data[0]
                            # Add owner as member
                            sb.table('community_members').insert({
                                'community_id': community['id'],
                                'user_name': your_name,
                                'role': 'owner'
                            }).execute()
                            
                            # Success - show code prominently
                            st.session_state.community_logged_in = True
                            st.session_state.community_code = code
                            st.session_state.community_name = community_name
                            st.session_state.user_name = your_name
                            st.session_state.show_login = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error creating community: {e}")
                else:
                    st.error("Supabase not available. Please try again later.")
        
        if st.button("← Back", key="back_create"):
            st.session_state.login_step = 'initial'
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close container
    
    return False

# Database setup
DB_PATH = Path("pokerguys.db")

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Players per session
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            buy_in_chips REAL DEFAULT 0,
            final_chips REAL DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ============== STYLING (Binance-inspired Dark Mode) ==============
DARK_CSS = """
<style>
    /* Binance-inspired dark theme */
    .stApp {
        background-color: #0b0e11;
        color: #eaecef;
    }
    
    /* Cards */
    .stCard {
        background-color: #1e2329;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #2a2e39;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1e2329;
        border: 1px solid #2a2e39;
        color: #eaecef;
    }
    
    /* Tables */
    .dataframe {
        background-color: #1e2329 !important;
        color: #eaecef !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f0b90b !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #f0b90b;
        color: #000;
        border: none;
        border-radius: 4px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1e2329;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #0b8a4e;
        color: white;
    }
    .stError {
        background-color: #f6465d;
        color: white;
    }
    
    /* Profit/Loss colors */
    .profit { color: #0b8a4e; }
    .loss { color: #f6465d; }
</style>
"""

LIGHT_CSS = """
<style>
    /* Light mode */
    .stApp {
        background-color: #ffffff;
        color: #1e2329;
    }
    
    .stCard {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #e0e0e0;
    }
    
    h1, h2, h3 {
        color: #f0b90b !important;
    }
</style>
"""

def apply_theme():
    """Apply Binance-inspired theme"""
    theme = st.session_state.get('theme', 'dark')
    if theme == 'dark':
        st.markdown(DARK_CSS, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# ============== SESSION STATE ==============
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'players' not in st.session_state:
    st.session_state.players = []  # Each: {name, hands, buy_in, stack}
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# ============== DATABASE FUNCTIONS ==============
def save_session(date, location, players_data):
    """Save a session to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Insert session
    c.execute("INSERT INTO sessions (date, location) VALUES (?, ?)",
              (date, location))
    session_id = c.lastrowid
    
    # Insert players
    for p in players_data:
        final_chips = p.get('stack', p.get('final', 0))
        c.execute("""
            INSERT INTO session_players (session_id, player_name, buy_in_chips, final_chips)
            VALUES (?, ?, ?, ?)
        """, (session_id, p['name'], p['buy_in'], final_chips))
    
    conn.commit()
    conn.close()
    return session_id

def load_sessions():
    """Load all sessions"""
    conn = sqlite3.connect(DB_PATH)
    sessions = pd.read_sql("SELECT * FROM sessions ORDER BY date DESC", conn)
    conn.close()
    return sessions

def load_session_players(session_id):
    """Load players for a specific session"""
    conn = sqlite3.connect(DB_PATH)
    players = pd.read_sql(f"SELECT * FROM session_players WHERE session_id = {session_id}", conn)
    conn.close()
    return players

def delete_session(session_id):
    """Delete a session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM session_players WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

# ============== CALCULATIONS ==============
def calculate_pnl(players_data):
    """
    Calculate P&L for each player
    Returns: (results_df, is_balanced, discrepancy)
    """
    results = []
    
    for p in players_data:
        buy_in = float(p.get('buy_in', 0))
        # Use 'stack' (new) or 'final' (legacy)
        final = float(p.get('stack', p.get('final', 0)))
        pnl = final - buy_in
        results.append({
            'Player': p['name'],
            'Buy-in': buy_in,
            'Final': final,
            'P&L': pnl
        })
    
    df = pd.DataFrame(results)
    
    if len(df) > 0:
        total_pnl = df['P&L'].sum()
        # Table should be balanced (net zero)
        is_balanced = abs(total_pnl) < 0.01  # Allow tiny floating point errors
        discrepancy = total_pnl
    else:
        is_balanced = True
        discrepancy = 0
    
    return df, is_balanced, discrepancy

def calculate_streaks(all_players, sessions):
    """Calculate longest winning streak and highest loss for each player"""
    # Get all sessions with dates
    sessions_sorted = sessions.sort_values('date')
    
    player_streaks = {}
    player_highest_loss = {}
    
    for player_name in all_players['player_name'].unique():
        player_sessions = all_players[all_players['player_name'] == player_name].copy()
        player_sessions = player_sessions.merge(sessions_sorted[['id', 'date']], left_on='session_id', right_on='id')
        player_sessions = player_sessions.sort_values('date')
        
        # Calculate winning streak
        wins = 0
        max_wins = 0
        win_streak_player = player_name
        win_count = 0
        
        for _, row in player_sessions.iterrows():
            if row['P&L'] > 0:
                wins += 1
                win_count += 1
                if wins > max_wins:
                    max_wins = wins
                    win_streak_player = player_name
            else:
                wins = 0
        
        player_streaks[player_name] = {'player': win_streak_player, 'count': max_wins}
        
        # Highest loss in a single session
        losses = player_sessions[player_sessions['P&L'] < 0]
        if not losses.empty:
            min_pnl = losses['P&L'].min()
            player_highest_loss[player_name] = min_pnl
        else:
            player_highest_loss[player_name] = 0
    
    return player_streaks, player_highest_loss

# ============== UI COMPONENTS ==============
def render_theme_toggle():
    """Render theme toggle button"""
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🌙" if st.session_state.theme == 'light' else "☀️"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()

def add_player():
    """Callback to add player"""
    name = st.session_state.get('input_name', '').strip()
    buy_in = float(st.session_state.get('input_buy_in', 1000))
    final = float(st.session_state.get('input_final', 0))
    
    if name:
        st.session_state.players.append({
            'name': name,
            'buy_in': buy_in,
            'final': final
        })
        st.session_state.input_name = ''  # Clear input
        st.session_state.input_buy_in = 1000
        st.session_state.input_final = 0

def render_player_input():
    """Render player input - table style like reference"""
    # Top section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        global_buy_in = st.number_input("Buy-in", min_value=0.0, value=1000.0, step=100.0, key="global_buy_in")
    
    with col2:
        new_name = st.text_input("Player", placeholder="Nickname...", key="new_player_name", label_visibility="collapsed")
        if st.button("➕ Add", type="primary", use_container_width=True):
            if new_name and new_name.strip():
                st.session_state.players.append({
                    'name': new_name.strip(),
                    'hands': 1,
                    'stack': float(global_buy_in),
                    'buy_in': float(global_buy_in)
                })
                st.rerun()
    
    st.divider()
    
    # Header row
    c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 1])
    with c1: st.markdown("**Name**")
    with c2: st.markdown("**Buy-in**")
    with c3: st.markdown("**Stack**")
    with c4: st.markdown("**P&L**")
    with c5: st.markdown("")
    
    if not st.session_state.players:
        st.info("No players yet.")
    else:
        total_up = 0
        total_down = 0
        
        for i, p in enumerate(st.session_state.players):
            pnl = p['stack'] - p['buy_in']
            pnl_color = "#f6465d" if pnl >= 0 else "#0b8a4e"
            pnl_prefix = "+" if pnl >= 0 else ""
            
            if pnl >= 0:
                total_up += pnl
            else:
                total_down += pnl
            
            # Player row - compact
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 1])
            
            with c1:
                p['name'] = st.text_input("", value=p['name'], key=f"name_{i}", label_visibility="collapsed")
            
            with c2:
                # Hands with +/-
                h1, h2, h3 = st.columns([1, 1, 1])
                with h1:
                    if st.button("−", key=f"dec_{i}", use_container_width=True):
                        if p['hands'] > 1:
                            p['hands'] -= 1
                            p['buy_in'] = p['hands'] * global_buy_in
                            st.rerun()
                with h2:
                    st.markdown(f"<div style='text-align:center;padding:8px 0;font-weight:bold;'>{p['hands']}</div>", unsafe_allow_html=True)
                with h3:
                    if st.button("+", key=f"inc_{i}", use_container_width=True):
                        p['hands'] += 1
                        p['buy_in'] = p['hands'] * global_buy_in
                        st.rerun()
            
            with c3:
                p['stack'] = st.number_input("", min_value=0.0, value=float(p['stack']), step=100.0, key=f"stack_{i}", label_visibility="collapsed")
            
            with c4:
                st.markdown(f"<div style='text-align:right;padding:8px 0;font-weight:bold;color:{pnl_color};'>{pnl_prefix}{int(pnl):,}</div>", unsafe_allow_html=True)
            
            with c5:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.players.pop(i)
                    st.rerun()
            
            st.markdown("<hr style='margin:2px 0;opacity:0.2;'>", unsafe_allow_html=True)
        
        # Totals
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Up", f"{total_up:,.0f}")
        with c2: st.metric("Total Down", f"{total_down:,.0f}")
        with c3:
            balance = total_up + total_down
            if abs(balance) < 1:
                st.success("✅ Balanced")
            else:
                st.error(f"❌ {balance:,.0f}")

def render_current_players():
    """Render current players list - DEPRECATED, using card layout now"""
    pass

def render_session_form():
    """Main session recording form"""
    st.header("🃏 New Session")
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Session Date", datetime.now())
    with col2:
        location = st.text_input("Location", placeholder="e.g., Home Game, Poker Club...")
    
    # Player input
    render_player_input()
    
    # Save button
    st.divider()
    
    if st.session_state.players:
        # Confirmation checkbox
        confirm = st.checkbox("I confirm to save session (this will clear current inputs)", key="confirm_save")
        
        if st.button("💾 Save Session", type="primary", use_container_width=True, disabled=not confirm):
            if not confirm:
                st.warning("请先勾选确认框")
                return
            
            # Validate
            df, is_balanced, discrepancy = calculate_pnl(st.session_state.players)
            
            if not is_balanced:
                st.error(f"Cannot save: Table imbalance of {discrepancy:+.2f} chips!")
                return
            
            # Save
            try:
                session_id = save_session(
                    date.strftime("%Y-%m-%d"),
                    location,
                    st.session_state.players
                )
                st.success(f"✅ Session saved! (ID: {session_id})")
                # Reset
                st.session_state.players = []
                st.rerun()
            except Exception as e:
                st.error(f"Error saving: {e}")
    else:
        st.info("Add players to save a session")

def render_history():
    """Render session history"""
    st.header("📜 Session History")
    
    sessions = load_sessions()
    
    if sessions.empty:
        st.info("No sessions recorded yet.")
        return
    
    # Display sessions
    for _, row in sessions.iterrows():
        with st.expander(f"📅 {row['date']} - {row['location'] or 'No location'}"):
            players = load_session_players(row['id'])
            
            # Calculate totals
            players['P&L'] = players['final_chips'] - players['buy_in_chips']
            
            # Display
            st.dataframe(
                players[['player_name', 'buy_in_chips', 'final_chips', 'P&L']].rename(
                    columns={'player_name': 'Player', 'buy_in_chips': 'Buy-in', 'final_chips': 'Final', 'P&L': 'P&L'}
                ),
                hide_index=True,
                use_container_width=True
            )
            
            # Actions
            col1, col2 = st.columns(2)
            with col1:
                total_in = players['buy_in_chips'].sum()
                total_out = players['final_chips'].sum()
                st.metric("Total Buy-in", f"{total_in:,.0f}")
            with col2:
                st.metric("Total Final", f"{total_out:,.0f}")
            
            if st.button(f"🗑️ Delete Session", key=f"del_{row['id']}"):
                delete_session(row['id'])
                st.rerun()

def render_stats():
    """Render statistics dashboard"""
    st.header("📊 Statistics")
    
    sessions = load_sessions()
    
    if sessions.empty:
        st.info("No data for statistics.")
        return
    
    # Load all players
    conn = sqlite3.connect(DB_PATH)
    all_players = pd.read_sql("SELECT * FROM session_players", conn)
    conn.close()
    
    if all_players.empty:
        st.info("No player data.")
        return
    
    # Calculate P&L
    all_players['P&L'] = all_players['final_chips'] - all_players['buy_in_chips']
    
    # Calculate streaks and highest loss
    player_streaks, player_highest_loss = calculate_streaks(all_players, sessions)
    
    # Find longest winning streak overall
    best_streak = max(player_streaks.values(), key=lambda x: x['count']) if player_streaks else {'player': 'N/A', 'count': 0}
    worst_loss = min(player_highest_loss.items(), key=lambda x: x[1]) if player_highest_loss else ('N/A', 0)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", len(sessions))
    with col2:
        total_buyins = all_players['buy_in_chips'].sum()
        st.metric("Total Buy-ins", f"{total_buyins:,.0f}")
    with col3:
        total_final = all_players['final_chips'].sum()
        st.metric("Total Final", f"{total_final:,.0f}")
    with col4:
        total_pnl = all_players['P&L'].sum()
        st.metric("Net P&L", f"{total_pnl:+,.0f}", delta_color="normal")
    
    # New: Longest Win Streak & Highest Loss
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏆 Longest Win Streak", f"{best_streak['count']} sessions", best_streak['player'])
    with col2:
        st.metric("📉 Highest Loss (Single Session)", f"{worst_loss[1]:+,.0f}", worst_loss[0])
    
    # New: Highest Average P&L per Session
    player_avg_pnl = all_players.groupby('player_name')['P&L'].mean()
    if not player_avg_pnl.empty:
        best_avg_player = player_avg_pnl.idxmax()
        best_avg_pnl = player_avg_pnl.max()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Highest Avg P&L/Session", f"{best_avg_pnl:+,.0f}", best_avg_player)
    
    # Player performance
    st.subheader("🏆 Player Performance")
    
    # Filter by minimum sessions
    min_sessions = st.slider("Minimum Sessions", min_value=1, max_value=20, value=5, key="min_sessions_filter")
    
    player_stats = all_players.groupby('player_name').agg({
        'buy_in_chips': 'sum',
        'final_chips': 'sum',
        'P&L': ['sum', 'mean', 'count']
    }).round(2)
    
    player_stats.columns = ['Total Buy-in', 'Total Final', 'Total P&L', 'Avg P&L', 'Sessions']
    player_stats = player_stats.sort_values('Total P&L', ascending=False)
    
    # Filter by minimum sessions
    player_stats_filtered = player_stats[player_stats['Sessions'] >= min_sessions]
    
    st.dataframe(
        player_stats_filtered,
        use_container_width=True
    )
    
    # Chart - P&L by player with filter
    st.subheader("📈 P&L Over Time")
    
    # Get unique player names (from filtered stats)
    player_names = sorted(player_stats_filtered.index.tolist())
    
    # Player filter dropdown
    selected_player = st.selectbox(
        "Filter by Player",
        options=["All Players"] + player_names,
        index=0,
        key="player_chart_filter"
    )
    
    # Filter data based on selection
    if selected_player != "All Players":
        filtered_players = all_players[all_players['player_name'] == selected_player].copy()
    else:
        filtered_players = all_players.copy()
    
    # Merge with session dates
    filtered_players = filtered_players.merge(
        sessions[['id', 'date']], 
        left_on='session_id', 
        right_on='id'
    )
    filtered_players = filtered_players.sort_values('date')
    
    # Calculate cumulative P&L
    if selected_player == "All Players":
        # Group by date and sum P&L for all players
        daily_pnl = filtered_players.groupby('date')['P&L'].sum().reset_index()
        daily_pnl['Cumulative P&L'] = daily_pnl['P&L'].cumsum()
    else:
        # For single player, calculate cumulative
        filtered_players['Cumulative P&L'] = filtered_players['P&L'].cumsum()
        daily_pnl = filtered_players[['date', 'P&L', 'Cumulative P&L']].copy()
    
    # Display chart
    if len(daily_pnl) > 0:
        fig = px.line(
            daily_pnl,
            x='date',
            y='Cumulative P&L',
            title=f"Cumulative P&L Over Time" + (f" - {selected_player}" if selected_player != "All Players" else ""),
            markers=True
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#eaecef',
            xaxis_title="Date",
            yaxis_title="Cumulative P&L"
        )
        fig.update_traces(line_color='#f0b90b', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data to display.")
    
    # Bar chart comparison (use filtered stats)
    if len(player_stats_filtered) > 0:
        fig = px.bar(
            player_stats_filtered.reset_index(),
            x='player_name',
            y='Total P&L',
            title="Player P&L Comparison" + (f" (≥{min_sessions} sessions)" if min_sessions > 1 else ""),
            color='Total P&L',
            color_continuous_scale=['#f6465d', '#f0b90b', '#0b8a4e']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#eaecef'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============== MAIN ==============
def main():
    """Main app"""
    # Initialize community/login system
    init_community_state()
    
    # Show welcome modal if not logged in
    if not st.session_state.get('community_logged_in', False):
        render_welcome_modal()
        return
    
    # User is logged in - show community info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**🏠 {st.session_state.community_name}**")
    st.sidebar.markdown(f"Code: `{st.session_state.community_code}`")
    st.sidebar.markdown(f"👤 {st.session_state.user_name}")
    if st.sidebar.button("Switch Community"):
        st.session_state.community_logged_in = False
        st.session_state.login_step = 'initial'
        st.rerun()
    
    apply_theme()
    
    # Larger header at top
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 3em; margin: 0;">🃏 PokerGuys</h1>
            <p style="color: #888; margin: 5px 0;">Texas Hold'em Session Tracker</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Phone preview toggle
    col1, col2 = st.columns([6, 1])
    with col2:
        phone_mode = st.checkbox("📱 Phone View", value=False, key="phone_mode")
    
    # Phone container
    if phone_mode:
        st.markdown("""
            <div style="
                max-width: 375px; 
                margin: 0 auto; 
                border: 2px solid #333; 
                border-radius: 20px; 
                padding: 10px;
                background: #0b0e11;
            ">
        """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["New Session", "History", "Statistics"])
    
    if page == "New Session":
        render_session_form()
    elif page == "History":
        render_history()
    elif page == "Statistics":
        render_stats()
    
    # Close phone container
    if phone_mode:
        st.markdown("</div>", unsafe_allow_html=True)
    elif page == "Statistics":
        render_stats()

if __name__ == "__main__":
    main()
