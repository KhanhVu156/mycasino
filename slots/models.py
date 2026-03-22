from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save  
from django.dispatch import receiver            

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=100)
    spins_count = models.IntegerField(default=0)           
    consecutive_wins = models.IntegerField(default=0)     
    wins_count = models.IntegerField(default=0) 

class SlotMachineType(models.Model):
    name = models.CharField(max_length=100)
    reels = models.IntegerField(help_text="Số cột (ví dụ 3)")
    win_patterns = models.JSONField(help_text="Dict: pattern -> multiplier, ví dụ {'777':300}")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Jackpot(models.Model):
    machine_type = models.OneToOneField(SlotMachineType, on_delete=models.CASCADE, related_name='jackpot')
    amount = models.IntegerField(default=1000)

class SpinRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine_type = models.ForeignKey(SlotMachineType, on_delete=models.CASCADE)
    result = models.CharField(max_length=20)
    bet = models.IntegerField()
    payout = models.IntegerField()
    balance_after = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    jackpot_hit = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)