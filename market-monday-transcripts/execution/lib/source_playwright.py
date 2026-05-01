"""
source_playwright.py
Source B: Headless Chromium + authenticated YouTube session via cookies.

Flow:
1. Load YouTube cookies from cookies.txt into the browser context
2. Navigate to the video, expand the description
3. Scroll the "Show transcript" button into the viewport
4. Click it with page.mouse to trigger the /youtubei/v1/get_panel XHR
5. Parse transcript segments from macroMarkersPanelItemViewModel

The cookies bypass Oracle Cloud's IP block (browser sessions aren't blocked the way
direct API calls are). get_panel returns 1000+ transcript segment view-models in one shot.

Cookies file: ~/.claude/skills/market-monday-transcripts/cookies.txt
Install: pip install playwright playwright-stealth && playwright install chromium
"""

import http.cookiejar
import os
import time

YOUTUBE_BASE = "https://www.youtube.com"
PAGE_LOAD_SLEEP = 5
EXPAND_SLEEP = 2
SCROLL_SLEEP = 1
RESPONSE_TIMEOUT_MS = 20_000

_COOKIES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cookies.txt",
)


def fetch(video_id):
    """
    Use headless Chromium with YouTube cookies to extract transcript via get_panel XHR.
    Returns (text, None) on success, (None, error_str) on failure.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright_not_installed"

    try:
        from playwright_stealth import Stealth
        _stealth = Stealth()
    except ImportError:
        _stealth = None

    # Load YouTube cookies
    pw_cookies = _load_cookies()
    if not pw_cookies:
        return None, "playwright:no_cookies_file"

    url = f"{YOUTUBE_BASE}/watch?v={video_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            viewport={"width": 1280, "height": 800},
        )
        ctx.add_cookies(pw_cookies)
        page = ctx.new_page()
        if _stealth:
            _stealth.apply_stealth_sync(page)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            browser.close()
            return None, f"playwright:page_load_failed:{str(e)[:80]}"

        time.sleep(PAGE_LOAD_SLEEP)

        # Expand description to reveal the Show transcript button
        page.evaluate("() => document.querySelector('tp-yt-paper-button#expand')?.click()")
        time.sleep(EXPAND_SLEEP)

        # Scroll the Show transcript button into the viewport
        page.evaluate(
            "() => { "
            "const b = Array.from(document.querySelectorAll(\"button[aria-label='Show transcript']\")"
            ").find(b => b.offsetParent !== null); "
            "if (b) b.scrollIntoView({behavior: 'instant', block: 'center'}); "
            "}"
        )
        time.sleep(SCROLL_SLEEP)

        # Get the button's viewport position
        rect = page.evaluate(
            "() => { "
            "const b = Array.from(document.querySelectorAll(\"button[aria-label='Show transcript']\")"
            ").find(b => b.offsetParent !== null); "
            "return b ? b.getBoundingClientRect() : null; "
            "}"
        )

        if not rect or not (0 <= rect["y"] <= 750) or rect["width"] == 0:
            browser.close()
            return None, "playwright:transcript_button_not_in_viewport"

        cx = rect["x"] + rect["width"] / 2
        cy = rect["y"] + rect["height"] / 2

        # Use expect_response to properly capture the get_panel XHR response
        try:
            with page.expect_response(
                lambda r: "/youtubei/v1/get_panel" in r.url and r.status == 200,
                timeout=RESPONSE_TIMEOUT_MS,
            ) as resp_info:
                page.mouse.move(cx, cy)
                time.sleep(0.2)
                page.mouse.click(cx, cy)

            response = resp_info.value
            data = response.json()
        except Exception as e:
            browser.close()
            return None, f"playwright:get_panel_failed:{str(e)[:100]}"

        browser.close()

    text = _parse_get_panel(data)
    if text:
        return text, None
    return None, "playwright:empty_panel_response"


def _load_cookies():
    """Load YouTube cookies from Netscape cookies.txt into Playwright format."""
    if not os.path.exists(_COOKIES_PATH):
        return []
    jar = http.cookiejar.MozillaCookieJar()
    try:
        jar.load(_COOKIES_PATH, ignore_discard=True, ignore_expires=True)
    except Exception:
        return []
    return [
        {
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "secure": bool(c.secure),
            "httpOnly": False,
        }
        for c in jar
        if "youtube" in c.domain or "google" in c.domain
    ]


def _parse_get_panel(data):
    """
    Parse the get_panel response.
    Transcript segments live at:
      content.engagementPanelSectionListRenderer.content.sectionListRenderer
      .contents[0].itemSectionRenderer.contents[i]
      .macroMarkersPanelItemViewModel.item.timelineItemViewModel
      .contentItems[j].transcriptSegmentViewModel.simpleText
    """
    try:
        section = (
            data.get("content", {})
            .get("engagementPanelSectionListRenderer", {})
            .get("content", {})
            .get("sectionListRenderer", {})
            .get("contents", [{}])[0]
            .get("itemSectionRenderer", {})
            .get("contents", [])
        )

        lines = []
        for item in section:
            tl = (
                item.get("macroMarkersPanelItemViewModel", {})
                .get("item", {})
                .get("timelineItemViewModel", {})
                .get("contentItems", [])
            )
            for ci in tl:
                text = ci.get("transcriptSegmentViewModel", {}).get("simpleText", "")
                if text and text.strip():
                    lines.append(text.strip())

        if not lines:
            return ""

        chunks = [" ".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
        return "\n\n".join(chunks)
    except Exception:
        return ""
