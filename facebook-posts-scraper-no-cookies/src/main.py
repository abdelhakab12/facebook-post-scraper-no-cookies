thonimport argparse
import json
import os
import sys
from typing import Any, Dict, List

# Ensure relative imports work when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from extractors.facebook_parser import FacebookPostScraper  # type: ignore
from utils.logger import setup_logging, get_logger  # type: ignore

def load_settings(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        # Fallback defaults if config is missing
        return {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "request_timeout": 15,
            "max_retries": 3,
            "sleep_between_requests": 1.0,
            "input_file": os.path.join("data", "sample_input.txt"),
            "output_file": os.path.join("data", "output_sample.json"),
            "max_posts_per_page": 50,
            "log_level": "INFO",
        }

    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    return settings

def read_input_urls(path: str) -> List[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    urls: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            urls.append(line)

    if not urls:
        raise ValueError("No valid URLs found in the input file.")

    return urls

def write_output(path: str, data: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape public Facebook posts without cookies."
    )
    parser.add_argument(
        "--config",
        default=os.path.join("src", "config", "settings.json"),
        help="Path to JSON settings file.",
    )
    parser.add_argument(
        "--input-file",
        help="Optional override for input file with Facebook page URLs.",
    )
    parser.add_argument(
        "--output-file",
        help="Optional override for output JSON file.",
    )
    parser.add_argument(
        "--max-posts-per-page",
        type=int,
        help="Optional override for maximum posts per page to scrape.",
    )

    return parser.parse_args()

def main() -> None:
    args = parse_args()
    settings = load_settings(args.config)

    # CLI overrides
    if args.input_file:
        settings["input_file"] = args.input_file
    if args.output_file:
        settings["output_file"] = args.output_file
    if args.max_posts_per_page is not None:
        settings["max_posts_per_page"] = args.max_posts_per_page

    log_level = settings.get("log_level", "INFO")
    setup_logging(log_level)
    logger = get_logger(__name__)

    input_file = settings.get("input_file")
    output_file = settings.get("output_file")
    max_posts_per_page = int(settings.get("max_posts_per_page", 50))

    logger.info("Starting Facebook post scraper (no cookies).")
    logger.debug("Using settings: %s", settings)

    try:
        urls = read_input_urls(input_file)
    except Exception as exc:
        logger.error("Failed to read input URLs: %s", exc, exc_info=True)
        sys.exit(1)

    scraper = FacebookPostScraper(
        user_agent=settings.get("user_agent"),
        request_timeout=int(settings.get("request_timeout", 15)),
        max_retries=int(settings.get("max_retries", 3)),
        sleep_between_requests=float(settings.get("sleep_between_requests", 1.0)),
    )

    all_posts: List[Dict[str, Any]] = []
    for url in urls:
        logger.info("Scraping page: %s", url)
        try:
            posts = scraper.scrape_page(url, max_posts=max_posts_per_page)
            logger.info("Scraped %d posts from %s", len(posts), url)
            all_posts.extend(posts)
        except Exception as exc:
            logger.error(
                "Error while scraping %s: %s", url, exc, exc_info=True
            )

    if not all_posts:
        logger.warning("No posts were scraped from any of the provided URLs.")

    try:
        write_output(output_file, all_posts)
        logger.info("Scraping complete. Output written to %s", output_file)
    except Exception as exc:
        logger.error("Failed to write output file: %s", exc, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()