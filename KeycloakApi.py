import httpx, configparser, datetime
from loguru import logger

from models import UserRepr
from request_helper import RequestHelper
from transliterate import translit

class KeycloakAPI:
    def __init__(self, config_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.host = self.config.get("KEYCLOAK", "host")
        self.username = self.config.get("KEYCLOAK", "username")
        self.password = self.config.get("KEYCLOAK", "password")
        self.requester = RequestHelper()
        self.token = None # will be generated
        self.access_token_expired_at = datetime.datetime.now()
        self.refresh_token_expired_at = datetime.datetime.now()
        self.refresh_token = None  # will be generated

    async def init_token(self):
        endpoint = "/realms/master/protocol/openid-connect/token"
        url = self.host + endpoint
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "username": self.username,
            "password": self.password,
            "client_id": "admin-cli",
            "grant_type": "password",
        }
        dt_now = datetime.datetime.now()
        response = await self.requester.post(url, data=payload, headers=headers)
        if 300 < response.status_code < 500:
            raise logger.error(f"Error getting token: {response.status_code}, error text: {response.text}")

        r_json = response.json()
        self.token = r_json.get("access_token")
        self.refresh_token = r_json.get("refresh_token")
        access_token_expires_in_secs = r_json.get("expires_in")
        refresh_token_expires_in_secs = r_json.get("expires_in")
        self.access_token_expired_at = dt_now + datetime.timedelta(seconds=access_token_expires_in_secs)
        self.refresh_token_expired_at = dt_now + datetime.timedelta(seconds=refresh_token_expires_in_secs)

    async def get_new_token(self):
        endpoint = "/realms/master/protocol/openid-connect/token"
        url = self.host + endpoint
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "refresh_token": self.refresh_token,
            "client_id": "admin-cli",
            "grant_type": "refresh_token",
        }
        dt_now = datetime.datetime.now()
        response = await self.requester.post(url, data=payload, headers=headers)
        if 300 < response.status_code < 500:
            raise logger.error(f"Error getting token: {response.status_code}, error text: {response.text}")

        r_json = response.json()
        self.token = r_json.get("access_token")
        access_token_expires_in_secs = r_json.get("expires_in")
        self.access_token_expired_at = dt_now + datetime.timedelta(seconds=access_token_expires_in_secs)

    async def verify_token(self):
        dt_now = datetime.datetime.now()
        if not (self.access_token_expired_at < dt_now):
            return
        if self.refresh_token_expired_at < dt_now:
            await self.init_token()
            return
        await self.get_new_token()

    async def add_user(self, user_info: UserRepr):
        await self.verify_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        username, passwd, email = self.gen_credentials(user_info.full_name)
        full_name_list = user_info.full_name.split(" ")
        last_name = full_name_list[0]
        first_name = full_name_list[1]
        realms_list = self.config.get("KEYCLOAK", "realms").split(',')
        for realm in realms_list:
            exist_user = await self.get_user(realm, username=username)
            if exist_user:
                logger.debug(f"User already exists in realm {realm}")
                return None
            logger.info(f"Creating new user {username} in realm {realm}")
            endpoint = f"/admin/realms/{realm}/users"
            url = self.host + endpoint
            payload = {
                "enabled": True,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "credentials": [{
                    "type": "password",
                    "value": passwd,
                    "temporary": True
                }]
            }
            response = await self.requester.post(url, data=payload, headers=headers)
            if 300 < response.status_code < 500:
                raise logger.error(f"Error getting user: {response.status_code}, error text: {response.text}")
            return response.json()
        return None


    async def get_user(self, realm, **kwargs):
        await self.verify_token()
        endpoint = f"/admin/realms/{realm}/users"
        url = self.host + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        params = ''
        c = 0
        for key, value in kwargs.items():
            if c == 0:
                params += '?'
            params += f'{key}={value}'
            if c != len(kwargs):
                params += '&'

        response = await self.requester.get(url, params=params, headers=headers)
        if 300 < response.status_code < 500:
            raise logger.error(f"Error getting user: {response.status_code}, error text: {response.text}")

        return response.json()

    def gen_credentials(self, full_name):
        full_name_list = full_name.split(" ")
        username = translit(full_name_list[0].lower(), "ru", reversed=True)
        username += '.'
        for cred in full_name_list[1:]:
            username += translit(cred[0].lower(), "ru", reversed=True)
        passwd = f"{username}123"
        email = f"{username}@kgeu.ru"
        return username, passwd, email





