import pandas as pd


def add_fight_outcomes(fight_data_file):
    """
    Add fight outcomes to the existing fight data CSV file.

    Scoring rules:
    - Fighter with higher attribute value gets 1 point
    - If attributes are equal, both fighters get 1 point
    - Fighter with more total points wins
    - Outcomes: "victory" (fighter 1 wins), "loss" (fighter 1 loses), "draw" (tie)
    """
    # Read the fight data
    df = pd.read_csv(fight_data_file)

    print(f"Adding outcomes to {len(df)} fights...")

    # Define the attributes to compare
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

    fighter_1_points = []
    fighter_2_points = []
    outcomes = []

    for _, fight in df.iterrows():
        f1_points = 0
        f2_points = 0

        # Compare each attribute
        for attr in attributes:
            fighter_1_value = fight[f"fighter_1_{attr}"]
            fighter_2_value = fight[f"fighter_2_{attr}"]

            # Skip if either value is missing
            if pd.isna(fighter_1_value) or pd.isna(fighter_2_value):
                continue

            # Award points based on comparison
            if fighter_1_value > fighter_2_value:
                f1_points += 1
            elif fighter_2_value > fighter_1_value:
                f2_points += 1
            else:  # Equal values
                f1_points += 1
                f2_points += 1

        # Determine outcome
        if f1_points > f2_points:
            outcome = "victory"
        elif f2_points > f1_points:
            outcome = "loss"
        else:
            outcome = "draw"

        fighter_1_points.append(f1_points)
        fighter_2_points.append(f2_points)
        outcomes.append(outcome)

    # Add outcome columns to the original DataFrame
    df["fighter_1_points"] = fighter_1_points
    df["fighter_2_points"] = fighter_2_points
    df["outcome"] = outcomes

    # Overwrite the original file
    df.to_csv(fight_data_file, index=False)

    # Print statistics
    outcome_counts = pd.Series(outcomes).value_counts()
    print(f"\nOutcome distribution:")
    print(f"Victories (Fighter 1 wins): {outcome_counts.get('victory', 0)}")
    print(f"Losses (Fighter 1 loses): {outcome_counts.get('loss', 0)}")
    print(f"Draws: {outcome_counts.get('draw', 0)}")

    print(f"\nOutcomes added to {fight_data_file}")
    print(f"Total columns now: {len(df.columns)}")

    # Display preview
    print("\nPreview of fights with outcomes:")
    preview_cols = ["fight_name", "fighter_1_points", "fighter_2_points", "outcome"]
    print(df[preview_cols].head(10))

    return df


# Usage
if __name__ == "__main__":
    fight_file = "data/processed/fight_data.csv"

    df_with_outcomes = add_fight_outcomes(fight_file)
