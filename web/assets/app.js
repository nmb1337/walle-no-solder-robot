const $ = (selector) => document.querySelector(selector);
const state = { image: null, profiles: [], active: null, recorder: null, chunks: [] };

function toast(text) {
  const el = $("#toast");
  el.textContent = text;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function addMessage(text, who = "bot") {
  const row = document.createElement("div");
  row.className = `message ${who}`;
  row.innerHTML = `<span class="avatar">${who === "bot" ? "W" : "我"}</span><p></p>`;
  row.querySelector("p").textContent = text;
  $("#messages").appendChild(row);
  $("#messages").scrollTop = 99999;
}

function renderState(device) {
  $("#device-status").textContent = device.online ? "在线" : "离线";
  $("#battery").textContent = `${device.battery ?? "--"}%`;
  $("#wifi").textContent = `${device.wifi ?? "--"} dBm`;
  $("#move-label").textContent = device.last_move || "停止";
  $("#audio-state").textContent = device.audio_state || "空闲";
  $("#camera-status").innerHTML = `<i></i>摄像头${device.camera ? "开启" : "关闭"}`;
  if (device.last_snapshot) {
    $("#camera-image").src = device.last_snapshot;
    $("#snapshot-time").textContent = "刚刚更新";
  }
}

function renderProfiles() {
  const select = $("#provider-select");
  select.innerHTML = `<option value="">演示模式</option>` + state.profiles.map((profile) =>
    `<option value="${escapeHtml(profile.name)}">${escapeHtml(profile.name)} · ${escapeHtml(profile.model || "模型未填写")}</option>`
  ).join("");
  select.value = state.active || "";
  const profile = state.profiles.find((item) => item.name === state.active);
  if (profile) {
    $("#provider-name").value = profile.name || "";
    $("#provider-url").value = profile.base_url || "";
    $("#provider-model").value = profile.model || "";
    $("#provider-proxy").value = profile.proxy_url || "";
    $("#provider-protocol").value = profile.protocol || "responses";
    $("#supports-image").checked = !!profile.supports_image;
    $("#supports-audio").checked = !!profile.supports_audio;
  } else {
    $("#provider-name").value = "";
    $("#provider-url").value = "";
    $("#provider-model").value = "";
    $("#provider-proxy").value = "";
    $("#provider-key").value = "";
  }
  $("#provider-label").textContent = profile ? `${profile.name} / ${profile.model || "模型未填写"}` : "演示模式";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

async function refresh() {
  try {
    const [health, device, providers] = await Promise.all([
      api("/api/health"), api("/api/device/state"), api("/api/providers"),
    ]);
    $("#service-pill").innerHTML = `<i></i>网关在线${health.proxy ? " · 代理已启用" : ""}`;
    renderState(device);
    state.profiles = providers.profiles || [];
    state.active = providers.active_profile;
    renderProfiles();
    if (!$("#provider-proxy").value && providers.proxy_url) $("#provider-proxy").value = providers.proxy_url;
  } catch (error) {
    $("#service-pill").innerHTML = "<i></i>网关未连接";
    toast("请先启动本地网关");
  }
}

async function snapshot() {
  try {
    const data = await api("/api/camera/snapshot", { method: "POST", body: "{}" });
    $("#camera-image").src = data.image;
    $("#snapshot-time").textContent = "刚刚更新";
    state.image = data.ai_image || data.image;
    toast(data.source === "demo" ? "当前是演示画面" : "已收到摄像头画面");
  } catch (error) {
    toast("拍照失败");
  }
}

async function sendChat(withImage = false) {
  const input = $("#chat-input");
  const text = input.value.trim() || "请描述当前画面";
  if (!withImage && !input.value.trim()) return;
  if (withImage && !state.image) await snapshot();
  addMessage(text, "user");
  input.value = "";
  $("#request-status").textContent = "请求中…";
  const started = Date.now();
  try {
    const data = await api(withImage ? "/api/ai/analyze-image" : "/api/ai/chat", {
      method: "POST",
      body: JSON.stringify(withImage ? { text, image: state.image } : { messages: [{ role: "user", content: text }] }),
    });
    addMessage(data.text || "没有收到文字回复");
    $("#provider-label").textContent = `${data.provider || "演示模式"} / ${data.model || "未配置"}`;
    $("#latency").textContent = `${data.latency_ms || Date.now() - started} ms`;
    $("#request-status").textContent = data.ok ? "正常" : "演示回复";
  } catch (error) {
    addMessage("网关请求失败，请检查服务和中转站配置。");
    $("#request-status").textContent = "失败";
  }
}

async function saveProvider() {
  const profile = {
    name: $("#provider-name").value.trim(),
    base_url: $("#provider-url").value.trim(),
    api_key: $("#provider-key").value,
    model: $("#provider-model").value.trim(),
    proxy_url: $("#provider-proxy").value.trim(),
    protocol: $("#provider-protocol").value,
    supports_image: $("#supports-image").checked,
    supports_audio: $("#supports-audio").checked,
  };
  if (!profile.name) { toast("请先填写供应商名称"); return; }
  const profiles = state.profiles.filter((item) => item.name !== profile.name);
  profiles.push(profile);
  try {
    await api("/api/providers", { method: "POST", body: JSON.stringify({ profiles, active_profile: profile.name, proxy_url: profile.proxy_url }) });
    state.profiles = profiles;
    state.active = profile.name;
    $("#provider-key").value = "";
    renderProfiles();
    toast("供应商配置已保存");
  } catch (error) {
    toast("保存失败");
  }
}

async function recordAudio() {
  if (state.recorder) {
    state.recorder.stop();
    return;
  }
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    const data = await api("/api/voice/transcribe", { method: "POST", body: "{}" });
    $("#chat-input").value = data.text;
    toast("当前浏览器不支持录音，已显示演示转写");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.chunks = [];
    state.recorder = new MediaRecorder(stream);
    state.recorder.ondataavailable = (event) => { if (event.data.size) state.chunks.push(event.data); };
    state.recorder.onstop = async () => {
      stream.getTracks().forEach((track) => track.stop());
      const blob = new Blob(state.chunks, { type: state.recorder.mimeType || "audio/webm" });
      const base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(",")[1]);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
      state.recorder = null;
      const data = await api("/api/voice/transcribe", { method: "POST", body: JSON.stringify({ audio_base64: base64, content_type: blob.type }) });
      $("#chat-input").value = data.text || "";
      toast(data.mock ? "未配置音频接口，显示演示转写" : "转写完成");
    };
    state.recorder.start();
    toast("正在录音，再点一次停止");
  } catch (error) {
    toast("无法访问麦克风");
  }
}

