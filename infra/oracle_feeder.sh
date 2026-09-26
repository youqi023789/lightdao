#!/bin/bash
# LightDAO §4.10 oracle 外部价格喂价器(验证者提交,合约取中位数)
# 价格源:/etc/lightdao/oracle_price(1e6缩放整数,50000=$0.05);将来可换成行情API抓取脚本写此文件
H=/root/.wasmd; [ -d /home/ubuntu/.wasmd ] && H=/home/ubuntu/.wasmd
ORACLE=wasm1f622csg2af6utlxvxgch2l9qf64ce3s4h5vseaph5ku8vzcgp6qqmsyace
CID=lightdao-mainnet-1
PRICE=$(cat /etc/lightdao/oracle_price 2>/dev/null | tr -d '[:space:]')
[ -z "$PRICE" ] && PRICE=50000
wasmd tx wasm execute "$ORACLE" "{\"submit_price\":{\"price\":\"$PRICE\"}}" \
  --from operator --home "$H" --keyring-backend test --chain-id "$CID" \
  --node tcp://127.0.0.1:26657 --gas 300000 --fees 60000ulight -y \
  >> /var/log/lightdao_oracle_feeder.log 2>&1
