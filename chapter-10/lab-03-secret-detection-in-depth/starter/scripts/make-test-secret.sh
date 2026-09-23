#!/usr/bin/env bash
# make-test-secret.sh — writes a SYNTHETIC, randomly generated credential-shaped string
# for secret-scanning labs (LAB-03, CAPSTONE).
#
# Why random and generated at runtime?
#   * The repository itself never stores a credential-shaped literal.
#   * The AWS documentation example key (AKIAIOSFODNN7EXAMPLE) is deliberately
#     allow-listed by common scanners, so it does NOT trigger detection (verified
#     with gitleaks 8.28.0 on 23 Sep 2026). A random value in the same format does.
# The value is NOT a real credential, is not paired with any account and grants access to nothing.
#
# Usage: ./make-test-secret.sh [output-file]   (default: config/test-credentials.env)
set -euo pipefail
OUT="${1:-config/test-credentials.env}"
mkdir -p "$(dirname "$OUT")"
rand() { ( set +o pipefail; LC_ALL=C tr -dc "$1" < /dev/urandom | head -c "$2" ); }
KEY_ID="AKIA$(rand 'A-Z2-7' 16)"
SECRET="$(rand 'A-Za-z0-9/+' 40)"
{
  echo "# SYNTHETIC TEST VALUE — intentionally insecure, generated for a Defending Tomorrow lab."
  echo "# Not a real credential. Delete this file when the lab is complete."
  echo "aws_access_key_id=${KEY_ID}"
  echo "aws_secret_access_key=${SECRET}"
} > "$OUT"
echo "Wrote synthetic test credential to ${OUT}"
