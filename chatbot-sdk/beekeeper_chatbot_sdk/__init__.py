from beekeeper_sdk import BeekeeperSDK


class BeekeeperChatBot:
    def __init__(self, tenant_url, api_token):
        self.sdk = BeekeeperSDK(tenant_url=tenant_url, api_token=api_token)
