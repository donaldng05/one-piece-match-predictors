import pandas as pd
import json


def clean_character_data(input_file, output_file):
    """
    Clean the character data CSV to extract only names and mean attribute scores.
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    cleaned_data = []

    for _, row in df.iterrows():
        try:
            # Parse the wiki_data to get the name
            wiki_data = json.loads(row["wiki_data"])
            character_name = wiki_data["name"]

            # Parse the power_scaling to get mean scores
            power_scaling = json.loads(row["power_scaling"])

            # Create a new row with name and mean scores
            cleaned_row = {"name": character_name}

            # Extract mean scores for each attribute
            attributes = [
                "strength",
                "travel_speed",
                "agility",
                "reaction_speed",
                "offense",
                "defense",
                "endurance",
                "durability",
                "stamina",
                "intelligence",
                "battle_iq",
                "combat_skills",
                "weapon_proficiency",
                "armament_haki",
                "observation_haki",
                "conqueror_haki",
                "devil_fruit",
                "mentality",
                "experience",
            ]

            for attr in attributes:
                if attr in power_scaling and power_scaling[attr] is not None:
                    cleaned_row[attr] = power_scaling[attr]["mean"]
                else:
                    cleaned_row[attr] = None

            cleaned_data.append(cleaned_row)

        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    # Create DataFrame and save
    cleaned_df = pd.DataFrame(cleaned_data)
    cleaned_df.to_csv(output_file, index=False)

    print(f"Cleaned data saved to {output_file}")
    print(f"Processed {len(cleaned_data)} characters")

    # Display first few rows as preview
    print("\nPreview of cleaned data:")
    print(cleaned_df.head())

    return cleaned_df


def fix_conqueror_haki(cleaned_character_file, output_file=None):
    """
    Fix Conqueror's Haki scores based on confirmed users from One Piece wiki.
    Give 1 for confirmed users, 0 for others.
    """

    # List of confirmed Conqueror's Haki users from One Piece wiki
    conqueror_users = {
        # Supreme King Haki Users (Current/Alive)
        "Shanks",
        "Monkey D. Luffy",
        "Silvers Rayleigh",
        "Boa Hancock",
        "Donquixote Doflamingo",
        "Chinjao",
        "Charlotte Linlin",  # Big Mom
        "Charlotte Katakuri",
        "Eustass Kid",
        "Sengoku",
        "Kaidou",  # Note: might be spelled as 'Kaido' in your data
        "Roronoa Zoro",
        "Yamato",
        "Monkey D. Garp",
        "Topman Marcus",
        "Marcus Mars",
        "Scopper Gaban",
        "Imu",
        # Deceased Users
        "Edward Newgate",  # Whitebeard
        "Portgas D. Ace",
        "Kozuki Oden",
        "Gol D. Roger",
        "Joy Boy",
        "Jaygarcia Saturn",
        "Rocks D. Xebec",
        "Harald",
        # Non-Canon Users
        "Naguri",
        "Douglas Bullet",
        # Alternative name formats (in case data uses different naming)
        "Big Mom",
        "Whitebeard",
        "Gold Roger",
        "Gol D Rogers",
        "Charlotte Big Mom",
        "Kaido",
        "Kaido of the Beasts",
        "Red-Haired Shanks",
        "Dark King Rayleigh",
        "Fire Fist Ace",
        "Buddha Sengoku",
        "Eustass Captain Kid",
        "Captain Kid",
        "Pirate Hunter Zoro",
    }

    # Read the character data
    df = pd.read_csv(cleaned_character_file)

    print(f"Fixing Conqueror's Haki for {len(df)} characters...")
    print(f"Known Conqueror's Haki users: {len(conqueror_users)}")

    # Create a copy to modify
    df_fixed = df.copy()

    # Fix Conqueror's Haki values
    matched_users = []
    unmatched_conquerors = conqueror_users.copy()

    for idx, row in df_fixed.iterrows():
        character_name = row["name"]

        # Check if character is a confirmed Conqueror's Haki user
        if character_name in conqueror_users:
            df_fixed.at[idx, "conqueror_haki"] = 1.0
            matched_users.append(character_name)
            unmatched_conquerors.discard(character_name)
        else:
            df_fixed.at[idx, "conqueror_haki"] = 0.0

    # Save the fixed data
    if output_file is None:
        output_file = cleaned_character_file  # Overwrite original

    df_fixed.to_csv(output_file, index=False)

    # Report results
    print(f"\nCONQUEROR'S HAKI FIXED:")
    print(f"Characters with Conqueror's Haki: {len(matched_users)}")
    print(f"Matched users: {sorted(matched_users)}")

    if unmatched_conquerors:
        print(f"\nKnown Conqueror users not found in dataset:")
        print(f"{sorted(list(unmatched_conquerors))}")

    print(f"\nUpdated distribution:")
    print(df_fixed["conqueror_haki"].value_counts().sort_index())

    print(f"\nFixed data saved to: {output_file}")

    return df_fixed


# Usage
if __name__ == "__main__":
    input_file = "data/raw/character_data.csv"
    output_file = "data/processed/character_data_cleaned.csv"

    cleaned_df = clean_character_data(input_file, output_file)

    cleaned_file = "data/processed/character_data_cleaned.csv"

    # Fix the Conqueror's Haki values
    df_fixed = fix_conqueror_haki(cleaned_file)
