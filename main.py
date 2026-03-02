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

# Database
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from dateutil import parser

# Config
st.set_page_config(
    page_title="PokerGuys",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            notes TEXT,
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
    st.session_state.players = []
if 'add_player_clicked' not in st.session_state:
    st.session_state.add_player_clicked = False
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None

# ============== DATABASE FUNCTIONS ==============
def save_session(date, location, notes, players_data):
    """Save a session to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Insert session
    c.execute("INSERT INTO sessions (date, location, notes) VALUES (?, ?, ?)",
              (date, location, notes))
    session_id = c.lastrowid
    
    # Insert players
    for p in players_data:
        c.execute("""
            INSERT INTO session_players (session_id, player_name, buy_in_chips, final_chips)
            VALUES (?, ?, ?, ?)
        """, (session_id, p['name'], p['buy_in'], p['final']))
    
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
        buy_in = float(p['buy_in']) if p['buy_in'] else 0
        final = float(p['final']) if p['final'] else 0
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
    """Render player input form - simplified version"""
    st.subheader("👥 Add Players")
    
    # Create a container for the input row
    container = st.container()
    
    with container:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            # Use a unique key with timestamp to force refresh
            name_input = st.text_input(
                "Player Name", 
                key=f"name_input_{len(st.session_state.players)}",
                placeholder="Enter player name..."
            )
        with col2:
            buy_in_input = st.number_input(
                "Buy-in (chips)", 
                min_value=0.0, 
                value=1000.0, 
                step=100.0,
                key=f"buyin_input_{len(st.session_state.players)}"
            )
        with col3:
            final_input = st.number_input(
                "Final Stack (chips)", 
                min_value=0.0, 
                value=0.0, 
                step=100.0,
                key=f"final_input_{len(st.session_state.players)}"
            )
        with col4:
            st.write("")  
            st.write("")
            add_clicked = st.button("➕ Add", key="add_player_btn")
    
    # Handle add button click
    if add_clicked and name_input:
        if name_input.strip():
            st.session_state.players.append({
                'name': name_input.strip(),
                'buy_in': float(buy_in_input),
                'final': float(final_input)
            })
            st.rerun()
        else:
            st.error("Please enter a player name!")
    
    # Show current count
    st.caption(f"Current players: {len(st.session_state.players)}")

def render_current_players():
    """Render current players list"""
    if not st.session_state.players:
        st.info("No players added yet. Add players above.")
        return
    
    # Display as editable table
    st.subheader("📋 Current Players")
    
    for i, p in enumerate(st.session_state.players):
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        
        with col1:
            st.text(p['name'])
        with col2:
            new_buy = st.number_input(f"Buy-in {i}", value=p['buy_in'], key=f"buy_{i}", step=100.0)
            p['buy_in'] = new_buy
        with col3:
            new_final = st.number_input(f"Final {i}", value=p['final'], key=f"final_{i}", step=100.0)
            p['final'] = new_final
        with col4:
            pnl = p['final'] - p['buy_in']
            color = "profit" if pnl >= 0 else "loss"
            st.markdown(f"<span class='{color}'>P&L: {pnl:+,.0f}</span>", unsafe_allow_html=True)
        with col5:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.players.pop(i)
                st.rerun()
    
    # Calculate and validate
    st.divider()
    df, is_balanced, discrepancy = calculate_pnl(st.session_state.players)
    
    if is_balanced:
        st.success(f"✅ Table is balanced! (Net: {discrepancy:+.2f})")
    else:
        st.error(f"❌ Table imbalance detected! Net: {discrepancy:+.2f}")
        st.warning("💡 Check for missing players, incorrect final stacks, or data entry errors.")
    
    return df, is_balanced

def render_session_form():
    """Main session recording form"""
    st.header("🃏 New Session")
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Session Date", datetime.now())
    with col2:
        location = st.text_input("Location", placeholder="e.g., Home Game, Poker Club...")
    
    notes = st.text_area("Notes (optional)", placeholder="Buy-in structure, game type, etc.")
    
    # Player input
    render_player_input()
    
    # Save button
    st.divider()
    
    if st.session_state.players:
        if st.button("💾 Save Session", type="primary", use_container_width=True):
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
                    notes,
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
                players[['player_name', 'buy_in_chips', 'final_chips', 'P&L']],
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
    
    # Player performance
    st.subheader("🏆 Player Performance")
    
    player_stats = all_players.groupby('player_name').agg({
        'buy_in_chips': 'sum',
        'final_chips': 'sum',
        'P&L': ['sum', 'mean', 'count']
    }).round(2)
    
    player_stats.columns = ['Total Buy-in', 'Total Final', 'Total P&L', 'Avg P&L', 'Sessions']
    player_stats = player_stats.sort_values('Total P&L', ascending=False)
    
    st.dataframe(
        player_stats,
        use_container_width=True
    )
    
    # Chart
    if len(player_stats) > 0:
        fig = px.bar(
            player_stats.reset_index(),
            x='player_name',
            y='Total P&L',
            title="Player P&L Comparison",
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
    apply_theme()
    render_theme_toggle()
    
    st.title("🃏 PokerGuys")
    st.caption("Texas Hold'em Session Tracker")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["New Session", "History", "Statistics"])
    
    if page == "New Session":
        render_session_form()
    elif page == "History":
        render_history()
    elif page == "Statistics":
        render_stats()

if __name__ == "__main__":
    main()
