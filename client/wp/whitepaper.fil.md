> Awtomatikang pagsasalin, hindi sinusuri ng tao. Kung may hindi pagkakatugma, ang orihinal na Tsino ang may kapangyarihan.
[中文原文 / Chinese original](/whitepaper.md)

# LightDAO White Paper V2.4 (2026-09-26 Mainnet Live na Bersyon)

> Nakabatay ang bersyon na ito sa draft ng disenyo ng V2.0, na may "live na deployment ng mainnet" at "mga pagbabago sa bersyon" sa harap, at idinagdag ng mga na-verify na on-chain na parameter. Ang pangunahing teksto (Kabanata 1~12) ay nananatiling hindi nagbabago mula sa disenyo ng V2.0; para sa anumang mga paglihis mula sa aktwal na sitwasyon, ang mga nakaraang tala at apendise ng seksyong ito ay mananaig.

## Mga pagbabago sa bersyon (V2.0 → V2.4)
- 2026-11-04 Errata (huwag baguhin ang numero ng bersyon, V2.4 pa rin): Ang orihinal na vault na `treasury_multisig` sa apendiks na "Mga Na-verify na Parameter at Address ng Mainnet" ay 5/7 multisig, na sumasalungat sa 3/5 ng tekstong §7.2/§7.3/§8.1, at sumasalungat din sa chain sa aktwal na sukat. (`{"signers":{}}` ay nagbabalik ng 5 address, walang 7 signers); ito ay pinag-isa bilang 3/5 ayon sa teksto, at ipinapahiwatig na ang threshold mismo ay wala sa loob ng interface ng query ng kontrata at maaari lamang suportahan ng mga talaan ng pag-deploy. Ang orihinal na mining root na nakasulat sa parehong seksyon ay "5/7 verifier multi-signature", at ang aktwal na pagsubok ay maaari lamang patunayan ang threshold na 5 (ang threshold ng 115 `submit_root` na kaganapan ay 5 lahat, at ang aktwal na bilang ng mga signing account ay eksaktong 5). Ang 7-seat na awtorisasyon ay ang layunin ng disenyo, at kasalukuyang walang on-chain na ebidensya. Ang mga salita ay binago nang naaayon.

1. **§4.5 Gas Economy: Na-deploy at na-verify sa mainnet**. Ang USD na naka-angkla sa dynamic na min-gas-price at 50% na pagkasira / 30% validators / 20% treasury allocation ay ipinatupad noong 2026-09-24 pagkatapos ilunsad ang panukala sa pamamahala (v2-lightfee) sa taas na 58627, 7 validators ang nag-coordinate ng paglipat, at ang pagsubok na network ay nag-ensayo upang mag-ensayo. Aktwal na pagsukat sa pangunahing network: ang mga hindi sapat na bayarin ay tinatanggihan, at ang buong bayarin ay tumpak na inilalaan ayon sa 50/30/20.
2. **Paglilinaw ng katutubong denom**: Ang staking/pamamahala/Gas ay `ulight` (LIGHT, 6 decimal place, kabuuang supply 2.5 bilyon). Ang inflation ng `stake` na hindi tumugma sa genesis ay na-reset sa zero (mint inflation=0) ng panukala sa pamamahala noong 2026-09-24. Ang pagpapalabas ng LIGHT ay ganap na pinapasan ng kontrata ng mining_reward, na inaalis ang dobleng pagpapalabas; ang umiiral na stake ay ang legacy denom na itatapon (tingnan ang Appendix C).
3. **§4.7 WebRTC Relay: Na-deploy**. 8 node coturn (TURN/STUN, TLS certificate turn-*.lightdao.net) + WSS signaling + REST temporary certificate (HMAC-SHA1); Ang mga channel ng data ng P2P ng kliyente ay magkaparehong ipinadala, at ang mga relay byte ay binibilang bilang 40% na kontribusyon sa bandwidth; end-to-end na aktwal na pagsukat ay matagumpay sa pamamagitan ng TURN relay transmission. Gumagamit ang Symmetric NAT ng TURN at nabigong mag-downgrade sa purong authentication mode (naaayon sa §4.7).
4. **§4.9 Smart Wallet: Online**. Passkey/WebAuthn seedless login (PRF derived key + AES-GCM ciphertext storage, plaintext ay hindi nahuhulog sa lupa) + Shamir 3-of-5 social recovery; Ang mnemonic na parirala ay pinanatili bilang isang pagpipiliang fallback.
5. **§4.10 Oracle ng Presyo: Ang feed ng presyo ay pinatakbo na**. 7 Ang verifier cron ay humalili sa pagsusumite ng external_median sa oracle_twap (kasalukuyang reference na presyo 50000 = $0.05); Ang TWAP sa chain ay isaaktibo pagkatapos maitatag ang LIGHT/USDC liquidity pool. Pagkatapos ng v3 upgrade, ang lightfee ay direktang nagbabasa ng external_median at nagko-convert ng dynamic na min-gas.
6. **Pamamahala ng Parameter**: Ililipat ng pag-upgrade ng v3 ang BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract ng lightfee sa on-chain na paramstore. Maaaring isaayos ang mga panukala ng parameter ng pamamahala sa runtime, na inaalis ang pangangailangang mag-coordinate ng mga upgrade.

## Live na pag-deploy ng Mainnet (2026-09-26)

- Chain na `lightdao-mainnet-1`, 7 validators (JP/KR/SG/US/HK/FR/UK) lahat ay naka-BOND, walang nakakulong; matugunan ang hard bottom line ng §4.7 "Ang mga verifier <7 ay hindi pinapayagang mag-TGE"
- Kliyente https://lightdao.net (PWA): Passkey wallet + mining + WebRTC relay + collection, multi-language (Chinese/English/Spanish)
- Sarado na loop ng pagmimina: Kontribusyon ng browser → Pang-araw-araw na pagsasapinal ng gateway → Ang Merkle root 5 ay nilagdaan sa chain (threshold 5, maaaring suriin sa chain) → Ang mga minero ay tumatanggap ng patunay na may patunay; Ang pang-araw-araw na ugat ay patuloy na isinumite
- Pamamahala sa pag-upgrade: v2-lightfee (inilapat @58627), mint zeroing (inilapat), v3-lightfee (nagkaisang pumasa, ang taas 118055 ay awtomatikong lumilipat)
- Para sa kumpletong endpoint/address ng kontrata/ history ng pag-upgrade, pakitingnan ang warehouse `docs/MAINNET_STATUS.md`

---

#LightDAO White Paper V2.0

** Buong text verification at proofreading optimized na bersyon (international web client · numerical audit · third party audit · economic model optimized na bersyon) **

Petsa ng paglabas: Agosto 4, 2026

Pangunahing prinsipyo: Ang mga browser ay mga node, lahat ay maaaring lumahok, at ang mga kita ay ibinabahagi ayon sa mga panuntunan

Legal na pagpoposisyon: Ang LIGHT at mga sub-token ay nakaposisyon bilang mga punto ng kontribusyon sa ekolohiya at mga sertipiko ng mga karapatan sa paghahabol sa pamamahagi ng kita ng SPV, at hindi mga securities o produktong pinansyal; ang mga partikular na legal na katangian ay napapailalim sa mga wastong legal na opinyon sa mga nauugnay na hurisdiksyon.

> Ang dokumentong ito ay isang na-verify at na-optimize na bersyon ng buong teksto ng puting papel at hindi bumubuo ng payo sa pamumuhunan, mga dokumento sa pag-iisyu ng mga securities, mga paglalarawan ng produkto sa pananalapi o anumang anyo ng pangako sa garantiya ng kapital. Mangyaring kumunsulta sa legal, buwis at mga propesyonal sa pananalapi bago lumahok.

---

## Talaan ng nilalaman

- Paunang pagdedeklara
- Prologue: Ang kwento ng tatlong tao
- Kabanata 1: Ang katotohanang nakikita natin
- Kabanata 2: Sagot ni LightDAO
- Kabanata 3: Pagsunod at legal na paghihiwalay
- Kabanata 4: Teknikal na Arkitektura
- Kabanata 5: Modelong Pang-ekonomiyang Token
- Kabanata 6: Mekanismo ng Pamamahala
- Kabanata 7: Mga pagsusuri at balanse ng kapangyarihan at kahulugan ng tungkulin
- Kabanata 8: Tiwala at Mekanismo ng Seguridad
- Kabanata 9: Mga operasyon sa pamumuhunan at mga diskarte sa paglabas
- Kabanata 10: Roadmap
- Kabanata 11: Kultura ng komunidad at ekolohiya ng developer
- Kabanata 12: Koponan at Mga Consultant
- Kabanata 13: Babala sa Panganib at Disclaimer
- Appendix A: Talaan ng buod ng mga pangunahing parameter
- Appendix B: Derivation ng numero at pagpapatunay
- Appendix C: Log ng Pagwawasto ng Audit
- Appendix D: Mabilis na Reference Index ng mga Tuntunin

---

## Executive Summary

**Ano ang LightDAO:** Isang desentralisadong autonomous na organisasyon na nagpapahintulot sa mga ordinaryong tao sa buong mundo na lumahok sa mga totoong pamumuhunan sa negosyo at magbahagi ng mga kita sa pamamagitan ng browser. Hindi kailangan ng mga user na bumili ng mining machine, magkaroon ng teknikal na background, o matugunan ang threshold ng mga kwalipikadong mamumuhunan - sa pamamagitan lamang ng isang browser at kaunting oras, ang mga user ay maaaring mag-ambag ng mga mapagkukunan ng network upang makatanggap ng LIGHT token reward, at lumahok sa mga desisyon sa pamumuhunan sa pamamagitan ng pagboto sa pamamahala.

**Anong problema ang nalutas:** Ang pinakamababang 50% ng pandaigdigang populasyon (humigit-kumulang 4 bilyong tao) ay nagmamay-ari lamang ng 2% ng kabuuang kayamanan (World Inequality Lab, 2026). Ang mga asset na may mataas na kalidad (pribadong equity, venture capital) ay hindi kasama ng kwalipikadong investor threshold ($200,000 taunang kita/$1 milyon netong halaga). Bagama't mayroong "universal participation" na salaysay sa larangan ng cryptocurrency, ang karamihan sa mga token sa kalaunan ay bumalik sa zero (CoinGecko 2025: 11.56 million token ang namatay), at ang DAO governance participation rate ay mga 3-12% lamang.

**Paano ito lutasin:** Dual-engine model - 70% ng mga pondo ay ini-invest sa antas ng komunidad na mahigpit na mga asset ng consumer (cash flow engine), at 30% ay na-invest sa cutting-edge na teknolohiya (growth engine). Ang mga pamumuhunan ay isinasagawa sa pamamagitan ng Cayman SPV, at ang mga kita ay ipinamamahagi ayon sa on-chain na mga panuntunan: 40% sa mga may hawak ng sub-token, 30% pabalik sa vault para sa muling pamumuhunan, 20% muling bumili ng LIGHT para sa pagkasira, at 10% na naipon sa mga pondo ng insurance.

**Mga Pangunahing Data:**

| Mga tagapagpahiwatig | Mga Halaga |
|------|------|
| Kabuuang halaga ng LIGHT | 2.5 bilyon, hindi kailanman maibibigay |
| Investment Vault | 850 milyon (baseline deployable ≈ $100 milyon) |
| Output ng pagmimina | 1 bilyon, hinahati bawat 2 taon |
| Inilabas sa Araw ng Unang Panahon | ≈684,900 piraso (average na 6.51/araw kapag nagtatrabaho ang 100,000 minero) |
| Deflation bottom line | Permanenteng ihinto ang pagsunog kapag ang sirkulasyon ay ≤ 1 bilyon (taon 11-12 ng base scenario) |
| Threshold ng Pamamahala | Panukala ≥ 5,000 LIGHT; Komite ≥ 50,000 ILAW |
| Technology Stack | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Mga Verifier | Initial 21 (minimum 10), upper limit 100 |
| Paunang financing | Dutch auction $15 milyon + Pre-TGE strategic financing $2.25-3.75 milyon |

**Differentiation:** Kasalukuyang ang tanging proyekto na pinagsasama ang "zero-threshold web mining" sa "compliant SPV entity investment." Iba sa Pi Network (walang praktikal na utility), Helium (nangangailangan ng $200+ hardware), at tradisyonal na DAO (high threshold elite governance).

**Roadmap:** 2026 Q4 paghahanda → 2027 Q1-Q2 development → Q3 audit test → Q4 TGE online → 2028 Q1 seed users → Q2-Q3 first investment → Q4 onwards scale.

---

## Paunang pagdedeklara

**Hindi ito isang panukala sa pamumuhunan**

Ang "ecological rewards" at "agreement income distribution" na inilalarawan sa white paper na ito ay mga insentibong pagsasaayos na nabuo ng endogenous na mekanismo ng kasunduan at hindi bumubuo ng anumang anyo ng mga securities issuance, pinansiyal na pagbebenta ng produkto, capital guarantee commitments o investment advice.

Ang LIGHT at sub-token ay walang intrinsic na halaga at ang presyo ay maaaring bumalik sa zero. Bago lumahok, mangyaring kumonsulta sa iyong sariling legal, buwis at pinansyal na mga propesyonal, at tanggapin ang buong responsibilidad para sa pribadong pag-iingat ng susi, deklarasyon ng buwis at paglahok.

---

## Prologue: Ang kwento ng tatlong tao

Nagtatrabaho si Maria bilang food delivery rider sa Maynila, nagtatrabaho ng 12 oras sa isang araw at kumikita ng humigit-kumulang 15,000 Philippine pesos (humigit-kumulang US$270) bawat buwan. Gusto niyang mamuhunan sa sikat na milk tea chain brand sa tabi, ngunit sinabi sa kanya ng kabilang partido: "Ang minimum na pamumuhunan ay nagsisimula sa US$25,000." Hindi makaipon si Maria ng US$25,000.

Nagmamaneho si Kwame ng ride-hailing service sa Lagos. Siya ay optimistiko tungkol sa artificial intelligence track at gustong mamuhunan sa isang maliit na kumpanya ng teknolohiya sa pananalapi. Sinabi sa kanya ng institusyon: "Ang minimum na halaga ng subscription ay US$100,000, at ang lock-in na panahon ay 5 taon." Hindi makabuo si Kwame ng US$100,000.

Si Elena ay isang retiradong guro sa São Paulo na may buwanang pensiyon na humigit-kumulang 3,000 Brazilian reals (humigit-kumulang US$550). Narinig niya na kumikita ang mga anak ng kanyang kapitbahay na nagtatrabaho sa mga kumpanya ng blockchain, ngunit hindi niya mabasa ang puting papel at hindi niya alam kung paano bumili at mag-configure ng mga propesyonal na kagamitan sa pagmimina.

Ang tatlo sa kanila ay kumakatawan sa karamihan ng mga ordinaryong tao sa buong mundo: mayroon silang paghuhusga at pagpayag na lumahok, ngunit kulang sila sa mababang limitasyon, malinaw at abot-kayang mga channel ng pakikilahok.

Idinisenyo ang LightDAO para sa mga taong ito. Gamit ang isang Internet-enabled na device, isang browser, at isang maliit na halaga ng pera, maaari kang lumahok sa ecological construction; sa pamamagitan ng isang sumusunod na istraktura ng SPV, ang mga gumagamit ay mayroon ding pagkakataon na hindi direktang ma-access ang pamamahagi ng cash flow ng mga de-kalidad na kumpanya at ang maagang paglago ng mga makabagong proyekto sa teknolohiya.

---

## Kabanata 1: Ang katotohanang nakikita natin

### 1.1 Hindi balanseng pamamahagi ng pandaigdigang kayamanan

Ayon sa World Inequality Report 2026 (mula rito ay tinutukoy bilang "Ulat") ng World Inequality Lab:

| Data | Pinagmulan |
|------|------|
| Ang yaman na pag-aari ng pinakamayamang 0.001% ng populasyon sa mundo (mga 60,000 katao) ay humigit-kumulang tatlong beses sa pinagsamang yaman ng pinakamababang 50% ng populasyon (mga 4 bilyong tao) | World Inequality Lab, 2026 |
| Ang nangungunang 1% ng populasyon sa mundo ay kumokontrol sa 23% ng kabuuang kita at 38% ng kabuuang kayamanan | World Inequality Lab, 2026 |
| Kinokontrol ng nangungunang 10% ng populasyon sa mundo ang 53% ng kabuuang kita at 75% ng kabuuang kayamanan | World Inequality Lab, 2026 |
| Ang pinakamababang 50% ng pandaigdigang populasyon ay tumatanggap lamang ng 8% ng kabuuang kita at 2% ng kabuuang yaman | World Inequality Lab, 2026 |

Itinuturo ng "Ulat": "Nananatili ang pandaigdigang hindi pagkakapantay-pantay sa makasaysayang matinding antas.

**Source Note:** Ang data sa itaas ay sinipi mula sa World Inequality Report 2026 ng World Inequality Lab. Ang ulat ay pinangunahan nina Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif at Thomas Piketty (kinumpirma ng opisyal na website ng wid.world). Bago ang opisyal na pagpapalabas, inirerekomenda na higit pang markahan ang mga partikular na numero ng tsart sa ulat upang mabawasan ang mga posibleng error sa pangalawang pagsasalin.

**Pagsusuri ng pagkakapare-pareho ng data:** Ang mga proporsyon sa itaas ay nagpapatuloy sa isang makatwirang trend sa pagtatapos ng 2022 World Inequality Report (ang nangungunang 10% ay nagmamay-ari ng 76% ng kabuuang kayamanan, ang pinakamababang 50% ay nagmamay-ari ng 2% ng kabuuang kayamanan), at ang paglihis ay nasa loob ng saklaw na tinatanggap ayon sa istatistika.

### 1.2 Ang mga ordinaryong tao ay hindi kasama sa mga asset na may mataas na kalidad

Ang mga pangunahing pandaigdigang hurisdiksyon ay may mahigpit na kwalipikadong mga limitasyon ng mamumuhunan para sa pribadong equity at venture capital:

**United States (SEC Regulation D, Rule 501, 17 CFR §230.501):** Ang mga kwalipikadong mamumuhunan (Accredited Investors) ay dapat matugunan ang isa sa mga sumusunod na kundisyon - ang taunang kita ng isang indibidwal ay hindi bababa sa US$200,000 (o kabuuang hindi bababa sa US$300,000) at may katumbas na pamantayan; o ang netong halaga (hindi kasama ang pangunahing paninirahan) ay hindi bababa sa US$1,000,000.

**EU (MiFID II, 2014/65/EU, Annex II):** Dapat matugunan ng mga propesyonal na mamumuhunan (Mga Propesyonal na Mamumuhunan) ang hindi bababa sa dalawa sa mga sumusunod na kundisyon - isang portfolio ng pamumuhunan ng instrumento sa pananalapi na hindi bababa sa 500,000 euro; humahawak ng isang propesyonal na posisyon sa industriya ng pananalapi nang hindi bababa sa isang taon; pagsasagawa ng malalaking transaksyon na hindi bababa sa 10 kada quarter.

