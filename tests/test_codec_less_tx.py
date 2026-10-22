"""Compile-time regression tests of the actual read_layout_ body with mock APIs.

Usage: python tests/test_codec_less_tx.py path/to/compile_commands.json [source.cpp]
Uses the existing ESPHome compiler; no device or host C++ runtime needed.
"""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
source_path = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "components/esp_audio_stack/codec_dev_backend.cpp"
source = source_path.read_text()
start = source.index("bool CodecDevBackend::read_layout_(")
end = source.index("\nbool CodecDevBackend::open(", start)
body = "constexpr " + source[start:end]
prefix = r'''
#include <cstdint>
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
constexpr int ESP_CODEC_DEV_OK = 0;
constexpr int ESP_CODEC_DEV_TYPE_OUT = 1;
constexpr int ESP_CODEC_DEV_TYPE_IN = 2;
constexpr int ESP_CODEC_DEV_I2S_MODE_TDM_PHILIPS = 3;
using esp_codec_dev_type_t = int;
struct Bus { unsigned sample_rate=48000, data_bit=16, slot_bit=16,
  total_slot=4, slot_mask=1; int mode=3; };
struct Map { unsigned value=0; };
struct Device { int status=-1, queries=0; };
constexpr int esp_codec_dev_get_data_layout(Device *d, Map *m) {
  ++d->queries; m->value=0x1234; return d->status;
}
struct Data {
  Bus bus{}; int status=0;
  static constexpr int query(const Data *d, int, Bus *b) { *b=d->bus; return d->status; }
  int (*get_bus_info)(const Data *, int, Bus *) = query;
};
struct CodecDevBackend {
  struct SampleConfig { unsigned sample_rate=48000, bits_per_sample=16,
    channels=4, channel_mask=1; };
  struct StreamLayout { Bus bus{}; Map memory{}; bool valid=false; };
  const Data *data_if_=nullptr;
  Device *tx_dev_=nullptr, *rx_dev_=nullptr;
  const void *tx_codec_if_=nullptr;
  constexpr bool read_layout_(int, const SampleConfig &, StreamLayout &);
};
'''
tests = r'''
constexpr bool check(int scenario) {
  Data data; Device tx, rx;
  CodecDevBackend b; b.data_if_=&data; b.tx_dev_=&tx; b.rx_dev_=&rx;
  CodecDevBackend::SampleConfig req;
  CodecDevBackend::StreamLayout result;
  int direction=ESP_CODEC_DEV_TYPE_OUT;
  bool expected=scenario==0 || scenario==10 || scenario==12;
  switch(scenario) {
    case 1: data.status=-1; break;
    case 2: data.bus.sample_rate=24000; break;
    case 3: data.bus.data_bit=32; break;
    case 4: data.bus.slot_mask=2; break;
    case 5: data.bus.total_slot=2; break;
    case 6: data.bus.slot_bit=32; break;
    case 7: data.bus.slot_mask=req.channel_mask=3; break;
    case 8: data.bus.slot_mask=req.channel_mask=0; break;
    case 9: b.tx_codec_if_=&tx; break;
    case 10: b.tx_codec_if_=&tx; tx.status=0; break;
    case 11: direction=ESP_CODEC_DEV_TYPE_IN; break;
    case 12: direction=ESP_CODEC_DEV_TYPE_IN; rx.status=0; break;
    case 13: data.bus.slot_mask=req.channel_mask=16; break;
    case 14: data.bus.mode=0; break;
    case 15: b.data_if_=nullptr; break;
    case 16: data.get_bus_info=nullptr; break;
  }
  bool ok=b.read_layout_(direction,req,result);
  if(ok!=expected || result.valid!=expected) return false;
  if(scenario==0) return tx.queries==0 && result.memory.value==0;
  if(scenario==9 || scenario==10) return tx.queries==1;
  if(scenario==11 || scenario==12) return rx.queries==1;
  return true;
}
'''
tests += "\n".join(f'static_assert(check({i}), "scenario {i}");' for i in range(17))
commands = json.loads(Path(sys.argv[1]).read_text())
command = next(x["command"] for x in commands if "g++.exe" in x["command"] or "g++ " in x["command"])
compiler = command.split(" -", 1)[0].strip('"')
unit = root / ".runtime/layout_test.cpp"
unit.parent.mkdir(exist_ok=True)
unit.write_text(prefix + body + tests)
subprocess.run([compiler, "-std=c++17", "-fsyntax-only", str(unit)], check=True)
print("PASS: 17 constexpr scenarios against production read_layout_ body")
