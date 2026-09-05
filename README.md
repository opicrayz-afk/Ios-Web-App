# iOS Web App — Theos Application (Ultimate Multi-Tab)

Ứng dụng iOS 14+ dùng WKWebView mạnh mẽ, được thiết kế để tự động hóa 100% cấu hình thông qua Python (auto_build.py). Khi có mạng, ứng dụng mở trang web của bạn; nếu tải trang thất bại, nó dùng giao diện báo lỗi ngoại tuyến an toàn.

Dự án này là một bước đột phá trong việc chuyển đổi Web thành App Native, hỗ trợ kiến trúc linh hoạt, tự động chuyển đổi dựa trên số lượng trang web bạn khai báo:

Chế độ 1 Tab: Giao diện web tràn viền (tràn qua Home Indicator), vuốt mượt mà, tích hợp nút "Settings" nổi với hiệu ứng kính mờ (Frosted glass).

Chế độ Đa Tab (Multi-Tab): Thanh điều hướng dưới cùng (Liquid Glass Tab Bar) chuẩn Apple, tích hợp hệ thống lưu trạng thái độc lập cho từng tab.

Dự án chỉ build slice arm64 (Makefile) để tương thích hoàn hảo với các thiết bị iOS hiện đại và tránh lỗi ABI arm64e.

🌟 Tính Năng Độc Quyền (Ultimate Features)

Auto-Build 100% bằng Python (auto_build.py):
Chỉ cần trả lời các câu hỏi trên Terminal trong 1 phút, Python sẽ tự động cấu hình Tên App, Bundle ID, UI/UX, Version và kích hoạt lệnh build của Theos. Đặc biệt, mã nguồn luôn được Backup và Khôi phục 100% sau mỗi lần build.

Kiến trúc Liquid Glass UI (ViewController.m):
Thanh Tab Bar áp dụng hiệu ứng kính mờ chuẩn hệ thống Apple. Khi người dùng vuốt đọc báo hoặc xem phim, Tab Bar tự động mờ dần và biến mất (Auto-hide) để giải phóng 100% diện tích màn hình. Khi vuốt ngược lên, Tab Bar sẽ hiện lại. Tối ưu vùng Safe Area để né Tai thỏ/Dynamic Island.

In-App Settings (Cài đặt nội bộ):
App tích hợp sẵn một Tab Settings (Bánh răng) cho phép bạn quản lý app trực tiếp trên điện thoại:

Thay đổi App Icon trực tiếp mà không cần build lại (Khai báo tự động qua CFBundleAlternateIcons trong Info.plist).

Thêm, Sửa (Tên & URL), Xóa các Web Tabs dễ dàng. Dữ liệu được lưu vĩnh viễn vào NSUserDefaults.

Xem thông tin thiết bị (Mã máy, Phiên bản iOS, Bundle ID).

Userscript / Tampermonkey Injector:
Trong phần Settings, mỗi Tab web có một trình soạn thảo JavaScript riêng biệt. Bạn có thể chèn mã chặn quảng cáo, thay đổi giao diện web... và bật/tắt độc lập cho từng tab.

Hệ sinh thái Quyền (Apple Permissions):
Hỗ trợ xin cấp quyền tự động cho: Camera, Mic, Ảnh, FaceID, Vị trí, Thông báo (Push/Local), Lời nhắc, App Tracking... Tích hợp cảnh báo thông minh chống Crash khi xin các quyền đặc biệt (như Apple Pay, VPN) mà thiếu chứng chỉ.

📂 Cấu Trúc Dự Án
```text
Tenduancuaban/
├── Makefile
├── main.m
├── AppDelegate.h/.m
├── ViewController.h/.m
├── Info.plist
├── control
├── auto_build.py
└── Resources/
    ├── index.html
    └── app_icon.png|.jpg|.webp|.bmp|.gif
```

(Lưu ý: Chỉ cần thả ảnh Icon bất kỳ định dạng nào vào thư mục Resources, Python sẽ tự động lọc định dạng tốt nhất, ghi vào Info.plist và dọn dẹp sạch sẽ các file rác của hệ điều hành).

🛠 Chuẩn bị Môi trường Build

1. Trên macOS

Cài đặt Xcode đầy đủ, mở Xcode ít nhất một lần để nhận giấy phép. Chạy xcode-select --install để cài đặt Command Line Tools.

Cài đặt Theos và cấu hình biến môi trường: export THEOS="$HOME/theos".

Đảm bảo bạn có SDK iOS (khuyên dùng iOS 14.x trở lên) nằm trong thư mục $THEOS/sdks.

2. Trên Windows (WSL) / Linux

Theos hỗ trợ biên dịch chéo rất tốt trên Linux/WSL. Tuy nhiên, WSL không thể ký số (Code-Signing) của Apple, nên app xuất ra sẽ là IPA chưa ký (Unsigned). Bạn có thể dùng TrollStore, Sideloadly hoặc AltStore để cài đặt.
Cấu hình biến môi trường tương tự: export THEOS="$HOME/theos".

🚀 Hướng dẫn Sử dụng (Build App)

Mở Terminal, truy cập vào thư mục mã nguồn và khởi chạy công cụ Python:

