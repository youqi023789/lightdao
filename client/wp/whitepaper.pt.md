> Tradução automática sem revisão humana. Em caso de divergência, prevalece a versão original em chinês.
[中文原文 / Chinese original](/whitepaper.md)

# LightDAO White Paper V2.4 (2026-09-26 Mainnet Live Version)

> Esta versão é baseada no rascunho de design V2.0, com "implantação da rede principal ao vivo" e "alterações de versão" na frente, e anexada com parâmetros verificados na cadeia. O texto principal (Capítulo 1 a 12) permanece inalterado em relação ao design da V2.0; para quaisquer desvios da situação real, prevalecerão as notas anteriores e anexos desta seção.

## Mudanças de versão (V2.0 → V2.4)
- 2026-11-04 Errata (não altere o número da versão, ainda V2.4): O cofre original `treasury_multisig` no apêndice "Parâmetros e endereços verificados da Mainnet" é 5/7 multisig, o que entra em conflito com 3/5 do texto §7.2/§7.3/§8.1 e também entra em conflito com a medição real na cadeia (`{"signers":{}}` retorna 5 endereços, não há 7 assinantes); foi unificado como 3/5 de acordo com o texto e é indicado que o limite em si não está na interface de consulta do contrato e só pode ser suportado por registros de implantação. A raiz de mineração original escrita na mesma seção é "5/7 verificador multi-assinatura", e o teste real só pode provar o limite de 5 (o limite de 115 eventos `submit_root` é todos 5, e o número real de assinaturas de contas é exatamente 5). A autorização de 7 lugares é o objetivo do projeto e atualmente não há evidências na cadeia. A redação foi alterada em conformidade.

1. **§4.5 Economia de Gás: Implantado e verificado na rede principal**. O preço mínimo do gás dinâmico ancorado em dólares e 50% de destruição / 30% de validadores / 20% de alocação de tesouraria foram implementados em 2026/09/24 após a proposta de governança (v2-lightfee) ter sido lançada na altura 58627, 7 validadores coordenaram a comutação e a rede de teste foi ensaiada de ponta a ponta. Medição real na rede principal: as taxas insuficientes são rejeitadas e as taxas completas são alocadas com precisão de acordo com 50/30/20.
2. **Esclarecimento sobre a denominação nativa**: Estacamento/governança/Gás são todos `ulight` (LIGHT, 6 casas decimais, fornecimento total de 2,5 bilhões). A inflação `aposta` incompatível com a génese foi reposta a zero (inflação da casa da moeda = 0) pela proposta de governação de 2026-09-24. A emissão de LIGHT é integralmente suportada pelo contrato mining_reward, eliminando a dupla emissão; a participação existente é a denominação herdada a ser alienada (ver Apêndice C).
3. **§4.7 Retransmissão WebRTC: Implantado**. 8 nós coturn (TURN/STUN, certificado TLS turn-*.lightdao.net) + sinalização WSS + certificado temporário REST (HMAC-SHA1); os canais de dados P2P do cliente são retransmitidos mutuamente e os bytes de retransmissão são contados como contribuição de 40% da largura de banda; a medição real ponta a ponta é bem-sucedida por meio da transmissão do relé TURN. O NAT simétrico usa TURN e não faz downgrade para o modo de autenticação pura (consistente com §4.7).
4. **§4.9 Carteira Inteligente: On-line**. Login sem sementes Passkey/WebAuthn (chave derivada de PRF + armazenamento de texto cifrado AES-GCM, texto simples não cai no chão) + recuperação social Shamir 3 de 5; a frase mnemônica é mantida como uma opção alternativa.
5. **§4.10 Price Oracle: O feed de preços foi executado**. 7 O cron do verificador se reveza para enviar external_median para oracle_twap (preço de referência atual 50.000 = US$ 0,05); O TWAP na cadeia será ativado após o estabelecimento do pool de liquidez LIGHT/USDC. Após a atualização v3, lightfee lê diretamente external_median e converte min-gas dinâmico.
6. **Governança de parâmetros**: A atualização v3 moverá BurnPct/TreasuryPct/TransferUsd/StaticPrice/OracleContract da lightfee para o paramstore on-chain. As propostas de parâmetros de governança podem ser ajustadas em tempo de execução, eliminando a necessidade de coordenar atualizações.

## Implantação da Mainnet ativa (26/09/2026)

- Cadeia `lightdao-mainnet-1`, 7 validadores (JP/KR/SG/US/HK/FR/UK) estão todos BONDED, nenhum preso; atender ao resultado final de §4.7 "Verificadores <7 não têm permissão para TGE"
- Cliente https://lightdao.net (PWA): Carteira de senha + mineração + retransmissão WebRTC + coleção, multilíngue (chinês/inglês/espanhol)
- Loop fechado de mineração: Contribuição do navegador → Finalização diária do gateway → Merkle root 5 é assinado na cadeia (limiar 5, pode ser verificado na cadeia) → Os mineradores recebem prova com prova; raiz diária é enviada continuamente
- Gerenciamento de atualização: v2-lightfee (aplicado em 58627), mint zeroing (aplicado), v3-lightfee (aprovado por unanimidade, altura 118055 muda automaticamente)
- Para obter o histórico completo de endpoint/endereço do contrato/atualização, consulte o warehouse `docs/MAINNET_STATUS.md`

---

# LightDAO 白皮书 V2.0

**Verificação de texto completo e versão otimizada para revisão (cliente web internacional · auditoria numérica · auditoria de terceiros · versão otimizada para modelo econômico) **

Data de lançamento: 4 de agosto de 2026

Princípio fundamental: os navegadores são nós, todos podem participar e os lucros são compartilhados de acordo com as regras

Posicionamento legal: LIGHT e sub-tokens são posicionados como pontos de contribuição ecológica e certificados de direitos de reivindicação de distribuição de renda SPV, e não são títulos ou produtos financeiros; atributos legais específicos estão sujeitos a pareceres jurídicos válidos nas jurisdições relevantes.

> Este documento é uma versão verificada e otimizada do texto completo do white paper e não constitui aconselhamento de investimento, documentos de emissão de títulos, descrições de produtos financeiros ou qualquer forma de compromisso de garantia de capital. Consulte profissionais jurídicos, fiscais e financeiros antes de participar.

---

## Índice

- Pré-declaração
- Prólogo: A história de três pessoas
- Capítulo 1: A verdade que vemos
- Capítulo 2: Resposta do LightDAO
- Capítulo 3: Conformidade e isolamento legal
- Capítulo 4: Arquitetura Técnica
- Capítulo 5: Modelo Econômico Token
- Capítulo 6: Mecanismo de Governança
- Capítulo 7: Verificações e equilíbrios de poder e definição de funções
- Capítulo 8: Mecanismo de Confiança e Segurança
- Capítulo 9: Operações de investimento e estratégias de saída
- Capítulo 10: Roteiro
- Capítulo 11: Cultura comunitária e ecologia do desenvolvedor
- Capítulo 12: Equipe e Consultores
- Capítulo 13: Aviso de Risco e Isenção de Responsabilidade
- Apêndice A: Tabela resumida dos principais parâmetros
- Apêndice B: Derivação numérica e verificação
- Apêndice C: Registro de correção de auditoria
- Apêndice D: Índice de referência rápida de termos

---

## Sumário executivo

**O que é LightDAO:** Uma organização autônoma descentralizada que permite que pessoas comuns em todo o mundo participem de investimentos empresariais reais e compartilhem lucros por meio de um navegador. Os usuários não precisam comprar uma máquina de mineração, ter formação técnica ou atingir o limite de investidores qualificados - com apenas um navegador e um pouco de tempo, os usuários podem contribuir com recursos de rede para receber recompensas de tokens LIGHT e participar de decisões de investimento por meio de votação de governança.

**Que problema foi resolvido:** Os 50% mais pobres da população global (aproximadamente 4 mil milhões de pessoas) possuem apenas 2% da riqueza total (World Inequality Lab, 2026). Ativos de alta qualidade (private equity, capital de risco) são excluídos pelo limite do investidor qualificado (renda anual de US$ 200.000/patrimônio líquido de US$ 1 milhão). Embora exista uma narrativa de “participação universal” no campo das criptomoedas, a grande maioria dos tokens eventualmente retorna a zero (CoinGecko 2025: 11,56 milhões de tokens morreram), e a taxa de participação na governança do DAO é de apenas cerca de 3-12%.

**Como resolver:** Modelo de motor duplo - 70% dos recursos são investidos em ativos de consumo rígidos de nível comunitário (motor de fluxo de caixa) e 30% são investidos em tecnologia de ponta (motor de crescimento). Os investimentos são executados através do Cayman SPV e os lucros são distribuídos de acordo com as regras da rede: 40% para detentores de subtokens, 30% de volta ao cofre para reinvestimento, 20% recompra LIGHT para destruição e 10% acumulados para fundos de seguros.

**Dados principais:**

| Indicadores | Valores |
|------|------|
| Quantidade total de LUZ | 2,5 mil milhões, nunca serão emitidos |
| Cofre de Investimento | 850 milhões (linha de base implantável ≈ US$ 100 milhões) |
| Produção mineira | 1 bilhão, reduzido pela metade a cada 2 anos |
| Lançado no Dia da Primeira Era | ≈684.900 peças (média 6,51/dia quando 100.000 mineiros trabalham) |
| Resultados da deflação | Cessar definitivamente a queima quando a circulação for ≤ mil milhões (anos 11-12 do cenário base) |
| Limiar de Governança | Proposta ≥ 5.000 LIGHT; Comitê ≥ 50.000 LUZ |
| Pilha de tecnologia | Cosmos SDK + Tendermint PoS + CosmWasm + PWA |
| Verificadores | Inicial 21 (mínimo 10), limite superior 100 |
| Financiamento inicial | Leilão holandês US$ 15 milhões + Financiamento estratégico pré-TGE US$ 2,25-3,75 milhões |

**Diferenciação:** Atualmente o único projeto que combina "mineração web de limite zero" com "investimento em entidade SPV compatível". Diferente da Pi Network (sem utilidade prática), Helium (requer hardware de mais de US$ 200) e DAO tradicional (governança de elite de alto limite).

**Roteiro:** Preparação para o 4º trimestre de 2026 → Desenvolvimento do 1º ao 2º trimestre de 2027 → Teste de auditoria do 3º trimestre → TGE on-line do 4º trimestre → Usuários iniciais do 1º trimestre de 2028 → Primeiro investimento do 2º ao 3º trimestre → Escala do 4º trimestre em diante.

---

## Pré-declaração

**Esta não é uma proposta de investimento**

As “recompensas ecológicas” e a “distribuição de renda do acordo” descritas neste white paper são acordos de incentivo gerados pelo mecanismo endógeno do acordo e não constituem qualquer forma de emissão de títulos, vendas de produtos financeiros, compromissos de garantia de capital ou consultoria de investimento.

LIGHT e subtokens não têm valor intrínseco e o preço pode voltar a zero. Antes de participar, consulte seus próprios profissionais jurídicos, fiscais e financeiros e assuma total responsabilidade pela custódia da chave privada, declaração fiscal e participação.

---

## Prólogo: A história de três pessoas

Maria trabalha como entregadora de comida em Manila, trabalhando 12 horas por dia e ganhando cerca de 15.000 pesos filipinos (aproximadamente US$ 270) por mês. Ela queria investir na popular rede de chá com leite ao lado, mas a outra parte lhe disse: “O investimento mínimo começa em US$ 25 mil”. Maria não conseguiu arranjar 25 mil dólares.

Kwame dirige um serviço de carona em Lagos. Ele está otimista quanto ao caminho da inteligência artificial e quer investir em uma pequena empresa de tecnologia financeira. A instituição disse a ele: “O valor mínimo da assinatura é de US$ 100 mil e o período de fidelização é de 5 anos”. Kwame não conseguiu arranjar 100 mil dólares.

Elena é uma professora aposentada em São Paulo com uma pensão mensal de aproximadamente 3.000 reais (aproximadamente US$ 550). Ela ouviu dizer que os filhos de seu vizinho estavam ganhando dinheiro trabalhando em empresas de blockchain, mas ela não conseguia ler o white paper e não sabia como comprar e configurar equipamentos profissionais de mineração.

Os três representam a grande maioria das pessoas comuns em todo o mundo: têm o discernimento e a vontade de participar, mas carecem de canais de participação de baixo limiar, transparentes e acessíveis.

LightDAO foi projetado para essas pessoas. Com um dispositivo com acesso à Internet, um navegador e uma pequena quantia em dinheiro, você pode participar da construção ecológica; por meio de uma estrutura SPV compatível, os usuários também têm a oportunidade de acessar indiretamente a distribuição de fluxo de caixa de empresas de alta qualidade e o crescimento inicial de projetos de tecnologia de ponta.

---

## Capítulo 1: A verdade que vemos

### 1.1 Distribuição desequilibrada da riqueza global

De acordo com o Relatório Mundial sobre Desigualdade 2026 (doravante denominado “Relatório”) do World Inequality Lab:

| Dados | Fonte |
|------|------|
| A riqueza pertencente aos 0,001% mais ricos da população mundial (cerca de 60.000 pessoas) é cerca de três vezes a riqueza combinada dos 50% mais pobres da população (cerca de 4 mil milhões de pessoas) | Laboratório Mundial de Desigualdade, 2026 |
| O 1% mais rico da população mundial controla 23% da renda total e 38% da riqueza total | Laboratório Mundial de Desigualdade, 2026 |
| Os 10% mais ricos da população mundial controlam 53% do rendimento total e 75% da riqueza total | Laboratório Mundial de Desigualdade, 2026 |
| Os 50% mais pobres da população global recebem apenas 8% do rendimento total e 2% da riqueza total | Laboratório Mundial de Desigualdade, 2026 |

O “Relatório” salienta: “A desigualdade global permanece em níveis historicamente extremos. A desigualdade não surge apenas do funcionamento natural do mercado, mas reflecte escolhas políticas, estruturas institucionais e a distribuição desigual do poder económico e político”.

**Nota da fonte:** Os dados acima são citados do Relatório Mundial de Desigualdade 2026 do World Inequality Lab. O relatório foi liderado por Lucas Chancel, Ricardo Gómez-Carrera, Rowaida Moshrif e Thomas Piketty (confirmado pelo site oficial wid.world). Antes do lançamento oficial, recomenda-se marcar ainda mais os números específicos do gráfico no relatório para reduzir possíveis erros na tradução secundária.

**Verificação da consistência dos dados:** As proporções acima continuam numa tendência razoável com a conclusão do Relatório Mundial sobre Desigualdade de 2022 (os 10% mais ricos possuem 76% da riqueza total, os 50% mais pobres possuem 2% da riqueza total), e o desvio está dentro do intervalo estatisticamente aceitável.

### 1.2 Pessoas comuns são excluídas de ativos de alta qualidade

As principais jurisdições globais têm limites rigorosos de investidores qualificados para capital privado e capital de risco:

**Estados Unidos (Regulamento SEC D, Regra 501, 17 CFR §230.501):** Os investidores qualificados (Investidores Credenciados) devem atender a uma das seguintes condições - a renda anual de um indivíduo não é inferior a US$ 200.000 (ou um total não inferior a US$ 300.000 com um cônjuge) e ter atendido ao padrão por dois anos consecutivos; ou o patrimônio líquido (excluindo residência principal) não seja inferior a US$ 1.000.000.

**UE (MiFID II, 2014/65/UE, Anexo II):** Os investidores profissionais (Investidores Profissionais) devem cumprir pelo menos duas das seguintes condições - uma carteira de investimento em instrumentos financeiros não inferior a 500.000 euros; ocupar um cargo profissional no setor financeiro há pelo menos um ano; executando transações em grande escala não inferiores a 10 por trimestre.

**Prática Global de Fundos de Private Equity:** O valor mínimo de subscrição para um único fundo geralmente fica entre US$ 250.000 e US$ 1.000.000; as regras regulatórias geralmente proíbem comportamentos evasivos, como “dividir ações, reduzir limites e manter ordens em nome de terceiros”.

