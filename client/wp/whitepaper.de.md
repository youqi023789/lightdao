> Maschinell übersetzt, nicht menschlich geprueft. Bei Abweichungen gilt die chinesische Originalversion.
[中文原文 / Chinese original](/whitepaper.md)

# LightDAO White Paper V2.4 (2026-09-26 Mainnet Live-Version)

> Diese Version basiert auf dem V2.0-Designentwurf, mit „Mainnet Deployment Live“ und „Version Changes“ im Vordergrund und angehängt mit verifizierten On-Chain-Parametern. Der Haupttext (Kapitel 1–12) bleibt gegenüber dem V2.0-Design unverändert; Bei Abweichungen von der tatsächlichen Situation gelten die vorstehenden Hinweise und Anhänge dieses Abschnitts.

## 版本变更(V2.0 → V2.4)
- 2026-11-04 勘误（不改版本号，仍为 V2.4）：附录《主网已验证参数与地址》原写金库 `treasury_multisig` 为 5/7 多签，与正文 §7.2/§7.3/§8.1 的 3/5 冲突，也与链上实测冲突（`{"signers":{}}` 返回 5 个地址，不存在 7 名签名人）；已按正文统一为 3/5，并标明阈值本身不在合约查询接口内、只能由部署记录佐证。同节原写挖矿根为「5/7 验证者多签」，实测可证的只有阈值 5（115 笔 `submit_root` 事件 threshold 全部为 5，实际签名账户恰好 5 个），7 席授权是设计目标、当前无链上证据，已改为相应措辞。

1. **§4.5 Gas 经济:已主网部署并验证**。USD 锚定动态 min-gas-price 与 50% 销毁 / 30% 验证者 / 20% 金库分配于 2026-09-24 经治理提案(v2-lightfee)在高度 58627 上线,7 验证者协调切换、测试网端到端彩排后执行。主网实测:不足额 fee 被拒、足额 fee 按 50/30/20 精确分配。
2. **原生 denom 厘清**:质押/治理/Gas 均为 `ulight`(LIGHT,6 位小数,总供应 25 亿)。genesis 误配的 `stake` 通胀已于 2026-09-24 经治理提案归零(mint inflation=0),LIGHT 发行完全由 mining_reward 合约承担,杜绝双重发行;存量 stake 为待处置的遗留 denom(见附录 C)。
3. **§4.7 WebRTC 中继:已部署**。8 节点 coturn(TURN/STUN,TLS 证书 turn-*.lightdao.net)+ WSS 信令 + REST 临时凭证(HMAC-SHA1);客户端 P2P 数据通道互中继,中继字节计入 40% 带宽贡献;端到端实测经 TURN 中继传输成功。对称 NAT 走 TURN 兜底,失败降级纯验证模式(与 §4.7 一致)。
4. **§4.9 智能钱包:已上线**。Passkey/WebAuthn 无种子登录(PRF 派生密钥 + AES-GCM 密文存储,明文不落地)+ Shamir 3-of-5 社交恢复;助记词作为回退选项保留。
5. **§4.10 价格预言机:喂价已运行**。7 验证者 cron 轮值向 oracle_twap 提交 external_median(当前参考价 50000 = $0.05);链上 TWAP 待 LIGHT/USDC 流动性池建立后启用。v3 升级后 lightfee 直接读 external_median 转动态 min-gas。
6. **参数治理**:v3 升级将 lightfee 的 BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract 迁入链上 paramstore,治理参数提案可运行时调整,无需再协调升级。

## Mainnet-Bereitstellung live (26.09.2026)

- 链 `lightdao-mainnet-1`,7 验证者(JP/KR/SG/US/HK/FR/UK)全部 BONDED、无 jailed;满足 §4.7「验证者<7 不得 TGE」的硬性底线
- 客户端 https://lightdao.net(PWA):Passkey 钱包 + 挖矿 + WebRTC 中继 + 领取,多语言(中/英/西)
- 挖矿闭环:浏览器贡献 → 网关每日定稿 → Merkle 根 5 签上链(阈值 5,链上可查) → 矿工凭 proof 领取;每日根持续提交
- 升级治理:v2-lightfee(已应用 @58627)、mint 归零(已应用)、v3-lightfee(全票通过,高度 118055 自动切换)
- 完整端点/合约地址/升级历史见仓库 `docs/MAINNET_STATUS.md`

---

#LightDAO Whitepaper V2.0

**Volltextüberprüfung und Korrekturlesen optimierte Version (internationaler Web-Client · numerische Prüfung · Prüfung durch Dritte · optimierte Version für Wirtschaftsmodelle) **

Erscheinungsdatum: 4. August 2026

Kernprinzip: Browser sind Knotenpunkte, jeder kann teilnehmen und Gewinne werden nach Regeln geteilt

Rechtliche Positionierung: LIGHT und Sub-Token werden als ökologische Beitragspunkte und SPV-Einkommensverteilungsanspruchsrechtszertifikate positioniert und sind keine Wertpapiere oder Finanzprodukte; Spezifische rechtliche Merkmale unterliegen den gültigen Rechtsgutachten in den jeweiligen Gerichtsbarkeiten.

> Dieses Dokument ist eine verifizierte und optimierte Version des vollständigen Textes des Whitepapers und stellt keine Anlageberatung, Wertpapieremissionsdokumente, Finanzproduktbeschreibungen oder irgendeine Form einer Kapitalgarantieverpflichtung dar. Bitte konsultieren Sie vor der Teilnahme Rechts-, Steuer- und Finanzexperten.

---

## Inhaltsverzeichnis

- Voranmeldung
- Prolog: Die Geschichte von drei Menschen
- Kapitel 1: Die Wahrheit, die wir sehen
- Kapitel 2: LightDAOs Antwort
- Kapitel 3: Compliance und rechtliche Isolation
- Kapitel 4: Technische Architektur
- Kapitel 5: Token-Wirtschaftsmodell
- Kapitel 6: Governance-Mechanismus
- Kapitel 7: Machtkontrollen und -balancen und Rollendefinition
- Kapitel 8: Vertrauens- und Sicherheitsmechanismus
- Kapitel 9: Investitionstätigkeit und Ausstiegsstrategien
- Kapitel 10: Roadmap
- Kapitel 11: Gemeinschaftskultur und Entwicklerökologie
- Kapitel 12: Team und Berater
- Kapitel 13: Risikowarnung und Haftungsausschluss
- Anhang A: Übersichtstabelle der wichtigsten Parameter
- Anhang B: Numerische Ableitung und Verifizierung
- Anhang C: Audit-Korrekturprotokoll
- Anhang D: Kurzreferenzindex der Begriffe

---

## Zusammenfassung

**Was ist LightDAO:** Eine dezentrale autonome Organisation, die es normalen Menschen auf der ganzen Welt ermöglicht, über einen Browser an echten Geschäftsinvestitionen teilzunehmen und Gewinne zu teilen. Benutzer müssen keine Mining-Maschine kaufen, keinen technischen Hintergrund haben oder die Schwelle qualifizierter Investoren erfüllen – mit nur einem Browser und wenig Zeit können Benutzer Netzwerkressourcen beisteuern, um LIGHT-Token-Belohnungen zu erhalten, und durch Governance-Abstimmungen an Investitionsentscheidungen teilnehmen.

**Welches Problem wird gelöst:** Die unteren 50 % der Weltbevölkerung (ungefähr 4 Milliarden Menschen) besitzen nur 2 % des Gesamtvermögens (World Inequality Lab, 2026). Hochwertige Vermögenswerte (Private Equity, Risikokapital) sind von der Schwelle für qualifizierte Anleger (200.000 US-Dollar Jahreseinkommen/1 Million US-Dollar Nettovermögen) ausgeschlossen. Obwohl es im Bereich der Kryptowährungen ein Narrativ der „universellen Beteiligung“ gibt, geht die überwiegende Mehrheit der Token irgendwann auf Null zurück (CoinGecko 2025: 11,56 Millionen Token sind gestorben), und die Beteiligungsquote an der DAO-Governance beträgt nur etwa 3–12 %.

**So lösen Sie das Problem:** Dual-Engineer-Modell – 70 % der Mittel werden in starre Konsumgüter auf Gemeindeebene investiert (Cashflow-Motor) und 30 % werden in Spitzentechnologie investiert (Wachstumsmotor). Investitionen werden über Cayman SPV getätigt und die Gewinne werden gemäß den On-Chain-Regeln verteilt: 40 % an Sub-Token-Inhaber, 30 % zurück in den Tresor zur Reinvestition, 20 % Rückkauf LIGHT zur Vernichtung und 10 % an Versicherungsfonds.

**Kerndaten:**

| Indikatoren | Werte |
|------|------|
| Gesamtmenge an LICHT | 2,5 Milliarden werden niemals ausgegeben |
| Anlagetresor | 850 Millionen (Basiseinsatz ≈ 100 Millionen US-Dollar) |
| Bergbauproduktion | 1 Milliarde, alle 2 Jahre halbiert |
| Veröffentlicht am First Era Day | ≈684.900 Stück (durchschnittlich 6,51/Tag, wenn 100.000 Bergleute arbeiten) |
| Deflationsergebnis | Stoppen Sie das Brennen dauerhaft, wenn die Auflage ≤ 1 Milliarde beträgt (Jahr 11-12 des Basisszenarios) |
| Governance-Schwellenwert | Vorschlag ≥ 5.000 LICHT; Ausschuss ≥ 50.000 LICHT |
| Technologie-Stack | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Prüfer | Anfänglich 21 (mindestens 10), Obergrenze 100 |
| Erstfinanzierung | Niederländische Auktion 15 Millionen US-Dollar + strategische Finanzierung vor TGE 2,25-3,75 Millionen US-Dollar |

**Unterscheidung:** Derzeit das einzige Projekt, das „Null-Schwellen-Web-Mining“ mit „konformer SPV-Entity-Investition“ kombiniert. Anders als Pi Network (kein praktischer Nutzen), Helium (erfordert Hardware im Wert von über 200 US-Dollar) und traditionelles DAO (Elite-Governance mit hohem Schwellenwert).

**Roadmap:** 2026 Q4 Vorbereitung → 2027 Q1-Q2 Entwicklung → Q3 Audit-Test → Q4 TGE online → 2028 Q1 Seed-Benutzer → Q2-Q3 erste Investition → Q4 ab Skalierung.

---

## Voranmeldung

**Dies ist kein Anlagevorschlag**

Die in diesem Whitepaper beschriebenen „ökologischen Belohnungen“ und „Vereinbarungseinkommensverteilung“ sind Anreizvereinbarungen, die durch den endogenen Mechanismus der Vereinbarung generiert werden, und stellen keinerlei Form der Wertpapieremission, des Verkaufs von Finanzprodukten, Kapitalgarantieverpflichtungen oder Anlageberatung dar.

LIGHT und Sub-Tokens haben keinen inneren Wert und der Preis kann auf Null zurückgehen. Bitte konsultieren Sie vor der Teilnahme Ihre eigenen Rechts-, Steuer- und Finanzexperten und tragen Sie die volle Verantwortung für die private Schlüsselverwahrung, Steuererklärung und Teilnahme.

---

## Prolog: Die Geschichte von drei Menschen

Maria arbeitet als Lebensmittellieferantin in Manila, arbeitet 12 Stunden am Tag und verdient etwa 15.000 philippinische Pesos (ca. 270 US-Dollar) pro Monat. Sie wollte in die beliebte Milchtee-Kettenmarke nebenan investieren, aber die andere Partei sagte ihr: „Die Mindestinvestition beginnt bei 25.000 US-Dollar.“ Maria konnte keine 25.000 US-Dollar aufbringen.

Kwame betreibt einen Fahrdienst in Lagos. Er ist optimistisch, was den Weg der künstlichen Intelligenz angeht, und möchte in ein kleines Finanztechnologieunternehmen investieren. Die Institution teilte ihm mit: „Der Mindestzeichnungsbetrag beträgt 100.000 US-Dollar und die Sperrfrist beträgt 5 Jahre.“ Kwame konnte keine 100.000 US-Dollar aufbringen.

Elena ist eine pensionierte Lehrerin in São Paulo mit einer monatlichen Rente von etwa 3.000 brasilianischen Real (ca. 550 US-Dollar). Sie hörte, dass die Kinder ihres Nachbarn Geld verdienten, indem sie in Blockchain-Unternehmen arbeiteten, aber sie konnte das Whitepaper nicht lesen und wusste nicht, wie man professionelle Bergbauausrüstung kauft und konfiguriert.

Die drei repräsentieren die große Mehrheit der einfachen Menschen auf der ganzen Welt: Sie haben das Urteilsvermögen und die Bereitschaft zur Teilnahme, aber es mangelt ihnen an niederschwelligen, transparenten und bezahlbaren Beteiligungskanälen.

LightDAO ist für diese Menschen konzipiert. Mit einem internetfähigen Gerät, einem Browser und einem kleinen Geldbetrag können Sie sich am ökologischen Bauen beteiligen; Durch eine konforme SPV-Struktur haben Benutzer auch die Möglichkeit, indirekt auf die Cashflow-Verteilung hochwertiger Unternehmen und das frühe Wachstum von Spitzentechnologieprojekten zuzugreifen.

---

## Kapitel 1: Die Wahrheit, die wir sehen

### 1.1 Ungleiche Verteilung des globalen Reichtums

Laut dem World Inequality Report 2026 (im Folgenden als „Bericht“ bezeichnet) des World Inequality Lab:

| Daten | Quelle |
|------|------|
| Das Vermögen der reichsten 0,001 % der Weltbevölkerung (etwa 60.000 Menschen) ist etwa dreimal so groß wie das Gesamtvermögen der ärmsten 50 % der Bevölkerung (etwa 4 Milliarden Menschen) | World Inequality Lab, 2026 |
| Das oberste 1 % der Weltbevölkerung kontrolliert 23 % des Gesamteinkommens und 38 % des Gesamtvermögens | World Inequality Lab, 2026 |
| Die oberen 10 % der Weltbevölkerung kontrollieren 53 % des Gesamteinkommens und 75 % des Gesamtvermögens | World Inequality Lab, 2026 |
| Die unteren 50 % der Weltbevölkerung erhalten nur 8 % des Gesamteinkommens und 2 % des Gesamtvermögens | World Inequality Lab, 2026 |

Der „Report“ weist darauf hin: „Die globale Ungleichheit bleibt auf einem historisch extremen Niveau. Ungleichheit entsteht nicht nur durch die natürliche Funktionsweise des Marktes, sondern spiegelt politische Entscheidungen, institutionelle Strukturen und die ungleiche Verteilung wirtschaftlicher und politischer Macht wider.“

**Quellenanmerkung:** Die oben genannten Daten stammen aus dem World Inequality Report 2026 des World Inequality Lab. Der Bericht wurde von Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif und Thomas Piketty geleitet (bestätigt von der offiziellen Website wid.world). Vor der offiziellen Veröffentlichung wird empfohlen, die spezifischen Diagrammnummern im Bericht zusätzlich zu kennzeichnen, um mögliche Fehler bei der Sekundärübersetzung zu reduzieren.

**Prüfung der Datenkonsistenz:** Die oben genannten Anteile weisen mit dem Abschluss des Weltungleichheitsberichts 2022 weiterhin einen vernünftigen Trend auf (die oberen 10 % besitzen 76 % des Gesamtvermögens, die unteren 50 % besitzen 2 % des Gesamtvermögens), und die Abweichung liegt innerhalb des statistisch akzeptablen Bereichs.

### 1.2 Normale Menschen sind von hochwertigen Vermögenswerten ausgeschlossen

In den wichtigsten globalen Jurisdiktionen gelten strenge Schwellenwerte für qualifizierte Anleger für Private Equity und Risikokapital:

**Vereinigte Staaten (SEC Regulation D, Regel 501, 17 CFR §230.501):** Qualifizierte Anleger (akkreditierte Anleger) müssen eine der folgenden Bedingungen erfüllen: Das Jahreseinkommen einer Person beträgt nicht weniger als 200.000 US-Dollar (oder insgesamt nicht weniger als 300.000 US-Dollar mit einem Ehepartner) und hat den Standard in zwei aufeinanderfolgenden Jahren erfüllt; oder das Nettovermögen (ohne Hauptwohnsitz) beträgt nicht weniger als 1.000.000 US-Dollar.

**EU (MiFID II, 2014/65/EU, Anhang II):** Professionelle Anleger (professionelle Anleger) müssen mindestens zwei der folgenden Bedingungen erfüllen – ein Finanzinstrument-Anlageportfolio von nicht weniger als 500.000 Euro; mindestens ein Jahr lang eine berufliche Position in der Finanzbranche innehaben; Durchführung von Großtransaktionen, mindestens 10 pro Quartal.

**Globale Private-Equity-Fonds-Praxis:** Der Mindestzeichnungsbetrag für einen einzelnen Fonds liegt normalerweise zwischen 250.000 und 1.000.000 US-Dollar; Regulierungsvorschriften verbieten im Allgemeinen ausweichende Verhaltensweisen wie „Aktien aufteilen, Schwellenwerte senken und Aufträge im Namen anderer halten“.

| 资产类型 | 普通人能否参与 | 主要原因 |
|----------|---------------|----------|
| 未上市优质企业股权 | 通常不能 | 合格投资者门槛较高，例如美国要求净资产不低于100万美元或年收入不低于20万美元 |
| 风险投资（早期科技公司） | 通常不能 | 主要面向合格投资者开放，单只基金投资金额通常不低于25万美元 |
| 上市公司股票 | 可以，但早期利润通常已被一级市场参与者获取 | 二级市场定价通常包含未来预期，投资者并不直接参与企业早期利润分配 |

### 1.3 Drei große Mängel im Bereich der Kryptowährungen

**Fehler 1: Extrem hohe Ausfallrate**

Laut dem statistischen Jahresbericht 2025 von CoinGecko werden allein im Jahr 2025 etwa **11,56 Millionen Token** auf Null zurückfallen oder den Handel einstellen (einschließlich Long-Tail-Token in jeder Kette). Von den mehr als 20 Millionen Token, die CoinGecko in der Vergangenheit verfolgt hat, befindet sich die überwiegende Mehrheit in einem „toten“ Zustand (kein Handelsvolumen, keine Entwicklungsaktivität und die Preise sind gegenüber historischen Höchstständen um mehr als 99 % gefallen).

Gleichzeitig ist die Ausfallrate traditioneller Aktienmärkte deutlich geringer als die von Kryptowährungen. Laut Bessembinders (2018) Artikel „Do Stocks Outperform Treasury Bills?“ veröffentlicht im „Journal of Financial Economics“, einer Studie über alle US-Aktien von 1926 bis 2016:

