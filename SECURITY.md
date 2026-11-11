# Security and signing policy

This public repository contains game source, not private credentials or player data.

- Never commit Android keystores, passwords, Base64 secrets, private tokens, or signing ZIPs.
- Store ANDROID_KEYSTORE_BASE64, ANDROID_KEYSTORE_PASSWORD, ANDROID_KEY_PASSWORD, and ANDROID_KEY_ALIAS as GitHub Actions repository secrets.
- Maintain a private offline copy of the release keystore and passwords. Losing it prevents updates signed with the same key.
- Never print signing credentials to Actions logs, issues, or pull requests.
- No telemetry, network services, or third-party SDKs without a deliberate privacy and licensing review.

Report vulnerabilities privately using GitHub private vulnerability reporting if enabled, or another private channel to the repository owner. Do not post working exploits or exposed credentials in public issues.