| Tipos de ativos | Pessoas comuns podem participar | Principais motivos |
|----------|---------------|----------|
| Participações em empresas não cotadas de alta qualidade | Geralmente não pode | O limite para investidores qualificados é mais elevado, por exemplo, os Estados Unidos exigem um património líquido não inferior a 1 milhão de dólares ou um rendimento anual não inferior a 200.000 dólares |
| Capital de risco (empresas tecnológicas em fase inicial) | Geralmente não | Aberto principalmente a investidores qualificados, o valor do investimento de um único fundo geralmente não é inferior a US$ 250.000 |
| Ações de empresas cotadas | Sim, mas os lucros iniciais foram geralmente capturados pelos participantes no mercado primário | A precificação do mercado secundário geralmente inclui expectativas futuras e os investidores não participam diretamente na distribuição antecipada de lucros da empresa |

### 1.3 Três grandes falhas no campo das criptomoedas

**Falha 1: Taxa de falha extremamente alta**

De acordo com o relatório estatístico anual de 2025 da CoinGecko, aproximadamente **11,56 milhões de tokens** retornarão a zero ou pararão de ser negociados somente em 2025 (incluindo tokens de cauda longa em cada cadeia). Dos mais de 20 milhões de tokens que a CoinGecko rastreou historicamente, a grande maioria está em um estado “morto” (sem volume de negociação, sem atividade de desenvolvimento e os preços caíram mais de 99% em relação aos máximos históricos).

Ao mesmo tempo, a taxa de insucesso dos mercados de ações tradicionais é muito inferior à das criptomoedas. De acordo com o artigo de Bessembinder (2018) "Do Stocks Outperform Treasury Bills?" publicado no "Journal of Financial Economics", um estudo de todas as ações dos EUA de 1926 a 2016:

| Métricas | Dados | Fontes |
|------|------|------|
| Proporção de ações que criam riqueza líquida total | Apenas cerca de 4% (1.092 ações) | Bessembinder (2018), JFE 129(3):440-475 |
| Retorno vitalício mediano das ações | Negativo (desempenho inferior aos títulos do Tesouro) | Bessembinder (2018), JFE |
| Cerca de 58% do desempenho vitalício das ações dos EUA | Títulos do Tesouro com baixo desempenho no mesmo período | Bessembinder (2018), JFE |
| Número de tokens a serem redefinidos para zero/interrupção da negociação em 2025 | ≈11,56 milhões | Relatório Anual CoinGecko 2025 |

**Conclusão Comparativa:** A taxa de perda permanente de capital no espaço das criptomoedas é muito maior do que no mercado de ações tradicional. Embora cerca de 58% das ações individuais no mercado de ações dos EUA tenham um desempenho inferior ao das obrigações do Tesouro, os investidores ainda podem obter retornos médios de mercado através de fundos de índice; no mercado de criptomoedas, a grande maioria dos tokens acaba voltando a zero e faltam ferramentas eficazes de diversificação semelhantes aos “índices”.

**Declaração da fonte:** Bessembinder, H. (2018). "As ações superam as letras do tesouro?" *Jornal de Economia Financeira*, 129(3), 440-475. Universidade Estadual do Arizona. Este artigo é um documento altamente citado na área de finanças (citações> 2.000), e os dados cobrem todas as ações dos EUA no banco de dados CRSP de 1926 a 2016. Os dados da CoinGecko vêm de seu Relatório Estatístico de Status de Sobrevivência de Token de 2025 (lançado em janeiro de 2026), que foi relatado por muitos meios de comunicação financeiros (Sina Finance, Phemex, RBC Crypto).

**Falha 2: A mineração é altamente centralizada**

A mineração de Bitcoin tem mostrado um alto grau de concentração:

| Piscina de mineração | Rácio de taxa de hash |
|------|---------|
| Fundição EUA | Cerca de 30% |
| AntPool | Cerca de 19% |
| Via BTC | Cerca de 14,5% |
| F2Pool | Cerca de 10% |
| Piscina MARA | Cerca de 5% |
| Os dois principais pools de mineração combinados | Mais de 50% |
| Os quatro principais pools de mineração combinados | Cerca de 75% |

**Nota da fonte:** Os dados acima são compilados do relatório mensal de distribuição de hashrate de 2025 (CoinGradient 2025.3 "Foundry, Antpool e Viabtc Dominate Bitcoin Mining"; HashrateIndex "Top 10 Bitcoin Mining Pools of 2025"). Os valores específicos de diferentes fontes de dados podem variar ligeiramente (geralmente dentro de ±2%), mas a conclusão de que “os quatro principais pools de mineração controlam cerca de 75% do poder computacional” se reflete em múltiplas plataformas de monitoramento convencionais.

**Falha 3: a taxa de participação na governança do DAO é extremamente baixa**

| Dados | Fonte |
|------|------|
| A taxa de participação votante da maioria dos DAOs é de apenas cerca de 3%-12% (a mediana é de cerca de 6%) | DeepDAO (2025) Agregação de dados de governança em cadeia; Relatório de governança do DAO da sala de reuniões (2024) |
| Um pequeno número de detentores de moeda controla a grande maioria dos direitos de voto (elevada concentração do poder de governação) | ACM (2024) "Governança DAO: poder de voto, participação e controvérsia" DOI:10.1145/3777416 |

### 1.4 Insights principais

Tenho julgamento, mas não tenho ingresso; Tenho visão, mas não tenho direito de falar; Quero participar, mas estou bloqueado por limites elevados.

---

## Capítulo 2: Resposta do LightDAO

### 2.1 Posicionamento central

LightDAO é uma organização nacional autônoma de investimento com governança on-chain como núcleo e SPV de conformidade como transportador de execução de investimentos. Através de uma cadeia pública projetada especificamente para nós da web leves, os usuários globais podem participar na manutenção da rede, na votação de governança e compartilhar benefícios ecológicos de acordo com as regras com apenas um navegador.

### 2.2 Modelo de motor duplo

| Motor | Direção de Investimento | Alvo | Características do rendimento |
|------|---------|------|---------|
| Motor Um: Motor de Fluxo de Caixa (Shou) | Activos de serviços de consumo rígido a nível comunitário | Formar fluxo de caixa contínuo e distribuir lucros de acordo com regras | Buscar estabilidade relativa, mas não prometer renda fixa |
| Motor 2: Motor de crescimento (ataque) | Empresas de tecnologia de ponta | Obter valorização do patrimônio e retornos de saída | Elevado potencial de flexibilidade, mas também pode enfrentar perdas ou falhas de saída |

**Disciplina de alocação:** Em princípio, alocar 70% dos recursos para ativos com fluxo de caixa estável e 30% para metas de alto crescimento.

**Caminho de crescimento em escala de investimento:** O tamanho de um único investimento cresce dinamicamente com o preço do LIGHT e a capacidade do cofre - o período de inicialização (LIGHT entre US$ 0,02 e US$ 0,05) é adequado para pequenos ativos em nível comunitário de US$ 2,55 milhões a US$ 6,37 milhões; o estágio de crescimento (US$ 0,05-US$ 0,30) entra em cadeias regionais e rodadas Seed-A de US$ 6,37 milhões a US$ 38,25 milhões (comparando com o Lower Middle Market) PE); no estágio maduro (US$ 0,30 a US$ 1,00), atinge o nível de PE do mercado médio de US$ 38,25 milhões a US$ 127,5 milhões; no estágio de escala (US$ 1,00+), pode executar aquisições em grande escala e investimentos pré-IPO de mais de US$ 127,5 milhões. Restrições severas: uma única transação não deve exceder 15% do valor restante da tesouraria de investimento (ver Capítulo 9 para detalhes).

**O primeiro princípio de posicionamento de meta:** Em vez de pressupor um nome de empresa específico, primeiro estabeleça uma estrutura de triagem - dê prioridade a ativos rígidos de serviços ao consumidor em nível comunitário, que exigem um modelo econômico comprovado de loja única, registros de fluxo de caixa estáveis ​​(a margem EBITDA nos últimos três anos não é inferior a 10% e a volatilidade inter-anual não é superior a 15%) e um caminho claro de expansão regional. O alvo específico é determinado pelas propostas da comunidade.

### 2.3 Proposta de valor central

**O navegador é o nó** - Não há necessidade de comprar uma máquina de mineração ou ter formação técnica profissional. Você pode participar de contribuições da rede visitando a plataforma web oficial.

**Todos podem participar** - Após atingir o limite de governança, os detentores de pequenos montantes de LIGHT também podem participar da votação para decidir em conjunto a direção da alocação dos fundos.

**Participação nos lucros de acordo com regras** - Os lucros operacionais das empresas investidas e os retornos de saída dos projetos de tecnologia serão distribuídos de acordo com as regras da rede e acordos SPV.

### 2.4 Lema

"Seu navegador também pode ser a porta de entrada para ativos de alta qualidade."

### 2.5 Análise de diferenciação competitiva de produtos

| Dimensão | Rede Pi | Hélio | DAO tradicional (MakerDAO, etc.) | LightDAO |
|------|-----------|--------|----------|----------|
| Método de participação | Clique no APP móvel | Comprar ponto de acesso de hardware (US$ 200 a US$ 1.000) | Compra de token + operação on-chain | Acesso ao navegador, custo zero de hardware |
| Custo de entrada | Zero (mas sem utilidade prática) | Alto (hardware + instalação) | Médio a alto (precisa adquirir tokens de governança) | Zero (apenas um navegador) |
| Quantidade total de fichas | 100 bilhões | 223 milhões | Varia | 2,5 bilhões |
| Função de investimento real | Nenhum | Nenhuma (apenas cobertura de rede) | Sim (mas o limiar é extremamente elevado) | Sim (estrutura SPV, todos podem participar) |
| Fonte de rendimento | Não está claro | Taxa de utilização da rede | Taxa de acordo | Lucro corporativo + retorno de saída + taxa de gás |
| Isolamento jurídico | Nenhum | Nenhum | Alguns sim | Cayman SPV+ZK-KYC |
| Taxa de participação na governação | Extremamente baixo (sem governação substancial) | Baixo | Cerca de 6% | Meta >15% (votação bidimensional + incentivos) |

**A principal diferença do LightDAO:** Atualmente é o único projeto que combina "mineração web de limite zero" com "investimento em entidade SPV compatível". Os usuários não apenas contribuem com recursos de rede para obter recompensas simbólicas, mas também participam diretamente em decisões reais de investimento empresarial por meio de votação de governança e compartilham lucros operacionais.

> **[Terminologia neste capítulo]**
> **DAO** (Organização Autônoma Descentralizada): Uma forma organizacional na qual as regras de governança são codificadas por meio de contratos inteligentes e as decisões coletivas são tomadas pelos detentores de tokens. Não existe uma hierarquia empresarial tradicional.
> **SPV** (Special Purpose Vehicle): pessoa jurídica independente (geralmente registrada nas Ilhas Cayman) estabelecida para transações ou investimentos específicos para obter isolamento de risco - as dívidas e responsabilidades legais do SPV não são transmitidas ao próprio DAO.
> **DePIN** (Rede de infraestrutura física descentralizada, rede de infraestrutura física descentralizada): um modelo de rede que usa tokens para incentivar os usuários a contribuir com recursos físicos (largura de banda, armazenamento, poder de computação, cobertura sem fio, etc.) para construir infraestrutura.
> **Lower Middle Market PE** (downstream mid-end private equity): um segmento de mercado da indústria global de private equity. O tamanho de uma única transação é geralmente de US$ 10 milhões a US$ 100 milhões, e o EBITDA da empresa-alvo está entre US$ 2 milhões e US$ 15 milhões.

---

## Capítulo 3: Compliance e isolamento legal

### 3.1 Camada de isolamento legal SPV

A DAO não detém participação direta em nenhuma empresa física. Todos os investimentos externos são executados através de veículos de propósito específico (SPVs) estabelecidos nas Ilhas Cayman.

| Pontos de projeto | Descrição |
|--------|------|
| Carta SPV | Fica claramente acordado que o funcionamento da SPV obedecerá à efetiva resolução da DAO |
| Definição legal de subtokens | Os subtokens são "certificados de direitos de reivindicação de distribuição de renda SPV", que representam apenas as qualificações de distribuição para fluxo de caixa futuro |
| Não acarreta direitos de accionista | Não acarreta direitos de governo societário, preferências de liquidação ou quaisquer direitos de acionistas |
| Diretores da SPV | são atendidos por terceiros independentes; DAO pode substituir diretores aprovando uma resolução válida |
| Supervisão de fundos | As contas bancárias são supervisionadas por instituições de custódia licenciadas e as transferências de fundos devem passar pela verificação de múltiplas assinaturas e conformidade |
| Resolução de litígios SPV | O estatuto da SPV estipula uma cláusula de arbitragem (SIAC ou ICC), e o DAO pode iniciar procedimentos de arbitragem através de uma resolução de governança |

### 3.2 Verificação opcional e proteção de privacidade

**Nenhuma identificação é necessária para participar do protocolo em si. ** Visite páginas da web, crie carteiras, contribua com recursos, receba LIGHT, inicie e participe de votações de governança - não há necessidade de fazer upload de documentos durante todo o processo e nenhuma informação de identificação pessoal (PII) é armazenada na cadeia.

Somente quando um usuário utiliza ativamente um serviço regulamentado de terceiros estará envolvida a verificação de que o próprio serviço deve funcionar de acordo com a lei. Esta verificação é coletada, realizada e mantida pelo prestador de serviço. LightDAO não coleta, transfere ou armazena quaisquer dados:

| Cenário | Quem realiza a verificação | O que o usuário precisa fazer |
|---|---|---|
| Compra/venda através de canais fiduciários | Terceiros licenciados (como MoonPay, Ramp Network, Transak) | Concluir o processo de conformidade de acordo com os requisitos do próprio prestador de serviços |
| Subtokens de troca (certificados de ações de investimento) | Dependendo dos requisitos do produto específico e do seu fornecedor de serviços | Só se pode fazer mineração e governança, sem qualquer verificação |
| Saque para cartão bancário/pagamento local | Prestador de serviços de levantamento e pagamento | Concluir o processo de conformidade conforme exigido pelo provedor de serviços |

Princípios fundamentais: **Verificação zero por padrão; a verificação só ocorre no momento em que o utilizador entra ativamente no serviço regulado, e fica a cargo do prestador do serviço. **Ninguém perderá o direito de minerar, reter, transferir ou votar devido a "falha na verificação".

> Tecnologia reservada: Se um determinado tipo de ativo exigir um limite de qualificação no futuro, o usuário terá o certificado na forma de prova de conhecimento zero (ZK), e a cadeia apenas verificará "se foi atendido" sem qualquer informação de identidade - isso faz parte do roteiro e não é um requisito atual.

### 3.3 Declaração de Responsabilidade Fiscal

O acordo não fornece serviços de declaração fiscal, e as obrigações fiscais de todas as recompensas ecológicas e rendimentos relacionados são suportadas pelos próprios utilizadores. Os usuários devem cumprir as leis e regulamentos relevantes do local de sua residência fiscal.

### 3.4 Acesso do usuário: aberto a todos

**Sem limite para inscrição e participação**: Não é necessário e-mail, número de celular, conta social ou comprovante de identidade; um dispositivo que possa abrir uma página da web é tudo que você precisa. LightDAO ** não restringe ativamente a participação do usuário em nenhum país ou região, nem implanta geofencing. **

As únicas restrições externas vêm de serviços de terceiros: se a lei de um determinado local tiver outros requisitos para serviços específicos (como depósitos e retiradas em moeda fiduciária), esses serviços serão executados por instituições locais licenciadas de acordo com a lei do seu lado e não afetarão o uso de funções em cadeia por ninguém (mineração, retenção, transferências, votação, propostas).

Se uma determinada jurisdição emitir regulamentos proibitivos explícitos no futuro, a sequência de resposta do protocolo será:

