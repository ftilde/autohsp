import requests
import os
import json
from datetime import datetime, timedelta, timezone


AUTH_TOKEN = os.getenv('AUTH_TOKEN')

base_url = 'https://backbone-web-api.production.munster.delcom.nl/'

standard_headers = {
    "User-Agent": "Android 7.1.2 - Brand: LGE - Model: Nexus 5",
    #"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Accept": "application/json, text/plain, */*",
    #{"Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Authorization": f"Bearer {AUTH_TOKEN}",
    #"x-user-role-id": "...",
    "x-custom-lang": "de",
    "x-platform": "CF",
    "Origin": "https://localhost",
    #{"Connection": "keep-alive",
    "Referer": "https://backbone-web-api.production.munster.delcom.nl/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "TE": "trailers",
}

gate_codes = {
    "Ballsporthalle": "8EF7A75C899B6BAE9296308CDB83530CE85232D06D53708ED0DAB180A06FABE2F0BD9BB6BB0420B655895072637A3DD9647F4EB97E8D65B250D80DC4CFED0FBB39B9A3BBF6E274966A13C0E1E35668E590579C46",
}

def request_get(path, params=None, extra_headers = None):
    url = base_url + path

    if extra_headers:
        headers = standard_headers + extra_headers

    response = requests.get(
        url,
        params=params,
        headers=standard_headers,
    )

    return response

def request_post(path, json=None, extra_headers = None):
    url = base_url + path

    if extra_headers:
        headers = standard_headers + extra_headers

    response = requests.post(
        url,
        json=json,
        headers=standard_headers,
    )

    return response

def book(member_id, booking_id):
    body = {"organizationId": 0,
            "memberId":member_id,
            "bookingId":booking_id,
            "primaryPurchaseMessage": 0,
            "secondaryPurchaseMessage": 0,
            #"params":{"startDate":"2025-04-13T15:00:00.000Z",
            #          "endDate":"2025-04-13T16:59:00.000Z",
            #          "bookableProductId":59,
            #          "bookableLinkedProductId":467,
            #          "bookingId":5617,
            #          "invitedMemberEmails":[],
            #          "invitedGuests":[],
            #          "invitedOthers":[],
            #          "primaryPurchaseMessage":null,
            #          "secondaryPurchaseMessage":null,
            #          "clickedOnBook":true
            #          },
            "dateOfRegistration": 0,
            }

    return request_post("participations", json=body)

def scan(gate_name):
    gate_code = gate_codes[gate_name]
    body = {"type":"AccessControlRequestEntryByCode",
            "isAsync":False,
            "params":{"gateCode":gate_code},
            }

    return request_post("tasks", json=body)

def fetch_participations(member_id, booking_id):
    filter = {
            "$and":[
                {"memberId": member_id},
                {"bookingId": booking_id},
                ]
            }

    params = {
        "s": json.dumps(filter)
    }

    return request_get("participations", params)

def datetime_to_str(dt):
    dt = dt.astimezone(timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def fetch_courses(start, productId=None, tagId=None, range_days=7):
    end = start + timedelta(days=range_days)
    filter = {"startDate":datetime_to_str(start),
              "endDate":datetime_to_str(end),
              #"tagIds":{"$in":[tagId]},
              "productIds":{"$in":[productId]},
              #"availableFromDate":{"$gt":"2025-04-01T18:45:27.098Z"},
              #"availableTillDate":{"$gte":"2025-04-05T22:00:00.000Z"}
              }

    params = {
        "s": json.dumps(filter),
        "join":["linkedProduct", "linkedProduct.translations", "product", "product.translations"]
    }

    return request_get("bookable-slots", params)

def fetch_auth():
    params = {
        "cf": 0
    }

    return request_get("auth", params)

def find_course(productId, level_str):
    now = datetime.now(timezone.utc)


    courses = fetch_courses(start=now,productId=productId).json()
    booking_id = None
    try:
        courses = courses["data"]
        for course in courses:
            booking = course["booking"]
            product = booking["linkedProduct"]
            if product["id"] == productId and level_str in booking["description"]:
                #print(product["description"])
                #print(product["id"])
                #print(booking["description"])
                #print(booking["startDate"])
                return booking["id"]
    except:
        print(courses)
        exit(1)

    return None

def try_book(member_id, booking_id):
    book_response = book(member_id=member_id, booking_id=booking_id).json()
    try:
        status = book_response["status"]
        print("Booking successful: {}".format(book_response))
        return book_response
    except:
        print(book_response)
        exit(1)

auth = fetch_auth().json();
print(auth)
member_id=auth["id"]

#tagId = 46
productId = 467
level_str = "Level 4"

booking_id = find_course(productId, level_str)

print("booking_id: " + str(booking_id))

print(try_book(member_id=member_id, booking_id=booking_id))
#print(fetch_participations(member_id=member_id, booking_id=booking_id).json())
#scan_result = scan("Ballsporthalle")
#print("scan: " + str(scan_result.json()))
