#import "ViewController.h"
#import <WebKit/WebKit.h>

// ==========================================
// 1. WEB TAB CONTROLLER
// ==========================================
@interface WebTabController : UIViewController <WKNavigationDelegate, WKUIDelegate, UIScrollViewDelegate>
@property (nonatomic, strong) WKWebView *webView;
@property (nonatomic, strong) NSDictionary *tabData;
@property (nonatomic, assign) CGFloat lastVelocityY;
@end

@implementation WebTabController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = UIColor.blackColor;

    WKWebViewConfiguration *config = [[WKWebViewConfiguration alloc] init];
    config.allowsInlineMediaPlayback = YES;
    config.mediaTypesRequiringUserActionForPlayback = WKAudiovisualMediaTypeNone;
    
    // Tính năng Userscript / Tampermonkey Injector
    if ([self.tabData[@"js_enabled"] boolValue] && [self.tabData[@"js_code"] length] > 0) {
        WKUserScript *script = [[WKUserScript alloc] initWithSource:self.tabData[@"js_code"] injectionTime:WKUserScriptInjectionTimeAtDocumentEnd forMainFrameOnly:NO];
        [config.userContentController addUserScript:script];
    }
    
    self.webView = [[WKWebView alloc] initWithFrame:self.view.bounds configuration:config];
    self.webView.navigationDelegate = self;
    self.webView.UIDelegate = self;
    self.webView.allowsBackForwardNavigationGestures = YES;
    self.webView.translatesAutoresizingMaskIntoConstraints = NO;
    self.webView.scrollView.delegate = self;
    self.webView.scrollView.contentInsetAdjustmentBehavior = UIScrollViewContentInsetAdjustmentNever;
    [self.view addSubview:self.webView];
    
    // Giao diện tràn màn hình - Tự động thích ứng Liquid Glass Tab Bar
    [NSLayoutConstraint activateConstraints:@[
        [self.webView.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor],
        [self.webView.bottomAnchor constraintEqualToAnchor:self.view.bottomAnchor], 
        [self.webView.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor],
        [self.webView.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor]
    ]];

    if (self.tabData[@"url"]) {
        [self.webView loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:self.tabData[@"url"]]]];
    }
}

// Tính năng ẩn hiện Tab Bar theo chiều vuốt
- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
    if (self.tabBarController.viewControllers.count <= 1) return; 
    CGFloat velocity = [scrollView.panGestureRecognizer velocityInView:scrollView].y;
    if (velocity < -50 && self.lastVelocityY >= -50) {
        [UIView animateWithDuration:0.3 animations:^{ self.tabBarController.tabBar.alpha = 0.0; }];
    } else if (velocity > 50 && self.lastVelocityY <= 50) {
        [UIView animateWithDuration:0.3 animations:^{ self.tabBarController.tabBar.alpha = 1.0; }];
    }
    self.lastVelocityY = velocity;
}

- (WKWebView *)webView:(WKWebView *)webView createWebViewWithConfiguration:(WKWebViewConfiguration *)configuration forNavigationAction:(WKNavigationAction *)navigationAction windowFeatures:(WKWindowFeatures *)windowFeatures {
    if (!navigationAction.targetFrame.isMainFrame) { [webView loadRequest:navigationAction.request]; }
    return nil;
}
@end

// ==========================================
// 2. USERSCRIPT EDITOR UI
// ==========================================
@interface ScriptEditVC : UIViewController
@property (nonatomic, strong) NSMutableDictionary *tabData;
@property (nonatomic, assign) NSInteger tabIndex;
@property (nonatomic, strong) UITextView *tv;
@property (nonatomic, strong) UISwitch *sw;
@end

