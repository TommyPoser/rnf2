from django.test import TestCase

# Create your tests here.


# items = get_array(
#     query="""SELECT i.id, i.pos, i.amount,
#                 CASE
#                   WHEN ws.name IS NOT NULL THEN ws.name
#                   WHEN ars.name IS NOT NULL THEN ars.name
#                   WHEN ss.name IS NOT NULL THEN ss.name
#                   ELSE c.name END AS name
#                 FROM inventory_inventory AS i
#                 LEFT JOIN inventory_consumeitems AS c ON i.consume_items_id = c.id
#                 LEFT JOIN inventory_weapon AS wd ON i.weapon_id = wd.id
#                 LEFT JOIN inventory_weapons AS ws ON wd.static_id = ws.id
#                 LEFT JOIN inventory_armor AS ard ON i.armor_id = ard.id
#                 LEFT JOIN inventory_armors AS ars ON ard.static_id = ars.id
#                 LEFT JOIN inventory_shield AS sd ON i.shield_id = sd.id
#                 LEFT JOIN inventory_shields AS ss ON Sd.static_id = ss.id
#                 WHERE i.player_id = %s
#                 ORDER BY i.pos
#                  """, params=[request.user.active_player])



# craft_box = Inventory.objects.filter(player=request.user.active_player,
#                                      pos__gt=20)\
#     .select_related('consume_items',
#                     'weapon', 'weapon__static',
#                     'armor', 'armor__static',
#                     'shield', 'shield__static')\
#     .annotate(level=Case(
#         When(consume_items__isnull=False, then=Value(0)),
#         When(craft_items__isnull=False, then=Value(0)),
#         When(weapon__isnull=False, then='weapon__level'),
#         When(armor__isnull=False, then=Value(0)),
#         When(shield__isnull=False, then=Value(0)),
#         output_field=IntegerField()))\
#     .order_by('-level')
# print(craft_box.first().level)


# resources = craft_box.aggregate(
#            steel=Sum(Coalesce(F('weapon__static__steel'), 0)
#                      + Coalesce(F('armor__static__steel'), 0)
#                      + Coalesce(F('shield__static__steel'), 0)),
#            wood=Sum(Coalesce(F('weapon__static__wood'), 0)
#                     + Coalesce(F('armor__static__wood'), 0)
#                     + Coalesce(F('shield__static__wood'), 0)),
#            leather=Sum(Coalesce(F('weapon__static__leather'), 0)
#                        + Coalesce(F('armor__static__leather'), 0)
#                        + Coalesce(F('shield__static__leather'), 0)),
#
#            )
# level = Min('weapon__level')

# resources.update(craft_box.filter(craft_items__name='coal')  # update spojuje první dict s druhou
#                  .aggregate(coal=Sum('amount')))

# print(resources)

# požadavky na consume items vznikají přímo zde na základě surovin
# a typu itemu k výrobě