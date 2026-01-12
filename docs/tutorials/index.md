---
aliases:
  - "Documentation Hub"
  - "導航中心"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "所有分析能力的導航中心，連接 docs 與 code"
version: v0.1.0
last_updated: 2026-01-13
updated_by: docs-team
---

# Tutorials & Capabilities

歡迎來到 SQUID JPA Analysis Pipeline。這裡是了解本專案所有分析能力的起點。

我們已實現以下分析工作流。點擊連結進入詳細文件：

## 1. Core Workflow (SQUID Characterization)

這是本專案最核心的功能：從模擬/數據提取 SQUID 電路模型參數 ($L_s, C_{eff}$)。

| Step | Analysis Capability | Implementations (Code) | Documentation |
|------|---------------------|------------------------|---------------|
| **1** | **Standardize Data** | `src/preprocess/convert_*.py` | [[../how-to/preprocess/index.md\|Preprocess Guide]] |
| **2** | **Visualize Raw** | `src/scripts/plot_admittance.py` | [[../reference/cli/plot-admittance.md\|Visualize Admittance]] |
| **3** | **Extract Resonance** | `src/extraction/admittance.py` | [[../explanation/physics/resonance-extraction.md\|Physics: Extraction]] |
| **4** | **Fit LC Model** | `src/scripts/admittance_fit.py` | [[./getting-started.md\|Tutorial: Start Here]]<br/>[[../how-to/analysis/admittance-fit.md\|How-to: Fit]] |

## 2. Flux Dependence Analysis

分析 VNA 測量的磁通依賴性 (Flux Sweep)。

| Feature | Description | Implementations (Code) | Documentation |
|---------|-------------|------------------------|---------------|
| **Visualization** | 繪製 Amplitude/Phase 熱圖 | `src/scripts/flux_dependence_plot.py` | [[../how-to/analysis/flux-dependence-plot.md\|How-to: Plot Flux]] |
| **Phase Tuning** | 相位解包裹與單位轉換 | `src/visualization/flux_plots.py` | [[../reference/cli/flux-dependence-plot.md\|CLI Reference]] |

## 3. Advanced / Experimental

這些功能用於特定診斷或遺留支援。

| Feature | Description | Implementations (Code) | Documentation |
|---------|-------------|------------------------|---------------|
| **Effective C Fit** | 假設 $L_s=0$，快速估算電容 | `src/scripts/effective_capacitance_fit.py` | [[../how-to/analysis/effective-capacitance.md\|How-to: C_eff Fit]] |
| **Q-Factor** | 從相位群延遲估算 Q 值 | `src/scripts/q_factor_tool.py` | (尚無詳細文件) |
| **Compare Fits** | 比較多次擬合結果 | `src/scripts/plot_comparison.py` | (尚無詳細文件) |

## Learning Path

建議的學習順序：

1. **New User**: 從 [[./getting-started.md\|Getting Started]] 開始，跑通一次完整的 Core Workflow。
2. **Analyst**: 閱讀 [[../explanation/physics/index.md\|Physics]] 理解模型原理，然後參考 [[../how-to/index.md\|How-to Guides]] 解決具體問題。
3. **Developer**: 閱讀 [[../explanation/pipeline/data-flow.md\|Pipeline Data Flow]] 與 [[../reference/guardrails/index.md\|Guardrails]] 了解如何貢獻代碼。

## Need to add a new feature?

參考 [[../how-to/extend/index.md\|Extensions]] 指南，了解如何新增數據來源或分析模組。
