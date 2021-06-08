import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Wingman.settings')
import django
django.setup()

from bs4 import BeautifulSoup
from main_app.models import Matches, Pools
from datetime import datetime, timedelta
from django.db.models import Avg, Sum
from main_app.utils.statistica import MAPS

# Nicknames in steam CS:GO wingman match history
PL1 = 'york111'
PL2 = 'I bring life and hope'

# Maps in separate rotation (if played one of them the other get skipped)
CONNECTED = ['de_calavera', 'de_pitstop']


def update_pool(pool):
    matches = Matches.objects.filter(match_pool=pool)
    r_won = matches.aggregate(n=Sum('match_r_won'))['n']
    r_lost = matches.aggregate(n=Sum('match_r_lost'))['n']
    k1 = matches.aggregate(n=Sum('match_K1'))['n']
    a1 = matches.aggregate(n=Sum('match_A1'))['n']
    d1 = matches.aggregate(n=Sum('match_D1'))['n']
    pts1 = matches.aggregate(n=Sum('match_score1'))['n']
    k2 = matches.aggregate(n=Sum('match_K2'))['n']
    a2 = matches.aggregate(n=Sum('match_A2'))['n']
    d2 = matches.aggregate(n=Sum('match_D2'))['n']
    pts2 = matches.aggregate(n=Sum('match_score2'))['n']

    pool.pool_m_won = len(matches.filter(match_r_won=9))
    pool.pool_m_lost = len(matches.filter(match_r_lost=9))
    pool.pool_m_tied = len(matches.filter(match_r_won=8))
    pool.pool_r_won = r_won
    pool.pool_r_lost = r_lost
    pool.pool_r_rate = r_won / r_lost
    pool.pool_K1 = k1
    pool.pool_A1 = a1
    pool.pool_D1 = d1
    pool.pool_KD1 = k1 / d1
    pool.pool_MVP1 = matches.aggregate(n=Sum('match_MVP1'))['n']
    pool.pool_HSP1 = matches.aggregate(n=Avg('match_HSP1'))['n']
    pool.pool_pts1 = pts1
    pool.pool_ptsadd1 = pts1 - (2 * k1 + a1)
    pool.pool_K2 = k2
    pool.pool_A2 = a2
    pool.pool_D2 = d2
    pool.pool_KD2 = k2 / d2
    pool.pool_MVP2 = matches.aggregate(n=Sum('match_MVP2'))['n']
    pool.pool_HSP2 = matches.aggregate(n=Avg('match_HSP2'))['n']
    pool.pool_pts2 = pts2
    pool.pool_ptsadd2 = pts2 - (2 * k2 + a2)

    if len(matches) == 7:
        # Checking maps that we didn't play after pool has ended
        playables = [ x[0] for x in MAPS[:-1] if x[1] < pool.pool_num < x[3] ]
        matches_in_pool = Matches.objects.filter(match_pool=pool)
        played = [ x.match_map for x in matches_in_pool ]

        for i in played: playables.remove(i)
        pool.pool_skipped = playables

    elif pool.pool_num > 1:

        # Checking which maps we skipped in current pool
        pools = Pools.objects.all()
        last_skipped = pools[pool.pool_num-2].pool_skipped

        not_skippable = [ map for map, _, active, __ in MAPS if not active ]
        not_skippable += ['*'] + CONNECTED + last_skipped

        matches_in_last = Matches.objects.filter(match_pool=pool)
        skipped = [ x.match_map for x in matches_in_last if x.match_r_won == 0 ]

        last20_pools = pools[len(pools)-21:len(pools)-1]
        l20_matches = Matches.objects.filter(match_pool__in=last20_pools)

        l20_stats = []
        for map, *_ in MAPS:
            if map not in not_skippable:
                m_matches = l20_matches.filter(match_map=map)
                r_won = m_matches.aggregate(n=Sum('match_r_won'))['n']
                r_lost = m_matches.aggregate(n=Sum('match_r_lost'))['n']
                l20_stats.append((map, r_won/r_lost))

        l20_stats.sort(key = lambda x: x[1])

        for i in range(2):
            skipped.append(l20_stats.pop(0)[0])

        skipped2 = list(set(skipped[0:2]))

        if len(matches_in_last.filter(match_map=CONNECTED[0])) > 0:
            skipped2.append(CONNECTED[1])
        elif len(matches_in_last.filter(match_map=CONNECTED[1])) > 0:
            skipped2.append(CONNECTED[0])

        pool.pool_skipped = skipped2
        print(skipped2)

    pool.save()


