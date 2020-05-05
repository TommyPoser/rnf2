from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Case, When, Sum, F, Min, Value, CharField, BooleanField, Q
import json, random
from index.defs import get_array, execute_query
from inventory.models import Inventory
from index.models import Player
from recon.models import Animal, Hunt
from map.models import Hexa
from inventory.views import make_grid

craft_box_range = [21, 26]


@login_required(redirect_field_name=None)
def index(request):

    player, hexa, animals, situation_instance = entry(request)

    state = ['', 'attacking', 'running', 'dead']

    animals_with_state = []
    for animal in animals:
        print(animal)
        animals_with_state.append(animal + (state[animal[3]],) )

    grid = make_grid(request, grid_max=34)
    slices = [6, 11, 16, 21, 24, 27, 29, 31, 33]

    if not hexa[5]:
        pass
    else:
        pass

    return render(request, 'recon.html', {'animals': animals_with_state,
                                          'grid': grid,
                                          'slices': slices,
                                          'craft_box_start': craft_box_range[0],
                                          'animals_start': craft_box_range[1]+1,
                                          })


def recon(request):
    if request.is_ajax():
        if request.method == 'POST':
            player, hexa, situation_list, situation = entry(request)
            animals, status = move(player, hexa, situation)
            return JsonResponse([animals, status], safe=False)


def leave_button(request):
    if request.is_ajax():
        if request.method == 'POST':
            animals, status, remaining = leave(request)
            return JsonResponse([animals, status], safe=False)


def leave(request):
    player, hexa, situation_list, situation = entry(request)
    attacking = situation.filter(behaviour=1)
    remaining = False
    for attacker in attacking:
        if random.randint(0, 100) < 75:
            attacker.delete()
        else:
            remaining = True

    animals, status = move(player, hexa, situation, leaving=True)
    return animals, status, remaining




def shot(request):
    if request.is_ajax():
        if request.method == 'POST':
            animal_number = json.loads(request.body.decode('utf-8'))
            hunt = Hunt.objects.filter(id=animal_number, player_id=request.user.active_player)

            animal = hunt.select_related('animal')\
                .values_list('hit_chance', 'hits', 'animal__shots', 'animal__aggression', 'behaviour',
                             'animal__meat', 'animal__leather', 'animal__feather', 'animal__scales', 'animal__venom')[0]

            Hunt.objects.filter(player_id=request.user.active_player, behaviour=2).exclude(id=animal_number).delete()

            status = 'miss'

            player, hexa, situation_list, situation = entry(request)

            if animal[0] >= random.randint(0, 100):
                status = 'hit'
                if int(animal[1])+1 >= animal[2]:
                    hunt.update(behaviour=3)
                    status = 'dead'
                    pos = craft_box_range[1]+1+(hunt[0].slot*2)
                    second = False
                    for i in range(1, 6):
                        if animal[i+4]:
                            if second: pos += 1
                            Inventory(player=player[0], pos=pos, consume_items_id=i, amount=animal[i+4]).save()
                            second = True
                else:
                    run_chance = random.randint(0, 14)*10+random.randint(0, 10)
                    if animal[4] != 1 and run_chance > animal[3]:
                        hunt.update(behaviour=2, hits=F('hits') + 1)
                    else:
                        hunt.update(behaviour=1, hits=F('hits') + 1)
            else:
                if animal[4]:
                    hunt.exclude(behaviour=1 or 3).delete()

            animals = on_place(player, hexa, situation)

            return JsonResponse([animals, status], safe=False)


def drag_and_drop(request):
    if request.is_ajax():
        if request.method == 'POST':
            arr = json.loads(request.body.decode('utf-8'))
            execute_query(
                query="""UPDATE inventory_inventory SET pos = %s
                         WHERE player_id = %s AND id = %s""",
                params=[arr["entNumber"], request.user.active_player, arr["dragNumber"]])

            animals = []

            if arr['initNumber'] > craft_box_range[1]:
                animals = loot(request)

            return JsonResponse(animals, safe=False)