**Global Private Equity Fund Practice:** Ang minimum na halaga ng subscription para sa isang pondo ay karaniwang nasa pagitan ng US$250,000 at US$1,000,000; sa pangkalahatan, ipinagbabawal ng mga regulasyong tuntunin ang mga umiiwas na gawi gaya ng "paghahati ng mga bahagi, pagbaba ng mga limitasyon, at paghawak ng mga order sa ngalan ng iba."

| Mga uri ng asset | Maaari bang lumahok ang mga ordinaryong tao | Pangunahing dahilan |
|----------|----------------|----------|
| Equity sa hindi nakalistang mataas na kalidad na mga kumpanya | Karaniwang hindi maaaring | Ang threshold para sa mga kwalipikadong mamumuhunan ay mas mataas, halimbawa, ang Estados Unidos ay nangangailangan ng netong halaga na hindi bababa sa US$1 milyon o taunang kita na hindi bababa sa US$200,000 |
| Venture capital (mga kumpanya ng teknolohiya sa maagang yugto) | Karaniwan hindi | Pangunahing bukas sa mga kwalipikadong mamumuhunan, ang halaga ng pamumuhunan ng isang pondo ay karaniwang hindi bababa sa US$250,000 |
| Mga nakalistang stock ng kumpanya | Oo, ngunit ang mga maagang kita ay karaniwang nakukuha ng mga pangunahing kalahok sa merkado | Ang pangalawang pagpepresyo sa merkado ay kadalasang kinabibilangan ng mga inaasahan sa hinaharap, at ang mga mamumuhunan ay hindi direktang nakikilahok sa maagang pamamahagi ng tubo ng kumpanya |

### 1.3 Tatlong pangunahing depekto sa larangan ng cryptocurrency

**Kapintasan 1: Napakataas na rate ng pagkabigo**

Ayon sa 2025 taunang istatistika ng ulat ng CoinGecko, humigit-kumulang **11.56 milyong token** ang babalik sa zero o titigil sa pangangalakal sa 2025 lamang (kabilang ang mga long-tail na token sa bawat chain). Sa higit sa 20 milyong mga token na nasubaybayan ng CoinGecko sa kasaysayan, ang karamihan ay nasa "patay" na estado (walang dami ng kalakalan, walang aktibidad sa pag-unlad, at ang mga presyo ay bumagsak ng higit sa 99% mula sa mga makasaysayang mataas).

Kasabay nito, ang rate ng pagkabigo ng mga tradisyonal na stock market ay mas mababa kaysa sa mga cryptocurrencies. Ayon sa papel ni Bessembinder (2018) na "Do Stocks Outperform Treasury Bills?" na inilathala sa "Journal of Financial Economics", isang pag-aaral ng lahat ng stock ng U.S. mula 1926 hanggang 2016:

| Mga sukatan | Data | Mga Pinagmulan |
|------|------|------|
| Proporsyon ng mga stock na lumilikha ng kabuuang netong yaman | Mga 4% lamang (1,092 stock) | Bessembinder (2018), JFE 129(3):440-475 |
| Median stock lifetime return | Negatibo (hindi gumaganap ang mga kuwenta ng Treasury) | Bessembinder (2018), JFE |
| Humigit-kumulang 58% ng panghabambuhay na pagganap ng mga stock ng U.S. | Hindi gumagana ang mga kuwenta ng Treasury sa parehong panahon | Bessembinder (2018), JFE |
| Bilang ng mga token na ire-reset sa zero/stop trading sa 2025 | ≈11.56 milyon | CoinGecko 2025 Taunang Ulat |

**Paghahambing na Konklusyon:** Ang rate ng permanenteng pagkawala ng kapital sa espasyo ng cryptocurrency ay mas mataas kaysa sa tradisyonal na stock market. Bagama't humigit-kumulang 58% ng mga indibidwal na stock sa U.S. stock market ang hindi gumaganap ng Treasury bonds, ang mga mamumuhunan ay maaari pa ring makakuha ng average na market return sa pamamagitan ng index funds; sa merkado ng cryptocurrency, ang karamihan sa mga token ay bumabalik sa zero, at may kakulangan ng mga epektibong tool sa diversification na katulad ng "mga index."

**Pinagmulan na pahayag:** Bessembinder, H. (2018). "Nahihigit ba ng Stocks ang Treasury Bills?" *Journal of Financial Economics*, 129(3), 440-475. Unibersidad ng Estado ng Arizona. Ang papel na ito ay isang mataas na binanggit na dokumento sa larangan ng pananalapi (mga pagsipi >2,000), at ang data ay sumasaklaw sa lahat ng mga stock ng US sa database ng CRSP mula 1926 hanggang 2016. Ang data ng CoinGecko ay nagmula sa kanyang 2025 Token Survival Status Statistical Report (inilabas noong Enero 2026), na iniulat ng maraming media sa pananalapi ng RBC, RBC).

**Kapintasan 2: Ang pagmimina ay lubos na sentralisado**

Ang pagmimina ng Bitcoin ay nagpakita ng mataas na antas ng konsentrasyon:

| pool ng pagmimina | ratio ng hash rate |
|------|---------|
| Foundry USA | Mga 30% |
| AntPool | Mga 19% |
| Sa pamamagitan ngBTC | Mga 14.5% |
| F2Pool | Mga 10% |
| Pool ng MARA | Mga 5% |
| Nangungunang dalawang mining pool pinagsama | Higit sa 50% |
| Nangungunang apat na mining pool na pinagsama | Mga 75% |

**Source Note:** Ang data sa itaas ay pinagsama-sama mula sa buwanang ulat ng pamamahagi ng hashrate noong 2025 (CoinGradient 2025.3 "Foundry, Antpool, at Viabtc Dominate Bitcoin Mining"; HashrateIndex "Nangungunang 10 Bitcoin Mining Pool ng 2025"). Ang mga partikular na halaga mula sa iba't ibang pinagmumulan ng data ay maaaring bahagyang mag-iba (karaniwan ay nasa loob ng ±2%), ngunit ang konklusyon na "ang nangungunang apat na pool ng pagmimina ay kumokontrol sa humigit-kumulang 75% ng kapangyarihan sa pag-compute" ay makikita sa maraming mainstream na mga platform ng pagsubaybay.

**Kapintasan 3: Ang rate ng pakikilahok sa pamamahala ng DAO ay napakababa**

| Data | Pinagmulan |
|------|------|
| Ang rate ng paglahok sa pagboto ng karamihan sa mga DAO ay halos 3%-12% lamang (ang median ay humigit-kumulang 6%) | DeepDAO (2025) On-chain na pagsasama-sama ng data ng pamamahala; Boardroom DAO Governance Report (2024) |
| Ang isang maliit na bilang ng mga may hawak ng pera ay kumokontrol sa karamihan ng mga karapatan sa pagboto (mataas na konsentrasyon ng kapangyarihan sa pamamahala) | ACM (2024) "Pamamahala ng DAO: Kapangyarihan sa Pagboto, Pakikilahok, at Kontrobersya" DOI:10.1145/3777416 |

### 1.4 Mga Pangunahing Insight

Mayroon akong paghatol, ngunit walang tiket sa pagpasok; Mayroon akong pangitain, ngunit walang karapatang magsalita; Gusto kong lumahok, ngunit naharang ako ng matataas na threshold.

---

## Kabanata 2: Sagot ni LightDAO

### 2.1 Core positioning

Ang LightDAO ay isang pambansang organisasyong autonomous sa pamumuhunan na may on-chain na pamamahala bilang core at pagsunod sa SPV bilang carrier ng pagpapatupad ng pamumuhunan. Sa pamamagitan ng pampublikong chain na partikular na idinisenyo para sa magaan na mga web node, ang mga global na user ay maaaring lumahok sa pagpapanatili ng network, pagboto sa pamamahala, at magbahagi ng mga benepisyo sa ekolohiya ayon sa mga panuntunan sa isang browser lamang.

### 2.2 Dual engine model

| Makina | Direksyon sa Pamumuhunan | Target | Mga Katangian ng Kita |
|------|---------|------|---------|
| Engine One: Cash Flow Engine (Shou) | Mga asset ng serbisyo ng mahigpit na pagkonsumo sa antas ng komunidad | Bumuo ng tuluy-tuloy na daloy ng pera at ipamahagi ang mga kita ayon sa mga patakaran | Ituloy ang relatibong katatagan, ngunit huwag mangako ng fixed income |
| Engine 2: Growth engine (pag-atake) | Mga kumpanya ng makabagong teknolohiya | Makakuha ng equity appreciation at exit returns | Mataas na potensyal na kakayahang umangkop, ngunit maaari ring harapin ang mga pagkalugi o pagkabigo sa paglabas |

**Disiplina sa paglalaan:** Sa prinsipyo, maglaan ng 70% ng mga pondo sa mga asset na may matatag na daloy ng salapi at 30% sa mga target na mataas ang paglago.

**Path ng paglago ng scale ng pamumuhunan:** Ang laki ng isang pamumuhunan ay dynamic na lumalaki sa presyo ng LIGHT at kapasidad ng vault - ang panahon ng pagsisimula (LIGHT $0.02-$0.05) ay angkop para sa maliliit na asset sa antas ng komunidad na $2.55 milyon-$6.37 milyon; ang yugto ng paglago ($0.05-$0.30) ay pumapasok sa mga panrehiyong chain at Seed-A round na $6.37 milyon-$38.25 milyon (benchmarking Lower Middle Market) PE); sa mature stage ($0.30-$1.00), umabot ito sa mid-market PE level na $38.25 milyon hanggang $127.5 milyon; sa scale stage ($1.00+), maaari itong magsagawa ng malalaking acquisition at Pre-IPO investment na higit sa $127.5 milyon. Mga paghihigpit: ang isang transaksyon ay hindi lalampas sa 15% ng natitirang halaga ng treasury ng pamumuhunan (tingnan ang Kabanata 9 para sa mga detalye).

**Ang unang prinsipyo sa pagpoposisyon ng target:** Sa halip na magpalagay ng isang partikular na pangalan ng kumpanya, magtatag muna ng isang screening framework - bigyang-priyoridad ang antas ng komunidad na mahigpit na mga asset ng serbisyo ng consumer, na nangangailangan ng isang napatunayang modelong pang-ekonomiya ng solong tindahan, matatag na mga talaan ng daloy ng pera (Ang margin ng EBITDA sa nakalipas na tatlong taon ay hindi bababa sa 10%, at hindi mas mataas sa 15%) ang pagbabago sa rehiyon. Ang partikular na target ay tinutukoy ng mga mungkahi ng komunidad.

### 2.3 Core value proposition

**Ang browser ay ang node** - Hindi na kailangang bumili ng mining machine o magkaroon ng propesyonal na teknikal na background. Maaari kang lumahok sa mga kontribusyon sa network sa pamamagitan ng pagbisita sa opisyal na web platform.

**Maaaring lumahok ang lahat** - Matapos maabot ang threshold ng pamamahala, ang mga may hawak ng maliit na halaga ng LIGHT ay maaari ding lumahok sa pagboto upang magkasamang magpasya sa direksyon ng paglalaan ng pondo.

**Pagbabahagi ng kita ayon sa mga panuntunan** - Ang mga kita sa pagpapatakbo ng mga namuhunang kumpanya at ang mga exit return ng mga proyektong teknolohiya ay ibabahagi alinsunod sa mga on-chain na panuntunan at mga pagsasaayos ng SPV.

### 2.4 Slogan

"Ang iyong browser ay maaari ding maging gateway sa mga asset na may mataas na kalidad."

### 2.5 Mapagkumpitensyang pagsusuri sa pagkakaiba-iba ng produkto

| Dimensyon | Pi Network | Helium | Tradisyunal na DAO (MakerDAO, atbp.) | LightDAO |
|------|-----------|--------|----------------------|---------|
| Paraan ng paglahok | Mag-click sa mobile APP | Bumili ng hardware hotspot ($200-$1000) | Bumili ng token + on-chain na operasyon | Pag-access sa browser, walang gastos sa hardware |
| Gastos sa pagpasok | Zero (ngunit walang praktikal na utility) | Mataas (hardware + pag-install) | Katamtaman hanggang mataas (kailangang bumili ng mga token ng pamamahala) | Zero (isang browser lang) |
| Kabuuang halaga ng mga token | 100 bilyon | 223 milyon | Nag-iiba | 2.5 bilyon |
| Aktwal na pamumuhunan function | Wala | Wala (tanging saklaw ng network) | Oo (ngunit ang threshold ay napakataas) | Oo (istraktura ng SPV, lahat ay maaaring lumahok) |
| Pinagmumulan ng kita | Hindi malinaw | Bayad sa paggamit ng network | Bayad sa kasunduan | Kita ng kumpanya + pagbabalik sa labas + Bayad sa gas |
| Legal na paghihiwalay | Wala | Wala | Ang ilang oo | Cayman SPV+ZK-KYC |
| Rate ng partisipasyon sa pamamahala | Napakababa (walang malaking pamamahala) | Mababa | Mga 6% | Target >15% (dual-dimensional na pagboto + mga insentibo) |

**Ang pangunahing pagkakaiba ng LightDAO:** Ito ang kasalukuyang nag-iisang proyekto na pinagsasama ang "zero-threshold web mining" sa "sumusunod na pamumuhunan sa entity ng SPV." Ang mga gumagamit ay hindi lamang nag-aambag ng mga mapagkukunan ng network upang makakuha ng mga gantimpala ng token, ngunit direktang lumahok din sa mga tunay na desisyon sa pamumuhunan ng negosyo sa pamamagitan ng pagboto sa pamamahala at pagbabahagi ng mga kita sa pagpapatakbo.

> **[Terminolohiya sa kabanatang ito]**
> **DAO** (Decentralized Autonomous Organization): Isang organisasyonal na anyo kung saan ang mga panuntunan sa pamamahala ay naka-encode sa pamamagitan ng mga matalinong kontrata at ang mga kolektibong desisyon ay ginagawa ng mga may hawak ng token. Walang tradisyonal na hierarchy ng kumpanya.
> **SPV** (Special Purpose Vehicle): isang independiyenteng legal na entity (karaniwang nakarehistro sa Cayman Islands) na itinatag para sa mga partikular na transaksyon o pamumuhunan upang makamit ang paghihiwalay sa panganib - ang mga utang at legal na pananagutan ng SPV ay hindi ipinadala sa mismong DAO.
> **DePIN** (Decentralized Physical Infrastructure Network, decentralized physical infrastructure network): Isang modelo ng network na gumagamit ng mga token para hikayatin ang mga user na mag-ambag ng mga pisikal na mapagkukunan (bandwidth, storage, computing power, wireless coverage, atbp.) para bumuo ng imprastraktura.
> **Lower Middle Market PE** (downstream mid-end private equity): isang market segment ng pandaigdigang pribadong equity na industriya. Ang laki ng isang transaksyon ay karaniwang $10 milyon hanggang $100 milyon, at ang EBITDA ng target na kumpanya ay nasa pagitan ng $2 milyon at $15 milyon.

---

## Kabanata 3: Pagsunod at legal na paghihiwalay

### 3.1 SPV legal na layer ng paghihiwalay

Ang DAO ay hindi direktang humahawak ng equity sa anumang pisikal na negosyo. Ang lahat ng panlabas na pamumuhunan ay isinasagawa sa pamamagitan ng mga espesyal na layunin ng sasakyan (SPV) na itinatag sa Cayman Islands.

| Mga Punto ng Disenyo | Paglalarawan |
|---------|------|
| SPV Charter | Malinaw na sinang-ayunan na ang pagpapatakbo ng SPV ay dapat sumunod sa epektibong resolusyon ng DAO |
| Legal na kahulugan ng mga sub-token | Ang mga sub-token ay "SPV income distribution claim rights certificates", na kumakatawan lamang sa mga kwalipikasyon sa pamamahagi para sa cash flow sa hinaharap |
| Hindi nagdadala ng mga karapatan ng shareholder | Hindi nagdadala ng mga karapatan sa pamamahala ng korporasyon, mga kagustuhan sa pagpuksa o anumang mga karapatan ng shareholder |
| Mga direktor ng SPV | ay pinaglilingkuran ng mga independiyenteng ikatlong partido; Maaaring palitan ng DAO ang mga direktor sa pamamagitan ng pagpasa ng wastong resolusyon |
| Pangangasiwa ng pondo | Ang mga bank account ay pinangangasiwaan ng mga lisensyadong institusyon ng kustodiya, at ang mga paglilipat ng pondo ay dapat pumasa sa multi-signature at pag-verify ng pagsunod |
| Paglutas ng hindi pagkakaunawaan ng SPV | Ang SPV charter ay nagtatakda ng arbitration clause (SIAC o ICC), at ang DAO ay maaaring magpasimula ng mga paglilitis sa arbitrasyon sa pamamagitan ng isang governance resolution |

### 3.2 Opsyonal na pag-verify at proteksyon sa privacy

**Walang pagkakakilanlan ang kinakailangan upang lumahok sa protocol mismo. ** Bisitahin ang mga web page, lumikha ng mga wallet, mag-ambag ng mga mapagkukunan, tumanggap ng LIGHT, magsimula at lumahok sa pagboto sa pamamahala - hindi na kailangang mag-upload ng mga dokumento sa buong proseso, at walang personal na pagkakakilanlan na impormasyon (PII) ang nakaimbak sa chain.

Kapag ang isang user ay aktibong gumagamit ng isang kinokontrol na serbisyo ng third-party, ang pagpapatunay na ang serbisyo mismo ay dapat gumanap alinsunod sa batas. Ang pagpapatunay na ito ay kinokolekta, isinagawa at iniingatan ng partido ng serbisyo. Ang LightDAO ay hindi nangongolekta, naglilipat o nag-iimbak ng anumang data:

| Sitwasyon | Sino ang nagsasagawa ng pag-verify | Ano ang kailangang gawin ng user |
|---|---|---|
| Pagbili/pagbebenta sa pamamagitan ng mga fiat channel | Mga lisensyadong third party (gaya ng MoonPay, Ramp Network, Transak) | Kumpletuhin ang proseso ng pagsunod ayon sa sariling mga kinakailangan ng service provider |
| Exchange sub-token (mga investment share certificate) | Depende sa mga kinakailangan ng partikular na produkto at service provider nito | Maaari mo lamang gawin ang pagmimina at pamamahala, nang walang anumang pagpapatunay |
| Mag-withdraw sa bank card/lokal na pagbabayad | Tagabigay ng serbisyo sa pag-withdraw at pagbabayad | Kumpletuhin ang proseso ng pagsunod ayon sa kinakailangan ng service provider |

Mga pangunahing prinsipyo: **Zero verification bilang default; Ang pag-verify ay nangyayari lamang sa sandaling ang gumagamit ay aktibong pumasok sa kinokontrol na serbisyo, at pinapasan ng service provider. **Walang mawawalan ng karapatan na magmina, mag-hold, maglipat o bumoto dahil sa "failure to verify".

> Nakareserba ang teknolohiya: Kung ang isang partikular na uri ng asset ay nangangailangan ng threshold ng kwalipikasyon sa hinaharap, hahawakan ng user ang certificate sa anyo ng zero-knowledge proof (ZK), at ive-verify lang ng chain "kung ito ay natugunan" nang walang anumang impormasyon sa pagkakakilanlan - bahagi ito ng roadmap at hindi isang kasalukuyang kinakailangan.

