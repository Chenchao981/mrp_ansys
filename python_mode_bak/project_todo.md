## 项目计划与任务跟踪（project_todo.md）

本文件用于集中管理本项目的范围、规划、里程碑、任务分解与进度跟踪，作为开发与验收的主控文档。内容已整合 `todo.md` 与 `todo-list.md` 并与 `MRP业务说明和计算公式.md` 的口径一致。

---

### 一、项目概览

- 项目名称: 车规功率芯片 MRP 系统（动态安全库存 + 月度下单）
- 产品范围: `LD公司-50KA`、`B公司-10LL`
- 数据来源: `rawdata.xlsx`（同源 `rawdata.txt`），销售预测与实际数据
- 核心目标:
  - 提高预测准确度（量化误差、偏差修正）
  - 动态安全库存（服务水平、滚动 σ、动态 LT）
  - 自动化订单建议（Order-Up-To，月度 Q 计算）

---

### 二、范围与交付物

- 范围内:
  - 读取 `rawdata.xlsx` 并解析为结构化时序数据
  - 指标计算：`D, e, bias, σ_error, F*`、`p1/p2/LT/H`、`EARR`、`SS/M/Q`
  - 明细与汇总导出（CSV/Excel），可选图表
  - 质量与异常报告（库存平衡校验、缺失/异常）
  - CLI 可执行脚本与可配置参数

- 交付物:
  - 代码与目录：`src/mrp/*.py`、`scripts/run_mrp.py`
  - 配置：`config.yaml`
  - 结果：`outputs/quality_report.csv`、`error_metrics.csv`、`leadtime_params.csv`、`earr_detail.csv`、`orders.csv`
  - 文档：`MRP业务说明和计算公式.md`、`todo-list.md`、本文件

---

### 三、里程碑与时间表（建议）

- 阶段一（数据基础，W1–W2）: 完成 Excel 解析、主表构建、质量报告
- 阶段二（核心计算，W3–W4）: 误差分析、动态安全库存、订单量计算
- 阶段三（集成与自动化，W5–W6）: 模块集成、CLI、参数化与回归测试
- 阶段四（可视化与交付，W7–W8）: 图表/报告、验收与上线

---

### 四、WBS（工作分解）与任务清单

表格字段说明：`ID | 模块 | 任务 | 负责人 | 状态 | 开始 | 截止 | 进度% | 产出 | 备注/阻塞`

| ID | 模块 | 任务 | 负责人 | 状态 | 开始 | 截止 | 进度% | 产出 | 备注/阻塞 |
|---|---|---|---|---|---|---|---:|---|---|
| IO-1 | IO | 读取 `rawdata.xlsx`（header=None） | TBD | Backlog |  |  | 0 | 暂存DF | 多段表头/块 |
| IO-2 | IO | 解析产品块为纵表 | TBD | Backlog |  |  | 0 | `df_long.csv` | 指标与月份映射 |
| NM-1 | Normalize | 构建产品×月份主表 | TBD | Backlog |  |  | 0 | `df_main.csv` | 键：company/product/month |
| NM-2 | Normalize | 计算 `D=S+S_other+OUT_other` | TBD | Backlog |  |  | 0 | 列 `D` |  |
| QC-1 | Quality | 库存平衡校验 `I_end≈I_start+R-D` | TBD | Backlog |  |  | 0 | `quality_report.csv` | 3% 阈值 |
| MT-1 | Metrics | 误差 `e=F-D` | TBD | Backlog |  |  | 0 | `error_metrics.csv` |  |
| MT-2 | Metrics | 偏差/σ（滚动 `W`）与 `F*` | TBD | Backlog |  |  | 0 | 列 `bias,sigma,F*` | `W=12` 默认 |
| LT-1 | Leadtime | 估计 `p1,p2`（NNLS/鲁棒） | TBD | Backlog |  |  | 0 | `leadtime_params.csv` | 约束 `p1+p2≤1` |
| LT-2 | Leadtime | 计算 `LT=1*p1+2*p2`、`H=1+LT` | TBD | Backlog |  |  | 0 | 列 `LT,H` |  |
| LT-3 | Leadtime | 预计到货 `EARR=p2*O_{t-2}+(p1+p2)*O_{t-1}` | TBD | Backlog |  |  | 0 | `earr_detail.csv` | 仅历史两期 |
| PL-1 | Policy | 覆盖期需求 `D_H` | TBD | Backlog |  |  | 0 | 中间列 | `H∈[2,3]` |
| PL-2 | Policy | 安全库存 `SS_H=Z*sigma*sqrt(H)` | TBD | Backlog |  |  | 0 | 中间列 | `Z=1.65` |
| PL-3 | Policy | 目标水位 `M=D_H+SS_H` | TBD | Backlog |  |  | 0 | 中间列 |  |
| PL-4 | Policy | 下单量 `Q=max(0,M-I_end-EARR)` | TBD | Backlog |  |  | 0 | `orders.csv` | 非负截断 |
| RP-1 | Report | 汇总/导出 CSV/Excel | TBD | Backlog |  |  | 0 | 多CSV |  |
| RP-2 | Report | 可视化（可选） | TBD | Backlog |  |  | 0 | 图表 | 趋势/误差/订单 |
| OPS-1 | Ops | `config.yaml` 与参数化 | TBD | Backlog |  |  | 0 | `config.yaml` | Z,W,阈值,输入输出 |
| OPS-2 | Ops | CLI：`python scripts/run_mrp.py --config config.yaml` | TBD | Backlog |  |  | 0 | 可运行脚本 |  |

