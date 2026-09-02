# Công cụ này giúp bạn thiết lập và xuất file ứng dụng (IPA/DEB) chỉ trong vòng chưa đầy 1 phút. Để sử dụng, hãy làm theo các bước sau:

# Bước chuẩn bị
Đảm bảo bạn đã cài đặt Python 3 trên máy tính/máy ảo (macOS hoặc WSL).

Đảm bảo đã đặt biến môi trường `$THEOS` thành công.

Mở Terminal, trỏ đường dẫn (`cd`) vào thư mục gốc của project (nơi chứa file `auto_build.py`).

## Chạy Công cụ
Khởi chạy tool bằng lệnh:

```bash
  python3 auto_build.py
```

Quy trình các bước thực hiện trên Tool
## 1. Chọn ngôn ngữ:
Tool sẽ yêu cầu bạn nhập *`1`* **(Tiếng Việt)** hoặc *`2`* **(English)**.

## 2. Điền thông tin cơ bản:

**Tên App:** Nhập tên sẽ hiển thị trên màn hình điện thoại (VD: *`Cửa Hàng Của Tôi`*).

**Bundle ID:** Mã định danh duy nhất của app (VD: *`com.cuahang.app`*).

**Link Website:** URL trang web bạn muốn biến thành app (VD: *`https://cuahang.com`*).

## 3. Tùy chỉnh trang HTML Offline:
Tool hỏi bạn có muốn đổi trang báo lỗi (khi mất mạng) không. Nếu chọn `y` (Yes), bạn có *`2`* cách:

**Cách 1 (Đường dẫn file):** Kéo thả file `.html` có sẵn trong máy bạn vào Terminal (hoặc nhập đường dẫn như *`/Users/name/Desktop/offline.html`*).

**Cách 2 (Nhập trực tiếp):** Copy toàn bộ code HTML của bạn và Paste (dán) trực tiếp vào Terminal. Sau khi dán xong, ấn **Enter** xuống một dòng mới, gõ chữ `EOF` và ấn **Enter** để kết thúc quá trình dán.

## 4. Cấp quyền Apple (Permissions):
Tool sẽ lần lượt hỏi bạn 8 quyền phổ biến nhất (*`Camera, Mic, Ảnh, Vị trí, FaceID, Bluetooth, Danh bạ, Lịch`*).

Nếu web của bạn không dùng tính năng nào, hãy gõ `n` (No) để bỏ qua (giúp app sạch hơn, không bị Apple nghi ngờ thu thập dữ liệu).

Nếu web của bạn có dùng tính năng đó, gõ `y` (Yes). Sau đó tool sẽ yêu cầu bạn nhập Lý do. Hãy nhập một câu ngắn gọn (VD: "*`Ứng dụng cần dùng camera để quét mã QR`*"). Câu này sẽ hiện lên màn hình iPhone khi app xin quyền người dùng.

## 5. Tùy chọn Build:

**Build DEB:** Chọn `y` nếu bạn muốn tạo file cho máy đã Jailbreak.

**Build IPA:** Chọn `y` nếu bạn muốn tạo file cài qua `TrollStore / Sideloadly`.
(Bạn có thể chọn `y` cho cả 2 nếu muốn tạo đồng thời).

## 6. Hoàn tất:
Sau khi bạn trả lời xong câu hỏi cuối cùng, tool sẽ tự động sửa toàn bộ code trong project và kích hoạt quy trình Build của Theos. Khi thấy thông báo **HOÀN TẤT!**, bạn chỉ cần mở thư mục `packages/` trong project để lấy file `.ipa` hoặc `.deb` ra cài đặt.