### 3.3 Pahayag ng Responsibilidad sa Buwis

Ang kasunduan ay hindi nagbibigay ng mga serbisyo sa pagdedeklara ng buwis, at ang mga obligasyon sa buwis ng lahat ng ekolohikal na gantimpala at kaugnay na kita ay pananagutan ng mga gumagamit mismo. Ang mga gumagamit ay dapat sumunod sa mga nauugnay na batas at regulasyon ng kanilang lokasyon ng paninirahan sa buwis.

### 3.4 Access ng user: bukas sa lahat

**Walang threshold para sa pagpaparehistro at paglahok**: Walang kinakailangang email, numero ng mobile phone, social account o patunay ng pagkakakilanlan; isang device na makakapagbukas ng web page ang kailangan mo. Hindi aktibong pinaghihigpitan ng LightDAO ** ang paglahok ng user sa anumang bansa o rehiyon, at hindi rin ito nagde-deploy ng geofencing. **

Ang tanging panlabas na mga hadlang ay nagmumula sa mga serbisyo ng third-party: kung ang batas ng isang partikular na lugar ay may iba pang mga kinakailangan para sa mga partikular na serbisyo (tulad ng mga deposito at pag-withdraw ng fiat currency), ang mga serbisyong iyon ay isasagawa ng mga lokal na lisensyadong institusyon alinsunod sa batas sa kanilang panig at hindi makakaapekto sa paggamit ng sinuman sa mga on-chain function (pagmimina, paghawak, paglilipat, pagboto, mga panukala).

Kung ang isang partikular na hurisdiksyon ay maglalabas ng mga tahasang nagbabawal na regulasyon sa hinaharap, ang pagkakasunud-sunod ng pagtugon ng protocol ay:

1. Una, tiyaking hindi maaapektuhan ang mga karapatan sa pagtatapon ng asset ng mga umiiral nang user - hindi mapi-freeze ang mga asset sa chain, at maaaring ilipat ng sinuman ang kanilang LIGHT at sub-token anumang oras;
2. Manatiling naa-access sa pamamagitan ng maraming front-end na portal (kabilang ang mga salamin ng IPFS at mga salamin ng komunidad);
3. Ang huling hakbang ay ang isaayos ang magagamit na saklaw ng **mga serbisyo ng third-party** sa loob ng saklaw ng legal na pagpapatupad.

Sa isang salita: *** ang mga paghihigpit ay maaari lamang mahulog sa mga serbisyo, hindi sa mga tao. **

### 3.5 Legal na mga deposito at pag-withdraw ng pera at mga cross-chain na channel

**Fiat currency channel (third-party service aggregation):** Ang protocol mismo ay hindi nagpapatakbo ng legal na currency deposit at withdrawal services, ngunit ang web platform ay nagsasama ng mga sumusunod na third-party na channel (MoonPay, Ramp Network, Transak, atbp.), na sumasaklaw sa mga pangunahing merkado sa North America, Europe, Southeast Asia, at Latin America; ang lokal na P2P market aggregation ay sumasaklaw sa Africa at South Asia; Sinusuportahan ng mga withdrawal ang mga lokal na paraan ng pagbabayad gaya ng GCash, M-Pesa, Pix, at GrabPay.

**Cross-chain bridge at LIGHT acquisition channel:** Built-in na mga transaksyon sa AMM sa LightDAO chain pagkatapos ng TGE; interoperability sa Cosmos ecosystem sa pamamagitan ng IBC; pagpaplano para sa wLIGHT (Ethereum/Solana) mula sa ika-6 na buwan; aplikasyon para sa listahan ng CEX mula sa ika-6 na buwan depende sa pagsunod. Ang cross-chain bridge ay pinatatakbo ng isang independiyenteng third party, at isang independiyenteng ulat sa pag-audit ay kinakailangan bago mag-online ang tulay.

### 3.6 Pahayag ng Pagsunod sa Mekanismo ng Imbitasyon (Anti-MLM Analysis)

Ang insentibo sa imbitasyon ng LightDAO ay **single-layer sharing** (tanging mga direktang nag-imbita lamang ang makakatanggap ng nakapirming proporsyon ng mga reward sa pagmimina ng inimbitahan), at walang mga pangunahing tampok ng multi-level marketing (MLM): walang multi-level na recursive na komisyon; ang kita ay nagmumula sa paglabas ng mga preset na token sa protocol sa halip na sa punong-guro ng bagong dating; walang gastos at walang entry fee para lumahok sa pagmimina. Ang istrukturang ito ay mas malapit sa "mga gantimpala sa rekomendasyon ng tagapag-ambag ng open source." Bago ang pormal na operasyon, isang lisensyadong abogado sa target na merkado ang kukuha para mag-isyu ng mga espesyal na opinyon sa pagsunod.

> **[Terminolohiya sa kabanatang ito]**
> **KYC** (Know Your Customer, Know Your Customer): Isang proseso ng pagsunod para sa mga institusyong pinansyal upang i-verify ang pagkakakilanlan ng user, kadalasang nangangailangan ng pagsusumite ng mga dokumento ng pagkakakilanlan, patunay ng address, atbp.
> **ZK-KYC** (Zero-Knowledge KYC, zero-knowledge proof KYC): Hindi kailangang ibunyag ng mga user ang partikular na personal na impormasyon sa kasunduan, at gagamit lang sila ng cryptography para patunayan na "Natutugunan ko ang ilang partikular na kundisyon" (gaya ng edad ≥ 18 taong gulang, hindi sinasang-ayunan na nasyonalidad) paraan ng pag-verify ng pagsunod. Walang orihinal na data ng dokumento ang nakaimbak sa chain.
> **PII** (Personal Identifiable Information, Personally Identifiable Information): Data na maaaring tumukoy sa isang partikular na natural na tao nang paisa-isa o pinagsama, gaya ng pangalan, ID number, address, biometric na katangian, atbp.
> **Reg D / Reg S** (Regulation D/Regulation S ng U.S. Securities Act): Pinapayagan ng Reg D ang mga pribadong placement sa "mga kwalipikadong mamumuhunan" sa United States nang walang pampublikong pagpaparehistro (Rule 501 definition standard); Pinapayagan ng Reg S ang pagbebenta ng mga securities sa mga tao sa labas ng United States nang hindi nagti-trigger ng mga kinakailangan sa pagpaparehistro sa U.S.
> **MiFID II** (EU Markets in Financial Instruments Directive II, 2014/65/EU): EU financial regulatory framework, ang Annex II nito ay tumutukoy sa identification criteria para sa "professional investors" (€500K financial instrument portfolio, 1 taon ng karanasan sa industriya ng pananalapi, 10 malakihang transaksyon kada quarter, na nakakatugon sa pangalawang kinakailangan).
> **MLM** (Multi-Level Marketing, multi-level marketing): isang modelo ng negosyo sa pamamagitan ng multi-level recursive commissions (downline development, downline development, at upline commissions layer by layer). Talagang naiiba ito sa mga reward sa rekomendasyon sa isang layer - Ang LightDAO ay isang solong layer lamang (Iniimbitahan ni A si B, nakakakuha si A ng bahagi mula sa B; Iniimbitahan ni B si C, hindi nakakakuha ng anumang bahagi si A mula sa C).
> **IBC** (Inter-Blockchain Communication, cross-chain communication protocol): ang katutubong cross-chain na pamantayan ng Cosmos ecosystem, na nagpapahintulot sa ligtas na paglipat ng mga asset at mensahe sa pagitan ng iba't ibang blockchain nang hindi nangangailangan ng sentralisadong tagapamagitan.

---

## Kabanata 4: Teknikal na Arkitektura

### 4.1 Ano ang pampublikong chain?

Ang pampublikong chain ng LightDAO ay mauunawaan bilang isang "public account book na may malinaw na mga panuntunan at hindi maaaring pakialaman sa kalooban": ang mga panuntunan sa pamamahala ay nakasulat sa code, at ang mga talaan ng pagboto, daloy ng kapital at pamamahagi ng tubo ng sinuman ay maaaring itanong at i-verify sa chain.

### 4.2 Mga teknikal na parameter at pagpapakita ng pagpili

| Mga teknikal na item | Pinili | Batayan sa pagpili |
|--------|------|---------|
| Pinagbabatayan na balangkas | Cosmos SDK | Modular architecture, maramihang produksyon chain verification |
| Mekanismo ng pinagkasunduan | Tendermint PoS | Agad na katiyakan; ang pagbuo ng block ay tumatagal ng 1.5-2 segundo; BFT fault tolerance ≤ 1/3 kasamaan |
| Mga Matalinong Kontrata | CosmWasm | WebAssembly + Rust, compile-time memory safety |
| Mga kakayahan sa cross-chain | IBC protocol | Cosmos native cross-chain standard |
| Front-end na pakikipag-ugnayan | Progressive Web App (PWA) | Tumatakbo ang browser, desktop/mobile adaptive, walang kinakailangang pag-install |

### 4.3 Magaan na mekanismo ng pagmimina ng node at modelo ng insentibo

#### 4.3.1 Paraan ng pagmimina

Ina-access ng mga user ang opisyal na web platform sa pamamagitan ng browser, gumawa ng wallet, at i-click ang "Start Mining". Sa panahon ng proseso ng pagmimina, ang mga gumagamit ay nag-aambag ng bandwidth ng network (relay ng data at pag-verify) at mga mapagkukunan ng lokal na pag-compute (magaan ang pag-verify ng block header) sa pamamagitan ng browser, at hindi umaasa sa mataas na enerhiya na kapangyarihan sa pag-compute.

**Pagpapatupad ng teknolohiya sa gilid ng web:** P2P relay ng data channel ng WebRTC; Pag-verify ng header ng block sa background ng Web Worker; Service Worker offline cache at tibok ng puso; WebSocket mahabang koneksyon.

**Pagbagay sa mobile browser:** Mag-ampon ng pinagsama-samang wastong sistema ng session (4 na oras sa isang araw = 100% na marka); walang mga puntos na ibabawas para sa muling pagkonekta sa loob ng 5 minuto ng pagdiskonekta; Ang mga naka-install na user ng PWA ay makakatanggap ng karagdagang 10% online time bonus; delegadong online na mekanismo (70% para sa delegado/30% para sa relay node).

#### 4.3.2—4.3.3 Incentive scheme at three-engine na modelo

Pinagtibay nito ang three-engine na modelo ng "PoC contribution proof + invitation fission incentive + behavioral bonus incentive."

#### 4.3.4 Mga sukat at timbang ng kontribusyon

| Dimensyon ng kontribusyon | Timbang | Paraan ng pagsukat |
|---------|------|---------|
| Ambag ng bandwidth relay | 40% | Ratio ng upload relay traffic sa verification data volume |
| Mabisang tagal ng session | 30% | Pang-araw-araw na pinagsama-samang epektibong mga session (4 na oras = 100%) |
| I-block ang kontribusyon sa pag-verify | 20% | Bilang at katumpakan ng epektibong na-verify na mga header ng block |
| Katatagan ng network | 10% | Pagkaantala ng koneksyon, rate ng pagkawala ng packet, oras ng pagtugon |

#### 4.3.5 Formula sa pagkalkula ng gantimpala

**Pang-araw-araw na Gantimpala sa Pagmimina = BaseReward × Marka ng Timbang ng Kontribusyon × (1 + Bonus ng Imbitasyon) × (1 + Bonus sa Pag-uugali)**

- BaseReward = Kabuuang halaga na inilabas ng buong network sa araw ÷ Kabuuang bilang ng mga aktibong minero sa araw
- Bonus ng imbitasyon = epektibong bilang ng mga inimbitahan × 1% (itaas na limitasyon 20%)
- Bonus sa pag-uugali = 5% paglahok sa pagboto + 5% kontribusyon sa nilalaman + 5% aktibidad ng komunidad + 5% kalidad ng pag-verify ng node (itaas na limitasyon 20%)
- Buong bonus coefficient = (1+20%) × (1+20%) = 1.44 beses

#### 4.3.6 Mag-imbita ng mga insentibo sa fission

| Antas | Wastong bilang ng mga imbitasyon | Ratio ng pagbabahagi ng imbitasyon | Karagdagang isang beses na reward | Bonus sa timbang ng pamamahala |
|------|------------|------------|--------------|------------|
| Mga Minero | 0 tao | — | Mga pangunahing reward sa pagmimina | Wala |
| Mangangaral | Hindi bababa sa 3 tao | 10% | 100 ILAW | Wala |
| Ambassador | Hindi bababa sa 10 tao | 15% | 500 LIGHT + on-chain na badge | Timbang ng pagboto +5% |
| Mga kasosyo | Hindi bababa sa 50 tao | 20% | 2,500 LIGHT + on-chain na badge | Timbang ng pagboto +10% |

Ang bonus sa timbang ng pamamahala at bonus ng reputasyon (hanggang sa +30%) ay independyenteng nakasalansan, na may kabuuang pinakamataas na limitasyon na +40%. Ang bonus ng imbitasyon ay umabot sa pinakamataas nito kapag mayroong 20 tao (20×1%=20%).

#### 4.3.7 Anti-cheating na mekanismo

Pag-detect ng integridad ng kapaligiran ng browser (Canvas/WebGL/WebRTC fingerprint), packet depth detection, IP clustering at behavior pattern analysis, multi-dimensional behavioral fingerprint (mouse trajectory/keyboard rhythm/scrolling behavior), invitation address authenticity verification. Gastos sa pag-atake ng Anti-Sybil: $50,000-$200,000 para gumawa ng 10,000 independiyenteng fingerprint; target na rate ng pagtuklas >90-95%.

### 4.4 LIGHT Token Function Matrix

Network fuel (Gas fee), mga karapatan sa pamamahala (pagboto/proposal/campaign), pledge binding (margin/campaign/verifier), investment exchange (sub-tokens), ecological incentives (mining/invitation/behavior), future expansion (dApp/NFT/cross-chain).

### 4.5 Bayad sa gas at mekanismo ng bayad sa transaksyon

**Prinsipyo ng Disenyo:** Ang bayad sa gas ay nakaangkla sa katumbas ng USD, at ang aktwal na halaga ng LIGHT na sinisingil ay awtomatikong kino-convert bawat 24 na oras ng on-chain na oracle (Seksyon 4.10). Tinitiyak nito na tumaas man o bumaba ang presyo ng LIGHT, ang aktwal na halaga ng pagbabayad ng user (sa US dollars) ay nananatiling stable, na iniiwasan ang problema ng "ang presyo ng currency ay tumaas ng 100 beses → ang transfer fee ay nagiging $10" o "ang presyo ng currency ay bumaba ng 90% → zero-cost ticket redemption".

**Target ng bayad sa gas na naka-angkla sa USD:**

| Uri ng transaksyon | Katumbas na target ng USD | Tunay na koleksyon kapag LIGHT=$0.05 | Tunay na koleksyon kapag LIGHT=$0.50 | Intensiyon ng disenyo |
|----------|-----------|-----------------|------------------|----------|
| Ordinaryong paglipat | $0.001 | 0.02 ILAW | 0.002 ILAW | Napakababa ng threshold upang matiyak na ang maliit na halaga ng mga user ay malayang makapaglipat ng pera |
| Pagboto sa Pamamahala | $0.005 | 0.10 ILAW | 0.01 ILAW | Bahagyang mas mataas kaysa sa paglipat upang maiwasan ang walang gastos na pagsisipilyo ng boto |
| Magsumite ng panukala | $0.10 | 2.0 LIGHT | 0.2 ILAW | Makipagtulungan sa sistema ng deposito upang madagdagan ang kaseryosohan ng panukala |
| Pagpapalitan ng sub-token | $0.50 | 10.0 LIGHT | 1.0 ILAW | Mas mataas na mga bayarin, tumutugma sa kabigatan ng malalaking operasyon |
| Pag-uulat ng tibok ng puso sa pagmimina | $0 (libre) | 0 | 0 | Walang Gas na sinisingil para sa mga kontribusyon sa pagmimina, na tinitiyak ang zero-cost participation |

**Mga panuntunan sa dynamic na conversion:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Mga panuntunan sa paglalaan ng bayad sa gas:**

| Patutunguhan | Proporsyon | Function |
|------|------|------|
| Permanenteng pagkawasak | 50% | Patuloy na deflation, binabawasan ang suplay ng sirkulasyon |
| Mga gantimpala ng validator | 30% | Bigyan ng insentibo ang mga validator na mapanatili ang seguridad ng network at gumawa ng mga block |
| Ecological Treasury | 20% | Karagdagang pagpopondo ng developer at mga pondo sa pagpapatakbo ng komunidad |

**Pagtatantya ng deflation ng bayad sa gas:** Kung ipagpalagay na ang average na 100,000 araw-araw na aktibong transaksyon at isang average na bayad sa gas na $0.005 (pangunahin ang pagboto at paglilipat), katumbas ng USD na nawasak bawat araw = 100,000 × $0.005 × 50% = $250/araw. Kapag LIGHT=$0.05, ito ay katumbas ng 5,000 LIGHT/araw≈1.825 milyon/taon; kapag LIGHT=$0.50, ito ay katumbas ng 500 LIGHT/araw≈182,500/taon. Ang dami ng LIGHT na may gas fee deflation ay bumababa habang tumataas ang presyo (ang katumbas ng USD ay pare-pareho), ngunit ang suporta nito para sa presyo ay makikita ng "patuloy na pagbili ng katumbas" - bawat transaksyon ay sumisira ng mga token sa isang nakapirming USD rate.

### 4.6 Verifier system

| Mga sukat | Mga Validator | Mga light node (mga minero ng browser) |
|-------|--------|-------------------|
| Mga Pananagutan | Block generation, consensus, full node | I-block ang pag-verify ng header, relay ng data |
| Staking | Minimum na 500,000 LIGHT | Wala |
| Kita | Bayad sa gas 30% + araw-araw na release pool 5% | Mga reward sa PoC mining (pang-araw-araw na release pool 95%) |
| Dami | Inisyal 21, itaas na limitasyon 100 | Walang pinakamataas na limitasyon |
| Pag-slash | 5% na parusa para sa dobleng pagpirma + 180-araw na pagbabawal | Wala |

**Magsimula sa mga yugto (BFT fault tolerance: N≥3f+1):**

| Yugto | Bilang ng mga validator | Fault tolerance f | Kondisyon sa paghinto ng chain | Karanasan ng user |
|------|-----------|-------|-----------|----------|
| Testnet (3 buwan bago ang TGE) | 7 | 2 | 3 offline sa parehong oras | Maaaring tiisin ng panloob na pagsubok ang mga maikling pagkaantala |
| Mainnet TGE | Minimum 10, target 21 | 3-6 | 4-7 offline sa parehong oras | Paminsan-minsang mga pagkaantala (<1 oras bawat quarter) upang makinis |
| Bukas para sa halalan simula sa ika-7 buwan | 21-100 | 6-33 | 7-34 offline sa parehong oras | Hindi alam ng user |

**Hard bottom line: Ang TGE ay hindi isasagawa kapag mayroong <7 validators. ** Mas mababa sa 7 ay nangangahulugang f ≤ 1. Ang anumang pagkabigo sa isang punto ay magiging sanhi ng pagsara ng buong chain, na katumbas ng "hindi magagamit ang produkto" para sa mga hindi teknikal na gumagamit.

