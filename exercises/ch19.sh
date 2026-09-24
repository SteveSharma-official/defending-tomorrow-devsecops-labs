#!/usr/bin/env bash
# Defending Tomorrow — Chapter 19: Security Testing at Scale
# AWS and Azure in Practice exercise (§19.11). Run the AWS block in AWS CloudShell and the
# Azure block in Azure Cloud Shell (Bash). Do not run this file as one script: copy each block
# into the shell for its platform, read the output, then run the cleanup lines.
# Prerequisite: ~/dt-env.sh from exercises/ch00.sh. Costs and cleanup are described in the book.

# --- Run the same commands in AWS CloudShell and in Azure Cloud Shell ---
git clone --depth 1 https://github.com/SteveSharma-official/defending-tomorrow-devsecops-labs.git
cd defending-tomorrow-devsecops-labs/chapter-19/lab-05-sast-codeql-semgrep/starter
python3 -m pip install --user --quiet semgrep
~/.local/bin/semgrep --test --config .semgrep/dt-sql-injection.yml \
  .semgrep/tests/dt-sql-injection.py --metrics=off
cd ~ && rm -rf defending-tomorrow-devsecops-labs   # cleanup
