import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

headers = {"User-Agent": "Mozilla/5.0"}
all_jobs = []

def get_job_links(page_number):
    url = f"https://www.rekrute.com/offres.html?s=1&p={page_number}&o=1"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    links = []

    for a in soup.select("a[href*='offre-emploi']"):
        href = a["href"]
        if "offre-emploi" in href:
            full_url = "https://www.rekrute.com" + href.split("#")[0]
            if full_url not in links:
                links.append(full_url)

    return list(set(links))

def scrape_job_details(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title_tag = soup.select_one("h1")
        title = title_tag.text.strip() if title_tag else ""

        # Try to extract city from the title
        city = ""
        if " - " in title:
            parts = title.split(" - ")
            if len(parts) > 1:
                city = parts[-1].strip()

        # Contract
        contract = ""
        for tag in soup.find_all("span"):
            if "Type de contrat" in tag.text:
                next_a = tag.find_next("a")
                if next_a:
                    contract = next_a.text.strip()
                break

        # Publication
        publication = ""
        for t in soup.find_all(string=True):
            if "Publication :" in t:
                publication = t.replace("Publication :", "").strip()
                break

        # Description
        desc = soup.select_one("div.description")
        if desc:
            description = re.sub(r'\s+', ' ', desc.get_text().strip())
        else:
            description = ""

        return {
            "title": title,
            "city": city,
            "contract": contract,
            "publication": publication,
            "description": description,
            "link": url
        }

    except Exception as e:
        print(f"❌ Error at {url}: {e}")
        return None

# Loop pages
for page in range(1, 6):
    print(f"\n📄 Scraping page {page}...")
    links = get_job_links(page)
    print(f"🔗 Found {len(links)} job links")

    for link in links:
        job = scrape_job_details(link)
        if job:
            all_jobs.append(job)
        time.sleep(0.3)

# Save to CSV (clean encoding)
df = pd.DataFrame(all_jobs)
df.to_csv("rekrute_deep_jobs.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ Done. {len(df)} jobs saved to rekrute_deep_jobs.csv")
