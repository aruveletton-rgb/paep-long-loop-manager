# paep-long-loop-manager

有边界的多阶段工程计划。版本 **1.1.0**，维护者标识 `paep-user`。

把工程目标拆成可以恢复的阶段，为每个阶段列出进入证据、工作范围、退出证据、负责人和停止条件。适合多阶段推进，以及从中断记录恢复之前的计划核对。

仓库：[paep-long-loop-manager](https://github.com/aruveletton-rgb/paep-long-loop-manager)。

## 包内文件

| 文件 | 用途 |
| --- | --- |
| `SKILL.md` | 宿主发现与加载的技能正文，包含 name、description 和版本 |
| `skill.yaml` | PAEP 的输入、输出、执行者、权限和 task/result 协议元数据 |
| `tests/test_long_loop_contract.py` | 依赖 PAEP 后端的权限契约测试 |
| `README.md` | 安装、调用和集成说明 |

## 输入、输出与边界

| 字段 | 要求 |
| --- | --- |
| `repository_path` | 必填；被评审项目的绝对目录，必须存在，并在 PAEP 配置允许的根目录范围内 |
| `brief` | 可选；具体目标、需要读取的材料相对路径、已有任务编号或中断背景；请勿包含敏感凭据 |
| 输出 | 协议任务产物 `artifacts/long-loop-report.md` |
| PAEP 执行者 | `codex`，review 模式，外部任务交接 |

恢复交接需带计划路径与摘要、最后完成阶段及证据、当前阶段和中断点、已授予权限及范围、未决事项与决策人。计划陈述不能代替执行证据；证据缺失时应记录 HANDOFF_INCOMPLETE。

当前权限仅允许读取声明的 `repository_path`。`skill.yaml` 不授予项目文件写入、网络、Shell、密钥或生产操作权限；报告通过任务协议声明的产物通道交付，不代表可以任意改写项目文件。扩大权限必须有独立、明确的任务授权。

本技能只生成有界计划，不是无限重试程序、后台调度器或自动化工作流；不会自行创建定时任务或启动实施。

## 安装到本地宿主

将导出的包放入宿主实际发现的技能根，每个技能单独占一个子目录，保证根入口为 `<技能根>/paep-long-loop-manager/SKILL.md`。例如，Codex 用户级目录是 `~/.agents/skills`，也可以按项目使用 `.agents/skills`；安装后先确认技能出现在宿主技能列表。[官方 OpenAI 技能说明](https://learn.chatgpt.com/docs/build-skills)介绍了这些发现目录与显式调用方式。

本包保持独立技能目录形式，没有附带插件清单。DSH 使用其自身实际扫描的技能根；共享同一份文件或目录链接时，两端仍需分别确认发现和加载成功，不能以文件存在推断技能已加载。

**源代码检出目录与活跃安装目录分开。** 当前 PAEP 包摘要会递归文件；把 `.git` 放入活跃技能包会改变摘要，并可能触发包大小/文件数限制。请从独立检出导出不含 `.git` 的安装包，或下载 GitHub ZIP 并把其中实际技能内容放到目标目录。不要再嵌套一层 `<仓库名>-main`。

以下 PowerShell 示例为首次安装，请替换本地路径。目标已存在时停止，先比较版本，不覆盖已有技能：

```powershell
$skillName = 'paep-long-loop-manager'
$sourceRoot = 'D:\skill-sources' # 独立源码检出区；可改为自己的目录
$skillRoot = Join-Path $env:USERPROFILE '.agents\skills' # 可改为宿主实际发现根
$checkout = Join-Path $sourceRoot $skillName
$archive = Join-Path $sourceRoot ($skillName + '.zip')
$destination = Join-Path $skillRoot $skillName
if ((Test-Path -LiteralPath $checkout) -or (Test-Path -LiteralPath $archive) -or (Test-Path -LiteralPath $destination)) {
    throw '示例面向首次安装；目标已存在，请先比较版本。'
}
New-Item -ItemType Directory -Path $sourceRoot -Force | Out-Null
git clone 'https://github.com/aruveletton-rgb/paep-long-loop-manager.git' $checkout
if ($LASTEXITCODE -ne 0) { throw 'clone 失败，停止安装' }
git -C $checkout archive --format=zip --output=$archive HEAD
if ($LASTEXITCODE -ne 0) { throw '导出失败，停止安装' }
New-Item -ItemType Directory -Path $destination | Out-Null
Expand-Archive -LiteralPath $archive -DestinationPath $destination
Get-Item -LiteralPath (Join-Path $destination 'SKILL.md')
```

更新时从独立检出获取新版本，记录目标提交，再导出到新目录比较并替换安装包；保留必要的旧版本与本地自定义。PAEP 与宿主若指向同一规范包，应保持同名技能内容一致，避免重复名称和版本漂移。

## 在 Codex 中显式调用

在当前会话选择此技能，或明确写出技能名称与材料路径。Codex CLI / IDE 可用 `$` 提及技能或通过 `/skills` 选择；不同桌面版本的选择入口以实际界面为准。调用示例：

```text
请使用 paep-long-loop-manager。
repository_path: D:\work\example-project
brief: 根据 docs/plan.md 和 audit/checkpoint.json 规划后续阶段；先核对上阶段退出证据，再决定从何处恢复。
只在声明的只读范围内检查资料，按 SKILL.md 输出报告；缺失证据如实列出。
```

将示例目录替换为真实项目，检查 brief 中材料确实存在。技能加载是读取工作方法；实际执行结果仍需查看报告与证据。

## 在 PAEP 调用界面中集成

PAEP 是独立应用，不包含在此技能仓库中。先启动已配置的 PAEP 服务，把**不含 `.git` 的技能包**放入其配置的技能根，再在技能目录中重新扫描，核对 name、版本、输入和权限。无需把本仓库复制成整个 PAEP 应用。

1. 在技能中心找到 `paep-long-loop-manager`，点击“使用”。
2. 填写项目绝对路径、目标、`repository_path` 与可选 `brief`；只填写本次允许读取的材料范围。
3. 生成调用指令与 TASK 文件，检查输出位置、约束和验收要求。
4. 将指令复制给**当前 Codex 会话**，或把 TASK 文件绝对路径交给它读取。需要 DSH 子任务时，由协调者明确任务范围、允许操作和产物路径，再通过已授权的 computer use 交接。
5. 执行结束后，在任务详情中导入真实结果，核对任务编号、执行者与证据路径。
6. 独立检查实际产物，再按界面确认验收；“已复制”“执行者报告完成”和“已验收”是不同状态。

首版 PAEP 通过可复制指令和本地任务文件连接当前会话，不会因点击生成而自动派发到 Codex 或自动控制 DSH。`skill.yaml` 的 executor 是交接配置，不能视为宿主账户、权限或网络连接已配置的证明。

## 契约测试

测试导入 `backend.skill_runtime` 和 `pytest`，需要已有 PAEP 源码与对应 Python 测试环境。它不是独立克隆后即可直接运行的自包含项目。

在能够导入 PAEP `backend` 的源码根运行，并替换下面两个绝对路径：

```powershell
python -B -m pytest 'D:\skill-sources\paep-long-loop-manager\tests' -q -p no:cacheprovider --basetemp 'D:\paep-test-output\paep-long-loop-manager'
```

使用本次测试专用、尚无重要内容的 `--basetemp` 目录。测试检查本包权限契约，不能替代宿主实际加载、GUI 交接或业务报告的验收。

## 许可

当前包未附带 `LICENSE` 文件；公开可见不等于已授予开源许可。复制、修改或再分发的许可范围请向权利人确认。本说明不添加或推定 MIT、Apache 等许可证。
