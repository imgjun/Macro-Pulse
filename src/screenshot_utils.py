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
    chrome_options.add_argument("--window-size=1920,1080")
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
        time.sleep(5)
        resize_window_for_element(driver, element)

        element.screenshot(output_path)
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
