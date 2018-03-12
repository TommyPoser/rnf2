from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import LogForm, RegForm, PlayerRequestForm
from .models import Player, User
from .defs import execute_query


@login_required(redirect_field_name=None)
def index(request):

    players, rp_form = add_player_render(request) # (tuple může mít i více než dva výstupy)

    if players:
        player = players.filter(pk=request.user.active_player)
    else:
        player = None

    return render(request, 'index.html', {'user': request.user,
                                          'rp_form': rp_form,
                                          'players': players.values_list(),
                                          'player': player,
                                          })


def switch_player(request):
    if Player.objects.filter(user_id=request.user.pk).count() > 1:
        execute_query(
        query="""UPDATE index_user, (SELECT player.id
                                      FROM index_player AS player
                                      LEFT JOIN index_user AS user ON player.user_id = user.id
                                      WHERE user.id = %s AND player.id != user.active_player
                                      LIMIT 1) AS new_id
                 SET active_player = new_id.id
                 WHERE index_user.id = %s""",
        params=[request.user.pk, request.user.pk])
    return redirect('/')


def add_player_render(request):
    rp_form = PlayerRequestForm(request.POST or None)

    if request.POST:
        if request.POST['action'] == 'add_player':
            add_player(request, rp_form)

    players = Player.objects.filter(user_id=request.user.pk)
    num_players = players.count()

    if num_players < 2:
        if num_players == 0:
            rp_form.message = "please create your main character"
        if num_players == 1:
            rp_form.message = "please create your second character"
    else:
        rp_form = None
    return players, rp_form


def add_player(request, add_player_form):
    if add_player_form.is_valid():
        add_player_form = add_player_form.save(commit=False)
        add_player_form.user = request.user
        add_player_form.save()
    return add_player_form


def logout_user(request):
    logout(request)
    return redirect('/')


def login_user(request):
    reg_redirect = request.session.get('reg_redirect')
    request.session['reg_redirect'] = None
    reg_form = RegForm(reg_redirect or None)
    log_form = LogForm(request.POST or None)
    if request.user.is_authenticated():
        return redirect('/')
    if request.POST and log_form.is_valid():
        user = log_form.login(request)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
    return render(request, 'login.html', {"reg_form": reg_form, "log_form": log_form})


def register_user(request):
    reg_form = RegForm(request.POST or None)
    if reg_form.is_valid():
        user = reg_form.register()
        if user is not None:
            if user.is_active:
                login(request, user)
    request.session['reg_redirect'] = request.POST
    return redirect('index:login_user')


