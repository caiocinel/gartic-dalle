from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from env import OPENAI_API_KEY
import openai
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime

openai.api_key = "API KEY here" #OPENAI_API_KEY

browser = webdriver.Chrome()
browser.get("https://gartic.com.br/")

alreadyDrawed: list[dict[str, str]] = []

while True:
    if browser.find_elements(By.CSS_SELECTOR, ".btPular").__len__() == 0:
        print("Not in a Room")
        sleep(1)
        continue

    if not browser.find_element(By.CSS_SELECTOR, ".btPular").is_displayed():
        print("Not drawing")
        sleep(1)
        continue

    element = browser.find_elements(By.CSS_SELECTOR, ".contentSpan")
    if element.__len__() == 0:
        sleep(5)
        continue

    value = element[0].text

    if value == "":
        sleep(2)
        continue

    print("Drawing: " + value)

    if not any(d["word"] == value for d in alreadyDrawed):
        print("Fetching image...")

        response = openai.Image.create(
            prompt=f"{value}, hand's drawed",
            n=1,
            size="256x256",
        )

        alreadyDrawed.append(
            {
                "word": value,
                "url": "https://i.imgur.com/FTgo0DQ.png",
            }
        )
        print("Fetching done...")

    print(
        f"Image link: {next((item for item in alreadyDrawed if item['word'] == value), None)['url']}"
    )

    img = Image.open(BytesIO(requests.get(next((item for item in alreadyDrawed if item['word'] == value), None)['url']).content))
    
    browser.execute_script("arguments[0].value = 1; arguments[0].dispatchEvent(new Event('change'))", browser.find_element(By.CSS_SELECTOR, "#tamanho"))        

    drawElement = browser.find_element(By.CSS_SELECTOR ,"#telaCanvas > canvas:nth-child(2)")    
    action = webdriver.ActionChains(driver=browser, duration=0)
    
    browser.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["gartic.com.br/room/atualizar.php"]})
    browser.execute_cdp_cmd('Network.enable', {})

    
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.load()[x, y]

            if (pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250):
                continue

            browser.execute_script(f"arguments[0].setAttribute('codigo', '{'%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])}'); arguments[0].dispatchEvent(new Event('click'))", browser.find_element(By.CSS_SELECTOR, "#cores > div:nth-child(1)"))
            action.move_to_element(drawElement)
            action.move_by_offset((-drawElement.size['width']/2 + 10) + x , (-drawElement.size['height']/2 + 10) + y)
            action.click()
            action.perform()
            print(f"{datetime.now().time()}")

    browser.execute_cdp_cmd('Network.setBlockedURLs', {"urls": [""]})
    browser.execute_cdp_cmd('Network.disable', {})
   
    while browser.find_element(By.CSS_SELECTOR, ".btPular").is_displayed():
        sleep(1)

    print("Ended drawing...")
