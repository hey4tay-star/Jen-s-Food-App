import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. SETTING THE MOOD (Visuals) ---
st.set_page_config(page_title="Her Recipe Gallery", layout="wide")

# This adds the "Paper & Ink" look
st.markdown("""
    <style>
    .main { background-color: #fdfaf0; } /* Creamy paper color */
    h1 { color: #2c3e50; font-family: 'Georgia', serif; }
    .stTextInput > div > div > input { background-color: #ffffff; border-radius: 10px; }
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

# --- 3. THE SIDEBAR (Filters & Surprise) ---
st.sidebar.header("Cooking Tools")

# Initialize a 'placeholder' for the surprise recipe so it doesn't disappear
if 'surprise_recipe' not in st.session_state:
    st.session_state.surprise_recipe = None

if st.sidebar.button("✨ Surprise Me!"):
    st.session_state.surprise_recipe = df.sample(n=1).iloc[0]
    st.balloons()

# If a surprise recipe has been picked, show it at the very top of the main page
if st.session_state.surprise_recipe is not None:
    recipe = st.session_state.surprise_recipe
    st.markdown("### 🌟 Your Random Suggestion")
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            if pd.notna(recipe['Image url']) and str(recipe['Image url']).startswith('http'):
                st.image(recipe['Image url'], use_container_width=True)
        with col2:
            st.subheader(recipe['Dish'])
            st.write(f"🏷️ {recipe['Category']}")
            if pd.notna(recipe['Notes']):
                st.info(recipe['Notes'])
        if st.button("Clear Surprise"):
            st.session_state.surprise_recipe = None
            st.rerun()
    st.markdown("---")

st.sidebar.write("---")
st.sidebar.header("Filter by Category")

# Generate unique tags for the filter
all_tags = []
for val in df['Category'].dropna():
    all_tags.extend([tag.strip() for tag in str(val).split(',')])
unique_tags = sorted(list(set(all_tags)))

selected_categories = st.sidebar.multiselect("Pick categories:", unique_tags)

# --- 4. THE SEARCH BAR ---
search_query = st.text_input("Or search for a specific dish:", placeholder="e.g., Chicken")

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
            
            
          
