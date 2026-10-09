// SPDX-License-Identifier: MIT
// Original Chan geometric face. No third-party artwork or fonts.
#pragma once

#include <string>
#include "esphome/components/display/display.h"

namespace chan {
inline void draw_face(esphome::display::Display &it, bool active,
                      const std::string &expression, const std::string &phase,
                      uint32_t now) {
  const auto black = esphome::Color(0, 0, 0);
  const auto white = esphome::Color(230, 235, 240);
  it.fill(black);
  if (!active) return;
  const int cx = it.get_width() / 2;
  const int cy = it.get_height() / 2;
  const bool blink = now % 5100 < 120;
  const int height = blink ? 3 : expression == "focused" ? 14 : 34;
  for (const int dx : {-48, 48}) {
    if (expression == "happy" && !blink) {
      it.line(cx + dx - 17, cy - 14, cx + dx, cy - 25, white);
      it.line(cx + dx, cy - 25, cx + dx + 17, cy - 14, white);
    } else {
      it.filled_rectangle(cx + dx - 12, cy - 20 - height / 2, 24, height, white);
    }
    if (expression == "sad")
      it.line(cx + dx - 16, cy - 48, cx + dx + 16, cy - 40, white);
  }
  if (expression == "surprised") {
    it.circle(cx, cy + 40, 12, white);
  } else if (expression == "warm" || expression == "happy") {
    it.line(cx - 24, cy + 30, cx - 12, cy + 42, white);
    it.line(cx - 12, cy + 42, cx + 12, cy + 42, white);
    it.line(cx + 12, cy + 42, cx + 24, cy + 30, white);
  } else {
    it.line(cx - 18, cy + 38, cx + 18, cy + 38, white);
  }
  const auto state_color = phase == "speaking" ? esphome::Color(80, 180, 255)
                         : phase == "thinking" ? esphome::Color(200, 150, 70)
                         : esphome::Color(80, 200, 120);
  it.filled_circle(cx, it.get_height() - 18, 4, state_color);
}
}  // namespace chan