### 4.7 Layer ng imprastraktura ng network

Ang mga validator node ay nagdadala ng mga gateway ng access sa WebSocket sa isang distributed na paraan (bawat validator ay may pinakamataas na limitasyon na 50,000 na koneksyon); Ang P2P signaling ay ibinibigay ng validator + community relay node; Ang heartbeat Merkle aggregation ay nagsusumite lamang ng Root hash per block (O(1) on-chain overhead); ang front end ay ipinamamahagi sa pamamagitan ng IPFS+CDN.

P2P network: WebRTC ICE framework (STUN priority/TURN fallback); humigit-kumulang 70-80% ng mga user ang maaaring direktang kumonekta, 20-30% ng simetriko NAT user ang pumasa sa TURN relay; kapag nabigo ang P2P, ibinababa ito sa "pure authentication mode".

Mga detalye ng pagganap: Theoretical TPS 1,000-3,000; laki ng bloke 2MB (naaayos ang pamamahala); light node synchronization <30 segundo; milyong node heartbeat Merkle aggregation <500ms.

### 4.8 Contribution proof na mekanismo ng pagpapatunay

Three-tier verification architecture: (1) Verifier random cross-sampling challenge (5% node bawat 10 minuto, 30 segundong oras ng pagtugon); (2) P2P peer mutual verification (8-16 na peer ay nakapag-iisa na nagtatala ng dami ng palitan ng data, kunin ang median); (3) Merkle aggregation on-chain (bawat block ay nagsusumite ng marka ng kontribusyon na Root, ang mga user ay maaaring mag-self-check sa pamamagitan ng Merkle Proof). Pagkabigong hamunin nang 3 beses nang sunud-sunod → ang marka para sa araw ay ire-reset sa zero; kabuuang 5 beses sa loob ng 7 araw → ma-trigger ang isang anti-cheating review.

### 4.9 Pamamahala ng Wallet at Key

Tatlong antas na arkitektura: (1) Naka-embed na smart wallet (Passkey/WebAuthn, walang mnemonic na pariralang kinakailangan, target ang 80%+ na user); (2) Social recovery wallet (3-5 restorer, Shamir sharding, 2/3 majority confirmation); (3) Self-hosted wallet (BIP-39 mnemonic phrase + hardware wallet compatible). Ang gas fee para sa unang 100 transaksyon ng mga bagong user ay babayaran ng ecological fund (Paymaster model).

### 4.10 Presyo ng Oracle

Ang on-chain na TWAP (30-araw na average na timbang na presyo ng LIGHT/USDC pool) ang pangunahing pinagmumulan ng presyo; 3+ panlabas na pagsasama-sama ng DEX/CEX ay dinagdagan (nagsusumite ang mga validator sa pag-ikot, kunin ang median); deviations >±15% trigger exception flag; hindi kasama sa TWAP (anti-flash loan manipulation) ang mga single block deviations >5%; fallback sa purong on-chain na TWAP kapag nabigo ang lahat ng external na oracle.

### 4.11 Arkitektura ng Module ng Smart Contract

10 pangunahing kontrata: light_token, mining_reward, pamamahala, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, insurance_fund. Dapat kumpletuhin ng pangunahing kontrata ang pormal na pag-verify bago ang TGE.

### 4.12 Protocol Upgrade at Chain Governance

Level 4 upgrade: L1 parameter adjustment (governance voting 24-72h) → L2 contract migration (pangunahing panukala + audit + 72h delay) → L3 consensus change (66% pumasa + 2/3 validator signal + 7-araw na panahon ng proteksyon ng tinidor) → L4 emergency repair (shadow committee suspension + 72h hot fix rat).

> **[Terminolohiya sa kabanatang ito]**
> **Cosmos SDK**: Isang modular blockchain development framework na nagbibigay-daan sa mga developer na bumuo ng mga custom na pampublikong chain tulad ng mga building block. Ilang production chain (gaya ng Cosmos Hub at Osmosis) ang nag-verify ng maturity nito.
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Isang consensus mechanism kung saan ang mga validator ay nakakuha ng karapatang gumawa ng mga block sa pamamagitan ng pag-pledge ng mga token (sa halip na makipagkumpitensya para sa computing power). Nagbibigay ng "instant finality" - kapag ang isang block ay ginawa, hindi na ito maibabalik.
> **BFT** (Byzantine Fault Tolerance, Byzantine Fault Tolerance): Isang mekanismo sa isang distributed system na maaaring magparaya sa ilang node na gumagawa ng masama o hindi gumagana at nakakamit pa rin ng tama ang consensus. Maaaring tiisin ng Tendermint BFT ang hindi hihigit sa 1/3 ng mga validator na kumikilos ng masama o sabay na mag-offline.
> **CosmWasm**: Sinusuportahan ng smart contract engine ng Cosmos ecosystem, batay sa teknolohiya ng WebAssembly, ang paggamit ng Rust language para magsulat ng mga kontrata, at may mga feature na pangkaligtasan sa oras ng pagsasama-sama ng memorya (pinipigilan ang mga karaniwang kahinaan gaya ng mga buffer overflows).
> **PWA** (Progressive Web App, Progressive Web App): Isang teknolohiya sa web na tumatakbo sa isang browser ngunit may native-like na karanasan sa application. Sinusuportahan nito ang offline na pag-cache, mga push notification, at pagdaragdag sa home screen nang hindi nagda-download at nag-i-install sa pamamagitan ng app store.
> **WebRTC/WebSocket**: Dalawang real-time na teknolohiya ng komunikasyon sa browser. Ginagamit ang WebRTC para sa P2P data relay (direktang pagpapadala sa pagitan ng mga node); Ginagamit ang WebSocket upang mapanatili ang mahabang koneksyon sa pagitan ng kliyente at ng verifier (pintig ng puso, notification ng reward).
> **PoC** (Proof of Contribution): Ang mekanismo ng insentibo na pinagtibay ng LightDAO ay nagbibigay ng mga reward sa pamamagitan ng pag-verify sa mga mapagkukunan ng network (bandwidth relay, block verification, online na oras) na aktwal na iniambag ng mga user, sa halip na umasa sa computing power competition o capital pledge.
> **Merkle Tree** (Merkle Tree): Isang istraktura ng data ng hash tree na nagbibigay-daan sa mahusay na pag-verify ng integridad ng isang partikular na entry sa malaking halaga ng data. Ang puting papel na ito ay ginagamit upang pagsama-samahin ang milyun-milyong light node na heartbeats sa isang Root hash at i-upload ito sa chain (O(1) storage overhead).
> **Gas fee**: Ang bayad sa pangangasiwa na kinakailangan upang magsagawa ng mga transaksyon o mga pagpapatakbo ng kontrata sa blockchain, na ginagamit upang mabayaran ang verifier para sa mga mapagkukunan ng computing at storage. Ang Gas fee ng LightDAO ay naka-angkla sa katumbas ng USD, at awtomatikong kino-convert sa halaga ng LIGHT ng oracle tuwing 24 na oras.
> **Slashing** (penalty): Isang mekanismo ng parusa kung saan ang isang verifier ay napipilitang ibawas ang bahagi ng mga ipinangakong token dahil sa paggawa ng masama (tulad ng double signing) o pagiging offline sa mahabang panahon. Ito ay isang pang-ekonomiyang garantiya para sa seguridad ng PoS network.
> **Oracle** (Oracle): Isang bahagi ng imprastraktura na ligtas na nagpapadala ng off-chain na data (gaya ng mga presyo sa merkado, panahon, mga marka ng sports) sa mga on-chain na smart contract. Gumagamit ang LightDAO ng hybrid na oracle architecture ng on-chain na TWAP + multi-source aggregation.
> **TWAP** (Time-Weighted Average na Presyo): Ang presyo ng bawat bloke sa loob ng isang yugto ng panahon ay pantay na tinitimbang ng oras upang mabawasan ang epekto ng pagmamanipula ng mga agarang malalaking transaksyon sa reference ng presyo.
> **AMM** (Automated Market Maker): Isang desentralisadong protocol ng kalakalan na nagsasagawa ng palitan ng token sa pamamagitan ng liquidity pool (sa halip na isang order book). Ang presyo ay awtomatikong tinutukoy ng proporsyon ng mga asset sa pool ayon sa isang formula.
> **DEX / CEX**: Ang DEX (Decentralized Exchange, decentralized exchange) ay hindi kailangang mag-host ng mga asset ng user at mag-trade ng peer-to-peer sa pamamagitan ng mga smart contract; Ang CEX (Centralized Exchange, centralized exchange) ay nangangailangan ng operator na kustodiya ng mga asset at tumugma sa mga transaksyon.
> **IPFS** (InterPlanetary File System, InterPlanetary File System): Decentralized file storage at distribution protocol, na ginagamit sa white paper na ito para sa censorship-resistant na pagho-host ng mga front-end na application (kahit na naka-block ang domain name, maa-access pa rin ng mga user ang platform sa pamamagitan ng IPFS).

---

## Kabanata 5: Token Economic Model

### 5.1 Kabuuang batayan ng disenyo

**LIGHT kabuuang supply: 2.5 bilyon (2,500,000,000), at hindi na ibibigay pa. **

| Mga proyekto sa pag-benchmark | Kabuuang halaga | Paraan ng paglahok | Paghahambing sa LightDAO |
|---------|------|---------|-----------------|
| Bitcoin | 21 milyon | PoW mining machine | Sanggunian sa pagsasalaysay, malayong mataas ang threshold |
| Helium (HNT) | 223 milyon | Hardware hotspot $200+ | DePIN benchmark, hardware limitadong sukat |
| Filecoin (FIL) | 2 bilyon | Storage hardware | Ang pinakamalapit sa magnitude, pareho ay "nag-aambag ng mga mapagkukunan bilang kapalit ng mga token" |
| Kaspa (KAS) | 28.7 bilyon | PoW graphics card | Masyadong malaki, maayos na pagtanggi ay may reference na halaga |
| Pi Network | 100 bilyon | Mga pag-click sa mobile | Negatibong materyal sa pagtuturo: Ang kabuuang halaga ay masyadong malaki → ang value perception ay napakababa |

**Ang pangunahing dahilan sa pagpili ng 2.5 bilyong barya:**

1. **Kakayahan sa pamumuhunan (pangunahing hadlang):** 850 milyong coin sa vault × base na presyo $0.15 × 75% na rate ng paggamit = **$95.63 milyon ≈ $100 milyon** na na-deploy na kapital, na umaabot sa pinakamababang mapagkakatiwalaang threshold ng Lower Middle Market PE. Batayan sa akademiko: Cong, Li & Wang (2021) "Tokenomics: Dynamic Adoption and Valuation" (*Review of Financial Studies* 34(3):1105-1155, NBER w27222) ay nagpapatunay na ang platform utility (investment return → repurchase → distribution support) ay ang pangunahing driver ng breadth value, hindi ang breadth value.
2. **Gabay sa network:** 1 bilyong coin ang mina, at 684,900 coin ang inilabas sa unang araw ng panahon. Kapag mayroong 100,000 aktibong minero, ang average per capita ay 6.51 LIGHT/araw, pinapanatili ang "integer perception".
3. **Pagiging posible sa pagpapatakbo:** 10% strategic operating fund (250 million coins) para malutas ang pre-TGE development/audit/legal funding gap ($1.10-2.85 million). Hindi kayang sakupin ng purong modelo ng komunidad ang gastos na ito.
4. **Pagiging posible ng deflation:** Ang ilalim na linya ng 1 bilyong barya ay naabot sa ika-11 hanggang ika-12 taon sa ilalim ng base scenario (25-30% na mas maikli kaysa sa 15 taon+ ng 21 bilyong plano).
5. ** Makatwirang benchmarking:** Ang parehong antas ng Filecoin (2 bilyon), na kabilang sa nangungunang limang proyekto sa larangan ng DePIN ayon sa halaga ng pamilihan.

### 5.2 Plano ng pamamahagi ng token

| Kategorya ng Paglalaan | Ratio | Dami | Layunin | Paraan ng Paglabas |
|---------|------|------|------|---------|
| Magaan na pagmimina ng node | 40% | 1 bilyon | Gantimpala ang mga nag-aambag sa network | Hinahati bawat 2 taon, inilabas sa real time batay sa kontribusyon |
| Corporate Investment Vault | 34% | 850 milyong piraso | Pagpapatupad ng pamumuhunan sa ilalim ng pamamahala ng DAO (nawasak kapag namumuhunan) | Multi-signature locking, inilabas at sinira lamang sa pamamagitan ng mga wastong resolusyon |
| Ecological Development Fund | 16% | 400 milyon | Liquidity, airdrops, pagpopondo ng developer, mga operasyon ng komunidad | Phased release (tingnan ang Seksyon 5.3) |
| Strategic operating fund | 10% | 250 milyong barya | Koponan, pag-audit, legal, imprastraktura, mga madiskarteng mamumuhunan | 12 buwang bangin + 36 na buwang linear (tingnan ang seksyon 5.X) |

**Industry Benchmarking (Tokenomics.net 2024-2025 cohort benchmark):** Mga reward sa komunidad/user na 20-35% (LightDAO: 40% mining + 16% ecology = 56%, mas mataas dahil sa walang VC round); treasury/reserves 15-25% (LightDAO: 34%, dahil sa investment function); team/investors 15-45% (LightDAO: 10%, mas mababa kaysa sa industriya, pinapanatili ang salaysay ng "Pambansang DAO").

### 5.3 Plano sa Paglabas ng Pondo sa Pagpapaunlad ng Ekolohiya

| Yugto | Oras | Proporsyon | Dami | Layunin |
|------|------|------|------|------|
| TGE | Araw 0 | 30% | 120 milyong piraso | DEX liquidity (60%=72 milyon) + seed airdrop (40%=48 milyon) |
| Linear release period 1 | ika-1 hanggang ika-12 buwan | 40% | 160 milyong barya | 13.33 milyong barya bawat buwan: mga insentibo sa komunidad, marketing, airdrop plan |
| Linear release period 2 | ika-13 hanggang ika-24 | 30% | 120 milyong barya | 10 milyong barya bawat buwan: pagpopondo ng developer, ekolohikal na konstruksyon, mga reserba |

### 5.4 Strategic Operation Fund (250 milyong barya)

| Subcategory | Proporsyon | Dami | Bagay | Panuntunan sa Pagpapalabas |
|--------|------|------|------|---------|
| Pagpapalitan ng serbisyo para sa mga token | 50% | 125 milyong barya | Mga kumpanya ng pagpapaunlad, mga institusyon ng pag-audit, mga law firm, mga operator ng verifier | 12 buwang bangin + 36 buwang linear; 30-50% ng mga bayad sa serbisyo na binayaran sa LIGHT |
| Madiskarteng financing | 30% | 75 milyong piraso | 2-3 DePIN/Cosmos ecological funds o consumer industry strategic parties | Ang pre-TGE ay ibinebenta sa halagang $0.03-$0.05 (nagtataas ng $2.25-3.75 milyon); 12 buwang bangin + 24 na buwang linear; nag-iisang mamumuhunan ≤ 2% ng kabuuang |
| Mga pangunahing kontribyutor | 20% | 50 milyong barya | 3-5 sponsors/core builder | 12 buwang bangin + 36 buwang linear; inilabas batay sa quarterly milestone assessment; walang benta sa panahon ng termino |

**Mga istratehiyang kinakailangan ng mamumuhunan:** Ang mga kontribusyon na hindi pinansyal (isa sa daloy ng deal, mga serbisyo ng verifier, mga mapagkukunan sa pagsunod) ay dapat ibigay, at hindi tinatanggap ang mga purong pinansiyal na mamumuhunan.

**Regulatory Compliance:** Ang pre-TGE sale ay gumagamit ng Reg S (hindi U.S. investors) + Reg D Rule 506(c) (U.S. qualified investors) dual-track exemption.

**Mga pangunahing panuntunan sa pagsisiwalat ng contributor:** Tanging ang kabuuang halaga (50 milyon = 2% ng kabuuang halaga) at mga panuntunan sa pagpapalabas ang ibinunyag, at hindi isiniwalat ang mga personal na pangalan at indibidwal na quota. Ibinunyag ang mga kategorya ng tungkulin: Teknolohiya/Pamumuhunan/Pagsunod/Komunidad.

### 5.5 Output ng pagmimina at plano sa paghahati

**Derivation:** 2A = 1 bilyon → A = 500 milyon (Unang Panahon). Pang-araw-araw na pagpapalabas = 500 milyon ÷ 730 = 684,932 piraso ≈ 684,900/araw. Bawat bloke = 684,932÷49,371 ≈ 13.87 LIGHT.

**Tandaan:** Ang reward pool para sa bawat block ay ibinabahagi ng buong network, kung saan ang 5% ay inilalaan sa mga validator (34,200/araw) at 95% ay inilalaan sa mga light node miners (650,700/araw).

| Panahon | Oras | Kabuuang output | Araw-araw na paglabas | Bawat block reward pool |
|------|------|---------|---------|------------|
| 1st Era | 0-24 na buwan | 500 milyon | ≈684,900 | ≈13.87 ILAW |
| 2nd Era | 25-48 na buwan | 250 milyong piraso | ≈342,500 | ≈6.93 ILAW |
| Ika-3 Panahon | 49-72 buwan | 125 milyong piraso | ≈171,200 | ≈3.47 ILAW |
| Ang Ika-4 na Panahon | 73-96 na buwan | 62.5 milyong piraso | ≈85,600 | ≈1.73 ILAW |
| Ang Ika-5 Panahon | 97-120 buwan | 31.25 milyong piraso | ≈42,800 | ≈0.87 ILAW |

**Suriin:** 5+2.5+1.25+0.625+0.3125+… = 5×2 = 1 bilyon ✓. 97% ang natapos sa loob ng unang 10 taon.

### 5.6 Modelo ng sangguniang kita ng user

| Laki ng network | Per capita araw-araw na kita | Buwanang kita | Taunang kita | Buong markup (1.44x) buwanang kita |
|---------|-----------|--------|--------|--------------------|
| 10,000 minero (yugto ng binhi) | ≈65.07 | ≈1,952 | ≈23,751 | ≈2,811 |
| 100,000 minero (growth stage) | ≈6.51 | ≈195.2 | ≈2,375 | ≈281.1 |
| 1 milyong minero (scale period) | ≈0.65 | ≈19.5 | ≈237.5 | ≈28.1 |

**Antas ng kasosyo (50 imbitasyon, 20% bahagi, buong bonus):**

| Sukat ng network | Sarili (kabilang ang bonus) | Pagbabahagi ng imbitasyon | Pang-araw-araw na komprehensibo | Buwanang komprehensibo |
|---------|------------|---------|--------|--------|
| 10,000 minero | ≈93.7 | ≈650.7 | ≈744.4 | ≈22,332 |
| 100,000 minero | ≈9.37 | ≈65.07 | ≈74.44 | ≈2,233 |
| 1 milyong minero | ≈0.94 | ≈6.51 | ≈7.45 | ≈223.4 |

### 5.7 Airdrop Growth Plan

