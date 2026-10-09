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
No component code is vendored. Device compatibility remains unverified.
Record revision and applicable notices before distributing code or binaries.
Gemini Live is a Google service subject to its service terms.

## Historical material

Earlier tags retain their original notices, including the removed ha-gemini-live
patch. That patch/backend are no longer in the current tree.
No binary firmware, third-party artwork, or audio is bundled.
