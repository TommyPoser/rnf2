from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.core.files import File
from vec_noise import pnoise2
from django.http import JsonResponse
import json, random
from index.defs import execute_query
from map.models import Town, Hexa, Pixel
from index.models import Player
from recon.views import leave
from PIL import Image, ImageDraw, ImageEnhance
from numpy import uint8, swapaxes

width = 1600
height = 800
hexa_a = 14
hexa_b = 12


@login_required(redirect_field_name=None)
def index(request):

    area = [[]]
    hexa = [[]]

    # with open('static/media/map.txt', 'r') as f:
    #     for line in f:
    #         row = [int(elt.strip()) for elt in line.split('\t')]
    #         area.append(row)

    hive = Hexa.objects.all().values_list('id', 'x', 'y', 'biome', 'town')

    for cell in hive:
        walk = 'no'
        if cell[3] is 0: walk = 'grass'
        if cell[3] is 1: walk = 'wood'
        if cell[3] is 2: walk = 'hills'
        if cell[4]: town = True
        else: town = False

        hexa.append([cell[0], cell[1], cell[2], walk, town])

    pos = Player.objects.filter(pk=request.user.active_player).values_list('pos')

    return render(request, 'map.html', {'area': area, 'width': width, 'height': height, 'hexa': hexa, 'pos': pos[0][0]})


def travel(request):
    if request.is_ajax():
        if request.method == 'POST':

            animals, status, remaining = leave(request)
            if remaining:
                return JsonResponse({}, safe=False)

            arr = json.loads(request.body.decode('utf-8'))

            hexa = Player.objects.filter(pk=request.user.active_player)\
                .select_related('pos').values_list('pos__id', 'pos__x', 'pos__y')[0]

            pick_data = []

            for pick in arr['hexaPicks']:
                pick_data.append(Hexa.objects.filter(pk=pick).values()[0])

            end = find_path(pick_data, hexa[1], hexa[2], hexa[0], hexa[0])

            Player.objects.filter(pk=request.user.active_player).update(pos=end)

            return JsonResponse({'start':  hexa[0], 'end': end}, safe=False)


def find_path(pick_data, x, y, id, id2):
    record = False
    record_data = []
    for pick in pick_data[:]:
        if (((pick['x'] == x+2*hexa_b or pick['x'] == x-2*hexa_b) and pick['y'] == y)
            or ((pick['x'] == x+hexa_b or pick['x'] == x-hexa_b) and
                    (pick['y'] == int(y+1.5*hexa_a) or pick['y'] == int(y-1.5*hexa_a))))\
            and pick['id'] != id2:

            biome = Hexa.objects.filter(pk=pick['id']).values_list('biome')[0][0]

            if not record and biome < 3:
                record = True
                record_data = [pick_data, pick['x'], pick['y'], pick['id'], id]
            else:
                pick_data.remove(pick)
    if record:
        return find_path(record_data[0], record_data[1], record_data[2], record_data[3], record_data[4])
    return id


