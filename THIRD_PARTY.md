# Third-party software

The root MIT license covers original project material only.

## Current baseline

- [M5Stack esphome-yaml](https://github.com/m5stack/esphome-yaml): official
  StackChan BSP and drivers, fetched by ESPHome. Its
  [MIT notice](LICENSES/m5stack-esphome-yaml-MIT.txt) is preserved.
  The successful build's exact upstream commit is unknown.
- [ESPHome](https://github.com/esphome/esphome): device used 2026.9.1.
  Tooling/runtime and dependencies retain their licenses. The root MIT license
  does not relicense compiled firmware.
- Home Assistant is installed independently and provided the demonstrated TTS.

## Planned backend

[kyvaith/pipecat-homeassistant](https://github.com/kyvaith/pipecat-homeassistant)
is the owner's existing add-on and proposed source of va_pipecat.
No component code is vendored. Half-duplex operation was owner-confirmed;
full-duplex compatibility remains unverified.
Record revision and applicable notices before distributing code or binaries.
Gemini Live is a Google service subject to its service terms.

## Experimental audio path

[ESPHome Audio Stack](https://github.com/n-IA-hane/esphome-audio-stack), MIT,
is fetched at `0482d741a938378ef948e3b8f3dd31536f9f2cc9` by the experimental
configurations. Its sources and optional Espressif AEC dependencies retain their
upstream notices/licenses. No component implementation is copied into this repo.
Experimental Pipecat revision: `a538d1d1bacc8609061719f0b05c1622147ccb4b`.
Experimental M5Stack BSP/driver revision: `cc708ddcc9dea7cfc746b408d2495ce281bbf2d2`.
The upstream [Audio Stack](LICENSES/esphome-audio-stack-MIT.txt) and
[Pipecat](LICENSES/pipecat-homeassistant-MIT.txt) MIT notices are retained.

## Historical material

Earlier tags retain their original notices, including the removed ha-gemini-live
patch. That patch/backend are no longer in the current tree.
No binary firmware, third-party artwork, or audio is bundled.

## Full AFE reference configuration

The full-AFE example adapts the SR/MMR/AEC/SE/post-AGC graph from
[jyoushiki Waveshare Audio VA](https://github.com/jyoushiki/esphome-waveshare-esp32-s3-audio-va),
revision c86ecd3c5124db85181c03ad35aec6578b82b849.
Copyright (c) 2026 Michal Zaniewicz and Juan Marcos Torero.
The [upstream MIT license](LICENSES/waveshare-audio-va-MIT.txt) is retained.
Board-specific pin, gain and output-codec settings are not copied.
