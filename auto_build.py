import os
import sys
import re
import plistlib
import shutil
import subprocess

# ANSI Color Codes for beautiful terminal styling
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

TEXTS = {
    'vi': {
        'header': "CÔNG CỤ TỰ ĐỘNG BUILD IOS WEB APP NÂNG CAO",
        'ask_app_name': "Nhập tên App (Bắt buộc): ",
        'ask_bundle_id': "Nhập Bundle ID (VD: com.myname.myapp) (Bắt buộc): ",
        'ask_url': "Nhập Link Website (VD: https://web.com) (Bắt buộc): ",
        'ask_version': "Nhập Version App (Mặc định: 1.0.0): ",
        'ask_author': "Nhập Tác giả / Maintainer (Mặc định: Developer): ",
        'ask_desc': "Nhập Mô tả ứng dụng: ",
        'ask_min_os': "Nhập phiên bản iOS tối thiểu - Minimum OS (VD: 13.0): ",
        'html_change': "Bạn có muốn thay đổi trang HTML offline không?",
        'html_mode': "Chọn cách nhập HTML:\n  1. Cung cấp đường dẫn file (.html)\n  2. Nhập/Dán code HTML trực tiếp\nLựa chọn (1 hoặc 2): ",
        'html_path': "Nhập đường dẫn file HTML: ",
        'html_raw': "Hãy dán/gõ code HTML bên dưới. (Gõ chữ 'EOF' ở một dòng riêng biệt rồi ấn Enter để kết thúc):",
        'perm_header': "CẤU HÌNH QUYỀN TRUY CẬP (APPLE PERMISSIONS)",
        'ask_perm': "Bạn có muốn yêu cầu quyền truy cập {0} không?",
        'ask_reason': "  -> Nhập lý do (Sẽ hiển thị cho người dùng khi xin quyền): ",
        'build_deb': "Bạn có muốn build file DEB (Dành cho máy Jailbreak) không?",
        'build_ipa': "Bạn có muốn build file IPA (Dành cho Sideload/TrollStore) không?",
        'processing': "ĐANG DỌN DẸP & XỬ LÝ DỮ LIỆU BUILD...",
        'done': "HOÀN TẤT! Quá trình thành công.",
        'error': "LỖI: Xảy ra sự cố trong quá trình build.",
        'err_req': "Đây là trường bắt buộc. Vui lòng nhập dữ liệu!",
        'err_theos': "❌ LỖI: Chưa thiết lập biến môi trường THEOS!\nVui lòng chạy lệnh sau trên Terminal trước khi mở tool:\nexport THEOS=\"$HOME/theos\""
    },
    'en': {
        'header': "ADVANCED IOS WEB APP AUTOMATION BUILD TOOL",
        'ask_app_name': "Enter App Name (Required): ",
        'ask_bundle_id': "Enter Bundle ID (e.g., com.myname.myapp) (Required): ",
        'ask_url': "Enter Web URL (e.g., https://web.com) (Required): ",
        'ask_version': "Enter App Version (Default: 1.0.0): ",
        'ask_author': "Enter Author / Maintainer (Default: Developer): ",
        'ask_desc': "Enter App Description: ",
        'ask_min_os': "Enter Minimum OS Version (e.g., 13.0): ",
        'html_change': "Do you want to change the offline HTML page?",
        'html_mode': "Choose HTML input method:\n  1. Provide a file path (.html)\n  2. Type/Paste raw HTML code\nChoice (1 or 2): ",
        'html_path': "Enter HTML file path: ",
        'html_raw': "Paste/Type your HTML code below. (Type 'EOF' on a new line and press Enter to finish):",
        'perm_header': "APPLE PERMISSIONS CONFIGURATION",
        'ask_perm': "Do you want to request {0} permission?",
        'ask_reason': "  -> Enter usage description (Shown to user): ",
        'build_deb': "Do you want to build a DEB file (For Jailbroken devices)?",
        'build_ipa': "Do you want to build an IPA file (For Sideload/TrollStore)?",
        'processing': "CLEANING UP & PROCESSING BUILD DATA...",
        'done': "DONE! Build completed successfully.",
        'error': "ERROR: An issue occurred during the build process.",
        'err_req': "This is a required field. Please enter a value!",
        'err_theos': "❌ ERROR: THEOS environment variable is not set!\nPlease run the following command in Terminal before opening the tool:\nexport THEOS=\"$HOME/theos\""
    }
}

PERMISSIONS = {
    'Camera': ['NSCameraUsageDescription'],
    'Microphone': ['NSMicrophoneUsageDescription'],
    'Photo Library': ['NSPhotoLibraryUsageDescription', 'NSPhotoLibraryAddUsageDescription'],
    'Location (Vị trí)': ['NSLocationWhenInUseUsageDescription', 'NSLocationAlwaysUsageDescription'],
    'FaceID / TouchID': ['NSFaceIDUsageDescription'],
    'Bluetooth': ['NSBluetoothAlwaysUsageDescription', 'NSBluetoothPeripheralUsageDescription'],
    'Contacts (Danh bạ)': ['NSContactsUsageDescription'],
    'Calendar (Lịch)': ['NSCalendarsUsageDescription']
}

