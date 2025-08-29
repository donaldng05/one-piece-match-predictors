import streamlit as st
import requests
import time
import pandas as pd
from PIL import Image
import io
import os

# Page configuration
st.set_page_config(page_title="One Piece Match Predictor", page_icon="⚔️", layout="wide")

# Custom CSS for styling
st.markdown(
    """
<style>
    .fighter-selection {
        border: 3px solid #8B4513;
        border-radius: 10px;
        padding: 20px;
        background-color: #F4E4BC;
        margin: 10px 0;
    }
    
    .selected-fighter {
        background-color: #FFE5D9;
        border: 3px solid #FF6B35;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .vs-text {
        font-size: 3rem;
        font-weight: bold;
        color: #8B4513;
        text-align: center;
        margin: 20px 0;
    }
    
    .loading-text {
        font-size: 1.5rem;
        text-align: center;
        color: #FF6B35;
    }
    
    .character-button {
        font-size: 0.8rem;
        padding: 5px;
        margin: 2px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Load character data
@st.cache_data
def load_character_data():
    """Load character data from CSV"""
    try:
        # Try to load from the data/processed directory
        df = pd.read_csv("data/processed/character_data_cleaned.csv")
        return df
    except FileNotFoundError:
        st.error(
            "❌ Could not find character_data_cleaned.csv. Please ensure the file exists in data/processed/"
        )
        return None


# Load the data
character_data = load_character_data()

# Import the exact character names from your extract_names.py
ALL_CHARACTER_NAMES = [
    # Top 10 (1-10)
    "Monkey_D_Luffy",
    "Roronoa_Zoro",
    "Nami",
    "Sanji",
    "Trafalgar_Law",
    "Nico_Robin",
    "Boa_Hancock",
    "Carrot",
    "Portgas_D_Ace",
    "Sabo",
    # Top 11-20
    "Yamato",
    "Shanks",
    "Donquixote_Rosinante",
    "Charlotte_Katakuri",
    "Usopp",
    "Tony_Tony_Chopper",
    "Crocodile",
    "Jinbe",
    "Marco",
    "Donquixote_Doflamingo",
    # 21-40 (first column)
    "Nefetari_Vivi",
    "Bentham",
    "Eustass_Kid",
    "Kozuki_Oden",
    "Perona",
    "Brook",
    "Smoker",
    "Franky",
    "Gol_D_Roger",
    "Dracule_Mihawk",
    "Edward_Newgate",
    "Going_Merry",
    "Silvers_Rayleigh",
    "Buggy",
    "Enel",
    "Kuzan",
    "Woop_Slap",
    "Tashigi",
    "Vinsmoke_Reiju",
    "Bartolomeo",
    # 41-60 (second column)
    "X_Drake",
    "Koby",
    "Rob_Lucci",
    "Monkey_D_Garp",
    "Charlotte_Pudding",
    "Marshall_D_Teach",
    "Kikuhime",
    "Izo",
    "Kozuki_Hiyori",
    "Shirahoshi",
    "Pell",
    "Issho",
    "Sakazuki",
    "Otama",
    "Killer",
    "Ulti",
    "Benn_Beckman",
    "Koala",
    "Borsalino",
    "Gaimon",
    # 61-80 (third column)
    "Pedro",
    "Monkey_D_Dragon",
    "Thousand_Sunny",
    "Bepo",
    "Kaidou",
    "Rockstar",
    "Dr_Hiriluk",
    "Rebecca",
    "Paulie",
    "Urouge",
    "Namule",
    "Senor_Pink",
    "Cavendish",
    "Gecko_Moria",
    "Karoo",
    "Monet",
    "Kaku",
    "Orlumbus",
    "Emporio_Ivankov",
    "Morgans",
    # 81-100 (fourth column)
    "Bellemere",
    "Basil_Hawkins",
    "Denjiro",
    "Gin",
    "Jewelry_Bonney",
    "Charlotte_Linlin",
    "Marguerite",
    "Wyper",
    "Kung_Fu_Dugong",
    "Charlotte_Mont_Dor",
    "Caesar_Clown",
    "Kin_emon",
    "Zeff",
    "Vista",
    "Charlotte_Perospero",
    "Kawamatsu",
    "Pandaman",
    "Bartholomew_Kuma",
    "Charlotte_Cracker",
    "Shushu",
]


def format_character_name(name):
    """Convert underscore format to display format"""
    return name.replace("_", " ").replace("D ", "D. ")


def get_character_stats(character_name):
    """Get character stats from the loaded data"""
    if character_data is None:
        return None

    # Try multiple name formats to find the character
    search_variations = [
        character_name,  # "Monkey_D_Luffy"
        character_name.replace("_", " "),  # "Monkey D Luffy"
        character_name.replace("_", "."),  # "Monkey.D.Luffy"
        character_name.replace("_D_", " D. "),  # "Monkey D. Luffy"
    ]

    character_row = None
    for name_variant in search_variations:
        character_row = character_data[character_data["name"] == name_variant]
        if not character_row.empty:
            break

    if character_row is None or character_row.empty:
        # Show what names are actually available for debugging
        st.error(f"❌ Character '{character_name}' not found in database")

        # Show first few character names from CSV for debugging
        if not character_data.empty:
            st.write("**Available characters in database (first 10):**")
            st.write(character_data["name"].head(10).tolist())

        return None

    # Extract the stats that match the API format
    try:
        stats = {
            "reaction_speed": float(character_row["reaction_speed"].iloc[0]),
            "stamina": float(character_row["stamina"].iloc[0]),
            "strength": float(character_row["strength"].iloc[0]),
            "offense": float(character_row["offense"].iloc[0]),
            "defense": float(character_row["defense"].iloc[0]),
            "combat_skills": float(character_row["combat_skills"].iloc[0]),
            "battle_iq": float(character_row["battle_iq"].iloc[0]),
            "armament_haki": float(character_row["armament_haki"].iloc[0]),
            "observation_haki": float(character_row["observation_haki"].iloc[0]),
            "conqueror_haki": float(character_row["conqueror_haki"].iloc[0]),
            "experience": float(character_row["experience"].iloc[0]),
        }
        return stats
    except KeyError as e:
        st.error(f"❌ Missing column in CSV: {e}")
        st.write("**Available columns:**")
        st.write(character_data.columns.tolist())
        return None


# Initialize session state
if "fighter1" not in st.session_state:
    st.session_state.fighter1 = None
if "fighter2" not in st.session_state:
    st.session_state.fighter2 = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "prediction_results" not in st.session_state:
    st.session_state.prediction_results = None
if "selection_step" not in st.session_state:
    st.session_state.selection_step = 1
if "show_all_characters" not in st.session_state:
    st.session_state.show_all_characters = False


def reset_selection():
    st.session_state.fighter1 = None
    st.session_state.fighter2 = None
    st.session_state.show_results = False
    st.session_state.prediction_results = None
    st.session_state.selection_step = 1


def get_prediction(fighter1_name, fighter2_name):
    """Call your prediction API endpoint"""
    try:
        # Get character stats
        fighter1_stats = get_character_stats(fighter1_name)
        fighter2_stats = get_character_stats(fighter2_name)

        # Stop if either character not found
        if not fighter1_stats or not fighter2_stats:
            st.error("❌ Cannot proceed: One or both characters not found in database")
            st.stop()  # This will stop the app execution
            return None

        # API endpoint
        api_url = "http://localhost:8000/predict"

        # Format the payload according to the API specification
        payload = {"fighter_1": fighter1_stats, "fighter_2": fighter2_stats}

        response = requests.post(api_url, json=payload, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        st.error(f"Error calling prediction API: {str(e)}")
        return None


def select_character(character_name):
    """Handle character selection"""
    if st.session_state.selection_step == 1:
        if character_name != st.session_state.fighter2:  # Can't select same character
            st.session_state.fighter1 = character_name
            st.session_state.selection_step = 2
            st.rerun()
    else:  # selection_step == 2
        if character_name != st.session_state.fighter1:  # Can't select same character
            st.session_state.fighter2 = character_name
            st.rerun()


def create_character_grid():
    """Create a comprehensive character selection grid"""

    # Display current selection step
    if st.session_state.selection_step == 1:
        st.markdown("#### 🥊 Select Fighter 1")
    else:
        st.markdown("#### 🥊 Select Fighter 2")

    # Top 10 Characters (Special layout)
    st.markdown("##### 🏆 Top 10 Most Popular")
    cols = st.columns(5)
    for i in range(10):
        col_idx = i % 5
        char_name = ALL_CHARACTER_NAMES[i]
        display_name = format_character_name(char_name)

        with cols[col_idx]:
            if st.button(
                f"{i+1}. {display_name}",
                key=f"top_{i}",
                use_container_width=True,
                help=f"Rank #{i+1}",
            ):
                select_character(char_name)

    # Toggle for showing all characters
    if st.button(
        "🔍 Show All 100 Characters"
        if not st.session_state.show_all_characters
        else "📦 Show Only Top 20"
    ):
        st.session_state.show_all_characters = not st.session_state.show_all_characters
        st.rerun()

    # Characters 11-20
    st.markdown("##### ⭐ Characters 11-20")
    cols = st.columns(5)
    for i in range(10, 20):
        col_idx = (i - 10) % 5
        char_name = ALL_CHARACTER_NAMES[i]
        display_name = format_character_name(char_name)

        with cols[col_idx]:
            if st.button(
                f"{i+1}. {display_name}",
                key=f"mid_{i}",
                use_container_width=True,
                help=f"Rank #{i+1}",
            ):
                select_character(char_name)

    # Show all characters if toggled
    if st.session_state.show_all_characters:
        # Characters 21-40
        st.markdown("##### 📋 Characters 21-40")
        cols = st.columns(5)
        for i in range(20, 40):
            col_idx = (i - 20) % 5
            char_name = ALL_CHARACTER_NAMES[i]
            display_name = format_character_name(char_name)

            with cols[col_idx]:
                if st.button(
                    f"{i+1}. {display_name}",
                    key=f"c21_40_{i}",
                    use_container_width=True,
                    help=f"Rank #{i+1}",
                ):
                    select_character(char_name)

        # Characters 41-60
        st.markdown("##### 📋 Characters 41-60")
        cols = st.columns(5)
        for i in range(40, 60):
            col_idx = (i - 40) % 5
            char_name = ALL_CHARACTER_NAMES[i]
            display_name = format_character_name(char_name)

            with cols[col_idx]:
                if st.button(
                    f"{i+1}. {display_name}",
                    key=f"c41_60_{i}",
                    use_container_width=True,
                    help=f"Rank #{i+1}",
                ):
                    select_character(char_name)

        # Characters 61-80
        st.markdown("##### 📋 Characters 61-80")
        cols = st.columns(5)
        for i in range(60, 80):
            col_idx = (i - 60) % 5
            char_name = ALL_CHARACTER_NAMES[i]
            display_name = format_character_name(char_name)

            with cols[col_idx]:
                if st.button(
                    f"{i+1}. {display_name}",
                    key=f"c61_80_{i}",
                    use_container_width=True,
                    help=f"Rank #{i+1}",
                ):
                    select_character(char_name)

        # Characters 81-100
        st.markdown("##### 📋 Characters 81-100")
        cols = st.columns(5)
        for i in range(80, 100):
            col_idx = (i - 80) % 5
            char_name = ALL_CHARACTER_NAMES[i]
            display_name = format_character_name(char_name)

            with cols[col_idx]:
                if st.button(
                    f"{i+1}. {display_name}",
                    key=f"c81_100_{i}",
                    use_container_width=True,
                    help=f"Rank #{i+1}",
                ):
                    select_character(char_name)


# Main app
st.title("⚔️ One Piece Match Predictor")
st.markdown("Select your fighters from the One Piece 7th Popularity Poll characters!")

# Check if character data is loaded
if character_data is None:
    st.error(
        "❌ Cannot load character data. Please check if 'data/processed/character_data_cleaned.csv' exists."
    )
    st.stop()

# Debug: Show what the CSV structure looks like
# if st.checkbox("🔍 Debug: Show CSV Info"):
#     st.write("**CSV Shape:**", character_data.shape)
#     st.write("**CSV Columns:**", character_data.columns.tolist())
#     st.write("**First 5 character names:**")
#     st.write(character_data['name'].head().tolist())

# Try to display the actual bounty poster image
try:
    # Look for the image in the data/processed directory
    image = Image.open("data/processed/Seventh_Popularity_Poll.png")
    st.image(
        image,
        caption="One Piece 7th Popularity Poll - Select characters below",
        use_container_width=True,
    )
except FileNotFoundError:
    try:
        # Try current directory
        image = Image.open("Seventh_Popularity_Poll.png")
        st.image(
            image,
            caption="One Piece 7th Popularity Poll - Select characters below",
            use_container_width=True,
        )
    except FileNotFoundError:
        st.warning(
            "⚠️ Place 'Seventh_Popularity_Poll.png' in the app directory to see the character poster!"
        )
        st.info("For now, use the character selection buttons below.")

# Show current selections
if st.session_state.fighter1 or st.session_state.fighter2:
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.fighter1:
            display_name1 = format_character_name(st.session_state.fighter1)
            rank1 = ALL_CHARACTER_NAMES.index(st.session_state.fighter1) + 1
            st.markdown(
                f'<div class="selected-fighter">Fighter 1: {display_name1} (#{rank1}) ✅</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="selected-fighter">Fighter 1: Not Selected</div>',
                unsafe_allow_html=True,
            )

    with col2:
        if st.session_state.fighter2:
            display_name2 = format_character_name(st.session_state.fighter2)
            rank2 = ALL_CHARACTER_NAMES.index(st.session_state.fighter2) + 1
            st.markdown(
                f'<div class="selected-fighter">Fighter 2: {display_name2} (#{rank2}) ✅</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="selected-fighter">Fighter 2: Not Selected</div>',
                unsafe_allow_html=True,
            )

# Character selection phase
if not st.session_state.show_results:
    create_character_grid()

    # Show battle button when both fighters are selected
    if st.session_state.fighter1 and st.session_state.fighter2:
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            display_name1 = format_character_name(st.session_state.fighter1)
            st.markdown(f"### ⚡ {display_name1}")

        with col2:
            st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

        with col3:
            display_name2 = format_character_name(st.session_state.fighter2)
            st.markdown(f"### ⚡ {display_name2}")

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🔥 START BATTLE! 🔥", type="primary", use_container_width=True
            ):
                st.session_state.show_results = True
                st.rerun()

            if st.button("🔄 Reset Selection", use_container_width=True):
                reset_selection()
                st.rerun()

# Loading and results phase
else:
    display_name1 = format_character_name(st.session_state.fighter1)
    display_name2 = format_character_name(st.session_state.fighter2)
    st.markdown(f"## ⚔️ {display_name1} VS {display_name2}")

    if st.session_state.prediction_results is None:
        # Loading screen
        st.markdown(
            '<div class="loading-text">🔄 Analyzing battle data...</div>',
            unsafe_allow_html=True,
        )

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simulate loading with progress updates
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 20:
                status_text.text("Loading character stats...")
            elif i < 40:
                status_text.text("Analyzing fighting abilities...")
            elif i < 60:
                status_text.text("Calculating battle scenarios...")
            elif i < 80:
                status_text.text("Processing Devil Fruit powers...")
            else:
                status_text.text("Finalizing prediction...")
            time.sleep(0.02)  # Small delay for visual effect

        # Get actual prediction
        st.session_state.prediction_results = get_prediction(
            st.session_state.fighter1, st.session_state.fighter2
        )

        progress_bar.empty()
        status_text.empty()
        st.rerun()

    else:
        # Display results
        results = st.session_state.prediction_results

        if results:
            # Winner announcement
            st.markdown("## 🏆 BATTLE RESULTS")

            prediction = results.get("prediction", "Unknown")
            confidence = results.get("confidence", 0)

            # Determine winner based on prediction
            if prediction == "victory":
                winner_name = format_character_name(st.session_state.fighter1)
            elif prediction == "loss":
                winner_name = format_character_name(st.session_state.fighter2)
            else:
                winner_name = "Draw"

            st.markdown(f"### 👑 Winner: **{winner_name}**")
            st.markdown(f"**Confidence:** {confidence:.1%}")

            # Probabilities
            col1, col2 = st.columns(2)

            probabilities = results.get("probabilities", {})
            with col1:
                st.markdown("#### 📊 Win Probabilities")
                for outcome, prob in probabilities.items():
                    if outcome == "victory":
                        label = (
                            f"{format_character_name(st.session_state.fighter1)} wins"
                        )
                    elif outcome == "loss":
                        label = (
                            f"{format_character_name(st.session_state.fighter2)} wins"
                        )
                    else:
                        label = outcome.capitalize()
                    st.metric(label, f"{prob:.1%}")

            # Fighter advantages
            with col2:
                advantages = results.get("fighter_1_advantage", {})
                if advantages:
                    st.markdown("#### ⚡ Fighter 1 Advantages")
                    positive_advantages = {k: v for k, v in advantages.items() if v > 0}
                    negative_advantages = {k: v for k, v in advantages.items() if v < 0}

                    if positive_advantages:
                        st.markdown(
                            f"**{format_character_name(st.session_state.fighter1)} is stronger in:**"
                        )
                        for stat, diff in positive_advantages.items():
                            st.markdown(f"• {stat.replace('_', ' ').title()}: +{diff}")

                    if negative_advantages:
                        st.markdown(
                            f"**{format_character_name(st.session_state.fighter2)} is stronger in:**"
                        )
                        for stat, diff in negative_advantages.items():
                            st.markdown(f"• {stat.replace('_', ' ').title()}: {diff}")

            # Summary
            summary = results.get("summary", "")
            if summary:
                st.markdown("#### 📝 Battle Analysis")
                st.markdown(summary)

        else:
            st.error("Failed to get prediction results. Please try again.")

        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 New Battle", type="primary", use_container_width=True):
                reset_selection()
                st.rerun()