@implementation ScriptEditVC
- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Tampermonkey Script";
    self.view.backgroundColor = [UIColor systemBackgroundColor];
    self.navigationItem.rightBarButtonItem = [[UIBarButtonItem alloc] initWithTitle:@"Save" style:UIBarButtonItemStyleDone target:self action:@selector(save)];

    self.sw = [[UISwitch alloc] initWithFrame:CGRectMake(20, 100, 50, 31)];
    self.sw.on = [self.tabData[@"js_enabled"] boolValue];
    [self.view addSubview:self.sw];

    UILabel *lbl = [[UILabel alloc] initWithFrame:CGRectMake(80, 100, 300, 31)];
    lbl.text = @"Enable Extension for this Tab";
    [self.view addSubview:lbl];

    self.tv = [[UITextView alloc] initWithFrame:CGRectMake(20, 150, self.view.bounds.size.width-40, self.view.bounds.size.height-200)];
    self.tv.layer.borderColor = [UIColor systemGrayColor].CGColor;
    self.tv.layer.borderWidth = 1;
    self.tv.layer.cornerRadius = 8;
    self.tv.font = [UIFont fontWithName:@"Courier" size:14];
    self.tv.text = self.tabData[@"js_code"];
    self.tv.autocapitalizationType = UITextAutocapitalizationTypeNone;
    [self.view addSubview:self.tv];
}
- (void)save {
    self.tabData[@"js_enabled"] = @(self.sw.on);
    self.tabData[@"js_code"] = self.tv.text;
    NSData *data = [[NSUserDefaults standardUserDefaults] objectForKey:@"AppTabs"];
    NSMutableArray *arr = [[NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingMutableContainers error:nil] mutableCopy];
    arr[self.tabIndex] = self.tabData;
    [[NSUserDefaults standardUserDefaults] setObject:[NSJSONSerialization dataWithJSONObject:arr options:0 error:nil] forKey:@"AppTabs"];
    [[NSUserDefaults standardUserDefaults] synchronize];
    [[NSNotificationCenter defaultCenter] postNotificationName:@"ReloadTabsNotification" object:nil];
    [self.navigationController popViewControllerAnimated:YES];
}
@end

// ==========================================
// 3. SETTINGS TAB CONTROLLER
// ==========================================
@interface SettingsTabController : UITableViewController
@property (nonatomic, strong) NSMutableArray *savedTabs;
@end

@implementation SettingsTabController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Settings";
    self.view.backgroundColor = [UIColor systemGroupedBackgroundColor];
    
    // Nút đóng nếu App chỉ có 1 tab (Mở dạng popup Modal)
    if (self.navigationController.viewControllers.firstObject == self && self.tabBarController == nil) {
        self.navigationItem.leftBarButtonItem = [[UIBarButtonItem alloc] initWithTitle:@"Close" style:UIBarButtonItemStyleDone target:self action:@selector(closeModal)];
    }
    [self loadTabs];
}
- (void)closeModal { [self dismissViewControllerAnimated:YES completion:nil]; }

- (void)loadTabs {
    NSData *data = [[NSUserDefaults standardUserDefaults] objectForKey:@"AppTabs"];
    if (data) self.savedTabs = [[NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingMutableContainers error:nil] mutableCopy];
    [self.tableView reloadData];
}

