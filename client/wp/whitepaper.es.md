> Traducción automática sin revisión humana. En caso de discrepancia, prevalece la versión original en chino.
[中文原文 / Chinese original](/whitepaper.md)

# Informe técnico de LightDAO V2.4 (versión en vivo de Mainnet del 26 de septiembre de 2026)

> Esta versión se basa en el borrador de diseño V2.0, con "implementación de la red principal en vivo" y "cambios de versión" al frente, y se adjuntan parámetros verificados en la cadena. El texto principal (Capítulos 1~12) permanece sin cambios respecto al diseño V2.0; para cualquier desviación de la situación real, prevalecerán las notas anteriores y anexos de este apartado.

## Cambios de versión (V2.0 → V2.4)
- 2026-11-04 Errata (no cambie el número de versión, sigue siendo V2.4): La bóveda original `treasury_multisig` en el apéndice "Parámetros y direcciones verificados de Mainnet" es 5/7 multisig, lo que entra en conflicto con el 3/5 del texto §7.2/§7.3/§8.1, y también entra en conflicto con la medición real en la cadena. (`{"signers":{}}` devuelve 5 direcciones, no hay 7 firmantes); se ha unificado como 3/5 según el texto y se indica que el umbral en sí no está dentro de la interfaz de consulta del contrato y solo puede ser respaldado por registros de implementación. La raíz de minería original escrita en la misma sección es "5/7 verificador multifirma", y la prueba real solo puede probar el umbral de 5 (el umbral de 115 eventos `submit_root` es 5, y el número real de cuentas firmadas es exactamente 5). La autorización de 7 asientos es el objetivo del diseño y actualmente no hay evidencia en cadena. La redacción se ha modificado en consecuencia.

1. **§4.5 Gas 经济:已主网部署并验证**。USD 锚定动态 min-gas-price 与 50% 销毁 / 30% 验证者 / 20% 金库分配于 2026-09-24 经治理提案(v2-lightfee)在高度 58627 上线,7 验证者协调切换、测试网端到端彩排后执行。主网实测:不足额 fee 被拒、足额 fee 按 50/30/20 精确分配。
2. **原生 denom 厘清**:质押/治理/Gas 均为 `ulight`(LIGHT,6 位小数,总供应 25 亿)。genesis 误配的 `stake` 通胀已于 2026-09-24 经治理提案归零(mint inflation=0),LIGHT 发行完全由 mining_reward 合约承担,杜绝双重发行;存量 stake 为待处置的遗留 denom(见附录 C)。
3. **§4.7 WebRTC 中继:已部署**。8 节点 coturn(TURN/STUN,TLS 证书 turn-*.lightdao.net)+ WSS 信令 + REST 临时凭证(HMAC-SHA1);客户端 P2P 数据通道互中继,中继字节计入 40% 带宽贡献;端到端实测经 TURN 中继传输成功。对称 NAT 走 TURN 兜底,失败降级纯验证模式(与 §4.7 一致)。
4. **§4.9 智能钱包:已上线**。Passkey/WebAuthn 无种子登录(PRF 派生密钥 + AES-GCM 密文存储,明文不落地)+ Shamir 3-of-5 社交恢复;助记词作为回退选项保留。
5. **§4.10 价格预言机:喂价已运行**。7 验证者 cron 轮值向 oracle_twap 提交 external_median(当前参考价 50000 = $0.05);链上 TWAP 待 LIGHT/USDC 流动性池建立后启用。v3 升级后 lightfee 直接读 external_median 转动态 min-gas。
6. **参数治理**:v3 升级将 lightfee 的 BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract 迁入链上 paramstore,治理参数提案可运行时调整,无需再协调升级。

## Implementación de Mainnet en vivo (2026-09-26)

- Cadena `lightdao-mainnet-1`, 7 validadores (JP/KR/SG/US/HK/FR/UK) están todos ENCARCELADOS, ninguno encarcelado; Cumplir con el objetivo final del §4.7 "Los verificadores <7 no pueden realizar TGE"
- Cliente https://lightdao.net (PWA): billetera Passkey + minería + retransmisión WebRTC + recolección, multilenguaje (chino/inglés/español)
- Ciclo cerrado de minería: contribución del navegador → finalización diaria de la puerta de enlace → Merkle root 5 está firmado en la cadena (umbral 5, se puede verificar en la cadena) → los mineros reciben prueba con prueba; La raíz diaria se envía continuamente.
- Gestión de actualizaciones: v2-lightfee (aplicado @58627), puesta a cero impecable (aplicado), v3-lightfee (aprobado por unanimidad, la altura 118055 cambia automáticamente)
- Para obtener el historial completo de actualizaciones/dirección de contrato/punto final, consulte el almacén `docs/MAINNET_STATUS.md`

---

# LightDAO 白皮书 V2.0

**Versión optimizada de verificación y revisión de texto completo (cliente web internacional · auditoría numérica · auditoría de terceros · versión optimizada del modelo económico) **

Fecha de lanzamiento: 4 de agosto de 2026

Principio básico: los navegadores son nodos, todos pueden participar y las ganancias se comparten de acuerdo con las reglas

Posicionamiento legal: LIGHT y los subtokens se posicionan como puntos de contribución ecológica y certificados de derechos de reclamación de distribución de ingresos de SPV, y no son valores ni productos financieros; Los atributos legales específicos están sujetos a opiniones legales válidas en las jurisdicciones relevantes.

> Este documento es una versión verificada y optimizada del texto completo del documento técnico y no constituye asesoramiento de inversión, documentos de emisión de valores, descripciones de productos financieros ni ninguna forma de compromiso de garantía de capital. Consulte a profesionales legales, fiscales y financieros antes de participar.

---

## Tabla de contenido

- Predeclaración
- Prólogo: La historia de tres personas.
- Capítulo 1: La verdad que vemos.
- Capítulo 2: La respuesta de LightDAO
- Capítulo 3: Cumplimiento y aislamiento legal
- Capítulo 4: Arquitectura Técnica
- Capítulo 5: Modelo económico de tokens
- Capítulo 6: Mecanismo de Gobernanza
- Capítulo 7: Controles y equilibrios de poder y definición de roles
- Capítulo 8: Mecanismo de confianza y seguridad
- Capítulo 9: Operaciones de inversión y estrategias de salida
- Capítulo 10: Hoja de ruta
- Capítulo 11: Cultura comunitaria y ecología de desarrolladores.
- Capítulo 12: Equipo y Consultores
- Capítulo 13: Advertencia de riesgo y descargo de responsabilidad
- Apéndice A: Tabla resumen de parámetros clave
- Apéndice B: Derivación y verificación numérica
- Apéndice C: Registro de corrección de auditoría
- Apéndice D: Índice de referencia rápida de términos

---

## Resumen ejecutivo

**Qué es LightDAO:** Una organización autónoma descentralizada que permite a personas comunes y corrientes de todo el mundo participar en inversiones comerciales reales y compartir ganancias a través de un navegador. Los usuarios no necesitan comprar una máquina de minería, tener experiencia técnica o alcanzar el umbral de inversores calificados: con solo un navegador y una pequeña cantidad de tiempo, los usuarios pueden contribuir con recursos de la red para recibir recompensas de tokens LIGHT y participar en decisiones de inversión a través de votaciones de gobernanza.

**Qué problema se resuelve:** El 50 % más pobre de la población mundial (aproximadamente 4 mil millones de personas) posee solo el 2 % de la riqueza total (World Inequality Lab, 2026). Los activos de alta calidad (capital privado, capital de riesgo) están excluidos del umbral de inversor calificado (200.000 dólares de ingreso anual/1 millón de dólares de patrimonio neto). Aunque existe una narrativa de "participación universal" en el campo de las criptomonedas, la gran mayoría de los tokens eventualmente regresan a cero (CoinGecko 2025: murieron 11,56 millones de tokens), y la tasa de participación en la gobernanza de DAO es solo de entre el 3% y el 12%.

**Cómo resolverlo:** Modelo de doble motor: el 70% de los fondos se invierte en activos de consumo rígidos a nivel comunitario (motor de flujo de efectivo) y el 30% en tecnología de punta (motor de crecimiento). Las inversiones se ejecutan a través de Cayman SPV y las ganancias se distribuyen de acuerdo con las reglas de la cadena: 40% a los poseedores de subtokens, 30% a la bóveda para reinversión, 20% recompra de LIGHT para destrucción y 10% acumulado a fondos de seguros.

**Datos básicos:**

| Indicadores | Valores |
|------|------|
| Cantidad total de LUZ | 2,5 mil millones, nunca serán emitidos |
| Bóveda de Inversión | 850 millones (línea de base implementable ≈ $100 millones) |
| Producción minera | 1.000 millones, reducido a la mitad cada 2 años |
| Lanzado el Día de la Primera Era | ≈684.900 piezas (media 6,51/día cuando trabajan 100.000 mineros) |
| Conclusión de la deflación | Dejar de quemar permanentemente cuando la circulación sea ≤ mil millones (años 11-12 del escenario base) |
| Umbral de gobernanza | Propuesta ≥ 5.000 LUZ; Comité ≥ 50.000 LUZ |
| Pila de tecnología | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Verificadores | Inicial 21 (mínimo 10), límite superior 100 |
| Financiación inicial | Subasta holandesa $15 millones + Financiamiento estratégico previo a TGE $2,25-3,75 millones |

**Diferenciación:** Actualmente, el único proyecto que combina "minería web de umbral cero" con "inversión de entidad SPV que cumple con las normas". A diferencia de Pi Network (sin utilidad práctica), Helium (requiere hardware de más de $200) y DAO tradicional (gobernanza de élite de alto umbral).

**Hoja de ruta:** Preparación del cuarto trimestre de 2026 → Desarrollo del primer y segundo trimestre de 2027 → Prueba de auditoría del tercer trimestre → TGE del cuarto trimestre en línea → Usuarios de semillas del primer trimestre de 2028 → Primera inversión del segundo y tercer trimestre → Escala del cuarto trimestre en adelante.

---

## Predeclaración

**Esta no es una propuesta de inversión**

Las "recompensas ecológicas" y la "distribución de ingresos del acuerdo" descritas en este documento técnico son acuerdos de incentivos generados por el mecanismo endógeno del acuerdo y no constituyen ninguna forma de emisión de valores, venta de productos financieros, compromisos de garantía de capital o asesoramiento de inversión.

LIGHT y los subtokens no tienen valor intrínseco y el precio puede volver a cero. Antes de participar, consulte a sus propios profesionales legales, fiscales y financieros, y asuma la responsabilidad total de la custodia de la clave privada, la declaración de impuestos y la participación.

---

## Prólogo: La historia de tres personas.

María trabaja como repartidora de comida en Manila, trabaja 12 horas al día y gana alrededor de 15.000 pesos filipinos (aproximadamente 270 dólares estadounidenses) al mes. Quería invertir en la popular marca de la cadena de té con leche de al lado, pero la otra parte le dijo: "La inversión mínima comienza en 25.000 dólares estadounidenses". María no pudo conseguir 25.000 dólares.

Kwame conduce un servicio de transporte en Lagos. Es optimista sobre el camino de la inteligencia artificial y quiere invertir en una pequeña empresa de tecnología financiera. La institución le dijo: "El monto mínimo de suscripción es de 100.000 dólares estadounidenses y el período de bloqueo es de 5 años". Kwame no pudo conseguir 100.000 dólares.

Elena es una profesora jubilada de São Paulo con una pensión mensual de aproximadamente 3.000 reales brasileños (aproximadamente 550 dólares estadounidenses). Escuchó que los hijos de su vecino estaban ganando dinero trabajando en empresas de blockchain, pero no podía leer el documento técnico y no sabía cómo comprar y configurar equipos de minería profesionales.

Los tres representan a la gran mayoría de la gente corriente de todo el mundo: tienen el criterio y la voluntad de participar, pero carecen de canales de participación de bajo umbral, transparentes y asequibles.

LightDAO está diseñado para estas personas. Con un dispositivo con acceso a Internet, un navegador y una pequeña suma de dinero, puedes participar en la construcción ecológica; A través de una estructura SPV compatible, los usuarios también tienen la oportunidad de acceder indirectamente a la distribución del flujo de caja de empresas de alta calidad y al crecimiento inicial de proyectos de tecnología de punta.

---

## Capítulo 1: La verdad que vemos

### 1.1 Distribución desequilibrada de la riqueza global

Según el Informe sobre la Desigualdad Mundial 2026 (en adelante, el “Informe”) del World Inequality Lab:

| Datos | Fuente |
|------|------|
| La riqueza que posee el 0,001% más rico de la población mundial (unas 60.000 personas) es aproximadamente tres veces la riqueza combinada del 50% más pobre de la población (unas 4.000 millones de personas) | Laboratorio de desigualdad mundial, 2026 |
| El 1% más rico de la población mundial controla el 23% del ingreso total y el 38% de la riqueza total | Laboratorio de desigualdad mundial, 2026 |
| El 10% más rico de la población mundial controla el 53% del ingreso total y el 75% de la riqueza total | Laboratorio de desigualdad mundial, 2026 |
| El 50% inferior de la población mundial recibe sólo el 8% del ingreso total y el 2% de la riqueza total | Laboratorio de desigualdad mundial, 2026 |

El "Informe" señala: "La desigualdad global permanece en niveles históricamente extremos. La desigualdad no surge simplemente del funcionamiento natural del mercado, sino que refleja opciones políticas, estructuras institucionales y la distribución desigual del poder económico y político".

**Nota de la fuente:** Los datos anteriores se citan del Informe sobre la desigualdad mundial 2026 del World Inequality Lab. El informe estuvo dirigido por Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif y Thomas Piketty (confirmado por el sitio web oficial wid.world). Antes del lanzamiento oficial, se recomienda marcar más los números de gráficos específicos en el informe para reducir posibles errores en la traducción secundaria.

**Verificación de coherencia de los datos:** Las proporciones anteriores continúan en una tendencia razonable con la conclusión del Informe sobre la desigualdad mundial de 2022 (el 10% superior posee el 76% de la riqueza total, el 50% inferior posee el 2% de la riqueza total), y la desviación está dentro del rango estadísticamente aceptable.

### 1.2 La gente corriente está excluida de los activos de alta calidad

Las principales jurisdicciones globales tienen umbrales estrictos para inversionistas calificados para capital privado y capital de riesgo:

**Estados Unidos (Reglamento D de la SEC, Regla 501, 17 CFR §230.501):** Los inversionistas calificados (Inversores Acreditados) deben cumplir una de las siguientes condiciones: el ingreso anual de un individuo no es inferior a 200 000 USD (o un total de no menos de 300 000 USD con un cónyuge) y ha cumplido con el estándar durante dos años consecutivos; o el patrimonio neto (excluyendo la residencia principal) no es inferior a 1.000.000 de dólares estadounidenses.

**UE (MiFID II, 2014/65/UE, Anexo II):** Los inversores profesionales (Inversores Profesionales) deben cumplir al menos dos de las siguientes condiciones: una cartera de inversiones en instrumentos financieros de al menos 500.000 euros; ocupar un cargo profesional en la industria financiera por no menos de un año; ejecutar transacciones a gran escala al menos 10 por trimestre.

**Práctica global de fondos de capital privado:** El monto mínimo de suscripción para un solo fondo suele estar entre USD 250 000 y USD 1 000 000; Las normas regulatorias generalmente prohíben comportamientos evasivos como "dividir acciones, reducir umbrales y mantener órdenes en nombre de otros".

