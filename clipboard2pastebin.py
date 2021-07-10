#!/C/Users/heslinr1/Documents/Software/Python/Spyder/python.exe
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 14:16:34 2021
Readsfrom the clipbaord or a specified file, pastes that text using
pastebin, and sends to clipboard the URL for that paste. Intended to 
automate creating Reddit posts of code.

@author: heslinr1
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import pyperclip

print(len(sys.argv))
if len(sys.argv) ==2:
    with open(sys.argv[1]) as file:
        text = file.readlines()
    file.close()
else:
    text = pyperclip.paste()    
url = "https://www.pastebin.com"
css = "#postform-text"

browser = webdriver.Firefox(executable_path = r"C:\Users\heslinr1\geckodriver\geckodriver.exe")
browser.get(url)
browser.find_element_by_css_selector(css).send_keys(text)

#Create new paste
browser.find_element_by_css_selector(".-big").click()
WebDriverWait(browser, 5).until(
    EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, "textarea"),
    text[-1]
    )
)

print("Link sent to clipboard: " + browser.current_url)
pyperclip.copy(browser.current_url)

