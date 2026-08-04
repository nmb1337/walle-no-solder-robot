<script>
  let input = "";
  let messages = [{ role: "bot", text: "你好，我是瓦力。配置供应商后，我可以看图、回答问题并执行动作。" }];
  let state = { online: true, battery: 87, wifi: -48, last_move: "停止" };
  let provider = "演示模式";
  async function call(path, body) { const response = await fetch(path, { method: body ? "POST" : "GET", headers: { "Content-Type": "application/json" }, body: body && JSON.stringify(body) }); return response.json(); }
  async function move(action) { state = (await call("/api/device/move", { action })).state; }
  async function send() { if (!input.trim()) return; messages = [...messages, { role: "user", text: input }]; const text = input; input = ""; const result = await call("/api/ai/chat", { messages: [{ role: "user", content: text }] }); messages = [...messages, { role: "bot", text: result.text }]; provider = `${result.provider} / ${result.model}`; }
</script>

<svelte:head><title>瓦力控制台</title></svelte:head>
<div class="shell"><header><b><span>W</span> 瓦力控制台</b><small>WALL-E LOCAL GATEWAY</small><i>● 网关在线</i></header><main><section><p class="eyebrow">视觉</p><h1>摄像头画面</h1><div class="preview"><span>CORE S3 / 640×480</span></div><div class="metrics"><div>设备<strong>{state.online ? "在线" : "离线"}</strong></div><div>电量<strong>{state.battery}%</strong></div><div>Wi-Fi<strong>{state.wifi} dBm</strong></div><div>供应商<strong>{provider}</strong></div></div><p class="eyebrow talk">对话</p><h2>和瓦力说话</h2><div class="chat">{#each messages as message}<div class:mine={message.role === "user"}><em>{message.role === "bot" ? "W" : "你"}</em><p>{message.text}</p></div>{/each}<footer><input bind:value={input} on:keydown={(e) => e.key === "Enter" && send()} placeholder="输入一句话"/><button on:click={send}>发送</button></footer></div></section><aside><p class="eyebrow">设备动作</p><h2>让瓦力动起来</h2><div class="pad"><button on:click={() => move("forward")}>↑</button><button on:click={() => move("left")}>←</button><button class="stop" on:click={() => move("stop")}>■</button><button on:click={() => move("right")}>→</button><button on:click={() => move("back")}>↓</button></div><p class="move-label">{state.last_move}</p><hr/><p class="eyebrow">配置</p><h2>供应商</h2><p class="note">完整配置面板在标准网页版本中提供，API Key 只写入本机网关。</p></aside></main></div>
