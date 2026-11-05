> Traduction automatique, non relue. En cas de divergence, la version chinoise fait foi.
[中文原文 / Chinese original](/whitepaper.md)

# Livre blanc LightDAO V2.4 (2026-09-26 Mainnet Live Version)

> Cette version est basée sur le projet de conception V2.0, avec « déploiement sur le réseau principal en direct » et « modifications de version » devant, et complété par des paramètres vérifiés en chaîne. Le texte principal (chapitres 1 à 12) reste inchangé par rapport à la conception V2.0 ; pour tout écart par rapport à la situation réelle, les notes et annexes précédentes de cette section prévaudront.

## Modifications de version (V2.0 → V2.4)
- 04/11/2026 Errata (ne pas changer le numéro de version, toujours V2.4) : Le coffre-fort d'origine `treasury_multisig` dans l'annexe "Paramètres et adresses vérifiés du réseau principal" est 5/7 multisig, ce qui entre en conflit avec les 3/5 du texte §7.2/§7.3/§8.1, et entre également en conflit avec la mesure réelle sur la chaîne (`{"signers":{}}` renvoie 5 adresses, il n'y a pas 7 signataires) ; il a été unifié à 3/5 selon le texte, et il est indiqué que le seuil lui-même ne se trouve pas dans l'interface de requête de contrat et ne peut être pris en charge que par les enregistrements de déploiement. La racine minière d'origine écrite dans la même section est "5/7 verifier multi-signature", et le test réel ne peut prouver que le seuil de 5 (le seuil de 115 événements `submit_root` est tous de 5, et le nombre réel de comptes signataires est exactement de 5). L'autorisation de 7 sièges est l'objectif de conception, et il n'existe actuellement aucune preuve en chaîne. Le libellé a été modifié en conséquence.

1. **§4.5 Gas 经济:已主网部署并验证**。USD 锚定动态 min-gas-price 与 50% 销毁 / 30% 验证者 / 20% 金库分配于 2026-09-24 经治理提案(v2-lightfee)在高度 58627 上线,7 验证者协调切换、测试网端到端彩排后执行。主网实测:不足额 fee 被拒、足额 fee 按 50/30/20 精确分配。
2. **原生 denom 厘清**:质押/治理/Gas 均为 `ulight`(LIGHT,6 位小数,总供应 25 亿)。genesis 误配的 `stake` 通胀已于 2026-09-24 经治理提案归零(mint inflation=0),LIGHT 发行完全由 mining_reward 合约承担,杜绝双重发行;存量 stake 为待处置的遗留 denom(见附录 C)。
3. **§4.7 WebRTC 中继:已部署**。8 节点 coturn(TURN/STUN,TLS 证书 turn-*.lightdao.net)+ WSS 信令 + REST 临时凭证(HMAC-SHA1);客户端 P2P 数据通道互中继,中继字节计入 40% 带宽贡献;端到端实测经 TURN 中继传输成功。对称 NAT 走 TURN 兜底,失败降级纯验证模式(与 §4.7 一致)。
4. **§4.9 智能钱包:已上线**。Passkey/WebAuthn 无种子登录(PRF 派生密钥 + AES-GCM 密文存储,明文不落地)+ Shamir 3-of-5 社交恢复;助记词作为回退选项保留。
5. **§4.10 价格预言机:喂价已运行**。7 验证者 cron 轮值向 oracle_twap 提交 external_median(当前参考价 50000 = $0.05);链上 TWAP 待 LIGHT/USDC 流动性池建立后启用。v3 升级后 lightfee 直接读 external_median 转动态 min-gas。
6. **参数治理**:v3 升级将 lightfee 的 BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract 迁入链上 paramstore,治理参数提案可运行时调整,无需再协调升级。

## Déploiement du réseau principal en direct (2026-09-26)

- Chaîne `lightdao-mainnet-1`, 7 validateurs (JP/KR/SG/US/HK/FR/UK) sont tous LIÉS, aucun n'est emprisonné ; respecter les critères du §4.7 : « Les vérificateurs < 7 ne sont pas autorisés à effectuer le TGE »
- Client https://lightdao.net (PWA) : Passkey wallet + mining + relais WebRTC + collection, multi-langue (chinois/anglais/espagnol)
- Boucle fermée de minage : Contribution du navigateur → Finalisation quotidienne de la passerelle → La racine Merkle 5 est signée sur la chaîne (seuil 5, peut être vérifié sur la chaîne) → Les mineurs reçoivent une preuve avec preuve ; la racine quotidienne est soumise en permanence
- Gestion des mises à niveau : v2-lightfee (appliqué @58627), zéro zéro (appliqué), v3-lightfee (adopté à l'unanimité, la hauteur 118055 change automatiquement)
- Pour l'historique complet du point de terminaison/de l'adresse du contrat/de la mise à niveau, veuillez consulter l'entrepôt `docs/MAINNET_STATUS.md`

---

# LightDAO 白皮书 V2.0

**Version optimisée pour la vérification et la relecture du texte intégral (client web international · audit numérique · audit tiers · version optimisée pour le modèle économique) **

Date de sortie : 4 août 2026

Principe de base : les navigateurs sont des nœuds, tout le monde peut participer et les bénéfices sont partagés selon des règles

Positionnement juridique : LIGHT et ses sous-tokens se positionnent comme des points de contribution écologiques et des certificats de droits de réclamation de distribution de revenus SPV, et ne sont pas des titres ou des produits financiers ; les attributs juridiques spécifiques sont soumis à des avis juridiques valides dans les juridictions concernées.

> Ce document est une version vérifiée et optimisée du texte intégral du livre blanc et ne constitue pas un conseil en investissement, des documents d'émission de titres, des descriptions de produits financiers ou toute forme d'engagement de garantie de capital. Veuillez consulter des professionnels juridiques, fiscaux et financiers avant de participer.

---

## Table des matières

- Prédéclaration
- Prologue : L'histoire de trois personnes
- Chapitre 1 : La vérité que nous voyons
- Chapitre 2 : La réponse de LightDAO
- Chapitre 3 : Conformité et isolement juridique
- Chapitre 4 : Architecture technique
- Chapitre 5 : Modèle économique des jetons
- Chapitre 6 : Mécanisme de gouvernance
- Chapitre 7 : Contrôles et contrepoids du pouvoir et définition des rôles
- Chapitre 8 : Mécanisme de confiance et de sécurité
- Chapitre 9 : Opérations d'investissement et stratégies de sortie
- Chapitre 10 : Feuille de route
- Chapitre 11 : Culture communautaire et écologie des développeurs
- Chapitre 12 : Équipe et consultants
- Chapitre 13 : Avertissement sur les risques et clause de non-responsabilité
- Annexe A : Tableau récapitulatif des paramètres clés
- Annexe B : Dérivation numérique et vérification
- Annexe C : Journal de correction d'audit
- Annexe D : Index de référence rapide des termes

---

## Résumé exécutif

**Qu'est-ce que LightDAO :** Une organisation autonome décentralisée qui permet aux gens ordinaires du monde entier de participer à de véritables investissements commerciaux et de partager les bénéfices via un navigateur. Les utilisateurs n'ont pas besoin d'acheter une machine minière, d'avoir une formation technique ou d'atteindre le seuil des investisseurs qualifiés - avec juste un navigateur et un peu de temps, les utilisateurs peuvent contribuer aux ressources du réseau pour recevoir des récompenses en jetons LIGHT et participer aux décisions d'investissement par le biais d'un vote de gouvernance.

**Quel problème est résolu :** Les 50 % les plus pauvres de la population mondiale (environ 4 milliards de personnes) ne possèdent que 2 % de la richesse totale (World Inequality Lab, 2026). Les actifs de haute qualité (capital-investissement, capital-risque) sont exclus du seuil d'investisseur qualifié (revenu annuel de 200 000 $/valeur nette de 1 million de dollars). Bien qu'il existe un récit de « participation universelle » dans le domaine des crypto-monnaies, la grande majorité des jetons finissent par revenir à zéro (CoinGecko 2025 : 11,56 millions de jetons sont morts), et le taux de participation à la gouvernance du DAO n'est que d'environ 3 à 12 %.

**Comment le résoudre :** Modèle à double moteur - 70 % des fonds sont investis dans des actifs de consommation rigides au niveau communautaire (moteur de flux de trésorerie) et 30 % sont investis dans une technologie de pointe (moteur de croissance). Les investissements sont exécutés via Cayman SPV et les bénéfices sont distribués selon les règles de la chaîne : 40 % aux détenteurs de sous-jetons, 30 % retournés au coffre-fort pour réinvestissement, 20 % de rachat de LIGHT pour destruction et 10 % attribués aux fonds d'assurance.

**Données de base :**

| Indicateurs | Valeurs |
|------|------|
| Quantité totale de LUMIÈRE | 2,5 milliards, ne seront jamais émis |
| Coffre-fort d'investissement | 850 millions (de base déployable ≈ 100 millions de dollars) |
| Production minière | 1 milliard, réduit de moitié tous les 2 ans |
| Sorti le jour de la Première Ère | ≈684 900 pièces (moyenne 6,51/jour lorsque 100 000 mineurs travaillent) |
| Conclusion pour la déflation | Arrêter définitivement de brûler lorsque la circulation est ≤ 1 milliard (années 11-12 du scénario de base) |
| Seuil de gouvernance | Proposition ≥ 5 000 LIGHT ; Comité ≥ 50 000 LUMIÈRE |
| Pile technologique | SDK Cosmos + PoS Tendermint + CosmWasm + PWA |
| Vérificateurs | Initiale 21 (minimum 10), limite supérieure 100 |
| Financement initial | Vente aux enchères néerlandaise 15 millions de dollars + financement stratégique pré-TGE 2,25 à 3,75 millions de dollars |

**Différenciation :** Actuellement, le seul projet qui combine « l'exploitation Web à seuil zéro » avec « l'investissement conforme d'une entité SPV ». Différent du Pi Network (pas d'utilité pratique), de l'Helium (nécessite plus de 200 $ de matériel) et du DAO traditionnel (gouvernance d'élite à seuil élevé).

**Feuille de route :** Préparation du 4e trimestre 2026 → Développement des 1er et 2e trimestres de 2027 → Test d'audit du 3e trimestre → TGE du 4e trimestre en ligne → Utilisateurs de semences du 1er trimestre de 2028 → Premier investissement des 2e et 3e trimestres → Mise à l'échelle du 4e trimestre.

---

## Prédéclaration

**Ceci n'est pas une proposition d'investissement**

Les « récompenses écologiques » et la « répartition des revenus de l'accord » décrites dans ce livre blanc sont des dispositifs incitatifs générés par le mécanisme endogène de l'accord et ne constituent aucune forme d'émission de titres, de vente de produits financiers, d'engagements de garantie de capital ou de conseil en investissement.

LIGHT et les sous-tokens n'ont aucune valeur intrinsèque et le prix peut revenir à zéro. Avant de participer, veuillez consulter vos propres professionnels juridiques, fiscaux et financiers, et assumer l'entière responsabilité de la conservation des clés privées, de la déclaration fiscale et de la participation.

---

## Prologue : L'histoire de trois personnes

Maria travaille comme livreuse de nourriture à Manille, travaillant 12 heures par jour et gagnant environ 15 000 pesos philippins (environ 270 dollars américains) par mois. Elle voulait investir dans la marque populaire de chaîne de thé au lait voisine, mais l'autre partie lui a dit : « L'investissement minimum commence à 25 000 $ US. Maria n'a pas pu réunir 25 000 dollars.

Kwame dirige un service de covoiturage à Lagos. Il est optimiste quant à la piste de l'intelligence artificielle et souhaite investir dans une petite entreprise de technologie financière. L'institution lui a indiqué : « Le montant minimum de souscription est de 100 000 $ US et la période de blocage est de 5 ans ». Kwame n'a pas pu réunir 100 000 dollars.

Elena est une enseignante à la retraite de São Paulo avec une pension mensuelle d'environ 3 000 réals brésiliens (environ 550 dollars américains). Elle a entendu dire que les enfants de son voisin gagnaient de l’argent en travaillant dans des sociétés blockchain, mais elle ne pouvait pas lire le livre blanc et ne savait pas comment acheter et configurer du matériel minier professionnel.

Tous trois représentent la grande majorité des gens ordinaires à travers le monde : ils ont le jugement et la volonté de participer, mais il leur manque des canaux de participation à bas seuil, transparents et abordables.

LightDAO est conçu pour ces personnes. Avec un appareil connecté à Internet, un navigateur et une petite somme d'argent, vous pouvez participer à une construction écologique ; Grâce à une structure SPV conforme, les utilisateurs ont également la possibilité d'accéder indirectement à la répartition des flux de trésorerie d'entreprises de haute qualité et à la croissance précoce de projets technologiques de pointe.

---

## Chapitre 1 : La vérité que nous voyons

### 1.1 Répartition déséquilibrée de la richesse mondiale

Selon le World Inequality Report 2026 (ci-après dénommé le « Rapport ») du World Inequality Lab :

| Données | Source |
|------|------|
| La richesse détenue par les 0,001 % les plus riches de la population mondiale (environ 60 000 personnes) représente environ trois fois la richesse combinée des 50 % les plus pauvres de la population (environ 4 milliards de personnes) | Laboratoire mondial sur les inégalités, 2026 |
| Les 1 % les plus riches de la population mondiale contrôlent 23 % du revenu total et 38 % de la richesse totale | Laboratoire mondial sur les inégalités, 2026 |
| Les 10 % les plus riches de la population mondiale contrôlent 53 % du revenu total et 75 % de la richesse totale | Laboratoire mondial sur les inégalités, 2026 |
| Les 50 % les plus pauvres de la population mondiale ne reçoivent que 8 % du revenu total et 2 % de la richesse totale | Laboratoire mondial sur les inégalités, 2026 |

Le « Rapport » souligne : « Les inégalités mondiales restent à des niveaux historiquement extrêmes. Les inégalités ne résultent pas seulement du fonctionnement naturel du marché, mais reflètent des choix politiques, des structures institutionnelles et la répartition inégale du pouvoir économique et politique.

**Note source :** Les données ci-dessus sont tirées du World Inequality Report 2026 du World Inequality Lab. Le rapport a été dirigé par Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif et Thomas Piketty (confirmé par le site officiel wid.world). Avant la publication officielle, il est recommandé de marquer davantage les numéros de graphiques spécifiques dans le rapport afin de réduire les erreurs possibles dans la traduction secondaire.

**Contrôle de cohérence des données :** Les proportions ci-dessus poursuivent une tendance raisonnable avec la conclusion du Rapport sur les inégalités mondiales 2022 (les 10 % les plus riches possèdent 76 % de la richesse totale, les 50 % les plus pauvres possèdent 2 % de la richesse totale), et l'écart se situe dans la fourchette statistiquement acceptable.

### 1.2 Les gens ordinaires sont exclus des actifs de haute qualité

Les principales juridictions mondiales ont des seuils stricts d’investisseurs qualifiés pour le capital-investissement et le capital-risque :

**États-Unis (Règlement SEC D, Règle 501, 17 CFR §230.501) :** Les investisseurs qualifiés (Investisseurs accrédités) doivent remplir l'une des conditions suivantes : le revenu annuel d'un individu n'est pas inférieur à 200 000 USD (ou un total d'au moins 300 000 USD avec un conjoint) et a satisfait à la norme pendant deux années consécutives ; ou la valeur nette (hors résidence principale) n'est pas inférieure à 1 000 000 $ US.

**UE (MiFID II, 2014/65/UE, Annexe II) :** Les investisseurs professionnels (Investisseurs professionnels) doivent remplir au moins deux des conditions suivantes : - un portefeuille d'investissement en instruments financiers d'au moins 500 000 euros ; occuper un poste professionnel dans le secteur financier depuis au moins un an ; exécuter des transactions à grande échelle au moins 10 par trimestre.

**Pratique mondiale des fonds de capital-investissement :** Le montant minimum de souscription pour un seul fonds est généralement compris entre 250 000 USD et 1 000 000 USD ; les règles réglementaires interdisent généralement les comportements évasifs tels que « le fractionnement d'actions, l'abaissement de seuils et la détention d'ordres pour le compte d'autrui ».

