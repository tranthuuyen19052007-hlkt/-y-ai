import http.server
import socketserver
import json
import urllib.parse
import os
import re
from datetime import datetime, timedelta

PORT = int(os.environ.get("PORT", 8000))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# ==============================================================================
# 1. CATALOG DỮ LIỆU & BẢNG GIÁ NIÊM YẾT HIỆN HÀNH (CÔNG TY MINH AN)
# Phòng tránh lỗi: "Dùng giá cũ" và "Bỏ sót hạng mục phụ kiện/dịch vụ"
# ==============================================================================

PRICE_LIST_VERSION = "PL-2026.Q4-REV2"
PRICE_LIST_EFFECTIVE_DATE = "01/10/2026"

CATALOG_DB = [
    {
        "sku": "DELL-U2723QE",
        "name": "Màn hình Dell UltraSharp 27 inch 4K U2723QE",
        "category": "Màn hình",
        "price": 12500000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 25,
        "restock_days": 5,
        "suggested_accessories": ["Cáp HDMI 2.1 chống nhiễu", "Giá treo màn hình North Bayou"],
        "keywords": ["dell 27", "dell 27 inch", "ultrasharp", "u2723qe", "màn hình dell 4k", "màn 27"]
    },
    {
        "sku": "DELL-P2422H",
        "name": "Màn hình Dell 24 inch P2422H FHD IPS",
        "category": "Màn hình",
        "price": 4200000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 40,
        "restock_days": 3,
        "suggested_accessories": ["Cáp DisplayPort 1.4"],
        "keywords": ["dell 24", "dell 24 inch", "p2422h", "màn hình văn phòng", "màn 24"]
    },
    {
        "sku": "PC-OFFICE-I5",
        "name": "Bộ máy tính văn phòng Minh An Core i5-13400 / 16GB RAM / 512GB NVMe",
        "category": "Máy tính",
        "price": 11800000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 18,
        "restock_days": 4,
        "suggested_accessories": ["Bộ phím chuột Logitech MK120", "Gói bảo hành tận nơi 24 tháng"],
        "keywords": ["pc i5", "máy tính i5", "máy tính văn phòng", "pc văn phòng", "case máy tính", "bộ máy tính"]
    },
    {
        "sku": "CISCO-CBS250-24T",
        "name": "Switch Cisco Business 250 Series 24-Port GE Smart Switch",
        "category": "Thiết bị mạng",
        "price": 8900000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 2, # Tồn kho ít để kích hoạt cảnh báo tiến độ với Vận hành
        "restock_days": 10,
        "suggested_accessories": ["Dịch vụ lắp đặt và cấu hình hệ thống mạng doanh nghiệp", "Dây nhảy mạng Cat6 2m CommsScope"],
        "keywords": ["switch cisco", "switch 24", "switch 24 port", "switch 24-port", "cbs250", "bộ chuyển mạch"]
    },
    {
        "sku": "AP-ARUBA-AP22",
        "name": "Bộ phát WiFi chuyên dụng Aruba Instant On AP22 Wi-Fi 6",
        "category": "Thiết bị mạng",
        "price": 3500000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 15,
        "restock_days": 7,
        "suggested_accessories": ["Adapter nguồn 12V PoE Injector", "Dịch vụ cấu hình WiFi doanh nghiệp"],
        "keywords": ["wifi", "aruba", "ap22", "access point", "bộ phát wifi", "wifi chuyên dụng"]
    },
    {
        "sku": "SVC-INSTALL-NETWORK",
        "name": "Dịch vụ lắp đặt và cấu hình hệ thống mạng doanh nghiệp trọn gói",
        "category": "Dịch vụ CNTT",
        "price": 5000000,
        "price_version": PRICE_LIST_VERSION,
        "stock": 999,
        "restock_days": 1,
        "suggested_accessories": [],
        "keywords": ["lắp đặt mạng", "dịch vụ mạng", "triển khai mạng", "cấu hình mạng", "dịch vụ lắp đặt", "triển khai hệ thống"]
    }
]