---

### 五、实现分工与文件映射

- IO（读取/解析）: `src/mrp/io.py`
- Normalize（主表构建）: `src/mrp/normalize.py`
- Metrics（误差/偏差/σ）: `src/mrp/metrics.py`
- Leadtime（p1/p2/LT/H/EARR）: `src/mrp/leadtime.py`
- Policy（SS/M/Q）: `src/mrp/policy.py`
- Report（导出/图表）: `src/mrp/report.py`
- CLI: `scripts/run_mrp.py`
- 配置: `config.yaml`

---

### 六、验收标准（Definition of Done / Acceptance）

- 读取并构建主表成功；键完整：`company, product, month`
- `quality_report.csv` 通过率 ≥ 95%，库存平衡相对误差 ≤ 配置阈值（默认 3%）
- 误差指标输出 `error_metrics.csv` 与抽验月手算一致（±1e-6）
- `p1,p2 ≥ 0` 且 `p1+p2 ≤ 1`；`leadtime_params.csv` 输出齐全
- 订单建议 `orders.csv`：若 `I_end+EARR ≥ D_H+SS_H` 则 `Q=0`
- 所有输出可复现（固定随机性、有配置快照）

---

### 七、风险与应对

- 数据质量：缺失/异常 → 质量报告与回填策略（移动中位/分位数）
- 低样本：`W` 不足 → 降维并标注置信度
- 拟合不稳：`p1/p2` → 启用鲁棒近似与约束优化
- 需求突变：人工覆盖入口与版本回滚

---

### 八、进度看板（Kanban）

- Backlog: IO-1, IO-2, NM-1, NM-2, QC-1, MT-1, MT-2, LT-1, LT-2, LT-3, PL-1, PL-2, PL-3, PL-4, RP-1, RP-2, OPS-1, OPS-2
- In Progress: （填写中）
- Review: （填写中）
- Done: （填写中）

更新格式示例：`[2025-08-xx] 将 IO-1 → In Progress（Owner: 张三），预计完成 08-xx。`

---

### 九、更新日志（Changelog）

- v0.1 新建文件，整合范围/里程碑/WBS/验收/风险/看板。

---

### 十、下一步行动（Next Actions）

- 指派负责人，填充 `负责人/开始/截止` 字段
- 建立仓库结构与空模块文件：`src/mrp/*.py`、`scripts/run_mrp.py`
- 创建 `config.yaml`，录入默认参数（`Z=1.65, W=12, balance_tolerance=0.03`）
- 启动 IO-1/IO-2，实现最小可运行链路（读 → 纵表 → 主表）


