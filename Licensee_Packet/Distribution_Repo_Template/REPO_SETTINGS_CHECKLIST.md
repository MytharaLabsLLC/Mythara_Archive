**Copyright © 2025 Herbert Velez Jr. All rights reserved.**  

# Distribution Repository Settings Checklist (Private)

Configure these settings to minimize exposure while inviting licensees:

## Access and Visibility

- Visibility: Private  
- Manage access: Invite collaborators as “Read” only  
- Require 2FA for collaborators (Org setting if available)

## Features

- Disable: Wikis, Projects, Discussions (optional)  
- Issues: Off (optional; turn on only if you want inbound tickets)  
- Pages: Off  
- Secrets: None  
- Dependabot alerts: On (optional)  
- Private vulnerability reporting: On (optional)

## Branches and Code

- Default branch: main  
- Branch protection: Require PRs for changes (applies to your own edits)  
- No source code committed beyond minimal README and administration docs

## Forking and Exfiltration

- Forking controls: At org level, restrict forking if possible  
- Actions: Disable repository forking via org policies where available  
- Watermarking: Embed proprietary headers in all docs

## Releases

- Attach only: mythara-engine-v1.0.0.zip and mythara-engine-v1.0.0.zip.sha256  
- Release notes include SHA-256 and licensing summary  
- Verify downloads match the hash prior to evaluation

## Contacts

- Licensing and support: [Mythara.Engine@yahoo.com](mailto:Mythara.Engine@yahoo.com)
