from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from index.defs import get_array
from index.defs import execute_query     # pozice je relativní vůči manage.py
from django.http import JsonResponse
import json


@login_required(redirect_field_name=None)
def index(request):

    items = get_array(
        query="""SELECT i.id, i.pos, i.amount,
                    CASE
                      WHEN ws.name IS NOT NULL THEN ws.name
                      WHEN ars.name IS NOT NULL THEN ars.name
                      WHEN ss.name IS NOT NULL THEN ss.name
                      ELSE c.name END AS name
                    FROM inventory_inventory AS i
                    LEFT JOIN inventory_consumeitems AS c ON i.consume_items_id = c.id
                    LEFT JOIN inventory_weapon AS wd ON i.weapon_id = wd.id
                    LEFT JOIN inventory_weapons AS ws ON wd.static_id = ws.id
                    LEFT JOIN inventory_armor AS ard ON i.armor_id = ard.id
                    LEFT JOIN inventory_armors AS ars ON ard.static_id = ars.id
                    LEFT JOIN inventory_shield AS sd ON i.shield_id = sd.id
                    LEFT JOIN inventory_shields AS ss ON Sd.static_id = ss.id
                    WHERE i.player_id = %s
                    ORDER BY i.pos
                     """, params=[request.user.active_player])

    grid = {}
    grid_max = 15
    j = 1

    for item in items:
        while j < item[1]:
            grid[j] = None
            j += 1
        grid[j] = {}
        grid[j] = item
        j += 1

    while j <= grid_max:
        grid[j] = None
        j += 1

    return render(request, 'inventory.html', {'grid': grid})



def save_events_json(request):
    if request.is_ajax():
        if request.method == 'POST':
            arr = json.loads(request.body.decode('utf-8'))
            execute_query(
                query="""UPDATE inventory_inventory SET pos = %s
                         WHERE player_id = %s AND id = %s""",
                params=[arr["entNumber"], request.user.active_player, arr["dragNumber"]])
            return JsonResponse(arr, safe=False)



