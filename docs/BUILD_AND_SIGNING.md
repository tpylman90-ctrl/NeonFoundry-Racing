# Android build and signing setup

The repo starts with two GitHub Actions workflows: **Repository checks** for every push and pull request, and **Android APK** for game changes or manual runs.

## Software

Godot 4.5.1 stable with matching export templates; Java 17; Android SDK platform/build tools 35.0.0. Android ARM64. Godot Mobile/Vulkan, with OpenGL fallback disabled.

## Release signing GitHub Secrets

Open the repo Settings > Secrets and variables > Actions. Add the four secrets using the private signing ZIP prepared separately:

| Secret | Purpose |
| --- | --- |
| ANDROID_KEYSTORE_BASE64 | Base64 text of your private release keystore |
| ANDROID_KEYSTORE_PASSWORD | Keystore password |
| ANDROID_KEY_PASSWORD | Key password (matches keystore password in this export) |
| ANDROID_KEY_ALIAS | The alias stored in the release keystore |

The CI workflow decodes the keystore only on the GitHub runner, verifies the release signature and deletes the temporary key. Do not commit, paste, screenshot or email the credentials.

## Packages

- Debug: com.tpylman.neonfoundryracing.debug
- Release: com.tpylman.neonfoundryracing

Keep the release package ID and signing certificate stable after distributing installable releases. Changing either prevents seamless in-place updates.

## Build routine

1. Run: python3 tools/check_repository.py
2. Run: python3 -m unittest discover -s tools/tests
3. Open game/project.godot in Godot and import the project.
4. GitHub Actions > Android APK > Run workflow (or make a game-source commit).
5. Download the uploaded APK artifact. Debug is always built; release builds only if all four secrets exist.
6. Verify the signed release with apksigner and install on an Android ARM64 device.
7. Check the startup label says Mobile/Vulkan. CI's headless test cannot confirm actual Android GPU speed.

No store release, third-party SDK, production account or gameplay content is configured yet.
