# Results

`raw/` is ignored because provider responses may contain sensitive text. Reproducible exports
belong in `processed/`; charts belong in `charts/`. Filenames should include the run ID.

Every artifact must identify its provider as `demo`, `live`, or `fixture`; its metric source as
`automatic`, `manual`, or `optional_llm_judge`; and its dataset/prompt/schema versions.

The absence of a manual score means **not reviewed**, never zero.
