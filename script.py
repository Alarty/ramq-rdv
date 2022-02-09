import ast
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import json

import GDriveConnection
import utils

to_email = os.environ.get('mailto')

results_filename = 'ramq-results'
# Create the connection to Gdrive if needed (with json file or env var)
gdrive_conn = None
if "gdrive_results" in os.environ.keys():
    secret_name = "gdrive_client_secret"
    if os.path.isfile(f"{secret_name}.json"):
        gdrive_conn = GDriveConnection.GDriveConnection(json_filename=f"{secret_name}.json")
    elif secret_name in os.environ.keys():
        gdrive_conn = GDriveConnection.GDriveConnection(json_content=json.loads(os.environ.get('gdrive_client_secret')))
    else:
        raise Exception(
            f"You should have a {secret_name}.json file or the json content of it as 'gdrive_client_secret' envvar")

results_fileid = None
# Load old results json file locally or through Gdrive connection
if "gdrive_results" not in os.environ.keys():
    if os.path.isfile(f"{results_filename}.json"):
        with open(f"{results_filename}.json") as json_file:
            old_slots = json_file.read()
    else:
        old_slots = None
else:
    results_fileid, old_slots = gdrive_conn.get_byte_file(results_filename)
    if old_slots is not None:
        old_slots = ast.literal_eval(old_slots.decode('utf8'))
print(f"Content of the json file :{old_slots}")

url = 'https://outlook.office365.com/owa/calendar/RAMQ_Bureau_QC@azqmar.onmicrosoft.com/bookings/'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("window-size=1920x1480")
chrome_options.add_argument("disable-dev-shm-usage")
driver = webdriver.Chrome(
    chrome_options=chrome_options, executable_path=ChromeDriverManager().install()
)
driver.delete_all_cookies()

print(url)
driver.get(url)
time.sleep(15)
elem = driver.find_element(By.CLASS_NAME, 'right.top.serviceCard')
elem.click()
print(elem.get_attribute('innerHTML'))
time.sleep(15)

elem2 = driver.find_element(By.CLASS_NAME, 'datePicker')
slots_founds = elem2.get_attribute('innerHTML')

driver.quit()


slots_to_return = slots_founds

slots_to_return = json.dumps(slots_to_return)

print(f"New slots {slots_to_return}")
print(f"Old slots {old_slots}")
flag_new = utils.compare_results(slots_to_return, old_slots)
print('Flag new')
print(flag_new)
# save the new json file containing most recent slots locally or in Gdrive
if "gdrive_results" in os.environ.keys():
    gdrive_conn.save_byte_file(slots_to_return, results_fileid, results_filename)
    print(f"Results saved in gdrives")

else:
    with open(f"{results_filename}.json", "w") as json_file:
        json_file.write(str(slots_to_return))
    print(f"Results saved in {results_filename}.json")
slots_to_return = ast.literal_eval(slots_to_return)
print(len(slots_to_return))
# if slot wanted appears
if len(slots_to_return) != 0:
    # send mail if something new happened
    if flag_new:
        # if we pass a list (stringyfied), convert it to list again
        if '[' in to_email:
            to_email = ast.literal_eval(to_email)
        utils.send_mail(slots_to_return, url, to_email)
        print("Mail sent")
else:
    print("No changes occurs")
print("End on script")
