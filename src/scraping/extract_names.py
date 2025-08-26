import cv2
import numpy as np
import requests


def extract_posters(
    img,
    start_x,
    start_y,
    poster_width,
    poster_height,
    rows,
    cols,
    character_names,
    start_num,
):
    """
    Extract posters from a grid layout and save them with consistent naming.

    Args:
        img: The source image
        start_x: Starting x coordinate
        start_y: Starting y coordinate
        poster_width: Width of each poster
        poster_height: Height of each poster
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        character_names: List of character names
        start_num: Starting number for poster numbering

    Returns:
        Number of posters extracted
    """
    poster_count = 0
    for row in range(rows):
        for col in range(cols):
            if poster_count >= len(character_names):
                break

            x = start_x + (col * poster_width)
            y = start_y + (row * poster_height)

            # Crop the poster
            crop = img[y : y + poster_height, x : x + poster_width]

            # Save with consistent naming format
            filename = f"data/processed/No_{start_num + poster_count}_{character_names[poster_count]}.png"
            cv2.imwrite(filename, crop)

            print(
                f"Extracted poster {start_num + poster_count}: {character_names[poster_count]} at ({x}, {y})"
            )
            poster_count += 1

    return poster_count


# Load image
img = cv2.imread("data/processed/Seventh_Popularity_Poll.png")
img_height, img_width = img.shape[:2]

# Character names for all 100 characters
all_character_names = [
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
    "Kozui_Hiyori",
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
    "Kaido",
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

total_extracted = 0

# Extract top 10 posters (1-10)
poster_width = 285
poster_height = 300
count = extract_posters(
    img, 0, 0, poster_width, poster_height, 2, 5, all_character_names[0:10], 1
)
total_extracted += count
print(f"Successfully extracted {count} top 10 character posters")

# Extract top 11-20 posters
poster_width_small = poster_width // 2  # 142
poster_height_small = 250
start_height_small = 625
count = extract_posters(
    img,
    0,
    start_height_small,
    poster_width_small,
    poster_height_small,
    1,
    10,
    all_character_names[10:20],
    11,
)
total_extracted += count
print(f"Successfully extracted {count} characters 11-20 posters")

# Extract remaining characters 21-100 (4 columns of 20 each)
start_height_remaining = 925
poster_height_remaining = 1056
column_width = img_width // 4
poster_height_column = poster_height_remaining // 20

for column in range(4):
    start_x = column * column_width
    start_idx = 20 + (column * 20)
    end_idx = start_idx + 20
    start_num = start_idx + 1

    count = extract_posters(
        img,
        start_x,
        start_height_remaining,
        column_width,
        poster_height_column,
        20,
        1,
        all_character_names[start_idx:end_idx],
        start_num,
    )
    total_extracted += count
    print(
        f"Successfully extracted {count} characters {start_num}-{start_num + 19} posters"
    )

print(f"Total characters extracted: {total_extracted}")
