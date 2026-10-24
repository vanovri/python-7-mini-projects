from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def fetch_html(url: str, use_selenium: bool = False) -> str:
    if use_selenium:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            return driver.page_source
        finally:
            driver.quit()

    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=12)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def scrape_quotes(url: str = "https://quotes.toscrape.com/", use_selenium: bool = False) -> List[Dict[str, Any]]:
    html = fetch_html(url, use_selenium=use_selenium)
    soup = BeautifulSoup(html, "html.parser")
    rows: List[Dict[str, Any]] = []
    for block in soup.select("div.quote"):
        text_el = block.select_one("span.text")
        author_el = block.select_one("small.author")
        tags = [t.get_text(strip=True) for t in block.select("div.tags a.tag")]
        rows.append(
            {
                "quote": text_el.get_text(strip=True).strip("“”\"") if text_el else "",
                "author": author_el.get_text(strip=True) if author_el else "",
                "tags": ", ".join(tags),
            }
        )
    return rows


def scrape_books(url: str = "https://books.toscrape.com/", use_selenium: bool = False) -> List[Dict[str, Any]]:
    html = fetch_html(url, use_selenium=use_selenium)
    soup = BeautifulSoup(html, "html.parser")
    rows: List[Dict[str, Any]] = []
    for article in soup.select("article.product_pod"):
        title_el = article.select_one("h3 a")
        price_el = article.select_one("p.price_color")
        stock_el = article.select_one("p.instock.availability")
        rows.append(
            {
                "title": title_el.get("title", "").strip() if title_el else "",
                "price": price_el.get_text(strip=True) if price_el else "",
                "availability": stock_el.get_text(strip=True) if stock_el else "",
            }
        )
    return rows


def scrape_hackernews(url: str = "https://news.ycombinator.com/", use_selenium: bool = False) -> List[Dict[str, Any]]:
    html = fetch_html(url, use_selenium=use_selenium)
    soup = BeautifulSoup(html, "html.parser")
    rows: List[Dict[str, Any]] = []
    for item in soup.select("tr.athing")[:15]:
        title_link = item.select_one("span.titleline > a")
        rank_el = item.select_one("span.rank")
        if title_link:
            rows.append(
                {
                    "rank": rank_el.get_text(strip=True).rstrip(".") if rank_el else "",
                    "headline": title_link.get_text(strip=True),
                    "link": title_link.get("href", ""),
                }
            )
    return rows


def save_to_csv(records: List[Dict[str, Any]], output_csv: Path) -> pd.DataFrame:
    df = pd.DataFrame(records)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    return df
