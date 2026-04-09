# 开发修改记录 / Development Changelog

## 2026.4.9 — 修复批量上传首个文件不导出 LRC/SRT 的 bug

### 修改文件及内容

#### 1. `VibeWhisper.ipynb` Cell 8

- **修复首个文件忽略 export_lrc/export_srt 设置的 bug**：原逻辑中 `if i + 1 == 1` 分支只下载 `.ass` 文件，完全忽略了用户的 `export_srt` 和 `export_lrc` 设置。改为统一收集所有输出文件，按需打包 zip 或直接下载单文件。

### Bug 修复汇总

| Bug | 文件 | 影响 | 修复方式 |
|-----|------|------|----------|
| 批量上传时第一个文件不导出 LRC/SRT | notebook Cell 8 | export_lrc=Yes 无效，用户被迫重新上传导致文件名出现 `(1)` | 移除 `if i + 1 == 1` 特殊分支，统一用 `download_files` 列表收集所有输出文件 |

---

## 2026.4.8 — 项目重命名 & 代码拆分 & Bug 修复

### 修改目的

1. 项目从 N46Whisper 重命名为 VibeWhisper，仓库迁移至 `sananisome/VibeWhisper`
2. 将 `srt2lrc` 拆分为独立文件，解耦与 `srt2ass.py` 的关系
3. 修复代码审查中发现的多个 bug

### 修改文件及内容

#### 1. 新增 `srt2lrc.py`

- 从 `srt2ass.py` 中提取 `srt2lrc()` 函数为独立模块
- 自带 `fileopen()` 辅助函数，不再依赖 `srt2ass.py`
- 使用标准库 `re` 替代第三方 `regex`，减少依赖
- **修复多行字幕丢失 bug**：SRT 中一条字幕包含多行文本时，旧逻辑只保留第一行，现在会合并所有文本行

#### 2. `srt2ass.py`

- 移除 `srt2lrc()` 函数（已迁移至 `srt2lrc.py`）
- **修复越界 bug**：当 SRT 文件最后一行为纯数字时，`lines[ln+1]` 会触发 `IndexError`，新增 `ln + 1 < len(lines)` 边界检查
- **修复未知 style 崩溃 bug**：当 `sub_style` 不在预设列表中时，`head_name` 未被赋值导致 `NameError`，现在 fallback 到 `default`

#### 3. `N46Whisper_v26.04.08.ipynb`

- `srt2ass.py` 下载地址更新为 `sananisome/VibeWhisper`，移除旧的 PAT token
- 新增下载 `srt2lrc.py`
- **Cell 8**：import 改为 `from srt2ass import srt2ass` + `from srt2lrc import srt2lrc`
- **Cell 9（ChatGPT 翻译）**：`from srt2ass import srt2lrc` → `from srt2lrc import srt2lrc`
- **Cell 10（Gemini 翻译）**：同上

#### 4. `README.md` / `README_CN.md`

- 标题从 `N46Whisper` 改为 `VibeWhisper`
- 项目简介更新，不再局限于坂道系字幕组
- 输出格式说明新增 LRC
- Colab 链接更新指向 `sananisome/VibeWhisper`

### Bug 修复汇总

| Bug | 文件 | 影响 | 修复方式 |
|-----|------|------|----------|
| Cell 9/10 `from srt2ass import srt2lrc` 找不到函数 | notebook | 翻译后导出 LRC 必崩 | 改为 `from srt2lrc import srt2lrc` |
| SRT 末尾纯数字行导致 `IndexError` | srt2ass.py:57 | 特定 SRT 文件转 ASS 崩溃 | 加边界检查 |
| 多行字幕只保留第一行 | srt2lrc.py | LRC 输出丢失内容 | 收集所有文本行再合并 |
| 未知 sub_style 导致 `NameError` | srt2ass.py:135 | 自定义 style 时崩溃 | fallback 到 default |
| 本地上传多文件只处理第一个 | notebook Cell 4 | 批量转录失效 | `file_names` 改为 `list(uploaded.keys())` |

---

## 2026.4.7 — 新增 LRC 歌词格式字幕输出

### 修改目的

让 N46Whisper 支持输出 LRC 歌词格式字幕，方便用户在音乐播放器等场景使用。

### 修改文件及内容

#### 1. `srt2ass.py`

- 新增 `srt2lrc(input_file)` 函数
  - 读取 SRT 文件，将每行字幕转换为 LRC 格式 `[MM:SS.xx]文本`
  - 时间戳只使用开始时间，小时数折算进分钟（如 `01:02:03` → `[62:03.xx]`）
  - 毫秒取前两位作为厘秒
  - 复用了已有的 `fileopen()` 函数处理编码
  - 输出文件与输入同名，扩展名改为 `.lrc`

#### 2. `N46Whisper.ipynb`

**Cell 6（Required settings / 通用参数）**
- 在 `export_srt` 下方新增 `export_lrc` 下拉选项
- 选项：`["No", "Yes"]`，默认 `"No"`

**Cell 8（Run Whisper / 运行 Whisper）**
- 导入语句新增 `srt2lrc`：`from srt2ass import srt2ass, srt2lrc`
- ASS 生成后，若 `export_lrc == 'Yes'`，调用 `srt2lrc()` 生成 LRC 文件
- 多文件打包 zip 时，若启用 LRC 导出，将 LRC 文件一并打包

**Cell 9（ChatGPT 翻译）**
- `output_format` 下拉选项新增 `"lrc"`
- 修改前：`["ass","srt"]`
- 修改后：`["ass","srt","lrc"]`
- 选择 `lrc` 时：先保存 SRT → 调用 `srt2lrc()` 转换 → 下载 LRC 文件

