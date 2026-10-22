# Branch archive — 2026-10-22

Owner approved consolidating current development into main and removing old
branches after preserving their unique commits. Annotated tags were pushed and
verified against the remote before merging or deleting any branch. Main is still
experimental; no GitHub Release was created from these archive tags.

| Former branch | Archive tag | Preserved commit |
| --- | --- | --- |
| `codex/initial-test-version` | `archive/2026-10-22/initial-test-version` | `1d43e149690777109e6e963e01e36135f752e72e` |
| `codex/esphome-hacs-installation` | `archive/2026-10-22/esphome-hacs-installation` | `947245cd4d2baf5a28736587874a21ec30606b94` |
| `codex/official-stackchan-base` | `archive/2026-10-22/official-stackchan-base` | `f2758806bc2f8c6bcd92a455957266d7278e48af` |
| `codex/full-duplex-poc` | `archive/2026-10-22/full-duplex-poc` | `0e4a9f836f0f0676b72ff965bcd60b3737c1c833` |
| `main` | `archive/2026-10-22/main-before-consolidation` | `2e82c51e36e979d564ce17aea60b71ee090299d6` |

The main-before-consolidation tag preserves the earlier main snapshot; main
itself remains the active branch. The three old feature branches had unique
commits and are preserved via these tags rather than merged into current code.
The full-duplex branch was merged into main with its complete history.

To inspect a snapshot, use git show with its tag. Create a recovery branch from
that tag only if needed; do not overwrite or delete archive tags during cleanup.
Archive source availability does not imply compatibility with current ESPHome.
