import os
import sys
import re
import plistlib
import shutil
import subprocess

# ANSI Color Codes
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

TEXTS = {
    'vi': {
        'header': "CÔNG CỤ TỰ ĐỘNG BUILD IOS WEB APP NÂNG CAO (ULTIMATE)",
        'ask_app_name': "Nhập tên App (Bắt buộc): ",
        'ask_bundle_id': "Nhập Bundle ID (VD: com.myname.myapp) (Bắt buộc): ",
        'ask_url': "Nhập Link Website (VD: https://web.com) (Bắt buộc): ",
        'ask_version': "Nhập Version App (Mặc định: 1.0.0): ",
        'ask_author': "Nhập Tác giả / Maintainer (Mặc định: Developer): ",
        'ask_desc': "Nhập Mô tả ứng dụng: ",
        'ask_min_os': "Nhập phiên bản iOS tối thiểu - Minimum OS (VD: 14.0): ",
        'html_change': "Bạn có muốn thay đổi trang HTML offline không?",
        'html_mode': "Chọn cách nhập HTML:\n  1. Cung cấp đường dẫn file (.html)\n  2. Nhập/Dán code HTML trực tiếp\nLựa chọn (1 hoặc 2): ",
        'html_path': "Nhập đường dẫn file HTML: ",
        'html_raw': "Hãy dán/gõ code HTML bên dưới. (Gõ chữ 'EOF' ở một dòng riêng biệt rồi ấn Enter để kết thúc):",
        'ask_exit': "Bạn có muốn bật tính năng Thoát ứng dụng (app://exit) không?",
        'perm_header': "CẤU HÌNH QUYỀN TRUY CẬP (APPLE PERMISSIONS)",
        'ask_perm': "Bạn có muốn yêu cầu quyền truy cập {0} không?",
        'ask_reason': "  -> Nhập lý do (Sẽ hiển thị cho người dùng khi xin quyền): ",
        'restricted_warn': "⚠️ CẢNH BÁO: Quyền này BẮT BUỘC phải có tệp chứng chỉ '.entitlements' và tài khoản Apple Developer trả phí (99$/năm). Nếu cố tình build vào thiết bị thường hoặc không có chứng chỉ, App sẽ bị Crash ngay khi mở!",
        'ask_proceed': "  -> Bạn vẫn muốn tiếp tục thêm quyền này chứ?",
        'build_deb': "Bạn có muốn build file DEB (Dành cho máy Jailbreak) không?",
        'build_ipa': "Bạn có muốn build file IPA (Dành cho Sideload/TrollStore) không?",
        'processing': "ĐANG TIÊM MÃ NATIVE & XỬ LÝ BUILD...",
        'restoring': "ĐANG KHÔI PHỤC MÃ NGUỒN VỀ TRẠNG THÁI GỐC ĐẢM BẢO 100%...",
        'done': "HOÀN TẤT! Quá trình thành công.",
        'error': "LỖI: Xảy ra sự cố trong quá trình build.",
        'err_req': "Đây là trường bắt buộc. Vui lòng nhập dữ liệu!",
        'err_theos': "❌ LỖI: Chưa thiết lập biến môi trường THEOS!\nVui lòng chạy lệnh: export THEOS=\"$HOME/theos\""
    },
    'en': {
        'header': "ADVANCED IOS WEB APP AUTOMATION BUILD TOOL (ULTIMATE)",
        'ask_app_name': "Enter App Name (Required): ",
        'ask_bundle_id': "Enter Bundle ID (e.g., com.myname.myapp) (Required): ",
        'ask_url': "Enter Web URL (e.g., https://web.com) (Required): ",
        'ask_version': "Enter App Version (Default: 1.0.0): ",
        'ask_author': "Enter Author / Maintainer (Default: Developer): ",
        'ask_desc': "Enter App Description: ",
        'ask_min_os': "Enter Minimum OS Version (e.g., 14.0): ",
        'html_change': "Do you want to change the offline HTML page?",
        'html_mode': "Choose HTML input method:\n  1. Provide a file path (.html)\n  2. Type/Paste raw HTML code\nChoice (1 or 2): ",
        'html_path': "Enter HTML file path: ",
        'html_raw': "Paste/Type your HTML code below. (Type 'EOF' on a new line and press Enter to finish):",
        'ask_exit': "Do you want to enable the Exit App feature (app://exit)?",
        'perm_header': "APPLE PERMISSIONS CONFIGURATION",
        'ask_perm': "Do you want to request {0} permission?",
        'ask_reason': "  -> Enter usage description (Shown to user): ",
        'restricted_warn': "⚠️ WARNING: This permission REQUIRES an '.entitlements' file and a paid Apple Developer account ($99/year). Building this without entitlements will result in an immediate App Crash!",
        'ask_proceed': "  -> Do you still want to proceed and inject this permission?",
        'build_deb': "Do you want to build a DEB file (For Jailbroken devices)?",
        'build_ipa': "Do you want to build an IPA file (For Sideload/TrollStore)?",
        'processing': "INJECTING NATIVE CODE & PROCESSING BUILD...",
        'restoring': "RESTORING 100% ORIGINAL SOURCE CODE...",
        'done': "DONE! Build completed successfully.",
        'error': "ERROR: An issue occurred during the build process.",
        'err_req': "This is a required field. Please enter a value!",
        'err_theos': "❌ ERROR: THEOS environment variable is not set!\nPlease run: export THEOS=\"$HOME/theos\""
    }
}

