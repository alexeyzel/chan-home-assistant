// StackChan diagnostic extension. No audio policy or gain changes.
#pragma once
#include "esphome/core/log.h"
#include <atomic>
#include <cstring>
#include <esp_timer.h>
#include <esp_heap_caps.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

namespace esphome::esp_afe {
struct ChanSpan {
  std::atomic<uint32_t> count{0}, total{0}, peak{0};
  void add(uint32_t us) {
    total.fetch_add(us, std::memory_order_relaxed);
    count.fetch_add(1, std::memory_order_relaxed);
    uint32_t old = peak.load(std::memory_order_relaxed);
    while (us > old && !peak.compare_exchange_weak(old, us, std::memory_order_relaxed)) {}
  }
  void dump(const char *label) {
    // Approximate interval aggregates: producers continue while counters reset.
    const auto n = count.exchange(0), sum = total.exchange(0), max = peak.exchange(0);
    ESP_LOGI("chan_profile", "%s n=%u avg_us=%u max_us=%u", label, (unsigned)n,
             (unsigned)(n ? sum / n : 0), (unsigned)max);
  }
};

struct ChanDiagnostics {
  ChanSpan input_wait, outside_reader, output_gap;
  std::atomic<uint32_t> last_reader_return{0}, last_output{0};
#if configGENERATE_RUN_TIME_STATS && configUSE_TRACE_FACILITY
  static constexpr UBaseType_t CAPACITY = 96;
  struct Previous { UBaseType_t id; uint32_t runtime; };
  TaskStatus_t *tasks = nullptr;
  Previous previous[CAPACITY]{};
  UBaseType_t previous_count = 0;
  uint32_t previous_total = 0;
  bool ready = false;
#endif
  void dump(bool active, int feed_samples) {
    ESP_LOGI("chan_profile", "v=1 active=%s feed_budget_us=%u", active ? "YES" : "NO",
             (unsigned)(feed_samples * 1000000UL / 16000));
    input_wait.dump("input_queue_wait");
    outside_reader.dump("outside_reader_wall");
    output_gap.dump("output_callback_gap");
#if configGENERATE_RUN_TIME_STATS && configUSE_TRACE_FACILITY
    if (tasks == nullptr)
      tasks = static_cast<TaskStatus_t *>(heap_caps_calloc(CAPACITY, sizeof(TaskStatus_t),
                                                         MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
    if (tasks == nullptr) {
      ESP_LOGW("chan_profile", "No RAM for task snapshot");
      return;
    }
    uint32_t total = 0;
    const int64_t begin = esp_timer_get_time();
    const UBaseType_t n = uxTaskGetSystemState(tasks, CAPACITY, &total);
    const uint32_t cost = static_cast<uint32_t>(esp_timer_get_time() - begin);
    if (n == 0) {
      ready = false;
      ESP_LOGW("chan_profile", "Task snapshot unavailable/capacity exceeded");
      return;
    }
    const uint32_t elapsed = total - previous_total; // unsigned wrap-safe, short intervals
    ESP_LOGI("chan_profile", "tasks=%u snapshot_us=%u window_us=%u baseline=%s",
             (unsigned)n, (unsigned)cost, (unsigned)elapsed, ready ? "NO" : "YES");
    if (ready && elapsed != 0) {
      for (UBaseType_t i = 0; i < n; ++i) {
        for (UBaseType_t j = 0; j < previous_count; ++j) {
          if (tasks[i].xTaskNumber != previous[j].id) continue;
          const uint32_t used = tasks[i].ulRunTimeCounter - previous[j].runtime;
          const float percent = 100.0f * used / elapsed;
          // One busy core is 100%; both cores combined may reach 200%.
          // IDLE0/IDLE1 percentages are per-core idle opportunity, not a guarantee
          // of audio deadline capacity. Snapshot state is instantaneous only.
          if (percent >= 0.5f || strstr(tasks[i].pcTaskName, "IDLE") ||
              strstr(tasks[i].pcTaskName, "afe") || strstr(tasks[i].pcTaskName, "audio"))
            ESP_LOGI("chan_cpu", "%s cpu_one_core=%.1f%% prio=%u state=%u stack_min=%u",
                     tasks[i].pcTaskName, percent, (unsigned)tasks[i].uxCurrentPriority,
                     (unsigned)tasks[i].eCurrentState, (unsigned)tasks[i].usStackHighWaterMark);
          break;
        }
      }
    }
    for (UBaseType_t i = 0; i < n; ++i)
      previous[i] = {tasks[i].xTaskNumber, tasks[i].ulRunTimeCounter};
    previous_count = n;
    previous_total = total;
    ready = true;
#else
    ESP_LOGW("chan_profile", "FreeRTOS runtime stats disabled");
#endif
  }
};
}  // namespace esphome::esp_afe
