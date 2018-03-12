from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from index.defs import execute_query, get_array
from inventory.models import ConsumeItems, Weapons, Armors, Shields


def index(request):
    return redirect('consume_items/')


@user_passes_test(lambda u: u.is_staff, redirect_field_name=None)
def consume_items(request):

    if request.POST:
        entry = request.POST['entry']
        array = entry2array(entry)
        execute_query(
            query="""DELETE FROM inventory_consumeitems""",
            params=[])

        for row in array:
            if row[0]:
                execute_query(
                    query="""INSERT INTO inventory_consumeitems (name, max_stack)
                             VALUES (%s, %s)""",
                    params=row)

    textarea = get_textarea(get_array(
        query="""SELECT * FROM inventory_consumeitems""",
        params=[]))
    thead = ConsumeItems._meta.get_fields()

    return render(request, 'staticDB.html', {"textarea": textarea,
                                             "thead": thead,
                                             "link": "staticDB:consume_items"})


@user_passes_test(lambda u: u.is_staff, redirect_field_name=None)
def weapons(request):

    if request.POST:
        entry = request.POST['entry']
        array = entry2array(entry)
        execute_query(
            query="""DELETE FROM inventory_weapons""",
            params=[])

        for row in array:
            if row[0]:
                execute_query(
                    query="""INSERT INTO inventory_weapons (name, steel, wood, leather, focus, focus_offset, attack, defence, dmg, dmg_offset, stun, deattack)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    params=row)

    textarea = get_textarea(get_array(
        query="""SELECT * FROM inventory_weapons""",
        params=[]))
    thead = Weapons._meta.get_fields()

    return render(request, 'staticDB.html', {"textarea": textarea,
                                             "thead": thead,
                                             "link": "staticDB:weapons"})


@user_passes_test(lambda u: u.is_staff, redirect_field_name=None)
def armors(request):

    if request.POST:
        entry = request.POST['entry']
        array = entry2array(entry)
        execute_query(
            query="""DELETE FROM inventory_armors""",
            params=[])

        for row in array:
            if row[0]:
                execute_query(
                    query="""INSERT INTO inventory_armors (name, steel, wood, leather, min_movement, armor)
                             VALUES (%s, %s, %s, %s, %s, %s)""",
                    params=row)

    textarea = get_textarea(get_array(
        query="""SELECT * FROM inventory_armors""",
        params=[]))
    thead = Armors._meta.get_fields()

    return render(request, 'staticDB.html', {"textarea": textarea,
                                             "thead": thead,
                                             "link": "staticDB:armors"})


@user_passes_test(lambda u: u.is_staff, redirect_field_name=None)
def shields(request):

    if request.POST:
        entry = request.POST['entry']
        array = entry2array(entry)
        execute_query(
            query="""DELETE FROM inventory_shields""",
            params=[])

        for row in array:
            if row[0]:
                execute_query(
                    query="""INSERT INTO inventory_shields (name, steel, wood, leather, min_movement, defence)
                             VALUES (%s, %s, %s, %s, %s, %s)""",
                    params=row)

    textarea = get_textarea(get_array(
        query="""SELECT * FROM inventory_shields""",
        params=[]))
    thead = Shields._meta.get_fields()

    return render(request, 'staticDB.html', {"textarea": textarea,
                                             "thead": thead,
                                             "link": "staticDB:shields"})


def entry2array(entry):
    table = entry.split('\r\n')
    array = []
    for row in table:
        cells = row.split('\t')
        array.append(cells)
    return array


def get_textarea(items):
    textarea = ''
    for item in items:
        item = iter(item)
        next(item)
        i = 0
        for cell in item:
            if i > 0:
                tab = '\t'
            else:
                tab = ''
            i += 1
            textarea = textarea + tab + str(cell)
        textarea += '\r\n'
    return textarea

