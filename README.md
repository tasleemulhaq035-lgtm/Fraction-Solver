# ➗ Fraction Solver & Master Calculator 🧮

A sleek, modern, multi-functional calculator application built entirely in Python using the Kivy framework. This app goes far beyond basic arithmetic, offering a deep-math fraction analysis engine, a dedicated smart calculator, and a persistent calculation history—all wrapped in a premium, custom-designed Light Mode UI.

---

## 🚀 Download the App

Want to try the app without compiling the code yourself? You can download the latest Android `.apk` directly to your phone!

**👉 [Download the Latest APK & Source Code Here](https://github.com/tasleemulhaq035-lgtm/Fraction-Solver/releases/latest)**

---

## ✨ Features

### 1. 🔢 The Fraction Engine (Primary Tab: ½)
Not just a calculator, but a step-by-step mathematical analyst. Enter any fraction or fraction-based equation to receive:
* **Equation Solving:** Add, subtract, multiply, or divide fractions with standard Order of Operations.
* **Deep Simplification:** Automatically finds the Greatest Common Divisor (GCD) and reduces fractions to their lowest terms.
* **Mixed Numbers:** Converts improper fractions into perfectly formatted mixed numbers.
* **Long Division & Decimals:** Calculates exact decimals, including advanced tracking for repeating/recurring decimal cycles.
* **Advanced Math:** Automatically calculates the reciprocal and the Continued Fraction notation.

### 2. 🧮 Smart Calculator (Secondary Tab: =)
A fully featured, daily-use calculator designed for speed and precision.
* **Smart Rounding:** Floating-point math is intelligently rounded to 8 decimal places to prevent screen overflow and `0.0000000001` graphical bugs.
* **Percentage Support:** Built-in `%` parsing for quick real-world math.
* **Sleek UI:** Custom `ModernButton` components with dynamic touch animations and shadow/bevel effects.

### 3. 🕒 Calculation History (Tertiary Tab: H)
Never lose track of your work.
* **Auto-Tracking:** Every successful calculation made in the normal calculator is automatically logged.
* **Responsive Text:** Highly complex equations automatically wrap to the next line instead of flying off the screen.
* **Wipe the Slate:** A dedicated, bright-red "Delete All" button to instantly clear your session memory.

---

## 🎨 UI / UX Design
This app does not use standard, rigid Kivy components. The interface was engineered from the ground up:
* **Custom Navigation Bar:** Uses custom Kivy Canvas drawing to create "floating" navigation tabs.
* **Active State Highlighting:** Selected tabs feature a sleek, dynamic Deep Orange (`#D35400`) pill-shaped background that automatically scales to `1.6x` width for a premium native-app feel.
* **Absolute Light Theme:** A custom `LightBoxLayout` forces a pure, crisp (`#F4F6F9`) background, completely overriding Kivy's default dark textures.
* **Dynamic Geometry:** Buttons automatically calculate their own corner radius based on screen size, ensuring they always remain perfectly proportioned pills/circles and never stretch into strange ovals.

---

## ⚙️ The CI/CD Pipeline & Build Architecture
This application is compiled into a native Android `.apk` using a highly customized, military-grade **GitHub Actions** workflow. 

To overcome standard `python-for-android` (p4a) limitations and Cython compilation bugs, the build pipeline is strictly locked to the following architecture:
* **OS:** Ubuntu-22.04 runner.
* **Java:** strictly `Java 17` (Temurin distribution) to satisfy modern Gradle 8.0+ requirements.
* **Cython:** Locked precisely to `Cython==0.29.37` to guarantee successful Kivy C++ translation without silent failures.
* **Engine:** Uses the `develop` branch of `python-for-android` to bypass critical file-copying bugs found in the current master branch.

### How to Build the APK Yourself
Because the GitHub Actions workflow is already fully configured, building a new version of the app from source is entirely automated:
1. Fork or clone this repository.
2. Make a change to `main.py` or `buildozer.spec`.
3. Push the commit to the `main` or `master` branch.
4. Go to the **Actions** tab in GitHub.
5. Wait ~15-18 minutes for the cloud computer to complete the C++ compilation.
6. Download the newly packaged `.apk` from the **Artifacts** section at the bottom of the successful run summary!

---

## 🛠️ Tech Stack
* **Language:** Python 3
* **Framework:** Kivy (GUI)
* **Compiler:** Buildozer / python-for-android
* **Automation:** GitHub Actions

---
*Designed and engineered with persistence, precision, and a whole lot of math.* 🚀
