
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
service = Service(executable_path=ChromeDriverManager().install()) #загрузка браузера
driver = webdriver.Chrome(service=service, options=options)


driver.get('https://fragment.com/stars')

con_but = driver.find_element("xpath", "//button[@class='btn btn-primary tm-header-action tm-header-button ton-auth-link']")
con_but.click()

time.sleep(10)

pickle.dump(driver.get_cookies(), open(os.getcwd() + "/cookie.pkl", 'wb'))