SALES_TEAM = [
    {"id": "NV01", "name": "Nguyễn Văn An", "email": "an.nv@minhan.vn", "phone": "0912.111.001", "active_leads": 12},
    {"id": "NV02", "name": "Trần Thị Bình", "email": "binh.tt@minhan.vn", "phone": "0912.111.002", "active_leads": 14},
    {"id": "NV03", "name": "Lê Hoàng Cường", "email": "cuong.lh@minhan.vn", "phone": "0912.111.003", "active_leads": 9},
    {"id": "NV04", "name": "Phạm Thu Dung", "email": "dung.pt@minhan.vn", "phone": "0912.111.004", "active_leads": 11},
    {"id": "NV05", "name": "Vũ Minh Đức", "email": "duc.vm@minhan.vn", "phone": "0912.111.005", "active_leads": 15},
    {"id": "NV06", "name": "Hoàng Ngọc Hạnh", "email": "hanh.hn@minhan.vn", "phone": "0912.111.006", "active_leads": 8}
]

MANAGER_INFO = {
    "name": "Đặng Quốc Thái",
    "role": "Trưởng phòng Kinh doanh B2B",
    "email": "thai.dq@minhan.vn"
}

OPPORTUNITIES_DB = []

# ==============================================================================
# 2. CÁC HÀM TIỆN ÍCH & TRÍCH XUẤT THỰC THỂ
# ==============================================================================

def assign_sales_rep():
    """Phân bổ công bằng cho 6 NVKD theo cơ chế Round-robin cân bằng tải việc"""
    sorted_reps = sorted(SALES_TEAM, key=lambda x: x["active_leads"])
    chosen = sorted_reps[0]
    chosen["active_leads"] += 1
    return chosen

def parse_relative_or_exact_date(text):
    now = datetime.now()
    text_lower = text.lower()
    
    date_match = re.search(r'(\b[0-3]?[0-9])[/-]([0-1]?[0-9])([/-](20\d{2}))?\b', text)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(4)) if date_match.group(4) else now.year
        try:
            return datetime(year, month, day), f"{day:02d}/{month:02d}/{year}"
        except Exception:
            pass

    if "thứ sáu tuần này" in text_lower or "thứ 6 tuần này" in text_lower:
        days_ahead = 4 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target = now + timedelta(days=days_ahead)
        return target, f"Thứ Sáu ({target.strftime('%d/%m/%Y')})"

    days_match = re.search(r'trong\s+(\d+)\s+ngày', text_lower)
    if days_match:
        d = int(days_match.group(1))
        target = now + timedelta(days=d)
        return target, f"Trong {d} ngày ({target.strftime('%d/%m/%Y')})"

    if "gấp" in text_lower:
        target = now + timedelta(days=3)
        return target, f"Gấp trong 3 ngày ({target.strftime('%d/%m/%Y')})"

    target = now + timedelta(days=7)
    return target, "Tiêu chuẩn (7 ngày)"

# ==============================================================================
# 3. WORKFLOW AGENT ENGINES (TUÂN THỦ 100% SƠ ĐỒ QUY TRÌNH MINH AN)
# ==============================================================================

