# Create the public GitHub repository

- **Repository name:** `Windows-Admin-Toolkit`
- **Description (copy/paste):** A free, open-source Windows 10/11 maintenance and diagnostics toolkit with a modern Python GUI, 69 built-in commands, safety warnings, and one-click system tools.
- **Visibility:** Public
- **License:** MIT (this package already contains a LICENSE file)
- **Suggested topics:** `windows`, `python`, `tkinter`, `diagnostics`, `system-maintenance`, `windows-11`, `open-source`, `admin-tools`

## Publish using GitHub web UI

1. Create a public, **empty** repository named `Windows-Admin-Toolkit`. Leave GitHub's optional README/LICENSE initializers **unchecked** because these files already exist in the package.
2. Upload **the extracted files and folders inside** `Windows_Admin_Toolkit_v1.2.0-beta.1/`, not the outer ZIP itself. Be sure `.github/workflows/windows-ci.yml` and `.gitignore` are also uploaded (some file upload tools hide dotfiles).
3. Confirm GitHub renders `README.md`, shows the MIT license and displays `assets/app_preview.png`.
4. Check the GitHub Actions tab to see the Windows unit tests and unsigned beta EXE build. CI verifies code/tests and build completion, **not Windows command correctness**.
5. After real Windows pilot testing, create a GitHub Release tagged `v1.2.0-beta.1`. Do not label it stable or attach an untested EXE as a verified binary.
6. Enable private vulnerability reporting / security advisories in repository security settings, if available.

**Important:** Files uploaded directly through the GitHub web interface must preserve the `.github/workflows/` folder structure. The ZIP in this deliverable is a backup/distribution archive; GitHub source should be the actual extracted file tree.