```bash
python3 auto_build.py
```

Công cụ sẽ hướng dẫn bạn qua các bước:

Ngôn ngữ: Chọn Tiếng Việt hoặc English.

Thông tin: Nhập Tên App, Bundle ID, số lượng Tab và khai báo URL cho từng Tab.

Quyền: Chọn y/n cho từng quyền bạn muốn App yêu cầu. Chú ý các cảnh báo màu đỏ.

Đóng gói: Chọn Build DEB hoặc IPA.

📦 Xuất bản và Cài đặt

Kết quả build sẽ nằm trong thư mục packages/:

make package -> Tạo file .deb (Dành cho máy Jailbreak).

make ipa -> Tạo file .ipa (Dành cho Sideload/TrollStore/Ký số).

Cài đặt lên máy chưa Jailbreak:
Bạn cần ký số file IPA bằng chứng chỉ Apple Developer:

```bash
make ipa SIGN_IDENTITY="Apple Development: Tên Bạn (TEAMID)" PROVISIONING_PROFILE="$HOME/Profiles/tenapp.mobileprovision"
```

Hoặc đơn giản hơn: Kéo file .ipa vào các công cụ miễn phí như Sideloadly, AltStore, hoặc TrollStore.

Cài đặt lên máy đã Jailbreak:

```bash
scp packages/tenapp_1.0.0_iphoneos-arm.deb root@IP_CỦA_IPHONE:/var/mobile/
ssh root@IP_CỦA_IPHONE 'dpkg -i /var/mobile/tenapp_1.0.0_iphoneos-arm.deb'
```

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# iOS Web App — Theos Application (Ultimate Multi-Tab)

An iOS 14+ application using a powerful WKWebView, 100% automated via a Python script (auto_build.py). When online, it loads your websites; if the page fails to load, it falls back to a custom offline UI.

This project is a breakthrough in Web-to-Native transformation, supporting a dynamic architecture that automatically switches based on the number of websites:

Single-Tab Mode: Fullscreen web view (spanning across the Home Indicator), smooth scrolling, with a frosted glass floating "Settings" button.

Multi-Tab Mode: A Liquid Glass Tab Bar at the bottom, integrating an independent state preservation system for each tab.

The project intentionally builds only the arm64 slice (Makefile) to ensure perfect compatibility with modern iOS devices and avoid arm64e ABI issues.

🌟 Ultimate Features

100% Python Auto-Build (auto_build.py):
Answer simple Terminal prompts in 1 minute, and Python configures the App Name, Bundle ID, UI/UX, Version, and triggers the Theos build. Your original source code is 100% Backed Up and Restored automatically after every build.

Liquid Glass UI Architecture (ViewController.m):
The Tab Bar uses Apple's native frosted glass effect. When users scroll down to read or watch videos, the Tab Bar fades out (Auto-hide) to free up 100% of the screen. Scrolling up brings it back. Safe areas are optimized for the Notch/Dynamic Island.

In-App Settings:
A built-in Settings Tab (Gear icon) lets you manage the app directly on the device:

Change the App Icon instantly without rebuilding (Configured via CFBundleAlternateIcons in Info.plist).

Add, Edit (Name & URL), or Delete Web Tabs dynamically. Data is permanently saved to NSUserDefaults.

View device info (Device Model, iOS Version, Bundle ID).

Userscript / Tampermonkey Injector:
Inside Settings, each Web Tab has its own JavaScript editor. You can inject ad-blockers or custom UI scripts and toggle them independently.

Apple Permissions Ecosystem:
Auto-request permissions for Camera, Mic, Photos, FaceID, Location, Push Notifications, Reminders, App Tracking, etc. Built-in smart warnings prevent App Crashes when requesting restricted permissions (like Apple Pay, VPN) without proper entitlements.

📂 Project Structure
```text
Yourprojectname/
├── Makefile
├── main.m
├── AppDelegate.h/.m
├── ViewController.h/.m
├── Info.plist
├── control
├── auto_build.py
└── Resources/
    ├── index.html
    └── app_icon.png|.jpg|.webp|.bmp|.gif
```

(Note: Just drop an Icon image of any format into Resources. Python will pick the best format, inject it into Info.plist, and clean up OS junk files automatically).

🚀 How to Build

Open Terminal, navigate to the source folder, and run:

```bash
python3 auto_build.py
```

The tool will guide you:

Language: Choose Vietnamese or English.

Info: Enter App Name, Bundle ID, number of Tabs, and their URLs.

Permissions: Choose y/n for Apple permissions. Pay attention to red restricted warnings.

Package: Choose DEB or IPA.

The generated files (.ipa or .deb) will be saved in the packages/ directory!

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Giấy phép / License 
## Copyright © 2026 *opicrayz-afk*.

Phát hành theo [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).

Fork / phân phối phải tuân thủ GPL (công khai mã nguồn tương ứng). Chi tiết: [LICENSE](https://github.com/opicrayz-afk/Web-Ios-App-/blob/main/LICENSE).

Released under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).

Forks / distributions must comply with the GPL (disclosing the corresponding source code). Details: [LICENSE](https://github.com/opicrayz-afk/Web-Ios-App-/blob/main/LICENSE).
