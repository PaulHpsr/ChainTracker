import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet
from .forms import WalletForm
from web3 import Web3
import json
from web3.middleware import ExtraDataToPOAMiddleware
from django.conf import settings

# Importe la fonction depuis blockchain_tracker/views.py
from blockchain_tracker.views import get_cached_market_data


@login_required
def portfolio_dashboard(request):
    wallets = Wallet.objects.filter(user=request.user)
    portfolio_data = []
    crypto_distribution = {}

    # Mapping CoinGecko IDs
    coin_id_mapping = {
        'ethereum': 'ethereum',
        'bnb': 'binancecoin',
        'polygon': 'matic-network',
    }

    for wallet in wallets:
        wallet_info = {"wallet": wallet}
        crypto_type = wallet.crypto_type

        alchemy_url = settings.ALCHEMY_API_ENDPOINTS.get(crypto_type)

        if alchemy_url:
            web3 = Web3(Web3.HTTPProvider(alchemy_url))

        # Injecter le middleware PoA pour BNB et Polygon
        if crypto_type in ["bnb", "polygon"] and web3:
            web3.middleware_onion.clear()
            web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        if web3 and web3.is_connected():
            try:
                balance_wei = web3.eth.get_balance(wallet.address)
                balance_eth = web3.from_wei(balance_wei, 'ether')
                wallet_info["balance"] = float(balance_eth)
            except Exception as ex:
                wallet_info["balance"] = 0
                wallet_info["error"] = str(ex)
        else:
            wallet_info["balance"] = 0
            wallet_info["error"] = "Connexion au noeud échouée ou Crypto non supportée"

# Utiliser la fonction get_cached_market_data pour récupérer le prix depuis CoinGecko
        coin_id = coin_id_mapping.get(crypto_type)
        if coin_id:
            price, _ = get_cached_market_data(coin_id)
        else:
            price = 0

        wallet_info["price_usd"] = price
        wallet_info["wallet_value_usd"] = wallet_info["balance"] * price

        # Accumuler la répartition
        crypto_name = wallet.get_crypto_type_display()
        crypto_distribution[crypto_name] = crypto_distribution.get(
            crypto_name, 0) + wallet_info["wallet_value_usd"]

        portfolio_data.append(wallet_info)

    # Conversion JSON
    crypto_distrib_json = json.dumps(crypto_distribution)

    context = {
        "portfolio_data": portfolio_data,
        "crypto_distribution": crypto_distribution,
        "crypto_distrib_json": crypto_distrib_json,
    }
    return render(request, "portfolio/dashboard.html", context)


@login_required
def add_wallet(request):
    if request.method == "POST":
        form = WalletForm(request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user
            wallet.save()
            return redirect("portfolio_dashboard")
    else:
        form = WalletForm()
    return render(request, "portfolio/add_wallet.html", {"form": form})


@login_required
def delete_wallet(request, pk):
    wallet = get_object_or_404(Wallet, pk=pk)
    if wallet.user != request.user:
        raise Http404("Vous n'êtes pas autorisé à supprimer ce portefeuille.")
    if request.method == "POST":
        wallet.delete()
        messages.success(request, "Portefeuille supprimé avec succès.")
        return redirect('portfolio_dashboard')
    return render(request, 'portfolio/delete_wallet_confirm.html', {'wallet': wallet})
