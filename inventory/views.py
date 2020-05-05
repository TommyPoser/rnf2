from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from index.defs import get_array, execute_query
from django.http import JsonResponse
import json
from django.db.models import Case, When, Sum, F, Min, Value, CharField, BooleanField, IntegerField, Q
from django.db.models.functions import Coalesce
from inventory.models import Inventory, ConsumeItems, CraftItems, CraftRequirements, Weapon, Weapons, Armors, Shield, Shields, Semiproduct
from index.models import Player

craft_box_range = [21, 26]


@login_required(redirect_field_name=None)
def index(request):

    items = list(Inventory.objects
        .filter(player=request.user.active_player, pos__lt=craft_box_range[0], amount__gt=0)\
        .select_related('consume_items').order_by('consume_items__id')\
        .annotate(item_id=Case(
            When(consume_items__isnull=False, then='consume_items__id'),
            When(craft_items__isnull=False, then=F('craft_items__id')+Value(10000)),
                 output_field=IntegerField()))
        .annotate(max_stack=Case(
            When(consume_items__isnull=False, then='consume_items__max_stack'),
            When(craft_items__isnull=False, then='craft_items__max_stack'),
                 output_field=IntegerField()))
        .values_list('id', 'item_id', 'amount', 'max_stack')
    )

    deleted = 0
    for i in range(1, len(items)):
        j = i-1-deleted
        items[j] = list(items[j])
        items[i] = list(items[i])
        if items[j][1] == items[i][1] and items[j][2] < items[j][3]:
            total = items[i][2]+items[j][2]
            if total <= items[j][3]:
                items[j][2] = total
                deleted += 1
                Inventory.objects.filter(id=items[j][0]).update(amount=total)
                Inventory.objects.filter(id=items[i][0]).delete()
            else:
                items[j][2] = items[j][3]
                items[i][2] = total-items[i][3]
                Inventory.objects.filter(id=items[j][0]).update(amount=items[i][3])
                Inventory.objects.filter(id=items[i][0]).update(amount=total-items[i][3])

    grid = make_grid(request, grid_max=26)
    slices = [6, 11, 16, 21, 24]

    craft = CraftItems.objects.values_list('name', 'id') \
        .union(Weapons.objects.values_list('name', F('id') + 1000),
               Armors.objects.values_list('name', F('id') + 2000),
               Shields.objects.values_list('name', F('id') + 3000)
               )

    return render(request, 'inventory.html', {'grid': grid,
                                              'slices': slices,
                                              'craft_box_start': craft_box_range[0],
                                              'craft': craft})


def make_grid(request, grid_max):
    items = Inventory.objects.filter(player=request.user.active_player) \
        .select_related('consume_items', 'craft_items'
                        'weapon', 'weapon__static',
                        'armor', 'armor__static',
                        'shield', 'shield__static',
                        'semiproduct') \
        .annotate(name=Case(
            When(consume_items__isnull=False, then='consume_items__name'),
            When(craft_items__isnull=False, then='craft_items__name'),
            When(weapon__isnull=False, then='weapon__static__name'),
            When(armor__isnull=False, then='armor__static__name'),
            When(shield__isnull=False, then='shield__static__name'),
            When(semiproduct__isnull=False, then=Value('component')),
            output_field=CharField(max_length=20),
                )) \
        .annotate(level=Case(
            When(weapon__isnull=False, then='weapon__level'),
            When(semiproduct__isnull=False, then='semiproduct__level'),
            default=Value(''),
            output_field=CharField(max_length=2),
                )) \
        .annotate(steel=Case(
            When(weapon__isnull=False, then='weapon__static__steel'),
            When(armor__isnull=False, then='armor__static__steel'),
            When(shield__isnull=False, then='shield__static__steel'),
            When(semiproduct__isnull=False, then='semiproduct__steel'),
            default=Value(''),
            output_field=CharField(max_length=2),
                )) \
        .annotate(wood=Case(
            When(weapon__isnull=False, then='weapon__static__wood'),
            When(armor__isnull=False, then='armor__static__wood'),
            When(shield__isnull=False, then='shield__static__wood'),
            When(semiproduct__isnull=False, then='semiproduct__wood'),
            default=Value(''),
            output_field=CharField(max_length=2),
                )) \
        .annotate(leather=Case(
            When(weapon__isnull=False, then='weapon__static__leather'),
            When(armor__isnull=False, then='armor__static__leather'),
            When(shield__isnull=False, then='shield__static__leather'),
            When(semiproduct__isnull=False, then='semiproduct__leather'),
            default=Value(''),
            output_field=CharField(max_length=2),
                )) \
        .annotate(not_null_amount=Case(
            When(amount__isnull=False, then='amount'),
            default=Value(''),
            output_field=CharField(max_length=2),
                )) \
        .values_list('id', 'pos', 'not_null_amount', 'name', 'level', 'steel', 'wood', 'leather', 'equip').order_by('pos')

    grid = []
    j = 1

    for item in items:
        while j < item[1] and j <= grid_max:
            grid.append(None)
            j += 1
        if j <= grid_max:
            grid.append(item)
            j += 1

    while j <= grid_max:
        grid.append(None)
        j += 1
    return grid


