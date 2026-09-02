# Web Ios App — Theos application

Ứng dụng iOS 13+ dùng `WKWebView`. Khi có mạng, nó mở `https://linkwebsitecuaban`; nếu tải trang thất bại, nó dùng `Resources/index.html` trong bundle.

Project chỉ build slice `arm64`. Đây là lựa chọn cố ý: nó chạy được cả máy arm64 và arm64e, đồng thời tránh ABI arm64e không tương thích khi deployment target là iOS 13.

## Cấu trúc

```text
Tenduancuaban/
├── Makefile
├── main.m
├── AppDelegate.h/.m
├── ViewController.h/.m
├── Info.plist
├── Entitlements.plist
├── control
├── Resources/index.html
├── Resources/app_icon
└── build.sh
```

`ViewController` bật JavaScript, DOM storage mặc định của WebKit, media inline/PiP và autoplay; xử lý `input[type=file]` bằng trình chọn tài liệu cho ảnh, âm thanh và video. Camera/micro/photo library được iOS hỏi quyền khi ứng dụng mở; trên iOS 15+, trang `linkwebsitecuaban` cũng nhận cấp phép WebKit cho `getUserMedia`. Tệp được chọn từng tệp một để tương thích tuyệt đối với bộ SDK Theos iOS 13–16. `Info.plist` được khai báo như bundle resource để Theos đặt nó ở đúng gốc của `.app`—điều kiện bắt buộc để IPA cài và mở được.

## Chuẩn bị trên macOS

1. Cài Xcode đầy đủ, mở Xcode một lần, sau đó chạy `xcode-select --install` nếu máy yêu cầu Command Line Tools.
2. Cài Theos theo tài liệu chính thức và đặt biến môi trường, ví dụ `export THEOS="$HOME/theos"`.
3. Đảm bảo SDK iPhoneOS trong `$THEOS/sdks` hoặc dùng SDK của Xcode theo cấu hình Theos của bạn.
4. Trong thư mục project, chạy `chmod +x build.sh` rồi `./build.sh`.

## Chuẩn bị trên WSL

Theos có thể biên dịch chéo trên Linux/WSL khi đã cài toolchain và iOS SDK tương thích. WSL không có Apple code-signing identity, vì vậy chỉ tạo IPA **chưa ký**. Hãy chuyển IPA sang macOS để ký, hoặc ký qua dịch vụ/CI macOS mà bạn kiểm soát.

```bash
export THEOS="$HOME/theos"
chmod +x build.sh
./build.sh
```

## Kết quả build

```bash
make package  # packages/bundleidcuaban_1.0.0_iphoneos-arm.deb
make ipa      # packages/tenappcuaban.ipa (chưa ký nếu không truyền biến)
make verify-ipa # kiểm tra IPA có Info.plist, executable và index.html
```

`make package` dành cho jailbreak rootful. Với jailbreak rootless, chạy `make package THEOS_PACKAGE_SCHEME=rootless` và thay `Architecture` trong `control` thành `iphoneos-arm64` trước khi phát hành gói rootless.

## IPA cho máy không jailbreak

IPA phải được ký bằng certificate/provisioning profile khớp với bundle identifier `bundleidcuaban`. Dùng lệnh sau trên macOS (thay đúng tên certificate/profile của bạn):

```bash
make ipa \
  SIGN_IDENTITY="Apple Development: Your Name (TEAMID)" \
  PROVISIONING_PROFILE="$HOME/Profiles/tenappcuaban.mobileprovision"
```
Lệnh đưa profile vào `embedded.mobileprovision`, ký `.app`, rồi đóng `Payload/tenappcuaban.app` thành IPA. Sau đó cài bằng Xcode Devices and Simulators, Apple Configurator, hoặc quy trình MDM/Ad Hoc/TestFlight phù hợp với profile. Không thể cài hợp lệ lên máy không jailbreak nếu không có ký số Apple hợp lệ.

## Cài DEB trên máy jailbreak

Chép file trong `packages/` sang máy, rồi dùng trình quản lý gói như Sileo/Zebra hoặc cài qua SSH:

```bash
scp packages/bundleidcuaban_1.0.0_iphoneos-arm.deb root@DEVICE_IP:/var/mobile/
ssh root@DEVICE_IP 'dpkg -i /var/mobile/bundleidcuaban_1.0.0_iphoneos-arm.deb'
```

Trên jailbreak rootless, dùng file DEB đã build với scheme `rootless`, không dùng package rootful.

## Thay HTML offline

`Resources/index.html` đã là bản sao của file HTML được cung cấp. Muốn thay mới rồi build:

