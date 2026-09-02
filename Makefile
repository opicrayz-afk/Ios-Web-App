TARGET := iphone:clang:latest:13.0
# An arm64 slice runs on arm64e hardware as well.  Keeping only arm64 avoids
# the incompatible pre-iOS-14 arm64e ABI and preserves the iOS 13 minimum.
ARCHS = arm64
FINALPACKAGE = 1

include $(THEOS)/makefiles/common.mk

APPLICATION_NAME = YourAppName
YourAppName_FILES = main.m AppDelegate.m ViewController.m
YourAppName_FRAMEWORKS = UIKit WebKit AVFoundation Photos
YourAppName_CFLAGS = -fobjc-arc
# Theos only copies resources declared below.  Info.plist must be at the
# root of the .app bundle; declaring it as a bundle resource ensures that.
YourAppName_BUNDLE_RESOURCES = Info.plist
YourAppName_BUNDLE_RESOURCE_DIRS = Resources
YourAppName_INSTALL_PATH = /Applications

# Jailbreak package: make package
THEOS_PACKAGE_SCHEME ?= rootful
THEOS_PACKAGE_FORMAT = deb

include $(THEOS_MAKE_PATH)/application.mk

# IPA package: make ipa SIGN_IDENTITY="Apple Distribution: Your Name (TEAMID)" \
#                         PROVISIONING_PROFILE=/absolute/path/profile.mobileprovision
IPA_NAME = $(APPLICATION_NAME).ipa
IPA_DIR = .theos/ipa
IPA_APP = $(IPA_DIR)/Payload/$(APPLICATION_NAME).app
IPA_OUTPUT = packages/$(IPA_NAME)
SIGN_IDENTITY ?=
PROVISIONING_PROFILE ?=

.PHONY: ipa clean-ipa verify-ipa

ipa: stage clean-ipa

	@mkdir -p $(IPA_DIR)/Payload
	@cp -R .theos/_/Applications/$(APPLICATION_NAME).app $(IPA_DIR)/Payload/
	@if [ -n "$(PROVISIONING_PROFILE)" ]; then security cms -D -i "$(PROVISIONING_PROFILE)" -o "$(IPA_DIR)/profile.plist"; fi
	@if [ -n "$(PROVISIONING_PROFILE)" ]; then /usr/libexec/PlistBuddy -x -c "Print :Entitlements" "$(IPA_DIR)/profile.plist" > "$(IPA_DIR)/Entitlements.plist"; fi
	@if [ -n "$(PROVISIONING_PROFILE)" ]; then cp "$(PROVISIONING_PROFILE)" "$(IPA_APP)/embedded.mobileprovision"; fi
	@if [ -n "$(SIGN_IDENTITY)" ] && [ -n "$(PROVISIONING_PROFILE)" ]; then codesign --force --sign "$(SIGN_IDENTITY)" --entitlements "$(IPA_DIR)/Entitlements.plist" --timestamp=none "$(IPA_APP)"; else echo "Warning: IPA is unsigned. Set both SIGN_IDENTITY and PROVISIONING_PROFILE for a non-jailbreak device."; fi
	@mkdir -p packages
	@cd $(IPA_DIR) && zip -qry ../../$(IPA_OUTPUT) Payload
	@echo "Created $(IPA_OUTPUT)"

# Read-only structural check for an IPA produced by the target above.
verify-ipa: ipa
	@unzip -l $(IPA_OUTPUT) | grep -q "Payload/$(APPLICATION_NAME).app/Info.plist"
	@unzip -l $(IPA_OUTPUT) | grep -q "Payload/$(APPLICATION_NAME).app/$(APPLICATION_NAME)"
	@unzip -l $(IPA_OUTPUT) | grep -q "Payload/$(APPLICATION_NAME).app/index.html"
	@echo "IPA structure verified."

clean-ipa:
	@rm -rf $(IPA_DIR)