1. Primeiro, garantir que os direitos de alienação de ativos dos usuários existentes não sejam afetados - os ativos na cadeia não podem ser congelados e qualquer pessoa pode transferir seus LIGHT e subtokens a qualquer momento;
2. Permanecer acessíveis através de múltiplos portais front-end (incluindo espelhos IPFS e espelhos comunitários);
3. A última etapa é ajustar o escopo disponível de **serviços de terceiros** no âmbito da aplicação da lei.

Em uma palavra: *** as restrições só podem recair sobre os serviços, não sobre as pessoas. **

### 3.5 Depósitos e saques em moeda legal e canais entre cadeias

**Canal de moeda fiduciária (agregação de serviços de terceiros):** O protocolo em si não opera serviços legais de depósito e retirada de moeda, mas a plataforma web integra canais de terceiros compatíveis (MoonPay, Ramp Network, Transak, etc.), cobrindo os principais mercados da América do Norte, Europa, Sudeste Asiático e América Latina; a agregação do mercado P2P local abrange a África e o Sul da Ásia; as retiradas suportam métodos de pagamento locais, como GCash, M-Pesa, Pix e GrabPay.

**Ponte entre cadeias e canais de aquisição LIGHT:** Transações AMM integradas na cadeia LightDAO após TGE; interoperabilidade com o ecossistema Cosmos através do IBC; planejamento para wLIGHT (Ethereum/Solana) a partir do 6º mês; solicitação de listagem CEX a partir do 6º mês dependendo do cumprimento. A ponte entre cadeias é operada por terceiros independentes e é necessário um relatório de auditoria independente antes que a ponte fique online.

### 3.6 Declaração de conformidade do mecanismo de convite (análise anti-MLM)

O incentivo de convite da LightDAO é **compartilhamento de camada única** (apenas os convidadores diretos recebem uma proporção fixa das recompensas de mineração do convidado) e não possui os recursos principais do marketing multinível (MLM): sem comissão recursiva multinível; a receita vem da liberação de tokens predefinidos no protocolo, e não do principal do recém-chegado; não há custo zero e nenhuma taxa de entrada para participar da mineração. Esta estrutura está mais próxima de "recompensas de recomendação de contribuidores de projetos de código aberto". Antes da operação formal, será contratado um advogado licenciado no mercado-alvo para emitir pareceres especiais de compliance.

> **[Terminologia neste capítulo]**
> **KYC** (Know Your Customer, Know Your Customer): Um processo de conformidade para instituições financeiras verificarem a identidade do usuário, geralmente exigindo o envio de documentos de identidade, comprovante de endereço, etc.
> **ZK-KYC** (KYC de conhecimento zero, KYC de prova de conhecimento zero): os usuários não precisam divulgar informações pessoais específicas ao contrato e usam criptografia apenas para provar "Eu atendo certas condições" (como idade ≥ 18 anos, nacionalidade não sancionada) método de verificação de conformidade. Nenhum dado do documento original é armazenado na cadeia.
> **PII** (Informações de Identificação Pessoal, Informações de Identificação Pessoal): Dados que podem identificar uma pessoa física específica individualmente ou em combinação, como nome, número de identificação, endereço, características biométricas, etc.
> **Reg D / Reg S** (Regulamento D/Regulamento S da Lei de Valores Mobiliários dos EUA): O Reg D permite colocações privadas para "investidores qualificados" nos Estados Unidos sem registro público (padrão de definição da Regra 501); Reg S permite a venda de títulos a pessoas fora dos Estados Unidos sem acionar requisitos de registro nos EUA.
> **MiFID II** (Diretiva II dos Mercados de Instrumentos Financeiros da UE, 2014/65/UE): quadro regulamentar financeiro da UE, o seu Anexo II define os critérios de identificação para "investidores profissionais" (carteira de instrumentos financeiros de 500 mil euros, 1 ano de experiência no setor financeiro, 10 transações de grande escala por trimestre, cumprindo o segundo requisito).
> **MLM** (Marketing Multinível, marketing multinível): um modelo de negócio através de comissões recursivas multinível (desenvolvimento de downline, desenvolvimento de downline e comissões de upline camada por camada). É essencialmente diferente das recompensas de recomendação de camada única - LightDAO é apenas de camada única (A convida B, A recebe uma parte de B; B convida C, A não recebe nenhuma parte de C).
> **IBC** (Inter-Blockchain Communication, protocolo de comunicação cross-chain): o padrão cross-chain nativo do ecossistema Cosmos, permitindo a transferência segura de ativos e mensagens entre diferentes blockchains sem a necessidade de um intermediário centralizado.

---

## Capítulo 4: Arquitetura Técnica

### 4.1 O que é a cadeia pública?

A cadeia pública da LightDAO pode ser entendida como um "livro de contas públicas com regras transparentes e que não pode ser alterado à vontade": as regras de governança estão escritas no código e os registros de votação, fluxos de capital e distribuição de lucros de qualquer pessoa podem ser consultados e verificados na cadeia.

### 4.2 Parâmetros técnicos e demonstração de seleção

| Itens técnicos | Seleção | Base de seleção |
|-------|------|--------|
| Quadro subjacente | Cosmos SDK | Arquitetura modular, verificação de múltiplas cadeias produtivas |
| Mecanismo de consenso | PoS Tendermint | Certeza instantânea; a geração do bloco leva de 1,5 a 2 segundos; Tolerância a falhas BFT ≤ 1/3 mal |
| Contratos Inteligentes | CosmWasm | WebAssembly + Rust, segurança de memória em tempo de compilação |
| Capacidades entre cadeias | Protocolo IBC | Padrão de cadeia cruzada nativo do Cosmos |
| Interação front-end | Aplicativo Web Progressivo (PWA) | Navegador em execução, adaptável para desktop/móvel, sem necessidade de instalação |

### 4.3 Mecanismo leve de mineração de nós e modelo de incentivo

#### 4.3.1 Método de mineração

Os usuários acessam a plataforma web oficial através de um navegador, criam uma carteira e clicam em “Iniciar Mineração”. Durante o processo de mineração, os usuários contribuem com largura de banda de rede (retransmissão e verificação de dados) e recursos de computação locais (verificação leve de cabeçalho de bloco) por meio do navegador e não dependem de poder de computação de alta energia.

**Implementação de tecnologia no lado da Web:** Retransmissão P2P do canal de dados WebRTC; Verificação do cabeçalho do bloco em segundo plano do Web Worker; Cache e pulsação off-line do Service Worker; Conexão longa do WebSocket.

**Adaptação do navegador mobile:** Adotar um sistema de sessões válidas cumulativas (4 horas por dia = pontuação de 100%); nenhum ponto será deduzido por reconectar dentro de 5 minutos após a desconexão; Os usuários instalados do PWA receberão um bônus adicional de 10% de tempo online; mecanismo on-line delegado (70% para o delegado/30% para o nó de retransmissão).

#### 4.3.2—4.3.3 Esquema de incentivos e modelo de três motores

Adota o modelo trimotor de “prova de contribuição PoC + incentivo de fissão de convite + incentivo de bônus comportamental”.

#### 4.3.4 Dimensões e peso da contribuição

| Dimensão contribuição | Peso | Método de medição |
|--------|------|--------|
| Contribuição de retransmissão de largura de banda | 40% | Proporção entre o tráfego de retransmissão de upload e o volume de dados de verificação |
| Duração efetiva da sessão | 30% | Sessões efetivas cumulativas diárias (4 horas = 100%) |
| Contribuição de verificação de bloco | 20% | Número e precisão dos cabeçalhos de bloco efetivamente verificados |
| Estabilidade da rede | 10% | Atraso de conexão, taxa de perda de pacotes, tempo de resposta |

#### 4.3.5 Fórmula de cálculo de recompensa

**Recompensa diária de mineração = Recompensa base × Pontuação de peso de contribuição × (1 + bônus de convite) × (1 + bônus de comportamento)**

- BaseReward = Valor total liberado por toda a rede no dia ÷ Número total de mineradores ativos no dia
- Bônus de convite = número efetivo de convidados × 1% (limite máximo de 20%)
- Bônus de comportamento = 5% de participação na votação + 5% de contribuição de conteúdo + 5% de atividade da comunidade + 5% de qualidade de verificação de nó (limite superior de 20%)
- Coeficiente de bônus total = (1+20%) × (1+20%) = 1,44 vezes

#### 4.3.6 Convidar incentivos à fissão

| Nível | Número válido de convites | Proporção de participação de convites | Recompensa única adicional | Bônus de peso de governança |
|------|------------|------------|--------------|------------|
| Mineiros | 0 pessoas | — | Recompensas básicas de mineração | Nenhum |
| Pregador | Nada menos que 3 pessoas | 10% | 100 LUZ | Nenhum |
| Embaixador | Nada menos que 10 pessoas | 15% | 500 LIGHT + emblema na corrente | Peso de votação +5% |
| Parceiros | Nada menos que 50 pessoas | 20% | 2.500 LIGHT + emblema na corrente | Peso de votação +10% |

O bônus de ponderação de governança e o bônus de reputação (até +30%) são acumulados de forma independente, com um limite superior total de +40%. O bônus de convite atinge seu pico quando há 20 pessoas (20×1%=20%).

#### 4.3.7 Mecanismo anti-trapaça

Detecção de integridade do ambiente do navegador (impressão digital Canvas/WebGL/WebRTC), detecção de profundidade de pacote, clustering de IP e análise de padrão de comportamento, impressão digital comportamental multidimensional (trajetória do mouse/ritmo do teclado/comportamento de rolagem), verificação de autenticidade de endereço de convite. Custo do ataque anti-Sybil: US$ 50.000 a US$ 200.000 para criar 10.000 impressões digitais independentes; meta de taxa de detecção> 90-95%.

### 4.4 Matriz de funções do token LIGHT

Combustível de rede (taxa de gás), direitos de governança (voto/proposta/campanha), vinculação de promessa (margem/campanha/verificador), troca de investimento (subtokens), incentivos ecológicos (mineração/convite/comportamento), expansão futura (dApp/NFT/cross-chain).

### 4.5 Taxa de gás e mecanismo de taxa de transação

**Princípio de Design:** A taxa de gás é ancorada no equivalente em dólares americanos, e o valor real de LIGHT cobrado é convertido automaticamente a cada 24 horas pelo oráculo da rede (Seção 4.10). Isso garante que não importa se o preço do LIGHT sobe ou desce, o custo real de pagamento do usuário (em dólares americanos) permanece estável, evitando o problema de "o preço da moeda aumenta 100 vezes → a taxa de transferência passa a ser de US$ 10" ou "o preço da moeda cai 90% → resgate de bilhetes com custo zero".

**Meta de taxa de gás ancorada em dólares americanos:**

| Tipo de transação | Objectivo equivalente em dólares americanos | Arrecadação real quando LIGHT=$0,05 | Arrecadação real quando LIGHT=$0,50 | Intenção de design |
|--------|------------|------------------|------------------|----------|
| Transferência normal | US$ 0,001 | 0,02 LUZ | 0,002 LUZ | Limite extremamente baixo para garantir que usuários de pequenas quantias possam transferir dinheiro livremente |
| Votação sobre Governança | US$ 0,005 | 0,10 LUZ | 0,01 LUZ | Ligeiramente superior à transferência para evitar a eliminação gratuita de votos |
| Envie uma proposta | US$ 0,10 | 2.0 LUZ | 0,2 LUZ | Cooperar com o sistema de depósitos para aumentar a seriedade da proposta |
| Troca de subtokens | US$ 0,50 | 10,0 LUZ | 1.0 LUZ | Taxas mais elevadas, correspondentes à seriedade das operações em grande escala |
| Relatórios de pulsação de mineração | $0 (grátis) | 0 | 0 | Não há cobrança de gás pelas contribuições mineiras, garantindo participação a custo zero |

**Regras de conversão dinâmica:**

- 实际Gas费（LIGHT）= USD目标 ÷ 预言机24h TWAP价格
- 每24小时（UTC 00:00区块）由oracle_twap合约自动更新换算比率
- 设置下限：任何交易类型的Gas费不低于0.001 LIGHT（防止价格为零时Gas归零）
- 设置上限：任何交易类型的Gas费不高于100 LIGHT（防止价格极低时Gas过高阻碍使用）
- USD目标值本身可通过微型提案（$100保证金）由治理调整

**Regras de alocação de taxas de gás:**

| Destino | Proporção | Função |
|------|------|------|
| Destruição permanente | 50% | Continuação da deflação, reduzindo a oferta em circulação |
| Recompensas do validador | 30% | Incentivar os validadores a manter a segurança da rede e produzir blocos |
| Tesouro Ecológico | 20% | Financiamento complementar para desenvolvedores e fundos operacionais comunitários |

**Estimativa de deflação da taxa de gás:** Supondo uma média de 100.000 transações ativas diárias e uma taxa de gás média de US$ 0,005 (principalmente votação e transferências), o equivalente a dólares americanos destruídos por dia = 100.000 × US$ 0,005 × 50% = US$ 250/dia. Quando LUZ=$0,05, equivale a 5.000 LUZ/dia≈1,825 milhão/ano; quando LIGHT=$0,50, é equivalente a 500 LIGHT/dia≈182.500/ano. A quantidade de LIGHT com a deflação da taxa de gás diminui à medida que o preço aumenta (o equivalente em dólares é constante), mas seu suporte ao preço é refletido pela "compra contínua do equivalente" - cada transação está destruindo tokens a uma taxa fixa em dólares.

### 4.6 Sistema verificador

| Dimensões | Validadores | Nós leves (mineradores de navegador) |
|------|--------|-------------------|
| Responsabilidades | Geração de blocos, consenso, nó completo | Verificação de cabeçalho de bloco, retransmissão de dados |
| Estacamento | Mínimo 500.000 LUZ | Nenhum |
| Renda | Taxa de gás 30% + pool de liberação diária 5% | Recompensas de mineração PoC (pool de lançamento diário 95%) |
| Quantidade | Inicial 21, limite superior 100 | Sem limite superior |
| Cortando | Multa de 5% por dupla assinatura + banimento de 180 dias | Nenhum |

**Início em etapas (tolerância a falhas BFT: N≥3f+1):**

| Fase | Número de validadores | Tolerância a falhas f | Condições de parada da corrente | Experiência do usuário |
|------|-----------|-------|-----------|----------|
| Testnet (3 meses antes do TGE) | 7 | 2 | 3 off-line ao mesmo tempo | Os testes internos podem tolerar pequenas interrupções |
| Rede principal TGE | Mínimo 10, meta 21 | 3-6 | 4-7 offline ao mesmo tempo | Interrupções ocasionais (<1 vez por trimestre) para suavizar |
| Aberto para eleição a partir do 7º mês | 21-100 | 6-33 | 7-34 off-line ao mesmo tempo | Usuário não sabe |

**Resumindo: o TGE não deve ser executado quando houver <7 validadores. ** Menos de 7 significa f ≤ 1. Qualquer falha de ponto único causará o desligamento de toda a cadeia, o que equivale a "indisponibilidade do produto" para usuários não técnicos.

### 4.7 Camada de infraestrutura de rede

Os nós validadores transportam gateways de acesso WebSocket de forma distribuída (cada validador tem um limite máximo de 50.000 conexões); A sinalização P2P é fornecida pelo validador + nó de retransmissão da comunidade; A agregação Merkle de pulsação envia apenas o hash raiz por bloco (O(1) sobrecarga na cadeia); o front-end é distribuído através de IPFS+CDN.

Rede P2P: estrutura WebRTC ICE (prioridade STUN/fallback TURN); cerca de 70-80% dos usuários podem se conectar diretamente, 20-30% dos usuários NAT simétricos passam pelo relé TURN; quando o P2P falha, ele é rebaixado para o "modo de autenticação pura".

Especificações de desempenho: TPS teórico 1.000-3.000; tamanho do bloco 2 MB (governança ajustável); sincronização de nó leve <30 segundos; agregação Merkle de pulsação de um milhão de nós <500 ms.

