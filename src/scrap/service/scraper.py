from playwright.sync_api import sync_playwright, TimeoutError 
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageScraper(ABC):
    @abstractmethod
    def __init__(self, website: str, search_url: str, search_url_extra: str, selector: str ) -> None:
        self.website = website
        self.search_url = search_url
        self.search_url_extra = search_url_extra
        self.selector = selector
        
    
    def parse_search(self, url: str, selector: str) -> BeautifulSoup:
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url)  
                page.wait_for_selector(selector)  

                html = BeautifulSoup(page.content(), 'html.parser')
                browser.close()
            return html
        except Exception as e:
            logger.error(f"Error parsing page {url}: {e}")

        

    
    @abstractmethod
    def extract_links(self, html: BeautifulSoup) -> List[str]:
        pass
    
    @abstractmethod
    def extract_img_source(self, html: BeautifulSoup) -> dict:
        pass 
    
    @abstractmethod
    def fetch_img_details(self, link: str):
        pass


    def fetch_all_images(self, links: list):
        max_threads = int(os.getenv('MAX_THREAD', 4))  
        all_images = []

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_link = {executor.submit(self.fetch_img_details, link): link for link in links}
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    result = future.result()
                    if result:
                        all_images.append(result)
                except Exception as e:
                    logger.error(f"Error processing {link}: {e}")
        
        return all_images
        
       
           


