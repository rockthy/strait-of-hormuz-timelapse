import asyncio
from playwright.async_api import async_playwright
import datetime
import os


TARGET_LAT = 26.5
TARGET_LON = 56.3
TARGET_ZOOM = 8
TARGET_QUERIES = [
    "Strait of Hormuz",
    "26.5,56.3",
    "Bandar Abbas, Iran",
]


async def focus_map_on_hormuz(page):
    """Force map to center on Strait of Hormuz by searching and verifying location."""
    search_input = page.locator('input[placeholder="Ship / Port / Container"]')
    if await search_input.count() == 0:
        print("Map search input not found; relying on URL coordinates.")
        return

    # Keep trying to center the map until coordinates are close to target.
    # Target: 26.5°N, 56.3°E (Strait of Hormuz)
    max_retries = 5
    tolerance = 5.0  # Accept if within 5 degrees
    
    for attempt in range(max_retries):
        try:
            # Try geographic name first, then coordinates
            query = TARGET_QUERIES[attempt % len(TARGET_QUERIES)]
            await search_input.fill(query)
            await page.keyboard.press("Enter")
            await asyncio.sleep(3)
            
            # Try to read current coordinates from the map display.
            # VesselFinder shows coordinates in the bottom-left corner.
            coords = await page.evaluate("""
                () => {
                    // Try to find coordinate display in the map UI
                    const coordText = document.body.innerText;
                    const latMatch = coordText.match(/Lat:\\s*([\\d.-]+)/);
                    const lonMatch = coordText.match(/Lon:\\s*([\\d.-]+)/);
                    
                    if (latMatch && lonMatch) {
                        return {lat: parseFloat(latMatch[1]), lon: parseFloat(lonMatch[1])};
                    }
                    return null;
                }
            """)
            
            if coords:
                print(f"Attempt {attempt + 1}: searched '{query}', map center: {coords['lat']:.2f}°N, {coords['lon']:.2f}°E")
                
                # Check if we're close to target (26.5, 56.3)
                lat_diff = abs(coords['lat'] - TARGET_LAT)
                lon_diff = abs(coords['lon'] - TARGET_LON)
                
                if lat_diff < tolerance and lon_diff < tolerance:
                    print(f"Map centered on Strait of Hormuz!")
                    return
            else:
                print(f"Attempt {attempt + 1}: searched '{query}', could not read coordinates")
                
        except Exception as e:
            print(f"Search attempt {attempt + 1} failed: {e}")
    
    print("Warning: Could not verify proper map centering after retries; proceeding with screenshot.")


async def capture():
    os.makedirs("screenshots", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--disable-dev-shm-usage"])
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        async def block_nonessential_resources(route):
            if route.request.resource_type in {"font", "media"}:
                await route.abort()
                return
            await route.continue_()

        await context.route("**/*", block_nonessential_resources)
        page = await context.new_page()
        page.set_default_navigation_timeout(45000)
        page.set_default_timeout(30000)
        
        url = f"https://www.vesselfinder.com/?lat={TARGET_LAT}&lon={TARGET_LON}&zoom={TARGET_ZOOM}"
        print(f"Navigating to {url}...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for the map canvas to appear
            print("Waiting for map canvas...")
            await page.wait_for_selector("canvas", timeout=30000)

            # Force focus on Strait of Hormuz in case the site falls back to a prior/default viewport.
            await focus_map_on_hormuz(page)
            
            # Sometimes it needs a bit more time to zoom and center correctly
            print("Waiting for map to center and zoom...")
            await asyncio.sleep(20)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/hormuz_{timestamp}.png"
            
            # Hide some UI elements to get a cleaner map if possible
            try:
                await page.add_script_tag(content="""
                    document.querySelectorAll('.map-controls, .header, .footer, #services-menu, .ad-container').forEach(el => el.style.display = 'none');
                """)
            except:
                pass

            await page.screenshot(path=filename, timeout=15000)
            print(f"Screenshot saved to {filename}")
            
        except Exception as e:
            print(f"Error during capture: {e}")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                await page.screenshot(path=f"screenshots/error_{timestamp}.png", timeout=5000)
            except Exception as screenshot_error:
                print(f"Failed to save error screenshot: {screenshot_error}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