### 4.8 Mecanismo de verificação de prova de contribuição

Arquitetura de verificação de três níveis: (1) Desafio de amostragem cruzada aleatória do verificador (5% nós a cada 10 minutos, tempo de resposta de 30 segundos); (2) Verificação mútua entre pares P2P (8 a 16 pares registram independentemente o volume de troca de dados, calculando a mediana); (3) Agregação Merkle on-chain (cada bloco envia pontuação de contribuição Root, os usuários podem autoverificar por meio do Merkle Proof). Deixar de desafiar 3 vezes seguidas → a pontuação do dia será zerada; um total de 5 vezes em 7 dias → uma revisão anti-trapaça será acionada.

### 4.9 Carteira e gerenciamento de chaves

Arquitetura de três camadas: (1) Carteira inteligente incorporada (Passkey/WebAuthn, sem necessidade de frase mnemônica, alvo de mais de 80% de usuários); (2) Carteira de recuperação social (3-5 restauradores, fragmentação de Shamir, 2/3 de confirmação da maioria); (3) Carteira auto-hospedada (frase mnemônica BIP-39 + carteira de hardware compatível). As taxas do gás para as primeiras 100 transações de novos usuários serão pagas pelo fundo ecológico (modelo Paymaster).

### 4.10 Oráculo de Preço

O TWAP on-chain (preço médio ponderado de 30 dias do pool LIGHT/USDC) é a principal fonte de preço; 3+ agregação DEX/CEX externa é complementada (os validadores enviam em rotação, pegam a mediana); desvios >±15% acionam sinalizadores de exceção; desvios de bloco único >5% não estão incluídos no TWAP (manipulação de empréstimo anti-flash); fallback para TWAP puro na cadeia quando todos os oráculos externos falharem.

### 4.11 Arquitetura do Módulo de Contrato Inteligente

10 contratos principais: light_token, mining_reward, governança, treasury_multisig, subtoken_factory, oracle_twap, anti_fraud, validator_registry, vesting, insurance_fund. O contrato principal deve passar pela verificação formal antes da TGE.

### 4.12 Atualização de Protocolo e Governança da Cadeia

Atualização de nível 4: ajuste de parâmetro L1 (votação de governança 24-72h) → Migração de contrato L2 (proposta principal + auditoria + atraso de 72h) → Mudança de consenso L3 (66% aprovado + 2/3 sinais de validador + período de proteção de fork de 7 dias) → Reparo de emergência L4 (suspensão do comitê sombra + hot fix de múltiplas assinaturas + ratificação de 72h).

> **[Terminologia neste capítulo]**
> **Cosmos SDK**: uma estrutura modular de desenvolvimento de blockchain que permite aos desenvolvedores montar cadeias públicas personalizadas como blocos de construção. Diversas cadeias produtivas (como Cosmos Hub e Osmose) verificaram sua maturidade.
> **Tendermint PoS** (Proof of Stake, Proof of Stake): Um mecanismo de consenso no qual os validadores obtêm o direito de produzir blocos prometendo tokens (em vez de competir pelo poder computacional). Fornece "finalidade instantânea" - depois que um bloco é enviado, ele não pode ser revertido.
> **BFT** (Tolerância a Falhas Bizantinas, Tolerância a Falhas Bizantinas): Um mecanismo em um sistema distribuído que pode tolerar alguns nós fazendo mal ou funcionando mal e ainda assim alcançar o consenso corretamente. O Tendermint BFT não pode tolerar mais do que 1/3 dos validadores agindo mal ou ficando offline ao mesmo tempo.
> **CosmWasm**: O mecanismo de contrato inteligente do ecossistema Cosmos, baseado na tecnologia WebAssembly, suporta o uso da linguagem Rust para escrever contratos e possui recursos de segurança de memória em tempo de compilação (evitando vulnerabilidades comuns, como buffer overflows).
> **PWA** (Progressive Web App, Progressive Web App): uma tecnologia da Web executada em um navegador, mas com uma experiência de aplicativo semelhante à nativa. Ele suporta cache offline, notificações push e adição à tela inicial sem baixar e instalar na app store.
> **WebRTC/WebSocket**: Duas tecnologias de comunicação em tempo real do navegador. WebRTC é usado para retransmissão de dados P2P (transmissão direta entre nós); WebSocket é usado para manter uma longa conexão entre o cliente e o verificador (pulsação, notificação de recompensa).
> **PoC** (Prova de Contribuição): O mecanismo de incentivo adotado pela LightDAO emite recompensas verificando os recursos de rede (retransmissão de largura de banda, verificação de bloco, tempo online) realmente contribuídos pelos usuários, em vez de depender da competição de poder de computação ou promessa de capital.
> **Merkle Tree** (Merkle Tree): Uma estrutura de dados em árvore hash que permite a verificação eficiente da integridade de uma entrada específica em uma grande quantidade de dados. Este white paper é usado para agregar milhões de pulsações de nós leves em um único hash raiz e carregá-lo na cadeia (sobrecarga de armazenamento O(1)).
> **Gas fee**: A taxa de manuseio necessária para executar transações ou operações contratuais no blockchain, usada para compensar o verificador pelos recursos de computação e armazenamento. A taxa de gás do LightDAO é ancorada no equivalente em dólares americanos e é automaticamente convertida no valor de LIGHT pelo oráculo a cada 24 horas.
> **Slashing** (penalidade): Mecanismo de penalidade em que um verificador é forçado a deduzir parte dos tokens prometidos devido a atos ilícitos (como assinatura dupla) ou por estar offline por um longo período. É uma garantia económica para a segurança da rede PoS.
> **Oracle** (Oracle): um componente de infraestrutura que transmite com segurança dados fora da rede (como preços de mercado, clima, resultados esportivos) para contratos inteligentes na rede. LightDAO usa uma arquitetura oracle híbrida de TWAP on-chain + agregação multifonte.
> **TWAP** (Preço Médio Ponderado pelo Tempo): O preço de cada bloco dentro de um período de tempo é igualmente ponderado pelo tempo para reduzir o impacto da manipulação de transações instantâneas de grande valor na referência de preço.
> **AMM** (Formador de Mercado Automatizado): Um protocolo de negociação descentralizado que realiza a troca de tokens por meio de um pool de liquidez (em vez de uma carteira de pedidos). O preço é determinado automaticamente pela proporção de ativos no pool de acordo com uma fórmula.
> **DEX / CEX**: DEX (Decentralized Exchange, exchange descentralizada) não precisa hospedar ativos de usuários e negocia peer-to-peer por meio de contratos inteligentes; CEX (Centralized Exchange, bolsa centralizada) exige que a operadora custódia de ativos e combine transações.
> **IPFS** (InterPlanetary File System, InterPlanetary File System): protocolo descentralizado de armazenamento e distribuição de arquivos, usado neste white paper para hospedagem resistente à censura de aplicativos front-end (mesmo que o nome de domínio esteja bloqueado, os usuários ainda poderão acessar a plataforma por meio de IPFS).

---

## Capítulo 5: Modelo Econômico de Token

### 5.1 Base total do projeto

**Fornecimento total da LIGHT: 2,5 bilhões (2.500.000.000), e nunca será emitido adicionalmente. **

| Projetos de benchmarking | Montante total | Métodos de participação | Comparabilidade com LightDAO |
|--------|------|---------|------------------|
| Bitcoin | 21 milhões | Máquina de mineração PoW | Referência narrativa, o limite é muito alto |
| Hélio (HNT) | 223 milhões | Ponto de acesso de hardware $ 200 + | Benchmark DePIN, escala limitada de hardware |
| Filecoin (FIL) | 2 bilhões | Hardware de armazenamento | Os mais próximos em magnitude, ambos estão “contribuindo com recursos em troca de tokens” |
| Kaspa (KAS) | 28,7 bilhões | Placa gráfica PoW | Declínio muito grande e suave tem valor de referência |
| Rede Pi | 100 bilhões | Cliques em dispositivos móveis | Material didático negativo: O valor total é muito grande → a percepção de valor é extremamente baixa |

**Principal razão para escolher 2,5 bilhões de moedas:**

1. **Capacidade de investimento (restrição primária):** 850 milhões de moedas no cofre × preço base US$ 0,15 × taxa de utilização de 75% = **US$ 95,63 milhões ≈ US$ 100 milhões** capital implantável, atingindo o limite mínimo de credibilidade do Lower Middle Market PE. Base acadêmica: Cong, Li & Wang (2021) "Tokenomics: Dynamic Adoption and Valuation" (*Review of Financial Studies* 34(3):1105-1155, NBER w27222) prova que a utilidade da plataforma (retorno do investimento → recompra → suporte de preço) é o impulsionador fundamental do valor do token, não da amplitude de distribuição.
2. **Orientação da rede:** 1 bilhão de moedas são extraídas e 684.900 moedas são liberadas no primeiro dia da época. Quando há 100 mil mineradores ativos, a média per capita é de 6,51 LIGHT/dia, mantendo a “percepção de número inteiro”.
3. **Viabilidade operacional:** 10% de fundo operacional estratégico (250 milhões de moedas) para resolver a lacuna de desenvolvimento/auditoria/financiamento legal pré-TGE (US$ 1,10-2,85 milhões). O modelo comunitário puro não pode cobrir este custo.
4. **Viabilidade de deflação:** O resultado final de 1 bilhão de moedas é alcançado no 11º ao 12º ano no cenário base (25-30% menor que os 15 anos+ do plano de 21 bilhões).
5. **Benchmarking razoável:** O mesmo nível do Filecoin (2 bilhões), que está entre os cinco principais projetos na área DePIN em valor de mercado.

### 5.2 Plano de distribuição de tokens

| Categoria de Alocação | Proporção | Quantidade | Finalidade | Método de liberação |
|--------|------|------|------|--------|
| Mineração de nós leves | 40% | 1 bilhão | Recompensar contribuidores da rede | Reduzido para metade a cada 2 anos, divulgado em tempo real com base na contribuição |
| Cofre de Investimento Corporativo | 34% | 850 milhões de peças | Execução de investimentos sob governança DAO (destruída durante o investimento) | Bloqueio com múltiplas assinaturas, liberado e destruído somente através de resoluções válidas |
| Fundo de Desenvolvimento Ecológico | 16% | 400 milhões | Liquidez, lançamentos aéreos, financiamento de desenvolvedores, operações comunitárias | Libertação faseada (ver secção 5.3) |
| Fundo operacional estratégico | 10% | 250 milhões de moedas | Equipe, auditoria, jurídico, infraestrutura, investidores estratégicos | 12 meses de precipício + 36 meses lineares (ver secção 5.X) |

**Benchmarking da indústria (benchmarking de coorte Tokenomics.net 2024-2025):** Recompensas da comunidade/usuário 20-35% (LightDAO: 40% mineração + 16% ecologia = 56%, maior devido a nenhuma rodada de VC); tesouraria/reservas 15-25% (LightDAO: 34%, devido à função de investimento); equipe/investidores 15-45% (LightDAO: 10%, muito inferior à indústria, mantendo a narrativa “National DAO”).

### 5.3 Plano de Liberação do Fundo de Desenvolvimento Ecológico

| Palco | Tempo | Proporção | Quantidade | Finalidade |
|------|------|------|------|------|
| TGE | Dia 0 | 30% | 120 milhões de peças | Liquidez DEX (60% = 72 milhões) + lançamento aéreo de sementes (40% = 48 milhões) |
| Período de liberação linear 1 | 1º ao 12º mês | 40% | 160 milhões de moedas | 13,33 milhões de moedas por mês: incentivos comunitários, marketing, plano de lançamento aéreo |
| Período de liberação linear 2 | 13 a 24 | 30% | 120 milhões de moedas | 10 milhões de moedas por mês: financiamento para desenvolvedores, construção ecológica, reservas |

### 5.4 Fundo de Operações Estratégicas (250 milhões de moedas)

| Subcategoria | Proporção | Quantidade | Objeto | Regra de Liberação |
|--------|------|------|------|--------|
| Troca de serviços por tokens | 50% | 125 milhões de moedas | Empresas de desenvolvimento, instituições de auditoria, escritórios de advocacia, operadores de verificação | 12 meses de penhasco + 36 meses lineares; 30-50% das taxas de serviço pagas na LIGHT |
| Financiamento estratégico | 30% | 75 milhões de peças | 2-3 Fundos ecológicos DePIN/Cosmos ou partes estratégicas da indústria de consumo | Pré-TGE foi vendido por US$ 0,03 a US$ 0,05 (arrecadando US$ 2,25 a 3,75 milhões); 12 meses de penhasco + 24 meses lineares; investidor único ≤ 2% do total |
| Contribuidores principais | 20% | 50 milhões de moedas | 3-5 patrocinadores/construtores principais | 12 meses de penhasco + 36 meses lineares; divulgado com base na avaliação trimestral de marcos; nenhuma venda durante o prazo |

**Requisitos do investidor estratégico:** Contribuições não financeiras (de fluxo de negócios, serviços de verificação, recursos de conformidade) devem ser fornecidas, e investidores puramente financeiros não são aceitos.

**Conformidade regulatória:** A venda pré-TGE adota isenção de via dupla Reg S (investidores fora dos EUA) + Reg D Rule 506(c) (investidores qualificados dos EUA).

**Regras de divulgação dos principais contribuidores:** Somente o valor total (50 milhões = 2% do valor total) e as regras de liberação são divulgados, e nomes pessoais e cotas individuais não são divulgados. Categorias de função divulgadas: Tecnologia/Investimento/Compliance/Comunidade.

### 5.5 Produção de mineração e plano de redução pela metade

**Derivação:** 2A = 1 bilhão → A = 500 milhões (Primeira Era). Lançamento diário = 500 milhões ÷ 730 = 684.932 peças ≈ 684.900/dia. Cada bloco = 684.932÷49.371 ≈ 13,87 LUZ.

**Observação:** O conjunto de recompensas para cada bloco é compartilhado por toda a rede, dos quais 5% são alocados para validadores (34.200/dia) e 95% são alocados para mineradores de nós leves (650.700/dia).

| Época | Tempo | Produção total | Lançamento diário | Conjunto de recompensas por bloco |
|------|------|---------|---------|------------|
| 1ª Era | 0-24 meses | 500 milhões | ≈684.900 | ≈13,87 LUZ |
| 2ª Era | 25-48 meses | 250 milhões de peças | ≈342.500 | ≈6,93 LUZ |
| A 3ª Era | 49-72 meses | 125 milhões de peças | ≈171.200 | ≈3,47 LUZ |
| A 4ª Era | 73-96 meses | 62,5 milhões de peças | ≈85.600 | ≈1,73 LUZ |
| A 5ª Era | 97-120 meses | 31,25 milhões de peças | ≈42.800 | ≈0,87 LUZ |

**Verificar:** 5+2,5+1,25+0,625+0,3125+… = 5×2 = 1 bilhão ✓. 97% concluídos nos primeiros 10 anos.

### 5.6 Modelo de referência de renda do usuário

| Tamanho da rede | Rendimento diário per capita | Renda mensal | Renda anual | Markup total (1,44x) renda mensal |
|--------|-----------|--------|--------|--------|
| 10.000 mineiros (estágio de semente) | ≈65,07 | ≈1.952 | ≈23.751 | ≈2.811 |
| 100.000 mineradores (estágio de crescimento) | ≈6,51 | ≈195,2 | ≈2.375 | ≈281,1 |
| 1 milhão de mineradores (período de escala) | ≈0,65 | ≈19,5 | ≈237,5 | ≈28,1 |

**Nível de parceiro (50 convites, 20% de participação, bônus total):**

| Escala de rede | Próprio (incluindo bônus) | Compartilhar convite | Diário abrangente | Mensal abrangente |
|---------|------------|---------|--------|--------|
| 10.000 mineiros | ≈93,7 | ≈650,7 | ≈744,4 | ≈22.332 |
| 100.000 mineiros | ≈9,37 | ≈65,07 | ≈74,44 | ≈2.233 |
| 1 milhão de mineiros | ≈0,94 | ≈6,51 | ≈7,45 | ≈223,4 |

