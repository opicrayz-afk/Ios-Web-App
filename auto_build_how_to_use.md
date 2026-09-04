# Công cụ này giúp bạn thiết lập và xuất file ứng dụng (IPA/DEB) chỉ trong vòng chưa đầy 1 phút. Để sử dụng, hãy làm theo các bước sau:

# Bước chuẩn bị
Đảm bảo bạn đã cài đặt Python 3 trên máy tính/máy ảo (*`macOS hoặc WSL`*).

Đảm bảo đã đặt biến môi trường `$THEOS` thành công.

Mở Terminal, trỏ đường dẫn (`cd`) vào thư mục gốc của project (nơi chứa file `auto_build.py`).

Lưu ý: Bạn chỉ cần bỏ ảnh Icon của bạn vào thư mục `Resources` (Hỗ trợ mọi định dạng: `.png, .jpg, .jpeg, .webp, .gif...`). Tool sẽ tự động quét, chọn file ưu tiên cao nhất làm App Icon chuẩn và dọn dẹp sạch sẽ các file rác của hệ điều hành.

Chạy Công cụ
Khởi chạy tool bằng lệnh:

```bash
  python3 auto_build.py
```
Quy trình các bước thực hiện trên Tool

1. Chọn ngôn ngữ:
Tool sẽ yêu cầu bạn nhập 1 (Tiếng Việt) hoặc 2 (English). Ngay sau bước này, tool sẽ âm thầm sao lưu (Backup) 100% mã nguồn gốc của bạn vào RAM để đảm bảo an toàn tuyệt đối.

2. Điền thông tin cơ bản:
Tên App: Nhập tên sẽ hiển thị trên màn hình điện thoại (VD: Cửa Hàng Của Tôi).

Bundle ID: Mã định danh duy nhất của app (VD: com.cuahang.app).