| 资产类型 | 普通人能否参与 | 主要原因 |
|----------|---------------|----------|
| 未上市优质企业股权 | 通常不能 | 合格投资者门槛较高，例如美国要求净资产不低于100万美元或年收入不低于20万美元 |
| 风险投资（早期科技公司） | 通常不能 | 主要面向合格投资者开放，单只基金投资金额通常不低于25万美元 |
| 上市公司股票 | 可以，但早期利润通常已被一级市场参与者获取 | 二级市场定价通常包含未来预期，投资者并不直接参与企业早期利润分配 |

### 1.3 Tres fallas importantes en el campo de las criptomonedas

**Defecto 1: Tasa de fallas extremadamente alta**

Según el informe estadístico anual de CoinGecko de 2025, aproximadamente **11,56 millones de tokens** volverán a cero o dejarán de comercializarse solo en 2025 (incluidos los tokens de cola larga en cada cadena). De los más de 20 millones de tokens que CoinGecko ha rastreado históricamente, la gran mayoría se encuentra en un estado "muerto" (sin volumen de operaciones, sin actividad de desarrollo y los precios han caído más del 99% desde máximos históricos).

Al mismo tiempo, la tasa de fracaso de los mercados bursátiles tradicionales es mucho menor que la de las criptomonedas. Según el artículo de Bessembinder (2018) "¿Las acciones superan a las letras del Tesoro?" publicado en el "Journal of Financial Economics", un estudio de todas las acciones estadounidenses desde 1926 hasta 2016:

| Métricas | Datos | Fuentes |
|------|------|------|
| Proporción de acciones que crean riqueza neta total | Sólo alrededor del 4% (1.092 acciones) | Bessembinder (2018), JFE 129(3):440-475 |
| Rentabilidad media de toda la vida de las acciones | Negativo (por debajo del rendimiento de las letras del Tesoro) | Bessembinder (2018), JFE |
| Alrededor del 58% del rendimiento de por vida de las acciones estadounidenses | Letras del Tesoro con peor rendimiento durante el mismo período | Bessembinder (2018), JFE |
| Número de tokens que se restablecerán a cero/dejarán de comercializarse en 2025 | ≈11,56 millones | Informe anual CoinGecko 2025 |

**Conclusión comparativa:** La tasa de pérdida permanente de capital en el espacio de las criptomonedas es mucho mayor que en el mercado de valores tradicional. Aunque alrededor del 58% de las acciones individuales en el mercado de valores estadounidense tienen un rendimiento inferior al de los bonos del Tesoro, los inversores aún pueden obtener rendimientos promedio del mercado a través de fondos indexados; En el mercado de las criptomonedas, la gran mayoría de los tokens acaban volviendo a cero y faltan herramientas de diversificación eficaces similares a los "índices".

**Declaración de la fuente:** Bessembinder, H. (2018). "¿Las acciones superan a las letras del Tesoro?" *Revista de Economía Financiera*, 129(3), 440-475. Universidad Estatal de Arizona. Este documento es un documento muy citado en el campo de las finanzas (citas >2000) y los datos cubren todas las acciones estadounidenses en la base de datos CRSP desde 1926 hasta 2016. Los datos de CoinGecko provienen de su Informe estadístico del estado de supervivencia de tokens de 2025 (publicado en enero de 2026), que ha sido informado por muchos medios financieros (Sina Finance, Phemex, RBC Crypto).

**Defecto 2: La minería está muy centralizada**

La minería de Bitcoin ha mostrado un alto grado de concentración:

| Piscina minera | Relación de tasa de hash |
|------|---------|
| Fundición EE.UU. | Alrededor del 30% |
| piscina de hormigas | Alrededor del 19% |
| A través de BTC | Alrededor del 14,5% |
| Piscina F2 | Alrededor del 10% |
| Piscina MARÁ | Alrededor del 5% |
| Los dos principales grupos mineros combinados | Más del 50% |
| Los cuatro principales grupos mineros combinados | Alrededor del 75% |

**Nota de la fuente:** Los datos anteriores se compilan del informe mensual de distribución de hashrate de 2025 (CoinGradient 2025.3 "Foundry, Antpool y Viabtc dominan la minería de Bitcoin"; HashrateIndex "Los 10 principales grupos de minería de Bitcoin de 2025"). Los valores específicos de diferentes fuentes de datos pueden variar ligeramente (generalmente dentro de ±2%), pero la conclusión de que "los cuatro principales grupos de minería controlan aproximadamente el 75% de la potencia informática" se refleja en múltiples plataformas de monitoreo convencionales.

**Defecto 3: la tasa de participación en la gobernanza de DAO es extremadamente baja**

| Datos | Fuente |
|------|------|
| La tasa de participación en la votación de la mayoría de las DAO es solo de entre el 3% y el 12% (la mediana es de aproximadamente el 6%) | DeepDAO (2025) Agregación de datos de gobernanza en cadena; Informe de gobernanza de DAO de la sala de juntas (2024) |
| Un pequeño número de tenedores de divisas controla la gran mayoría de los derechos de voto (alta concentración del poder de gobernanza) | ACM (2024) "Gobernanza de DAO: poder de voto, participación y controversia" DOI:10.1145/3777416 |

### 1.4 Perspectivas principales

Tengo criterio, pero no boleto de entrada; Tengo visión, pero no tengo derecho a hablar; Quiero participar, pero estoy bloqueado por umbrales altos.

---

## Capítulo 2: La respuesta de LightDAO

### 2.1 Posicionamiento central

LightDAO es una organización autónoma de inversión nacional con la gobernanza en cadena como núcleo y el SPV de cumplimiento como portador de ejecución de inversiones. A través de una cadena pública diseñada específicamente para nodos web livianos, los usuarios globales pueden participar en el mantenimiento de la red, la votación de gobernanza y compartir beneficios ecológicos de acuerdo con reglas con un solo navegador.

### 2.2 Modelo de doble motor

| Motor | Dirección de Inversiones | Objetivo | Características de ingresos |
|------|---------|------|---------|
| Motor uno: Motor de flujo de caja (Shou) | Activos de servicios de consumo rígido a nivel comunitario | Formar un flujo de caja continuo y distribuir las ganancias según las reglas | Persiguen una relativa estabilidad, pero no prometen renta fija |
| Motor 2: Motor de crecimiento (ataque) | Empresas de tecnología de punta | Obtenga revalorización de las acciones y rendimientos de salida | Alto potencial de flexibilidad, pero también puede enfrentar pérdidas o fracaso de salida |

**Disciplina de asignación:** En principio, asignar el 70% de los fondos a activos con flujo de caja estable y el 30% a objetivos de alto crecimiento.

**Ruta de crecimiento a escala de inversión:** El tamaño de una única inversión crece dinámicamente con el precio de LIGHT y la capacidad de la bóveda: el período de inicio (LIGHT entre $0,02 y $0,05) es adecuado para pequeños activos a nivel comunitario de entre $2,55 y $6,37 millones; la etapa de crecimiento ($0,05-$0,30) ingresa a cadenas regionales y rondas Seed-A de $6,37 millones-$38,25 millones (evaluación comparativa del mercado medio inferior) PE); en la etapa madura ($0,30-$1,00), alcanza el nivel de PE del mercado medio de $38,25 millones a $127,5 millones; en la etapa de escala ($1,00+), puede ejecutar adquisiciones a gran escala e inversiones previas a la IPO de más de $127,5 millones. Restricciones estrictas: una sola transacción no excederá el 15% del monto restante del tesoro de inversión (consulte el Capítulo 9 para más detalles).

**El primer principio de posicionamiento objetivo:** En lugar de presuponer un nombre de empresa específico, primero establezca un marco de selección: dé prioridad a los rígidos activos de servicio al consumidor a nivel comunitario, que requieren un modelo económico probado de tienda única, registros de flujo de efectivo estables (el margen EBITDA en los últimos tres años no es inferior al 10% y la volatilidad interanual no es superior al 15%) y un camino claro de expansión regional. El objetivo específico está determinado por las propuestas comunitarias.

### 2.3 Propuesta de valor central

**El navegador es el nodo** - No es necesario comprar una máquina de minería ni tener experiencia técnica profesional. Puedes participar en aportes de la red visitando la plataforma web oficial.

**Todos pueden participar** - Después de alcanzar el umbral de gobernanza, los titulares de pequeñas cantidades de LIGHT también pueden participar en la votación para decidir conjuntamente la dirección de la asignación de fondos.

**Reparto de ganancias según reglas** - Las ganancias operativas de las empresas invertidas y los retornos de salida de los proyectos tecnológicos se distribuirán de acuerdo con las reglas en cadena y los acuerdos SPV.

### 2.4 Lema

"Su navegador también puede ser la puerta de entrada a activos de alta calidad".

### 2.5 Análisis de diferenciación de productos competitivos

| Dimensión | Red Pi | Helio | DAO tradicional (MakerDAO, etc.) | LuzDAO |
|------|-----------|--------|---------------------|----------|
| Método de participación | Haga clic en la APLICACIÓN móvil | Compra de punto de acceso de hardware ($200-$1000) | Compra de token + operación en cadena | Acceso al navegador, coste de hardware cero |
| Costo de entrada | Cero (pero sin utilidad práctica) | Alta (hardware + instalación) | Medio a alto (necesita comprar tokens de gobernanza) | Zero (solo un navegador) |
| Cantidad total de fichas | 100 mil millones | 223 millones | Varía | 2.500 millones |
| Función de inversión real | Ninguno | Ninguno (solo cobertura de red) | Sí (pero el umbral es extremadamente alto) | Sí (estructura SPV, todos pueden participar) |
| Fuente de ingresos | Poco claro | Tarifa de uso de red | Tarifa del acuerdo | Beneficio corporativo + retorno de salida + Tarifa de gas |
| Aislamiento legal | Ninguno | Ninguno | Algunos si | Caimán SPV+ZK-KYC |
| Tasa de participación en la gobernanza | Extremadamente bajo (sin gobernanza sustancial) | Bajo | Alrededor del 6% | Objetivo >15% (votación bidimensional + incentivos) |

**La principal diferencia de LightDAO:** Actualmente es el único proyecto que combina "minería web de umbral cero" con "inversión de entidad SPV que cumple con las normas". Los usuarios no solo contribuyen con recursos de la red para obtener recompensas simbólicas, sino que también participan directamente en decisiones de inversión empresarial reales a través de votaciones de gobernanza y comparten las ganancias operativas.

> **[Terminología en este capítulo]**
> **DAO** (Organización autónoma descentralizada): una forma organizativa en la que las reglas de gobernanza se codifican a través de contratos inteligentes y los poseedores de tokens toman decisiones colectivas. No existe una jerarquía empresarial tradicional.
> **SPV** (Vehículo de Propósito Especial): una entidad legal independiente (generalmente registrada en las Islas Caimán) establecida para transacciones o inversiones específicas para lograr el aislamiento de riesgos; las deudas y responsabilidades legales del SPV no se transmiten a la propia DAO.
> **DePIN** (Red de infraestructura física descentralizada, red de infraestructura física descentralizada): un modelo de red que utiliza tokens para alentar a los usuarios a contribuir con recursos físicos (ancho de banda, almacenamiento, potencia informática, cobertura inalámbrica, etc.) para construir infraestructura.
> **Lower Middle Market PE** (capital privado downstream de gama media): un segmento de mercado de la industria global de capital privado. El tamaño de una sola transacción suele ser de 10 a 100 millones de dólares, y el EBITDA de la empresa objetivo está entre 2 y 15 millones de dólares.

---

## Capítulo 3: Cumplimiento y aislamiento legal

### 3.1 Capa de aislamiento legal de SPV

DAO no posee directamente acciones en ninguna empresa física. Todas las inversiones externas se ejecutan a través de entidades de propósito especial (SPV) establecidas en las Islas Caimán.

| Puntos de diseño | Descripción |
|---------|------|
| Carta SPV | Se acuerda claramente que la operación de la SPV deberá cumplir con la resolución efectiva de la DAO |
| Definición legal de subtokens | Los subtokens son "certificados de derechos de reclamación de distribución de ingresos de SPV", que solo representan las calificaciones de distribución para el flujo de caja futuro |
| No conlleva derechos de accionista | No conlleva derechos de gobierno corporativo, preferencias de liquidación ni ningún derecho de los accionistas |
| Directores de SPV | son atendidos por terceros independientes; DAO puede reemplazar a los directores aprobando una resolución válida |
| Supervisión de fondos | Las cuentas bancarias están supervisadas por instituciones de custodia autorizadas y las transferencias de fondos deben pasar una verificación de cumplimiento y firma múltiple |
| Resolución de disputas SPV | El estatuto del SPV estipula una cláusula de arbitraje (SIAC o ICC), y la DAO puede iniciar procedimientos de arbitraje a través de una resolución de gobernanza |

### 3.2 Verificación opcional y protección de la privacidad

**No se requiere identificación para participar en el protocolo en sí. ** Visite páginas web, cree billeteras, contribuya con recursos, reciba LUZ, inicie y participe en votaciones de gobernanza: no es necesario cargar documentos durante todo el proceso y no se almacena información de identificación personal (PII) en la cadena.

Sólo cuando un usuario utilice activamente un servicio de un tercero regulado se procederá a la verificación de que el propio servicio debe realizar de conformidad con la ley. Esta verificación es recopilada, realizada y conservada por la parte del servicio. LightDAO no recopila, transfiere ni almacena ningún dato:

| Escenario | Quién realiza la verificación | Qué debe hacer el usuario |
|---|---|---|
| Compra/venta a través de canales fiduciarios | Terceros autorizados (como MoonPay, Ramp Network, Transak) | Completar el proceso de cumplimiento según los propios requisitos del proveedor de servicios |
| Subtokens de intercambio (certificados de acciones de inversión) | Según los requisitos del producto específico y su proveedor de servicios | Sólo se puede hacer minería y gobernanza, sin ningún tipo de verificación |
| Retiro a tarjeta bancaria/pago local | Proveedor de servicios de retiro y pago | Completar el proceso de cumplimiento según lo requiera el proveedor del servicio |

Principios básicos: **Verificación cero de forma predeterminada; La verificación sólo se produce en el momento en que el usuario ingresa activamente al servicio regulado, y corre a cargo del prestador del servicio. **Nadie perderá el derecho a extraer, poseer, transferir o votar debido a "falta de verificación".

> Tecnología reservada: si un determinado tipo de activo requiere un umbral de calificación en el futuro, el usuario tendrá el certificado en forma de prueba de conocimiento cero (ZK) y la cadena solo verificará "si se cumple" sin ninguna información de identidad; esto es parte de la hoja de ruta y no es un requisito actual.

### 3.3 Declaración de Responsabilidad Fiscal

El acuerdo no proporciona servicios de declaración de impuestos y las obligaciones fiscales de todas las recompensas ecológicas y los ingresos relacionados corren a cargo de los propios usuarios. Los usuarios deben cumplir con las leyes y regulaciones pertinentes de su ubicación de residencia fiscal.

### 3.4 Acceso de usuarios: abierto a todos

**Sin umbral para registrarse y participar**: No se requiere correo electrónico, número de teléfono móvil, cuenta social ni prueba de identidad; Todo lo que necesitas es un dispositivo que pueda abrir una página web. LightDAO ** no restringe activamente la participación de los usuarios en ningún país o región, ni implementa geocercas. **

Las únicas restricciones externas provienen de servicios de terceros: si la ley de un determinado lugar tiene otros requisitos para servicios específicos (como depósitos y retiros de moneda fiduciaria), esos servicios serán realizados por instituciones locales autorizadas de acuerdo con la ley de su lado y no afectarán el uso de las funciones en cadena por parte de nadie (minería, tenencia, transferencias, votación, propuestas).

Si una determinada jurisdicción emite regulaciones prohibitivas explícitas en el futuro, la secuencia de respuesta del protocolo es:

