# ABOUTME: Checks that the pending release notes name every releasable commit since the
# ABOUTME: last release, so a changelog entry Release Please drops fails the build loudly.

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


RELEASE_BRANCH = "release-please--branches--main"
CONFIG_PATH = Path(".release-please-config.json")
CHANGELOG_PATH = "CHANGELOG.md"

# Release Please's own release commits describe the release being prepared, not a
# change in it, so they never appear in the notes they generate.
RELEASE_COMMIT = re.compile(r"^chore(\([^)]*\))?!?: release ")

REMEDY = """
Release Please silently drops a commit whose message its conventional-commits
parser cannot read, and the run still succeeds. The usual trigger is a body line
that starts with a bare word followed by '(' whose parentheses do not close as a
simple scope, which squash-merged pull request bodies containing code hit easily
(conventional-commits/parser#54, googleapis/release-please#2878).

To recover a dropped commit, edit the body of its merged pull request and add:

    BEGIN_COMMIT_OVERRIDE
    <type>: <subject>
    END_COMMIT_OVERRIDE

Release Please parses that block instead of the squash commit message on its next
run, and rebuilds the release pull request from it. Editing CHANGELOG.md on the
release branch is not enough: the release notes come from the pull request body,
and Release Please force-pushes that branch on every push to main.

To avoid the trigger in the first place, indent the offending body line by one
space so it no longer starts at column one.
"""


def run(*args: str) -> str:
    return subprocess.run(  # noqa: S603
        args, capture_output=True, text=True, check=True
    ).stdout


def git(*args: str) -> str:
    return run("git", *args)


def gh(*args: str) -> str:
    return run("gh", *args)


def changelog_types() -> set[str]:
    """The commit types Release Please renders into the changelog."""
    config = json.loads(CONFIG_PATH.read_text())
    sections = config["packages"]["."]["changelog-sections"]
    return {section["type"] for section in sections if not section.get("hidden")}


def releasable_commits(base: str, head: str, types: set[str]) -> list[tuple[str, str]]:
    subject_pattern = re.compile(rf"^({'|'.join(sorted(types))})(\([^)]*\))?!?: ")
    log = git("log", "--first-parent", "--format=%H%x1f%s", f"{base}..{head}")
    commits: list[tuple[str, str]] = []
    for line in log.splitlines():
        if not line:
            continue
        sha, subject = line.split("\x1f", 1)
        if RELEASE_COMMIT.match(subject) or not subject_pattern.match(subject):
            continue
        commits.append((sha, subject))
    return commits


def pending_notes() -> list[tuple[str, str]]:
    """The release pull request's body and changelog, labelled for reporting."""
    pulls = json.loads(
        gh(
            "pr",
            "list",
            "--head",
            RELEASE_BRANCH,
            "--state",
            "open",
            "--json",
            "number,body",
            "--limit",
            "1",
        )
    )
    if not pulls:
        return []
    number = pulls[0]["number"]
    changelog = gh(
        "api",
        "-H",
        "Accept: application/vnd.github.raw",
        f"repos/{{owner}}/{{repo}}/contents/{CHANGELOG_PATH}?ref={RELEASE_BRANCH}",
    )
    return [
        (f"the body of release pull request #{number}", pulls[0]["body"] or ""),
        (f"{CHANGELOG_PATH} on {RELEASE_BRANCH}", changelog),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pending release notes name every releasable"
        " commit since the last release."
    )
    parser.add_argument("--base", help="last released ref (default: the newest tag)")
    parser.add_argument(
        "--head", default="HEAD", help="ref to check up to (default: HEAD)"
    )
    parser.add_argument(
        "--notes",
        action="append",
        type=Path,
        metavar="FILE",
        help="check these files instead of the open release pull request",
    )
    args = parser.parse_args()

    base = args.base or git("describe", "--tags", "--abbrev=0", args.head).strip()
    commits = releasable_commits(base, args.head, changelog_types())
    if not commits:
        print(f"No releasable commits in {base}..{args.head}; nothing to check.")
        return 0

    print(f"{len(commits)} releasable commit(s) in {base}..{args.head}")

    if args.notes:
        notes = [(str(path), path.read_text()) for path in args.notes]
    else:
        notes = pending_notes()
        if not notes:
            print(
                f"\nFAIL: {len(commits)} releasable commit(s) since {base}, but no open"
                f" release pull request on {RELEASE_BRANCH} describes them.",
                file=sys.stderr,
            )
            print(REMEDY, file=sys.stderr)
            return 1

    failed = False
    for label, text in notes:
        missing = [(sha, subject) for sha, subject in commits if sha not in text]
        if not missing:
            print(f"OK: {label} names all of them.")
            continue
        failed = True
        print(f"\nFAIL: {label} is missing {len(missing)} commit(s):", file=sys.stderr)
        for sha, subject in missing:
            print(f"  {sha[:8]} {subject}", file=sys.stderr)

    if failed:
        print(REMEDY, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