**Economic model:** Kabuuang airdrop budget = target na naabot sa mga user × per capita airdrop × (1+waste rate) = 100,000 × 150 LIGHT × 1.3 ≈ 19.5 million (acquisition type) + 35.5 million (ecological type) = **55 million** (accounting for 13.75% of the ecological fund).

| Uri ng airdrop | Mga kundisyon sa pag-trigger | solong quota | Badyet |
|---------|---------|---------|------|
| Unang Pagmimina Airdrop | Nakumpleto ang 4 na oras ng epektibong pagmimina sa unang pagkakataon | 50 ILAW | 15 milyong piraso |
| Heograpikal na pagpapalawak | Kumpletuhin ng mga user ng target na market ang ZK-KYC | 100 ILAW | 10 milyong piraso |
| Learn-to-Earn | Kumpletuhin ang Module ng Edukasyon + Pagsusulit | 30 ILAW | 6 Milyong Barya |
| Pagboto sa Unang Pamamahala | Unang Paglahok sa Pagboto | 20 ILAW | 3 milyong barya |
| Pagkakaloob ng pagkatubig | LP injection ≥$50 lock-up sa loob ng 30 araw | 200 ILAW | 10 milyong piraso |
| Paglikha ng nilalaman | Mga tutorial/pagsasalin na na-verify ng komunidad | 50-200 ILAW | 6 milyong piraso |
| Mga channel ng kooperasyon | Pagpaparehistro + unang pagmimina sa pamamagitan ng mga kasosyo | 80 ILAW | 5 milyong piraso |

**CAC verification:** 55 million coins × $0.03 = $1.65 million ÷ 30,000 retain active miners = **$55/person** (industry range $50-200, sa low end). Academic na batayan: Zheng (2023) "Operation Dumbo Drop: Sa Airdrop o Hindi sa Airdrop para sa Paunang Tagumpay sa Pag-aalok ng Coin?" nagpapatunay na ang rate ng pagpapanatili ng mga airdrop na nakatali sa kaganapan ay 3-5 beses kaysa sa mga purong airdrop.

**Anti-aabuso:** Natatanging fingerprint ng browser + ZK-KYC; limitado sa 1 claim bawat kategorya bawat address; 30-araw na panahon ng lock-in; awtomatikong pag-recycle nang walang on-chain na aktibidad sa loob ng 30 araw pagkatapos ng pag-claim.

### 5.8 Dual Engine Flywheel at Capital Pool

Flywheel: Pagboto → Vault LIGHT na pagkasira → USDC na pagbabayad → Profit reflow → Muling pagbili at pagkasira → Presyo ng suporta → Higit pang mga user.

Dual-track system: stable treasury (USDC, profit retention) + flexible treasury (LIGHT layer, nawasak kapag namumuhunan at hindi dumadaloy sa market). Hinahati ang mga buyback gamit ang TWAP, na may isang order na ≤ 5% ng average na pang-araw-araw na dami ng trading.

### 5.9 Pag-isyu at pangangalakal ng sub-token

Ang kabuuang halaga ng pagpapalabas = halaga ng pamumuhunan ÷ $1; ang presyo ng palitan ay batay sa 30-araw na VWAP; lahat ng LIWANAG na nakuha mula sa palitan ay masisira; 50% ng mga tagasuporta/30% airdrop/20% operating reserve ay ipapamahagi (naka-lock sa loob ng 6 na buwan). Ang limitasyon ng dibidendo para sa isang address ay 15%. Ang mga sub-token ay kinakalakal sa on-chain na AMM, na may 30-araw na lock-in na panahon pagkatapos ng pag-isyu, at mamarkahan na "liquidated" pagkatapos ng withdrawal.

### 5.10 Paunang Pagkalikido at Pagtuklas ng Presyo

**TGE (Token Generation Event, token generation event) arrangement: **

| Proyekto | Plano |
|------|------|
| Paunang liquidity pool | Mula sa 120 milyong piraso na inilabas ng ecological development fund na TGE, 72 milyong piraso (60%) ang inilaan at na-inject sa DEX liquidity pool |
| Ipinares na mga asset | USDC (pangunahing pool), USDT (auxiliary pool) |
| Airdrop | Ang natitirang 48 milyon (40%) ay gagamitin para sa mga airdrop sa mga gumagamit ng binhi (tingnan ang Seksyon 5.7 Airdrop Plan) |
| Nakalista sa mga palitan | Unang nakalista sa mga desentralisadong palitan (tulad ng Osmosis, JunoSwap) pagkatapos ng TGE; mag-apply para sa paglilista sa mga sentralisadong palitan simula sa ika-6 na buwan depende sa mga kundisyon sa pagsunod |

**Detalyadong mekanismo ng Dutch Auction:**

Ang Dutch auction ay isang paraan ng pagpepresyo kung saan bumababa ang mga presyo mula mataas hanggang mababa. Sa kaibahan sa mga English auction (kung saan ang mga presyo ay bid mula sa mababa hanggang mataas), sa isang Dutch auction ang nagbebenta ay nagtatakda ng panimulang mataas na presyo at ang presyo ay awtomatikong bumababa sa paglipas ng panahon hanggang sa ang mamimili ay magsumite ng isang subscription sa isang partikular na punto ng presyo. Ang unang presyo kung saan naabot ng kabuuang halaga ng subscription ang target ay ang panghuling presyo ng pagbubukas.

**Bakit pumili ng Dutch auction sa isang nakapirming presyo o English auction:**

| Pagpepresyo | Mga Bentahe | Mga disadvantages | Kakayahang magamit |
|---------|------|------|--------|
| Nakatakdang presyo pre-sale | Simple | Ang pagpepresyo ay subjective, kung ito ay masyadong mataas, ito ay hindi magbebenta, kung ito ay masyadong mababa, ito ay snapped up ng mga robot | Hindi angkop (walang function ng pagtuklas ng presyo) |
| British auction (pag-bid) | Buong pagtuklas ng presyo | Ang malalaking mamimili ay maaaring madiskarteng maghintay at magtaas ng mga presyo; digmaan sa gas | Hindi angkop (on-chain gas war ay hindi kasama ang maliliit na user) |
| **Dutch Auction** | **Awtomatikong pagtuklas ng presyo; walang kinakailangang pag-bid (walang gas war); pantay na pakikilahok ng malalaki at maliliit na mamimili; anti-bot (ang mekanismo ng pagbabawas ng presyo ay natural na pumipigil sa pagtakbo sa harap)** | Ang panimulang presyo at rate ng deceleration ay kailangang itakda nang makatwirang | **Pinaka-angkop (patas + mahusay + anti-manipulasyon)** |

**Mga tukoy na parameter ng LightDAO Dutch auction:**

| Mga Parameter | Mga Setting | Paglalarawan |
|------|------|------|
| Target ng auction | LIGHT token (inilalaan mula sa 72 milyon na inilabas ng ecological fund TGE) | Ang USDC mula sa auction ay ilalagay sa stable vault |
| Target na halaga ng pangangalap ng pondo | **$15 milyon USDC** | $5 milyon → pinakamababang reserba ng stable treasury; $10 milyon → paunang puhunan na kapital |
| Panimulang presyo | $0.20/LIGHT | Mas mataas kaysa sa inaasahang presyo ng ekwilibriyo, tinitiyak na hindi ito mawawala sa ilang segundo |
| Rate ng deceleration | Bawasan ng 5% bawat oras | Simula sa $0.20, bumababa sa $0.017 pagkatapos ng humigit-kumulang 48 oras (kung walang nag-subscribe) |
| Pinakamababang presyo ng reserba | $0.01/LIGHT | Kung ang reserbang presyo ay ibinaba at ang target ay hindi pa rin naabot, ang auction ay ipagpapaliban ng 24 na oras o ang bilang ng mga bagay ay maisasaayos |
| Paraan ng subscription | Isusumite ng user ang "Handa akong bumili ng X USDC na katumbas na LIGHT sa kasalukuyang presyo" | Walang kinakailangang pag-bid, ang sistema ay maaayos ayon sa pinal na pinag-isang presyo (anumang labis ay ibabalik nang walang kabayaran) |
| itaas na limitasyon ng solong user | Hindi hihigit sa 5% ng target na halaga ng pangangalap ng pondo (i.e. $750,000) | Pigilan ang nag-iisang mamimili mula sa pagmonopolyo sa mga unang chip |
| Mga Kinakailangan sa KYC | Pinahusay na Pag-verify (Tax Residency) | Mga Kinakailangan sa Pagsunod |

**Patunguhan ng mga pondo mula sa mga resulta ng auction:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Panahon ng proteksyon sa pagtuklas ng presyo:** Ang isang circuit breaker ng pagbabagu-bago ng presyo ay ise-set up sa unang 72 oras pagkatapos ng TGE - kung ang presyo ng transaksyon ng DEX ay lumihis ng higit sa ±50% mula sa presyo ng pagbubukas ng auction, ang sub-token exchange function ay masususpindi (hindi maaapektuhan ang pagmimina at paglilipat) upang maiwasan ang matinding haka-haka na makagambala sa ecological startup. Ang fuse ay awtomatikong ilalabas pagkatapos ng 72 oras.

**Bakit $15 milyon sa halip na mas mababa:** Ang paunang pamumuhunan na kapital na $10 milyon ay kailangang suportahan ang 3-5 na pamumuhunan sa unang taon (isang solong pamumuhunan ay $2-5 milyon, tingnan ang sukat ng panahon ng pagsisimula sa Seksyon 9.1). Kung $5 milyon lamang ang itataas (lahat bilang mga reserba), walang mai-deploy na kapital sa pamumuhunan sa unang taon at hindi magsisimula ang flywheel. $15 milyon = reserbang $5 milyon + puhunan $10 milyon, na siyang pinakamababang balanse sa pagitan ng "safety bottom line" at "flywheel start".

### 5.11 Deflation mechanism at bottom line

** Dami ng sirkulasyon = paglabas ng pagmimina + pagpapalabas ng ekolohiya + inilabas na estratehikong pondo − palitan at pagkasira − pagkasira ng gas − muling pagbili at pagkasira. ** 850 milyong mga barya mula sa investment vault ay hindi pa nakapasok sa sirkulasyon. Teoretikal na itaas na limitasyon ng sirkulasyon = 10+4+2.5 = **1.65 bilyon**.

| Mga kundisyon sa pag-trigger | Pag-uugali ng system |
|---------|---------|
| Sirkulasyon ≤ 1.5 bilyong piraso | Signal ng pagbagal (napakababang senaryo ng pagkasira) |
| Dami ng sirkulasyon ≤ 1.2 bilyong piraso | Maagang babala na anunsyo, pagsususpinde ng aktibong pagkasira (tungkol sa ika-8 taon ng base na senaryo) |
| Dami ng sirkulasyon ≤ 1 bilyon | Mahirap na huminto, lahat ng mga pagkasira ay permanenteng sarado (base scenario ay tungkol sa taong 11-12) |

### 5.12 Mekanismo ng pag-stabilize ng presyo (anti-death spiral)

**Punong Prinsipyo:** Ang LightDAO ay hindi nakakasagabal sa pang-araw-araw na pagtuklas ng presyo sa merkado. Inaayos lamang ng protocol ang mga parameter nito sa matinding pababang mga senaryo upang mabawasan ang panganib na mahulog sa isang "death spiral".

**Lohika ng pagmamarka:** Sa iba't ibang pabagu-bagong kapaligiran, ang parehong pagtanggi ay kumakatawan sa iba't ibang antas ng abnormalidad. Ang isang matalim na pagbaba sa isang low-volatility market ay isang mas malakas na abnormal na signal at nangangailangan ng mas mataas na intensity intervention; ang isang matalim na pagbaba sa isang high-volatility market ay medyo karaniwan at mas magaan na interbensyon ay maaaring gamitin. Samakatuwid, ang intensity ng interbensyon ay positibong nauugnay sa abnormalidad ng signal, sa halip na depende lamang sa ganap na halaga ng pagbaba.

**Buong flow chart ng mekanismo:**

| Katayuan ng merkado | 30-araw na makasaysayang pagkasumpungin | Mga kundisyon sa pag-trigger | Antas ng signal | Pagpapatupad pagkatapos ng trigger | Mga kondisyon sa pagbawi |
|---------|--------------|---------|---------|----------|---------|
| Mababang pagkasumpungin | ≤30% | Pinagsama-samang pagbaba ng ≥40% para sa 5 magkakasunod na araw | Antas I | Bumaba sa 50% ang output ng pagmimina; tumaas ang ratio ng pagkawasak mula 20% hanggang 35%; ang panahon ng publicity ng pagsasaayos ng parameter ng panganib ay pinaikli mula 72h hanggang 12h; ang komite ng anino ay pumasok sa aktibong estado (ang pansamantalang karapatan sa pagsususpinde lamang ang maaaring gamitin alinsunod sa batas) | Ang presyo ay tumaas sa itaas ng 30-araw na moving average, at rebound ng ≥80% mula sa trigger price, at nanatiling ganoon sa loob ng 10 magkakasunod na araw |
| Katamtamang pagbabagu-bago | 30%-60% | Pinagsama-samang pagbaba para sa 7 magkakasunod na araw ≥ 50% | Antas II | Bumaba sa 50% ang output ng pagmimina; ang ratio ng pagkawasak ay tumaas mula 20% hanggang 30%; ang panahon ng publisidad ay pinaikli sa 24 na oras; ang komite ng anino ay pumasok sa aktibong estado | Ang presyo ay tumaas sa itaas ng 30-araw na moving average, at rebound ng ≥ 60% mula sa trigger price, at nanatiling ganoon sa loob ng 7 magkakasunod na araw |
| Mataas na pagkasumpungin | 60%-100% | 10 magkakasunod na araw ng pinagsama-samang pagbaba ≥55% | Antas III | Bumaba sa 75% ang output ng pagmimina; ang ratio ng pagkawasak ay tumaas mula 20% hanggang 25%; ang panahon ng publisidad ay pinaikli sa 48 oras; ang komite ng anino ay pumasok sa standby | Ang presyo ay tumaas sa itaas ng 30-araw na moving average, at rebound ng ≥40% mula sa trigger price, at nanatiling ganoon sa loob ng 5 magkakasunod na araw |
| Matinding pagkasumpungin | >100% | Pinagsama-samang pagbaba para sa 10 magkakasunod na araw ≥ 65% | Antas III | Ipinatupad ayon sa Level III na mga panukala para sa mataas na pagkasumpungin | Ipinatupad ayon sa Level III na mga kondisyon sa pagbawi para sa mataas na pagkasumpungin |

**Mga kundisyon sa pagbubukod:** Kapag ang pagbaba ng Bitcoin sa parehong panahon ay mas mababa sa 50% ng pagbaba ng LIGHT, ang mekanismo sa itaas ay maaaring ma-trigger upang maalis ang isang sistematikong pagbagsak ng merkado (ibig sabihin, kung ang BTC ay bumagsak din sa parehong panahon, ito ay isang pangkalahatang kaganapan sa merkado, at walang hiwalay na interbensyon ang pinasimulan para sa LIGHT).

**Paglalarawan ng lohika sa pagbawi:** Ang mga kinakailangan sa pag-rebound at pagbaba ng tagal sa antas ng abnormality: Ang Level I ay nangangailangan ng pinakamataas na rebound amplitude (80%) at ang pinakamahabang oras ng pagkumpirma (10 araw), habang ang Level III ay nangangailangan ng medyo mas mababang mga kinakailangan (40%/5 araw). Ang kaayusan na ito ay naaayon sa progresibong lohika ng "mas malakas ang abnormal na signal, mas malakas ang interbensyon, at mas mahigpit ang kumpirmasyon sa pagbawi".

**Volatility at data source ng presyo:** Ang 30-araw na makasaysayang volatility at pinagsama-samang pagbaba ay ibinibigay ng on-chain price oracle (tingnan ang Seksyon 4.10), batay sa snapshot ng TWAP ng pang-araw-araw na UTC 00:00 block, at huwag umasa sa anumang external na data source.

### 5.13 Sustainability Stress Test ng Mga Kita

| Mga sitwasyon ng stress | Ano-kung | Mga tugon sa protocol | Mga pinakamasamang resulta |
|---------|---------|---------|---------|
| Nabigo ang lahat ng pamumuhunan | Ang lahat ng namuhunang kumpanya ay nalugi o nabigong lumabas | Ang pondo ng seguro (10% ng mga kita na naipon) ay sumasaklaw sa bahagi ng mga pagkalugi; matatag na reserbang treasury (≥$8 milyon) upang mapanatili ang mga operasyon; ang mga bagong pamumuhunan ay sinuspinde hanggang sa muling pagsusuri ng komunidad | Ang mga may hawak ng sub-token ay hindi makakatanggap ng mga dibidendo; Ang magaan na presyo ay nasa ilalim ng presyon ngunit hindi bumabalik sa zero (patuloy na gumagana ang mga function ng pagmimina at pamamahala) |
| Ang merkado ay bumagsak ng 80% | LIGHT presyo ay bumaba ng 80% mula sa peak | I-trigger ang mekanismo ng anti-death spiral (antas II o antas III); ang output ng pagmimina ay nabawasan ng 50-75%; ang ratio ng pagkawasak ay nadagdagan; maaaring suspindihin ng komite ng anino ang mga operasyong may mataas na peligro | Lumiliit ang kita ng user ngunit patuloy na gumagana ang network; awtomatikong inaalis ang mekanismo kapag natugunan ang mga kondisyon sa pagbawi |
| Mga pangunahing pagbabawal sa regulasyon sa merkado | Isang malaking bansa ang ganap na nagbawal ng mga asset ng crypto | Ang front-end switching IPFS mirror ay nananatiling naa-access; hindi maaapektuhan ang mga on-chain na asset at mga umiiral nang karapatan at interes ng user; Ang pagiging available ng serbisyo ng third-party ay inaayos lamang sa loob ng saklaw ng legal na pagpapatupad; Ang mga operasyon ng SPV sa Cayman Islands ay hindi napapailalim sa hurisdiksyon ng isang bansa | Ang paglago ng gumagamit sa rehiyon ay tumitigil; ang ibang mga rehiyon sa buong mundo ay hindi apektado |
| Malaking pagkawala ng mga user | Ang mga aktibong minero ay bumaba ng higit sa 70% | Awtomatikong ibinabahagi ang BaseReward (lumiliit ang denominator → tumataas ang kita ng bawat kapita ng mga nananatiling gumagamit); ang mga insentibo sa imbitasyon ay binibigyan ng timbang upang maakit ang mga daloy ng pagbalik; pansamantalang ibinababa ang mga threshold ng pamamahala (dynamic na mekanismo sa Seksyon 5.14) | Ang seguridad ng network ay nabawasan ngunit ang kadena ay hindi ititigil (Tendermint BFT kinukunsinti <1/3 validators pagiging offline) |
| Mga pangunahing kahinaan sa smart contract | Mga mapagsamantalang kahinaan na makikita sa mga pangunahing kontrata | Multi-signature emergency suspension ng fund outflows (72-hour time lock ay nagbibigay ng response window); Magsimula ng backup na boto sa paglipat ng kontrata (L4 level emergency repair, tingnan ang Seksyon 4.12); Sinasaklaw ng pondo ng insurance ang mga pagkalugi ng user | Maaaring masira ang ilang pondo; Nagpapatuloy ang mga normal na operasyon pagkatapos makumpleto ang paglipat |

