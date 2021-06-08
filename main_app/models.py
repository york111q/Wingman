from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime

# Create your models here.
class Pools(models.Model):
    pool_num = models.IntegerField(default=0)
    pool_m_won = models.IntegerField(default=0)
    pool_m_lost = models.IntegerField(default=0)
    pool_m_tied = models.IntegerField(default=0)
    pool_r_won = models.IntegerField(default=0)
    pool_r_lost = models.IntegerField(default=0)
    pool_r_rate = models.FloatField(default=0.0)
    pool_K1 = models.IntegerField(default=0)
    pool_A1 = models.IntegerField(default=0)
    pool_D1 = models.IntegerField(default=0)
    pool_KD1 = models.FloatField(default=0.0)
    pool_MVP1 = models.IntegerField(default=0)
    pool_HSP1 = models.IntegerField(default=0)
    pool_pts1 = models.IntegerField(default=0)
    pool_ptsadd1 = models.IntegerField(default=0)
    pool_K2 = models.IntegerField(default=0)
    pool_A2 = models.IntegerField(default=0)
    pool_D2 = models.IntegerField(default=0)
    pool_KD2 = models.FloatField(default=0.0)
    pool_MVP2 = models.IntegerField(default=0)
    pool_HSP2 = models.IntegerField(default=0)
    pool_pts2 = models.IntegerField(default=0)
    pool_ptsadd2 = models.IntegerField(default=0)
    pool_skipped = ArrayField(models.CharField(max_length=32, blank=True), default=list)

    def __str__(self):
        return 'Pool nr ' + str(self.pool_num)


class Matches(models.Model):
    match_map = models.CharField(max_length=32)
    match_date = models.DateTimeField(unique=True)
    match_duration = models.DurationField()
    match_waiting = models.DurationField()
    match_r_won = models.IntegerField()
    match_r_lost = models.IntegerField()
    match_K1 = models.IntegerField()
    match_A1 = models.IntegerField()
    match_D1 = models.IntegerField()
    match_MVP1 = models.IntegerField()
    match_HSP1 = models.IntegerField()
    match_score1 = models.IntegerField()
    match_K2 = models.IntegerField()
    match_A2 = models.IntegerField()
    match_D2 = models.IntegerField()
    match_MVP2 = models.IntegerField()
    match_HSP2 = models.IntegerField()
    match_score2 = models.IntegerField()
    match_pool = models.ForeignKey(Pools, on_delete=models.CASCADE)

    def __str__(self):
        return self.match_date.strftime('%Y-%m-%d') + ' ' + self.match_map
