# Workspace, building and publication

## Workspace identity

On the owner's Windows machine:

- Workspace: `C:/My Projects/Codex/Chan - Stackchan HA companion`
- Git checkout: workspace + `/repository`
- Remote: https://github.com/alexeyzel/chan-home-assistant
- Working branch: `codex/full-duplex-poc`
- Prior app cwd `C:/Users/Alexe/OneDrive/Documents/ChatGPT/chan-stackchan` is stale.
  Always check explicit working directory; it previously caused process creation
  failure. The outer workspace has a local AGENTS.md pointer to the nested repo.

Adjacent reference checkouts: upstream-stock, upstream-m5stack, upstream-dravix,
upstream-audio-stack, upstream-pipecat; pinned source URLs are in REFERENCE_INDEX.
Inspect actual git revisions before treating those checkout contents as evidence.
Do not clean/reset unrelated work or remove archives. Machine paths are not
portable project requirements; resolve relative paths on another host.

## Local toolchains

- Workspace `.venv-esphome-2026-10/Scripts/python.exe`: ESPHome 2026.10.0,
  ESP-IDF 5.5.6. This matches the last supplied owner installation log.
- `.venv-duplex/Scripts/python.exe`: ESPHome 2026.9.1 / earlier IDF 5.5.5 builds.
- YAML min_version is a lower bound, not a toolchain pin. Check actual version.
- Build logs sit outside the repo in the workspace; final current log is
  `audio-lab-buffered-final-build.txt`. Do not commit raw logs or local binaries.

PowerShell, from the repository directory:

```powershell
& ..\.venv-esphome-2026-10\Scripts\python.exe -m esphome version
& ..\.venv-esphome-2026-10\Scripts\python.exe -m esphome config firmware/stackchan-audio-lab-buffered.example.yaml
& ..\.venv-esphome-2026-10\Scripts\python.exe -m esphome compile firmware/stackchan-audio-lab-buffered.example.yaml
& ..\.venv-esphome-2026-10\Scripts\python.exe -m esptool image-info firmware/.esphome/stackchan-audio-lab-buffered-build/build/firmware.ota.bin
```

Config output can contain expanded secrets: do not expose or publish it. Existing
local secrets/build binaries use placeholder settings; owner compiles the public
YAML with real secrets. Do not hand them these local test binaries or flash the
robot automatically. USB images must identify ESP32-S3, chip ID 9,16 MB. Historical
browser chip-C6 error did not establish that our checked S3 binary was C6.

## Known Windows build issues

1. Cleanup of an old build tree can fail with WinError5 under managed_components.
   A distinct build_path avoids mixing/colliding metadata. Do not recursively
   delete guessed paths; inspect exact resolved target and preserve evidence.
2. Generated `CMakeFiles/sections.ld-*.bat` can pass shell suffix
   `|| (set FAIL_LINE=3& goto :ABORT)` as arguments to ldgen.py. C++ compiles but
   sections.ld is missing at link. This is a local Windows build issue, separate
   from the owner's RingBuffer source error. Successful workaround: inspect that
   generated command, run its Python+ldgen arguments directly without the shell
   suffix using subprocess argument list/cwd=build, then rerun unchanged YAML.
   No compiler/toolchain source patch or application format change is required.
   Never run an arbitrary log command blindly. Only apply if the exact error recurs.
3. Concurrent new toolchain installation previously hit a framework download lock;
   complete installation first, then retry the dependent build.

Do not suggest clean build as a universal audio/clock/transport fix. Record actual
errors and exact workaround. Full builds can be slow; report progress without
claiming hardware success. Documentation-only edits do not require firmware builds.

## Code navigation

| Concern | First location to inspect |
| --- | --- |
| Active lab sequencing, feeding, gain, clock guard | firmware/stackchan-audio-lab-buffered.example.yaml |
| RAM capture, authentication, WAV routes/state | components/esp_afe/chan_capture.h (delivered lab pins remote 12c218e) |
| AFE graph, task callbacks and profiling | components/esp_afe/esp_afe.cpp and chan profiling helpers in that component |
| Speaker staging/accepted-byte behavior | components/esp_audio_stack/esp_audio_stack.cpp and speaker/esp_audio_stack_speaker.cpp |
| RX/TX frame packing and underrun counters | components/esp_audio_stack/audio_pipeline.cpp |
| Codec-less TX layout correction | components/esp_audio_stack/codec_dev_backend.cpp |
| ESPHome 2026.10 buffer compatibility | components/esp_audio_stack/audio_core_ring_buffer_caps.h |
| Pipecat transport/session behavior | pinned upstream va_pipecat component; local reference checkout upstream-pipecat |

Inspect the actual remote revision named by YAML before assuming local HEAD changes
will be compiled. Editing vendored code alone does not update a pinned Git source.

## Tests and evidence discipline

- tests/test_codec_less_tx.py checks production layout-validation control flow
  against mocks; inspect its invocation requirements before running.
- tests/test_ring_buffer_compat.py accepts compile_commands.json from a successful
  build, downloads exact 2026.9.1/2026.10.0 headers and checks production header
  compilation with integrity debug on/off. FreeRTOS/heap are stubs, not runtime
  allocator/audio verification. Artifacts under ignored .runtime/.
- esptool image-info confirms target/header/hash, not successful installation,
  sample continuity, microphone quality or echo control.
- Runtime CPU percentages are per one core. Static RAM percentages exclude
  dynamic AFE/capture allocations. Do not convert idle snapshots into a promise
  of capacity for camera/animation/motors.

## Publication and future updates

Owner authorized project commits/pushes to the working branch. Keep this distinct
from publishing a release: no release until physical validation. Preserve upstream
licenses, dependency pins and previous examples. Stage only intended project files;
check status/diff first and do not include secrets, WAVs, build output or raw logs.
Do not reset user edits. A component change must be available remotely before a
copy-paste YAML can pin it; validate the delivered remote configuration.

After a test: update CURRENT_STATE, append VALIDATION evidence, update the firmware
catalog/protocol if needed. Record log filenames, exact config/source versions,
owner report, numerical observations and remaining uncertainty separately. When
opening a new chat, use this actual workspace and ask it to start with AGENTS.md.
