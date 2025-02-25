import asyncio
import boto3
import os

from collections.abc import Callable
from datetime import datetime
from dotenv import load_dotenv
from typing import List

from telegram_comm import send_telegram_message

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

S3_OUTPUT_BUCKET = "s3://aachen-appointment-artifacts"
START_PAGE = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
APPOINTMENT_NOT_AVAILABLE_TEXT = "Kein freier Termin verfügbar - test"
APPOINTMENTS_AVAILABLE_TEXT = "APPOINTMENTS ARE AVAILABLE!"
TELEGRAM_MESSAGE = f"{APPOINTMENTS_AVAILABLE_TEXT}! Go to link : {START_PAGE}"

def setup_driver():
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    # Comment below if you want browser to be visible
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver

def find_free_appointment(driver: WebDriver):
    driver.get(
        START_PAGE
    )

    wait_until(
        driver,
        By.ID,
        ["cookie_msg_btn_no"],
        wait_method=EC.element_to_be_clickable,
        timeout=3,
        step_title="Cookies"
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[1]/div[2]/form/div[5]/h3"],
        wait_method=EC.visibility_of_element_located,
        step_title="Einladung/Visa dropdown"
    )

    einladung_counter_button = wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[1]/div[2]/form/div[5]/div/ul/li[1]/div/div/div[2]/span[2]/button"],
        wait_method=EC.element_to_be_clickable,
        should_click=False,
        step_title="Increase counter for applications"
    )
    # Click twice for two persons (parents)
    einladung_counter_button.click()
    einladung_counter_button.click()

    # Submit form
    driver.find_element(by=By.XPATH, value="/html/body/main/div[1]/div[2]/form/input[4]").submit()

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[2]/div/div/div[3]/button[1]"],
        wait_method=EC.visibility_of_element_located,
        timeout=3,
        step_title="Submit button for notice that address has changes"
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div/details[2]/div/form/input[4]"],
        wait_method=EC.element_to_be_clickable,
        step_title="Select Auslanderamt aachen office"
    )

    wait_until(
        driver,
        By.XPATH,
        ["/html/body/main/div[1]/details/div/dl/dt[1]/span"],
        wait_method=EC.visibility_of_element_located,
        should_click=False,
        step_title="Sample text to be visible at termin page"
    )

    try:
        driver.find_element(By.XPATH, f"//*[text()='{APPOINTMENT_NOT_AVAILABLE_TEXT}']")
        print("No appointment available -- exiting")
        return
    except NoSuchElementException:
        print(APPOINTMENTS_AVAILABLE_TEXT)
        asyncio.run(send_telegram_message(TELEGRAM_MESSAGE))
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
            assert len(paths)==1, "If the element is not to be clicked, only 1 path allowed"
            return WebDriverWait(driver, timeout).until(
                wait_method(
                    (criteria, paths[0]))
            )
        for path in paths:
            WebDriverWait(driver, timeout).until(
                wait_method(
                    (criteria, path))
            ).click()
    except Exception as e:
        print(f"Error during the step: {step_title}")
        raise e


def save_source_ang_image(driver: WebDriver):
    _PAGE_OUTPUT_PATH = "aachen-termin"
    tmp_local_path = f"/tmp/{_PAGE_OUTPUT_PATH}"

    html_content = driver.page_source

    if not os.path.exists(tmp_local_path):
        os.makedirs(tmp_local_path, exist_ok=True)

    now_str = datetime.now().strftime("%Y-%m-%d_%H:%M")
    output_html = tmp_local_path + "/" + now_str + ".html"
    output_png = tmp_local_path + "/" + now_str + ".png"

    s3 = boto3.resource('s3')
    s3.Bucket(S3_OUTPUT_BUCKET).upload_file(output_html, output_html.replace("/tmp/", ""))
    s3.Bucket(S3_OUTPUT_BUCKET).upload_file(output_png, output_png.replace("/tmp/", ""))

    with open(output_html, "w", encoding="utf-8") as file:
        file.write(html_content)
    driver.save_screenshot(output_png)
    print(f"HTML content saved to {output_html}, screenshot saved to {output_png}")


def main():

    # Load environment variables from .env file
    load_dotenv()

    driver = setup_driver()
    try:
        find_free_appointment(driver)
    except Exception as e:
        print(f"Error received during the execution of program: {e}")
        save_source_ang_image(driver)
    finally:
        driver.close()

if __name__ == "__main__":
    main()