| Types d'actifs | Les gens ordinaires peuvent-ils participer | Principales raisons |
|--------------|---------------|--------------|
| Participations dans des sociétés non cotées de qualité | Généralement ne peut pas | Le seuil pour les investisseurs qualifiés est plus élevé, par exemple, les États-Unis exigent une valeur nette d'au moins 1 million de dollars américains ou un revenu annuel d'au moins 200 000 dollars américains |
| Capital-risque (entreprises technologiques en démarrage) | Généralement pas | Principalement ouvert aux investisseurs qualifiés, le montant d'investissement d'un seul fonds n'est généralement pas inférieur à 250 000 $ US |
| Actions de sociétés cotées | Oui, mais les premiers bénéfices ont généralement été captés par les acteurs du marché primaire | Les prix du marché secondaire incluent généralement les attentes futures et les investisseurs ne participent pas directement à la distribution précoce des bénéfices de l'entreprise |

### 1.3 Trois failles majeures dans le domaine des cryptomonnaies

**Défaut 1 : taux d'échec extrêmement élevé**

Selon le rapport statistique annuel 2025 de CoinGecko, environ **11,56 millions de jetons** reviendront à zéro ou cesseront d'être négociés rien qu'en 2025 (y compris les jetons à longue traîne sur chaque chaîne). Sur les plus de 20 millions de jetons suivis historiquement par CoinGecko, la grande majorité sont dans un état « mort » (aucun volume de transactions, aucune activité de développement et les prix ont chuté de plus de 99 % par rapport aux sommets historiques).

Dans le même temps, le taux d’échec des marchés boursiers traditionnels est bien inférieur à celui des crypto-monnaies. Selon l'article de Bessembinder (2018) « Les actions surpassent-elles les bons du Trésor ? publiée dans le "Journal of Financial Economics", une étude de toutes les actions américaines de 1926 à 2016 :

| Métriques | Données | Sources |
|------|------|------|
| Proportion d'actions qui créent la richesse nette totale | Seulement environ 4% (1 092 titres) | Bessembinder (2018), JFE 129(3):440-475 |
| Rendement médian des actions sur la durée de vie | Négatif (sous-performe les bons du Trésor) | Bessembinder (2018), JFE |
| Environ 58 % de la performance sur toute la durée de vie des actions américaines | Bons du Trésor sous-performés sur la même période | Bessembinder (2018), JFE |
| Nombre de jetons à remettre à zéro/stop trading en 2025 | ≈11,56 millions | Rapport annuel CoinGecko 2025 |

**Conclusion comparative :** Le taux de perte en capital permanente dans l'espace des crypto-monnaies est beaucoup plus élevé que sur le marché boursier traditionnel. Bien qu'environ 58 % des actions individuelles du marché boursier américain sous-performent les obligations du Trésor, les investisseurs peuvent toujours obtenir des rendements moyens du marché grâce aux fonds indiciels ; sur le marché des cryptomonnaies, la grande majorité des tokens finissent par revenir à zéro, et il y a un manque d'outils de diversification efficaces similaires aux « indices ».

**Déclaration source :** Bessembinder, H. (2018). « Les actions surpassent-elles les bons du Trésor ? *Journal of Financial Economics*, 129(3), 440-475. Université d'État de l'Arizona. Cet article est un document très cité dans le domaine de la finance (citations >2 000), et les données couvrent toutes les actions américaines de la base de données CRSP de 1926 à 2016. Les données de CoinGecko proviennent de son rapport statistique sur le statut de survie des jetons 2025 (publié en janvier 2026), qui a été rapporté par de nombreux médias financiers (Sina Finance, Phemex, RBC Crypto).

**Défaut n°2 : le minage est hautement centralisé**

Le minage de Bitcoin a montré un haut degré de concentration :

| Piscine minière | Taux de hachage |
|------|--------------|
| Fonderie États-Unis | Environ 30% |
| AntPool | Environ 19% |
| ViaBTC | Environ 14,5% |
| F2Pool | Environ 10% |
| Piscine MARA | Environ 5% |
| Les deux principaux pools miniers combinés | Plus de 50% |
| Les quatre principaux pools miniers combinés | Environ 75% |

**Remarque sur la source :** Les données ci-dessus sont compilées à partir du rapport mensuel sur la distribution du hashrate de 2025 (CoinGradient 2025.3 « Foundry, Antpool et Viabtc Dominate Bitcoin Mining » ; HashrateIndex « Top 10 Bitcoin Mining Pools of 2025 »). Les valeurs spécifiques provenant de différentes sources de données peuvent varier légèrement (généralement dans une fourchette de ± 2 %), mais la conclusion selon laquelle « les quatre principaux pools miniers contrôlent environ 75 % de la puissance de calcul » se reflète dans plusieurs plates-formes de surveillance grand public.

**Défaut 3 : le taux de participation à la gouvernance du DAO est extrêmement faible**

