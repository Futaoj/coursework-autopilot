# Coursework Autopilot

![Measured Pass Rate](https://img.shields.io/badge/measured_pass_rate-100%25%20(8%2F8)-brightgreen)
![Skill Validation](https://img.shields.io/badge/skill_validation-2%2F2%20passed-brightgreen)
![Smoke Checks](https://img.shields.io/badge/smoke_checks-3%2F3%20passed-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![MCP Tools](https://img.shields.io/badge/MCP_tools-2-informational)
![Helper Scripts](https://img.shields.io/badge/helper_scripts-3-informational)

`coursework-autopilot` 是一个面向课程设计/课程作业场景的 Skill 与本地 MCP 工具链。它可以把老师下发的 `.zip`、混合 PDF/DOCX/TXT 材料或已有 `COURSE_REQUIREMENTS.md` 规范化成需求文件，在确认环节后继续推进实现、验证和正式报告撰写。

仓库里同时提供两套内容：
- 开发版 skill：`skills/coursework-autopilot`
- 可发布版 skill 包：`publish/coursework-autopilot`

## 核心能力

- 从原始课程压缩包提取并生成 `COURSE_REQUIREMENTS.md`
- 检查已有 workspace 是否已经完成规范化
- 通过 MCP 暴露 `extract_course_requirements` 与 `inspect_course_workspace`
- 提供可直接套用的课程设计报告模板
- 在 skill 内明确要求“先确认需求，再编码”

## 指标准则

上面的徽章是本仓库当前版本的实测结果，不是对所有课程压缩包场景的无限泛化保证。

- `measured_pass_rate 100% (8/8)`：来自项目虚拟环境中的 `./.venv/bin/pytest -q`
- `skill_validation 2/2 passed`：`skills/coursework-autopilot` 和 `publish/coursework-autopilot` 都通过 `quick_validate.py`
- `smoke_checks 3/3 passed`：验证了报告模板生成、requirements 提取、workspace 检查三条核心辅助脚本链路
- `MCP_tools 2`：当前 MCP 服务暴露 2 个工具
- `helper_scripts 3`：当前 skill 内置 3 个可执行脚本

## 仓库结构

```text
.
├── mcp_server/                      # 本地 MCP server
├── src/course_design_autopilot/     # 核心提取与检查逻辑
├── tests/                           # pytest 测试
├── skills/coursework-autopilot/     # 开发中的 skill
└── publish/coursework-autopilot/    # 整理好的发布包
```

`skills/coursework-autopilot` 目前包含完整的 bundled resources：

- `scripts/`
  `extract_course_requirements.py`
  `inspect_course_workspace.py`
  `init_report_from_template.py`
- `references/`
  `mcp-contract.md`
  `repo-layout.md`
  `report-writing.md`
  `setup.md`
- `assets/`
  `report-template/REPORT.md`

## 快速开始

### 1. 安装依赖

```bash
python -m pip install -e .
```

### 2. 本地运行 MCP server

```bash
python -m mcp_server
```

### 3. 不走 MCP，直接用脚本

```bash
python skills/coursework-autopilot/scripts/extract_course_requirements.py <archive.zip> <workspace>
python skills/coursework-autopilot/scripts/inspect_course_workspace.py <workspace>
python skills/coursework-autopilot/scripts/init_report_from_template.py <output.md>
```

## 平台接入

### Codex

- Skill 开发目录：`skills/coursework-autopilot`
- Skill 发布目录：`publish/coursework-autopilot`
- 本地 MCP server 启动命令：

```bash
python -m mcp_server
```

如果你的 Codex 环境支持项目级 MCP 配置，直接复用 `mcp_server/client-config.example.json` 里的结构即可。

### Claude Code

Claude Code 官方文档支持项目级 MCP 配置，项目范围的服务可以写进仓库根目录 `.mcp.json`，也可以用命令行添加。

示例做法 1：直接用命令添加本地 server。

```bash
claude mcp add coursework-autopilot --scope project -- python -m mcp_server
```

示例做法 2：手动在仓库根目录创建 `.mcp.json`。

```json
{
  "mcpServers": {
    "coursework-autopilot": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {}
    }
  }
}
```

如果你不想接 MCP，也可以在 Claude Code 里直接运行仓库内脚本：

```bash
python skills/coursework-autopilot/scripts/extract_course_requirements.py <archive.zip> <workspace>
```

### OpenCode

OpenCode 支持在 `opencode.json` 或 `opencode.jsonc` 中通过 `mcp` 字段配置本地 MCP server。

示例配置：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coursework-autopilot": {
      "type": "local",
      "command": ["python", "-m", "mcp_server"],
      "enabled": true
    }
  }
}
```

配置完成后可以用这些命令确认状态：

```bash
opencode mcp list
opencode run "Use coursework-autopilot to inspect this coursework workspace"
```

### 其他平台

只要运行环境支持本地 MCP server，核心接入思路都一样：

1. 在仓库根目录安装依赖
2. 以 `python -m mcp_server` 启动 server
3. 把这个命令注册到对应平台的 MCP 配置里
4. 如果平台不支持 MCP，就直接调用 `skills/coursework-autopilot/scripts/` 下的脚本

## 验证命令

```bash
./.venv/bin/pytest -q
python path/to/skill-creator/scripts/quick_validate.py skills/coursework-autopilot
python path/to/skill-creator/scripts/quick_validate.py publish/coursework-autopilot
```

## 发布说明

如果你要把 skill 单独分发，优先使用 `publish/coursework-autopilot/`。这个目录应当作为最终 GitHub 发布包和后续打 tag 的基准内容。
