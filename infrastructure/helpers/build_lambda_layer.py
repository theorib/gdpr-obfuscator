import os
import subprocess
from typing import List


def generate_lambda_dependency_requirements(
    project_root: str,
) -> List[str]:
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
                "--directory",
                project_root,
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


def build_lambda_dependencies_layer(
    dependencies: List[str],
    project_root: str,
    target_dir: str = "build/layers/deps/python",
):
    """Build dependencies for the Lambda layer.

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
                "--directory",
                project_root,
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


def build_lambda_gdpr_obfuscator_layer(
    project_root: str,
    target_dir: str = "build/layers/gdpr_obfuscator/python",
):
    """Build the GDPR Obfuscator Lambda layer.

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
                "--directory",
                project_root,
                "--target",
                target_dir,
                ".",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")


def build_lambda_dependency_requirements(
    project_root: str,
    lambda_layer_deps_target_dir: str,
    lambda_layer_gdpr_obfuscator_target_dir: str,
):
    requirements = generate_lambda_dependency_requirements(project_root)

    build_lambda_dependencies_layer(
        requirements, project_root=project_root, target_dir=lambda_layer_deps_target_dir
    )
    build_lambda_gdpr_obfuscator_layer(
        project_root=project_root, target_dir=lambda_layer_gdpr_obfuscator_target_dir
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python build_lambda_layer.py <project_root> <deps_target_dir> <gdpr_obfuscator_target_dir>")
        sys.exit(1)

    project_root = sys.argv[1]
    deps_target_dir = sys.argv[2]
    gdpr_obfuscator_target_dir = sys.argv[3]

    build_lambda_dependency_requirements(
        project_root,
        deps_target_dir,
        gdpr_obfuscator_target_dir,
    )
