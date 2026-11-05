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

Le minage de Bitcoin a fait preuve d’un haut degré de concentration :

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

**Canal de devises Fiat (agrégation de services tiers) :** Le protocole lui-même n'exploite pas de services légaux de dépôt et de retrait de devises, mais la plateforme Web intègre des canaux tiers conformes (MoonPay, Ramp Network, Transak, etc.), couvrant les principaux marchés d'Amérique du Nord, d'Europe, d'Asie du Sud-Est et d'Amérique latine ; l'agrégation locale du marché P2P couvre l'Afrique et l'Asie du Sud ; les retraits prennent en charge les méthodes de paiement locales telles que GCash, M-Pesa, Pix et GrabPay.

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

Architecture de vérification à trois niveaux : (1) défi d'échantillonnage croisé aléatoire du vérificateur (5 % de nœuds toutes les 10 minutes, temps de réponse de 30 secondes) ; (2) Vérification mutuelle par les pairs P2P (8 à 16 pairs enregistrent indépendamment le volume d'échange de données, prennent la médiane) ; (3) Agrégation Merkle en chaîne (chaque bloc soumet le score de contribution Root, les utilisateurs peuvent s'auto-vérifier via Merkle Proof). Défaut de contester 3 fois de suite → le score de la journée sera remis à zéro ; un total de 5 fois en 7 jours → un contrôle anti-triche sera déclenché.

### 4.9 Gestion du portefeuille et des clés

Architecture à trois niveaux : (1) Portefeuille intelligent intégré (Passkey/WebAuthn, aucune phrase mnémonique requise, cible plus de 80 % des utilisateurs) ; (2) Portefeuille de récupération sociale (3-5 restaurateurs, partage de Shamir, confirmation majoritaire des 2/3) ; (3) Portefeuille auto-hébergé (phrase mnémonique BIP-39 + portefeuille matériel compatible). Les frais de gaz pour les 100 premières transactions des nouveaux utilisateurs seront payés par le fonds écologique (modèle Paymaster).

### 4.10 Prix Oracle

Le TWAP en chaîne (prix moyen pondéré dans le temps sur 30 jours du pool LIGHT/USDC) est la principale source de prix ; 3+ agrégations DEX/CEX externes sont complétées (les validateurs soumettent en rotation, prennent la médiane) ; les écarts > ± 15 % déclenchent des indicateurs d'exception ; les écarts de bloc uniques > 5 % ne sont pas inclus dans le TWAP (manipulation de prêt anti-flash) ; repli vers un TWAP pur en chaîne lorsque tous les oracles externes échouent.

### 4.11 Architecture du module de contrat intelligent

10 contrats principaux : light_token, mining_reward, gouvernance, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. Le contrat principal doit faire l'objet d'une vérification formelle avant TGE.

### 4.12 Mise à niveau du protocole et gouvernance de la chaîne

Mise à niveau de niveau 4 : ajustement des paramètres L1 (vote de gouvernance 24-72h) → migration du contrat L2 (proposition majeure + audit + délai de 72h) → changement de consensus L3 (66% réussi + 2/3 signaux du validateur + période de protection de la fourche de 7 jours) → réparation d'urgence L4 (suspension du comité fantôme + correctif multi-signatures + ratification de 72h).

> **[Terminologie dans ce chapitre]**
> **Cosmos SDK** : un cadre de développement modulaire de blockchain qui permet aux développeurs d'assembler des chaînes publiques personnalisées comme des blocs de construction. Plusieurs chaînes de production (comme Cosmos Hub et Osmosis) ont vérifié sa maturité.
> **Tendermint PoS** (Proof of Stake, Proof of Stake) : Un mécanisme de consensus dans lequel les validateurs obtiennent le droit de produire des blocs en promettant des tokens (plutôt que de rivaliser pour la puissance de calcul). Fournit une « finalité instantanée » : une fois qu’un bloc est validé, il ne peut pas être annulé.
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

### 5.4 战略运营基金（2.5亿枚）

| 子类别 | 占比 | 数量 | 对象 | 释放规则 |
|--------|------|------|------|---------|
| 服务换代币 | 50% | 1.25亿枚 | 开发公司、审计机构、律所、验证者运营商 | 12月cliff + 36月线性；以LIGHT支付服务费的30-50% |
| 战略融资 | 30% | 7,500万枚 | 2-3家DePIN/Cosmos生态基金或消费行业战略方 | Pre-TGE以$0.03-$0.05出售（募集$225-375万）；12月cliff + 24月线性；单投资者≤总量2% |
| 核心贡献者 | 20% | 5,000万枚 | 3-5名发起人/核心建设者 | 12月cliff + 36月线性；按季度里程碑考核释放；任期内不得出售 |

**战略投资者要求：** 必须提供非资金贡献（deal flow、验证者服务、合规资源之一），纯财务投资者不接受。

**监管合规：** Pre-TGE sale采用Reg S（非美国投资者）+ Reg D Rule 506(c)（美国合格投资者）双轨豁免。

**核心贡献者披露规则：** 仅披露总额（5,000万枚=总量2%）和释放规则，不公开个人姓名和单人额度。角色类别公开：技术/投资/合规/社区。

### 5.5 挖矿产出与减半计划

**推导：** 2A = 10亿 → A = 5亿（第一纪元）。日释放 = 5亿÷730 = 684,932枚 ≈ 68.49万/天。每区块 = 684,932÷49,371 ≈ 13.87 LIGHT。

**注意：** 每区块奖励池为全网共享，其中5%划拨验证者（3.42万/天），95%分配轻节点矿工（65.07万/天）。

| 纪元 | 时间 | 产出总量 | 日释放量 | 每区块奖励池 |
|------|------|---------|---------|------------|
| 第1纪元 | 0—24月 | 5亿枚 | ≈68.49万 | ≈13.87 LIGHT |
| 第2纪元 | 25—48月 | 2.5亿枚 | ≈34.25万 | ≈6.93 LIGHT |
| 第3纪元 | 49—72月 | 1.25亿枚 | ≈17.12万 | ≈3.47 LIGHT |
| 第4纪元 | 73—96月 | 6,250万枚 | ≈8.56万 | ≈1.73 LIGHT |
| 第5纪元 | 97—120月 | 3,125万枚 | ≈4.28万 | ≈0.87 LIGHT |

**校验：** 5+2.5+1.25+0.625+0.3125+… = 5×2 = 10亿 ✓。97%在前10年完成。

### 5.6 用户收益参考模型

| 网络规模 | 人均日收益 | 月收益 | 年收益 | 满加成(1.44x)月收益 |
|---------|-----------|--------|--------|-------------------|
| 1万矿工（种子期） | ≈65.07 | ≈1,952 | ≈23,751 | ≈2,811 |
| 10万矿工（成长期） | ≈6.51 | ≈195.2 | ≈2,375 | ≈281.1 |
| 100万矿工（规模期） | ≈0.65 | ≈19.5 | ≈237.5 | ≈28.1 |

**合伙人级（50邀请，20%分成，满加成）：**

| 网络规模 | 自身(含加成) | 邀请分成 | 日综合 | 月综合 |
|---------|------------|---------|--------|--------|
| 1万矿工 | ≈93.7 | ≈650.7 | ≈744.4 | ≈22,332 |
| 10万矿工 | ≈9.37 | ≈65.07 | ≈74.44 | ≈2,233 |
| 100万矿工 | ≈0.94 | ≈6.51 | ≈7.45 | ≈223.4 |

### 5.7 空投增长计划

**经济模型：** 空投总预算 = 目标触达用户 × 人均空投 × (1+浪费率) = 100,000 × 150 LIGHT × 1.3 ≈ 1,950万枚（获取类）+ 3,550万枚（生态类）= **5,500万枚**（占生态基金4亿的13.75%）。

| 空投类型 | 触发条件 | 单次额度 | 预算 |
|---------|---------|---------|------|
| 首挖空投 | 首次完成4小时有效挖矿 | 50 LIGHT | 1,500万枚 |
| 地理扩张 | 目标市场用户完成ZK-KYC | 100 LIGHT | 1,000万枚 |
| Learn-to-Earn | 完成教育模块+测验 | 30 LIGHT | 600万枚 |
| 治理首投 | 首次参与投票 | 20 LIGHT | 300万枚 |
| 流动性提供 | LP注入≥$50锁仓30天 | 200 LIGHT | 1,000万枚 |
| 内容创作 | 经社区验证的教程/翻译 | 50-200 LIGHT | 600万枚 |
| 合作渠道 | 通过合作方注册+首挖 | 80 LIGHT | 500万枚 |

**CAC验证：** 5,500万枚×$0.03 = $165万 ÷ 30,000留存活跃矿工 = **$55/人**（行业区间$50-200，处于低端）。学术依据：Zheng (2023) "Operation Dumbo Drop: To Airdrop or Not to Airdrop for Initial Coin Offering Success?" 证明活动绑定型空投留存率为纯空投的3-5倍。

**防滥用：** 唯一浏览器指纹+ZK-KYC；每类每地址限领1次；30天锁定期；领取后30天无链上活动自动回收。

### 5.8 双引擎飞轮与资金池

飞轮：投票→金库LIGHT销毁→USDC支付→利润回流→回购销毁→价格支撑→更多用户。

双轨制：稳定金库（USDC，利润截留）+ 弹性金库（LIGHT层，投资时销毁不流入市场）。回购采用TWAP拆单，单笔≤日均交易量5%。

### 5.9 子代币发行与交易

发行总量=投资金额÷$1；兑换价以30天VWAP为基准；兑换所得LIGHT全部销毁；分配50%赞成者/30%空投/20%运营储备（锁仓6月）。单地址分红上限15%。子代币在链内AMM交易，发行后30天锁定期，退出后标记"已清算"下架。

### 5.10 初始流动性与价格发现

**TGE（Token Generation Event，代币生成事件）安排：**

| 项目 | 方案 |
|------|------|
| 初始流动性池 | 从生态发展基金TGE释放的1.2亿枚中，划拨7,200万枚（60%）注入DEX流动性池 |
| 配对资产 | USDC（主池）、USDT（辅池） |
| 空投 | 剩余4,800万枚（40%）用于种子用户空投（见5.7节空投计划） |
| 上线交易所 | TGE后首先上线去中心化交易所（如Osmosis、JunoSwap）；第6个月起视合规情况申请中心化交易所上市 |

**荷兰式拍卖（Dutch Auction）详细机制：**

荷兰式拍卖是一种"价格由高至低递减"的定价方式。与英式拍卖（价格由低至高竞价）相反，荷兰式拍卖中卖方设定一个起始高价，价格随时间自动下降，直到买方在某个价格点提交认购。第一个使总认购额达到目标的价格即为最终开盘价。

**为什么选择荷兰式拍卖而非固定价格或英式拍卖：**

| 定价方式 | 优点 | 缺点 | 适用性 |
|---------|------|------|--------|
| 固定价格预售 | 简单 | 定价主观，过高则卖不出，过低则被机器人抢购 | 不适合（无价格发现功能） |
| 英式拍卖（竞价） | 价格发现充分 | 大额买家可策略性等待、抬价；gas war | 不适合（链上gas war排斥小额用户） |
| **荷兰式拍卖** | **自动价格发现；无需竞价（无gas war）；大小买家平等参与；防机器人（价格递减机制天然抑制抢跑）** | 需要合理设定起始价和递减速率 | **最适合（公平+高效+防操纵）** |

**LightDAO荷兰式拍卖具体参数：**

| 参数 | 设定 | 说明 |
|------|------|------|
| 拍卖标的 | LIGHT代币（从生态基金TGE释放的7,200万枚中划拨） | 拍卖所得USDC注入稳定金库 |
| 目标募集额 | **$1,500万 USDC** | $500万→稳定金库最低储备；$1,000万→初始投资资本 |
| 起始价 | $0.20/LIGHT | 高于预期均衡价，确保不会"秒光" |
| 递减速率 | 每小时下降5% | 从$0.20起，约48小时后降至$0.017（若无人认购） |
| 最低保留价 | $0.01/LIGHT | 若降至保留价仍未达目标，拍卖延期24小时或调整标的数量 |
| 认购方式 | 用户提交"我愿意以当前价格购买X USDC等值的LIGHT" | 无需竞价，系统按最终统一价格结算（多退少不补） |
| 单用户上限 | 不超过目标募集额的5%（即$75万） | 防止单一买家垄断初始筹码 |
| KYC要求 | 增强验证（税务居民身份） | 合规要求 |

**拍卖结果的资金去向：**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**价格发现保护期：** TGE后前72小时设价格波动熔断——若DEX交易价格较拍卖开盘价偏离超过±50%，暂停子代币兑换功能（不影响挖矿和转账），防止极端投机行为干扰生态启动。72小时后熔断自动解除。

**为什么$1,500万而非更低：** 初始投资资本$1,000万需支撑首年3-5笔投资（单笔$200-500万，见9.1节启动期规模）。若仅募集$500万（全部作为储备），则首年无任何可部署投资资本，飞轮无法启动。$1,500万 = 储备$500万 + 投资$1,000万，是"安全底线"与"飞轮启动"的最小可行平衡。

### 5.11 通缩机制与底线

**流通量 = 挖矿释放 + 生态释放 + 战略基金已释放 − 兑换销毁 − Gas销毁 − 回购销毁。** 投资金库8.5亿枚从未进入流通。流通量理论上限 = 10+4+2.5 = **16.5亿枚**。

| 触发条件 | 系统行为 |
|---------|---------|
| 流通量≤15亿枚 | 减速信号（极端低销毁情景） |
| 流通量≤12亿枚 | 预警公示，暂停主动销毁（基准情景约第8年） |
| 流通量≤10亿枚 | 硬停止，所有销毁永久关闭（基准情景约第11-12年） |

### 5.12 价格稳定机制（防死亡螺旋）

**核心原则：** LightDAO 不干预日常市场价格发现。协议仅在极端下跌情形下调整自身参数，以降低陷入"死亡螺旋"的风险。

**分级逻辑：** 在不同波动环境中，同等跌幅所代表的异常程度不同。低波动市场中的大幅下跌属于更强的异常信号，需要更高强度的干预；高波动市场中的大幅下跌相对常见，可采用较轻干预。因此，干预强度与信号的异常程度正相关，而非仅取决于跌幅的绝对值。

**机制全流程表：**

| 市场状态 | 30日历史波动率 | 触发条件 | 信号等级 | 触发后执行 | 恢复条件 |
|---------|--------------|---------|---------|-----------|---------|
| 低波动 | ≤30% | 连续5日累计跌幅≥40% | I级 | 挖矿产出降至50%；销毁比例由20%提升至35%；风险参数调整公示期由72h缩短至12h；影子委员会进入激活状态（仅可依法行使临时暂停权） | 价格站上30日均线，且较触发价反弹≥80%，并连续保持10日 |
| 中波动 | 30%—60% | 连续7日累计跌幅≥50% | II级 | 挖矿产出降至50%；销毁比例由20%提升至30%；公示期缩短至24h；影子委员会进入激活状态 | 价格站上30日均线，且较触发价反弹≥60%，并连续保持7日 |
| 高波动 | 60%—100% | 连续10日累计跌幅≥55% | III级 | 挖矿产出降至75%；销毁比例由20%提升至25%；公示期缩短至48h；影子委员会进入待命状态 | 价格站上30日均线，且较触发价反弹≥40%，并连续保持5日 |
| 极端波动 | >100% | 连续10日累计跌幅≥65% | III级 | 按高波动状态的III级措施执行 | 按高波动状态的III级恢复条件执行 |

**排除条件：** 仅当同期比特币跌幅低于 LIGHT 跌幅的50%时，上述机制方可触发，以排除系统性市场崩盘情形（即：若BTC同期也暴跌，则属于市场整体事件，不单独对LIGHT启动干预）。

**恢复逻辑说明：** 反弹要求与持续时间随异常等级递减：I级要求最高反弹幅度（80%）和最长确认时间（10日），III级要求相对较低（40%/5日）。该安排符合"异常信号越强、干预越强、恢复确认越严格"的递进逻辑。

**波动率与价格数据来源：** 30日历史波动率和累计跌幅均由链上价格预言机（见4.10节）提供，以每日UTC 00:00区块的TWAP快照为计算基准，不依赖任何外部数据源。

### 5.13 收益可持续性压力测试

| 压力情景 | 假设条件 | 协议应对 | 最坏结果 |
|---------|---------|---------|---------|
| 全部投资失败 | 所有被投企业亏损或退出失败 | 保险基金（利润10%计提）覆盖部分损失；稳定金库储备（≥$800万）维持运营；暂停新投资直至社区重新评估 | 子代币持有者无法获得分红；LIGHT价格承压但不归零（挖矿和治理功能持续运行） |
| 市场暴跌80% | LIGHT价格较峰值下跌80% | 触发防死亡螺旋机制（II级或III级）；挖矿产出削减50-75%；销毁比例提升；影子委员会可暂停高危操作 | 用户收益缩水但网络持续运行；恢复条件达成后机制自动解除 |
| 主要市场监管禁令 | 某大国全面禁止加密资产 | 前端切换 IPFS 镜像保持可访问；链上资产与已有用户权益不受影响；仅在法律强制范围内调整第三方服务可用性；SPV在开曼群岛运营不受单一国家管辖 | 该区域用户增长停滞；全球其他区域不受影响 |
| 用户大规模流失 | 活跃矿工下降超70% | BaseReward自动重新分配（分母缩小→留存用户人均收益上升）；邀请激励加权吸引回流；治理门槛临时下调（5.14节动态机制） | 网络安全性下降但不会停链（Tendermint BFT容忍<1/3验证者离线） |
| 智能合约重大漏洞 | 核心合约被发现可利用漏洞 | 多签紧急暂停资金流出（72小时时间锁提供响应窗口）；发起备用合约迁移投票（L4级紧急修复，见4.12节）；保险基金覆盖用户损失 | 部分资金可能受损；迁移完成后恢复正常运营 |

### 5.14 代际平衡机制

治理门槛动态调整：每新增100万累计活跃矿工，提案门槛自动下调5%（下限2,500 LIGHT）。

> **【本章术语】**
> **TGE**（Token Generation Event，代币生成事件）：代币首次通过智能合约创建并分发的时点，通常伴随初始流动性池建立、荷兰式拍卖定价和首次公开交易。类似于传统金融中的IPO，但不涉及证券交易所上市。
> **减半**（Halving）：挖矿产出每隔固定周期（LightDAO为2年/730天）自动减少50%的机制。目的是制造渐进稀缺性——随着时间推移，新增供应越来越少，若需求不减则价格获得支撑。比特币采用每4年减半。
> **金库**（Treasury）：由多签合约锁定的代币储备，仅可通过治理决议释放。LightDAO设有两类金库：投资金库（持有LIGHT，投资执行时销毁）和稳定金库（持有USDC，用于支付投资对价和运营开支）。
> **通缩**（Deflation）：代币总供应量或流通量持续减少的过程。LightDAO通过四种机制实现通缩：投资执行销毁、子代币兑换销毁、Gas费销毁（50%）、利润回购销毁。
> **死亡螺旋**（Death Spiral）：代币价格下跌→矿工收益缩水→矿工退出→网络安全性/贡献度下降→信心进一步丧失→价格继续下跌的恶性循环。第5.12节的分级干预机制专为阻断此循环而设计。
> **子代币**（Sub-token）：每完成一次企业投资后按规则发行的SPV收益分配请求权凭证（如收购咖啡品牌→CAFE代币）。持有子代币=持有对未来利润的分配资格，不代表股东权利或公司治理权。
> **LP**（Liquidity Provider，流动性提供者）：向DEX流动性池注入等值两种资产（如LIGHT+USDC）的参与者，赚取交易手续费作为回报。LP是DEX正常运行的基础。
> **VWAP**（Volume-Weighted Average Price，成交量加权平均价格）：将一段时间内的价格按每笔交易的成交量加权平均，反映真实市场成交成本。LightDAO用30天VWAP作为子代币兑换的定价基准。
> **CAC**（Customer Acquisition Cost，用户获取成本）：获取一个有效活跃用户的平均成本。LightDAO空投计划的目标CAC为$55/留存活跃矿工（行业区间$50-200）。
> **wLIGHT**（Wrapped LIGHT，封装LIGHT）：通过跨链桥在Ethereum或Solana上发行的LIGHT等价代币，由桥合约锁定等量原生LIGHT作为1:1储备。目的是让非Cosmos生态用户也能获取和持有LIGHT。
> **荷兰式拍卖**（Dutch Auction）：一种"价格由高至低递减"的定价方式。卖方设定起始高价，价格随时间自动下降，直到买方在某个价格点提交认购。第一个使总认购额达到目标的价格即为最终成交价。优点是无需竞价（无gas war）、大小买家平等、天然防机器人抢跑。

---

## 第六章：治理机制

### 6.1 双维度投票模型

持币权重（含声誉+层级加成，总上限+40%）+ 地址数量（1地址=1票，关联地址合并）。投票权90天有效，5枚LIGHT转账可激活。声誉加成：持币满1年+15次有效投票→最高+30%。

### 6.2 动态通过率

最低通过率＝50%＋（50%－实际投票率）。投票率≥50%时简单多数。

### 6.3 提案参数

| 类型 | 保证金 | 持币投票率 | 地址投票率 | 通过率 | 执行延迟 |
|------|--------|-----------|-----------|--------|---------|
| 微型 | $100 | ≥15% | ≥20% | 动态≥55% | 24h |
| 收购型 | $500 | ≥25% | ≥30% | 动态≥60% | 72h |
| 风投型 | $500 | ≥35% | ≥40% | 动态≥60% | 72h |
| 重大 | $1,000 | ≥45% | ≥50% | 动态≥66% | 72h |
| 紧急 | $2,000 | ≥50% | ≥60% | ≥75% | 非资金6h/高危1h；资金操作仍受72h时间锁 |

### 6.4 提案生命周期

提交资格：≥5,000枚LIGHT + 连续质押30天 + 保证金。公示72h（修订≤2次）。投票7日（快速通道48h，≤50万USDC）。否决冷却90天。生效延迟24h。

**门槛说明：** 5,000枚在种子期（1万矿工）≈77天基础产出；合伙人级≈7天。治理第7月激活，早期用户有充足积累时间。

### 6.5 投票激励

参与有基础激励（均分），判断正确有额外加成（押注池50%）。押注区间5—500 LIGHT。抑制羊群效应：反对者即使"站错队"仍获基础激励。

### 6.6 成败奖惩

善意失败：退50%保证金+30天冷却。恶意失败（造假/重复）：全额没收+永久禁止。造假举证：封顶5,000 LIGHT，成立奖40%罚没金+500 LIGHT。

### 6.7 财务透明

链上实时仪表盘+季度财务报告+年度独立审计（TGE前须完成首次审计）+投资标的即时披露。

---

## 第七章：权力制衡与角色定义

### 7.1 初始监护人

权限仅限文档/格式/官网信息。任期≤24月。须指定备选监护人（连续30天无法签名→自动接管）。同时失能→48h紧急投票指定临时管理人。

### 7.2 权力转移路线图

| 阶段 | 时间 | 权限 | 投资审批 |
|------|------|------|---------|
| 创世期 | 0—6月 | 监护人（非资金类） | 监护人+社区多签3/5 |
| 过渡期 | 7—12月 | 监护人+核心贡献者联名 | 同上+核心贡献者 |
| 成熟期 | 13—24月 | 治理委员会3/5 | 常规双维度投票 |
| 自治期 | 25月+ | 全体持有者 | 同成熟期 |

### 7.3 治理委员会

五人分权（轮值主席/财务/技术/社区/密钥），季度轮换，任期6月可连任1次。竞选质押50,000 LIGHT + 100地址联名。决策≥3人且覆盖≥3职位。

**门槛说明：** 50,000枚在种子期≈合伙人67天（2.2月）；成长期≈672天（22月）。委员会第13月首选举，早期合伙人可达。

### 7.4 影子委员会

仅限"违法/制裁/重大欺诈"临时暂停。72h内须全体追认（反对>60%→解除）。连续2次被否决→自动弹劾解散。

### 7.5—7.6 竞选验证与密钥预案

SimHash>80%取消资格；AI内容须补充说明；缺席质询扣20%得票。密钥分片备份+季度健康检查+7天公示判定+投票更换。

---

## 第八章：信任与安全机制

### 8.1 五大安全机制

时间锁72h（紧急提案不可豁免资金操作）；多签3/5；季度轮换≤2届；造假罚没100%；全交易上链。

### 8.2 保险基金

成功投资利润的**10%**计提。理赔须独立报告+DAO 66%赞成+单次≤池20%。补充来源：造假罚没金的30%。定位"部分缓冲"非全额保障。

### 8.3 极端预案

监管黑天鹅→IPFS+移除管理员权限；欺诈→影子委员会暂停（72h追认）+保险基金+SPV仲裁；死亡螺旋→5.12节机制；合约漏洞→多签暂停+迁移投票；验证者集体作恶→BFT容忍<1/3，超过则链暂停+紧急投票迁移。

---

## 第九章：投资运营与退出策略

### 9.1 投资标的筛选与规模

**投资规模分阶段成长轨迹（公式：金库剩余×15%×LIGHT价格）：**

| 阶段 | LIGHT价格 | 金库初始期单笔上限 | 适配标的 | 行业对标 |
|------|----------|-----------------|---------|---------|
| 启动期(Y1-2) | $0.02—$0.05 | $255万—$637万 | 单店/小型连锁、天使轮 | 微型PE |
| 成长期(Y3-5) | $0.05—$0.30 | $637万—$3,825万 | 区域连锁30-200店、Seed-A轮 | Lower Middle Market PE |
| 成熟期(Y5-8) | $0.30—$1.00 | $3,825万—$1.275亿 | 跨国连锁/中型科技、B-C轮 | Middle Market PE |
| 规模期(Y8+) | $1.00+ | $1.275亿+ | 大型收购、Pre-IPO | 大型PE/成长期VC |

### 9.2 投资决策流程

项目发现（≥5,000 LIGHT）→独立尽调→72h公示→双维度投票→24/72h执行。

### 9.3 退出与利润分配

年度分红：**40%**子代币持有者 / **30%**稳定金库 / **20%**回购LIGHT销毁 / **10%**保险基金。
退出收益：**70%**稳定金库 / **30%**回购销毁。

### 9.4 投资纪律

| 规则 | 内容 |
|------|------|
| 单笔销毁上限 | 金库剩余×15%（初始8.5亿×15%=1.275亿枚） |
| 单一标的 | ≤金库总价值25% |
| 行业集中 | ≤组合40% |
| 地域集中 | ≤组合30% |
| 稳定金库储备 | TGE时$500万（拍卖），第24月前达$800万 |
| 冷静期 | 连续2次失败→180天 |

**金库容量：** 8.5亿枚×$0.10=$8,500万（初始总容量）；×$0.30=$2.55亿；×$1.00=$8.5亿。15%单笔上限使投资节奏与价格正相关。

> **【本章术语】**
> **EBITDA**（Earnings Before Interest, Taxes, Depreciation and Amortization，息税折旧摊销前利润）：衡量企业核心经营盈利能力的指标，排除了财务结构（利息）、税务政策（税）、会计选择（折旧/摊销）的干扰，便于跨企业、跨行业比较。EBITDA margin = EBITDA ÷ 营业收入。
> **DCF**（Discounted Cash Flow，现金流折现法）：将企业未来预期现金流按一定折现率换算为当前价值的估值方法。适用于现金流稳定的成熟企业（如消费连锁），不适用于尚无盈利的早期科技公司。
> **IPO**（Initial Public Offering，首次公开募股）：企业首次在证券交易所公开发行股票并上市交易。对LightDAO而言，被投企业IPO是增长引擎标的的主要退出路径之一。
> **Pre-IPO**：企业在正式上市前的最后一轮私募融资，通常估值已接近上市后水平，风险低于早期轮次但回报倍数也较低。
> **TWAP执行**（Time-Weighted Average Price Execution）：将大额回购订单拆分为多笔小额订单，在一段时间内均匀执行，以避免单笔大单对市场价格造成冲击。LightDAO规定单笔回购不超过日均交易量的5%。

---

## 第十章：路线图

| 阶段 | 时间 | 核心目标 | 关键里程碑 | 前置条件 |
|------|------|---------|-----------|---------|
| 筹备期 | 2026年Q4 | 法律实体+团队+资金到位 | 开曼/BVI实体注册完成；技术合伙人或开发团队签约；战略投资者意向确认（2-3家）；启动资金≥$15万到位 | 创始人确定身份公开方式；完成BP和Pitch Deck |
| 开发期 | 2027年Q1—Q2 | 核心系统开发 | 10个智能合约模块开发完成；PWA前端开发完成；7个验证者测试网部署；内部Alpha测试通过 | 开发团队到位；需求文档（技术Spec）定稿 |
| 审计与测试期 | 2027年Q3 | 安全性与合规性验证 | 独立安全审计报告发布（≥1家顶级机构）；法律合规意见书发布（MLM+证券法）；5万并发压力测试通过；反作弊系统误报率<2%；治理投票演练完成 | 合约开发冻结（Code Freeze）；审计费用到位 |
| TGE与主网上线 | 2027年Q4 | 代币发行+网络启动 | 荷兰式拍卖完成（目标$1,500万）；主网上线（≥10验证者）；挖矿平台公开开放；DEX流动性池建立；种子空投发放 | 审计通过；验证者≥7（硬性底线）；拍卖合约部署 |
| 信仰构建期 | 2028年Q1（TGE后第1-3月） | 3—5万种子用户 | 活跃矿工突破3万；首次治理投票演练；社区多语言频道建立（英/中/西/葡/菲）；首份月度社区报告发布 | TGE完成；社区运营团队到位 |
| 价值锚定期 | 2028年Q2—Q3（TGE后第4-9月） | 首笔投资+过渡期治理 | 首个投资提案通过（第4-6月内适用创世期多签审批；第7月起适用过渡期联名审批）；首笔SPV交割完成；验证者开放竞选（第7月起）；首份季度财务报告发布 | 稳定金库USDC≥$500万；投资标的尽调完成 |
| 治理成熟期 | 2028年Q4—2029年Q1（TGE后第10-15月） | 委员会选举+去中心化过渡 | 治理委员会首次选举（第13月）；进入成熟期（委员会3/5决策）；wLIGHT跨链桥上线；CEX上市申请提交；开发者资助计划启动 | 活跃矿工≥10万；≥100个地址联名候选人 |
| 生态扩张期 | 2029年Q2起（TGE后第16月+） | 规模化复制 | 活跃矿工突破20—50万；完成2—3笔投资；首笔利润回流验证；LIGHT回购销毁启动 | 治理委员会运转正常；投资模式已验证 |
| 成熟运营期 | 2029年Q4起（TGE后第25月+） | 飞轮自转+完全自治 | 进入自治期（全体持有者重大提案）；投资组合累计部署≥$3,000万；通缩数据公开可验证 | 治理完全去中心化 |

**路线图设计原则：**

- **审计先于TGE：** 绝不在未完成独立安全审计的情况下发行代币。这是用户资金安全的基本保障。
- **验证者先于用户：** 主网上线时验证者≥10个（BFT容错f≥3），确保网络不会因单点故障停摆。
- **投资先于扩张：** 首笔投资成功并产生可验证的利润回流后，方进入规模化扩张。避免"先圈人后找项目"的本末倒置。
- **时间缓冲：** 每个阶段预留20-30%时间缓冲。技术开发、审计修复、法律流程均可能超预期，路线图不应是"最乐观情景"。

**与白皮书发布日（2026年8月4日）的关系：** 白皮书于2026年8月发布，作为项目愿景和技术设计的公开声明。实际执行从2026年Q4开始（筹备期），TGE目标为2027年Q4。白皮书发布与TGE之间约14个月的间隔用于团队组建、开发、审计和合规准备。

---

## 第十一章：社区文化与开发者生态

### 11.1 四条价值观

- **透明优于完美** ——有瑕疵的公开，胜过完美的隐藏。所有金库流动、投资决策、治理投票永久上链可查。
- **渐进优于激进** ——小步快跑，持续迭代。首笔投资从$200-500万起步，验证模式后再扩大规模。
- **责任优于权利** ——权力与义务对等。治理委员会成员须质押50,000 LIGHT并公开施政纲领，失职则罚没。
- **多元优于同质** ——不同声音是系统的免疫力。双维度投票（持币+地址）确保巨鲸和散户都有话语权。

### 11.2 陪审团制度

| 维度 | 规则 |
|------|------|
| 组成 | 随机抽取12名持有≥10,000枚LIGHT且无违规记录的用户 |
| 任期 | 30天，届满后重新随机抽取 |
| 职责 | 审理反作弊处罚申诉、提案造假指控、社区争议 |
| 流程 | 被处罚用户可在72小时内提交证据；陪审团须在48小时内作出裁决 |
| 裁决标准 | 12人中≥8人（2/3多数）同意方可维持或撤销处罚 |
| 回避 | 与当事方存在邀请关系或同一IP段的陪审员自动替换 |
| 报酬 | 任期内每日获得5 LIGHT的陪审服务补贴（从生态基金列支） |

### 11.3 开发者生态计划

| 模块 | 内容 | 资金来源 | 申请方式 |
|------|------|---------|---------|
| 开发者资助（Grants） | 面向在LightDAO链上构建dApp、工具、基础设施的团队，单个资助$5—50万等值LIGHT | 生态发展基金（线性释放期二） | 提交提案→技术审核官评估→治理投票（微型提案流程） |
| SDK与API | 提供JavaScript/TypeScript SDK、REST API、WebSocket接口，降低第三方开发门槛 | 技术审核官主导开发 | 开源，GitHub公开 |
| 黑客松 | 每季度举办一次线上黑客松，奖金池$10万等值LIGHT | 生态发展基金 | 公开报名，无门槛 |
| 漏洞赏金（Bug Bounty） | 核心合约漏洞赏金计划，单个有效漏洞奖励$1,000—$50,000（按严重度分级） | 保险基金 + 生态发展基金 | 通过Immunefi或自建平台提交 |
| CosmWasm合约市场 | 鼓励第三方部署智能合约，Gas费收入的20%回流生态金库支持开发者 | Gas费分配（见4.5节） | 自动，无需申请 |

### 11.4 多语言与本地化策略

| 维度 | 规划 |
|------|------|
| 平台语言 | 首发支持英语、中文、西班牙语、葡萄牙语、菲律宾语；第6个月起增加法语、阿拉伯语、斯瓦希里语、印尼语 |
| 治理语言 | 提案和竞选纲领接受任何语言提交，系统提供机器翻译+社区人工校对 |
| 社区运营 | 按语言设立独立社区频道（Discord/Telegram），各频道配备本地化社区联络志愿者 |
| 文档翻译 | 白皮书及核心文档由社区翻译志愿者完成，翻译贡献计入"内容贡献"行为加成（5%） |
| 本地化资助 | 生态发展基金中预留10%（4,000万枚）专项用于本地化社区建设和翻译激励 |

---

## 第十二章：团队与顾问

### 12.1 核心角色定义

| 角色 | 职责 | 背景要求 | 披露方式 |
|------|------|---------|---------|
| 初始监护人/项目发起人 | 部署初始合约、维护文档、协调早期运营 | 区块链行业≥3年经验，有智能合约部署或DeFi协议运营记录 | TGE前公开真实身份或提供第三方身份验证报告（如公证人签名+链上消息验证） |
| 技术负责人 | 合约架构设计、开发团队管理、审计对接 | Cosmos SDK/CosmWasm开发经验，有生产链部署记录 | 同上 |
| 投资负责人 | 标的筛选、尽调协调、SPV设立、退出管理 | 私募股权/风险投资行业经验，有已完成退出案例 | 同上 |
| 合规顾问 | 法律架构设计、监管对接、MLM合规意见 | 持有美国/欧盟/开曼执业资格的律师 | 公开律所名称（个人姓名除非本人同意否则不公开） |

### 12.2 顾问委员会

- 由3—5名独立顾问组成，涵盖：DePIN技术、跨境投资合规、社区运营、消费行业；
- 顾问以LIGHT代币形式获得咨询报酬（从战略运营基金"服务换代币"部分列支），锁仓12个月；
- 顾问名单在TGE前公开，并接受社区质询（去中心化文字质询会，见7.5节）；
- 顾问不得同时担任治理委员会成员（利益冲突隔离）。

### 12.3 团队承诺与约束

| 约束 | 规则 |
|------|------|
| 代币锁仓 | 核心团队持有的LIGHT（含战略运营基金分配）须锁仓12个月，解锁后线性释放36个月 |
| 出售限制 | 初始监护人在任期内（≤24个月）不得出售通过任何渠道获得的LIGHT（含空投、奖励、薪酬） |
| 利益冲突 | 团队成员的利益冲突须在任命时完整披露（是否持有其他DAO代币、是否与潜在投资标的存在关联） |
| 未披露后果 | 未披露利益冲突一经查实，永久禁止参与治理，已解锁代币的50%罚没至保险基金 |
| 替换机制 | 核心角色离职或失能时，由治理委员会（成立前由初始监护人+备选监护人）指定继任者，须经社区公示72小时无异议 |

### 12.4 核心贡献者薪酬（战略运营基金20%部分）

- 总额：5,000万枚LIGHT（占总量2%）
- 覆盖人数：3—5人
- 释放规则：12月cliff + 36月线性（即第13个月起每月释放约115.7万枚）
- 里程碑绑定：每季度由治理委员会（成立前由初始监护人+独立第三方）确认里程碑达成后方可释放当季额度
- 披露规则：仅披露总额和释放规则，不公开个人姓名和单人额度（保护隐私，同时通过链上多签地址可验证总额不超发）

---

## 第十三章：风险提示与免责声明

### 13.1 风险提示

| 风险类型 | 说明 | 缓解措施 |
|---------|------|---------|
| 市场风险 | LIGHT价格可能出现大幅波动，历史价格不代表未来表现。TGE初期流动性有限，价格可能剧烈波动 | 荷兰式拍卖公平定价；TGE后72小时±50%熔断；防死亡螺旋四级干预机制 |
| 项目风险 | 投资标的可能亏损，风投项目可能失败，本金可能全部损失。PE/VC行业历史平均失败率约50-70%（单笔） | 双引擎分散（70%现金流+30%增长）；单一标的≤25%；行业≤40%；地域≤30%；保险基金10%计提 |
| 技术风险 | 智能合约可能存在未被发现的漏洞；浏览器兼容性可能影响挖矿体验；跨链桥可能被攻击 | TGE前独立审计+形式化验证；Bug Bounty $1K-$50K；72小时时间锁；多签暂停机制 |
| 监管风险 | 各国及地区监管政策可能发生变化，可能导致部分功能受限或特定区域用户无法参与 | 开曼 SPV 架构；默认零验证（核验由持牌第三方在其服务侧承担）；前端 IPFS 镜像抗审查；不面向特定国家营销 |
| 流动性风险 | 子代币在早期可能缺乏足够交易深度；LIGHT在TGE初期可能面临抛售压力 | 子代币AMM初始流动性（发行量6%）；30天转让锁定期；团队/投资者12月cliff+36月线性 |
| 稀释风险 | 随活跃矿工增长，人均挖矿收益将自然稀释（BaseReward分母增大） | 设计意图：早期参与者承担更高风险获得更高回报；后期用户可通过邀请分成加速积累；治理门槛动态下调 |
| 运营风险 | 被投企业经营管理可能不达预期；SPV运营依赖第三方董事；投资团队可能流失 | SPV章程约束+独立董事；DAO可投票更换董事；SIAC/ICC仲裁条款；关键人保险（探索中） |
| 跨链桥风险 | wLIGHT跨链桥由第三方运营，桥合约漏洞可能导致资产损失（历史上跨链桥是最大单点损失来源） | 桥上线前独立审计；桥接资产不超过总供应量5%；风险披露；用户可选择仅使用原生链 |
| 验证者风险 | 验证者集体离线或作恶可能导致链暂停出块，所有用户操作（挖矿、投票、转账）暂时不可用 | Tendermint BFT容忍<1/3作恶；验证者≥21个（f=6）；Slashing惩罚；紧急迁移投票机制 |

### 13.2 免责声明

- LIGHT 及子代币不是证券，不具有内在价值，价格可能归零。本白皮书不构成任何形式的证券发行文件、投资要约或投资建议。
- 协议收入分配取决于底层资产的实际经营表现，历史数据不代表未来收益。任何关于投资回报的描述均为前瞻性估计，非承诺。
- 用户须自行承担私钥丢失、泄露导致的全部损失，协议不提供找回服务。使用第一层（Passkey）或第二层（社交恢复）钱包可降低此风险，但不消除。
- 本协议面向全球用户（受限于适用法律法规），用户应自行确认其所在司法辖区对加密资产、DAO组织及SPV收益凭证的法律态度，并确保参与行为合法合规。
- 本白皮书中的前瞻性陈述（包括路线图、收益模型、通缩估算、投资规模预测）均为基于当前假设的预测，实际结果可能因市场、技术、监管、团队执行等因素而重大偏离。
- 邀请激励为单层分成机制，不构成多层次营销或金字塔计划。但用户仍应自行确认其所在司法辖区对推荐奖励的法律态度。
- 参与LightDAO生态的最低年龄为18岁（或所在司法辖区的法定成年年龄，以较高者为准）。未成年人不得参与挖矿、治理或投资。

---

## 附录A：关键参数汇总表

| 类别 | 参数 | 数值 |
|------|------|------|
| 发行 | 总量 | 25亿枚，永不增发 |
| 发行 | 挖矿 | 40% = 10亿枚 |
| 发行 | 投资金库 | 34% = 8.5亿枚 |
| 发行 | 生态基金 | 16% = 4亿枚 |
| 发行 | 战略运营 | 10% = 2.5亿枚（服务50%/融资30%/贡献者20%） |
| 发行 | 减半周期 | 每2年 |
| 发行 | 第一纪元日释放 | ≈68.49万枚（矿工95%=65.07万，验证者5%=3.42万） |
| 发行 | 每区块奖励池 | ≈13.87 LIGHT |
| 挖矿 | 贡献权重 | 带宽40%/会话30%/验证20%/稳定10% |
| 挖矿 | 满加成 | 1.44倍 |
| 邀请 | 布道者/大使/合伙人 | 3人10%+100L / 10人15%+500L+5% / 50人20%+2500L+10% |
| 行为 | 四项×5% | 上限20% |
| Gas费 | 定价机制 | USD等值锚定，每24h由预言机自动换算为LIGHT数量 |
| Gas费 | 普通转账 | $0.001等值（@$0.05时=0.02 LIGHT） |
| Gas费 | 治理投票 | $0.005等值（@$0.05时=0.10 LIGHT） |
| Gas费 | 分配规则 | 50%销毁 / 30%验证者 / 20%生态金库 |
| 通缩 | 减速/预警/底线 | ≤15亿/≤12亿/≤10亿（流通量） |
| 通缩 | 理论上限 | 16.5亿（10+4+2.5，金库8.5亿永不流通） |
| 治理 | 提案门槛 | ≥5,000 LIGHT + 30天质押 |
| 治理 | 委员会质押 | 50,000 LIGHT + 100地址 |
| 治理 | 陪审团 | 10,000 LIGHT |
| 治理 | 押注 | 5—500 LIGHT |
| 治理 | 声誉加成 | 1年+15次投票→+30%（总上限+40%） |
| 投资 | 单笔上限 | 金库剩余×15%（初始1.275亿枚） |
| 投资 | 基准可部署 | 8.5亿×$0.15×75% = $9,563万≈$1亿 |
| 投资 | 利润分配(年度) | 40/30/20/10 |
| 投资 | 利润分配(退出) | 70/30 |
| 拍卖 | 目标 | $1,500万（$500万储备+$1,000万投资资本） |
| 储备 | 稳定金库 | TGE $500万→第24月$800万 |
| 保险 | 计提 | 利润10% |
| 空投 | 总预算 | 5,500万枚（生态基金13.75%），CAC≈$55/留存用户 |
| 验证者 | 初始/上限 | 21（最低10）/ 100 |
| 验证者 | 最低质押 | 500,000 LIGHT |
| 验证者 | TGE硬性底线 | ≥7个，否则不得上线 |

---

## 附录B：数值推导与校验

### B.1 挖矿产出

2A=10亿→A=5亿。日释放=5亿÷730=684,932≈68.49万。矿工池=684,932×95%=650,685≈65.07万。验证者=684,932×5%=34,247≈3.42万。每区块=684,932÷49,371≈13.87。校验：684,932×730=499,999,960≈5亿 ✓

### B.2 治理门槛可达性

10万矿工基准（6.51/天，合伙人74.44/天）：提案5,000→768天/67天；委员会50,000→7,684天(21年)/672天(22月)；陪审团10,000→1,537天(4.2年)/134天(4.5月)；押注500→77天/6.7天。

种子期（1万矿工，65.07/天，合伙人744.4/天）：提案→77天(2.5月)/6.7天；委员会→768天(25月)/67天(2.2月)；陪审团→154天(5月)/13.4天。

### B.3 通缩时间线

流通量=挖矿+生态+战略(vested)−兑换−Gas−回购。金库8.5亿永不流通。

| 年 | 累计挖矿 | 生态 | 战略 | 兑换 | Gas | 回购 | 流通量 |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2.50 | 2.80 | 0 | 0 | 0.01 | 0 | ≈5.29 |
| 2 | 5.00 | 4.00 | 0.83 | 0.05 | 0.02 | 0 | ≈9.76 |
| 3 | 6.25 | 4.00 | 1.67 | 0.20 | 0.03 | 0.05 | ≈11.64 |
| 4 | 7.50 | 4.00 | 2.50 | 0.45 | 0.04 | 0.20 | ≈13.31(峰值) |
| 5 | 8.13 | 4.00 | 2.50 | 0.80 | 0.05 | 0.50 | ≈13.28 |
| 6 | 8.75 | 4.00 | 2.50 | 1.20 | 0.06 | 0.90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2.50 | 1.60 | 0.07 | 1.40 | ≈12.49 |
| 8 | 9.38 | 4.00 | 2.50 | 2.00 | 0.08 | 1.90 | ≈11.89 |
| 9 | 9.53 | 4.00 | 2.50 | 2.40 | 0.09 | 2.30 | ≈11.24 |
| 10 | 9.69 | 4.00 | 2.50 | 2.80 | 0.10 | 2.70 | ≈10.59 |
| 11 | 9.77 | 4.00 | 2.50 | 3.10 | 0.11 | 3.00 | ≈10.06 |
| 12 | 9.84 | 4.00 | 2.50 | 3.40 | 0.12 | 3.30 | ≈9.52 |

结论：峰值Y4≈13.31亿；预警线12亿约Y8触及；底线10亿约Y11-12触及；减速线15亿仅极端低销毁情景。

---

## 附录C：审计修正日志（累计36项）

含原22项（L1-5, A1-4, D1-4, M1-8, G1-3）+ 技术架构7项（T1-7）+ 本轮经济模型优化7项：

| 编号 | 修正 |
|------|------|
| E-1 | 总量21亿→25亿（投资容量约束驱动） |
| E-2 | 分配50/30/20→40/34/16/10（新增战略运营基金10%） |
| E-3 | 荷兰拍卖$1,000万→$1,500万（初始投资资本$500万→$1,000万） |
| E-4 | 新增5.7节空投增长计划（5,500万枚，CAC $55/人） |
| E-5 | 验证者分阶段启动（测试网7→TGE最低10/目标21→开放100） |
| E-6 | 通缩触发线调整（14/12/10→15/12/10，适配16.5亿流通上限） |
| E-7 | 外部引用全部替换为可验证来源（移除不可验证SSRN论文） |

---

## 附录D：术语速查索引

各术语的完整解释已标注于其首次出现章节末尾的【本章术语】注释块中。本索引按字母顺序列出所有术语及其所在章节，便于快速定位。

| 术语 | 定义所在章节 |
|------|------------|
| AMM（自动做市商） | 第四章 |
| BFT（拜占庭容错） | 第四章 |
| CAC（用户获取成本） | 第五章 |
| CEX（中心化交易所） | 第四章 |
| Cosmos SDK | 第四章 |
| CosmWasm | 第四章 |
| DAO（去中心化自治组织） | 第二章 |
| DCF（现金流折现法） | 第九章 |
| DePIN（去中心化物理基础设施网络） | 第二章 |
| DEX（去中心化交易所） | 第四章 |
| EBITDA（息税折旧摊销前利润） | 第九章 |
| Gas费 | 第四章 |
| IBC（跨链通信协议） | 第三章 |
| IPFS（星际文件系统） | 第四章 |
| KYC（了解你的客户） | 第三章 |
| LIGHT（原生代币） | 第四章 |
| LP（流动性提供者） | 第五章 |
| Lower Middle Market PE（下游中端私募股权） | 第二章 |
| Merkle Tree（默克尔树） | 第四章 |
| MiFID II（欧盟金融工具市场指令II） | 第三章 |
| MLM（多层次营销） | 第三章 |
| PII（个人可识别信息） | 第三章 |
| PoC（贡献证明） | 第四章 |
| PoS（权益证明） | 第四章 |
| PoW（工作量证明） | 第四章 |
| Pre-IPO | 第九章 |
| PWA（渐进式Web应用） | 第四章 |
| Reg D / Reg S（美国证券法D/S条例） | 第三章 |
| Slashing（罚没） | 第四章 |
| SPV（特殊目的载体） | 第二章 |
| TGE（代币生成事件） | 第五章 |
| TWAP（时间加权平均价格） | 第四章 |
| TWAP执行（回购拆单） | 第九章 |
| VWAP（成交量加权平均价格） | 第五章 |
| wLIGHT（封装LIGHT） | 第五章 |
| ZK-KYC（零知识证明KYC） | 第三章 |
| 子代币（Sub-token） | 第五章 |
| 死亡螺旋（Death Spiral） | 第五章 |
| 减半（Halving） | 第五章 |
| 金库（Treasury） | 第五章 |
| 荷兰式拍卖（Dutch Auction） | 第五章 |
| 预言机（Oracle） | 第四章 |

---

**白皮书全文完**

**版权说明：** 本文档为开源社区文档，可自由转载，但须保留完整内容。

---

# 附录:主网已验证参数与地址(V2.4 实况)

## A. §4.5 Gas 经济实测参数
- min-gas-price 公式:`(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`;当前 TransferUsdTarget=$0.001、UsdPerLight=$0.05、RefTransferGas=100000 → **0.2 ulight/gas**
- 分配实测(总 fee 300000 ulight):销毁 150000(50%)/ 金库 60000(20%)/ 验证者 90000(30%),精确匹配
- 销毁地址:`wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu`(确定性死地址)
- 金库:`treasury_multisig` 合约(3/5 多签;链上 `signers` 查询返回 5 名签名人,阈值本身不在查询接口内)

## B. 核心合约地址
见仓库 `docs/MAINNET_STATUS.md`(light_token / mining_reward / governance / treasury_multisig / oracle_twap / vesting 等 10 合约)。

## C. 遗留 denom(stake)处置
genesis 误配 mint_denom=stake 已归零停止增发;存量 stake(约 2.56e11 微单位)为无用途遗留,处置方案(兑换/销毁)待治理提案,不影响 ulight 经济模型。

## D. §4.4 vesting 实况
vault 250,000,000 LIGHT,3 个独立 schedule:75M(cliff 0)/ 100M(cliff 1 年)/ 75M(cliff 2 年),已上链。

## E. 安全实践
- 主网升级为 x/upgrade 治理 + 全节点同块高协调 + auto-swap 看门狗,测试网端到端彩排后执行
- Passkey 种子仅密文存储;Shamir 分片本地不保存
- 合约挖矿根提交阈值 5(链上每笔 `submit_root` 事件实测 threshold=5;当前 5 个授权账户在签,7 席为设计目标);反女巫/反作弊见 §4.8
