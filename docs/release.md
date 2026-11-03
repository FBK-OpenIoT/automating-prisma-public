# Release preparation

Abstracts and historical outputs are deliberately retained. Review data rights
separately before changing repository visibility.

Run `uv run pytest`, `uv run python scripts/check_release.py`, and `uv build`.
The checker scans tracked/staged files and locally reachable Git blobs for
full-text artifacts and common credential formats. It does not certify arbitrary
embedded prose, all possible secrets, abstract licenses, or remote pull-request
references and forks.

The original history contained `vectorstore_claude/pdf_index/index.pkl` and
`index.faiss`. Deleting current files alone cannot remove that history. A private
recovery bundle is kept outside the repository during cleanup. Never publish it
or merge its old history into the cleaned branch.

The rewritten local history must be propagated to the remote before publication.
A normal push rejects divergent history. Coordinate forced updates with
collaborators and inspect other branches, tags, pull-request references, and
clones. See [GitHub's guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).
Local checks cannot purge copies held elsewhere.
