# TravelNearBy

旅行周边游 Agent 的离线骨架实现，提供 POI 过滤、路线排序、行程排期与基础校验能力，便于后续接入 LLM 与在线数据源。

## 功能概览
- **POI 检索**：按城市、主题、半径过滤示例 POI 数据，并从城市中心开始排序。
- **路线排序**：使用最近邻策略估算路途时间并排序，支持步行/公交/驾车三种速度假设。
- **行程排期**：按照每日开始/结束时间生成日程，无法容纳的景点会自动顺延或丢弃。
- **校验报告**：检查营业时间、长距离通勤、预算与主题覆盖风险。

## 快速开始
1. 安装依赖（当前仅使用标准库，无需额外安装）。
2. 运行示例脚本：
   ```bash
   python examples/demo.py
   ```
3. 输出包括行程提要与校验摘要，可根据业务需求替换数据源或接入 LLM 作为 Planner/Verifier。

## 目录结构
- `travel_nearby/agent.py`：规划入口，协调检索、排序与校验。
- `travel_nearby/tools.py`：距离计算、POI 过滤、路线生成、日程排期与校验工具。
- `travel_nearby/data.py`：示例 POI 数据（北京、上海）与城市中心坐标。
- `travel_nearby/models.py`：行程与校验相关的数据模型。
- `examples/demo.py`：运行示例。

## 后续扩展建议
- 替换 `data.py` 为实时数据源（地图/票务 API）。
- 增加 LLM 提示词与工具路由，将 `TravelPlanner` 拓展为多阶段 Agent（Planner → Verifier → Refiner）。
- 引入更多指标（人流、评分、儿童友好度）并改进路线优化策略。
