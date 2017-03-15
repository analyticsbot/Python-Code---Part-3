# import all required modules
from selenium import webdriver
import time, re, hashlib, csv
import pandas as pd
from selenium.webdriver.common.keys import Keys
import usaddress
import logging, datetime, sys
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.ERROR)

username = ''
salutation = '' #Mr. Miss
client_name = ''
client_address = ''
billing_card_number = ''
card_cvv_number = ''
billing_address = ''
billing_expiry_date = ''

# log file initialize
logging.basicConfig(level=logging.DEBUG, 
                    filename='logfile_' + username+'.log', # log to this file
                    format='%(asctime)s -- %(message)s') # include timestamp
headers = ['Date' , 'Client_Name', 'State', 'County', 'searchterm', 'recordyear', 'last_document_type', \
           'last_document_left', 'right_side_name', 'right_side_address', 'right_side_date', 'Doctypes', 'Record_Count', 'last data record found', \
           'parsed_rows', 'client_name', 'client_address', 'billing_card_number', 'card_cvv_number', 'billing_address', 'billing_expiry_date']

ignore_keywords = ['escrow', 'law', 'associates', 'law', 'service', 'recorder', 'recorders', '$' , 'iiii', 'service', 'closing', 'title']
##ignore_keywords = ['law', 'service']
logging.info("Sentences will following keywords will be ignored -- " + ', '.join(ignore_keywords))
try:
    writer = pd.ExcelWriter('client_log_'+ username +'.xlsx')
    df_data = pd.read_excel('client_log_'+ username +'.xlsx','Sheet1')
    print("Opened the client log file. Read the contents into a dataframe!")
    #change these 
    stop_last_document_left = df_data.iloc[df_data.shape[0]-1]['last_document_left']
    stop_right_side_name = df_data.iloc[df_data.shape[0]-1]['right_side_name']
    stop_right_side_address = df_data.iloc[df_data.shape[0]-1]['right_side_address']
    stop_right_side_date = df_data.iloc[df_data.shape[0]-1]['right_side_date']
except:
    writer = pd.ExcelWriter('client_log_'+ username +'.xlsx', engine='xlsxwriter')
    df_data = pd.DataFrame(columns=headers)
    #change these 
    stop_last_document_left = ''
    stop_right_side_name = ''
    stop_right_side_address = ''
    stop_right_side_date = ''

# static variables
url_login = 'https://web.datatree.com/Account/Login?ReturnUrl=%2f'
pwd = ''
state = 'CA'
county = 'SAN DIEGO'
keyword = '"mail to"'
input_file_name = ''
output_file_name = 'dataoutput_' + username + '.csv'
last_document_type = ''
text_box_left_parsed = ''
last_document_left = ''
right_side_name = ''
right_side_address = ''
right_side_date = ''

MAX_PAGES_SCRAPE = 'ALL'

DOCUMENT_TYPE_LEFT_ALLOWED = ['AFFIDAVIT OF DEATH']

logging.info("Process started for " + salutation  + ' ' +client_name + ', address = '+ client_address)
logging.info("Billing details, billing_card_number = " + billing_card_number  + ', card_cvv_number: ' +card_cvv_number + \
             ', billing_address = '+ billing_address + ', billing_expiry_date = ' + billing_expiry_date)

try:
    df_past = pd.read_csv(input_file_name)
    logging.info("Successfully read last file : " + input_file_name)
except:
    df_past = False
    logging.error("Cannot read last file : " + input_file_name)