| Metriken | Daten | Quellen |
|------|------|------|
| Anteil der Aktien, die das gesamte Nettovermögen schaffen | Nur etwa 4 % (1.092 Aktien) | Bessembinder (2018), JFE 129(3):440-475 |
| Mittlere Aktienrendite über die gesamte Lebensdauer | Negativ (schlechter als Staatsanleihen) | Bessembinder (2018), JFE |
| Etwa 58 % der Lifetime-Performance von US-Aktien | Staatsanleihen schnitten im gleichen Zeitraum schlechter ab | Bessembinder (2018), JFE |
| Anzahl der Token, die im Jahr 2025 auf Null zurückgesetzt werden/den Handel einstellen | ≈11,56 Millionen | CoinGecko Jahresbericht 2025 |

**Vergleichende Schlussfolgerung:** Die Rate des dauerhaften Kapitalverlusts im Kryptowährungsbereich ist viel höher als am traditionellen Aktienmarkt. Obwohl etwa 58 % der einzelnen Aktien am US-Aktienmarkt schlechter abschneiden als Staatsanleihen, können Anleger über Indexfonds dennoch durchschnittliche Marktrenditen erzielen; Auf dem Kryptowährungsmarkt fällt die überwiegende Mehrheit der Token am Ende auf Null zurück, und es mangelt an wirksamen Diversifizierungsinstrumenten, die „Indizes“ ähneln.

**Quellenangabe:** Bessembinder, H. (2018). „Sind Aktien besser als Staatsanleihen?“ *Journal of Financial Economics*, 129(3), 440-475. Arizona State University. Dieses Papier ist ein häufig zitiertes Dokument im Finanzbereich (Zitate >2.000), und die Daten decken alle US-Aktien in der CRSP-Datenbank von 1926 bis 2016 ab. Die Daten von CoinGecko stammen aus dem 2025 Token Survival Status Statistical Report (veröffentlicht im Januar 2026), über den viele Finanzmedien (Sina Finance, Phemex, RBC Crypto) berichtet haben.

**Fehler 2: Der Bergbau ist stark zentralisiert**

Der Bitcoin-Mining hat einen hohen Konzentrationsgrad gezeigt:

| Bergbaubecken | Hash-Rate-Verhältnis |
|------|---------|
| Gießerei USA | Etwa 30 % |
| AntPool | Etwa 19 % |
| ViaBTC | Etwa 14,5 % |
| F2Pool | Etwa 10 % |
| MARA-Pool | Etwa 5 % |
| Die beiden besten Mining-Pools zusammen | Mehr als 50 % |
| Die vier besten Mining-Pools zusammen | Etwa 75 % |

**Quellenanmerkung:** Die oben genannten Daten wurden aus dem monatlichen Hashrate-Verteilungsbericht von 2025 zusammengestellt (CoinGradient 2025.3 „Foundry, Antpool, and Viabtc Dominate Bitcoin Mining“; HashrateIndex „Top 10 Bitcoin Mining Pools of 2025“). Die spezifischen Werte aus verschiedenen Datenquellen können geringfügig variieren (normalerweise innerhalb von ±2 %), aber die Schlussfolgerung, dass „die vier größten Mining-Pools etwa 75 % der Rechenleistung kontrollieren“, spiegelt sich in mehreren gängigen Überwachungsplattformen wider.

**Fehler 3: Die Beteiligungsquote an der DAO-Governance ist extrem niedrig**

| 数据 | 来源 |
|------|------|
| 多数 DAO 的投票参与率仅约3%—12%（中位数约6%） | DeepDAO (2025) 链上治理数据聚合；Boardroom DAO Governance Report (2024) |
| 少数持币者控制绝大多数投票权（治理权力高度集中） | ACM (2024) "DAO Governance: Voting Power, Participation, and Controversy" DOI:10.1145/3777416 |

### 1.4 Kernerkenntnisse

Ich habe ein Urteil, aber keine Eintrittskarte; Ich habe eine Vision, aber kein Recht zu sprechen; Ich möchte teilnehmen, bin aber durch hohe Hürden blockiert.

---

## Kapitel 2: LightDAOs Antwort

### 2.1 Kernpositionierung

LightDAO ist eine nationale autonome Organisation für Investitionen mit On-Chain-Governance als Kern und Compliance-SPV als Träger der Investitionsausführung. Über eine öffentliche Kette, die speziell für leichtgewichtige Webknoten entwickelt wurde, können globale Benutzer mit nur einem Browser an der Netzwerkwartung und Governance-Abstimmung teilnehmen und ökologische Vorteile gemäß Regeln teilen.

### 2.2 Zweimotoriges Modell

| Motor | Anlagerichtung | Ziel | Einkommensmerkmale |
|------|---------|------|---------|
| Motor Eins: Cashflow-Motor (Shou) | Starre Verbrauchsdienstleistungsvermögenswerte auf Gemeinschaftsebene | Kontinuierlichen Cashflow bilden und Gewinne nach Regeln verteilen | Streben Sie nach relativer Stabilität, versprechen Sie aber keine festen Erträge |
| Motor 2: Wachstumsmotor (Angriff) | Spitzentechnologieunternehmen | Erhalten Sie Aktienwertsteigerungen und Exit-Renditen | Hohe potenzielle Flexibilität, kann aber auch mit Verlusten oder Ausstiegsfehlern rechnen |

**Allokationsdisziplin:** Grundsätzlich sollten 70 % der Mittel Vermögenswerten mit stabilem Cashflow und 30 % wachstumsstarken Zielen zugewiesen werden.

**Wachstumspfad der Investitionsskala:** Die Größe einer einzelnen Investition wächst dynamisch mit dem Preis von LIGHT und der Tresorkapazität – die Startphase (LIGHT 0,02–0,05 US-Dollar) eignet sich für kleine Vermögenswerte auf Gemeindeebene von 2,55 Mio. US-Dollar bis 6,37 Mio. US-Dollar; Die Wachstumsphase (0,05–0,30 $) umfasst regionale Ketten und Seed-A-Runden von 6,37 Mio. $ bis 38,25 Mio. $ (Benchmarking des unteren Mittelmarkts) PE); im ausgereiften Stadium (0,30–1,00 US-Dollar) erreicht es das mittlere Markt-KGV-Niveau von 38,25 bis 127,5 Millionen US-Dollar; In der Größenordnung (ab 1,00 US-Dollar) kann das Unternehmen umfangreiche Akquisitionen und Pre-IPO-Investitionen von mehr als 127,5 Millionen US-Dollar durchführen. Harte Einschränkungen: Eine einzelne Transaktion darf 15 % des verbleibenden Betrags der Anlagekasse nicht überschreiten (Einzelheiten siehe Kapitel 9).

**Das erste Zielpositionierungsprinzip:** Anstatt einen bestimmten Firmennamen vorauszusetzen, etablieren Sie zunächst einen Screening-Rahmen – geben Sie den starren Verbraucherservice-Assets auf Gemeindeebene Vorrang, die ein bewährtes Einzelgeschäfts-Wirtschaftsmodell, stabile Cashflow-Aufzeichnungen (die EBITDA-Marge in den letzten drei Jahren beträgt nicht weniger als 10 % und die Volatilität zwischen den Jahren beträgt nicht mehr als 15 %) und einen klaren regionalen Expansionspfad erfordern. Das konkrete Ziel wird durch Community-Vorschläge bestimmt.

### 2.3 Kernwertversprechen

**Der Browser ist der Knotenpunkt** – Es ist nicht erforderlich, eine Mining-Maschine zu kaufen oder über einen professionellen technischen Hintergrund zu verfügen. Sie können sich an Netzwerkbeiträgen beteiligen, indem Sie die offizielle Webplattform besuchen.

**Jeder kann teilnehmen** – Nach Erreichen der Governance-Schwelle können auch Inhaber kleiner LIGHT-Beträge an der Abstimmung teilnehmen, um gemeinsam über die Richtung der Mittelzuteilung zu entscheiden.

**Gewinnbeteiligung gemäß Regeln** – Die Betriebsgewinne der investierten Unternehmen und die Exit-Renditen von Technologieprojekten werden gemäß den On-Chain-Regeln und SPV-Vereinbarungen verteilt.

### 2.4 Slogan

„Ihr Browser kann auch das Tor zu hochwertigen Assets sein.“

### 2.5 Analyse der Wettbewerbsproduktdifferenzierung

| Dimension | Pi-Netzwerk | Helium | Traditionelles DAO (MakerDAO usw.) | LightDAO |
|------|-----------|--------|-------|----------|
| Teilnahmemethode | Klicken Sie auf mobile APP | Hardware-Hotspot kaufen (200–1000 $) | Token kaufen + On-Chain-Vorgang | Browserzugriff, keine Hardwarekosten |
| Eintrittskosten | Null (aber kein praktischer Nutzen) | Hoch (Hardware + Installation) | Mittel bis hoch (Governance-Tokens müssen erworben werden) | Zero (nur ein Browser) |
| Gesamtzahl der Token | 100 Milliarden | 223 Millionen | Variiert | 2,5 Milliarden |
| Tatsächliche Investitionsfunktion | Keine | Keine (nur Netzabdeckung) | Ja (aber die Schwelle ist extrem hoch) | Ja (SPV-Struktur, jeder kann teilnehmen) |
| Einnahmequelle | Unklar | Netzwerknutzungsgebühr | Vertragsgebühr | Unternehmensgewinn + Exit-Rendite + Gasgebühr |
| Rechtliche Isolation | Keine | Keine | Einige ja | Cayman SPV+ZK-KYC |
| Governance-Beteiligungsquote | Extrem niedrig (keine wesentliche Governance) | Niedrig | Etwa 6 % | Ziel >15 % (zweidimensionale Abstimmung + Anreize) |

**Der Hauptunterschied von LightDAO:** Es ist derzeit das einzige Projekt, das „Null-Schwellen-Web-Mining“ mit „konformer SPV-Entity-Investition“ kombiniert. Benutzer steuern nicht nur Netzwerkressourcen bei, um Token-Belohnungen zu erhalten, sondern beteiligen sich auch direkt an echten Unternehmensinvestitionsentscheidungen durch Governance-Abstimmungen und Anteile an Betriebsgewinnen.

> **[Terminologie in diesem Kapitel]**
> **DAO** (Decentralized Autonomous Organization): Eine Organisationsform, in der Governance-Regeln durch Smart Contracts kodiert werden und kollektive Entscheidungen von Token-Inhabern getroffen werden. Es gibt keine traditionelle Unternehmenshierarchie.
> **SPV** (Special Purpose Vehicle): eine unabhängige juristische Person (normalerweise auf den Kaimaninseln registriert), die für bestimmte Transaktionen oder Investitionen gegründet wurde, um eine Risikoisolierung zu erreichen – die Schulden und rechtlichen Verbindlichkeiten des SPV werden nicht an die DAO selbst übertragen.
> **DePIN** (Decentralized Physical Infrastructure Network, dezentrales physisches Infrastrukturnetzwerk): Ein Netzwerkmodell, das Token verwendet, um Benutzer dazu zu ermutigen, physische Ressourcen (Bandbreite, Speicher, Rechenleistung, drahtlose Abdeckung usw.) zum Aufbau der Infrastruktur beizutragen.
> **Lower Middle Market PE** (Downstream Mid-End Private Equity): ein Marktsegment der globalen Private-Equity-Branche. Der Umfang einer einzelnen Transaktion beträgt normalerweise 10 bis 100 Millionen US-Dollar, und das EBITDA des Zielunternehmens liegt zwischen 2 und 15 Millionen US-Dollar.

---

## Kapitel 3: Compliance und rechtliche Isolation

### 3.1 SPV-rechtliche Isolationsschicht

DAO ist nicht direkt an einem physischen Unternehmen beteiligt. Alle externen Investitionen werden über auf den Cayman-Inseln gegründete Zweckgesellschaften (Special Purpose Vehicles, SPVs) getätigt.

| Designpunkte | Beschreibung |
|---------|------|
| SPV-Charta | Es besteht eindeutig Einigkeit darüber, dass der Betrieb des SPV im Einklang mit dem wirksamen Beschluss des DAO | steht
| Rechtliche Definition von Sub-Tokens | Unter-Tokens sind „SPV-Income-Distribution-Claim-Rights-Zertifikate“, die lediglich die Ausschüttungsqualifikationen für zukünftige Cashflows darstellen |
| Keine Aktionärsrechte | Verfügt über keine Corporate-Governance-Rechte, Liquidationspräferenzen oder Aktionärsrechte |
| SPV-Direktoren | werden von unabhängigen Dritten bedient; DAO kann Direktoren durch die Verabschiedung eines gültigen Beschlusses ersetzen |
| Fondsaufsicht | Bankkonten werden von lizenzierten Depotbanken überwacht und Geldtransfers müssen eine Mehrfachsignatur- und Compliance-Verifizierung bestehen |
| SPV-Streitbeilegung | Die SPV-Charta sieht eine Schiedsklausel (SIAC oder ICC) vor, und die DAO kann ein Schiedsverfahren durch einen Governance-Beschluss einleiten |

### 3.2 Optionale Verifizierung und Datenschutz

**Für die Teilnahme am Protokoll selbst ist keine Identifizierung erforderlich. ** Besuchen Sie Webseiten, erstellen Sie Wallets, tragen Sie Ressourcen bei, erhalten Sie LIGHT, initiieren Sie Governance-Abstimmungen und nehmen Sie daran teil – während des gesamten Prozesses müssen keine Dokumente hochgeladen werden, und es werden keine personenbezogenen Daten (PII) in der Kette gespeichert.

Nur wenn ein Nutzer einen regulierten Drittanbieterdienst aktiv nutzt, ist die Überprüfung erforderlich, dass der Dienst selbst gesetzeskonform funktionieren muss. Diese Überprüfung wird vom Servicepartner erfasst, durchgeführt und aufbewahrt. LightDAO erhebt, überträgt oder speichert keine Daten:

| Szenario | Wer führt die Verifizierung durch | Was der Benutzer tun muss |
|---|---|---|
| Kauf/Verkauf über Fiat-Kanäle | Lizenzierte Dritte (wie MoonPay, Ramp Network, Transak) | Schließen Sie den Compliance-Prozess gemäß den eigenen Anforderungen des Dienstleisters ab |
| Sub-Tokens (Investmentaktienzertifikate) austauschen | Abhängig von den Anforderungen des jeweiligen Produkts und seines Dienstleisters | Sie können nur Mining und Governance durchführen, ohne jegliche Überprüfung |
| Auf Bankkarte/lokale Zahlung abheben | Auszahlungs- und Zahlungsdienstleister | Schließen Sie den vom Dienstanbieter geforderten Compliance-Prozess ab |

Grundprinzipien: **Standardmäßig keine Überprüfung; Die Überprüfung erfolgt erst in dem Moment, in dem der Nutzer den regulierten Dienst aktiv betritt, und wird vom Diensteanbieter getragen. **Niemand wird das Recht verlieren, zu schürfen, zu behalten, zu übertragen oder abzustimmen, weil die Überprüfung fehlschlägt.

> Technologie vorbehalten: Wenn für eine bestimmte Art von Vermögenswerten in Zukunft Qualifikationsschwellenwerte erforderlich sind, verfügen Benutzer über ihre eigenen Anmeldeinformationen in Form eines wissensfreien Nachweises (ZK), und die Kette überprüft nur, „ob diese erfüllt sind“, ohne jegliche Identitätsinformationen – dies ist Teil der Roadmap und keine aktuelle Anforderung.

### 3.3 Erklärung zur steuerlichen Verantwortung

Die Vereinbarung sieht keine Steuererklärungsdienste vor und die Steuerpflichten aller ökologischen Belohnungen und damit verbundenen Einnahmen werden von den Nutzern selbst getragen. Benutzer sollten sich an die relevanten Gesetze und Vorschriften ihres steuerlichen Wohnsitzes halten.

### 3.4 Benutzerzugang: offen für alle

**Keine Schwelle für Registrierung und Teilnahme**: Es sind keine E-Mail-Adresse, Mobiltelefonnummer, soziales Konto oder Identitätsnachweis erforderlich; Sie benötigen lediglich ein Gerät, das eine Webseite öffnen kann. LightDAO** schränkt die Benutzerbeteiligung in keinem Land oder in keiner Region aktiv ein und setzt auch kein Geofencing ein. **

Die einzigen externen Einschränkungen ergeben sich aus Diensten Dritter: Wenn das Gesetz eines bestimmten Ortes andere Anforderungen für bestimmte Dienste (z. B. Ein- und Auszahlungen in Fiat-Währung) vorsieht, werden diese Dienste von lokal lizenzierten Institutionen gemäß dem Gesetz auf ihrer Seite durchgeführt und haben keinen Einfluss auf die Nutzung von On-Chain-Funktionen (Mining, Halten, Transfers, Abstimmungen, Vorschläge) durch irgendjemanden.

Wenn eine bestimmte Gerichtsbarkeit in Zukunft explizite Verbotsvorschriften erlässt, lautet die Antwortsequenz des Protokolls:

1. Stellen Sie zunächst sicher, dass die Vermögensverfügungsrechte bestehender Benutzer nicht beeinträchtigt werden – Vermögenswerte in der Kette können nicht eingefroren werden und jeder kann sein LIGHT und seine Untertoken jederzeit übertragen;
2. Bleiben Sie über mehrere Front-End-Portale (einschließlich IPFS-Spiegel und Community-Spiegel) zugänglich.
3. Im letzten Schritt erfolgt die Anpassung des verfügbaren Umfangs der **Dienste Dritter** im Rahmen der Rechtsdurchsetzung.

Mit einem Wort: *** Einschränkungen können nur Dienstleistungen betreffen, nicht Menschen. **

### 3.5 Ein- und Auszahlungen in legaler Währung und kettenübergreifende Kanäle

**Fiat-Währungskanal (Drittanbieter-Service-Aggregation):** Das Protokoll selbst betreibt keine legalen Ein- und Auszahlungsdienste in Währungen, aber die Webplattform integriert konforme Drittanbieterkanäle (MoonPay, Ramp Network, Transak usw.), die wichtige Märkte in Nordamerika, Europa, Südostasien und Lateinamerika abdecken; die lokale P2P-Marktaggregation deckt Afrika und Südasien ab; Abhebungen unterstützen lokale Zahlungsmethoden wie GCash, M-Pesa, Pix und GrabPay.

