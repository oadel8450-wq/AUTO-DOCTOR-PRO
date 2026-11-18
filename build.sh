#!/bin/bash

set -e

echo "=================================="
echo " AUTO DOCTOR PRO APK BUILD"
echo " Developer: Adel Omar Abdel Aziz"
echo " AL ADL GROUP"
echo "=================================="

echo "Updating packages..."
sudo apt update

echo "Installing dependencies..."
sudo apt install -y \
    git zip unzip \
    openjdk-17-jdk \
    python3-pip \
    python3-venv \
    build-essential \
    autoconf \
    automake \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libffi-dev \
    libssl-dev \
    cmake

echo "Installing Buildozer..."
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade buildozer cython==0.29.33

echo "Accepting Android SDK licenses..."
export ANDROID_ACCEPT_SDK_LICENSE=1

echo "Building AUTO DOCTOR PRO APK..."

buildozer android debug

echo "=================================="
echo "BUILD COMPLETED"
echo "=================================="

mkdir -p bin

echo "APK FILES:"
ls -lh bin/*.apk

echo "AUTO DOCTOR PRO READY!"
