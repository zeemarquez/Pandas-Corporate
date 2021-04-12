# %%
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import gspread
import time
import random as rd

driver = webdriver.Chrome(ChromeDriverManager().install())
# %%
driver.get('https://belbex.com/locales/madrid-provincia/alquiler/')

# %%

 aceptar = driver.find_element_by_class_name("formbutton")
# %%
 aceptar.click()
# %%
cards = driver.find_elements_by_class_name("addressWrapper")
card1 = cards[0].find_element_by_xpath('..')
# %%
driver.execute_script("window.scrollTo(0, 100000)") 
# %%
for card in cards:
    title = card.find_element_by_class_name('re-Card-title').text
    print(title)

# %%
len(cards)
# %%
class Item:
    headers = 'asdasdad'

# %%
text = 'españa'
# %%

nextPage = driver.find_element_by_xpath("//*[@aria-label='Página Siguiente']")
# %%
driver.execute_script("window.scrollBy(0, 400)")
# %%

# %%
response = requests.get('https://datos.gob.es/apidata/catalog/dataset/title/mirador?_sort=title&_pageSize=10&_page=0')
# %%
headers = {
    'Accept: text/csv',
}
# %%
