# INTENTIONALLY INSECURE — lab use only (Step 7)

Two separate attacks on the model supply chain:

**A. Tampering in transit (after signing).** Run **Actions → model-supply-chain → Run workflow** on `main`
with **simulate_tamper** ticked. The deploy job alters `model.json` after it was signed — as a compromised
artifact store or registry would.

**B. Training-data poisoning (before signing).** On a branch named `data-refresh`, replace
`data/phishing-urls.csv` with `lab-changes/phishing-urls-poisoned.csv` (29 phishing rows relabelled as
benign — the "refreshed" dataset an attacker slipped into the data pipeline). Push and open a PR.
