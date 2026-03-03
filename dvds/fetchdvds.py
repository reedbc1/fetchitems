import requests
import json

# use to update 
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
        "referer": "https://slouc.na2.iiivega.com/",
    }

    payload = {
        "searchText": "*",
        "sorting": "relevance",
        "sortOrder": "asc",
        "searchType": "everything",
        "universalLimiterIds": ["at_library"],
        "materialTypeIds": ["33"],
        "locationIds": ["59"],
        "pageNum": 0,
        "pageSize": 1,
        "resourceType": "FormatGroup"
    }

    response = requests.post(url, headers=headers, json=payload)

    records = response.json()

    parsed = []
    for r in records.get('data'):
        parsed.append(
            {
                'id': r.get("id"),
                'title': r.get('title'),
                'publicationDate': r.get('publicationDate'),
                'coverUrl': r.get('coverUrl', {}).get('medium'),
                'editionId': r.get('materialTabs', [])[0].get('editions', [])[0].get('id')
            }
        )

    return parsed


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
    e = response.json().get('edition')

    null_genres = {'Feature films', 'Video recordings for the hearing impaired'}
    return {
        'id': id,
        'genre': ", ".join([g for g in e.get('subjGenre') if g not in null_genres]),
        'actors': ", ".join(e.get('noteParticipant'))
    }    


if __name__ == "__main__":
    print(format_groups())
    # print(get_edition('83fa7012-82c5-11ee-a04e-fd82fa1fe033'))


