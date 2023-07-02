import os
import subprocess


def run_pyinstaller():
    """Builds the snake.exe relative_path using pyinstaller"""
    parent_path = os.path.dirname(os.path.dirname(__file__))
    script_path = os.path.join(parent_path, "snake", "main.py")
    dist_path = parent_path
    spec_path = os.path.join(parent_path, "scripts", "pyinstaller_work")
    work_path = os.path.join(spec_path, "build")
    assets_path = os.path.join(parent_path, "assets")
    out_assets_path = os.path.join("pyinstaller_work", "assets")
    data_path = f"{assets_path};{out_assets_path}"
    icon_path = os.path.join(parent_path, "assets", "images", "icon.ico")
    command = [
        "pyinstaller",
        script_path,
        "--noconsole",
        "--onefile",
        "--add-data", data_path,
        "-n", "snake",
        "--icon", icon_path,
        "--distpath", dist_path,
        "--specpath", spec_path,
        "--workpath", work_path
    ]

    subprocess.run(command, check=True)


if __name__ == "__main__":
    run_pyinstaller()