# TỪ ĐIỂN QUYỀN HẠN ĐẦY ĐỦ CỦA APPLE
PERM_DATA = {
    # === NHÓM QUYỀN CƠ BẢN VÀ THÔNG DỤNG ===
    'Camera': {
        'plist': ['NSCameraUsageDescription'],
        'frameworks': ['AVFoundation'],
        'imports': ['<AVFoundation/AVFoundation.h>'],
        'code': 'if ([AVCaptureDevice authorizationStatusForMediaType:AVMediaTypeVideo] == AVAuthorizationStatusNotDetermined) {\n        [AVCaptureDevice requestAccessForMediaType:AVMediaTypeVideo completionHandler:^(BOOL granted) {}];\n    }'
    },
    'Microphone': {
        'plist': ['NSMicrophoneUsageDescription'],
        'frameworks': ['AVFoundation'],
        'imports': ['<AVFoundation/AVFoundation.h>'],
        'code': 'AVAudioSession *audioSession = [AVAudioSession sharedInstance];\n    NSError *audioError = nil;\n    [audioSession setCategory:AVAudioSessionCategoryPlayAndRecord withOptions:AVAudioSessionCategoryOptionDefaultToSpeaker error:&audioError];\n    [audioSession setActive:YES error:&audioError];\n    if (audioSession.recordPermission == AVAudioSessionRecordPermissionUndetermined) {\n        [audioSession requestRecordPermission:^(BOOL granted) {}];\n    }'
    },
    'Photo Library': {
        'plist': ['NSPhotoLibraryUsageDescription', 'NSPhotoLibraryAddUsageDescription'],
        'frameworks': ['Photos'],
        'imports': ['<Photos/Photos.h>'],
        'code': 'if ([PHPhotoLibrary authorizationStatus] == PHAuthorizationStatusNotDetermined) {\n        [PHPhotoLibrary requestAuthorization:^(PHAuthorizationStatus status) {}];\n    }'
    },
    'Location (Vị trí)': {
        'plist': ['NSLocationWhenInUseUsageDescription', 'NSLocationAlwaysUsageDescription'],
        'frameworks': ['CoreLocation'],
        'imports': ['<CoreLocation/CoreLocation.h>'],
        'interface': '@property (nonatomic, strong) CLLocationManager *locManager;',
        'code': 'self.locManager = [[CLLocationManager alloc] init];\n    [self.locManager requestWhenInUseAuthorization];'
    },
    'FaceID / TouchID / Passwords': {
        'plist': ['NSFaceIDUsageDescription'],
        'frameworks': ['LocalAuthentication'],
        'imports': ['<LocalAuthentication/LocalAuthentication.h>'],
        'code': 'LAContext *context = [[LAContext alloc] init];\n    NSError *authError = nil;\n    [context canEvaluatePolicy:LAPolicyDeviceOwnerAuthenticationWithBiometrics error:&authError];'
    },
    'App Tracking (Theo dõi - Analytics/Ads)': {
        'plist': ['NSUserTrackingUsageDescription'],
        'frameworks': ['AppTrackingTransparency'],
        'imports': ['<AppTrackingTransparency/AppTrackingTransparency.h>'],
        'code': 'if (@available(iOS 14, *)) {\n        [ATTrackingManager requestTrackingAuthorizationWithCompletionHandler:^(ATTrackingManagerAuthorizationStatus status) {}];\n    }'
    },
    'Notifications (Thông báo Push/Local)': {
        'plist': [], 
        'frameworks': ['UserNotifications'],
        'imports': ['<UserNotifications/UserNotifications.h>'],
        'code': '[[UNUserNotificationCenter currentNotificationCenter] requestAuthorizationWithOptions:(UNAuthorizationOptionAlert | UNAuthorizationOptionSound | UNAuthorizationOptionBadge) completionHandler:^(BOOL granted, NSError * _Nullable error) {}];'
    },
    'Reminders (Lời nhắc)': {
        'plist': ['NSRemindersUsageDescription'],
        'frameworks': ['EventKit'],
        'imports': ['<EventKit/EventKit.h>'],
        'code': 'EKEventStore *reminderStore = [[EKEventStore alloc] init];\n    [reminderStore requestAccessToEntityType:EKEntityTypeReminder completion:^(BOOL granted, NSError * _Nullable error) {}];'
    },
    'Local Network (Mạng nội bộ)': {
        'plist': ['NSLocalNetworkUsageDescription'],
        'frameworks': [],
        'imports': [],
        'code': ''
    },
    'Speech Recognition (Nhận diện giọng nói)': {
        'plist': ['NSSpeechRecognitionUsageDescription'],
        'frameworks': ['Speech'],
        'imports': ['<Speech/Speech.h>'],
        'code': '[SFSpeechRecognizer requestAuthorization:^(SFSpeechRecognizerAuthorizationStatus status) {}];'
    },
    'Motion & Fitness (Chuyển động & Thể chất)': {
        'plist': ['NSMotionUsageDescription'],
        'frameworks': ['CoreMotion'],
        'imports': ['<CoreMotion/CoreMotion.h>'],
        'interface': '@property (nonatomic, strong) CMMotionActivityManager *motionManager;',
        'code': 'self.motionManager = [[CMMotionActivityManager alloc] init];\n    [self.motionManager queryActivityStartingFromDate:[NSDate date] toDate:[NSDate date] toQueue:[NSOperationQueue mainQueue] withHandler:^(NSArray<CMMotionActivity *> * _Nullable activities, NSError * _Nullable error) {}];'
    },
    'Apple Music (Thư viện nhạc)': {
        'plist': ['NSAppleMusicUsageDescription'],
        'frameworks': ['MediaPlayer'],
        'imports': ['<MediaPlayer/MediaPlayer.h>'],
        'code': '[MPMediaLibrary requestAuthorization:^(MPMediaLibraryAuthorizationStatus status) {}];'
    },
    'Bluetooth': {
        'plist': ['NSBluetoothAlwaysUsageDescription', 'NSBluetoothPeripheralUsageDescription'],
        'frameworks': ['CoreBluetooth'],
        'imports': ['<CoreBluetooth/CoreBluetooth.h>'],
        'interface': '@property (nonatomic, strong) CBCentralManager *btManager;',
        'code': 'self.btManager = [[CBCentralManager alloc] initWithDelegate:nil queue:nil];'
    },
    'Contacts (Danh bạ)': {
        'plist': ['NSContactsUsageDescription'],
        'frameworks': ['Contacts'],
        'imports': ['<Contacts/Contacts.h>'],
        'code': 'CNContactStore *contactStore = [[CNContactStore alloc] init];\n    [contactStore requestAccessForEntityType:CNEntityTypeContacts completionHandler:^(BOOL granted, NSError * _Nullable error) {}];'
    },
    'Calendar (Lịch)': {
        'plist': ['NSCalendarsUsageDescription'],
        'frameworks': ['EventKit'],
        'imports': ['<EventKit/EventKit.h>'],
        'code': 'EKEventStore *eventStore = [[EKEventStore alloc] init];\n    [eventStore requestAccessToEntityType:EKEntityTypeEvent completion:^(BOOL granted, NSError * _Nullable error) {}];'
    },

    # === NHÓM QUYỀN ĐẶC QUYỀN (RESTRICTED) ===
    'HealthKit (Dữ liệu Sức khỏe)': {
        'plist': ['NSHealthShareUsageDescription', 'NSHealthUpdateUsageDescription'],
        'frameworks': ['HealthKit'],
        'imports': ['<HealthKit/HealthKit.h>'],
        'restricted': True,
        'code': 'if ([HKHealthStore isHealthDataAvailable]) {\n        HKHealthStore *healthStore = [[HKHealthStore alloc] init];\n    }'
    },
    'HomeKit (Nhà thông minh)': {
        'plist': ['NSHomeKitUsageDescription'],
        'frameworks': ['HomeKit'],
        'imports': ['<HomeKit/HomeKit.h>'],
        'restricted': True,
        'interface': '@property (nonatomic, strong) HMHomeManager *homeManager;',
        'code': 'self.homeManager = [[HMHomeManager alloc] init];'
    },
    'Siri (Trợ lý ảo)': {
        'plist': ['NSSiriUsageDescription'],
        'frameworks': ['Intents'],
        'imports': ['<Intents/Intents.h>'],
        'restricted': True,
        'code': '[INPreferences requestSiriAuthorization:^(INSiriAuthorizationStatus status) {}];'
    },
    'Apple Pay (Thanh toán gốc)': {
        'plist': [],
        'frameworks': ['PassKit'],
        'imports': ['<PassKit/PassKit.h>'],
        'restricted': True,
        'code': ''
    },
    'VPN & Network Extension': {
        'plist': [],
        'frameworks': ['NetworkExtension'],
        'imports': ['<NetworkExtension/NetworkExtension.h>'],
        'restricted': True,
        'code': ''
    }
}

