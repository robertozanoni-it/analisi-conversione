import asyncio
from playwright.async_api import async_playwright
import os

async def verify_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load the local index.html
        path = os.path.abspath("index.html")
        await page.goto(f"file://{path}")

        # Check title
        title = await page.title()
        print(f"Title: {title}")

        # Wait for React to render (Babel transpile might take a bit)
        await page.wait_for_selector("h1")
        print("Header found")

        # Check if the upload input exists
        upload_input = await page.query_selector("input[type='file']")
        if upload_input:
            print("Upload input found")
        else:
            print("Upload input NOT found")

        # Simulate file upload (using the test_image.png if it exists)
        if os.path.exists("test_image.png"):
            await upload_input.set_input_files("test_image.png")
            print("Image uploaded")

            # Wait for analyze button
            analyze_btn = await page.wait_for_selector("button:has-text('Analizza Landing Page')")
            print("Analyze button found, clicking...")
            await analyze_btn.click()

            # Wait for analysis to complete (mock takes 4s)
            print("Waiting for results...")
            await page.wait_for_selector("h2:has-text('Analisi Strategica Completa')", timeout=10000)
            print("Results found!")

            # Check for specific sections
            sections = [
                "Stima Impatto sulla Conversione",
                "Efficacia Above the Fold",
                "Attrito del Form",
                "Analisi Strategica Profonda"
            ]
            for section in sections:
                found = await page.query_selector(f"h2:has-text('{section}')")
                if found:
                    print(f"Section '{section}' found")
                else:
                    print(f"Section '{section}' NOT found")

            await page.screenshot(path="verification_screenshot.png", full_page=True)
            print("Screenshot saved to verification_screenshot.png")
        else:
            print("test_image.png not found, skipping analysis test")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_app())
