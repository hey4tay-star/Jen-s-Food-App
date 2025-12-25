import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SETTING THE MOOD (Visuals) ---
st.set_page_config(
    page_title="The Jen Cookbook", # Put the EXACT name you want here
    page_icon="🍳", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# This adds the "Paper & Ink" look
st.markdown("""
    <style>
    /* This makes the app feel like a recipe card */
    .stApp {
        background-color: #fdfaf0;
    }
    .stHeader {
        background-color: rgba(0,0,0,0);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 Jen's Cookbook")

# --- 2. THE CONNECTION (Data) ---
url = st.secrets["gsheets_url"]
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# This line cleans up your column names (removes spaces, fixes caps)
df.columns = df.columns.str.strip().str.capitalize()

# This shuffles the order EVERY time the app is opened
df = df.sample(frac=1).reset_index(drop=True)

# --- 3. THE SURPRISE SECTION (Main Page) ---
# This stays on the main screen, not in the sidebar
if 'surprise_recipe' not in st.session_state:
    st.session_state.surprise_recipe = None

col_btn, col_empty = st.columns([1, 2])

with col_btn:
    if st.button("✨ Surprise Me!", use_container_width=True):
        st.session_state.surprise_recipe = df.sample(n=1).iloc[0]
        st.balloons()

if st.session_state.surprise_recipe is not None:
    recipe = st.session_state.surprise_recipe
    st.markdown("""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #e6e6e6; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #2c3e50;">🌟 How about this?</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if pd.notna(recipe['Image url']) and str(recipe['Image url']).startswith('http'):
            st.image(recipe['Image url'], use_container_width=True)
    with col2:
        st.header(recipe['Dish'])
        st.write(f"🏷️ **Category:** {recipe['Category']}")
        if pd.notna(recipe['Notes']):
            st.info(f"💡 {recipe['Notes']}")
        if st.button("Close Suggestion ✕"):
            st.session_state.surprise_recipe = None
            st.rerun()
    st.markdown("---")

# --- 4. THE FILTERS (Cleanly in the Sidebar) ---
st.sidebar.header("🔍 Find a Recipe")

all_tags = []
for val in df['Category'].dropna():
    all_tags.extend([tag.strip() for tag in str(val).split(',')])
unique_tags = sorted(list(set(all_tags)))

selected_categories = st.sidebar.multiselect("Filter by Category:", unique_tags)
search_query = st.sidebar.text_input("Search by Name:", placeholder="e.g. Pasta")

# --- 5. THE FILTERING LOGIC ---
filtered_df = df.copy()

# Filter by Category (Multiselect)
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].apply(
        lambda x: any(cat in str(x) for cat in selected_categories) if pd.notna(x) else False
    )]

# Filter by Search Bar (Text input)
if search_query:
    filtered_df = filtered_df[filtered_df['Dish'].str.contains(search_query, case=False, na=False)]

# --- 6. DISPLAYING THE DISHES (The Gallery) ---
st.header("All Recipes")

if filtered_df.empty:
    st.write("No recipes found. Try a different search!")
else:
    # Set the number of columns (3 is usually best for mobile/desktop mix)
    cols = st.columns(3)
    
    for index, (i, row) in enumerate(filtered_df.iterrows()):
        with cols[index % 3]:
            # Image Container
            if pd.notna(row['Image url']) and str(row['Image url']).startswith('http'):
                st.image(row['Image url'], use_container_width=True)
            else:
                st.warning("📸 Photo coming soon!")
            
            # Text Details
            st.subheader(row['Dish'])
            st.caption(f"🏷️ {row['Category']}")
            
            if pd.notna(row['Notes']):
                # A nice italicized block for your personal notes
                st.markdown(f"*{row['Notes']}*")
            
            # Adds visual spacing between rows
            st.write("") 
            st.markdown("---")
            
            
          
