# PythonCompiler - EXE打包工具

PythonCompiler 是一个使用PyInstaller将Python脚本打包成exe文件的工具，提供了图形界面和命令行两种使用方式。

## 安装

### 1. 安装PyInstaller

**注意**：程序启动时会自动检查并安装以下默认库（如果未安装会自动安装）：
- `pyinstaller` - 主要打包工具
- `setuptools` - Python打包和分发工具
- `wheel` - Python二进制包构建工具
- `pip` - Python包管理工具
- `pefile` - PyInstaller依赖：用于处理PE文件
- `altgraph` - PyInstaller依赖：图形算法库
- `pyinstaller-hooks-contrib` - PyInstaller钩子扩展
- `pywin32-ctypes` - Windows平台支持（仅Windows系统）

也可以手动安装：

```bash
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install pyinstaller
```

## 使用方法

### 方式一：图形界面（推荐）

运行GUI版本：

```bash
python pyinstaller_gui.py
```

功能特点：
- **启动时自动检查并安装默认库**（如pyinstaller）
- 可视化选择Python脚本文件
- 选择输出目录
- 可选添加图标文件
- 设置程序名称
- **自动安装依赖库**：输入库名称，自动下载安装
- 多种打包选项（单文件模式、窗口模式等）
- 实时显示打包日志

### 方式二：命令行

运行命令行版本：

```bash
python pyinstaller_cli.py <脚本路径> [选项]
```

#### 基本用法

```bash
# 基本打包
python pyinstaller_cli.py script.py

# 指定输出目录和程序名称
python pyinstaller_cli.py script.py -o dist -n MyApp

# 添加图标，使用窗口模式（无控制台）
python pyinstaller_cli.py script.py -i icon.ico -w

# 不使用单文件模式（生成文件夹）
python pyinstaller_cli.py script.py --no-onefile

# 自动安装依赖库（打包前自动安装）
python pyinstaller_cli.py script.py -d requests numpy pandas

# 从文件读取依赖库列表
python pyinstaller_cli.py script.py --deps-file requirements.txt
```

#### 命令行参数

- `script`: 要打包的Python脚本路径（必需）
- `-o, --output`: 输出目录（默认: dist）
- `-i, --icon`: 图标文件路径 (.ico)
- `-n, --name`: 程序名称（默认: 脚本文件名）
- `--onefile`: 打包为单文件（默认）
- `--no-onefile`: 不使用单文件模式
- `-w, --windowed`: 窗口模式（无控制台窗口）
- `--clean`: 清理临时文件（默认）
- `--no-clean`: 不清理临时文件
- `--add-arg`: 额外的PyInstaller参数（可多次使用）
- `-d, --dependencies`: 需要安装的依赖库（可指定多个，用空格分隔）
- `--deps-file`: 从文件读取依赖库列表（每行一个库名，支持逗号分隔）
- `--no-auto-install`: 不自动安装依赖库

## 自动安装依赖库功能

### GUI版本
1. 在"依赖库（自动安装）"区域输入需要安装的库名称
2. 支持多种输入方式：
   - 逗号分隔：`requests, numpy, pandas`
   - 换行分隔：每行一个库名
   - 混合使用
3. 勾选"打包前自动安装依赖库"选项（默认启用）
4. 也可以点击"立即安装"按钮单独安装依赖库
5. 打包时会自动先安装所有依赖库，然后再进行打包

### 命令行版本
```bash
# 方式1: 直接在命令行指定
python pyinstaller_cli.py script.py -d requests numpy pandas

# 方式2: 从文件读取（推荐）
# 创建 requirements.txt 文件，每行一个库名
python pyinstaller_cli.py script.py --deps-file requirements.txt

# 禁用自动安装（如果只想打包，不安装依赖）
python pyinstaller_cli.py script.py -d requests --no-auto-install
```

**注意**：
- 依赖库会在打包前自动安装到当前Python环境
- 如果某个库安装失败，会显示警告但继续尝试打包
- 建议使用虚拟环境以避免污染系统Python环境

## 打包选项说明

### 单文件模式 (--onefile)
- **启用**: 生成单个exe文件，所有依赖都打包在一起
- **禁用**: 生成一个文件夹，包含exe和依赖文件

### 窗口模式 (--windowed)
- **启用**: 无控制台窗口，适合GUI程序
- **禁用**: 显示控制台窗口，适合命令行程序

### 清理临时文件 (--clean)
- **启用**: 打包前清理之前的临时文件
- **禁用**: 保留临时文件（可能加快后续打包速度）

## 输出位置

打包完成后，exe文件会生成在：
- 如果指定了输出目录：`<输出目录>/<程序名称>.exe`
- 如果未指定：`dist/<程序名称>.exe`

## 注意事项

1. **默认库自动安装**: 
   - 程序启动时会自动检查并安装必要的默认库（如pyinstaller）
   - 如果检测到缺少默认库，会自动尝试安装
   - 需要网络连接才能自动安装
2. **图标文件**: 图标文件必须是`.ico`格式
3. **依赖库**: 
   - 工具支持自动安装依赖库，只需输入库名称即可
   - 也可以手动安装：`pip install <库名>`
   - 建议使用虚拟环境以避免污染系统Python环境
4. **文件大小**: 单文件模式生成的exe文件会比较大
5. **杀毒软件**: 某些杀毒软件可能会误报，这是正常现象
6. **网络连接**: 自动安装依赖库需要网络连接，确保能访问PyPI

## 常见问题

### Q: 打包后的exe文件很大？
A: 这是正常的，PyInstaller会打包Python解释器和所有依赖。可以使用`--exclude-module`排除不需要的模块。

### Q: 打包后运行报错？
A: 检查是否所有依赖都已正确打包，查看打包日志中的警告信息。

### Q: 如何减小exe文件大小？
A: 
- 使用虚拟环境，只安装必要的依赖
- 使用`--exclude-module`排除不需要的模块
- 考虑使用`--no-onefile`模式

## 许可证

MIT License

