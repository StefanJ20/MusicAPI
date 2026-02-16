from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest
import os
import requests #type: ignore
from django.contrib.auth.decorators import login_required

SC_CLIENT_ID = os.environ["SC_CLIENT_ID"]
SC_CLIENT_SECRET = os.environ["SC_CLIENT_SECRET"]
SC_REDIRECT_URI = os.environ["SC_REDIRECT_URI"] 

@login_required
def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

@require_GET
def soundcloud_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    if not code or not state:
        return HttpResponseBadRequest("Missing code/state")

    return redirect("/finish-login")

@require_POST
def soundcloud_exchange_token(request):
    code = request.POST.get("code")
    code_verifier = request.POST.get("code_verifier")
    redirect_uri = request.POST.get("redirect_uri", SC_REDIRECT_URI)

    if not code or not code_verifier:
        return HttpResponseBadRequest("Missing code or code_verifier")

    resp = requests.post(
        "https://secure.soundcloud.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": SC_CLIENT_ID,
            "client_secret": SC_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": code_verifier,
        },
        headers={"accept": "application/json; charset=utf-8"},
        timeout=20,
    )
    if resp.status_code != 200:
        return JsonResponse({"error": "token_exchange_failed", "details": resp.text}, status=resp.status_code)

    token_json = resp.json()

    # Store these securely server-side (DB tied to your user, or encrypted session):
    request.session["sc_access_token"] = token_json.get("access_token")
    request.session["sc_refresh_token"] = token_json.get("refresh_token")

    return JsonResponse({"ok": True})


@require_GET
def soundcloud_search_tracks(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"collection": [], "next_href": None})

    access_token = request.session.get("sc_access_token")
    if not access_token:
        return JsonResponse({"error": "not_logged_in"}, status=401)

    r = requests.get(
        "https://api.soundcloud.com/tracks",
        params={
            "q": q,
            "access": "playable",
            "limit": 10,
            "linked_partitioning": "true",
        },
        headers={
            "accept": "application/json; charset=utf-8",
            "Authorization": f"OAuth {access_token}",
        },
        timeout=20,
    )
    return JsonResponse(r.json(), status=r.status_code, safe=False)