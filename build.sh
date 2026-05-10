#!/bin/bash
# ============================================================
#  Titan Studio PRO - Build Script
#  Usage:
#    chmod +x build.sh
#    ./build.sh          # builds debug APK
#    ./build.sh release  # builds release APK
#    ./build.sh clean    # clean build artifacts
#    ./build.sh deploy   # build + deploy to connected device
# ============================================================

APP_NAME="Titan Studio PRO"
VERSION="13.0.0"
APK_DIR="./bin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  ${APP_NAME} v${VERSION} - Build Script${NC}"
echo -e "${BLUE}============================================${NC}"

# Check buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo -e "${RED}ERROR: buildozer not found!${NC}"
    echo "Install it with: pip install buildozer"
    exit 1
fi

# Check Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}ERROR: Java not found!${NC}"
    echo "Install with: sudo apt install openjdk-17-jdk"
    exit 1
fi

MODE=${1:-debug}

case "$MODE" in
    clean)
        echo -e "${YELLOW}Cleaning build artifacts...${NC}"
        buildozer android clean
        rm -rf .buildozer/android/platform/build-*/build/other_builds/
        echo -e "${GREEN}Clean done.${NC}"
        ;;

    release)
        echo -e "${YELLOW}Building RELEASE APK...${NC}"
        echo -e "${RED}Make sure keystore is configured in buildozer.spec!${NC}"
        buildozer -v android release
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}SUCCESS! Release APK is in: ${APK_DIR}/${NC}"
            ls -lh ${APK_DIR}/*.apk 2>/dev/null
        else
            echo -e "${RED}Build FAILED. Check errors above.${NC}"
            exit 1
        fi
        ;;

    deploy)
        echo -e "${YELLOW}Building and deploying to device...${NC}"
        echo "Make sure USB debugging is ON and device is connected."
        buildozer -v android debug deploy run logcat
        ;;

    debug|*)
        echo -e "${YELLOW}Building DEBUG APK...${NC}"
        echo "This may take 20-40 minutes on first build."
        buildozer -v android debug
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}============================================${NC}"
            echo -e "${GREEN}  BUILD SUCCESS!${NC}"
            echo -e "${GREEN}============================================${NC}"
            echo -e "APK location:"
            ls -lh ${APK_DIR}/*.apk 2>/dev/null
            echo ""
            echo "To install on connected device:"
            echo "  adb install ${APK_DIR}/*.apk"
        else
            echo -e "${RED}Build FAILED. Check errors above.${NC}"
            echo ""
            echo "Common fixes:"
            echo "  1. Run: ./build.sh clean  then try again"
            echo "  2. Remove 'edge-tts' from requirements in buildozer.spec if aiohttp fails"
            echo "  3. Check Java version: java -version (need Java 11 or 17)"
            exit 1
        fi
        ;;
esac