doc_types = ['AFFIDAVIT OF DEATH']
"""
POSSIBLE VALUES
['UNDETERMINED', 'DEED', 'DEED OF TRUST', 'RELEASE', 'AFFIDAVIT OF DEATH', 'ABSTRACT OF JUDGMENT', 'FEDERAL LIEN', 'SUBSTITUTION', 'NOTICE OF DEFAULT', 'LIEN', 'NOTICE', 'AFFIDAVIT OF DEATH', 'TRUST', 'ORDER', 'POWER OF ATTORNEY', 'ASSESSMENT LIEN', 'STATE LIEN', 'RESCISSION', 'ASSIGNMENT', 'SUBSTITUTION & RELEASE', 'RESTRICTIONS', 'FINANCING STATEMENT', 'AGREEMENT', 'EASEMENT', 'SUBORDINATION', 'AFFIDAVIT', 'CERTIFICATE', 'MORTGAGE', 'MODIFICATION', 'ACKNOWLEDGEMENT', 'PARTIAL RELEASE', 'LIS PENDENS', 'BUSINESS', 'JUDGMENT', 'DECLARATION', 'SURVEY', 'SATISFACTION', 'MECHANICS LIEN', 'ASSIGNMENT OF RENTS', 'REQUEST', 'RIDER', 'SALE', 'CONDOMINIUM', 'NOTE', 'MINERAL/MINING CLAIM', 'HOMESTEAD', 'BOND', 'LICENSE', 'WITHDRAWAL', 'SUBSTITUTION & PARTIAL', 'REVOCATION', 'PROBATE', 'NOTICE OF TRUSTEES SALE', 'DEATH CERTIFICATE', 'BANKRUPTCY', 'CONTRACT', 'ANNEXATION', 'AMENDMENT', 'OPTION', 'MORTGAGE/DEED OF TRUST', 'MEMORANDUM', 'INDENTURE', 'FORECLOSURE', 'CIVIL ACTION', 'APPLICATION', 'TERMINATION', 'RESOLUTION', 'PETITION', 'PARTIAL ASSIGNMENT', 'CANCELLATION', 'ABANDONMENT']
"""

years = ['2015']
"""POSSIBLE VALUES
['2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000']
"""

logging.info("Starting the process. Variables are state = " + state + ", county = " + county + ",keyword = " + keyword + \
             ", document types selected are " + '; '.join(doc_types) + ", for year(s)" + '; '.join(years))

# initialize pandas
df = pd.DataFrame(columns = ['date', 'text_box_left','DOCUMENT_TYPE_LEFT', 'DOCUMENT_TYPE_RIGHT', 'RECORDING_DATE', 'APN', \
                             'ADDRESS', 'address_number_right', 'streetName_right', 'PlaceName_right', 'StateName_right',
                             'ZipCode_right','OWNER_BORROWER','SELLER_LENDER', 'text',\
                             'parsed_name_address', 'parsed_name', 'parsed_address',\
                             'address_number', 'streetName','StreetNamePostType', 'PlaceName', 'StateName',\
                             'ZipCode','StreetNamePostType', 'StreetNamePreDirectional', 'hash_value', 'is_parsed'])

# initialize pandas
df_bad = pd.DataFrame(columns = ['date', 'text_box_left','DOCUMENT_TYPE_LEFT', 'DOCUMENT_TYPE_RIGHT', 'RECORDING_DATE', 'APN', \
                             'ADDRESS', 'address_number_right', 'streetName_right', 'PlaceName_right', 'StateName_right',
                             'ZipCode_right','OWNER_BORROWER','SELLER_LENDER', 'text',\
                             'parsed_name_address', 'parsed_name', 'parsed_address',\
                             'address_number', 'streetName','StreetNamePostType', 'PlaceName', 'StateName',\
                             'ZipCode','StreetNamePostType', 'StreetNamePreDirectional', 'hash_value', 'is_parsed'])

# start the firefox instance
driver = webdriver.Firefox()
#driver = webdriver.Chrome('chromedriver.exe')
driver.maximize_window()
driver.get(url_login)

# username handling on the website
username_elem = driver.find_element_by_id('UserName')
username_elem.send_keys(username)

# password handling
pwd_elem = driver.find_element_by_id('Password')
pwd_elem.send_keys(pwd)

# press enter to login
pwd_elem.submit()

logging.info("Successfully logged into account : " + username)

# waiting for 5 second before proceeding
time.sleep(5)
flexi_search_url = 'https://web.datatree.com/flexsearch'
driver.get(flexi_search_url)

# waiting for 5 second before proceeding
time.sleep(5)