1. Primero, garantizar que los derechos de disposición de activos de los usuarios existentes no se vean afectados: los activos en la cadena no se pueden congelar y cualquiera puede transferir su LIGHT y sus subtokens en cualquier momento;
2. Seguir siendo accesible a través de múltiples portales front-end (incluidos los espejos IPFS y los espejos comunitarios);
3. El último paso es ajustar el alcance disponible de **servicios de terceros** dentro del alcance de la aplicación legal.

En una palabra: *** las restricciones sólo pueden recaer sobre los servicios, no sobre las personas. **

### 3.5 Depósitos y retiros de moneda legal y canales entre cadenas

**Canal de moneda fiduciaria (agregación de servicios de terceros):** El protocolo en sí no opera servicios de depósito y retiro de moneda legal, pero la plataforma web integra canales de terceros compatibles (MoonPay, Ramp Network, Transak, etc.), que cubren los principales mercados de América del Norte, Europa, el Sudeste Asiático y América Latina; la agregación del mercado local P2P cubre África y el sur de Asia; Los retiros admiten métodos de pago locales como GCash, M-Pesa, Pix y GrabPay.

**Puente entre cadenas y canales de adquisición LIGHT:** Transacciones AMM integradas en la cadena LightDAO después de TGE; interoperabilidad con el ecosistema Cosmos a través de IBC; planificación para wLIGHT (Ethereum/Solana) a partir del sexto mes; Solicitud de cotización en CEX a partir del 6º mes dependiendo del cumplimiento. El puente entre cadenas es operado por un tercero independiente y se requiere un informe de auditoría independiente antes de que el puente entre en funcionamiento.

### 3.6 Declaración de cumplimiento del mecanismo de invitación (análisis anti-MLM)

El incentivo de invitación de LightDAO es **compartir en una sola capa** (solo los que invitan directamente reciben una proporción fija de las recompensas mineras del invitado) y no tiene las características principales del marketing multinivel (MLM): sin comisión recursiva multinivel; los ingresos provienen de la liberación de tokens preestablecidos en el protocolo en lugar del principal del recién llegado; No hay costo ni tarifa de entrada para participar en la minería. Esta estructura se acerca más a las "recompensas por recomendación de contribuyentes de proyectos de código abierto". Antes de la operación formal, se contratará a un abogado autorizado en el mercado objetivo para que emita opiniones especiales de cumplimiento.

> **[Terminología en este capítulo]**
> **KYC** (Conozca a su cliente, conozca a su cliente): un proceso de cumplimiento para que las instituciones financieras verifiquen la identidad del usuario, que generalmente requiere la presentación de documentos de identidad, comprobante de domicilio, etc.
> **ZK-KYC** (KYC de conocimiento cero, KYC a prueba de conocimiento cero): los usuarios no necesitan revelar información personal específica en el acuerdo y solo usan criptografía para demostrar que "cumplo con ciertas condiciones" (como edad ≥ 18 años, nacionalidad no sancionada) como método de verificación de cumplimiento. No se almacenan datos del documento original en la cadena.
> **PII** (Información de Identificación Personal, Información de Identificación Personal): Datos que pueden identificar a una persona física específica de forma individual o combinada, como nombre, número de identificación, dirección, características biométricas, etc.
> **Reg D / Reg S** (Regulación D/Regulación S de la Ley de Valores de EE. UU.): Reg D permite colocaciones privadas a "inversores calificados" en los Estados Unidos sin registro público (estándar de definición de la Regla 501); Reg S permite la venta de valores a personas fuera de los Estados Unidos sin activar los requisitos de registro en los EE. UU.
> **MiFID II** (Directiva II de Mercados de Instrumentos Financieros de la UE, 2014/65/UE): Marco regulatorio financiero de la UE, su Anexo II define los criterios de identificación para "inversores profesionales" (cartera de instrumentos financieros de 500.000 €, 1 año de experiencia en la industria financiera, 10 transacciones a gran escala por trimestre, cumpliendo el segundo requisito).
> **MLM** (Multi-Level Marketing, marketing multinivel): un modelo de negocio a través de comisiones recursivas multinivel (desarrollo de línea descendente, desarrollo de línea descendente y comisiones de línea ascendente capa por capa). Es esencialmente diferente de las recompensas de recomendación de una sola capa: LightDAO es solo de una sola capa (A invita a B, A recibe una parte de B; B invita a C, A no recibe ninguna parte de C).
> **IBC** (Inter-Blockchain Communication, protocolo de comunicación entre cadenas): el estándar nativo entre cadenas del ecosistema Cosmos, que permite la transferencia segura de activos y mensajes entre diferentes blockchains sin necesidad de un intermediario centralizado.

---

## Capítulo 4: Arquitectura técnica

### 4.1 ¿Qué es la cadena pública?

La cadena pública de LightDAO puede entenderse como un "libro de cuentas públicas con reglas transparentes y que no puede ser manipulado a voluntad": las reglas de gobernanza están escritas en el código, y los registros de votación, los flujos de capital y la distribución de ganancias de cualquier persona pueden consultarse y verificarse en la cadena.

### 4.2 Parámetros técnicos y demostración de selección.

| Artículos técnicos | Selección | Bases de selección |
|--------|------|---------|
| Marco subyacente | SDK de Cosmos | Arquitectura modular, verificación de múltiples cadenas de producción |
| Mecanismo de consenso | Punto de venta Tendermint | Certeza instantánea; la generación de bloques tarda entre 1,5 y 2 segundos; Tolerancia a fallos BFT ≤ 1/3 del mal |
| Contratos inteligentes | CosmoWasm | WebAssembly + Rust, seguridad de la memoria en tiempo de compilación |
| Capacidades entre cadenas | Protocolo CIB | Estándar de cadena cruzada nativo de Cosmos |
| Interacción frontal | Aplicación web progresiva (PWA) | Navegador en ejecución, adaptable a escritorio/móvil, no requiere instalación |

### 4.3 Mecanismo de minería de nodos ligeros y modelo de incentivos

#### 4.3.1 Método de minería

Los usuarios acceden a la plataforma web oficial a través de un navegador, crean una billetera y hacen clic en "Iniciar minería". Durante el proceso de minería, los usuarios aportan ancho de banda de red (retransmisión y verificación de datos) y recursos informáticos locales (verificación de encabezado de bloque liviano) a través del navegador, y no dependen de potencia informática de alta energía.

**Implementación de tecnología del lado web:** Retransmisión P2P del canal de datos WebRTC; Verificación del encabezado del bloque de fondo de Web Worker; Caché y latidos fuera de línea de Service Worker; Conexión larga WebSocket.

**Adaptación del navegador móvil:** Adopte un sistema de sesión válido acumulativo (4 horas al día = puntuación del 100%); no se deducirán puntos por volver a conectarse dentro de los 5 minutos posteriores a la desconexión; Los usuarios instalados de PWA recibirán un bono adicional de tiempo en línea del 10%; Mecanismo en línea delegado (70% para el delegado/30% para el nodo de retransmisión).

#### 4.3.2—4.3.3 Esquema de incentivos y modelo de tres motores

Adopta el modelo de tres motores de "prueba de contribución PoC + incentivo de fisión de invitación + incentivo de bonificación por comportamiento".

#### 4.3.4 Dimensiones y peso de la contribución

| Dimensión de contribución | Peso | Método de medición |
|---------|------|---------|
| Contribución de retransmisión de ancho de banda | 40% | Relación entre el tráfico de retransmisión de carga y el volumen de datos de verificación |
| Duración efectiva de la sesión | 30% | Sesiones efectivas acumuladas diarias (4 horas = 100%) |
| Contribución de verificación de bloque | 20% | Número y precisión de encabezados de bloque verificados efectivamente |
| Estabilidad de la red | 10% | Retraso de conexión, tasa de pérdida de paquetes, tiempo de respuesta |

#### 4.3.5 Fórmula de cálculo de recompensa

**Recompensa de minería diaria = Recompensa base × Puntuación de peso de contribución × (1 + Bonificación de invitación) × (1 + Bonificación de comportamiento)**

- BaseReward = Monto total liberado por toda la red en el día ÷ Número total de mineros activos en el día
- Bonificación por invitación = número efectivo de invitados × 1% (límite superior 20%)
- Bonificación por comportamiento = 5 % de participación en la votación + 5 % de contribución de contenido + 5 % de actividad de la comunidad + 5 % de calidad de verificación del nodo (límite superior 20 %)
- Coeficiente de bonificación total = (1+20%) × (1+20%) = 1,44 veces

#### 4.3.6 Invitar incentivos de fisión

| Nivel | Número válido de invitaciones | Proporción de participación de invitación | Recompensa única adicional | Bonificación por ponderación de la gobernanza |
|------|------------|------------|--------------|------------|
| Mineros | 0 personas | — | Recompensas mineras básicas | Ninguno |
| Predicador | No menos de 3 personas | 10% | 100 LUZ | Ninguno |
| Embajador | Nada menos que 10 personas | 15% | 500 LIGHT + insignia en cadena | Peso de voto +5% |
| Socios | Nada menos que 50 personas | 20% | 2.500 LUZ + insignia en cadena | Peso de voto +10% |

El bono de peso de gobernanza y el bono de reputación (hasta +30%) se acumulan de forma independiente, con un límite superior total de +40%. El bono de invitación alcanza su punto máximo cuando hay 20 personas (20×1%=20%).

#### 4.3.7 Mecanismo anti-trampas

Detección de integridad del entorno del navegador (huella digital Canvas/WebGL/WebRTC), detección de profundidad de paquetes, agrupamiento de IP y análisis de patrones de comportamiento, huella digital de comportamiento multidimensional (trayectoria del mouse/ritmo del teclado/comportamiento de desplazamiento), verificación de autenticidad de la dirección de invitación. Costo del ataque anti-Sybil: entre 50.000 y 200.000 dólares para crear 10.000 huellas dactilares independientes; Objetivo de tasa de detección >90-95%.

### 4.4 Matriz de funciones del token LIGHT

Combustible de red (tarifa de gas), derechos de gobernanza (votación/propuesta/campaña), compromiso vinculante (margen/campaña/verificador), intercambio de inversiones (subtokens), incentivos ecológicos (minería/invitación/comportamiento), expansión futura (dApp/NFT/cadena cruzada).

### 4.5 Mecanismo de tarifa de gas y tarifa de transacción

**Principio de diseño:** La tarifa del gas está fijada en el equivalente en USD, y el oráculo de la cadena convierte automáticamente la cantidad real de LUZ cobrada cada 24 horas (Sección 4.10). Esto garantiza que, independientemente de si el precio de LIGHT sube o baja, el costo de pago real del usuario (en dólares estadounidenses) permanece estable, evitando el problema de "el precio de la moneda aumenta 100 veces → la tarifa de transferencia se convierte en $10" o "el precio de la moneda cae un 90% → canje de boletos sin costo".

**Objetivo de tarifa de gas anclada en USD:**

| Tipo de transacción | Objetivo equivalente en USD | Cobro real cuando LIGHT=$0.05 | Cobro real cuando LUZ=$0.50 | Intención de diseño |
|---------|------------|------------------|------------------|----------|
| Transferencia ordinaria | $0,001 | 0,02 LUZ | 0.002 LUZ | Umbral extremadamente bajo para garantizar que los usuarios de pequeñas cantidades puedan transferir dinero libremente |
| Votación de gobernanza | $0,005 | 0,10 LUZ | 0,01 LUZ | Ligeramente superior a la transferencia para evitar un roce de votos sin costes |
| Enviar una propuesta | $0,10 | 2.0 LUZ | 0.2 LUZ | Cooperar con el sistema de depósito para aumentar la seriedad de la propuesta |
| Intercambio de subtokens | $0,50 | 10.0 LUZ | 1.0 LUZ | Tarifas más altas, a la altura de la seriedad de las operaciones a gran escala |
| Informes de latidos mineros | $0 (gratis) | 0 | 0 | No se cobra Gas por aportes mineros, asegurando participación sin costo |

**Reglas de conversión dinámica:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Reglas de asignación de tarifas de gas:**

| Destino | Proporción | Función |
|------|------|------|
| Destrucción permanente | 50% | Deflación continua, reducción de la oferta circulante |
| Recompensas del validador | 30% | Incentivar a los validadores para mantener la seguridad de la red y producir bloques |
| Tesoro Ecológico | 20% | Financiamiento complementario para desarrolladores y fondos operativos comunitarios |

**Estimación de deflación de la tarifa del gas:** Suponiendo un promedio de 100 000 transacciones activas diarias y una tarifa promedio del gas de $0,005 (principalmente votaciones y transferencias), el equivalente a USD destruidos por día = 100 000 × $0,005 × 50 % = $250/día. Cuando LUZ=$0,05, equivale a 5.000 LUZ/día≈1,825 millones/año; cuando LUZ=$0,50, equivale a 500 LUZ/día≈182.500/año. La cantidad de LIGHT con la deflación de la tarifa del gas disminuye a medida que aumenta el precio (el equivalente en USD es constante), pero su soporte para el precio se refleja en la "compra continua del equivalente": cada transacción destruye tokens a una tasa fija en USD.

### 4.6 Sistema verificador

| Dimensiones | Validadores | Nodos ligeros (mineros de navegador) |
|------|--------|-------------------|
| Responsabilidades | Generación de bloques, consenso, nodo completo | Verificación de encabezado de bloque, retransmisión de datos |
| Replanteo | Mínimo 500.000 LUZ | Ninguno |
| Ingresos | Tarifa de gas 30% + piscina de liberación diaria 5% | Recompensas de minería PoC (grupo de lanzamiento diario 95%) |
| Cantidad | Inicial 21, límite superior 100 | Sin límite superior |
| Cortando | Penalización del 5% por doble fichaje + prohibición de 180 días | Ninguno |

**Inicio por etapas (tolerancia a fallos BFT: N≥3f+1):**

| Fase | Número de validadores | Tolerancia a fallos f | Condiciones de parada de la cadena | Experiencia de usuario |
|------|-----------|-------|-----------|----------|
| Testnet (3 meses antes de TGE) | 7 | 2 | 3 desconectados al mismo tiempo | Las pruebas internas pueden tolerar breves interrupciones |
| Red principal TGE | Mínimo 10, objetivo 21 | 3-6 | 4-7 sin conexión al mismo tiempo | Interrupciones ocasionales (<1 vez por trimestre) para suavizar |
| Abierto a elecciones a partir del séptimo mes | 21-100 | 6-33 | 7-34 sin conexión al mismo tiempo | Usuario inconsciente |

** Conclusión definitiva: TGE no se ejecutará cuando haya <7 validadores. ** Menos de 7 significa f ≤ 1. Cualquier falla en un solo punto provocará que se apague toda la cadena, lo que equivale a "indisponibilidad del producto" para usuarios no técnicos.

### 4.7 Capa de infraestructura de red

Los nodos validadores llevan puertas de enlace de acceso WebSocket de forma distribuida (cada validador tiene un límite superior de 50.000 conexiones); La señalización P2P la proporciona el validador + nodo de retransmisión comunitario; La agregación Heartbeat Merkle solo envía el hash raíz por bloque (O(1) sobrecarga en la cadena); el front-end se distribuye a través de IPFS+CDN.

Red P2P: marco WebRTC ICE (prioridad STUN/respaldo TURN); alrededor del 70-80% de los usuarios pueden conectarse directamente, el 20-30% de los usuarios de NAT simétrica pasan por el relé TURN; cuando falla P2P, se degrada al "modo de autenticación pura".

Especificaciones de rendimiento: TPS teórico 1.000-3.000; tamaño de bloque 2 MB (gobernanza ajustable); sincronización de nodos de luz <30 segundos; Millones de latidos del nodo Agregación de Merkle <500 ms.

