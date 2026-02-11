
import requests
import json

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
    "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://slouc.na2.iiivega.com/"
}
body = {
    "searchText": "*",
    "sorting": "relevance",
    "sortOrder": "asc",
    "searchType": "everything",
    "universalLimiterIds": ["at_library"],
    "locationIds": ["59"],
    "pageNum": 0,
    "pageSize": 1,
    "resourceType": "FormatGroup"
}

response = requests.post(url, headers=headers, json=body)
records = response.json()
print(json.dumps(records, indent=2))

parsed = []
for record in records.get("data"):
    # get separate record for each item in materials
    for material in record.get("materialTabs"):
        parsed.append({
            "id": record.get("id"),
            "title": record.get("title"),
            "author": record.get("primaryAgent", {}).get("label"),
            "publicationDate": record.get("publicationDate"),
            "materialName": material.get("name"),
            "callNumber": material.get("callNumber"),
            "description": material.get("description"),
            "editionId": material.get("editions")[0].get("id")
    })

print(json.dumps(parsed, indent=2))