time.sleep(300)
##driver.find_element_by_xpath('//*[@id="body"]/div[7]/div/div').click()
##time.sleep(15)
logging.info("Starting parsing data")
count = 0
post_count = 0
stop_post_count = 0
doc_count = 0
hash_value = [1,2,3]
cur_date = str(datetime.datetime.now().strftime ("%Y-%m-%d"))
text_box_left = ''
continue_ = True
while continue_:
    if count == 0:
        count +=1
        doc_count = driver.find_element_by_css_selector('.doc-count.ng-binding').text
        logging.info("Total document available -- " + str(doc_count))
        logging.info("Parsing page 1")
    else:
        next_ = driver.find_element_by_link_text('Next')
        next_.click()
        logging.info("Parsing page "+  str(count+1))
        count +=1
        if hash_value[-1] == hash_value[-2]:
            logging.info("No next page exists. Exiting")
            break
    if MAX_PAGES_SCRAPE !='ALL':
        if count> MAX_PAGES_SCRAPE:
            continue_ = False
    try:        
        time.sleep(10)
        results =  driver.find_elements_by_id('flexSearchResults')
        time.sleep(10)
        try:
            driver.execute_script("return arguments[0].scrollIntoView();", results[0])
        except:
            pass
        time.sleep(10)
        for result in results:
            post_count +=1
            #if (results.index(result)+1) %2 == 0:
            driver.execute_script("return arguments[0].scrollIntoView();", result)
            time.sleep(1)
            try:
                text_box_left = result.find_element_by_css_selector('.col-md-10.flexsearch-highlights').text
            except:
                text_box_left = 'NA'
            try:
                DOCUMENT_TYPE_LEFT = result.find_element_by_css_selector('.doc-title-textdecoration').get_attribute('title')
                last_document_type = DOCUMENT_TYPE_LEFT.title()
            except:
                DOCUMENT_TYPE_LEFT = 'NA'
##ALLEN..........................................................................
##            if DOCUMENT_TYPE_LEFT not in DOCUMENT_TYPE_LEFT_ALLOWED:
##                continue
##ALLEN....................................
            
            if results.index(result) == len(results)-1:
                hash_value.append(hashlib.md5(text_box_left).hexdigest())
            try:
                x = result.find_elements_by_css_selector('.doc-data-style.ng-binding')
            except:
                pass
            try:
                DOCUMENT_TYPE_RIGHT = x[0].text.title()
            except:
                DOCUMENT_TYPE_RIGHT = 'NA'
            try:
                RECORDING_DATE = x[2].text
            except:
                RECORDING_DATE = 'NA'
            try:
                APN = x[3].text
            except:
                APN = 'NA'
            try:
                ADDRESS = x[4].text.title()
                parse_address = usaddress.parse(ADDRESS)
                parse_address_dict = {}
                for i in parse_address:
                    if i[1] not in parse_address_dict.keys():
                            parse_address_dict[i[1]] = i[0]
                    else:
                            parse_address_dict[i[1]] += ' '+ i[0]
        

                try:
                    address_number_right = str(parse_address_dict['AddressNumber']).title()
                except:
                    address_number_right = 'NA'
                try:
                    streetName_right = str(parse_address_dict['StreetName']).title()
                except:
                    streetName_right = 'NA'
                    
                    


                    
                try:
                    PlaceName_right = str(parse_address_dict['PlaceName']).title()
                except:
                    PlaceName_right = 'NA'
                try:
                    StateName_right = str(parse_address_dict['StateName']).upper()
                except:
                    StateName_right = 'NA'
                try:
                    ZipCode_right = parse_address_dict['ZipCode']
                except:
                    ZipCode_right = 'NA'                
            except:
                ADDRESS = 'NA'
                address_number_right = streetName_right = PlaceName_right = StateName_right = ZipCode_right = 'NA'
            try:
                OWNER_BORROWER = ' '.join(x[5].text.title().split()[::-1])
                OWNER_BORROWER = OWNER_BORROWER.split()
                OWNER_BORROWER = ' '.join([i for i in OWNER_BORROWER if len(i)>1])
            except:
                OWNER_BORROWER = 'NA'
            try:
                SELLER_LENDER = ' '.join(x[6].text.title().split()[::-1])
                SELLER_LENDER = SELLER_LENDER.split()
                SELLER_LENDER = ' '.join([i for i in SELLER_LENDER if len(i)>1])
            except:
                SELLER_LENDER = 'NA'

            try:
                try:
                    data_from_left = text_box_left.lower().split(keyword.replace('"',''))[1]
                    hash_left_data = hashlib.md5(text_box_left).hexdigest()
                    if df_past:
                        if df_past.query('hash_value == "' + hash_left_data + '"').shape[0] == 0:
                            logging.info("Found existing record. Exiting")
                            df.to_csv(output_file_name, index = False)
                            logging.info("Output written to file : ", output_file_name)
                            sys.exit(1)
                except Exception,e:
                    #print str(e), '\n'
                    data_from_left = 'NA'

                if data_from_left == 'NA':
                    continue
                
                name_address = re.findall(r'\s([a-z][a-z]+.*?)$', data_from_left)[0]
                name_address = re.findall(r'(\w\w.*?\s\w\w\.?\s*\d\d\d\d\d)', name_address)[0]
                
                name_address_split = name_address.split()
                b = 0
                for i in name_address_split:
                    b+=1
                    try:
                        i = int(i)
                        isinstance(i, int)
                        break
                    except Exception,e:
                        #print 'aaa', str(e)
                        pass
                name = ' '.join(name_address_split[:b-1]).title()
                name = name.split()
                name = ' '.join([i for i in name if len(i)>1])
                address = ' '.join(name_address_split[b-1:]).title()
                parse_address = usaddress.parse(address)
                parse_address_dict = {}
                for i in parse_address:
                    if i[1] not in parse_address_dict.keys():
                            parse_address_dict[i[1]] = i[0]
                    else:
                            parse_address_dict[i[1]] += ' '+ i[0]
                try:
                    address_number = str(parse_address_dict['AddressNumber']).title()
