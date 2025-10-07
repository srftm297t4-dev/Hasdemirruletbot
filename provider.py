import os, re
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from typing import List, Dict

load_dotenv()
SITE_URL = os.getenv("SITE_URL")  # hedef site
RESULT_ITEMS_SELECTOR = os.getenv("RESULT_ITEMS_SELECTOR", "[data-results] li")
RESULT_NUMBER_SELECTOR = os.getenv("RESULT_NUMBER_SELECTOR", ".num")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "50"))

RED_SET = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
def num_to_color(n: int) -> str:
    if n == 0: return "green"
    return "red" if n in RED_SET else "black"

async def fetch_last_n_results(n: int = MAX_RESULTS) -> List[Dict]:
    """Sayfadan son n sonucu (en yeni başta) çıkarır."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            await page.goto(SITE_URL, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(2000)

            items = await page.query_selector_all(RESULT_ITEMS_SELECTOR)
            out = []
            if not items:
                body = await page.text_content("body") or ""
                nums = [int(x) for x in re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', body)][:n]
                out = [{"idx": i, "number": v, "color": num_to_color(v)} for i, v in enumerate(nums)]
            else:
                for i, it in enumerate(items[:n]):
                    node = await it.query_selector(RESULT_NUMBER_SELECTOR) or it
                    raw = (await node.text_content() or "").strip()
                    m = re.search(r'([0-9]|[1-2][0-9]|3[0-6])', raw)
                    if not m: continue
                    num = int(m.group(1))
                    out.append({"idx": i, "number": num, "color": num_to_color(num), "raw": raw})
            await browser.close()
            return out
        except:
            await browser.close()
            raise
