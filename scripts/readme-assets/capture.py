# /// script
# requires-python = ">=3.12"
# dependencies = ["playwright", "imageio-ffmpeg"]
# ///
"""Regenerate the README screenshots and the demo GIF.

Needs the demo server running (fake tools, scripted model), a local Chrome and
Playwright's ffmpeg (`uvx playwright install ffmpeg`, once):

    uv run python scripts/readme-assets/demo_server.py &
    uv run scripts/readme-assets/capture.py            # writes docs/assets/

Restart the demo server between runs: the fake GitHub numbers its pull
requests from 13, and the script the model replays says #13.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from playwright.async_api import Browser, Page, async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8100"
OUT = Path(__file__).resolve().parents[2] / "docs" / "assets"
PROMPT = "tickup feels slow, check it and scale the backend to 2 if it needs it"

DESKTOP = {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 2}
PHONE = {
    "viewport": {"width": 390, "height": 844},
    "device_scale_factor": 3,
    "is_mobile": True,
    "has_touch": True,
}
# Learn mode's explainer boxes are for people learning Kubernetes, not for a
# first look at the product.
QUIET = "localStorage.setItem('jarvis.learn', 'off')"


async def _page(browser: Browser, **options) -> Page:
    context = await browser.new_context(color_scheme="dark", **options)
    await context.add_init_script(QUIET)
    return await context.new_page()


async def _shot(page: Page, route: str, name: str, wait: int = 2500) -> None:
    await page.goto(f"{BASE}/#{route}")
    await page.wait_for_timeout(wait)
    await page.screenshot(path=OUT / f"{name}.png")
    print("wrote", name)


async def _chat(page: Page, *, pause_on_approval: int = 2500, still: str | None = None) -> None:
    """Type the prompt, wait for the gate, approve, wait for the answer."""
    await page.goto(f"{BASE}/#jarvis")
    await page.wait_for_timeout(1500)
    box = page.locator("textarea")
    await box.click()
    await box.press_sequentially(PROMPT, delay=35)
    await page.wait_for_timeout(400)
    await box.press("Enter")
    dialog = page.get_by_role("alertdialog")
    await dialog.wait_for(timeout=60_000)
    await page.wait_for_timeout(pause_on_approval)
    if still:
        await page.screenshot(path=OUT / f"{still}.png")
        print("wrote", still)
    await dialog.get_by_role("button", name="Approve").click()
    await page.get_by_text("Want me to look into it?").wait_for(timeout=60_000)
    await page.wait_for_timeout(3000)
    await page.screenshot(path=OUT / "chat.png")
    print("wrote chat")


def _gif(video: Path, target: Path, width: int = 800, fps: int = 8) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    graph = (
        f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];"
        # Flat UI on black: few colours and no dithering keep it small and sharp.
        "[a]palettegen=max_colors=32:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=none:diff_mode=rectangle"
    )
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-vf", graph, str(target)], check=True)
    print("wrote", target.name, f"{target.stat().st_size / 1e6:.1f} MB")


def _mp4(video: Path, target: Path) -> None:
    """The same recording, sharp and tiny, for posts that play video."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-c:v",
            "libx264",
            "-crf",
            "28",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(target),
        ],
        check=True,
    )
    print("wrote", target.name)


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome")

        # The demo, recorded. The approval still comes from the same run.
        with tempfile.TemporaryDirectory() as tmp:
            context = await browser.new_context(
                color_scheme="dark",
                viewport={"width": 1280, "height": 800},
                device_scale_factor=2,
                record_video_dir=tmp,
                record_video_size={"width": 1280, "height": 800},
            )
            await context.add_init_script(QUIET)
            page = await context.new_page()
            await _chat(page, still="approval")
            await context.close()
            video = next(Path(tmp).glob("*.webm"))
            _mp4(video, OUT / "demo.mp4")
            _gif(video, OUT / "demo.gif")

        page = await _page(browser, **DESKTOP)
        await _shot(page, "status", "status")
        await _shot(page, "cluster", "cluster")
        await _shot(page, "delivery", "delivery")
        await _shot(page, "jarvis/tools", "tools")

        phone = await _page(browser, **PHONE)
        await _shot(phone, "status", "phone-status")
        await _shot(phone, "jarvis", "phone-chat")
        await _shot(phone, "cluster", "phone-cluster")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
