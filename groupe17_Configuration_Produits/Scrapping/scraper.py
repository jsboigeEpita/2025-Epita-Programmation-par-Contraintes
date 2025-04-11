#%%
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import random
import time
import json
#%%

# proxy = "43.153.79.9:13001"

class ScrapingPcPartBuilder:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # Masque Selenium
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--disable-extensions")
        #Headeless mode
        self.options.add_argument("--headless")
        # self.options.add_argument("--force-device-scale-factor=1.25")
        # self.options.add_argument(f"--proxy-server={proxy}")

        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        # self.options.add_argument("--headless")  # Run in headless mode
        self.service = Service()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
    

    def start_scraping(self):
        # self.driver.get("https://pcpartpicker.com")
        # self.driver.implicitly_wait(10)
        scrapper.driver.get('https://pcpartpicker.com/')
        # time.sleep(3)
        self.driver.implicitly_wait(random.randint(1,3))
        scrapper.driver.get('https://pcpartpicker.com/list/')
        component_types = ["storage"]
        for component in component_types:
            self.driver.get(f"https://pcpartpicker.com/products/{component}/")
            self.driver.implicitly_wait(5)
            while True:
                productText = scrapper.driver.execute_script("return document.getElementsByClassName('pp-filter-count')[1].textContent.split(' ')[0]")
                if productText != "Loading":
                    break
                time.sleep(0.5)
            elementsNbr = int(productText)
            pageNbr = elementsNbr // 100 + 1
            print(elementsNbr, pageNbr)
            components = []
            headerRow = self.driver.find_elements(By.CLASS_NAME, 'tablesorter-headerRow')[0].text.split('\n')[1:-2]
            for i in range(1, pageNbr + 1):
                start_page = time.time()
                print(f"Scraping page {i} of {pageNbr} for {component}")
                self.driver.get(f"https://pcpartpicker.com/products/{component}/#page={i}")
                time.sleep(2)
                pageComponents = self.driver.find_elements(By.CLASS_NAME, 'tr__product')
                for pageComponent in pageComponents:
                    start_components = time.time()
                    componentData = {}
                    componentData['name'] = pageComponent.find_elements(By.CLASS_NAME, 'td__name')[0].text.split('\n')[0]
                    componentData['price'] = pageComponent.find_elements(By.CLASS_NAME, 'td__price')[0].text.split('A')[0]
                    specs = pageComponent.find_elements(By.CLASS_NAME, 'td__spec')
                    for j in range(len(specs)):
                        componentData[headerRow[j]] = specs[j].text
                    components.append(componentData)
                    end_components = time.time()
                    print(f"Components scraped in {end_components - start_components:.2f} seconds")
                end_page = time.time()
                print(f"Page {i} scraped in {end_page - start_page:.2f} seconds")
            with open(f"{component}_data.json", "w", encoding="utf-8") as f:
                json.dump(components, f, indent=4, ensure_ascii=False)


# %%
scrapper = ScrapingPcPartBuilder()
scrapper.start_scraping()
#%%
scrapper.driver.close()

# %%
