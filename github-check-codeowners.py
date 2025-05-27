#!/bin/env python3

# SPDX-License-Identifier: WTFPL OR 0BSD OR EUPL-1.2
# Created by Mark Janssen / Sig-I/O with some AI assistance

import re
import os
import sys
import argparse
from github import Github

# === Configuration ===
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # Token with REPO:Admin permissions
ORG_NAME = "YOUR_ORG_NAME"  # Organisation to check
verbose = True;

# === Initialization ===
if not GITHUB_TOKEN:
    print("❌ GH_TOKEN environment variable not set.")
    sys.exit(1)

g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)

CODEOWNERS_PATHS = [
    ".github/CODEOWNERS",
    "CODEOWNERS",
    "docs/CODEOWNERS"
]

CODEOWNERS_LINE_REGEX = re.compile(r"^(\S+)\s+(.+)$")

# === Functions ===

def get_codeowners_file(repo):
    for path in CODEOWNERS_PATHS:
        try:
            contents = repo.get_contents(path)
            return contents.decoded_content.decode("utf-8")
        except:
            continue
    return None

def parse_codeowners(content):
    rules = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = CODEOWNERS_LINE_REGEX.match(line)
        if match:
            path, owners = match.groups()
            owners = owners.split()
            rules.append((path, owners))
    return rules

def has_write_access(repo, owner):
    if owner.startswith("@"):
        owner = owner[1:]

    if "/" in owner:
        team_slug = owner.split("/")[-1].lower()
        try:
            for team in repo.get_teams():
                if team.slug.lower() == team_slug:
                    return team.permission in ["admin", "push"]
        except Exception as e:
            print(f"    ⚠️ Error checking team '{team_slug}': {e}")
        return False
    else:
        try:
            permission = repo.get_collaborator_permission(owner)
            return permission in ["write", "admin"]
        except:
            return False

def check_repo_codeowners(repo):
    if repo.archived and verbose:
        print(f"⏭️  Skipping archived repo: {repo.full_name}")
        return

    if verbose:
        print(f"🔍 Checking repository: {repo.full_name}") 
    content = get_codeowners_file(repo)
    if not content:
        print(f"  ❌ CODEOWNERS file not found for {repo.full_name}.")
        return

    rules = parse_codeowners(content)
    for path, owners in rules:
        for owner in owners:
            if not has_write_access(repo, owner):
                print(f"  ⚠️  {owner} does NOT have write access for {repo.full_name}/{path}")

# === Main ===

def main():
    global verbose
    parser = argparse.ArgumentParser(description="Check CODEOWNERS status in GitHub repositories.")
    parser.add_argument("--repo", help="Specify a single repository to check (format: org/repo)")
    parser.add_argument("-q", "--quiet", help="Only print findings", action="store_true")
    args = parser.parse_args()

    if args.quiet:
        verbose = False

    if args.repo:
        try:
            repo = g.get_repo(args.repo)
            check_repo_codeowners(repo)
        except Exception as e:
            print(f"❌ Could not load repository {args.repo}: {e}")
    else:
        if verbose:
            print(f"📦 Checking all repositories in organization '{ORG_NAME}'...")
        for repo in org.get_repos():
            check_repo_codeowners(repo)

if __name__ == "__main__":
    main()