### 4.8 Mecanismo de verificación de prueba de contribución

Arquitectura de verificación de tres niveles: (1) Desafío de muestreo cruzado aleatorio del verificador (5% de nodos cada 10 minutos, tiempo de respuesta de 30 segundos); (2) Verificación mutua entre pares P2P (de 8 a 16 pares registran de forma independiente el volumen de intercambio de datos y se toma la mediana); (3) Agregación de Merkle en cadena (cada bloque envía la puntuación de contribución Root, los usuarios pueden realizar una autoverificación a través de Merkle Proof). Si no se realiza el desafío 3 veces seguidas → la puntuación del día se restablecerá a cero; un total de 5 veces en 7 días → se activará una revisión antitrampas.

### 4.9 Gestión de carteras y claves

Arquitectura de tres niveles: (1) Cartera inteligente integrada (Clave de acceso/WebAuthn, no se requiere frase mnemotécnica, dirigido a más del 80 % de usuarios); (2) Cartera de recuperación social (3-5 restauradores, fragmentación de Shamir, confirmación mayoritaria de 2/3); (3) Cartera autohospedada (frase mnemotécnica BIP-39 + compatible con cartera de hardware). Las tarifas del gas para las primeras 100 transacciones de nuevos usuarios serán pagadas por el fondo ecológico (modelo Paymaster).

### 4.10 Precio Oráculo

El TWAP en cadena (precio promedio ponderado en el tiempo de 30 días del grupo LIGHT/USDC) es la principal fuente de precios; Se complementa la agregación externa DEX/CEX 3+ (los validadores se envían en rotación, toman la mediana); las desviaciones >±15 % activan indicadores de excepción; las desviaciones de un solo bloque >5% no están incluidas en TWAP (manipulación de préstamos anti-flash); recurrir a TWAP puro en cadena cuando todos los oráculos externos fallan.

### 4.11 Arquitectura del módulo de contrato inteligente

10 contratos principales: light_token, mining_reward, gobernanza, Treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, Insurance_fund. El contrato núcleo deberá completar verificación formal ante TGE.

### 4.12 Actualización del protocolo y gobernanza de la cadena

Actualización de nivel 4: ajuste de parámetros L1 (votación de gobernanza 24-72 h) → Migración de contrato L2 (propuesta importante + auditoría + retraso de 72 h) → cambio de consenso L3 (66 % aprobado + 2/3 señales de validador + período de protección de bifurcación de 7 días) → reparación de emergencia L4 (suspensión del comité paralelo + corrección urgente de firmas múltiples + ratificación de 72 h).

> **[Terminología en este capítulo]**
> **Cosmos SDK**: un marco de desarrollo de blockchain modular que permite a los desarrolladores ensamblar cadenas públicas personalizadas como bloques de construcción. Varias cadenas productivas (como Cosmos Hub y Osmosis) han comprobado su madurez.
> **Tendermint PoS** (Prueba de participación, Prueba de participación): un mecanismo de consenso en el que los validadores obtienen el derecho de producir bloques prometiendo tokens (en lugar de competir por la potencia informática). Proporciona "finalidad instantánea": una vez que se envía un bloque, no se puede revertir.
> **BFT** (Tolerancia a fallas bizantinas, tolerancia a fallas bizantinas): un mecanismo en un sistema distribuido que puede tolerar que algunos nodos hagan mal o funcionen mal y aun así lograr el consenso correctamente. Tendermint BFT no puede tolerar que más de 1/3 de los validadores actúen mal o se desconecten al mismo tiempo.
> **CosmWasm**: El motor de contrato inteligente del ecosistema Cosmos, basado en la tecnología WebAssembly, admite el uso del lenguaje Rust para escribir contratos y tiene funciones de seguridad de memoria en tiempo de compilación (que previenen vulnerabilidades comunes como desbordamientos de búfer).
> **PWA** (Aplicación web progresiva, aplicación web progresiva): una tecnología web que se ejecuta en un navegador pero que tiene una experiencia de aplicación similar a la nativa. Admite almacenamiento en caché sin conexión, notificaciones automáticas y agregar a la pantalla de inicio sin descargarlo ni instalarlo a través de la tienda de aplicaciones.
> **WebRTC/WebSocket**: Dos tecnologías de comunicación en tiempo real del navegador. WebRTC se utiliza para la retransmisión de datos P2P (transmisión directa entre nodos); WebSocket se utiliza para mantener una conexión larga entre el cliente y el verificador (latidos, notificación de recompensa).
> **PoC** (Prueba de contribución): el mecanismo de incentivo adoptado por LightDAO emite recompensas al verificar los recursos de la red (retransmisión de ancho de banda, verificación de bloques, tiempo en línea) realmente aportados por los usuarios, en lugar de depender de la competencia de potencia informática o la promesa de capital.
> **Merkle Tree** (Merkle Tree): Una estructura de datos de árbol hash que permite una verificación eficiente de la integridad de una entrada específica en una gran cantidad de datos. Este documento técnico se utiliza para agregar millones de latidos de nodos ligeros en un único hash raíz y cargarlo en la cadena (sobrecarga de almacenamiento O(1)).
> **Tarifa de gas**: la tarifa de manejo requerida para ejecutar transacciones u operaciones de contrato en la cadena de bloques, utilizada para compensar al verificador por los recursos informáticos y de almacenamiento. La tarifa de gas de LightDAO está fijada en el equivalente en USD y el oráculo la convierte automáticamente en la cantidad de LIGHT cada 24 horas.
> **Recorte** (penalización): Un mecanismo de penalización en el que un verificador se ve obligado a deducir parte de los tokens prometidos debido a una mala conducta (como una doble firma) o a estar desconectado durante mucho tiempo. Es una garantía económica para la seguridad de la red PoS.
> **Oracle** (Oracle): un componente de infraestructura que transmite de forma segura datos fuera de la cadena (como precios de mercado, clima, resultados deportivos) a contratos inteligentes dentro de la cadena. LightDAO utiliza una arquitectura Oracle híbrida de agregación de fuentes múltiples TWAP + en cadena.
> **TWAP** (Precio promedio ponderado en el tiempo): el precio de cada bloque dentro de un período de tiempo se pondera igualmente por el tiempo para reducir el impacto de la manipulación de transacciones instantáneas de gran cantidad en la referencia del precio.
> **AMM** (Creador de mercado automatizado): un protocolo comercial descentralizado que realiza el intercambio de tokens a través de un fondo de liquidez (en lugar de un libro de órdenes). El precio se determina automáticamente por la proporción de activos en el grupo según una fórmula.
> **DEX / CEX**: DEX (Intercambio descentralizado, intercambio descentralizado) no necesita alojar los activos de los usuarios y comercia entre pares a través de contratos inteligentes; CEX (Centralized Exchange, intercambio centralizado) requiere que el operador custodie los activos y iguale las transacciones.
> **IPFS** (Sistema de archivos interplanetario, sistema de archivos interplanetario): protocolo de distribución y almacenamiento de archivos descentralizado, utilizado en este documento técnico para el alojamiento resistente a la censura de aplicaciones front-end (incluso si el nombre de dominio está bloqueado, los usuarios aún pueden acceder a la plataforma a través de IPFS).

---

## Capítulo 5: Modelo económico de tokens

### 5.1 Base de diseño total

**Suministro total de LIGHT: 2.500 millones (2.500.000.000), y nunca se emitirá adicionalmente. **

| Proyectos de benchmarking | Importe total | Métodos de participación | Comparabilidad con LightDAO |
|---------|------|---------|------------------|
| Bitcoin | 21 millones | Máquina de minería PoW | Referencia narrativa, el umbral es muy alto |
| Helio (HNT) | 223 millones | Punto de acceso de hardware $200+ | Punto de referencia DePIN, escala limitada de hardware |
| Filecoin (FIL) | 2 mil millones | Hardware de almacenamiento | Los más cercanos en magnitud, ambos están "aportando recursos a cambio de tokens" |
| Kaspa (KAS) | 28,7 mil millones | Tarjeta gráfica PoW | Una caída demasiado grande y suave tiene un valor de referencia |
| Red Pi | 100 mil millones | Clics móviles | Material didáctico negativo: la cantidad total es demasiado grande → la percepción del valor es extremadamente baja |

**Razón principal para elegir 2.500 millones de monedas:**

1. **Capacidad de inversión (restricción principal):** 850 millones de monedas en la bóveda × precio base $0,15 × tasa de utilización del 75% = **$95,63 millones ≈ $100 millones** capital desplegable, alcanzando el umbral mínimo creíble de PE del mercado medio bajo. Base académica: Cong, Li & Wang (2021) "Tokenomics: Dynamic Adoption and Valuation" (*Review of Financial Studies* 34(3):1105-1155, NBER w27222) demuestra que la utilidad de la plataforma (retorno de la inversión → recompra → soporte de precios) es el impulsor fundamental del valor simbólico, no la amplitud de la distribución.
2. **Guía de red:** Se extraen mil millones de monedas y se liberan 684,900 monedas el primer día de la época. Cuando hay 100.000 mineros activos, la media per cápita es de 6,51 LUZ/día, manteniendo la "percepción de entero".
3. **Viabilidad operativa:** 10% de fondo operativo estratégico (250 millones de monedas) para resolver la brecha de desarrollo/auditoría/financiamiento legal anterior a TGE ($1,10-2,85 millones). El modelo comunitario puro no puede cubrir este coste.
4. **Viabilidad de la deflación:** El resultado final de mil millones de monedas se alcanza entre los años 11 y 12 según el escenario base (un 25-30 % menos que los 15 años o más del plan de 21 mil millones).
5. **Evaluación comparativa razonable:** El mismo nivel que Filecoin (2 mil millones), que se encuentra entre los cinco proyectos principales en el campo DePIN por valor de mercado.

### 5.2 Plan de distribución de tokens

| Categoría de asignación | Proporción | Cantidad | Propósito | Método de liberación |
|---------|------|------|------|---------|
| Minería de nodos ligeros | 40% | 1 mil millones | Colaboradores de la red de recompensas | Reducido a la mitad cada 2 años, publicado en tiempo real según la contribución |
| Bóveda de Inversión Corporativa | 34% | 850 millones de piezas | Ejecución de inversiones bajo gobernanza DAO (destruida al invertir) | Bloqueo multifirma, sólo liberado y destruido mediante resoluciones válidas |
| Fondo de Desarrollo Ecológico | 16% | 400 millones | Liquidez, lanzamientos aéreos, financiación de desarrolladores, operaciones comunitarias | Lanzamiento gradual (ver Sección 5.3) |
| Fondo operativo estratégico | 10% | 250 millones de monedas | Equipo, auditoría, legal, infraestructura, inversores estratégicos | 12 meses cliff + 36 meses lineales (ver sección 5.X) |

**Evaluación comparativa de la industria (comparativa de cohorte de Tokenomics.net 2024-2025):** Recompensas para la comunidad/usuario 20-35 % (LightDAO: 40 % minería + 16 % ecología = 56 %, mayor debido a que no hay ronda de VC); tesorería/reservas 15-25% (LightDAO: 34%, debido a la función de inversión); equipo/inversores 15-45% (LightDAO: 10%, muy por debajo de la industria, manteniendo la narrativa "National DAO").

### 5.3 Plan de Liberación del Fondo de Desarrollo Ecológico

| Etapa | Hora | Proporción | Cantidad | Propósito |
|------|------|------|------|------|
| TGE | Día 0 | 30% | 120 millones de piezas | Liquidez DEX (60% = 72 millones) + lanzamiento aéreo de semillas (40% = 48 millones) |
| Período de liberación lineal 1 | 1.º al 12.º mes | 40% | 160 millones de monedas | 13,33 millones de monedas por mes: incentivos comunitarios, marketing, plan de lanzamiento aéreo |
| Período de liberación lineal 2 | 13 al 24 | 30% | 120 millones de monedas | 10 millones de monedas al mes: financiación de promotores, construcción ecológica, reservas |

### 5.4 Fondo de Operación Estratégica (250 millones de monedas)

| Subcategoría | Proporción | Cantidad | Objeto | Regla de liberación |
|--------|------|------|------|---------|
| Servicio de intercambio de tokens | 50% | 125 millones de monedas | Empresas promotoras, entidades de auditoría, despachos de abogados, operadores verificadores | 12 meses acantilado + 36 meses lineales; 30-50% de las tarifas de servicio pagadas en LIGHT |
| Financiamiento estratégico | 30% | 75 millones de piezas | 2-3 fondos ecológicos DePIN/Cosmos o partidos estratégicos de la industria de consumo | La versión anterior a TGE se vendió por entre 0,03 y 0,05 dólares (recaudando entre 2,25 y 3,75 millones de dólares); 12 meses acantilado + 24 meses lineales; inversor único ≤ 2% del total |
| Contribuyentes principales | 20% | 50 millones de monedas | 3-5 patrocinadores/constructores principales | 12 meses acantilado + 36 meses lineales; publicado en base a una evaluación trimestral de hitos; no venta durante el plazo |

**Requisitos estratégicos para inversionistas:** Se deben proporcionar contribuciones no financieras (una de flujo de transacciones, servicios de verificación, recursos de cumplimiento) y no se aceptan inversionistas puramente financieros.

**Cumplimiento normativo:** La venta previa a TGE adopta la exención de doble vía Reg S (inversores no estadounidenses) + Reg D Rule 506(c) (inversores calificados de EE. UU.).

**Reglas de divulgación de los contribuyentes principales:** Solo se divulga el monto total (50 millones = 2 % del monto total) y las reglas de divulgación, y no se divulgan los nombres personales ni las cuotas individuales. Categorías de roles divulgadas: Tecnología/Inversión/Cumplimiento/Comunidad.

### 5.5 Producción minera y plan de reducción a la mitad

**Derivación:** 2A = 1 billón → A = 500 millones (Primera Era). Liberación diaria = 500 millones ÷ 730 = 684.932 piezas ≈ 684.900/día. Cada bloque = 684.932÷49.371 ≈ 13,87 LUZ.

**Nota:** El grupo de recompensas para cada bloque es compartido por toda la red, del cual el 5% se asigna a los validadores (34,200/día) y el 95% se asigna a los mineros de nodos ligeros (650,700/día).

| Época | Hora | Producción total | Lanzamiento diario | Fondo de recompensas por bloque |
|------|------|---------|---------|------------|
| 1ª Época | 0-24 meses | 500 millones | ≈684.900 | ≈13,87 LUZ |
| 2da Época | 25-48 meses | 250 millones de piezas | ≈342.500 | ≈6,93 LUZ |
| La 3ra Era | 49-72 meses | 125 millones de piezas | ≈171.200 | ≈3,47 LUZ |
| La 4ta Era | 73-96 meses | 62,5 millones de piezas | ≈85.600 | ≈1,73 LUZ |
| La Quinta Era | 97-120 meses | 31,25 millones de piezas | ≈42.800 | ≈0,87 LUZ |

**Compruebe:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = mil millones ✓. 97% completado dentro de los primeros 10 años.

### 5.6 Modelo de referencia de ingresos de los usuarios

| Tamaño de la red | Ingreso diario per cápita | Ingresos mensuales | Ingresos anuales | Margen total (1,44x) ingreso mensual |
|---------|-----------|----------------|--------|------------------|
| 10.000 mineros (etapa semilla) | ≈65,07 | ≈1.952 | ≈23,751 | ≈2.811 |
| 100.000 mineros (etapa de crecimiento) | ≈6,51 | ≈195,2 | ≈2.375 | ≈281,1 |
| 1 millón de mineros (período de escala) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28,1 |

**Nivel de socio (50 invitaciones, 20% de participación, bonificación completa):**

