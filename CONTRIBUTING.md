# Contributing to Windows Admin Toolkit

Thank you for helping improve the toolkit. This is an MIT-licensed Python/Tkinter application.

## Before opening a pull request

1. Describe the user problem and Windows versions affected.
2. New commands require a documented syntax and Windows-version requirements, a plain-English explanation, an appropriate safety/risk level, and explicit flags for admin, drive letter, report or user input.
3. Never add arbitrary shell commands, silent deletion, credential collection, security bypasses or automatic registry cleaners.
4. Run `python -m unittest discover -s tests -v` and, where possible, the Tkinter smoke/click-through tests.
5. Include automated tests for validators or launcher changes. If you executed commands on Windows, specify OS build/edition and whether elevation was used.
6. Use README/USER_MANUAL/COMMAND_REFERENCE updates and screenshots as appropriate. Avoid posting private logs or real workstation identities.

Source coding style is deliberately standard-library-first; optional build tooling (PyInstaller) is development-only. Until physical Windows validation completes, label feature/test evidence as simulated versus live.
