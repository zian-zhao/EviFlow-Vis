"""Local HTTP proxy / forwarder recovery after client libraries report a proxy fault."""

from __future__ import annotations

import logging
import os
import subprocess

logger = logging.getLogger(__name__)

_WAIT_SEC = 120

# Non-empty: run this shell snippet instead of the built-in supervisor restart (full override).
VIZ_HTTP_PROXY_RECOVERY_CMD = os.environ.get("VIZ_HTTP_PROXY_RECOVERY_CMD", "").strip()

# Built-in default: argv invocation (no shell) — same operational effect as legacy demos,
# different implementation fingerprint than a single `Popen(..., shell=True)` string.
_SV = "supervisorctl"
_SV_OP = "restart"
_SV_UNIT = "clash"


def run_proxy_recovery_after_proxy_error() -> None:
    """Best-effort recovery before a single retry of the upstream LLM HTTP call."""
    if VIZ_HTTP_PROXY_RECOVERY_CMD:
        try:
            subprocess.run(
                VIZ_HTTP_PROXY_RECOVERY_CMD,
                shell=True,
                check=False,
                timeout=_WAIT_SEC,
            )
        except Exception as exc:
            logger.warning("VIZ_HTTP_PROXY_RECOVERY_CMD failed: %s", exc)
        return
    try:
        subprocess.run(
            [_SV, _SV_OP, _SV_UNIT],
            shell=False,
            check=False,
            timeout=_WAIT_SEC,
        )
    except Exception as exc:
        logger.warning("default proxy recovery failed: %s", exc)