| Escala de red | Auto (incluido el bono) | Compartir invitación | Integral diario | Integral mensual |
|---------|------------|-----------------|--------|--------|
| 10.000 mineros | ≈93,7 | ≈650,7 | ≈744,4 | ≈22,332 |
| 100.000 mineros | ≈9,37 | ≈65,07 | ≈74,44 | ≈2,233 |
| 1 millón de mineros | ≈0,94 | ≈6,51 | ≈7,45 | ≈223,4 |

### 5.7 Plan de crecimiento de lanzamiento aéreo

**Modelo económico:** Presupuesto total de lanzamiento aéreo = usuarios objetivo alcanzados × lanzamiento aéreo per cápita × (1+tasa de desperdicio) = 100.000 × 150 LUZ × 1,3 ≈ 19,5 millones (tipo de adquisición) + 35,5 millones (tipo ecológico) = **55 millones** (que representa el 13,75% del fondo ecológico de 400 millones).

| Tipo de lanzamiento aéreo | Condiciones de activación | Cuota única | Presupuesto |
|---------|---------|---------|------|
| Primer lanzamiento aéreo minero | Completó 4 horas de minería efectiva por primera vez | 50 LUZ | 15 millones de piezas |
| Expansión geográfica | Los usuarios del mercado objetivo completan ZK-KYC | 100 LUZ | 10 millones de piezas |
| Aprender a ganar | Módulo educativo completo + cuestionario | 30 LUZ | 6 millones de monedas |
| Primera votación sobre gobernanza | Primera participación en la votación | 20 LUZ | 3 millones de monedas |
| Provisión de liquidez | Inyección LP ≥$50 bloqueo por 30 días | 200 LUZ | 10 millones de piezas |
| Creación de contenido | Tutoriales/traducciones verificados por la comunidad | 50-200 LUZ | 6 millones de piezas |
| Canales de cooperación | Registro + primera minería a través de socios | 80 LUZ | 5 millones de piezas |

**Verificación CAC:** 55 millones de monedas × $0,03 = $1,65 millones ÷ 30.000 mineros activos retenidos = **$55/persona** (rango de la industria $50-200, en el extremo inferior). Base académica: Zheng (2023) "Operación Dumbo Drop: ¿Lanzar desde el aire o no para el éxito de la oferta inicial de monedas?" demuestra que la tasa de retención de los lanzamientos aéreos vinculados a eventos es de 3 a 5 veces mayor que la de los lanzamientos aéreos puros.

**Anti-abuso:** Huella digital única del navegador + ZK-KYC; limitado a 1 reclamo por categoría por dirección; período de bloqueo de 30 días; Reciclaje automático sin actividad en la cadena dentro de los 30 días posteriores al reclamo.

### 5.8 Volante de motor dual y grupo capital

Volante: Votación → Destrucción de Vault LIGHT → Pago en USDC → Reflujo de ganancias → Recompra y destrucción → Soporte de precios → Más usuarios.

Sistema de doble vía: tesorería estable (USDC, retención de ganancias) + tesorería flexible (capa LIGERA, destruida al invertir y que no fluye hacia el mercado). Las recompras se dividen mediante TWAP, con una sola orden ≤ 5% del volumen de negociación diario promedio.

### 5.9 Emisión y negociación de subtokens

El monto total de la emisión = monto de la inversión ÷ $1; el precio de cambio se basa en VWAP de 30 días; toda LUZ obtenida del intercambio será destruida; Se distribuirá el 50 % de los seguidores/30 % del lanzamiento aéreo/20 % de la reserva operativa (bloqueado durante 6 meses). El límite de dividendo para una sola dirección es del 15%. Los subtokens se negocian en la AMM en cadena, con un período de bloqueo de 30 días después de su emisión, y se marcarán como "liquidados" después de su retiro.

### 5.10 Liquidez inicial y descubrimiento de precios

**Disposición TGE (Evento de generación de tokens, evento de generación de tokens): **

| Proyecto | Plano |
|------|------|
| Fondo de liquidez inicial | De los 120 millones de piezas liberadas por el fondo de desarrollo ecológico TGE, 72 millones de piezas (60%) se asignaron e inyectaron en el fondo de liquidez DEX |
| Activos emparejados | USDC (grupo principal), USDT (grupo auxiliar) |
| Lanzamiento aéreo | Los 48 millones restantes (40%) se utilizarán para lanzamientos aéreos a usuarios de semillas (consulte la Sección 5.7 Plan de lanzamiento aéreo) |
| Cotizado en bolsas | Cotizó por primera vez en intercambios descentralizados (como Osmosis, JunoSwap) después de TGE; solicitar cotización en bolsas centralizadas a partir del sexto mes, según las condiciones de cumplimiento |

**Mecanismo detallado de la subasta holandesa:**

La subasta holandesa es un método de fijación de precios en el que los precios disminuyen de mayor a menor. A diferencia de las subastas inglesas (donde los precios se ofertan de menor a mayor), en una subasta holandesa el vendedor fija un precio inicial alto y el precio disminuye automáticamente con el tiempo hasta que el comprador envía una suscripción a un precio determinado. El primer precio al que el importe total de la suscripción alcanza el objetivo es el precio de apertura final.

**¿Por qué elegir una subasta holandesa en lugar de una subasta de precio fijo o inglesa?**

| Precios | Ventajas | Desventajas | Aplicabilidad |
|---------|------|------|--------|
| Preventa a precio fijo | Sencillo | El precio es subjetivo, si es demasiado alto, no se venderá, si es demasiado bajo, los robots lo adquirirán | No adecuado (sin función de descubrimiento de precios) |
| Subasta británica (licitación) | Descubrimiento de precio completo | Los grandes compradores pueden esperar estratégicamente y subir los precios; guerra del gas | No adecuado (la guerra del gas en cadena excluye a los pequeños usuarios) |
| **Subasta holandesa** | **Descubrimiento automático de precios; no se requiere licitación (no hay guerra del gas); participación igualitaria de grandes y pequeños compradores; anti-bot (el mecanismo de reducción de precios inhibe naturalmente el avance)** | El precio inicial y la tasa de desaceleración deben fijarse de manera razonable | **Más adecuado (justo + eficiente + antimanipulación)** |

**Parámetros específicos de la subasta holandesa LightDAO:**

| Parámetros | Configuración | Descripción |
|------|------|------|
| Objetivo de subasta | Tokens LIGHT (asignados de los 72 millones liberados por el fondo ecológico TGE) | El USDC de la subasta se inyectará en la bóveda del establo |
| Monto objetivo de recaudación de fondos | **$15 millones de dólares** | $5 millones → reserva mínima de tesorería estable; 10 millones de dólares → capital de inversión inicial |
| Precio inicial | $0.20/LUZ | Más alto que el precio de equilibrio esperado, asegurando que no se perderá en segundos |
| Tasa de desaceleración | Disminución del 5% cada hora | A partir de $0,20, cayendo a $0,017 después de aproximadamente 48 horas (si nadie se suscribe) |
| Precio mínimo de reserva | $0.01/LUZ | Si se baja el precio de reserva y aún no se alcanza el objetivo, la subasta se pospondrá 24 horas o se ajustará el número de objetos |
| Método de suscripción | El usuario envía "Estoy dispuesto a comprar X USDC equivalente a LIGHT al precio actual" | No es necesario pujar, el sistema liquidará según el precio final unificado (el exceso se reembolsará sin compensación) |
| Límite superior de usuario único | No más del 5% del monto objetivo de recaudación de fondos (es decir, 750 000 dólares) | Evitar que un único comprador monopolice las fichas iniciales |
| Requisitos KYC | Verificación mejorada (residencia fiscal) | Requisitos de cumplimiento |

**Destino de los fondos según los resultados de la subasta:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Período de protección de descubrimiento de precios:** Se establece un disyuntor de fluctuación de precios en las primeras 72 horas después de TGE: si el precio de la transacción DEX se desvía en más de ±50% del precio de apertura de la subasta, la función de intercambio de subtokens se suspenderá (la minería y las transferencias no se verán afectadas) para evitar que la especulación extrema interfiera con la puesta en marcha ecológica. El fusible se liberará automáticamente después de 72 horas.

**Por qué $15 millones en lugar de menos:** El capital de inversión inicial de $10 millones debe respaldar de 3 a 5 inversiones en el primer año (una sola inversión equivale a $2-5 millones; consulte la escala del período de inicio en la Sección 9.1). Si sólo se recaudan 5 millones de dólares (todos como reservas), no habrá capital de inversión disponible durante el primer año y el volante no arrancará. 15 millones de dólares = reserva de 5 millones de dólares + inversión de 10 millones de dólares, que es el equilibrio mínimo viable entre el "resultado final de seguridad" y el "inicio del volante".

### 5.11 Mecanismo de deflación y resultado final

**Volumen de circulación = liberación minera + liberación ecológica + fondo estratégico liberado − intercambio y destrucción − destrucción de gas − recompra y destrucción. ** 850 millones de monedas de la bóveda de inversiones nunca han entrado en circulación. Límite superior teórico de circulación = 10+4+2,5 = **1,65 mil millones**.

| Condiciones de activación | Comportamiento del sistema |
|---------|---------|
| Circulación ≤ 1,5 mil millones de piezas | Señal de desaceleración (escenario de destrucción extremadamente baja) |
| Volumen de circulación ≤ 1,2 mil millones de piezas | Anuncio de alerta temprana, suspensión de la destrucción activa (aproximadamente el octavo año del escenario base) |
| Volumen de circulación ≤ mil millones | Parada brusca, todas las destrucciones están cerradas permanentemente (el escenario base es aproximadamente el año 11-12) |

### 5.12 Mecanismo de estabilización de precios (espiral anti-muerte)

**Principio básico:** LightDAO no interfiere con el descubrimiento diario de precios de mercado. El protocolo sólo ajusta sus parámetros en escenarios extremos a la baja para reducir el riesgo de caer en una "espiral de muerte".

**Lógica de calificación:** En diferentes entornos volátiles, la misma disminución representa diferentes grados de anormalidad. Una fuerte caída en un mercado de baja volatilidad es una señal anormal más fuerte y requiere una intervención de mayor intensidad; una fuerte caída en un mercado de alta volatilidad es relativamente común y se puede utilizar una intervención más ligera. Por tanto, la intensidad de la intervención se relaciona positivamente con la anormalidad de la señal, en lugar de depender únicamente del valor absoluto de la disminución.

**Diagrama de flujo completo del mecanismo:**

| 市场状态 | 30日历史波动率 | 触发条件 | 信号等级 | 触发后执行 | 恢复条件 |
|---------|--------------|---------|---------|-----------|---------|
| 低波动 | ≤30% | 连续5日累计跌幅≥40% | I级 | 挖矿产出降至50%；销毁比例由20%提升至35%；风险参数调整公示期由72h缩短至12h；影子委员会进入激活状态（仅可依法行使临时暂停权） | 价格站上30日均线，且较触发价反弹≥80%，并连续保持10日 |
| 中波动 | 30%—60% | 连续7日累计跌幅≥50% | II级 | 挖矿产出降至50%；销毁比例由20%提升至30%；公示期缩短至24h；影子委员会进入激活状态 | 价格站上30日均线，且较触发价反弹≥60%，并连续保持7日 |
| 高波动 | 60%—100% | 连续10日累计跌幅≥55% | III级 | 挖矿产出降至75%；销毁比例由20%提升至25%；公示期缩短至48h；影子委员会进入待命状态 | 价格站上30日均线，且较触发价反弹≥40%，并连续保持5日 |
| 极端波动 | >100% | 连续10日累计跌幅≥65% | III级 | 按高波动状态的III级措施执行 | 按高波动状态的III级恢复条件执行 |

**Condiciones de exclusión:** Solo cuando la caída de Bitcoin en el mismo período es inferior al 50 % de la caída de LIGHT, se puede activar el mecanismo anterior para descartar un colapso sistémico del mercado (es decir, si BTC también se desploma en el mismo período, es un evento general del mercado y no se inicia ninguna intervención separada para LIGHT).

**Descripción de la lógica de recuperación:** Los requisitos de rebote y la duración disminuyen con el nivel de anomalía: el nivel I requiere la amplitud de rebote más alta (80 %) y el tiempo de confirmación más largo (10 días), mientras que el nivel III requiere requisitos relativamente más bajos (40 %/5 días). Este acuerdo está en consonancia con la lógica progresista de que "cuanto más fuerte sea la señal anormal, más fuerte será la intervención y más estricta será la confirmación de la recuperación".

**Fuente de datos de volatilidad y precios:** La volatilidad histórica de 30 días y la caída acumulada son proporcionadas por el oráculo de precios en cadena (ver Sección 4.10), basado en la instantánea TWAP del bloque diario UTC de las 00:00, y no dependen de ninguna fuente de datos externa.

### 5.13 Prueba de estrés de sostenibilidad de ganancias

| 压力情景 | 假设条件 | 协议应对 | 最坏结果 |
|---------|---------|---------|---------|
| 全部投资失败 | 所有被投企业亏损或退出失败 | 保险基金（利润10%计提）覆盖部分损失；稳定金库储备（≥$800万）维持运营；暂停新投资直至社区重新评估 | 子代币持有者无法获得分红；LIGHT价格承压但不归零（挖矿和治理功能持续运行） |
| 市场暴跌80% | LIGHT价格较峰值下跌80% | 触发防死亡螺旋机制（II级或III级）；挖矿产出削减50-75%；销毁比例提升；影子委员会可暂停高危操作 | 用户收益缩水但网络持续运行；恢复条件达成后机制自动解除 |
| 主要市场监管禁令 | 某大国全面禁止加密资产 | 前端切换 IPFS 镜像保持可访问；链上资产与已有用户权益不受影响；仅在法律强制范围内调整第三方服务可用性；SPV在开曼群岛运营不受单一国家管辖 | 该区域用户增长停滞；全球其他区域不受影响 |
| 用户大规模流失 | 活跃矿工下降超70% | BaseReward自动重新分配（分母缩小→留存用户人均收益上升）；邀请激励加权吸引回流；治理门槛临时下调（5.14节动态机制） | 网络安全性下降但不会停链（Tendermint BFT容忍<1/3验证者离线） |
| 智能合约重大漏洞 | 核心合约被发现可利用漏洞 | 多签紧急暂停资金流出（72小时时间锁提供响应窗口）；发起备用合约迁移投票（L4级紧急修复，见4.12节）；保险基金覆盖用户损失 | 部分资金可能受损；迁移完成后恢复正常运营 |

### 5.14 Mecanismo de equilibrio intergeneracional

Ajuste dinámico del umbral de gobernanza: por cada millón de nuevos mineros activos acumulados, el umbral de propuesta se reduce automáticamente en un 5% (límite inferior 2500 LIGHT).

