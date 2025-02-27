import asyncio
from typing import List
from crawl4ai import *
from langchain_google_community import GoogleSearchAPIWrapper  # Nueva librería recomendada
import os
from dotenv import load_dotenv
#langchain_google_community

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://aws.amazon.com/es/bedrock/pricing",
        )
        print(result.markdown)

class Crawler():
    async def crawl_sequential(self, urls: List[str]):
        print("\n=== Sequential Crawling with Session Reuse ===")

        browser_config = BrowserConfig(
            headless=True,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
        )

        crawl_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator()
        )

        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.start()

        markdown_results = []  # Lista para almacenar los resultados

        try:
            session_id = "session1"  # Reuse the same session across all URLs
            for url in urls:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id=session_id
                )
                if result.success:
                    print(f"Successfully crawled: {url}")
                    markdown_results.append(result.markdown_v2.raw_markdown)
                else:
                    print(f"Failed: {url} - Error: {result.error_message}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await crawler.close()

        return "\n\n".join(markdown_results)  # Retorna los resultados combinados

class InternetSearch():
    google_api_key = 0 ############
    google_cse_id = 0 #####0

    def __init__(self, num_results=3):
        self.num_results = num_results
        #self.search = GoogleSearchAPIWrapper(google_api_key=self.google_api_key, google_cse_id=self.google_cse_id)

    def searchUrls(self, query: str):
        try:
            search_results = self.search.results(query, num_results=self.num_results)
            urls = [result["link"] for result in search_results]
            print("Resultados de búsqueda en Google:", urls)
            return urls
        except Exception as e:
            print("Error en la búsqueda en Google:", e)
            return []

    async def getWebMarkDown(self, query: str):
        crw = Crawler()
        # urls = self.searchUrls(query)  # Obtener lista de URLs
        # if not urls:
        #     return "No se encontraron resultados."

        text = await crw.crawl_sequential(query)  # Llamar correctamente la función asíncrona
        return text

async def main_async():
    search = InternetSearch()
    txt = await search.getWebMarkDown("https://aws.amazon.com/es/bedrock/pricing")  # Ejecutar la búsqueda y el crawling

    # Guardar el resultado en un archivo txt
    with open("output.txt", "w", encoding="utf-8") as file:
        file.write(txt)

    print("El resultado se ha guardado en 'output.txt'.")
    await main()

if __name__ == "__main__":
    asyncio.run(main_async())
