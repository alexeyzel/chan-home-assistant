#pragma once
// Bounded RAM-only diagnostic recording. Audio task never sends network data.
#include <atomic>
#include <algorithm>
#include <cstring>
#include <string>
#include <esp_heap_caps.h>
#include <esp_http_server.h>
#include <esp_timer.h>
#include <mbedtls/base64.h>
#include "esphome/core/log.h"
namespace esphome::esp_afe {
class ChanCapture {
 public:
  static constexpr size_t RATE=16000, LIMIT=RATE*8;
  enum State { EMPTY, RECORDING, READY, DOWNLOADING };
  std::atomic<int> state{EMPTY};
  std::atomic_flag guard=ATOMIC_FLAG_INIT;
  std::atomic<uint32_t> skipped{0};
  int16_t *data{nullptr}, *stimulus{nullptr};
  size_t frames{0}, stimulus_frames{0};
  bool recording_enabled{true};
  uint32_t missing{0}, copy_max_us{0};
  httpd_handle_t server{nullptr};
  std::string authorization;
  void set_password(const char *password) {
    if (server || !password || strlen(password)<12 || strlen(password)>64 ||
        !strcmp(password,"CHANGE_THIS_PASSWORD")) return;
    std::string text=std::string("diagnostic:")+password;
    unsigned char encoded[128]; size_t n=0;
    if (mbedtls_base64_encode(encoded,sizeof(encoded),&n,
          reinterpret_cast<const unsigned char *>(text.data()),text.size())==0)
      authorization=std::string("Basic ")+std::string(reinterpret_cast<char *>(encoded),n);
  }
  bool start_server() {
    if (server) return true;
    if (authorization.empty()) { ESP_LOGE("chan_capture","Set capture_password (12-64 characters) first"); return false; }
    httpd_config_t cfg=HTTPD_DEFAULT_CONFIG();
    cfg.server_port=8088; cfg.ctrl_port=32778; cfg.stack_size=6144;
    cfg.max_uri_handlers=6; cfg.lru_purge_enable=true;
    if (httpd_start(&server,&cfg)!=ESP_OK) return false;
    const char *paths[]={"/mic0.wav","/mic2.wav","/reference.wav","/processed.wav","/stimulus.wav"};
    for(auto path:paths) {
      httpd_uri_t uri{}; uri.uri=path; uri.method=HTTP_GET; uri.handler=&ChanCapture::serve; uri.user_ctx=this;
      if(httpd_register_uri_handler(server,&uri)!=ESP_OK) {
        httpd_stop(server); server=nullptr; return false;
      }
    }
    return true;
  }
  bool begin(bool enabled=true) {
    if(guard.test_and_set()) return false;
    if(state==RECORDING || state==DOWNLOADING) { guard.clear(); return false; }
    if(!data) data=static_cast<int16_t *>(heap_caps_malloc(LIMIT*8,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    if(!stimulus) stimulus=static_cast<int16_t *>(heap_caps_malloc(LIMIT*2,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    if(!data || !stimulus || !start_server()) {
      ESP_LOGE("chan_capture","Allocation/auth/server failed; test cancelled"); guard.clear(); return false;
    }
    recording_enabled=enabled; frames=0; missing=0; copy_max_us=0; skipped=0; state=RECORDING;
    guard.clear(); ESP_LOGI("chan_capture","Recording 8s: mic0/mic2/reference/processed, 16kHz"); return true;
  }
  void append(const int16_t *mic,const int16_t *ref,const int16_t *out,size_t n,int channels,bool valid) {
    if(state!=RECORDING || !recording_enabled) return;
    if(guard.test_and_set()) { ++skipped; return; }
    if(state!=RECORDING) { guard.clear(); return; }
    const int64_t start=esp_timer_get_time(); n=std::min(n,LIMIT-frames);
    for(size_t i=0;i<n;++i) {
      data[4*(frames+i)]=mic[i*channels];
      data[4*(frames+i)+1]=channels>1?mic[i*channels+1]:0;
      data[4*(frames+i)+2]=ref?ref[i]:0;
      data[4*(frames+i)+3]=out[i];
    }
    if(!valid) ++missing;
    frames+=n;
    copy_max_us=std::max(copy_max_us,static_cast<uint32_t>(esp_timer_get_time()-start));
    // Publish READY only after the test has stopped, not while playback runs.
    guard.clear();
  }
  bool finish(bool save_stimulus) {
    if(guard.test_and_set()) return false;
    if(state==DOWNLOADING) { guard.clear(); return false; }
    if(state==RECORDING) state=frames?READY:EMPTY;
    if(save_stimulus && state==READY) {
      stimulus_frames=frames;
      for(size_t i=0;i<frames;++i) stimulus[i]=data[4*i+3];
    }
    ESP_LOGI("chan_capture","samples=%u missing_blocks=%u copy_max_us=%u skipped=%u stimulus_samples=%u",
      (unsigned)frames,(unsigned)missing,(unsigned)copy_max_us,(unsigned)skipped.load(),(unsigned)stimulus_frames);
    guard.clear(); return true;
  }
  bool has_stimulus() const { return stimulus_frames!=0; }
  int16_t playback_sample(size_t i) const { return i<stimulus_frames?stimulus[i]:0; }
  static esp_err_t serve(httpd_req_t *req) {
    auto *self=static_cast<ChanCapture *>(req->user_ctx);
    char auth[160]{};
    if(httpd_req_get_hdr_value_str(req,"Authorization",auth,sizeof(auth))!=ESP_OK ||
        self->authorization.empty() || self->authorization!=auth) {
      httpd_resp_set_status(req,"401 Unauthorized");
      httpd_resp_set_hdr(req,"WWW-Authenticate","Basic realm=\"StackChan diagnostics\"");
      return httpd_resp_send(req,"Authentication required",HTTPD_RESP_USE_STRLEN);
    }
    if(self->guard.test_and_set()) return httpd_resp_send_err(req,HTTPD_503_SERVICE_UNAVAILABLE,"Busy");
    if(self->state!=READY) { self->guard.clear(); return httpd_resp_send_err(req,HTTPD_503_SERVICE_UNAVAILABLE,"Complete a recording first"); }
    self->state=DOWNLOADING; self->guard.clear();
    int channel=0;
    if(!strcmp(req->uri,"/mic2.wav")) channel=1;
    else if(!strcmp(req->uri,"/reference.wav")) channel=2;
    else if(!strcmp(req->uri,"/processed.wav")) channel=3;
    else if(!strcmp(req->uri,"/stimulus.wav")) channel=4;
    size_t samples=channel==4?self->stimulus_frames:self->frames;
    uint8_t header[44]{};
    auto put16=[&](int at,uint16_t v){header[at]=v;header[at+1]=v>>8;};
    auto put32=[&](int at,uint32_t v){for(int j=0;j<4;++j)header[at+j]=v>>(8*j);};
    memcpy(header,"RIFF",4);put32(4,36+samples*2);memcpy(header+8,"WAVEfmt ",8);
    put32(16,16);put16(20,1);put16(22,1);put32(24,RATE);put32(28,RATE*2);
    put16(32,2);put16(34,16);memcpy(header+36,"data",4);put32(40,samples*2);
    httpd_resp_set_type(req,"audio/wav");httpd_resp_set_hdr(req,"Cache-Control","no-store");
    esp_err_t rc=httpd_resp_send_chunk(req,reinterpret_cast<char *>(header),44);
    int16_t chunk[512];
    for(size_t pos=0;rc==ESP_OK && pos<samples;pos+=512) {
      size_t n=std::min<size_t>(512,samples-pos);
      for(size_t i=0;i<n;++i)chunk[i]=channel==4?self->stimulus[pos+i]:self->data[4*(pos+i)+channel];
      rc=httpd_resp_send_chunk(req,reinterpret_cast<char *>(chunk),n*2);
    }
    if(rc==ESP_OK)rc=httpd_resp_send_chunk(req,nullptr,0);
    self->state.store(READY);return rc;
  }
};
}
