import os
import sys
import re
import plistlib
import shutil
import subprocess

TEXTS = {
    'vi': {
        'header': "CÔNG CỤ TỰ ĐỘNG BUILD IOS WEB APP",
        'ask_app_name': "Nhập tên App (Bắt buộc): ",
        'ask_bundle_id': "Nhập Bundle ID (VD: com.myname.myapp) (Bắt buộc): ",
        'ask_url': "Nhập Link Website (VD: https://web.com) (Bắt buộc): ",
        'html_change': "Bạn có muốn thay đổi trang HTML offline không?",
        'html_mode': "Chọn cách nhập HTML:\n  1. Cung cấp đường dẫn file (.html)\n  2. Nhập/Dán code HTML trực tiếp\nLựa chọn (1 hoặc 2): ",
        'html_path': "Nhập đường dẫn file HTML: ",
        'html_raw': "Hãy dán/gõ code HTML bên dưới. (Gõ chữ 'EOF' ở một dòng riêng biệt rồi ấn Enter để kết thúc):",
        'perm_header': "CẤU HÌNH QUYỀN TRUY CẬP (APPLE PERMISSIONS)",
        'ask_perm': "Bạn có muốn yêu cầu quyền truy cập {0} không?",
        'ask_reason': "  -> Nhập lý do (Sẽ hiển thị cho người dùng khi xin quyền): ",
        'build_deb': "Bạn có muốn build file DEB (Dành cho máy Jailbreak) không?",
        'build_ipa': "Bạn có muốn build file IPA (Dành cho Sideload/TrollStore) không?",
        'processing': "ĐANG XỬ LÝ DỮ LIỆU & BUILD...",
        'done': "HOÀN TẤT! Quá trình thành công.",
        'error': "LỖI: Xảy ra sự cố trong quá trình build.",
        'err_req': "Đây là trường bắt buộc. Vui lòng nhập dữ liệu!",
        'err_theos': "❌ LỖI: Chưa thiết lập biến môi trường THEOS!\nVui lòng chạy lệnh sau trên Terminal trước khi mở tool:\nexport THEOS=\"$HOME/theos\""
    },
    'en': {
        'header': "IOS WEB APP AUTOMATION BUILD TOOL",
        'ask_app_name': "Enter App Name (Required): ",
        'ask_bundle_id': "Enter Bundle ID (e.g., com.myname.myapp) (Required): ",
        'ask_url': "Enter Web URL (e.g., https://web.com) (Required): ",
        'html_change': "Do you want to change the offline HTML page?",
        'html_mode': "Choose HTML input method:\n  1. Provide a file path (.html)\n  2. Type/Paste raw HTML code\nChoice (1 or 2): ",
        'html_path': "Enter HTML file path: ",
        'html_raw': "Paste/Type your HTML code below. (Type 'EOF' on a new line and press Enter to finish):",
        'perm_header': "APPLE PERMISSIONS CONFIGURATION",
        'ask_perm': "Do you want to request {0} permission?",
        'ask_reason': "  -> Enter usage description (Shown to user): ",
        'build_deb': "Do you want to build a DEB file (For Jailbroken devices)?",
        'build_ipa': "Do you want to build an IPA file (For Sideload/TrollStore)?",
        'processing': "PROCESSING & BUILDING...",
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
    print(f"\n{'='*50}\n{text.center(50)}\n{'='*50}\n")

def ask_input(prompt, t_err, mandatory=True):
    while True:
        data = input(prompt).strip()
        if data:
            return data
        if not mandatory:
            return ""
        print(f"⚠️ {t_err}")

def ask_yes_no(prompt):
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ['y', 'yes']:
            return True
        elif ans in ['n', 'no']:
            return False

def main():
    print("Select Language / Chọn ngôn ngữ:\n1. Tiếng Việt\n2. English")
    lang_choice = input("Choice (1/2): ").strip()
    lang = 'en' if lang_choice == '2' else 'vi'
    t = TEXTS[lang]

    # Kiểm tra biến THEOS trước khi làm bất cứ điều gì
    if not os.environ.get("THEOS"):
        print_banner(t['err_theos'])
        sys.exit(1)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print_banner(t['header'])

    app_name = ask_input(t['ask_app_name'], t['err_req'])
    app_name_nospace = "".join(e for e in app_name if e.isalnum())
    bundle_id = ask_input(t['ask_bundle_id'], t['err_req'])
    web_url = ask_input(t['ask_url'], t['err_req'])

    html_content = None
    if ask_yes_no(t['html_change']):
        mode = ask_input(t['html_mode'], t['err_req'])
        if mode == '1':
            path = ask_input(t['html_path'], t['err_req'])
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    html_content = f.read()
            else:
                print("⚠️ File not found! Keeping default." if lang == 'en' else "⚠️ Không tìm thấy file! Giữ nguyên mặc định.")
        else:
            print(f"\n{t['html_raw']}")
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

    if os.path.exists("control"):
        with open("control", "r", encoding="utf-8") as f:
            c_data = f.read()
        c_data = re.sub(r"Package: .*", f"Package: {bundle_id}", c_data)
        c_data = re.sub(r"Name: .*", f"Name: {app_name}", c_data)
        with open("control", "w", encoding="utf-8") as f:
            f.write(c_data)

    if os.path.exists("Makefile"):
        with open("Makefile", "r", encoding="utf-8") as f:
            m_data = f.read()
        m_data = re.sub(r"APPLICATION_NAME\s*=\s*.*", f"APPLICATION_NAME = {app_name_nospace}", m_data)
        with open("Makefile", "w", encoding="utf-8") as f:
            f.write(m_data)

    if os.path.exists("Info.plist"):
        with open("Info.plist", "rb") as f:
            p_dict = plistlib.load(f)
        
        p_dict["CFBundleDisplayName"] = app_name
        p_dict["CFBundleName"] = app_name_nospace
        p_dict["CFBundleExecutable"] = app_name_nospace
        p_dict["CFBundleIdentifier"] = bundle_id
        
        domain = web_url.replace("https://", "").replace("http://", "").split("/")[0]
        p_dict["WKAppBoundDomains"] = [domain]

        for perm_list in PERMISSIONS.values():
            for k in perm_list:
                p_dict.pop(k, None)
                
        for k, v in granted_perms.items():
            p_dict[k] = v

        with open("Info.plist", "wb") as f:
            plistlib.dump(p_dict, f)

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

    if html_content is not None:
        os.makedirs("Resources", exist_ok=True)
        with open("Resources/index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    try:
        subprocess.run(["make", "clean"], check=True)
        if build_deb:
            subprocess.run(["make", "package"], check=True)
        if build_ipa:
            subprocess.run(["make", "ipa"], check=True)
        print_banner(t['done'])
    except subprocess.CalledProcessError:
        print_banner(t['error'])

if __name__ == "__main__":
    main()
