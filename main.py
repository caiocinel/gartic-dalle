OPENAI_API_KEY = "API KEY here"

import importlib.util
import sys
import subprocess


# Check if all dependencies are installed
if selenium := importlib.util.find_spec("selenium") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'selenium'])

if openai := importlib.util.find_spec("openai") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'openai'])

if PIL := importlib.util.find_spec("PIL") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'Pillow'])

if requests := importlib.util.find_spec("requests") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'requests'])



from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import openai
from PIL import Image
from io import BytesIO
import requests

openai.api_key = OPENAI_API_KEY

browser = webdriver.Chrome()
browser.get("https://gartic.com.br/")

# this list is used to fetch the word only once, {word: "word", url: "url"}
alreadyDrawed: list[dict[str, str]] = [] 

while True:
    # If user is in a room
    if browser.find_elements(By.CSS_SELECTOR, ".btPular").__len__() == 0:
        sleep(5)
        continue

    # If user is drawing
    if not browser.find_element(By.CSS_SELECTOR, ".btPular").is_displayed():
        sleep(1)
        continue

    # Get the word to draw
    element = browser.find_elements(By.CSS_SELECTOR, ".contentSpan")
    if element.__len__() == 0:
        sleep(5)
        continue

    value = element[0].text

    if value == "":
        sleep(2)
        continue

    print("Drawing: " + value)

    # Check if the word was already drawed, prevent to fetch the same word twice
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
                "url": response['images'][0]['url'],
            }
        )

    img = Image.open(BytesIO(requests.get(next((item for item in alreadyDrawed if item['word'] == value), None)['url']).content))

    #Change brush size to 1px    
    browser.execute_script("arguments[0].value = 1; arguments[0].dispatchEvent(new Event('change'))", browser.find_element(By.CSS_SELECTOR, "#tamanho"))

    drawElement = browser.find_element(By.CSS_SELECTOR ,"#telaCanvas > canvas:nth-child(2)")    
    action = webdriver.ActionChains(driver=browser, duration=0)
    

    #Block gartic drawing backend url to prevent disconnects while drawing
    print("Blocking Gartic servers...")
    browser.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["gartic.com.br/room/atualizar.php"]})
    browser.execute_cdp_cmd('Network.enable', {})

    
    print("Start drawing...")
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.load()[x, y]

            # If pixel is white then skip (background already is white, best performance)
            if (pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250): 
                continue

            # Change color to pixel color
            browser.execute_script(f"arguments[0].setAttribute('codigo', '{'%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])}'); arguments[0].dispatchEvent(new Event('click'))", browser.find_element(By.CSS_SELECTOR, "#cores > div:nth-child(1)"))
            action.move_to_element(drawElement)

            # Selenium moves to center of the element, so we need to move to the top left corner and add relative position
            action.move_by_offset((-drawElement.size['width']/2 + 10) + x , (-drawElement.size['height']/2 + 10) + y)
            action.click()
            action.perform()

    print("Drawing finished...")

    print("Unblocking Gartic servers...")
    browser.execute_cdp_cmd('Network.setBlockedURLs', {"urls": [""]})
    browser.execute_cdp_cmd('Network.disable', {})
   
    # Wait for round to finish
    while browser.find_element(By.CSS_SELECTOR, ".btPular").is_displayed():
        sleep(1)

    print("Drawing round finished...")
