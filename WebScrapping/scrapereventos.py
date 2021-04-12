import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import gspread
import time
import random as rd

# CLASES

class SeleniumDriver:

    def __init__(self, headless = False, driverPath = None):

        if driverPath != None:
            if headless:
                self.driver = self.get_driver_headless(driverPath)
            else:
                self.driver = self.get_driver_simple(driverPath)
        else:
            if headless:
                self.driver = self.get_driver_headless()
            else:
                self.driver = webdriver.Chrome(ChromeDriverManager().install())
            


    def get_driver_headless(self):

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_experimental_option("prefs", {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
            }) 
        options.add_argument('--window-size=1920,1080')  
        options.add_argument('--headless')

        return webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
    
    def get_driver_simple(self, driverPath):

        return webdriver.Chrome(executable_path=driverPath)


class Item:

    headers = 'Titulo;Descripcion;Link;Telefono'

    def __init__(self, title, description, link, phone):
        self.title = title
        self.description = description
        self.link = link
        self.phone = phone

    def getcsvline(self):
        self.arguments = [
            self.title,
            self.description,
            self.link,
            self.phone,
        ]
        return ';'.join(self.arguments)

class Eventos:

    def __init__(self, start_url = 'https://www.eventoplus.com/directorio/resultados/agencias-de-eventos/'):
        sel = SeleniumDriver(headless=True)
        self.driver = sel.driver
        self.start_url = start_url
        self.items = []
        self.currentPage = 1
    
    def start(self):

        self.openurl(self.start_url)
        self.acceptCookies()
        while True:
            #self.scrollDown()
            time.sleep(1)
            self.getItems()
            if self.isNextPage():
                self.currentPage += 1
                try:
                    self.gotoNextPage()
                except:
                    break
                print('Page ' + str(self.currentPage) + ' ...')
            else:
                break
                
        print('')
        print('...Finished...')
        print('')
        
    def closeDriver(self):
        self.driver.close()

    def openurl(self,url):
        self.driver.get(url)
    
    def acceptCookies(self):
        button = self.driver.find_element_by_id('onetrust-accept-btn-handler')
        button.click()
    
    def isNextPage(self):
        nextPage = None
        try:
            no_results = self.driver.find_elements_by_xpath("/html/body/div[4]/ul[2]/li/div[1]/div[4]/div[2]/div")[5]
            nextPage = True
        except:
            nextPage = False

        return nextPage
    
    def gotoNextPage(self):
        self.driver.find_element_by_xpath("//*[contains(text(), 'Siguiente >')]").click()

    def scrollDown(self, times = 1):
        for n in range(40):
            self.driver.execute_script("window.scrollBy(0, 400)")

    def getItems(self):

        cardsElements = self.driver.find_elements_by_xpath("/html/body/div[4]/ul[2]/li/div[1]/div[4]/div[2]/div")[1:-1]

        for card in cardsElements:

            title, description, link, phone = '','','',''

            try:
                title = card.find_element_by_class_name('mb1 h2').text
            except:
                pass

            try:
                description = card.find_element_by_class_name('descripcion').text
            except:
                pass

            try:
                link = card.find_element_by_tag_name('a').get_attribute("href")
            except:
                pass
            
            if 'www.eventoplus.com/directorio/proveedores' in link:
                phone = self.getPhone(link)
    
                newItem = Item(title, description, link, phone)
                self.items.append(newItem)
                
        print('Elements:',len(self.items))

    def getPhone(self, link):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(link)

        try:
            tlf = self.driver.find_element_by_xpath("//*[contains(text(), 'Ver Teléfono')]").find_element_by_xpath('..').find_elements_by_tag_name('a')[1].get_attribute("href").replace('tel:','')
        except:
            try:
                tlf = self.driver.find_element_by_xpath("//*[contains(text(), 'Ver Email')]").find_element_by_xpath('..').find_elements_by_tag_name('a')[1].get_attribute("href").replace('mailto:','')
            except:
                tlf = ''

        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return tlf

# HELPERS FUNCTIONS

def cleanText(string):
    string = string.replace('ñ','n')
    string = string.replace('á','a')
    string = string.replace('é','e')
    string = string.replace('í','i')
    string = string.replace('ó','o')
    string = string.replace('ú','u')
    string = string.replace('Á','A')
    string = string.replace('É','E')
    string = string.replace('Í','I')
    string = string.replace('Ó','O')
    string = string.replace('Ú','U')
    string = string.replace('"','')
    string = string.replace('-',' ')

    return string

def writeToCSV(filepath,items, headers = None):
    csv = open(filepath,"a")
    lines = []
    if headers != None:
        csv.write(headers + "\n")

    for item in items:
        line = (item.getcsvline())
        csv.write(line + "\n")
    
    csv.close()

def csvtovalues(filepath, separator = ';'):
    csvlines  = open(filepath, "r").readlines()
    values = []
    for line in csvlines:
        values.append(line.split(separator)[:-1])
    
    return values

def column(matrix, i):
    return [row[i] for row in matrix]

def without(array,i):
	return array[:i] + array[i+1:]

def filterExistingRows(rows):
    filt_rows = []
    links = column(table,3)
    for row in rows:
        if not (row[3] in links):
            filt_rows.append(row)
    return filt_rows

def isInRow(keyword,row):
    if keyword.lower() in row[0].lower() or keyword in row[2].lower():
        return True
    else:
        return False

def deleteDuplicates(filepath):
    csvread = open(filepath,"r")
    f = csvread.readlines()

    for i, line in enumerate(f):
        if line in without(f,i):
            f.pop(i)

    csvread.close()

    csvwrite = open(filepath,"w")
    csvwrite.writelines(f)

# MAIN PROGRAM

def main_eventos():
    evts = Eventos()
    evts.start()
    evts.closeDriver()

    print('Elementos: '+ str(len(evts.items)))

    writeToCSV('/Users/zeemarquez/Documents/Python/Pandas Corporate/WebScrapping/eventos.csv', evts.items, headers= Item.headers)

main_eventos()