@user_passes_test(lambda u: u.is_staff, redirect_field_name=None)
def generate_map(request):

    execute_query(
        query="""DELETE FROM map_hexa;
                 DELETE FROM map_pixel;
                 ALTER TABLE map_hexa AUTO_INCREMENT = 1;
                 ALTER TABLE map_pixel AUTO_INCREMENT = 1""",
        params=[])

    base = 3
    scale = 0.004
    scale_t = 0.04
    exp = 2.4
    k = 1.32
    r = 100

    area = [[0 for y in range(height)] for x in range(width)]
    area_T = [[0 for x in range(width)] for y in range(height)]
    pixels = [[0 for x in range(width)] for y in range(height)]
    w_mask = [[[0, 0, 0, 255] for y in range(height)] for x in range(width)]
    t_mask = [[[0, 0, 0, 255] for y in range(height)] for x in range(width)]
    h_mask = [[[0, 0, 0, 255] for y in range(height)] for x in range(width)]
    m_mask = [[[0, 0, 0, 255] for y in range(height)] for x in range(width)]
    towns = []

    for yc in range(int(height/r)):
        for xc in range(int(width/r)):

            town = [0, 0, 0.0]

            for yr in range(r):
                for xr in range(r):
                    x = xc*r+xr
                    y = yc*r+yr
                    noise = pnoise2(scale*x, scale*y, octaves=4, persistence=0.25, lacunarity=3, repeatx=width*scale, repeaty=height*scale, base=base)
                    z = pow((noise+1.0)*k/2.0, exp)
                    noise2 = pnoise2(scale*x, scale*y, octaves=4, persistence=0.3, lacunarity=3, repeatx=width*scale, repeaty=height*scale, base=(base+1))
                    tree = pow((noise2+1.0)*k/2.0, exp)
                    noise3 = pnoise2(scale_t*x, scale_t*y, octaves=1, persistence=0.5, repeatx=width*scale_t, repeaty=height*scale_t, base=(base+2))
                    t = (noise3+1)/2

                    w_pixel = [0, 0, 0, 255]
                    t_pixel = [0, 0, 0, 255]
                    h_pixel = [0, 0, 0, 255]
                    m_pixel = [0, 0, 0, 255]

                    if 0.23 <= z < 0.50 and tree > 0.5:
                        a = 1
                        t_pixel = [0, 0, 0, 0]
                    elif 0.50 < z <= 0.75:
                        a = 2
                        h_pixel = [0, 0, 0, 0]
                    elif 0.75 < z:
                        a = 3
                        m_pixel = [0, 0, 0, 0]
                    elif z < 0.23:
                        a = 4
                        w_pixel = [0, 0, 0, 0]
                    else:
                        a = 0

                    if ((0.23 <= z < 0.505 and 0.43 < tree)
                        or (0.23 <= z < 0.25 or 0.47 <= z < 0.505)) \
                        and tree < 0.5 \
                        and (town_distance(towns, x, y))\
                        and 70 < x < (width-70) and 70 < y < (height-70)\
                        and ((x%(2*hexa_b) == hexa_b and y%(1.5*hexa_a) == hexa_a)
                             or (x%(2*hexa_b) == 0 and y%(1.5*hexa_a) == (2.5*hexa_a)))\
                        and t > town[2]:
                            town = [x, y, t]
                            towns.append(town)

                    area[x][y] = a
                    area_T[y][x] = a
                    pixels[y][x] = z
                    w_mask[x][y] = w_pixel
                    t_mask[x][y] = t_pixel
                    h_mask[x][y] = h_pixel
                    m_mask[x][y] = m_pixel


            if town[2] > 0.01:
                x = town[0]
                y = town[1]
                for i in range(5):
                    for j in range(5):
                        area[int(x+i)][int(y+j)] = 5

    # with open('static/media/map.txt', 'w') as f:
    #     map_data = File(f)
    #     for row in area:
    #         map_data.write('\t'.join(str(cell) for cell in row))
    #         map_data.write('\n')

    w_mask = swapaxes(w_mask, 0, 1)
    t_mask = swapaxes(t_mask, 0, 1)
    h_mask = swapaxes(h_mask, 0, 1)
    m_mask = swapaxes(m_mask, 0, 1)

    w_mask = Image.fromarray(uint8(w_mask), mode='RGBA')
    t_mask = Image.fromarray(uint8(t_mask), mode='RGBA')
    h_mask = Image.fromarray(uint8(h_mask), mode='RGBA')
    m_mask = Image.fromarray(uint8(m_mask), mode='RGBA')

    grass_img = Image.new("RGBA", w_mask.size, (60, 179, 113, 255))
    water_img = Image.new("RGBA", w_mask.size, (32, 80, 103, 255))
    trees_img = Image.new("RGBA", w_mask.size, (34, 139, 34, 255))
    hills_img = Image.new("RGBA", w_mask.size, (244, 164, 96, 255))
    mountains_img = Image.new("RGBA", w_mask.size, (102, 102, 102, 255))

    img = Image.composite(grass_img, water_img, w_mask)
    img = Image.composite(img, trees_img, t_mask)
    img = Image.composite(img, hills_img, h_mask)
    img = Image.composite(img, mountains_img, m_mask)
    img.save('static/media/map.png', quality=95)



    a = hexa_a
    b = hexa_b
    hexa = []
    just_one = 0
    wave = Image.open('static/media/wave2.png')
    tree = Image.open('static/media/tree3.png')
    grass_img = Image.open('static/media/grass.png')
    rock_img = Image.open('static/media/rock2.png')
    pos = Player.objects.filter(pk=request.user.active_player).values_list('pos')

    for yc in range(int(height/(1.5*a))):
        if yc < 2:
            pass
        else:
            if yc % 2 is 0:
                d = 0
                last = 0
            else:
                d = b
                last = 1
            for xc in range(int(width/(2*b)-last)):
                x = int(xc*2*b+d)
                y = int(yc*1.5*a)

                grass = 0
                wood = 0
                hills = 0
                mountains = 0
                water = 0
                town = False
                n = 0

                for xi in range(2*b):
                    yi = int((b-xi)*0.577350269)
                    for biome in area[int(x+xi)][int(y+yi):int(y+2*a-yi)]:
                        if biome is 0: grass += 1
                        elif biome is 1: wood += 1
                        elif biome is 2: hills += 1
                        elif biome is 3: mountains += 1
                        elif biome is 4: water += 1
                        elif biome is 5: town = True
                        n += 1

                walk = 'no'
                hexabiome = 4

                if n > 0:
                    if (grass+wood+hills)/n > 0.1:
                        if wood < grass > hills:
                            walk = 'grass'
                            hexabiome = 0
                        elif grass < wood > hills:
                            walk = 'wood'
                            hexabiome = 1
                        elif grass < hills > wood:
                            walk = 'hills'
                            hexabiome = 2

                if town:
                    town_name = 'Town'+str(x)+'_'+str(y)
                    new_town = Town(name=town_name)
                    new_town.save()
                    Hexa(x=x, y=y, biome=hexabiome, grass=grass, wood=wood, hills=hills, mountains=mountains, water=water, town=new_town).save()
                else:
                    Hexa(x=x, y=y, biome=hexabiome, grass=grass, wood=wood, hills=hills, mountains=mountains, water=water).save()

                hexa.append([x, y, walk])

                if just_one == pos[0][0]:
                    print(pos[0][0])
                    size_x = 1200
                    size_y = 400

                    img = Image.new('RGBA', (size_x, size_y), (0, 0, 0, 0))

                    points, lowest_point = make_path(x, y+a, size_x, size_y, pixels, scope=50, lowest_point=0)

                    points, lowest_point = make_path(x, y-4*a, size_x, size_y, pixels, scope=700, lowest_point=lowest_point)
                    img = make_land(img, size_x, size_y, points)

                    points, lowest_point = make_path(x, y-3*a, size_x, size_y, pixels, scope=600, lowest_point=lowest_point)
                    img = make_land(img, size_x, size_y, points)

                    points, lowest_point = make_path(x, y-a, size_x, size_y, pixels, scope=240, lowest_point=lowest_point)
                    img = make_land(img, size_x, size_y, points)

                    points, lowest_point = make_path(x, y, size_x, size_y, pixels, scope=132, lowest_point=lowest_point)
                    img = make_land(img, size_x, size_y, points)

                    points, lowest_point = make_path(x, y+a, size_x, size_y, pixels, scope=50, lowest_point=lowest_point)
                    img = make_land(img, size_x, size_y, points)

                    img = add_trees(img, x, y+a, area_T, points, size_x, tree, scope=50)

                    img = color2transparent(img, size_x, size_y)

                    img = add_trees(img, x, y+a, area_T, points, size_x, tree, scope=50, resample=5)

                    img = add_grass(img, x, y+a, area_T, points, size_x, grass_img, scope=50, resample=0)
                    img = add_grass(img, x, y+a, area_T, points, size_x, grass_img, scope=50, resample=5)

                    img = add_rock(img, x, y+a, area_T, points, size_x, rock_img, scope=50, resample=0)
                    img = add_rock(img, x, y+a, area_T, points, size_x, rock_img, scope=50, resample=5)

                    img = color2transparent(img, size_x, size_y)

                    img.save('static/media/recon.png', quality=95)

                just_one += 1

    return redirect('/map/')