### 5.7 Plano de crescimento de lançamento aéreo

**Modelo econômico:** Orçamento total do lançamento aéreo = usuários alvo alcançados × lançamento aéreo per capita × (1 + taxa de desperdício) = 100.000 × 150 LIGHT × 1,3 ≈ 19,5 milhões (tipo de aquisição) + 35,5 milhões (tipo ecológico) = **55 milhões** (representando 13,75% do fundo ecológico de 400 milhões).

| Tipo de lançamento aéreo | Condições de desencadeamento | Cota única | Orçamento |
|---------|---------|---------|------|
| Primeiro lançamento aéreo de mineração | Concluiu 4 horas de mineração efetiva pela primeira vez | 50 LUZ | 15 milhões de peças |
| Expansão geográfica | Usuários do mercado-alvo completam ZK-KYC | 100 LUZ | 10 milhões de peças |
| Aprenda a Ganhar | Módulo Educacional Completo + Questionário | 30 LUZ | 6 milhões de moedas |
| Primeira votação de governança | Primeira Participação na Votação | 20 LUZ | 3 milhões de moedas |
| Fornecimento de liquidez | Injeção de LP ≥$50 lock-up por 30 dias | 200 LUZ | 10 milhões de peças |
| Criação de conteúdo | Tutoriais/traduções verificadas pela comunidade | 50-200 LUZ | 6 milhões de peças |
| Canais de cooperação | Cadastro + primeira mineração através de parceiros | 80 LUZ | 5 milhões de peças |

**Verificação CAC:** 55 milhões de moedas × US$ 0,03 = US$ 1,65 milhão ÷ 30.000 mineradores ativos retidos = **US$ 55/pessoa** (faixa da indústria US$ 50-200, no limite inferior). Base acadêmica: Zheng (2023) "Operação Dumbo Drop: Airdrop ou não Airdrop para sucesso na oferta inicial de moedas?" prova que a taxa de retenção de airdrops vinculados a eventos é 3-5 vezes maior que a de airdrops puros.

**Antiabuso:** Impressão digital exclusiva do navegador + ZK-KYC; limitado a 1 reclamação por categoria e por endereço; Período de carência de 30 dias; reciclagem automática sem atividade na rede dentro de 30 dias após a reclamação.

### 5.8 Volante com motor duplo e pool de capital

Flywheel: Votação → Destruição do Vault LIGHT → Pagamento em USDC → Retorno de lucro → Recompra e destruição → Suporte de preço → Mais usuários.

Sistema dual-track: tesouraria estável (USDC, retenção de lucros) + tesouraria flexível (camada LIGHT, destruída ao investir e não fluindo para o mercado). As recompras são divididas usando TWAP, com uma única ordem ≤ 5% do volume médio diário de negociação.

### 5.9 Emissão e negociação de subtokens

O valor total da emissão = valor do investimento ÷ $1; o preço de troca é baseado no VWAP de 30 dias; toda a LIGHT obtida na troca será destruída; Serão distribuídos 50% dos apoiadores/30% airdrop/20% reserva operacional (bloqueado por 6 meses). O limite de dividendos para um único endereço é de 15%. Os subtokens são negociados no AMM on-chain, com um período de lock-in de 30 dias após a emissão, e serão marcados como “liquidados” após a retirada.

### 5.10 Liquidez Inicial e Descoberta de Preço

**Arranjo TGE (Evento de Geração de Token, evento de geração de token): **

| Projeto | Plano |
|------|------|
| Reserva de liquidez inicial | Dos 120 milhões de peças liberadas pelo fundo de desenvolvimento ecológico TGE, 72 milhões de peças (60%) foram alocadas e injetadas no pool de liquidez DEX |
| Ativos emparelhados | USDC (pool principal), USDT (pool auxiliar) |
| Lançamento aéreo | Os 48 milhões restantes (40%) serão usados ​​para lançamentos aéreos para usuários de sementes (ver Seção 5.7 Plano de lançamento aéreo) |
| Listado em bolsas | Listado pela primeira vez em bolsas descentralizadas (como Osmosis, JunoSwap) após TGE; candidatar-se à cotação em bolsas centralizadas a partir do 6º mês dependendo das condições de cumprimento |

**Mecanismo detalhado do leilão holandês:**

O leilão holandês é um método de precificação em que os preços diminuem de alto para baixo. Ao contrário dos leilões ingleses (onde os preços são licitados de baixo para cima), num leilão holandês o vendedor define um preço inicial alto e o preço diminui automaticamente ao longo do tempo até que o comprador submeta uma subscrição a um determinado preço. O primeiro preço pelo qual o valor total da assinatura atinge a meta é o preço final de abertura.

**Por que escolher um leilão holandês em vez de um leilão de preço fixo ou um leilão inglês:**

| Preços | Vantagens | Desvantagens | Aplicabilidade |
|--------|------|------|--------|
| Pré-venda com preço fixo | Simples | O preço é subjetivo, se for muito alto não vai vender, se for muito baixo será abocanhado por robôs | Não adequado (sem função de descoberta de preço) |
| Leilão britânico (licitação) | Descoberta de preço total | Os grandes compradores podem esperar estrategicamente e aumentar os preços; guerra do gás | Não adequado (a guerra do gás em cadeia exclui pequenos utilizadores) |
| **Leilão Holandês** | **Descoberta automática de preços; não é necessária licitação (sem guerra do gás); participação igualitária de grandes e pequenos compradores; anti-bot (mecanismo de redução de preços inibe naturalmente o front-running)** | O preço inicial e a taxa de desaceleração devem ser definidos de forma razoável | **Mais adequado (justo + eficiente + antimanipulação)** |

**Parâmetros específicos do leilão holandês LightDAO:**

| Parâmetros | Configurações | Descrição |
|------|------|------|
| Alvo do leilão | Tokens LIGHT (alocados dos 72 milhões liberados pelo fundo ecológico TGE) | USDC do leilão será injetado no cofre estável |
| Montante alvo de angariação de fundos | **US$ 15 milhões em USDC** | US$ 5 milhões → reserva mínima do tesouro estável; US$ 10 milhões → capital de investimento inicial |
| Preço inicial | $ 0,20 / LUZ | Superior ao preço de equilíbrio esperado, garantindo que não será perdido em segundos |
| Taxa de desaceleração | Diminuir 5% a cada hora | Começando em US$ 0,20, caindo para US$ 0,017 após cerca de 48 horas (se ninguém assinar) |
| Preço mínimo de reserva | $ 0,01/LUZ | Caso o preço de reserva seja reduzido e a meta ainda não seja atingida, o leilão será adiado por 24 horas ou o número de objetos será ajustado |
| Método de assinatura | O usuário envia "Estou disposto a comprar LIGHT equivalente a X USDC pelo preço atual" | Não é necessária licitação, o sistema liquidará de acordo com o preço final unificado (qualquer excesso será reembolsado sem compensação) |
| Limite superior de usuário único | Não mais que 5% do valor alvo da arrecadação de fundos (ou seja, US$ 750.000) | Impedir que um único comprador monopolize os chips iniciais |
| Requisitos KYC | Verificação Aprimorada (Residência Fiscal) | Requisitos de Conformidade |

**Destino dos fundos dos resultados do leilão:**

```
用户认购总额 $1,500万 USDC
    ├── $500万 → 稳定金库（最低储备，覆盖运营+应急）
    └── $1,000万 → 初始投资资本（稳定金库中可部署部分）

拍卖售出的LIGHT → 买家钱包（进入流通）
未售出的LIGHT（若有）→ 注入DEX流动性池
```

**Período de proteção para descoberta de preço:** Um disjuntor de flutuação de preço é configurado nas primeiras 72 horas após o TGE - se o preço da transação DEX se desviar em mais de ±50% do preço de abertura do leilão, a função de troca de subtokens será suspensa (mineração e transferências não serão afetadas) para evitar que especulações extremas interfiram na inicialização ecológica. O fusível será liberado automaticamente após 72 horas.

**Por que US$ 15 milhões em vez de menos:** O capital de investimento inicial de US$ 10 milhões precisa apoiar de 3 a 5 investimentos no primeiro ano (um único investimento é de US$ 2 a 5 milhões, consulte a escala do período de inicialização na Seção 9.1). Se apenas forem angariados 5 milhões de dólares (todos como reservas), não haverá capital de investimento distribuível no primeiro ano e o volante não arrancará. US$ 15 milhões = reserva de US$ 5 milhões + investimento de US$ 10 milhões, que é o equilíbrio mínimo viável entre “resultados de segurança” e “partida do volante”.

### 5.11 Mecanismo de deflação e resultados financeiros

**Volume de circulação = liberação de mineração + liberação ecológica + liberação de fundo estratégico − troca e destruição − destruição de gás − recompra e destruição. ** 850 milhões de moedas do cofre de investimentos nunca entraram em circulação. Limite superior teórico de circulação = 10+4+2,5 = **1,65 bilhão**.

| Condições de desencadeamento | Comportamento do sistema |
|--------|---------|
| Circulação ≤ 1,5 mil milhões de peças | Sinal de abrandamento (cenário de destruição extremamente baixo) |
| Volume de circulação ≤ 1,2 mil milhões de peças | Anúncio de alerta precoce, suspensão da destruição activa (cerca do 8.º ano do cenário base) |
| Volume de circulação ≤ mil milhões | Parada brusca, todas as destruições estão permanentemente fechadas (o cenário base é cerca dos anos 11-12) |

### 5.12 Mecanismo de estabilização de preços (espiral anti-morte)

**Princípio Básico:** LightDAO não interfere na descoberta diária de preços de mercado. O protocolo apenas ajusta seus parâmetros em cenários de queda extrema para reduzir o risco de cair em uma “espiral mortal”.

**Lógica de classificação:** Em diferentes ambientes voláteis, o mesmo declínio representa diferentes graus de anormalidade. Um declínio acentuado num mercado de baixa volatilidade é um sinal anormal mais forte e requer uma intervenção de maior intensidade; um declínio acentuado num mercado de alta volatilidade é relativamente comum e pode ser utilizada uma intervenção mais leve. Portanto, a intensidade da intervenção está positivamente relacionada com a anormalidade do sinal, em vez de depender apenas do valor absoluto do declínio.

**Fluxograma completo do mecanismo:**

| Situação do mercado | Volatilidade histórica de 30 dias | Condições de desencadeamento | Nível de sinal | Execução após trigger | Condições de recuperação |
|---------|----------|---------|---------|----------|---------|
| Baixa volatilidade | ≤30% | Queda acumulada de ≥40% durante 5 dias consecutivos | Nível I | A produção mineira caiu para 50%; a taxa de destruição aumentou de 20% para 35%; o período de divulgação dos ajustes dos parâmetros de risco foi reduzido de 72h para 12h; o comité sombra entrou no estado ativo (apenas o direito de suspensão temporária pode ser exercido nos termos da lei) | O preço ficou acima da média móvel de 30 dias e recuperou ≥80% do preço de gatilho, permanecendo assim por 10 dias consecutivos |
| Flutuação média | 30%-60% | Queda acumulada durante 7 dias consecutivos ≥ 50% | Nível II | A produção mineira caiu para 50%; a taxa de destruição aumentou de 20% para 30%; o período de publicidade foi reduzido para 24 horas; o comitê sombra entrou no estado ativo | O preço ficou acima da média móvel de 30 dias e recuperou ≥ 60% do preço de gatilho, permanecendo assim por 7 dias consecutivos |
| Alta volatilidade | 60%-100% | 10 dias consecutivos de declínio acumulado ≥55% | Nível III | A produção mineira caiu para 75%; a taxa de destruição aumentou de 20% para 25%; o período de publicidade foi reduzido para 48 horas; o comitê sombra entrou em espera | O preço ficou acima da média móvel de 30 dias e recuperou ≥40% do preço de gatilho, permanecendo assim por 5 dias consecutivos |
| Volatilidade extrema | >100% | Queda acumulada durante 10 dias consecutivos ≥ 65% | Nível III | Implementado de acordo com medidas de Nível III para elevada volatilidade | Implementado de acordo com condições de recuperação de nível III para volatilidade elevada |

**Condições de exclusão:** Somente quando o declínio do Bitcoin no mesmo período for inferior a 50% do declínio do LIGHT, o mecanismo acima pode ser acionado para descartar um colapso sistêmico do mercado (ou seja, se o BTC também despencar no mesmo período, é um evento geral do mercado e nenhuma intervenção separada é iniciada para o LIGHT).

**Descrição da lógica de recuperação:** Os requisitos e a duração do rebote diminuem com o nível de anormalidade: o Nível I requer a maior amplitude de rebote (80%) e o tempo de confirmação mais longo (10 dias), enquanto o Nível III requer requisitos relativamente mais baixos (40%/5 dias). Este arranjo está em linha com a lógica progressiva de “quanto mais forte o sinal anormal, mais forte é a intervenção e mais rigorosa é a confirmação da recuperação”.

**Fonte de dados de volatilidade e preço:** A volatilidade histórica de 30 dias e o declínio cumulativo são fornecidos pelo oráculo de preços na rede (consulte a Seção 4.10), com base no instantâneo TWAP do bloco diário de 00:00 UTC, e não dependem de nenhuma fonte de dados externa.

### 5.13 Teste de estresse de sustentabilidade de ganhos

| Cenários de estresse | E se | Respostas do protocolo | Resultados de pior caso |
|---------|---------|---------|---------|
| Todos os investimentos falharam | Todas as empresas investidas sofreram perdas ou não conseguiram sair | O fundo de seguros (10% dos lucros acumulados) cobre parte das perdas; reservas de tesouraria estáveis ​​(≥8 milhões de dólares) para manter as operações; novos investimentos são suspensos até que a comunidade reavalie | Os detentores de subtokens não podem receber dividendos; O preço da LIGHT está sob pressão, mas não volta a zero (as funções de mineração e governança continuam a operar) |
| O mercado despencou 80% | O preço da LIGHT caiu 80% em relação ao pico | Acionar o mecanismo espiral antimorte (nível II ou nível III); a produção mineira é reduzida em 50-75%; a taxa de destruição aumenta; o comité sombra pode suspender operações de alto risco | A renda dos usuários diminui, mas a rede continua a operar; o mecanismo é automaticamente levantado quando as condições de recuperação são satisfeitas |
| Principais proibições regulatórias do mercado | Um grande país proibiu completamente os ativos criptográficos | O espelho IPFS de comutação front-end permanece acessível; os ativos na rede e os direitos e interesses existentes dos usuários não são afetados; a disponibilidade de serviços de terceiros só é ajustada no âmbito da aplicação da lei; As operações da SPV nas Ilhas Cayman não estão sujeitas à jurisdição de um único país | O crescimento dos utilizadores na região estagnou; outras regiões do mundo não são afetadas |
| Perda em grande escala de usuários | Mineiros ativos caíram mais de 70% | O BaseReward é automaticamente redistribuído (o denominador diminui → a renda per capita dos usuários retidos aumenta); os incentivos aos convites são ponderados para atrair fluxos de retorno; os limiares de governação são temporariamente reduzidos (mecanismo dinâmico na secção 5.14) | A segurança da rede é reduzida, mas a cadeia não será interrompida (Tendermint BFT tolera <1/3 validadores estando offline) |
| Principais vulnerabilidades de contratos inteligentes | Vulnerabilidades exploráveis ​​encontradas em contratos principais | Suspensão emergencial de saídas de fundos com múltiplas assinaturas (bloqueio de tempo de 72 horas fornece janela de resposta); Iniciar votação de migração de contrato de backup (reparo de emergência de nível L4, ver Seção 4.12); Fundo de seguros cobre perdas de usuários | Alguns fundos podem ser danificados; As operações normais são retomadas após a conclusão da migração |

### 5.14 Mecanismo de equilíbrio intergeracional

