document.addEventListener("DOMContentLoaded", function () {
    // 1. KHAI BÁO BIẾN & DOM ELEMENTS
    const symbols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    let spinning = false;
    let intervals = [];

    const reel1 = document.getElementById('reel1');
    const reel2 = document.getElementById('reel2');
    const reel3 = document.getElementById('reel3');
    const spinForm = document.getElementById('spin-form');
    const spinBtn = document.getElementById('spin-btn');
    const betInput = document.getElementById('bet');
    const balanceSpan = document.getElementById('balance');
    const jackpotSpan = document.getElementById('jackpot');
    const resultDiv = document.getElementById('result');
    const navbarBalance = document.getElementById('navbar-balance');

    // 2. HÀM TẠO HIỆU ỨNG QUAY (Bắt đầu)
    function startSpin() {
        // Các trục quay với tốc độ khác nhau để tạo cảm giác chân thực
        intervals[0] = setInterval(() => reel1.innerText = symbols[Math.floor(Math.random() * 10)], 80);
        intervals[1] = setInterval(() => reel2.innerText = symbols[Math.floor(Math.random() * 10)], 60);
        intervals[2] = setInterval(() => reel3.innerText = symbols[Math.floor(Math.random() * 10)], 100);
    }

    // 3. HÀM DỪNG QUAY VÀ HIỂN THỊ KẾT QUẢ (Kết thúc)
    function stopSpin(finalResults) {
        // Dừng lần lượt từng trục từ trái sang phải
        setTimeout(() => {
            clearInterval(intervals[0]);
            reel1.innerText = finalResults[0];
        }, 300);
        setTimeout(() => {
            clearInterval(intervals[1]);
            reel2.innerText = finalResults[1];
        }, 600);
        setTimeout(() => {
            clearInterval(intervals[2]);
            reel3.innerText = finalResults[2];
        }, 900);
    }

    // 4. XỬ LÝ SỰ KIỆN KHI NHẤN NÚT QUAY
    spinForm.addEventListener('submit', async function (e) {
        e.preventDefault(); // Chặn hành vi load lại trang mặc định của Form
        
        if (spinning) return; // Nếu đang quay thì không làm gì cả (chống spam)

        const bet = parseInt(betInput.value);
        const balance = parseInt(balanceSpan.innerText);

        // Validate dữ liệu phía Client trước khi gửi lên Server
        if (isNaN(bet) || bet <= 0 || bet > balance) {
            alert('Số tiền cược không hợp lệ hoặc vượt quá số dư!');
            return;
        }

        // Đổi trạng thái UI (Đang quay)
        spinning = true;
        spinBtn.disabled = true;
        spinBtn.innerText = "ĐANG QUAY...";
        resultDiv.style.display = 'none';
        document.querySelector('.slot-machine')?.classList.remove('win');

        startSpin();

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const machineId = spinForm.dataset.machineId;
            
            // Gửi request AJAX lên Backend
            const response = await fetch(`/machine/${machineId}/spin/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ bet: bet })
            });

            const data = await response.json();

            // Nếu Server trả về lỗi (vd: 400, 500)
            if (!response.ok) {
                throw new Error(data.error || 'Có lỗi xảy ra từ Server');
            }

            // Gọi hàm dừng quay với kết quả từ Server
            stopSpin(data.result.split(''));

            // Đợi hiệu ứng dừng quay xong (1 giây) rồi mới cập nhật giao diện
            setTimeout(() => {
                // Cập nhật số dư (ở form và navbar)
                balanceSpan.innerText = data.new_balance;
                navbarBalance.innerText = data.new_balance;
                
                // Cập nhật Jackpot
                jackpotSpan.innerText = data.jackpot;

                // Hiển thị thông báo thắng/thua
                resultDiv.style.display = 'block';
                resultDiv.className = data.payout > 0 ? 'alert alert-success' : 'alert alert-danger';
                resultDiv.innerText = data.message;

                // Nếu thắng, thêm hiệu ứng phát sáng
                if (data.payout > 0) {
                    document.querySelector('.slot-machine')?.classList.add('win');
                }

                // Mở khóa nút Quay
                spinBtn.disabled = false;
                spinBtn.innerText = "QUAY";
                spinning = false;
                
                // Cập nhật lại max của ô input tiền cược
                betInput.max = data.new_balance;
            }, 1000); // 1000ms khớp với thời gian dừng của trục thứ 3

        } catch (error) {
            // Xử lý khi mất mạng hoặc server lỗi
            console.error('Error:', error);
            alert(error.message);
            
            // Reset lại trạng thái
            intervals.forEach(interval => clearInterval(interval));
            intervals = [];
            spinBtn.disabled = false;
            spinBtn.innerText = "QUAY";
            spinning = false;
            reel1.innerText = '?'; 
            reel2.innerText = '?'; 
            reel3.innerText = '?';
        }
    });
});