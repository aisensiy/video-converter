# 视频转换器

一个用于将视频文件（FLV、TS）转换为 MP4 格式的 Python 脚本，同时支持可选的 MP3 音频提取功能。

## 功能特点

- 支持将 FLV 和 TS 视频文件转换为 MP4 格式
- 可选的 MP3 音频提取功能
- 支持单文件和批量目录处理
- 自动跳过小于 100MB 的文件
- 批处理时显示进度条
- 详细的转换统计信息

## 环境要求

- Python 3.x
- FFmpeg

## 安装步骤

1. 确保已安装 Python 3.x
2. 在系统上安装 FFmpeg
3. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 单文件转换

```bash
python convert_to_mp.py <输入文件> <输出目录> [--mp3]
```

### 目录批量处理

```bash
python convert_to_mp.py <输入目录> <输出目录> [--mp3]
```

### 参数说明

- `输入文件/输入目录`：要转换的视频文件路径或包含视频文件的目录路径
- `输出目录`：转换后的文件保存位置
- `--mp3`：（可选）提取音频并保存为 MP3 格式

### 使用示例

转换单个视频文件：

```bash
python convert_to_mp.py ~/videos/input.flv ~/converted
```

转换视频文件并提取 MP3：

```bash
python convert_to_mp.py ~/videos/input.ts ~/converted --mp3
```

处理目录中的所有视频：

```bash
python convert_to_mp.py ~/videos ~/converted
```

## 注意事项

- 仅处理大于 100MB 的文件
- 支持的输入格式：FLV、TS
- 输出视频格式：MP4
- 可选的音频输出格式：MP3
- 使用 FFmpeg 的 copy 模式保留原始视频和音频流
