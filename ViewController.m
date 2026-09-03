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
    
    [NSLayoutConstraint activateConstraints:@[
        
        [self.webView.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor],
         
        [self.webView.bottomAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.bottomAnchor],
        
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
    AVAudioSession *audioSession = AVAudioSession.sharedInstance;
    NSError *error = nil;
    [audioSession setCategory:AVAudioSessionCategoryPlayAndRecord withOptions:AVAudioSessionCategoryOptionDefaultToSpeaker error:&error];
    [audioSession setActive:YES error:&error];

    if ([AVCaptureDevice authorizationStatusForMediaType:AVMediaTypeVideo] == AVAuthorizationStatusNotDetermined) {
        [AVCaptureDevice requestAccessForMediaType:AVMediaTypeVideo completionHandler:^(__unused BOOL granted) {}];
    }
    
    if (audioSession.recordPermission == AVAudioSessionRecordPermissionUndetermined) {
        [audioSession requestRecordPermission:^(__unused BOOL granted) {}];
    }
    
    if ([PHPhotoLibrary authorizationStatus] == PHAuthorizationStatusNotDetermined) {
        [PHPhotoLibrary requestAuthorization:^(__unused PHAuthorizationStatus status) {}];
    }
}
#pragma mark - WKNavigationDelegate

- (void)webView:(WKWebView *)webView decidePolicyForNavigationAction:(WKNavigationAction *)navigationAction decisionHandler:(void (^)(WKNavigationActionPolicy))decisionHandler {
    NSURL *url = navigationAction.request.URL;
    
    if ([url.scheme isEqualToString:@"app"] && [url.host isEqualToString:@"exit"]) {
        decisionHandler(WKNavigationActionPolicyCancel);
        
        exit(0); 
        return;
    }
    
    decisionHandler(WKNavigationActionPolicyAllow);
}


- (void)webView:(WKWebView *)webView didFailProvisionalNavigation:(WKNavigation *)navigation withError:(NSError *)error {
    if (error.code != NSURLErrorCancelled) [self loadOfflinePage];
}

- (void)webView:(WKWebView *)webView didFailNavigation:(WKNavigation *)navigation withError:(NSError *)error {
    if (error.code != NSURLErrorCancelled) [self loadOfflinePage];
}

#pragma mark - WKUIDelegate

#if __IPHONE_OS_VERSION_MAX_ALLOWED >= 150000
- (void)webView:(WKWebView *)webView requestMediaCapturePermissionForOrigin:(WKSecurityOrigin *)origin initiatedByFrame:(WKFrameInfo *)frame type:(WKMediaCaptureType)type decisionHandler:(void (^)(WKPermissionDecision decision))decisionHandler API_AVAILABLE(ios(15.0)) {
    
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
    [alert addAction:[UIAlertAction actionWithTitle:@"Chấp Nhận" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action) { completionHandler(); }]];
    [self presentViewController:alert animated:YES completion:nil];
}

- (void)webView:(WKWebView *)webView runJavaScriptConfirmPanelWithMessage:(NSString *)message initiatedByFrame:(WKFrameInfo *)frame completionHandler:(void (^)(BOOL result))completionHandler {
    NSString *title = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleDisplayName"];
    UIAlertController *alert = [UIAlertController alertControllerWithTitle:title message:message preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Hủy" style:UIAlertActionStyleCancel handler:^(__unused UIAlertAction *action) { completionHandler(NO); }]];
    [alert addAction:[UIAlertAction actionWithTitle:@"Chấp Nhận" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action) { completionHandler(YES); }]];
    [self presentViewController:alert animated:YES completion:nil];
}

#pragma mark - UIDocumentPickerDelegate

#pragma mark - Intercept Custom URLs (Exit App)

- (void)webView:(WKWebView *)webView decidePolicyForNavigationAction:(WKNavigationAction *)navigationAction decisionHandler:(void (^)(WKNavigationActionPolicy))decisionHandler {
    NSURL *url = navigationAction.request.URL;
    
    if ([url.scheme isEqualToString:@"app"] && [url.host isEqualToString:@"exit"]) {
        decisionHandler(WKNavigationActionPolicyCancel);
        exit(0);
        return;
    }
    
    decisionHandler(WKNavigationActionPolicyAllow);
}

@end