def equip(request, item_id):
    if item_id:
        item = Inventory.objects.filter(player=request.user.active_player, id=item_id)\
            .select_related('weapon__static', 'armor__static')\
            .values_list('weapon_id', 'shield_id', 'weapon__static__twohand',
                         'armor_id', 'armor__static__body_part')[0]

        if item[0] or item[1]:   # weapon or shield
            if item[2] is False or item[2] is None:   # new twohand
                equiped_count = Inventory.objects\
                    .filter(player=request.user.active_player, equip=2).count()
                twohand = Inventory.objects.filter(player=request.user.active_player, equip=2) \
                            .select_related('weapon__static').filter(weapon__static__twohand=True)
                if equiped_count > 1 or twohand:
                    execute_query(
                    query="""UPDATE inventory_inventory SET equip = 1
                             WHERE player_id = %s AND inventory_inventory.equip = 2 LIMIT 1""",
                    params=[request.user.active_player])
            else:
                Inventory.objects\
                    .filter(player=request.user.active_player, equip=2)\
                    .update(equip=1)

            Inventory.objects.filter(player=request.user.active_player, id=item_id)\
                .filter(Q(weapon__isnull=False) | Q(shield__isnull=False)).update(equip=2)
        elif item[3]:   # armor_id
            Inventory.objects \
                .filter(player=request.user.active_player, armor__isnull=False, equip=item[4]) \
                .update(equip=1)
            Inventory.objects.filter(player=request.user.active_player, id=item_id, armor__isnull=False)\
                .update(equip=item[4])

    return redirect('/inventory/')


def unequip(request, item_id):
    if item_id:
        Inventory.objects.filter(player=request.user.active_player, id=item_id).update(equip=1)
    return redirect('/inventory/')


def drag_and_drop(request):
    if request.is_ajax():
        if request.method == 'POST':
            arr = json.loads(request.body.decode('utf-8'))
            execute_query(
                query="""UPDATE inventory_inventory SET pos = %s
                         WHERE player_id = %s AND id = %s""",
                params=[arr["entNumber"], request.user.active_player, arr["dragNumber"]])

            craft_item = {}
            if arr['toCraft']:
                to_craft = int(arr['toCraft'])

                if to_craft > 3000:
                    to_craft_id = to_craft - 3000
                    craft_item = shield_craft(request=request, to_craft_id=to_craft_id)
                elif to_craft > 2000:
                    to_craft_id = to_craft - 2000
                elif to_craft > 1000:
                    to_craft_id = to_craft - 1000
                    craft_item = weapon_craft(request=request, to_craft_id=to_craft_id)
                else:
                    to_craft_id = to_craft

                arr.update(craft_item)

            return JsonResponse(arr, safe=False)


def make_item(request):
    if request.method == 'POST':

        please = False

        if 'please' in request.POST:
            please = True

        to_craft = int(request.POST['craft'])

        if to_craft > 3000:
            to_craft_id = to_craft - 3000
            make_shield(request=request, to_craft_id=to_craft_id, please=please)
        elif to_craft > 2000:
            to_craft_id = to_craft - 2000
        elif to_craft > 1000:
            to_craft_id = to_craft - 1000
            make_weapon(request=request, to_craft_id=to_craft_id, please=please)
        else:
            craft_item(request, to_craft)

    return redirect('/inventory/')


def craft_item(request, to_craft_id):

    requirements = list(CraftRequirements.objects.filter(craft_item_id=to_craft_id).values_list('consume_item_id', 'consume_amount', 'craft_amount'))
    print(requirements[0][2])
    build = False
    sumitems = []

    for requirement in requirements:
        amount = Inventory.objects.filter(player=request.user.active_player, pos__range=craft_box_range,
                                          consume_items_id=requirement[0])\
                    .aggregate(amount=Sum(Coalesce(F('amount'), 0)))['amount']
        sumitems.append([requirement[0], amount, requirement[1]])
        build = True if amount >= requirement[1] else False

    if build:
        pos = 0
        for sumitem in sumitems:
            required_amount = sumitem[2]
            items = Inventory.objects.filter(player=request.user.active_player, pos__range=craft_box_range,
                                             consume_items_id=sumitem[0]).values_list('id', 'amount')
            for item in items:
                if item[1] <= required_amount:
                    instance = Inventory.objects.filter(id=item[0])
                    pos = instance.values_list('pos')[0][0]
                    instance.delete()
                    required_amount -= item[1]
                else:
                    Inventory.objects.filter(id=item[0]).update(amount=(item[1]-required_amount))

        player_instance = Player.objects.get(id=request.user.active_player)
        craft_items_instance = CraftItems.objects.get(id=to_craft_id)
        print(craft_items_instance)
        Inventory(player=player_instance, pos=pos, craft_items=craft_items_instance, amount=requirements[0][2]).save()

    return None


