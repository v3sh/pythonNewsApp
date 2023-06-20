import requests # Library install required
from datetime import datetime,timezone
from gdacs.api import GDACSAPIReader # Library Install required
from common_methods import progress_bar as pb

def reliefweb_api_calls():
    # ... your existing code ...
     # Send a GET request to the API endpoint
    #response = requests.get('https://api.reliefweb.int/v1/disasters')
    #response = requests.get('https://api.reliefweb.int/v1/disasters?appname=apidoc&limit=3&preset=latest&fields[include][]=url')

    # Send a POST request to the API endpoint
    url_api = 'https://api.reliefweb.int/v1/disasters?appname=news_agg'
    payload = {
          "limit": 8,
          "preset": "latest",
          "fields": {
                      "include": ["url","country","type.name","date","status","id"]
                    }     
    }
    
    response= requests.post(url_api,json = payload) 
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
    else:
        print("Error occurred while retrieving data from the API.")
        
    listOfData = [] ;
    bar = pb(len(data))
    count = 1;
    # Insert data into PostgreSQL table
    for disaster in data['data']:
        count=count+1
        dis_id = str(disaster['fields']['id'])
        dis_name = disaster['fields']['name']
        dis_source_url = disaster['fields']['url']
        
        disaster_type = disaster['fields']['type']
        
        
        dis_date = disaster['fields']['date']['event']
        print(f"The dis_date in relief Web :- {dis_date,type(dis_date)}")
        dis_status = disaster['fields']['status']
        # To list the affected countries as a List rather than set of values in a Dictionary
        country = disaster['fields']['country']
        dis_country = [values['name'] for values in country]
        dis_category = set()
        for classifier in dis_country:
            if classifier == 'Canada':
                dis_category.add('Domestic')
            else:
                dis_category.add('International')
        
        # Convert dis_date to a datetime object
        dis_date_obj = datetime.strptime(dis_date, '%Y-%m-%dT%H:%M:%S%z')
        current_date = datetime.now(timezone.utc)
        print(current_date)
        # Calculate the difference between dis_date_obj and dis_date
        time_diff = current_date - dis_date_obj
        print(f"Time Difference:- {time_diff}\n{dis_date_obj}\n{current_date}")

        # Check the time difference and assign dis_status accordingly
        if time_diff.days <= 1:
            dis_status = "Alert"
        elif 2 <= time_diff.days <= 4:
            dis_status = "Ongoing"
        else:
            dis_status = "Past"

        

        dis_id = "reliefweb_"+dis_id
        dictionary = {'dis_id':dis_id, 'dis_name':dis_name, 'dis_status':dis_status ,'dis_country':dis_country,'dis_source_url':str(dis_source_url),'dis_type':[dis_type['name'] for dis_type in disaster_type],'dis_date':str(dis_date),'dis_category':list(dis_category)}
        bar.update(count)
        listOfData.append(dictionary)
        
    return listOfData


# For GDACS API    
def gdacs_api_calls():
    client = GDACSAPIReader()
    events = client.latest_events() # all recent events
    #[None, 'TC', 'EQ', 'FL', 'VO', 'DR', 'WF']
    dis_events = {
        'None':'In Sea/Ocean Bodies',
        'TC':'Tropical Cyclone',
        'EQ':'Earthquake',
        'FL':'Flood',
        'VO':'Volcano',
        'DR':'Drought',
        'WF':'Wild Fire'
    }
    listOfData = [] ;
    bar = pb(len(events.features))
    count = 1;
    for gdacs_dis in events.features:
        
        dis_id = str(gdacs_dis['properties']['eventid'])
        dis_name = gdacs_dis["properties"]["description"]
        dis_country = gdacs_dis["properties"]["country"]
        dis_source_url = gdacs_dis["properties"]["url"]["report"]
        disaster_type = dis_events[gdacs_dis["properties"]["eventtype"]]
        print(f"disaster_type:- {[disaster_type]}")
        dis_date = gdacs_dis["properties"]["fromdate"]
       
        dis_status = gdacs_dis["properties"]["alertlevel"]
        # Convert dis_date to a datetime object
        dis_date_obj = datetime.strptime(dis_date, '%Y-%m-%dT%H:%M:%S')
        # Calculate the difference between dis_date and the current system date
        current_date = datetime.now()
        print(current_date)
        time_diff = current_date - dis_date_obj
        print(f"Time Difference:- {time_diff}\n{dis_date_obj}\n{current_date}")
        # Check the time difference and assign dis_status accordingly
        if time_diff.days <= 1:
            dis_status = "Alert"
        elif 2 <= time_diff.days <= 4:
            dis_status = "Ongoing"
        else:
            dis_status = "Past"

        dis_category = set()
        if 'Canada' in dis_country:
            dis_category.add('Domestic')
        elif 'Ocean Body' in dis_country:
            dis_category.add('Ocean Body')
        else:
            dis_category.add('International')
        
        #dis_to_date = gdacs_dis["properties"]["todate"]
              
        dis_id = "gdacs_"+dis_id
        dictionary = {'dis_id':dis_id, 'dis_name':dis_name,'dis_status':dis_status ,'dis_country':[dis_country] if dis_country else ['Ocean Body'],'dis_source_url':str(dis_source_url),'dis_type':[disaster_type],'dis_date':dis_date,'dis_category':list(dis_category)} #[dis_type for dis_type in disaster_type]
        bar.update(count)
        listOfData.append(dictionary)
    
    return listOfData