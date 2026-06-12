"""Pricing service for 20 African countries with live exchange rates."""
import httpx
from datetime import datetime, timedelta
from typing import Dict, Optional
import json


class PricingService:
    """Manage pricing across 20 African countries with live exchange rates."""

    # USD base prices
    USD_PRICES = {
        "personal": 5,
        "professional": 49
    }

    # Country configuration
    COUNTRIES = {
        "RW": {
            "name": "Rwanda",
            "currency": "RWF",
            "operators": {"MTN": "MTN_MOMO_RWA", "Airtel": "AIRTEL_OAPI_RWA"}
        },
        "KE": {
            "name": "Kenya",
            "currency": "KES",
            "operators": {"M-Pesa": "MPESA_KEN", "Airtel": "AIRTEL_OAPI_KEN"}
        },
        "UG": {
            "name": "Uganda",
            "currency": "UGX",
            "operators": {"MTN": "MTN_MOMO_UGA", "Airtel": "AIRTEL_OAPI_UGA"}
        },
        "TZ": {
            "name": "Tanzania",
            "currency": "TZS",
            "operators": {"Vodacom": "VODACOM_TZA", "Airtel": "AIRTEL_OAPI_TZA", "Tigo": "TIGO_TZA"}
        },
        "ZM": {
            "name": "Zambia",
            "currency": "ZMW",
            "operators": {"MTN": "MTN_MOMO_ZMB", "Airtel": "AIRTEL_OAPI_ZMB"}
        },
        "GH": {
            "name": "Ghana",
            "currency": "GHS",
            "operators": {"MTN": "MTN_MOMO_GHA", "Vodafone": "VODAFONE_GHA", "AirtelTigo": "AIRTELTIGO_GHA"}
        },
        "CM": {
            "name": "Cameroon",
            "currency": "XAF",
            "operators": {"MTN": "MTN_MOMO_CMR", "Orange": "ORANGE_CMR"}
        },
        "CI": {
            "name": "Côte d'Ivoire",
            "currency": "XOF",
            "operators": {"MTN": "MTN_MOMO_CIV", "Orange": "ORANGE_CIV", "Moov": "MOOV_CIV"}
        },
        "SN": {
            "name": "Senegal",
            "currency": "XOF",
            "operators": {"Orange": "ORANGE_SEN", "Free": "FREE_SEN"}
        },
        "BJ": {
            "name": "Benin",
            "currency": "XOF",
            "operators": {"MTN": "MTN_MOMO_BEN", "Moov": "MOOV_BEN"}
        },
        "ZA": {
            "name": "South Africa",
            "currency": "ZAR",
            "operators": {"Vodacom": "VODACOM_ZAF"}
        },
        "MW": {
            "name": "Malawi",
            "currency": "MWK",
            "operators": {"Airtel": "AIRTEL_OAPI_MWI", "TNM": "TNM_MWI"}
        },
        "CD": {
            "name": "Congo DRC",
            "currency": "CDF",
            "operators": {"Airtel": "AIRTEL_OAPI_COD", "Orange": "ORANGE_COD", "Vodacom": "VODACOM_COD"}
        },
        "BF": {
            "name": "Burkina Faso",
            "currency": "XOF",
            "operators": {"Orange": "ORANGE_BFA", "Moov": "MOOV_BFA"}
        },
        "GA": {
            "name": "Gabon",
            "currency": "XAF",
            "operators": {"Airtel": "AIRTEL_OAPI_GAB"}
        },
        "MG": {
            "name": "Madagascar",
            "currency": "MGA",
            "operators": {"Airtel": "AIRTEL_OAPI_MDG", "Orange": "ORANGE_MDG", "Telma": "TELMA_MDG"}
        },
        "NE": {
            "name": "Niger",
            "currency": "XOF",
            "operators": {"Airtel": "AIRTEL_OAPI_NER", "Orange": "ORANGE_NER"}
        },
        "TD": {
            "name": "Chad",
            "currency": "XAF",
            "operators": {"Airtel": "AIRTEL_OAPI_TCD"}
        },
        "CG": {
            "name": "Congo",
            "currency": "XAF",
            "operators": {"Airtel": "AIRTEL_OAPI_COG"}
        },
        "NG": {
            "name": "Nigeria",
            "currency": "NGN",
            "operators": {"MTN": "MTN_MOMO_NGA", "Airtel": "AIRTEL_OAPI_NGA", "9mobile": "9MOBILE_NGA"}
        }
    }

    # Cache for exchange rates (refreshed every 24 hours)
    _exchange_rates_cache: Optional[Dict[str, float]] = None
    _cache_timestamp: Optional[datetime] = None
    _cache_duration = timedelta(hours=24)

    @staticmethod
    async def fetch_exchange_rates() -> Dict[str, float]:
        """
        Fetch live exchange rates from exchangerate-api.com.
        Returns dictionary of currency code -> rate (USD base).
        """
        # Check cache first
        if (PricingService._exchange_rates_cache and
            PricingService._cache_timestamp and
            datetime.utcnow() - PricingService._cache_timestamp < PricingService._cache_duration):
            print(f"[PRICING] Using cached exchange rates (age: {datetime.utcnow() - PricingService._cache_timestamp})")
            return PricingService._exchange_rates_cache

        try:
            # Free API endpoint - no key required for basic usage
            url = "https://open.er-api.com/v6/latest/USD"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if data.get("result") == "success":
                    rates = data.get("rates", {})

                    # Cache the rates
                    PricingService._exchange_rates_cache = rates
                    PricingService._cache_timestamp = datetime.utcnow()

                    print(f"[PRICING] SUCCESS: Fetched fresh exchange rates from API")
                    print(f"[PRICING]   Sample rates: RWF={rates.get('RWF')}, KES={rates.get('KES')}, NGN={rates.get('NGN')}")

                    return rates
                else:
                    raise Exception(f"API returned error: {data}")

        except Exception as e:
            print(f"[PRICING] WARNING: Failed to fetch live rates: {str(e)}")

            # Fallback to approximate rates if API fails
            fallback_rates = {
                "RWF": 1300.0,
                "KES": 155.0,
                "UGX": 3750.0,
                "TZS": 2350.0,
                "ZMW": 27.0,
                "GHS": 15.5,
                "XAF": 605.0,
                "XOF": 605.0,
                "ZAR": 18.5,
                "MWK": 1700.0,
                "CDF": 2700.0,
                "MGA": 4600.0,
                "NGN": 1650.0
            }

            print(f"[PRICING]   Using fallback rates")
            PricingService._exchange_rates_cache = fallback_rates
            PricingService._cache_timestamp = datetime.utcnow()

            return fallback_rates

    @staticmethod
    async def get_country_pricing(country_code: str) -> Dict:
        """
        Get pricing for a specific country with live exchange rates.

        Args:
            country_code: Two-letter country code (e.g., "RW")

        Returns:
            Dictionary with country, currency, personal price, professional price, operators
        """
        if country_code not in PricingService.COUNTRIES:
            raise ValueError(f"Country code '{country_code}' not supported")

        country_data = PricingService.COUNTRIES[country_code]
        currency = country_data["currency"]

        # Fetch live exchange rates
        exchange_rates = await PricingService.fetch_exchange_rates()

        # Get exchange rate for this currency
        exchange_rate = exchange_rates.get(currency)
        if not exchange_rate:
            raise ValueError(f"Exchange rate for {currency} not available")

        # Calculate prices in local currency
        personal_price = int(PricingService.USD_PRICES["personal"] * exchange_rate)
        professional_price = int(PricingService.USD_PRICES["professional"] * exchange_rate)

        # Round to nice numbers
        personal_price = PricingService._round_price(personal_price, currency)
        professional_price = PricingService._round_price(professional_price, currency)

        return {
            "country": country_data["name"],
            "currency": currency,
            "personal": str(personal_price),
            "professional": str(professional_price),
            "operators": list(country_data["operators"].keys()),
            "exchange_rate": exchange_rate,
            "last_updated": PricingService._cache_timestamp.isoformat() if PricingService._cache_timestamp else None
        }

    @staticmethod
    def _round_price(price: int, currency: str) -> int:
        """Round price to nice numbers based on currency."""
        # For large value currencies (thousands), round to nearest 100 or 1000
        if price >= 10000:
            return round(price / 1000) * 1000
        elif price >= 1000:
            return round(price / 100) * 100
        elif price >= 100:
            return round(price / 10) * 10
        else:
            # For small value currencies, round to nearest 5 or 10
            if price >= 50:
                return round(price / 10) * 10
            else:
                return round(price / 5) * 5

    @staticmethod
    async def list_all_pricing() -> list:
        """Get pricing for all supported countries."""
        results = []
        for country_code in PricingService.COUNTRIES.keys():
            try:
                pricing = await PricingService.get_country_pricing(country_code)
                results.append({
                    "code": country_code,
                    **pricing
                })
            except Exception as e:
                print(f"[PRICING] Error getting pricing for {country_code}: {str(e)}")

        return results

    @staticmethod
    def get_operators(country_code: str) -> Dict[str, str]:
        """Get mobile money operators for a country."""
        if country_code not in PricingService.COUNTRIES:
            raise ValueError(f"Country code '{country_code}' not supported")

        return PricingService.COUNTRIES[country_code]["operators"]
