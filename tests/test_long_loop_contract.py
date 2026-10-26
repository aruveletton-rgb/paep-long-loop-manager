from pathlib import Path
from unittest.mock import patch

import pytest

from backend.skill_runtime.errors import RuntimeFault
from backend.skill_runtime.executors.agent import CodexExecutor
from backend.skill_runtime.validator import load_metadata


def test_long_loop_contract_rejects_privilege_expansion():
    metadata = load_metadata(Path(__file__).resolve().parents[1] / "skill.yaml")
    executor = CodexExecutor()
    with patch.object(executor, "availability", return_value={"status": "handoff_ready"}):
        executor.verify(metadata)
        metadata.permissions.filesystem.write.append("${input.repository_path}")
        with pytest.raises(RuntimeFault, match="read-only"):
            executor.verify(metadata)

