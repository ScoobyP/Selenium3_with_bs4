import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


class Web_scraping:
    df = pd.DataFrame()
    def __init__(self):
        self.page = 1
        self.driver = webdriver.Chrome()
        self.df_data = {'Title': [], 'Company Name': [], 'Salary Range': [], 'Experience Required': [],
                        'Location': [], 'Description': [], 'Skills Required': [], 'Application Link': []}
        self.url = "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=data+science&txtLocation="
        self.initialise_driver()

    # Opening up the Chrome window
    def initialise_driver(self):

        self.driver.get(self.url)
        try:
            google_popup = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "closeSpanId")))
            google_popup.click()
            print('CLOSED THE POPUP')
        except:
            pass

    # Closing down any POPUPS of same website
    def handle_popup(self):
        try:
            google_account_popup_closebutton = WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located((By.ID, "closeSpanId")))
            google_account_popup_closebutton.click()
            print('CLOSED THE POPUP')
        except:
            pass

    # Confirming whether the page is loaded correctly or not, if NOT we refresh the page in loop
    # It returns us data containers
    def page_load_confirm(self):
        containers=[]
        try:
            height = self.driver.execute_script('return document.body.scrollHeight')
            print(f'Page height: {height}')
            self.driver.execute_script(f'window.scrollTo(0,{height})')

            is_ready = self.driver.execute_script('return document.readyState')
            print('Ready State: ', is_ready)

            while not is_ready == 'complete':
                self.driver.refresh()
                print('PAGE REFRESHED')
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_all_elements_located((By.CLASS_NAME, "clearfix job-bx wht-shd-bx")))
                except:
                    print('RELOAD TAKING TOO MUCH TIME')

                is_ready = self.driver.execute_script('return document.readyState')
                print('STATUS AFTER REFRESH: ', is_ready)

                if is_ready == 'complete':
                    break
                else:
                    continue

            try:
                data = self.driver.page_source
                soup = BeautifulSoup(data, 'lxml')
                containers = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")
                print('Length of boxes present: ', len(containers))
            except:
                print('ERROR: NO BOXES FOUND')

            while len(containers) < 1:
                print('NO BOXES FOUND')
                self.driver.refresh()
                print('PAGE REFRESHED')
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_all_elements_located((By.CLASS_NAME, "clearfix job-bx wht-shd-bx")))
                except:
                    print('RELOAD TAKING TOO MUCH TIME')
                data = self.driver.page_source
                soup = BeautifulSoup(data, 'lxml')
                containers = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")
                print('Length of boxes present: ', len(containers))

                if len(containers) > 1:
                    break
                else:
                    continue

        except Exception:
            print('TIMEOUT: PAGE NOT LOADED CORRECTLY')

        print('Page Loaded Successfully')
        return containers

    # creating a DataFrame from the data of containers, obtained after page loads correctly
    def making_df_table(self, container):
        for i in container:
            # Name column
            try:
                title = i.find('h2')
                self.df_data['Title'].append(title.text.strip())
            except:
                self.df_data['Title'].append(np.nan)

            # Company Name column
            try:
                co_na = i.find('h3', class_="joblist-comp-name").get_text(strip=True)
                self.df_data['Company Name'].append(co_na)
            except:
                self.df_data['Company Name'].append(np.nan)

            # Location, Salary and Experience columns
            x = i.find('ul', class_='top-jd-dtl clearfix').find_all('li')

            # Experience , Salary, Location  :
            if len(x) > 2:
                # Location on 2
                try:
                    self.df_data['Location'].append(x[2].text[13:].strip())
                except:
                    self.df_data['Location'].append(np.nan)

                # Salary on 1
                try:
                    self.df_data['Salary Range'].append(x[1].text.strip())
                except:
                    self.df_data['Salary Range'].append(np.nan)

            else:
                # Location on 1
                try:
                    self.df_data['Location'].append(x[1].text[13:].strip())
                    self.df_data['Salary Range'].append(np.nan)
                except:
                    self.df_data['Location'].append(np.nan)

            # Experience at 0
            try:
                self.df_data['Experience Required'].append(x[0].text[11:].strip())
            except:
                self.df_data['Experience Required'].append(np.nan)

            # Description AND Job Skills column
            y = i.find('ul', class_='list-job-dtl clearfix').find_all('li')

            # Job description
            try:
                self.df_data['Description'].append(y[0].text[17:].strip())
            except:
                self.df_data['Description'].append(np.nan)

            # Job skills
            try:
                self.df_data['Skills Required'].append(y[1].text[13:].strip())
            except:
                self.df_data['Skills Required'].append(np.nan)

            # Application Link Application Link
            try:
                apply_link = i.header.h2.a['href']
                self.df_data['Application Link'].append(apply_link)
            except:
                self.df_data['Application Link'].append(np.nan)

    # Navigating to the next page (if available), else we click - Next 10 pages
    def go_to_next_page(self):
        try:

            self.handle_popup()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, f'{self.page}')))
            next_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, f'{self.page}')))
            next_button.click()
            print(f'Page: {self.page} clicked', '\n')
            time.sleep(1.5)
            return 1

        except:
            try:

                self.handle_popup()
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, 'Next 10 pages')))
                next_10_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, 'Next 10 pages')))
                next_10_button.click()
                print(f'Next 10 pages clicked, Page: {self.page} clicked , \n')
                time.sleep(1.5)
                return 1
            except:
                print('Process FINISHED')
                return 0

        finally:
            self.handle_popup()
            time.sleep(2)

    # Our main program, which uses all of the functions(methods) created in our class, in a certain order
    def main_scrape_data(self):
        df = pd.DataFrame()
        while True:
            # Handling POPUPS
            self.handle_popup()

            # Storing the value of 'containers' from the function in to variable 'containers'
            containers = self.page_load_confirm()

            print('Page: ', self.page)

            # Creating the Data Table
            self.making_df_table(containers)

            print(f'Page: {self.page},  data extracted')

            time.sleep(1)

            # increasing the page value by 1 with every loop
            self.page += 1

            # Handling the POPUP again
            self.handle_popup()

            # Navigating to next page
            if self.go_to_next_page() == 0:
                break
            else:
                continue

        df.DataFrame(self.df_data)

        df.to_csv('website_jobs.csv')


if __name__ == "__main__":

    # Running the Program
    start = time.time()

    class_obj = Web_scraping()
    class_obj.main_scrape_data()

    print(f' Total time: {round(time.time() - start, 4)} seconds')