# Độ ưu tiên của định dạng ảnh App Icon
ICON_EXT_PRIORITY = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']

def print_banner(text):
    print(f"\n{CYAN}{'='*60}{RESET}\n{BOLD}{CYAN}{text.center(60)}{RESET}\n{CYAN}{'='*60}{RESET}\n")

def ask_input(prompt, t_err, mandatory=True, default=""):
    while True:
        data = input(f"{GREEN}{prompt}{RESET}").strip()
        if data: return data
        if not mandatory: return default
        print(f"{RED}⚠️ {t_err}{RESET}")

def ask_yes_no(prompt):
    while True:
        ans = input(f"{YELLOW}{prompt} (y/n): {RESET}").strip().lower()
        if ans in ['y', 'yes']: return True
        elif ans in ['n', 'no']: return False

def backup_original_files():
    """Sao lưu 100% các file gốc và TOÀN BỘ thư mục Resources vào bộ nhớ (RAM)."""
    backups = {}
    files_to_backup = ["control", "Makefile", "Info.plist", "ViewController.m"]
    
    if os.path.exists("Resources"):
        for root, dirs, files in os.walk("Resources"):
            for file in files:
                files_to_backup.append(os.path.join(root, file))
                
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                backups[file_path] = f.read()
    return backups

def restore_original_files(backups, t_msg):
    """Khôi phục lại toàn bộ file gốc từ RAM, tiêu diệt hoàn toàn file rác sinh ra trong lúc build."""
    print_banner(t_msg)
    
    if os.path.exists("Resources"):
        shutil.rmtree("Resources")
        
    for file_path, content in backups.items():
        if os.path.dirname(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
    print(f"{GREEN}✅ Đã khôi phục hoàn tất 100% mã nguồn gốc.{RESET}")

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

    # --- BƯỚC QUAN TRỌNG: BACKUP TỔNG THỂ TRƯỚC KHI HỎI BẤT KỲ THỨ GÌ ---
    original_backups = backup_original_files()

    app_name = ask_input(t['ask_app_name'], t['err_req'])
    app_name_nospace = "".join(e for e in app_name if e.isalnum())
    bundle_id = ask_input(t['ask_bundle_id'], t['err_req'])
    web_url = ask_input(t['ask_url'], t['err_req'])
    version = ask_input(t['ask_version'], "", mandatory=False, default="1.0.0")
    author = ask_input(t['ask_author'], "", mandatory=False, default="Developer")
    description = ask_input(t['ask_desc'], "", mandatory=False, default="A Web-based iOS Application")
    min_os = ask_input(t['ask_min_os'], "", mandatory=False, default="14.0")

    domain = web_url.replace("https://", "").replace("http://", "").split("/")[0]

    html_content = None
    if ask_yes_no(t['html_change']):
        mode = ask_input(t['html_mode'], t['err_req'])
        if mode == '1':
            path = ask_input(t['html_path'], t['err_req'])
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f: html_content = f.read()
            else:
                print(f"{RED}⚠️ File not found! Keeping default.{RESET}" if lang == 'en' else f"{RED}⚠️ Không tìm thấy file! Giữ nguyên mặc định.{RESET}")
        else:
            print(f"\n{CYAN}{t['html_raw']}{RESET}")
            lines = []
            while True:
                line = input()
                if line.strip() == "EOF": break
                lines.append(line)
            html_content = "\n".join(lines)

    print()
    enable_exit = ask_yes_no(t['ask_exit'])

    print_banner(t['perm_header'])
    granted_perms = {}
    needed_frameworks = set()
    needed_imports = set()
    needed_interfaces = set()
    needed_codes = []

    for perm_name, data in PERM_DATA.items():
        if ask_yes_no(t['ask_perm'].format(perm_name)):
            # Cảnh báo thông minh nếu là quyền Restricted
            if data.get('restricted'):
                print(f"\n{RED}{BOLD}{t['restricted_warn']}{RESET}")
                if not ask_yes_no(t['ask_proceed']):
                    continue # Bỏ qua quyền này nếu người dùng chọn 'No'
            
            # Nếu có yêu cầu description plist
            if data.get('plist'):
                reason = ask_input(t['ask_reason'], t['err_req'])
                for key in data['plist']: granted_perms[key] = reason
                
            needed_frameworks.update(data.get('frameworks', []))
            needed_imports.update(data.get('imports', []))
            if 'interface' in data: needed_interfaces.add(data['interface'])
            if data.get('code'): needed_codes.append(data['code'])

    print_banner("BUILD OPTIONS")
    build_deb = ask_yes_no(t['build_deb'])
    build_ipa = ask_yes_no(t['build_ipa'])
    print_banner(t['processing'])

    try:
        # 1. Update control
        if os.path.exists("control"):
            with open("control", "r", encoding="utf-8") as f: c_data = f.read()
            c_data = re.sub(r"Package:.*", f"Package: {bundle_id}", c_data)
            c_data = re.sub(r"Name:.*", f"Name: {app_name}", c_data)
            c_data = re.sub(r"Version:.*", f"Version: {version}", c_data)
            c_data = re.sub(r"Description:.*", f"Description: {description}", c_data)
            c_data = re.sub(r"Maintainer:.*", f"Maintainer: {author}", c_data)
            c_data = re.sub(r"Author:.*", f"Author: {author}", c_data)
            c_data = re.sub(r"Depends: firmware \(>= .*\)", f"Depends: firmware (>= {min_os})", c_data)
            with open("control", "w", encoding="utf-8") as f: f.write(c_data)

        # 2. Update Makefile
        if os.path.exists("Makefile"):
            with open("Makefile", "r", encoding="utf-8") as f: m_data = f.read()
            
            if re.search(r"^TARGET\s*[:]?=", m_data, flags=re.MULTILINE):
                m_data = re.sub(r"^TARGET\s*[:]?=.*", f"TARGET = iphone:clang:latest:{min_os}", m_data, flags=re.MULTILINE)
            else:
                m_data = f"TARGET = iphone:clang:latest:{min_os}\n" + m_data

            m_data = re.sub(r"APPLICATION_NAME\s*=\s*.*", f"APPLICATION_NAME = {app_name_nospace}", m_data)
            m_data = re.sub(r"IPA_NAME\s*=\s*.*", f"IPA_NAME = {app_name_nospace}.ipa", m_data)
            
            frameworks_str = "UIKit WebKit " + " ".join(needed_frameworks)
            
            m_data = re.sub(r"^[a-zA-Z0-9]+_FILES\s*=.*", f"{app_name_nospace}_FILES = main.m AppDelegate.m ViewController.m", m_data, flags=re.MULTILINE)
            m_data = re.sub(r"^[a-zA-Z0-9]+_FRAMEWORKS\s*=.*", f"{app_name_nospace}_FRAMEWORKS = {frameworks_str}", m_data, flags=re.MULTILINE)
            m_data = re.sub(r"^[a-zA-Z0-9]+_CFLAGS\s*=.*", f"{app_name_nospace}_CFLAGS = -fobjc-arc -Wno-deprecated-declarations -Wno-error", m_data, flags=re.MULTILINE)
            m_data = re.sub(r"^[a-zA-Z0-9]+_BUNDLE_RESOURCES\s*=.*", f"{app_name_nospace}_BUNDLE_RESOURCES = Info.plist", m_data, flags=re.MULTILINE)
            m_data = re.sub(r"^[a-zA-Z0-9]+_BUNDLE_RESOURCE_DIRS\s*=.*", f"{app_name_nospace}_BUNDLE_RESOURCE_DIRS = Resources", m_data, flags=re.MULTILINE)
            m_data = re.sub(r"^[a-zA-Z0-9]+_INSTALL_PATH\s*=.*", f"{app_name_nospace}_INSTALL_PATH = /Applications", m_data, flags=re.MULTILINE)

            with open("Makefile", "w", encoding="utf-8") as f: f.write(m_data)

        # 3. Handle HTML, Smart Icon & Clean up Resources
        os.makedirs("Resources", exist_ok=True)
        if html_content is not None:
            with open("Resources/index.html", "w", encoding="utf-8") as f: f.write(html_content)

        found_icons = []
        for f_name in os.listdir("Resources"):
            f_path = os.path.join("Resources", f_name)
            if os.path.isfile(f_path):
                name_lower = f_name.lower()
                
                # Dọn dẹp rác hệ điều hành
                if ":zone.identifier" in name_lower or name_lower == ".ds_store" or re.search(r"\(\d+\)\.(png|jpg|jpeg|webp|bmp|gif)", name_lower):
                    os.remove(f_path)
                    continue
                    
                # Dọn dẹp file text thừa
                if name_lower.endswith(('.txt', '.md', '.rtf')) or "choose one" in name_lower or "png and jpg" in name_lower:
                    os.remove(f_path)
                    continue

                # Thu thập các file icon hợp lệ
                if name_lower.startswith("app_icon"):
                    ext = os.path.splitext(name_lower)[1]
                    if ext in ICON_EXT_PRIORITY:
                        found_icons.append(f_name)

        # Bộ lọc ưu tiên định dạng ảnh thông minh
        final_icon_name = "app_icon.png"
        if found_icons:
            found_icons.sort(key=lambda x: ICON_EXT_PRIORITY.index(os.path.splitext(x.lower())[1]))
            final_icon_name = found_icons[0] # Lấy file có độ ưu tiên cao nhất
            
            # Xóa sạch các icon có độ ưu tiên thấp hơn (tránh nặng app)
            for duplicate_icon in found_icons[1:]:
                os.remove(os.path.join("Resources", duplicate_icon))
                print(f"{YELLOW}⚠️  Removed lower priority icon: {duplicate_icon}{RESET}")

        # 4. Update Info.plist
        if os.path.exists("Info.plist"):
            with open("Info.plist", "rb") as f: p_dict = plistlib.load(f)
            
            p_dict["CFBundleDisplayName"] = app_name
            p_dict["CFBundleName"] = app_name_nospace
            p_dict["CFBundleExecutable"] = app_name_nospace
            p_dict["CFBundleIdentifier"] = bundle_id
            p_dict["CFBundleShortVersionString"] = version
            p_dict["CFBundleVersion"] = version
            p_dict["MinimumOSVersion"] = min_os
            p_dict["WKAppBoundDomains"] = [domain]
            p_dict["CFBundleIconFiles"] = [final_icon_name] 

            for perm_list in PERM_DATA.values():
                if perm_list.get('plist'):
                    for k in perm_list['plist']: p_dict.pop(k, None)
            for k, v in granted_perms.items(): p_dict[k] = v

            with open("Info.plist", "wb") as f: plistlib.dump(p_dict, f)

        # 5. Inject Objective-C Code (KHÔNG SỬA UI)
        if os.path.exists("ViewController.m"):
            with open("ViewController.m", "r", encoding="utf-8") as f: vc_data = f.read()
                
            vc_data = re.sub(r'static NSString \* const kStartURL = @".*";', f'static NSString * const kStartURL = @"{web_url}";', vc_data)
            vc_data = re.sub(r'\[origin\.host caseInsensitiveCompare:@".*?"\]', f'[origin.host caseInsensitiveCompare:@"{domain}"]', vc_data)

            # 5.0 Auto-translate Native Alerts
            if lang == 'en':
                vc_data = re.sub(r'actionWithTitle:@"Hủy"', 'actionWithTitle:@"Cancel"', vc_data)
                vc_data = re.sub(r'actionWithTitle:@"(chấp nhận|Chấp Nhận)"', 'actionWithTitle:@"Accept"', vc_data)
                vc_data = re.sub(
                    r"<h2>Không thể tải nội dung</h2><p>Hãy kiểm tra kết nối mạng và thử lại.</p>", 
                    "<h2>Content Unavailable</h2><p>Please check your internet connection and try again.</p>", 
                    vc_data
                )
            else:
                vc_data = re.sub(r'actionWithTitle:@"Cancel"', 'actionWithTitle:@"Hủy"', vc_data)
                vc_data = re.sub(r'actionWithTitle:@"Accept"', 'actionWithTitle:@"Chấp Nhận"', vc_data)
                vc_data = re.sub(r'actionWithTitle:@"chấp nhận"', 'actionWithTitle:@"Chấp Nhận"', vc_data)
                vc_data = re.sub(
                    r"<h2>Content Unavailable</h2><p>Please check your internet connection and try again.</p>", 
                    "<h2>Không thể tải nội dung</h2><p>Hãy kiểm tra kết nối mạng và thử lại.</p>", 
                    vc_data
                )

            # 5.1 Auto-remove legacy permissions code
            vc_data = re.sub(r'\s*\[self requestMediaPermissionsIfNeeded\];', '', vc_data)
            vc_data = re.sub(r'- \(void\)requestMediaPermissionsIfNeeded\s*\{.*?\n\}\n*(?=-|\@end)', '', vc_data, flags=re.DOTALL)
            vc_data = re.sub(r'#pragma mark - Intercept Custom URLs \(Exit App\).*?decisionHandler\(WKNavigationActionPolicyAllow\);\s*\}\s*', '', vc_data, flags=re.DOTALL)

            # 5.2 Handle Imports
            import_block = "// --- AUTO_INJECT_IMPORTS_START ---\n" + "\n".join([f"#import {i}" for i in needed_imports]) + "\n// --- AUTO_INJECT_IMPORTS_END ---\n"
            if "// --- AUTO_INJECT_IMPORTS_START ---" in vc_data:
                vc_data = re.sub(r"// --- AUTO_INJECT_IMPORTS_START ---.*?// --- AUTO_INJECT_IMPORTS_END ---\n?", import_block if needed_imports else "", vc_data, flags=re.DOTALL)
            elif needed_imports:
                vc_data = re.sub(r'(#import "ViewController\.h"|#import <UIKit/UIKit\.h>)', r'\1\n' + import_block, vc_data, count=1)

            # 5.3 Handle Interface
            interface_content = "\n".join(needed_interfaces)
            interface_block = f"// --- AUTO_INJECT_INTERFACE_START ---\n@interface ViewController ()\n{interface_content}\n@end\n// --- AUTO_INJECT_INTERFACE_END ---\n"
            if "// --- AUTO_INJECT_INTERFACE_START ---" in vc_data:
                vc_data = re.sub(r"// --- AUTO_INJECT_INTERFACE_START ---.*?// --- AUTO_INJECT_INTERFACE_END ---\n?", interface_block if needed_interfaces else "", vc_data, flags=re.DOTALL)
            elif needed_interfaces:
                vc_data = re.sub(r'(@implementation ViewController)', interface_block + r'\n\1', vc_data, count=1)

            # 5.4 Handle Permissions Method
            method_content = "\n    ".join(needed_codes)
            method_block = f"// --- AUTO_INJECT_METHOD_START ---\n- (void)requestAllPermissions {{\n    {method_content}\n}}\n// --- AUTO_INJECT_METHOD_END ---\n"
            if "// --- AUTO_INJECT_METHOD_START ---" in vc_data:
                vc_data = re.sub(r"// --- AUTO_INJECT_METHOD_START ---.*?// --- AUTO_INJECT_METHOD_END ---\n?", method_block if needed_codes else "", vc_data, flags=re.DOTALL)
            elif needed_codes:
                vc_data = re.sub(r'(@implementation ViewController)', r'\1\n' + method_block, vc_data, count=1)

            # 5.5 Call permissions inside viewDidLoad
            call_stmt = "    [self requestAllPermissions]; // AUTO_INJECT_CALL"
            if "// AUTO_INJECT_CALL" not in vc_data and needed_codes:
                vc_data = re.sub(r'(- \(void\)viewDidLoad\s*\{)', r'\1\n' + call_stmt, vc_data, count=1)
            elif not needed_codes and "// AUTO_INJECT_CALL" in vc_data:
                vc_data = re.sub(r'\s*\[self requestAllPermissions\]; // AUTO_INJECT_CALL\n?', '', vc_data)

            # 5.6 Handle Exit App Feature
            exit_block = """
// --- AUTO_INJECT_EXIT_START ---
- (void)webView:(WKWebView *)webView decidePolicyForNavigationAction:(WKNavigationAction *)navigationAction decisionHandler:(void (^)(WKNavigationActionPolicy))decisionHandler {
    NSURL *url = navigationAction.request.URL;
    if ([url.scheme isEqualToString:@"app"] && [url.host isEqualToString:@"exit"]) {
        decisionHandler(WKNavigationActionPolicyCancel);
        exit(0);
        return;
    }
    decisionHandler(WKNavigationActionPolicyAllow);
}
// --- AUTO_INJECT_EXIT_END ---
"""
            if "// --- AUTO_INJECT_EXIT_START ---" in vc_data:
                vc_data = re.sub(r"\n?// --- AUTO_INJECT_EXIT_START ---.*?// --- AUTO_INJECT_EXIT_END ---\n?", exit_block if enable_exit else "\n", vc_data, flags=re.DOTALL)
            elif enable_exit:
                parts = vc_data.rsplit("@end", 1)
                if len(parts) == 2:
                    vc_data = parts[0] + exit_block + "@end\n"

            with open("ViewController.m", "w", encoding="utf-8") as f: f.write(vc_data)

        if not os.path.exists("Makefile"):
            print_banner(f"{RED}❌ ERROR: 'Makefile' not found!{RESET}")
            sys.exit(1)

        # 6. Execute Build
        subprocess.run(["make", "clean"], check=True)
        if build_deb: subprocess.run(["make", "package"], check=True)
        if build_ipa: subprocess.run(["make", "ipa"], check=True)
        print_banner(f"{GREEN}{t['done']}{RESET}")

    except subprocess.CalledProcessError:
        print_banner(f"{RED}{t['error']}{RESET}")
        
    finally:
        # BƯỚC CUỐI CÙNG: KHÔI PHỤC TOÀN BỘ FILE GỐC VÀ ICON GỐC
        restore_original_files(original_backups, t['restoring'])

if __name__ == "__main__":
    main()
