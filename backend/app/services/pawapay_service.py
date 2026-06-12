"""PawaPay mobile money payment integration."""
import requests
import uuid
from typing import Dict, Optional
from datetime import datetime


class PawaPayService:
    """PawaPay mobile money payment service for 19 African countries."""

    BASE_URL = "https://api.pawapay.cloud"  # Production
    # BASE_URL = "https://api.sandbox.pawapay.cloud"  # Sandbox

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def initiate_deposit(
        self,
        amount: str,
        currency: str,
        phone_number: str,
        correspondent: str,
        statement_description: str = "ACTI Subscription"
    ) -> Dict:
        """Initiate mobile money deposit."""
        deposit_id = str(uuid.uuid4())

        payload = {
            "depositId": deposit_id,
            "amount": amount,
            "currency": currency,
            "correspondent": correspondent,
            "payer": {
                "type": "MSISDN",
                "address": {"value": phone_number}
            },
            "customerTimestamp": datetime.utcnow().isoformat() + "Z",
            "statementDescription": statement_description
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/deposits",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            print(f"[PAWAPAY] Deposit status: {response.status_code}")

            if response.status_code in [200, 201, 202]:
                return {
                    "success": True,
                    "deposit_id": deposit_id,
                    "status": "SUBMITTED"
                }
            else:
                return {
                    "success": False,
                    "deposit_id": deposit_id,
                    "status": "FAILED",
                    "message": response.text
                }
        except Exception as e:
            print(f"[ERROR] PawaPay: {str(e)}")
            return {
                "success": False,
                "deposit_id": deposit_id,
                "status": "FAILED",
                "message": str(e)
            }

    def check_deposit_status(self, deposit_id: str) -> Dict:
        """Check deposit status."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/deposits/{deposit_id}",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get("status"),
                    "data": data
                }
            return {
                "success": False,
                "status": "UNKNOWN",
                "message": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "status": "UNKNOWN",
                "message": str(e)
            }


# Mobile operators by country
CORRESPONDENTS = {
    "RW": {"MTN": "MTN_MOMO_RWA", "AIRTEL": "AIRTEL_OAPI_RWA"},
    "KE": {"MPESA": "MPESA_KEN", "AIRTEL": "AIRTEL_OAPI_KEN"},
    "UG": {"MTN": "MTN_MOMO_UGA", "AIRTEL": "AIRTEL_OAPI_UGA"},
    "TZ": {"VODACOM": "VODACOM_MPESA_TZA", "AIRTEL": "AIRTEL_OAPI_TZA", "TIGO": "TIGO_TZA"},
    "ZM": {"MTN": "MTN_MOMO_ZMB", "AIRTEL": "AIRTEL_OAPI_ZMB"},
    "GH": {"MTN": "MTN_MOMO_GHA", "VODAFONE": "VODAFONE_GHA", "AIRTELTIGO": "AIRTELTIGO_GHA"},
    "CM": {"MTN": "MTN_MOMO_CMR", "ORANGE": "ORANGE_CMR"},
    "CI": {"MTN": "MTN_MOMO_CIV", "ORANGE": "ORANGE_CIV", "MOOV": "MOOV_CIV"},
    "SN": {"ORANGE": "ORANGE_SEN", "FREE": "FREE_SEN"},
    "BJ": {"MTN": "MTN_MOMO_BEN", "MOOV": "MOOV_BEN"},
    "ZA": {"VODACOM": "VODACOM_ZAF"},
    "MW": {"AIRTEL": "AIRTEL_OAPI_MWI", "TNM": "TNM_MWI"},
    "CD": {"AIRTEL": "AIRTEL_OAPI_COD", "ORANGE": "ORANGE_COD", "VODACOM": "VODACOM_COD"},
}


def get_correspondent_code(country: str, operator: str) -> Optional[str]:
    """Get PawaPay correspondent code."""
    country_ops = CORRESPONDENTS.get(country.upper())
    if country_ops:
        return country_ops.get(operator.upper())
    return None
