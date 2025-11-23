#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PythonCompiler - PyInstaller 命令行打包工具
使用命令行方式将Python脚本打包成exe文件
"""

import argparse
import subprocess
import os
import sys
import importlib.util

# 默认需要安装的库列表
# 包括PyInstaller及其依赖，以及常用的打包工具库
DEFAULT_LIBRARIES = [
    'pyinstaller',           # 主要打包工具
    'setuptools',            # Python打包和分发工具
    'wheel',                 # Python二进制包构建工具
    'pip',                   # Python包管理工具（通常已安装，但确保可用）
    'pefile',                # PyInstaller依赖：用于处理PE文件
    'altgraph',              # PyInstaller依赖：图形算法库
    'pyinstaller-hooks-contrib',  # PyInstaller钩子扩展
    'pywin32-ctypes',        # Windows平台支持（Windows系统）
]


def is_package_installed(package_name):
    """检查包是否已安装"""
    try:
        # 对于特殊包，使用pip show检查
        if package_name in ['pyinstaller', 'setuptools', 'wheel', 'pip']:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        # 对于其他包，尝试导入
        # 处理带连字符的包名（如pyinstaller-hooks-contrib）
        import_name = package_name.replace('-', '_')
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            # 如果导入失败，尝试用pip show检查
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        return spec is not None
    except Exception:
        return False


def check_and_install_default_libs(verbose=True):
    """检查并安装默认库"""
    # 根据平台过滤库（例如pywin32-ctypes只在Windows上需要）
    libraries_to_check = []
    for lib in DEFAULT_LIBRARIES:
        # Windows平台才需要pywin32-ctypes
        if lib == 'pywin32-ctypes':
            if sys.platform == 'win32':
                libraries_to_check.append(lib)
        else:
            libraries_to_check.append(lib)
    
    missing_libs = []
    for lib in libraries_to_check:
        if not is_package_installed(lib):
            missing_libs.append(lib)
    
    if missing_libs:
        if verbose:
            print("=" * 60)
            print("检测到缺少必要的库，正在自动安装...")
            print(f"需要安装: {', '.join(missing_libs)}")
            print("=" * 60)
        
        success, failed_deps = install_dependencies(missing_libs, verbose=verbose)
        
        if not success:
            if verbose:
                print(f"警告: 以下默认库安装失败: {', '.join(failed_deps)}")
                print("请手动安装: pip install " + " ".join(failed_deps))
            return False
        else:
            if verbose:
                print("所有默认库安装完成！")
            return True
    else:
        if verbose:
            print("所有默认库已安装 ✓")
        return True


def install_dependencies(dependencies, verbose=True):
    """
    安装依赖库
    
    参数:
        dependencies: 依赖库列表
        verbose: 是否显示详细输出
    
    返回:
        (success: bool, failed_deps: list)
    """
    if not dependencies:
        return True, []
    
    print("=" * 60)
    print("开始安装依赖库...")
    print(f"需要安装的库: {', '.join(dependencies)}")
    print("=" * 60)
    
    failed_deps = []
    for dep in dependencies:
        try:
            if verbose:
                print(f"\n正在安装: {dep}")
            
            cmd = [sys.executable, "-m", "pip", "install", dep]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE if not verbose else None,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                if verbose:
                    print(f"✓ {dep} 安装成功")
            else:
                if verbose:
                    print(f"✗ {dep} 安装失败")
                failed_deps.append(dep)
                
        except Exception as e:
            if verbose:
                print(f"安装 {dep} 时发生错误: {str(e)}")
            failed_deps.append(dep)
    
    print("=" * 60)
    if not failed_deps:
        print("所有依赖库安装完成！")
    else:
        print(f"以下库安装失败: {', '.join(failed_deps)}")
    print("=" * 60)
    
    return len(failed_deps) == 0, failed_deps


def build_exe(script_path, output_dir=None, icon_path=None, name=None,
              onefile=True, windowed=False, clean=True, additional_args=None,
              dependencies=None, auto_install=True):
    """
    使用PyInstaller打包Python脚本为exe
    
    参数:
        script_path: Python脚本路径
        output_dir: 输出目录
        icon_path: 图标文件路径
        name: 程序名称
        onefile: 是否打包为单文件
        windowed: 是否使用窗口模式（无控制台）
        clean: 是否清理临时文件
        additional_args: 额外的PyInstaller参数列表
        dependencies: 需要安装的依赖库列表
        auto_install: 是否自动安装依赖库
    """
    if not os.path.exists(script_path):
        print(f"错误: 找不到脚本文件: {script_path}")
        return False
    
    # 如果启用了自动安装，先安装依赖库
    if auto_install and dependencies:
        success, failed_deps = install_dependencies(dependencies)
        if failed_deps:
            print(f"警告: 以下库安装失败: {', '.join(failed_deps)}")
            print("将继续尝试打包...")
    
    # 构建命令
    cmd = ["pyinstaller"]
    
    # 输出目录
    if output_dir:
        cmd.extend(["--distpath", output_dir])
    
    # 图标
    if icon_path:
        if os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
        else:
            print(f"警告: 图标文件不存在: {icon_path}")
    
    # 程序名称
    if name:
        cmd.extend(["--name", name])
    
    # 选项
    if onefile:
        cmd.append("--onefile")
    
    if windowed:
        cmd.append("--windowed")
    
    if clean:
        cmd.append("--clean")
    
    # 额外参数
    if additional_args:
        cmd.extend(additional_args)
    
    # 添加脚本路径
    cmd.append(script_path)
    
    print("=" * 60)
    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # 执行命令
        result = subprocess.run(cmd, check=True)
        
        print("=" * 60)
        print("打包成功！")
        if output_dir:
            print(f"输出目录: {os.path.abspath(output_dir)}")
        else:
            print(f"输出目录: {os.path.abspath('dist')}")
        print("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"打包失败！错误代码: {e.returncode}")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="PythonCompiler - EXE打包工具（命令行版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本打包
  python pyinstaller_cli.py script.py
  
  # 指定输出目录和名称
  python pyinstaller_cli.py script.py -o dist -n MyApp
  
  # 添加图标，窗口模式
  python pyinstaller_cli.py script.py -i icon.ico -w
  
  # 不使用单文件模式
  python pyinstaller_cli.py script.py --no-onefile
  
  # 自动安装依赖库
  python pyinstaller_cli.py script.py -d requests numpy pandas
  
  # 从文件读取依赖库
  python pyinstaller_cli.py script.py --deps-file requirements.txt
        """
    )
    
    parser.add_argument("script", help="要打包的Python脚本路径")
    parser.add_argument("-o", "--output", dest="output_dir", 
                       help="输出目录（默认: dist）")
    parser.add_argument("-i", "--icon", dest="icon_path",
                       help="图标文件路径 (.ico)")
    parser.add_argument("-n", "--name", dest="name",
                       help="程序名称（默认: 脚本文件名）")
    parser.add_argument("--onefile", action="store_true", default=True,
                       help="打包为单文件（默认）")
    parser.add_argument("--no-onefile", dest="onefile", action="store_false",
                       help="不使用单文件模式")
    parser.add_argument("-w", "--windowed", action="store_true",
                       help="窗口模式（无控制台窗口）")
    parser.add_argument("--clean", action="store_true", default=True,
                       help="清理临时文件（默认）")
    parser.add_argument("--no-clean", dest="clean", action="store_false",
                       help="不清理临时文件")
    parser.add_argument("--add-arg", dest="additional_args", action="append",
                       help="额外的PyInstaller参数（可多次使用）")
    parser.add_argument("-d", "--dependencies", dest="dependencies", nargs="+",
                       help="需要安装的依赖库（可指定多个，用空格分隔）")
    parser.add_argument("--deps-file", dest="deps_file",
                       help="从文件读取依赖库列表（每行一个库名）")
    parser.add_argument("--no-auto-install", dest="auto_install", action="store_false",
                       default=True, help="不自动安装依赖库")
    
    args = parser.parse_args()
    
    # 检查并安装默认库（如pyinstaller）
    if not check_and_install_default_libs(verbose=True):
        print("错误: 无法安装必要的默认库，程序无法继续")
        sys.exit(1)
    
    # 处理依赖库
    dependencies = []
    if args.dependencies:
        dependencies.extend(args.dependencies)
    if args.deps_file:
        if os.path.exists(args.deps_file):
            with open(args.deps_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 支持逗号分隔
                        for dep in line.split(','):
                            dep = dep.strip()
                            if dep:
                                dependencies.append(dep)
        else:
            print(f"警告: 依赖文件不存在: {args.deps_file}")
    
    # 去重
    dependencies = list(set(dependencies))
    
    # 如果没有指定名称，使用脚本文件名
    if not args.name:
        args.name = os.path.splitext(os.path.basename(args.script))[0]
    
    success = build_exe(
        script_path=args.script,
        output_dir=args.output_dir,
        icon_path=args.icon_path,
        name=args.name,
        onefile=args.onefile,
        windowed=args.windowed,
        clean=args.clean,
        additional_args=args.additional_args,
        dependencies=dependencies,
        auto_install=args.auto_install
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