Link Website: URL trang web bạn muốn biến thành app (VD: https://cuahang.com).

(Các thông tin bổ sung: Tool sẽ hỏi thêm về Version, Tên tác giả và Phiên bản iOS tối thiểu. Bạn có thể ấn Enter để dùng giá trị mặc định).

3. Tùy chỉnh trang HTML Offline:
Tool hỏi bạn có muốn đổi trang báo lỗi (khi mất mạng) không. Nếu chọn y (Yes), bạn có 2 cách:

Cách 1 (Đường dẫn file): Kéo thả file .html có sẵn trong máy bạn vào Terminal (hoặc nhập đường dẫn như /Users/name/Desktop/index.html).

Cách 2 (Nhập trực tiếp): Copy toàn bộ code HTML của bạn và Paste (dán) trực tiếp vào Terminal. Sau khi dán xong, ấn Enter xuống một dòng mới, gõ chữ EOF và ấn Enter để kết thúc quá trình dán.

4. Tính năng Thoát ứng dụng (Exit App):
Tool sẽ hỏi bạn có muốn bật tính năng thoát ứng dụng không. Nếu chọn y, bạn có thể gán link app://exit vào bất kỳ nút bấm nào trên HTML web của bạn để đóng app ngay lập tức như một ứng dụng Native thực thụ.

5. Cấp quyền Apple (Permissions):
Tool sẽ lần lượt hỏi bạn toàn bộ các quyền trong hệ sinh thái Apple, chia làm 2 nhóm:

Nhóm Quyền Thông Dụng: (Camera, Mic, Ảnh, Vị trí, FaceID, App Tracking, Thông báo, Lời nhắc, Danh bạ, Lịch...).
Nếu web của bạn có dùng tính năng đó, gõ y (Yes). Sau đó tool sẽ yêu cầu bạn nhập Lý do ngắn gọn (VD: "Ứng dụng cần dùng camera để quét mã QR").

Nhóm Quyền Đặc Biệt (Restricted): (HealthKit, HomeKit, Siri, Apple Pay, VPN).
⚠️ LƯU Ý QUAN TRỌNG: Khi bạn chọn các quyền này, tool sẽ hiện cảnh báo đỏ. Đây là các quyền can thiệp sâu, BẮT BUỘC phải có tệp chứng chỉ .entitlements và tài khoản Apple Developer 99$/năm. Nếu bạn không có chứng chỉ mà vẫn ấn y để cố tình build, app sẽ bị văng (Crash) ngay khi mở! Hãy chọn n nếu bạn dùng chứng chỉ miễn phí (Sideloadly/TrollStore).

6. Tùy chọn Build:
Build DEB: Chọn y nếu bạn muốn tạo file cho máy đã Jailbreak.

Build IPA: Chọn y nếu bạn muốn tạo file cài qua TrollStore / Sideloadly.

(Bạn có thể chọn y cho cả 2 nếu muốn tạo đồng thời).

7. Hoàn tất & Tự động Khôi phục:
Sau khi build xong (dù thành công hay lỗi), tool sẽ tự động Khôi phục (Restore) lại chính xác 100% mã nguồn gốc và file Icon ban đầu của bạn. Khi thấy thông báo HOÀN TẤT!, bạn chỉ cần mở thư mục packages/ trong project để lấy file .ipa hoặc .deb ra cài đặt.

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# This tool helps you set up and export application files (IPA/DEB) in under a minute. To use it, follow the steps below:

# Preparation
Make sure you have Python 3 installed on your computer/virtual machine (macOS or WSL).

Ensure that the $THEOS environment variable has been set successfully.

Open Terminal, navigate (cd) to the root directory of the project (where the auto_build.py file is located).

Note: You only need to drop your Icon image into the Resources folder (Supports all formats: .png, .jpg, .jpeg, .webp, .gif...). The tool will automatically scan, prioritize the best format as the standard App Icon, and clean up all OS junk files.

Running the Tool
Launch the tool with the command:
```bash
python3 auto_build.py
```
Workflow steps within the Tool

1. Choose language:
The tool will ask you to enter 1 (Vietnamese) or 2 (English). Immediately after this, the tool will silently backup 100% of your original source code to RAM for absolute safety.

2. Enter basic information:
App Name: Enter the name that will appear on the phone screen (e.g., My Store).

Bundle ID: Unique identifier for the app (e.g., com.mystore.app).

Website Link: The URL of the website you want to turn into an app (e.g., https://mystore.com).

(Additional info: The tool will also ask for Version, Author Name, and Minimum iOS Version. You can press Enter to use default values).

3. Customize the offline HTML page:
The tool asks if you want to change the error page (when offline). If you choose y (Yes), you have 2 options:

Option 1 (File path): Drag and drop an .html file from your computer into the Terminal (or enter the path like /Users/name/Desktop/index.html).

Option 2 (Direct input): Copy your entire HTML code and paste it directly into the Terminal. After pasting, press Enter to go to a new line, type EOF, and press Enter again to finish the paste process.

4. Exit App Feature:
The tool will ask if you want to enable the exit application feature. If you choose y, you can assign the link app://exit to any button in your HTML web code to forcefully close the app instantly like a real Native application.

5. Apple Permissions:
The tool will sequentially ask you about all permissions in the Apple ecosystem, divided into 2 groups:

Common Permissions: (Camera, Mic, Photos, Location, FaceID, App Tracking, Notifications, Reminders, Contacts, Calendar...).
If your website uses a feature, type y (Yes). The tool will then ask for a short Reason (e.g., "The app needs to use the camera to scan QR codes").

Restricted Permissions: (HealthKit, HomeKit, Siri, Apple Pay, VPN).
⚠️ CRITICAL NOTE: When you select these, the tool will display a red warning. These are deep-level permissions that REQUIRE an .entitlements file and a $99/year Apple Developer account. If you force an injection by pressing y without entitlements, the app will Crash immediately upon opening! Choose n if you use free certificates (Sideloadly/TrollStore).

6. Build Options:
Build DEB: Choose y if you want to create a file for Jailbroken devices.

Build IPA: Choose y if you want to create a file for installation via TrollStore / Sideloadly.

(You can choose y for both if you want to generate them simultaneously).

7. Completion & Auto-Restore:
After the build process is complete (whether successful or failed), the tool will automatically Restore your original source code and Icon file precisely 100%. When you see the COMPLETED! message, simply open the packages/ folder in the project to retrieve the .ipa or .deb file and install it.
