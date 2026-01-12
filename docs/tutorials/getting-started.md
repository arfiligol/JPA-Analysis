---
aliases:
  - "Getting Started"
  - "快速入門"
tags:
  - boundary/system
  - audience/team
status: stable
owner: docs-team
audience: team
scope: "第一次使用 JPA Analysis Pipeline 的完整流程"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Getting Started

歡迎使用 JPA Analysis Pipeline！本教程將帶你完成從「原始數據」到「分析報告」的完整流程。

## 1. Environment Setup

確保你已經安裝 `uv`。

```bash
# 安裝依賴
uv sync
```

## 2. Prepare Data

我們使用範例數據 `data/raw/admittance/PF6FQ_Q0_Float_Im_Y11.csv` (假設存在，或使用你自己的 CSV)。

### 轉換數據
首先，將 CSV 轉換為標準 JSON。

```bash
uv run convert-hfss-admittance \
    --component-id DemoJPA \
    data/raw/admittance/PF6FQ_Q0_Float_Im_Y11.csv
```

成功後，你會看到生成了 `data/preprocessed/DemoJPA.json`。

## 3. Visualize Raw Data

在擬合前，先看一下數據長什麼樣子。

```bash
uv run plot-admittance DemoJPA
```

這會打開瀏覽器顯示互動式圖表。確認：
- 是否有清晰的共振模式（斜線或曲線）？
- 是否有雜訊？

## 4. Run Analysis

現在執行 SQUID 模型擬合。

```bash
uv run squid-model-with-Ls-fit DemoJPA
```

### 解讀結果
終端機會輸出類似：
```
Mode 1: Ls=0.0823 nH, C=1.4502 pF, RMSE=0.0123
```
圖表會顯示紅色的擬合虛線疊加在數據點上。

## 5. Next Steps

恭喜！你已經完成了第一次分析。

- **想要批次處理？** 指令支援多個檔案：`uv run squid-model-fit JPA1 JPA2 JPA3`
- **想要輸出 Matplotlib 圖？** 加上 `--matplotlib` 參數。
- **遇到問題？** 查看 [[../reference/cli/index.md|CLI Reference]] 或 [[../how-to/index.md|How-to Guides]]。