### 5.14 Intergenerational balancing mechanism

Dynamic na pagsasaayos ng threshold ng pamamahala: para sa bawat 1 milyong bagong pinagsama-samang aktibong minero, ang threshold ng panukala ay awtomatikong binabaan ng 5% (ibabang limitasyon 2,500 LIGHT).

> **[Terminolohiya sa kabanatang ito]**
> **TGE** (Token Generation Event): Ang punto kung kailan unang ginawa at ipinamahagi ang isang token sa pamamagitan ng isang matalinong kontrata, karaniwang sinasamahan ng pagtatatag ng isang paunang liquidity pool, pagpepresyo sa auction ng Dutch, at ang unang pampublikong transaksyon. Katulad ng isang IPO sa tradisyonal na pananalapi, ngunit hindi nagsasangkot ng listahan ng stock exchange.
> **Halving** (Halving): Isang mekanismo kung saan ang output ng pagmimina ay awtomatikong nababawasan ng 50% bawat takdang panahon (2 taon/730 araw para sa LightDAO). Ang layunin ay lumikha ng progresibong kakapusan - habang lumilipas ang panahon, paunti-unti ang naidagdag na bagong supply, at kung hindi bababa ang demand, susuportahan ang mga presyo. Ang Bitcoin ay gumagamit ng paghahati tuwing 4 na taon.
> **Treasury** (Treasury): Token reserves na naka-lock ng mga multi-signature na kontrata, na maaari lang i-release sa pamamagitan ng mga resolusyon sa pamamahala. Ang LightDAO ay may dalawang uri ng mga vault: mga investment vault (na mayroong LIGHT at nasisira kapag ang mga pamumuhunan ay naisakatuparan) at mga stable na vault (na may hawak na USDC at ginagamit upang magbayad ng pagsasaalang-alang sa pamumuhunan at mga gastos sa pagpapatakbo).
> **Deflation** (Deflation): Ang proseso kung saan patuloy na bumababa ang kabuuang supply o sirkulasyon ng mga token. Nakakamit ng LightDAO ang deflation sa pamamagitan ng apat na mekanismo: pagpapatupad at pagkasira ng pamumuhunan, pagpapalitan at pagkasira ng sub-token, pagkasira ng bayad sa gas (50%), at muling pagbili at pagkasira ng tubo.
> **Death Spiral** (Death Spiral): Bumaba ang mga presyo ng token → lumiliit ang kita ng mga minero → huminto ang mga minero → bumababa ang seguridad/kontribusyon ng network → karagdagang pagkawala ng kumpiyansa → isang masamang ikot kung saan patuloy na bumababa ang mga presyo. Ang namarkahang mekanismo ng interbensyon sa Seksyon 5.12 ay idinisenyo upang matakpan ang cycle na ito.
> **Sub-token** (Sub-token): SPV income distribution claim certificate na inisyu alinsunod sa mga patakaran pagkatapos makumpleto ang bawat corporate investment (tulad ng pagkuha ng coffee brand → CAFE token). May hawak na mga sub-token = may hawak na mga kwalipikasyon para sa pamamahagi ng mga hinaharap na kita at hindi kumakatawan sa mga karapatan ng shareholder o mga karapatan sa pamamahala ng korporasyon.
> **LP** (Liquidity Provider): Ang mga kalahok na nag-iniksyon ng dalawang asset na may katumbas na halaga (gaya ng LIGHT+USDC) sa DEX liquidity pool ay makakakuha ng mga bayarin sa transaksyon bilang kapalit. Ang LP ang batayan para sa normal na operasyon ng DEX.
> **VWAP** (Volume-Weighted Average na Presyo): Ang presyo sa loob ng isang yugto ng panahon ay tinitimbang ng dami ng bawat transaksyon, na sumasalamin sa tunay na halaga ng transaksyon sa merkado. Gumagamit ang LightDAO ng 30-araw na VWAP bilang benchmark ng pagpepresyo para sa sub-token exchange.
> **CAC** (Customer Acquisition Cost, user acquisition cost): Ang average na gastos para makakuha ng epektibong aktibong user. Ang target na CAC ng LightDAO airdrop program ay $55/napanatili na aktibong mga minero (saklaw ng industriya $50-200).
> **wLIGHT** (Wrapped LIGHT, encapsulated LIGHT): LIGHT-equivalent token na inisyu sa Ethereum o Solana sa pamamagitan ng cross-chain bridges, at ang katumbas na halaga ng native LIGHT ay naka-lock ng kontrata ng bridge bilang 1:1 na reserba. Ang layunin ay payagan ang mga hindi gumagamit ng ecosystem ng Cosmos na makakuha at humawak ng LIGHT.
> **Dutch Auction** (Dutch Auction): Isang paraan ng pagpepresyo kung saan bumababa ang presyo mula mataas hanggang mababa. Nagtatakda ang nagbebenta ng panimulang mataas na presyo, at awtomatikong bumababa ang presyo sa paglipas ng panahon hanggang sa magsumite ang mamimili ng subscription sa isang partikular na punto ng presyo. Ang unang presyo kung saan naabot ng kabuuang halaga ng subscription ang target ay ang panghuling presyo ng transaksyon. Ang kalamangan ay walang pag-bid na kinakailangan (walang gas war), ang mga mamimili sa lahat ng laki ay pantay, at ito ay natural na lumalaban sa robot preemption.

---

## Kabanata 6: Mekanismo ng Pamamahala

### 6.1 Dalawang-dimensional na modelo ng pagboto

Currency holding weight (kabilang ang reputasyon + level bonus, kabuuang pinakamataas na limitasyon +40%) + bilang ng mga address (1 address = 1 boto, ang mga nauugnay na address ay pinagsama-sama). Ang mga karapatan sa pagboto ay may bisa sa loob ng 90 araw at maaaring i-activate sa pamamagitan ng paglilipat ng 5 LIGHT. Bonus sa reputasyon: Hawak ang pera sa loob ng 1 taon + 15 wastong boto → hanggang +30%.

### 6.2 Dynamic na pass rate

Minimum passing rate = 50% + (50% - aktwal na rate ng pagboto). Simple majority kapag ang rate ng pagboto ≥50%.

### 6.3 Mga parameter ng panukala

| Uri | Margin | Rate ng pagboto ng token | Rate ng pagboto sa address | Pass rate | Pagkaantala ng pagpapatupad |
|------|--------|-----------|-----------|--------|---------|
| Micro | $100 | ≥15% | ≥20% | Dynamic ≥55% | 24h |
| Uri ng pagkuha | $500 | ≥25% | ≥30% | Dynamic ≥60% | 72h |
| Uri ng venture capital | $500 | ≥35% | ≥40% | Dynamic ≥60% | 72h |
| Major | $1,000 | ≥45% | ≥50% | Dynamic ≥66% | 72h |
| Emergency | $2,000 | ≥50% | ≥60% | ≥75% | Walang pagpopondo 6h/high-risk 1h; ang mga pagpapatakbo ng kapital ay napapailalim pa rin sa 72h time lock |

### 6.4 Ikot ng buhay ng panukala

Kwalipikasyon sa pagsusumite: ≥5,000 LIGHT + 30 magkakasunod na araw ng pledge + deposito. Pampublikong anunsyo 72h (binago ≤ 2 beses). Nagaganap ang pagboto sa loob ng 7 araw (48h para sa fast track, ≤500,000 USDC). Paglamig ng veto sa loob ng 90 araw. Ang pagiging epektibo ay naantala sa loob ng 24 na oras.

**Paglalarawan sa threshold:** 5,000 coin sa yugto ng binhi (10,000 minero) ≈ 77 araw ng pangunahing output; antas ng kasosyo ≈ 7 araw. Isasaaktibo ang pamamahala sa ikapitong buwan, at magkakaroon ng sapat na oras ng pag-iipon ang mga naunang gumagamit.

### 6.5 Mga insentibo sa pagboto

Mayroong pangunahing insentibo para sa paglahok (kahit pagbabahagi), at mayroong karagdagang bonus para sa tamang paghuhusga (50% ng pool ng pagtaya). Tumaya sa hanay na 5-500 LIGHT. Pigilan ang herding effect: Ang mga kalaban ay tumatanggap pa rin ng mga pangunahing insentibo kahit na sila ay "nasa maling koponan".

### 6.6 Mga gantimpala at parusa para sa tagumpay o pagkabigo

Pagkabigo sa mabuting loob: 50% refund ng deposito + 30 araw na cooldown. Nakakahamak na pagkabigo (pamemeke/pag-uulit): buong halaga na nakumpiska + permanenteng pagbabawal. Patunay ng panloloko: nilimitahan sa 5,000 LIGHT, 40% penalty ng establishment bonus + 500 LIGHT.

### 6.7 Transparency sa Pananalapi

Real-time na dashboard sa chain + quarterly financial report + annual independent audit (dapat makumpleto ang unang audit bago ang TGE) + real-time na pagsisiwalat ng mga target sa pamumuhunan.

---

## Kabanata 7: Pagsusuri at pagbabalanse ng kapangyarihan at kahulugan ng tungkulin

### 7.1 Paunang Tagapangalaga

Limitado ang mga pahintulot sa dokumento/format/opisyal na impormasyon sa website. Termino ≤ 24 na buwan. Dapat magtalaga ng alternatibong tagapag-alaga (hindi makapirma sa loob ng 30 magkakasunod na araw → awtomatikong kinuha). Sabay-sabay na kapansanan → 48h emergency na pagboto upang humirang ng pansamantalang tagapamahala.

### 7.2 Roadmap ng Power Transfer

| Yugto | Oras | Mga Pahintulot | Pag-apruba sa Pamumuhunan |
|------|------|------|---------|
| Panahon ng paglikha | 0-6 na buwan | Tagapangalaga (di-pinansyal) | Tagapangalaga + multi-pirma ng komunidad 3/5 |
| Panahon ng paglipat | Hulyo-Disyembre | Ang Guardian + core contributor ay magkasamang lumagda | Pareho sa itaas + pangunahing contributor |
| Panahon ng kapanahunan | 13-24 na buwan | Komite sa Pamamahala 3/5 | Regular na two-dimensional na pagboto |
| Panahon ng awtonomiya | 25 buwan + | Lahat ng may hawak | Parehong panahon ng kapanahunan |

### 7.3 Komite sa Pamamahala

Ang kapangyarihan ay nahahati sa limang tao (umiikot na chairman/pinansya/teknolohiya/komunidad/key), quarterly rotation, at ang termino ay anim na buwan at maaaring muling mahalal nang isang beses. Nangako ang kampanya ng 50,000 LIGHT + 100 address joint signatures. Ang paggawa ng desisyon ay kinabibilangan ng ≥3 tao at sumasaklaw sa ≥3 posisyon.

**Paglalarawan ng threshold:** 50,000 coin sa seed stage ≈ 67 araw (2.2 buwan) para sa mga partner; sa yugto ng paglago ≈ 672 araw (22 buwan). Ang unang halalan ng komite sa ika-13 buwan ay magagamit sa mga unang kasosyo.

### 7.4 Shadow Committee

Pansamantalang pagsususpinde para sa "mga paglabag/parusa/major fraud" lamang. Ang lahat ng mga boto ay dapat pagtibayin sa loob ng 72 oras (pagsalungat >60%→binasura). Dalawang beses na magkasunod na tinanggihan → awtomatikong na-impeach at na-disband.

### 7.5—7.6 Pag-verify ng kampanya at pangunahing plano

SimHash>80% diskwalipikasyon; Ang nilalaman ng AI ay dapat dagdagan ng paliwanag; 20% ng mga boto ay ibabawas para sa mga absent na tanong. Key shard backup + quarterly health check + 7-araw na pampublikong anunsyo + pagpapalit ng pagboto.

---

## Kabanata 8: Tiwala at Mekanismo ng Seguridad

### 8.1 Limang pangunahing mekanismo ng seguridad

Time lock 72h (ang mga panukalang pang-emergency ay hindi exempt sa capital operations); multi-signing 3/5; quarterly rotation ≤ 2 session; 100% na parusa para sa pandaraya; lahat ng transaksyon ay nasa kadena.

### 8.2 Pondo ng Seguro

**10%** ng matagumpay na kita sa pamumuhunan ay naipon. Ang mga claim ay dapat independiyenteng iulat + DAO 66% pabor + solong ≤ pool 20%. Karagdagang mapagkukunan: 30% ng multa para sa pamemeke. Ang pagpoposisyon ng "partial buffer" ay hindi ganap na proteksyon.

### 8.3 Matinding plano

Pangangasiwa ng black swan → IPFS + pagtanggal ng mga karapatan ng administrator; pandaraya → pagsususpinde ng shadow committee (72h ratification) + insurance fund + SPV arbitration; spiral ng kamatayan → Seksyon 5.12 mekanismo; kahinaan sa kontrata → multi-signature suspension + migration voting; ang mga validator ay sama-samang gumagawa ng masama → BFT tolerance <1/3, kung lumampas, ang chain ay masususpindi + emergency voting migration.

---

## Kabanata 9: Mga Pagpapatakbo sa Pamumuhunan at Mga Diskarte sa Paglabas

### 9.1 Pagsusuri at sukat ng mga target sa pamumuhunan

**Phase-by-stage growth trajectory ng investment scale (formula: treasury surplus × 15% × LIGHT na presyo): **

| Yugto | MAGAAN na presyo | Isang limitasyon sa transaksyon sa unang panahon ng vault | Mga target ng adaptasyon | Pag-benchmark ng industriya |
|------|---------|-----------------|----------|----------|
| Panahon ng pagsisimula (Y1-2) | $0.02—$0.05 | $2.55 milyon—$6.37 milyon | Nag-iisang tindahan/maliit na chain, angel round | Micro PE |
| Yugto ng paglago (Y3-5) | $0.05—$0.30 | $6.37 milyon—$38.25 milyon | Regional chain 30-200 na tindahan, Seed-A round | Lower Middle Market PE |
| Yugto ng kapanahunan (Y5-8) | $0.30—$1.00 | $38.25 milyon—$127.5 milyon | Multinational chain/medium-sized na teknolohiya, round B-C | Middle Market PE |
| Panahon ng scale (Y8+) | $1.00+ | $127.5 milyon+ | Mga malakihang pagkuha, Pre-IPO | Malaking PE/Yugto ng Paglago VC |

### 9.2 Proseso ng paggawa ng desisyon sa pamumuhunan

Pagtuklas ng proyekto (≥5,000 LIGHT) → independent due diligence → 72h public announcement → two-dimensional na pagboto → 24/72h execution.

### 9.3 Paglabas at pamamahagi ng kita

Taunang dibidendo: **40%** mga may hawak ng sub-token / **30%** stable vault / **20%** muling bumili ng LIGHT para sa pagkasira / **10%** pondo ng seguro.
Lumabas sa kita: **70%** Stable Vault / **30%** Muling Bumili at Mag-burn.

### 9.4 Disiplina sa Pamumuhunan

| Mga Panuntunan | Nilalaman |
|------|------|
| Isang limitasyon sa pagkasira | Vault na natitira × 15% (initial 850 million × 15% = 127.5 million coins) |
| Nag-iisang target | ≤25% ng kabuuang halaga ng vault |
| Konsentrasyon ng industriya | ≤40% ng portfolio |
| Heograpikal na konsentrasyon | ≤30% ng portfolio |
| Stable treasury reserves | $5 milyon sa TGE (auction), umaabot sa $8 milyon sa ika-24 na buwan |
| Panahon ng paglamig | 2 magkasunod na pagkabigo → 180 araw |

**Vault capacity:** 850 milyong piraso × $0.10 = $85 milyon (unang kabuuang kapasidad); × $0.30 = $255 milyon; × $1.00 = $850 milyon. Ang 15% na limitasyon sa iisang transaksyon ay ginagawang positibong nauugnay sa presyo ang bilis ng pamumuhunan.

> **[Terminolohiya sa kabanatang ito]**
> **EBITDA** (Mga Kita Bago ang Interes, Mga Buwis, Depreciation at Amortization): Isang indicator na sumusukat sa kakayahang kumita ng mga pangunahing operasyon ng kumpanya, inaalis ang interference ng istrukturang pampinansyal (interes), patakaran sa buwis (buwis), at mga pagpipilian sa accounting (depreciation/amortization), na nagpapadali sa paghahambing ng cross-enterprise at cross-industry. EBITDA margin = EBITDA ÷ operating income.
> **DCF** (Discounted Cash Flow, discounted cash flow method): Isang paraan ng pagtatasa na nagko-convert sa inaasahang daloy ng cash sa hinaharap ng kumpanya sa kasalukuyang halaga sa isang partikular na rate ng diskwento. Ito ay angkop para sa mga mature na negosyo na may stable na cash flow (tulad ng mga consumer chain), ngunit hindi para sa maagang yugto ng mga kumpanya ng teknolohiya na hindi pa kumikita.
> **IPO** (Initial Public Offering): Ang unang pagkakataon na ang isang kumpanya ay pampublikong nag-isyu ng mga pagbabahagi sa isang stock exchange at nakalista para sa pangangalakal. Para sa LightDAO, ang IPO ng mga namuhunang kumpanya ay isa sa mga pangunahing daanan ng paglabas para sa mga makina ng paglago.
> **Pre-IPO**: Ang huling round ng pribadong equity financing bago opisyal na nakalista ang kumpanya. Kadalasan ang valuation ay malapit sa post-IPO level, ang panganib ay mas mababa kaysa sa mga naunang round ngunit ang return multiple ay mas mababa din.
> **Pagpapatupad ng TWAP** (Pagpapatupad ng Average na Presyo ng Time-Weighted): Hatiin ang malalaking halaga ng repurchase order sa maramihang mga order na may maliit na halaga at isagawa ang mga ito nang pantay-pantay sa isang yugto ng panahon upang maiwasan ang epekto ng isang malaking order sa presyo ng merkado. Itinakda ng LightDAO na ang isang muling pagbili ay hindi lalampas sa 5% ng average na pang-araw-araw na dami ng kalakalan.

---

## Kabanata 10: Roadmap

