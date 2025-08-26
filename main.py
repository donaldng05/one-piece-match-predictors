from src.scraping.scraper import OnePieceCharacterScraper
import asyncio
import logging

logger = logging.getLogger(__name__)

async def main():
    scraper = OnePieceCharacterScraper()
    characters = ["Monkey_D._Luffy", "Roronoa_Zoro", "Kaido"]
    
    results = []
    for char in characters:
        logger.info(f"Processing character: {char}")
        result = await scraper.process_character(char)
        if result:
            results.append(result)
            logger.info(f"Successfully processed {char}")
            print(f"\nResults for {char}:")
            print("Wiki Data:", result["wiki_data"])
            print("Power Scaling:", result["power_scaling"])
        
    scraper.save_to_csv(results)

if __name__ == "__main__":
    asyncio.run(main())