def make_weapon(request, to_craft_id, please):
    craft_weapon = weapon_craft(request=request, to_craft_id=to_craft_id)
    weapon_to_craft = Weapons.objects.get(id=to_craft_id)
    level = craft_weapon['level']
    rest_steel = craft_weapon['rest_steel']
    rest_wood = craft_weapon['rest_wood']
    rest_leather = craft_weapon['rest_leather']
    rest_level = craft_weapon['rest_level']

    if craft_weapon['build'] or please:

        craft_consumption(request, craft_weapon)

        new_weapon = Weapon(static=weapon_to_craft, level=level, quality=1, dur=1)
        new_weapon.save()
        player_instance = Player.objects.get(id=request.user.active_player)
        Inventory(player=player_instance, pos=(craft_box_range[0]), weapon=new_weapon, equip=1).save()

        if rest_steel or rest_wood or rest_leather:
            semiproduct = Semiproduct(level=rest_level, steel=rest_steel, wood=rest_wood, leather=rest_leather)
            semiproduct.save()
            Inventory(player=player_instance, pos=(craft_box_range[0]+1), semiproduct=semiproduct).save()
    return None


def make_shield(request, to_craft_id, please):
    craft_weapon = shield_craft(request=request, to_craft_id=to_craft_id)
    shield_to_craft = Shields.objects.get(id=to_craft_id)
    level = craft_weapon['level']
    rest_steel = craft_weapon['rest_steel']
    rest_wood = craft_weapon['rest_wood']
    rest_leather = craft_weapon['rest_leather']
    rest_level = craft_weapon['rest_level']

    if craft_weapon['build'] or please:

        craft_consumption(request, craft_weapon)

        new_weapon = Shield(static=shield_to_craft, level=level, quality=1)
        new_weapon.save()
        player_instance = Player.objects.get(id=request.user.active_player)
        Inventory(player=player_instance, pos=(craft_box_range[0]), shield=new_weapon, equip=1).save()

        if rest_steel or rest_wood or rest_leather:
            semiproduct = Semiproduct(level=rest_level, steel=rest_steel, wood=rest_wood, leather=rest_leather)
            semiproduct.save()
            Inventory(player=player_instance, pos=(craft_box_range[0]+1), semiproduct=semiproduct).save()
    return None


def weapon_craft(request, to_craft_id):
    weapon_to_craft = Weapons.objects.get(id=to_craft_id)
    required_steel = weapon_to_craft.steel
    required_wood = weapon_to_craft.wood
    required_leather = weapon_to_craft.leather

    crafting = craft_box(request, weapon_to_craft, required_steel, required_wood, required_leather)
    return crafting


def shield_craft(request, to_craft_id):
    shield_to_craft = Shields.objects.get(id=to_craft_id)
    required_steel = shield_to_craft.steel
    required_wood = shield_to_craft.wood
    required_leather = shield_to_craft.leather

    crafting = craft_box(request, shield_to_craft, required_steel, required_wood, required_leather)
    return crafting


def craft_consumption(request, craft_weapon):
    for weapon in craft_weapon['weapon_to_delete']:
        Weapon.objects.filter(id=weapon).delete()
    for semiproduct in craft_weapon['semiproduct_to_delete']:
        Semiproduct.objects.filter(id=semiproduct).delete()
    for shield in craft_weapon['shield_to_delete']:
        Shield.objects.filter(id=shield).delete()

    coal = craft_weapon['coal']

    coal_stacks = Inventory.objects \
        .filter(player=request.user.active_player,
                pos__range=craft_box_range) \
        .select_related('craft_items') \
        .filter(craft_items__name='coal') \
        .order_by('amount') \
        .values_list('id', 'amount')

    i = craft_box_range[0] + 2
    for coal_stack in coal_stacks:
        if coal_stack[1] <= coal:
            coal -= coal_stack[1]
            Inventory.objects.filter(id=coal_stack[0]).delete()
        else:
            Inventory.objects.filter(id=coal_stack[0]).update(amount=(coal_stack[1] - coal), pos=i)
            coal = 0
            i += 1
    return None


