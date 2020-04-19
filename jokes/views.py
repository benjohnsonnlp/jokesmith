from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Player, Session


def index(request):
    return render(request, "jokes/index.html")


def login(request):
    name = request.POST["username"]
    player, _ = Player.objects.get_or_create(name=name)

    return HttpResponseRedirect(reverse("landing", args=[player.id]))


def player(request, player_id):
    player = Player.objects.get(pk=player_id)
    sessions = Session.objects.filter()
    context = {
        "player": player,
        "sessions": sessions,
    }
    return render(request, "jokes/landing.html", context=context)


def add_session(request):
    name = request.POST["name"]
    session, _ = Session.objects.get_or_create(name=name)

    player = get_object_or_404(Player, pk=request.POST["player_id"])
    player.session = session
    player.save()
    return HttpResponseRedirect(reverse("session", args=[player.id, session.id]))


def session(request, player_id, session_id):
    session: Session = get_object_or_404(Session, pk=session_id)
    player: Player = get_object_or_404(Player, pk=player_id)
    player.session = session
    player.save()
    return render(request, 'jokes/session.html', {
        'session': session,
        'player': player,
    })
