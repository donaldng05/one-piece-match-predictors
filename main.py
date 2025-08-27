from src.scraping.scraper import OnePieceCharacterScraper
import asyncio
import logging
import pandas as pd
import os
import json

logger = logging.getLogger(__name__)


async def main():
    scraper = OnePieceCharacterScraper()

    # Load existing data to preserve it
    csv_file = "data/raw/character_data.csv"
    existing_results = []
    processed = set()

    if os.path.exists(csv_file):
        try:
            existing_df = pd.read_csv(csv_file)
            # Convert existing data back to the format expected by scraper
            for _, row in existing_df.iterrows():
                # Use json.loads instead of eval to handle null values properly
                wiki_data = json.loads(row["wiki_data"].replace("null", "null"))
                power_scaling = json.loads(row["power_scaling"].replace("null", "null"))

                existing_results.append(
                    {"wiki_data": wiki_data, "power_scaling": power_scaling}
                )

                # Extract character name to add to processed set
                processed.add(wiki_data["name"])
            print(f"Loaded {len(existing_results)} existing characters")
        except Exception as e:
            print(f"Error loading existing data: {e}")

    characters = [
        # Start from Nami since first 2 are done
        # "Nami",
        # "Sanji",
        # "Trafalgar_Law",
        # "Nico_Robin",
        # "Boa_Hancock",
        # "Carrot",
        # "Portgas_D._Ace",
        # "Sabo",
        # # Top 11-20
        # "Yamato",
        # "Shanks",
        # "Donquixote_Rosinante",
        # "Charlotte_Katakuri",
        # "Usopp",
        # "Tony_Tony_Chopper",
        # "Crocodile",
        # "Jinbe",
        # "Marco",
        # "Donquixote_Doflamingo",
        # # 21-40 (first column)
        # "Nefertari_Vivi",
        # "Bentham",
        # "Eustass_Kid",
        # "Kozuki_Oden",
        # "Perona",
        # "Brook",
        # "Smoker",
        # "Franky",
        # "Gol_D._Roger",
        # "Dracule_Mihawk",
        # "Edward_Newgate",
        # "Going_Merry",
        # "Silvers_Rayleigh",
        # "Buggy",
        # "Enel",
        # "Kuzan",
        # "Woop_Slap",
        # "Tashigi",
        # "Vinsmoke_Reiju",
        # "Bartolomeo",
        # # 41-60 (second column)
        # "X_Drake",
        # "Koby",
        # "Rob_Lucci",
        # "Monkey_D._Garp",
        # "Charlotte_Pudding",
        # "Marshall_D._Teach",
        # "Kikuhime",
        # "Izo",
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
        "Monkey_D._Dragon",
        "Thousand_Sunny",
        "Bepo",
        # "Kaido",
        "Rockstar",
        "Dr._Hiriluk",
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
        "Charlotte_Mont-d'Or",
        "Caesar_Clown",
        "Kin'emon",
        "Zeff",
        "Vista",
        "Charlotte_Perospero",
        "Kawamatsu",
        "Pandaman",
        "Bartholomew_Kuma",
        "Charlotte_Cracker",
        "Shushu",
    ]

    # Start with existing results to preserve previous data
    results = existing_results.copy()

    for char in characters:
        if char in processed:
            print(f"Skipping {char} (already processed)")
            continue

        logger.info(f"Processing character: {char}")
        result = await scraper.process_character(char)
        if result:
            results.append(result)
            print(f"Successfully processed {char}")
            scraper.save_to_csv(results)

    scraper.save_to_csv(results)


if __name__ == "__main__":
    asyncio.run(main())