def step_1_and_2_intake_and_classify(raw_text):
    text_lower = raw_text.lower()
    
    email = None
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    if email_match:
        email = email_match.group(0)

    phone = None
    phone_match = re.search(r'(0|\+84)[3|5|7|8|9][0-9]{8}', raw_text)
    if phone_match:
        phone = phone_match.group(0)

    company_name = "Doanh nghiệp liên hệ qua Email / Form"
    company_match = re.search(r'(công ty|cty|doanh nghiệp|tập đoàn|tnhh|cp)\s+([^,\.\n\r]+)', raw_text, re.IGNORECASE)
    if company_match:
        company_name = company_match.group(0).strip()

    contact_person = "Đại diện Quý Doanh nghiệp"
    contact_match = re.search(r'(tôi là|tên tôi là|liên hệ|anh|chị|mình là)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*)', raw_text)
    if contact_match:
        contact_person = contact_match.group(2).strip()

    deadline_dt, deadline_str = parse_relative_or_exact_date(raw_text)

    budget_vnd = None
    budget_declared = False
    budget_match = re.search(r'(\d+([\.,]\d+)?)\s*(triệu|tr|tỷ|vnd|vnđ|đ)', text_lower)
    if budget_match:
        val = float(budget_match.group(1).replace(',', '.'))
        unit = budget_match.group(3)
        budget_vnd = val * 1_000_000_000 if "tỷ" in unit else val * 1_000_000
        budget_declared = True

    discount_pct = 0.0
    discount_match = re.search(r'chiết khấu\s*(\d+(\.\d+)?)%', text_lower)
    if discount_match:
        discount_pct = float(discount_match.group(1))

    items_found = []
    for product in CATALOG_DB:
        matched = False
        for kw in product["keywords"]:
            if kw in text_lower:
                matched = True
                break
        
        if matched:
            qty = 1
            for kw in product["keywords"]:
                p1 = rf'(\d+)\s*(bộ|cái|chiếc|màn|bộ phát|switch|thiết bị)?\s*{re.escape(kw)}'
                p2 = rf'{re.escape(kw)}\s*(\d+)'
                m1 = re.search(p1, text_lower)
                m2 = re.search(p2, text_lower)
                if m1:
                    qty = int(m1.group(1))
                    break
                elif m2:
                    qty = int(m2.group(1))
                    break
            
            if not any(x["sku"] == product["sku"] for x in items_found):
                items_found.append({
                    "sku": product["sku"],
                    "name": product["name"],
                    "category": product["category"],
                    "quantity": qty,
                    "unit_price": product["price"],
                    "price_version": product["price_version"],
                    "stock_available": product["stock"],
                    "restock_days": product["restock_days"],
                    "suggested_accessories": product["suggested_accessories"]
                })

    has_sufficient_items = len(items_found) > 0
    
    clarification_email = None
    if not has_sufficient_items:
        clarification_email = f"""Kính gửi {contact_person},
Lời đầu tiên, Công ty Thiết bị & Dịch vụ Công nghệ Minh An xin gửi lời cảm ơn Quý khách đã quan tâm đến giải pháp của chúng tôi.

Chúng tôi đã tiếp nhận yêu cầu từ Quý công ty. Tuy nhiên, để bộ phận Kỹ thuật & Bán hàng có thể lập Bảng dự thảo chi tiết và chính xác nhất, kính mong Quý khách cung cấp thêm một số thông tin:
1. Danh mục thiết bị/dịch vụ cụ thể cần trang bị (Ví dụ: Số lượng máy tính để bàn, màn hình kích thước bao nhiêu inch, thiết bị mạng...).
2. Thời gian và địa điểm dự kiến Quý công ty cần hoàn thành việc bàn giao & lắp đặt.
3. Dự toán ngân sách dự kiến (nếu có) để Minh An tư vấn cấu hình tối ưu chi phí nhất.

Ngay khi nhận được thông tin bổ sung, chuyên viên kinh doanh của Minh An sẽ phản hồi Báo giá chính thức trong vòng 2 giờ làm việc.

Trân trọng,
Bộ phận Tiếp nhận Cơ hội Kinh doanh - Công ty Minh An
Hotline: 024.3999.8888 | Email: b2b@minhan.vn"""

    return {
        "company_name": company_name,
        "contact_person": contact_person,
        "email": email or "Chưa cung cấp",
        "phone": phone or "Chưa cung cấp",
        "requested_deadline_dt": deadline_dt,
        "requested_deadline_str": deadline_str,
        "budget_vnd": budget_vnd,
        "budget_declared": budget_declared,
        "requested_discount_pct": discount_pct,
        "items": items_found,
        "is_sufficient": has_sufficient_items,
        "clarification_email": clarification_email
    }

