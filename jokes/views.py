import json

from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Player, Session, Response


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
    player: Player = get_object_or_404(Player, pk=player_id)
    with transaction.atomic():
        try:
            session: Session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return HttpResponseRedirect(reverse("landing", args=[player.id]))
        if player.session == session:
            if player.submitted_prompts:
                phase = "questions"
            elif player.is_ready and session.started:
                phase = 'prompts'
            elif player.is_ready:
                phase = 'readied'
            else:
                phase = 'start'
        else:
            if session.started:
                phase = 'waiting'
            else:
                phase = 'start'
            player.session = session
            player.save()
    return render(request, 'jokes/session.html', {
        'session': session,
        'phase': phase,
        'player': player,
        'players': session.player_set.all(),
    })


def get_question(request, player_id, session_id):
    player: Player = get_object_or_404(Player, pk=player_id)
    unanswered_questions = player.get_unanswered_questions()
    response: Response = None
    if unanswered_questions:
        response = unanswered_questions[0]

    ajax_response = {
        "response": response.dict() if response else None,
        "prompt": response.prompt.dict() if response else None,
    }
    return HttpResponse(json.dumps(ajax_response, indent=2))


def get_voting(request, player_id, session_id):
    player: Player = get_object_or_404(Player, pk=player_id)
    session: Session = get_object_or_404(Session, pk=session_id)

    can_vote = True
    response = session.response_set.all().first()
    # get all the responses with the same prompt and session as ^
    responses = response.prompt.response_set.filter(session=session)
    for r in responses:
        if r.player == player:
            can_vote = False
    ajax_response = {
        "prompt": response.prompt.dict(),
        "responses": [r.dict() for r in responses],
        "can_vote": can_vote,
    }
    return HttpResponse(json.dumps(ajax_response, indent=2))