Ajuste dinâmico do limite de governança: para cada 1 milhão de novos mineradores ativos cumulativos, o limite da proposta é automaticamente reduzido em 5% (limite inferior de 2.500 LIGHT).

> **[Terminologia neste capítulo]**
> **TGE** (Evento de Geração de Token): O momento em que um token é criado e distribuído pela primeira vez por meio de um contrato inteligente, geralmente acompanhado pelo estabelecimento de um pool de liquidez inicial, preços de leilão holandês e a primeira transação pública. Semelhante a um IPO em finanças tradicionais, mas não envolve listagem em bolsa de valores.
> **Halving** (Halving): Um mecanismo pelo qual a produção de mineração é automaticamente reduzida em 50% a cada período fixo (2 anos/730 dias para LightDAO). O objectivo é criar uma escassez progressiva - à medida que o tempo passa, cada vez menos oferta é adicionada e, se a procura não diminuir, os preços serão apoiados. O Bitcoin adota o halving a cada 4 anos.
> **Tesouro** (Tesouro): Reservas de tokens bloqueadas por contratos de múltiplas assinaturas, que só podem ser liberadas por meio de resoluções de governança. LightDAO tem dois tipos de cofres: cofres de investimento (que guardam LIGHT e são destruídos quando os investimentos são executados) e cofres estáveis ​​(que guardam USDC e são usados ​​para pagar contraprestações de investimento e despesas operacionais).
> **Deflação** (Deflação): O processo no qual a oferta total ou circulação de tokens continua a diminuir. LightDAO atinge a deflação por meio de quatro mecanismos: execução e destruição de investimentos, troca e destruição de subtokens, destruição de taxas de gás (50%) e recompra e destruição de lucros.
> **Espiral da Morte** (Espiral da Morte): Os preços dos tokens caem → a renda dos mineiros diminui → os mineiros desistem → a segurança/contribuição da rede diminui → maior perda de confiança → um ciclo vicioso em que os preços continuam a cair. O mecanismo de intervenção gradual na Secção 5.12 foi concebido para interromper este ciclo.
> **Sub-token** (Sub-token): certificado de reivindicação de distribuição de renda SPV emitido de acordo com as regras após a conclusão de cada investimento corporativo (como a aquisição de uma marca de café → token CAFE). Detenção de subtokens = detenção de qualificações para distribuição de lucros futuros e não representa direitos dos acionistas ou direitos de governança corporativa.
> **LP** (Provedor de Liquidez): Os participantes que injetam dois ativos de igual valor (como LIGHT+USDC) no pool de liquidez DEX ganham taxas de transação em troca. LP é a base para o funcionamento normal do DEX.
> **VWAP** (Preço Médio Ponderado por Volume): O preço dentro de um período de tempo é ponderado pelo volume de cada transação, refletindo o verdadeiro custo de transação do mercado. LightDAO usa VWAP de 30 dias como referência de preços para troca de subtokens.
> **CAC** (Custo de Aquisição de Cliente, custo de aquisição de usuário): O custo médio para adquirir um usuário ativo efetivo. O CAC alvo do programa de lançamento aéreo LightDAO é de US$ 55/mineradores ativos retidos (faixa da indústria de US$ 50-200).
> **wLIGHT** (Wrapped LIGHT, encapsulated LIGHT): tokens equivalentes a LIGHT emitidos em Ethereum ou Solana por meio de pontes de cadeia cruzada, e uma quantidade igual de LIGHT nativo é bloqueada pelo contrato de ponte como uma reserva 1:1. O objetivo é permitir que usuários que não sejam do ecossistema Cosmos obtenham e mantenham LIGHT.
> **Leilão Holandês** (Leilão Holandês): Um método de precificação em que o preço diminui de alto para baixo. O vendedor define um preço inicial alto e o preço diminui automaticamente com o tempo até que o comprador envie uma assinatura com um determinado preço. O primeiro preço pelo qual o valor total da assinatura atinge a meta é o preço final da transação. A vantagem é que não há necessidade de licitação (sem guerra de gás), compradores de todos os tamanhos são iguais e é naturalmente resistente à preempção do robô.

---

## Capítulo 6: Mecanismo de Governança

### 6.1 Modelo de votação bidimensional

Peso da moeda (incluindo reputação + bônus de nível, limite máximo total +40%) + número de endereços (1 endereço = 1 voto, endereços associados são mesclados). Os direitos de voto são válidos por 90 dias e podem ser ativados através da transferência de 5 LIGHTs. Bônus de reputação: Manter a moeda por 1 ano + 15 votos válidos → até +30%.

### 6.2 Taxa de aprovação dinâmica

Taxa mínima de aprovação = 50% + (50% - taxa real de votação). Maioria simples quando a taxa de votação for ≥50%.

### 6.3 Parâmetros da proposta

| Tipo | Margem | Taxa de votação simbólica | Taxa de votação de endereço | Taxa de aprovação | Atraso na execução |
|------|--------|-----------|-----------|--------|---------|
| Micro | US$ 100 | ≥15% | ≥20% | Dinâmico ≥55% | 24h |
| Tipo de aquisição | US$ 500 | ≥25% | ≥30% | Dinâmico ≥60% | 72h |
| Tipo de capital de risco | US$ 500 | ≥35% | ≥40% | Dinâmico ≥60% | 72h |
| Principal | US$ 1.000 | ≥45% | ≥50% | Dinâmico ≥66% | 72h |
| Emergência | US$ 2.000 | ≥50% | ≥60% | ≥75% | Não financiamento 6h/alto risco 1h; operações de capital ainda estão sujeitas a bloqueio de 72 horas |

### 6.4 Ciclo de vida da proposta

Qualificação de envio: ≥5.000 LIGHT + 30 dias consecutivos de penhor + depósito. Anúncio público 72h (revisado ≤ 2 vezes). A votação ocorre dentro de 7 dias (48h para fast track, ≤500.000 USDC). Veto resfriamento por 90 dias. A eficácia é atrasada por 24 horas.

**Descrição do limite:** 5.000 moedas no estágio inicial (10.000 mineradores) ≈ 77 dias de produção básica; nível de parceiro ≈ 7 dias. A governança será ativada no sétimo mês e os primeiros usuários terão tempo de acumulação suficiente.

### 6.5 Incentivos de votação

Existe um incentivo básico para participação (mesmo compartilhamento) e há um bônus adicional para julgamento correto (50% do pool de apostas). Aposte na faixa 5-500 LIGHT. Suprimir o efeito de rebanho: os oponentes ainda recebem incentivos básicos mesmo que estejam “no time errado”.

### 6.6 Recompensas e penalidades por sucesso ou fracasso

Falha de boa fé: reembolso de 50% do depósito + 30 dias de espera. Falha maliciosa (falsificação/repetição): valor total confiscado + banimento permanente. Prova de fraude: limitado a 5.000 LIGHT, penalidade de 40% do bônus de estabelecimento + 500 LIGHT.

### 6.7 Transparência Financeira

Dashboard em tempo real da cadeia + relatório financeiro trimestral + auditoria independente anual (a primeira auditoria deve ser concluída antes da TGE) + divulgação em tempo real das metas de investimento.

---

## Capítulo 7: Verificações e equilíbrios de poder e definição de funções

### 7.1 Guardião Inicial

As permissões são limitadas às informações do documento/formato/site oficial. Prazo ≤ 24 meses. Deve ser designado um tutor alternativo (impossibilitado de assinar por 30 dias consecutivos → assumido automaticamente). Incapacidade simultânea → Votação emergencial de 48h para nomeação de gestor temporário.

### 7.2 Roteiro de transferência de energia

| Palco | Tempo | Permissões | Aprovação de Investimento |
|------|------|------|---------|
| Período de criação | 0-6 meses | Guardião (não financeiro) | Guardião + assinatura múltipla da comunidade 3/5 |
| Período de transição | Julho-Dezembro | Guardian + contribuidor principal assinado em conjunto | Igual ao acima + contribuidor principal |
| Período de maturidade | 13-24 meses | Comitê de Governança 3/5 | Votação bidimensional regular |
| Período de autonomia | 25 meses + | Todos os titulares | Mesmo prazo de vencimento |

### 7.3 Comitê de Governança

O poder é dividido entre cinco pessoas (presidente rotativo/finanças/tecnologia/comunidade/chave), rodízio trimestral, e o mandato é de seis meses, podendo ser reeleito uma vez. A campanha promete 50.000 assinaturas conjuntas LIGHT + 100 endereços. A tomada de decisões envolve ≥3 pessoas e abrange ≥3 cargos.

**Descrição do limite:** 50.000 moedas na fase inicial ≈ 67 dias (2,2 meses) para parceiros; na fase de crescimento ≈ 672 dias (22 meses). A primeira eleição do comitê no 13º mês está disponível para os primeiros sócios.

### 7.4 Comitê Sombra

Suspensão temporária apenas para "violações/sanções/fraudes graves". Todos os votos devem ser ratificados dentro de 72 horas (oposição >60%→rejeitada). Rejeitado duas vezes consecutivas → automaticamente impeachment e dissolvido.

### 7.5—7.6 Verificação de campanha e plano principal

SimHash>80% desqualificação; O conteúdo da IA ​​deve ser complementado com explicação; 20% dos votos serão deduzidos para questões ausentes. Backup de fragmentos de chave + verificação de integridade trimestral + anúncio público de 7 dias + substituição de votação.

---

## Capítulo 8: Mecanismo de Confiança e Segurança

### 8.1 Cinco principais mecanismos de segurança

Time lock 72h (propostas emergenciais não estão isentas de operações de capital); assinatura múltipla 3/5; rodízio trimestral ≤ 2 sessões; Penalidade de 100% por fraude; todas as transações estão na cadeia.

### 8.2 Fundo de Seguro

**10%** dos lucros de investimentos bem-sucedidos são acumulados. As reivindicações devem ser relatadas de forma independente + DAO 66% a favor + único ≤ pool 20%. Fonte complementar: 30% da multa por falsificação. O posicionamento de "buffer parcial" não é proteção total.

### 8.3 Plano extremo

Supervisão cisne negro → IPFS + remoção de direitos de administrador; fraude → suspensão do comitê sombra (ratificação em 72h) + fundo de seguro + arbitragem SPV; espiral mortal → Mecanismo da Seção 5.12; vulnerabilidade contratual → suspensão de múltiplas assinaturas + votação de migração; validadores fazendo o mal coletivamente → tolerância BFT <1/3, se ultrapassada, a cadeia será suspensa + migração emergencial de votação.

---

## Capítulo 9: Operações de Investimento e Estratégias de Saída

### 9.1 Triagem e escala das metas de investimento

**Trajetória de crescimento fase a fase da escala de investimento (fórmula: excedente de tesouraria × 15% × preço LIGHT): **

| Palco | Preço LEVE | Limite único de transações no período inicial do cofre | Metas de adaptação | Benchmarking da indústria |
|------|----------|------------------|----------|----------|
| Período de arranque (Anos 1-2) | US$ 0,02—US$ 0,05 | US$ 2,55 milhões — US$ 6,37 milhões | Loja única/pequena rede, anjo redondo | Micro-PE |
| Fase de crescimento (Y3-5) | US$ 0,05—US$ 0,30 | US$ 6,37 milhões — US$ 38,25 milhões | Rede regional 30-200 lojas, rodada Semente-A | PE do Mercado Médio Inferior |
| Estágio de maturidade (Y5-8) | US$ 0,30—US$ 1,00 | US$ 38,25 milhões — US$ 127,5 milhões | Rede multinacional/média tecnologia, rodada B-C | PE de mercado médio |
| Período de escala (Y8+) | $ 1,00 + | US$ 127,5 milhões+ | Aquisições em grande escala, pré-IPO | PE em grande escala/VC em estágio de crescimento |

### 9.2 Processo de tomada de decisão de investimento

Descoberta do projeto (≥5.000 LIGHT) → due diligence independente → anúncio público 72h → votação bidimensional → execução 24/72h.

### 9.3 Saída e distribuição de lucros

Dividendo anual: **40%** detentores de subtokens / **30%** cofre estável / **20%** recompra LIGHT para destruição / **10%** fundo de seguro.
Renda de saída: **70%** Stable Vault / **30%** Recompra e Queima.

### 9.4 Disciplina de Investimento

| Regras | Conteúdo |
|------|------|
| Limite único de destruição | Cofre restante × 15% (inicial 850 milhões × 15% = 127,5 milhões de moedas) |
| Alvo único | ≤25% do valor total do cofre |
| Concentração da indústria | ≤40% da carteira |
| Concentração geográfica | ≤30% da carteira |
| Reservas de tesouraria estáveis ​​| US$ 5 milhões na TGE (leilão), atingindo US$ 8 milhões no 24º mês |
| Período de reflexão | 2 falhas consecutivas → 180 dias |

**Capacidade do cofre:** 850 milhões de peças × US$ 0,10 = US$ 85 milhões (capacidade total inicial); × US$ 0,30 = US$ 255 milhões; × US$ 1,00 = US$ 850 milhões. O limite de transação única de 15% torna o ritmo de investimento positivamente relacionado ao preço.

> **[Terminologia neste capítulo]**
> **EBITDA** (Lucro antes de juros, impostos, depreciação e amortização): indicador que mede a lucratividade das principais operações de uma empresa, eliminando a interferência da estrutura financeira (juros), da política tributária (impostos) e das escolhas contábeis (depreciação/amortização), facilitando comparações entre empresas e setores. Margem EBITDA = EBITDA ÷ lucro operacional.
> **DCF** (Fluxo de caixa descontado, método de fluxo de caixa descontado): método de avaliação que converte o fluxo de caixa futuro esperado da empresa em valor atual a uma determinada taxa de desconto. É adequado para empresas maduras com fluxo de caixa estável (como cadeias de consumo), mas não para empresas tecnológicas em fase inicial que ainda não são rentáveis.
> **IPO** (Oferta Pública Inicial): A primeira vez que uma empresa emite ações publicamente em uma bolsa de valores e é listada para negociação. Para a LightDAO, o IPO das empresas investidas é um dos principais caminhos de saída dos motores de crescimento.
> **Pré-IPO**: A última rodada de financiamento de capital privado antes da empresa ser oficialmente listada. Normalmente a avaliação está próxima do nível pós-IPO, o risco é menor do que nas rodadas anteriores, mas o múltiplo de retorno também é menor.
> **Execução TWAP** (Execução de preço médio ponderado pelo tempo): divida ordens de recompra de grandes quantidades em várias ordens de pequenas quantidades e execute-as uniformemente durante um período de tempo para evitar o impacto de uma única ordem grande no preço de mercado. LightDAO estipula que uma única recompra não deve exceder 5% do volume médio diário de negociação.

---

## Capítulo 10: Roteiro

