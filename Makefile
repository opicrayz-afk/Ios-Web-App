TARGET = iphone:clang:latest:14.0
ARCHS = arm64
DEBUG = 0
FINALPACKAGE = 1

APPLICATION_NAME = MultiWebApp
MultiWebApp_FILES = main.m AppDelegate.m ViewController.m
MultiWebApp_FRAMEWORKS = UIKit WebKit
MultiWebApp_CFLAGS = -fobjc-arc -Wno-deprecated-declarations -Wno-error
MultiWebApp_BUNDLE_RESOURCES = Info.plist
MultiWebApp_BUNDLE_RESOURCE_DIRS = Resources
MultiWebApp_INSTALL_PATH = /Applications

include $(THEOS)/makefiles/common.mk
include $(THEOS_MAKE_PATH)/application.mk
