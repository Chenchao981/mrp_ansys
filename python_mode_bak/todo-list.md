## 构建代码的 TODO 列表（基于 rawdata.xlsx + 业务口径）

本清单用于指导用 Python 快速实现读取 `rawdata.xlsx`，并按 `todo.md`、`计算MRP公式.md` 与 `MRP业务说明和计算公式.md` 的统一口径完成 MRP 核心计算与输出。

---

### 0) 项目结构与依赖

- 目录建议
  - `src/mrp/__init__.py`
  - `src/mrp/io.py`（Excel 读取与原始块解析）
  - `src/mrp/normalize.py`（宽表 → 纵表、字段标准化与数据模型构建）
  - `src/mrp/metrics.py`（预测误差、偏差、σ、库存平衡校验）
  - `src/mrp/leadtime.py`（p1/p2 估计、LT/H 计算、EARR 预计到货）
  - `src/mrp/policy.py`（SS、目标水位 M、下单量 Q 计算）
  - `src/mrp/report.py`（明细表、汇总表、异常质检、可视化可选）
  - `scripts/run_mrp.py`（命令行入口）
  - `config.yaml`（Z、W、异常阈值等参数）
  - `outputs/`（结果输出目录）

- 依赖
  - pandas, numpy, scipy (optimize.nnls), openpyxl, pydantic/attrs（可选，用于数据模型校验）

---

### 1) 读取与解析 rawdata.xlsx（原始 → 结构化）

- 任务
  - [ ] 使用 `pandas.read_excel('rawdata.xlsx', header=None)` 读取，考虑多行表头与分段结构。
  - [ ] 逐行扫描解析“产品块”：遇到 `公司/客户`、`产品`、`分类`（预测数据/实际数据）切换上下文。
  - [ ] 抽取行内“指标名称 + 1~12月数值”，形成记录：`{company, product, data_type, metric_name, month, value}`。
  - [ ] 允许空白行与缺失值，保留原始位置信息（便于溯源）。

- 字段与映射（最小可用集合）
  - 预测区（销售输入）：`预测交货数量 → F_t`
  - 实际区：
    - `订货量 → O_t`
    - `收货数量 → R_t`
    - `交货数量 → S_t`
    - `其他客户交货 → S_other_t`
    - `其他出库数量 → OUT_other_t`
    - `期初库存余额 → I_start_t`
    - `期末库存余额 → I_end_t`

- 输出
  - [ ] 纵表 DataFrame：`columns=[company, product, data_type, metric, month(1-12|datetime), value]`
  - [ ] 宽表（按产品×月份汇总后的计算基表）

---

### 2) 标准化与质量校验

- 任务
  - [ ] 规范产品键：如 `LD公司-50KA`、`B公司-10LL`。
  - [ ] 月份归一：将 `1月..12月` 映射为可排序的 `Period`/`Timestamp`。
  - [ ] 构建按产品×月份的主表，包含：`F, O, R, S, S_other, OUT_other, I_start, I_end`。
  - [ ] 计算实际总消耗：`D = S + S_other + OUT_other`。
  - [ ] 库存平衡校验：`I_end ≈ I_start + R - D`，偏差>阈值（默认 3%）标记为异常。

- 输出
  - [ ] `quality_report.csv`（缺失、异常、库存平衡误差）

---

### 3) 预测误差与滚动统计

- 任务
  - [ ] 误差：`e_t = F_t - D_t`（若某产品缺预测，先用 `D` 的移动平均/季节平滑补一个临时 `F`）。
  - [ ] 偏差：`bias_t = mean(e_{t-W+1..t})`（默认 `W=12`，不足则用现有长度并标注置信度）。
  - [ ] 修正预测：`F*_t = F_t + bias_t`。
  - [ ] 标准差：`σ_error,t = stdev(e_{t-W+1..t})`。

- 输出
  - [ ] `error_metrics.csv`（含每月 `e, bias, sigma, F*`）

---

### 4) 提前期分布 p1/p2 动态估计与 H 期预计到货 EARR

- 任务
  - [ ] 基于历史 `O→R` 的关系估计：`R_t ≈ p1*O_{t-1} + p2*O_{t-2}`。
  - [ ] 采用 NNLS/最小二乘约束：`p1,p2 ≥ 0, p1+p2 ≤ 1`；若实现受限，用鲁棒近似：
        `p1 = median(R_t/O_{t-1})`（截断[0,1]），`p2 = max(0, 1-p1)` 并可再做一次回归微调。
  - [ ] 动态平均提前期：`LT_t = 1*p1 + 2*p2`；审视周期 `P=1`，`H_t = 1 + LT_t ∈ [2,3]`。
  - [ ] 预计在 `H_t` 内可到货（仅依赖历史两期已下单）：
        `EARR_{t,H} = p2*O_{t-2} + (p1 + p2)*O_{t-1}`。

- 输出
  - [ ] `leadtime_params.csv`（按产品列出 p1, p2, LT）
  - [ ] `earr_detail.csv`（各月 EARR 明细）