| Fase | Tempo | Objetivos principais | Principais marcos | Pré-requisitos |
|------|------|---------|-----------|--------|
| Período de preparação | 4º trimestre de 2026 | Pessoa jurídica + equipe + recursos disponíveis | Registro de entidade Cayman/BVI concluído; parceiro técnico ou equipe de desenvolvimento assinado; intenção estratégica do investidor confirmada (2-3 empresas); capital inicial ≥ $ 150.000 em vigor | fundador determina método de divulgação de identidade; conclusão do BP e Pitch Deck |
| Período de desenvolvimento | 1º-2º trimestre de 2027 | Desenvolvimento de sistema central | Foram desenvolvidos 10 módulos de contratos inteligentes; O desenvolvimento do front-end do PWA foi concluído; 7 testnets verificadores foram implantados; o teste Alpha interno foi aprovado | Equipe de desenvolvimento instalada; documento de requisitos (especificações técnicas) finalizado |
| Período de auditoria e testes | 3º trimestre de 2027 | Verificação de segurança e conformidade | Divulgação de relatório de auditoria de segurança independente (≥1 instituição de topo); divulgação de carta de parecer de conformidade legal (MLM + lei de valores mobiliários); 50.000 testes de estresse simultâneos aprovados; taxa de falsos positivos do sistema anti-trapaça <2%; exercício de votação sobre governação concluído | Congelamento de desenvolvimento de contrato (Code Freeze); taxas de auditoria em vigor |
| TGE e rede principal online | 4º trimestre de 2027 | Emissão de token + lançamento da rede | Leilão holandês concluído (meta de US$ 15 milhões); mainnet online (≥10 validadores); plataforma de mineração aberta ao público; Pool de liquidez DEX estabelecido; lançamento aéreo de sementes emitido | Auditoria aprovada; validadores ≥7 (resultado final); implantação de contrato de leilão |
| Período de construção de crenças | 1º trimestre de 2028 (1º ao 3º mês após TGE) | 30.000-50.000 usuários iniciais | Mineiros ativos ultrapassaram 30.000; primeiro exercício de votação de governação; canal comunitário multilíngue estabelecido (inglês/chinês/espanhol/português/Filipinas); primeiro relatório mensal da comunidade divulgado | TGE concluído; equipe de operações comunitárias instalada |
| Período de âncora de valor | 2º-3º trimestre de 2028 (4º a 9º mês após TGE) | Primeiro investimento + governação do período de transição | Primeira proposta de investimento aprovada (a aprovação multiassinatura durante o período de génese aplica-se do 4º ao 6º mês; a aprovação conjunta durante o período transitório aplica-se a partir do 7º mês); a primeira entrega do SPV é concluída; os validadores estão abertos para eleição (a partir do 7º mês); é divulgado o primeiro relatório financeiro trimestral | tesouraria estável USDC≥$5 milhões; due diligence da meta de investimento é concluída |
| Período de maturidade da governação | 4º trimestre de 2028-1º trimestre de 2029 (10º a 15º mês após TGE) | Eleição do comitê + transição para descentralização | Primeira eleição do comitê de governança (13º mês); Entrando no prazo de vencimento (3/5 decisão do comitê); A ponte de cadeia cruzada wLIGHT fica online; O pedido de listagem CEX é enviado; Começa o plano de financiamento do desenvolvedor | Mineiros ativos ≥ 100.000; ≥ 100 endereços de candidatos conjuntos |
| Período de expansão ecológica | A partir do segundo trimestre de 2029 (16º mês + após TGE) | Replicação em larga escala | Os mineradores ativos ultrapassaram 200.000-500.000; 2-3 investimentos foram concluídos; a primeira verificação de repatriação de lucros; Recompra e destruição da LIGHT iniciadas | O comitê de governança está funcionando normalmente; o modelo de investimento foi verificado |
| Período de operação maduro | A partir do quarto trimestre de 2029 (25º mês + após TGE) | Rotação do volante + autonomia total | Entrada no período de autonomia (grandes propostas de todos os titulares); implantação cumulativa da carteira de investimentos ≥ US$ 30 milhões; dados de deflação são publicamente verificáveis ​​| A governança é completamente descentralizada |

**Princípios de design do roteiro:**

- **Auditoria antes da TGE:** Os tokens nunca serão emitidos sem a conclusão de uma auditoria de segurança independente. Esta é a garantia básica para a segurança dos fundos dos usuários.
- **Os verificadores vêm antes dos usuários:** Quando a rede principal ficar online, haverá ≥10 verificadores (tolerância a falhas BFT f≥3), garantindo que a rede não será desligada devido a um único ponto de falha.
- **O investimento precede a expansão:** Somente depois que o primeiro investimento for bem-sucedido e gerar retorno de lucro verificável é que poderemos iniciar uma expansão em grande escala. Evite colocar a carroça na frente dos bois “circulando as pessoas primeiro e encontrando os projetos depois”.
- **Time Buffer:** Reserve 20-30% de buffer de tempo para cada estágio. O desenvolvimento tecnológico, as reparações de auditoria e os processos legais podem todos exceder as expectativas, e o roteiro não deve ser um “cenário muito optimista”.

**Relação com a data de lançamento do white paper (4 de agosto de 2026):** O white paper foi lançado em agosto de 2026 como uma declaração pública da visão e design técnico do projeto. A implementação real começará no quarto trimestre de 2026 (período preparatório), e a meta do TGE é o quarto trimestre de 2027. O intervalo de aproximadamente 14 meses entre o lançamento do white paper e o TGE foi usado para formação de equipe, desenvolvimento, auditoria e preparação de conformidade.

---

## Capítulo 11: Cultura Comunitária e Ecologia do Desenvolvedor

### 11.1 Quatro Valores

- **A transparência é melhor que a perfeição** - É melhor revelar as imperfeições do que esconder a perfeição. Todos os fluxos de tesouraria, decisões de investimento e votos de governança estão permanentemente disponíveis na cadeia.
- **Gradual é melhor que radical** - Dê pequenos passos e continue iterando. O primeiro investimento começará entre US$ 2 e 5 milhões e a escala será ampliada após a verificação do modelo.
- **Responsabilidades são melhores que direitos** - Direitos e obrigações são iguais. Os membros do comitê de governança devem prometer 50.000 LIGHT e divulgar sua agenda política. Caso não cumpram suas funções, serão multados.
- **Diversidade é melhor que homogeneidade** - Vozes diferentes são a imunidade do sistema. A votação bidimensional (moeda + endereço) garante que tanto as baleias quanto os investidores de varejo tenham uma palavra a dizer.

### 11.2 Sistema de júri

| Dimensões | Regras |
|------|------|
| Composição | Selecione aleatoriamente 12 usuários que possuam ≥10.000 LIGHTs e não tenham registros de violação |
| Prazo | 30 dias, será sorteado novamente após o vencimento |
| Responsabilidades | Ouça reclamações sobre penalidades anti-trapaça, acusações de fraude em propostas e disputas comunitárias |
| Processo | Usuários punidos podem enviar provas em até 72 horas; o júri deve dar o veredicto em 48 horas |
| Padrões de julgamento | ≥8 em cada 12 pessoas (maioria de 2/3) devem concordar em manter ou revogar a pena |
| Evitar | Substituição automática de jurados que tenham relação de convite com as partes ou estejam na mesma faixa de IP |
| Remuneração | Receber subsídio diário de serviço do júri de 5 LIGHT durante o período (desembolsado pelo fundo ecológico) |

### 11.3 Plano Ecológico do Desenvolvedor

| Módulo | Conteúdo | Fontes de financiamento | Como se inscrever |
|------|------|---------|---------|
| Financiamento para desenvolvedores (subsídios) | Para equipes que criam dApps, ferramentas e infraestrutura na cadeia LightDAO, uma doação única de US$ 5 a 500.000 equivalente ao LIGHT | Fundo de Desenvolvimento Ecológico (Liberação Linear Fase 2) | Envie uma proposta → Avaliação do responsável pela revisão técnica → Votação de governança (processo de microproposta) |
| SDK e API | Fornece interfaces JavaScript/TypeScript SDK, REST API e WebSocket para reduzir o limite para desenvolvimento de terceiros | Oficial de revisão técnica lidera desenvolvimento | Código aberto, público no GitHub |
| Hackatona | Um hackathon online é realizado trimestralmente, com uma premiação de US$ 100.000 equivalente ao LIGHT | Fundo de Desenvolvimento Ecológico | Inscrições abertas, sem limite |
| Recompensa de insetos | Programa principal de recompensas por bugs, recompensa de US$ 1.000 a US$ 50.000 por uma única vulnerabilidade válida (classificada de acordo com a gravidade) | Fundo de Seguros + Fundo de Desenvolvimento Ecológico | Envie através do Immunefi ou plataforma autoconstruída |
| Mercado de contratos CosmWasm | Incentive terceiros a implantar contratos inteligentes e 20% da receita das taxas de gás será devolvida ao tesouro ecológico para apoiar os desenvolvedores | Distribuição da taxa de gás (ver secção 4.5) | Automático, sem necessidade de aplicação |

### 11.4 Estratégia multilíngue e de localização

| Dimensões | Planejamento |
|------|------|
| Linguagem da plataforma | Inicialmente oferece suporte a inglês, chinês, espanhol, português e filipino; Francês, árabe, suaíli e indonésio serão adicionados a partir do 6º mês |
| Linguagem de governança | Propostas e plataformas de campanha são aceitas em qualquer idioma, e o sistema oferece tradução automática + revisão de manual comunitário |
| Operações Comunitárias | Estabeleça canais comunitários independentes (Discord/Telegram) por idioma, e cada canal seja equipado com voluntários de ligação com a comunidade localizados |
| Tradução de Documentos | Os white papers e documentos principais são preenchidos por voluntários de tradução da comunidade, e as contribuições de tradução estão incluídas no bônus de comportamento "Contribuição de conteúdo" (5%) |
| Financiamento de localização | 10% (40 milhões de moedas) do fundo de desenvolvimento ecológico são reservados para a construção de comunidades de localização e incentivos à tradução |

---

## Capítulo 12: Equipe e Consultores

### 12.1 Definição da função principal

| Função | Responsabilidades | Requisitos de antecedentes | Métodos de divulgação |
|------|------|---------|---------|
| Guardião Inicial/Patrocinador do Projeto | Implantar contratos iniciais, manter documentos e coordenar operações iniciais | ≥ 3 anos de experiência na indústria de blockchain, com implantação de contratos inteligentes ou registros de operação de protocolo DeFi | Divulgue sua verdadeira identidade perante a TGE ou forneça um relatório de verificação de identidade de terceiros (como assinatura notarial + verificação de mensagem em cadeia) |
| Líder técnico | Projeto de arquitetura de contrato, gerenciamento de equipe de desenvolvimento, docking de auditoria | Experiência de desenvolvimento Cosmos SDK/CosmWasm, registro de implantação da cadeia de produção | Igual ao acima |
| Responsável pelo investimento | Triagem de alvos, coordenação de devida diligência, estabelecimento de SPV, gestão de saídas | Experiência na indústria de private equity/capital de risco, com casos de saída concluídos | Igual ao acima |
| Consultor de compliance | Desenho de estrutura jurídica, docking regulatório, consultoria de conformidade MLM | Advogado com qualificações nos EUA/UE/Cayman | Nome do escritório de advocacia público (nome pessoal não será divulgado a menos que eu concorde) |

### 12.2 Conselho Consultivo

- Composto por 3 a 5 consultores independentes, cobrindo: tecnologia DePIN, conformidade de investimentos transfronteiriços, operações comunitárias e indústrias de consumo;
- Os consultores recebem remuneração de consultoria na forma de tokens LIGHT (desembolsados ​​da parte “Service Token Exchange” do fundo operacional estratégico), e a posição fica bloqueada por 12 meses;
- A lista de consultores é tornada pública antes da TGE e está aberta a consultas comunitárias (reunião descentralizada de consulta de texto, ver Secção 7.5);
- Os Conselheiros não poderão atuar simultaneamente como membros do Comitê de Governança (segregação de conflitos de interesses).

### 12.3 Compromisso e restrições da equipe

| Restrições | Regras |
|------|------|
| Bloqueio de token | LIGHT (incluindo alocação estratégica de fundos operacionais) detidos pela equipe principal deve ser bloqueado por 12 meses e liberado linearmente por 36 meses após o desbloqueio |
| Restrições de vendas | O tutor inicial não está autorizado a vender LIGHT obtido por qualquer canal (incluindo airdrops, recompensas e compensações) durante o mandato (≤24 meses) |
| Conflito de interesses | Os conflitos de interesses dos membros da equipe devem ser totalmente divulgados no momento da nomeação (se possuem outros tokens DAO, se estão relacionados a potenciais alvos de investimento) |
| Consequências da não divulgação | Assim que for verificada a não divulgação de conflito de interesses, você será permanentemente banido de participar da governança e 50% dos tokens desbloqueados serão confiscados ao fundo de seguros |
| Mecanismo de substituição | Quando uma função central sai ou fica incapacitada, o comitê de governança (tutor inicial + tutor alternativo antes do estabelecimento) designará um sucessor, que deverá ser anunciado publicamente pela comunidade por 72 horas sem objeção |

### 12.4 Remuneração do contribuidor principal (20% do fundo operacional estratégico)

- Valor total: 50 milhões de LIGHTs (representando 2% do valor total)
- Número de pessoas abrangidas: 3-5 pessoas
- Regras de lançamento: penhasco de dezembro + 36 meses lineares (ou seja, aproximadamente 1,157 milhão de moedas serão lançadas todos os meses a partir do 13º mês)
- Vinculação do marco: A cada trimestre, o comitê de governança (responsável inicial + terceiro independente antes do estabelecimento) confirma que o marco foi alcançado antes que a cota trimestral possa ser liberada.
- Regras de divulgação: apenas o valor total e as regras de liberação são divulgados, e nomes pessoais e cotas individuais não são divulgados (para proteger a privacidade e, ao mesmo tempo, o valor total pode ser verificado através do endereço de assinatura múltipla na cadeia que o valor total não é excedido)

---

## Capítulo 13: Aviso de Risco e Isenção de Responsabilidade

### 13.1 Aviso de risco

| Tipo de risco | Descrição | Medidas de mitigação |
|--------|------|--------|
| Risco de Mercado | Os preços da LIGHT podem flutuar significativamente e os preços históricos não representam desempenho futuro. TGE tem liquidez inicial limitada e preços podem oscilar violentamente | Preço justo do leilão holandês; ±50% dos disjuntores 72 horas após TGE; mecanismo de intervenção de quatro níveis da espiral anti-morte |
| Risco do Projeto | O objectivo de investimento pode sofrer perdas, o projecto de capital de risco pode falhar e todo o capital pode ser perdido. A taxa média histórica de insucesso da indústria de PE/VC é de cerca de 50-70% (negócio único) | Descentralização dual-engine (70% de fluxo de caixa + 30% de crescimento); meta única ≤ 25%; indústria ≤ 40%; região ≤ 30%; Provisão de 10% para fundos de seguros |
| Riscos técnicos | Os contratos inteligentes podem ter vulnerabilidades não descobertas; a compatibilidade do navegador pode afetar a experiência de mineração; pontes entre cadeias podem ser atacadas | Auditoria independente + verificação formal perante a TGE; Recompensa de insetos de US$ 1 mil a US$ 50 mil; Bloqueio de horário de 72 horas; mecanismo de suspensão com múltiplas assinaturas |
| Riscos regulatórios | As políticas regulatórias em vários países e regiões podem mudar, o que pode resultar em funções limitadas ou na incapacidade de participação de usuários em regiões específicas | Estrutura Cayman SPV; verificação zero padrão (a verificação é realizada por um terceiro licenciado em seu serviço); o espelho IPFS frontal é resistente à censura; não comercializado para países específicos |
| Risco de liquidez | O subtoken pode não ter profundidade de negociação suficiente no estágio inicial; LIGHT pode enfrentar pressão de venda na fase inicial da TGE | A liquidez inicial do subtoken AMM (6% da emissão); Período de bloqueio de transferência de 30 dias; Equipe/investidor penhasco de 12 meses + linear de 36 meses |
| Risco de diluição | À medida que o número de mineiros activos aumenta, a receita mineira per capita será naturalmente diluída (o denominador BaseReward aumenta) | Intenção do design: os primeiros participantes assumem riscos mais elevados para obter retornos mais elevados; usuários posteriores podem acelerar a acumulação por meio do compartilhamento de convites; o limite de governança é reduzido dinamicamente |
| Risco operacional | A operação e gestão da empresa investida podem não corresponder às expectativas; As operações da SPV contam com diretores terceirizados; a equipe de investimento pode estar perdida | Restrições estatutárias da SPV + diretores independentes; DAO pode votar para substituir diretores; Cláusulas de arbitragem SIAC/ICC; seguro de pessoas-chave (em exploração) |
| Riscos de pontes entre cadeias | A ponte cross-chain wLIGHT é operada por terceiros, e as lacunas no contrato da ponte podem levar a perdas de ativos (história, as pontes cross-chain são a maior fonte individual de perdas) | Auditoria independente antes da ponte entrar em operação; os ativos da ponte não excedem 5% da oferta total; divulgação de riscos; os usuários podem optar por usar apenas a cadeia nativa |
| Risco do validador | Os validadores ficando off-line coletivamente ou cometendo o mal podem fazer com que a cadeia suspenda a produção de blocos e todas as operações do usuário (mineração, votação, transferências) fiquem temporariamente indisponíveis | Tendermint BFT tolera <1/3 do mal; validadores ≥ 21 (f=6); Pena cortante; mecanismo de votação de migração de emergência |