- (void)saveTabsAndReload {
    NSData *data = [NSJSONSerialization dataWithJSONObject:self.savedTabs options:0 error:nil];
    [[NSUserDefaults standardUserDefaults] setObject:data forKey:@"AppTabs"];
    [[NSUserDefaults standardUserDefaults] synchronize];
    [self loadTabs];
    [[NSNotificationCenter defaultCenter] postNotificationName:@"ReloadTabsNotification" object:nil];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView { return 4; }
- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    if (section == 0) return @"App & Device Info";
    if (section == 1) return @"Manage Web Tabs";
    if (section == 2) return @"Add New Tab";
    if (section == 3) return @"App Icon";
    return @"";
}
- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) return 3;
    if (section == 1) return self.savedTabs.count;
    if (section == 2) return 1;
    if (section == 3) return 1;
    return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    UITableViewCell *cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"Cell"];
    if (indexPath.section == 0) {
        cell.selectionStyle = UITableViewCellSelectionStyleNone;
        if (indexPath.row == 0) { cell.textLabel.text = @"Bundle ID"; cell.detailTextLabel.text = [[NSBundle mainBundle] bundleIdentifier]; }
        if (indexPath.row == 1) { cell.textLabel.text = @"Device"; cell.detailTextLabel.text = [UIDevice currentDevice].model; }
        if (indexPath.row == 2) { cell.textLabel.text = @"iOS Version"; cell.detailTextLabel.text = [UIDevice currentDevice].systemVersion; }
    } else if (indexPath.section == 1) {
        NSDictionary *tab = self.savedTabs[indexPath.row];
        cell.textLabel.text = tab[@"name"];
        cell.detailTextLabel.text = [NSString stringWithFormat:@"%@ %@", [tab[@"js_enabled"] boolValue] ? @"[JS ON]" : @"", tab[@"url"]];
        cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
    } else if (indexPath.section == 2) {
        cell.textLabel.text = @"➕ Add New Web Tab";
        cell.textLabel.textColor = [UIColor systemBlueColor];
    } else if (indexPath.section == 3) {
        cell.textLabel.text = @"🔄 Change App Icon";
        cell.textLabel.textColor = [UIColor systemPurpleColor];
    }
    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    [tableView deselectRowAtIndexPath:indexPath animated:YES];
    
    if (indexPath.section == 1) { 
        UIAlertController *sheet = [UIAlertController alertControllerWithTitle:@"Manage Tab" message:self.savedTabs[indexPath.row][@"name"] preferredStyle:UIAlertControllerStyleActionSheet];
        
        [sheet addAction:[UIAlertAction actionWithTitle:@"Edit Info (Name & URL)" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
            UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Edit Info" message:nil preferredStyle:UIAlertControllerStyleAlert];
            [alert addTextFieldWithConfigurationHandler:^(UITextField *tf) { tf.text = self.savedTabs[indexPath.row][@"name"]; }];
            [alert addTextFieldWithConfigurationHandler:^(UITextField *tf) { tf.text = self.savedTabs[indexPath.row][@"url"]; }];
            [alert addAction:[UIAlertAction actionWithTitle:@"Save" style:UIAlertActionStyleDefault handler:^(UIAlertAction *a) {
                NSMutableDictionary *mut = [self.savedTabs[indexPath.row] mutableCopy];
                mut[@"name"] = alert.textFields[0].text; mut[@"url"] = alert.textFields[1].text;
                self.savedTabs[indexPath.row] = mut;
                [self saveTabsAndReload];
            }]];
            [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
            [self presentViewController:alert animated:YES completion:nil];
        }]];
        
        [sheet addAction:[UIAlertAction actionWithTitle:@"Userscript (Tampermonkey)" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
            ScriptEditVC *vc = [[ScriptEditVC alloc] init];
            vc.tabData = [self.savedTabs[indexPath.row] mutableCopy];
            vc.tabIndex = indexPath.row;
            [self.navigationController pushViewController:vc animated:YES];
        }]];
        
        [sheet addAction:[UIAlertAction actionWithTitle:@"Delete Tab" style:UIAlertActionStyleDestructive handler:^(UIAlertAction * _Nonnull action) {
            [self.savedTabs removeObjectAtIndex:indexPath.row];
            [self saveTabsAndReload];
        }]];
        
        [sheet addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
        if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) {
            sheet.popoverPresentationController.sourceView = [tableView cellForRowAtIndexPath:indexPath];
            sheet.popoverPresentationController.sourceRect = [tableView cellForRowAtIndexPath:indexPath].bounds;
        }
        [self presentViewController:sheet animated:YES completion:nil];
        
    } else if (indexPath.section == 2) { 
        UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"New Tab" message:nil preferredStyle:UIAlertControllerStyleAlert];
        [alert addTextFieldWithConfigurationHandler:^(UITextField *tf) { tf.placeholder = @"Display Name"; }];
        [alert addTextFieldWithConfigurationHandler:^(UITextField *tf) { tf.placeholder = @"https://..."; }];
        [alert addAction:[UIAlertAction actionWithTitle:@"Add" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
            [self.savedTabs addObject:@{@"name": alert.textFields[0].text, @"url": alert.textFields[1].text, @"js_code": @"", @"js_enabled": @(NO)}];
            [self saveTabsAndReload];
        }]];
        [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
        [self presentViewController:alert animated:YES completion:nil];
        
    } else if (indexPath.section == 3) {
        UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Change Icon" message:@"Enter the exact filename of the icon." preferredStyle:UIAlertControllerStyleAlert];
        [alert addTextFieldWithConfigurationHandler:^(UITextField *tf) { tf.placeholder = @"Icon Name (or blank for Default)"; }];
        [alert addAction:[UIAlertAction actionWithTitle:@"Apply" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
            NSString *iconName = alert.textFields[0].text.length > 0 ? alert.textFields[0].text : nil;
            if ([[UIApplication sharedApplication] supportsAlternateIcons]) {
                [[UIApplication sharedApplication] setAlternateIconName:iconName completionHandler:nil];
            }
        }]];
        [alert addAction:[UIAlertAction actionWithTitle:@"Cancel" style:UIAlertActionStyleCancel handler:nil]];
        [self presentViewController:alert animated:YES completion:nil];
    }
}
@end