document.addEventListener("click", (event) => {
  const move = event.target.closest("[data-move]");
  if (move) api("/api/device/move", { method: "POST", body: JSON.stringify({ action: move.dataset.move }) }).then((data) => renderState(data.state)).catch(() => toast("动作发送失败"));
  const head = event.target.closest("[data-head]");
  const arm = event.target.closest("[data-arm]");
  if (head) {
    document.querySelectorAll("[data-head]").forEach((item) => item.classList.remove("selected"));
    head.classList.add("selected");
    api("/api/device/action", { method: "POST", body: JSON.stringify({ head: head.dataset.head }) }).catch(() => toast("头部动作发送失败"));
  }
  if (arm) {
    document.querySelectorAll("[data-arm]").forEach((item) => item.classList.remove("selected"));
    arm.classList.add("selected");
    api("/api/device/action", { method: "POST", body: JSON.stringify({ arm: arm.dataset.arm }) }).catch(() => toast("手臂动作发送失败"));
  }
});

$("#refresh-btn").onclick = refresh;
$("#snapshot-btn").onclick = snapshot;
$("#send-btn").onclick = () => sendChat(false);
$("#analyze-btn").onclick = () => sendChat(true);
$("#mic-btn").onclick = recordAudio;
$("#save-provider").onclick = saveProvider;
$("#provider-select").onchange = () => { state.active = $("#provider-select").value; renderProfiles(); };
$("#snapshot-interval").oninput = (event) => {
  $("#interval-value").textContent = `${event.target.value} 秒`;
  api("/api/settings", { method: "POST", body: JSON.stringify({ screenshot_interval: Number(event.target.value) }) }).catch(() => {});
};
$("#auto-snapshot").onchange = (event) => api("/api/settings", { method: "POST", body: JSON.stringify({ screenshot_enabled: event.target.checked }) });
["mic", "camera", "speaker"].forEach((key) => $(`#${key}-toggle`).onchange = (event) => api("/api/device/action", { method: "POST", body: JSON.stringify({ [key]: event.target.checked }) }));

$("#camera-image").src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2NDAiIGhlaWdodD0iMzYwIj48cmVjdCB3aWR0aD0iNjQwIiBoZWlnaHQ9IjM2MCIgZmlsbD0iIzIwMjUyMiIvPjx0ZXh0IHg9IjMyMCIgeT0iMTg1IiBmaWxsPSIjZjRlZGRmIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkxvYWRpbmcgY2FtZXJhLi4uPC90ZXh0Pjwvc3ZnPg==";
refresh();
setInterval(() => api("/api/device/state").then(renderState).catch(() => {}), 5000);
