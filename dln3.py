import requests
import json
from solana.rpc.api import Client
from solana.transaction import Transaction, VersionedTransaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import SYS_PROGRAM_ID
from solana.rpc.types import TxOpts
import base64
import os
# Solana setup
solana_client = Client("https://solana-mainnet.g.alchemy.com/v2/KgpuMjqocuyieV47x-HcBYGyi8LrIFb8")
private_key = os.getenv('PRIVATE_KEY') # Your Solana private key
keypair = Keypair.from_secret_key(bytes.fromhex(private_key))
public_key = keypair.public_key

# Function to get a quote
def get_quote(src_chain_id, src_chain_token_in, src_chain_token_in_amount, dst_chain_id, dst_chain_token_out, affiliate_fee_percent, prepend_operating_expenses):
    url = "https://api.dln.trade/v1.0/dln/order/quote"
    params = {
        "srcChainId": src_chain_id,
        "srcChainTokenIn": src_chain_token_in,
        "srcChainTokenInAmount": src_chain_token_in_amount,
        "dstChainId": dst_chain_id,
        "dstChainTokenOut": dst_chain_token_out,
        "dstChainTokenOutAmount": "auto",
        "affiliateFeePercent": affiliate_fee_percent,
        "prependOperatingExpenses": prepend_operating_expenses
    }
    
    response = requests.get(url, params=params)
    quote = response.json()
    return quote

# Function to create and send a transaction
def create_and_send_transaction(quote):
    try:
        # Extract necessary fields from the tx dictionary
        quotetx = quote.get('tx', {})
        nested_tx = quotetx.get('tx', {})
        allowance_target = quotetx.get('allowanceTarget')
        allowance_value = quotetx.get('allowanceValue')
        to = nested_tx.get('to')
        data = nested_tx.get('data')
        value = nested_tx.get('value')

        # Ensure the required fields are not None
        if allowance_target is None or allowance_value is None or to is None or data is None or value is None:
            raise ValueError("Missing required transaction fields: 'allowanceTarget', 'allowanceValue', 'to', 'data', or 'value'")

        # Convert allowance_value to integer
        allowance_value = int(allowance_value)

        # Decode the hex-encoded transaction data
        decoded_data = base64.b64decode(data)

        # Deserialize the transaction
        versioned_tx = VersionedTransaction.deserialize(decoded_data)

        # Sign the transaction
        versioned_tx.sign([keypair])

        # Send the transaction
        response = solana_client.send_raw_transaction(versioned_tx.serialize())
        print(f'Transaction signature: {response["result"]}')

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
quote = get_quote(
    src_chain_id="1",
    src_chain_token_in="SOL",
    src_chain_token_in_amount="1000000",
    dst_chain_id="42161",
    dst_chain_token_out="ETH",
    affiliate_fee_percent="0.1",
    prepend_operating_expenses="true"
)
create_and_send_transaction(quote)