// ==========================================
// 4. MAIN ROOT CONTROLLER (Tab Bar / 1-Tab Mode)
// ==========================================
@interface ViewController : UITabBarController
@property (nonatomic, strong) UIVisualEffectView *floatingBtn;
@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    // LIQUID GLASS TAB BAR
    if (@available(iOS 13.0, *)) {
        UITabBarAppearance *appearance = [[UITabBarAppearance alloc] init];
        [appearance configureWithDefaultBackground]; 
        self.tabBar.standardAppearance = appearance;
        if (@available(iOS 15.0, *)) { self.tabBar.scrollEdgeAppearance = appearance; }
    }
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(buildTabs) name:@"ReloadTabsNotification" object:nil];
    [self buildTabs];
}

- (void)buildTabs {
    NSData *data = [[NSUserDefaults standardUserDefaults] objectForKey:@"AppTabs"];
    NSArray *tabsList;
    if (data) {
        tabsList = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
    } else {
        // Dữ liệu Mặc định (Demo 2 Tabs cho Github)
        NSString *jsonStr = @"[{\"name\": \"Lezhin\", \"url\": \"https://www.lezhinus.com\", \"js_code\": \"\", \"js_enabled\": false}, {\"name\": \"OLM\", \"url\": \"https://olm.vn\", \"js_code\": \"\", \"js_enabled\": false}]";
        tabsList = [NSJSONSerialization JSONObjectWithData:[jsonStr dataUsingEncoding:NSUTF8StringEncoding] options:0 error:nil];
        [[NSUserDefaults standardUserDefaults] setObject:[jsonStr dataUsingEncoding:NSUTF8StringEncoding] forKey:@"AppTabs"];
    }

    NSMutableArray *viewControllers = [NSMutableArray array];
    
    for (int i = 0; i < tabsList.count; i++) {
        WebTabController *webVC = [[WebTabController alloc] init];
        webVC.tabData = tabsList[i];
        webVC.tabBarItem = [[UITabBarItem alloc] initWithTitle:tabsList[i][@"name"] image:[UIImage systemImageNamed:@"globe"] tag:i];
        [viewControllers addObject:webVC];
    }
    
    // Tự động chuyển đổi kiến trúc Đơn Tab <-> Đa Tab
    if (tabsList.count <= 1) {
        self.tabBar.hidden = YES;
        [self setupFloatingButton];
    } else {
        self.tabBar.hidden = NO;
        if (self.floatingBtn) { [self.floatingBtn removeFromSuperview]; self.floatingBtn = nil; }
        
        SettingsTabController *settingsVC = [[SettingsTabController alloc] initWithStyle:UITableViewStyleGrouped];
        UINavigationController *navSettings = [[UINavigationController alloc] initWithRootViewController:settingsVC];
        navSettings.tabBarItem = [[UITabBarItem alloc] initWithTitle:@"Settings" image:[UIImage systemImageNamed:@"gear"] tag:99];
        [viewControllers addObject:navSettings];
    }
    
    [self setViewControllers:viewControllers animated:YES];
}

// LIQUID GLASS FLOATING BUTTON (Dành cho App 1 Tab)
- (void)setupFloatingButton {
    if (!self.floatingBtn) {
        UIBlurEffect *blur = [UIBlurEffect effectWithStyle:UIBlurEffectStyleSystemThinMaterialDark];
        self.floatingBtn = [[UIVisualEffectView alloc] initWithEffect:blur];
        self.floatingBtn.frame = CGRectMake(self.view.bounds.size.width - 65, self.view.bounds.size.height - 100, 44, 44);
        self.floatingBtn.layer.cornerRadius = 22;
        self.floatingBtn.clipsToBounds = YES;

        UIButton *btn = [UIButton buttonWithType:UIButtonTypeSystem];
        btn.frame = self.floatingBtn.bounds;
        [btn setImage:[UIImage systemImageNamed:@"gearshape.fill"] forState:UIControlStateNormal];
        btn.tintColor = [UIColor whiteColor];
        [btn addTarget:self action:@selector(openSettingsModal) forControlEvents:UIControlEventTouchUpInside];
        [self.floatingBtn.contentView addSubview:btn];
        [self.view addSubview:self.floatingBtn];
    }
}

- (void)openSettingsModal {
    SettingsTabController *settingsVC = [[SettingsTabController alloc] initWithStyle:UITableViewStyleGrouped];
    UINavigationController *nav = [[UINavigationController alloc] initWithRootViewController:settingsVC];
    [self presentViewController:nav animated:YES completion:nil];
}
@end