def execute_full_workflow(raw_text, follow_up_text=None, parent_opp_id=None):
    full_text = raw_text
    if follow_up_text:
        full_text = f"{raw_text}\n\n[KHÁCH HÀNG BỔ SUNG THÔNG TIN]:\n{follow_up_text}"

    intake = step_1_and_2_intake_and_classify(full_text)
    
    if not intake["is_sufficient"]:
        now = datetime.now()
        temp_opp_id = parent_opp_id or f"OPP-PENDING-{now.strftime('%m%d%H%M')}"
        pending_record = {
            "opp_id": temp_opp_id,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "company_name": intake["company_name"],
            "contact_person": intake["contact_person"],
            "email": intake["email"],
            "phone": intake["phone"],
            "status": "CẦN_LÀM_RÕ",
            "clarification_email": intake["clarification_email"],
            "raw_text": full_text
        }
        return {
            "status": "NEED_CLARIFICATION",
            "message": "Yêu cầu chưa đủ thông tin định lượng. Agent đã lập bản nháp yêu cầu làm rõ gửi khách hàng.",
            "data": pending_record
        }

    now = datetime.now()
    opp_id = parent_opp_id if (parent_opp_id and not parent_opp_id.startswith("OPP-PENDING")) else f"OPP-{now.strftime('%Y%m%d')}-{len(OPPORTUNITIES_DB) + 101}"
    assigned_sales = assign_sales_rep()
    sla_deadline = now + timedelta(hours=2)

    total_list_price = 0
    max_lead_days = 2
    stock_analysis = []
    omitted_accessories_suggested = []

    for it in intake["items"]:
        subtotal = it["unit_price"] * it["quantity"]
        total_list_price += subtotal
        
        is_in_stock = it["quantity"] <= it["stock_available"]
        if not is_in_stock:
            lead_needed = it["restock_days"]
            max_lead_days = max(max_lead_days, lead_needed)
            stock_analysis.append({
                "sku": it["sku"],
                "name": it["name"],
                "requested_qty": it["quantity"],
                "available_qty": it["stock_available"],
                "shortage": it["quantity"] - it["stock_available"],
                "restock_days": lead_needed,
                "status": "THIẾU_HÀNG"
            })
        else:
            stock_analysis.append({
                "sku": it["sku"],
                "name": it["name"],
                "requested_qty": it["quantity"],
                "available_qty": it["stock_available"],
                "shortage": 0,
                "restock_days": 2,
                "status": "ĐỦ_HÀNG_SẴN_SÀNG"
            })

        for acc in it["suggested_accessories"]:
            if not any(acc.lower() in full_text.lower() for acc in [acc]):
                if acc not in omitted_accessories_suggested:
                    omitted_accessories_suggested.append(acc)

    feasible_delivery_dt = now + timedelta(days=max_lead_days)
    feasible_delivery_str = feasible_delivery_dt.strftime("Ngày %d/%m/%Y")

    is_deadline_feasible = True
    deadline_warning_note = None
    if intake["requested_deadline_dt"]:
        if intake["requested_deadline_dt"].date() < feasible_delivery_dt.date():
            is_deadline_feasible = False
            deadline_warning_note = f"Khách yêu cầu giao vào {intake['requested_deadline_str']}, nhưng Vận hành cần tối thiểu đến {feasible_delivery_str} do kẹt tiến độ nhập linh kiện."

    discount_pct = intake["requested_discount_pct"]
    discount_amount = total_list_price * (discount_pct / 100.0)
    price_after_discount = total_list_price - discount_amount
    vat_amount = price_after_discount * 0.10
    final_grand_total = price_after_discount + vat_amount

    requires_approval = False
    approval_reasons = []

    if discount_pct > 5.0:
        requires_approval = True
        approval_reasons.append(f"Mức chiết khấu đề nghị {discount_pct}% vượt thẩm quyền tối đa của NVKD (quy định: tối đa 5.0%).")

    if final_grand_total > 100_000_000:
        requires_approval = True
        approval_reasons.append(f"Quy mô hợp đồng {final_grand_total:,.0f} VNĐ vượt ngưỡng phân quyền của NVKD (quy định: > 100.000.000 VNĐ cần Trưởng phòng duyệt).")

    if not is_deadline_feasible:
        requires_approval = True
        approval_reasons.append(f"Thời hạn giao hàng: {deadline_warning_note} Cần Trưởng phòng duyệt cam kết tiến độ hoặc phương án giao từng phần.")

    budget_mismatch_note = None
    if intake["budget_declared"]:
        if final_grand_total > intake["budget_vnd"]:
            approval_reasons.append(f"Dự toán ({final_grand_total:,.0f} đ) cao hơn ngân sách dự kiến của KH ({intake['budget_vnd']:,.0f} đ).")
            budget_mismatch_note = f"Ngân sách khách hàng: {intake['budget_vnd']:,.0f} đ | Báo giá: {final_grand_total:,.0f} đ (Vượt {final_grand_total - intake['budget_vnd']:,.0f} đ)"

    items_table_lines = []
    for it in intake["items"]:
        items_table_lines.append(
            f"  + {it['name']} ({it['sku']}):\n"
            f"    Số lượng: {it['quantity']} chiếc | Đơn giá: {it['unit_price']:,.0f} VNĐ | Thành tiền: {it['unit_price']*it['quantity']:,.0f} VNĐ"
        )
    items_table_str = "\n".join(items_table_lines)

    customer_proposal_draft = f"""Kính gửi Quý khách hàng / {intake['contact_person']},
Đại diện Công ty Cổ phần Thiết bị & Dịch vụ Công nghệ Minh An, xin chân thành cảm ơn Quý công ty đã tin tưởng gửi yêu cầu báo giá giải pháp thiết bị công nghệ.

Căn cứ theo Bảng giá niêm yết hiện hành ({PRICE_LIST_VERSION}), chúng tôi xin gửi Dự thảo Đề xuất cho Hồ sơ {opp_id}:

1. DANH MỤC THIẾT BỊ BÁO GIÁ:
{items_table_str}

- Tổng giá trị thiết bị (chưa chiết khấu): {total_list_price:,.0f} VNĐ
- Chiết khấu thương mại ({discount_pct}%): -{discount_amount:,.0f} VNĐ
- Thuế VAT (10%): +{vat_amount:,.0f} VNĐ
-----------------------------------------------------------
=> TỔNG CỘNG THANH TOÁN: {final_grand_total:,.0f} VNĐ

2. TIẾN ĐỘ & PHƯƠNG ÁN BÀN GIAO TRIỂN KHAI:
- Thời gian bàn giao hoàn tất khả thi: {feasible_delivery_str}
{f"(*) Lưu ý về tiến độ: Đối với các hạng mục đang trong chu kỳ nhập khẩu, Minh An có thể hỗ trợ phương án bàn giao trước phần thiết bị có sẵn để Quý khách vận hành kịp kế hoạch." if not is_deadline_feasible else "- Hàng hóa có sẵn trong kho, sẵn sàng vận chuyển và lắp đặt ngay theo lịch hẹn."}

3. HẠNG MỤC TƯ VẤN BỔ SUNG (NẾU CẦN):
{f"- Minh An khuyến nghị Quý khách bổ sung: {', '.join(omitted_accessories_suggested)} để hệ thống hoạt động đồng bộ và tối ưu nhất." if len(omitted_accessories_suggested) > 0 else "- Cấu hình trên đã đầy đủ phụ kiện tiêu chuẩn đi kèm."}

Chuyên viên Kinh doanh phụ trách trực tiếp hồ sơ của Quý khách:
- Họ và tên: {assigned_sales['name']}
- Số điện thoại: {assigned_sales['phone']} | Email: {assigned_sales['email']}

Chúng tôi đính kèm Bảng Báo Giá chính thức có dấu mộc điện tử. Kính mong nhận được phản hồi từ Quý công ty.

Trân trọng,
CÔNG TY THIẾT BỊ VÀ DỊCH VỤ CÔNG NGHỆ MINH AN
"""

    opportunity_record = {
        "opp_id": opp_id,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "company_name": intake["company_name"],
        "contact_person": intake["contact_person"],
        "email": intake["email"],
        "phone": intake["phone"],
        "assigned_sales": assigned_sales,
        "sla_deadline": sla_deadline.strftime("%H:%M %d/%m/%Y"),
        "approver": MANAGER_INFO,
        "items": intake["items"],
        "omitted_accessories_suggested": omitted_accessories_suggested,
        "total_list_price": total_list_price,
        "discount_pct": discount_pct,
        "discount_amount": discount_amount,
        "vat_amount": vat_amount,
        "final_grand_total": final_grand_total,
        "budget_declared": intake["budget_declared"],
        "budget_vnd": intake["budget_vnd"],
        "budget_mismatch_note": budget_mismatch_note,
        "requested_deadline": intake["requested_deadline_str"],
        "feasible_deadline": feasible_delivery_str,
        "is_deadline_feasible": is_deadline_feasible,
        "stock_analysis": stock_analysis,
        "requires_approval": requires_approval,
        "approval_reasons": approval_reasons,
        "price_version_used": PRICE_LIST_VERSION,
        "status": "CHỜ_TRƯỞNG_PHÒNG_DUYỆT" if requires_approval else "ĐÃ_SẴN_SÀNG_GỬI_KH",
        "customer_proposal_draft": customer_proposal_draft,
        "raw_text": full_text
    }

    existing_idx = None
    for i, o in enumerate(OPPORTUNITIES_DB):
        if o["opp_id"] == opp_id:
            existing_idx = i
            break
    if existing_idx is not None:
        OPPORTUNITIES_DB[existing_idx] = opportunity_record
    else:
        OPPORTUNITIES_DB.insert(0, opportunity_record)

    return {
        "status": "SUCCESS",
        "opportunity": opportunity_record
    }

