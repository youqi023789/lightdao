/* LightDAO §4.7 WebRTC 中继模块 v1 — P2P 数据通道中继 + 真实带宽计量
 * 职责:
 *  - 连 /signal 信令,与在线对等体建立 RTCDataChannel
 *  - 在 peer 间转发中继包(真实中继工作),计量中继字节
 *  - 暴露 getRelayBytes()/getBandwidthKbps() 供挖矿心跳的 40% 带宽分使用
 *  - 周期向信令上报 relay 字节(服务端汇总)
 * 零外部依赖。用法: LDRelay.start(minerAddr) / LDRelay.stop()
 */
(function (global) {
  "use strict";
  const MAX_PEERS = 4;          // 同时中继的对等体上限
  const RELAY_INTERVAL = 4000;  // 每4s发一个中继包
  const PKT_SIZE = 2048;        // 中继包大小(字节)
  const REPORT_INTERVAL = 10000;

  let ws = null, myId = null, started = false;
  let pcs = {};   // peerId -> {pc, dc}
  let relayBytes = 0, fwdBytes = 0, recvBytes = 0;
  let t0 = 0, iceServers = null, myAddr = "";
  let S = { pending: [], remoteSet: {}, };

  function log(m) { if (global.LDRelayLog) global.LDRelayLog(m); }

  async function getIce() {
    const r = await fetch(location.origin + "/turn/");
    return (await r.json()).iceServers;
  }
  function connectSignal() {
    return new Promise((res, rej) => {
      const u = (location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/signal";
      ws = new WebSocket(u);
      ws.onopen = () => { ws.send(JSON.stringify({ type: "hello", addr: myAddr, region: "web" })); res(); };
      ws.onerror = rej;
      ws.onmessage = ev => handle(JSON.parse(ev.data));
    });
  }
  function handle(m) {
    if (m.type === "welcome") { myId = m.id; log("relay信令连接 id=" + myId); refresh(); }
    else if (m.type === "peer-list") { maybeConnect(m.peers); }
    else if (m.type === "peer-count") { /* ignore */ }
    else if (m.type === "offer") { onOffer(m); }
    else if (m.type === "answer") { onAnswer(m); }
    else if (m.type === "ice") { queueOrAdd(m.from, m.candidate); }
  }
  function refresh() { if (ws && ws.readyState === 1) ws.send(JSON.stringify({ type: "peers" })); }

  function queueOrAdd(from, c) {
    const e = pcs[from];
    if (e && e.remoteSet) e.pc.addIceCandidate(c).catch(() => {});
    else { (S.pending[from] = S.pending[from] || []).push(c); }
  }
  function flush(from) {
    const e = pcs[from]; if (!e) return;
    e.remoteSet = true;
    (S.pending[from] || []).forEach(c => e.pc.addIceCandidate(c).catch(() => {}));
    S.pending[from] = [];
  }

  function maybeConnect(peers) {
    const have = Object.keys(pcs).length;
    if (have >= MAX_PEERS) return;
    for (const p of peers) {
      if (have >= MAX_PEERS) break;
      if (pcs[p.id]) continue;
      connectTo(p.id); have++;
    }
  }
  function newPC(toId) {
    const pc = new RTCPeerConnection({ iceServers: iceServers || [], iceTransportPolicy: "all" });
    pcs[toId] = { pc, dc: null, remoteSet: false };
    pc.onicecandidate = e => { if (e.candidate && ws) ws.send(JSON.stringify({ type: "ice", to: toId, candidate: e.candidate })); };
    pc.onconnectionstatechange = () => {
      if (pc.connectionState === "failed" || pc.connectionState === "disconnected") { dropPeer(toId); }
    };
    pc.ondatachannel = e => { wireDC(toId, e.channel); };
    return pc;
  }
  function connectTo(toId) {
    const pc = newPC(toId);
    const dc = pc.createDataChannel("relay", { ordered: false, maxRetransmits: 3 });
    wireDC(toId, dc);
    pc.createOffer().then(o => pc.setLocalDescription(o)).then(() => {
      ws.send(JSON.stringify({ type: "offer", to: toId, sdp: pc.localDescription }));
    }).catch(e => log("offer err " + e));
  }
  async function onOffer(m) {
    const pc = newPC(m.from);
    pc.ondatachannel = e => wireDC(m.from, e.channel);
    await pc.setRemoteDescription(m.sdp);
    flush(m.from);
    const a = await pc.createAnswer();
    await pc.setLocalDescription(a);
    ws.send(JSON.stringify({ type: "answer", to: m.from, sdp: pc.localDescription }));
  }
  async function onAnswer(m) {
    const e = pcs[m.from]; if (!e) return;
    await e.pc.setRemoteDescription(m.sdp);
    flush(m.from);
  }
  function wireDC(toId, dc) {
    const e = pcs[toId]; if (e) e.dc = dc;
    dc.onopen = () => { log("relay通道打开 → " + toId); };
    dc.onclose = () => dropPeer(toId);
    dc.onmessage = ev => {
      const n = (ev.data && ev.data.byteLength) || 0;
      recvBytes += n;
      // 转发给其他 peer(真实中继):计量 fwdBytes
      for (const [id, o] of Object.entries(pcs)) {
        if (id !== toId && o.dc && o.dc.readyState === "open") {
          try { o.dc.send(ev.data); fwdBytes += n; } catch (e) {}
        }
      }
    };
  }
  function dropPeer(id) {
    const e = pcs[id]; if (e) { try { e.pc.close(); } catch (err) {} }
    delete pcs[id]; delete S.pending[id];
  }

  // 周期发中继包(产生真实中继流量)
  setInterval(() => {
    if (!started) return;
    const pkt = new Uint8Array(PKT_SIZE);
    for (const [id, e] of Object.entries(pcs)) {
      if (e.dc && e.dc.readyState === "open") { try { e.dc.send(pkt); relayBytes += PKT_SIZE; } catch (err) {} }
    }
  }, RELAY_INTERVAL);

  // 周期上报信令 + 刷新 peer 列表
  setInterval(() => {
    if (!started || !ws || ws.readyState !== 1) return;
    if (relayBytes + fwdBytes > 0) ws.send(JSON.stringify({ type: "relay", bytes: relayBytes + fwdBytes }));
    refresh();
  }, REPORT_INTERVAL);

  global.LDRelay = {
    async start(addr) {
      if (started) return true;
      myAddr = addr || ("wasm1relay" + Math.random().toString(36).slice(2, 10));
      try {
        iceServers = await getIce();
        await connectSignal();
        started = true; t0 = Date.now();
        log("relay已启动, TURN节点=" + (iceServers ? iceServers.length : 0));
        return true;
      } catch (e) { log("relay启动失败 " + (e.message || e)); return false; }
    },
    stop() { started = false; Object.keys(pcs).forEach(dropPeer); if (ws) ws.close(); ws = null; },
    getRelayBytes() { return relayBytes + fwdBytes; },
    getRecvBytes() { return recvBytes; },
    getPeerCount() { return Object.keys(pcs).filter(id => pcs[id].dc && pcs[id].dc.readyState === "open").length; },
    // 由中继字节推算带宽 kbps(供挖矿40%带宽分)
    getBandwidthKbps() {
      const el = (Date.now() - t0) / 1000;
      if (el <= 0) return 0;
      return Math.round((relayBytes + fwdBytes) * 8 / el / 1000);
    },
    isStarted() { return started; },
  };
})(typeof window !== "undefined" ? window : globalThis);
