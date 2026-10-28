import random

class BaseSlotMachine:
    def __init__(self, reels, win_patterns):
        self.reels = reels
        self.win_patterns = win_patterns
        self.symbols = [str(i) for i in range(10)]

    def spin(self):
        """Quay ngẫu nhiên các trục"""
        return ''.join(random.choice(self.symbols) for _ in range(self.reels))

    def get_payout(self, result, bet):
        """
        Tính toán tiền thắng dựa trên kết quả và cược.
        Trả về: (Tiền thắng, Có nổ hũ hay không)
        """
        hits = [pat for pat in self.win_patterns if pat in result]
        if not hits:
            return 0, False
        
        # Tìm pattern có hệ số thưởng cao nhất
        best_pat = max(hits, key=lambda p: self.win_patterns[p])
        multiplier = self.win_patterns[best_pat]
        payout = bet * multiplier
        
        # Kiểm tra xem pattern này có phải là giải Độc Đắc (Jackpot) không
        jackpot_pattern = max(self.win_patterns, key=lambda p: self.win_patterns[p])
        is_jackpot = (best_pat == jackpot_pattern)
        
        return payout, is_jackpot

    def generate_forced_win(self):
        """
        Hàm hỗ trợ Pity System: Tạo ra một kết quả thắng (giải nhỏ).
        Chọn ngẫu nhiên 1 pattern không phải Jackpot.
        """
        non_jackpot_patterns = [p for p in self.win_patterns.keys() if self.win_patterns[p] < max(self.win_patterns.values())]
        if not non_jackpot_patterns:
            non_jackpot_patterns = list(self.win_patterns.keys())
        
        pattern = random.choice(non_jackpot_patterns)
        
        # Căn chỉnh độ dài pattern cho khớp với số trục (reels)
        # VD: pattern "77", reels 3 -> "770" hoặc "077"
        result_list = ['0'] * self.reels
        for i in range(min(len(pattern), self.reels)):
            result_list[i] = pattern[i]
        
        return ''.join(result_list)