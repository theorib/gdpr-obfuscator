import os
import subprocess
import zipfile
from pathlib import Path
from typing import List


def generate_lambda_dependency_requirements() -> List[str]:
    """Generate a list of dependencies for the Lambda layer, excluding AWS runtime dependencies.

    Returns:
        List[str]: List of dependencies for the Lambda layer.
    """
    try:
        aws_runtime_dependencies = [
            "#",
            ".",
            "boto3",
            "botocore",
            "jmespath",
            "python-dateutil",
            "s3transfer",
            "six",
            "urllib3",
        ]

        result = subprocess.run(
            [
                "uv",
                "export",
                "--frozen",
                "--no-dev",
                "--no-editable",
                "--no-hashes",
                "--format",
                "requirements.txt",
                "--no-annotate",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        raw_requirements = result.stdout

        filtered_requirements = filter(
            lambda item: not any(
                item.startswith(dependency) for dependency in aws_runtime_dependencies
            ),
            raw_requirements.splitlines(),
        )

        requirements = list(filtered_requirements)

        return requirements

    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return []
    except FileNotFoundError:
        print("uv command not found - is it installed?")
        return []


def install_lambda_layer_dependencies(
    dependencies: List[str], target_dir: str = "build/layers/deps/python"
):
    """Install dependencies for the Lambda layer.

    Args:
        dependencies (List[str]): _description_
        target_dir (str, optional): _description_. Defaults to "build/layers/deps/python".
    """
    try:
        os.makedirs(target_dir, exist_ok=True)
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--no-deps",
                "--no-installer-metadata",
                "--no-compile-bytecode",
                "--python-platform",
                "x86_64-manylinux2014",
                "--python",
                "3.13",
                "--target",
                target_dir,
                *dependencies,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")


def install_lambda_layer_gdpr_obfuscator(
    target_dir: str = "build/layers/gdpr_obfuscator/python",
):
    """Install the GDPR Obfuscator Lambda layer.

    Args:
        target_dir (str, optional): Target directory for the GDPR Obfuscator Lambda layer. Defaults to "build/layers/gdpr_obfuscator/python".
    """
    try:
        os.makedirs(target_dir, exist_ok=True)
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--no-deps",
                "--no-compile-bytecode",
                "--no-installer-metadata",
                "--target",
                target_dir,
                ".",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")


def zip_directory(source_dir: str, target_dir: str):
    """Create a reproducible ZIP archive with consistent timestamps to mantain checksum integrity between generations"""
    try:
        zip_path = f"{target_dir}.zip"
        source_path = Path(source_dir)

        fixed_timestamp = (2024, 1, 1, 0, 0, 0)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk directory and add files in sorted order for determinism
            for file_path in sorted(source_path.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)

                    # Create ZipInfo with fixed timestamp
                    zinfo = zipfile.ZipInfo(str(arcname))
                    zinfo.date_time = fixed_timestamp
                    zinfo.compress_type = zipfile.ZIP_DEFLATED

                    # Set file permissions (0644 for files)
                    zinfo.external_attr = 0o644 << 16

                    with file_path.open("rb") as f:
                        zipf.writestr(zinfo, f.read())

    except Exception as e:
        print(f"Error zipping directory: {e}")


def get_lambda_dependency_requirements():
    requirements = generate_lambda_dependency_requirements()

    install_lambda_layer_dependencies(
        requirements, target_dir="build/layers/deps/python"
    )
    install_lambda_layer_gdpr_obfuscator(
        target_dir="build/layers/gdpr_obfuscator/python"
    )

    zip_directory("build/layers/deps", "dist/gdpr_obfuscator_layer_deps")
    zip_directory("build/layers/gdpr_obfuscator", "dist/gdpr_obfuscator_layer")


if __name__ == "__main__":
    get_lambda_dependency_requirements()