# ==============================================================================
# 4. HTTP REQUEST HANDLER
# ==============================================================================

class MinhAnFullHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/api/catalog":
            self.send_json({"version": PRICE_LIST_VERSION, "effective_date": PRICE_LIST_EFFECTIVE_DATE, "products": CATALOG_DB})
        elif path == "/api/sales-team":
            self.send_json(SALES_TEAM)
        elif path == "/api/manager":
            self.send_json(MANAGER_INFO)
        elif path == "/api/opportunities":
            self.send_json(OPPORTUNITIES_DB)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_body) if post_body else {}
        except Exception:
            data = {}

        if path == "/api/process-request":
            raw_text = data.get("text", "")
            follow_up = data.get("follow_up", None)
            opp_id = data.get("opp_id", None)
            if not raw_text.strip():
                self.send_json({"error": "Văn bản yêu cầu không được để trống"}, status=400)
                return
            result = execute_full_workflow(raw_text, follow_up, opp_id)
            self.send_json(result)

        elif path == "/api/approve-opportunity":
            opp_id = data.get("opp_id")
            action = data.get("action", "APPROVE")
            adjusted_discount = data.get("adjusted_discount", None)
            manager_notes = data.get("notes", "")

            target_opp = None
            for opp in OPPORTUNITIES_DB:
                if opp["opp_id"] == opp_id:
                    target_opp = opp
                    break

            if not target_opp:
                self.send_json({"error": "Không tìm thấy hồ sơ cơ hội"}, status=404)
                return

            if action == "APPROVE":
                target_opp["status"] = "ĐÃ_PHÊ_DUYỆT"
                target_opp["requires_approval"] = False
                target_opp["approval_history"] = {
                    "action": "APPROVED",
                    "approver": MANAGER_INFO["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": manager_notes or "Đã phê duyệt theo chính sách khách hàng doanh nghiệp."
                }
            elif action == "REJECT":
                target_opp["status"] = "ĐÃ_TỪ_CHỐI"
                target_opp["requires_approval"] = False
                target_opp["approval_history"] = {
                    "action": "REJECTED",
                    "approver": MANAGER_INFO["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": manager_notes or "Yêu cầu đàm phán lại mức chiết khấu hoặc tiến độ."
                }
            elif action == "ADJUST_DISCOUNT":
                new_disc = float(adjusted_discount)
                target_opp["discount_pct"] = new_disc
                disc_amount = target_opp["total_list_price"] * (new_disc / 100.0)
                after_disc = target_opp["total_list_price"] - disc_amount
                vat = after_disc * 0.10
                target_opp["discount_amount"] = disc_amount
                target_opp["vat_amount"] = vat
                target_opp["final_grand_total"] = after_disc + vat
                target_opp["status"] = "ĐÃ_PHÊ_DUYỆT"
                target_opp["requires_approval"] = False
                target_opp["approval_history"] = {
                    "action": "ADJUSTED_AND_APPROVED",
                    "approver": MANAGER_INFO["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "notes": f"Trưởng phòng điều chỉnh chiết khấu về {new_disc}%. {manager_notes}"
                }

            self.send_json({"success": True, "opportunity": target_opp})

        elif path == "/api/update-stock":
            sku = data.get("sku")
            new_stock = int(data.get("stock", 0))
            for p in CATALOG_DB:
                if p["sku"] == sku:
                    p["stock"] = new_stock
                    self.send_json({"success": True, "product": p})
                    return
            self.send_json({"error": "Không tìm thấy SKU"}, status=404)
        else:
            self.send_error(404, "Not Found")

    def serve_file(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_error(404, "File not found")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MinhAnFullHandler) as httpd:
        print(f"🚀 MINH AN BACKEND RUNNING ON http://localhost:{PORT}")
        httpd.serve_forever()