def craft_box(request, weapon_to_craft, required_steel, required_wood, required_leather):

    craft_box_weapons = Inventory.objects.filter(player=request.user.active_player,
                                                 pos__range=craft_box_range) \
        .select_related('weapon', 'weapon__static', 'semiproduct', 'shield', 'shield__static') \
        .annotate(level=Case(
            When(weapon__isnull=False, then='weapon__level'),
            When(semiproduct__isnull=False, then='semiproduct__level'),
            When(shield__isnull=False, then='shield__level'),
            default=0.0
        )) \
        .annotate(steel=Case(
            When(weapon__isnull=False, then='weapon__static__steel'),
            When(semiproduct__isnull=False, then='semiproduct__steel'),
            When(shield__isnull=False, then='shield__static__steel'),
            default=0.0
        )) \
        .annotate(wood=Case(
            When(weapon__isnull=False, then='weapon__static__wood'),
            When(semiproduct__isnull=False, then='semiproduct__wood'),
            When(shield__isnull=False, then='shield__static__wood'),
            default=0.0
        )) \
        .annotate(leather=Case(
            When(weapon__isnull=False, then='weapon__static__leather'),
            When(semiproduct__isnull=False, then='semiproduct__leather'),
            When(shield__isnull=False, then='shield__static__leather'),
            default=0.0
    )) \
        .order_by('-level') \
        .values_list('steel',
                     'wood',
                     'leather',
                     'level',
                     Coalesce(F('weapon__id'), 0),
                     Coalesce(F('semiproduct__id'), 0),
                     Coalesce(F('shield__id'), 0))
    steel = 0.0
    wood = 0.0
    leather = 0.0
    slm = 1.2  # same level multiplier
    nlm = 2.2  # next level multiplier
    level = 0
    max_level = 0
    degradation = False
    rest_steel = 0.0
    rest_wood = 0.0
    rest_leather = 0.0
    rest_level = 0.0
    weapon_to_delete = []
    semiproduct_to_delete = []
    shield_to_delete = []

    for weapon in craft_box_weapons:
        steel += weapon[0]
        wood += weapon[1]
        leather += weapon[2]

        weapon_to_delete.append(weapon[4])
        semiproduct_to_delete.append(weapon[5])
        shield_to_delete.append(weapon[6])

        if max_level < weapon[3]:
            max_level = weapon[3]

        if steel >= required_steel * slm and wood >= required_wood * slm and leather >= required_leather * slm:
            level = weapon[3]
            rest_steel = steel - required_steel * slm
            rest_wood = wood - required_wood * slm
            rest_leather = leather - required_leather * slm
            rest_level = level

        if steel >= required_steel * nlm and wood >= required_wood * nlm and leather >= required_leather * nlm:
            level = weapon[3] + 1
            rest_steel = steel - required_steel * nlm
            rest_wood = wood - required_wood * nlm
            rest_leather = leather - required_leather * nlm
            rest_level = weapon[3]
            break

    if level < max_level:
        degradation = True

    build = False
    if level > 0:
        build = True
    else:
        craft_box_nonweapons = Inventory.objects \
            .filter(player=request.user.active_player,
                    weapon__isnull=True,
                    semiproduct__isnull=True,
                    pos__range=craft_box_range) \
            .select_related('consume_items',
                            'armor', 'armor__static') \
            .aggregate(
                steel=Sum(Coalesce(F('armor__static__steel'), 0)),
                wood=Sum(Coalesce(F('armor__static__wood'), 0)),
                leather=Sum(Coalesce(F('armor__static__leather'), 0)),
            )

        if craft_box_nonweapons['steel']:
            steel += craft_box_nonweapons['steel']
        if craft_box_nonweapons['wood']:
            wood += craft_box_nonweapons['wood']
        if craft_box_nonweapons['leather']:
            leather += craft_box_nonweapons['leather']

        if steel >= required_steel * slm and wood >= required_wood * slm and leather >= required_leather * slm:
            build = True
        else:
            build = False

    coal_consumption = 0
    if build:
        coal = Inventory.objects \
                        .filter(player=request.user.active_player,
                                pos__range=craft_box_range) \
                        .select_related('craft_items') \
                        .filter(craft_items__name='coal') \
                        .aggregate(coal=Sum(Coalesce(F('amount'), 0)))['coal']

        if coal:
            coal_consumption = int(steel/5)+1
            if float(coal) <= coal_consumption:
                build = False
        else:
            build = False

    return {'name': weapon_to_craft.name, 'build': build, 'level': level, 'coal': coal_consumption,
            'weapon_to_delete': weapon_to_delete, 'semiproduct_to_delete': semiproduct_to_delete, 'shield_to_delete': shield_to_delete,
            'rest_steel': rest_steel, 'rest_wood': rest_wood, 'rest_leather': rest_leather, 'rest_level': rest_level}