> **[Terminología en este capítulo]**
> **TGE** (Evento de generación de tokens): el momento en el que un token se crea y distribuye por primera vez a través de un contrato inteligente, generalmente acompañado por el establecimiento de un fondo de liquidez inicial, el precio de subasta holandés y la primera transacción pública. Similar a una IPO en las finanzas tradicionales, pero no implica una cotización en bolsa.
> **Halving** (Reducir a la mitad): Un mecanismo mediante el cual la producción minera se reduce automáticamente en un 50% cada período fijo (2 años/730 días para LightDAO). El objetivo es crear una escasez progresiva: a medida que pasa el tiempo, se agrega cada vez menos oferta nueva y, si la demanda no disminuye, los precios se mantendrán. Bitcoin adopta la reducción a la mitad cada 4 años.
> **Tesorería** (Tesorería): Reservas de tokens bloqueadas por contratos de firmas múltiples, que solo pueden liberarse mediante resoluciones de gobernanza. LightDAO tiene dos tipos de bóvedas: bóvedas de inversión (que contienen LIGHT y se destruyen cuando se ejecutan las inversiones) y bóvedas estables (que contienen USDC y se utilizan para pagar la contraprestación de la inversión y los gastos operativos).
> **Deflación** (Deflación): El proceso en el que la oferta o circulación total de tokens continúa disminuyendo. LightDAO logra la deflación a través de cuatro mecanismos: ejecución y destrucción de inversiones, intercambio y destrucción de subtokens, destrucción de tarifas de gas (50%) y recompra y destrucción de ganancias.
> **Espiral de la Muerte** (Espiral de la Muerte): Los precios de los tokens caen → los ingresos de los mineros se reducen → los mineros abandonan → la seguridad/contribución de la red disminuye → una mayor pérdida de confianza → un círculo vicioso en el que los precios continúan cayendo. El mecanismo de intervención gradual de la Sección 5.12 está diseñado para interrumpir este ciclo.
> **Subtoken** (Subtoken): certificado de reclamo de distribución de ingresos de SPV emitido de acuerdo con las reglas después de que se completa cada inversión corporativa (como la adquisición de una marca de café → token CAFE). Tener subtokens = tener calificaciones para la distribución de ganancias futuras y no representa derechos de los accionistas ni derechos de gobierno corporativo.
> **LP** (Proveedor de liquidez): los participantes que inyectan dos activos de igual valor (como LIGHT+USDC) en el fondo de liquidez DEX obtienen a cambio tarifas de transacción. LP es la base para el funcionamiento normal de DEX.
> **VWAP** (Precio promedio ponderado por volumen): El precio dentro de un período de tiempo se pondera por el volumen de cada transacción, lo que refleja el verdadero costo de transacción del mercado. LightDAO utiliza VWAP de 30 días como referencia de precios para el intercambio de subtokens.
> **CAC** (Costo de Adquisición de Clientes, costo de adquisición de usuarios): El costo promedio para adquirir un usuario activo efectivo. El CAC objetivo del programa de lanzamiento aéreo LightDAO es de $55/mineros activos retenidos (rango de la industria de $50-200).
> **wLIGHT** (LUZ envuelta, LUZ encapsulada): tokens equivalentes a LUZ emitidos en Ethereum o Solana a través de puentes entre cadenas, y una cantidad igual de LUZ nativa está bloqueada por el contrato puente como reserva 1:1. El propósito es permitir que los usuarios del ecosistema que no pertenecen a Cosmos obtengan y mantengan LUZ.
> **Dutch Auction** (Subasta holandesa): Un método de fijación de precios en el que el precio disminuye de mayor a menor. El vendedor establece un precio inicial alto y el precio disminuye automáticamente con el tiempo hasta que el comprador envía una suscripción a un precio determinado. El primer precio al que el monto total de la suscripción alcanza el objetivo es el precio final de la transacción. La ventaja es que no se requiere oferta (no hay guerra de gas), los compradores de todos los tamaños son iguales y, naturalmente, es resistente a la preferencia de los robots.

---

## Capítulo 6: Mecanismo de gobernanza

### 6.1 Modelo de votación bidimensional

Peso de tenencia de moneda (incluida reputación + bonificación de nivel, límite superior total +40%) + número de direcciones (1 dirección = 1 voto, las direcciones asociadas se fusionan). Los derechos de voto son válidos por 90 días y se pueden activar transfiriendo 5 LUCES. Bonificación de reputación: Mantener la moneda durante 1 año + 15 votos válidos → hasta +30%.

### 6.2 Tasa de aprobación dinámica

Tasa mínima de aprobación = 50% + (50% - tasa de votación real). Mayoría simple cuando la tasa de votación es ≥50%.

### 6.3 Parámetros de la propuesta

| Tipo | Margen | Tasa de votación de tokens | Tasa de votación de direcciones | Tasa de aprobación | Retraso de ejecución |
|------|--------|-----------|-----------|----------------|---------|
| micro | $100 | ≥15% | ≥20% | Dinámico ≥55% | 24h |
| Tipo de adquisición | $500 | ≥25% | ≥30% | Dinámico ≥60% | 72h |
| Tipo de capital riesgo | $500 | ≥35% | ≥40% | Dinámico ≥60% | 72h |
| Mayor | $1,000 | ≥45% | ≥50% | Dinámico ≥66% | 72h |
| Emergencia | $2,000 | ≥50% | ≥60% | ≥75% | Sin financiación 6h/alto riesgo 1h; las operaciones de capital siguen sujetas a un bloqueo temporal de 72 horas |

### 6.4 Ciclo de vida de la propuesta

Calificación de envío: ≥5,000 LIGHT + 30 días consecutivos de prenda + depósito. Convocatoria pública 72h (revisada ≤ 2 veces). La votación se realiza en un plazo de 7 días (48 horas para la vía rápida, ≤500.000 USDC). Veto se enfría durante 90 días. La eficacia se retrasa 24 horas.

**Descripción del umbral:** 5000 monedas en la etapa inicial (10 000 mineros) ≈ 77 días de producción básica; nivel de socio ≈ 7 días. La gobernanza se activará en el séptimo mes y los primeros usuarios tendrán suficiente tiempo de acumulación.

### 6.5 Incentivos al voto

Hay un incentivo básico por participar (incluso compartir) y hay una bonificación adicional por el juicio correcto (50% del fondo de apuestas). Apuesta por el rango 5-500 LIGHT. Suprimir el efecto de manada: los oponentes siguen recibiendo incentivos básicos incluso si están "en el equipo equivocado".

### 6.6 Recompensas y penalizaciones por el éxito o el fracaso

Fallo de buena fe: reembolso del 50% del depósito + 30 días de recuperación. Fallo malicioso (falsificación/repetición): importe total confiscado + prohibición permanente. Prueba de fraude: tope de 5.000 LIGHT, penalización del 40% del bono de establecimiento + 500 LIGHT.

### 6.7 Transparencia financiera

Panel de control en tiempo real de la cadena + informe financiero trimestral + auditoría independiente anual (la primera auditoría debe completarse antes del TGE) + divulgación de objetivos de inversión en tiempo real.

---

## Capítulo 7: Controles y equilibrios de poder y definición de roles

### 7.1 Tutor inicial

Los permisos se limitan a la información del documento/formato/sitio web oficial. Plazo ≤ 24 meses. Se debe designar un tutor alternativo (no se puede firmar durante 30 días consecutivos → se asume automáticamente). Invalidez simultánea → Votación de emergencia de 48h para designar gerente interino.

### 7.2 Hoja de ruta de transferencia de energía

| Etapa | Hora | Permisos | Aprobación de inversión |
|------|------|------|---------|
| Periodo de creación | 0-6 meses | Tutor (no financiero) | Guardian + multifirma comunitaria 3/5 |
| Período de transición | julio-diciembre | Guardian + colaborador principal firmado conjuntamente | Igual que arriba + colaborador principal |
| Periodo de vencimiento | 13-24 meses | Comité de Gobernanza 3/5 | Votación bidimensional periódica |
| Periodo de autonomía | 25 meses + | Todos los titulares | Mismo plazo de vencimiento |

### 7.3 Comité de Gobernanza

El poder se divide entre cinco personas (presidente rotativo/finanzas/tecnología/comunidad/clave), rotación trimestral, el mandato es de seis meses y puede ser reelegido una vez. La campaña promete 50.000 firmas conjuntas de LIGHT + 100 direcciones. La toma de decisiones involucra a ≥3 personas y cubre ≥3 puestos.

**Descripción del umbral:** 50.000 monedas en la etapa inicial ≈ 67 días (2,2 meses) para socios; en la etapa de crecimiento ≈ 672 días (22 meses). La primera elección del comité en el mes 13 está disponible para los primeros socios.

### 7.4 Comité en la sombra

Suspensión temporal únicamente por "violaciones/sanciones/fraude grave". Todos los votos deben ser ratificados en un plazo de 72 horas (oposición >60%→desestimada). Rechazado dos veces seguidas → automáticamente impugnado y disuelto.

### 7.5—7.6 Verificación de campaña y plan clave

SimHash>80% descalificación; El contenido de IA debe complementarse con explicaciones; Se descontará el 20% de los votos por preguntas ausentes. Copia de seguridad de fragmentos de claves + verificación de estado trimestral + anuncio público de 7 días + reemplazo de votación.

---

## Capítulo 8: Mecanismo de confianza y seguridad

### 8.1 Cinco mecanismos de seguridad principales

Bloqueo temporal 72 h (las propuestas de emergencia no están exentas de operaciones de capital); firma múltiple 3/5; rotación trimestral ≤ 2 sesiones; Sanción del 100% por fraude; todas las transacciones están en la cadena.

### 8.2 Fondo de Seguro

**Se acumula el 10%** de los beneficios de la inversión exitosa. Las reclamaciones deben informarse de forma independiente + DAO 66 % a favor + single ≤ pool 20 %. Fuente complementaria: 30% de la multa por falsificación. Colocar un "búfer parcial" no es una protección total.

### 8.3 Plan extremo

Supervisión cisne negro → IPFS + eliminación de derechos de administrador; fraude → suspensión del comité paralelo (ratificación de 72 horas) + fondo de seguro + arbitraje SPV; espiral de muerte → Mecanismo de la Sección 5.12; vulnerabilidad del contrato → suspensión de firmas múltiples + votación de migración; validadores colectivamente haciendo el mal → Tolerancia BFT <1/3, si se excede, la cadena se suspenderá + migración de votación de emergencia.

---

## Capítulo 9: Operaciones de inversión y estrategias de salida

### 9.1 Selección y escala de los objetivos de inversión

**Trayectoria de crecimiento etapa por etapa de la escala de inversión (fórmula: superávit de tesorería × ​​15% × precio LIGHT): **

| Etapa | Precio LUZ | Límite de transacción única en el período inicial de la bóveda | Objetivos de adaptación | Evaluación comparativa de la industria |
|------|----------|------------------|----------|----------|
| Período de puesta en marcha (Y1-2) | $0,02—$0,05 | 2,55 millones de dólares—6,37 millones de dólares | Tienda única/cadena pequeña, ángel redondo | MicroPE |
| Etapa de crecimiento (Y3-5) | $0,05—$0,30 | 6,37 millones de dólares—38,25 millones de dólares | Cadena regional de 30 a 200 tiendas, ronda Seed-A | PE del mercado medio bajo |
| Etapa de madurez (Y5-8) | $0,30—$1,00 | 38,25 millones de dólares—127,5 millones de dólares | Cadena multinacional/mediana tecnología, ronda B-C | PE del mercado medio |
| Período de escala (Y8+) | $1.00+ | 127,5 millones de dólares+ | Adquisiciones a gran escala, Pre-IPO | PE a gran escala/VC en etapa de crecimiento |

### 9.2 Proceso de toma de decisiones de inversión

Descubrimiento de proyecto (≥5.000 LIGHT) → due diligence independiente → anuncio público 72h → votación bidimensional → ejecución 24/72h.

### 9.3 Salida y distribución de beneficios

Dividendo anual: **40%** poseedores de sub-tokens / **30%** bóveda estable / **20%** recompra de LUZ para destrucción / **10%** fondo de seguro.
Ingresos de salida: **70%** Bóveda estable / **30%** Recompra y quema.

### 9.4 Disciplina de inversión

| Reglas | Contenido |
|------|------|
| Límite de destrucción único | Bóveda restante × 15% (inicial 850 millones × 15% = 127,5 millones de monedas) |
| Objetivo único | ≤25% del valor total de la bóveda |
| Concentración industrial | ≤40% de la cartera |
| Concentración geográfica | ≤30% de la cartera |
| Reservas del tesoro estables | $5 millones en TGE (subasta), llegando a $8 millones al mes 24 |
| Período de reflexión | 2 fallos consecutivos → 180 días |

**Capacidad de la bóveda:** 850 millones de piezas × 0,10 dólares = 85 millones de dólares (capacidad total inicial); × 0,30 dólares = 255 millones de dólares; × $1,00 = $850 millones. El límite de transacción única del 15% hace que el ritmo de inversión esté relacionado positivamente con el precio.

> **[Terminología en este capítulo]**
> **EBITDA** (Ganancias antes de intereses, impuestos, depreciación y amortización): Un indicador que mide la rentabilidad de las operaciones principales de una empresa, eliminando la interferencia de la estructura financiera (intereses), la política fiscal (impuestos) y las opciones contables (depreciación/amortización), facilitando comparaciones entre empresas y entre industrias. Margen EBITDA = EBITDA ÷ resultado operativo.
> **DCF** (Flujo de caja descontado, método de flujo de caja descontado): Un método de valoración que convierte el flujo de caja futuro esperado de la empresa en el valor actual a una determinada tasa de descuento. Es adecuado para empresas maduras con flujo de caja estable (como cadenas de consumo), pero no para empresas de tecnología en etapa inicial que aún no son rentables.
> **IPO** (Oferta Pública Inicial): La primera vez que una empresa emite públicamente acciones en una bolsa de valores y cotiza en bolsa. Para LightDAO, la salida a bolsa de las empresas en las que invierte es una de las principales vías de salida de los motores de crecimiento.
> **Pre-IPO**: La última ronda de financiación de capital privado antes de que la empresa cotice oficialmente. Por lo general, la valoración se acerca al nivel posterior a la IPO, el riesgo es menor que en rondas anteriores, pero el múltiplo de rendimiento también es menor.
> **Ejecución TWAP** (Ejecución de precio promedio ponderado en el tiempo): divida las órdenes de recompra de gran cantidad en múltiples órdenes de pequeña cantidad y ejecútelas de manera uniforme durante un período de tiempo para evitar el impacto de una sola orden grande en el precio de mercado. LightDAO estipula que una sola recompra no excederá el 5% del volumen de negociación diario promedio.

---

## Capítulo 10: Hoja de ruta

