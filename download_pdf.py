from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import requests
import asyncio
import socketio
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from config import first_semester_path, second_semester_path, username, password, year, headless, download_first_semester, download_second_semester

def get_pdf(socketio):
    socketio.emit('progress', {'message': "starting..."}, namespace='/task')
    # Initialize Chrome WebDriver
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--new-tab-link")
    if headless == True:
        chrome_options.add_argument("--headless")
    driver = Chrome(options=chrome_options)

    driver.set_window_size(1234, 792)

    # Open the URL
    driver.get("https://gannacademy.myschoolapp.com/app/student#studentmyday/assignment-center")
    print("opened browser")
    socketio.emit('progress', {'message': "Opened Browser"}, namespace='/task')
    

    # Wait for the Username field to be clickable
    username_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "Username"))
    )
    time.sleep(0.25)
    username_field.click()
    text_to_send = username + "@gannacademy.org"
    # enter username element
    username_field.send_keys(text_to_send)
    username_field.send_keys(Keys.ENTER)
    print("Entered username field")
    socketio.emit('progress', {'message': "Entered Username"}, namespace='/task')

    # Wait for the URL to include "login.microsoftonline.com"
    WebDriverWait(driver, 10).until(EC.url_contains("login.microsoftonline.com"))

    # Wait for the password field to be clickable
    password_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "i0118"))
    )
    time.sleep(0.25)
    password_field.click()
    password_field.send_keys(password)
    password_field.send_keys(Keys.ENTER)
    print("Entered password field")
    socketio.emit('progress', {'message': "Entered Password"}, namespace='/task')

    try:
        # Wait for yes button / id="idSIButton9" to be clickable
        yes_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        time.sleep(0.25)
        yes_button.click()
        print("entered yes")
        socketio.emit('progress', {'message': "Entered Yes"}, namespace='/task')
    except:
        pass

    # Wait for the report dropdown to be clickable
    report_dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#report-dropdown > .caret"))
    )
    time.sleep(0.25)
    report_dropdown.click()
    print("Opened Dropdown")
    socketio.emit('progress', {'message': "Opened Dropdown"}, namespace='/task')

    # Wait for the "View Assignment Grades" link to be clickable
    view_grades_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "View Assignment Grades"))
    )
    time.sleep(0.25)
    view_grades_link.click()
    print("Clicked view assignment grades")
    socketio.emit('progress', {'message': "Clicked View Assignment Grades"}, namespace='/task')

    # Wait for the new tab to open and switch the WebDriver's focus to it
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    all_handles = driver.window_handles
    driver.switch_to.window(all_handles[1])
    print("Switched to new tab")
    socketio.emit('progress', {'message': "Switched to New Tab"}, namespace='/task')


    if download_first_semester == True:
        #switch to first semester
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="L_c1i0_cb3224_ct3224_ct4"]/select'))
        )
        dropdown.click()
        socketio.emit('progress', {'message': "Opened Dropdown to switch semester/grade"}, namespace='/task')

        time.sleep(1.25)

        dropdown.send_keys(Keys.UP)
        time.sleep(1.25)
        dropdown.send_keys(Keys.UP)
        time.sleep(1.25)
        dropdown.send_keys(Keys.ENTER)
        socketio.emit('progress', {'message': "Switched to first semester"}, namespace='/task')

        generate_report = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Generate Report"))
        )
        time.sleep(0.25)
        generate_report.click()
        print("clicked generate report")
        socketio.emit('progress', {'message': "Generating First Semester Report"}, namespace='/task')

        iframe = WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'trying-hard'))
        )

        time.sleep(2)

        while True:
            try:
                element = driver.find_element(By.XPATH, "/html/body")
                base_uri = element.get_property("baseURI")
                if "/api/Report/ReportJob/" in base_uri:
                    print(f"Found it! The baseURI is '{base_uri}'")
                    socketio.emit('progress', {'message': "Got First Semester PDF"}, namespace='/task')
                    URL = base_uri
                    # Perform additional actions here if needed
                    break
                else:
                    print(f"The baseURI is '{base_uri}'. Trying again...")
                    socketio.emit('progress', {'message': "Waiting for First Semester PDF to Load"}, namespace='/task')
                    time.sleep(2)  # Add a delay before checking again
            except (NoSuchElementException, StaleElementReferenceException):
                print("baseURI property not found or stale element. Trying again...")
                time.sleep(2)  # Add a delay before checking again

        # get cookies
        cookies = driver.get_cookies()

        # Convert the list of cookies to a dictionary
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            # Requests sorts cookies= alphabetically
            # 'cookie': 's=aLeezGIaZjN0w6/BmiS5Kghhb2r5QsO/Wk58eOWhWIs=; mp_b4726c21784ae6857d9c56cfb9866654_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18ab7c8443441e4-096b44babd3e47-19525634-13c680-18ab7c8443441e4%22%2C%22%24device_id%22%3A%20%2218ab7c8443441e4-096b44babd3e47-19525634-13c680-18ab7c8443441e4%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fgannacademy.myschoolapp.com%2Fapp%3FsvcId%3Dedu%26envId%3Dp-7kX8hIPgrkeeZXCVn1fL7w%26bb_id%3D1%22%2C%22%24initial_referring_domain%22%3A%20%22gannacademy.myschoolapp.com%
            'referer': 'https://gannacademy.myschoolapp.com/app/student',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'wh-version': '2024.03.18.5',
            'x-requested-with': 'XMLHttpRequest',
        }

        #call getting pdf
        response = requests.get(URL, cookies=cookies_dict, headers=headers)

        # Save the PDF content to a file
        with open(first_semester_path, 'wb') as f:
            f.write(response.content)
        print("PDF saved successfully")
        socketio.emit('progress', {'message': "First Semester PDF Saved"}, namespace='/task')  


    if download_second_semester == True:
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="L_c1i0_cb3224_ct3224_ct4"]/select'))
        )
        dropdown.click()

        time.sleep(0.25)

        dropdown.send_keys(Keys.UP, Keys.UP, Keys.ENTER)
        socketio.emit('progress', {'message': "Switched to second semester"}, namespace='/task')
        
        generate_report = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Generate Report"))
        )
        time.sleep(0.25)
        generate_report.click()
        print("clicked generate report")
        socketio.emit('progress', {'message': "Generating Second Semester Report"}, namespace='/task')

        iframe = WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'trying-hard'))
        )

        time.sleep(2)

        while True:
            try:
                element = driver.find_element(By.XPATH, "/html/body")
                base_uri = element.get_property("baseURI")
                if "/api/Report/ReportJob/" in base_uri:
                    print(f"Found it! The baseURI is '{base_uri}'")
                    socketio.emit('progress', {'message': "Got Second Semseter PDF"}, namespace='/task')
                    URL = base_uri
                    # Perform additional actions here if needed
                    break
                else:
                    print(f"The baseURI is '{base_uri}'. Trying again...")
                    socketio.emit('progress', {'message': "Waiting for PDF to Load"}, namespace='/task')
                    time.sleep(2)  # Add a delay before checking again
            except (NoSuchElementException, StaleElementReferenceException):
                print("baseURI property not found or stale element. Trying again...")
                time.sleep(2)  # Add a delay before checking again

        # get cookies
        cookies = driver.get_cookies()

        # Convert the list of cookies to a dictionary
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            # Requests sorts cookies= alphabetically
            # 'cookie': 's=aLeezGIaZjN0w6/BmiS5Kghhb2r5QsO/Wk58eOWhWIs=; mp_b4726c21784ae6857d9c56cfb9866654_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18ab7c8443441e4-096b44babd3e47-19525634-13c680-18ab7c8443441e4%22%2C%22%24device_id%22%3A%20%2218ab7c8443441e4-096b44babd3e47-19525634-13c680-18ab7c8443441e4%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fgannacademy.myschoolapp.com%2Fapp%3FsvcId%3Dedu%26envId%3Dp-7kX8hIPgrkeeZXCVn1fL7w%26bb_id%3D1%22%2C%22%24initial_referring_domain%22%3A%20%22gannacademy.myschoolapp.com%
            'referer': 'https://gannacademy.myschoolapp.com/app/student',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'wh-version': '2024.03.18.5',
            'x-requested-with': 'XMLHttpRequest',
        }

        #call getting pdf
        response = requests.get(URL, cookies=cookies_dict, headers=headers)

        # Save the PDF content to a file
        with open(second_semester_path, 'wb') as f:
            f.write(response.content)
        print("PDF saved successfully")
        socketio.emit('progress', {'message': "PDF Saved"}, namespace='/task')
        
    #quit driver
    driver.quit