def print_banner(text):
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}{text.center(60)}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

def ask_input(prompt, t_err, mandatory=True, default=""):
    while True:
        data = input(f"{GREEN}{prompt}{RESET}").strip()
        if data:
            return data
        if not mandatory:
            return default
        print(f"{RED}⚠️ {t_err}{RESET}")

def ask_yes_no(prompt):
    while True:
        ans = input(f"{YELLOW}{prompt} (y/n): {RESET}").strip().lower()
        if ans in ['y', 'yes']:
            return True
        elif ans in ['n', 'no']:
            return False

def main():
    print(f"{BOLD}Select Language / Chọn ngôn ngữ:{RESET}\n1. Tiếng Việt\n2. English")
    lang_choice = input("Choice (1/2): ").strip()
    lang = 'en' if lang_choice == '2' else 'vi'
    t = TEXTS[lang]

    if not os.environ.get("THEOS"):
        print_banner(t['err_theos'])
        sys.exit(1)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print_banner(t['header'])

    app_name = ask_input(t['ask_app_name'], t['err_req'])
    app_name_nospace = "".join(e for e in app_name if e.isalnum())
    bundle_id = ask_input(t['ask_bundle_id'], t['err_req'])
    web_url = ask_input(t['ask_url'], t['err_req'])
    
    version = ask_input(t['ask_version'], "", mandatory=False, default="1.0.0")
    author = ask_input(t['ask_author'], "", mandatory=False, default="Developer")
    description = ask_input(t['ask_desc'], "", mandatory=False, default="A Web-based iOS Application")
    min_os = ask_input(t['ask_min_os'], "", mandatory=False, default="13.0")

    html_content = None
    if ask_yes_no(t['html_change']):
        mode = ask_input(t['html_mode'], t['err_req'])
        if mode == '1':
            path = ask_input(t['html_path'], t['err_req'])
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    html_content = f.read()
            else:
                print(f"{RED}⚠️ File not found! Keeping default.{RESET}" if lang == 'en' else f"{RED}⚠️ Không tìm thấy file! Giữ nguyên mặc định.{RESET}")
        else:
            print(f"\n{CYAN}{t['html_raw']}{RESET}")
            lines = []
            while True:
                line = input()
                if line.strip() == "EOF":
                    break
                lines.append(line)
            html_content = "\n".join(lines)

    print_banner(t['perm_header'])
    granted_perms = {}
    for perm_name, plist_keys in PERMISSIONS.items():
        if ask_yes_no(t['ask_perm'].format(perm_name)):
            reason = ask_input(t['ask_reason'], t['err_req'])
            for key in plist_keys:
                granted_perms[key] = reason

    print_banner("BUILD OPTIONS")
    build_deb = ask_yes_no(t['build_deb'])
    build_ipa = ask_yes_no(t['build_ipa'])

    print_banner(t['processing'])

    # 1. Update control
    if os.path.exists("control"):
        with open("control", "r", encoding="utf-8") as f:
            c_data = f.read()
        c_data = re.sub(r"Package:.*", f"Package: {bundle_id}", c_data)
        c_data = re.sub(r"Name:.*", f"Name: {app_name}", c_data)
        c_data = re.sub(r"Version:.*", f"Version: {version}", c_data)
        c_data = re.sub(r"Description:.*", f"Description: {description}", c_data)
        c_data = re.sub(r"Maintainer:.*", f"Maintainer: {author}", c_data)
        c_data = re.sub(r"Author:.*", f"Author: {author}", c_data)
        c_data = re.sub(r"Depends: firmware \(>= .*\)", f"Depends: firmware (>= {min_os})", c_data)
        with open("control", "w", encoding="utf-8") as f:
            f.write(c_data)

    # 2. Update Makefile
    if os.path.exists("Makefile"):
        with open("Makefile", "r", encoding="utf-8") as f:
            m_data = f.read()
        
        m_data = re.sub(r"TARGET\s*:=\s*iphone:clang:latest:.*", f"TARGET := iphone:clang:latest:{min_os}", m_data)
        m_data = re.sub(r"APPLICATION_NAME\s*=\s*.*", f"APPLICATION_NAME = {app_name_nospace}", m_data)
        m_data = re.sub(r"IPA_NAME\s*=\s*.*", f"IPA_NAME = {app_name_nospace}.ipa", m_data)
        
        m_data = re.sub(r"^[a-zA-Z0-9]+_FILES\s*=.*", f"{app_name_nospace}_FILES = main.m AppDelegate.m ViewController.m", m_data, flags=re.MULTILINE)
        m_data = re.sub(r"^[a-zA-Z0-9]+_FRAMEWORKS\s*=.*", f"{app_name_nospace}_FRAMEWORKS = UIKit WebKit AVFoundation Photos", m_data, flags=re.MULTILINE)
        m_data = re.sub(r"^[a-zA-Z0-9]+_CFLAGS\s*=.*", f"{app_name_nospace}_CFLAGS = -fobjc-arc -Wno-deprecated-declarations -Wno-error", m_data, flags=re.MULTILINE)
        m_data = re.sub(r"^[a-zA-Z0-9]+_BUNDLE_RESOURCES\s*=.*", f"{app_name_nospace}_BUNDLE_RESOURCES = Info.plist", m_data, flags=re.MULTILINE)
        m_data = re.sub(r"^[a-zA-Z0-9]+_BUNDLE_RESOURCE_DIRS\s*=.*", f"{app_name_nospace}_BUNDLE_RESOURCE_DIRS = Resources", m_data, flags=re.MULTILINE)
        m_data = re.sub(r"^[a-zA-Z0-9]+_INSTALL_PATH\s*=.*", f"{app_name_nospace}_INSTALL_PATH = /Applications", m_data, flags=re.MULTILINE)

        with open("Makefile", "w", encoding="utf-8") as f:
            f.write(m_data)

    # 3. Handle HTML & Clean up Resources Directory
    os.makedirs("Resources", exist_ok=True)
    if html_content is not None:
        with open("Resources/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    # 3.1: Dọn dẹp Icon thừa (Ưu tiên PNG nếu có cả 2)
    icon_png = os.path.join("Resources", "app_icon.png")
    icon_jpg = os.path.join("Resources", "app_icon.jpg")
    if os.path.exists(icon_png) and os.path.exists(icon_jpg):
        os.remove(icon_jpg)
        print(f"{YELLOW}⚠️  Detected both PNG and JPG icons. Removed 'app_icon.jpg' to optimize app size.{RESET}")

    # 3.2: Dọn dẹp file văn bản/hướng dẫn thừa trong thư mục Resources
    for f_name in os.listdir("Resources"):
        f_path = os.path.join("Resources", f_name)
        if os.path.isfile(f_path):
            name_lower = f_name.lower()
            # Xóa các file .txt, .md, hoặc file chứa chuỗi hướng dẫn cụ thể
            if name_lower.endswith(('.txt', '.md', '.rtf')) or "choose one" in name_lower or "png and jpg" in name_lower:
                os.remove(f_path)
                print(f"{YELLOW}🗑️  Removed unnecessary extra file: {f_name}{RESET}")

    # 4. Update Info.plist
    if os.path.exists("Info.plist"):
        with open("Info.plist", "rb") as f:
            p_dict = plistlib.load(f)
        
        p_dict["CFBundleDisplayName"] = app_name
        p_dict["CFBundleName"] = app_name_nospace
        p_dict["CFBundleExecutable"] = app_name_nospace
        p_dict["CFBundleIdentifier"] = bundle_id
        p_dict["CFBundleShortVersionString"] = version
        p_dict["CFBundleVersion"] = version
        p_dict["MinimumOSVersion"] = min_os
        
        domain = web_url.replace("https://", "").replace("http://", "").split("/")[0]
        p_dict["WKAppBoundDomains"] = [domain]

        # 4.1: Xác định đúng định dạng Icon để gán vào Plist
        icon_files = []
        if os.path.exists(icon_png):
            icon_files.append("app_icon.png")
        elif os.path.exists(icon_jpg):
            icon_files.append("app_icon.jpg")
        else:
            # Fallback nếu vô tình xóa hết icon
            icon_files = ["app_icon.png"]
        p_dict["CFBundleIconFiles"] = icon_files

        for perm_list in PERMISSIONS.values():
            for k in perm_list:
                p_dict.pop(k, None)
                
        for k, v in granted_perms.items():
            p_dict[k] = v

        with open("Info.plist", "wb") as f:
            plistlib.dump(p_dict, f)

    # 5. Update ViewController.m
    if os.path.exists("ViewController.m"):
        with open("ViewController.m", "r", encoding="utf-8") as f:
            vc_data = f.read()
        vc_data = re.sub(
            r'static NSString \* const kStartURL = @".*";', 
            f'static NSString * const kStartURL = @"{web_url}";', 
            vc_data
        )
        with open("ViewController.m", "w", encoding="utf-8") as f:
            f.write(vc_data)

    if not os.path.exists("Makefile"):
        print_banner(f"{RED}❌ ERROR: 'Makefile' not found!{RESET}")
        sys.exit(1)

    # 6. Execute Build
    try:
        subprocess.run(["make", "clean"], check=True)
        if build_deb:
            subprocess.run(["make", "package"], check=True)
        if build_ipa:
            subprocess.run(["make", "ipa"], check=True)
        print_banner(f"{GREEN}{t['done']}{RESET}")
    except subprocess.CalledProcessError:
        print_banner(f"{RED}{t['error']}{RESET}")

if __name__ == "__main__":
    main()
