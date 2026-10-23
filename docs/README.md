# Documentation map

Read order for a new chat: repository AGENTS.md → CURRENT_STATE.md → the current
protocol. Do not choose firmware by its modification date or an old “next test”
paragraph. CURRENT_STATE is the current decision record; VALIDATION is a timeline.

| Document | Role |
| --- | --- |
| [CURRENT_STATE](CURRENT_STATE.md) | Active artifact, evidence, constraints, immediate next action |
| [HEADROOM_AUDIO_LAB](HEADROOM_AUDIO_LAB.md) | Current12dB and pre/post-AGC test procedure |
| [BUFFERED_AUDIO_LAB](BUFFERED_AUDIO_LAB.md) | Previous log41 baseline design/procedure |
| [LAB41_ANALYSIS](LAB41_ANALYSIS.md) | Latest hardware measurements and proposed next experiment |
| [EXPERIMENT_HISTORY](EXPERIMENT_HISTORY.md) | What was tried, result and retained firmware |
| [REFERENCE_INDEX](REFERENCE_INDEX.md) | Source donors, exact pins, lessons and limits |
| [BRANCH_ARCHIVE](BRANCH_ARCHIVE.md) | Retired branches, exact archive tags and recovery context |
| [DEVELOPMENT](DEVELOPMENT.md) | Workspace layout, build commands, Windows issues, publishing |
| [VALIDATION](VALIDATION.md) | Detailed chronological evidence; later observations supersede earlier pending notes |
| [ES7210_GAIN_AUDIT](ES7210_GAIN_AUDIT.md) | Gain comparison and initial low-level recordings; 36 dB is not current recommendation |
| [AUDIO_REFERENCE_RESEARCH](AUDIO_REFERENCE_RESEARCH.md) | Stock comparison, schematic reference routing and clock investigation |
| [NATIVE_16K](NATIVE_16K.md) | Rate-conversion decision and original 36 dB candidates |
| [AFE_PROFILING](AFE_PROFILING.md) | CPU/callback metric definitions and core-balance experiment |
| [AFE_PORT](AFE_PORT.md) | Original Waveshare AFE port; historical configuration |
| [AUDIO_LAB](AUDIO_LAB.md) | Original 48 kHz lab and capture internals; historical protocol |
| [FULL_DUPLEX_POC](FULL_DUPLEX_POC.md) | Initial design and eventual acceptance criteria; initial software-reference plan superseded |
| [DUPLEX_TEST](DUPLEX_TEST.md) | Earliest raw/standalone-AEC tests; historical protocol |

On a new result, update CURRENT_STATE and the evidence ledger together. Update
the history/status catalog when a candidate is tested or superseded. Keep raw
recordings/logs outside Git and cite their filenames in the relevant entry.
