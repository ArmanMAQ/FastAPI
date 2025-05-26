import requests

class PowerBIClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.powerbi.com/v1.0/myorg"

    def export_report(self, group_id, report_id, export_body):
        url = f"{self.base_url}/groups/{group_id}/reports/{report_id}/ExportTo"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=export_body)
        response.raise_for_status()
        return response.json()

    # Add more methods as needed for your use case

# Instead of getting token from msal, get it from the user (e.g., via Swagger UI or request header)
def get_power_bi_client_from_token(access_token):
    return PowerBIClient(access_token)