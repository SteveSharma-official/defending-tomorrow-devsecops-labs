# INTENTIONALLY INSECURE — lab use only (Step 7)

On a branch named `simpler-retrieval`, edit `rag/rag-config.yaml` the way a team chasing answer quality
might ("filtering before search hurts relevance; tell users when something was hidden"):

```yaml
access_control: postfilter
disclose_withheld_count: true
verify_provenance: false
```