**Cross-Chain-Bridge und LIGHT-Erwerbskanäle:** Integrierte AMM-Transaktionen in der LightDAO-Kette nach TGE; Interoperabilität mit dem Cosmos-Ökosystem durch IBC; Planung für wLIGHT (Ethereum/Solana) ab dem 6. Monat; Antrag auf CEX-Notierung ab dem 6. Monat je nach Compliance. Die Cross-Chain-Brücke wird von einem unabhängigen Dritten betrieben und es ist ein unabhängiger Prüfbericht erforderlich, bevor die Brücke online geht.

### 3.6 Compliance-Erklärung zum Einladungsmechanismus (Anti-MLM-Analyse)

Der Einladungsanreiz von LightDAO ist **Single-Layer-Sharing** (nur direkte Einladende erhalten einen festen Anteil der Mining-Belohnungen des Eingeladenen) und verfügt nicht über die Kernfunktionen von Multi-Level-Marketing (MLM): keine mehrstufige rekursive Provision; Die Einnahmen stammen aus der Freigabe voreingestellter Token im Protokoll und nicht aus dem Kapital des Neuankömmlings. Für die Teilnahme am Bergbau fallen keine Kosten und keine Teilnahmegebühr an. Diese Struktur ähnelt eher den „Belohnungen für Empfehlungen von Open-Source-Projektmitwirkenden“. Vor der formellen Inbetriebnahme wird ein zugelassener Anwalt im Zielmarkt beauftragt, spezielle Compliance-Gutachten abzugeben.

> **[Terminologie in diesem Kapitel]**
> **KYC** (Know Your Customer, Know Your Customer): Ein Compliance-Prozess für Finanzinstitute zur Überprüfung der Benutzeridentität, der in der Regel die Vorlage von Ausweisdokumenten, Adressnachweisen usw. erfordert.
> **ZK-KYC** (Zero-Knowledge KYC, Zero-Knowledge Proof KYC): Benutzer müssen im Rahmen der Vereinbarung keine spezifischen personenbezogenen Daten offenlegen und verwenden Kryptografie nur zum Nachweis der Compliance-Überprüfungsmethode „Ich erfülle bestimmte Bedingungen“ (z. B. Alter ≥ 18 Jahre, nicht sanktionierte Nationalität). In der Kette werden keine Originaldokumentdaten gespeichert.
> **PII** (persönlich identifizierbare Informationen, persönlich identifizierbare Informationen): Daten, die eine bestimmte natürliche Person einzeln oder in Kombination identifizieren können, wie z. B. Name, ID-Nummer, Adresse, biometrische Merkmale usw.
> **Reg D / Reg S** (Regulation D/Regulation S des U.S. Securities Act): Reg D erlaubt Privatplatzierungen an „qualifizierte Anleger“ in den Vereinigten Staaten ohne öffentliche Registrierung (Definitionsstandard Regel 501); Reg S erlaubt den Verkauf von Wertpapieren an Personen außerhalb der Vereinigten Staaten, ohne dass eine US-Registrierungspflicht besteht.
> **MiFID II** (EU-Richtlinie über Märkte für Finanzinstrumente II, 2014/65/EU): EU-Finanzregulierungsrahmen, dessen Anhang II die Identifizierungskriterien für „professionelle Anleger“ definiert (500.000 € Finanzinstrumentenportfolio, 1 Jahr Erfahrung in der Finanzbranche, 10 Großtransaktionen pro Quartal, Erfüllung der zweiten Anforderung).
> **MLM** (Multi-Level-Marketing, Multi-Level-Marketing): ein Geschäftsmodell durch mehrstufige rekursive Provisionen (Downline-Entwicklung, Downline-Entwicklung und Upline-Provisionen Schicht für Schicht). Es unterscheidet sich wesentlich von einschichtigen Empfehlungsbelohnungen – LightDAO ist nur einschichtig (A lädt B ein, A erhält einen Anteil von B; B lädt C ein, A erhält keinen Anteil von C).
> **IBC** (Inter-Blockchain Communication, kettenübergreifendes Kommunikationsprotokoll): der native kettenübergreifende Standard des Cosmos-Ökosystems, der die sichere Übertragung von Vermögenswerten und Nachrichten zwischen verschiedenen Blockchains ermöglicht, ohne dass ein zentraler Vermittler erforderlich ist.

---

## Kapitel 4: Technische Architektur

### 4.1 Was ist die öffentliche Kette?

Die öffentliche Kette von LightDAO kann als „öffentliches Kontobuch mit transparenten Regeln verstanden werden, das nicht nach Belieben manipuliert werden kann“: Governance-Regeln sind in den Code geschrieben, und die Abstimmungsaufzeichnungen, Kapitalflüsse und Gewinnverteilungen aller Personen können in der Kette abgefragt und überprüft werden.

### 4.2 Technische Parameter und Auswahldemonstration

| Technische Artikel | Auswahl | Auswahlbasis |
|--------|------|---------|
| Grundgerüst | Cosmos SDK | Modulare Architektur, Verifizierung mehrerer Produktionsketten |
| Konsensmechanismus | Tendermint PoS | Sofortige Gewissheit; Die Blockgenerierung dauert 1,5–2 Sekunden. BFT-Fehlertoleranz ≤ 1/3 böse |
| Intelligente Verträge | CosmWasm | WebAssembly + Rust, Speichersicherheit zur Kompilierungszeit |
| Kettenübergreifende Fähigkeiten | IBC-Protokoll | Nativer kettenübergreifender Cosmos-Standard |
| Front-End-Interaktion | Progressive Web-App (PWA) | Browser läuft, Desktop/mobil adaptiv, keine Installation erforderlich |

### 4.3 Leichter Node-Mining-Mechanismus und Anreizmodell

#### 4.3.1 Mining-Methode

Benutzer greifen über einen Browser auf die offizielle Webplattform zu, erstellen eine Wallet und klicken auf „Mining starten“. Während des Mining-Prozesses tragen Benutzer über den Browser Netzwerkbandbreite (Datenweiterleitung und -überprüfung) und lokale Rechenressourcen (leichte Block-Header-Überprüfung) bei und sind nicht auf hochenergetische Rechenleistung angewiesen.

**Webseitige Technologieimplementierung:** WebRTC-Datenkanal P2P-Relay; Verifizierung des Web Worker-Hintergrundblock-Headers; Offline-Cache und Heartbeat des Service Workers; Lange WebSocket-Verbindung.

**Anpassung an mobile Browser:** Einführung eines kumulativen gültigen Sitzungssystems (4 Stunden pro Tag = 100 % Punktzahl); Es werden keine Punkte abgezogen, wenn die Verbindung innerhalb von 5 Minuten nach der Trennung wiederhergestellt wird. Benutzer, die PWA installiert haben, erhalten einen zusätzlichen Online-Zeitbonus von 10 %; delegierter Online-Mechanismus (70 % für den Delegierten/30 % für den Relay-Knoten).

#### 4.3.2–4.3.3 Anreizsystem und Drei-Motoren-Modell

Es übernimmt das dreimotorige Modell „PoC-Beitragsnachweis + Einladungsspaltungsanreiz + Verhaltensbonusanreiz“.

#### 4.3.4 Beitragsdimensionen und -gewicht

| Beitragsdimension | Gewicht | Messmethode |
|---------|------|---------|
| Bandbreiten-Relay-Beitrag | 40 % | Verhältnis von Upload-Relay-Verkehr zum Verifizierungsdatenvolumen |
| Effektive Sitzungsdauer | 30 % | Tägliche kumulative effektive Sitzungen (4 Stunden = 100 %) |
| Beitrag zur Blockverifizierung | 20 % | Anzahl und Genauigkeit effektiv verifizierter Blockheader |
| Netzwerkstabilität | 10 % | Verbindungsverzögerung, Paketverlustrate, Antwortzeit |

#### 4.3.5 Formel zur Belohnungsberechnung

**Tägliche Mining-Belohnung = BaseReward × Beitragsgewichtungspunktzahl × (1 + Einladungsbonus) × (1 + Verhaltensbonus)**

- BaseReward = Gesamtbetrag, der vom gesamten Netzwerk an diesem Tag freigegeben wurde ÷ Gesamtzahl der aktiven Miner an diesem Tag
- Einladungsbonus = effektive Anzahl der Eingeladenen × 1 % (Obergrenze 20 %)
- Verhaltensbonus = 5 % Abstimmungsbeteiligung + 5 % Inhaltsbeitrag + 5 % Community-Aktivität + 5 % Knotenverifizierungsqualität (Obergrenze 20 %)
- Voller Bonuskoeffizient = (1+20 %) × (1+20 %) = 1,44-fach

#### 4.3.6 Anreize zur Spaltung einladen

| Ebene | Gültige Anzahl Einladungen | Einladungsanteilsverhältnis | Zusätzliche einmalige Belohnung | Governance-Gewichtsbonus |
|------|------------|------------|--------------|------------|
| Bergleute | 0 Personen | — | Grundlegende Bergbaubelohnungen | Keine |
| Prediger | Nicht weniger als 3 Personen | 10 % | 100 LICHT | Keine |
| Botschafter | Nicht weniger als 10 Personen | 15 % | 500 LIGHT + Abzeichen an der Kette | Stimmgewicht +5 % |
| Partner | Nicht weniger als 50 Personen | 20 % | 2.500 LIGHT + Abzeichen an der Kette | Stimmgewicht +10 % |

Der Governance-Gewichtungsbonus und der Reputationsbonus (bis zu +30 %) sind unabhängig voneinander stapelbar, mit einer Gesamtobergrenze von +40 %. Der Einladungsbonus erreicht seinen Höhepunkt bei 20 Personen (20×1%=20%).

#### 4.3.7 Anti-Cheating-Mechanismus

Erkennung der Integrität der Browserumgebung (Canvas/WebGL/WebRTC-Fingerabdruck), Pakettiefenerkennung, IP-Clustering und Verhaltensmusteranalyse, mehrdimensionaler Verhaltensfingerabdruck (Mausbewegung/Tastaturrhythmus/Scrollverhalten), Überprüfung der Authentizität der Einladungsadresse. Kosten für den Anti-Sybil-Angriff: 50.000 bis 200.000 US-Dollar für die Erstellung von 10.000 unabhängigen Fingerabdrücken; Zielerkennungsrate >90-95 %.

### 4.4 LIGHT-Token-Funktionsmatrix

Netzwerktreibstoff (Gasgebühr), Governance-Rechte (Abstimmung/Vorschlag/Kampagne), Pfandbindung (Marge/Kampagne/Verifizierer), Investitionsaustausch (Sub-Tokens), ökologische Anreize (Bergbau/Einladung/Verhalten), zukünftige Erweiterung (dApp/NFT/Cross-Chain).

### 4.5 Gasgebühren- und Transaktionsgebührenmechanismus

**Designprinzip:** Die Gasgebühr ist im USD-Äquivalent verankert und der tatsächlich berechnete LIGHT-Betrag wird automatisch alle 24 Stunden vom On-Chain-Orakel umgerechnet (Abschnitt 4.10). Dadurch wird sichergestellt, dass die tatsächlichen Zahlungskosten des Benutzers (in US-Dollar) unabhängig davon, ob der Preis von LIGHT steigt oder fällt, stabil bleiben, wodurch das Problem vermieden wird, dass „der Währungspreis um das Hundertfache steigt → die Überweisungsgebühr beträgt 10 US-Dollar“ oder „der Währungspreis um 90 % sinkt → kostenlose Ticketeinlösung“.

**USD-verankertes Gasgebührenziel:**

| Transaktionstyp | USD-Äquivalent-Ziel | Echte Sammlung, wenn LIGHT=$0,05 | Echte Sammlung, wenn LICHT=0,50 $ | Designabsicht |
|---------|------------|------------------|------------------|----------|
| Normale Überweisung | 0,001 $ | 0,02 LICHT | 0,002 LICHT | Extrem niedriger Schwellenwert, um sicherzustellen, dass Benutzer mit kleinen Beträgen frei Geld überweisen können |
| Governance-Abstimmung | 0,005 $ | 0,10 LICHT | 0,01 LICHT | Etwas höher als die Überweisung, um ein kostenloses Vote-Brushing zu verhindern |
| Einen Vorschlag einreichen | 0,10 $ | 2.0 LICHT | 0,2 LICHT | Mit dem Pfandsystem zusammenarbeiten, um die Ernsthaftigkeit des Vorschlags zu erhöhen |
| Sub-Token-Austausch | 0,50 $ | 10,0 LICHT | 1,0 LICHT | Höhere Gebühren entsprechend der Schwere von Großoperationen |
| Mining-Heartbeat-Reporting | 0 $ (kostenlos) | 0 | 0 | Für Bergbaubeiträge wird kein Gas erhoben, wodurch eine kostenfreie Teilnahme gewährleistet ist |

**Dynamische Konvertierungsregeln:**

- Tatsächliche Gasgebühr (LIGHT) = USD-Ziel ÷ Oracle 24h TWAP-Preis
- Das Umrechnungsverhältnis wird durch den oracle_twap-Vertrag automatisch alle 24 Stunden aktualisiert (Block UTC 00:00).
- Legen Sie eine Untergrenze fest: Die Gasgebühr für jede Transaktionsart darf nicht weniger als 0,001 LIGHT betragen (um zu verhindern, dass Gas auf Null zurückfällt, wenn der Preis Null ist).
- Legen Sie eine Obergrenze fest: Die Gasgebühr für jede Transaktionsart darf nicht höher als 100 LIGHT sein (um zu verhindern, dass übermäßig viel Gas die Nutzung behindert, wenn der Preis extrem niedrig ist).
- Der USD-Zielwert selbst kann durch die Governance über Mikrovorschläge angepasst werden (Marge von 100 USD).

**Regeln zur Zuteilung der Gasgebühren:**

| Ziel | Anteil | Funktion |
|------|------|------|
| Dauerhafte Zerstörung | 50 % | Anhaltende Deflation, Verringerung des Zirkulationsangebots |
| Validator-Belohnungen | 30 % | Anreize für Validatoren schaffen, die Netzwerksicherheit aufrechtzuerhalten und Blöcke zu erzeugen |
| Ökologische Schatzkammer | 20 % | Ergänzende Entwicklerfinanzierung und kommunale Betriebsfonds |

**Schätzung der Gasgebührendeflation:** Unter der Annahme von durchschnittlich 100.000 täglich aktiven Transaktionen und einer durchschnittlichen Gasgebühr von 0,005 US-Dollar (hauptsächlich Abstimmungen und Überweisungen) beträgt der Gegenwert der pro Tag zerstörten USD = 100.000 × 0,005 US-Dollar × 50 % = 250 US-Dollar/Tag. Wenn LICHT = 0,05 $, entspricht dies 5.000 LICHT/Tag≈1,825 Millionen/Jahr; Wenn LICHT = 0,50 $, entspricht dies 500 LICHT/Tag≈182.500/Jahr. Die Menge an LIGHT mit Gasgebührendeflation nimmt mit steigendem Preis ab (der USD-Äquivalent ist konstant), aber die Unterstützung des Preises spiegelt sich im „kontinuierlichen Kauf des Äquivalents“ wider – jede Transaktion zerstört Token zu einem festen USD-Kurs.

### 4.6 Verifier-System

| Abmessungen | Validatoren | Leichte Knoten (Browser-Miner) |
|------|--------|-------------------|
| Verantwortlichkeiten | Blockgenerierung, Konsens, vollständiger Knoten | Blockheader-Überprüfung, Datenweiterleitung |
| Abstecken | Mindestens 500.000 LICHT | Keine |
| Einkommen | Gasgebühr 30 % + täglicher Freigabepool 5 % | PoC-Mining-Belohnungen (täglicher Release-Pool 95 %) |
| Menge | Anfänglich 21, Obergrenze 100 | Keine Obergrenze |
| Schlitzen | 5 % Strafe für Doppelsignatur + 180-Tage-Sperre | Keine |

**Start in Stufen (BFT-Fehlertoleranz: N≥3f+1):**

| Phase | Anzahl der Validatoren | Fehlertoleranz f | Kettenstoppbedingungen | Benutzererfahrung |
|------|-----------|-------|-----------|----------|
| Testnet (3 Monate vor TGE) | 7 | 2 | 3 gleichzeitig offline | Interne Tests können kurze Unterbrechungen tolerieren |
| Mainnet TGE | Mindestens 10, Ziel 21 | 3-6 | 4-7 gleichzeitig offline | Gelegentliche Unterbrechungen (<1 Mal pro Quartal) zur Glättung |
| Zur Wahl ab dem 7. Monat geöffnet | 21-100 | 6-33 | 7-34 gleichzeitig offline | Benutzer ist sich dessen nicht bewusst |

**Klares Fazit: TGE darf nicht ausgeführt werden, wenn <7 Validatoren vorhanden sind. ** Weniger als 7 bedeutet f ≤ 1. Jeder einzelne Fehler führt zum Herunterfahren der gesamten Kette, was für technisch nicht versierte Benutzer einer „Nichtverfügbarkeit des Produkts“ gleichkommt.

### 4.7 Netzwerkinfrastrukturschicht

Die Validator-Knoten übertragen WebSocket-Zugriffs-Gateways auf verteilte Weise (jeder Validator hat eine Obergrenze von 50.000 Verbindungen); Die P2P-Signalisierung wird vom Validator + Community-Relay-Knoten bereitgestellt; Heartbeat Merkle-Aggregation übermittelt nur den Root-Hash pro Block (O(1) On-Chain-Overhead); Das Frontend wird über IPFS+CDN verteilt.

P2P-Netzwerk: WebRTC ICE-Framework (STUN-Priorität/TURN-Fallback); etwa 70–80 % der Benutzer können eine direkte Verbindung herstellen, 20–30 % der symmetrischen NAT-Benutzer passieren TURN Relay; Wenn P2P fehlschlägt, wird es auf den „reinen Authentifizierungsmodus“ herabgestuft.

Leistungsspezifikationen: Theoretische TPS 1.000–3.000; Blockgröße 2 MB (Governance einstellbar); Lichtknotensynchronisation <30 Sekunden; Millionen Knoten-Heartbeat Merkle-Aggregation <500 ms.

### 4.8 Mechanismus zur Überprüfung des Beitragsnachweises

Dreistufige Verifizierungsarchitektur: (1) Zufalls-Cross-Sampling-Challenge des Verifizierers (5 % Knoten alle 10 Minuten, 30 Sekunden Reaktionszeit); (2) gegenseitige P2P-Peer-Verifizierung (8–16 Peers zeichnen unabhängig voneinander das Datenaustauschvolumen auf, nehmen Sie den Median); (3) Merkle-Aggregation in der Kette (jeder Block übermittelt die Beitragsbewertung an Root, Benutzer können sich über Merkle Proof selbst überprüfen). Dreimal hintereinander nicht bestanden → die Tagespunktzahl wird auf Null zurückgesetzt; Insgesamt 5 Mal innerhalb von 7 Tagen → Es wird eine Anti-Cheating-Überprüfung ausgelöst.

