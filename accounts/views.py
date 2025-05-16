# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def signup_view(request):
    """
    Vue pour l'inscription des nouveaux utilisateurs.
    Utilise le formulaire UserCreationForm intégré par Django.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Inscription réussie. Vous pouvez maintenant vous connecter.")
            return redirect('login')  # redirige vers la page de connexion, dont le nom d'URL est 'login'
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserCreationForm()
    
    return render(request, "registration/signup.html", {"form": form})
