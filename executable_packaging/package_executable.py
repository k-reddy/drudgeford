#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Execute a shell command and handle errors."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True, cwd=cwd
        )
        print(f"Successfully executed: {command}")
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    # Get the script's directory and the target directory
    script_dir = Path(__file__).parent
    target_dir = script_dir.parent  # drudgeford directory

    # Change to the target directory
    os.chdir(target_dir)
    print(f"Changed working directory to: {target_dir}")

    # List of commands to execute
    commands = [
        # Code sign the app
        'codesign --force --deep --strict --sign "Developer ID Application: Keerthi Reddy (CKMMRP742B)" --options runtime executable_packaging/executable_file/drudgeford.app',
        # Create zip for notarization
        'ditto -c -k --keepParent "executable_packaging/executable_file/drudgeford.app" "executable_packaging/executable_file/drudgeford.zip"',
        # Submit app for notarization and wait for result
        'xcrun notarytool submit "executable_packaging/executable_file/drudgeford.zip" --keychain-profile "Drudgeford-notary" --wait',
        # Staple the app
        'xcrun stapler staple "executable_packaging/executable_file/drudgeford.app"',
        # Create DMG
        """create-dmg \\
            --volname "drudgeford" \\
            --window-pos 200 120 \\
            --window-size 800 400 \\
            --volicon executable_packaging/executable_file/drudgeford.build/icons/icons.icns \\
            --icon-size 100 \\
            --icon drudgeford.app 200 200 \\
            --hide-extension drudgeford.app \\
            --app-drop-link 600 200 \\
            executable_packaging/executable_file/drudgeford.dmg \\
            executable_packaging/executable_file/drudgeford.app""",
        # Code sign DMG
        'codesign --sign "Developer ID Application: Keerthi Reddy (CKMMRP742B)" --options runtime executable_packaging/executable_file/drudgeford.dmg',
        # Submit DMG for notarization
        'xcrun notarytool submit "executable_packaging/executable_file/drudgeford.dmg" --keychain-profile "Drudgeford-notary" --wait',
        # Staple DMG
        'xcrun stapler staple "executable_packaging/executable_file/drudgeford.dmg"',
        # Verify notarization for app (dmg will say error)
        "spctl --assess -vv executable_packaging/executable_file/drudgeford.app",
    ]

    # Execute commands in sequence
    for command in commands:
        print("\n" + "=" * 80)
        print(f"Executing command:\n{command}\n")
        _ = run_command(command)


if __name__ == "__main__":
    main()