**Cell 10（Google Gemini 翻译）**
- 同 Cell 9，`output_format` 新增 `"lrc"` 选项及对应保存逻辑

**Cell 15（Ollama 翻译）**
- 同 Cell 9，`output_format` 新增 `"lrc"` 选项及对应保存逻辑

### LRC 格式说明

```
[00:05.23]こんにちは
[00:08.50]今日はいい天気ですね
```

- 每行格式：`[MM:SS.xx]` + 文本
- 仅记录开始时间，无结束时间（LRC 标准规范）
- 广泛用于音乐播放器歌词显示

---

## 2026.4.7 — 新增 ChickenRice-v2 模型 & Whisper-VAD 支持

### 修改目的

让 N46Whisper 支持两个 TransWithAI 项目：
1. [Faster-Whisper-TransWithAI-ChickenRice](https://github.com/TransWithAI/Faster-Whisper-TransWithAI-ChickenRice) — 日语→中文专用 Whisper 模型
2. [whisper-vad](https://github.com/TransWithAI/whisper-vad) — 基于 Whisper 编码器的 VAD 模型

### 修改文件及内容

#### 1. `N46Whisper.ipynb`

**Cell 1（更新日志 Markdown）**
- 在最新更新部分顶部插入 2026.4.7 条目

**Cell 6（Required settings）**
- `model_size` 下拉选项新增 `"ChickenRice-v2"`
- 修改前：`["base","small","medium", "large-v1","large-v2","large-v3"]`
- 修改后：`["base","small","medium", "large-v1","large-v2","large-v3","ChickenRice-v2"]`

**Cell 7（Advanced settings）**
- 在 `is_vad_filter` 参数下方新增 `vad_type` 下拉选项
- 选项：`["Silero", "Whisper-VAD (TransWithAI)"]`，默认 `"Silero"`

**Cell 8（Run Whisper）— 完整重写**

主要改动点：

1. **安装依赖**
   - 新增安装 `faster-whisper-transwithai-chickenrice` 包（pip 安装，失败则从 GitHub 安装）
   - 该包提供 VAD 注入机制（`inject_vad` / `uninject_vad`）

2. **模型名称映射**
   ```python
   MODEL_MAP = {
       "ChickenRice-v2": "chickenrice0721/whisper-large-v2-translate-zh-v0.2-st-ct2",
   }
   actual_model = MODEL_MAP.get(model_size, model_size)
   ```
   - 用户选择 `ChickenRice-v2` 时，实际加载 HuggingFace 上的 CTranslate2 模型
   - 其他模型名称保持原样直接传给 `WhisperModel()`

3. **Whisper-VAD 集成**
   - 当 `vad_type == "Whisper-VAD (TransWithAI)"` 时：
     - 从 HuggingFace (`TransWithAI/Whisper-Vad-EncDec-ASMR-onnx`) 下载 ONNX 模型到 `models/` 目录
     - 通过 `inject_vad()` 将 Whisper-VAD 注入 faster-whisper 的 VAD 管线
     - 注入机制原理：使用 `unittest.mock` 补丁拦截 faster-whisper 内部的 Silero VAD 调用，替换为 Whisper-VAD ONNX 推理
     - 自动将 `vad_filter` 设为 `True`（注入后需要启用才生效）
   - 加载失败时自动回退到 Silero VAD
   - 全部转录完成后调用 `uninject_vad()` 清理

4. **转录状态显示**
   - 打印当前使用的模型名和 VAD 类型，方便用户确认配置

5. **保留的原有逻辑**
   - Google Drive / 本地上传文件处理
   - 视频提取音频（ffmpeg）
   - beam_size 开关
   - SRT/ASS 转换和下载
   - 批量文件处理

#### 2. `README.md`

- "What's Latest" 部分顶部新增 2026.4.7 条目（3 条）
- "Update history" 部分顶部新增 2026.4.7 条目（3 条）
- 移除了原有的 "This project will NO LONGER be maintained" 声明

#### 3. `README_CN.md`

- "最近更新" 部分顶部新增 2026.4.7 条目（3 条）
- "更新日志" 部分顶部新增 2026.4.7 条目（3 条）
- 移除了原有的不再维护声明

### 依赖关系

| 包名 | 用途 | 安装方式 |
|------|------|----------|
| `faster-whisper` | 语音识别核心 | pip（原有） |
| `faster-whisper-transwithai-chickenrice` | VAD 注入机制 | pip / git+https |
| `huggingface_hub` | 下载 ONNX 模型 | 随 faster-whisper 安装 |

### HuggingFace 模型

| 模型 | Repo ID | 说明 |
|------|---------|------|
| ChickenRice-v2 | `chickenrice0721/whisper-large-v2-translate-zh-v0.2-st-ct2` | CTranslate2 格式，~3GB |
| Whisper-VAD ONNX | `TransWithAI/Whisper-Vad-EncDec-ASMR-onnx` | 两个文件：`model.onnx` + `model_metadata.json` |

### 后续维护注意事项

- 如果 ChickenRice 发布新版本模型，更新 `MODEL_MAP` 中的 HuggingFace repo ID 即可
- 如果 Whisper-VAD 更新 ONNX 模型，HuggingFace repo 会自动更新，无需改代码
- `faster-whisper-transwithai-chickenrice` 包的 API 如有变动（`inject_vad` / `uninject_vad` / `VadConfig`），需同步修改 Cell 8
- `vad_type` 变量通过 `if 'vad_type' in dir()` 做了兼容检查，即使用户用旧版 Cell 7 也不会报错
