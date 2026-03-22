import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
from .models import SlotMachineType, UserProfile, SpinRecord, Jackpot
from .slot_logic import BaseSlotMachine
from .forms import CustomAuthenticationForm

@login_required
def machine_list(request):
    machines = SlotMachineType.objects.all()
    return render(request, 'slots/machine_list.html', {'machines': machines})

@login_required
def play_machine(request, machine_id):
    machine = get_object_or_404(SlotMachineType, id=machine_id)
    profile = request.user.userprofile
    jackpot, _ = Jackpot.objects.get_or_create(machine_type=machine, defaults={'amount': 1000})
    return render(request, 'slots/play.html', {
        'machine': machine,
        'balance': profile.balance,
        'jackpot': jackpot.amount
    })

@login_required
def spin(request, machine_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    bet = int(data.get('bet', 0))
    machine = get_object_or_404(SlotMachineType, id=machine_id)
    profile = request.user.userprofile

    
    if bet <= 0 or bet > profile.balance:
        return JsonResponse({'error': 'Invalid bet'}, status=400)

    profile.balance -= bet
    profile.save()

    slot = BaseSlotMachine(machine.reels, machine.win_patterns)

   
    force_win = False
    if profile.wins_count < 3:
        
        import random
        if random.random() < 0.7: 
            force_win = True

    if force_win:
    
        win_patterns = machine.win_patterns
        pattern = random.choice(list(win_patterns.keys()))
        multiplier = win_patterns[pattern]
        payout = bet * multiplier
        is_jackpot = (multiplier == max(win_patterns.values()))

        
        result = pattern * (machine.reels // len(pattern)) + pattern[:machine.reels % len(pattern)]
        result = result.ljust(machine.reels, '0')  # Đảm bảo đủ độ dài

        
        profile.wins_count += 1
        profile.save()
    else:
       
        result = slot.spin()
        payout, is_jackpot = slot.get_payout(result, bet)
        
        if payout > 0 and profile.wins_count < 3:
            profile.wins_count += 1
            profile.save()

   
    jackpot, _ = Jackpot.objects.get_or_create(machine_type=machine, defaults={'amount': 1000})
    if is_jackpot and payout > 0:
        payout += jackpot.amount     
        jackpot.amount = 1000        
    else:
        
        contribution = max(1, int(bet * 0.01))
        jackpot.amount += contribution
    jackpot.save()

    
    profile.balance += payout
    profile.save()

    
    SpinRecord.objects.create(
        user=request.user,
        machine_type=machine,
        result=result,
        bet=bet,
        payout=payout,
        balance_after=profile.balance,
        jackpot_hit=is_jackpot
    )

    
    return JsonResponse({
        'result': result,
        'payout': payout,
        'new_balance': profile.balance,
        'jackpot': jackpot.amount,
        'is_jackpot': is_jackpot,
        'message': f"🎉 You won ${payout}!" if payout > 0 else "😞 God bless you.",
        'wins_left': max(0, 3 - profile.wins_count)  
    })
    
@login_required
def history(request):
    spins = SpinRecord.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'slots/history.html', {'spins': spins})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('machine_list')
    else:
        form = UserCreationForm()
    return render(request, 'slots/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            remember_me = form.cleaned_data.get('remember_me', False)
            if not remember_me:
                request.session.set_expiry(0)  
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)  
            return redirect('machine_list')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'slots/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')