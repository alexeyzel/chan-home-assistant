"""Compile production CapsRingBuffer against exact upstream ESPHome headers.
FreeRTOS/heap stubs check API compatibility, not runtime allocator behavior.
Usage: python tests/test_ring_buffer_compat.py compile_commands.json
"""
import json, subprocess, sys, urllib.request
from pathlib import Path
root = Path(__file__).resolve().parents[1]
commands = json.loads(Path(sys.argv[1]).read_text())
command = next(x['command'] for x in commands if 'g++.exe' in x['command'] or 'g++ ' in x['command'])
compiler = command.split(' -', 1)[0].strip('"')
base = root / '.runtime/ring_compat'
base.mkdir(parents=True, exist_ok=True)
files = {
 'freertos/FreeRTOS.h': '#pragma once\n#include <cstddef>\nusing TickType_t=unsigned; using BaseType_t=int; using UBaseType_t=unsigned; constexpr int pdPASS=1;\n',
 'freertos/ringbuf.h': '''#pragma once
#include "FreeRTOS.h"
struct StaticRingbuffer_t { char dummy[80]; };
using RingbufHandle_t=void*;
enum RingbufferType_t {RINGBUF_TYPE_BYTEBUF,RINGBUF_TYPE_NOSPLIT};
RingbufHandle_t xRingbufferCreateStatic(size_t,RingbufferType_t,uint8_t*,StaticRingbuffer_t*);
void vRingbufferDelete(RingbufHandle_t);
void* xRingbufferReceive(RingbufHandle_t,size_t*,TickType_t);
void vRingbufferReturnItem(RingbufHandle_t,void*);
int xRingbufferSend(RingbufHandle_t,const void*,size_t,TickType_t);
void vRingbufferGetInfo(RingbufHandle_t,UBaseType_t*,UBaseType_t*,UBaseType_t*,UBaseType_t*,UBaseType_t*);
''',
 'esp_heap_caps.h': '#pragma once\n#include <cstddef>\n#include <cstdint>\nconstexpr unsigned MALLOC_CAP_INTERNAL=1,MALLOC_CAP_SPIRAM=2,MALLOC_CAP_8BIT=4;\nvoid* heap_caps_malloc(size_t,uint32_t); void heap_caps_free(void*);\n',
 'esp_memory_utils.h':'#pragma once\nbool esp_ptr_internal(const void*);\n',
}
for name, text in files.items():
 p=base/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
unit=base/'probe.cpp'
unit.write_text('#include <cstdint>\n#define USE_ESP32\n#include "'+(root/'components/esp_audio_stack/audio_core_ring_buffer_caps.h').as_posix()+'"\n')
for version, month in [('2026.9.1',9),('2026.10.0',10)]:
 p=base/'esphome/components/ring_buffer/ring_buffer.h'; p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/esphome/esphome/{version}/esphome/components/ring_buffer/ring_buffer.h').read())
 p=base/'esphome/core/version.h';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(f'#pragma once\n#define VERSION_CODE(a,b,c) ((a)*10000+(b)*100+(c))\n#define ESPHOME_VERSION_CODE VERSION_CODE(2026,{month},0)\n')
 for debug in [False,True]:
  args=[compiler,'-std=c++17','-fsyntax-only','-I'+str(base),str(unit)]
  if debug: args.append('-DESP_AFE_RING_INTEGRITY_DEBUG')
  subprocess.run(args,check=True)
  print(f'PASS: upstream {version}, integrity_debug={debug}')
