import requests
import json
import re

"""
To-do:
- Make format groups and editions async
"""

def format_groups():
    url = "https://na2.iiivega.com/api/search-result/search/format-groups"
    headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "anonymous-user-id": "c6aeabfe-dcc0-4e1a-8fa2-3934d465cb70",
    "api-version": "2",
    "content-type": "application/json",
    "iii-customer-domain": "slouc.na2.iiivega.com",
    "iii-host-domain": "slouc.na2.iiivega.com",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://slouc.na2.iiivega.com/"
  }
    body = {"searchText":"*","sorting":"relevance","sortOrder":"asc","searchType":"everything","universalLimiterIds":["at_library"],"materialTypeIds":["1"],"locationIds":["59"],"pageNum":0,"pageSize":10,"resourceType":"FormatGroup"}

    response = requests.post(url, headers=headers, json=body)
    records = response.json()

    parsed = []
    for record in records.get("data"):
        # get separate record for each item in materials
        for material in record.get("materialTabs"):
            materialName = material.get("name")
            if materialName.lower() != "book":
                continue
            parsed.append({
                "id": record.get("id"),
                "title": record.get("title"),
                "author": record.get("primaryAgent", {}).get("label"),
                "publicationDate": record.get("publicationDate"),
                "materialName": materialName,
                "callNumber": material.get("callNumber"),
                "description": material.get("description"),
                "editionId": material.get("editions")[0].get("id")
        })
    
    return parsed
        
# next, just get subjects with call to editions.
def get_edition(id):
    url = f"https://na2.iiivega.com/api/search-result/editions/{id}"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "anonymous-user-id": "c6aeabfe-dcc0-4e1a-8fa2-3934d465cb70",
        "api-version": "1",
        "iii-customer-domain": "slouc.na2.iiivega.com",
        "iii-host-domain": "slouc.na2.iiivega.com",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Referer": "https://slouc.na2.iiivega.com/"
    }

    response = requests.get(url, headers=headers)
    e = response.json()
    e_details = e.get("edition")

    lang = e_details.get("itemLanguage")

    subjects = []
    for key in e_details.keys():
        if re.match("subj", key) is not None:
            subjects.extend(e_details[key])

    e_info = {
        "language": lang,
        "subjects": subjects
    }

    return {key: value for key, value in e_info.items() if value is not None}

# flatten lists to strings
def flatten_data(data):
    for record in data:
        for key in record.keys():
            if isinstance(record[key], list):
                record[key] = ", ".join(record[key])

# fetch records, get editions, and flatten lists
def get_data(): 
    result = format_groups()
    for item in result:
        item.update(get_edition(item["editionId"]))
    flatten_data(result)
    return result

if __name__ == "__main__":
    result = get_data()
    with open("data.json", "w") as f:
        json.dump(result, f, indent=2)

    with open("data.json", "r") as f:
        data = json.load(f)
    
    print(data)

    
    






        