def loot(request):
    player, hexa, situation_list, situation = entry(request)
    animals = on_place(player, hexa, situation)
    inventory = Inventory.objects.filter(player=request.user.active_player, pos__gt=craft_box_range[1]).values_list('pos')

    status = 'looting'

    for dead in situation.filter(behaviour=3):
        if dead.slot+craft_box_range[1] not in inventory:
            status += ' | '+str(dead.slot)

    return [animals, status]


def entry(request):
    player = Player.objects.filter(pk=request.user.active_player)
    hexa = player.select_related('pos') \
        .values_list('pos__grass', 'pos__wood', 'pos__hills', 'pos__mountains', 'pos__water', 'pos__town')[0]

    print('grass %d, wood %d, hills %d, mountains %d, water %d' % (hexa[0], hexa[1], hexa[2], hexa[3], hexa[4]))

    if not hexa[5]:
        situation_instance = Hunt.objects.filter(player=request.user.active_player).select_related('animal')
        situation = list(situation_instance.values_list('id', 'animal__name', 'hit_chance', 'behaviour', 'slot'))
    else:
        situation = None
        situation_instance = None

    return player, hexa, situation, situation_instance


def move(player, hexa, situation, leaving=False):
    animals = []

    attacking = situation.filter(behaviour=1).select_related('animal')\
        .values_list('id', 'animal__name', 'animal__size', 'hits', 'slot')

    for attacker in attacking:
        hit_chance = attacker[2] - random.randint(0, 30 - 12 * attacker[3])
        animals.append([attacker[0], attacker[1], hit_chance, 1, attacker[4]])

    if situation:
        situation.exclude(behaviour=1).delete()

    Inventory.objects.filter(player=player[0], pos__gt=craft_box_range[1]).delete()

    status = ''

    if not leaving:
        for s in range(4):
            if situation.filter(slot=s):
                continue
            animals, status = spawn_animal(animals, hexa, player, s)

    return animals, status


def on_place(player, hexa, situation):
    animals = []

    no_idles = situation.exclude(behaviour=0).select_related('animal')\
        .values_list('id', 'animal__name', 'animal__size', 'hits', 'behaviour', 'slot')

    for no_idle in no_idles:
        hit_chance = no_idle[2] - random.randint(0, 30) + 12 * no_idle[3]
        animals.append([no_idle[0], no_idle[1], hit_chance, no_idle[4], no_idle[5]])

    if situation:
        situation.filter(behaviour=0).delete()

    startled = random.randint(1, 3)
    print('startled %d' % startled)

    for s in range(4):
        if situation.filter(slot=s):
            continue
        if startled > 0:
            startled -= 1
            continue
        animals = spawn_animal(animals, hexa, player, s)
    return animals


def spawn_animal(animals, hexa, player, s):
    aim = random.randint(0, 660)
    biome = 0
    status = ''
    for i in range(5):
        biome += hexa[i]
        if aim < biome:
            shot = random.randint(0, 100)
            animal_instance = Animal.objects.filter(biome=i, presence__gte=shot).order_by('presence')
            animal = animal_instance.values_list('id', 'name', 'aggression', 'shots', 'size').first()
            if animal:
                if animal[0] < 12:
                    attack_chance = random.randint(0, 9) * 10 + random.randint(0, 10)
                    behaviour = 1 if attack_chance <= animal[2] else 0
                    hit_chance = animal[4] - random.randint(0, 18 if behaviour == 1 else 30)
                else:
                    behaviour = 3
                    hit_chance = 0

                    pos = craft_box_range[1] + 1 + s * 2
                    Inventory(player=player[0], pos=pos, consume_items_id=7, amount=random.randint(1, 3)).save()
                    status = 'items'

                hunt = Hunt(player=player[0], animal=animal_instance[0], behaviour=behaviour,
                            hit_chance=hit_chance, slot=s)
                hunt.save()
                animals.append([hunt.pk, animal[1], hit_chance, behaviour, s])
            break
    return animals, status