| Yugto | Oras | Mga Pangunahing Layunin | Mga Pangunahing Milestone | Mga Kinakailangan |
|------|------|---------|-----------|---------|
| Panahon ng paghahanda | Q4 2026 | Legal na entity + koponan + mga pondo sa lugar | Nakumpleto ang pagpaparehistro ng Cayman/BVI entity; nilagdaan ang technical partner o development team; nakumpirma ang intensyon ng madiskarteng mamumuhunan (2-3 kumpanya); panimulang kapital ≥ $150,000 sa lugar | tinutukoy ng tagapagtatag ang paraan ng pagsisiwalat ng pagkakakilanlan; pagkumpleto ng BP at Pitch Deck |
| Panahon ng pag-unlad | Q1-Q2 2027 | Pagbuo ng core system | 10 matalinong mga module ng kontrata ang binuo; Ang PWA front-end development ay natapos na; 7 verifier testnets ang na-deploy; ang panloob na pagsubok sa Alpha ay lumipas na | Nakalagay ang development team; dokumento ng mga kinakailangan (teknikal na Spec) natapos |
| Panahon ng pag-audit at pagsubok | Q3 2027 | Pag-verify sa seguridad at pagsunod | Paglabas ng independiyenteng ulat sa pag-audit ng seguridad (≥1 nangungunang institusyon); pagpapalabas ng liham ng opinyon sa pagsunod sa batas (MLM + securities law); 50,000 kasabay na stress test ang pumasa; anti-cheating system false positive rate <2%; natapos ang pagsasanay sa pagboto sa pamamahala | Pag-freeze ng pagpapaunlad ng kontrata (Code Freeze); mga bayarin sa pag-audit sa lugar |
| TGE at mainnet online | Q4 2027 | Pag-isyu ng token + paglulunsad ng network | Nakumpleto ang auction ng Dutch (target na $15 milyon); mainnet online (≥10 validators); platform ng pagmimina bukas sa publiko; Naitatag ang DEX liquidity pool; seed airdrop na inisyu | Naipasa ang audit; validators ≥7 (hard bottom line); deployment ng kontrata sa auction |
| Panahon ng pagbuo ng paniniwala | Q1 2028 (ika-1 hanggang ika-3 buwan pagkatapos ng TGE) | 30,000-50,000 mga gumagamit ng binhi | Ang mga aktibong minero ay lumampas sa 30,000; pagsasanay sa pagboto sa unang pamamahala; itinatag ang channel ng maraming wika sa komunidad (Ingles/Chinese/Spanish/Portuguese/Philippines); unang buwanang ulat ng komunidad na inilabas | Nakumpleto ang TGE; pangkat ng pagpapatakbo ng komunidad sa lugar |
| Halaga ng anchor period | Q2-Q3 ng 2028 (ika-4 hanggang ika-9 na buwan pagkatapos ng TGE) | Unang pamumuhunan + panahon ng transisyonal na pamamahala | Ang unang panukala sa pamumuhunan ay naipasa (ang multi-signature na pag-apruba sa panahon ng simula ay nalalapat sa ika-4 hanggang ika-6 na buwan; ang magkasanib na pag-apruba sa panahon ng transisyonal ay nalalapat mula sa ika-7 buwan); nakumpleto ang unang paghahatid ng SPV; ang mga validator ay bukas para sa halalan (mula sa ika-7 buwan); ang unang quarterly financial report ay inilabas | matatag na treasury USDC≥$5 milyon; nakumpleto na ang target na pamumuhunan dahil sa pagsusumikap |
| Panahon ng kapanahunan ng pamamahala | 2028 Q4-2029 Q1 (ika-10 hanggang ika-15 buwan pagkatapos ng TGE) | Halalan ng komite + transisyon ng desentralisasyon | Unang halalan ng komite ng pamamahala (ika-13 buwan); Pagpasok sa panahon ng kapanahunan (3/5 na desisyon ng komite); wLIGHT cross-chain bridge napupunta online; Ang aplikasyon sa listahan ng CEX ay isinumite; Nagsisimula ang plano sa pagpopondo ng developer | Mga aktibong minero ≥ 100,000; ≥ 100 address sa magkasanib na mga kandidato |
| Panahon ng pagpapalawak ng ekolohiya | Simula sa Q2 ng 2029 (ika-16 na buwan + pagkatapos ng TGE) | Malaking pagtitiklop | Ang mga aktibong minero ay lumampas sa 200,000-500,000; 2-3 pamumuhunan ang nakumpleto; ang unang pagpapatunay sa pagpapauwi ng tubo; LIGHT repurchase at destruction nagsimula | Ang komite ng pamamahala ay gumagana nang normal; ang modelo ng pamumuhunan ay napatunayan na |
| Mature na panahon ng operasyon | Simula sa Q4 ng 2029 (ika-25 buwan + pagkatapos ng TGE) | Pag-ikot ng flywheel + kumpletong awtonomiya | Pagpasok sa panahon ng awtonomiya (mga pangunahing panukala mula sa lahat ng may hawak); pinagsama-samang investment portfolio deployment ≥ $30 milyon; ang data ng deflation ay pampublikong nabe-verify | Ganap na desentralisado ang pamamahala |

**Mga prinsipyo sa disenyo ng roadmap:**

- **Pag-audit bago ang TGE:** Ang mga token ay hindi kailanman ibibigay nang hindi nakumpleto ang isang independiyenteng pag-audit sa seguridad. Ito ang pangunahing garantiya para sa seguridad ng mga pondo ng user.
- **Nauuna ang mga verifier sa mga user:** Kapag nag-online ang mainnet, magkakaroon ng ≥10 verifier (BFT fault tolerance f≥3), na tinitiyak na hindi magsasara ang network dahil sa isang punto ng pagkabigo.
- **Nauuna ang pamumuhunan sa pagpapalawak:** Pagkatapos lamang na maging matagumpay ang unang pamumuhunan at makabuo ng nabe-verify na kita, maaari tayong pumasok sa malakihang pagpapalawak. Iwasang ilagay ang cart bago ang kabayo sa pamamagitan ng "pagpapalibot muna ng mga tao at paghahanap ng mga proyekto sa ibang pagkakataon".
- **Time Buffer:** Magreserba ng 20-30% time buffer para sa bawat yugto. Ang pagpapaunlad ng teknolohiya, pag-aayos ng pag-audit, at mga legal na proseso ay maaaring lahat ay lumampas sa mga inaasahan, at ang roadmap ay hindi dapat maging isang "pinaka-optimistikong senaryo."

**Kaugnayan sa Petsa ng Paglabas ng White Paper (Agosto 4, 2026):** Ang White Paper ay inilabas noong Agosto 2026 bilang pampublikong pahayag ng pananaw at teknikal na disenyo ng proyekto. Ang aktwal na pagpapatupad ay magsisimula sa Q4 ng 2026 (panahon ng paghahanda), at ang target ng TGE ay Q4 ng 2027. Ang humigit-kumulang 14 na buwang agwat sa pagitan ng paglabas ng white paper at ng TGE ay ginamit para sa pagbuo ng team, pagbuo, pag-audit, at paghahanda sa pagsunod.

---

## Kabanata 11: Kultura ng Komunidad at Ekolohiya ng Developer

### 11.1 Apat na Halaga

- **Ang transparency ay mas mahusay kaysa sa pagiging perpekto** - Mas mainam na ibunyag ang mga di-kasakdalan kaysa itago ang pagiging perpekto. Ang lahat ng treasury flow, mga desisyon sa pamumuhunan, at mga boto sa pamamahala ay permanenteng magagamit sa chain.
- **Ang unti-unti ay mas mahusay kaysa sa radikal** - Gumawa ng maliliit na hakbang at patuloy na umulit. Ang unang pamumuhunan ay magsisimula sa $2-5 milyon, at ang sukat ay lalawak pagkatapos ma-verify ang modelo.
- **Ang mga responsibilidad ay mas mahusay kaysa sa mga karapatan** - Ang mga karapatan at obligasyon ay pantay. Ang mga miyembro ng komite ng pamamahala ay dapat mangako ng 50,000 LIGHT at ibunyag ang kanilang agenda sa patakaran. Kung hindi nila magawa ang kanilang mga tungkulin, sila ay pagmumultahin.
- **Ang pagkakaiba-iba ay mas mahusay kaysa sa homogeneity** - Iba't ibang boses ang kaligtasan ng system. Tinitiyak ng two-dimensional na pagboto (coin + address) na parehong may sasabihin ang mga balyena at retail na mamumuhunan.

### 11.2 Sistema ng hurado

| Mga sukat | Mga Panuntunan |
|------|------|
| Komposisyon | Random na pumili ng 12 user na may hawak na ≥10,000 LIGHT at walang mga rekord ng paglabag |
| Termino | 30 araw, ay random na iguguhit muli pagkatapos ng pag-expire |
| Mga Pananagutan | Pakinggan ang mga reklamo laban sa panloloko, mga akusasyon sa pandaraya sa panukala, at mga hindi pagkakaunawaan sa komunidad |
| Proseso | Ang mga pinarusahan na gumagamit ay maaaring magsumite ng ebidensya sa loob ng 72 oras; ang hurado ay dapat gumawa ng hatol sa loob ng 48 oras |
| Mga pamantayan ng paghatol | ≥8 sa 12 tao (2/3 mayorya) ay dapat sumang-ayon na panatilihin o bawiin ang parusa |
| Pag-iwas | Awtomatikong pagpapalit ng mga hurado na may kaugnayan sa imbitasyon sa mga partido o nasa parehong hanay ng IP |
| Kabayaran | Makatanggap ng pang-araw-araw na subsidy sa serbisyo ng hurado na 5 LIGHT sa panahon ng termino (ibinabayad mula sa ecological fund) |

### 11.3 Developer Ecological Plan

| Module | Nilalaman | Mga Pinagmumulan ng Pagpopondo | Paano Mag-apply |
|------|------|---------|---------|
| Pagpopondo ng Developer (Grants) | Para sa mga team na bumubuo ng mga dApp, tool, at imprastraktura sa LightDAO chain, isang grant na $5-500,000 na katumbas ng LIGHT | Ecological Development Fund (Linear Release Phase 2) | Magsumite ng panukala → Pagsusuri ng opisyal ng teknikal na pagsusuri → Pagboto sa pamamahala (proseso ng micro-proposal) |
| SDK at API | Magbigay ng mga interface ng JavaScript/TypeScript SDK, REST API, at WebSocket upang babaan ang threshold para sa pag-develop ng third-party | Ang opisyal ng teknikal na pagsusuri ay nangunguna sa pag-unlad | Open source, pampubliko sa GitHub |
| Hackathon | Ang online hackathon ay ginaganap kada quarter, na may premyong $100,000 na katumbas ng LIGHT | Ecological Development Fund | Buksan ang pagpaparehistro, walang threshold |
| Bug Bounty | Core contract bug bounty program, reward $1,000-$50,000 para sa isang balidong kahinaan (namarkahan ayon sa kalubhaan) | Insurance Fund + Ecological Development Fund | Isumite sa pamamagitan ng Immunefi o self-built platform |
| CosmWasm Contract Market | Hikayatin ang mga third party na mag-deploy ng mga smart contract, at 20% ng kita sa gas fee ay ibabalik sa ecological treasury para suportahan ang mga developer | Pamamahagi ng bayad sa gas (tingnan ang Seksyon 4.5) | Awtomatiko, walang kinakailangang aplikasyon |

### 11.4 Multi-language at localization na diskarte

| Mga sukat | Pagpaplano |
|------|------|
| Wika ng platform | Sa simula ay sumusuporta sa English, Chinese, Spanish, Portuguese, at Filipino; Ang French, Arabic, Swahili, at Indonesian ay idaragdag mula sa ika-6 na buwan |
| Wika ng pamamahala | Ang mga panukala at platform ng kampanya ay tinatanggap sa anumang wika, at ang system ay nagbibigay ng machine translation + community manual proofreading |
| Mga Pagpapatakbo ng Komunidad | Magtatag ng mga independiyenteng channel ng komunidad (Discord/Telegram) ayon sa wika, at ang bawat channel ay nilagyan ng mga localized community liaison volunteer |
| Pagsasalin ng Dokumento | Ang mga puting papel at pangunahing dokumento ay kinukumpleto ng mga boluntaryo sa pagsasalin ng komunidad, at ang mga kontribusyon sa pagsasalin ay kasama sa bonus ng pag-uugali na "Contribution ng Nilalaman" (5%) |
| Pagpopondo sa Lokalisasyon | 10% (40 milyong barya) ng ecological development fund ay partikular na nakalaan para sa localization community building at translation insentibo |

---

## Kabanata 12: Koponan at Mga Consultant

### 12.1 Pangunahing kahulugan ng tungkulin

| Tungkulin | Mga Pananagutan | Mga Kinakailangan sa Background | Mga Paraan ng Pagbubunyag |
|------|------|---------|---------|
| Paunang Tagapangalaga/Sponsor ng Proyekto | I-deploy ang mga paunang kontrata, panatilihin ang mga dokumento, at i-coordinate ang mga maagang operasyon | ≥ 3 taong karanasan sa industriya ng blockchain, na may smart contract deployment o DeFi protocol operation records | Ibunyag ang iyong tunay na pagkakakilanlan bago ang TGE o magbigay ng ulat sa pag-verify ng pagkakakilanlan ng third-party (tulad ng pirma ng notaryo + pag-verify ng on-chain na mensahe) |
| Pinuno ng teknikal | Kontrata disenyo ng arkitektura, development team management, audit docking | Karanasan sa pagbuo ng Cosmos SDK/CosmWasm, record ng deployment ng chain ng produksyon | Pareho sa itaas |
| Tagapangasiwa ng pamumuhunan | Target na screening, koordinasyon ng angkop na pagsisikap, pagtatatag ng SPV, pamamahala sa labasan | Karanasan sa pribadong equity/venture capital na industriya, na may nakumpletong exit cases | Pareho sa itaas |
| Compliance consultant | Disenyo ng legal na istraktura, docking ng regulasyon, payo sa pagsunod sa MLM | Abogado na may mga kwalipikasyon sa US/EU/Cayman | Pangalan ng pampublikong law firm (hindi isisiwalat ang personal na pangalan maliban kung sumasang-ayon ako) |

### 12.2 Advisory Board

- Binubuo ng 3-5 independyenteng consultant, na sumasaklaw sa: teknolohiya ng DePIN, pagsunod sa pamumuhunan sa cross-border, mga operasyon ng komunidad, at mga industriya ng consumer;
- Ang mga consultant ay tumatanggap ng bayad sa pagkonsulta sa anyo ng mga LIGHT token (ibinabahagi mula sa "service exchange para sa mga token" na bahagi ng strategic operating fund) at ikinukulong sa loob ng 12 buwan;
- Ang listahan ng mga consultant ay ginawang pampubliko bago ang TGE at bukas para sa mga katanungan sa komunidad (desentralisadong text inquiry meeting, tingnan ang Seksyon 7.5);
- Maaaring hindi sabay na magsilbi ang mga tagapayo bilang mga miyembro ng Governance Committee (conflict of interest segregation).

### 12.3 Pangako at Paghihigpit ng Koponan

| Mga hadlang | Mga Panuntunan |
|------|------|
| Token Lockup | LIGHT (kabilang ang strategic operating fund allocation) na hawak ng core team ay dapat na naka-lock sa loob ng 12 buwan at linearly na i-release sa loob ng 36 na buwan pagkatapos ng pag-unlock |
| Mga paghihigpit sa pagbebenta | Ang unang tagapag-alaga ay hindi pinapayagang magbenta ng LIGHT na nakuha sa pamamagitan ng anumang channel (kabilang ang mga airdrop, reward, at kompensasyon) sa panahon ng termino ng panunungkulan (≤24 na buwan) |
| Salungatan ng interes | Ang mga salungatan ng interes ng mga miyembro ng koponan ay dapat na ganap na ibunyag sa oras ng appointment (kung sila man ay may hawak na iba pang mga token ng DAO, kung ang mga ito ay nauugnay sa mga potensyal na target sa pamumuhunan) |
| Mga kahihinatnan ng kabiguang ibunyag | Sa sandaling ma-verify ang kabiguan na ibunyag ang isang salungatan ng interes, ikaw ay permanenteng pagbabawalan sa paglahok sa pamamahala, at 50% ng mga naka-unlock na token ay kukumpiskahin sa pondo ng seguro |
| Mekanismo ng pagpapalit | Kapag ang isang pangunahing tungkulin ay umalis o nawalan ng kakayahan, ang komite ng pamamahala (paunang tagapag-alaga + alternatibong tagapag-alaga bago ang pagtatatag) ay magtatalaga ng isang kahalili, na dapat ipahayag sa publiko ng komunidad sa loob ng 72 oras nang walang pagtutol |

### 12.4 Core contributor compensation (20% ng strategic operating fund)

- Kabuuang halaga: 50 milyong LIGHT (nagkabilang ng 2% ng kabuuang halaga)
- Bilang ng mga taong sakop: 3-5 tao
- Mga panuntunan sa pagpapalabas: December cliff + 36 na buwang linear (ibig sabihin, humigit-kumulang 1.157 milyong barya ang ilalabas bawat buwan simula sa ika-13 buwan)
- Milestone binding: Bawat quarter, kinukumpirma ng komite ng pamamahala (unang tagapag-alaga + independiyenteng ikatlong partido bago ang pagtatatag) na ang milestone ay naabot bago maipalabas ang quarterly quota.
- Mga panuntunan sa pagsisiwalat: ang kabuuang halaga at mga panuntunan sa pagpapalabas lamang ang isiwalat, at ang mga personal na pangalan at solong tao na quota ay hindi isiwalat (upang protektahan ang privacy, at sa parehong oras, ang kabuuang halaga ay maaaring ma-verify sa pamamagitan ng multi-signature address sa chain na ang kabuuang halaga ay hindi lalampas)

---

## Kabanata 13: Babala sa Panganib at Disclaimer

### 13.1 Babala sa panganib

