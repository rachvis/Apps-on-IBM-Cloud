import time
import requests


class FeatureFlagClient:
    def __init__(self, app_config_url: str, app_config_guid: str, app_config_apikey: str, environment_id: str):
        self.app_config_url = app_config_url.rstrip("/")
        self.app_config_guid = app_config_guid
        self.app_config_apikey = app_config_apikey
        self.environment_id = environment_id
        self._iam_token = ""
        self._token_expiry = 0

    def _get_iam_token(self) -> str:
        now = int(time.time())
        if self._iam_token and now < self._token_expiry:
            return self._iam_token

        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.app_config_apikey,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            timeout=6,
        )
        response.raise_for_status()
        payload = response.json()
        self._iam_token = payload["access_token"]
        self._token_expiry = int(time.time()) + int(payload.get("expires_in", 3600)) - 60
        return self._iam_token

    def is_enabled(self, flag_key: str, fallback: bool = False) -> bool:
        if not all([self.app_config_url, self.app_config_guid, self.app_config_apikey, self.environment_id]):
            return fallback

        try:
            iam_token = self._get_iam_token()
            url = (
                f"{self.app_config_url}/apprapp/feature/v1/instances/{self.app_config_guid}/"
                f"environments/{self.environment_id}/features/{flag_key}"
            )
            headers = {
                "Authorization": f"Bearer {iam_token}",
                "Accept": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=4)
            response.raise_for_status()
            payload = response.json()
            return bool(payload.get("enabled", fallback))
        except Exception:
            return fallback
