from web3 import Web3

# Connect to the Ethereum node
alchemy_url = "https://eth-mainnet.alchemyapi.io/v2/your-api-key"  # Replace with your Alchemy API key
web3 = Web3(Web3.HTTPProvider(alchemy_url))

def main():
    # Get the latest block number
    latest_block = web3.eth.block_number
    print("The latest block number is", latest_block)

if __name__ == "__main__":
    main()