### 4.9 Wallet- und Schlüsselverwaltung

Dreistufige Architektur: (1) Eingebettetes Smart Wallet (Passkey/WebAuthn, keine mnemonische Phrase erforderlich, Zielgruppe sind 80 %+ Benutzer); (2) Social-Recovery-Wallet (3-5 Restauratoren, Shamir-Sharding, 2/3 Mehrheitsbestätigung); (3) Selbstgehostetes Wallet (kompatibel mit BIP-39-Mnemonik und Hardware-Wallet). Die Gasgebühren für die ersten 100 Transaktionen neuer Nutzer werden vom Ökofonds übernommen (Paymaster-Modell).

### 4.10 Preis Oracle

On-Chain-TWAP (zeitgewichteter 30-Tage-Durchschnittspreis des LIGHT/USDC-Pools) ist die Hauptpreisquelle; 3+ externe DEX/CEX-Aggregation wird ergänzt (Validatoren reichen abwechselnd ein, nehmen den Median); Abweichungen >±15 % lösen Ausnahmeflags aus; Einzelblockabweichungen >5 % werden nicht in TWAP (Anti-Flash-Loan-Manipulation) einbezogen; Fallback auf reines On-Chain-TWAP, wenn alle externen Orakel ausfallen.

### 4.11 Architektur des Smart Contract-Moduls

10 Kernverträge: Light_token, Mining_Reward, Governance, Treasury_Multisig, Subtoken_Factory, Oracle_Twap, Anti_Fraud, Validator_Registry, Vesting, Insurance_Fund. Der Kernvertrag muss vor TGE eine formelle Prüfung durchlaufen.

### 4.12 Protokoll-Upgrade und Chain Governance

Level-4-Upgrade: L1-Parameteranpassung (Governance-Abstimmung 24–72 Stunden) → L2-Vertragsmigration (großer Vorschlag + Prüfung + 72-Stunden-Verzögerung) → L3-Konsensänderung (66 % bestanden + 2/3 Validierungssignale + 7-tägiger Fork-Schutzzeitraum) → L4-Notfallreparatur (Suspendierung des Schattenausschusses + Multi-Signatur-Hotfix + 72-Stunden-Ratifizierung).

> **[Terminologie in diesem Kapitel]**
> **Cosmos SDK**: Ein modulares Blockchain-Entwicklungsframework, das es Entwicklern ermöglicht, benutzerdefinierte öffentliche Ketten wie Bausteine zusammenzustellen. Mehrere Produktionsketten (wie Cosmos Hub und Osmosis) haben seine Reife bestätigt.
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Ein Konsensmechanismus, bei dem Validatoren das Recht erhalten, Blöcke zu produzieren, indem sie Token verpfänden (anstatt um Rechenleistung zu konkurrieren). Bietet „sofortige Endgültigkeit“ – sobald ein Block übermittelt wurde, kann er nicht mehr zurückgesetzt werden.
> **BFT** (Byzantine Fault Tolerance, Byzantine Fault Tolerance): Ein Mechanismus in einem verteilten System, der tolerieren kann, dass einige Knoten Böses tun oder nicht richtig funktionieren, und dennoch einen korrekten Konsens erzielt. Tendermint BFT kann nicht tolerieren, dass sich mehr als ein Drittel der Validatoren böse verhalten oder gleichzeitig offline gehen.
> **CosmWasm**: Die intelligente Vertrags-Engine des Cosmos-Ökosystems, die auf der WebAssembly-Technologie basiert, unterstützt die Verwendung der Rust-Sprache zum Schreiben von Verträgen und verfügt über Speichersicherheitsfunktionen zur Kompilierungszeit (die häufige Schwachstellen wie Pufferüberläufe verhindern).
> **PWA** (Progressive Web App, Progressive Web App): Eine Webtechnologie, die in einem Browser ausgeführt wird, aber ein natives Anwendungserlebnis bietet. Es unterstützt Offline-Caching, Push-Benachrichtigungen und das Hinzufügen zum Startbildschirm, ohne dass es über den App Store heruntergeladen und installiert werden muss.
> **WebRTC/WebSocket**: Zwei Browser-Echtzeit-Kommunikationstechnologien. WebRTC wird für die P2P-Datenweiterleitung (direkte Übertragung zwischen Knoten) verwendet; WebSocket wird verwendet, um eine lange Verbindung zwischen dem Client und dem Verifizierer aufrechtzuerhalten (Heartbeat, Belohnungsbenachrichtigung).
> **PoC** (Proof of Contribution): Der von LightDAO eingeführte Anreizmechanismus vergibt Belohnungen, indem er die tatsächlich von den Benutzern beigesteuerten Netzwerkressourcen (Bandbreitenweiterleitung, Blockverifizierung, Online-Zeit) überprüft, anstatt sich auf einen Wettbewerb um Rechenleistung oder eine Kapitalzusage zu verlassen.
> **Merkle Tree** (Merkle Tree): Eine Hash-Baum-Datenstruktur, die eine effiziente Überprüfung der Integrität eines bestimmten Eintrags in einer großen Datenmenge ermöglicht. Dieses Whitepaper wird verwendet, um Millionen von Light-Node-Heartbeats in einem einzigen Root-Hash zusammenzufassen und ihn in die Kette hochzuladen (O(1)-Speicheraufwand).
> **Gasgebühr**: Die Bearbeitungsgebühr, die für die Ausführung von Transaktionen oder Vertragsvorgängen auf der Blockchain erforderlich ist und als Vergütung des Verifizierers für die Rechen- und Speicherressourcen dient. Die Gasgebühr von LightDAO ist in USD-Äquivalenten verankert und wird vom Orakel alle 24 Stunden automatisch in die Menge an LICHT umgerechnet.
> **Slashing** (Strafe): Ein Strafmechanismus, bei dem ein Verifizierer gezwungen wird, einen Teil der verpfändeten Token abzuziehen, weil er ein Fehlverhalten (z. B. Doppelsignierung) begangen hat oder längere Zeit offline war. Es ist eine wirtschaftliche Garantie für die Sicherheit des PoS-Netzwerks.
> **Oracle** (Oracle): Eine Infrastrukturkomponente, die Off-Chain-Daten (wie Marktpreise, Wetter, Sportergebnisse) sicher in On-Chain-Smart-Contracts überträgt. LightDAO verwendet eine hybride Oracle-Architektur aus On-Chain-TWAP + Multi-Source-Aggregation.
> **TWAP** (Zeitgewichteter Durchschnittspreis): Der Preis jedes Blocks innerhalb eines Zeitraums wird gleichmäßig mit der Zeit gewichtet, um den Manipulationseffekt sofortiger Transaktionen mit großen Beträgen auf die Preisreferenz zu reduzieren.
> **AMM** (Automated Market Maker): Ein dezentrales Handelsprotokoll, das den Token-Austausch über einen Liquiditätspool (und nicht über ein Auftragsbuch) realisiert. Der Preis wird anhand einer Formel automatisch durch den Anteil der Vermögenswerte im Pool bestimmt.
> **DEX / CEX**: DEX (Decentralized Exchange, dezentraler Austausch) muss keine Benutzerressourcen hosten und handelt Peer-to-Peer über intelligente Verträge; CEX (Centralized Exchange, zentralisierte Börse) verlangt vom Betreiber, Vermögenswerte zu verwahren und Transaktionen abzugleichen.
> **IPFS** (InterPlanetary File System, InterPlanetary File System): Dezentrales Dateispeicher- und -verteilungsprotokoll, das in diesem Whitepaper für zensurresistentes Hosting von Front-End-Anwendungen verwendet wird (selbst wenn der Domainname blockiert ist, können Benutzer weiterhin über IPFS auf die Plattform zugreifen).

---

## Kapitel 5: Token-Wirtschaftsmodell

### 5.1 Gesamtdesignbasis

**LIGHT-Gesamtvorrat: 2,5 Milliarden (2.500.000.000) und wird nie zusätzlich ausgegeben. **

| Benchmarking-Projekte | Gesamtbetrag | Beteiligungsmethoden | Vergleichbarkeit mit LightDAO |
|---------|------|---------|----|
| Bitcoin | 21 Millionen | PoW-Mining-Maschine | Erzählbezug, die Schwelle liegt weit hoch |
| Helium (HNT) | 223 Millionen | Hardware-Hotspot ab 200 $ | DePIN-Benchmark, Hardware begrenzter Umfang |
| Filecoin (FIL) | 2 Milliarden | Speicherhardware | Beide sind der Größenordnung nach „Beitrag von Ressourcen im Austausch gegen Token“ |
| Kaspa (KAS) | 28,7 Milliarden | PoW-Grafikkarte | Zu groß, glatter Rückgang hat Referenzwert |
| Pi-Netzwerk | 100 Milliarden | Mobile Klicks | Negatives Lehrmaterial: Die Gesamtmenge ist zu groß → die Wertwahrnehmung ist extrem gering |

**Hauptgrund für die Wahl von 2,5 Milliarden Münzen:**

1. **Investitionskapazität (primäre Einschränkung):** 850 Millionen Münzen im Tresor × Grundpreis 0,15 $ × 75 % Auslastungsrate = **95,63 Millionen $ ≈ 100 Millionen $** einsetzbares Kapital, das den minimalen glaubwürdigen Schwellenwert für PE im unteren mittleren Marktsegment erreicht. Akademische Grundlage: Cong, Li & Wang (2021) „Tokenomics: Dynamic Adoption and Valuation“ (*Review of Financial Studies* 34(3):1105-1155, NBER w27222) beweist, dass der Plattformnutzen (Investitionsrendite → Rückkauf → Preisunterstützung) der grundlegende Treiber des Token-Werts ist, nicht die Verteilungsbreite.
2. **Netzwerkanleitung:** Am ersten Tag der Epoche wurden 1 Milliarde Münzen geschürft und 684.900 Münzen freigegeben. Bei 100.000 aktiven Bergleuten beträgt der Durchschnitt pro Kopf 6,51 LICHT/Tag, wobei die „ganzzahlige Wahrnehmung“ erhalten bleibt.
3. **Betriebliche Machbarkeit:** 10 % strategischer Betriebsfonds (250 Millionen Münzen) zur Schließung der Entwicklungs-/Prüfungs-/rechtlichen Finanzierungslücke vor TGE (1,10–2,85 Millionen US-Dollar). Das reine Community-Modell kann diese Kosten nicht decken.
4. **Machbarkeit einer Deflation:** Das Endergebnis von 1 Milliarde Münzen wird im 11. bis 12. Jahr im Basisszenario erreicht (25–30 % kürzer als die 15 Jahre+ des 21-Milliarden-Plans).
5. **Angemessenes Benchmarking:** Das gleiche Niveau wie Filecoin (2 Milliarden), das nach Marktwert zu den fünf größten Projekten im DePIN-Bereich gehört.

### 5.2 Token-Verteilungsplan

| Zuordnungskategorie | Verhältnis | Menge | Zweck | Freigabemethode |
|---------|------|------|------|---------|
| Leichtes Node-Mining | 40 % | 1 Milliarde | Mitwirkende im Belohnungsnetzwerk | Alle 2 Jahre halbiert, in Echtzeit basierend auf dem Beitrag veröffentlicht |
| Tresor für Unternehmensinvestitionen | 34 % | 850 Millionen Stück | Investitionsausführung unter DAO-Governance (wird beim Investieren zerstört) | Sperrung mehrerer Signaturen, nur durch gültige Beschlüsse freigegeben und zerstört |
| Ökologischer Entwicklungsfonds | 16 % | 400 Millionen | Liquidität, Airdrops, Entwicklerfinanzierung, Community-Operationen | Stufenweise Freigabe (siehe Abschnitt 5.3) |
| Strategischer Betriebsfonds | 10 % | 250 Millionen Münzen | Team, Wirtschaftsprüfung, Recht, Infrastruktur, strategische Investoren | 12 Monate Cliff + 36 Monate linear (siehe Abschnitt 5.X) |

**Branchen-Benchmarking (Tokenomics.net Kohorten-Benchmark 2024–2025):** Community-/Benutzerbelohnungen 20–35 % (LightDAO: 40 % Bergbau + 16 % Ökologie = 56 %, höher, da keine VC-Runde); Treasury/Reserven 15-25 % (LightDAO: 34 %, aufgrund der Anlagefunktion); Team/Investoren 15–45 % (LightDAO: 10 %, weit weniger als die Branche, unter Beibehaltung des „National DAO“-Narrativs).

### 5.3 Freigabeplan für den Fonds für ökologische Entwicklung

| Bühne | Zeit | Anteil | Menge | Zweck |
|------|------|------|------|------|
| TGE | Tag 0 | 30 % | 120 Millionen Stück | DEX-Liquidität (60 % = 72 Millionen) + Seed Airdrop (40 % = 48 Millionen) |
| Linearer Veröffentlichungszeitraum 1 | 1. bis 12. Monat | 40 % | 160 Millionen Münzen | 13,33 Millionen Münzen pro Monat: Community-Anreize, Marketing, Airdrop-Plan |
| Linearer Veröffentlichungszeitraum 2 | 13. bis 24. | 30 % | 120 Millionen Münzen | 10 Millionen Münzen pro Monat: Entwicklerfinanzierung, ökologisches Bauen, Reserven |

### 5.4 Strategischer Operationsfonds (250 Millionen Münzen)

| Unterkategorie | Anteil | Menge | Objekt | Freigaberegel |
|--------|------|------|------|---------|
| Service-Austausch für Token | 50 % | 125 Millionen Münzen | Entwicklungsunternehmen, Prüfinstitute, Anwaltskanzleien, Verifizierer | 12 Monate Cliff + 36 Monate linear; 30-50 % der Servicegebühren werden in LIGHT | gezahlt
| Strategische Finanzierung | 30 % | 75 Millionen Stück | 2-3 DePIN/Cosmos ökologische Fonds oder strategische Parteien der Verbraucherindustrie | Pre-TGE für 0,03 bis 0,05 US-Dollar verkauft (Erlös von 2,25 bis 3,75 Millionen US-Dollar); 12 Monate Cliff + 24 Monate linear; Einzelinvestor ≤ 2 % der Gesamtsumme |
| Hauptmitwirkende | 20 % | 50 Millionen Münzen | 3-5 Sponsoren/Kernbauer | 12 Monate Cliff + 36 Monate linear; veröffentlicht auf der Grundlage einer vierteljährlichen Meilensteinbewertung; kein Verkauf während der Laufzeit |

**Strategische Anlegeranforderungen:** Nichtfinanzielle Beiträge (z. B. Dealflow, Verifizierungsdienste, Compliance-Ressourcen) müssen bereitgestellt werden, und reine Finanzinvestoren werden nicht akzeptiert.

**Konformität mit den gesetzlichen Bestimmungen:** Der Verkauf vor dem TGE übernimmt die zweigleisige Ausnahmeregelung Reg S (Nicht-US-Investoren) + Reg D Rule 506(c) (Qualifizierte US-Investoren).

**Regeln zur Offenlegung der Hauptbeitragszahler:** Nur der Gesamtbetrag (50 Millionen = 2 % des Gesamtbetrags) und die Freigaberegeln werden offengelegt, persönliche Namen und individuelle Quoten werden nicht offengelegt. Offengelegte Rollenkategorien: Technologie/Investition/Compliance/Community.

### 5.5 Bergbauproduktion und Halbierungsplan

**Ableitung:** 2A = 1 Milliarde → A = 500 Millionen (Erste Ära). Tägliche Veröffentlichung = 500 Millionen ÷ 730 = 684.932 Stück ≈ 684.900/Tag. Jeder Block = 684.932 ÷ 49.371 ≈ 13,87 LICHT.

**Hinweis:** Der Belohnungspool für jeden Block wird vom gesamten Netzwerk geteilt, wovon 5 % den Validatoren (34.200/Tag) und 95 % den Light-Node-Minern (650.700/Tag) zugewiesen werden.

| Epoche | Zeit | Gesamtleistung | Tägliche Veröffentlichung | Belohnungspool pro Block |
|------|------|---------|---------|------------|
| 1. Ära | 0-24 Monate | 500 Millionen | ≈684.900 | ≈13,87 LICHT |
| 2. Ära | 25-48 Monate | 250 Millionen Stück | ≈342.500 | ≈6,93 LICHT |
| Die 3. Ära | 49-72 Monate | 125 Millionen Stück | ≈171.200 | ≈3,47 LICHT |
| Die 4. Ära | 73-96 Monate | 62,5 Millionen Stück | ≈85.600 | ≈1,73 LICHT |
| Die 5. Ära | 97-120 Monate | 31,25 Millionen Stück | ≈42.800 | ≈0,87 LICHT |

**Prüfung:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 Milliarde ✓. 97 % wurden innerhalb der ersten 10 Jahre abgeschlossen.

### 5.6 Referenzmodell zum Nutzereinkommen

| Netzwerkgröße | Pro-Kopf-Tageseinkommen | Monatliches Einkommen | Jahreseinkommen | Voller Aufschlag (1,44x) monatliches Einkommen |
|---------|-----------|--------|--------|-----|
| 10.000 Bergleute (Seed-Stadium) | ≈65,07 | ≈1.952 | ≈23.751 | ≈2.811 |
| 100.000 Bergleute (Wachstumsphase) | ≈6,51 | ≈195,2 | ≈2.375 | ≈281,1 |
| 1 Million Bergleute (Skalenzeitraum) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28,1 |

**Partnerstufe (50 Einladungen, 20 % Anteil, voller Bonus):**

| Netzwerkgröße | Selbst (einschließlich Bonus) | Einladung teilen | Täglich umfassend | Monatlich umfassend |
|---------|------------|---------|--------|--------|
| 10.000 Bergleute | ≈93,7 | ≈650,7 | ≈744,4 | ≈22.332 |
| 100.000 Bergleute | ≈9,37 | ≈65,07 | ≈74,44 | ≈2.233 |
| 1 Million Bergleute | ≈0,94 | ≈6,51 | ≈7,45 | ≈223,4 |

### 5.7 Airdrop-Wachstumsplan

**Wirtschaftsmodell:** Gesamtbudget für Luftabwürfe = Ziel erreichte Benutzer × Luftabwurf pro Kopf × (1+Abfallrate) = 100.000 × 150 LICHT × 1,3 ≈ 19,5 Millionen (Erwerbsart) + 35,5 Millionen (ökologische Art) = **55 Millionen** (entspricht 13,75 % des ökologischen Fonds von 400 Millionen).

