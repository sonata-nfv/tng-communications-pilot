import sys
import json
import requests
import urllib3


def get_oauth_token(username, password):
    url = SAPI_ENDPOINT + "/o/token"
    postData = {
        "grant_type": "password",
        "username": username,
        "password": password
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(
        postData), headers=headers, verify=False)
    parsedResponse = json.loads(response.content.decode('utf-8'))
    return parsedResponse["access_token"]


def post_new_user(token, user):
    url = SAPI_ENDPOINT + "/users"
    postData = {
        "domain": "quobis",
        "username": user,
        "email": user + "@quobis.com",
        "role": "user",
        "capabilities": []
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    response = requests.post(url, data=json.dumps(
        postData), headers=headers, verify=False)

    if response.status_code == 409:
        print("User already exists")
        return
    if response.status_code != 201:
        print("There was an error during the creation of the user " + user)
        return
    else:
        print("User " + user + " was created")
        return


def get_users(token):
    url = SAPI_ENDPOINT + "/users/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(url, headers=headers, verify=False)
    parsedResponse = json.loads(response.content.decode('utf-8'))
    return parsedResponse


def get_userUID(users, user):
    for item in users:
        if item["username"] == user:
            return item["id"]


def delete_user(token, user):
    url = SAPI_ENDPOINT + "/users/" + user
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    response = requests.delete(url, headers=headers, verify=False)
    if response.status_code != 200:
        print("There was an error during the deletion of the user")
        return
    else:
        print("User " + user + " was deleted")
        return


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "usages:\n %s add_user <initial_user_number> <final_user_number> <service_uri>\n \
%s remove_user <initial_user_number> <final_user_number> <service_uri>" % (sys.argv[0], sys.argv[0]))
        sys.exit(0)

    # CLI ARGUMENTS
    TASK = str(sys.argv[1])
    USER_START = int(sys.argv[2])
    USER_STOP = int(sys.argv[3])
    WAC_URI = str(sys.argv[4])

    # DEFAULT PARAMETERS
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    DOMAIN = "quobis"
    EMAIL_DOMAIN = "quobis.com"
    SAPI_ENDPOINT = "https://" + WAC_URI + "/sapi"

    # Remove warnings for insecure
    urllib3.disable_warnings()

    # GET bearer token for the admin user
    adminAccessToken = get_oauth_token(ADMIN_USERNAME, ADMIN_PASSWORD)

    if TASK == "add_user":
        for iteration in range(USER_START, USER_STOP + 1):
            user = "5gtango" + str(iteration)
            post_new_user(adminAccessToken, user)

    if TASK == "remove_user":
        # GET users
        users = get_users(adminAccessToken)

        for iteration in range(USER_START, USER_STOP + 1):
            user = "5gtango" + str(iteration)
            # GET the user
            userUID = get_userUID(users, user)
            # Delete the user
            if userUID != None:
                delete_user(adminAccessToken, userUID)
            else:
                print("User " + user + " was not found")
