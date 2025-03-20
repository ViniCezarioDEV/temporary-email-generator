import requests
import time
from colorama import init, Fore
init(autoreset=True)
BASE_URL = "https://api.mail.tm"


#generate temp email
def create_account():
    domain = requests.get(f"{BASE_URL}/domains").json()['hydra:member'][0]['domain']
    email = f"temp_{int(time.time())}@{domain}"
    password = "12345678"

    response = requests.post(f"{BASE_URL}/accounts", json={"address": email, "password": password})

    if response.status_code == 201:
        print(f"{Fore.CYAN}[LOG] {Fore.WHITE}Email created: {email}")
        return email, password
    else:
        print(f"{Fore.RED}[ERROR] {Fore.WHITE} Account not generated:", response.text)
        return None, None


#generate auth token
def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", json={"address": email, "password": password})
    if response.status_code == 200:
        return response.json()["token"]
    print(f"{Fore.RED}[ERROR] {Fore.WHITE} Token not reached:", response.text)
    return None


#get list of emails
def get_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    if response.status_code == 200:
        return response.json()["hydra:member"]
    print(f"{Fore.RED}[ERROR] {Fore.WHITE} Messages not reached (INBOX):", response.text)
    return []


#get message details
def get_message(token, message_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages/{message_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    print(f"{Fore.RED}[ERROR] {Fore.WHITE} Message not reached (MESSAGE):", response.text)
    return None

email, password = create_account()
if email and password:
    token = get_token(email, password)
    if token:
        checked_messages = set()

        while True:
            messages = get_inbox(token)
            for msg in messages:
                if msg["id"] not in checked_messages:
                    print(f"\n{Fore.CYAN}New message:\n"
                          f"{Fore.YELLOW}SUBJECT: {Fore.WHITE}{msg['subject']}\n"
                          f"{Fore.YELLOW}FROM: {Fore.WHITE}{msg['from']['address']}")
                    msg_details = get_message(token, msg['id'])
                    if msg_details:
                        print(f"{Fore.YELLOW}Message content:{Fore.WHITE}\n"
                              f"{msg_details['text']}\n")
                        checked_messages.add(msg["id"])

            print(f"\n{Fore.CYAN}[LOG] {Fore.WHITE} Waiting new emails...   (15seconds)")
            time.sleep(15)
