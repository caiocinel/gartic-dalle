from selenium import webdriver
import pyautogui
from selenium.webdriver.common.by import By
from time import sleep
from env import OPENAI_API_KEY
import openai
from PIL import Image
from io import BytesIO
import requests
import keyboard
from datetime import datetime

openai.api_key = "API KEY here" #OPENAI_API_KEY

browser = webdriver.Chrome()
browser.get("https://gartic.com.br/")

alreadyDrawed: list[dict[str, str]] = []

def get_initial_win_size() -> tuple[int, int]:
    frame_grid = browser.find_element(By.CSS_SELECTOR ,'#telaCanvas > canvas:nth-child(2)')
    browser_location = browser.get_window_position() 
    x = browser_location['x'] + 17 + 2
    y = browser_location['y'] + 73 + 25 + 10
    print(f"Element Position: {frame_grid.location}")
    print(f"Browser Position: {browser_location}")
    return (frame_grid.location['x'] + x, frame_grid.location['y'] + y)
    

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

        # response = openai.Image.create(
        #     prompt=f"{value}, hand's drawed",
        #     n=1,
        #     size="256x256",
        # )

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
    
    winPos = get_initial_win_size()

    for x in range(img.width):
        for y in range(img.height):
            pixel = img.load()[x, y]

            if (pixel[0] > 250 and pixel[1] > 250 and pixel[2] > 250):
                continue

            pyautogui.click(x=(winPos[0] + x), y=(winPos[1] + y), _pause=False)

   
    try:
        while browser.find_element(By.CSS_SELECTOR, ".btPular").is_displayed():
            sleep(1)
    except:
        pass

    print("Ended drawing...")

