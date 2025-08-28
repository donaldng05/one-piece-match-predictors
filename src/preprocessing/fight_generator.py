import pandas as pd
from itertools import combinations


def create_fight_data(cleaned_character_file, output_file):
    """
    Create fight data using hybrid approach: separate columns + differences + binary comparisons.
    """
    # Read the cleaned character data
    df = pd.read_csv(cleaned_character_file)

    # Remove any rows with missing names
    df = df.dropna(subset=["name"])

    print(f"Creating fights for {len(df)} characters...")

    # Get all attribute columns (excluding 'name')
    attributes = [col for col in df.columns if col != "name"]

    fight_data = []

    # Generate all possible fight combinations
    for i, (idx1, fighter1) in enumerate(df.iterrows()):
        for idx2, fighter2 in df.iterrows():
            if idx1 >= idx2:  # Avoid duplicates and self-fights
                continue

            fight_row = {
                "fight_name": f"{fighter1['name']} vs {fighter2['name']}",
                "fighter_1_name": fighter1["name"],
                "fighter_2_name": fighter2["name"],
            }

            # Add separate columns for each fighter
            for attr in attributes:
                fight_row[f"fighter_1_{attr}"] = fighter1[attr]
                fight_row[f"fighter_2_{attr}"] = fighter2[attr]

                # Add difference features (fighter_1 - fighter_2)
                if pd.notna(fighter1[attr]) and pd.notna(fighter2[attr]):
                    fight_row[f"{attr}_diff"] = fighter1[attr] - fighter2[attr]
                    # Add binary comparison (1 if fighter_1 > fighter_2, 0 otherwise)
                    fight_row[f"{attr}_advantage"] = (
                        1 if fighter1[attr] > fighter2[attr] else 0
                    )
                else:
                    fight_row[f"{attr}_diff"] = None
                    fight_row[f"{attr}_advantage"] = None

            fight_data.append(fight_row)

    # Create DataFrame
    fight_df = pd.DataFrame(fight_data)

    # Save to CSV
    fight_df.to_csv(output_file, index=False)

    print(f"Fight data saved to {output_file}")
    print(f"Generated {len(fight_data)} fights")
    print(f"Columns created: {len(fight_df.columns)}")

    # Display first few rows as preview
    print("\nPreview of fight data:")
    print(
        fight_df[
            [
                "fight_name",
                "fighter_1_strength",
                "fighter_2_strength",
                "strength_diff",
                "strength_advantage",
            ]
        ].head()
    )

    return fight_df


# Usage
if __name__ == "__main__":
    cleaned_file = "data/processed/character_data_cleaned.csv"
    fight_file = "data/processed/fight_data.csv"

    fight_df = create_fight_data(cleaned_file, fight_file)
