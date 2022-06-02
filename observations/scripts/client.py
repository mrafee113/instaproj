import re
import sys
import json
import email
import random
import string
import secrets
import pathlib
import imaplib

from instagrapi import Client
from django.conf import settings
from instagrapi.types import Hashtag
from instagrapi.mixins.challenge import ChallengeChoice
from utils.selenium import web_driver, DriverHandler as H


def change_password_handler(username):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(15))
    print(f'WARNING! NEW PASSWORD: {password}', file=sys.stderr)
    return password


def get_code_from_email(username):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(settings.GMAIL_USER, settings.GMAIL_PASS)
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = payload.get_payload(decode=True).decode()
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
    return False


def get_code_from_sms(username):
    for i in range(10):
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit():
            return code


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False


def settings_file_path(filename: str) -> pathlib.PosixPath:
    return settings.BASE_DIR / 'data' / filename


def prepare_driver_for_cookies(settings_filename: str = 'insta_settings.json'):
    settings_filepath = settings_file_path(settings_filename)
    with open(settings_filepath, 'r+') as file:
        useragent = json.load(file)['user_agent']

    data_dir = f'/tmp/rand{random.randint(1, 1000)}'
    pathlib.Path(data_dir).mkdir(exist_ok=True)
    driver = web_driver(headless=False, data_dir=data_dir, useragent=useragent)
    H.get_url(driver, url='https://www.instagram.com/')
    return driver


def dump_cookies_from_driver(driver, settings_filename: str = 'insta_settings.json'):
    cookies: dict = {c['name']: c['value'] for c in driver.get_cookies()}
    settings_filepath = settings_file_path(settings_filename)
    with open(settings_filepath, 'r+') as file:
        client_settings = json.load(file)
        client_settings.update({'cookies': cookies})
        file.seek(0)
        json.dump(client_settings, file, indent=2)

    driver.close()


def renew_client_settings(settings_filename: str = 'insta_settings.json'):
    client = Client()
    client.challenge_code_handler = challenge_code_handler
    client.change_password_handler = change_password_handler

    settings_filepath = settings_file_path(settings_filename)
    with open(settings_filepath) as file:
        client_settings: dict = json.load(file)
    for del_key in ['uuids', 'cookies', 'mid', 'authorization_data']:
        if del_key in client_settings:
            del client_settings[del_key]

    client.set_settings(client_settings)
    client.login(settings.IG_USER, settings.IG_PASS)
    uuid_keys = ['phone_id', 'uuid', 'client_session_id', 'advertising_id',
                 'android_device_id', 'request_id', 'tray_session_id']
    uuids = {key: getattr(client, key) for key in uuid_keys if getattr(client, key)}
    client_settings.update({'uuids': uuids})
    client_settings.update({'authorization_data': client.authorization_data})
    with open(settings_filepath, 'w') as file:
        json.dump(client_settings, file, indent=2)


def setup_client(settings_filename: str = 'insta_settings.json', cookies: bool = True, renew: bool = False) -> Client:
    if renew:
        renew_client_settings()

    client = Client()
    # client.challenge_code_handler = challenge_code_handler
    # client.change_password_handler = change_password_handler

    filepath = settings_file_path(settings_filename)
    with open(filepath) as file:
        client_settings = json.load(file)
    if not cookies and 'cookies' in client_settings:
        del client_settings['cookies']
    client.set_settings(client_settings)
    client.login(settings.IG_USER, settings.IG_PASS)
    return client


def search_hashtags(client: Client, query: str, count: int = 60) -> list[Hashtag]:
    params = {
        "search_surface": "hashtag_search_page",
        "timezone_offset": client.timezone_offset,
        "count": 30,
        "q": query,
    }
    result = client.private_request("tags/search/", params=params)
    from instagrapi.extractors import extract_hashtag_v1
    return [extract_hashtag_v1(ht) for ht in result["results"]]

# todo: write script to eval all tags all over again
