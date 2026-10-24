import argparse
from pathlib import Path
from scraper import scrape_quotes, scrape_books, scrape_hackernews, save_to_csv


def run_cli_demo(target: str = "books", use_selenium: bool = False) -> None:
    out_dir = Path(__file__).parent / "output"
    if target == "quotes":
        records = scrape_quotes(use_selenium=use_selenium)
        csv_path = out_dir / "quotes.csv"
    elif target == "hn":
        records = scrape_hackernews(use_selenium=use_selenium)
        csv_path = out_dir / "hackernews.csv"
    else:
        records = scrape_books(use_selenium=use_selenium)
        csv_path = out_dir / "books_prices.csv"

    df = save_to_csv(records, csv_path)
    print(f"[06 Web Scraper] Extracted {len(df)} rows ({target}) -> saved to {csv_path}")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 06: Web Scraper")
    parser.add_argument(
        "--target",
        choices=["books", "quotes", "hn"],
        default="books",
        help="Target site preset to scrape",
    )
    parser.add_argument(
        "--selenium", action="store_true", help="Use headless Selenium Chrome driver"
    )
    args = parser.parse_args()
    run_cli_demo(target=args.target, use_selenium=args.selenium)
