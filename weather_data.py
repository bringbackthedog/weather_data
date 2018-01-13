from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import glob
import os
import pandas as pd
import re


def weather_data(years,months = ['January','February','March','April','May','June','July','August',
                                 'September','October','November','December'],province= 'Quebec'):

    '''
    :param years: (iterable)
        should be a range (between 1840 - 2018)
        ie: range(1998-1999) <- for year 1998
        OR list of strings ie: ['1998','1999']

    :param months: Default is every month
        Should be list of strings   ie: ['February'] OR ['August','September','October']
                
    :param province: should be string of province name
        ie: 'Quebec'
        
    '''


    #This block defines the vars to be used later (has to be global since we want df to be avail outside of function)
    
    global df
    global dict

    dict = {'dates': []}
    df = pd.DataFrame(columns=['Tm', 'D', 'Tx', 'Tn', 'S', 'S%N', 'P', 'P%N'])




    # launching chrome webdriver
    chrome_path = r"C:\Users\Utilisateur\Documents\Python\WinPython-64bit-3.5.4.0Qt5\chromedriver.exe"
       
    #setting chrome webdriver download directory - this should be the same directory as script 
    chrome_options = webdriver.ChromeOptions()
      # dir where files should be d/l'd to
    prefs = {'download.default_directory': 'C:/Users/Utilisateur/Documents/Python/Python Projects/weather'} 
    chrome_options.add_experimental_option('prefs', prefs)

    #actual launch of browser
    driver = webdriver.Chrome(chrome_path, chrome_options=chrome_options)

    # website to crawl
    url = "http://climate.weather.gc.ca/prods_servs/cdn_climate_summary_e.html"

    # go to website
    driver.get(url)

    ###############################
    #
    # ###   Skipping for now   ###
    #
    # years = range(1998, 1999)
    #
    # months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
    #           'November', 'December']
    #
    # province = 'Quebec'
    #
    ###############################

    # loop to d/l all CSVs

    for year in years:

        for month in months:
            yearElement = Select(driver.find_element_by_xpath('''//*[@id="intYear"]'''))
            yearElement.select_by_visible_text(str(year).capitalize())

            monthElement = Select(driver.find_element_by_xpath('''//*[@id="intMonth"]'''))
            monthElement.select_by_visible_text(month)

            provinceElement = Select(driver.find_element_by_xpath('''//*[@id="prov"]'''))
            provinceElement.select_by_visible_text(province.capitalize())

            # click CSV format
            driver.find_element_by_xpath('''//*[@id="frmSummary"]/label[1]''').click()

            # download csv to directory
            driver.find_element_by_xpath('''//*[@id="frmSummary"]/input''').click()

            #wait for download
            time.sleep(3)
            
                   


            #find CSV files in dir
            list_of_files = glob.glob('*.csv')  
            
            #latest d/l'd file: file
            file = max(list_of_files, key=os.path.getctime)
            
            #print status:  downloaded file
            print('Successfully downloaded ' + file + '\n')
            
            #This block creates dates Dict which will create the index of the final df
            #date is extracted from filename (file format: "eng-climate-summaries-Quebec-1,1995")
            date = re.compile('\d+').findall(file)
            date = date[0] + '-' + date[1]
            dict['dates'].append(date)


            with open(file, 'r'):
                data = pd.read_csv(file, skiprows=31,
                                   usecols=['Stn_Name', 'Tm', 'D', 'Tx',
                                            'Tn', 'S', 'S%N', 'P', 'P%N'],
                                   index_col=0)

                # this adds the latest value in dict as a row name (index)
                # extracts the desired columns in this file as pandas series with .loc method
                # puts them in an unamed dict using .to_dict() method
                # finally adds it to the row we just created
                df.loc[dict['dates'][-1]] = data.loc["MONTREAL/ST-HUBERT A",
                                                     ['Tm', 'D', 'Tx', 'Tn', 'S', 'S%N', 'P', 'P%N']].to_dict()

                      
            # This block should delete the file after the info is extracted from it
            ###os.remove(file)  #COMMENT OUT IF YOU WANT TO KEEP THE FILE
           
          
            #print status (end with space for next loop readibility): 
            print('Data successfully extracted! \n')
            print('Deleted file from local directory')
            print('\n'*3)
            
            
            # wait 1 second between each loop
            ###time.sleep(1)  #necessary?

    # close brower
    driver.close()

    # rename cols 
    df = df.rename(columns={'Tm': 'AvgTemp', 'D': 'DiffFromNormal', 'Tx': 'MaxTemp',
                            'Tn': 'MinTemp', 'S': 'Snowfall_cm', 'S%N': 'PCTofNormalSnow',
                            'P': 'TotalPrecipitation_mm',
                            'P%N': 'PctOfNormalPrecipitation'})
    


