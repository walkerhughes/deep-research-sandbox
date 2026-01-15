#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic models.

This script generates TypeScript type definitions from the shared_types Pydantic models
to ensure type consistency between the Python backend and TypeScript frontend.

Usage:
    python scripts/generate_types.py [--output PATH]

Requirements:
    pip install pydantic-to-typescript

The generated types will be placed in packages/shared/typescript/src/generated.ts
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    try:
        import pydantic2ts  # noqa: F401
        return True
    except ImportError:
        return False


def install_dependencies() -> None:
    """Install required dependencies."""
    print("Installing pydantic-to-typescript...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pydantic-to-typescript"],
        check=True,
    )


def generate_types(output_path: Path) -> None:
    """Generate TypeScript types from Pydantic models."""
    from pydantic2ts import generate_typescript_defs

    # Add the shared_types package to the path
    shared_types_path = Path(__file__).parent.parent / "packages" / "shared" / "python"
    sys.path.insert(0, str(shared_types_path))

    print(f"Generating TypeScript types to {output_path}...")

    # Generate from the shared_types module
    generate_typescript_defs(
        "shared_types",
        str(output_path),
        exclude=("BaseModel",),
    )

    print(f"TypeScript types generated successfully at {output_path}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TypeScript types from Pydantic models"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(__file__).parent.parent
        / "packages"
        / "shared"
        / "typescript"
        / "src"
        / "generated.ts",
        help="Output path for generated TypeScript file",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies if not present",
    )

    args = parser.parse_args()

    if not check_dependencies():
        if args.install:
            install_dependencies()
        else:
            print(
                "Error: pydantic-to-typescript is not installed.\n"
                "Run with --install flag or: pip install pydantic-to-typescript",
                file=sys.stderr,
            )
            sys.exit(1)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    generate_types(args.output)


if __name__ == "__main__":
    main()
