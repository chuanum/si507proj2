#################################
##### Name: Chuan He    
##### Uniqname: chuanum
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import sys

def open_cache():
    '''opens the cache file if it exists, or creates one if it doesn't exist

    Parameters
    ----------
    None

    Returns
    -------
    cache file: dict
    '''
    try:
        filename = 'proj2_nps.json'
        file = open(filename,'r')
        contents = file.read()
        cache_dict = json.loads(contents)
        file.close()
    except:
        cache_dict = {}

    return cache_dict


cache = open_cache()





class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self,name,category,address,zipcode,phone):
        self.name = name
        self.category = category
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return str(self.name) + ' (' +str(self.category)+'): '+str(self.address)+' '+str(self.zipcode)

    def to_dic(self):
        return self.__dict__

    



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    url = 'https://www.nps.gov/index.htm'
    if cache.get('state_url'):
        print('Using cache')
        return cache['state_url']
    else:  
        page = requests.get(url)
        print('Fetching')
        soup = BeautifulSoup(page.content,'html.parser')
        search = soup.find_all(class_ = 'dropdown-menu SearchBar-keywordSearch')
        dic = {}
        for i in search[0].find_all('a'):
            dic[i.string.lower()] = "https://www.nps.gov"+i.get('href')
        cache['state_url'] = dic
        return dic

    

    
    
        

    
        
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    print('Fetching')
    page = requests.get(site_url)
    soup = BeautifulSoup(page.content,'html.parser')
    name = soup.find(class_ = 'Hero-title').string
    category = soup.find(class_ = 'Hero-designation').string
    city = soup.find(itemprop="addressLocality").string
    state = soup.find(itemprop="addressRegion").string
    address = city + ', ' + state
    zipcode = soup.find(class_='postal-code').string
    phone = soup.find(itemprop="telephone").string
    return NationalSite(name,category,address,zipcode.strip(),phone.replace('\n',''))


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    print('Fetching')
    page = requests.get(state_url)
    soup = BeautifulSoup(page.content,'html.parser')
    result = soup.find_all(class_='col-md-9 col-sm-9 col-xs-12 table-cell list_left')
    url_list = []
    for i in result:
        url_list.append('https://www.nps.gov'+i.find('a').get('href')+'index.htm')
    obj_list = []
    for url in url_list:
        obj = get_site_instance(url)
        obj_list.append(obj)

    return obj_list


    
    


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    params = {'key':secrets.API_KEY,'origin':site_object.zipcode,'radius':'10','maxMatches':'10','ambiguities' : 'ignore','outFormat' : 'json'}
    key = secrets.API_KEY
    origin = site_object.zipcode
    radius = 10
    maxMatches = 10
    ambiguities = 'ignore'
    outFormat = 'json'
    url = 'http://www.mapquestapi.com/search/v2/radius'
    print('Fetching')
    response = requests.get(url,params=params)
    dic = json.loads(response.text)
    return dic

def main():
    dic = build_state_url_dict()
    value = True
    while True:
        while value:
            state_name = input('''\nEnter a state name (e.g. Michigan, michigan) or 'exit': ''')
            if state_name == 'exit':
                sys.exit()
            elif state_name.lower() not in dic.keys():
                print('[Error] Enter proper state name\n')
            else:
                state_url = dic[state_name.lower()]
                break
        if value == True:
            print('----------------------------------')
            print('List of national sites in '+state_name)
            print('----------------------------------')
            if cache.get(state_name):
                for obj in cache[state_name]:
                    print('Using cache')
                obj_list = cache[state_name]
                number = 1
                for obj in obj_list:
                    info = '['+str(number)+'] '+obj.info()
                    number += 1
                    print(info)
            else:
                obj_list = get_sites_for_state(state_url)
                cache[state_name] = obj_list
                number = 1
                for obj in obj_list:
                    info = '['+str(number)+'] '+obj.info()
                    number += 1
                    print(info)
        while True:
            num = input('''\nChoose the number for detail search or 'exit' or 'back': ''')
            if num == 'exit':
                sys.exit()
            elif num == 'back':
                break
            try:
                x=int(num)-1
                obj = obj_list[x]
                break
            except:
                print('[Error] Invalid input\n\n----------------------------------')      
        if num == 'back':
            value = True
            continue
        print('----------------------------------')
        print('Places near '+obj.name)
        print('----------------------------------')
        if cache[state_name][x].__dict__.get('nearby'):
            print('Using cache')
            site_nearby = cache[state_name][x].__dict__['nearby']
            for i in range(len(site_nearby['searchResults'])):
                name = site_nearby['searchResults'][i]['name']
                category = site_nearby['searchResults'][i]['fields']['group_sic_code_name']
                if category == '':
                    category = 'no category'
                address = site_nearby['searchResults'][i]['fields']['address']
                if address == '':
                    address = 'no address'
                city = site_nearby['searchResults'][i]['fields']['city']
                if city == '':
                    city = 'no city'
                info = '- '+name+' ('+category+'): '+address+', '+city
                print(info)
        else:

            site_nearby = get_nearby_places(obj)
            cache[state_name][x].__dict__['nearby'] = site_nearby
            for i in range(len(site_nearby['searchResults'])):
                name = site_nearby['searchResults'][i]['name']
                category = site_nearby['searchResults'][i]['fields']['group_sic_code_name']
                if category == '':
                    category = 'no category'
                address = site_nearby['searchResults'][i]['fields']['address']
                if address == '':
                    address = 'no address'
                city = site_nearby['searchResults'][i]['fields']['city']
                if city == '':
                    city = 'no city'
                info = '- '+name+' ('+category+'): '+address+', '+city
                print(info)
        value = False

    

if __name__ == "__main__":
    
    main()