| Fase | Hora | Objetivos centrales | Hitos clave | Requisitos previos |
|------|------|---------|-----------|-----------------|
| Periodo de preparación | Cuarto trimestre de 2026 | Entidad jurídica + equipo + fondos disponibles | Registro de entidad de Caimán/BVI completado; socio técnico o equipo de desarrollo firmado; intención estratégica del inversor confirmada (2-3 empresas); capital inicial ≥ 150.000 dólares vigente | el fundador determina el método de divulgación de la identidad; finalización de BP y Pitch Deck |
| Periodo de desarrollo | Q1-Q2 2027 | Desarrollo del sistema central | Se han desarrollado 10 módulos de contratos inteligentes; Se ha completado el desarrollo del front-end de PWA; Se han implementado 7 redes de prueba de verificación; la prueba Alpha interna ha pasado | Equipo de desarrollo implementado; documento de requisitos (especificaciones técnicas) finalizado |
| Período de auditoría y pruebas | Tercer trimestre de 2027 | Verificación de seguridad y cumplimiento | Publicación de un informe de auditoría de seguridad independiente (≥1 institución superior); publicación de carta de opinión de cumplimiento legal (MLM + ley de valores); Se pasaron 50.000 pruebas de estrés simultáneas; tasa de falsos positivos del sistema anti-trampas <2%; ejercicio de votación de gobernanza completado | Congelación del desarrollo de contratos (Code Freeze); honorarios de auditoría vigentes |
| TGE y mainnet en línea | Cuarto trimestre de 2027 | Emisión de tokens + lanzamiento de red | Se completó la subasta holandesa (objetivo de 15 millones de dólares); mainnet en línea (≥10 validadores); plataforma minera abierta al público; Se establece un fondo de liquidez DEX; lanzamiento aéreo de semillas emitido | Auditoría aprobada; validadores ≥7 (resultado final estricto); implementación del contrato de subasta |
| Período de construcción de creencias | Primer trimestre de 2028 (del 1.º al 3.er mes después de TGE) | 30.000-50.000 usuarios de semillas | Los mineros activos superaron los 30.000; primer ejercicio de votación de gobernanza; establecimiento de un canal comunitario multilingüe (inglés/chino/español/portugués/filipinas); primer informe comunitario mensual publicado | TGE completado; equipo de operaciones comunitarias establecido |
| Período de anclaje del valor | Q2-T3 de 2028 (cuarto al noveno mes después de TGE) | Primera inversión + gobernanza del período de transición | Primera propuesta de inversión aprobada (la aprobación con múltiples firmas durante el período de génesis se aplica entre el cuarto y sexto mes; la aprobación conjunta durante el período de transición se aplica a partir del séptimo mes); se completa la primera entrega SPV; los validadores están abiertos a elecciones (a partir del séptimo mes); se publica el primer informe financiero trimestral | tesorería estable USDC≥5 millones de dólares; se completa la diligencia debida sobre el objetivo de inversión |
| Período de vencimiento de la gobernanza | 2028 T4-2029 T1 (mes 10.º a 15.º después de TGE) | Elección del comité + transición a la descentralización | Primera elección del comité de gobierno (mes 13); Entrar en el plazo de vencimiento (3/5 decisión del comité); El puente entre cadenas wLIGHT se pone en línea; Se envía la solicitud de cotización en CEX; Comienza el plan de financiación para desarrolladores | Mineros activos ≥ 100.000; ≥ 100 direcciones candidatos conjuntos |
| Periodo de expansión ecológica | A partir del segundo trimestre de 2029 (mes 16 + después de TGE) | Replicación a gran escala | Los mineros activos superaban los 200.000-500.000; Se completaron 2-3 inversiones; la primera verificación de repatriación de beneficios; Comienza la recompra y destrucción de LIGHT | El comité de gobernanza funciona con normalidad; el modelo de inversión ha sido verificado |
| Período de operación madura | A partir del cuarto trimestre de 2029 (mes 25 + después de TGE) | Rotación del volante + autonomía total | Entrando en el período de autonomía (importantes propuestas de todos los titulares); despliegue de cartera de inversiones acumulada ≥ 30 millones de dólares; los datos de deflación son públicamente verificables | La gobernanza está completamente descentralizada |

**Principios de diseño de la hoja de ruta:**

- **Auditoría antes de TGE:** Nunca se emitirán tokens sin completar una auditoría de seguridad independiente. Esta es la garantía básica para la seguridad de los fondos de los usuarios.
- **Los verificadores están antes que los usuarios:** Cuando la red principal se conecte, habrá ≥10 verificadores (tolerancia a fallas BFT f≥3), lo que garantiza que la red no se cerrará debido a un único punto de falla.
- **La inversión precede a la expansión:** Sólo después de que la primera inversión sea exitosa y genere ganancias verificables podremos iniciar una expansión a gran escala. Evite poner el carro delante del caballo "haciendo circular a las personas primero y encontrando proyectos después".
- **Búfer de tiempo:** Reserve entre un 20 y un 30 % de margen de tiempo para cada etapa. El desarrollo de tecnología, las reparaciones de auditoría y los procesos legales pueden superar las expectativas, y la hoja de ruta no debería ser un "escenario más optimista".

**Relación con la fecha de publicación del Libro Blanco (4 de agosto de 2026):** El Libro Blanco se publicó en agosto de 2026 como una declaración pública de la visión y el diseño técnico del proyecto. La implementación real comenzará en el cuarto trimestre de 2026 (período preparatorio) y el objetivo del TGE es el cuarto trimestre de 2027. La brecha de aproximadamente 14 meses entre la publicación del documento técnico y el TGE se utilizó para la formación del equipo, el desarrollo, la auditoría y la preparación para el cumplimiento.

---

## Capítulo 11: Cultura comunitaria y ecología de desarrolladores

### 11.1 Cuatro valores

- **La transparencia es mejor que la perfección** - Es mejor revelar las imperfecciones que ocultar la perfección. Todos los flujos de tesorería, las decisiones de inversión y las votaciones de gobernanza están permanentemente disponibles en la cadena.
- **Gradual es mejor que radical** - Da pequeños pasos y sigue iterando. La primera inversión comenzará entre 2 y 5 millones de dólares y la escala se ampliará después de verificar el modelo.
- **Las responsabilidades son mejores que los derechos** - Los derechos y las obligaciones son iguales. Los miembros del comité de gobernanza deben prometer 50.000 LUZ y revelar su agenda política. Si no cumplen con sus deberes, serán multados.
- **La diversidad es mejor que la homogeneidad** - Las diferentes voces son la inmunidad del sistema. La votación bidimensional (moneda + dirección) garantiza que tanto las ballenas como los inversores minoristas tengan voz y voto.

### 11.2 Sistema de jurado

| Dimensiones | Reglas |
|------|------|
| Composición | Seleccione aleatoriamente 12 usuarios que tengan ≥10,000 LIGHT y no tengan antecedentes de infracción |
| Término | 30 días, se sorteará nuevamente al azar después del vencimiento |
| Responsabilidades | Escuche quejas de sanciones contra trampas, acusaciones de fraude de propuestas y disputas comunitarias |
| Proceso | Los usuarios sancionados pueden presentar pruebas en un plazo de 72 horas; el jurado deberá emitir veredicto en un plazo de 48 horas |
| Estándares de juicio | ≥8 de cada 12 personas (mayoría de 2/3) deben aceptar mantener o revocar la pena |
| Evitación | Reemplazo automático de jurados que tengan relación de invitación con las partes o estén en el mismo rango de IP |
| Remuneración | Recibe un subsidio diario por servicio de jurado de 5 LUZ durante la vigencia (desembolsado del fondo ecológico) |

### 11.3 Plan Ecológico Desarrollador

| Módulo | Contenido | Fuentes de financiación | Cómo aplicar |
|------|------|---------|---------|
| Financiamiento para desarrolladores (subvenciones) | Para los equipos que crean dApps, herramientas e infraestructura en la cadena LightDAO, una subvención única de entre 5 y 500 000 dólares equivalente a LIGHT | Fondo de Desarrollo Ecológico (Lanzamiento Lineal Fase 2) | Enviar una propuesta → Evaluación del oficial de revisión técnica → Votación de gobernanza (proceso de micropropuesta) |
| SDK y API | Proporcionar SDK de JavaScript/TypeScript, API REST e interfaces WebSocket para reducir el umbral para el desarrollo de terceros | Oficial de revisión técnica lidera el desarrollo | Código abierto, público en GitHub |
| Hackatón | Cada trimestre se celebra un hackathon online, con un premio acumulado de 100.000 dólares equivalente a LIGHT | Fondo de Desarrollo Ecológico | Inscripción abierta, sin umbral |
| Recompensa de errores | Programa de recompensas por errores del contrato principal, recompensa de entre 1000 y 50 000 dólares por una única vulnerabilidad válida (clasificada según la gravedad) | Fondo de Seguros + Fondo de Desarrollo Ecológico | Enviar a través de Immunefi o plataforma de construcción propia |
| Mercado de contratos CosmWasm | Aliente a terceros a implementar contratos inteligentes y el 20% de los ingresos por tarifas de gas se devolverá al tesoro ecológico para apoyar a los desarrolladores | Distribución de tarifas de gas (ver Sección 4.5) | Automático, no requiere solicitud |

### 11.4 Estrategia multilingüe y de localización

| 维度 | 规划 |
|------|------|
| 平台语言 | 首发支持英语、中文、西班牙语、葡萄牙语、菲律宾语；第6个月起增加法语、阿拉伯语、斯瓦希里语、印尼语 |
| 治理语言 | 提案和竞选纲领接受任何语言提交，系统提供机器翻译+社区人工校对 |
| 社区运营 | 按语言设立独立社区频道（Discord/Telegram），各频道配备本地化社区联络志愿者 |
| 文档翻译 | 白皮书及核心文档由社区翻译志愿者完成，翻译贡献计入"内容贡献"行为加成（5%） |
| 本地化资助 | 生态发展基金中预留10%（4,000万枚）专项用于本地化社区建设和翻译激励 |

---

## Capítulo 12: Equipo y Consultores

### 12.1 Definición de rol principal

| Rol | Responsabilidades | Requisitos de antecedentes | Métodos de divulgación |
|------|------|---------|---------|
| Tutor inicial/Patrocinador del proyecto | Implementar contratos iniciales, mantener documentos y coordinar operaciones iniciales | ≥ 3 años de experiencia en la industria blockchain, con registros de implementación de contratos inteligentes o operaciones de protocolo DeFi | Revelar su verdadera identidad ante TGE o proporcionar un informe de verificación de identidad de un tercero (como firma notarial + verificación de mensajes en cadena) |
| Líder técnico | Diseño de arquitectura de contrato, gestión de equipos de desarrollo, acoplamiento de auditoría | Experiencia en desarrollo de Cosmos SDK/CosmWasm, récord de implementación de la cadena de producción | Igual que arriba |
| Responsable de inversiones | Selección de objetivos, coordinación de diligencia debida, establecimiento de SPV, gestión de salida | Experiencia en la industria de capital privado/capital riesgo, con casos de salida completados | Igual que arriba |
| Consultor de cumplimiento | Diseño de estructura legal, acoplamiento regulatorio, asesoramiento en cumplimiento de MLM | Abogado con calificaciones en EE. UU., UE y Caimán | Nombre público del bufete de abogados (el nombre personal no se revelará a menos que esté de acuerdo) |

### 12.2 Consejo Asesor

- Compuesto por entre 3 y 5 consultores independientes, que cubren: tecnología DePIN, cumplimiento de inversiones transfronterizas, operaciones comunitarias e industrias de consumo;
- Los consultores reciben una remuneración por consultoría en forma de tokens LIGHT (desembolsados ​​por la parte "Service Token Exchange" del fondo operativo estratégico), y la posición está bloqueada durante 12 meses;
- La lista de consultores se hace pública ante el TGE y está abierta a consultas de la comunidad (reunión descentralizada de consulta de textos, ver Sección 7.5);
- Los asesores no podrán fungir simultáneamente como miembros del Comité de Gobernanza (segregación por conflicto de intereses).

### 12.3 Compromiso y limitaciones del equipo

| Restricciones | Reglas |
|------|------|
| Bloqueo de tokens | LIGHT (incluida la asignación estratégica de fondos operativos) en poder del equipo central debe bloquearse durante 12 meses y liberarse linealmente durante 36 meses después del desbloqueo |
| Restricciones de venta | El tutor inicial no puede vender LUZ obtenida a través de ningún canal (incluidos lanzamientos aéreos, recompensas y compensaciones) durante el mandato (≤24 meses) |
| Conflicto de intereses | Los conflictos de intereses de los miembros del equipo deben revelarse completamente en el momento del nombramiento (si poseen otros tokens DAO, si están relacionados con posibles objetivos de inversión) |
| Consecuencias de la falta de divulgación | Una vez que se verifique que no se ha revelado un conflicto de intereses, se le prohibirá permanentemente participar en la gobernanza y el 50% de los tokens desbloqueados serán confiscados al fondo de seguro |
| Mecanismo de sustitución | Cuando un rol central abandona o queda incapacitado, el comité de gobierno (tutor inicial + tutor alternativo antes del establecimiento) designará un sucesor, que deberá ser anunciado públicamente por la comunidad durante 72 horas sin objeciones |

### 12.4 Compensación de los contribuyentes principales (20 % del fondo operativo estratégico)

- Monto total: 50 millones de LIGHTs (que representan el 2% del monto total)
- Número de personas cubiertas: 3-5 personas
- Reglas de lanzamiento: Acantilado de diciembre + 36 meses lineales (es decir, se lanzarán aproximadamente 1,157 millones de monedas cada mes a partir del mes 13)
- Vinculación de hitos: cada trimestre, el comité de gobierno (guardián inicial + tercero independiente antes del establecimiento) confirma que se alcanza el hito antes de que se pueda liberar la cuota trimestral.
- Reglas de divulgación: solo se divulgan el monto total y las reglas de liberación, y no se divulgan los nombres personales ni las cuotas de una sola persona (para proteger la privacidad y, al mismo tiempo, el monto total se puede verificar a través de la dirección de firma múltiple en la cadena para que no se exceda el monto total)

---

## Capítulo 13: Advertencia de riesgo y descargo de responsabilidad

### 13.1 Advertencia de riesgo

| Tipo de riesgo | Descripción | Medidas de mitigación |
|---------|------|---------|
| Riesgo de Mercado | Los precios de LIGHT pueden fluctuar significativamente y los precios históricos no representan el desempeño futuro. TGE tiene liquidez inicial limitada y los precios pueden fluctuar violentamente | Precios justos en subasta holandesa; ±50% de disyuntores 72 horas después de TGE; mecanismo de intervención de cuatro niveles en espiral contra la muerte |
| Riesgo del proyecto | El objetivo de la inversión puede sufrir pérdidas, el proyecto de capital de riesgo puede fracasar y perder todo el capital. La tasa de fracaso promedio histórica de la industria de PE/VC es de alrededor del 50-70% (acuerdo único) | Descentralización de doble motor (70% de flujo de caja + 30% de crecimiento); objetivo único ≤ 25%; industria ≤ 40%; región ≤ 30%; Provisión del 10% para fondos de seguros |
| Riesgos técnicos | Los contratos inteligentes pueden tener vulnerabilidades no descubiertas; la compatibilidad del navegador puede afectar la experiencia minera; puentes entre cadenas pueden ser atacados | Auditoría independiente + verificación formal ante TGE; Recompensa por errores entre 1.000 y 50.000 dólares; bloqueo de tiempo de 72 horas; mecanismo de suspensión multifirma |
| Riesgos regulatorios | Las políticas regulatorias en varios países y regiones pueden cambiar, lo que puede resultar en funciones limitadas o incapacidad para que los usuarios de regiones específicas participen | Estructura Caimán SPV; verificación cero predeterminada (la verificación la realiza un tercero autorizado en su lado de servicio); el espejo IPFS frontal es resistente a la censura; no comercializado en países específicos |
| Riesgo de liquidez | Es posible que el subtoken carezca de profundidad comercial suficiente en la etapa inicial; LIGHT puede enfrentar presión de venta en la etapa inicial de TGE | La liquidez inicial del subtoken AMM (6% de la emisión); período de bloqueo de transferencia de 30 días; Equipo/inversor Acantilado de 12 meses + lineal de 36 meses |
| Riesgo de dilución | A medida que aumenta el número de mineros activos, los ingresos mineros per cápita naturalmente se diluirán (aumenta el denominador BaseReward) | Intención del diseño: los primeros participantes asumen mayores riesgos para obtener mayores rendimientos; los usuarios posteriores pueden acelerar la acumulación compartiendo invitaciones; el umbral de gobernanza se reduce dinámicamente |
| Riesgo operacional | Es posible que el funcionamiento y gestión de la empresa invertida no cumpla con las expectativas; Las operaciones de SPV dependen de directores externos; el equipo inversor puede perderse | Restricciones de estatutos de SPV + directores independientes; DAO puede votar para reemplazar a los directores; cláusulas de arbitraje SIAC/ICC; seguro para personas clave (en exploración) |
| Riesgos del puente entre cadenas | El puente entre cadenas wLIGHT es operado por un tercero, y las lagunas jurídicas del contrato del puente pueden provocar pérdidas de activos (en la historia, los puentes entre cadenas son la mayor fuente de pérdidas) | Auditoría independiente antes de que el puente entre en funcionamiento; los activos puente no superan el 5% de la oferta total; divulgación de riesgos; los usuarios pueden optar por utilizar sólo la cadena nativa |
| Riesgo del validador | Los validadores que se desconectan colectivamente o cometen maldades pueden hacer que la cadena suspenda la producción de bloques y todas las operaciones de los usuarios (minería, votación, transferencias) no estén disponibles temporalmente | Tendermint BFT tolera <1/3 del mal; validadores ≥ 21 (f=6); Pena cortante; mecanismo de votación de migración de emergencia |