| Uri ng panganib | Paglalarawan | Mga hakbang sa pagpapagaan |
|---------|------|---------|
| Panganib sa Market | Ang LIGHT na mga presyo ay maaaring magbago nang malaki, at ang mga makasaysayang presyo ay hindi kumakatawan sa pagganap sa hinaharap. Ang TGE ay may limitadong paunang pagkatubig at ang mga presyo ay maaaring magbago nang marahas | Dutch auction patas na pagpepresyo; ±50% circuit breaker 72 oras pagkatapos ng TGE; anti-death spiral four-level intervention mechanism |
| Mga Panganib sa Proyekto | Ang target na pamumuhunan ay maaaring magdusa ng pagkalugi, ang venture capital na proyekto ay maaaring mabigo, at ang punong-guro ay maaaring mawala nang buo. Ang makasaysayang average na rate ng pagkabigo ng industriya ng PE/VC ay humigit-kumulang 50-70% (iisang deal) | Dual-engine decentralization (70% cash flow + 30% growth); solong target ≤ 25%; industriya ≤ 40%; rehiyon ≤ 30%; 10% na probisyon para sa mga pondo ng insurance |
| Mga teknikal na panganib | Ang mga matalinong kontrata ay maaaring may hindi natuklasang mga kahinaan; ang pagiging tugma ng browser ay maaaring makaapekto sa karanasan sa pagmimina; cross-chain bridges ay maaaring salakayin | Independent audit + pormal na pag-verify bago ang TGE; Bug Bounty $1K-$50K; 72-oras na lock ng oras; multi-signature na mekanismo ng pagsususpinde |
| Mga panganib sa regulasyon | Maaaring magbago ang mga patakaran sa regulasyon sa iba't ibang bansa at rehiyon, na maaaring magresulta sa limitadong mga function o kawalan ng kakayahan para sa mga user sa mga partikular na rehiyon na lumahok | Istraktura ng Cayman SPV; default na zero verification (ang pag-verify ay isinasagawa ng isang lisensyadong third party sa panig ng serbisyo nito); Ang front-end na salamin ng IPFS ay lumalaban sa censorship; hindi ibinebenta sa mga partikular na bansa |
| Panganib sa pagkatubig | Ang sub-token ay maaaring kulang sa sapat na lalim ng kalakalan sa maagang yugto; Maaaring harapin ng LIGHT ang selling pressure sa maagang yugto ng TGE | Ang paunang pagkatubig ng sub-token AMM (6% ng pagpapalabas); 30-araw na panahon ng lock-up ng paglipat; Koponan/mamumuhunan 12-buwang bangin + 36-buwan na linear |
| Panganib sa pagbabanto | Habang dumarami ang bilang ng mga aktibong minero, ang kita ng per capita mining ay natural na mababanaw (tumataas ang BaseReward denominator) | Intensiyon sa disenyo: ang mga naunang kalahok ay nagkakaroon ng mas mataas na panganib upang makakuha ng mas mataas na kita; sa ibang pagkakataon ang mga user ay maaaring mapabilis ang akumulasyon sa pamamagitan ng pagbabahagi ng imbitasyon; ang threshold ng pamamahala ay dynamic na binabaan |
| Panganib sa pagpapatakbo | Ang operasyon at pamamahala ng namuhunan na kumpanya ay maaaring hindi matugunan ang mga inaasahan; Ang mga operasyon ng SPV ay umaasa sa mga third-party na direktor; maaaring mawala ang investment team | Mga paghihigpit sa charter ng SPV + mga independiyenteng direktor; Maaaring bumoto ang DAO upang palitan ang mga direktor; SIAC/ICC arbitration clause; insurance ng pangunahing tao (sa ilalim ng paggalugad) |
| Mga panganib sa cross-chain bridge | Ang wLIGHT cross-chain bridge ay pinatatakbo ng isang third party, at ang mga butas sa kontrata ng tulay ay maaaring humantong sa pagkalugi ng asset (kasaysayan, ang mga cross-chain bridge ay ang pinakamalaking pinagmumulan ng mga pagkalugi) | Independent audit bago mag-online ang tulay; ang mga asset ng tulay ay hindi lalampas sa 5% ng kabuuang supply; pagsisiwalat ng panganib; maaaring piliin ng mga user na gamitin lamang ang katutubong chain |
| Panganib ng validator | Ang mga validator na sama-samang nag-o-offline o gumagawa ng kasamaan ay maaaring magsanhi sa chain na suspindihin ang block production, at lahat ng operasyon ng user (pagmimina, pagboto, paglilipat) ay pansamantalang hindi magagamit | Pinahihintulutan ng Tendermint BFT ang <1/3 kasamaan; mga validator ≥ 21 (f=6); Paglalaslas ng parusa; mekanismo ng pagboto ng emergency migration |

### 13.2 Disclaimer

- Ang LIGHT at sub-token ay hindi mga securities, walang intrinsic na halaga, at ang presyo ay maaaring bumalik sa zero. Ang puting papel na ito ay hindi bumubuo ng anumang anyo ng dokumento ng pagbibigay ng mga securities, alok sa pamumuhunan o payo sa pamumuhunan.
- Ang pamamahagi ng kita ng kasunduan ay nakasalalay sa aktwal na pagganap ng pagpapatakbo ng pinagbabatayan na mga asset, at hindi kumakatawan sa kita sa hinaharap ang makasaysayang data. Ang anumang mga paglalarawan ng mga return ng pamumuhunan ay mga pagtatantya sa hinaharap at hindi mga pangako.
- Dapat tanggapin ng user ang lahat ng pagkalugi na dulot ng pagkawala o pagtagas ng pribadong key, at ang kasunduan ay hindi nagbibigay ng mga serbisyo sa pagkuha. Ang paggamit ng Tier 1 (Passkey) o Tier 2 (Social Recovery) na wallet ay nakakabawas sa panganib na ito, ngunit hindi nito inaalis.
- Ang kasunduang ito ay bukas sa mga user sa buong mundo (napapailalim sa mga naaangkop na batas at regulasyon). Dapat kumpirmahin ng mga user ang legal na saloobin sa mga naka-encrypt na asset, mga organisasyon ng DAO at mga sertipiko ng kita ng SPV sa kanilang mga nasasakupan, at tiyaking legal at sumusunod ang kanilang paglahok.
- Ang mga forward-looking na pahayag sa puting papel na ito (kabilang ang mga roadmap, modelo ng kita, pagtatantya ng deflation, pagtataya sa sukat ng pamumuhunan) ay mga hula batay sa kasalukuyang mga pagpapalagay, at ang mga aktwal na resulta ay maaaring makabuluhang lumihis dahil sa merkado, teknolohiya, regulasyon, pagpapatupad ng koponan at iba pang mga kadahilanan.
- Ang mga insentibo sa imbitasyon ay isang mekanismo ng pagbabahagi sa isang antas at hindi bumubuo ng mga multi-level na marketing o pyramid scheme. Gayunpaman, dapat pa ring kumpirmahin ng mga user ang legal na saloobin sa mga reward sa referral sa kanilang nasasakupan.
- Ang minimum na edad para lumahok sa LightDAO ecosystem ay 18 taong gulang (o ang legal na edad ng mayorya sa iyong hurisdiksyon, alinman ang mas mataas). Ang mga menor de edad ay hindi pinapayagang lumahok sa pagmimina, pamamahala o pamumuhunan.

---

## Appendix A: Talaan ng buod ng mga pangunahing parameter

| Kategorya | Parameter | Halaga |
|------|------|------|
| Pagpapalabas | Kabuuang halaga | 2.5 bilyong piraso, hindi na ipapalabas |
| Pagpapalabas | Pagmimina | 40% = 1 bilyong barya |
| Pagpapalabas | Investment Vault | 34% = 850 milyong barya |
| Pagpapalabas | Ecological Fund | 16% = 400 milyong piraso |
| Pagpapalabas | Mga Madiskarteng Operasyon | 10% = 250 milyong barya (serbisyo 50%/financing 30%/contributors 20%) |
| Pagpapalabas | Halving cycle | Bawat 2 taon |
| Pagpapalabas | First Era Day Release | ≈684,900 (miners 95% = 650,700, validators 5% = 34,200) |
| Pagpapalabas | Reward pool bawat bloke | ≈13.87 ILAW |
| Pagmimina | Bigat ng kontribusyon | Bandwidth 40%/session 30%/verification 20%/stability 10% |
| Pagmimina | Buong bonus | 1.44 beses |
| Imbitasyon | Ebanghelista/Ambassador/Kasosyo | 3 tao 10%+100L/10 tao 15%+500L+5%/50 tao 20%+2500L+10% |
| Pag-uugali | Apat na item × 5% | Pinakamataas na limitasyon 20% |
| Bayad sa gas | Mekanismo ng pagpepresyo | USD katumbas na anchoring, awtomatikong na-convert sa LIGHT na dami ng oracle tuwing 24 na oras |
| Bayad sa gas | Ordinaryong paglipat | katumbas ng $0.001 (@$0.05=0.02 LIGHT) |
| Bayad sa gas | Pagboto sa pamamahala | $0.005 katumbas (@$0.05=0.10 LIGHT) |
| Bayad sa gas | Mga panuntunan sa pamamahagi | 50% pagkasira / 30% validators / 20% ecological treasury |
| Deflation | Slowdown/maagang babala/bottom line | ≤1.5 bilyon/≤1.2 bilyon/≤1 bilyon (dami ng sirkulasyon) |
| Deflation | Teoretikal na itaas na limitasyon | 1.65 bilyon (10+4+2.5, 850 milyon sa treasury ay hindi kailanman ipapaikot) |
| Pamamahala | Limitasyon ng Panukala | ≥5,000 LIGHT + 30 araw ng staking |
| Pamamahala | Committee Staking | 50,000 LIGHT + 100 Address |
| PAMAMAHALA | HURADO | 10,000 ILAW |
| Pamamahala | Pagtaya | 5—500 ILAW |
| Pamamahala | Bonus sa reputasyon | 1 taon +15 boto → +30% (kabuuang cap +40%) |
| Pamumuhunan | Isang limitasyon | Vault na natitira × 15% (initial 127.5 million coins) |
| Pamumuhunan | Baseline deployable | 850 milyon × $0.15 × 75% = $95.63 milyon ≈ $100 milyon |
| Pamumuhunan | Pamamahagi ng kita (taon) | 40/30/20/10 |
| Pamumuhunan | Pamamahagi ng kita (paglabas) | 70/30 |
| Auction | Target | $15 milyon ($5 milyon na reserba + $10 milyon na namuhunan na kapital) |
| Mga reserba | Matatag na Treasury | TGE $5 milyon → Buwan 24 $8 milyon |
| Insurance | Kita | Kita 10% |
| Airdrop | Kabuuang badyet | 55 milyon (ecological fund 13.75%), CAC≈$55/retained user |
| Mga Validator | Inisyal/Cap | 21 (minimum 10) / 100 |
| Validator | Pinakamababang stake | 500,000 ILAW |
| Verifier | TGE hard bottom line | ≥7, kung hindi, hindi ito papayagang mag-online |

---

## Appendix B: Derivation at pagpapatunay ng numero

### B.1 Output ng pagmimina

2A=1 bilyon→A=500 milyon. Pang-araw-araw na pagpapalabas = 500 milyon ÷ 730 = 684,932 ≈ 684,900. Mining pool=684,932×95%=650,685≈650,700. Mga Verifier=684,932×5%=34,247≈34,200. Bawat bloke=684,932÷49,371≈13.87. Pagpapatunay: 684,932×730=499,999,960≈500 milyon ✓

### B.2 Accessibility ng threshold ng pamamahala

100,000 minero benchmark (6.51/day, partner 74.44/day): proposal 5,000→768 days/67 days; komite 50,000→7,684 araw (21 taon)/672 araw (22 buwan); hurado 10,000→1,537 araw (4.2 taon)/134 araw (4.5 buwan); taya 500→77 araw/6.7 araw.

Panahon ng binhi (10,000 minero, 65.07/araw, kasosyo 744.4/araw): panukala → 77 araw (2.5 buwan) / 6.7 araw; komite → 768 araw (25 buwan) / 67 araw (2.2 buwan); hurado → 154 araw (5 buwan) / 13.4 araw.

### B.3 Timeline ng Deflation

Dami ng sirkulasyon = pagmimina + ekolohiya + diskarte (vested) − exchange − Gas − repurchase. 850 milyon sa treasury ay hindi na ipapaikot.

| Taon | Pinagsama-samang Pagmimina | Ekolohiya | Diskarte | Palitan | Gas | Pagbili | Sirkulasyon |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2.50 | 2.80 | 0 | 0 | 0.01 | 0 | ≈5.29 |
| 2 | 5.00 | 4.00 | 0.83 | 0.05 | 0.02 | 0 | ≈9.76 |
| 3 | 6.25 | 4.00 | 1.67 | 0.20 | 0.03 | 0.05 | ≈11.64 |
| 4 | 7.50 | 4.00 | 2.50 | 0.45 | 0.04 | 0.20 | ≈13.31(tugatog) |
| 5 | 8.13 | 4.00 | 2.50 | 0.80 | 0.05 | 0.50 | ≈13.28 |
| 6 | 8.75 | 4.00 | 2.50 | 1.20 | 0.06 | 0.90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2.50 | 1.60 | 0.07 | 1.40 | ≈12.49 |
| 8 | 9.38 | 4.00 | 2.50 | 2.00 | 0.08 | 1.90 | ≈11.89 |
| 9 | 9.53 | 4.00 | 2.50 | 2.40 | 0.09 | 2.30 | ≈11.24 |
| 10 | 9.69 | 4.00 | 2.50 | 2.80 | 0.10 | 2.70 | ≈10.59 |
| 11 | 9.77 | 4.00 | 2.50 | 3.10 | 0.11 | 3.00 | ≈10.06 |
| 12 | 9.84 | 4.00 | 2.50 | 3.40 | 0.12 | 3.30 | ≈9.52 |

Konklusyon: Ang pinakamataas na Y4≈1.331 bilyon; ang linya ng babala na 1.2 bilyon ay hinawakan ng Y8; ang ilalim na linya ng 1 bilyon ay hinawakan ng Y11-12; ang deceleration line na 1.5 bilyon ay isang napakababang senaryo ng pagkawasak.

---

## Appendix C: Log ng pagwawasto ng audit (36 na mga item sa kabuuan)

Naglalaman ng 22 orihinal na item (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 item sa teknikal na arkitektura (T1-7) + 7 item sa pag-optimize ng economic model sa round na ito:

| Numero | Pagwawasto |
|------|------|
| E-1 | Kabuuang halaga 2.1 bilyon → 2.5 bilyon (hinimok ng mga limitasyon sa kapasidad ng pamumuhunan) |
| E-2 | Allocation 50/30/20→40/34/16/10 (10% ng mga bagong strategic operating funds) |
| E-3 | Dutch auction $10 milyon→$15 milyon (inisyal na kapital sa pamumuhunan $5 milyon→$10 milyon) |
| E-4 | Bagong 5.7-section na airdrop growth plan (55 milyong piraso, CAC $55/tao) |
| E-5 | Ang mga verifier ay inilunsad sa mga yugto (Testnet 7→TGE minimum 10/Target 21→Open 100) |
| E-6 | Deflation trigger line adjustment (14/12/10 → 15/12/10, inangkop sa 1.65 bilyong limitasyon ng sirkulasyon) |
| E-7 | Palitan ang lahat ng panlabas na pagsipi ng mga nabe-verify na mapagkukunan (alisin ang mga hindi nabe-verify na papel ng SSRN) |

---

## Appendix D: Mabilis na Index ng Mga Tuntunin

Ang kumpletong paliwanag ng bawat termino ay nakasaad sa [Mga Tuntunin sa Kabanatang ito] na bloke ng komento sa dulo ng kabanata kung saan ito unang lumabas. Inililista ng index na ito ang lahat ng termino at ang kanilang mga kabanata sa pagkakasunud-sunod ng alpabeto para sa mabilis na pag-navigate.

| Terminolohiya | Kahulugan Kabanata |
|------|------------|
| AMM (Automated Market Maker) | Kabanata 4 |
| BFT (Byzantine Fault Tolerance) | Kabanata 4 |
| CAC (Customer Acquisition Cost) | Kabanata 5 |
| CEX (Centralized Exchange) | Kabanata 4 |
| Cosmos SDK | Kabanata 4 |
| CosmWasm | Kabanata 4 |
| DAO (Desentralisadong Autonomous Organization) | Kabanata 2 |
| DCF (Discounted Cash Flow Method) | Kabanata 9 |
| DePIN (Decentralized Physical Infrastructure Network) | Kabanata 2 |
| DEX (Desentralisadong Palitan) | Kabanata 4 |
| EBITDA (mga kita bago ang interes, mga buwis, depreciation at amortization) | Kabanata 9 |
| Bayarin sa Gas | Kabanata 4 |
| IBC (Inter-chain Communication Protocol) | Kabanata 3 |
| IPFS (InterPlanetary File System) | Kabanata 4 |
| KYC (Know Your Customer) | Kabanata 3 |
| LIGHT (katutubong token) | Kabanata 4 |
| LP (Liquidity Provider) | Kabanata 5 |
| Lower Middle Market PE (Downstream Middle Market Private Equity) | Kabanata 2 |
| Puno ng Merkle | Kabanata 4 |
| MiFID II (EU Markets sa Financial Instruments Directive II) | Kabanata 3 |
| MLM (Multi-Level Marketing) | Kabanata 3 |
| PII (Personal na Makikilalang Impormasyon) | Kabanata 3 |
| PoC (Patunay ng Kontribusyon) | Kabanata 4 |
| PoS (Patunay ng Stake) | Kabanata 4 |
| PoW (Katunayan ng Trabaho) | Kabanata 4 |
| Pre-IPO | Kabanata 9 |
| PWA (Progressive Web Application) | Kabanata 4 |
| Reg D / Reg S (Regulation D/S ng U.S. Securities Act) | Kabanata 3 |
| Pag-slash | Kabanata 4 |
| SPV (Special Purpose Vehicle) | Kabanata 2 |
| TGE (Token Generation Event) | Kabanata 5 |
| TWAP (Time Weighted Average na Presyo) | Kabanata 4 |
| TWAP Execution (Repurchase and Split Orders) | Kabanata 9 |
| VWAP (Volume Weighted Average na Presyo) | Kabanata 5 |
| wLIGHT (naka-encapsulated LIGHT) | Kabanata 5 |
| ZK-KYC (Zero-Knowledge Proof KYC) | Kabanata 3 |
| Sub-token | Kabanata 5 |
| Death Spiral | Kabanata 5 |
| Hinahati | Kabanata 5 |
| Treasury (Treasury) | Kabanata 5 |
| Dutch Auction | Kabanata 5 |
| Oracle | Kabanata 4 |

---

**Natapos ang buong puting papel**

**Copyright Statement:** Ang dokumentong ito ay isang open source na dokumento ng komunidad at maaaring malayang kopyahin, ngunit ang kumpletong nilalaman ay dapat na panatilihin.

---

# Appendix: Mga na-verify na parameter at address ng Mainnet (V2.4 live)

## A. §4.5 Mga Parameter na Nasusukat sa Ekonomiya ng Gas
- min-gas-price formula: `(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`; Kasalukuyang TransferUsdTarget=$0.001, UsdPerLight=$0.05, RefTransferGas=100000 → **0.2 ulight/gas**
- Pagsusukat sa pamamahagi (kabuuang bayad 300000 ulight): pagkasira 150000 (50%)/treasury 60000(20%)/verifier 90000(30%), eksaktong tugma
- Destruction address: `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (deterministic dead address)
- Treasury: kontrata ng `treasury_multisig` (3/5 multi-signature; ang query ng `signers` sa chain ay nagbabalik ng 5 signer, ang threshold mismo ay wala sa query interface)

## B. pangunahing address ng kontrata
Tingnan ang repositoryong `docs/MAINNET_STATUS.md` (light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting at iba pang 10 kontrata).

## C. Legacy denom(stake) disposal
genesis mismatch mint_denom=stake ay na-reset sa zero at huminto ang karagdagang pagpapalabas; ang umiiral na stake (humigit-kumulang 2.56e11 micro units) ay iniwang walang layunin, at ang disposal plan (exchange/destroy) ay nakabinbin ang mga panukala sa pamamahala at hindi makakaapekto sa ulight economic model.

## D. §4.4 vesting live
Vault 250,000,000 LIGHT, 3 independiyenteng iskedyul: 75M (cliff 0)/ 100M (cliff 1 taon)/ 75M (cliff 2 taon), nasa chain na.

## E. Mga Kasanayang Pangkaligtasan
- Ang pangunahing network ay na-upgrade sa x/upgrade na pamamahala + mataas na koordinasyon ng lahat ng mga node sa parehong block + auto-swap watchdog, na isinagawa pagkatapos ng end-to-end na rehearsal ng network ng pagsubok
- Ang mga buto ng passkey ay nag-iimbak lamang ng ciphertext; Ang mga shamir shards ay hindi nag-iimbak ng mga ito nang lokal.
- Contract mining root submission threshold 5 (aktwal na measurement threshold=5 para sa bawat `submit_root` event sa chain; kasalukuyang 5 awtorisadong account ang pinipirmahan, at 7 upuan ang target ng disenyo); para sa anti-witch/anti-cheating, tingnan ang §4.8