| Airdrop-Typ | Auslösebedingungen | Einzelkontingent | Budget |
|---------|---------|---------|------|
| Erster Mining-Airdrop | Zum ersten Mal 4 Stunden effektives Mining abgeschlossen | 50 LICHT | 15 Millionen Stück |
| Geografische Expansion | Zielmarktnutzer vervollständigen ZK-KYC | 100 LICHT | 10 Millionen Stück |
| Lernen, um zu verdienen | Komplettes Bildungsmodul + Quiz | 30 LICHT | 6 Millionen Münzen |
| Erste Governance-Abstimmung | Erste Teilnahme an der Abstimmung | 20 LICHT | 3 Millionen Münzen |
| Liquiditätsbereitstellung | LP-Injektion ≥50 $ Sperrfrist für 30 Tage | 200 LICHT | 10 Millionen Stück |
| Inhaltserstellung | Von der Community verifizierte Tutorials/Übersetzungen | 50-200 LICHT | 6 Millionen Stück |
| Kooperationskanäle | Registrierung + erstes Mining durch Partner | 80 LICHT | 5 Millionen Stück |

**CAC-Verifizierung:** 55 Millionen Münzen × 0,03 $ = 1,65 Millionen $ ÷ 30.000 behaltene aktive Miner = **55 $/Person** (Branchenspanne 50–200 $, am unteren Ende). Akademische Grundlage: Zheng (2023) „Operation Dumbo Drop: Airdrop oder nicht Airdrop für den Erfolg des ersten Münzangebots?“ beweist, dass die Retentionsrate von ereignisgebundenen Airdrops drei- bis fünfmal so hoch ist wie die von reinen Airdrops.

**Anti-Missbrauch:** Eindeutiger Browser-Fingerabdruck + ZK-KYC; begrenzt auf 1 Anspruch pro Kategorie und Adresse; 30-tägige Sperrfrist; Automatisches Recycling ohne Aktivität in der Kette innerhalb von 30 Tagen nach der Reklamation.

### 5.8 Zweimotoriges Schwungrad und Kapitalpool

Schwungrad: Abstimmung → Vault LIGHT-Zerstörung → USDC-Zahlung → Gewinnrückfluss → Rückkauf und Zerstörung → Preisunterstützung → Mehr Benutzer.

Zweigleisiges System: stabiles Treasury (USDC, Gewinneinbehaltung) + flexibles Treasury (LIGHT-Schicht, zerstört beim Investieren und fließt nicht in den Markt). Rückkäufe werden mithilfe von TWAP aufgeteilt, wobei eine einzelne Order ≤ 5 % des durchschnittlichen täglichen Handelsvolumens beträgt.

### 5.9 Ausgabe und Handel von Sub-Token

Der Gesamtausgabebetrag = Investitionsbetrag ÷ 1 USD; der Umtauschpreis basiert auf dem 30-Tage-VWAP; alles durch den Austausch erhaltene LICHT wird zerstört; 50 % der Unterstützer/30 % Airdrop/20 % Betriebsreserve werden verteilt (für 6 Monate gesperrt). Die Dividendengrenze für eine einzelne Adresse beträgt 15 %. Sub-Tokens werden im On-Chain-AMM mit einer 30-tägigen Sperrfrist nach der Ausgabe gehandelt und werden nach der Auszahlung als „liquidiert“ gekennzeichnet.

### 5.10 Anfangsliquidität und Preisermittlung

**TGE-Anordnung (Token Generation Event, Token-Generierungsereignis): **

| Projekt | Planen |
|------|------|
| Anfänglicher Liquiditätspool | Von den 120 Millionen Stück, die vom ökologischen Entwicklungsfonds TGE freigegeben wurden, wurden 72 Millionen Stück (60 %) zugewiesen und in den DEX-Liquiditätspool eingespeist |
| Gepaarte Vermögenswerte | USDC (Hauptpool), USDT (Hilfspool) |
| Airdrop | Die restlichen 48 Millionen (40 %) werden für Airdrops an Seed-Nutzer verwendet (siehe Abschnitt 5.7 Airdrop-Plan) |
| An Börsen notiert | Erstmals nach TGE an dezentralen Börsen (wie Osmosis, JunoSwap) notiert; Je nach Compliance-Bedingungen ab dem 6. Monat die Notierung an zentralen Börsen beantragen |

**Detaillierter Mechanismus der niederländischen Auktion:**

Die niederländische Auktion ist eine Preismethode, bei der die Preise von hoch nach niedrig sinken. Im Gegensatz zu englischen Auktionen (bei denen die Preise von niedrig nach hoch geboten werden) legt der Verkäufer bei einer niederländischen Auktion einen anfänglichen Höchstpreis fest und der Preis sinkt automatisch mit der Zeit, bis der Käufer ein Abonnement zu einem bestimmten Preispunkt abschließt. Der erste Preis, bei dem der Gesamtzeichnungsbetrag das Ziel erreicht, ist der endgültige Eröffnungspreis.

**Warum eine niederländische Auktion einer Festpreis- oder englischen Auktion vorziehen:**

| Preise | Vorteile | Nachteile | Anwendbarkeit |
|---------|------|------|--------|
| Vorverkauf zum Festpreis | Einfach | Der Preis ist subjektiv. Wenn er zu hoch ist, wird er nicht verkauft, ist er zu niedrig, wird er von Robotern aufgekauft | Nicht geeignet (keine Preisfindungsfunktion) |
| Britische Auktion (Gebot) | Vollständige Preisfindung | Große Käufer können strategisch abwarten und die Preise erhöhen; Gaskrieg | Nicht geeignet (Gaskrieg in der Kette schließt kleine Nutzer aus) |
| **Niederländische Auktion** | **Automatische Preisermittlung; keine Ausschreibung erforderlich (kein Gaskrieg); gleichberechtigte Beteiligung großer und kleiner Käufer; Anti-Bot (Preissenkungsmechanismus verhindert natürlich das Front-Running)** | Der Startpreis und die Verzögerungsrate müssen angemessen eingestellt werden | **Am besten geeignet (fair + effizient + Anti-Manipulation)** |

**Spezifische Parameter für die niederländische LightDAO-Auktion:**

| Parameter | Einstellungen | Beschreibung |
|------|------|------|
| Auktionsziel | LIGHT-Token (zugeteilt aus den 72 Millionen, die vom Ökofonds TGE freigegeben wurden) | USDC aus der Auktion werden in den stabilen Tresor eingespeist |
| Ziel-Spendenbetrag | **15 Millionen USDC** | 5 Millionen US-Dollar → Mindestreserve der stabilen Staatskasse; 10 Millionen US-Dollar → Anfangsinvestitionskapital |
| Startpreis | 0,20 $/LICHT | Höher als der erwartete Gleichgewichtspreis, um sicherzustellen, dass er nicht innerhalb von Sekunden verloren geht |
| Verzögerungsrate | Jede Stunde um 5 % verringern | Beginnend bei 0,20 $, Abfall auf 0,017 $ nach etwa 48 Stunden (wenn sich niemand anmeldet) |
| Mindestreservepreis | 0,01 $/LICHT | Sollte der Mindestpreis gesenkt werden und das Ziel immer noch nicht erreicht werden, wird die Auktion um 24 Stunden verschoben oder die Anzahl der Objekte angepasst |
| Abonnementmethode | Der Benutzer sendet „Ich bin bereit, X USDC-Äquivalent LIGHT zum aktuellen Preis zu kaufen“ | Es ist kein Bieten erforderlich, das System rechnet nach dem endgültigen Einheitspreis ab (jeder Mehrpreis wird entschädigungslos zurückerstattet) |
| Obergrenze für Einzelbenutzer | Nicht mehr als 5 % des angestrebten Spendenbetrags (d. h. 750.000 $) | Verhindern Sie, dass ein einzelner Käufer die anfänglichen Chips monopolisiert |
| KYC-Anforderungen | Erweiterte Überprüfung (Steueransässigkeit) | Compliance-Anforderungen |

**Ziel der Mittel aus Auktionsergebnissen:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Schutzzeitraum für Preisfindung:** In den ersten 72 Stunden nach TGE wird ein Schutz vor Preisschwankungen eingerichtet. Wenn der DEX-Transaktionspreis um mehr als ±50 % vom Eröffnungspreis der Auktion abweicht, wird die Sub-Token-Austauschfunktion ausgesetzt (Mining und Transfers sind davon nicht betroffen), um zu verhindern, dass extreme Spekulationen das ökologische Startup beeinträchtigen. Die Sicherung wird nach 72 Stunden automatisch freigegeben.

**Warum 15 Millionen US-Dollar statt weniger:** Das anfängliche Investitionskapital von 10 Millionen US-Dollar muss im ersten Jahr 3–5 Investitionen unterstützen (eine einzelne Investition beträgt 2–5 Millionen US-Dollar, siehe Umfang der Startphase in Abschnitt 9.1). Wenn nur 5 Millionen US-Dollar eingesammelt werden (alles als Reserven), gibt es im ersten Jahr kein einsetzbares Investitionskapital und das Schwungrad kommt nicht in Gang. 15 Millionen US-Dollar = 5 Millionen US-Dollar Reserve + 10 Millionen US-Dollar Investition, was das minimal mögliche Gleichgewicht zwischen „Sicherheitsergebnis“ und „Schwungradstart“ darstellt.

### 5.11 Deflationsmechanismus und Endergebnis

**Umlaufvolumen = Bergbaufreigabe + ökologische Freigabe + freigegebene strategische Mittel – Austausch und Zerstörung – Gasvernichtung – Rückkauf und Zerstörung. ** 850 Millionen Münzen aus dem Anlagetresor sind nie in Umlauf gekommen. Theoretische Umlaufobergrenze = 10+4+2,5 = **1,65 Milliarden**.

| Auslösebedingungen | Systemverhalten |
|---------|---------|
| Auflage ≤ 1,5 Milliarden Stück | Verlangsamungssignal (Szenario mit extrem geringer Zerstörung) |
| Umlaufvolumen ≤ 1,2 Milliarden Stück | Frühwarnmeldung, Aussetzung der aktiven Zerstörung (ca. 8. Jahr des Basisszenarios) |
| Umlaufvolumen ≤ 1 Milliarde | Harter Stopp, alle Zerstörungen sind dauerhaft geschlossen (Basisszenario ist etwa Jahr 11-12) |

### 5.12 Preisstabilisierungsmechanismus (Anti-Todesspirale)

**Grundprinzipien:** LightDAO beeinträchtigt nicht die tägliche Marktpreisermittlung. Das Protokoll passt seine Parameter nur in extremen Abwärtsszenarien an, um das Risiko zu verringern, in eine „Todesspirale“ zu geraten.

**Bewertungslogik:** In verschiedenen volatilen Umgebungen stellt derselbe Rückgang unterschiedliche Grade der Anomalie dar. Ein starker Rückgang in einem Markt mit geringer Volatilität ist ein stärkeres abnormales Signal und erfordert eine Intervention mit höherer Intensität; Ein starker Rückgang in einem Markt mit hoher Volatilität ist relativ häufig und es können geringere Eingriffe vorgenommen werden. Daher hängt die Intensität des Eingriffs positiv mit der Abnormalität des Signals zusammen und hängt nicht nur vom absoluten Wert des Rückgangs ab.

**Vollständiges Flussdiagramm des Mechanismus:**

| Marktstatus | 30-tägige historische Volatilität | Auslösebedingungen | Signalpegel | Ausführung nach Trigger | Wiederherstellungsbedingungen |
|---------|--------------|---------|---------|----------|---------|
| Geringe Volatilität | ≤30 % | Kumulierter Rückgang von ≥40 % an 5 aufeinanderfolgenden Tagen | Stufe I | Die Bergbauproduktion sank auf 50 %; die Zerstörungsrate stieg von 20 % auf 35 %; Der Veröffentlichungszeitraum für die Risikoparameteranpassung wurde von 72 Stunden auf 12 Stunden verkürzt. Der Schattenausschuss trat in den aktiven Zustand ein (nur das Recht zur vorübergehenden Suspendierung kann gemäß dem Gesetz ausgeübt werden) | Der Preis lag über dem gleitenden 30-Tage-Durchschnitt, erholte sich um ≥ 80 % vom Auslösepreis und blieb dies an 10 aufeinanderfolgenden Tagen |
| Mittlere Fluktuation | 30%-60% | Kumulierter Rückgang an 7 aufeinanderfolgenden Tagen ≥ 50 % | Stufe II | Die Bergbauproduktion sank auf 50 %; die Zerstörungsquote stieg von 20 % auf 30 %; die Werbedauer wurde auf 24 Stunden verkürzt; Das Schattenkomitee trat in den aktiven Zustand ein | Der Preis lag über dem gleitenden 30-Tage-Durchschnitt, erholte sich um ≥ 60 % vom Auslösepreis und blieb dies sieben Tage in Folge |
| Hohe Volatilität | 60 %-100 % | 10 aufeinanderfolgende Tage mit kumulativem Rückgang ≥55 % | Stufe III | Die Bergbauproduktion sank auf 75 %; die Zerstörungsrate stieg von 20 % auf 25 %; die Werbedauer wurde auf 48 Stunden verkürzt; das Schattenkomitee ging in den Standby-Modus | Der Preis lag über dem gleitenden 30-Tage-Durchschnitt, erholte sich um ≥40 % vom Auslösepreis und blieb dies fünf Tage in Folge |
| Extreme Volatilität | >100 % | Kumulierter Rückgang an 10 aufeinanderfolgenden Tagen ≥ 65 % | Stufe III | Umgesetzt gemäß Level III-Maßnahmen für hohe Volatilität | Implementiert gemäß den Wiederherstellungsbedingungen der Stufe III für hohe Volatilität |

**Ausschlussbedingungen:** Nur wenn der Rückgang von Bitcoin im gleichen Zeitraum weniger als 50 % des Rückgangs von LIGHT beträgt, kann der oben genannte Mechanismus ausgelöst werden, um einen systemischen Marktzusammenbruch auszuschließen (d. h. wenn BTC im gleichen Zeitraum ebenfalls einbricht, handelt es sich um ein Gesamtmarktereignis, und es wird kein separater Eingriff für LIGHT eingeleitet).

**Beschreibung der Wiederherstellungslogik:** Die Rebound-Anforderungen und die Dauer nehmen mit der Anomaliestufe ab: Level I erfordert die höchste Rebound-Amplitude (80 %) und die längste Bestätigungszeit (10 Tage), während Level III relativ geringere Anforderungen erfordert (40 %/5 Tage). Diese Anordnung steht im Einklang mit der progressiven Logik: „Je stärker das abnormale Signal, desto stärker der Eingriff und desto strenger die Bestätigung der Wiederherstellung“.

**Volatilitäts- und Preisdatenquelle:** Die 30-tägige historische Volatilität und der kumulative Rückgang werden vom On-Chain-Preisorakel (siehe Abschnitt 4.10) basierend auf dem TWAP-Snapshot des täglichen UTC-Blocks um 00:00 Uhr bereitgestellt und basieren nicht auf externen Datenquellen.

### 5.13 Ergebnis-Nachhaltigkeits-Stresstest

| Stressszenarien | Was-wäre-wenn | Protokollantworten | Worst-Case-Ergebnisse |
|---------|---------|---------|---------|
| Alle Investitionen scheiterten | Alle investierten Unternehmen erlitten Verluste oder scheiterten am Ausstieg | Der Versicherungsfonds (10 % des aufgelaufenen Gewinns) deckt einen Teil der Verluste ab; stabile Treasury-Reserven (≥8 Millionen US-Dollar) zur Aufrechterhaltung des Betriebs; neue Investitionen werden ausgesetzt, bis die Community eine Neubewertung durchführt | Sub-Token-Inhaber können keine Dividenden erhalten; Der LIGHT-Preis steht unter Druck, kehrt aber nicht auf Null zurück (Bergbau- und Governance-Funktionen funktionieren weiterhin) |
| Der Markt brach um 80 % ein | Der LIGHT-Preis fiel gegenüber dem Höchststand um 80 % | Lösen Sie den Anti-Todes-Spiralmechanismus aus (Stufe II oder Stufe III); Die Bergbauproduktion wird um 50-75 % reduziert; die Zerstörungsrate wird erhöht; Das Schattenkomitee kann Hochrisikooperationen aussetzen | Das Benutzereinkommen sinkt, das Netzwerk funktioniert jedoch weiter. Der Mechanismus wird automatisch aufgehoben, wenn die Wiederherstellungsbedingungen erfüllt sind |
| Wichtige Marktregulierungsverbote | Ein großes Land hat Krypto-Assets vollständig verboten | Der Front-End-Switching-IPFS-Spiegel bleibt zugänglich; On-Chain-Assets und bestehende Benutzerrechte und -interessen werden nicht beeinträchtigt; Die Verfügbarkeit von Diensten Dritter wird nur im Rahmen der Rechtsdurchsetzung angepasst; SPV-Operationen auf den Cayman Islands unterliegen nicht der Gerichtsbarkeit eines einzelnen Landes | Das Nutzerwachstum in der Region stagniert; andere Regionen weltweit sind nicht betroffen |
| Massenhafter Nutzerverlust | Aktive Miner gingen um mehr als 70 % zurück | BaseReward wird automatisch umverteilt (Nenner kleiner → Pro-Kopf-Einkommen der behaltenen Nutzer steigt); Einladungsanreize werden so gewichtet, dass sie Rückströme anlocken; Governance-Schwellenwerte werden vorübergehend gesenkt (dynamischer Mechanismus in Abschnitt 5.14) | Die Netzwerksicherheit wird verringert, aber die Kette wird nicht gestoppt (Tendermint BFT toleriert, dass <1/3 Validatoren offline sind) |
| Große Schwachstellen bei Smart Contracts | Ausnutzbare Schwachstellen in Kernverträgen gefunden | Notfallaussetzung von Geldabflüssen mit mehreren Unterschriften (72-Stunden-Zeitsperre bietet Reaktionsfenster); Abstimmung über die Migration des Backup-Vertrags einleiten (Notfallreparatur auf L4-Ebene, siehe Abschnitt 4.12); Versicherungsfonds deckt Nutzerverluste ab | Einige Gelder können beschädigt sein; Der normale Betrieb wird nach Abschluss der Migration wieder aufgenommen |

### 5.14 Ausgleichsmechanismus zwischen den Generationen

Dynamische Anpassung des Governance-Schwellenwerts: Für jede 1 Million neue kumulative aktive Miner wird der Vorschlagsschwellenwert automatisch um 5 % gesenkt (Untergrenze 2.500 LIGHT).

