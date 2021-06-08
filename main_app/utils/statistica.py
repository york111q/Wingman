import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Wingman.settings')
import django
django.setup()

from main_app.models import Matches, Pools
from django.db.models import Avg, Sum
from datetime import timedelta
import math

# List of tuples containing map name, number of pool when map entered wingman,
# is it still active or not and when map left wingman.
MAPS = [('Shortdust', 0, True, 999), ('Overpass', 0, True, 999),
        ('Rialto', 0, False, 139), ('Inferno', 0, True, 999),
        ('Train', 0, True, 999), ('Shortnuke', 0, True, 999),
        ('Cobblestone', 0, True, 999), ('Lake', 0, True,999),
        ('Vertigo', 63, True, 999), ('de_calavera', 138, True, 999),
        ('de_pitstop', 138, True, 999), ('*', 0 , True, 999)]

# Maps that cannot be skipped based on their round rate: connected or not active
# Also their format is like in display not like in MAPS
N_SKIP = ['Calavera', 'Pitstop', 'Rialto']


def stat():
    pools = Pools.objects.all().order_by('-pool_num')
    matches = Matches.objects.filter(match_pool__in=pools)
    return make_stats(matches, pools)


def stat20():
    pools = Pools.objects.all().order_by('-pool_num')[:20]
    matches = Matches.objects.filter(match_pool__in=pools)
    return make_stats(matches, pools)


