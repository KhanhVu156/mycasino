import random

class BaseSlotMachine:
    def __init__(self, reels, win_patterns):
        self.reels = reels
        self.win_patterns = win_patterns
        self.symbols = [str(i) for i in range(10)]

    def spin(self):
        return ''.join(random.choice(self.symbols) for _ in range(self.reels))

    def get_payout(self, result, bet):
        hits = [pat for pat in self.win_patterns if pat in result]
        if not hits:
            return 0, False
        best_pat = max(hits, key=lambda p: self.win_patterns[p])
        multiplier = self.win_patterns[best_pat]
        payout = bet * multiplier
        jackpot_pattern = max(self.win_patterns, key=lambda p: self.win_patterns[p])
        is_jackpot = (best_pat == jackpot_pattern)
        return payout, is_jackpot