> **[Terminologie in diesem Kapitel]**
> **TGE** (Token Generation Event): Der Zeitpunkt, an dem ein Token zum ersten Mal über einen Smart Contract erstellt und verteilt wird, normalerweise begleitet von der Einrichtung eines anfänglichen Liquiditätspools, einer niederländischen Auktionspreisgestaltung und der ersten öffentlichen Transaktion. Ähnlich einem Börsengang im traditionellen Finanzwesen, jedoch ohne Börsennotierung.
> **Halbierung** (Halving): Ein Mechanismus, bei dem die Mining-Leistung in jedem festgelegten Zeitraum (2 Jahre/730 Tage für LightDAO) automatisch um 50 % reduziert wird. Ziel ist es, eine fortschreitende Knappheit zu schaffen – mit der Zeit kommt immer weniger neues Angebot hinzu, und wenn die Nachfrage nicht zurückgeht, werden die Preise gestützt. Bitcoin führt alle 4 Jahre eine Halbierung durch.
> **Treasury** (Treasury): Token-Reserven, die durch Multi-Signatur-Verträge gesperrt sind und nur durch Governance-Beschlüsse freigegeben werden können. LightDAO verfügt über zwei Arten von Tresoren: Investitionstresore (die LIGHT aufbewahren und bei der Ausführung von Investitionen zerstört werden) und stabile Tresore (die USDC aufbewahren und zur Zahlung von Investitionsentgelten und Betriebskosten verwendet werden).
> **Deflation** (Deflation): Der Prozess, bei dem das Gesamtangebot oder der Umlauf an Token weiter abnimmt. LightDAO erreicht eine Deflation durch vier Mechanismen: Ausführung und Vernichtung von Investitionen, Austausch und Vernichtung von Sub-Token, Vernichtung von Gasgebühren (50 %) sowie Rückkauf und Vernichtung von Gewinnen.
> **Todesspirale** (Death Spiral): Token-Preise fallen → Einkommen der Miner schrumpft → Miner kündigen → Netzwerksicherheit/Beitrag sinkt → weiterer Vertrauensverlust → ein Teufelskreis, in dem die Preise weiter fallen. Der abgestufte Interventionsmechanismus in Abschnitt 5.12 soll diesen Zyklus unterbrechen.
> **Sub-Token** (Sub-Token): SPV-Einkommensverteilungsanspruchszertifikat, das gemäß den Regeln nach Abschluss jeder Unternehmensinvestition ausgestellt wird (z. B. Erwerb einer Kaffeemarke → CAFE-Token). Das Halten von Sub-Tokens bedeutet das Halten von Qualifikationen für die Ausschüttung zukünftiger Gewinne und stellt keine Aktionärsrechte oder Corporate-Governance-Rechte dar.
> **LP** (Liquiditätsanbieter): Teilnehmer, die zwei gleichwertige Vermögenswerte (z. B. LIGHT+USDC) in den DEX-Liquiditätspool einspeisen, erhalten im Gegenzug Transaktionsgebühren. LP ist die Grundlage für den normalen Betrieb von DEX.
> **VWAP** (Volumengewichteter Durchschnittspreis): Der Preis innerhalb eines Zeitraums wird mit dem Volumen jeder Transaktion gewichtet und spiegelt die tatsächlichen Markttransaktionskosten wider. LightDAO verwendet den 30-Tage-VWAP als Preisbenchmark für den Sub-Token-Austausch.
> **CAC** (Customer Acquisition Cost, Benutzerakquisekosten): Die durchschnittlichen Kosten für die Akquise eines effektiven aktiven Benutzers. Der angestrebte CAC des LightDAO-Airdrop-Programms liegt bei 55 US-Dollar pro behaltenem aktiven Miner (Branchenspanne 50–200 US-Dollar).
> **wLIGHT** (Wrapped LIGHT, gekapseltes LIGHT): LIGHT-äquivalente Token, die über Cross-Chain-Brücken auf Ethereum oder Solana ausgegeben werden, und eine gleiche Menge an nativem LIGHT wird durch den Brückenvertrag als 1:1-Reserve gesperrt. Der Zweck besteht darin, Benutzern außerhalb des Kosmos-Ökosystems zu ermöglichen, LICHT zu erhalten und zu halten.
> **Niederländische Auktion** (Niederländische Auktion): Eine Preismethode, bei der der Preis von hoch nach niedrig sinkt. Der Verkäufer legt einen anfänglichen Höchstpreis fest, der mit der Zeit automatisch sinkt, bis der Käufer ein Abonnement zu einem bestimmten Preispunkt abschließt. Der erste Preis, bei dem der gesamte Abonnementbetrag das Ziel erreicht, ist der endgültige Transaktionspreis. Der Vorteil besteht darin, dass keine Gebote erforderlich sind (kein Gaskrieg), Käufer aller Größenordnungen gleich sind und es von Natur aus resistent gegen die Bevorzugung von Robotern ist.

---

## Kapitel 6: Governance-Mechanismus

### 6.1 Zweidimensionales Abstimmungsmodell

Währungsgewichtung (einschließlich Reputation + Levelbonus, Gesamtobergrenze +40 %) + Anzahl der Adressen (1 Adresse = 1 Stimme, zugehörige Adressen werden zusammengeführt). Die Stimmrechte sind 90 Tage gültig und können durch die Übertragung von 5 LIGHTs aktiviert werden. Reputationsbonus: Halten der Währung für 1 Jahr + 15 gültige Stimmen → bis zu +30 %.

### 6.2 Dynamische Erfolgsquote

Mindesterfolgsquote = 50 % + (50 % – tatsächliche Abstimmungsquote). Einfache Mehrheit bei einer Abstimmungsquote von ≥50 %.

### 6.3 Angebotsparameter

| Geben Sie | ein Marge | Token-Abstimmungsrate | Adressabstimmungsrate | Erfolgsquote | Ausführungsverzögerung |
|------|--------|-----------|-----------|--------|---------|
| Mikro | 100 $ | ≥15 % | ≥20 % | Dynamisch ≥55 % | 24h |
| Erwerbsart | 500 $ | ≥25 % | ≥30 % | Dynamisch ≥60 % | 72h |
| Risikokapitaltyp | 500 $ | ≥35 % | ≥40 % | Dynamisch ≥60 % | 72h |
| Major | 1.000 $ | ≥45 % | ≥50 % | Dynamisch ≥66 % | 72h |
| Notfall | 2.000 $ | ≥50 % | ≥60 % | ≥75 % | Nicht finanzierend 6 Stunden/Hochrisiko 1 Stunde; Kapitalgeschäfte unterliegen weiterhin einer 72-Stunden-Zeitsperre |

### 6.4 Lebenszyklus des Angebots

Einreichungsvoraussetzung: ≥5.000 LIGHT + 30 aufeinanderfolgende Tage der Zusage + Anzahlung. Öffentliche Ankündigung 72 Stunden (überarbeitet ≤ 2 Mal). Die Abstimmung erfolgt innerhalb von 7 Tagen (48 Stunden für Fast Track, ≤500.000 USDC). Veto-Abkühlung für 90 Tage. Die Wirksamkeit verzögert sich um 24 Stunden.

**Schwellenwertbeschreibung:** 5.000 Münzen in der Seed-Phase (10.000 Miner) ≈ 77 Tage Grundproduktion; Partnerstufe ≈ 7 Tage. Die Governance wird im siebten Monat aktiviert und frühe Benutzer haben ausreichend Akkumulierungszeit.

### 6.5 Wahlanreize

Es gibt einen Grundanreiz für die Teilnahme (sogar das Teilen) und einen zusätzlichen Bonus für die richtige Einschätzung (50 % des Wettpools). Wetten Sie auf den Bereich 5-500 LIGHT. Den Herdeneffekt unterdrücken: Gegner erhalten auch dann grundlegende Anreize, wenn sie „im falschen Team“ sind.

### 6.6 Belohnungen und Strafen für Erfolg oder Misserfolg

Versäumnis in gutem Glauben: 50 % Rückerstattung der Anzahlung + 30 Tage Wartezeit. Böswilliges Versäumnis (Fälschung/Wiederholung): vollständiger Betrag eingezogen + dauerhafte Sperre. Betrugsnachweis: Höchstgrenze 5.000 LIGHT, 40 % Strafe des Gründungsbonus + 500 LIGHT.

### 6.7 Finanzielle Transparenz

Echtzeit-Dashboard in der Kette + vierteljährlicher Finanzbericht + jährliche unabhängige Prüfung (die erste Prüfung muss vor TGE abgeschlossen sein) + Offenlegung der Investitionsziele in Echtzeit.

---

## Kapitel 7: Machtkontrollen und -balancen und Rollendefinition

### 7.1 Erster Vormund

Die Berechtigungen sind auf Dokument-/Format-/offizielle Website-Informationen beschränkt. Laufzeit ≤ 24 Monate. Es muss ein Ersatzvormund benannt werden (30 aufeinanderfolgende Tage nicht unterschriftsfähig → automatisch übernommen). Gleichzeitige Arbeitsunfähigkeit → 48-Stunden-Notabstimmung zur Ernennung eines vorübergehenden Managers.

### 7.2 Energieübertragungs-Roadmap

| Bühne | Zeit | Berechtigungen | Investitionsgenehmigung |
|------|------|------|---------|
| Erstellungszeitraum | 0-6 Monate | Vormund (nichtfinanziell) | Guardian + Community-Multisignatur 3/5 |
| Übergangsfrist | Juli-Dezember | Guardian + Hauptmitwirkender gemeinsam unterzeichnet | Wie oben + Hauptmitarbeiter |
| Laufzeit | 13-24 Monate | Governance-Ausschuss 3/5 | Regelmäßige zweidimensionale Abstimmung |
| Autonomiezeitraum | 25 Monate + | Alle Inhaber | Gleiche Laufzeit |

### 7.3 Governance-Ausschuss

Die Macht wird auf fünf Personen aufgeteilt (rotierender Vorsitzender/Finanzen/Technologie/Community/Schlüssel), vierteljährlich wechselnd, die Amtszeit beträgt sechs Monate und kann einmal wiedergewählt werden. Die Kampagne sieht 50.000 gemeinsame Unterschriften von LIGHT + 100 Adressen vor. An der Entscheidungsfindung sind ≥3 Personen beteiligt und es werden ≥3 Positionen abgedeckt.

**Schwellenwertbeschreibung:** 50.000 Münzen in der Seed-Phase ≈ 67 Tage (2,2 Monate) für Partner; in der Wachstumsphase ≈ 672 Tage (22 Monate). Für Frühpartner steht die erste Wahl des Gremiums im 13. Monat zur Verfügung.

### 7.4 Schattenausschuss

Vorübergehende Aussetzung nur wegen „Verstößen/Sanktionen/schwerwiegendem Betrug“. Alle Abstimmungen müssen innerhalb von 72 Stunden bestätigt werden (Einspruch >60 %→abgewiesen). Zweimal hintereinander abgelehnt → automatisch angeklagt und aufgelöst.

### 7.5–7.6 Kampagnenüberprüfung und Schlüsselplan

SimHash>80 % Disqualifikation; KI-Inhalte müssen durch Erläuterungen ergänzt werden; Bei fehlenden Fragen werden 20 % der Stimmen abgezogen. Schlüssel-Shard-Backup + vierteljährlicher Gesundheitscheck + 7-tägige öffentliche Ankündigung + Abstimmungsersatz.

---

## Kapitel 8: Vertrauens- und Sicherheitsmechanismus

### 8.1 Fünf wichtige Sicherheitsmechanismen

Zeitsperre 72h (Notfallvorschläge sind nicht von Kapitaloperationen ausgenommen); Mehrfachsignierung 3/5; vierteljährliche Rotation ≤ 2 Sitzungen; 100 % Strafe bei Betrug; Alle Transaktionen finden in der Kette statt.

### 8.2 Versicherungsfonds

Es fallen **10 %** der erfolgreichen Anlagegewinne an. Ansprüche müssen unabhängig gemeldet werden + DAO 66 % dafür + Single ≤ Pool 20 %. Ergänzende Quelle: 30 % der Geldbuße wegen Fälschung. Die Positionierung „Teilpuffer“ ist kein vollständiger Schutz.

### 8.3 Extremplan

Überwachung Black Swan → IPFS + Entfernung von Administratorrechten; Betrug → Suspendierung des Schattenausschusses (72-Stunden-Ratifizierung) + Versicherungsfonds + SPV-Schiedsverfahren; Todesspirale → Abschnitt 5.12 Mechanismus; Vertragsanfälligkeit → Sperrung mit mehreren Signaturen + Migrationsabstimmung; Validatoren tun gemeinsam Böses → BFT-Toleranz <1/3, bei Überschreitung wird die Kette unterbrochen + Notabstimmungsmigration.

---

## Kapitel 9: Investitionstätigkeit und Ausstiegsstrategien

### 9.1 Screening und Umfang der Investitionsziele

**Phasenweiser Wachstumspfad des Investitionsumfangs (Formel: Kassenüberschuss × 15 % × LIGHT-Preis): **

| Bühne | LIGHT-Preis | Einzeltransaktionslimit in der Anfangsperiode des Tresors | Anpassungsziele | Branchen-Benchmarking |
|------|----------|----|----------|----------|
| Anlaufzeit (Y1-2) | 0,02 $ – 0,05 $ | 2,55 Millionen US-Dollar – 6,37 Millionen US-Dollar | Einzelgeschäft/kleine Kette, Engel rund | Mikro-PE |
| Wachstumsphase (Y3-5) | 0,05 $ – 0,30 $ | 6,37 Millionen US-Dollar – 38,25 Millionen US-Dollar | Regionale Kette 30-200 Filialen, Seed-A-Runde | PE im unteren mittleren Marktsegment |
| Reifegrad (Y5-8) | 0,30 $ – 1,00 $ | 38,25 Millionen US-Dollar – 127,5 Millionen US-Dollar | Multinationale Kette/mittelständische Technologie, rund B-C | Mittelstands-PE |
| Skalenzeitraum (Y8+) | 1,00 $+ | 127,5 Millionen US-Dollar+ | Große Akquisitionen, Pre-IPO | Groß angelegtes PE/Wachstumsphasen-VC |

### 9.2 Investitionsentscheidungsprozess

Projektfindung (≥5.000 LIGHT) → unabhängige Due Diligence → 72 Stunden öffentliche Ankündigung → zweidimensionale Abstimmung → 24/72 Stunden Ausführung.

### 9.3 Ausstieg und Gewinnausschüttung

Jährliche Dividende: **40 %** Sub-Token-Inhaber / **30 %** stabiler Tresor / **20 %** Rückkauf LIGHT zur Vernichtung / **10 %** Versicherungsfonds.
Exit-Ertrag: **70 %** Stable Vault / **30 %** Rückkauf und Verbrennung.

### 9.4 Investitionsdisziplin

| Regeln | Inhalt |
|------|------|
| Einzelvernichtungsgrenze | Verbleibender Tresor × 15 % (anfänglich 850 Millionen × 15 % = 127,5 Millionen Münzen) |
| Einzelziel | ≤25 % des Gesamtwertes des Tresors |
| Branchenkonzentration | ≤40 % des Portfolios |
| Geografische Konzentration | ≤30 % des Portfolios |
| Stabile Treasury-Reserven | 5 Millionen US-Dollar bei TGE (Auktion), bis zum 24. Monat 8 Millionen US-Dollar |
| Bedenkzeit | 2 aufeinanderfolgende Ausfälle → 180 Tage |

**Tresorkapazität:** 850 Millionen Stück × 0,10 $ = 85 Millionen $ (ursprüngliche Gesamtkapazität); × 0,30 $ = 255 Millionen $; × 1,00 $ = 850 Millionen $. Durch die 15 %-Einzeltransaktionsgrenze steht das Investitionstempo in einem positiven Verhältnis zum Preis.

> **[Terminologie in diesem Kapitel]**
> **EBITDA** (Ergebnis vor Zinsen, Steuern und Abschreibungen): Ein Indikator, der die Rentabilität der Kerngeschäfte eines Unternehmens misst und die Beeinflussung durch Finanzstruktur (Zinsen), Steuerpolitik (Steuer) und Rechnungslegungsoptionen (Abschreibungen/Amortisationen) eliminiert und unternehmens- und branchenübergreifende Vergleiche erleichtert. EBITDA-Marge = EBITDA ÷ Betriebsergebnis.
> **DCF** (Discounted Cash Flow, Discounted-Cashflow-Methode): Eine Bewertungsmethode, die den erwarteten zukünftigen Cashflow des Unternehmens zu einem bestimmten Abzinsungssatz in den aktuellen Wert umrechnet. Es eignet sich für reife Unternehmen mit stabilem Cashflow (z. B. Verbraucherketten), nicht jedoch für Technologieunternehmen im Frühstadium, die noch nicht profitabel sind.
> **IPO** (Initial Public Offering): Das erste Mal, dass ein Unternehmen öffentlich Aktien an einer Börse ausgibt und zum Handel zugelassen wird. Für LightDAO ist der Börsengang investierter Unternehmen einer der wichtigsten Exit-Pfade für Wachstumsmotoren.
> **Pre-IPO**: Die letzte Runde der Private-Equity-Finanzierung, bevor das Unternehmen offiziell an der Börse notiert wird. Normalerweise liegt die Bewertung nahe am Post-IPO-Niveau, das Risiko ist geringer als bei den früheren Runden, aber auch der Renditemultiplikator ist niedriger.
> **TWAP-Ausführung** (Zeitgewichtete Durchschnittspreisausführung): Teilen Sie Rückkaufaufträge mit großen Beträgen in mehrere Aufträge mit kleinen Beträgen auf und führen Sie diese gleichmäßig über einen bestimmten Zeitraum aus, um die Auswirkungen eines einzelnen Großauftrags auf den Marktpreis zu vermeiden. LightDAO schreibt vor, dass ein einzelner Rückkauf 5 % des durchschnittlichen täglichen Handelsvolumens nicht überschreiten darf.

---

## Kapitel 10: Roadmap