##                    name = OWNER_BORROWER
##                    address_number = address_number_right  
                except:
                    address_number = 'NA'
                try:
                    streetName = str(parse_address_dict['StreetName']).title()
##                    streetName = streetName_right
                except:
                    streetName = 'NA'
                try:
                    StreetNamePostType = str(parse_address_dict['StreetNamePostType']).title()
                except:
                    StreetNamePostType = 'NA'
                try:
                    PlaceName = str(parse_address_dict['PlaceName']).title()
##                    PlaceName = PlaceName_right
                except:
                    PlaceName = 'NA'
                try:
                    StateName = str(parse_address_dict['StateName']).upper()
##                    StateName = StateName_right
                except:
                    StateName = 'NA'
                try:
                    ZipCode = parse_address_dict['ZipCode']
##                    ZipCode = ZipCode_right
                except:
                    ZipCode = 'NA'
                try:
                    StreetNamePostType = str(parse_address_dict['StreetNamePostType']).title()
                except:
                    StreetNamePostType = 'NA'
                try:
                    StreetNamePreDirectional = str(parse_address_dict['StreetNamePreDirectional']).title()
                except:
                    StreetNamePreDirectional = 'NA'
                is_parsed = 1

                if not any(word in text_box_left.lower() for word in ignore_keywords):
                    if ((OWNER_BORROWER.strip() not in ['NA','']) or (ADDRESS.strip() not in ['NA',''])):
                        if (streetName=='NA') and (PlaceName=='NA') and (StateName=='NA') and (ZipCode=='NA'):
                            name = OWNER_BORROWER
                            streetName = streetName_right
                            PlaceName = PlaceName_right
                            StateName = StateName_right
                            ZipCode = ZipCode_right
                            df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                                  ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                                  address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                             ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]
                        else:                           
##allen                              

