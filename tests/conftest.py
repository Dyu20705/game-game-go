"""Test fixtures that keep temporary files inside the writable workspace."""

from pathlib import Path
import re
import shutil

import pytest


@pytest.fixture
def tmp_path(request):
    """Workspace-local replacement for pytest's temp fixture in restricted sandboxes."""

    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    path = Path.cwd() / ".test_tmp" / safe_name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    yield path
    if path.exists():
        shutil.rmtree(path)

