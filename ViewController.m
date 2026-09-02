#import "ViewController.h"
#import <WebKit/WebKit.h>
#import <AVFoundation/AVFoundation.h>
#import <Photos/Photos.h>

static NSString * const kStartURL = @"https://your website link";

@interface ViewController () <WKNavigationDelegate, WKUIDelegate, UIDocumentPickerDelegate>
@property (nonatomic, strong) WKWebView *webView;
@property (nonatomic, copy) void (^openPanelCompletion)(NSArray<NSURL *> * _Nullable URLs);
@property (nonatomic, assign) BOOL loadedOfflinePage;
@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = UIColor.blackColor;

    WKWebViewConfiguration *configuration = [[WKWebViewConfiguration alloc] init];
    configuration.allowsInlineMediaPlayback = YES;
    configuration.mediaTypesRequiringUserActionForPlayback = WKAudiovisualMediaTypeNone;
    configuration.allowsPictureInPictureMediaPlayback = YES;
    configuration.preferences.javaScriptEnabled = YES;
    configuration.preferences.javaScriptCanOpenWindowsAutomatically = YES;

    WKWebViewConfiguration *config = [[WKWebViewConfiguration alloc] init];
    self.webView = [[WKWebView alloc] initWithFrame:self.view.bounds configuration:config];
    self.webView.navigationDelegate = self;
    self.webView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    self.webView.frame = self.view.bounds;
    self.webView.UIDelegate = self;
    self.webView.allowsBackForwardNavigationGestures = YES;
    self.webView.translatesAutoresizingMaskIntoConstraints = NO;
    self.webView.scrollView.contentInsetAdjustmentBehavior = UIScrollViewContentInsetAdjustmentNever;
    [self.view addSubview:self.webView];
    // Thay thế khối NSLayoutConstraint cũ bằng khối này:
    [NSLayoutConstraint activateConstraints:@[
        // Né phần Notch/Dynamic Island ở trên cùng (dùng safeAreaLayoutGuide)
        [self.webView.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor],
         
        // Né thanh Home Indicator ở dưới đáy (dùng safeAreaLayoutGuide)
        [self.webView.bottomAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.bottomAnchor],
        
        // Căn khít 2 bên trái phải (dùng safeAreaLayoutGuide)
        [self.webView.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor],
        [self.webView.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor]
    ]];

    [self loadRemotePage];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    [self requestMediaPermissionsIfNeeded];
}

- (void)loadRemotePage {
    NSURL *url = [NSURL URLWithString:kStartURL];
    [self.webView loadRequest:[NSURLRequest requestWithURL:url cachePolicy:NSURLRequestUseProtocolCachePolicy timeoutInterval:20.0]];
}

- (void)loadOfflinePage {
    if (self.loadedOfflinePage) return;
    self.loadedOfflinePage = YES;

    NSURL *htmlURL = [[NSBundle mainBundle] URLForResource:@"index" withExtension:@"html" subdirectory:@"Resources"];
    if (!htmlURL) htmlURL = [[NSBundle mainBundle] URLForResource:@"index" withExtension:@"html"];
    if (htmlURL) {
        [self.webView loadFileURL:htmlURL allowingReadAccessToURL:htmlURL.URLByDeletingLastPathComponent];
    } else {
        [self.webView loadHTMLString:@"<html><body style='background:#000;color:#fff;font-family:-apple-system;padding:24px'><h2>Không thể tải nội dung</h2><p>Hãy kiểm tra kết nối mạng và thử lại.</p></body></html>" baseURL:nil];
    }
}

- (void)requestMediaPermissionsIfNeeded {
    // 1. QUAN TRỌNG: Thiết lập phiên âm thanh để cho phép Ghi âm (Record)
    AVAudioSession *audioSession = AVAudioSession.sharedInstance;
    NSError *error = nil;
    [audioSession setCategory:AVAudioSessionCategoryPlayAndRecord withOptions:AVAudioSessionCategoryOptionDefaultToSpeaker error:&error];
    [audioSession setActive:YES error:&error];

    // 2. Xin quyền Camera
    if ([AVCaptureDevice authorizationStatusForMediaType:AVMediaTypeVideo] == AVAuthorizationStatusNotDetermined) {
        [AVCaptureDevice requestAccessForMediaType:AVMediaTypeVideo completionHandler:^(__unused BOOL granted) {}];
    }
    
    // 3. Xin quyền Micro
    if (audioSession.recordPermission == AVAudioSessionRecordPermissionUndetermined) {
        [audioSession requestRecordPermission:^(__unused BOOL granted) {}];
    }
    
    // 4. Xin quyền Thư viện ảnh
    if ([PHPhotoLibrary authorizationStatus] == PHAuthorizationStatusNotDetermined) {
        [PHPhotoLibrary requestAuthorization:^(__unused PHAuthorizationStatus status) {}];
    }
}
#pragma mark - WKNavigationDelegate

- (void)webView:(WKWebView *)webView didFailProvisionalNavigation:(WKNavigation *)navigation withError:(NSError *)error {
    if (error.code != NSURLErrorCancelled) [self loadOfflinePage];
}

- (void)webView:(WKWebView *)webView didFailNavigation:(WKNavigation *)navigation withError:(NSError *)error {
    if (error.code != NSURLErrorCancelled) [self loadOfflinePage];
}

#pragma mark - WKUIDelegate

#if __IPHONE_OS_VERSION_MAX_ALLOWED >= 150000
- (void)webView:(WKWebView *)webView requestMediaCapturePermissionForOrigin:(WKSecurityOrigin *)origin initiatedByFrame:(WKFrameInfo *)frame type:(WKMediaCaptureType)type decisionHandler:(void (^)(WKPermissionDecision decision))decisionHandler API_AVAILABLE(ios(15.0)) {
    // Only the configured first-party site receives automatic WebKit capture approval.
    // iOS still enforces the camera/microphone grants requested above.
    BOOL isTrustedOrigin = [origin.host caseInsensitiveCompare:@"your website link but dont need https://"] == NSOrderedSame;
    decisionHandler(isTrustedOrigin ? WKPermissionDecisionGrant : WKPermissionDecisionDeny);
}
#endif

- (WKWebView *)webView:(WKWebView *)webView createWebViewWithConfiguration:(WKWebViewConfiguration *)configuration forNavigationAction:(WKNavigationAction *)navigationAction windowFeatures:(WKWindowFeatures *)windowFeatures {
    if (!navigationAction.targetFrame.isMainFrame) {
        [webView loadRequest:navigationAction.request];
    }
    return nil;
}

- (void)webView:(WKWebView *)webView runJavaScriptAlertPanelWithMessage:(NSString *)message initiatedByFrame:(WKFrameInfo *)frame completionHandler:(void (^)(void))completionHandler {
    NSString *title = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleDisplayName"];
    UIAlertController *alert = [UIAlertController alertControllerWithTitle:title message:message preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action) { completionHandler(); }]];
    [self presentViewController:alert animated:YES completion:nil];
}

- (void)webView:(WKWebView *)webView runJavaScriptConfirmPanelWithMessage:(NSString *)message initiatedByFrame:(WKFrameInfo *)frame completionHandler:(void (^)(BOOL result))completionHandler {
    NSString *title = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleDisplayName"];
    UIAlertController *alert = [UIAlertController alertControllerWithTitle:title message:message preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Hủy" style:UIAlertActionStyleCancel handler:^(__unused UIAlertAction *action) { completionHandler(NO); }]];
    [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action) { completionHandler(YES); }]];
    [self presentViewController:alert animated:YES completion:nil];
}

#pragma mark - UIDocumentPickerDelegate

@end
