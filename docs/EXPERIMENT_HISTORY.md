# Experiment history and retained artifacts

Status as of2026-10-22. These are historical comparisons, not a sequence to repeat.
CURRENT_STATE.md selects the active test. “Compiled” never means device success.
Raw evidence stays outside Git; detailed analysis is in VALIDATION.md.

## Before this implementation

Owner reports: stock M5Stack plus StackChan AI Server worked stably; Dotty received
input but did not play responses; stackchan-idf ran but voice interaction was not
suitable; Dravix had errors including speaker failure; earlier own ESPHome attempts
failed to establish a stable base. Exact binaries/revisions for those attempts are
unknown. kyvaith/pipecat-homeassistant was the installed Pipecat project.

## Milestones and failures

| Evidence | Experiment / result | Retained lesson |
| --- | --- | --- |
| Initial BSP | Official ESPHome boot/TTS audible via media_player.stackchan; higher HA volume acceptable | Working hardware baseline; main revision was not pinned at that time |
| Early Pipecat | Clear input, eventually audible replies; web client also sometimes silent while output WAV contained speech | Separate generated audio, transport and local playback failures |
| Early barge-in | Parent bus busy, speaker failed; reverting restored conversation | One shared I2S owner required |
| test1/test2, logs15–20 | Raw duplex, standalone SR/FD AEC; repeated self-interruption | Simultaneous IO exists; AEC enabled is not proof it works |
| Logs19/20 | Mic gain18 instead of36 reduced full-scale probe peaks, echo persisted | Do not rediscover18dB as an AEC solution by itself |
| Logs21/22 | Software-reference delay160ms suppressed self-interruption in one run | Useful historical echo-only baseline; delay is not a hardware constant |
| Log23 | Maximum-volume deliberate stop requests failed | Echo suppression alone is not double-talk/barge-in success |
| Log24 | Codec-less TX layout query returned0x106, capture never started | Patch missing codec metadata path, retain bus validation |
| Log25 | RX and response queue ran, no audible response; clock mismatch identified | AW88298 needs64fs for our bus; accepted bytes do not prove playback |
| Log26 | Clock-corrected hardware reference: owner heard replies, no self-interruption, could interrupt | Partial hardware POC; preserve source5ec1eb8, not a qualified release |
| Log27 | Normal speech often failed to interrupt; initial Start lost after WS disconnect | Startup recovery and speech fidelity remain separate problems |
| Logs29/30 | Uplink/startup experiments still unsatisfactory; quiet replies/disconnects/misrecognition | Do not mark bounded retry or x4 gain as robust fixes |
| Log31 | Full Waveshare AFE port: about59.84% entirely zero256-sample output blocks | Full graph initially starved; source compatibility did not prove throughput |
| Logs32/33 | Performance profile improved but did not solve recognition; core 0 saturated while core 1 idle55–56% | Measure per-core scheduling; move bus task tocore 1, retain profiling |
| Logs34/35 + server14-02 log | Disconnect on interruption, no continued conversation | WS send/reconnect failure is not automatically an AEC/Gemini failure |
| Log36 + first lab WAVs | Quiet raw mic≈−64dBFS RMS at6dB gain | Isolate local audio; gain audit found official BSP36dB |
| Native16k build | User requested removal of48→16 input conversion; only live output24→16 remains | Match shared bus and AW88298 sample-rate register |
| chan-install.txt | Owner upgraded to ESPHome 2026.10; handle_ field became handle_() | Version-compatible CapsRingBuffer fix80e0d8c, verified2026.9/10 headers |
| Log 38 | Password missing; no capture/server; connection refused | Set capture_password, inspect error before blaming Stop/network |
| Log 39 / Lab 1 | Native16k/36dB quiet recording good, no clipping | Owner-tested quiet path, not echo-safe duplex |
| Log 40 / Lab 2 | Raw mics clip≈21–23%; feeding8s PCM took≈10s with many short frames | Fix lab feed pacing and test ADC headroom; cannot judge AEC cleanly |
| c933d10 /0e51724 | New buffered lab,18dB hypothesis, normalized stimulus, timing guards | Compiled only; owner tests pending |

## Firmware catalog

Paths below are relative to firmware/. Old YAML pins may not compile with newer
ESPHome; they are comparisons, not supported alternative current builds.

| File | Status/use |
| --- | --- |
| stackchan-audio-lab-buffered.example.yaml | **Active pending hardware test** |
| stackchan-audio-lab-16k.example.yaml | Preceding36dB lab: quiet pass/playback fail logs39/40; preserve comparison |
| stackchan-pipecat-16k.example.yaml | Compiled deferred live candidate, still36dB; buffered-lab changes not ported |
| stackchan-audio-lab-v2.example.yaml | 48k bus/36dB gain-audit candidate, superseded by native16k |
| stackchan-audio-lab.example.yaml | Original48k/6dB isolated lab; low input levels |
| stackchan-afe-balanced.example.yaml | Core1 bus/performance-profile live experiment; historical |
| stackchan-afe-profile.example.yaml | Added CPU/callback metrics; historical |
| stackchan-afe-perf.example.yaml | Donor compiler/cache/PSRAM profile; partial improvement |
| stackchan-full-afe.example.yaml | Initial AFE graph port; severe missing audio log 31 |
| stackchan-hwref-uplink.example.yaml | Bounded startup retry and post-AEC x4 gain; not qualified |
| stackchan-hwref.example.yaml | Clock-corrected hardware-reference line; log 26 partial success, log 27 limitations |
| stackchan-duplex-probe.example.yaml | Software-reference diagnostics/delay experiments; history needed for exact variant |
| stackchan-duplex-fd.example.yaml | FD standalone-AEC experiment, self-interruption persisted |
| stackchan-duplex-aec.example.yaml | Early SR standalone AEC, self-interruption |
| stackchan-duplex.example.yaml | Raw shared-bus duplex, no echo-safe conversation |
| official-baseline.example.yaml | Owner-proven BSP approach, upstreammain/exact old build SHA unknown |

Do not overwrite the owner's working installation automatically. Keep previous
examples/history; no mass deletion or reset is needed. Historical tagsv0.1.1/v0.1.2
refer to the retired Assist-first project, not this Pipecat POC.

## Evidence files on this machine

C:/Users/Alexe/Downloads/ contains owner recordings/logs when still available.
Use exact names; numeric browser suffixes are not firmware versions.

- Log 39: `chan-logs (39).txt`; `mic0 (1).wav`, `mic2 (1).wav`,
  `reference (1).wav`, `processed (1).wav`, `stimulus.wav`.
- Log 40: `chan-logs (40).txt`; `mic0 (2).wav`, `mic2 (2).wav`,
  `reference (2).wav`, `processed (2).wav`, `stimulus (1).wav`.
- Original quiet lab: `chan-logs (36).txt`, `mic0.wav`, `mic2.wav`,
  `reference.wav`, `processed.wav`.
- Install failure: `chan-install.txt`; password failure: `chan-logs (38).txt`.
- Historical Pipecat disconnect evidence includes
  `b2705758_pipecat_assist_2026-10-17T14-02-27.773Z.log`.

These files are private evidence, not repository inputs to publish. If missing,
use documented measurements and clearly state that reinspection is unavailable.
