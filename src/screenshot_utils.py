import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


MARKETMAP_URLS = {
    "kospi": "https://markets.hankyung.com/marketmap/kospi",
    "kosdaq": "https://markets.hankyung.com/marketmap/kosdaq",
}
MARKETMAP_CONTAINER_SELECTORS = (
    "div.map-area",
    "#map_area.map-area",
    "div.fiq-marketmap",
    "#map_area.fiq-marketmap",
)
MARKETMAP_SVG_SELECTOR = "svg.anychart-ui-support"


def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1280")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.set_capability("pageLoadStrategy", "eager")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome Driver: {e}")
        return None


def wait_for_first_visible(driver, selectors, timeout=20):
    wait = WebDriverWait(driver, timeout)
    last_error = None

    for selector in selectors:
        try:
            print(f"Waiting for selector: {selector}")
            return wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
            )
        except Exception as exc:
            last_error = exc

    if last_error:
        raise last_error

    raise RuntimeError("No selectors provided.")


def resize_window_for_element(driver, element, min_width=1600, padding=120):
    dimensions = driver.execute_script(
        """
        const el = arguments[0];
        el.scrollIntoView({block: 'start', inline: 'nearest'});
        const rect = el.getBoundingClientRect();
        return {
            width: Math.ceil(Math.max(rect.width, el.scrollWidth, el.clientWidth)),
            height: Math.ceil(Math.max(rect.height, el.scrollHeight, el.clientHeight)),
        };
        """,
        element,
    )

    width = max(min_width, dimensions["width"] + 40)
    height = max(1200, dimensions["height"] + padding)
    print(f"Resizing window to {width}x{height} for element capture...")
    driver.set_window_size(width, height)
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'start', inline: 'nearest'});", element
    )
    time.sleep(2)


def wait_for_svg_content(driver, element, timeout=20):
    wait = WebDriverWait(driver, timeout)

    def svg_is_ready(_driver):
        data = _driver.execute_script(
            """
            const container = arguments[0];
            const svg = container.querySelector(arguments[1]);
            if (!svg) {
                return null;
            }

            const rect = svg.getBoundingClientRect();
            const rectCount = svg.querySelectorAll("rect").length;
            const textCount = svg.querySelectorAll("text").length;
            return {
                width: Math.ceil(rect.width),
                height: Math.ceil(rect.height),
                rectCount,
                textCount,
            };
            """,
            element,
            MARKETMAP_SVG_SELECTOR,
        )

        if not data:
            return False

        return (
            data["width"] > 1000
            and data["height"] > 500
            and data["rectCount"] > 20
            and data["textCount"] > 10
        )

    wait.until(svg_is_ready)


def save_screenshot_with_padding(driver, element, output_path, padding=48):
    bounds = driver.execute_script(
        """
        const container = arguments[0];
        const svg = container.querySelector(arguments[1]);
        const target = svg || container;
        const containerRect = container.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();

        return {
            x: Math.max(0, Math.floor(Math.min(containerRect.left, targetRect.left) + window.scrollX)),
            y: Math.max(0, Math.floor(Math.min(containerRect.top, targetRect.top) + window.scrollY)),
            width: Math.ceil(Math.max(containerRect.right, targetRect.right) - Math.min(containerRect.left, targetRect.left)),
            height: Math.ceil(Math.max(containerRect.bottom, targetRect.bottom) - Math.min(containerRect.top, targetRect.top)),
        };
        """,
        element,
        MARKETMAP_SVG_SELECTOR,
    )

    clip = {
        "x": max(0, bounds["x"] - padding),
        "y": max(0, bounds["y"] - padding),
        "width": bounds["width"] + (padding * 2),
        "height": bounds["height"] + (padding * 2),
        "scale": 1,
    }

    try:
        screenshot = driver.execute_cdp_cmd(
            "Page.captureScreenshot",
            {
                "format": "png",
                "fromSurface": True,
                "captureBeyondViewport": True,
                "clip": clip,
            },
        )
        with open(output_path, "wb") as file_handle:
            file_handle.write(base64.b64decode(screenshot["data"]))
    except Exception:
        element.screenshot(output_path)


def take_finviz_screenshot(output_path="finviz_map.png"):
    """
    Takes a screenshot of the Finviz map (#canvas-wrapper).
    """
    driver = get_chrome_driver()
    if not driver:
        return None

    try:
        url = "https://finviz.com/map.ashx"
        print(f"Navigating to {url}...")
        driver.get(url)

        # Wait for the map to load
        print("Waiting for map element...")
        wait = WebDriverWait(driver, 20)
        element = wait.until(
            EC.visibility_of_element_located((By.ID, "canvas-wrapper"))
        )

        # Add delay to ensure canvas is rendered
        print("Waiting for canvas to render...")
        time.sleep(5)

        # Take screenshot of the element
        element.screenshot(output_path)
        print(f"Screenshot saved to {output_path}")
        return output_path

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Failed to take screenshot: {e}")
        return None
    finally:
        if "driver" in locals() and driver:
            driver.quit()


def take_kospi_screenshot(output_path="kospi_map.png"):
    """
    Takes a screenshot of the KOSPI heatmap SVG from Hankyung market map.
    """
    return take_hankyung_marketmap_screenshot("kospi", output_path)


def take_kosdaq_screenshot(output_path="kosdaq_map.png"):
    """
    Takes a screenshot of the KOSDAQ heatmap from Hankyung market map.
    """
    return take_hankyung_marketmap_screenshot("kosdaq", output_path)


def take_hankyung_marketmap_screenshot(market, output_path):
    """
    Takes a screenshot of the requested Hankyung market map container.
    """
    driver = get_chrome_driver()
    if not driver:
        return None

    try:
        url = MARKETMAP_URLS[market]
        print(f"Navigating to {url}...")
        driver.get(url)

        print("Waiting for map element...")
        element = wait_for_first_visible(
            driver, MARKETMAP_CONTAINER_SELECTORS, timeout=20
        )
        print("Waiting for chart to render...")
        wait_for_svg_content(driver, element, timeout=20)
        resize_window_for_element(driver, element)
        time.sleep(3)

        save_screenshot_with_padding(driver, element, output_path)
        print(f"Screenshot saved to {output_path}")
        return output_path

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Failed to take {market.upper()} screenshot: {e}")
        return None
    finally:
        if "driver" in locals() and driver:
            driver.quit()