| Phase | Zeit | Kernziele | Wichtige Meilensteine ​​| Voraussetzungen |
|------|------|---------|-----------|---------|
| Vorbereitungszeit | Q4 2026 | Juristische Person + Team + vorhandene Mittel | Unternehmensregistrierung auf den Cayman-/BVI-Inseln abgeschlossen; technischer Partner oder Entwicklungsteam unterzeichnet; strategische Investorenabsicht bestätigt (2-3 Unternehmen); Startkapital ≥ 150.000 $ vorhanden | Gründer legt Methode zur Offenlegung der Identität fest; Fertigstellung von BP und Pitch Deck |
| Entwicklungszeitraum | Q1-Q2 2027 | Kernsystementwicklung | Es wurden 10 Smart-Contract-Module entwickelt; Die PWA-Frontend-Entwicklung ist abgeschlossen; 7 Verifizierer-Testnetze wurden bereitgestellt; interner Alpha-Test wurde bestanden | Entwicklungsteam vorhanden; Anforderungsdokument (technische Spezifikation) fertiggestellt |
| Audit- und Testzeitraum | Q3 2027 | Sicherheits- und Compliance-Überprüfung | Veröffentlichung eines unabhängigen Sicherheitsauditberichts (≥1 Top-Institution); Veröffentlichung eines Stellungnahmeschreibens zur Einhaltung gesetzlicher Vorschriften (MLM + Wertpapierrecht); 50.000 gleichzeitiger Stresstest bestanden; Falsch-Positiv-Rate des Anti-Cheating-Systems <2 %; Governance-Abstimmung abgeschlossen | Einfrieren der Vertragsentwicklung (Code Freeze); Prüfungsgebühren vorhanden |
| TGE und Mainnet online | Q4 2027 | Token-Ausgabe + Netzwerkstart | Niederländische Auktion abgeschlossen (Ziel: 15 Millionen US-Dollar); Mainnet online (≥10 Validatoren); für die Öffentlichkeit zugängliche Bergbauplattform; DEX-Liquiditätspool eingerichtet; Samen-Airdrop ausgegeben | Audit bestanden; Validatoren ≥7 (hartes Endergebnis); Bereitstellung von Auktionsverträgen |
| Zeit der Glaubensbildung | Q1 2028 (1. bis 3. Monat nach TGE) | 30.000–50.000 Seed-Nutzer | Die Zahl der aktiven Bergleute überstieg 30.000; erste Governance-Abstimmung; Mehrsprachiger Community-Kanal eingerichtet (Englisch/Chinesisch/Spanisch/Portugiesisch/Philippinisch); erster monatlicher Community-Bericht veröffentlicht | TGE abgeschlossen; Community-Operations-Team vor Ort |
| Wertankerzeitraum | Q2-Q3 von 2028 (4. bis 9. Monat nach TGE) | Erste Investition + Übergangsperiode Governance | Erster Investitionsvorschlag angenommen (Multi-Signatur-Genehmigung während des Entstehungszeitraums gilt für den 4. bis 6. Monat; gemeinsame Genehmigung während des Übergangszeitraums gilt ab dem 7. Monat); die erste SPV-Lieferung ist abgeschlossen; Validatoren stehen zur Wahl (ab dem 7. Monat); der erste Quartalsfinanzbericht wird veröffentlicht | stabiles Treasury USDC≥5 Mio. $; Due Diligence des Investitionsziels ist abgeschlossen |
| Laufzeit der Governance | 2028 Q4-2029 Q1 (10. bis 15. Monat nach TGE) | Ausschusswahl + Dezentralisierungsübergang | Erste Wahl des Governance-Ausschusses (13. Monat); Eintragung der Fälligkeitsfrist (3/5 Beschluss des Gremiums); wLIGHT Cross-Chain-Brücke geht online; Antrag auf Notierung an der CEX wurde eingereicht; Entwicklerfinanzierungsplan beginnt | Aktive Bergleute ≥ 100.000; ≥ 100 Adressen gemeinsamer Kandidaten |
| Ökologische Expansionsperiode | Ab dem 2. Quartal 2029 (16. Monat + nach TGE) | Replikation im großen Maßstab | Die Zahl der aktiven Bergleute überstieg 200.000–500.000; 2-3 Investitionen wurden abgeschlossen; die erste Überprüfung der Gewinnrückführung; LIGHT Rückkauf und Zerstörung begonnen | Der Governance-Ausschuss arbeitet normal; das Anlagemodell wurde verifiziert |
| Ausgereifter Betriebszeitraum | Ab dem 4. Quartal 2029 (25. Monat + nach TGE) | Schwungraddrehung + vollständige Autonomie | Eintritt in die Autonomieperiode (wichtige Vorschläge aller Inhaber); kumulativer Einsatz des Anlageportfolios ≥ 30 Millionen US-Dollar; Deflationsdaten sind öffentlich überprüfbar | Die Governance ist vollständig dezentralisiert |

**Roadmap-Designprinzipien:**

- **Prüfung vor TGE:** Token werden niemals ohne Abschluss einer unabhängigen Sicherheitsprüfung ausgegeben. Dies ist die grundlegende Garantie für die Sicherheit der Benutzergelder.
- **Verifizierer kommen vor Benutzern:** Wenn das Hauptnetz online geht, gibt es ≥10 Verifizierer (BFT-Fehlertoleranz f≥3), um sicherzustellen, dass das Netzwerk nicht aufgrund eines Single Point of Failure heruntergefahren wird.
- **Investition geht der Expansion voraus:** Erst wenn die erste Investition erfolgreich ist und eine nachweisbare Gewinnrendite generiert, können wir mit der groß angelegten Expansion beginnen. Vermeiden Sie es, das Pferd von hinten aufzuzäumen, indem Sie „zuerst die Leute in Umlauf bringen und erst später Projekte finden“.
- **Zeitpuffer:** Reservieren Sie 20–30 % Zeitpuffer für jede Stufe. Technologieentwicklung, Audit-Reparaturen und rechtliche Prozesse können alle die Erwartungen übertreffen, und die Roadmap sollte kein „optimistischstes Szenario“ sein.

**Beziehung zum Veröffentlichungsdatum des Weißbuchs (4. August 2026):** Das Weißbuch wurde im August 2026 als öffentliche Erklärung der Vision und des technischen Designs des Projekts veröffentlicht. Die tatsächliche Umsetzung beginnt im vierten Quartal 2026 (Vorbereitungszeitraum) und das TGE-Ziel ist das vierte Quartal 2027. Die etwa 14 Monate dauernde Lücke zwischen der Veröffentlichung des Whitepapers und der TGE wurde für die Teambildung, Entwicklung, Prüfung und Compliance-Vorbereitung genutzt.

---

## Kapitel 11: Gemeinschaftskultur und Entwicklerökologie

### 11.1 Vier Werte

- **Transparenz ist besser als Perfektion** - Es ist besser, Unvollkommenheiten aufzudecken, als Perfektion zu verbergen. Alle Finanzströme, Investitionsentscheidungen und Governance-Abstimmungen sind dauerhaft in der Kette verfügbar.
- **Schrittweise ist besser als radikal** - Machen Sie kleine Schritte und iterieren Sie weiter. Die erste Investition beginnt bei 2 bis 5 Millionen US-Dollar und der Umfang wird nach Überprüfung des Modells erweitert.
- **Verantwortungen sind besser als Rechte** - Rechte und Pflichten sind gleich. Mitglieder des Governance-Ausschusses müssen 50.000 LIGHT zusagen und ihre politische Agenda offenlegen. Kommen sie ihren Pflichten nicht nach, wird ihnen ein Bußgeld auferlegt.
- **Vielfalt ist besser als Homogenität** - Unterschiedliche Stimmen sind die Immunität des Systems. Durch die zweidimensionale Abstimmung (Coin + Adresse) wird sichergestellt, dass sowohl Wale als auch Kleinanleger ein Mitspracherecht haben.

### 11.2 Jurysystem

| Abmessungen | Regeln |
|------|------|
| Zusammensetzung | Wählen Sie nach dem Zufallsprinzip 12 Benutzer aus, die über ≥ 10.000 LIGHTs verfügen und über keine Verstöße verfügen |
| Begriff | 30 Tage, wird nach Ablauf erneut ausgelost |
| Verantwortlichkeiten | Hören Sie sich Beschwerden über Betrugsstrafen, Anschuldigungen wegen Angebotsbetrugs und Community-Streitigkeiten an |
| Prozess | Bestrafte Nutzer können innerhalb von 72 Stunden Beweise vorlegen; Die Jury muss innerhalb von 48 Stunden ein Urteil fällen |
| Beurteilungsstandards | ≥8 von 12 Personen (2/3 Mehrheit) müssen der Aufrechterhaltung oder Aufhebung der Strafe zustimmen |
| Vermeidung | Automatischer Ersatz von Juroren, die in einem Einladungsverhältnis zu den Parteien stehen oder sich im gleichen IP-Bereich befinden |
| Vergütung | Erhalten Sie während der Laufzeit einen täglichen Jurydienstzuschuss von 5 LIGHT (ausgezahlt aus dem Ökofonds) |

### 11.3 Ökologischer Entwicklerplan

| Modul | Inhalt | Finanzierungsquellen | So bewerben Sie sich |
|------|------|---------|---------|
| Entwicklerfinanzierung (Zuschüsse) | Für Teams, die dApps, Tools und Infrastruktur in der LightDAO-Kette entwickeln, ein einziger Zuschuss von 5-500.000 US-Dollar entsprechend LIGHT | Ökologischer Entwicklungsfonds (lineare Freigabephase 2) | Einen Vorschlag einreichen → Bewertung des technischen Prüfers → Governance-Abstimmung (Mikrovorschlagsprozess) |
| SDK und API | Stellen Sie JavaScript/TypeScript SDK, REST API und WebSocket-Schnittstellen bereit, um den Schwellenwert für die Entwicklung durch Dritte zu senken | Der technische Prüfbeauftragte leitet die Entwicklung | Open Source, öffentlich auf GitHub |
| Hackathon | Jedes Quartal findet ein Online-Hackathon mit einem Preispool von 100.000 US-Dollar im Gegenwert von LIGHT | statt Ökologischer Entwicklungsfonds | Offene Registrierung, keine Schwelle |
| Bug Bounty | Kernvertrag-Bug-Bounty-Programm, Prämie zwischen 1.000 und 50.000 US-Dollar für eine einzige gültige Schwachstelle (abgestuft nach Schweregrad) | Versicherungsfonds + Fonds für ökologische Entwicklung | Einreichen über Immunefi oder eine selbst erstellte Plattform |
| CosmWasm-Vertragsmarkt | Ermutigen Sie Dritte, intelligente Verträge einzusetzen, und 20 % der Einnahmen aus den Gasgebühren werden an die Umweltkasse zurückgegeben, um Entwickler zu unterstützen | Gasgebührenverteilung (siehe Abschnitt 4.5) | Automatisch, keine Anwendung erforderlich |

### 11.4 Mehrsprachigkeit und Lokalisierungsstrategie

| 维度 | 规划 |
|------|------|
| 平台语言 | 首发支持英语、中文、西班牙语、葡萄牙语、菲律宾语；第6个月起增加法语、阿拉伯语、斯瓦希里语、印尼语 |
| 治理语言 | 提案和竞选纲领接受任何语言提交，系统提供机器翻译+社区人工校对 |
| 社区运营 | 按语言设立独立社区频道（Discord/Telegram），各频道配备本地化社区联络志愿者 |
| 文档翻译 | 白皮书及核心文档由社区翻译志愿者完成，翻译贡献计入"内容贡献"行为加成（5%） |
| 本地化资助 | 生态发展基金中预留10%（4,000万枚）专项用于本地化社区建设和翻译激励 |

---

## Kapitel 12: Team und Berater

### 12.1 Kernrollendefinition

| Rolle | Verantwortlichkeiten | Hintergrundanforderungen | Offenlegungsmethoden |
|------|------|---------|---------|
| Erster Vormund/Projektsponsor | Stellen Sie erste Verträge bereit, pflegen Sie Dokumente und koordinieren Sie frühe Vorgänge | ≥ 3 Jahre Erfahrung in der Blockchain-Branche, mit Smart-Contract-Einsatz oder DeFi-Protokoll-Betriebsaufzeichnungen | Geben Sie Ihre wahre Identität vor TGE bekannt oder legen Sie einen Bericht zur Identitätsüberprüfung durch einen Dritten vor (z. B. notarielle Unterschrift + Überprüfung der Nachricht in der Kette) |
| Technischer Leiter | Vertragsarchitekturdesign, Entwicklungsteammanagement, Audit-Docking | Cosmos SDK/CosmWasm-Entwicklungserfahrung, Bereitstellungsprotokoll in der Produktionskette | Wie oben |
| Verantwortlicher für Investitionen | Target-Screening, Due-Diligence-Koordination, SPV-Gründung, Exit-Management | Erfahrung in der Private-Equity-/Venture-Capital-Branche, mit abgeschlossenen Exit-Fällen | Wie oben |
| Compliance-Berater | Gestaltung der Rechtsstruktur, regulatorisches Docking, MLM-Compliance-Beratung | Anwalt mit US-/EU-/Cayman-Qualifikationen | Name der Anwaltskanzlei (persönlicher Name wird nicht bekannt gegeben, es sei denn, ich stimme zu) |

### 12.2 Beirat

- Bestehend aus 3-5 unabhängigen Beratern, die folgende Bereiche abdecken: DePIN-Technologie, grenzüberschreitende Investment-Compliance, Community Operations und Verbraucherindustrie;
- Berater erhalten eine Beratungsvergütung in Form von LIGHT-Tokens (ausgezahlt aus dem „Service Token Exchange“-Teil des strategischen Betriebsfonds), und die Position ist für 12 Monate gesperrt;
- Die Liste der Berater wird vor TGE veröffentlicht und ist offen für Community-Anfragen (dezentrales Text-Anfragetreffen, siehe Abschnitt 7.5);
- Berater dürfen nicht gleichzeitig Mitglieder des Governance-Ausschusses sein (Trennung von Interessenkonflikten).

### 12.3 Team-Engagement und Einschränkungen

| Einschränkungen | Regeln |
|------|------|
| Token-Sperre | LIGHT (einschließlich strategischer Betriebsmittelzuweisung), das vom Kernteam gehalten wird, muss für 12 Monate gesperrt und nach der Freischaltung linear für 36 Monate freigegeben werden |
| Verkaufsbeschränkungen | Dem ursprünglichen Vormund ist es während der Amtszeit (≤24 Monate) nicht gestattet, LIGHT zu verkaufen, das er über irgendeinen Kanal (einschließlich Airdrops, Belohnungen und Vergütungen) erhalten hat |
| Interessenkonflikt | Die Interessenkonflikte der Teammitglieder müssen zum Zeitpunkt der Ernennung vollständig offengelegt werden (ob sie andere DAO-Tokens besitzen, ob sie mit potenziellen Investitionszielen in Zusammenhang stehen) |
| Folgen einer unterlassenen Offenlegung | Sobald die Nichtoffenlegung eines Interessenkonflikts nachgewiesen ist, wird Ihnen die Teilnahme an der Governance dauerhaft untersagt und 50 % der freigeschalteten Token werden an den Versicherungsfonds konfisziert |
| Ersatzmechanismus | Wenn eine Kernrolle ausscheidet oder handlungsunfähig wird, bestimmt das Governance-Komitee (ursprünglicher Vormund + alternativer Vormund vor der Einrichtung) einen Nachfolger, der von der Gemeinschaft 72 Stunden lang ohne Einspruch öffentlich bekannt gegeben werden muss |

### 12.4 Kernbeitragszahlervergütung (20 % des strategischen Betriebsfonds)

- Gesamtbetrag: 50 Millionen LIGHTs (entspricht 2 % des Gesamtbetrags)
- Anzahl der abgedeckten Personen: 3-5 Personen
- Freigaberegeln: Dezember-Klippe + 36 Monate linear (d. h. ab dem 13. Monat werden jeden Monat etwa 1,157 Millionen Münzen freigegeben)
- Meilensteinbindung: Jedes Quartal bestätigt das Governance-Komitee (ursprünglicher Vormund + unabhängiger Dritter vor der Gründung), dass der Meilenstein erreicht ist, bevor die vierteljährliche Quote freigegeben werden kann.
- Offenlegungsregeln: Es werden nur der Gesamtbetrag und die Freigaberegeln offengelegt, persönliche Namen und Einzelquoten werden nicht offengelegt (zum Schutz der Privatsphäre und gleichzeitig kann der Gesamtbetrag durch die Multi-Signatur-Adresse in der Kette überprüft werden, um sicherzustellen, dass der Gesamtbetrag nicht überschritten wird).

---

## Kapitel 13: Risikowarnung und Haftungsausschluss

### 13.1 Risikowarnung

| Risikoart | Beschreibung | Schadensbegrenzungsmaßnahmen |
|---------|------|---------|
| Marktrisiko | LIGHT-Preise können erheblich schwanken und historische Preise stellen keine zukünftige Wertentwicklung dar. TGE verfügt über eine begrenzte Anfangsliquidität und die Preise können stark schwanken | Faire Preise bei niederländischen Auktionen; ±50 % Leistungsschalter 72 Stunden nach TGE; Anti-Todesspirale, vierstufiger Interventionsmechanismus |
| Projektrisiken | Das Investitionsziel kann Verluste erleiden, das Risikokapitalprojekt kann scheitern und das Kapital kann vollständig verloren gehen. Die historische durchschnittliche Ausfallrate der PE/VC-Branche liegt bei etwa 50-70 % (Einzelgeschäft) | Zweimotorige Dezentralisierung (70 % Cashflow + 30 % Wachstum); Einzelziel ≤ 25 %; Industrie ≤ 40 %; Region ≤ 30 %; 10 % Rückstellung für Krankenkassen |
| Technische Risiken | Intelligente Verträge können unentdeckte Schwachstellen aufweisen. Die Browserkompatibilität kann sich auf das Mining-Erlebnis auswirken. Cross-Chain-Brücken können angegriffen werden | Unabhängiges Audit + formelle Verifizierung vor TGE; Fehlerprämie 1.000–50.000 US-Dollar; 72-Stunden-Zeitsperre; Multi-Signatur-Aufhängungsmechanismus |
| Regulatorische Risiken | Die Regulierungsrichtlinien in verschiedenen Ländern und Regionen können sich ändern, was dazu führen kann, dass die Funktionen eingeschränkt sind oder Benutzer in bestimmten Regionen nicht teilnehmen können | Cayman SPV-Struktur; Standardmäßige Nullverifizierung (die Verifizierung wird von einem lizenzierten Dritten auf seiner Serviceseite durchgeführt); Der Front-End-IPFS-Spiegel ist zensurresistent. nicht in bestimmten Ländern vermarktet |
| Liquiditätsrisiko | Möglicherweise mangelt es dem Sub-Token in der Anfangsphase an ausreichender Handelstiefe; LIGHT könnte in der frühen Phase von TGE | unter Verkaufsdruck geraten Die anfängliche Liquidität des Sub-Tokens AMM (6 % der Emission); 30-tägige Übertragungssperrfrist; Team/Investor 12-Monats-Cliff + 36-Monats-Linear |
| Verwässerungsrisiko | Wenn die Zahl der aktiven Miner steigt, werden die Pro-Kopf-Mining-Einnahmen natürlich verwässert (BaseReward-Nenner erhöht sich) | Designabsicht: Frühe Teilnehmer gehen höhere Risiken ein, um höhere Renditen zu erzielen; spätere Benutzer können die Akkumulation durch das Teilen von Einladungen beschleunigen; die Governance-Schwelle wird dynamisch gesenkt |
| Operationelles Risiko | Der Betrieb und das Management des investierten Unternehmens entsprechen möglicherweise nicht den Erwartungen; SPV-Operationen sind auf externe Direktoren angewiesen; Das Investmentteam könnte verloren gehen | Beschränkungen der SPV-Charter + unabhängige Direktoren; DAO kann für die Ersetzung von Direktoren stimmen; SIAC/ICC-Schiedsklauseln; Schlüsselpersonenversicherung (in Erforschung) |
| Cross-Chain-Bridge-Risiken | Die wLIGHT-Cross-Chain-Brücke wird von einem Dritten betrieben und Lücken im Bridge-Vertrag können zu Vermögensverlusten führen (in der Vergangenheit waren Cross-Chain-Bridges die größte einzelne Verlustquelle) | Unabhängiges Audit, bevor die Brücke online geht; Brückenvermögen übersteigt nicht 5 % des Gesamtangebots; Offenlegung von Risiken; Benutzer können wählen, nur die native Kette | zu verwenden
| Validatorrisiko | Wenn Validatoren gemeinsam offline gehen oder Böses begehen, kann dies dazu führen, dass die Kette die Blockproduktion stoppt und alle Benutzeroperationen (Mining, Abstimmung, Transfers) vorübergehend nicht verfügbar sind | Tendermint BFT verträgt <1/3 des Übels; Validatoren ≥ 21 (f=6); Hiebstrafe; Notfall-Migrations-Abstimmungsmechanismus |