##                           address_number = address_number_right
##                           streetName = streetName_right
##                           PlaceName = PlaceName_right
##                           StateName = StateName_right
##                           ZipCode = ZipCode_right
##???                    name_address, name, address
##                              If ADDRESS not in ('NA', '  '):
##                                 continue
##                            df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
##                                  ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
##                                  address_number, streetName, StreetNamePostType, PlaceName, StateName,\
##                                  ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]
##                          else: 
##allen address
##                            If address not in ['NA', '  ']:
##                                 continue                            
                            name = OWNER_BORROWER
                            df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                                  ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                                  address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                             ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]
                        
                        logging.info("Record number - " + str(post_count) + "; Right hand name and address present. Parsed full address -- " + address \
                                      + '; streetName = ' + streetName + '; PlaceName = '+ PlaceName + '; StateName = ' + StateName\
                                      + '; ZipCode = ' + ZipCode + '\n and hash value -- ' + hash_left_data)

                        if stop_post_count == 0:
                            last_document_left = DOCUMENT_TYPE_LEFT
                            right_side_name = OWNER_BORROWER
                            right_side_address = ADDRESS
                            right_side_date = RECORDING_DATE
                            stop_post_count+=1


                        if ((stop_last_document_left.lower().strip() == last_document_left.lower().strip()) and (stop_right_side_name.lower().strip() == right_side_name.lower().strip()) and\
                           (stop_right_side_address.lower().strip() == right_side_address.lower().strip()) and (stop_right_side_date.lower().strip() == right_side_date.lower().strip())):
                            logging.info("Record number - " + str(post_count) + "; Right hand name, address, document type match found. Stopping --; last_document_left "\
                                          + last_document_left + '; right_side_name = ' + right_side_name + '; right_side_address = '+ right_side_address + '\n and hash value -- ' + hash_left_data)
                            continue_ = False
                            break
                        
                    else:                     
                        if (streetName!='NA') and (PlaceName!='NA') and (StateName!='NA') and (ZipCode!='NA') and (address_number !='NA'):
                            text_box_left_parsed = text_box_left
                            name = OWNER_BORROWER
##allen address
##                              If ADDRESS not in 'NA', '  ':
##                                 continue                                 
                            df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                                      ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                                      address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                                 ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]
                            
                            logging.info("Record number - " + str(post_count) + "; Right hand name addres not present but Parsed the full address -- " + address \
                                          + '; streetName = ' + streetName + '; PlaceName = '+ PlaceName + '; StateName = ' + StateName\
                                          + '; ZipCode = ' + ZipCode + '\n and hash value -- ' + hash_left_data)
                        else:
                         
                            df_bad.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                                      ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                                      address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                                 ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]

                            logging.error("Record number - " + str(post_count) + "; NA present in either of streetname, placename, statename, zipcode or address number -- " + address \
                                          + '; streetName = ' + streetName + '; PlaceName = '+ PlaceName + '; StateName = ' + StateName\
                                          + '; ZipCode = ' + ZipCode + '\n and hash value -- ' + hash_left_data)                    
                

                else:
     
                    logging.info("Record number - " + str(post_count) + "; Not parsing. Either of ignore keywords in the left hand side text -- " + data_from_left + '\n and hash value -- ' + \
                                 hash_left_data)
                    df_bad.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                                  ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                                  address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                             ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]                    
                    
            except Exception,e:
                #print '111', str(e)
                logging.error("Record number - " + str(post_count) + "; Cant parse data for left hand side text -- " + data_from_left + '\n and hash value -- ' + \
                             hash_left_data)
                is_parsed = 0
                name = 'NA'
                name_address = 'NA'
                address = 'NA'
                streetName='NA'
                StreetNamePostType='NA'
                PlaceName='NA'
                StateName='NA'
                ZipCode='NA'
                StreetNamePostType='NA'
                StreetNamePreDirectional='NA'
                address_number = 'NA'
                try:
                    data_from_left = text_box_left.lower().split(keyword.replace('"',''))[1]
                    hash_left_data = hashlib.md5(text_box_left).hexdigest()
                except Exception,e:
                    #print str(e), '\n'
                    data_from_left = 'NA'
                    hash_left_data = hashlib.md5(text_box_left).hexdigest()

                if ((OWNER_BORROWER.strip() not in ['NA','']) or (ADDRESS.strip() not in ['NA',''])):
                    last_document_left = DOCUMENT_TYPE_LEFT
                    right_side_name = OWNER_BORROWER
                    right_side_address = ADDRESS
                    right_side_date = RECORDING_DATE
                    if (streetName=='NA') and (PlaceName=='NA') and (StateName=='NA') and (ZipCode=='NA'):
                        name = OWNER_BORROWER
                        address_number = address_number_right
                        streetName = streetName_right
                        PlaceName = PlaceName_right
                        StateName = StateName_right
                        ZipCode = ZipCode_right