def town_distance(towns, x, y):
    for town in towns:
        dx = town[0]-x
        dy = town[1]-y
        c = (dx**2+dy**2)**0.5
        if c < 150:
            return False
    return True


def shift(x, scope):
    # print('shift scope: %d' % (scope))
    left_shift = right_shift = int(scope/2)

    if x - left_shift < 0:
        right_shift += left_shift - x
        left_shift = x

    if right_shift + x > width:
        left_shift += x + right_shift - width
        right_shift = width - x

    return left_shift, right_shift


def make_path(x, y, size_x, size_y, pixels, scope, lowest_point):
    z_multiplier = 1000
    zoom = 1-(scope**0.75/400)
    left_shift, right_shift = shift(x, scope)

    step = int(size_x / (right_shift + left_shift)) + 1
    path = pixels[y][int(x - left_shift):int(x + right_shift)]

    if not lowest_point:
        lowest_point = min(path) * z_multiplier - 20

    # print('left %d, right %d, X %d, Y %d, step %d' % (left_shift, right_shift, x, y, step))

    points = []

    for i, point in enumerate(path):
        points.append((i * step, int(size_y - (point * z_multiplier * zoom - lowest_point))))
    return points, lowest_point


def make_land(img, size_x, size_y, points):
    points_polygon = points
    points_polygon.append((size_x, size_y))
    points_polygon.append((0, size_y))

    img2 = Image.new('RGBA', (size_x, size_y), (0, 0, 0, 0))
    drawing = ImageDraw.Draw(img2, mode='RGBA')
    drawing.polygon(points_polygon, fill=(5, 5, 5, 255))
    drawing.line(points, fill=(0, 0, 0, 255), width=3)

    img.alpha_composite(img2)
    return img


