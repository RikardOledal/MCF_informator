import re
from dotenv import load_dotenv
from firecrawl import Firecrawl
from backend.constants import DATA_PATH
from pathlib import Path

load_dotenv()

TARGET_URL = "https://www.mcf.se/sv/rad-till-privatpersoner/"


def clean_mcf_markdown(text: str) -> str:
    r"""
    Removes soft hyphens (\u00ad) from the string.
    Removes '## Dela sidan med andra' and '**Kakor på webbplatsen**' along with everything after them.
    Removes unnecessary whitespace at the start and end of the string.
    """
    text = text.replace("\u00ad", "")
    for cutoff in ["## Dela sidan med andra", "**Kakor på webbplatsen**"]:
        if cutoff in text:
            text = text.split(cutoff)[0]
    return text.strip()


def safe_filename(title: str) -> str:
    r"""
    Removes <>:"/\|?* from string to make it suitable for a filename.
    Also changes whitespaces to _
    """
    cleaned = re.sub(r'[<>:"/\\|?*]', "", title).strip()
    return re.sub(r"\s+", "_", cleaned)


def scrape_mcf(
        limit: int | None = None,
        scrape_url: str = "https://www.mcf.se/sv/rad-till-privatpersoner/",
        output_folder: Path | str = DATA_PATH) -> None:
    """
    Scrapes pages using firecrawl.
    First maps all pages (using 1 firecrawl credit)
    Limits result to set limit if not all pages should be scraped.
    Cleans text and filename.
    Saves files as markdownfiles in the output-folder
    """
    app = Firecrawl()
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Map site (1 credit)
    map_result = app.map(url=scrape_url, limit=200)
    filtered_urls = sorted(
        set(
            link.url
            for link in map_result.links
            if link.url.startswith(scrape_url)
            and "#" not in link.url
            and not link.url.lower().endswith(".pdf")
        )
    )

    if limit:
        filtered_urls = filtered_urls[:limit]

    print(f"Scrapes {len(filtered_urls)} pages from MCF...")

    # 2. Batch-scrape (using 1 credit per page)
    batch_result = app.batch_scrape(
        filtered_urls,
        formats=["markdown"],
        only_main_content=True,
    )

    # 3. Clean strings and save as .md-files
    saved = 0
    for i, doc in enumerate(batch_result.data):
        if not doc.markdown:
            continue

        title = doc.metadata.title if doc.metadata and doc.metadata.title else f"page_{i}"
        url = doc.metadata.url if doc.metadata and doc.metadata.url else ""
        cleaned_md = clean_mcf_markdown(doc.markdown)

        content = f"---\ntitle: {title}\nurl: {url}\n---\n\n{cleaned_md}\n"
        filepath = output_folder / f"{safe_filename(title)}.md"
        filepath.write_text(content, encoding="utf-8")
        saved += 1

    print(f"Scraping complete! {saved} files saved in {output_folder}")


if __name__ == "__main__":
    scrape_mcf()