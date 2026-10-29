# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement


@pytest.mark.parametrize("package", ["data-designer-config", "data-designer-engine", "data-designer"])
def test_package_pyarrow_requirement_matches_workspace_security_floor(package: str) -> None:
    root = Path(__file__).resolve().parents[3]
    metadata = tomllib.loads((root / "packages" / package / "pyproject.toml").read_text())
    project = metadata["project"]
    if "dependencies" in project.get("dynamic", []):
        dependencies = metadata["tool"]["hatch"]["metadata"]["hooks"]["uv-dynamic-versioning"]["dependencies"]
    else:
        dependencies = project["dependencies"]
    # Other dynamic requirements contain version templates rendered by Hatch.
    # Inspect only Arrow; its requirement has no version template.
    arrow = [Requirement(value) for value in dependencies if value.startswith("pyarrow")]
    assert len(arrow) == 1
    assert "24.0.0" not in arrow[0].specifier
    assert "25.0.0" not in arrow[0].specifier
    assert "25.0.1" in arrow[0].specifier
    assert "26.0.0" not in arrow[0].specifier
    lock = tomllib.loads((root / "uv.lock").read_text())
    versions = [entry["version"] for entry in lock["package"] if entry["name"] == "pyarrow"]
    assert versions and all(version in arrow[0].specifier for version in versions)