def make_stats(matches, pools):
    all_stats = []
    indiv_stats = []

    # Preparing list of all skips to further count it
    skip_list = []
    for pool in pools:
        skip_list.extend(pool.pool_skipped)


    for map, entered, active, left in MAPS:
        if map == '*':
            m_matches = matches
        else:
            m_matches = matches.filter(match_map=map)

        if len(m_matches) == 0:
            row = {
                'map_name': map.replace('de_', '').capitalize(),
                'm_won': 0,
                'm_lost': 0,
                'm_tied': 0,
                'm_duration': timedelta(seconds=0),
                'm_waiting': timedelta(seconds=0),
                'r_won': 0,
                'r_lost': 0,
                'm_win_rate': 0,
                'r_mean': 0,
                'r_rate': 0,
                'm_skips': skip_list.count(map),
                'm_out': ('-', '-'),
                'ud': '-:-',
                'proj_RR': 0
            }

            irow = {
                'map_name': map.replace('de_', '').capitalize(),
                'm_K1': 0,
                'm_A1': 0,
                'm_D1': 0,
                'm_MVP1': 0,
                'm_HSP1': 0,
                'm_pts1': 0,
                'm_addpts1': 0,
                'm_KR1': 0,
                'm_KD1': 0,
                'm_K2': 0,
                'm_A2': 0,
                'm_D2': 0,
                'm_MVP2': 0,
                'm_HSP2': 0,
                'm_pts2': 0,
                'm_addpts2': 0,
                'm_KR2': 0,
                'm_KD2': 0,
                'tot_KD': 0,
            }

        else:
            row = {
                'map_name': map.replace('de_', '').capitalize(),
                'm_won': len(m_matches.filter(match_r_won=9)),
                'm_lost': len(m_matches.filter(match_r_lost=9)),
                'm_tied': len(m_matches.filter(match_r_won=8)),
                'm_duration': m_matches.aggregate(n=Avg('match_duration'))['n'],
                'm_waiting': m_matches.aggregate(n=Avg('match_waiting'))['n'],
                'r_won': m_matches.aggregate(n=Sum('match_r_won'))['n'],
                'r_lost': m_matches.aggregate(n=Sum('match_r_lost'))['n'],
                'm_skips': skip_list.count(map)
            }

            row['m_win_rate'] = row['m_won'] / row['m_lost']
            row['r_mean'] = (row['r_won'] + row['r_lost']) / (row['m_won'] + row['m_lost'] + row['m_tied'])
            row['r_rate'] = row['r_won'] / row['r_lost']
            row['ud'] = '-:-'


            # Looking for results which will be out of 20 pools after this one
            last_pool_matches = Matches.objects.filter(match_pool__in=pools[0:1])
            out_pool_maps = list(zip(*[(x.match_map, x.match_r_won, x.match_r_lost) for x in last_pool_matches]))

            if map in out_pool_maps[0]:
                map_tup = out_pool_maps[0].index(map)
                row['m_out'] = out_pool_maps[1][map_tup], out_pool_maps[2][map_tup]
            else:
                row['m_out'] = '-', '-'


            irow = {
                'map_name': map.replace('de_', '').capitalize(),
                'm_K1': m_matches.aggregate(n=Sum('match_K1'))['n'],
                'm_A1': m_matches.aggregate(n=Sum('match_A1'))['n'],
                'm_D1': m_matches.aggregate(n=Sum('match_D1'))['n'],
                'm_MVP1': m_matches.aggregate(n=Sum('match_MVP1'))['n'],
                'm_HSP1': m_matches.aggregate(n=Avg('match_HSP1'))['n'],
                'm_pts1': m_matches.aggregate(n=Sum('match_score1'))['n'],
                'm_K2': m_matches.aggregate(n=Sum('match_K2'))['n'],
                'm_A2': m_matches.aggregate(n=Sum('match_A2'))['n'],
                'm_D2': m_matches.aggregate(n=Sum('match_D2'))['n'],
                'm_MVP2': m_matches.aggregate(n=Sum('match_MVP2'))['n'],
                'm_HSP2': m_matches.aggregate(n=Avg('match_HSP2'))['n'],
                'm_pts2': m_matches.aggregate(n=Sum('match_score2'))['n'],
            }

            irow['m_addpts1'] = irow['m_pts1'] - (irow['m_K1'] * 2 + irow['m_A1'])
            irow['m_KR1'] = irow['m_K1'] / (row['r_won'] + row['r_lost'])
            irow['m_KD1'] = irow['m_K1'] / irow['m_D1']
            irow['m_addpts2'] = irow['m_pts2'] - (irow['m_K2'] * 2 + irow['m_A2'])
            irow['m_KR2'] = irow['m_K2'] / (row['r_won'] + row['r_lost'])
            irow['m_KD2'] = irow['m_K2'] / irow['m_D2']
            irow['tot_KD'] = (irow['m_K1'] + irow['m_K2']) / (irow['m_D1'] + irow['m_D2'])


        # Determining if map is active, being played and with witch result
        # to further display colors in summary table
        cur_pool = pools[0]
        cur_pool_matches = Matches.objects.filter(match_pool=cur_pool)
        cur_pool_maps = list(zip(*[(x.match_map, x.match_r_won) for x in cur_pool_matches]))

        if not active:
            row['status'] = "notactive"
        else:
            if map in pools[0].pool_skipped:
                row['status'] = "skipped"
            else:
                if map not in cur_pool_maps[0]:
                    row['status'] = "notplayed"
                else:
                    map_rounds_won = cur_pool_maps[1][cur_pool_maps[0].index(map)]
                    if map_rounds_won == 9:
                        row['status'] = "matchwon"
                    elif map_rounds_won == 8:
                        row['status'] = "matchtied"
                    elif map_rounds_won < 8:
                        row['status'] = "matchlost"
                    else:
                        row['status'] = "error"


        # Creating projected round rate of this map
        if row['map_name'] == '*' or row['r_won'] + row['r_lost'] == 0:
            row['proj_RR'] = row['r_rate']
        elif row['status'] == "notplayed":
            row['proj_RR'] = ((row['r_won'] + 9) / row['r_lost'],
                              row['r_won'] / (row['r_lost'] + 9))
        elif type(row['m_out'][0]) is type(1):
            row['proj_RR'] = (row['r_won'] - row['m_out'][0]) / (row['r_lost'] - row['m_out'][1])
        else:
            row['proj_RR'] = row['r_rate']


        # Saving stats as nested list
        all_stats.append(row)
        indiv_stats.append(irow)


    # Removing asterix nested lists as it should always be at the end
    asterix_stats = all_stats.pop(), indiv_stats.pop()
    asterix_stats[0]['m_skips'] = '-'

    # Sorting list as it should be shown
    all_stats.sort(key = lambda x: -x['r_rate'])
    indiv_stats.sort(key = lambda x: -x['tot_KD'])


    # Adding predictation of skipped maps
    ls_skipped = pools[0].pool_skipped
    ls_skipped.extend(['Calavera', 'Pitstop', 'Rialto'])
    pred_skipped = [ all_stats.index(x) for x in all_stats if x['map_name'] not in ls_skipped ]
    for i in range(2):
        all_stats[pred_skipped[-i-1]]['status'] += ' willskip'


    # Counting prediction which score to skip or save from skip (U/D)
    maps_to_count = set([ map for map, entered, active, left in MAPS if active ])
    maps_not_to_count = pools[0].pool_skipped
    maps_not_to_count.extend(N_SKIP)
    maps_not_to_count = set(maps_not_to_count)
    maps_to_count = list(maps_to_count.difference(maps_not_to_count))

    maps_rrs = []
    for num, i in enumerate(all_stats):
        if i['map_name'] in maps_to_count:
            maps_rrs.append((i['map_name'], i['r_rate'], i['r_won'], i['r_lost'], num))

    maps_rrs.sort(key = lambda x: x[1])

    for map, rr, won, lost, ind in maps_rrs[2:]:
        if all_stats[ind]['status'].startswith('notplayed'):
            down_rr = maps_rrs[1][1]
            r_won_to_down = math.floor(down_rr * (lost + 9))
            if r_won_to_down - won < 0:
                all_stats[ind]['ud'] = '0:9'
            elif r_won_to_down - won == 8:
                all_stats[ind]['ud'] = '7:9'
            else:
                all_stats[ind]['ud'] = str(r_won_to_down - won) + ':9'

    for map, rr, won, lost, ind in maps_rrs[:2]:
        if all_stats[ind]['status'].startswith('notplayed'):
            up_rr = maps_rrs[2][1]
            r_lost_to_up = math.floor((won + 9) / up_rr)
            if r_lost_to_up - lost < 0:
                all_stats[ind]['ud'] = '9:0'
            elif r_lost_to_up - lost == 8:
                all_stats[ind]['ud'] = '9:7'
            else:
                all_stats[ind]['ud'] = '9:' + str(r_lost_to_up - lost)


    # Moving back asterix scores at the back
    all_stats.append(asterix_stats[0])
    indiv_stats.append(asterix_stats[1])

    return all_stats, indiv_stats