| Données | Source |
|------|------|
| Le taux de participation au vote de la plupart des DAO n'est que d'environ 3 à 12 % (la médiane est d'environ 6 %) | DeepDAO (2025) Agrégation de données de gouvernance en chaîne ; Rapport sur la gouvernance du Boardroom DAO (2024) |
| Un petit nombre de détenteurs de devises contrôlent la grande majorité des droits de vote (forte concentration du pouvoir de gouvernance) | ACM (2024) « Gouvernance DAO : pouvoir de vote, participation et controverse » DOI:10.1145/3777416 |

### 1.4 Informations principales

J'ai du jugement, mais pas de ticket d'entrée ; J'ai une vision, mais pas le droit de parler ; Je veux participer, mais je suis bloqué par des seuils élevés.

---

## Chapitre 2 : La réponse de LightDAO

### 2.1 Positionnement central

LightDAO est une organisation nationale autonome en matière d'investissement avec une gouvernance en chaîne comme noyau et un SPV de conformité comme support d'exécution des investissements. Grâce à une chaîne publique conçue spécifiquement pour les nœuds Web légers, les utilisateurs du monde entier peuvent participer à la maintenance du réseau, au vote de gouvernance et partager les avantages écologiques selon des règles avec un seul navigateur.

### 2.2 Modèle à double moteur

| Moteur | Direction des investissements | Cible | Caractéristiques du revenu |
|------|---------|------|---------|
| Moteur un : moteur de flux de trésorerie (Shou) | Actifs de services de consommation rigides au niveau communautaire | Générez un flux de trésorerie continu et distribuez les bénéfices selon les règles | Rechercher une stabilité relative, mais ne pas promettre des titres à revenu fixe |
| Moteur 2 : Moteur de croissance (attaque) | Entreprises de technologie de pointe | Obtenez une appréciation des actions et des rendements de sortie | Flexibilité potentielle élevée, mais risque également de subir des pertes ou un échec de sortie |

**Discipline d'allocation :** En principe, allouer 70 % des fonds à des actifs à flux de trésorerie stables et 30 % à des objectifs à forte croissance.

**Chemin de croissance à l'échelle de l'investissement :** La taille d'un investissement unique augmente de manière dynamique avec le prix de LIGHT et la capacité du coffre-fort - la période de démarrage (LIGHT 0,02 $ à 0,05 $) convient aux petits actifs au niveau communautaire de 2,55 millions de dollars à 6,37 millions de dollars ; la phase de croissance (0,05 $ à 0,30 $) entre dans les chaînes régionales et les tours de table Seed-A de 6,37 millions de dollars à 38,25 millions de dollars (référence PE du marché intermédiaire inférieur) ; au stade de maturité (0,30 $ - 1,00 $), il atteint le niveau de PE du marché intermédiaire de 38,25 millions de dollars à 127,5 millions de dollars ; au stade de l'échelle (1,00 $+), il peut réaliser des acquisitions à grande échelle et des investissements pré-IPO de plus de 127,5 millions de dollars. Contraintes strictes : une seule transaction ne doit pas dépasser 15 % du montant restant de la trésorerie d'investissement (voir chapitre 9 pour plus de détails).

**Le premier principe de positionnement cible :** Au lieu de présupposer un nom d'entreprise spécifique, établissez d'abord un cadre de sélection : donnez la priorité aux actifs de services aux consommateurs rigides au niveau communautaire, qui nécessitent un modèle économique éprouvé à magasin unique, des flux de trésorerie stables (la marge d'EBITDA au cours des trois dernières années n'est pas inférieure à 10 % et la volatilité interannuelle n'est pas supérieure à 15 %) et une voie d'expansion régionale claire. La cible spécifique est déterminée par les propositions de la communauté.

### 2.3 Proposition de valeur fondamentale

**Le navigateur est le nœud** - Pas besoin d'acheter une machine minière ou d'avoir une formation technique professionnelle. Vous pouvez participer aux contributions du réseau en visitant la plateforme web officielle.

**Tout le monde peut participer** - Après avoir atteint le seuil de gouvernance, les détenteurs de petites quantités de LIGHT peuvent également participer au vote pour décider conjointement de l'orientation de l'allocation des fonds.

**Partage des bénéfices selon les règles** - Les bénéfices d'exploitation des entreprises investies et les rendements de sortie des projets technologiques seront distribués conformément aux règles en chaîne et aux accords SPV.

### 2.4 Slogan

"Votre navigateur peut également être la passerelle vers des ressources de haute qualité."

### 2.5 Analyse de différenciation des produits concurrentiels

| Dimensions | Réseau Pi | Hélium | DAO traditionnel (MakerDAO, etc.) | LumièreDAO |
|------|-----------|--------|---------------|----------|
| Mode de participation | Cliquez sur l'application mobile | Acheter un point d'accès matériel (200 $ à 1 000 $) | Achat de jeton + opération en chaîne | Accès par navigateur, aucun coût matériel |
| Coût d'entrée | Zéro (mais aucune utilité pratique) | Élevé (matériel + installation) | Moyen à élevé (nécessite d'acheter des jetons de gouvernance) | Zéro (juste un navigateur) |
| Montant total de jetons | 100 milliards | 223 millions | Varie | 2,5 milliards |
| Fonction d'investissement réelle | Aucun | Aucun (uniquement couverture réseau) | Oui (mais le seuil est extrêmement élevé) | Oui (structure SPV, tout le monde peut participer) |
| Source de revenus | Peu clair | Frais d'utilisation du réseau | Frais d'accord | Bénéfice de l'entreprise + rendement de sortie + frais de gaz |
| Isolement juridique | Aucun | Aucun | Certains oui | Caïman SPV+ZK-KYC |
| Taux de participation à la gouvernance | Extrêmement faible (pas de gouvernance substantielle) | Faible | Environ 6% | Cible >15 % (vote bidimensionnel + incitations) |

**La principale différence de LightDAO :** Il s'agit actuellement du seul projet qui combine "l'exploration de sites Web à seuil zéro" avec un "investissement d'entité SPV conforme". Les utilisateurs contribuent non seulement aux ressources du réseau pour obtenir des récompenses symboliques, mais participent également directement aux décisions d'investissement réelles de l'entreprise par le biais de votes de gouvernance et de partage des bénéfices d'exploitation.

> **[Terminologie dans ce chapitre]**
> **DAO** (Decentralized Autonomous Organization) : Une forme organisationnelle dans laquelle les règles de gouvernance sont codées via des contrats intelligents et les décisions collectives sont prises par les détenteurs de jetons. Il n’y a pas de hiérarchie traditionnelle dans l’entreprise.
> **SPV** (Special Purpose Vehicle) : une entité juridique indépendante (généralement enregistrée aux îles Caïmans) créée pour des transactions ou des investissements spécifiques afin d'isoler les risques - les dettes et les responsabilités juridiques du SPV ne sont pas transmises au DAO lui-même.
> **DePIN** (Decentralized Physical Infrastructure Network, réseau d'infrastructure physique décentralisé) : modèle de réseau qui utilise des jetons pour encourager les utilisateurs à contribuer aux ressources physiques (bande passante, stockage, puissance de calcul, couverture sans fil, etc.) pour construire l'infrastructure.
> **Lower Middle Market PE** (downstream mid-end private equity) : segment de marché du secteur mondial du private equity. La taille d'une seule transaction est généralement comprise entre 10 et 100 millions de dollars, et l'EBITDA de la société cible se situe entre 2 et 15 millions de dollars.

---

## Chapitre 3 : Conformité et isolement juridique

### 3.1 Couche d'isolement juridique SPV

DAO ne détient directement des capitaux propres dans aucune entreprise physique. Tous les investissements externes sont exécutés par l'intermédiaire de véhicules à vocation spéciale (SPV) établis aux îles Caïmans.

| Points de conception | Descriptif |
|---------|------|
| Charte SPV | Il est clairement convenu que le fonctionnement du SPV devra être conforme à la résolution effective du DAO |
| Définition légale des sous-jetons | Les sous-jetons sont des « certificats de droits de réclamation de distribution de revenus SPV », qui représentent uniquement les qualifications de distribution pour les flux de trésorerie futurs |
| Ne confère pas de droits d'actionnaire | Ne comporte pas de droits de gouvernance d'entreprise, de préférences de liquidation ou de droits d'actionnaire |
| Directeurs de SPV | sont servis par des tiers indépendants ; DAO peut remplacer les administrateurs en adoptant une résolution valide |
| Surveillance des fonds | Les comptes bancaires sont supervisés par des institutions de conservation agréées et les transferts de fonds doivent passer une vérification de signature multiple et de conformité |
| Résolution des litiges SPV | La charte du SPV prévoit une clause d'arbitrage (SIAC ou ICC), et le DAO peut engager une procédure d'arbitrage par le biais d'une résolution de gouvernance |

### 3.2 Vérification facultative et protection de la vie privée

**Aucune pièce d'identité n'est requise pour participer au protocole lui-même. ** Visitez des pages Web, créez des portefeuilles, contribuez aux ressources, recevez LIGHT, lancez et participez au vote de gouvernance - il n'est pas nécessaire de télécharger des documents pendant tout le processus et aucune information personnelle identifiable (PII) n'est stockée sur la chaîne.

Ce n'est que lorsqu'un utilisateur utilise activement un service tiers réglementé que la vérification que le service lui-même doit fonctionner conformément à la loi entre en jeu. Cette vérification est collectée, entreprise et conservée par le prestataire de service. LightDAO ne collecte, ne transfère ni ne stocke aucune donnée :

| Scénario | Qui effectue la vérification | Ce que l'utilisateur doit faire |
|---|---|---|
| Acheter/vendre via les canaux fiduciaires | Tiers agréés (tels que MoonPay, Ramp Network, Transak) | Compléter le processus de conformité selon les propres exigences du prestataire |
| Sous-jetons d'échange (certificats d'actions d'investissement) | En fonction des exigences du produit spécifique et de son prestataire de services | Vous ne pouvez faire que du minage et de la gouvernance, sans aucune vérification |
| Retrait sur carte bancaire/paiement local | Prestataire de services de retrait et de paiement | Compléter le processus de conformité tel que requis par le fournisseur de services |

Principes fondamentaux : **Zéro vérification par défaut ; la vérification n'a lieu qu'au moment où l'utilisateur accède activement au service réglementé et est à la charge du prestataire de services. **Personne ne perdra le droit d'exploiter, de détenir, de transférer ou de voter en raison d'un « défaut de vérification ».

> Technologie réservée : Si un certain type d'actif nécessite à l'avenir un seuil de qualification, l'utilisateur détiendra le certificat sous forme de preuve de connaissance zéro (ZK), et la chaîne vérifiera uniquement "si il est atteint" sans aucune information d'identité - cela fait partie de la feuille de route et n'est pas une exigence actuelle.

### 3.3 Déclaration de responsabilité fiscale

L'accord ne prévoit pas de services de déclaration fiscale et les obligations fiscales de toutes les récompenses écologiques et revenus associés sont supportées par les utilisateurs eux-mêmes. Les utilisateurs doivent respecter les lois et réglementations en vigueur en vigueur dans leur lieu de résidence fiscale.

### 3.4 Accès utilisateurs : ouvert à tous

**Aucun seuil d'inscription et de participation** : Aucun e-mail, numéro de téléphone portable, compte social ou preuve d'identité n'est requis ; un appareil capable d’ouvrir une page Web est tout ce dont vous avez besoin. LightDAO ** ne restreint pas activement la participation des utilisateurs dans aucun pays ou région, et ne déploie pas non plus de géorepérage. **

Les seules contraintes externes proviennent des services tiers : si la loi d'un certain endroit impose d'autres exigences pour des services spécifiques (tels que les dépôts et les retraits en monnaie fiduciaire), ces services seront fournis par des institutions locales agréées conformément à la loi de leur côté et n'affecteront pas l'utilisation par quiconque des fonctions en chaîne (mining, détention, transferts, vote, propositions).

Si une certaine juridiction émet des réglementations prohibitives explicites à l’avenir, la séquence de réponse du protocole est la suivante :

1. Premièrement, assurez-vous que les droits de disposition des actifs des utilisateurs existants ne sont pas affectés : les actifs de la chaîne ne peuvent pas être gelés et n'importe qui peut transférer son LIGHT et ses sous-jetons à tout moment ;
2. Rester accessible via plusieurs portails frontaux (y compris les miroirs IPFS et les miroirs communautaires) ;
3. La dernière étape consiste à ajuster la portée disponible des **services tiers** dans le cadre de l'application de la loi.

En un mot : les restrictions *** ne peuvent concerner que les services, pas les personnes. **

### 3.5 Dépôts et retraits en devises légales et canaux inter-chaînes

**Canal de devises Fiat (agrégation de services tiers) :** Le protocole lui-même n'exploite pas de services légaux de dépôt et de retrait de devises, mais la plateforme Web intègre des canaux tiers conformes (MoonPay, Ramp Network, Transak, etc.), couvrant les principaux marchés d'Amérique du Nord, d'Europe, d'Asie du Sud-Est et d'Amérique latine ; l'agrégation locale du marché P2P couvre l'Afrique et l'Asie du Sud ; les retraits prennent en charge les méthodes de paiement locales telles que GCash, M-Pesa, Pix et GrabPay.

**Pont inter-chaînes et canaux d'acquisition LIGHT :** Transactions AMM intégrées dans la chaîne LightDAO après TGE ; l'interopérabilité avec l'écosystème Cosmos via IBC ; planification de wLIGHT (Ethereum/Solana) à partir du 6ème mois ; demande de cotation CEX à partir du 6ème mois selon conformité. Le pont inter-chaînes est exploité par un tiers indépendant et un rapport d'audit indépendant est requis avant la mise en ligne du pont.

### 3.6 Déclaration de conformité du mécanisme d'invitation (analyse anti-MLM)

L'incitation à l'invitation de LightDAO est un **partage monocouche** (seuls les inviteurs directs reçoivent une proportion fixe des récompenses minières de l'invité) et n'a pas les fonctionnalités de base du marketing multi-niveaux (MLM) : pas de commission récursive multi-niveaux ; les revenus proviennent de la libération de jetons prédéfinis dans le protocole plutôt que du principal du nouveau venu ; il n'y a aucun coût ni aucun frais d'entrée pour participer à l'exploitation minière. Cette structure est plus proche des « récompenses de recommandation des contributeurs de projets open source ». Avant l'opération formelle, un avocat agréé sur le marché cible sera engagé pour émettre des avis de conformité spéciaux.

> **[Terminologie dans ce chapitre]**
> **KYC** (Know Your Customer, Know Your Customer) : processus de conformité permettant aux institutions financières de vérifier l'identité des utilisateurs, nécessitant généralement la présentation de pièces d'identité, d'un justificatif de domicile, etc.
> **ZK-KYC** (Zero-Knowledge KYC, zero-knowledge proof KYC) : les utilisateurs n'ont pas besoin de divulguer d'informations personnelles spécifiques dans le cadre de l'accord et n'utilisent la cryptographie que pour prouver "Je remplis certaines conditions" (telles que l'âge ≥ 18 ans, la nationalité non sanctionnée) méthode de vérification de la conformité. Aucune donnée du document original n'est stockée sur la chaîne.
> **PII** (Personally Identifiable Information, Personally Identifiable Information) : Données permettant d'identifier une personne physique spécifique individuellement ou en combinaison, telles que le nom, le numéro d'identification, l'adresse, les caractéristiques biométriques, etc.
> **Reg D / Reg S** (Regulation D/Regulation S du U.S. Securities Act) : Reg D autorise les placements privés auprès d'« investisseurs qualifiés » aux États-Unis sans enregistrement public (norme de définition de la Règle 501) ; Reg S autorise la vente de titres à des personnes en dehors des États-Unis sans déclencher les exigences d'enregistrement américaines.
> **MiFID II** (Directive européenne sur les marchés d'instruments financiers II, 2014/65/UE) : ​​cadre de régulation financière de l'UE, son Annexe II définit les critères d'identification des « investisseurs professionnels » (500 K€ de portefeuille d'instruments financiers, 1 an d'expérience dans le secteur financier, 10 transactions à grande échelle par trimestre, répondant à la deuxième exigence).
> **MLM** (Multi-Level Marketing, multi-level marketing) : un business model à travers des commissions récursives multi-niveaux (développement downline, développement downline et commissions upline couche par couche). C'est fondamentalement différent des récompenses de recommandation à une seule couche - LightDAO n'est qu'à une seule couche (A invite B, A obtient une part de B ; B invite C, A n'obtient aucune part de C).
> **IBC** (Inter-Blockchain Communication, cross-chain communication protocol) : le standard cross-chain natif de l'écosystème Cosmos, permettant le transfert sécurisé d'actifs et de messages entre différentes blockchains sans avoir besoin d'un intermédiaire centralisé.

---

## Chapitre 4 : Architecture technique

### 4.1 Qu'est-ce que la chaîne publique ?

La chaîne publique de LightDAO peut être comprise comme un « livre de comptes public avec des règles transparentes et ne peut être falsifié à volonté » : les règles de gouvernance sont écrites dans le code, et les dossiers de vote, les flux de capitaux et la répartition des bénéfices de chacun peuvent être interrogés et vérifiés sur la chaîne.

### 4.2 Paramètres techniques et démonstration de sélection

| Articles techniques | Sélection | Base de sélection |
|--------|------|---------|
| Cadre sous-jacent | SDK Cosmos | Architecture modulaire, vérification de plusieurs chaînes de production |
| Mécanisme de consensus | PoS à la menthe tendre | Certitude instantanée ; la génération de blocs prend 1,5 à 2 secondes ; Tolérance aux pannes BFT ≤ 1/3 mal |
| Contrats intelligents | CosmWasm | WebAssembly + Rust, sécurité de la mémoire au moment de la compilation |
| Capacités inter-chaînes | Protocole IBC | Norme inter-chaînes native de Cosmos |
| Interaction frontale | Application Web progressive (PWA) | Navigateur en cours d'exécution, adaptatif ordinateur/mobile, aucune installation requise |

### 4.3 Mécanisme léger d'exploration de nœuds et modèle d'incitation

#### 4.3.1 Méthode de minage

Les utilisateurs accèdent à la plateforme Web officielle via un navigateur, créent un portefeuille et cliquent sur « Démarrer le minage ». Pendant le processus d'exploration de données, les utilisateurs contribuent à la bande passante du réseau (relais et vérification des données) et aux ressources informatiques locales (vérification légère des en-têtes de bloc) via le navigateur, et ne dépendent pas d'une puissance de calcul à haute énergie.

**Mise en œuvre de la technologie côté Web :** Relais P2P du canal de données WebRTC ; Vérification de l'en-tête du bloc en arrière-plan de Web Worker ; Cache hors ligne et battement de cœur de Service Worker ; Longue connexion WebSocket.

**Adaptation du navigateur mobile :** Adopter un système de sessions cumulées valides (4 heures par jour = score de 100 %) ; aucun point ne sera déduit pour la reconnexion dans les 5 minutes suivant la déconnexion ; Les utilisateurs installés par PWA recevront un bonus de temps en ligne supplémentaire de 10 % ; mécanisme délégué en ligne (70% pour le délégué/30% pour le nœud relais).

#### 4.3.2—4.3.3 Programme d'incitation et modèle trimoteur

Il adopte le modèle à trois moteurs « preuve de contribution PoC + incitation à la fission d'invitation + incitation à bonus comportemental ».

#### 4.3.4 Dimensions et poids de la contribution

| Dimension contributive | Poids | Méthode de mesure |
|---------|------|---------|
| Contribution au relais de bande passante | 40% | Rapport entre le trafic de relais de téléchargement et le volume de données de vérification |
| Durée effective de la session | 30% | Séances efficaces cumulées quotidiennes (4 heures = 100%) |
| Bloquer la contribution à la vérification | 20% | Nombre et précision des en-têtes de bloc effectivement vérifiés |
| Stabilité du réseau | 10% | Délai de connexion, taux de perte de paquets, temps de réponse |

#### 4.3.5 Formule de calcul des récompenses

**Récompense minière quotidienne = BaseReward × Score de poids de contribution × (1 + Bonus d'invitation) × (1 + Bonus de comportement)**

- BaseReward = Montant total libéré par l'ensemble du réseau ce jour-là ÷ Nombre total de mineurs actifs ce jour-là
- Bonus d'invitation = nombre effectif d'invités × 1% (limite supérieure 20%)
- Bonus de comportement = 5 % de participation au vote + 5 % de contribution au contenu + 5 % d'activité communautaire + 5 % de qualité de vérification des nœuds (limite supérieure de 20 %)
- Coefficient de bonus complet = (1+20%) × (1+20%) = 1,44 fois

#### 4.3.6 Inviter des incitations à la fission

| Niveau | Nombre d'invitations valide | Ratio de partage des invitations | Récompense unique supplémentaire | Bonus de pondération de gouvernance |
|------|------------|------------|--------------|------------|
| Mineurs | 0 personnes | — | Récompenses minières de base | Aucun |
| Prédicateur | Pas moins de 3 personnes | 10% | 100 LUMIÈRE | Aucun |
| Ambassadeur | Pas moins de 10 personnes | 15% | 500 LIGHT + badge sur chaîne | Poids des votes +5% |
| Partenaires | Pas moins de 50 personnes | 20% | 2 500 LIGHT + badge en chaîne | Poids des votes +10% |

Le bonus de pondération de gouvernance et le bonus de réputation (jusqu'à +30 %) sont cumulés indépendamment, avec une limite supérieure totale de +40 %. Le bonus d'invitation atteint son maximum lorsqu'il y a 20 personnes (20×1%=20%).

#### 4.3.7 Mécanisme anti-triche

Détection de l'intégrité de l'environnement du navigateur (empreinte digitale Canvas/WebGL/WebRTC), détection de la profondeur des paquets, clustering IP et analyse des modèles de comportement, empreinte comportementale multidimensionnelle (trajectoire de la souris/rythme du clavier/comportement de défilement), vérification de l'authenticité de l'adresse d'invitation. Coût de l’attaque anti-Sybil : 50 000 $ à 200 000 $ pour créer 10 000 empreintes digitales indépendantes ; taux de détection cible > 90 à 95 %.

### 4.4 Matrice de fonction du jeton LIGHT

Carburant de réseau (frais de gaz), droits de gouvernance (vote/proposition/campagne), engagement de engagement (marge/campagne/vérificateur), échange d'investissement (sous-jetons), incitations écologiques (exploitation minière/invitation/comportement), expansion future (dApp/NFT/cross-chain).

### 4.5 Mécanisme de frais de gaz et de frais de transaction

**Principe de conception :** Les frais de gaz sont ancrés avec l'équivalent en USD, et le montant réel de LIGHT facturé est automatiquement converti toutes les 24 heures par l'oracle en chaîne (Section 4.10). Cela garantit que, peu importe si le prix de LIGHT augmente ou diminue, le coût de paiement réel de l'utilisateur (en dollars américains) reste stable, évitant ainsi le problème du « le prix de la devise augmente de 100 fois → les frais de transfert deviennent 10 $ » ou « le prix de la devise baisse de 90 % → échange de billets sans frais".

**Objectif des frais de gaz ancrés en USD :**

| Type d'opération | Objectif équivalent en USD | Véritable collection lorsque LIGHT=$0.05 | Véritable collection lorsque LIGHT=$0.50 | Intention de conception |
|---------|------------|--------|------------------|--------------|
| Virement ordinaire | 0,001 $ | 0,02 LUMIÈRE | 0,002 LUMIÈRE | Seuil extrêmement bas pour garantir que les utilisateurs de petits montants puissent transférer de l'argent librement |
| Vote sur la gouvernance | 0,005 $ | 0,10 LUMIÈRE | 0,01 LUMIÈRE | Légèrement supérieur au transfert pour éviter un brossage des votes sans coût |
| Soumettre une proposition | 0,10 $ | 2.0 LUMIÈRE | 0.2 LUMIÈRE | Coopérer avec le système de caution pour augmenter le sérieux de la proposition |
| Échange de sous-jetons | 0,50 $ | 10.0 LUMIÈRE | 1.0 LUMIÈRE | Des frais plus élevés, à la hauteur du sérieux des opérations à grande échelle |
| Rapports sur les battements de cœur miniers | 0 $ (gratuit) | 0 | 0 | Aucun gaz n'est facturé pour les contributions minières, garantissant une participation sans frais |

**Règles de conversion dynamique :**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Règles de répartition des frais de gaz :**

| Destination | Proportion | Fonction |
|------|------|------|
| Destruction permanente | 50% | Déflation continue, réduisant l'offre de circulation |
| Récompenses du validateur | 30% | Inciter les validateurs à maintenir la sécurité du réseau et à produire des blocs |
| Trésor écologique | 20% | Financement supplémentaire des promoteurs et fonds de fonctionnement communautaire |

**Estimation de la déflation des frais de gaz :** En supposant une moyenne de 100 000 transactions actives quotidiennes et des frais de gaz moyens de 0,005 $ (principalement des votes et des transferts), l'équivalent en USD détruits par jour = 100 000 × 0,005 $ × 50 % = 250 $/jour. Lorsque LIGHT=0,05$, cela équivaut à 5 000 LIGHT/jour≈1,825 million/an ; lorsque LIGHT=0,50$, cela équivaut à 500 LIGHT/jour≈182 500/an. La quantité de LIGHT avec la déflation des frais de gaz diminue à mesure que le prix augmente (l'équivalent en USD est constant), mais son soutien au prix se reflète par « l'achat continu de l'équivalent » - chaque transaction détruit des jetons à un taux fixe en USD.

### 4.6 Système de vérification

| Dimensions | Validateurs | Nœuds légers (mineurs de navigateur) |
|------|--------|---------|
| Responsabilités | Génération de blocs, consensus, nœud complet | Vérification d'en-tête de bloc, relais de données |
| Jalonnement | Minimum 500 000 LUMIÈRE | Aucun |
| Revenu | Frais de gaz 30 % + pool de libération quotidienne 5 % | Récompenses minières PoC (pool de libération quotidienne 95%) |
| Quantité | Initiale 21, limite supérieure 100 | Pas de limite supérieure |
| Tranchant | 5% de pénalité pour double signature + interdiction de 180 jours | Aucun |

**Démarrer par étapes (tolérance aux pannes BFT : N≥3f+1) :**

| Phases | Nombre de validateurs | Tolérance aux pannes f | Conditions d'arrêt de la chaîne | Expérience utilisateur |
|------|-----------|-------|---------------|----------|
| Testnet (3 mois avant TGE) | 7 | 2 | 3 hors ligne en même temps | Les tests internes peuvent tolérer de courtes interruptions |
| Réseau principal TGE | Minimum 10, objectif 21 | 3-6 | 4-7 hors ligne en même temps | Interruptions occasionnelles (<1 fois par trimestre) pour lisser |
| Ouvert aux élections à partir du 7ème mois | 21-100 | 6-33 | 7-34 hors ligne en même temps | Utilisateur ignorant |

**Résultat absolu : TGE ne doit pas être exécuté lorsqu'il y a <7 validateurs. ** Moins de 7 signifie f ≤ 1. Toute défaillance ponctuelle entraînera l'arrêt de l'ensemble de la chaîne, ce qui équivaut à une « indisponibilité du produit » pour les utilisateurs non techniques.

### 4.7 Couche d'infrastructure réseau

Les nœuds validateurs transportent les passerelles d'accès WebSocket de manière distribuée (chaque validateur a une limite supérieure de 50 000 connexions) ; La signalisation P2P est fournie par le nœud validateur + relais communautaire ; L'agrégation Heartbeat Merkle soumet uniquement le hachage racine par bloc (surcharge O (1) en chaîne); le frontal est distribué via IPFS+CDN.

Réseau P2P : framework WebRTC ICE (priorité STUN/repli TURN) ; environ 70 à 80 % des utilisateurs peuvent se connecter directement, 20 à 30 % des utilisateurs NAT symétriques passent le relais TURN ; lorsque le P2P échoue, il est rétrogradé en « mode d’authentification pure ».

Spécifications de performance : TPS théorique 1 000-3 000 ; taille de bloc 2 Mo (gouvernance réglable) ; synchronisation des nœuds lumineux <30 secondes ; Agrégation Merkle de battements de cœur d’un million de nœuds <500 ms.

### 4.8 Mécanisme de vérification des preuves de contribution

Architecture de vérification à trois niveaux : (1) défi d'échantillonnage croisé aléatoire du vérificateur (5 % de nœuds toutes les 10 minutes, temps de réponse de 30 secondes) ; (2) Vérification mutuelle par les pairs P2P (8 à 16 pairs enregistrent indépendamment le volume d'échange de données, prennent la médiane) ; (3) Agrégation Merkle en chaîne (chaque bloc soumet le score de contribution Root, les utilisateurs peuvent s'auto-vérifier via Merkle Proof). Défaut de contester 3 fois de suite → le score de la journée sera remis à zéro ; un total de 5 fois en 7 jours → un contrôle anti-triche sera déclenché.

### 4.9 Gestion du portefeuille et des clés

Architecture à trois niveaux : (1) Portefeuille intelligent intégré (Passkey/WebAuthn, aucune phrase mnémonique requise, cible plus de 80 % des utilisateurs) ; (2) Portefeuille de récupération sociale (3-5 restaurateurs, partage de Shamir, confirmation majoritaire des 2/3) ; (3) Portefeuille auto-hébergé (phrase mnémonique BIP-39 + portefeuille matériel compatible). Les frais de gaz pour les 100 premières transactions des nouveaux utilisateurs seront payés par le fonds écologique (modèle Paymaster).

### 4.10 Prix Oracle

Le TWAP en chaîne (prix moyen pondéré dans le temps sur 30 jours du pool LIGHT/USDC) est la principale source de prix ; 3+ agrégations DEX/CEX externes sont complétées (les validateurs soumettent en rotation, prennent la médiane) ; les écarts > ± 15 % déclenchent des indicateurs d'exception ; les écarts de bloc uniques > 5 % ne sont pas inclus dans le TWAP (manipulation de prêt anti-flash) ; repli vers un TWAP pur en chaîne lorsque tous les oracles externes échouent.

### 4.11 Architecture du module de contrat intelligent

10 contrats principaux : light_token, mining_reward, gouvernance, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. Le contrat principal doit faire l'objet d'une vérification formelle avant TGE.

### 4.12 Mise à niveau du protocole et gouvernance de la chaîne

Mise à niveau de niveau 4 : ajustement des paramètres L1 (vote de gouvernance 24-72h) → migration du contrat L2 (proposition majeure + audit + délai de 72h) → changement de consensus L3 (66% réussi + 2/3 signaux du validateur + période de protection de la fourche de 7 jours) → réparation d'urgence L4 (suspension du comité fantôme + correctif multi-signatures + ratification de 72h).

> **[Terminologie dans ce chapitre]**
> **Cosmos SDK** : un cadre de développement de blockchain modulaire qui permet aux développeurs d'assembler des chaînes publiques personnalisées comme des blocs de construction. Plusieurs chaînes de production (comme Cosmos Hub et Osmosis) ont vérifié sa maturité.
> **Tendermint PoS** (Proof of Stake, Proof of Stake) : Un mécanisme de consensus dans lequel les validateurs obtiennent le droit de produire des blocs en promettant des tokens (plutôt que de rivaliser pour la puissance de calcul). Fournit une « finalité instantanée » : une fois qu’un bloc est soumis, il ne peut pas être annulé.
> **BFT** (Byzantine Fault Tolerance, Byzantine Fault Tolerance) : mécanisme dans un système distribué qui peut tolérer que certains nœuds fassent du mal ou fonctionnent mal tout en parvenant correctement à un consensus. Tendermint BFT ne peut tolérer pas plus d'un tiers des validateurs agissant mal ou se déconnectant en même temps.
> **CosmWasm** : le moteur de contrats intelligents de l'écosystème Cosmos, basé sur la technologie WebAssembly, prend en charge l'utilisation du langage Rust pour rédiger des contrats et dispose de fonctionnalités de sécurité de la mémoire au moment de la compilation (empêchant les vulnérabilités courantes telles que les débordements de tampon).
> **PWA** (Progressive Web App, Progressive Web App) : une technologie Web qui s'exécute sur un navigateur mais offre une expérience d'application de type natif. Il prend en charge la mise en cache hors ligne, les notifications push et l'ajout à l'écran d'accueil sans téléchargement ni installation via l'App Store.
> **WebRTC/WebSocket** : Deux technologies de communication en temps réel du navigateur. WebRTC est utilisé pour le relais de données P2P (transmission directe entre nœuds) ; WebSocket est utilisé pour maintenir une longue connexion entre le client et le vérificateur (battement de cœur, notification de récompense).
> **PoC** (Preuve de contribution) : le mécanisme d'incitation adopté par LightDAO délivre des récompenses en vérifiant les ressources réseau (relais de bande passante, vérification des blocs, temps en ligne) réellement fournies par les utilisateurs, plutôt que de s'appuyer sur la concurrence en matière de puissance de calcul ou sur un gage de capital.
> **Merkle Tree** (Merkle Tree) : Une structure de données d'arbre de hachage qui permet une vérification efficace de l'intégrité d'une entrée spécifique dans une grande quantité de données. Ce livre blanc est utilisé pour regrouper des millions de battements de cœur de nœuds légers en un seul hachage racine et le télécharger sur la chaîne (surcharge de stockage O(1)).
> **Frais de gaz** : Les frais de traitement nécessaires à l'exécution de transactions ou d'opérations contractuelles sur la blockchain, utilisés pour rémunérer le vérificateur pour les ressources de calcul et de stockage. Les frais de gaz de LightDAO sont ancrés en équivalent USD et sont automatiquement convertis en quantité de LIGHT par l'oracle toutes les 24 heures.
> **Slashing** (pénalité) : un mécanisme de pénalité dans lequel un vérificateur est obligé de déduire une partie des jetons promis en raison d'un acte répréhensible (comme une double signature) ou d'une longue période de déconnexion. C'est une garantie économique pour la sécurité du réseau PoS.
> **Oracle** (Oracle) : un composant d'infrastructure qui transmet en toute sécurité des données hors chaîne (telles que les prix du marché, la météo, les résultats sportifs) dans des contrats intelligents en chaîne. LightDAO utilise une architecture Oracle hybride d'agrégation multi-sources TWAP + en chaîne.
> **TWAP** (Prix moyen pondéré dans le temps) : le prix de chaque bloc au cours d'une période donnée est également pondéré par le temps pour réduire l'impact de manipulation des transactions instantanées de gros montant sur la référence de prix.
> **AMM** (Automated Market Maker) : Un protocole de trading décentralisé qui réalise l'échange de jetons via un pool de liquidités (plutôt qu'un carnet d'ordres). Le prix est automatiquement déterminé par la proportion d'actifs dans le pool selon une formule.
> **DEX / CEX** : DEX (Decentralized Exchange, échange décentralisé) n'a pas besoin d'héberger les actifs des utilisateurs et négocie en peer-to-peer via des contrats intelligents ; CEX (Centralized Exchange, échange centralisé) oblige l'opérateur à conserver les actifs et à faire correspondre les transactions.
> **IPFS** (InterPlanetary File System, InterPlanetary File System) : Protocole de stockage et de distribution de fichiers décentralisé, utilisé dans ce livre blanc pour un hébergement résistant à la censure d'applications front-end (même si le nom de domaine est bloqué, les utilisateurs peuvent toujours accéder à la plateforme via IPFS).

---

## Chapitre 5 : Modèle économique des jetons

### 5.1 Base de conception totale

**Offre totale LIGHT : 2,5 milliards (2 500 000 000), et ne sera jamais émise en plus. **

| Projets d'analyse comparative | Montant total | Modalités de participation | Comparabilité avec LightDAO |
|---------|------|---------|------------------|
| Bitcoin | 21 millions | Machine minière PoW | Référence narrative, le seuil est bien haut |
| Hélium (HNT) | 223 millions | Point d'accès matériel 200 $+ | Benchmark DePIN, échelle matérielle limitée |
| Filecoin (FIL) | 2 milliards | Matériel de stockage | Les plus proches en termes d'ampleur, les deux sont des « contributions de ressources en échange de jetons » |
| Kaspa (KAS) | 28,7 milliards | Carte graphique PoW | Une baisse trop importante et douce a une valeur de référence |
| Réseau Pi | 100 milliards | Clics mobiles | Matériel pédagogique négatif : le montant total est trop important → la perception de la valeur est extrêmement faible |

**Raison principale du choix de 2,5 milliards de pièces :**

1. **Capacité d'investissement (contrainte principale) :** 850 millions de pièces dans le coffre-fort × prix de base 0,15 $ × taux d'utilisation de 75 % = **95,63 millions de dollars ≈ 100 millions de dollars** capital déployable, atteignant le seuil minimum crédible du PE du marché intermédiaire inférieur. Base académique : Cong, Li & Wang (2021) « Tokenomics : Dynamic Adoption and Valuation » (*Review of Financial Studies* 34(3) :1105-1155, NBER w27222) prouve que l'utilité de la plateforme (retour sur investissement → rachat → soutien des prix) est le moteur fondamental de la valeur symbolique, et non l'étendue de la distribution.
2. **Conseils du réseau :** 1 milliard de pièces sont extraites et 684 900 pièces sont libérées le premier jour de l'époque. Lorsqu'il y a 100 000 mineurs actifs, la moyenne par habitant est de 6,51 LIGHT/jour, maintenant ainsi une « perception entière ».
3. **Faisabilité opérationnelle :** Fonds de fonctionnement stratégique de 10 % (250 millions de pièces) pour résoudre le déficit de développement/audit/financement juridique pré-TGE (1,10 à 2,85 millions de dollars). Le modèle communautaire pur ne peut pas couvrir ce coût.
4. **Faisabilité de la déflation :** Le seuil inférieur de 1 milliard de pièces est atteint dans les 11e à 12e années dans le scénario de base (25 à 30 % plus court que les 15 ans et plus du plan de 21 milliards).
5. **Analyse comparative raisonnable :** Le même niveau que Filecoin (2 milliards), qui figure parmi les cinq premiers projets du domaine DePIN en termes de valeur marchande.

### 5.2 Plan de distribution des jetons

| Catégorie d'allocation | Rapport | Quantité | Objectif | Méthode de publication |
|---------|------|------|------|---------|
| Exploration de nœuds légère | 40% | 1 milliard | Récompenser les contributeurs du réseau | Réduit de moitié tous les 2 ans, publié en temps réel en fonction des contributions |
| Coffre-fort d'investissement d'entreprise | 34% | 850 millions de pièces | Exécution des investissements sous gouvernance DAO (détruite lors de l'investissement) | Verrouillage multi-signature, uniquement libéré et détruit via des résolutions valides |
| Fonds de développement écologique | 16% | 400 millions | Liquidité, parachutages, financement des développeurs, opérations communautaires | Libération progressive (voir section 5.3) |
| Fonds de fonctionnement stratégique | 10% | 250 millions de pièces | Équipe, audit, juridique, infrastructure, investisseurs stratégiques | 12 mois falaise + 36 mois linéaires (voir section 5.X) |

**Analyse comparative de l'industrie (référence de cohorte Tokenomics.net 2024-2025) :** Récompenses de la communauté/utilisateur de 20 à 35 % (LightDAO : 40 % d'exploitation minière + 16 % d'écologie = 56 %, plus élevé en raison de l'absence de cycle de capital-risque) ; trésorerie/réserves 15-25 % (LightDAO : 34 %, en raison de la fonction d'investissement) ; équipe/investisseurs 15-45 % (LightDAO : 10 %, bien inférieur à l'industrie, maintenant le récit « National DAO »).

### 5.3 Plan de déblocage du Fonds de développement écologique

| Scène | Temps | Proportion | Quantité | Objectif |
|------|------|------|------|------|
| TGE | Jour 0 | 30% | 120 millions de pièces | Liquidité DEX (60 % = 72 millions) + parachutage de départ (40 % = 48 millions) |
| Période de diffusion linéaire 1 | 1er au 12ème mois | 40% | 160 millions de pièces | 13,33 millions de pièces par mois : incitations communautaires, marketing, plan de largage |
| Période de diffusion linéaire 2 | du 13 au 24 | 30% | 120 millions de pièces | 10 millions de pièces par mois : financement des développeurs, construction écologique, réserves |

### 5.4 Fonds d'opérations stratégiques (250 millions de pièces)

| Sous-catégorie | Proportion | Quantité | Objet | Règle de libération |
|--------|------|------|------|---------|
| Échange de services contre des jetons | 50% | 125 millions de pièces | Sociétés de développement, institutions d'audit, cabinets d'avocats, opérateurs vérificateurs | 12 mois falaise + 36 mois linéaires ; 30 à 50 % des frais de service payés en LIGHT |
| Financement stratégique | 30% | 75 millions de pièces | 2-3 Fonds écologiques DePIN/Cosmos ou acteurs stratégiques de l'industrie de la consommation | Pré-TGE vendu entre 0,03 et 0,05 $ (levant de 2,25 à 3,75 millions de dollars) ; 12 mois falaise + 24 mois linéaires ; investisseur unique ≤ 2% du total |
| Contributeurs principaux | 20% | 50 millions de pièces | 3-5 sponsors/constructeurs de base | 12 mois falaise + 36 mois linéaires ; publié sur la base d'une évaluation trimestrielle des étapes ; pas de vente pendant le terme |

**Exigences des investisseurs stratégiques :** Les contributions non financières (flux de transactions, services de vérification, ressources de conformité) doivent être fournies, et les investisseurs purement financiers ne sont pas acceptés.

**Conformité réglementaire :** La vente pré-TGE adopte l'exemption à double voie Reg S (investisseurs non américains) + Reg D Rule 506(c) (investisseurs qualifiés américains).

**Règles de divulgation des principaux contributeurs :** Seuls le montant total (50 millions = 2 % du montant total) et les règles de libération sont divulgués, et les noms personnels et les quotas individuels ne sont pas divulgués. Catégories de rôles divulguées : Technologie/Investissement/Conformité/Communauté.

### 5.5 Production minière et plan de réduction de moitié

**Dérivation :** 2A = 1 milliard → A = 500 millions (Première Ère). Sortie quotidienne = 500 millions ÷ 730 = 684 932 pièces ≈ 684 900/jour. Chaque bloc = 684 932÷49 371 ≈ 13,87 LUMIÈRE.

**Remarque :** Le pool de récompenses pour chaque bloc est partagé par l'ensemble du réseau, dont 5 % sont alloués aux validateurs (34 200/jour) et 95 % sont alloués aux mineurs de nœuds légers (650 700/jour).

| Époque | Temps | Production totale | Sortie quotidienne | Pool de récompenses par bloc |
|------|------|---------|---------|------------|
| 1ère Ère | 0-24 mois | 500 millions | ≈684 900 | ≈13,87 LUMIÈRE |
| 2e ère | 25-48 mois | 250 millions de pièces | ≈342 500 | ≈6,93 LUMIÈRE |
| La 3ème Ère | 49-72 mois | 125 millions de pièces | ≈171 200 | ≈3,47 LUMIÈRE |
| La 4ème Ère | 73-96 mois | 62,5 millions de pièces | ≈85 600 | ≈1,73 LUMIÈRE |
| La 5ème Ère | 97-120 mois | 31,25 millions de pièces | ≈42 800 | ≈0,87 LUMIÈRE |

**Vérifiez :** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 milliard ✓. 97 % terminés au cours des 10 premières années.

### 5.6 Modèle de référence des revenus des utilisateurs

| Taille du réseau | Revenu quotidien par habitant | Revenu mensuel | Revenu annuel | Revenu mensuel à majoration complète (1,44x) |
|---------|-----------|--------|-------------|-------------------|
| 10 000 mineurs (stade graine) | ≈65,07 | ≈1 952 | ≈23 751 | ≈2 811 |
| 100 000 mineurs (stade de croissance) | ≈6,51 | ≈195,2 | ≈2 375 | ≈281,1 |
| 1 million de mineurs (période d'échelle) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28,1 |

**Niveau partenaire (50 invitations, 20 % de partage, bonus complet) :**

| Échelle du réseau | Soi (y compris bonus) | Partage d'invitations | Quotidien complet | Mensuel complet |
|---------|------------|---------|--------|-------------|
| 10 000 mineurs | ≈93,7 | ≈650,7 | ≈744,4 | ≈22 332 |
| 100 000 mineurs | ≈9,37 | ≈65,07 | ≈74,44 | ≈2 233 |
| 1 million de mineurs | ≈0,94 | ≈6,51 | ≈7,45 | ≈223,4 |

### 5.7 Plan de croissance des parachutages

**Modèle économique :** Budget total du largage = utilisateurs cibles atteints × largage par habitant × (1+taux de gaspillage) = 100 000 × 150 LIGHT × 1,3 ≈ 19,5 millions (type d'acquisition) + 35,5 millions (type écologique) = **55 millions** (représentant 13,75 % du fonds écologique de 400 millions).

| Type de largage | Conditions de déclenchement | Quota unique | Budget |
|---------|---------|---------|------|
| Premier largage minier | Vous avez terminé 4 heures d'exploitation minière efficace pour la première fois | 50 LUMIÈRE | 15 millions de pièces |
| Expansion géographique | Les utilisateurs du marché cible complètent ZK-KYC | 100 LUMIÈRE | 10 millions de pièces |
| Apprendre à gagner | Module éducatif complet + Quiz | 30 LUMIÈRE | 6 millions de pièces |
| Premier vote sur la gouvernance | Première participation au vote | 20 LUMIÈRE | 3 millions de pièces |
| Provision de liquidité | Injection LP ≥50$ lock-up pendant 30 jours | 200 LUMIÈRE | 10 millions de pièces |
| Création de contenu | Tutoriels/traductions vérifiés par la communauté | 50-200 LUMIÈRE | 6 millions de pièces |
| Canaux de coopération | Inscription + premier minage via des partenaires | 80 LUMIÈRE | 5 millions de pièces |

**Vérification CAC :** 55 millions de pièces × 0,03 $ = 1,65 million de dollars ÷ 30 000 mineurs actifs retenus = **55 $/personne** (fourchette sectorielle de 50 à 200 $, dans le bas de l'échelle). Base académique : Zheng (2023) « Opération Dumbo Drop : parachuter ou ne pas parachuter pour le succès de l'offre initiale de pièces ? prouve que le taux de rétention des largages liés à un événement est 3 à 5 fois supérieur à celui des largages purs.

**Anti-abus :** Empreinte digitale unique du navigateur + ZK-KYC ; limité à 1 réclamation par catégorie et par adresse ; Période de blocage de 30 jours ; recyclage automatique sans activité en chaîne dans les 30 jours suivant la réclamation.

### 5.8 Volant moteur double et pool de capitaux

Volant d'inertie : Vote → Destruction de Vault LIGHT → Paiement USDC → Redistribution des bénéfices → Rachat et destruction → Support des prix → Plus d'utilisateurs.

Système à double voie : trésorerie stable (USDC, rétention des bénéfices) + trésorerie flexible (couche LÉGÈRE, détruite lors de l'investissement et non affluée sur le marché). Les rachats sont répartis via TWAP, avec un seul ordre ≤ 5 % du volume quotidien moyen des transactions.

### 5.9 Émission et négociation de sous-tokens

Le montant total de l'émission = montant de l'investissement ÷ 1 $ ; le prix d'échange est basé sur le VWAP à 30 jours ; toute la LUMIÈRE obtenue lors de l'échange sera détruite ; 50% des supporters/30% airdrop/20% réserve de fonctionnement seront distribués (bloqué 6 mois). La limite de dividende pour une seule adresse est de 15 %. Les sous-jetons sont négociés sur l'AMM en chaîne, avec une période de blocage de 30 jours après leur émission, et seront marqués « liquidés » après le retrait.

### 5.10 Liquidité initiale et découverte des prix

**Arrangement TGE (Token Generation Event, événement de génération de jetons) : **

| Projet | Planifier |
|------|------|
| Pool de liquidité initial | Sur les 120 millions de pièces débloquées par le fonds de développement écologique TGE, 72 millions de pièces (60%) ont été allouées et injectées dans le pool de liquidité DEX |
| Actifs jumelés | USDC (pool principal), USDT (pool auxiliaire) |
| Largage aérien | Les 48 millions restants (40 %) seront utilisés pour les largages aériens vers les utilisateurs de semences (voir la section 5.7 Plan de largage aérien) |
| Coté en bourse | Coté pour la première fois sur des bourses décentralisées (telles que Osmosis, JunoSwap) après TGE ; demander une cotation sur les bourses centralisées à partir du 6ème mois selon conditions de respect |

**Mécanisme détaillé des enchères néerlandaises :**

Les enchères néerlandaises sont une méthode de tarification dans laquelle les prix diminuent de haut en bas. Contrairement aux enchères anglaises (où les prix sont offerts du plus bas au plus élevé), dans les enchères néerlandaises, le vendeur fixe un prix de départ élevé et le prix diminue automatiquement au fil du temps jusqu'à ce que l'acheteur soumette une souscription à un certain niveau de prix. Le premier cours auquel le montant total de la souscription atteint l'objectif est le cours final d'ouverture.

**Pourquoi choisir une vente aux enchères néerlandaise plutôt qu'une vente aux enchères à prix fixe ou une vente aux enchères anglaise :**

| Tarifs | Avantages | Inconvénients | Applicabilité |
|---------|------|------|--------|
| Prévente à prix fixe | Simple | Le prix est subjectif, s'il est trop élevé, il ne se vendra pas, s'il est trop bas, il sera happé par les robots | Ne convient pas (pas de fonction de découverte des prix) |
| Vente aux enchères britannique (enchères) | Découverte plein tarif | Les gros acheteurs peuvent stratégiquement attendre et augmenter les prix ; guerre du gaz | Ne convient pas (la guerre du gaz en chaîne exclut les petits utilisateurs) |
| **Enchères néerlandaises** | ** Découverte automatique des prix ; aucune offre requise (pas de guerre du gaz) ; participation égale des grands et petits acheteurs ; anti-bot (le mécanisme de réduction des prix inhibe naturellement le front-running)** | Le prix de départ et le taux de décélération doivent être fixés de manière raisonnable | **Le plus adapté (équitable + efficace + anti-manipulation)** |

**Paramètres spécifiques aux enchères néerlandaises LightDAO :**

| Paramètres | Paramètres | Descriptif |
|------|------|------|
| Cible des enchères | Tokens LIGHT (attribués sur les 72 millions débloqués par le fonds écologique TGE) | L'USDC de l'enchère sera injecté dans le coffre-fort stable |
| Montant cible de la collecte de fonds | **15 millions de dollars américains** | 5 millions de dollars → réserve minimale de trésorerie stable ; 10 millions de dollars → capital d'investissement initial |
| Prix ​​de départ | 0,20 $/LUMIÈRE | Supérieur au prix d'équilibre attendu, garantissant qu'il ne sera pas perdu en quelques secondes |
| Taux de décélération | Diminution de 5% toutes les heures | À partir de 0,20 $, tombant à 0,017 $ après environ 48 heures (si personne ne s'abonne) |
| Prix ​​de réserve minimum | 0,01 $/LUMIÈRE | Si le prix de réserve est abaissé et que l'objectif n'est toujours pas atteint, la vente aux enchères sera reportée de 24 heures ou le nombre d'objets sera ajusté |
| Mode d'abonnement | L'utilisateur soumet "Je suis prêt à acheter X LIGHT équivalent à l'USDC au prix actuel" | Aucune enchère n'est nécessaire, le système réglera selon le prix final unifié (tout excédent sera remboursé sans indemnité) |
| Limite supérieure pour un seul utilisateur | Pas plus de 5 % du montant cible de la collecte de fonds (soit 750 000 $) | Empêcher un seul acheteur de monopoliser les jetons initiaux |
| Exigences KYC | Vérification améliorée (résidence fiscale) | Exigences de conformité |

**Destination des fonds issus des résultats des enchères :**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Période de protection contre la découverte des prix :** Un coupe-circuit contre les fluctuations de prix est mis en place dans les 72 heures suivant le TGE - si le prix de la transaction DEX s'écarte de plus de ± 50 % du prix d'ouverture des enchères, la fonction d'échange de sous-tokens sera suspendue (l'exploitation minière et les transferts ne seront pas affectés) pour empêcher une spéculation extrême d'interférer avec le démarrage écologique. Le fusible sera automatiquement libéré après 72 heures.

**Pourquoi 15 millions de dollars au lieu de moins :** Le capital d'investissement initial de 10 millions de dollars doit soutenir 3 à 5 investissements au cours de la première année (un seul investissement équivaut à 2 à 5 millions de dollars, voir l'échelle de la période de démarrage dans la section 9.1). Si seulement 5 millions de dollars sont collectés (le tout sous forme de réserves), il n’y aura aucun capital d’investissement déployable la première année et le volant d’inertie ne démarrera pas. 15 millions de dollars = réserve 5 millions de dollars + investissement 10 millions de dollars, ce qui est l'équilibre minimum réalisable entre « résultat net en matière de sécurité » et « démarrage par volant d'inertie ».

### 5.11 Mécanisme de déflation et résultat net

**Volume de circulation = libération minière + libération écologique + fonds stratégique débloqué − échange et destruction − destruction de gaz − rachat et destruction. ** 850 millions de pièces du coffre-fort d'investissement ne sont jamais entrées en circulation. Limite supérieure théorique de circulation = 10+4+2,5 = **1,65 milliard**.

| Conditions de déclenchement | Comportement du système |
|---------|---------|
| Tirage ≤ 1,5 milliard d'exemplaires | Signal de ralentissement (scénario de destruction extrêmement faible) |
| Volume de circulation ≤ 1,2 milliard de pièces | Annonce d'alerte précoce, suspension de la destruction active (vers la 8ème année du scénario de base) |
| Volume de diffusion ≤ 1 milliard | Arrêt brutal, toutes les destructions sont définitivement fermées (le scénario de base se situe vers les années 11-12) |

### 5.12 Mécanisme de stabilisation des prix (spirale anti-mortalité)

**Principes fondamentaux :** LightDAO n'interfère pas avec la découverte quotidienne des prix du marché. Le protocole n'ajuste ses paramètres que dans des scénarios extrêmement baissiers pour réduire le risque de tomber dans une « spirale de la mort ».

**Logique de notation :** Dans différents environnements volatils, la même baisse représente différents degrés d'anomalie. Une forte baisse sur un marché à faible volatilité constitue un signal anormal plus fort et nécessite une intervention de plus grande intensité ; une forte baisse sur un marché très volatil est relativement courante et une intervention plus légère peut être utilisée. Par conséquent, l’intensité de l’intervention est positivement liée à l’anomalie du signal, plutôt que de dépendre uniquement de la valeur absolue de la baisse.

**Organigramme complet du mécanisme :**

| Statut du marché | Volatilité historique sur 30 jours | Conditions de déclenchement | Niveau de signal | Exécution après déclenchement | Conditions de récupération |
|---------|--------------|---------|---------|----------|---------|
| Faible volatilité | ≤30% | Baisse cumulée de ≥40 % pendant 5 jours consécutifs | Niveau I | La production minière a chuté à 50 % ; le taux de destruction est passé de 20 % à 35 % ; la période de publicité sur l'ajustement des paramètres de risque a été raccourcie de 72h à 12h ; le comité fantôme est entré dans l'état actif (seul le droit de suspension temporaire peut être exercé conformément à la loi) | Le prix s'est maintenu au-dessus de la moyenne mobile sur 30 jours et a rebondi de ≥80 % par rapport au prix de déclenchement, et est resté ainsi pendant 10 jours consécutifs |
| Fluctuation moyenne | 30%-60% | Baisse cumulée pendant 7 jours consécutifs ≥ 50% | Niveau II | La production minière a chuté à 50 % ; le taux de destruction est passé de 20 % à 30 % ; la période de publicité a été réduite à 24 heures ; le comité fantôme est entré dans l'état actif | Le prix s'est maintenu au-dessus de la moyenne mobile sur 30 jours et a rebondi de ≥ 60 % par rapport au prix de déclenchement, et est resté ainsi pendant 7 jours consécutifs |
| Forte volatilité | 60%-100% | 10 jours consécutifs de déclin cumulé ≥55% | Niveau III | La production minière a chuté à 75 % ; le taux de destruction est passé de 20 % à 25 % ; la période de publicité a été réduite à 48 heures ; le comité fantôme est entré en veille | Le prix s'est maintenu au-dessus de la moyenne mobile sur 30 jours et a rebondi de ≥40 % par rapport au prix de déclenchement, et est resté ainsi pendant 5 jours consécutifs |
| Volatilité extrême | >100% | Baisse cumulée pendant 10 jours consécutifs ≥ 65% | Niveau III | Mis en œuvre conformément aux mesures de niveau III pour une volatilité élevée | Mis en œuvre selon les conditions de recouvrement de niveau III en cas de forte volatilité |

**Conditions d'exclusion :** Ce n'est que lorsque la baisse du Bitcoin au cours de la même période est inférieure à 50 % de la baisse du LIGHT que le mécanisme ci-dessus peut être déclenché pour exclure un effondrement systémique du marché (c'est-à-dire que si le BTC s'effondre également au cours de la même période, il s'agit d'un événement global du marché et aucune intervention distincte n'est initiée pour LIGHT).

**Description de la logique de récupération :** Les exigences et la durée du rebond diminuent avec le niveau d'anomalie : le niveau I nécessite l'amplitude de rebond la plus élevée (80 %) et le temps de confirmation le plus long (10 jours), tandis que le niveau III nécessite des exigences relativement inférieures (40 %/5 jours). Cette disposition s'inscrit dans la logique progressive selon laquelle « plus le signal anormal est fort, plus l'intervention est forte et plus la confirmation de la récupération est stricte ».

**Source de données sur la volatilité et les prix :** La volatilité historique sur 30 jours et la baisse cumulée sont fournies par l'oracle des prix en chaîne (voir Section 4.10), sur la base de l'instantané TWAP du bloc quotidien UTC 00:00, et ne reposent sur aucune source de données externe.

### 5.13 Test de résistance sur la viabilité des bénéfices

| Scénarios de stress | Et si | Réponses du protocole | Dans le pire des cas |
|---------|---------|---------|-------------|
| Tous les investissements ont échoué | Toutes les sociétés investies ont subi des pertes ou n'ont pas réussi à sortir | Le fonds d'assurance (10 % des bénéfices accumulés) couvre une partie des pertes ; des réserves de trésorerie stables (≥8 millions de dollars) pour maintenir les opérations ; les nouveaux investissements sont suspendus jusqu'à ce que la communauté réévalue | Les détenteurs de sous-jetons ne peuvent pas recevoir de dividendes ; Le prix du LIGHT est sous pression mais ne revient pas à zéro (les fonctions minières et de gouvernance continuent de fonctionner) |
| Le marché a plongé de 80% | Le prix de LIGHT a chuté de 80 % par rapport au sommet | Déclencher le mécanisme spirale anti-mort (niveau II ou niveau III) ; la production minière est réduite de 50 à 75 % ; le taux de destruction est augmenté ; le comité fantôme peut suspendre les opérations à haut risque | Les revenus des utilisateurs diminuent mais le réseau continue de fonctionner ; le mécanisme est automatiquement levé lorsque les conditions de récupération sont remplies |
| Principales interdictions réglementaires du marché | Un grand pays a complètement interdit les actifs cryptographiques | Le miroir IPFS de commutation frontale reste accessible ; les actifs en chaîne et les droits et intérêts des utilisateurs existants ne sont pas affectés ; la disponibilité des services tiers n'est adaptée que dans le cadre de l'application de la loi ; Les opérations du SPV aux îles Caïmans ne sont pas soumises à la juridiction d'un seul pays | La croissance des utilisateurs dans la région a stagné ; les autres régions du monde ne sont pas concernées |
| Perte d'utilisateurs à grande échelle | Les mineurs actifs ont chuté de plus de 70 % | BaseReward est automatiquement redistribué (le dénominateur diminue → le revenu par habitant des utilisateurs retenus augmente) ; les incitations aux invitations sont pondérées pour attirer des flux de retour ; les seuils de gouvernance sont temporairement abaissés (mécanisme dynamique dans la section 5.14) | La sécurité du réseau est réduite mais la chaîne ne sera pas arrêtée (Tendermint BFT tolère que <1/3 des validateurs soient hors ligne) |
| Vulnérabilités majeures des contrats intelligents | Vulnérabilités exploitables trouvées dans les contrats principaux | Suspension d'urgence multi-signatures des sorties de fonds (un délai de 72 heures offre une fenêtre de réponse) ; Lancer un vote de migration du contrat de sauvegarde (réparation d'urgence de niveau L4, voir section 4.12) ; Le fonds d'assurance couvre les pertes des utilisateurs | Certains fonds peuvent être endommagés ; Les opérations normales reprennent une fois la migration terminée |

### 5.14 Mécanisme d’équilibrage intergénérationnel

Ajustement dynamique du seuil de gouvernance : pour chaque million de nouveaux mineurs actifs cumulés, le seuil de proposition est automatiquement abaissé de 5 % (limite inférieure 2 500 LIGHT).

> **[Terminologie dans ce chapitre]**
> **TGE** (Token Generation Event) : moment où un token est créé et distribué pour la première fois via un contrat intelligent, généralement accompagné de la création d'un pool de liquidité initial, du prix des enchères néerlandaises et de la première transaction publique. Semblable à une introduction en bourse dans la finance traditionnelle, mais n’implique pas de cotation en bourse.
> **Halving** (Halving) : Un mécanisme par lequel la production minière est automatiquement réduite de 50 % à chaque période fixe (2 ans/730 jours pour LightDAO). L’objectif est de créer une pénurie progressive : au fil du temps, de moins en moins de nouvelle offre s’ajoute, et si la demande ne diminue pas, les prix seront soutenus. Bitcoin adopte la réduction de moitié tous les 4 ans.
> **Treasury** (Treasury) : réserves de jetons verrouillées par des contrats multi-signatures, qui ne peuvent être libérées que par le biais de résolutions de gouvernance. LightDAO dispose de deux types de coffres-forts : les coffres-forts d'investissement (qui contiennent LIGHT et sont détruits lorsque les investissements sont exécutés) et les coffres-forts stables (qui contiennent de l'USDC et sont utilisés pour payer la contrepartie de l'investissement et les dépenses d'exploitation).
> **Déflation** (Déflation) : Le processus dans lequel l'offre totale ou la circulation des jetons continue de diminuer. LightDAO parvient à la déflation grâce à quatre mécanismes : exécution et destruction des investissements, échange et destruction de sous-jetons, destruction des frais de gaz (50 %), et rachat et destruction des bénéfices.
> **Death Spiral** (Death Spiral) : les prix des jetons chutent → les revenus des mineurs diminuent → les mineurs démissionnent → la sécurité/contribution du réseau diminue → une nouvelle perte de confiance → un cercle vicieux dans lequel les prix continuent de baisser. Le mécanisme d’intervention progressive décrit à la section 5.12 est conçu pour interrompre ce cycle.
> **Sous-token** (Sous-token) : certificat de réclamation de distribution de revenus SPV délivré conformément aux règles après la réalisation de chaque investissement d'entreprise (comme l'acquisition d'une marque de café → token CAFE). Détenir des sous-jetons = détenir des qualifications pour la distribution des bénéfices futurs et ne représente pas les droits des actionnaires ni les droits de gouvernance d'entreprise.
> **LP** (Fournisseur de liquidités) : les participants qui injectent deux actifs de valeur égale (tels que LIGHT+USDC) dans le pool de liquidité DEX perçoivent en retour des frais de transaction. LP est la base du fonctionnement normal de DEX.
> **VWAP** (Prix moyen pondéré par le volume) : le prix sur une période donnée est pondéré par le volume de chaque transaction, reflétant le véritable coût de transaction du marché. LightDAO utilise le VWAP de 30 jours comme référence de tarification pour l'échange de sous-jetons.
> **CAC** (Customer Acquisition Cost, coût d'acquisition utilisateur) : Le coût moyen pour acquérir un utilisateur actif efficace. Le CAC cible du programme de largage LightDAO est de 55 $/mineurs actifs retenus (fourchette industrielle de 50 à 200 $).
> **wLIGHT** (Wrapped LIGHT, encapsulated LIGHT) : jetons équivalents LIGHT émis sur Ethereum ou Solana via des ponts inter-chaînes, et une quantité égale de LIGHT native est verrouillée par le contrat de pont sous forme de réserve 1:1. Le but est de permettre aux utilisateurs de l’écosystème non-Cosmos d’obtenir et de conserver la LUMIÈRE.
> **Dutch Auction** (Dutch Auction) : Une méthode de tarification dans laquelle le prix diminue de haut en bas. Le vendeur fixe un prix de départ élevé et le prix diminue automatiquement au fil du temps jusqu'à ce que l'acheteur soumette un abonnement à un certain niveau de prix. Le premier prix auquel le montant total de la souscription atteint l'objectif est le prix final de la transaction. L’avantage est qu’aucun appel d’offres n’est requis (pas de guerre du gaz), que les acheteurs de toutes tailles sont égaux et qu’il est naturellement résistant à la préemption des robots.

---

## Chapitre 6 : Mécanisme de gouvernance

### 6.1 Modèle de vote bidimensionnel

Poids de détention de la devise (y compris réputation + bonus de niveau, limite supérieure totale +40%) + nombre d'adresses (1 adresse = 1 vote, les adresses associées sont fusionnées). Les droits de vote sont valables 90 jours et peuvent être activés en transférant 5 LIGHT. Bonus de réputation : Détention de la monnaie pendant 1 an + 15 votes valides → jusqu'à +30%.

### 6.2 Taux de réussite dynamique

Taux de réussite minimum = 50 % + (50 % - taux de vote réel). Majorité simple lorsque taux de vote ≥50%.

### 6.3 Paramètres de la proposition

| Tapez | Marge | Taux de vote des jetons | Taux de vote sur les adresses | Taux de réussite | Retard d'exécution |
|------|--------|-----------|---------------|--------|-------------|
| Micro | 100 $ | ≥15% | ≥20% | Dynamique ≥55% | 24h |
| Type d'acquisition | 500 $ | ≥25% | ≥30% | Dynamique ≥60% | 72h |
| Type de capital-risque | 500 $ | ≥35% | ≥40% | Dynamique ≥60% | 72h |
| Majeur | 1 000 $ | ≥45% | ≥50% | Dynamique ≥66% | 72h |
| Urgence | 2 000 $ | ≥50% | ≥60% | ≥75% | Non-financement 6h/à haut risque 1h ; les opérations en capital restent soumises à un blocage horaire de 72 heures |

### 6.4 Cycle de vie de la proposition

Qualification de soumission : ≥5 000 LIGHT + 30 jours consécutifs de gage + dépôt. Annonce publique 72h (révisée ≤ 2 fois). Le vote a lieu dans un délai de 7 jours (48h pour le fast track, ≤500 000 USDC). Veto au refroidissement pendant 90 jours. L'efficacité est retardée de 24 heures.

**Description du seuil :** 5 000 pièces au stade d'amorçage (10 000 mineurs) ≈ 77 jours de production de base ; niveau partenaire ≈ 7 jours. La gouvernance sera activée au septième mois et les premiers utilisateurs disposeront d'un temps d'accumulation suffisant.

### 6.5 Incitations au vote

Il existe une incitation de base à la participation (voire au partage) et un bonus supplémentaire au jugement correct (50 % du pool de paris). Misez sur la gamme 5-500 LIGHT. Supprimez l'effet grégaire : les adversaires reçoivent toujours des incitations de base même s'ils font « partie de la mauvaise équipe ».

### 6.6 Récompenses et pénalités en cas de succès ou d'échec

Échec de bonne foi : remboursement de l'acompte de 50 % + temps de recharge de 30 jours. Défaillance malveillante (contrefaçon/répétition) : montant total confisqué + bannissement permanent. Preuve de fraude : plafonné à 5 000 LIGHT, 40% de malus de bonus d'établissement + 500 LIGHT.

### 6.7 Transparence financière

Tableau de bord en temps réel sur la chaîne + rapport financier trimestriel + audit indépendant annuel (le premier audit doit être réalisé avant TGE) + divulgation en temps réel des objectifs d'investissement.

---

## Chapitre 7 : Contrôles et contrepoids du pouvoir et définition des rôles

### 7.1 Tuteur initial

Les autorisations sont limitées aux informations sur le document/format/site officiel. Durée ≤ 24 mois. Un tuteur alternatif doit être désigné (impossible de signer pendant 30 jours consécutifs → prise en charge automatique). Invalidité simultanée → Vote d'urgence 48h pour désigner un gérant intérimaire.

### 7.2 Feuille de route pour le transfert de puissance

| Scène | Temps | Autorisations | Approbation d'investissement |
|------|------|------|---------|
| Période de création | 0-6 mois | Gardien (non financier) | Gardien + communauté multi-signature 3/5 |
| Période de transition | Juillet-décembre | Guardian + contributeur principal signés conjointement | Comme ci-dessus + contributeur principal |
| Période d'échéance | 13-24 mois | Comité de gouvernance 3/5 | Vote bidimensionnel régulier |
| Période d'autonomie | 25 mois + | Tous les titulaires | Même période d'échéance |

### 7.3 Comité de gouvernance

Le pouvoir est réparti entre cinq personnes (président tournant/finances/technologie/communauté/clé), à rotation trimestrielle, et le mandat est de six mois et peut être réélu une fois. La campagne promet 50 000 signatures conjointes LIGHT + 100 adresses. La prise de décision implique ≥3 personnes et couvre ≥3 postes.

**Description du seuil :** 50 000 pièces au stade d'amorçage ≈ 67 jours (2,2 mois) pour les partenaires ; au stade de croissance ≈ 672 jours (22 mois). La première élection du comité au 13ème mois est ouverte aux premiers partenaires.

### 7.4 Comité fantôme

Suspension temporaire pour « violations/sanctions/fraude majeure » uniquement. Tous les votes doivent être ratifiés dans les 72 heures (opposition > 60 % → rejetée). Rejeté deux fois de suite → automatiquement mis en accusation et dissous.

### 7.5—7.6 Vérification de la campagne et plan clé

SimHash>80 % de disqualification ; Le contenu de l’IA doit être complété par des explications ; 20% des votes seront déduits pour les questions absentes. Sauvegarde des fragments de clé + bilan de santé trimestriel + annonce publique sur 7 jours + remplacement du vote.

---

## Chapitre 8 : Mécanisme de confiance et de sécurité

### 8.1 Cinq mécanismes de sécurité majeurs

Blocage horaire 72h (les propositions d'urgence ne sont pas exemptées d'opérations en capital) ; multi-signature 3/5 ; rotation trimestrielle ≤ 2 séances ; Pénalité de 100 % en cas de fraude ; toutes les transactions se font sur la chaîne.

### 8.2 Fonds d'assurance

**10 %** des bénéfices d'investissement réussis sont accumulés. Les réclamations doivent être déclarées de manière indépendante + DAO 66 % en faveur + simple ≤ pool 20 %. Source complémentaire : 30 % de l'amende pour contrefaçon. Le positionnement "tampon partiel" n'est pas une protection complète.

### 8.3 Plan extrême

Supervision cygne noir → IPFS + suppression des droits administrateur ; fraude → suspension du comité fantôme (72h de ratification) + fonds d'assurance + arbitrage SPV ; spirale de la mort → mécanisme de la section 5.12 ; vulnérabilité du contrat → suspension multi-signatures + vote de migration ; validateurs faisant collectivement le mal → tolérance BFT <1/3, si dépassée, la chaîne sera suspendue + migration de vote d'urgence.

---

## Chapitre 9 : Opérations d'investissement et stratégies de sortie

### 9.1 Sélection et échelle des objectifs d'investissement

** Trajectoire de croissance étape par étape de l'échelle d'investissement (formule : excédent de trésorerie × 15 % × prix LIGHT) : **

| Scène | prix LUMIÈRE | Limite de transaction unique pendant la période initiale du coffre-fort | Objectifs d'adaptation | Analyse comparative de l'industrie |
|------|----------|--------|----------|--------------|
| Période de démarrage (Y1-2) | 0,02 $—0,05 $ | 2,55 millions de dollars – 6,37 millions de dollars | Magasin unique/petite chaîne, ange rond | MicroPE |
| Stade de croissance (Y3-5) | 0,05 $ à 0,30 $ | 6,37 millions de dollars – 38,25 millions de dollars | Chaîne régionale 30-200 magasins, cycle Seed-A | PE du marché intermédiaire inférieur |
| Stade de maturité (Y5-8) | 0,30 $ à 1,00 $ | 38,25 millions de dollars – 127,5 millions de dollars | Chaîne multinationale/technologie de taille moyenne, ronde B-C | PE du marché intermédiaire |
| Période d'échelle (Y8+) | 1,00 $+ | 127,5 millions de dollars+ | Acquisitions à grande échelle, pré-IPO | PE/VC à grande échelle en phase de croissance |

### 9.2 Processus de prise de décision en matière d'investissement

Découverte du projet (≥5 000 LIGHT) → due diligence indépendante → annonce publique 72h → vote bidimensionnel → exécution 24/72h.

### 9.3 Sortie et répartition des bénéfices

Dividende annuel : **40 %** détenteurs de sous-jetons / **30 %** coffre-fort stable / **20 %** rachat de LIGHT pour destruction / **10 %** fonds d'assurance.
Revenu de sortie : **70 %** Stable Vault / **30 %** Rachat et brûlage.

### 9.4 Discipline en matière d'investissement

| Règles | Contenu |
|------|------|
| Limite de destruction unique | Coffre-fort restant × 15 % (850 millions × 15 % initiaux = 127,5 millions de pièces) |
| Cible unique | ≤25% de la valeur totale du coffre-fort |
| Concentration industrielle | ≤40% du portefeuille |
| Concentration géographique | ≤30% du portefeuille |
| Réserves de trésorerie stables | 5 millions de dollars au TGE (enchères), atteignant 8 millions de dollars au 24e mois |
| Délai de réflexion | 2 échecs consécutifs → 180 jours |

**Capacité du coffre-fort :** 850 millions de pièces × 0,10 $ = 85 millions de dollars (capacité totale initiale) ; × 0,30 $ = 255 millions de dollars ; × 1,00 $ = 850 millions de dollars. La limite de 15 % par transaction unique rend le rythme d'investissement positivement lié au prix.

> **[Terminologie dans ce chapitre]**
> **EBITDA** (bénéfice avant intérêts, impôts, dépréciation et amortissement) : indicateur qui mesure la rentabilité des opérations principales d'une entreprise, en éliminant l'interférence de la structure financière (intérêts), de la politique fiscale (fiscalité) et des choix comptables (dépréciation/amortissement), facilitant les comparaisons entre entreprises et entre secteurs. Marge d'EBITDA = EBITDA ÷ résultat opérationnel.
> **DCF** (Discounted Cash Flow, méthode des flux de trésorerie actualisés) : méthode de valorisation qui convertit les flux de trésorerie futurs attendus de l'entreprise en la valeur actuelle à un certain taux d'actualisation. Il convient aux entreprises matures disposant de flux de trésorerie stables (telles que les chaînes de consommation), mais pas aux entreprises technologiques en démarrage qui ne sont pas encore rentables.
> **IPO** (Initial Public Offer) : première fois qu'une entreprise émet publiquement des actions en bourse et est cotée à la négociation. Pour LightDAO, l’introduction en bourse des sociétés investies est l’une des principales voies de sortie pour les moteurs de croissance.
> **Pré-IPO** : Dernier tour de table de financement en capital-investissement avant la cotation officielle de la société. Habituellement, la valorisation est proche du niveau post-IPO, le risque est inférieur à celui des tours précédents mais le multiple de rendement est également inférieur.
> **TWAP Execution** (Time-Weighted Average Price Execution) : divisez les ordres de rachat de gros montant en plusieurs ordres de petit montant et exécutez-les uniformément sur une période de temps pour éviter l'impact d'un seul ordre important sur le prix du marché. LightDAO stipule qu'un seul rachat ne doit pas dépasser 5 % du volume quotidien moyen des transactions.

---

## Chapitre 10 : Feuille de route

| Phases | Temps | Objectifs fondamentaux | Étapes clés | Conditions préalables |
|------|------|---------|---------------|-------------|
| Période de préparation | T4 2026 | Entité juridique + équipe + fonds en place | Enregistrement de l'entité Caïman/BVI terminé ; partenaire technique ou équipe de développement signé ; intention stratégique de l'investisseur confirmée (2-3 entreprises) ; capital de démarrage ≥ 150 000 $ en place | le fondateur détermine la méthode de divulgation de l'identité ; achèvement du BP et du Pitch Deck |
| Période de développement | T1-T2 2027 | Développement du système de base | 10 modules de contrats intelligents ont été développés ; Le développement frontal de PWA est terminé ; 7 réseaux de test de vérificateurs ont été déployés ; Les tests Alpha internes ont réussi | Équipe de développement en place ; document d'exigences (spécifications techniques) finalisé |
| Période d'audit et de tests | T3 2027 | Vérification de sécurité et de conformité | Publication d'un rapport d'audit de sécurité indépendant (≥1 institution de premier plan) ; publication de la lettre d'avis de conformité juridique (MLM + droit des valeurs mobilières) ; 50 000 tests de résistance simultanés réussis ; taux de faux positifs du système anti-triche <2 % ; exercice de vote sur la gouvernance terminé | Gel du développement des contrats (Code Freeze); frais d'audit en place |
| TGE et réseau principal en ligne | T4 2027 | Émission de jetons + lancement du réseau | Enchères néerlandaises terminées (objectif de 15 millions de dollars) ; réseau principal en ligne (≥10 validateurs) ; plateforme minière ouverte au public ; Pool de liquidité DEX établi ; parachutage de graines émis | Audit réussi ; validateurs ≥7 (résultat ferme); déploiement du contrat d'enchères |
| Période de construction des croyances | T1 2028 (1er au 3ème mois après TGE) | 30 000 à 50 000 utilisateurs de semences | Les mineurs actifs dépassaient les 30 000 ; premier exercice de vote sur la gouvernance ; création d'une chaîne communautaire multilingue (anglais/chinois/espagnol/portugais/Philippines) ; premier rapport communautaire mensuel publié | TGE terminé ; équipe d'opérations communautaires en place |
| Période d'ancrage de la valeur | T2-T3 de 2028 (4ème au 9ème mois après TGE) | Premier investissement + gouvernance de la période transitoire | Première proposition d'investissement adoptée (l'approbation multi-signature pendant la période de genèse s'applique du 4ème au 6ème mois ; l'approbation conjointe pendant la période transitoire s'applique à partir du 7ème mois) ; la première livraison SPV est terminée ; les validateurs sont ouverts à l'élection (à partir du 7ème mois) ; le premier rapport financier trimestriel est publié | trésorerie stable USDC≥5 millions de dollars ; la vérification diligente des objectifs d'investissement est terminée |
| Période de maturité de la gouvernance | 2028 T4-2029 T1 (10ème au 15ème mois après TGE) | Élection du comité + transition décentralisation | Première élection du comité de gouvernance (13ème mois) ; Saisie de la période d'échéance (décision 3/5 du comité) ; Le pont à chaînes croisées wLIGHT est mis en ligne ; La demande d'inscription au CEX est soumise ; Le plan de financement des développeurs démarre | Mineurs actifs ≥ 100 000 ; ≥ 100 adresses cocandidats |
| Période d'expansion écologique | A partir du T2 2029 (16ème mois + après TGE) | Réplication à grande échelle | Les mineurs actifs dépassaient 200 000 à 500 000 ; 2-3 investissements ont été réalisés ; la première vérification du rapatriement des bénéfices ; Le rachat et la destruction de LIGHT ont commencé | Le comité de gouvernance fonctionne normalement ; le modèle d'investissement a été vérifié |
| Période d'exploitation mature | A partir du T4 2029 (25ème mois + après TGE) | Rotation du volant + autonomie complète | Entrée en période d’autonomie (propositions majeures de tous les titulaires) ; déploiement cumulatif du portefeuille d'investissement ≥ 30 millions de dollars ; les données sur la déflation sont publiquement vérifiables | La gouvernance est complètement décentralisée |

**Principes de conception de la feuille de route :**

- **Audit avant TGE :** Les jetons ne seront jamais émis sans avoir effectué un audit de sécurité indépendant. C'est la garantie fondamentale de la sécurité des fonds des utilisateurs.
- **Les vérificateurs passent avant les utilisateurs :** Lorsque le réseau principal sera en ligne, il y aura ≥10 vérificateurs (tolérance aux pannes BFT f≥3), garantissant que le réseau ne s'arrêtera pas en raison d'un seul point de défaillance.
- **L'investissement précède l'expansion :** Ce n'est qu'une fois que le premier investissement est réussi et génère un bénéfice vérifiable que nous pouvons entrer dans une expansion à grande échelle. Évitez de mettre la charrue avant les bœufs en « faisant circuler les gens d'abord et trouvant les projets ensuite ».
- **Tampon de temps :** Réservez un tampon de temps de 20 à 30 % pour chaque étape. Le développement technologique, les réparations d’audit et les processus juridiques peuvent tous dépasser les attentes, et la feuille de route ne devrait pas être un « scénario des plus optimistes ».

**Relation avec la date de publication du livre blanc (4 août 2026) :** Le livre blanc a été publié en août 2026 en tant que déclaration publique de la vision et de la conception technique du projet. La mise en œuvre effective débutera au quatrième trimestre 2026 (période préparatoire) et l'objectif du TGE est le quatrième trimestre 2027. L'intervalle d'environ 14 mois entre la publication du livre blanc et le TGE a été utilisé pour la formation, le développement, l'audit et la préparation de la conformité de l'équipe.

---

## Chapitre 11 : Culture communautaire et écologie des développeurs

### 11.1 Quatre valeurs

- **La transparence vaut mieux que la perfection** - Il vaut mieux révéler les imperfections que cacher la perfection. Tous les flux de trésorerie, décisions d'investissement et votes de gouvernance sont disponibles en permanence sur la chaîne.
- **Mieux vaut progresser que radical** - Faites de petits pas et continuez à répéter. Le premier investissement débutera entre 2 et 5 millions de dollars, et l'échelle sera élargie après vérification du modèle.
- **Les responsabilités valent mieux que les droits** - Les droits et les obligations sont égaux. Les membres du comité de gouvernance doivent promettre 50 000 LIGHT et divulguer leur programme politique. S’ils ne remplissent pas leurs fonctions, ils seront condamnés à une amende.
- **La diversité vaut mieux que l'homogénéité** - Les différentes voix sont l'immunité du système. Le vote bidimensionnel (pièce + adresse) garantit que les baleines et les investisseurs particuliers ont leur mot à dire.

### 11.2 Système de jury

| Dimensions | Règles |
|------|------|
| Composition | Sélectionnez au hasard 12 utilisateurs détenant ≥10 000 LIGHT et n'ayant aucun casier judiciaire |
| Terme | 30 jours, sera tiré au sort à nouveau après expiration |
| Responsabilités | Écoutez les plaintes relatives aux sanctions anti-triche, les accusations de fraude aux propositions et les conflits communautaires |
| Processus | Les utilisateurs sanctionnés peuvent soumettre des preuves dans les 72 heures ; le jury doit rendre son verdict dans les 48 heures |
| Normes de jugement | ≥8 personnes sur 12 (majorité 2/3) doivent accepter de maintenir ou révoquer la sanction |
| Évitement | Remplacement automatique des jurés ayant une relation d'invitation avec les parties ou étant dans la même plage IP |
| Rémunération | Recevez une subvention quotidienne de service de juré de 5 LIGHT pendant le mandat (déboursée par le fonds écologique) |

### 11.3 Plan Ecologique Aménageur

| Module | Contenu | Sources de financement | Comment postuler |
|------|------|---------|---------|
| Financement des développeurs (subventions) | Pour les équipes créant des dApps, des outils et des infrastructures sur la chaîne LightDAO, une subvention unique de 5 à 500 000 $ équivalente à LIGHT | Fonds de développement écologique (phase de libération linéaire 2) | Soumettre une proposition → Évaluation du réviseur technique → Vote sur la gouvernance (processus de micro-proposition) |
| SDK et API | Fournissez des interfaces JavaScript/TypeScript SDK, REST API et WebSocket pour abaisser le seuil de développement tiers | L'agent d'examen technique dirige le développement | Open source, public sur GitHub |
| Hackathon | Un hackathon en ligne est organisé chaque trimestre, avec une cagnotte de 100 000 $ équivalent à LIGHT | Fonds de développement écologique | Inscription ouverte, sans seuil |
| Prime aux bogues | Programme de bug bounty du contrat principal, récompense entre 1 000 $ et 50 000 $ pour une seule vulnérabilité valide (classée en fonction de la gravité) | Fonds d'Assurance + Fonds de Développement Ecologique | Soumettre via Immunefi ou une plateforme auto-construite |
| Marché des contrats CosmWasm | Encouragez les tiers à déployer des contrats intelligents, et 20 % des revenus des redevances gaz seront reversés au trésor écologique pour soutenir les développeurs | Répartition des frais de gaz (voir section 4.5) | Automatique, aucune application requise |

### 11.4 Stratégie multilingue et de localisation

| Dimensions | Planification |
|------|------|
| Langue de la plateforme | Prend initialement en charge l'anglais, le chinois, l'espagnol, le portugais et le philippin ; Le français, l'arabe, le swahili et l'indonésien seront ajoutés à partir du 6ème mois |
| Langage de gouvernance | Les propositions et les plateformes de campagne sont acceptées dans n'importe quelle langue, et le système fournit une traduction automatique + une relecture du manuel communautaire |
| Opérations communautaires | Établir des chaînes communautaires indépendantes (Discord/Telegram) par langue, et chaque chaîne est équipée de bénévoles de liaison communautaire localisés |
| Traduction de documents | Les livres blancs et les documents de base sont complétés par des traducteurs bénévoles de la communauté, et les contributions à la traduction sont incluses dans le bonus de comportement « Contribution au contenu » (5 %) |
| Financement de la localisation | 10 % (40 millions de pièces) du fonds de développement écologique sont réservés au renforcement de la communauté de localisation et aux incitations à la traduction |

---

## Chapitre 12 : Équipe et consultants

### 12.1 Définition du rôle principal

| Rôle | Responsabilités | Exigences de fond | Méthodes de divulgation |
|------|------|---------|---------|
| Gardien initial/parrain du projet | Déployer les contrats initiaux, conserver les documents et coordonner les premières opérations | ≥ 3 ans d'expérience dans l'industrie de la blockchain, avec déploiement de contrats intelligents ou enregistrements d'opérations de protocole DeFi | Divulguez votre véritable identité avant TGE ou fournissez un rapport de vérification d'identité d'un tiers (tel qu'une signature de notaire + une vérification de message en chaîne) |
| Responsable technique | Conception d'architecture contractuelle, gestion d'équipe de développement, docking d'audit | Expérience de développement Cosmos SDK/CosmWasm, historique de déploiement de la chaîne de production | Comme ci-dessus |
| Responsable investissement | Ciblage cible, coordination des due diligences, création de SPV, gestion des sorties | Expérience dans le secteur du capital-investissement/capital-risque, avec dossiers de sortie complétés | Comme ci-dessus |
| Consultant en conformité | Conception de structure juridique, arrimage réglementaire, conseil en conformité MLM | Avocat avec qualifications aux États-Unis/UE/Caïmans | Nom du cabinet d'avocats public (le nom personnel ne sera pas divulgué sauf si j'accepte) |

### 12.2 Conseil consultatif

- Composé de 3 à 5 consultants indépendants, couvrant : la technologie DePIN, la conformité des investissements transfrontaliers, les opérations communautaires et les industries de consommation ;
- Les consultants reçoivent une rémunération de conseil sous forme de tokens LIGHT (décaissés sur la partie « Service Token Exchange » du fonds de fonctionnement stratégique), et le poste est verrouillé pendant 12 mois ;
- La liste des consultants est rendue publique avant le TGE et est ouverte aux enquêtes communautaires (réunion décentralisée d'enquête de texte, voir section 7.5) ;
- Les conseillers ne peuvent pas être simultanément membres du comité de gouvernance (ségrégation des conflits d'intérêts).

### 12.3 Engagement et contraintes de l'équipe

| Contraintes | Règles |
|------|------|
| Verrouillage des jetons | LIGHT (y compris l'allocation stratégique des fonds de fonctionnement) détenu par l'équipe de base doit être bloqué pendant 12 mois et libéré de manière linéaire pendant 36 mois après son déverrouillage |
| Restrictions de vente | Le tuteur initial n'est pas autorisé à vendre la LUMIÈRE obtenue par quelque canal que ce soit (y compris les parachutages, les récompenses et les compensations) pendant la durée de son mandat (≤ 24 mois) |
| Conflit d'intérêts | Les conflits d'intérêts des membres de l'équipe doivent être entièrement divulgués au moment de la nomination (qu'ils détiennent d'autres jetons DAO, qu'ils soient liés à des cibles d'investissement potentielles) |
| Conséquences du défaut de divulgation | Une fois le défaut de divulgation d'un conflit d'intérêt vérifié, vous serez définitivement interdit de participer à la gouvernance, et 50% des tokens débloqués seront confisqués au fonds d'assurance |
| Mécanisme de remplacement | Lorsqu'un rôle principal quitte ou devient incapable, le comité de gouvernance (tuteur initial + tuteur alternatif avant l'établissement) désignera un successeur, qui devra être annoncé publiquement par la communauté pendant 72 heures sans objection |

### 12.4 Rémunération des contributeurs principaux (20 % du fonds de fonctionnement stratégique)

- Montant total : 50 millions de LIGHTs (soit 2% du montant total)
- Nombre de personnes couvertes : 3 à 5 personnes
- Règles de sortie : décembre cliff + 36 mois linéaires (soit environ 1,157 million de pièces seront libérées chaque mois à partir du 13ème mois)
- Obligation de jalon : Chaque trimestre, le comité de gouvernance (tuteur initial + tiers indépendant avant établissement) confirme que le jalon est atteint avant que le quota trimestriel puisse être débloqué.
- Règles de divulgation : seuls le montant total et les règles de libération sont divulgués, et les noms personnels et les quotas d'une seule personne ne sont pas divulgués (pour protéger la vie privée, et en même temps, le montant total peut être vérifié via l'adresse multi-signature sur la chaîne que le montant total n'est pas dépassé)

---

## Chapitre 13 : Avertissement sur les risques et clause de non-responsabilité

### 13.1 Avertissement sur les risques

| Type de risque | Descriptif | Mesures d'atténuation |
|---------|------|---------|
| Risque de marché | Les prix du LIGHT peuvent fluctuer considérablement et les prix historiques ne représentent pas les performances futures. TGE a une liquidité initiale limitée et les prix peuvent fluctuer violemment | Prix ​​équitables aux enchères néerlandaises ; ±50 % des disjoncteurs 72 heures après TGE ; mécanisme d'intervention à quatre niveaux en spirale anti-mort |
| Risque du projet | La cible d'investissement peut subir des pertes, le projet de capital-risque peut échouer et tout le capital peut être perdu. Le taux d'échec moyen historique du secteur PE/VC est d'environ 50 à 70 % (accord unique) | Décentralisation bi-moteur (70% de cash-flow + 30% de croissance) ; cible unique ≤ 25 % ; industrie ≤ 40 % ; région ≤ 30 % ; Provision de 10% pour les fonds d'assurance |
| Risques techniques | Les contrats intelligents peuvent présenter des vulnérabilités non découvertes ; la compatibilité du navigateur peut affecter l'expérience de minage ; les ponts à chaînes croisées peuvent être attaqués | Audit indépendant + vérification formelle devant TGE ; Bounty contre les bogues de 1 000 $ à 50 000 $ ; Verrouillage horaire de 72 heures ; mécanisme de suspension multi-signatures |
| Risques réglementaires | Les politiques réglementaires dans divers pays et régions peuvent changer, ce qui peut entraîner des fonctions limitées ou l'impossibilité pour les utilisateurs de régions spécifiques de participer | Structure SPV des Caïmans ; vérification du zéro par défaut (la vérification est effectuée par un tiers agréé du côté du service) ; Le miroir IPFS frontal est résistant à la censure ; non commercialisé dans des pays spécifiques |
| Risque de liquidité | Le sous-jeton peut ne pas avoir une profondeur de négociation suffisante au début ; LIGHT pourrait faire face à une pression de vente au début de TGE | La liquidité initiale du sous-token AMM (6% de l'émission) ; Période de blocage du transfert de 30 jours ; Équipe/investisseur Cliff 12 mois + linéaire 36 mois |
| Risque de dilution | À mesure que le nombre de mineurs actifs augmente, les revenus miniers par habitant seront naturellement dilués (le dénominateur BaseReward augmente) | Intention de conception : les premiers participants prennent des risques plus élevés pour obtenir des rendements plus élevés ; les utilisateurs ultérieurs peuvent accélérer l'accumulation grâce au partage d'invitations ; le seuil de gouvernance est abaissé de manière dynamique |
| Risque opérationnel | Le fonctionnement et la gestion de l'entreprise investie peuvent ne pas répondre aux attentes ; Les opérations du SPV s'appuient sur des administrateurs tiers ; l'équipe d'investissement pourrait être perdue | Restrictions de la charte SPV + administrateurs indépendants ; DAO peut voter pour remplacer les administrateurs ; Clauses d'arbitrage SIAC/ICC ; assurance personne clé (en cours d'exploration) |
| Risques de pont inter-chaînes | Le pont inter-chaînes wLIGHT est exploité par un tiers et les lacunes du contrat de pont peuvent entraîner des pertes d'actifs (historique, les ponts inter-chaînes sont la plus grande source de pertes) | Audit indépendant avant la mise en ligne du pont ; les actifs de relais ne dépassent pas 5 % de l’offre totale ; divulgation des risques ; les utilisateurs peuvent choisir d'utiliser uniquement la chaîne native |
| Risque du validateur | Les validateurs se déconnectant collectivement ou commettant des actes malveillants peuvent entraîner la suspension de la production de blocs par la chaîne, et toutes les opérations des utilisateurs (extraction, vote, transferts) sont temporairement indisponibles | Tendermint BFT tolère <1/3 du mal ; validateurs ≥ 21 (f=6) ; Pénalité coupante ; mécanisme de vote d'urgence sur la migration |

### 13.2 Avis de non-responsabilité

- LIGHT et les sous-tokens ne sont pas des titres, n'ont aucune valeur intrinsèque et le prix peut revenir à zéro. Ce livre blanc ne constitue aucune forme de document d’émission de titres, d’offre d’investissement ou de conseil en investissement.
- La répartition des revenus de l'accord dépend de la performance opérationnelle réelle des actifs sous-jacents et les données historiques ne représentent pas les revenus futurs. Toutes les descriptions des retours sur investissement sont des estimations prospectives et ne constituent pas des promesses.
- L'utilisateur doit supporter toutes les pertes causées par la perte ou la fuite de la clé privée, et l'accord ne fournit pas de services de récupération. L’utilisation d’un portefeuille Tier 1 (Passkey) ou Tier 2 (Social Recovery) réduit ce risque, mais ne l’élimine pas.
- Cet accord est ouvert aux utilisateurs du monde entier (sous réserve des lois et réglementations applicables). Les utilisateurs doivent confirmer l'attitude juridique à l'égard des actifs cryptés, des organisations DAO et des certificats de revenus SPV dans leurs juridictions, et s'assurer que leur participation est légale et conforme.
- Les déclarations prospectives contenues dans ce livre blanc (y compris les feuilles de route, les modèles de revenus, les estimations de déflation, les prévisions d'échelle d'investissement) sont des prédictions basées sur des hypothèses actuelles, et les résultats réels peuvent différer considérablement en raison du marché, de la technologie, de la réglementation, de l'exécution de l'équipe et d'autres facteurs.
- Les incitations sur invitation sont un mécanisme de partage à un seul niveau et ne constituent pas des systèmes de marketing à plusieurs niveaux ou pyramidaux. Cependant, les utilisateurs doivent toujours confirmer l'attitude légale à l'égard des récompenses de parrainage dans leur juridiction.
- L'âge minimum pour participer à l'écosystème LightDAO est de 18 ans (ou l'âge légal de la majorité dans votre juridiction, selon la valeur la plus élevée). Les mineurs ne sont pas autorisés à participer à l’exploitation minière, à la gouvernance ou aux investissements.

---

## Annexe A : Tableau récapitulatif des paramètres clés

| Catégorie | Paramètre | Valeur |
|------|------|------|
| Émission | Montant total | 2,5 milliards de pièces, plus jamais émises |
| Émission | Exploitation minière | 40% = 1 milliard de pièces |
| Émission | Coffre-fort d'investissement | 34% = 850 millions de pièces |
| Émission | Fonds écologique | 16% = 400 millions de pièces |
| Émission | Opérations stratégiques | 10 % = 250 millions de pièces (service 50 %/financement 30 %/contributeurs 20 %) |
| Émission | Cycle de réduction de moitié | Tous les 2 ans |
| Émission | Sortie du jour de la première ère | ≈684 900 (mineurs 95 % = 650 700, validateurs 5 % = 34 200) |
| Émission | Pool de récompenses par bloc | ≈13,87 LUMIÈRE |
| Exploitation minière | Poids des contributions | Bande passante 40 %/session 30 %/vérification 20 %/stabilité 10 % |
| Exploitation minière | Bonus complet | 1,44 fois |
| Invitations | Évangéliste/Ambassadeur/Partenaire | 3 personnes 10%+100L/10 personnes 15%+500L+5%/50 personnes 20%+2500L+10% |
| Comportement | Quatre articles × 5% | Limite supérieure 20% |
| Frais de gaz | Mécanisme de tarification | Ancrage équivalent USD, automatiquement converti en quantité LUMIÈRE par l'oracle toutes les 24 heures |
| Frais de gaz | Virement ordinaire | Équivalent à 0,001 $ (@0,05 $ = 0,02 LUMIÈRE) |
| Frais de gaz | Vote de gouvernance | Équivalent à 0,005 $ (@0,05 $ = 0,10 LÉGER) |
| Frais de gaz | Règles de répartition | 50% destruction / 30% validateurs / 20% trésor écologique |
| Déflation | Ralentissement/alerte précoce/résultat | ≤1,5 milliard/≤1,2 milliard/≤1 milliard (volume de circulation) |
| Déflation | Limite supérieure théorique | 1,65 milliard (10+4+2,5, 850 millions dans le trésor ne seront jamais distribués) |
| Gouvernance | Seuil de proposition | ≥5 000 LIGHT + 30 jours de jalonnement |
| Gouvernance | Jalonnement en comité | 50 000 LUMIÈRE + 100 adresses |
| GOUVERNANCE | JURY | 10 000 LUMIÈRE |
| Gouvernance | Paris | 5—500 LUMIÈRE |
| Gouvernance | Bonus de réputation | 1 an +15 voix → +30% (plafond total +40%) |
| Investissement | Limite unique | Coffre-fort restant × 15 % (127,5 millions de pièces initiales) |
| Investissement | Déployable de base | 850 millions × 0,15 $ × 75 % = 95,63 millions $ ≈ 100 millions $ |
| Investissement | Répartition des bénéfices (annuel) | 40/30/20/10 |
| Investissement | Répartition des bénéfices (sortie) | 70/30 |
| Vente aux enchères | Cible | 15 millions de dollars (réserve de 5 millions de dollars + capital investi de 10 millions de dollars) |
| Réserves | Trésorerie stable | TGE 5 millions $ → Mois 24 8 millions $ |
| Assurance | Bénéfice | Bénéfice 10% |
| Largage aérien | Budget total | 55 millions (fonds écologique 13,75%), CAC≈55$/utilisateur retenu |
| Validateurs | Initiale/Majuscule | 21 (minimum 10) / 100 |
| Validateur | Mise minimale | 500 000 LUMIÈRE |
| Vérificateur | Résultat net du TGE | ≥7, sinon il ne sera pas autorisé à se connecter |

---

## Annexe B : Dérivation numérique et vérification

### B.1 Production minière

2A=1 milliard → A=500 millions. Libération quotidienne = 500 millions ÷ 730 = 684 932 ≈ 684 900. Pool minier = 684 932 × 95 % = 650 685≈650 700. Vérificateurs=684 932×5 %=34 247≈34 200. Chaque bloc = 684 932÷49 371≈13,87. Vérification : 684 932×730=499 999 960≈500 millions ✓

### B.2 Seuil de gouvernance d'accessibilité

Benchmark de 100 000 mineurs (6,51/jour, partenaire 74,44/jour) : proposition 5 000→768 jours/67 jours ; comité 50 000 → 7 684 jours (21 ans)/672 jours (22 mois) ; jury 10 000 → 1 537 jours (4,2 ans)/134 jours (4,5 mois) ; pariez 500 → 77 jours/6,7 jours.

Période d'amorçage (10 000 mineurs, 65,07/jour, partenaires 744,4/jour) : proposition → 77 jours (2,5 mois) / 6,7 jours ; comité → 768 jours (25 mois) / 67 jours (2,2 mois) ; jury → 154 jours (5 mois) / 13,4 jours.

### B.3 Chronologie de la déflation

Volume de circulation = exploitation minière + écologie + stratégie (acquise) − échange − Gaz − rachat. 850 millions du Trésor ne circuleront jamais.

| Année | Exploitation minière cumulative | Écologie | Stratégie | Échange | Gaz | Rachat | Circulation |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2,50 | 2,80 | 0 | 0 | 0,01 | 0 | ≈5,29 |
| 2 | 17h00 | 16h00 | 0,83 | 0,05 | 0,02 | 0 | ≈9,76 |
| 3 | 6h25 | 16h00 | 1,67 | 0,20 | 0,03 | 0,05 | ≈11,64 |
| 4 | 7h50 | 16h00 | 2,50 | 0,45 | 0,04 | 0,20 | ≈13,31(pic) |
| 5 | 8.13 | 16h00 | 2,50 | 0,80 | 0,05 | 0,50 | ≈13,28 |
| 6 | 8h75 | 16h00 | 2,50 | 1.20 | 0,06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 16h00 | 2,50 | 1,60 | 0,07 | 1h40 | ≈12,49 |
| 8 | 9.38 | 16h00 | 2,50 | 2h00 | 0,08 | 1,90 | ≈11,89 |
| 9 | 9.53 | 16h00 | 2,50 | 2h40 | 0,09 | 14h30 | ≈11,24 |
| 10 | 9,69 | 16h00 | 2,50 | 2,80 | 0,10 | 2,70 | ≈10,59 |
| 11 | 9.77 | 16h00 | 2,50 | 3.10 | 0,11 | 3h00 | ≈10.06 |
| 12 | 9.84 | 16h00 | 2,50 | 3h40 | 0,12 | 3h30 | ≈9,52 |

Conclusion : Le pic Y4≈1,331 milliard ; la ligne d'avertissement de 1,2 milliard est touchée par Y8 ; le seuil inférieur de 1 milliard est touché par Y11-12 ; la ligne de décélération de 1,5 milliard n’est qu’un scénario de destruction extrêmement faible.

---

## Annexe C : Journal de correction d'audit (36 éléments au total)

Contient 22 éléments originaux (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 éléments d'architecture technique (T1-7) + 7 éléments d'optimisation de modèle économique dans ce tour :

| Numéro | Correction |
|------|------|
| E-1 | Montant total 2,1 milliards → 2,5 milliards (en raison des contraintes de capacité d'investissement) |
| E-2 | Allocation 50/30/20→40/34/16/10 (10% des nouveaux fonds stratégiques de fonctionnement) |
| E-3 | Vente aux enchères néerlandaise 10 millions de dollars → 15 millions de dollars (capital d'investissement initial 5 millions de dollars → 10 millions de dollars) |
| E-4 | Nouveau plan de croissance du largage aérien en 5,7 sections (55 millions de pièces, CAC $55/personne) |
| E-5 | Les vérificateurs sont lancés par étapes (Testnet 7→TGE minimum 10/Target 21→Open 100) |
| E-6 | Ajustement de la ligne de déclenchement de la déflation (14/12/10 → 15/12/10, adapté à la limite de circulation de 1,65 milliard) |
| E-7 | Remplacez toutes les citations externes par des sources vérifiables (supprimez les articles SSRN invérifiables) |

---

## Annexe D : Index rapide des termes

Une explication complète de chaque terme est notée dans le bloc de commentaires [Termes de ce chapitre] à la fin du chapitre où il apparaît pour la première fois. Cet index répertorie tous les termes et leurs chapitres par ordre alphabétique pour une navigation rapide.

| Terminologie | Chapitre de définition |
|------|------------|
| AMM (teneur de marché automatisé) | Chapitre 4 |
| BFT (tolérance aux pannes byzantine) | Chapitre 4 |
| CAC (Coût d'Acquisition Client) | Chapitre 5 |
| CEX (échange centralisé) | Chapitre 4 |
| SDK Cosmos | Chapitre 4 |
| CosmWasm | Chapitre 4 |
| DAO (Organisation Autonome Décentralisée) | Chapitre 2 |
| DCF (Méthode des Flux de Trésorerie Actualisés) | Chapitre 9 |
| DePIN (réseau d'infrastructure physique décentralisé) | Chapitre 2 |
| DEX (échange décentralisé) | Chapitre 4 |
| EBITDA (bénéfice avant intérêts, impôts et amortissements) | Chapitre 9 |
| Frais de gaz | Chapitre 4 |
| IBC (Protocole de communication inter-chaînes) | Chapitre 3 |
| IPFS (système de fichiers interplanétaire) | Chapitre 4 |
| KYC (Connaissez votre client) | Chapitre 3 |
| LIGHT (jeton natif) | Chapitre 4 |
| LP (Fournisseur de Liquidités) | Chapitre 5 |
| PE du marché intermédiaire inférieur (capital-investissement du marché intermédiaire en aval) | Chapitre 2 |
| Arbre Merkle | Chapitre 4 |
| MiFID II (Directive européenne sur les marchés d'instruments financiers II) | Chapitre 3 |
| MLM (marketing multi-niveaux) | Chapitre 3 |
| PII (informations personnellement identifiables) | Chapitre 3 |
| PoC (Preuve de contribution) | Chapitre 4 |
| PoS (preuve de participation) | Chapitre 4 |
| PoW (preuve de travail) | Chapitre 4 |
| Pré-IPO | Chapitre 9 |
| PWA (Application Web Progressive) | Chapitre 4 |
| Reg D / Reg S (Règlement D/S du U.S. Securities Act) | Chapitre 3 |
| Tranchant | Chapitre 4 |
| SPV (véhicule à usage spécial) | Chapitre 2 |
| TGE (événement de génération de jetons) | Chapitre 5 |
| TWAP (Prix moyen pondéré dans le temps) | Chapitre 4 |
| Exécution TWAP (ordres de rachat et de fractionnement) | Chapitre 9 |
| VWAP (Prix moyen pondéré par le volume) | Chapitre 5 |
| wLIGHT (LUMIÈRE encapsulée) | Chapitre 5 |
| ZK-KYC (KYC à preuve zéro) | Chapitre 3 |
| Sous-jeton | Chapitre 5 |
| Spirale de la mort | Chapitre 5 |
| Réduire de moitié | Chapitre 5 |
| Trésor (Trésor) | Chapitre 5 |
| Vente aux enchères néerlandaise | Chapitre 5 |
| Oracle | Chapitre 4 |

---

**Fin du livre blanc complet**

**Déclaration de droits d'auteur :** Ce document est un document communautaire open source et peut être librement reproduit, mais le contenu complet doit être conservé.

---

# Annexe : Paramètres et adresses vérifiés sur le réseau principal (V2.4 live)

## A. §4.5 Paramètres mesurés économiques du gaz
- formule de prix minimum du gaz : `(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas` ; TransferUsdTarget actuel = 0,001 $, UsdPerLight = 0,05 $, RefTransferGas = 100 000 → **0,2 ulight/gas**
- Mesure de distribution (frais totaux 300 000 ulight) : destruction 150 000 (50 %)/trésor 60 000 (20 %)/vérificateur 90 000 (30 %), correspondance exacte
- Adresse de destruction : `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (adresse morte déterministe)
- Trésorerie : contrat `treasury_multisig` (multi-signature 3/5 ; la requête `signers` sur la chaîne renvoie 5 signataires, le seuil lui-même n'est pas dans l'interface de requête)

## B. Adresse principale du contrat
Voir le référentiel `docs/MAINNET_STATUS.md` (light_token / mining_reward / gouvernance / treasury_multisig / oracle_twap / vesting et 10 autres contrats).

## C. Élimination de la dénomination (mise) héritée
Genesis Mismatch mint_denom=la mise a été réinitialisée à zéro et les émissions supplémentaires ont été arrêtées ; la mise existante (environ 2,56e11 micro-unités) est laissée sans objet, et le plan de cession (échange/destruction) est en attente de propositions de gouvernance et n'affectera pas le modèle économique ulight.

## D. §4.4 acquisition en direct
Voûte 250 000 000 LUMIÈRE, 3 horaires indépendants : 75M (falaise 0)/ 100M (falaise 1 an)/ 75M (falaise 2 ans), déjà sur la chaîne.

## E. Pratiques de sécurité
- Le réseau principal est mis à niveau vers la gouvernance x/upgrade + coordination élevée de tous les nœuds dans le même bloc + chien de garde d'échange automatique, exécuté après la répétition de bout en bout du réseau de test
- Les graines de clé d'accès stockent uniquement le texte chiffré ; Les fragments Shamir ne les stockent pas localement.
- Seuil de soumission de racine d'extraction de contrat 5 (seuil de mesure réel = 5 pour chaque événement `submit_root` sur la chaîne ; actuellement 5 comptes autorisés sont en train de signer et 7 sièges sont l'objectif de conception) ; pour l'anti-sorcière/anti-triche, voir §4.8
