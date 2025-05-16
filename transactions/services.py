import pandas as pd
from web3 import Web3
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def connect_alchemy(url):
    web3 = Web3(Web3.HTTPProvider(url))
    if not web3.is_connected():
        logger.error("Impossible de se connecter à Alchemy via %s", url)
        raise Exception("Erreur : Impossible de se connecter à Alchemy.")
    logger.info("Connexion à Alchemy réussie.")
    return web3


def fetch_latest_block(web3):
    block_number = web3.eth.block_number
    block = web3.eth.get_block(block_number, full_transactions=True)
    return block


def extract_transactions(web3, block):
    """
    Extrait les transactions du bloc Ethereum-like et retourne un DataFrame.
    """
    transactions = []

    # Récupération sécurisée des transactions suivant le type du bloc
    txs = None
    if isinstance(block, dict):
        txs = block.get("transactions", [])
    else:
        txs = getattr(block, "transactions", [])

    for tx in txs:
        try:
            transactions.append({
                "hash": tx.hash.hex() if hasattr(tx, "hash") else tx["hash"],
                "from": tx["from"] if isinstance(tx, dict) and "from" in tx else getattr(tx, "from", None),
                "to": tx.get("to") if isinstance(tx, dict) else getattr(tx, "to", None),
                "value": float(web3.from_wei(tx["value"], 'ether') if isinstance(tx, dict) else web3.from_wei(tx.value, 'ether')),
                "gas": tx["gas"] if isinstance(tx, dict) else tx.gas,
                "gasPrice": float(web3.from_wei(tx["gasPrice"], 'gwei') if isinstance(tx, dict) else web3.from_wei(tx.gasPrice, 'gwei')),
            })
        except Exception as e:
            tx_identifier = tx.hash.hex() if hasattr(tx, "hash") else (
                tx.get("hash") if isinstance(tx, dict) else "inconnu")
            logger.error(
                "Erreur lors du traitement de la transaction %s : %s", tx_identifier, e)
    df = pd.DataFrame(transactions)
    logger.info("Nombre de transactions extraites : %d", len(df))
    return df

# --- Bitcoin ---


def get_bitcoin_latest_blockhash():
    """
    Récupère le hash du dernier bloc Bitcoin via Alchemy.
    """
    alchemy_btc_url = settings.ALCHEMY_API_ENDPOINTS.get("bitcoin")
    if not alchemy_btc_url:
        raise Exception("URL Alchemy Bitcoin non configurée")

    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getbestblockhash",
        "params": []
    }
    response = requests.post(alchemy_btc_url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    return result.get("result")


def get_bitcoin_block(block_hash):
    """
    Récupère un bloc Bitcoin complet (avec transactions) via Alchemy.
    """
    alchemy_btc_url = settings.ALCHEMY_API_ENDPOINTS.get("bitcoin")
    if not alchemy_btc_url:
        raise Exception("URL Alchemy Bitcoin non configurée")

    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getblock",
        # True pour récupérer les transactions complètes
        "params": [block_hash, True]
    }
    response = requests.post(alchemy_btc_url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def extract_bitcoin_transactions(block_data):
    """
    Transforme les transactions Bitcoin en DataFrame.
    Gère à la fois le cas où chaque transaction est un dictionnaire détaillé
    et le cas où c'est simplement une chaîne (hash).
    """
    transactions = []
    block = block_data.get("result", {})
    txs = block.get("tx", [])
    for tx in txs:
        try:
            if isinstance(tx, str):
                transactions.append({
                    "hash": tx,
                    "inputs": None,
                    "outputs": None,
                    "confirmations": block.get("confirmations", 0),
                })
            elif isinstance(tx, dict):
                transactions.append({
                    "hash": tx.get("hash", "N/A"),
                    "inputs": tx.get("vin", []),
                    "outputs": tx.get("vout", []),
                    "confirmations": block.get("confirmations", 0),
                })
            else:
                logger.error("Format de transaction BTC inconnu : %s", tx)
        except Exception as e:
            logger.error(
                "Erreur lors du traitement d'une transaction BTC : %s", e)
    df = pd.DataFrame(transactions)
    logger.info("Nombre de transactions BTC extraites : %d", len(df))
    return df
