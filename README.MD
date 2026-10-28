# 🎰 Diamond Casino - Slot Machine Web App

> **Dự án Web Game (Portfolio Project)**  
> Ứng dụng mô phỏng máy quay xổ số (Slot Machine) chuẩn Production, tích hợp kiến trúc **Single Page Application (SPA)** với AJAX và quản lý trạng thái giao diện thông minh.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0.6-green)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)](https://www.sqlite.org/)

---

## 📑 THÔNG TIN DỰ ÁN

- **Tên dự án:** Diamond Casino (Web Game Slot Machine)
- **Mục đích:** Xây dựng một ứng dụng web giải trí trực tuyến, thể hiện kỹ năng Full-stack (Backend Django + Frontend AJAX/Bootstrap).
- **Điểm nhấn kỹ thuật:** Xử lý đồng thời (Concurrency), Hệ thống bù may mắn (Pity System), Giao diện Responsive và Hỗ trợ Dark/Light Mode.

---

## 🚀 TÍNH NĂNG NỔI BẬT

### 1. Kiến trúc Backend & Xử lý dữ liệu (Django)

- **Chống Race Condition (Tranh chấp dữ liệu):** Sử dụng `transaction.atomic()` và `select_for_update()` trong quá trình quay số. Điều này đảm bảo dù người chơi có spam click liên tục, số dư tài khoản và tiền hũ (Jackpot) luôn được tính toán chính xác tuyệt đối.
- **Tối ưu hóa truy vấn (Query Optimization):** Sử dụng `select_related('jackpot')` ở trang chủ để giải quyết triệt để lỗi N+1 Query, giúp giảm tải Database khi hiển thị danh sách máy.
- **Hệ thống Pity (Bù may mắn):** Tự động theo dõi chuỗi thua của người chơi. Nếu thua 10 lần liên tiếp, hệ thống sẽ tự động "ép" ra một kết quả thắng nhỏ để giữ chân người chơi (áp dụng tư duy của các game Gacha hiện đại).
- **Jackpot động:** Trích 1% tiền cược vào hũ. Khi nổ hũ, toàn bộ tiền hũ được cộng vào tài khoản và reset về mức cơ bản.

### 2. Kiến trúc Frontend & UI/UX (Bootstrap 5 & Vanilla JS)

- **AJAX Spin (Không tải lại trang):** Sử dụng `Fetch API` để giao tiếp với Backend. Hiệu ứng quay (Reels) được xử lý mượt mà bằng Javascript với các khoảng thời gian (delay) khác nhau tạo cảm giác hồi hộp.
- **Dark/Light Mode:** Tích hợp công tắc chuyển đổi giao diện (Toggle Switch). Sử dụng `localStorage` để ghi nhớ lựa chọn của người dùng qua các lần tải trang. Màu sắc được quản lý bằng CSS Variables để tối ưu độ tương phản.
- **Giao diện Glassmorphism:** Các thẻ (Card) máy Slot sử dụng hiệu ứng kính mờ, kết hợp viền Vàng (Gold) phát sáng và hiệu ứng Hover nảy lên cực kỳ thu hút.
- **Responsive:** Sử dụng CSS `clamp()` để máy Slot tự động thu nhỏ vừa vặn trên màn hình điện thoại.

---

## 🛠️ CÔNG NGHỆ SỬ DỤNG

| Thành phần | Công nghệ |
| ------------ | ----------- |
| **Backend** | Python 3.11, Django 5.0.6 |
| **Database** | SQLite3 (Mặc định) |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Giao diện** | Bootstrap 5.3.2, FontAwesome, Animate.css |
| **Font chữ** | Google Fonts (Quicksand) |

---

## 📂 CẤU TRÚC THƯ MỤC

```text
mycasino/
├── mycasino/                   # Thư mục cấu hình chính của Django
├── slots/                      # App xử lý logic Game
│   ├── migrations/             # Chứa các file migrate Database
│   ├── static/slots/           
│   │   ├── css/style.css       # Toàn bộ CSS (Dark/Light, Animations)
│   │   └── js/play.js          # Logic AJAX quay số và cập nhật UI
│   ├── templates/slots/        # Chứa các file HTML (base, play, login,...)
│   ├── admin.py                # Đăng ký Models vào trang Admin
│   ├── forms.py                # Form validate (Đăng nhập, Cược)
│   ├── models.py               # Cấu trúc Database (User, Máy, Lịch sử)
│   ├── slot_logic.py           # Chứa thuật toán quay và tính tiền (Core Logic)
│   ├── urls.py                 # Định tuyến URL của app slots
│   └── views.py                # Xử lý logic API và Render giao diện
├── db.sqlite3                  # Database
├── manage.py                   
├── requirements.txt            # Danh sách thư viện
└── README.md                   
```

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT & CHẠY (Sử dụng Conda)

### Bước 1: Tạo môi trường ảo

```bash
conda create -n casino_env python=3.11 -y
conda activate casino_env
```

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Khởi tạo Database & Tạo tài khoản Admin

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Bước 4: Chạy Server

```bash
python manage.py runserver
```

### Bước 5: Cấu hình dữ liệu ban đầu (Bắt buộc)

1. Truy cập vào trang quản trị: `http://127.0.0.1:8000/admin/`
2. Đăng nhập bằng tài khoản Superuser vừa tạo.
3. Vào mục **Slot machine types** -> Bấm **Add**.
4. Điền thông tin cấu hình cho máy, ví dụ:
   - **Name:** Máy Cổ Điển
   - **Reels:** 3
   - **Win patterns:** `{"777": 300, "888": 150, "55": 20}` *(Bắt buộc định dạng JSON)*
5. Bấm **Save**.

Bây giờ bạn có thể truy cập `http://127.0.0.1:8000/`, đăng ký tài khoản và bắt đầu quay thử!

---

## 🧠 TƯ DUY GIẢI THUẬT (CORE LOGIC)

1. **Sinh kết quả quay (`slot_logic.py`):**
   Sử dụng thư viện `random` để chọn ngẫu nhiên các ký tự từ `0-9` cho từng trục. Kết quả trả về là một chuỗi (VD: `"777"`).
2. **Tính toán tiền thắng (`get_payout`):**
   Duyệt qua `win_patterns` (JSON), kiểm tra xem chuỗi kết quả có chứa pattern nào không. Nếu có, lấy pattern có hệ số thưởng cao nhất và nhân với tiền cược.
3. **Ép thắng (`generate_forced_win`):**
   Khi kích hoạt Pity System, thuật toán sẽ loại bỏ pattern Jackpot (để tránh lạm phát tiền tệ), chọn ngẫu nhiên một pattern nhỏ hơn, căn chỉnh độ dài cho khớp với số trục và trả về kết quả.

---

## ⚠️ LƯU Ý KỸ THUẬT

- **Bảo mật:** Đã tích hợp CSRF Token cho mọi request POST (quay số). Dữ liệu cược được validate chặt chẽ từ Server thông qua `SpinForm` để chống hack tiền.
- **Xử lý lỗi:** Nếu mất kết nối mạng trong lúc quay, Javascript sẽ tự động bắt lỗi (`try/catch`), dừng hiệu ứng và thông báo cho người chơi mà không làm đơ trang.
- **Light Mode:** Màu vàng Neon được chuyển thành màu Vàng Hổ Phách (Amber) khi ở Light Mode để đảm bảo người dùng không bị chói mắt và dễ đọc chữ.