```bash
./build.sh /duong-dan/index.html
```

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Web Ios App — Theos application

An iOS 13+ application using `WKWebView`. When online, it loads `https://yourwebsitelink`; if the page fails to load, it falls back to `Resources/index.html` within the bundle.

The project only builds the `arm64` slice. This is an intentional choice: it runs on both arm64 and arm64e devices, while avoiding arm64e ABI incompatibilities when the deployment target is set to iOS 13.

## Structure

```text
Yourprojectname/
├── Makefile
├── main.m
├── AppDelegate.h/.m
├── ViewController.h/.m
├── Info.plist
├── Entitlements.plist
├── control
├── Resources/index.html
├── Resources/app_icon
└── build.sh
```

`ViewController` enables JavaScript, default WebKit DOM storage, inline/PiP media, and autoplay; it handles `input[type=file]` using the document picker for images, audio, and video. iOS requests Camera/Microphone/Photo Library permissions when the app opens; on iOS 15+, the `yourwebsitelink` page also receives WebKit authorization for `getUserMedia`. Files are selected one by one for absolute compatibility with the iOS 13–16 Theos SDK. `Info.plist` is declared as a bundle resource so Theos places it at the exact root of the `.app`—a mandatory requirement for the IPA to be installed and opened.

## Prerequisites on macOS

1. Install the full version of Xcode, open it once, and then run `xcode-select --install` if your machine requests Command Line Tools.
2. Install Theos according to the official documentation and set the environment variable, e.g., `export THEOS="$HOME/theos"`.
3. Ensure the iPhoneOS SDK is present in `$THEOS/sdks` or use Xcode's SDK based on your Theos configuration.
4. In the project directory, run `chmod +x build.sh` followed by `./build.sh`.

## Prerequisites on WSL

Theos can cross-compile on Linux/WSL once a compatible toolchain and iOS SDK are installed. WSL does not have an Apple code-signing identity, so it will only generate an **unsigned** IPA. Transfer the IPA to macOS for signing, or sign it via a macOS CI/service that you control.

```bash
export THEOS="$HOME/theos"
chmod +x build.sh
./build.sh
```

## Build Results

```bash
make package  # packages/yourbundleid_1.0.0_iphoneos-arm.deb
make ipa      # packages/yourappname.ipa (unsigned if no variables are passed)
make verify-ipa # verify IPA contains Info.plist, executable, and index.html
```

`make package` is intended for rootful jailbreaks. For rootless jailbreaks, run `make package THEOS_PACKAGE_SCHEME=rootless` and change the `Architecture` in the `control` file to `iphoneos-arm64` before releasing the rootless package.

## IPA for Non-Jailbroken Devices

The IPA must be signed with a certificate/provisioning profile that matches the `yourbundleid` bundle identifier. Use the following command on macOS (replace with your actual certificate/profile names):

```bash
make ipa \
  SIGN_IDENTITY="Apple Development: Your Name (TEAMID)" \
  PROVISIONING_PROFILE="$HOME/Profiles/yourappname.mobileprovision"
```

The command injects the profile into `embedded.mobileprovision`, signs the `.app`, and then packages `Payload/yourappname.app` into an IPA. Afterward, install it using Xcode Devices and Simulators, Apple Configurator, or via an MDM/Ad Hoc/TestFlight process suited for your profile. It cannot be validly installed on a non-jailbroken device without a valid Apple digital signature.

## Installing the DEB on Jailbroken Devices

Copy the file from `packages/` to your device, then use a package manager like Sileo/Zebra or install it via SSH:

```bash
scp packages/yourbundleid_1.0.0_iphoneos-arm.deb root@DEVICE_IP:/var/mobile/
ssh root@DEVICE_IP 'dpkg -i /var/mobile/yourbundleid_1.0.0_iphoneos-arm.deb'
```

On rootless jailbreaks, use the DEB file built with the `rootless` scheme; do not use the rootful package.

## Replacing Offline HTML

`Resources/index.html` is already a copy of the provided HTML file. To replace it with a new one and build:

```bash
./build.sh /path-to/index.html
```

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Giấy phép / License 
Copyright © 2026 *opicrayz-afk*.

Phát hành theo [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).

Fork / phân phối phải tuân thủ GPL (công khai mã nguồn tương ứng). Chi tiết: [LICENSE](https://github.com/opicrayz-afk/Web-Ios-App-/blob/main/LICENSE).

Released under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html) (GPL-3.0).

Forks / distributions must comply with the GPL (disclosing the corresponding source code). Details: [LICENSE](https://github.com/opicrayz-afk/Web-Ios-App-/blob/main/LICENSE).
