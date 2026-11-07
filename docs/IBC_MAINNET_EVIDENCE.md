
## 2026-11-07 09:39 UTC 主网 ↔ Osmosis 通道实测证据

- 中继身份：主网 `wasm1tplhv9hclk9y3d8ahshf37auwenmn8jx9rw3yp`；Osmosis 侧同一条助记词派生 `osmo1tplhv9hclk9y3d8ahshf37auwenmn8jx8yv5mc`（只放油钱的热钱包，和金库/结算密钥无关）
- 通道：主网 `channel-0` ↔ Osmosis `channel-111104`，端口 `transfer`，版本 `ics20-1`
- 双向 ICS-20 实测：去程 1000 ulight，回程 500（denom `ibc/8B6805CEA56A0A5D…`）；主网 `recv_packet` 事件序列=5→6，交易 `EC0348785ADD56C88275…`，回查在途报文 0 条
- 中继进程：`lightdao-ibc-mainnet.service`（systemd，Restart=on-failure；配 watchdog 双向盯梢）
- 结论：主网跨链从「链上 0 客户端 / 0 通道」变为「1 条通道 OPEN 且双向有回执」；LIGHT 以原生 `ulight` 经 ICS-20 直接搬运，无需 wLIGHT 封装。
