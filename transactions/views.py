import json
from hexbytes import HexBytes
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from .services import (
    connect_alchemy,
    fetch_latest_block,
    extract_transactions,
    get_bitcoin_latest_blockhash,
    get_bitcoin_block,
    extract_bitcoin_transactions,
)
from web3.middleware import ExtraDataToPOAMiddleware
import logging

logger = logging.getLogger(__name__)


def clean_hexbytes(obj):
    """Convert recursively HexBytes objects to hex strings in dicts/lists."""
    if isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, dict):
        return {k: clean_hexbytes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_hexbytes(i) for i in obj]
    else:
        return obj


def transactions_view(request):
    chain = request.GET.get("chain", "ethereum")

    if chain in ["ethereum", "bnb", "polygon"]:
        alchemy_url = settings.ALCHEMY_API_ENDPOINTS.get(chain)
        try:
            web3 = connect_alchemy(alchemy_url)
            if chain in ["bnb", "polygon"]:
                web3.middleware_onion.clear()
                web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

            block = fetch_latest_block(web3)
            df = extract_transactions(web3, block)
            transactions = df.to_dict(orient='records')

            # Nettoyage des HexBytes dans transactions
            cleaned_transactions = clean_hexbytes(transactions)
            transactions_json = json.dumps(cleaned_transactions)

            gas_price = web3.from_wei(web3.eth.gas_price, 'gwei')
            last_block = web3.eth.block_number
            stats = {
                'gas_price': f"{gas_price} Gwei",
                'last_block': last_block,
            }
            error_message = None
        except Exception as e:
            logger.exception("Erreur Ethereum-like")
            transactions = []
            transactions_json = json.dumps([])
            stats = {}
            error_message = str(e)

    elif chain == "bitcoin":
        try:
            block_hash = get_bitcoin_latest_blockhash()
            block_data = get_bitcoin_block(block_hash)
            df = extract_bitcoin_transactions(block_data)
            transactions = df.to_dict(orient='records')
            transactions_json = json.dumps(transactions)

            stats = {
                "last_block_hash": block_hash,
                "nb_transactions": len(df),
                "gas_price": "N/A",
            }
            error_message = None
        except Exception as e:
            logger.exception("Erreur BTC")
            transactions = []
            transactions_json = json.dumps([])
            stats = {}
            error_message = f"Erreur lors de la récupération des données Bitcoin : {e}"
    else:
        transactions = []
        transactions_json = json.dumps([])
        stats = {}
        error_message = "Chaîne non supportée."

    context = {
        'transactions': transactions,
        'transactions_json': transactions_json,
        'stats': stats,
        'last_updated': timezone.now(),
        'error_message': error_message,
        'selected_chain': chain,
    }
    return render(request, 'transactions/transactions_list.html', context)
