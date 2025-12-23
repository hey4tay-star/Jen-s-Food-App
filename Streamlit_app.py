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

st.title("📖 Our Family Cookbook")

# --- 2. THE CONNECTION (Data) ---
# We pull the URL from your Secret settings for security
url = st.secrets["gsheets_url"]
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

# --- 3. THE SIDEBAR (Filters) ---
st.sidebar.header("Filter by Category")

# This logic handles your multiple categories (comma separated)
# It creates one clean list of all unique tags you've used
all_tags = []
for index, row in df.iterrows():
    if pd.notna(row['Category']):
        tags = [tag.strip() for tag in str(row['Category']).split(',')]
        all_tags.extend(tags)
unique_tags = sorted(list(set(all_tags)))

selected_categories = st.sidebar.multiselect("Pick categories:", unique_tags)

# --- 4. THE SEARCH BAR ---
search_query = st.text_input("Or search for a specific dish:", placeholder="e.g., Chicken")

# --- 5. THE FILTERING LOGIC ---
filtered_df = df.copy()

if selected_categories:
    # This checks if the dish has ANY of the selected tags
    filtered_df = filtered_df[filtered_df['Category'].apply(
        lambda x: any(cat in str(x) for cat in selected_categories) if pd.notna(x) else False
    )]

if search_query:
    filtered_df = filtered_df[filtered_df['Dish'].str.contains(search_query, case=False, na=False)]

# --- 6. DISPLAYING THE DISHES (The Gallery) ---
if filtered_df.empty:
    st.write("No recipes found. Try a different search!")
else:
    cols = st.columns(3)
    for index, (i, row) in enumerate(filtered_df.iterrows()):
        with cols[index % 3]:
            # This 'if' check prevents the crash if the URL is missing
            if pd.notna(row['Image URL']) and str(row['Image URL']).startswith('http'):
                st.image(row['Image URL'], use_container_width=True)
            else:
                # This shows a placeholder if you forgot a link
                st.warning("📸 No photo added yet!")
            
            st.subheader(row['Dish'])
            st.caption(f"🏷️ {row['Category']}")
            if pd.notna(row['Notes']):
                st.write(f"*{row['Notes']}*")
            st.markdown("---")
            
          