---

### 5) 动态安全库存、目标水位与下单量

- 任务
  - [ ] 覆盖期需求聚合：令 `H=H_t`，`h=floor(H)`，`phi=H-h`：
        `D_H = sum(F*_{t+1..t+h}) + phi*F*_{t+h+1}`。
  - [ ] 覆盖期安全库存：`SS_H = Z * σ_error,t * sqrt(H)`（`Z` 默认 1.65，可配置）。
  - [ ] 计算：`M_t = D_H + SS_H`。
  - [ ] 下单量：`Q_t = max(0, M_t - I_end_t - EARR_{t,H})`。
  - [ ] 边界处理：`Q_t` 负值置 0；缺值回退并记录原因；约束 `0≤p1,p2≤1`、`p1+p2≤1`。

- 输出
  - [ ] `orders.csv`（每月建议下单量 Q，含解释字段：D_H, SS_H, I_end, EARR, H, LT）

---

### 6) 报表与可视化（可选，但推荐）

- 任务
  - [ ] 趋势图：库存（I_end）vs 目标水位（M）vs 预计到货（EARR）。
  - [ ] 误差时间序列与 σ 动态。
  - [ ] 订单量 Q 柱状图。
  - [ ] 质量报告/异常列表导出。

- 输出
  - [ ] `reports/` 下 PNG/HTML 图表与汇总 Markdown/Excel。

---

### 7) 配置、CLI 与输出规范

- `config.yaml` 示例
  ```yaml
  service_level: 0.95     # Z=1.65
  Z: 1.65
  window_months: 12       # W
  balance_tolerance: 0.03 # 库存平衡相对误差阈值
  robust_p_estimation: true
  fallback_forecast_ma: 3 # 缺预测时的移动平均窗
  input_excel: rawdata.xlsx
  output_dir: outputs
  ```

- CLI（`scripts/run_mrp.py`）
  ```bash
  python scripts/run_mrp.py --config config.yaml
  ```

---

### 8) 关键函数与签名建议（Python）

```python
# src/mrp/io.py
def read_raw_excel(path: str) -> "pd.DataFrame":
    """读取原始 Excel 为未加工 DataFrame（header=None）。"""

# src/mrp/normalize.py
def parse_blocks(df_raw) -> "pd.DataFrame":
    """解析产品块，产出纵表：company, product, data_type, metric, month, value。"""

def build_timeseries(df_long) -> "pd.DataFrame":
    """构建按产品×月份的主表（含 F,O,R,S,S_other,OUT_other,I_start,I_end,D）。"""

# src/mrp/metrics.py
def compute_forecast_errors(df_main, window: int) -> "pd.DataFrame":
    """计算 e, bias, sigma，并生成 F*。"""

def validate_inventory_balance(df_main, tol: float) -> "pd.DataFrame":
    """库存平衡校验与异常标注。"""

# src/mrp/leadtime.py
def estimate_p1_p2(df_main) -> "pd.DataFrame":
    """基于 O→R 历史关系估计 p1,p2（优先 NNLS，退化到鲁棒中位数）。"""

def compute_LT_H(params) -> "pd.DataFrame":
    """计算 LT=1*p1+2*p2，H=1+LT。"""

def compute_EARR(df_main, params) -> "pd.DataFrame":
    """EARR = p2*O_{t-2} + (p1+p2)*O_{t-1}。"""

# src/mrp/policy.py
def compute_orders(df_main, params) -> "pd.DataFrame":
    """计算 D_H, SS_H, M, Q（非负截断），输出 orders 明细。"""

# src/mrp/report.py
def export_reports(df_quality, df_lead, df_orders, outdir: str) -> None:
    """导出 CSV/Excel/图表。"""
```

---

### 9) 验收标准（Acceptance Criteria）

- [ ] 能正确读取 `rawdata.xlsx` 并构建产品×月份主表。
- [ ] 生成 `quality_report.csv`，库存平衡相对误差 ≤ 配置阈值（默认 3%）的月占比 ≥ 95%。
- [ ] 生成 `error_metrics.csv`，并与手工校验的样例月一致（误差容忍 ±1e-6）。
- [ ] p1/p2 约束满足：`p1,p2 ≥ 0` 且 `p1+p2 ≤ 1`；`leadtime_params.csv` 输出完整。
- [ ] `orders.csv` 中 Q 的逻辑正确：当 `I_end + EARR ≥ D_H + SS_H` 时，对应月 `Q=0`。
- [ ] 所有输出均包含 `company, product, month`（或时间段）等关键键，便于追溯。

---

### 10) 下一步

- [ ] 按上述签名生成 Python 脚手架与最小可运行版本。
- [ ] 用 `LD公司-50KA` 与 `B公司-10LL` 跑首轮结果，提交 `outputs/` 与图表。
- [ ] 与业务复核参数：Z、W、p1/p2 稳健性与解释性。


