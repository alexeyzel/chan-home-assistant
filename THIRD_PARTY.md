# Third-party components and attribution

Original project code is covered by the root MIT license. The following projects
retain their own licenses and ownership. No complete robot platform is imported.

## Reused hardware configuration and external drivers

**M5Stack — esphome-yaml**

- Repository: https://github.com/m5stack/esphome-yaml
- Revision: `cc708ddcc9dea7cfc746b408d2495ce281bbf2d2`
- Source configuration: [stackchan-bsp.factory.yaml](https://github.com/m5stack/esphome-yaml/blob/cc708ddcc9dea7cfc746b408d2495ce281bbf2d2/examples/kit/stackchan-bsp.factory.yaml)
- License: [MIT](https://github.com/m5stack/esphome-yaml/blob/cc708ddcc9dea7cfc746b408d2495ce281bbf2d2/LICENSE), Copyright (c) 2025 m5stack.
- Preserved notice: [LICENSES/m5stack-esphome-yaml-MIT.txt](LICENSES/m5stack-esphome-yaml-MIT.txt).

`firmware/packages/official-stackchan.yaml` imports the official BSP directly.
No local hardware-definition copy is maintained. GPIOs, power rails, codecs,
servo calibration formulas and sensor definitions come from that package.
The later external-component source pins all seven M5Stack drivers to the same
revision, taking precedence over upstream's moving-main source in ESPHome.

`firmware/chan.yaml` adds activation, voice-state handling and Assist. Its explicit
behavior overlays replace the display test card with the original Chan face,
set screen/body lights off by default, and omit the factory camera/IR/AC demo and
calibration buttons from the initial Chan interaction. It does not change hardware
pin assignments. Official servo drivers and feedback/native controls remain;
custom tracking and motion are not implemented. The standalone
`firmware/official-baseline.example.yaml` imports the factory BSP without those
Chan overlays for comparison during hardware diagnosis.

M5Stack drivers are fetched by ESPHome, not copied into this repository. Preserve
the M5Stack MIT notice when distributing components or compiled firmware.

## Runtime/build dependencies

| Project | Use | License/source |
| --- | --- | --- |
| [ESPHome](https://github.com/esphome/esphome) | Firmware framework, native HA API, audio/display/touch components | [MIT for Python/tooling; GPLv3 for C++/runtime](https://github.com/esphome/esphome/blob/2026.9.1/LICENSE) |
| [Home Assistant Core](https://github.com/home-assistant/core) | Host platform, entity registries, services, Assist and LLM APIs | [Apache-2.0](https://github.com/home-assistant/core/blob/2026.10.0/LICENSE.md) |
| [ESP-IDF](https://github.com/espressif/esp-idf) | ESP32 build/runtime framework selected by ESPHome | [Apache-2.0 and component notices](https://github.com/espressif/esp-idf/blob/v5.5.5/LICENSE) |

These platforms are installed separately. Firmware builds include their code and
transitive libraries. Source availability and notices must follow the applicable
licenses when distributing binaries; the root MIT license does not relicense
ESPHome or its dependencies. This test repository distributes configuration and
original source, not a public precompiled firmware image.

## Optional voice integration and a compatibility patch

**Matt Pyne — ha-gemini-live**

- Repository: https://github.com/matt123p/ha-gemini-live
- Inspected version: `1.0.9`.
- Inspected revision: `d4ad0e523eca92f1c395e82da14d6da0fafd71be`.
- License: [MIT](https://github.com/matt123p/ha-gemini-live/blob/d4ad0e523eca92f1c395e82da14d6da0fafd71be/LICENSE), Copyright (c) 2026 Matt Pyne.
- Role: optional Assist-compatible Gemini Live backend, installed independently.

The full integration is not vendored. The patch in
`patches/ha-gemini-live-tool-results.patch` contains upstream context plus an
original small fix for HA 2026.10 ToolResult serialization. Its upstream MIT
notice is preserved in `LICENSES/ha-gemini-live-MIT.txt`. Apply it only to the
inspected revision as documented in `docs/GEMINI_LIVE.md`.

Chan uses HA's public LLM API. Gemini is a separate Google service subject to
its own terms, not an open-source component licensed by this repository.

## Future backend and hardware references

- [Frigate](https://github.com/blakeblackshear/frigate),
  [MIT license](https://github.com/blakeblackshear/frigate/blob/master/LICENSE):
  intended future vision backend; no code copied and no dependency in v0.1.
- [M5Stack StackChan hardware documentation](https://docs.m5stack.com/en/StackChan)
  and [official ESPHome device guide](https://docs.m5stack.com/en/homeassistant/devices/stackchan):
  hardware references; diagrams and product images are not redistributed.

The geometric face in `firmware/packages/face.yaml` is original project code. No third-party
artwork, character sprites, audio files, icons, or fonts are bundled.
