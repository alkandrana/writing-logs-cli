from wlogs import load_config
import sys, requests
import maskpass
import keyring as kr
# AUTH WORKFLOW
# 1. User sends request
# 2. Attempt to load token from keyring
#       If token present
#           send_request()
#       If no token present
#           get_refresh_token()

# 3. send request
#       if response unauthorized
#           get_refresh_token()


def check_server_health(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code < 500
    except requests.RequestException:
        return False


def send_auth_request(request):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    request["headers"] = headers
    res = validate_response(request)
    return res


def get_refresh_token():
    refresh_token = kr.get_password("wlogs", "refresh_token")
    if refresh_token:
        refresh(refresh_token)
    else:
        login()


def get_access_token():
    access_token = kr.get_password("wlogs", "access_token")
    if access_token:
        return access_token
    else:
        get_refresh_token()
        return kr.get_password("wlogs", "access_token")


def validate_response(request):
    # check server
    if not check_server_health(load_config()["api_url"]):
        print("The server appears to be down.")
        sys.exit(1)
    # send request
    response = send_request(request)
    # if request succeeded
    if (
        200 <= response.status_code < 300
        or 400 <= response.status_code < 500
        and response.status_code != 401
    ):
        return response
    # if access token expired
    elif response.status_code == 401:
        get_refresh_token()
        response = send_request(request)
        if 200 <= response.status_code < 300 or 400 <= response.status_code < 500:
            return response
        else:
            print("Request failed.")
            print("An error occurred:", response.status_code, response.reason)
            if response.json():
                error = response.json()
                print(f"Error message: {error}")
            sys.exit(1)
    # if request did not succeed
    else:
        print("Non-authorization error.")
        print("An error occurred:", response.status_code, response.reason)
        if response.json():
            error = response.json()
            print(f"Error message: {error}")
        sys.exit(1)


def send_request(request):
    access_token = get_access_token()
    request["headers"]["Authorization"] = f"Bearer {access_token}"
    # print(f"Sending authenticated request: {request['endpoint']}")
    if request["method"] == "POST":
        response = requests.post(
            request["endpoint"], json=request["payload"], headers=request["headers"]
        )
    elif request["method"] == "PATCH":
        response = requests.patch(
            request["endpoint"], json=request["payload"], headers=request["headers"]
        )
    elif request["method"] == "GET":
        response = requests.get(request["endpoint"], headers=request["headers"])
    else:
        print("Method not recognized.")
        sys.exit(1)
    return response


def handle_missing_token():
    access_token = kr.get_password("wlogs", "access_token")
    if not access_token:
        refresh_token = kr.get_password("wlogs", "refresh_token")
        if not refresh_token:
            login()


def build_request(access_token, body, method, url):
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    request = {
        "method": method,
        "endpoint": url,
        "headers": header,
    }
    if body:
        request["payload"] = body
    return request


def login():
    print("Initiating login: ")
    # hit login endpoint
    username = input("Enter your username: ")
    password = maskpass.askpass()
    payload = {"email": username, "password": password}
    url = load_config()
    response = requests.post(f"{url['api_url']}/login", json=payload)
    #               if login success
    if 200 <= response.status_code < 300:
        #                   restart_request()
        auth = response.json()
        kr.set_password("wlogs", "access_token", auth["accessToken"])
        kr.set_password("wlogs", "refresh_token", auth["refreshToken"])
    #               if no login success
    else:
        #                   prompt user to check credentials/register
        print(
            "Login failed. Please check your credentials and try again. "
            "You can also register for a new account with 'wlogs register'"
        )
        print(f"Details: {response.status_code} {response.reason}")
        #                   terminate
        sys.exit(1)


def refresh(refresh_token):
    # hit refresh endpoint
    payload = {"refreshToken": refresh_token}
    response = requests.post(f"{load_config()['api_url']}/refresh", json=payload)
    #               if refresh success
    if 200 <= response.status_code < 300:
        #                   save tokens
        auth = response.json()
        kr.set_password("wlogs", "access_token", auth["accessToken"])
        kr.set_password("wlogs", "refresh_token", auth["refreshToken"])
    #                   send_request()
    #               if not refresh success
    elif response.status_code == 401:
        login()


def cmd_login(_):
    login()


def register(_):
    username = input("Enter your username: ")
    password = maskpass.askpass()
    payload = {"email": username, "password": password}
    url = f"{load_config()['api_url']}/register"
    print("API url: ", url, payload)
    res = requests.post(url, json=payload)
    if 200 <= res.status_code < 300:
        print("Successfully registered.")
        print("Use 'wlogs login' to continue.")
    else:
        print("Something went wrong: ", res.status_code, res.reason, res.json())


def parse_auth(subparsers):
    register_parser = subparsers.add_parser("register")
    register_parser.set_defaults(func=register)

    login_parser = subparsers.add_parser("login")
    login_parser.set_defaults(func=cmd_login)
