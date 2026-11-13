# HỆ THỐNG AI AGENT XỬ LÝ CƠ HỘI BÁN HÀNG B2B - CÔNG TY MINH AN

Hệ thống AI Agent hoàn thiện được thiết kế chuyên biệt để tự động hóa 100% quy trình xử lý cơ hội bán hàng B2B theo sơ đồ nghiệp vụ của **Công ty Minh An**, giải quyết dứt điểm các điểm nghẽn thực tế:
- ❌ **Chấm dứt việc bỏ sót hạng mục:** Tự động đối chiếu phụ kiện/dịch vụ đi kèm (cáp, module, gói lắp đặt...).
- ❌ **Chấm dứt lỗi dùng giá cũ:** Áp dụng bảng giá niêm yết hiện hành thời gian thực (`PL-2026.Q4-REV2`).
- ❌ **Chấm dứt việc hứa sai thời hạn:** Tự động tính toán ngày khả thi theo tồn kho thực tế của Vận hành; cảnh báo xung đột nếu khách yêu cầu gấp.
- ❌ **Chấm dứt đùn đẩy lead:** Phân bổ Round-Robin công bằng cho 6 NVKD, thiết lập SLA đếm ngược 2 giờ và chỉ định đích danh người duyệt.

---

## 🔁 ĐỐI CHIẾU SƠ ĐỒ QUY TRÌNH (WORKFLOW COMPLIANCE)

```text
[Bắt đầu: Tiếp nhận yêu cầu]
         │
         ▼
[Phân loại & Kiểm tra thông tin]
         │
    (Có đủ thông tin?)
    ├── [KHÔNG] ──► [Yêu cầu KH làm rõ/bổ sung] ──► (Khách trả lời) ──► (Quay lại Bắt đầu)
    └── [CÓ]
         │
         ▼
[Tạo Hồ sơ Cơ hội & Gắn người phụ trách (1 trong 6 NVKD)]
         │
         ▼
[Thẩm định tồn kho & giá (NVKD & Vận hành)]
         │
         ▼
[Lập Báo giá & Dự thảo đề xuất]
         │
    (Có vượt thẩm quyền / Cần chiết khấu đặc biệt?)
    ├── [CÓ]   ──► [Trưởng phòng duyệt: Duyệt / Từ chối / Sửa chiết khấu]
    └── [KHÔNG]
         │
         ▼
[Kết thúc: Cập nhật & Theo dõi (Lưu CRM, Xuất Báo giá, In ấn)]
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY TRÊN LOCALHOST

### Cách 1: Chạy bằng file 1-click (Khuyên dùng trên Windows)
Nhấp đúp chuột vào file:
```
run.bat
```
*(Hệ thống sẽ tự động khởi động server và mở trình duyệt web tại `http://localhost:8000`)*

### Cách 2: Chạy qua dòng lệnh Terminal
```bash
python app.py
```
Sau đó mở trình duyệt truy cập: **`http://localhost:8000`**

---

## ☁️ HƯỚNG DẪN DEPLOY LÊN CLOUD (MIỄN PHÍ & DỄ DÀNG)

Dự án được cấu hình chuẩn production với kiến trúc **Zero-dependency** (chỉ dùng Python standard library), sẵn sàng deploy lên mọi nền tảng:

### Cách 1: Deploy lên Render.com (Khuyên dùng - Miễn phí)
1. Đẩy code lên GitHub.
2. Vào [Render.com](https://render.com) > **New Web Service** > Chọn repository của bạn.
3. Cấu hình:
   - **Environment:** `Python 3`
   - **Build Command:** *(để trống)*
   - **Start Command:** `python app.py`
4. Bấm **Deploy Web Service** là xong! Render sẽ tự động gán domain HTTPS miễn phí.

### Cách 2: Deploy lên Railway.app
1. Vào [Railway.app](https://railway.app) > **New Project** > **Deploy from GitHub repo**.
2. Railway sẽ tự động nhận diện file `Procfile` và khởi chạy ngay lập tức.

### Cách 3: Deploy bằng Docker
```bash
docker build -t minhan-ai-agent .
docker run -p 8000:8000 minhan-ai-agent
```

### Cách 4: Deploy Static (GitHub Pages / Vercel / Netlify)
Nhờ kiến trúc **Dual-Engine**, toàn bộ logic AI Agent đã được đóng gói trực tiếp trong giao diện frontend:
- Bạn chỉ cần upload thư mục `static/` lên **GitHub Pages**, **Vercel** hoặc **Netlify**.
- Toàn bộ tính năng tiếp nhận, xử lý báo giá, check tồn kho và duyệt đơn đều chạy mượt mà ngay trên trình duyệt mà không cần cài server!

---

## 🎯 HƯỚNG DẪN THỬ NGHIỆM 3 KỊCH BẢN THỰC TẾ

Trên giao diện web đã tích hợp sẵn 3 nút thử nghiệm nhanh:

1. **🟢 Kịch bản 1 (Đơn chuẩn - Tự động duyệt):**
   - Đủ thông tin (5 PC i5 + 5 màn hình Dell 24 inch, chiết khấu 3%).
   - Tồn kho đầy đủ $\rightarrow$ Hoàn thành thẩm định và xuất bản nháp email sẵn sàng gửi cho khách.
2. **🟡 Kịch bản 2 (Thiếu thông tin & Vòng lặp làm rõ):**
   - Khách hỏi chung chung "muốn nâng cấp máy tính...".
   - Agent kích hoạt nhánh: Soạn email xin làm rõ.
   - **Vòng lặp tương tác:** Có khung nhập câu trả lời của khách hàng $\rightarrow$ bấm *"Cập nhật & Chuyển sang Tạo Hồ sơ"* để Agent tiếp tục quy trình.
3. **🔴 Kịch bản 3 (Vượt thẩm quyền & Kẹt kho):**
   - Khách cần gấp 15 màn hình 4K + 5 Switch Cisco 24-Port, xin chiết khấu 8%.
   - Kho chỉ còn 2 Switch (cần thêm 10 ngày nhập hàng), chiết khấu > 5% $\rightarrow$ Chuyển sang Tab *"Trưởng phòng duyệt"*.
   - Trưởng phòng có thể bấm: **Duyệt**, **Từ chối**, hoặc **Điều chỉnh lại mức chiết khấu** (ví dụ chỉnh về 6% và duyệt).

---

## 📁 DANH MỤC FILE DỰ ÁN

- [`app.py`](file:///c:/Users/Acer/New%20folder/app.py): Backend Python xử lý toàn bộ logic 6 bước Agent, REST API, Database giả định (Catalog, 6 NVKD, Opportunities).
- [`static/index.html`](file:///c:/Users/Acer/New%20folder/static/index.html): Giao diện Single Page Dashboard trực quan, tương tác thời gian thực.
- [`run.bat`](file:///c:/Users/Acer/New%20folder/run.bat): Launcher 1-click cho Windows.
- [`README.md`](file:///c:/Users/Acer/New%20folder/README.md): Tài liệu hướng dẫn chi tiết.
