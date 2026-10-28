import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.views.decorators.http import require_POST

from .models import SlotMachineType, UserProfile, SpinRecord, Jackpot
from .slot_logic import BaseSlotMachine
from .forms import CustomAuthenticationForm, SpinForm

@login_required
def machine_list(request):
    """
    Hiển thị danh sách máy slot.
    TỐI ƯU: Sử dụng select_related('jackpot') để lấy thông tin hũ (Jackpot) 
    trong cùng 1 câu query, tránh lỗi N+1 Query làm chậm web.
    """
    machines = SlotMachineType.objects.select_related('jackpot').all()
    return render(request, 'slots/machine_list.html', {'machines': machines})

@login_required
def play_machine(request, machine_id):
    machine = get_object_or_404(SlotMachineType, id=machine_id)
    profile = request.user.userprofile
    # Đảm bảo máy chơi có hũ, nếu chưa có thì tạo mới mặc định 1000
    jackpot, _ = Jackpot.objects.get_or_create(machine_type=machine, defaults={'amount': 1000})
    return render(request, 'slots/play.html', {
        'machine': machine,
        'balance': profile.balance,
        'jackpot': jackpot.amount
    })

@login_required
@require_POST
def spin(request, machine_id):
    """
    Xử lý logic quay số.
    Sử dụng transaction.atomic để đảm bảo tính toàn vẹn dữ liệu (tránh race condition).
    """
    try:
        data = json.loads(request.body)
        form = SpinForm(data)
        if not form.is_valid():
            return JsonResponse({'error': 'Dữ liệu cược không hợp lệ.'}, status=400)
        bet = form.cleaned_data['bet']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu gửi lên không phải JSON hợp lệ.'}, status=400)

    machine = get_object_or_404(SlotMachineType, id=machine_id)
    slot = BaseSlotMachine(machine.reels, machine.win_patterns)

    # Sử dụng transaction để khóa dữ liệu (select_for_update), chống spam click
    with transaction.atomic():
        profile = UserProfile.objects.select_for_update().get(user=request.user)
        jackpot, _ = Jackpot.objects.select_for_update().get_or_create(machine_type=machine, defaults={'amount': 1000})

        if bet > profile.balance:
            return JsonResponse({'error': 'Số dư của bạn không đủ.'}, status=400)

        # 1. Trừ tiền cược
        profile.balance -= bet
        profile.spins_count += 1

        # 2. Xử lý Pity System (Hệ thống bù)
        # Nếu thua 10 lần liên tiếp, tự động cho thắng nhỏ để giữ chân người chơi.
        force_win = False
        if profile.consecutive_losses >= 10:
            force_win = True
            profile.consecutive_losses = 0 # Reset chuỗi thua

        is_jackpot = False
        
        # 3. Tính kết quả
        if force_win:
            result = slot.generate_forced_win()
            payout, is_jackpot = slot.get_payout(result, bet)
            if payout == 0: 
                payout = bet * 2 
        else:
            result = slot.spin()
            payout, is_jackpot = slot.get_payout(result, bet)

        # 4. Cập nhật trạng thái thắng/thua
        if payout > 0:
            profile.consecutive_wins += 1
            profile.consecutive_losses = 0
            profile.wins_count += 1
        else:
            profile.consecutive_wins = 0
            profile.consecutive_losses += 1

        # 5. Xử lý Nổ hũ (Jackpot)
        if is_jackpot and payout > 0:
            payout += jackpot.amount     
            jackpot.amount = 1000 # Reset hũ về mức cơ bản
        else:
            # Trích 1% tiền cược vào hũ (tối thiểu $1)
            contribution = max(1, int(bet * 0.01))
            jackpot.amount += contribution
        
        jackpot.save()

        # 6. Cộng tiền thắng vào tài khoản
        profile.balance += payout
        profile.save()

        # 7. Lưu lịch sử
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
        'message': f"🎉 Bạn thắng ${payout}!" if payout > 0 else "😞 Chúc bạn may mắn lần sau.",
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
            if not form.cleaned_data.get('remember_me', False):
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