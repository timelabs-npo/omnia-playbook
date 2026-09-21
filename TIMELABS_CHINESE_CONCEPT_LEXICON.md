# TIMELABS_CHINESE_CONCEPT_LEXICON

## Notes
- Purpose: ontology expansion, not literal translation.
- S/T = Simplified / Traditional variants where materially distinct.

| Timelabs term | English equivalents | Simplified Chinese | Traditional Chinese | Chinese technical synonyms | Literal translation | Technical meaning in Chinese usage | False friends / pitfalls | Example source tradition |
|---|---|---|---|---|---|---|---|---|
| Intent | intent, objective policy | 意图 | 意圖 | 意图驱动, 业务意图 | intention | high-level target compiled to policy/action plans in network systems | 意图 ≠ user wish text only; often machine-compilable goal | 意图驱动网络白皮书 traditions |
| Constraint | invariant, bound | 约束 | 約束 | 约束条件, 边界条件 | constraint | formal boundary on feasible state/action set | often merged with policy in English docs; Chinese often separates | 控制理论/优化 literature |
| Policy | policy rule set | 策略 | 策略 | 策略编排, 策略控制 | strategy/policy | executable rule systems in control planes | 策略 not equivalent to political policy here | 网络控制面 material |
| Authority ceiling | maximum delegated authority | 权限上限 | 權限上限 | 授权边界, 权责边界 | authority upper bound | strict delegation cap with forbidden domains | 审批流程 wording can blur hard bounds | 运维安全治理 docs |
| Evidence | evidence | 证据 | 證據 | 证据链, 可验证证据 | evidence | verifiable supporting data and lineage | 证明 can imply theorem proof; not always empirical evidence | 科研复现/可信计算 |
| Receipt | receipt/proof record | 回执 | 回執 | 执行回执, 操作回执 | return receipt | operation acknowledgment artifact | 审计日志 ≠ 回执 exactly; receipt is action-specific proof | 工程审计实践 |
| Provenance | provenance/lineage | 溯源 | 溯源 | 来源追踪, 谱系, 沿袭 | trace to source | source lineage and transformation history | 追溯 often compliance-only; provenance is technical lineage | 供应链溯源 and data lineage |
| Observation | measurement/observation | 观测 | 觀測 | 观测值, 测量帧 | observe | bounded sensor/state capture with explicit source | 观察 can be human-only in colloquial use | 监控与测量 systems |
| Claim | assertion | 声明 | 聲明 | 主张, 断言 | statement | explicit proposition requiring evidence tier | 声称 in media sense is weaker | 论证/科学方法 |
| Deterministic replay | reproducible replay | 确定性重放 | 確定性重放 | 可复现回放 | deterministic replay | same inputs and ordering produce same outputs | 可重复 may be statistical repeatability, not byte equivalence | 工业控制/仿真 |
| World model | world model | 世界模型 | 世界模型 | 环境模型, 场景模型 | world model | often coupled with embodied closed loop and simulation-reality bridge | not only latent model in RL papers | 具身智能 and 数字孪生 traditions |
| World state | world state | 世界状态 | 世界狀態 | 全局状态, 场景状态 | world state | authoritative state snapshot/time slice | 状态 in controls may mean scalar state, not ontology state | 仿真/游戏/机器人 |
| Digital twin | digital twin | 数字孪生 | 數字孿生 | 虚实映射, 虚实融合 | digital twin | synchronized model for analysis/control/rehearsal | often overloaded as mere 3D model; should include data loop | 工业互联网/城市孪生 |
| Agent | agent | 智能体 | 智能體 | 自主体, 代理体 | intelligent body | autonomous decision/execution entity (software/robotic) | 代理 in networking means proxy; context required | 多智能体 systems |
| Multi-agent | multi-agent systems | 多智能体 | 多智能體 | 群体智能体系统 | many agents | interacting autonomous agents with coordination/conflict | often conflated with microservices | AAMAS and Chinese MAS literature |
| Embodied intelligence | embodied AI | 具身智能 | 具身智能 | 具身智能体, 具身认知 | embodied intelligence | intelligence emerging through body-environment interaction | not limited to hardware robots in Chinese usage | CAAI and university surveys |
| Identifier | identifier | 标识 | 標識 | 身份标识, 节点标识 | identifier mark | identity label decoupled from locator in many future-network works | 标识 can mean logo/mark in general Chinese | 标识网络 literature |
| Locator | locator | 定位标识/位置标识 | 定位標識/位置標識 | Locator, 位置标识 | location marker | topological/network location information | 定位 can imply physical GPS; protocol context needed | 身份位置分离 papers |
| Naming | naming | 命名 | 命名 | 名称体系, 名字解析 | naming | human/service naming layer often separate from identity | 名称 often conflated with DNS only | ICN/标识解析 works |
| Resolution | resolution | 解析 | 解析 | 标识解析, 名称解析 | resolve/parse | mapping from name/identifier to routable/usable endpoint | 解析 also means “analysis” generally | DNS/标识解析 systems |
| Reachability | reachability | 可达性 | 可達性 | 连通性 | reachable | whether endpoint/path is currently reachable | connectivity test results can be path-specific, not global truth | 网络测量 literature |
| Routing | routing | 路由 | 路由 | 路径转发 | route | control/data-plane forwarding decision process | path selection may be policy-constrained beyond shortest path | 路由体系 papers |
| Path selection | policy-constrained path choice | 路径选择 | 路徑選擇 | 路径感知, 策略选路 | choose path | choosing among candidate paths under constraints | often merged with routing in English docs; Chinese may separate | 路径感知 network research |
| Multipath | multipath transport/routing | 多路径 | 多路徑 | 多路径传输 | many paths | concurrent or failover path use at transport/network layers | can be confused with link aggregation only | MPTCP/算力网络 research |
| Trust root | root of trust | 信任根 | 信任根 | 根信任, 根证书 | trust root | bootstrapping trust anchor set | 信任 vs 可信 semantics differ by field | PKI/可信计算 traditions |
| Authorization | authorization | 授权 | 授權 | 访问控制, 鉴权 | grant authority | explicit permission grant under policy | 鉴权 (authn/authz mixed) ambiguity | 安全访问控制 literature |
| Control plane | control plane | 控制面 | 控制面 | 网络控制平面 | control surface | policy/signaling/management decision layer | often contrasted with data plane in Chinese standards | SDN/未来网络 material |
| Data plane | data plane | 数据面 | 數據面 | 转发面 | data surface | packet/flow forwarding execution path | 数据层 in OSI may confuse newcomers | SDN and programmable network works |
| Intent-driven networking | IDN | 意图驱动网络 | 意圖驅動網絡 | 自智网络, 意图编排 | intent-driven network | natural language/high-level intent compiled to network behaviors | “autonomous” marketing language may overstate capability | Chinese IDN whitepapers |
| Deterministic networking | deterministic networking | 确定性网络 | 確定性網絡 | DetNet, TSN融合 | deterministic network | bounded latency/jitter/reliability guarantees | deterministic ≠ globally deterministic computation | DetNet/industrial networking |
| Compute network | compute-network integration | 算力网络 | 算力網絡 | 算网融合, 算力路由 | computing-power network | joint scheduling of compute/storage/network resources | easy false friend with CDN only | Chinese operator whitepapers |
| Semantic communication | semantic communication | 语义通信 | 語義通信 | 任务导向通信 | semantic communication | transmit task-relevant meaning, not only bit fidelity | semantic here is comms-theoretic, not web ontology | Chinese comms research |
| Artificial life | artificial life | 人工生命 | 人工生命 | 数字生命, 虚拟生命 | artificial life | computational life-like systems, emergence, adaptation | “virtual avatar” is narrower | ALIFE + Chinese complex systems |
| Emergence | emergence | 涌现 | 湧現 | 涌现行为 | emergent | macro behavior from micro interactions | often used rhetorically without mechanistic proof | complexity science literature |
| Self-organization | self-organization | 自组织 | 自組織 | 自组织系统 | self organize | order formation without central controller | can be overstated in centrally-controlled systems | complex systems/control |