path_to_strona = os.path.join(os.getcwd(), 'static', 'main_app', 'strona', 'strona.html')
path_to_notpool = os.path.join(os.getcwd(), 'static', 'main_app', 'notpool.txt')

# Creating list of matches that wasn't played in pool-play
print("Preparing list of non-pool matches")
with open(path_to_notpool, encoding='utf-8') as f:
    not_pools = []
    for line in f.readlines():
        if len(line) > 12:
            line = line.replace('\n', '')
            date_line = datetime.strptime(line, '%Y-%m-%d %H:%M:%S')
            not_pools.append(date_line)

# Scraping data from steam website
with open(path_to_strona, encoding='utf-8') as f:
    print("Parsing website")
    soup = BeautifulSoup(f, "html.parser")

print("Extracting data")
l_table = soup.select("table.csgo_scoreboard_inner_left")
r_table = soup.select("table.csgo_scoreboard_inner_right")

l_matches = []
for match in l_table:
    ls = match.text.split()
    if ls[2] == '2019-10-10' and ls[3] == '14:36:43':
        ls[2] = '2019-10-11'
    l_matches.append([ls[1], ls[2] + 'T' + ls[3], ls[9], ls[12]])

r_matches = []
for match in r_table:
    ls = [x.text.replace('★', '0').replace('%', '').strip() for x in match.select('td')]
    ind1 = ls.index(PL1)
    ind2 = ls.index(PL2) if PL2 in ls else 1
    stats = ls[ind1+2:ind1+8]
    stats.extend(ls[ind2+2:ind2+8])

    if ind1 > 16:
        stats.extend([ls[16][-1], ls[16][0]])
    else:
        stats.extend([ls[16][0], ls[16][-1]])

    if 'I bring life and hope' in ls:
        r_matches.append(list(map(lambda x : int(x or '0'), stats)))
    else:
        r_matches.append(False)

matches = list(zip(l_matches, r_matches))
matches.sort(key = lambda x: x[0][1])

# Dealing with Pools model and saving each scraped match
pools = Pools.objects.all()
if not pools:
    Pools.objects.create(pool_num = 1)

for match in matches:
    last_pool = Pools.objects.last()
    last_pool_matches = Matches.objects.filter(match_pool=last_pool)

    if len(last_pool_matches) < 7:
        current_pool = last_pool
    else:
        update_pool(last_pool)
        Pools.objects.create(pool_num = len(Pools.objects.all()) + 1)
        current_pool = Pools.objects.last()

    match_date = datetime.strptime(match[0][1], '%Y-%m-%dT%H:%M:%S')
    if match_date not in not_pools:

        if match[1]:
            wait = match[0][2].split(':')
            waiting = int(wait[0]) * 60 + int(wait[1])
            dur = match[0][3].split(':')
            duration = int(dur[0]) * 60 + int(dur[1])

            try:
                Matches.objects.create(
                    match_map = match[0][0],
                    match_date = match[0][1],
                    match_duration = timedelta(seconds=duration),
                    match_waiting = timedelta(seconds=waiting),
                    match_r_won = match[1][12],
                    match_r_lost = match[1][13],
                    match_K1 = match[1][0],
                    match_A1 = match[1][1],
                    match_D1 = match[1][2],
                    match_MVP1 = match[1][3],
                    match_HSP1 = match[1][4],
                    match_score1 = match[1][5],
                    match_K2 = match[1][6],
                    match_A2 = match[1][7],
                    match_D2 = match[1][8],
                    match_MVP2 = match[1][9],
                    match_HSP2 = match[1][10],
                    match_score2 = match[1][11],
                    match_pool = current_pool
                )
                print(f'Added new match to database: {match_date} {match[0][0]}')

            except django.db.utils.IntegrityError:
                print("Match already exists, skipping.")
                update_pool(Matches.objects.filter(match_date=match[0][1])[0].match_pool)

update_pool(last_pool)
