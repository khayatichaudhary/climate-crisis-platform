import requests
import pandas as pd
import os

def fetch_crisis_data():
    """
    Fetches real disaster data from GDACS API
    """
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
    
    params = {
        "eventtypes": "EQ,TC,FL,DR,VO",  # Earthquake, Cyclone, Flood, Drought, Volcano
        "pagesize": 100,
        "pagenumber": 1
    }
    
    headers = {
        "Accept": "application/json"
    }
    
    print("Fetching crisis data from GDACS API...")
    response = requests.get(url, params=params, headers=headers)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        events = data.get('features', [])
        
        records = []
        for event in events:
            props = event.get('properties', {})
            record = {
                'id': props.get('eventid', 'Unknown'),
                'title': props.get('name', 'Unknown'),
                'type': props.get('eventtype', 'Unknown'),
                'country': props.get('country', 'Unknown'),
                'date': props.get('fromdate', 'Unknown'),
                'severity': props.get('alertlevel', 'Unknown'),
                'affected_countries': props.get('affectedcountries', 'Unknown')
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        print(f"Successfully fetched {len(df)} disaster records!")
        return df
    
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:200])
        return None

if __name__ == "__main__":
    df = fetch_crisis_data()
    if df is not None:
        print(df.head(10))
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv("data/raw/crisis_data.csv", index=False)
        print("\nData saved to data/raw/crisis_data.csv ✅")