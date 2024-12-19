import sys
from subprocess import run
import platform


def create_build_script():
    python_exe = sys.executable
    main_script = "frontend_main.py"

    include_modules = [
        "backend.utils.config",
        "pyxel_ui.constants",
        "pyxel_ui.models.entity",
        "pyxel_ui.models.tasks",
        "pyxel_ui.models.font",
        "pyxel_ui.models.view_params",
        "pyxel_ui.models.view_section",
        "pyxel_ui.engine",
        "pyxel_ui.utils",
        "pyxel_ui.enums",
        "pyxel_ui.controllers.view_factory",
        "pyxel_ui.controllers.view_manager",
        "pyxel_ui.controllers.user_input_manager",
        "pyxel_ui.views.sprite",
        "server.tcp_client",
        "server.task_jsonifier",
        "server.server_utils",
    ]

    nuitka_command = [
        python_exe,
        "-m",
        "nuitka",
        "--follow-imports",
        "--standalone",
        "--static-libpython=no",
        "--output-dir=banana",
        "--nofollow-import-to=numpy",
    ]

    # Add macOS specific flags
    if platform.system() == "Darwin":
        nuitka_command.extend(
            [
                "--macos-create-app-bundle",
                "--include-module=_sysconfigdata__darwin_darwin",
                "--python-flag=no_site",
                "--macos-app-icon=executable/static/drudgeford_cover.png",
            ]
        )

    # Add module includes
    for module in include_modules:
        nuitka_command.extend(["--include-module=" + module])

    # Add package data and assets
    nuitka_command.extend(
        [
            "--include-package-data=pyxel_ui",
            "--include-package-data=backend",
            "--include-package-data=server",
            "--include-data-dir=pyxel_ui/assets/Press_Start_2P=pyxel_ui/assets/Press_Start_2P",
            "--include-data-files=my_resource.pyxres=my_resource.pyxres",
        ]
    )

    # Additional compilation options
    nuitka_command.extend(
        [
            "--show-progress",
            "--show-memory",
        ]
    )

    # Add main script
    nuitka_command.append(main_script)

    print("Running Nuitka with command:")
    print(" ".join(nuitka_command))

    print("\nStarting Nuitka compilation...")
    result = run(nuitka_command)

    if result.returncode == 0:
        print("Compilation completed successfully!")
        print("Your executable can be found in the 'banana' directory")
    else:
        print("Compilation failed with error code:", result.returncode)


if __name__ == "__main__":
    create_build_script()
