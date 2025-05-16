
import os
from django.conf import settings
from django.shortcuts import render
from web3 import Web3
import requests
from django.core.cache import cache


def get_market_data(api_url):
    """
    Récupère via CoinGecko le prix en USD et la capitalisation d'une cryptomonnaie
    à partir de l'URL API fournie.
    """
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    price = data['market_data']['current_price']['usd']
    market_cap = data['market_data']['market_cap']['usd']
    return price, market_cap


def get_bitcoin_data():
    """
    Envoie une requête JSON-RPC à l'endpoint Bitcoin d'Alchemy.
    La méthode 'getblockchaininfo' est utilisée (à adapter selon la documentation).
    """
    url = settings.ALCHEMY_API_ENDPOINTS.get("bitcoin")
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getblockchaininfo",
        "params": []
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_solana_data():
    """
    Envoie une requête JSON-RPC à l'endpoint Solana d'Alchemy.
    On utilise ici la méthode 'getLatestBlockhash'.
    """
    url = settings.ALCHEMY_API_ENDPOINTS.get("solana")
    headers = {"Content-Type": "application/json"}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLatestBlockhash",
        "params": []
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_cached_market_data(coin_id, timeout=120):
    """
    Récupère les données de marché depuis CoinGecko pour le coin spécifié.
    Le résultat est mis en cache pendant `timeout` secondes.
    """
    cache_key = f"coingecko_market_data_{coin_id}"
    data = cache.get(cache_key)
    if data is None:
        market_data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        try:
            data = get_market_data(market_data_url)
        except Exception as e:
            data = ("Non disponible", "Non disponible")
        cache.set(cache_key, data, timeout)
    return data


def home_view(request):
    chain = request.GET.get("chain", "ethereum")
    ALCHEMY_URL = settings.ALCHEMY_API_ENDPOINTS.get(chain)
    if not ALCHEMY_URL:
        chain = "ethereum"
        ALCHEMY_URL = settings.ALCHEMY_API_ENDPOINTS.get("ethereum")

    coin_ids = {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "bnb": "binancecoin",
        "solana": "solana",
        "polygon": "matic-network",
    }
    coin_id = coin_ids.get(chain, "ethereum")

    #  fonction de cache pour récupérer les données de marché
    price, cap = get_cached_market_data(coin_id, timeout=120)

    # Pour les chaînes EVM – utiliser Web3
    evm_chains = ["ethereum", "bnb", "polygon"]
    if chain in evm_chains:
        web3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
        if not web3.is_connected():
            extra_stats = {
                "gas_price": "Non disponible",
                "last_finalized_block": "Non disponible",
                "last_safe_block": "Non disponible",
                "tps": "Non disponible",
            }
            error_message = "Erreur lors de la connexion à l'API Alchemy."
        else:
            gas_price_gwei = web3.from_wei(web3.eth.gas_price, 'gwei')
            last_block = web3.eth.block_number
            extra_stats = {
                "gas_price": f"{gas_price_gwei} Gwei",
                "last_finalized_block": f"{last_block}",
                "last_safe_block": f"{last_block}",
                "tps": "17.3 TPS",
            }
            error_message = None
    elif chain == "bitcoin":
        try:
            btc_data = get_bitcoin_data()
            result = btc_data.get("result", {})
            block_height = result.get("blocks", "Non disponible")
            best_block_hash = result.get("bestblockhash", "Non disponible")
            extra_stats = {
                "gas_price": "N/A",
                "last_finalized_block": f"Block height: {block_height}",
                "last_safe_block": f"Best block hash: {best_block_hash}",
                "tps": "N/A",
            }
            error_message = None
        except Exception as e:
            extra_stats = {
                "gas_price": "Non disponible",
                "last_finalized_block": "Non disponible",
                "last_safe_block": "Non disponible",
                "tps": "Non disponible",
            }
            error_message = "Erreur lors de la récupération des données Bitcoin."
    elif chain == "solana":
        try:
            sol_data = get_solana_data()
            result_value = sol_data.get("result", {}).get("value", {})
            blockhash = result_value.get("blockhash", "Non disponible")
            last_valid_block_height = result_value.get(
                "lastValidBlockHeight", "Non disponible")
            extra_stats = {
                "gas_price": "N/A",
                "last_finalized_block": f"Last valid block height: {last_valid_block_height}",
                "last_safe_block": f"Blockhash: {blockhash}",
                "tps": "N/A",
            }
            error_message = None
        except Exception as e:
            extra_stats = {
                "gas_price": "Non disponible",
                "last_finalized_block": "Non disponible",
                "last_safe_block": "Non disponible",
                "tps": "Non disponible",
            }
            error_message = "Erreur lors de la récupération des données Solana."
    else:
        extra_stats = {
            "gas_price": "Non disponible",
            "last_finalized_block": "Non disponible",
            "last_safe_block": "Non disponible",
            "tps": "Non disponible",
        }
        error_message = None

    stats = {
        "price": price,
        "market_cap": cap,
    }
    stats.update(extra_stats)

    context = {
        "title": f"{chain.upper()} Tracker",
        "message": f"Bienvenue sur {chain.upper()} Tracker, votre explorateur de blockchain.",
        "stats": stats,
        "error_message": error_message,
        "selected_chain": chain,
    }

    return render(request, "home.html", context)
