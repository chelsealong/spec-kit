"""Regression tests for concurrent create-new-feature invocations.

See https://github.com/github/spec-kit/issues/4270: sequential numbering
scans, picks max+1, and used to create the feature directory with a
non-exclusive `mkdir -p` (or its `exist_ok=True`/`-Force` twins). Two
invocations racing for the same number could both pass the scan and both
"succeed", with the second silently overwriting the first's spec.md.
"""

from __future__ import annotations

import concurrent.futures
from pathlib import Path

import pytest

from tests.conftest import requires_bash
from tests.parity_helpers import (
    HAS_POWERSHELL,
    bash_cmd,
    install_scripts,
    make_repo,
    ps_cmd,
    py_cmd,
    run,
)

SCRIPT = "create-new-feature"
TEMPLATE_BODY = "# Spec Template\n\nBody.\n"
WORKERS = 5


def _setup_repo(tmp_path: Path, name: str) -> Path:
    repo = make_repo(tmp_path, name)
    install_scripts(repo, SCRIPT)
    templates = repo / ".specify" / "templates"
    templates.mkdir(parents=True)
    (templates / "spec-template.md").write_text(TEMPLATE_BODY, encoding="utf-8")
    return repo


def _assert_no_lost_writes(repo: Path, results: list) -> None:
    successes = [r for r in results if r.returncode == 0]
    specs_dir = repo / "specs"
    created = sorted(p for p in specs_dir.iterdir() if p.is_dir())

    # Every successful invocation must have reserved its own directory.
    # Before the fix, two racing invocations could both "succeed" while
    # sharing (and one overwriting the other's) directory.
    assert len(created) == len(successes), (
        f"{len(successes)} invocations reported success but only "
        f"{len(created)} feature directories exist: {[p.name for p in created]}"
    )
    for feature_dir in created:
        spec_file = feature_dir / "spec.md"
        assert spec_file.is_file(), f"{feature_dir} is missing spec.md"
        assert spec_file.read_text(encoding="utf-8") == TEMPLATE_BODY


@requires_bash
def test_bash_concurrent_invocations_do_not_clobber_each_other(
    tmp_path: Path,
) -> None:
    repo = _setup_repo(tmp_path, "bash")

    def launch():
        return run(
            bash_cmd(repo, SCRIPT, "--short-name", "race", "race condition test"),
            repo,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(lambda _: launch(), range(WORKERS)))

    _assert_no_lost_writes(repo, results)


def test_python_concurrent_invocations_do_not_clobber_each_other(
    tmp_path: Path,
) -> None:
    repo = _setup_repo(tmp_path, "python")

    def launch():
        return run(
            py_cmd(repo, SCRIPT, "--short-name", "race", "race condition test"),
            repo,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(lambda _: launch(), range(WORKERS)))

    _assert_no_lost_writes(repo, results)


@pytest.mark.skipif(not HAS_POWERSHELL, reason="no PowerShell available")
def test_powershell_concurrent_invocations_do_not_clobber_each_other(
    tmp_path: Path,
) -> None:
    repo = _setup_repo(tmp_path, "powershell")

    def launch():
        return run(
            ps_cmd(repo, SCRIPT, "-ShortName", "race", "race condition test"),
            repo,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(lambda _: launch(), range(WORKERS)))

    _assert_no_lost_writes(repo, results)
