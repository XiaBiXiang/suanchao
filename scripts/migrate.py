"""
Alembic 迁移命令包装脚本

示例:
    python scripts/migrate.py upgrade head
    python scripts/migrate.py downgrade -1
    python scripts/migrate.py current
    python scripts/migrate.py history
    python scripts/migrate.py stamp 20260309_0001
"""

from __future__ import annotations

import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config


def build_alembic_config() -> Config:
    project_root = Path(__file__).resolve().parent.parent
    config = Config(str(project_root / "alembic.ini"))
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alembic migration commands.")
    parser.add_argument(
        "action",
        choices=["upgrade", "downgrade", "current", "history", "stamp"],
        help="Alembic action to run.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Revision target (e.g. head, -1, base, 20260309_0001).",
    )

    args = parser.parse_args()
    config = build_alembic_config()

    if args.action == "upgrade":
        command.upgrade(config, args.target or "head")
        return
    if args.action == "downgrade":
        command.downgrade(config, args.target or "-1")
        return
    if args.action == "stamp":
        command.stamp(config, args.target or "head")
        return
    if args.action == "current":
        command.current(config)
        return
    if args.action == "history":
        command.history(config)
        return

    raise ValueError(f"Unsupported action: {args.action}")


if __name__ == "__main__":
    main()
