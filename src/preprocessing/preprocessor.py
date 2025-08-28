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


# Usage
if __name__ == "__main__":
    input_file = "data/raw/character_data.csv"
    output_file = "data/processed/character_data_cleaned.csv"

    cleaned_df = clean_character_data(input_file, output_file)
