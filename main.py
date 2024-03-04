import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


def handle_popup(driver):

    try:
        google_account_popup_closebutton = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.ID, "closeSpanId")))
        google_account_popup_closebutton.click()
        print('CLOSED THE POPUP')
    except Exception:
        pass


def page_load_confirm(driver):
    try:
        height = driver.execute_script('return document.body.scrollHeight')
        driver.execute_script(f'window.scrollTo(0,{height})')
        is_ready = driver.execute_script('return document.readyState')
        while is_ready != 'complete':
            driver.refresh()
            print('PAGE REFRESHED')
            try:
                WebDriverWait(driver, 12).until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, "clearfix job-bx wht-shd-bx")))

            except Exception as e:
                print(f'Taking too much time, {str(e)}')

            print('Status after refresh: ', is_ready)

            is_ready = driver.execute_script('return document.readyState')
            if is_ready == 'complete':
                break
            else:
                continue

    except Exception as e:
        print(f'Some unknown ERROR occured, {str(e)}')

    print('Page Loaded Successfully')


driver = webdriver.Chrome()
url = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=data+science&txtLocation='
driver.get(url)

try:
    google_account_popup_closebutton = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "closeSpanId")))
    google_account_popup_closebutton.click()
    print('CLOSED THE POPUP')
except:
    pass

time.sleep(2)

page = 1

# Creating Lists to Make Columns
name = []
company_name = []
exp = []
location = []
job_descp = []
skills_req = []
link = []
salary = []

while True:

    handle_popup(driver)

    page_load_confirm(driver)

    print('Page: ', page)

    data = driver.page_source

    soup = BeautifulSoup(data, 'lxml')

    containers = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")

    for i in containers:
        # Name column
        try:
            title = i.find('h2')
            name.append(title.text.strip())
        except:
            name.append(np.nan)

        # Company Name column
        try:
            co_na = i.find('h3', class_="joblist-comp-name").get_text(strip=True)
            company_name.append(co_na)
        except:
            company_name.append(np.nan)

        # Location, Salary and Experience columns
        x = i.find('ul', class_='top-jd-dtl clearfix').find_all('li')

        # Experience , Salary, Location   ;; try if len(x) == 3, else:
        if len(x) > 2:
            # Location on 2
            try:
                location.append(x[2].text[13:].strip())
            except:
                location.append(np.nan)

            # Salary on 1
            try:
                salary.append(x[1].text.strip())
            except:
                salary.append(np.nan)

        else:
            # Location on 1
            try:
                location.append(x[1].text[13:].strip())
                salary.append(np.nan)
            except:
                location.append(np.nan)

        # Experience at 0
        try:
            exp.append(x[0].text[11:].strip())
        except:
            exp.append(np.nan)

        # Description AND Job Skills column
        y = i.find('ul', class_='list-job-dtl clearfix').find_all('li')

        # Job description
        try:
            job_descp.append(y[0].text[17:].strip())
        except:
            job_descp.append(np.nan)

        # Job skills
        try:
            skills_req.append(y[1].text[13:].strip())
        except:
            skills_req.append(np.nan)

        try:
            apply_link = i.header.h2.a['href']
            link.append(apply_link)
        except:
            link.append(np.nan)

    print(f'Page: {page},  data extracted')

    time.sleep(1)

    page += 1

    handle_popup(driver)

    try:
        handle_popup(driver)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, f'{page}')))
        next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, f'{page}')))
        next_button.click()
        print(f'Page: {page} clicked', '\n')
        time.sleep(1.5)
    except:
        try:

            handle_popup(driver)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT, 'Next 10 pages')))
            next_10_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Next 10 pages')))
            next_10_button.click()
            print(f'Next 10 pages clicked, Page: {page} clicked , \n')
            time.sleep(1.5)
        except:
            print('Process FINISHED')
            break


    finally:

        handle_popup(driver)
        time.sleep(2)

driver.quit()

# Crating a DataFrame with Pandas
df_data = {'Title': name, 'Company Name': company_name, 'Salary Range': salary,'Experience Required': exp, 'Location': location, 'Description': job_descp, 'Skills Required': skills_req, 'Application Link': link}
df = pd.DataFrame(df_data)
df.to_csv('website_jobs1.csv')