##allen address
##                              If ADDRESS not in 'NA', '  ':
##                                 continue                             
                        df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                              ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                              address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                         ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]
                    
                        logging.info("Record number - " + str(post_count) + "; Right hand name and address present. Parsed full address -- " + address \
                                  + '; streetName = ' + streetName + '; PlaceName = '+ PlaceName + '; StateName = ' + StateName\
                                  + '; ZipCode = ' + ZipCode + '\n and hash value -- ' + hash_left_data)
                        
                    else:
##allen address
##                              If ADDRESS not in 'NA', '  ':
##                                 continue                             
                        name = OWNER_BORROWER
                        df.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                              ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                              address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                         ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]


                        if ((stop_last_document_left.lower().strip() == last_document_left.lower().strip()) and (stop_right_side_name.lower().strip() == right_side_name.lower().strip()) and\
                           (stop_right_side_address.lower().strip() == right_side_address.lower().strip()) and (stop_right_side_date.lower().strip() == right_side_date.lower().strip())):
                            logging.info("Record number - " + str(post_count) + "; Right hand name, address, document type match found. Stopping --; last_document_left "\
                                          + last_document_left + '; right_side_name = ' + right_side_name + '; right_side_address = '+ right_side_address + '\n and hash value -- ' + hash_left_data)
                            continue_ = False
                else:
                    df_bad.loc[post_count] = [cur_date, text_box_left, DOCUMENT_TYPE_LEFT, DOCUMENT_TYPE_RIGHT, RECORDING_DATE, APN, \
                              ADDRESS, address_number_right, streetName_right, PlaceName_right, StateName_right, ZipCode_right, OWNER_BORROWER, SELLER_LENDER, data_from_left, name_address, name, address,\
                              address_number, streetName, StreetNamePostType, PlaceName, StateName,\
                         ZipCode, StreetNamePostType, StreetNamePreDirectional, hash_left_data, is_parsed]

                
                
    except Exception,e:
        #print '222', str(e)
        pass
        
nrow = df_data.shape[0]
parsed_rows_total = sum(list(df['is_parsed']))
df_data.loc[nrow+1] = [str(datetime.datetime.now()), username, state, county, keyword, ', '.join(years),\
                       last_document_type, last_document_left, right_side_name, right_side_address,\
                       right_side_date , ','.join(doc_types), doc_count, text_box_left_parsed,\
                       parsed_rows_total,client_name, client_address, billing_card_number, \
                       card_cvv_number, billing_address, billing_expiry_date]
df_data.to_excel(writer,'Sheet1', index = False, header = headers)
writer.save()
logging.info("Client log file generated as excel")
logging.info("Total number of rows parsed successfully :: " + str(parsed_rows_total))
driver.close()
logging.info("Total pages scraped : " + str(count))
logging.info("Total records scraped : " +  str(df.shape[0]))
df.to_csv(output_file_name[:-4]+'_testing.csv', index = True)
new_df = df[['OWNER_BORROWER','ADDRESS','address_number_right', 'streetName_right', 'PlaceName_right', 'StateName_right',
                             'ZipCode_right','parsed_name', 'parsed_address', 'address_number', 'streetName','StreetNamePostType', 'PlaceName', 'StateName',\
                             'ZipCode', 'DOCUMENT_TYPE_LEFT']]
new_df.to_csv(output_file_name, index = False)
logging.info("Output written to file : " + output_file_name)
df_bad.to_csv(output_file_name[:-4] + '_bad_data.csv', index = True)
logging.info("Bad Output written to file : " + output_file_name[:-4] + '_bad_data.csv')
logging.shutdown()
