from django.contrib import admin
from .models import SlotMachineType, UserProfile, Jackpot, SpinRecord

admin.site.register(SlotMachineType)
admin.site.register(UserProfile)
admin.site.register(Jackpot)
admin.site.register(SpinRecord)