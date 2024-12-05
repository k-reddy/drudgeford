import sys
from subprocess import run


def create_build_script():
    # Ensure we're using Python's executable for the compilation
    python_exe = sys.executable

    main_script = "frontend_main.py"

    # List of modules to include
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
    ]

    # Base Nuitka command
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

    # Additional options for better compilation
    nuitka_command.extend(
        [
            "--show-progress",
            "--show-memory",
            "--enable-console",
        ]
    )

    # Add the main script at the end
    nuitka_command.append(main_script)

    # Print the command for debugging
    print("Running Nuitka with command:")
    print(" ".join(nuitka_command))

    # Run the compilation
    print("\nStarting Nuitka compilation...")
    result = run(nuitka_command)

    if result.returncode == 0:
        print("Compilation completed successfully!")
        print("Your executable can be found in the 'banana' directory")
    else:
        print("Compilation failed with error code:", result.returncode)


if __name__ == "__main__":
    create_build_script()
