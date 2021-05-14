import shutil
import os, sys
import time
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from openpyxl import load_workbook, Workbook, formatting, styles, worksheet
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
from pandas import ExcelWriter
import numpy as np
from google.cloud import storage
import logging


print('Starting Process')
print('Checking if there are duplicated files in the folder...')
paths = []
for row in os.listdir('/home/ajimenez/ui-automation'):
    if 'r539cy' in row:
        paths.append('/home/ajimenez/ui-automation/'+row)
        
for path in paths:
    os.remove(path)
    print('Erasing duplicated file!')

out_path='/home/ajimenez/ui-automation'
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
prefs = {'download.default_directory' : out_path}
options.add_experimental_option('prefs', prefs)
# options.add_experimental_option('service_log_path':'/dev/null')
download_path = '/home/ajimenez/ui-automation'

driver = webdriver.Chrome('/home/ajimenez/.wdm/drivers/chromedriver/linux64/86.0.4240.22/chromedriver',options=options)
#driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
command_result = driver.execute("send_command", params)

#Following Code is for State Level

print('Opening Selenium Driver to fill automatically the form - State Level')

driver.get('https://oui.doleta.gov/unemploy/claims.asp')
print('This may take a while, please wait :)')
path = "UI_Weekly"

select_filter = []

#This element selects the option to download the file as an XML 

element1=driver.find_element_by_xpath(
            '//input[@id="xml"]')
element1.click()
print('Element1: '+str(element1))
#This element selects the option to choose the state option to enable the combobox that has all the states

element2=driver.find_element_by_xpath(
            '//input[@value="state"]')
element2.click()

element_strt = Select(driver.find_element_by_xpath(
            '//select[@name="strtdate"]'))

options_strt = element_strt.options

select_box = Select(driver.find_element_by_xpath("//select[@name='strtdate']"))
select_box.select_by_index(1) #2019 = 2, 2020 = 1

#For the combobox that has all the states, it selects the element that has that combobox with all the options
#then loop the options and select all the elements accordin to its index

element3=Select(driver.find_element_by_xpath(
        '//select[@id="states"]'))
options = element3.options

for ele_index in range(int(len(options))):
   
    select_box = Select(driver.find_element_by_xpath("//select[@id='states']"))
    select_box.select_by_index(ele_index)

    element = select_box.options[ele_index]

#This element is necessary to trigger the submit of the form to download the XML file 
    
element4=driver.find_element_by_xpath(
            '//input[@name="submit"]')
element4.click()

today = date.today()

print(element4)
time.sleep(10) #This time depends on the time spent to download the file and being moved to the other folder

driver.close()

print('Closing Selenium Driver - State Level')

#This creates the folder that will contain the report, if it's already created it will directly put the xml files in there
#else it will create the folder and then move the files

isDir = os.path.isdir(path)

if isDir:
    shutil.move("/home/ajimenez/ui-automation/r539cy.xml", "/home/ajimenez/ui-automation/UI_Weekly/Unemployment_Insurance_Weekly_Claims_State_"+str(today.year)+str(today.month)+str(today.day)+".xml")
    select_filter.append('State')
    print('Moving State XML to UI Directory\n')
else:
    os.mkdir(path)
    shutil.move("/home/ajimenez/ui-automation/r539cy.xml", "/home/ajimenez/ui-automation/UI_Weekly/Unemployment_Insurance_Weekly_Claims_State_"+str(today.year)+str(today.month)+str(today.day)+".xml")
    select_filter.append('State')
    print('Moving State XML to UI Directory\n')

print('Starting DataFrame Creation\n')

#This list of paths takes the name of the files to see wich one State to validate it later
paths_ui = []
for row in os.listdir('/home/ajimenez/ui-automation/UI_Weekly'):
    act_date = str(today.year)+str(today.month)+str(today.day)
    if act_date in row:
        paths_ui.append('/home/ajimenez/ui-automation/UI_Weekly/'+row)

#This is an array that will have dataframes inside 
df_list = []

#This is a loop that takes each XML file and gathers all the info to create a dataframe 
for path in paths_ui:
    for row in select_filter:
        if row in path:
            tree = ET.parse(path)
            root = tree.getroot()
            df = pd.DataFrame()
            
            for child in root:
                dict={}
                for element in child:
                    if element.text.strip():
                        dict[element.tag] = element.text
                    else:
                        for val in element:
                            dict[element.tag+'_'+val.tag] = val.text
                df = df.append(dict,ignore_index=True)
    
            l_df = list(df)
            l_df.sort(reverse=True)
            df = df[l_df]
            df_list.append(df)


print('Here is the df_list:')
print(df_list)
#This shows the list of dataframes to know the information that is stored and to see that
#it only has 2 dataframes

print('\n\nStarting Report Creation/Format')

#print(df_list)

#This notebook is in charge to write the information from the list of dataframes of DataFrame Creation notebook
#So it creates an xls file with the date of creation and then it attach each dataframe to a sheet of the file

book = Workbook()
writer = pd.ExcelWriter('/home/ajimenez/ui-automation/jobless claim weekly '+str(today.year)+str(today.month)+str(today.day)+".xlsx", engine='openpyxl')
writer.book = book
print('Creating jobless claim weekly File')
for data in df_list:
    print(data.columns)
    if 'stateName' in data.columns:
        print('This is working')
        data.to_excel(writer, 'State UI', header=True, index=False)
       	print('Creating State UI sheet')
       	print(data)
writer.save()

print('\n\nCreating CSV File...')
base = pd.read_excel('/home/ajimenez/ui-automation/jobless claim weekly '+str(today.year)+str(today.month)+str(today.day)+".xlsx", sheet_name='State UI')
base = base[['stateName','weekEnded','InitialClaims','ReflectingWeekEnded','ContinuedClaims','CoveredEmployment','InsuredUnemploymentRate']]
len(base.columns)

base = base.rename(columns = {'stateName':'State','weekEnded':'Filed week ended','InitialClaims':'Initial Claims','ReflectingWeekEnded': 'Reflecting Week Ended','ContinuedClaims':'Continued Claims','CoveredEmployment':'Covered Employment','InsuredUnemploymentRate':'Insured Unemployment Rate'}, inplace = False)
base.to_csv('/home/ajimenez/ui-automation/jobless claim weekly '+str(today.year)+str(today.month)+str(today.day)+".csv",index=False)
os.remove('/home/ajimenez/ui-automation/jobless claim weekly '+str(today.year)+str(today.month)+str(today.day)+".xlsx")
print('DONE CREATING CSV FILE\n\n')

print('\n\nUploading the report to the Bucket\n\n')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
upload_blob('unemployment-insurance-buck', '/home/ajimenez/ui-automation/jobless claim weekly '+str(today.year)+str(today.month)+str(today.day)+".csv","jobless claim weekly "+str(today.year)+str(today.month)+str(today.day)+".csv")
print('-------------------UPLOADED SUCCESFULLY TO BUCKET---------------------')