### 13.2 Descargo de responsabilidad

- LIGHT y los subtokens no son valores, no tienen valor intrínseco y el precio puede volver a cero. Este documento técnico no constituye ningún tipo de documento de emisión de valores, oferta de inversión o asesoramiento de inversión.
- La distribución de ingresos del acuerdo depende del desempeño operativo real de los activos subyacentes, y los datos históricos no representan ingresos futuros. Cualquier descripción de los rendimientos de las inversiones son estimaciones prospectivas y no promesas.
- El usuario debe asumir todas las pérdidas causadas por la pérdida o filtración de la clave privada, y el acuerdo no proporciona servicios de recuperación. El uso de una billetera de Nivel 1 (Clave de acceso) o Nivel 2 (Recuperación social) reduce este riesgo, pero no lo elimina.
- Este acuerdo está abierto a usuarios de todo el mundo (sujeto a las leyes y regulaciones aplicables). Los usuarios deben confirmar la actitud legal hacia los activos cifrados, las organizaciones DAO y los certificados de ingresos SPV en sus jurisdicciones, y asegurarse de que su participación sea legal y conforme.
- Las declaraciones prospectivas contenidas en este documento técnico (incluidas hojas de ruta, modelos de ingresos, estimaciones de deflación, pronósticos de escala de inversión) son predicciones basadas en suposiciones actuales, y los resultados reales pueden desviarse significativamente debido al mercado, la tecnología, la regulación, la ejecución del equipo y otros factores.
- Los incentivos por invitación son un mecanismo de reparto de un solo nivel y no constituyen marketing multinivel ni esquemas piramidales. Sin embargo, los usuarios aún deben confirmar la actitud legal hacia las recompensas por referencias en su jurisdicción.
- La edad mínima para participar en el ecosistema LightDAO es 18 años (o la mayoría de edad legal en tu jurisdicción, la que sea mayor). A los menores no se les permite participar en minería, gobernanza o inversiones.

---

## Apéndice A: Tabla resumen de parámetros clave

| Categoría | Parámetro | Valor |
|------|------|------|
| Emisión | Importe total | 2.500 millones de unidades, nunca más emisiones |
| Emisión | Minería | 40% = mil millones de monedas |
| Emisión | Bóveda de Inversión | 34% = 850 millones de monedas |
| Emisión | Fondo Ecológico | 16% = 400 millones de piezas |
| Emisión | Operaciones Estratégicas | 10% = 250 millones de monedas (servicio 50%/financiación 30%/contribuyentes 20%) |
| Emisión | Ciclo de reducción a la mitad | Cada 2 años |
| Emisión | Lanzamiento del día de la primera era | ≈684.900 (mineros 95% = 650.700, validadores 5% = 34.200) |
| Emisión | Fondo de recompensas por bloque | ≈13,87 LUZ |
| Minería | Peso de la contribución | Ancho de banda 40%/sesión 30%/verificación 20%/estabilidad 10% |
| Minería | Bonificación completa | 1,44 veces |
| Invitación | Evangelista/Embajador/Socio | 3 personas 10%+100L/10 personas 15%+500L+5%/50 personas 20%+2500L+10% |
| Comportamiento | Cuatro artículos × 5% | Límite superior 20% |
| Tarifa de gas | Mecanismo de fijación de precios | Anclaje equivalente a USD, convertido automáticamente en cantidad de LUZ por el oráculo cada 24 horas |
| Tarifa de gas | Transferencia ordinaria | $0.001 equivalente (@$0.05=0.02 LUZ) |
| Tarifa de gas | Votación de gobernanza | $0.005 equivalente (@$0.05=0.10 LUZ) |
| Tarifa de gas | Reglas de distribución | 50% destrucción / 30% validadores / 20% tesoro ecológico |
| Deflación | Desaceleración/alerta temprana/resultado final | ≤1,5 mil millones/≤1,2 mil millones/≤1 mil millones (volumen de circulación) |
| Deflación | Límite superior teórico | 1,65 mil millones (10+4+2,5, 850 millones del tesoro nunca circularán) |
| Gobernanza | Umbral de propuesta | ≥5.000 LUZ + 30 días de stake |
| Gobernanza | Estaca del comité | 50.000 LUZ + 100 Direcciones |
| GOBERNANZA | JURADO | 10.000 LUZ |
| Gobernanza | Apuestas | 5—500 LUZ |
| Gobernanza | Bonificación de reputación | 1 año +15 votos → +30% (límite total +40%) |
| Inversión | Límite único | Bóveda restante × 15% (inicial 127,5 millones de monedas) |
| Inversión | Línea de base desplegable | 850 millones × $0,15 × 75% = $95,63 millones ≈ $100 millones |
| Inversión | Distribución de beneficios (anual) | 40/30/20/10 |
| Inversión | Distribución de beneficios (salida) | 70/30 |
| Subasta | Objetivo | 15 millones de dólares (reserva de 5 millones de dólares + capital invertido de 10 millones de dólares) |
| Reservas | Tesorería estable | TGE $5 millones → Mes 24 $8 millones |
| Seguros | Beneficio | Beneficio 10% |
| Lanzamiento aéreo | Presupuesto total | 55 millones (fondo ecológico 13,75%), CAC≈$55/usuario retenido |
| Validadores | Inicial/Cap | 21 (mínimo 10) / 100 |
| Validador | Apuesta mínima | 500.000 LUZ |
| Verificador | Resultado final duro de TGE | ≥7, de lo contrario no se permitirá conectarse |

---

## Apéndice B: Derivación y verificación numérica

### B.1 Producción minera

2A=1 mil millones→A=500 millones. Liberación diaria = 500 millones ÷ 730 = 684,932 ≈ 684,900. Fondo minero=684,932×95%=650,685≈650,700. Verificadores=684,932×5%=34,247≈34,200. Cada bloque=684.932÷49.371≈13,87. Verificación: 684.932×730=499.999.960≈500 millones ✓

### B.2 Accesibilidad del umbral de gobernanza

Punto de referencia de 100.000 mineros (6,51/día, socio 74,44/día): propuesta 5.000→768 días/67 días; comité 50.000→7.684 días (21 años)/672 días (22 meses); jurado 10.000→1.537 días (4,2 años)/134 días (4,5 meses); apuesta 500→77 días/6,7 días.

Período semilla (10.000 mineros, 65,07/día, socios 744,4/día): propuesta → 77 días (2,5 meses) / 6,7 días; comité → 768 días (25 meses) / 67 días (2,2 meses); jurado → 154 días (5 meses) / 13,4 días.

### B.3 Cronología de la deflación

Volumen de circulación = minería + ecología + estrategia (adquirida) − intercambio − Gas − recompra. 850 millones del tesoro nunca se pondrán en circulación.

| Año | Minería acumulativa | Ecología | Estrategia | Intercambio | Gas | Recompra | Circulación |
|----|---------|------|------|------|-----|------|--------|
| 1 | 2,50 | 2,80 | 0 | 0 | 0,01 | 0 | ≈5,29 |
| 2 | 5.00 | 4.00 | 0,83 | 0,05 | 0,02 | 0 | ≈9,76 |
| 3 | 6.25 | 4.00 | 1,67 | 0,20 | 0,03 | 0,05 | ≈11,64 |
| 4 | 7,50 | 4.00 | 2,50 | 0,45 | 0,04 | 0,20 | ≈13,31(pico) |
| 5 | 8.13 | 4.00 | 2,50 | 0,80 | 0,05 | 0,50 | ≈13,28 |
| 6 | 8,75 | 4.00 | 2,50 | 1.20 | 0,06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 4.00 | 2,50 | 1,60 | 0,07 | 1,40 | ≈12,49 |
| 8 | 9.38 | 4.00 | 2,50 | 2.00 | 0,08 | 1,90 | ≈11,89 |
| 9 | 9,53 | 4.00 | 2,50 | 2,40 | 0,09 | 2.30 | ≈11,24 |
| 10 | 9,69 | 4.00 | 2,50 | 2,80 | 0,10 | 2,70 | ≈10,59 |
| 11 | 9,77 | 4.00 | 2,50 | 3.10 | 0,11 | 3.00 | ≈10.06 |
| 12 | 9,84 | 4.00 | 2,50 | 3.40 | 0,12 | 3.30 | ≈9,52 |

Conclusión: El pico Y4≈1.331 mil millones; Y8 toca la línea de advertencia de 1.200 millones; el resultado final de 1.000 millones se alcanza en los años 11-12; la línea de desaceleración de 1.500 millones es sólo un escenario de destrucción extremadamente baja.

---

## Apéndice C: Registro de correcciones de auditoría (36 elementos en total)

Contiene 22 elementos originales (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 elementos de arquitectura técnica (T1-7) + 7 elementos de optimización del modelo económico en esta ronda:

| Número | Corrección |
|------|------|
| E-1 | Importe total 2.100 millones → 2.500 millones (impulsado por limitaciones de la capacidad de inversión) |
| E-2 | Asignación 50/30/20→40/34/16/10 (10 % de los nuevos fondos operativos estratégicos) |
| E-3 | Subasta holandesa $10 millones→$15 millones (capital de inversión inicial $5 millones→$10 millones) |
| E-4 | Nuevo plan de crecimiento de lanzamiento aéreo de 5,7 secciones (55 millones de piezas, 55 dólares CAC por persona) |
| E-5 | Los verificadores se lanzan por etapas (Testnet 7→TGE mínimo 10/Target 21→Open 100) |
| E-6 | Ajuste de la línea de activación de deflación (14/12/10 → 15/12/10, adaptado al límite de circulación de 1.650 millones) |
| E-7 | Reemplace todas las citas externas con fuentes verificables (elimine los artículos SSRN no verificables) |

---

## Apéndice D: Índice rápido de términos

Se incluye una explicación completa de cada término en el bloque de comentarios [Términos de este capítulo] al final del capítulo donde aparece por primera vez. Este índice enumera todos los términos y sus capítulos en orden alfabético para una navegación rápida.

| Terminología | Capítulo de definición |
|------|------------|
| AMM (Creador de mercado automatizado) | Capítulo 4 |
| BFT (tolerancia a fallas bizantinas) | Capítulo 4 |
| CAC (Costo de Adquisición de Clientes) | Capítulo 5 |
| CEX (Intercambio Centralizado) | Capítulo 4 |
| SDK de Cosmos | Capítulo 4 |
| CosmoWasm | Capítulo 4 |
| DAO (Organización Autónoma Descentralizada) | Capítulo 2 |
| DCF (Método de flujo de caja descontado) | Capítulo 9 |
| DePIN (Red de infraestructura física descentralizada) | Capítulo 2 |
| DEX (Intercambio Descentralizado) | Capítulo 4 |
| EBITDA (beneficios antes de intereses, impuestos, depreciación y amortización) | Capítulo 9 |
| Tarifa de gas | Capítulo 4 |
| IBC (Protocolo de comunicación entre cadenas) | Capítulo 3 |
| IPFS (Sistema de archivos interplanetario) | Capítulo 4 |
| KYC (Conozca a su cliente) | Capítulo 3 |
| LUZ (token nativo) | Capítulo 4 |
| LP (Proveedor de Liquidez) | Capítulo 5 |
| PE del mercado medio inferior (capital privado del mercado medio downstream) | Capítulo 2 |
| Árbol Merkle | Capítulo 4 |
| MiFID II (Directiva de la UE sobre mercados de instrumentos financieros II) | Capítulo 3 |
| MLM (Marketing multinivel) | Capítulo 3 |
| PII (Información de identificación personal) | Capítulo 3 |
| PoC (Prueba de Contribución) | Capítulo 4 |
| PoS (Prueba de participación) | Capítulo 4 |
| PoW (Prueba de trabajo) | Capítulo 4 |
| Pre-IPO | Capítulo 9 |
| PWA (Aplicación Web Progresiva) | Capítulo 4 |
| Reg D / Reg S (Reglamento D/S de la Ley de Valores de EE. UU.) | Capítulo 3 |
| Cortando | Capítulo 4 |
| SPV (Vehículo de Propósito Especial) | Capítulo 2 |
| TGE (Evento de Generación de Tokens) | Capítulo 5 |
| TWAP (Precio promedio ponderado en el tiempo) | Capítulo 4 |
| Ejecución TWAP (Órdenes de Recompra y División) | Capítulo 9 |
| VWAP (Precio promedio ponderado por volumen) | Capítulo 5 |
| wLIGHT (LUZ encapsulada) | Capítulo 5 |
| ZK-KYC (KYC a prueba de conocimiento cero) | Capítulo 3 |
| Subtoken | Capítulo 5 |
| Espiral de la muerte | Capítulo 5 |
| Reducir a la mitad | Capítulo 5 |
| Hacienda (Tesorería) | Capítulo 5 |
| Subasta holandesa | Capítulo 5 |
| Oráculo | Capítulo 4 |

---

**Fin del documento técnico completo**

**Declaración de derechos de autor:** Este documento es un documento comunitario de código abierto y se puede reproducir libremente, pero se debe conservar el contenido completo.

---

# Apéndice: direcciones y parámetros verificados de Mainnet (V2.4 en vivo)

## A. §4.5 Parámetros medidos económicos del gas
- fórmula de precio mínimo del gas: `(TransferUsdTarget / UsdPerLight) × 10^6 / RefTransferGas`; Transferencia actualUsdTarget=$0,001, UsdPerLight=$0,05, RefTransferGas=100000 → **0,2 ulight/gas**
- Medición de distribución (tarifa total 300000 ulight): destrucción 150000 (50%)/tesorería 60000(20%)/verificador 90000(30%), coincidencia exacta
- Dirección de destrucción: `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (dirección muerta determinista)
- Tesorería: contrato `treasury_multisig` (3/5 multifirma; la consulta `firmantes` en la cadena devuelve 5 firmantes, el umbral en sí no está en la interfaz de consulta)

## B. Dirección del contrato principal
Ver repositorio `docs/MAINNET_STATUS.md` (light_token/mining_reward/gobernanza/treasury_multisig/oracle_twap/vesting y otros 10 contratos).

## C. Eliminación de denominaciones (participaciones) heredadas
La falta de coincidencia de génesis mint_denom=stake se restableció a cero y se detuvo la emisión adicional; la participación existente (aproximadamente 2,56e11 microunidades) queda sin propósito, y el plan de eliminación (intercambio/destrucción) está pendiente de propuestas de gobernanza y no afectará el modelo económico ligero.

## D. §4.4 adquisición de derechos en vivo
Bóveda 250.000.000 LUZ, 3 horarios independientes: 75M (cliff 0)/ 100M (cliff 1 año)/ 75M (cliff 2 años), ya en cadena.

## E. Prácticas de seguridad
- La red principal se actualiza a x/gobierno de actualización + alta coordinación de todos los nodos en el mismo bloque + vigilancia de intercambio automático, ejecutado después del ensayo de extremo a extremo de la red de prueba
- Las semillas de clave de acceso sólo almacenan texto cifrado; Los fragmentos de Shamir no los almacenas localmente.
- Umbral de envío de raíz de minería de contrato 5 (umbral de medición real = 5 para cada evento `submit_root` en la cadena; actualmente hay 5 cuentas autorizadas firmando y 7 puestos son el objetivo de diseño); para anti-brujas/anti-trampas, ver §4.8
