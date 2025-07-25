import os
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware

load_dotenv()

SPONSOR_PRIVATE_KEY = os.getenv("SPONSOR_PRIVATE_KEY")
PROVIDER_URL = os.getenv("PROVIDER_URL")
VANA_TOKEN_ADDRESS = os.getenv("VANA_TOKEN_ADDRESS")

if not SPONSOR_PRIVATE_KEY or not PROVIDER_URL or not VANA_TOKEN_ADDRESS:
    raise Exception("Missing required environment variables.")

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

# Add POA middleware if using a chain like BSC or other POA chains
#w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Minimal ERC20 ABI
VANA_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function",
    },
]

def send_vana_tokens(to_address: str, amount_wei: int):
    account = w3.eth.account.from_key(SPONSOR_PRIVATE_KEY)
    sponsor_address = account.address

    vana_contract = w3.eth.contract(address=VANA_TOKEN_ADDRESS, abi=VANA_ABI)

    # Check ETH balance for gas
    eth_balance = w3.eth.get_balance(sponsor_address)
    if eth_balance < w3.to_wei(0.001, 'ether'):
        raise Exception("Sponsor wallet has insufficient ETH for gas.")

    # Check VANA balance
    vana_balance = vana_contract.functions.balanceOf(sponsor_address).call()
    if vana_balance < amount_wei:
        raise Exception("Sponsor wallet has insufficient VANA tokens.")

    # Prepare transaction
    nonce = w3.eth.get_transaction_count(sponsor_address)
    tx = vana_contract.functions.transfer(to_address, amount_wei).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 100000,  # estimate or set your gas limit
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })

    # Sign transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=SPONSOR_PRIVATE_KEY)

    # Send transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction confirmed in block {receipt.blockNumber}")

    return receipt

if __name__ == "__main__":
    # Example: send 0.01 VANA with 18 decimals
    recipient = "0xUserWalletAddressHere"
    amount = w3.to_wei(0.01, 'ether')  # Adjust decimals if needed

    send_vana_tokens(recipient, amount)
