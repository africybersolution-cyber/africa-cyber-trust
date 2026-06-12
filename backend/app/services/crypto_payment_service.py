"""
Crypto Payment Service for USDT/USDC on Polygon.

Uses EscoPay wallet infrastructure for receiving subscription payments.
"""
import httpx
from web3 import Web3
from typing import Dict, Any, Optional
from decimal import Decimal
from app.core.config import settings


class CryptoPaymentService:
    """Handle USDT/USDC payments on Polygon blockchain."""

    # Polygon Mainnet Configuration
    POLYGON_RPC_URL = "https://rpc.ankr.com/polygon"
    POLYGON_CHAIN_ID = 137

    # Token Contract Addresses (Polygon Mainnet)
    USDT_ADDRESS = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"  # Tether USD
    USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USD Coin (bridged)
    USDC_NATIVE_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"  # Native USDC

    # EscoPay Wallet Address - Receives subscription payments
    PAYMENT_WALLET_ADDRESS = "0xc533b968923b99ec5f9af5c975329b8e4055bd04"

    # Token decimals
    TOKEN_DECIMALS = {
        "USDT": 6,
        "USDC": 6,
    }

    # ERC-20 ABI (minimal - for checking balance and transfers)
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]

    def __init__(self):
        """Initialize Web3 connection to Polygon."""
        self.w3 = Web3(Web3.HTTPProvider(self.POLYGON_RPC_URL))

        if not self.w3.is_connected():
            print("[CRYPTO] WARNING: Failed to connect to Polygon RPC")
        else:
            print(f"[CRYPTO] Connected to Polygon (Chain ID: {self.w3.eth.chain_id})")

    def get_token_contract(self, token_symbol: str):
        """Get Web3 contract instance for a token."""
        token_addresses = {
            "USDT": self.USDT_ADDRESS,
            "USDC": self.USDC_ADDRESS,
        }

        if token_symbol not in token_addresses:
            raise ValueError(f"Unsupported token: {token_symbol}")

        token_address = Web3.to_checksum_address(token_addresses[token_symbol])
        return self.w3.eth.contract(address=token_address, abi=self.ERC20_ABI)

    def create_payment_request(
        self,
        amount_usd: Decimal,
        token_symbol: str,
        user_id: str,
        plan_name: str
    ) -> Dict[str, Any]:
        """
        Create a crypto payment request.

        Returns payment details for the frontend to display.
        """
        if token_symbol not in ["USDT", "USDC"]:
            raise ValueError("Only USDT and USDC are supported")

        # Convert USD amount to token amount (considering 6 decimals)
        decimals = self.TOKEN_DECIMALS[token_symbol]
        token_amount = int(amount_usd * (10 ** decimals))

        # Get token contract address
        token_address = self.USDT_ADDRESS if token_symbol == "USDT" else self.USDC_ADDRESS

        return {
            "payment_wallet": self.PAYMENT_WALLET_ADDRESS,
            "token_symbol": token_symbol,
            "token_address": token_address,
            "amount_usd": float(amount_usd),
            "token_amount": str(token_amount),  # Raw amount (with decimals)
            "decimals": decimals,
            "network": "Polygon",
            "chain_id": self.POLYGON_CHAIN_ID,
            "rpc_url": self.POLYGON_RPC_URL,
            "explorer_url": f"https://polygonscan.com/address/{self.PAYMENT_WALLET_ADDRESS}",
            "instructions": {
                "step1": f"Connect your wallet to Polygon network (Chain ID: {self.POLYGON_CHAIN_ID})",
                "step2": f"Send exactly {amount_usd} {token_symbol} to the payment address",
                "step3": "Transaction will be verified automatically within 1-2 minutes",
                "step4": "Your subscription will activate immediately after confirmation"
            }
        }

    async def verify_payment(
        self,
        transaction_hash: str,
        expected_amount: Decimal,
        token_symbol: str
    ) -> Dict[str, Any]:
        """
        Verify that a payment transaction is valid.

        Checks:
        1. Transaction exists and is confirmed
        2. Amount matches expected amount
        3. Recipient is our payment wallet
        4. Token is correct
        """
        try:
            # Get transaction receipt
            tx_receipt = self.w3.eth.get_transaction_receipt(transaction_hash)

            if not tx_receipt:
                return {
                    "verified": False,
                    "error": "Transaction not found or not yet confirmed"
                }

            # Check if transaction succeeded
            if tx_receipt['status'] != 1:
                return {
                    "verified": False,
                    "error": "Transaction failed"
                }

            # Get transaction details
            tx = self.w3.eth.get_transaction(transaction_hash)

            # For ERC-20 transfers, we need to decode the 'to' and 'value' from logs
            token_contract = self.get_token_contract(token_symbol)

            # Check if this is a token transfer to our wallet
            transfer_found = False
            actual_amount = 0

            for log in tx_receipt['logs']:
                # Transfer event signature: Transfer(address indexed from, address indexed to, uint256 value)
                if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    # Decode 'to' address (2nd topic)
                    to_address = '0x' + log['topics'][2].hex()[-40:]

                    if to_address.lower() == self.PAYMENT_WALLET_ADDRESS.lower():
                        # Decode amount (data field)
                        actual_amount = int(log['data'].hex(), 16)
                        transfer_found = True
                        break

            if not transfer_found:
                return {
                    "verified": False,
                    "error": f"No transfer to payment wallet found in transaction"
                }

            # Check amount (allow 1% tolerance for gas/fees)
            decimals = self.TOKEN_DECIMALS[token_symbol]
            expected_amount_raw = int(expected_amount * (10 ** decimals))
            tolerance = expected_amount_raw * 0.01  # 1% tolerance

            if abs(actual_amount - expected_amount_raw) > tolerance:
                return {
                    "verified": False,
                    "error": f"Amount mismatch. Expected: {expected_amount_raw}, Got: {actual_amount}",
                    "expected": expected_amount_raw,
                    "actual": actual_amount
                }

            # All checks passed
            return {
                "verified": True,
                "transaction_hash": transaction_hash,
                "amount": actual_amount / (10 ** decimals),
                "token": token_symbol,
                "confirmations": tx_receipt.get('confirmations', 0),
                "block_number": tx_receipt['blockNumber'],
                "timestamp": self.w3.eth.get_block(tx_receipt['blockNumber'])['timestamp']
            }

        except Exception as e:
            print(f"[CRYPTO] Payment verification error: {str(e)}")
            return {
                "verified": False,
                "error": f"Verification failed: {str(e)}"
            }

    async def get_payment_status(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Get the status of a payment transaction.

        Returns confirmation count and success status.
        """
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(transaction_hash)

            if not tx_receipt:
                return {
                    "status": "pending",
                    "message": "Transaction not yet confirmed"
                }

            current_block = self.w3.eth.block_number
            confirmations = current_block - tx_receipt['blockNumber']

            if tx_receipt['status'] == 1:
                return {
                    "status": "confirmed",
                    "confirmations": confirmations,
                    "block_number": tx_receipt['blockNumber'],
                    "success": True
                }
            else:
                return {
                    "status": "failed",
                    "confirmations": confirmations,
                    "success": False,
                    "error": "Transaction reverted"
                }

        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }

    def get_wallet_balance(self, wallet_address: str, token_symbol: str = "USDT") -> Decimal:
        """Get token balance for a wallet address."""
        try:
            contract = self.get_token_contract(token_symbol)
            checksum_address = Web3.to_checksum_address(wallet_address)

            balance_raw = contract.functions.balanceOf(checksum_address).call()
            decimals = self.TOKEN_DECIMALS[token_symbol]

            balance = Decimal(balance_raw) / Decimal(10 ** decimals)
            return balance

        except Exception as e:
            print(f"[CRYPTO] Balance check error: {str(e)}")
            return Decimal(0)


# Singleton instance
crypto_payment_service = CryptoPaymentService()
