# Chan project instructions

## Branch policy

Active development is on main following owner-approved consolidation on
2026-10-22. Old branches are preserved by archive tags; see docs/BRANCH_ARCHIVE.md.
Main remains experimental. Merging or pushing to main does not authorize a release.

## Read first and handoff discipline

This file applies to the nested repository. The workspace parent contains only
an entry-point AGENTS.md; source control is here, not in the parent directory.

1. Read docs/CURRENT_STATE.md before acting; it is the current status authority.
2. Read docs/BUFFERED_AUDIO_LAB.md for the active test and docs/EXPERIMENT_HISTORY.md
   to avoid repeating failed experiments. docs/REFERENCE_INDEX.md lists donors/pins.
3. Read docs/DEVELOPMENT.md for workspace/toolchain issues and docs/VALIDATION.md
   for detailed evidence. Historical “next test” paragraphs are not current orders.

As of 2026-10-23 the active YAML is firmware/stackchan-audio-lab-buffered.example.yaml.
Log41 hardware results: playback timing passed (7.098s for7s), but residual mic
clipping and low quiet processed speech remain. See docs/LAB41_ANALYSIS.md.
Next proposed experiment separates ADC headroom and AFE/AGC; not implemented yet.
Do not start an older experiment or claim reliable live interruption is solved.

After new evidence or a delivery, update CURRENT_STATE and VALIDATION together;
maintain the firmware catalog and current protocol when status changes. Separate
owner reports, measurements, source inference and compile-only validation. Do not
rewrite historical failures as successes or leave multiple “current” candidates.
Preserve raw evidence privately, cite filenames, and never commit owner recordings.

## Current direction

The current conversation supersedes the previous Assist-first design.
Target the official M5Stack StackChan AI Desktop Robot with ESPHome.
Prioritize Gemini Live through kyvaith/pipecat-homeassistant.
The immediate milestone is full-duplex audio, echo control, and voice interruption;
see docs/CURRENT_STATE.md. FULL_DUPLEX_POC.md retains historical design and
acceptance criteria. Defer faces, gestures and other product features.
HA Assist is a later separate mode. A custom Chan HA integration is not currently
required; do not rebuild the removed integration without a demonstrated need.

Intended modes: sleep, Pipecat conversation, HA Assist. Future work includes
faces, touch reactions, bounded gestures, Frigate tracking/identity, and
server-side personal prompts with a guest fallback. These are requirements, not
implemented capabilities. Coordinator placement remains to be decided when needed.

## Engineering

- Read docs/VALIDATION.md before changing hardware or audio.
- Preserve the demonstrated official BSP baseline.
- Do not change GPIOs, power rails, or codecs without source evidence.
- Prove Pipecat input/output and repeated start/stop on hardware before adding
  behavior. Compilation is not a successful device test.
- Account for shared audio resources and sample rates; prevent competing playback.
- Voice interruption requires measured echo control and buffer cancellation.
- User volume must remain a comfort control, not an AEC calibration step.
  Validate echo suppression across the supported audible volume range and during
  volume changes. Do not present low playback volume as the product solution.
- Resolve the Y-angle mismatch before motion; enforce calibrated limits and use
  one owner to arbitrate tracking and gestures.
- Frigate identity does not establish the speaker or grant HA permissions.
- Keep credentials, personal profiles, and memory server-side and out of Git.
- Pin BSP, external drivers, and voice components for releases.
- Preserve license notices, Git history and historical tags. The owner explicitly
  requested withdrawing public releases on 2026-10-22: keep old releases as drafts
  with their assets preserved; do not republish them without owner direction.
- No new release until physical validation; record exact tested versions.

## Communication

Use Ukrainian with the owner and English for identifiers, documentation, and
commits. Keep scope incremental. Distinguish observations from assumptions.
Deliver new device configurations as one copy-paste YAML with remote dependencies;
do not require local includes, file uploads, or manual component installation.

Do not require exact user timing for lab speech. Say: count roughly two seconds,
speak one short sentence, wait for END without Stop. A tail beyond second seven
is simply omitted from Lab 2 playback; no stopwatch is needed.
