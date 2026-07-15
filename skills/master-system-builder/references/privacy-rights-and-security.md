# Privacy, rights, and security

This guide is operational guidance, not legal advice.

## Access boundary

- Process only public material or material the user confirms they are authorized to use.
- Public viewing does not imply permission to republish a transcript or dataset.
- Do not bypass logins, payment, DRM, robots controls, rate limits, or technical restrictions.
- Let the human handle personal information, purchases, account consent, and terms acceptance.

## Keep out of packages and repositories

- API keys, OAuth tokens, cookies, passwords, private keys, and recovery codes.
- Signed URLs, session IDs, authorization headers, and temporary media manifests.
- Personal email addresses, account IDs, billing records, and customer data.
- Full paid books, course transcripts, member downloads, or private consultations unless stored in a user-controlled private location with an appropriate lawful basis.
- Absolute paths, internal hosts, or organization details that are unnecessary for operation.

## Safe state design

- Store credentials in the platform's credential manager, not package files.
- Store short-lived URLs only in ephemeral memory or a protected local cache.
- Persist provider IDs, checksums, timestamps, and source page URLs instead.
- Sanitize logs before saving them.
- Use restrictive file permissions for local secret state.

## Release review

Before publishing:

1. Start from a clean repository rather than changing a private repository to public.
2. Use synthetic examples.
3. Scan file names, current contents, Git history, dependencies, archives, and symlinks.
4. Search for secrets, personal paths, emails, hidden Unicode, encoded blobs, and unexpected network calls.
5. Confirm third-party licenses and attribution.
6. Rotate any credential that may have been committed; deletion alone does not remove it from history.
7. Run tests with network access denied. Core package creation and validation must remain local.

## Prohibited provenance mechanisms

Do not add covert telemetry, fingerprint users, transmit corpus statistics, or hide behavior-changing instructions. A public generator ID in local output is acceptable when it is documented and does not leave the machine.
