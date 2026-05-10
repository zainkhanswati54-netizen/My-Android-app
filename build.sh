#!/bin/bash
# ============================================================
#  Titan Studio PRO - build.sh
#  Version 13.0.0
#
#  USAGE:
#    chmod +x build.sh        (pehli baar sirf yeh karo)
#
#    ./build.sh               → Debug APK banao
#    ./build.sh release       → Release APK banao
#    ./build.sh clean         → Build cache saaf karo
#    ./build.sh deploy        → Build + phone pe install
#    ./build.sh setup         → System setup (pehli baar)
#    ./build.sh log           → Last build ka log dekho
#
#  NOTE: Yeh script Linux/Ubuntu pe chalti hai.
#        Windows pe GitHub Actions use karo (build.yml).
# ============================================================

APP_NAME="Titan Studio PRO"
VERSION="13.0.0"
APK_DIR="./bin"
LOG_FILE="./build_log.txt"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   ${APP_NAME} v${VERSION}${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

MODE=${1:-debug}

check_buildozer() {
    if ! command -v buildozer &> /dev/null; then
        echo -e "${RED}ERROR: buildozer nahi mila!${NC}"
        echo "Install: pip install buildozer cython"
        exit 1
    fi
}

check_java() {
    if ! command -v java &> /dev/null; then
        echo -e "${RED}ERROR: Java nahi mila!${NC}"
        echo "Install: sudo apt install openjdk-17-jdk"
        exit 1
    fi
    echo -e "${CYAN}Java: $(java -version 2>&1 | head -1)${NC}"
}

show_apk() {
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}   BUILD SUCCESSFUL!${NC}"
    echo -e "${GREEN}================================================${NC}"
    ls -lh ${APK_DIR}/*.apk 2>/dev/null
    echo ""
    echo "Phone pe install: adb install $(ls ${APK_DIR}/*.apk 2>/dev/null | head -1)"
}

show_error() {
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}   BUILD FAILED!${NC}"
    echo -e "${RED}================================================${NC}"
    echo "Fix try karo:"
    echo "  1. ./build.sh clean → phir dubara"
    echo "  2. ./build.sh log   → error dekho"
    echo "  3. buildozer.spec se edge-tts hatao agar aiohttp fail ho"
}

case "$MODE" in

    setup)
        echo -e "${YELLOW}System setup...${NC}"
        sudo apt-get update -qq
        sudo apt-get install -y git zip unzip openjdk-17-jdk \
            autoconf libtool pkg-config zlib1g-dev \
            libncurses5-dev libncursesw5-dev \
            cmake libffi-dev libssl-dev python3-pip
        pip install buildozer cython
        echo -e "${GREEN}Setup complete! Ab: ./build.sh${NC}"
        ;;

    clean)
        echo -e "${YELLOW}Cache saaf ho raha hai...${NC}"
        buildozer android clean
        rm -rf .buildozer/android/platform/build-*/build/other_builds/ 2>/dev/null
        rm -f ${LOG_FILE} 2>/dev/null
        echo -e "${GREEN}Clean done!${NC}"
        ;;

    log)
        [ -f "${LOG_FILE}" ] && tail -100 ${LOG_FILE} || echo "Log nahi mila. Pehle build karo."
        ;;

    release)
        check_buildozer; check_java
        echo -e "${YELLOW}RELEASE build...${NC}"
        buildozer -v android release 2>&1 | tee ${LOG_FILE}
        [ ${PIPESTATUS[0]} -eq 0 ] && show_apk || { show_error; exit 1; }
        ;;

    deploy)
        check_buildozer; check_java
        echo -e "${YELLOW}Build + Deploy...${NC}"
        buildozer -v android debug deploy run 2>&1 | tee ${LOG_FILE}
        ;;

    debug|*)
        check_buildozer; check_java
        echo -e "${YELLOW}DEBUG APK ban raha hai...${NC}"
        echo -e "${CYAN}Pehli baar 30-45 min lagenge.${NC}"
        buildozer -v android debug 2>&1 | tee ${LOG_FILE}
        [ ${PIPESTATUS[0]} -eq 0 ] && show_apk || { show_error; exit 1; }
        ;;

esac
