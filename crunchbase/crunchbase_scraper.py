from selenium import webdriver
import random, time, json

# instance of the firefox webdriver. in case of too many pages, use sth like PhantomJS
driver = webdriver.Firefox()

def get_json_for_company(company_url):
    """ function to retrive information about a company from crunchbase"""
    company = {"Statistics":{}, "Overview" : {},
               "Company Details" : {}, "Recent Timeline Activity":{},
               "Funding Rounds":{}, "Investors":{}, "Board Members and Advisors": {},\
               "Current Team": {},"News": {},"Offices/Locations":{},\
               "Acquisitions": {}, "Products": {}, "Competitors": {}, "Partners": {},\
               "Event Appearances": {}, "Images": {}, "Videos": {}}

    time.sleep(random.randint(2,10))
    driver.get(company_url) ## open the url
    time.sleep(10)
    ## get statistics
    company['Statistics']['Number of followers'] = returnText(getElement('number_of_followers', 'class'))
    company['Statistics']["Number of visits"] = returnText(getElement('.badge.page_views', 'css'))

    ## overview
    company['Overview']["Funding Received"] = returnText(getElement('funding_rounds', 'id')).split('-')[1].strip()[1:]
    company['Overview']["Acquisitions"] = returnText(getElement('//*[@id="acquisitions"]/span', 'xpath'))
    company['Overview']["Most Recent Funding"] = returnText(getElement('.table.container', 'css').find_elements_by_css_selector('td')[1]).split('/')[0][1:].strip()
    company['Overview']["Headquarters"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/div[2]/dd[1]/a', 'xpath'))
    company['Overview']["Description"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/div[2]/dd[2]', 'xpath'))
    company['Overview']["Founders"] = []

    founder_elems = driver.find_element_by_xpath('//*[@id="info-card-overview-content"]/div/dl/div[2]/dd[3]').find_elements_by_css_selector('.link_container')
    for elem in founder_elems:
        person_dict = {}
        person_dict['name'] = elem.find_element_by_css_selector('a').get_attribute('data-name')
        person_dict['person_url'] = elem.find_element_by_css_selector('a').get_attribute('href')
        company['Overview']["Founders"].append(person_dict)

    ## categories
    category_elems = getElement('//*[@id="info-card-overview-content"]/div/dl/div[2]/dd[4]', 'xpath').find_elements_by_css_selector('a')
    company['Overview']['Categories'] = ''
    for cat in category_elems:
        company['Overview']['Categories'] += returnText(cat) + ","
    company['Overview']['Categories'] = company['Overview']['Categories'][:-1]
    company['Overview']["Website"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/div[2]/dd[5]/a', 'xpath'))
    company['Overview']["Social"] = {}
    company['Overview']["Social"]["twitter_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.twitter').get_attribute('href')
    company['Overview']["Social"]["linkedin_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.linkedin').get_attribute('href')
    company['Overview']["Social"]["facebook_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.facebook').get_attribute('href')


    ## Company Details
    company["Company Details"]["Founded"] = returnText(getElement('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[1]/div[2]/div[1]/dd[1]' ,'xpath'))
    company["Company Details"]["Contact"] = returnText(getElement('//*[@id="main-content"]/div[2]/div[2]/div[3]/div[1]/div[2]/div[1]/dd[2]/span' ,'xpath'))
    company["Company Details"]["Employees"] = returnText(getElement('//*[@id="main-content"]/div[2]/div[2]/div[4]/div[1]/div[2]/div[1]/dd[2]' ,'xpath')).split('|')[0]
    getElement('//*[@id="description"]/span/p/label', 'xpath').click()
    company["Company Details"]["_Description"] = (getElement('description-ellipsis', 'class')).text

    ## recent timeline activity
    company["Recent Timeline Activity"], company["Recent Timeline Activity"]['_number'] = {}, driver.find_elements_by_css_selector('.card-header')[3].text[26:-1]

    ## funding rounds
    company["Funding Rounds"], company["Funding Rounds"]['_number'] = {}, returnText(getElement('//*[@id="funding_rounds"]/span', 'xpath'))

    ## Investors
    company["Investors"], company["Investors"]['_number'] = {}, returnText(getElement('//*[@id="investors"]/span', 'xpath'))

    ## Board Members and Advisors
    company["Board Members and Advisors"], company["Board Members and Advisors"]['_number'] = {}, returnText(getElement('//*[@id="board_members_and_advisors"]/span', 'xpath'))

    ## Current Team
    company["Current Team"], company["Current Team"]['_number'] = {},returnText(getElement('//*[@id="current_team"]/span', 'xpath'))

    ## News
    company["News"], company["News"]['_number'] = {}, returnText(getElement('//*[@id="news"]/span', 'xpath'))

    ## Offices/Locations
    company["Offices/Locations"], company["Offices/Locations"]['_number'] = {}, returnText(getElement('//*[@id="offices_locations"]/span', 'xpath'))

    ## Acquisitions
    company["Acquisitions"], company["Acquisitions"]['_number'] = {}, returnText(getElement('//*[@id="acquisitions"]/span', 'xpath'))
                                                         
    ## Products
    company["Products"], company["Products"]['_number'] = {}, returnText(getElement('//*[@id="products"]/span', 'xpath'))

    ## Competitors
    company["Competitors"], company["Competitors"]['_number'] = {}, returnText(getElement('//*[@id="competitors"]/span', 'xpath')) 

    ## Partners
    company["Partners"], company["Partners"]['_number'] = {}, returnText(getElement('//*[@id="partners"]/span', 'xpath'))
                                                
    ## Event Appearances
    company["Event Appearances"], company["Event Appearances"]['_number'] = {}, returnText(getElement('//*[@id="event_appearances"]/span', 'xpath'))

    ## Images
    company["Images"], company["Images"]['_number'] = {}, returnText(getElement('//*[@id="images"]/span', 'xpath'))

    ## Videos
    company["Videos"], company["Videos"]['_number'] = {}, returnText(getElement('//*[@id="videos"]/span', 'xpath'))

    ## Investments
    company["Investments"], company["Investments"]['_number'] = {}, returnText(getElement('//*[@id="investments"]/span', 'xpath'))

    return json.dumps(company)

def get_json_for_person(person_url):
    """ function to retrive information about person from crunchbase.com"""
    person = {"Statistics":{}, "Overview" : {}, "Person Details" : {},
               "Education" : {}, "Recent Timeline Activity":{},
               "Jobs":{}, "Board & Advisor Roles":{}, "Investments": {},\
               "News": {},"Memberships":{},\
               "Event Appearances": {}, "Images": {}, "Awards": {}}

    time.sleep(random.randint(2,10))
    driver.get(person_url) ## open the url
    time.sleep(10)
    ## get statistics
    person['Statistics']['Number of followers'] = returnText(getElement('number_of_followers', 'class'))

    ## overview
    person['Overview']["Primary Role"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/div/dd[1]', 'xpath'))
    person['Overview']["Born"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/dd[1]', 'xpath'))
    person['Overview']["Gender"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/dd[2]', 'xpath'))
    person['Overview']["Location"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/dd[3]', 'xpath'))
    person['Overview']["Website"] = returnText(getElement('//*[@id="info-card-overview-content"]/div/dl/dd[4]', 'xpath'))
    person['Overview']["Social"] = {}
    try:
        person['Overview']["Social"]["twitter_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.twitter').get_attribute('href')
    except:
        person['Overview']["Social"]["twitter_url"] = None
    try:
        person['Overview']["Social"]["linkedin_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.linkedin').get_attribute('href')
    except:
        person['Overview']["Social"]["linkedin_url"] = None
    try:
        person['Overview']["Social"]["facebook_url"] = getElement('info-card-overview-content', 'id').find_element_by_css_selector('.icons.facebook').get_attribute('href')
    except:
        person['Overview']["Social"]["facebook_url"] = None

    ## Person Details    
    try:
        getElement('//*[@id="description"]/span/p/label', 'xpath').click()
    except:
        pass
        ## see more element not present
    person['Person Details'], person['Person Details']["_description"] = {}, returnText(getElement('description-ellipsis', 'class'))
    
    ## Education
    person["Education"]["Universities"] = []
    try:
        education_elems = getElement('//*[@id="main-content"]/div[2]/div[2]/div[3]/div[8]/div[2]', 'xpath').find_elements_by_css_selector('.link_container')
        for elem in education_elems:
            person["Education"]["Universities"].append(elem.text)
        person["Education"]["_number"] = returnText(getElement('//*[@id="education"]/span', 'xpath'))
    except:
        person["Education"]["Universities"].append(None)
        person["Education"]["_number"] = None)

    ## recent timeline activity
    try:
        person["Recent Timeline Activity"], person["Recent Timeline Activity"]['_number'] = {}, driver.find_elements_by_css_selector('.card-header')[3].text[26:-1]
    except:
        person["Recent Timeline Activity"], person["Recent Timeline Activity"]['_number'] = {}, None

    ## Jobs
    person["Jobs"], person["Jobs"]['_number'] = {}, returnText(getElement('//*[@id="jobs"]/span', 'xpath'))

    ## Board & Advisor Roles
    person["Board & Advisor Roles"], person["Board & Advisor Roles"]['_number'] = {}, returnText(getElement('//*[@id="board_&_advisor_roles"]/span', 'xpath'))
    
    ## Investments
    person["Investments"], person["Investments"]['_number']= {}, returnText(getElement('//*[@id="investments"]/span', 'xpath'))

    ## News
    person["News"], person["News"]['_number']= {}, returnText(getElement('//*[@id="news"]/span', 'xpath'))

    ## Memberships
    person["Memberships"], person["Memberships"]['_number'] = {}, returnText(getElement('//*[@id="memberships"]/span', 'xpath'))

    ## Event Appearances
    person["Event Appearances"], person["Event Appearances"]['_number'] = {}, returnText(getElement('//*[@id="event_appearances"]/span', 'xpath')) 

    ## Images
    person["Images"], person["Images"]['_number'] = {}, returnText(getElement('//*[@id="images"]/span', 'xpath'))

    ## Awards
    person["Awards"], person["Awards"]['_number'] = {}, returnText(getElement('//*[@id="awards"]/span', 'xpath'))

    return json.dumps(person)

def getElement(element, method):
    try:
        if method == 'class':
            return driver.find_element_by_class_name(element)
        elif method == 'css':
            return driver.find_element_by_css_selector(element)
        elif method == 'xpath':
            return driver.find_element_by_xpath(element)
        elif method == 'id':
            return driver.find_element_by_id(element)
    except:
        return None
    
def returnText(elem):    
    try:
        if str(elem.text.strip().replace(')','').replace('(','')):
            return str(elem.text.strip().replace(')','').replace('(',''))
        else:
            return None
    except:
        return None
    
company_url = 'https://www.crunchbase.com/organization/facebook#/entity'
#company_url = 'https://www.crunchbase.com/organization/airbnb#/entity'
person_url= 'https://www.crunchbase.com/person/mark-zuckerberg#/entity'
person_url = 'https://www.crunchbase.com/person/mariya-gracheva#/entity'
#print get_json_for_company(company_url), '\n\n'
print get_json_for_person(person_url)
