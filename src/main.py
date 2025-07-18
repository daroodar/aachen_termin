import asyncio
import os
from collections.abc import Callable
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from logger import logger
from status_checker import check_success_in_last_hour
from telegram_comm import send_telegram_message

OUTPUT_FOLDER = "/home/ec2-user/code/aachen-termin/output"
START_PAGE = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
APPOINTMENT_NOT_AVAILABLE_TEXT = "Kein freier Termin verfügbar"
APPOINTMENTS_AVAILABLE_TEXT = "Appointments are available"
TELEGRAM_MESSAGE = (
    f"{APPOINTMENTS_AVAILABLE_TEXT} for Verpflichtungserklärung! Go to link : {START_PAGE} for "
    f"booking the appointment"
)

def setup_driver():
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    # Comment below if you want browser to be visible
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    return driver


def find_free_appointment(driver: WebDriver):
    driver.get(START_PAGE)

    wait_until(
        driver,
        By.ID,
        ["cookie_msg_btn_no"],
        wait_method=EC.element_to_be_clickable,
        timeout=3,
        step_title="Cookies",
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[1]/div[2]/form/div[5]/h3"],
        wait_method=EC.visibility_of_element_located,
        step_title="Einladung/Visa dropdown",
    )

    einladung_counter_button = wait_until(
        driver,
        By.XPATH,
        [
            "/html/body/main/div[1]/div[2]/form/div[5]/div/ul/li[1]/div/div/div[2]/span[2]/button"
        ],
        wait_method=EC.element_to_be_clickable,
        should_click=False,
        step_title="Increase counter for applications",
    )
    # Click twice for two persons (parents)
    einladung_counter_button.click()
    einladung_counter_button.click()

    # Submit form
    driver.find_element(
        by=By.XPATH, value="/html/body/main/div[1]/div[2]/form/input[4]"
    ).submit()

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[2]/div/div/div[3]/button[1]"],
        wait_method=EC.visibility_of_element_located,
        timeout=3,
        step_title="Submit button for notice that address has changes",
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div/div[4]/form/input[5]"],
        wait_method=EC.element_to_be_clickable,
        step_title="Select Weiter button",
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[1]/details/div/dl/dt[1]/span"],
        wait_method=EC.visibility_of_element_located,
        should_click=False,
        step_title="Sample text to be visible at termin page",
    )

    try:
        driver.find_element(By.XPATH, f"//*[text()='{APPOINTMENT_NOT_AVAILABLE_TEXT}']")
        logger.info("No appointment available -- exiting")
        return
    except NoSuchElementException:
        logger.info(APPOINTMENTS_AVAILABLE_TEXT)

        updated_in_last_hour = check_success_in_last_hour(
            time_to_check=3600,
            status_file=os.path.join(OUTPUT_FOLDER, "status.txt")
        )
        if not updated_in_last_hour:
            asyncio.run(send_telegram_message(TELEGRAM_MESSAGE))
        else:
            logger.info("Found new appointments but they are within the last hour, ignoring.")
            save_source_ang_image(driver)

def wait_until(
        driver,
        criteria: str,
        paths: List[str],
        step_title: str,
        wait_method: Callable = EC.visibility_of_element_located,
        timeout=10,
        should_click=True,
):
    try:
        if not should_click:
            assert (
                    len(paths) == 1
            ), "If the element is not to be clicked, only 1 path allowed"
            return WebDriverWait(driver, timeout).until(
                wait_method((criteria, paths[0]))
            )
        for path in paths:
            WebDriverWait(driver, timeout).until(wait_method((criteria, path))).click()
    except Exception as e:
        logger.info(f"Error during the step: {step_title}")
        raise e


def save_source_ang_image(driver: WebDriver):
    out_path = f"{OUTPUT_FOLDER}/aachen-termin"
    html_content = driver.page_source

    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    now_str = datetime.now().strftime("%Y-%m-%d_%H:%M")
    output_html = out_path + "/" + now_str + ".html"
    output_png = out_path + "/" + now_str + ".png"

    with open(output_html, "w", encoding="utf-8") as file:
        file.write(html_content)
    driver.save_screenshot(output_png)
    logger.info(
        f"HTML content saved to {output_html}, screenshot saved to {output_png}"
    )


def main():
    """
    Your helpful bot for scraping for appointments in Aachen. Only works for Verpflichtungserklärung
    appointments for now
    """

    # Load environment variables from .env file
    load_dotenv()

    driver = setup_driver()
    try:
        logger.info("\n\n" + "--" * 50 + "\n")
        logger.info("Executing new run now")
        find_free_appointment(driver)
    except Exception as e:
        logger.info(f"Error received during the execution of program: {e}")
        save_source_ang_image(driver)
    finally:
        driver.close()
        logger.info("Exiting the run")


if __name__ == "__main__":
    main()
