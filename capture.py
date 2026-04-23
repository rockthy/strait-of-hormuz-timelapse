import asyncio
from playwright.async_api import async_playwright
import datetime
import os

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Using a more direct URL if possible, or ensuring the map is centered
        # VesselFinder's main map can be tricky. Let's try to wait for the canvas or specific map elements.
        url = "https://www.vesselfinder.com/?lat=26.5&lon=56.3&zoom=8"
        print(f"Navigating to {url}...")
        
        try:
            await page.goto(url, wait_until="load", timeout=60000)
            
            # Wait for the map canvas to appear
            print("Waiting for map canvas...")
            await page.wait_for_selector("canvas", timeout=30000)
            
            # Sometimes it needs a bit more time to zoom and center correctly
            print("Waiting for map to center and zoom...")
            await asyncio.sleep(20)
            
            # Create screenshots directory
            os.makedirs("screenshots", exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/hormuz_{timestamp}.png"
            
            # Hide some UI elements to get a cleaner map if possible
            try:
                await page.add_script_tag(content="""
                    document.querySelectorAll('.map-controls, .header, .footer, #services-menu, .ad-container').forEach(el => el.style.display = 'none');
                """)
            except:
                pass

            await page.screenshot(path=filename)
            print(f"Screenshot saved to {filename}")
            
        except Exception as e:
            print(f"Error during capture: {e}")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(path=f"screenshots/error_{timestamp}.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