def add_trees(img, x, y, area_T, points, size_x, tree, scope, resample=0):

    left_shift, right_shift = shift(x, scope)
    step = int(size_x / (right_shift + left_shift)) + 1

    for i, biome in enumerate(area_T[y][int(x - left_shift):int(x + right_shift)]):
        if biome == 1:
            scale_x = (random.randint(-2, 10) / 40) + 1
            scale_y = (random.randint(-10, 6) / 40) + 1
            tree_resized = tree.resize((int(tree.width * scale_x), int(tree.height * scale_y)), resample=resample)
            img.paste(tree_resized, (i * step, int(points[i][1] - tree_resized.height + 5)), mask=tree_resized)
    return img


def add_grass(img, x, y, area_T, points, size_x, grass, scope, resample=0):

    left_shift, right_shift = shift(x, scope)
    step = int(size_x / (right_shift + left_shift)) + 1

    for i, biome in enumerate(area_T[y][int(x - left_shift):int(x + right_shift)]):
        if biome == 0:
            scale_x = (random.randint(-5, 4) / 10) + 1
            scale_y = (random.randint(-15, 4) / 20) + 1
            grass_resized = grass.resize((int(grass.width * scale_x), int(grass.height * scale_y)), resample=resample)
            img.paste(grass_resized, (i * step, int(points[i][1] - grass_resized.height + 5)), mask=grass_resized)
    return img


def add_rock(img, x, y, area_T, points, size_x, rock, scope, resample=0):

    left_shift, right_shift = shift(x, scope)
    step = int(size_x / (right_shift + left_shift)) + 1

    for i, biome in enumerate(area_T[y][int(x - left_shift):int(x + right_shift)]):
        if biome == 2:
            scale_x = (random.randint(-10, 4) / 20) + 1
            scale_y = (random.randint(-10, 4) / 20) + 1
            move_y = random.randint(0, 10)
            move_x = random.randint(-4, 4)
            rock_resized = rock.resize((int(rock.width * scale_x), int(rock.height * scale_y)), resample=resample)
            rock_rotated = rock_resized.rotate(random.randint(0, 360))
            img.paste(rock_rotated, (i * step + move_x - 20, int(points[i][1] - rock_rotated.height + 20 + move_y)), mask=rock_rotated)
    return img


def color2transparent(img, size_x, size_y):
    pixdata = img.load()
    for ix in range(size_x):
        for iy in range(size_y):
            if pixdata[ix, iy] == (5, 5, 5, 255):
                pixdata[ix, iy] = (5, 5, 5, 0)
    return img

