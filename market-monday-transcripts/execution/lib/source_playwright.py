"""
source_playwright.py
Source B: Headless Chromium browser automation via Playwright + stealth mode.

Replicates what paid transcript services (supadata.ai, noteGPT.io, etc.) do under
the hood: launch a real browser with masked automation signals, navigate to the YouTube
video, intercept the /youtubei/v1/get_transcript XHR that fires when the transcript
panel opens, and capture the structured JSON response.

This bypasses Oracle Cloud IP blocks because the request looks identical to a real
human using Chrome — not a scripted API call.

Install: pip install playwright playwright-stealth
         playwright install chromium
"""

import json
import threading
import time

YOUTUBE_BASE = "https://www.youtube.com"
XHR_PATH = "/youtubei/v1/get_transcript"
PAGE_TIMEOUT_MS = 45_000
XHR_WAIT_SECONDS = 30


def fetch(video_id):
    """
    Use headless Chromium to extract a YouTube transcript via XHR interception.
    Returns (text, None) on success, (None, error_str) on failure.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright_not_installed"

    try:
        from playwright_stealth import stealth_sync
        _has_stealth = True
    except ImportError:
        _has_stealth = False

    url = f"{YOUTUBE_BASE}/watch?v={video_id}"
    captured = {"data": None, "event": threading.Event()}

    def _on_response(response):
        if XHR_PATH in response.url:
            try:
                captured["data"] = response.json()
            except Exception:
                pass
            captured["event"].set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = context.new_page()

        if _has_stealth:
            stealth_sync(page)

        page.on("response", _on_response)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        except Exception as e:
            browser.close()
            return None, f"playwright:page_load_failed:{str(e)[:80]}"

        # Try to open the transcript panel via the "More actions" button
        transcript_opened = _open_transcript_panel(page)

        if transcript_opened:
            # Wait for the XHR to fire
            captured["event"].wait(timeout=XHR_WAIT_SECONDS)

        if captured["data"]:
            text = _parse_transcript_json(captured["data"])
            browser.close()
            if text:
                return text, None
            return None, "playwright:empty_transcript_json"

        # XHR not captured — fall back to DOM scraping of rendered segments
        text = _extract_from_dom(page)
        browser.close()

        if text:
            return text, None
        return None, "playwright:no_transcript_found"


def _open_transcript_panel(page):
    """Click the transcript button. Returns True if the panel was triggered."""
    try:
        # Dismiss cookie consent if present
        page.locator("button[aria-label*='Accept']").click(timeout=3000)
    except Exception:
        pass

    # Scroll down slightly so the video controls are visible
    page.evaluate("window.scrollBy(0, 300)")
    time.sleep(1)

    # Try the "More actions" (...) button below the video title
    for selector in [
        "button[aria-label='More actions']",
        "#above-the-fold button[aria-label]",
        "ytd-menu-renderer button",
    ]:
        try:
            page.locator(selector).first.click(timeout=4000)
            time.sleep(0.8)
            break
        except Exception:
            continue

    # Click "Show transcript" / "Open transcript" menu item
    for label in ["Show transcript", "Open transcript", "transcript"]:
        try:
            page.locator(f"text={label}").first.click(timeout=4000)
            time.sleep(1.5)
            return True
        except Exception:
            continue

    return False


def _parse_transcript_json(data):
    """
    Parse the /youtubei/v1/get_transcript JSON response.
    The response contains nested 'transcriptBodyRenderer' with 'cueGroups'.
    """
    try:
        actions = (
            data.get("actions", [{}])[0]
            .get("updateEngagementPanelAction", {})
            .get("content", {})
            .get("transcriptRenderer", {})
            .get("body", {})
            .get("transcriptBodyRenderer", {})
            .get("cueGroups", [])
        )
        lines = []
        for group in actions:
            cues = group.get("transcriptCueGroupRenderer", {}).get("cues", [])
            for cue in cues:
                runs = (
                    cue.get("transcriptCueRenderer", {})
                    .get("cue", {})
                    .get("simpleText", "")
                )
                if runs:
                    lines.append(runs.strip())

        if not lines:
            return ""

        chunks = [" ".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
        return "\n\n".join(chunks)
    except Exception:
        return ""


def _extract_from_dom(page):
    """Fallback: scrape rendered transcript segments from the DOM."""
    try:
        page.wait_for_selector(
            "ytd-transcript-segment-renderer", timeout=8000
        )
        elements = page.locator("ytd-transcript-segment-renderer .segment-text").all()
        lines = [el.inner_text().strip() for el in elements if el.inner_text().strip()]
        if not lines:
            return ""
        chunks = [" ".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
        return "\n\n".join(chunks)
    except Exception:
        return ""