### 13.2 Isenção de responsabilidade

- LIGHT e subtokens não são títulos, não possuem valor intrínseco e o preço pode voltar a zero. Este white paper não constitui qualquer forma de documento de emissão de valores mobiliários, oferta de investimento ou consultoria de investimento.
- A distribuição de rendimentos do contrato depende do desempenho operacional real dos ativos subjacentes, e os dados históricos não representam rendimentos futuros. Quaisquer descrições de retornos de investimento são estimativas prospectivas e não promessas.
- O usuário deverá arcar com todos os prejuízos causados ​​pela perda ou vazamento da chave privada, e o contrato não prevê serviços de recuperação. Usar uma carteira Tier 1 (Passkey) ou Tier 2 (Recuperação Social) reduz esse risco, mas não o elimina.
- Este acordo está aberto a usuários de todo o mundo (sujeito às leis e regulamentos aplicáveis). Os usuários devem confirmar a atitude legal em relação aos ativos criptografados, organizações DAO e certificados de renda SPV em suas jurisdições e garantir que sua participação seja legal e compatível.
- As declarações prospectivas neste white paper (incluindo roteiros, modelos de receita, estimativas de deflação, previsões de escala de investimento) são previsões baseadas em suposições atuais, e os resultados reais podem divergir significativamente devido ao mercado, tecnologia, regulamentação, execução da equipe e outros fatores.
- Os incentivos por convite são um mecanismo de partilha de nível único e não constituem marketing multinível ou esquemas de pirâmide. No entanto, os usuários ainda devem confirmar a atitude legal em relação às recompensas por indicação em sua jurisdição.
- A idade mínima para participar do ecossistema LightDAO é 18 anos (ou a maioridade legal em sua jurisdição, o que for maior). Os menores não estão autorizados a participar na mineração, governação ou investimento.

---

## Apêndice A: Tabela de resumo dos principais parâmetros

| Categoria | Parâmetro | Valor |
|------|------|------|
| Emissão | Montante total | 2,5 bilhões de peças, nunca mais emissão |
| Emissão | Mineração | 40% = 1 bilhão de moedas |
| Emissão | Cofre de Investimento | 34% = 850 milhões de moedas |
| Emissão | Fundo Ecológico | 16% = 400 milhões de peças |
| Emissão | Operações Estratégicas | 10% = 250 milhões de moedas (serviço 50%/financiamento 30%/contribuintes 20%) |
| Emissão | Ciclo de redução pela metade | A cada 2 anos |
| Emissão | Lançamento do Primeiro Dia da Era | ≈684.900 (mineradores 95% = 650.700, validadores 5% = 34.200) |
| Emissão | Conjunto de recompensas por bloco | ≈13,87 LUZ |
| Mineração | Peso da contribuição | Largura de banda 40%/sessão 30%/verificação 20%/estabilidade 10% |
| Mineração | Bônus total | 1,44 vezes |
| Convite | Evangelista/Embaixador/Parceiro | 3 pessoas 10%+100L/10 pessoas 15%+500L+5%/50 pessoas 20%+2500L+10% |
| Comportamento | Quatro itens × 5% | Limite superior 20% |
| Taxa de gás | Mecanismo de preços | Ancoragem equivalente em USD, convertida automaticamente em quantidade LIGHT pelo oráculo a cada 24 horas |
| Taxa de gás | Transferência normal | Equivalente a $ 0,001 (@ $ 0,05 = 0,02 LUZ) |
| Taxa de gás | Votação sobre governança | Equivalente a $ 0,005 (@ $ 0,05 = 0,10 LUZ) |
| Taxa de gás | Regras de distribuição | 50% destruição / 30% validadores / 20% tesouro ecológico |
| Deflação | Desaceleração/alerta antecipado/resultados | ≤1,5 mil milhões/≤1,2 mil milhões/≤1 mil milhões (volume de circulação) |
| Deflação | Limite superior teórico | 1,65 mil milhões (10+4+2,5, 850 milhões no tesouro nunca serão circulados) |
| Governança | Limite da proposta | ≥5.000 LIGHT + 30 dias de piquetagem |
| Governança | Estacamento do Comitê | 50.000 LUZ + 100 Endereços |
| GOVERNANÇA | JÚRI | 10.000 LUZ |
| Governança | Apostas | 5—500 LUZ |
| Governança | Bônus de reputação | 1 ano +15 votos → +30% (cap total +40%) |
| Investimento | Limite único | Cofre restante × 15% (127,5 milhões de moedas iniciais) |
| Investimento | Linha de base implantável | 850 milhões × US$ 0,15 × 75% = US$ 95,63 milhões ≈ US$ 100 milhões |
| Investimento | Distribuição de lucros (anual) | 40/30/20/10 |
| Investimento | Distribuição de lucros (saída) | 70/30 |
| Leilão | Alvo | US$ 15 milhões (US$ 5 milhões de reserva + US$ 10 milhões de capital investido) |
| Reservas | Tesouraria Estável | TGE $ 5 milhões → Mês 24 $ 8 milhões |
| Seguros | Lucro | Lucro 10% |
| Lançamento aéreo | Orçamento total | 55 milhões (fundo ecológico 13,75%), CAC≈$55/usuário retido |
| Validadores | Inicial/Cap | 21 (mínimo 10) / 100 |
| Validador | Participação mínima | 500.000 LUZ |
| Verificador | Resultado final da TGE | ≥7, caso contrário não será permitido ficar online |

---

## Apêndice B: Derivação numérica e verificação

### B.1 Produção de mineração

2A=1 bilhão→A=500 milhões. Liberação diária = 500 milhões ÷ 730 = 684.932 ≈ 684.900. Pool de mineração=684.932×95%=650.685≈650.700. Verificadores=684.932×5%=34.247≈34.200. Cada bloco=684.932÷49.371≈13,87. Verificação: 684.932×730=499.999.960≈500 milhões ✓

### B.2 Limite de acessibilidade de governança

Referência de 100.000 mineradores (6,51/dia, parceiro 74,44/dia): proposta 5.000→768 dias/67 dias; comitê 50.000→7.684 dias (21 anos)/672 dias (22 meses); júri 10.000→1.537 dias (4,2 anos)/134 dias (4,5 meses); aposta 500→77 dias/6,7 dias.

Período inicial (10.000 mineradores, 65,07/dia, parceiros 744,4/dia): proposta → 77 dias (2,5 meses) / 6,7 dias; comitê → 768 dias (25 meses) / 67 dias (2,2 meses); júri → 154 dias (5 meses) / 13,4 dias.

### B.3 Cronograma de Deflação

Volume de circulação = mineração + ecologia + estratégia (vested) − troca − gás − recompra. 850 milhões do tesouro nunca serão circulados.

| Ano | Mineração Cumulativa | Ecologia | Estratégia | Troca | Gás | Recompra | Circulação |
|----|--------|------|------|------|-----|------|--------|
| 1 | 2,50 | 2,80 | 0 | 0 | 0,01 | 0 | ≈5,29 |
| 2 | 5h00 | 4h00 | 0,83 | 0,05 | 0,02 | 0 | ≈9,76 |
| 3 | 6,25 | 4h00 | 1,67 | 0,20 | 0,03 | 0,05 | ≈11,64 |
| 4 | 7,50 | 4h00 | 2,50 | 0,45 | 0,04 | 0,20 | ≈13,31 (pico) |
| 5 | 8.13 | 4h00 | 2,50 | 0,80 | 0,05 | 0,50 | ≈13,28 |
| 6 | 8,75 | 4h00 | 2,50 | 1,20 | 0,06 | 0,90 | ≈13.09 |
| 7 | 9.06 | 4h00 | 2,50 | 1,60 | 0,07 | 1,40 | ≈12,49 |
| 8 | 9,38 | 4h00 | 2,50 | 2h00 | 0,08 | 1,90 | ≈11,89 |
| 9 | 9,53 | 4h00 | 2,50 | 2,40 | 0,09 | 2h30 | ≈11,24 |
| 10 | 9,69 | 4h00 | 2,50 | 2,80 | 0,10 | 2,70 | ≈10,59 |
| 11 | 9,77 | 4h00 | 2,50 | 3.10 | 0,11 | 3h00 | ≈10.06 |
| 12 | 9,84 | 4h00 | 2,50 | 3,40 | 0,12 | 3h30 | ≈9,52 |

Conclusão: O pico Y4≈1,331 bilhão; a linha de alerta de 1,2 mil milhões é tocada pelo Y8; o resultado final de mil milhões é atingido pelo ano 2011-12; a linha de desaceleração de 1,5 mil milhões é apenas um cenário de destruição extremamente baixa.

---

## Apêndice C: Registro de correção de auditoria (36 itens no total)

Contém 22 itens originais (L1-5, A1-4, D1-4, M1-8, G1-3) + 7 itens de arquitetura técnica (T1-7) + 7 itens de otimização de modelo econômico nesta rodada:

| Número | Correção |
|------|------|
| E-1 | Montante total 2,1 mil milhões → 2,5 mil milhões (impulsionado por restrições de capacidade de investimento) |
| E-2 | Dotação 50/30/20→40/34/16/10 (10% dos novos fundos operacionais estratégicos) |
| E-3 | Leilão holandês US$ 10 milhões→US$ 15 milhões (capital de investimento inicial US$ 5 milhões→US$ 10 milhões) |
| E-4 | Novo plano de crescimento de lançamento aéreo de 5,7 seções (55 milhões de peças, CAC US$ 55/pessoa) |
| E-5 | Os verificadores são lançados em etapas (Testnet 7→TGE mínimo 10/Target 21→Open 100) |
| E-6 | Ajustamento da linha de desencadeamento da deflação (14/12/10 → 15/12/10, adaptado ao limite de circulação de 1,65 mil milhões) |
| E-7 | Substituir todas as citações externas por fontes verificáveis ​​(remover artigos SSRN não verificáveis) |

---

## Apêndice D: Índice rápido de termos

Uma explicação completa de cada termo é anotada no bloco de comentários [Termos neste capítulo] no final do capítulo onde aparece pela primeira vez. Este índice lista todos os termos e seus capítulos em ordem alfabética para navegação rápida.

| Terminologia | Capítulo Definição |
|------|------------|
| AMM (Formador de Mercado Automatizado) | Capítulo 4 |
| BFT (tolerância a falhas bizantinas) | Capítulo 4 |
| CAC (Custo de Aquisição de Clientes) | Capítulo 5 |
| CEX (Câmbio Centralizado) | Capítulo 4 |
| Cosmos SDK | Capítulo 4 |
| CosmWasm | Capítulo 4 |
| DAO (Organização Autônoma Descentralizada) | Capítulo 2 |
| DCF (Método de Fluxo de Caixa Descontado) | Capítulo 9 |
| DePIN (Rede Descentralizada de Infraestrutura Física) | Capítulo 2 |
| DEX (Bolsa Descentralizada) | Capítulo 4 |
| EBITDA (lucro antes de juros, impostos, depreciação e amortização) | Capítulo 9 |
| Taxa de gás | Capítulo 4 |
| IBC (protocolo de comunicação entre cadeias) | Capítulo 3 |
| IPFS (sistema de arquivos interplanetários) | Capítulo 4 |
| KYC (Conheça Seu Cliente) | Capítulo 3 |
| LUZ (token nativo) | Capítulo 4 |
| LP (Provedor de Liquidez) | Capítulo 5 |
| Lower Middle Market PE (Downstream Middle Market Private Equity) | Capítulo 2 |
| Árvore Merkel | Capítulo 4 |
| MiFID II (Diretiva II dos Mercados de Instrumentos Financeiros da UE) | Capítulo 3 |
| MLM (Marketing Multinível) | Capítulo 3 |
| PII (informações de identificação pessoal) | Capítulo 3 |
| PoC (Prova de Contribuição) | Capítulo 4 |
| PoS (Prova de Participação) | Capítulo 4 |
| PoW (Prova de Trabalho) | Capítulo 4 |
| Pré-IPO | Capítulo 9 |
| PWA (Aplicativo Web Progressivo) | Capítulo 4 |
| Reg D / Reg S (Regulamento D/S da Lei de Valores Mobiliários dos EUA) | Capítulo 3 |
| Cortando | Capítulo 4 |
| SPV (veículo para fins especiais) | Capítulo 2 |
| TGE (Evento de Geração de Token) | Capítulo 5 |
| TWAP (Preço Médio Ponderado no Tempo) | Capítulo 4 |
| Execução TWAP (Ordens de Recompra e Split) | Capítulo 9 |
| VWAP (Preço Médio Ponderado por Volume) | Capítulo 5 |
| wLIGHT (LUZ encapsulada) | Capítulo 5 |
| ZK-KYC (KYC à prova de conhecimento zero) | Capítulo 3 |
| Subtoken | Capítulo 5 |
| Espiral da Morte | Capítulo 5 |
| Redução pela metade | Capítulo 5 |
| Tesouro (Tesouro) | Capítulo 5 |
| Leilão holandês | Capítulo 5 |
| Oráculo | Capítulo 4 |

---

**O artigo completo termina**

**Declaração de direitos autorais:** Este documento é um documento comunitário de código aberto e pode ser reproduzido livremente, mas o conteúdo completo deve ser mantido.

---

# Apêndice: Parâmetros e endereços verificados da Mainnet (V2.4 ativo)

## A. §4.5 Parâmetros Econômicos Medidos do Gás
- fórmula do preço mínimo do gás: `(TransferUsdTarget / UsdPerLight) × 10 ^ 6 / RefTransferGas`; TransferUsdTarget atual=$0,001, UsdPerLight=$0,05, RefTransferGas=100000 → **0,2 ulight/gas**
- Medição de distribuição (taxa total 300.000 ulight): destruição 150.000 (50%)/tesouraria 60.000(20%)/verificador 90.000(30%), correspondência exata
- Endereço de destruição: `wasm1aeaty43lrlt9rmkyxujkkfuddnsfye6az4htcu` (endereço morto determinístico)
- Tesouro: contrato `treasury_multisig` (3/5 multi-assinatura; a consulta `signers` na cadeia retorna 5 signatários, o limite em si não está na interface de consulta)

## B. Endereço do contrato principal
Veja o repositório `docs/MAINNET_STATUS.md` (light_token/mining_reward/governance/treasury_multisig/oracle_twap/vesting e outros 10 contratos).

## C. Eliminação de denominação (participação) legada
incompatibilidade de gênese mint_denom=stake foi zerada e a emissão adicional foi interrompida; a participação existente (aproximadamente 2,56e11 micro unidades) fica sem propósito, e o plano de alienação (troca/destruição) está pendente de propostas de governação e não afectará o modelo económico ulight.

## D. §4.4 aquisição de direitos ao vivo
Vault 250.000.000 LIGHT, 3 horários independentes: 75M (cliff 0)/ 100M (cliff 1 ano)/ 75M (cliff 2 anos), já na cadeia.

## E. Práticas de segurança
- A rede principal é atualizada para governança x/upgrade + alta coordenação de todos os nós no mesmo bloco + watchdog de troca automática, executado após o ensaio ponta a ponta da rede de teste
- Sementes de chave de acesso armazenam apenas texto cifrado; Os fragmentos de Shamir não os armazenam localmente.
- Limite 5 de envio de raiz de mineração de contrato (limite de medição real = 5 para cada evento `submit_root` na cadeia; atualmente 5 contas autorizadas estão assinando e 7 assentos são o alvo do design); para anti-bruxa/anti-trapaça, consulte §4.8