### 13.2 Haftungsausschluss

- LIGHT und Sub-Token sind keine Wertpapiere, haben keinen inneren Wert und der Preis kann auf Null zurückfallen. Dieses Whitepaper stellt keinerlei Wertpapieremissionsdokument, Anlageangebot oder Anlageberatung dar.
- Die Einkommensverteilung der Vereinbarung hängt von der tatsächlichen Betriebsleistung der zugrunde liegenden Vermögenswerte ab und historische Daten stellen keine zukünftigen Einnahmen dar. Jegliche Beschreibungen der Anlagerenditen sind zukunftsgerichtete Schätzungen und keine Versprechen.
- Der Benutzer muss alle Verluste tragen, die durch den Verlust oder den Verlust des privaten Schlüssels entstehen, und die Vereinbarung sieht keine Abrufdienste vor. Die Verwendung einer Tier-1- (Passkey) oder Tier-2-Wallet (Social Recovery) verringert dieses Risiko, beseitigt es jedoch nicht.
- Diese Vereinbarung steht Benutzern auf der ganzen Welt offen (vorbehaltlich der geltenden Gesetze und Vorschriften). Benutzer sollten die rechtliche Haltung gegenüber Kryptowährungs-Assets, DAO-Organisationen und SPV-Einkommenszertifikaten in ihrer Gerichtsbarkeit bestätigen und sicherstellen, dass ihre Teilnahme legal und konform ist.
- Die zukunftsgerichteten Aussagen in diesem Whitepaper (einschließlich Roadmaps, Ertragsmodelle, Deflationsschätzungen, Prognosen zum Investitionsumfang) sind Vorhersagen, die auf aktuellen Annahmen basieren. Die tatsächlichen Ergebnisse können aufgrund von Markt-, Technologie-, Regulierungs-, Teamausführungs- und anderen Faktoren erheblich abweichen.
- Einladungsanreize sind ein einstufiger Sharing-Mechanismus und stellen kein mehrstufiges Marketing oder Pyramidensystem dar. Benutzer sollten sich jedoch dennoch über die rechtliche Einstellung zu Empfehlungsprämien in ihrem Zuständigkeitsbereich informieren.
- Das Mindestalter für die Teilnahme am LightDAO-Ökosystem beträgt 18 Jahre (oder das gesetzliche Volljährigkeitsalter in Ihrer Gerichtsbarkeit, je nachdem, welches höher ist). Minderjährigen ist es nicht gestattet, sich am Bergbau, an der Regierungsführung oder an Investitionen zu beteiligen.

---

## Anhang A: Übersichtstabelle der wichtigsten Parameter

| Kategorie | Parameter | Wert |
|------|------|------|
| Ausgabe | Gesamtbetrag | 2,5 Milliarden Stück, nie mehr ausgegeben |
| Ausgabe | Bergbau | 40 % = 1 Milliarde Münzen |
| Ausgabe | Anlagetresor | 34 % = 850 Millionen Münzen |
| Ausgabe | Ökologischer Fonds | 16 % = 400 Millionen Stück |
| Ausgabe | Strategische Operationen | 10 % = 250 Millionen Münzen (Dienstleistung 50 %/Finanzierung 30 %/Geber 20 %) |
| Ausgabe | Halbierungszyklus | Alle 2 Jahre |
| Ausgabe | Veröffentlichung zum ersten Era-Tag | ≈684.900 (Miner 95 % = 650.700, Validatoren 5 % = 34.200) |
| Ausgabe | Belohnungspool pro Block | ≈13,87 LICHT |
| Bergbau | Beitragsgewicht | Bandbreite 40 %/Sitzung 30 %/Verifizierung 20 %/Stabilität 10 % |
| Bergbau | Voller Bonus | 1,44 mal |
| Einladung | Evangelist/Botschafter/Partner | 3 Personen 10 %+100 l/10 Personen 15 %+500 l+5 %/50 Personen 20 %+2500 l+10 % |
| Verhalten | Vier Artikel × 5 % | Obergrenze 20 % |
| Gasgebühr | Preismechanismus | USD-äquivalente Verankerung, vom Orakel automatisch alle 24 Stunden in LIGHT-Menge umgewandelt |
| Gasgebühr | Normale Überweisung | Äquivalent von 0,001 $ (@0,05 $=0,02 LICHT) |
| Gasgebühr | Governance-Abstimmung | Äquivalent von 0,005 $ (@0,05 $=0,10 LICHT) |
| Gasgebühr | Verteilungsregeln | 50 % Zerstörung / 30 % Validatoren / 20 % ökologische Schatzkammer |
| Deflation | Verlangsamung/Frühwarnung/Fazit | ≤1,5 Milliarden/≤1,2 Milliarden/≤1 Milliarde (Umlaufmenge) |
| Deflation | Theoretische Obergrenze | 1,65 Milliarden (10+4+2,5, 850 Millionen in der Staatskasse werden niemals in Umlauf gebracht) |
| Governance | Vorschlagsschwelle | ≥5.000 LICHT + 30 Tage Einsatz |
| Governance | Komitee-Einsatz | 50.000 LICHT + 100 Adressen |
| GOVERNANCE | JURY | 10.000 LICHT |
| Governance | Wetten | 5—500 LICHT |
| Governance | Reputationsbonus | 1 Jahr +15 Stimmen → +30 % (Gesamtobergrenze +40 %) |
| Investition | Einzellimit | Verbleibender Tresor × 15 % (ursprünglich 127,5 Millionen Münzen) |
| Investition | Baseline bereitstellbar | 850 Millionen US-Dollar × 0,15 US-Dollar × 75 % = 95,63 Millionen US-Dollar ≈ 100 Millionen US-Dollar |
| Investition | Gewinnausschüttung (jährlich) | 40/30/20/10 |
| Investition | Gewinnverteilung (Ausstieg) | 70/30 |
| Auktion | Ziel | 15 Millionen US-Dollar (5 Millionen US-Dollar Reserve + 10 Millionen US-Dollar investiertes Kapital) |
| Reserven | Stabiles Finanzministerium | TGE 5 Millionen US-Dollar → Monat 24 8 Millionen US-Dollar |
| Versicherung | Gewinn | Gewinn 10 % |
| Airdrop | Gesamtbudget | 55 Millionen (ökologischer Fonds 13,75 %), CAC≈$55/behaltener Benutzer |
| Validatoren | Initiale/Kappe | 21 (mindestens 10) / 100 |
| Validator | Mindesteinsatz | 500.000 LICHT |
| Prüfer | TGE hartes Endergebnis | ≥7, sonst darf es nicht online gehen |

---

## Anhang B: Numerische Ableitung und Verifizierung

### B.1 Bergbauproduktion

2A=1 Milliarde→A=500 Millionen. Tägliche Veröffentlichung = 500 Millionen ÷ 730 = 684.932 ≈ 684.900. Mining-Pool=684.932×95 %=650.685≈650.700. Prüfer=684.932×5 %=34.247≈34.200. Jeder Block = 684.932 ÷ 49.371 ≈ 13,87. Verifizierung: 684.932×730=499.999.960≈500 Millionen ✓

### B.2 Zugänglichkeit von Governance-Schwellenwerten

100.000 Miner-Benchmark (6,51/Tag, Partner 74,44/Tag): Vorschlag 5.000→768 Tage/67 Tage; Ausschuss 50.000→7.684 Tage (21 Jahre)/672 Tage (22 Monate); Jury 10.000→1.537 Tage (4,2 Jahre)/134 Tage (4,5 Monate); Wette 500→77 Tage/6,7 Tage.

Seed-Zeitraum (10.000 Miner, 65,07/Tag, Partner 744,4/Tag): Vorschlag → 77 Tage (2,5 Monate) / 6,7 Tage; Ausschuss → 768 Tage (25 Monate) / 67 Tage (2,2 Monate); Jury → 154 Tage (5 Monate) / 13,4 Tage.

### B.3 Deflationszeitplan

Umlaufvolumen = Bergbau + Ökologie + Strategie (verfallbar) − Tausch − Gas − Rückkauf. 850 Millionen in der Staatskasse werden niemals in Umlauf gebracht.

| Jahr | Kumulativer Bergbau | Ökologie | Strategie | Austausch | Gas | Rückkauf | Auflage |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2,50 | 2,80 | 0 | 0 | 0,01 | 0 | ≈5,29 |
| 2 | 5,00 | 4,00 | 0,83 | 0,05 | 0,02 | 0 | ≈9,76 |
| 3 | 6,25 | 4,00 | 1,67 | 0,20 | 0,03 | 0,05 | ≈11,64 |
| 4 | 7,50 | 4,00 | 2,50 | 0,45 | 0,04 | 0,20 | ≈13,31(Spitze) |
| 5 | 8.13 | 4,00 | 2,50 | 0,80 | 0,05 | 0,50 | ≈13,28 |
| 6 | 8,75 | 4,00 | 2,50 | 1,20 | 0,06 | 0,90 | ≈13,09 |
| 7 | 9.06 | 4,00 | 2,50 | 1,60 | 0,07 | 1,40 | ≈12,49 |
| 8 | 9,38 | 4,00 | 2,50 | 2,00 | 0,08 | 1,90 | ≈11,89 |
| 9 | 9,53 | 4,00 | 2,50 | 2,40 | 0,09 | 2,30 | ≈11,24 |
| 10 | 9,69 | 4,00 | 2,50 | 2,80 | 0,10 | 2,70 | ≈10,59 |
| 11 | 9,77 | 4,00 | 2,50 | 3.10 | 0,11 | 3,00 | ≈10,06 |
| 12 | 9,84 | 4,00 | 2,50 | 3,40 | 0,12 | 3,30 | ≈9,52 |

Fazit: Der Höhepunkt Y4≈1,331 Milliarden; die Warnlinie von 1,2 Milliarden wird von Y8 berührt; das Endergebnis von 1 Milliarde wird von Y11-12 berührt; Die Verzögerungslinie von 1,5 Milliarden ist nur ein Szenario mit extrem geringer Zerstörung.

---

## Anhang C: Audit-Korrekturprotokoll (insgesamt 36 Elemente)

Enthält 22 Originalgegenstände (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 technische Architekturgegenstände (T1-7) + 7 Wirtschaftsmodelloptimierungsgegenstände in dieser Runde:

| Nummer | Korrektur |
|------|------|
| E-1 | Gesamtbetrag 2,1 Milliarden → 2,5 Milliarden (bedingt durch Einschränkungen der Investitionskapazität) |
| E-2 | Zuteilung 50/30/20→40/34/16/10 (10 % der neuen strategischen Betriebsmittel) |
| E-3 | Niederländische Auktion 10 Mio. $→15 Mio. $ (Anfangsinvestitionskapital 5 Mio. $→10 Mio. $) |
| E-4 | Neuer 5,7-teiliger Airdrop-Wachstumsplan (55 Millionen Stück, CAC $ 55/Person) |
| E-5 | Verifizierer werden schrittweise eingeführt (Testnet 7→TGE mindestens 10/Target 21→Open 100) |
| E-6 | Anpassung der Deflationsauslöselinie (14.12.10 → 15.12.10, angepasst an die Umlaufgrenze von 1,65 Milliarden) |
| E-7 | Ersetzen Sie alle externen Zitate durch überprüfbare Quellen (entfernen Sie nicht überprüfbare SSRN-Papiere) |

---

## Anhang D: Kurzindex der Begriffe

Eine vollständige Erklärung jedes Begriffs finden Sie im Kommentarblock [Begriffe in diesem Kapitel] am Ende des Kapitels, in dem er zuerst erscheint. Dieser Index listet alle Begriffe und ihre Kapitel in alphabetischer Reihenfolge auf, um eine schnelle Navigation zu ermöglichen.

| Terminologie | Definition Kapitel |
|------|------------|
| AMM (Automatisierter Market Maker) | Kapitel 4 |
| BFT (Byzantinische Fehlertoleranz) | Kapitel 4 |
| CAC (Kundenakquisekosten) | Kapitel 5 |
| CEX (Zentralisierte Börse) | Kapitel 4 |
| Cosmos SDK | Kapitel 4 |
| CosmWasm | Kapitel 4 |
| DAO (Dezentrale Autonome Organisation) | Kapitel 2 |
| DCF (Discounted-Cashflow-Methode) | Kapitel 9 |
| DePIN (Dezentrales physisches Infrastrukturnetzwerk) | Kapitel 2 |
| DEX (Dezentrale Börse) | Kapitel 4 |
| EBITDA (Ergebnis vor Zinsen, Steuern und Abschreibungen) | Kapitel 9 |
| Gasgebühr | Kapitel 4 |
| IBC (Inter-Chain-Kommunikationsprotokoll) | Kapitel 3 |
| IPFS (InterPlanetary File System) | Kapitel 4 |
| KYC (Kennen Sie Ihren Kunden) | Kapitel 3 |
| LIGHT (natives Token) | Kapitel 4 |
| LP (Liquiditätsanbieter) | Kapitel 5 |
| Lower Middle Market PE (Downstream Middle Market Private Equity) | Kapitel 2 |
| Merkle-Baum | Kapitel 4 |
| MiFID II (EU-Richtlinie über Märkte für Finanzinstrumente II) | Kapitel 3 |
| MLM (Multi-Level-Marketing) | Kapitel 3 |
| PII (persönlich identifizierbare Informationen) | Kapitel 3 |
| PoC (Beitragsnachweis) | Kapitel 4 |
| PoS (Proof of Stake) | Kapitel 4 |
| PoW (Arbeitsnachweis) | Kapitel 4 |
| Vor dem Börsengang | Kapitel 9 |
| PWA (Progressive Webanwendung) | Kapitel 4 |
| Reg D / Reg S (Regulation D/S des U.S. Securities Act) | Kapitel 3 |
| Schlitzen | Kapitel 4 |
| SPV (Spezialfahrzeug) | Kapitel 2 |
| TGE (Token-Generierungsereignis) | Kapitel 5 |
| TWAP (Zeitgewichteter Durchschnittspreis) | Kapitel 4 |
| TWAP-Ausführung (Rückkauf- und Split-Orders) | Kapitel 9 |
| VWAP (Volumengewichteter Durchschnittspreis) | Kapitel 5 |
| wLIGHT (gekapseltes LICHT) | Kapitel 5 |
| ZK-KYC (Zero-Knowledge Proof KYC) | Kapitel 3 |
| Untertoken | Kapitel 5 |
| Todesspirale | Kapitel 5 |
| Halbierung | Kapitel 5 |
| Finanzministerium (Finanzministerium) | Kapitel 5 |
| Niederländische Auktion | Kapitel 5 |
| Orakel | Kapitel 4 |

---

**Vollständig weiße Papierenden**

**Urheberrechtserklärung:** Dieses Dokument ist ein Open-Source-Community-Dokument und kann frei reproduziert werden, der vollständige Inhalt muss jedoch erhalten bleiben.

---

# Anhang: Mainnet-verifizierte Parameter und Adressen (V2.4 live)

## A. §4.5 Gas 经济实测参数
- min-gas-price 公式:`(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`;当前 TransferUsdTarget=$0.001、UsdPerLight=$0.05、RefTransferGas=100000 → **0.2 ulight/gas**
- 分配实测(总 fee 300000 ulight):销毁 150000(50%)/ 金库 60000(20%)/ 验证者 90000(30%),精确匹配
- 销毁地址:`wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(确定性死地址)
- 金库:`treasury_multisig` 合约(3/5 多签;链上 `signers` 查询返回 5 名签名人,阈值本身不在查询接口内)

## B. 核心合约地址
见仓库 `docs/MAINNET_STATUS.md`(light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting 等 10 合约)。

## C. Entsorgung des Altwerts (Anteils).
Genesis Mismatch mint_denom=stake wurde auf Null zurückgesetzt und die weitere Ausgabe wurde gestoppt; Der bestehende Anteil (ungefähr 2,56e11 Mikroeinheiten) bleibt zwecklos, und der Veräußerungsplan (Austausch/Zerstörung) steht unter dem Vorbehalt von Governance-Vorschlägen und wird das Ulight-Wirtschaftsmodell nicht beeinträchtigen.

## D. §4.4 Live-Übertragung
Vault 250.000.000 LIGHT, 3 unabhängige Zeitpläne: 75M (Klippe 0)/ 100M (Klippe 1 Jahr)/ 75M (Klippe 2 Jahre), bereits in der Kette.

## E. 安全实践
- 主网升级为 x/upgrade 治理 + 全节点同块高协调 + auto-swap 看门狗,测试网端到端彩排后执行
- Passkey 种子仅密文存储;Shamir 分片本地不保存
- 合约挖矿根提交阈值 5(链上每笔 `submit_root` 事件实测 threshold=5;当前 5 个授权账户在签,7 席为设计目标);反女巫/反作弊见 §4.8
