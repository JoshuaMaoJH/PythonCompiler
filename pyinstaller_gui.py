#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PythonCompiler - PyInstaller GUI打包工具
使用图形界面帮助用户将Python脚本打包成exe文件
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import sys
import threading
import importlib.util


class PyInstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PythonCompiler - EXE打包工具")
        self.root.geometry("700x700")
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass  # 如果设置图标失败，继续运行
        
        # 变量
        self.script_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.name = tk.StringVar()
        self.onefile = tk.BooleanVar(value=True)
        self.windowed = tk.BooleanVar(value=False)
        self.clean = tk.BooleanVar(value=True)
        self.auto_install = tk.BooleanVar(value=True)
        
        # 默认需要安装的库列表
        # 包括PyInstaller及其依赖，以及常用的打包工具库
        self.default_libraries = [
            'pyinstaller',           # 主要打包工具
            'setuptools',            # Python打包和分发工具
            'wheel',                 # Python二进制包构建工具
            'pip',                   # Python包管理工具（通常已安装，但确保可用）
            'pefile',                # PyInstaller依赖：用于处理PE文件
            'altgraph',              # PyInstaller依赖：图形算法库
            'pyinstaller-hooks-contrib',  # PyInstaller钩子扩展
            'pywin32-ctypes',        # Windows平台支持（Windows系统）
        ]
        
        self.setup_ui()
        # 启动时检查并安装默认库
        self.check_and_install_default_libs()
        
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = tk.Label(self.root, text="PythonCompiler", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        subtitle_label = tk.Label(self.root, text="Python脚本打包成EXE工具", 
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 10))
        
        # Python脚本选择
        script_frame = tk.Frame(self.root)
        script_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(script_frame, text="Python脚本:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(script_frame, textvariable=self.script_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(script_frame, text="浏览", command=self.browse_script).pack(side=tk.LEFT)
        
        # 输出目录
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(output_frame, text="输出目录:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="浏览", command=self.browse_output).pack(side=tk.LEFT)
        
        # 图标文件（可选）
        icon_frame = tk.Frame(self.root)
        icon_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(icon_frame, text="图标文件:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(icon_frame, textvariable=self.icon_path, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(icon_frame, text="浏览", command=self.browse_icon).pack(side=tk.LEFT)
        tk.Button(icon_frame, text="清除", command=lambda: self.icon_path.set("")).pack(side=tk.LEFT)
        
        # 程序名称
        name_frame = tk.Frame(self.root)
        name_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(name_frame, text="程序名称:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(name_frame, textvariable=self.name, width=50).pack(side=tk.LEFT, padx=5)
        
        # 依赖库输入
        deps_frame = tk.LabelFrame(self.root, text="依赖库（自动安装）", padx=10, pady=10)
        deps_frame.pack(fill=tk.X, padx=20, pady=5)
        
        deps_label = tk.Label(deps_frame, text="输入需要安装的库名称，多个库用逗号或换行分隔:\n例如: requests, numpy, pandas 或每行一个库名")
        deps_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.deps_text = tk.Text(deps_frame, height=4, font=("Consolas", 9))
        self.deps_text.pack(fill=tk.X, pady=5)
        
        deps_check_frame = tk.Frame(deps_frame)
        deps_check_frame.pack(fill=tk.X)
        tk.Checkbutton(deps_check_frame, text="打包前自动安装依赖库", 
                      variable=self.auto_install).pack(side=tk.LEFT)
        tk.Button(deps_check_frame, text="立即安装", command=self.install_dependencies,
                 bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=10)
        
        # 选项框架
        options_frame = tk.LabelFrame(self.root, text="打包选项", padx=10, pady=10)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Checkbutton(options_frame, text="单文件模式 (--onefile)", 
                      variable=self.onefile).pack(anchor=tk.W)
        tk.Checkbutton(options_frame, text="窗口模式 (--windowed, 无控制台)", 
                      variable=self.windowed).pack(anchor=tk.W)
        tk.Checkbutton(options_frame, text="清理临时文件 (--clean)", 
                      variable=self.clean).pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="开始打包", command=self.start_build, 
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="清空日志", command=self.clear_log, 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # 日志输出
        log_frame = tk.LabelFrame(self.root, text="打包日志", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                   font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_script(self):
        """浏览选择Python脚本"""
        filename = filedialog.askopenfilename(
            title="选择Python脚本",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if filename:
            self.script_path.set(filename)
            # 自动设置输出目录为脚本所在目录
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))
            # 自动设置程序名称
            if not self.name.get():
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.name.set(base_name)
    
    def browse_output(self):
        """浏览选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def browse_icon(self):
        """浏览选择图标文件"""
        filename = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)
    
    def log(self, message):
        """在日志区域输出信息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def is_package_installed(self, package_name):
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
    
    def check_and_install_default_libs(self):
        """检查并安装默认库"""
        # 根据平台过滤库（例如pywin32-ctypes只在Windows上需要）
        libraries_to_check = []
        for lib in self.default_libraries:
            # Windows平台才需要pywin32-ctypes
            if lib == 'pywin32-ctypes':
                if sys.platform == 'win32':
                    libraries_to_check.append(lib)
            else:
                libraries_to_check.append(lib)
        
        missing_libs = []
        for lib in libraries_to_check:
            if not self.is_package_installed(lib):
                missing_libs.append(lib)
        
        if missing_libs:
            self.log("=" * 60)
            self.log("检测到缺少必要的库，正在自动安装...")
            self.log(f"需要安装: {', '.join(missing_libs)}")
            self.log("=" * 60)
            
            # 在新线程中安装，避免阻塞UI
            thread = threading.Thread(
                target=self._install_default_libs,
                args=(missing_libs,),
                daemon=True
            )
            thread.start()
        else:
            self.log("=" * 60)
            self.log("所有默认库已安装 ✓")
            self.log("=" * 60)
    
    def _install_default_libs(self, libs):
        """安装默认库（在后台线程中执行）"""
        failed_libs = []
        for lib in libs:
            try:
                self.log(f"\n正在安装: {lib}")
                cmd = [sys.executable, "-m", "pip", "install", lib]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                for line in process.stdout:
                    self.log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log(f"✓ {lib} 安装成功")
                else:
                    self.log(f"✗ {lib} 安装失败")
                    failed_libs.append(lib)
                    
            except Exception as e:
                error_msg = f"安装 {lib} 时发生错误: {str(e)}"
                self.log(error_msg)
                failed_libs.append(lib)
        
        self.log("=" * 60)
        if not failed_libs:
            self.log("所有默认库安装完成！")
        else:
            self.log(f"以下库安装失败: {', '.join(failed_libs)}")
            self.log("请手动安装: pip install " + " ".join(failed_libs))
        self.log("=" * 60)
    
    def parse_dependencies(self):
        """解析依赖库列表"""
        deps_text = self.deps_text.get(1.0, tk.END).strip()
        if not deps_text:
            return []
        
        # 支持逗号和换行分隔
        deps = []
        for line in deps_text.split('\n'):
            line = line.strip()
            if line:
                # 处理逗号分隔的情况
                for dep in line.split(','):
                    dep = dep.strip()
                    if dep:
                        deps.append(dep)
        
        return list(set(deps))  # 去重
    
    def install_dependencies(self):
        """安装依赖库"""
        deps = self.parse_dependencies()
        if not deps:
            messagebox.showwarning("警告", "请输入要安装的库名称！")
            return
        
        self.log("=" * 60)
        self.log("开始安装依赖库...")
        self.log(f"需要安装的库: {', '.join(deps)}")
        self.log("=" * 60)
        
        failed_deps = []
        for dep in deps:
            try:
                self.log(f"\n正在安装: {dep}")
                cmd = [sys.executable, "-m", "pip", "install", dep]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                for line in process.stdout:
                    self.log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log(f"✓ {dep} 安装成功")
                else:
                    self.log(f"✗ {dep} 安装失败")
                    failed_deps.append(dep)
                    
            except Exception as e:
                error_msg = f"安装 {dep} 时发生错误: {str(e)}"
                self.log(error_msg)
                failed_deps.append(dep)
        
        self.log("=" * 60)
        if not failed_deps:
            self.log("所有依赖库安装完成！")
            messagebox.showinfo("成功", "所有依赖库安装完成！")
        else:
            self.log(f"以下库安装失败: {', '.join(failed_deps)}")
            messagebox.showwarning("警告", f"以下库安装失败:\n{', '.join(failed_deps)}")
        self.log("=" * 60)
    
    def build_exe(self):
        """执行打包操作"""
        try:
            script = self.script_path.get()
            if not script or not os.path.exists(script):
                messagebox.showerror("错误", "请选择有效的Python脚本文件！")
                return
            
            # 如果启用了自动安装，先安装依赖库
            if self.auto_install.get():
                deps = self.parse_dependencies()
                if deps:
                    self.log("=" * 60)
                    self.log("自动安装依赖库...")
                    self.log("=" * 60)
                    
                    failed_deps = []
                    for dep in deps:
                        try:
                            self.log(f"正在安装: {dep}")
                            cmd = [sys.executable, "-m", "pip", "install", dep]
                            
                            process = subprocess.Popen(
                                cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True,
                                encoding='utf-8',
                                errors='replace'
                            )
                            
                            for line in process.stdout:
                                self.log(line.rstrip())
                            
                            process.wait()
                            
                            if process.returncode == 0:
                                self.log(f"✓ {dep} 安装成功")
                            else:
                                self.log(f"✗ {dep} 安装失败")
                                failed_deps.append(dep)
                                
                        except Exception as e:
                            error_msg = f"安装 {dep} 时发生错误: {str(e)}"
                            self.log(error_msg)
                            failed_deps.append(dep)
                    
                    if failed_deps:
                        self.log(f"警告: 以下库安装失败: {', '.join(failed_deps)}")
                        self.log("将继续尝试打包...")
                    else:
                        self.log("所有依赖库安装完成！")
                    
                    self.log("=" * 60)
            
            # 构建pyinstaller命令
            cmd = ["pyinstaller"]
            
            # 输出目录
            if self.output_dir.get():
                cmd.extend(["--distpath", self.output_dir.get()])
            
            # 图标
            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                cmd.extend(["--icon", self.icon_path.get()])
            
            # 程序名称
            if self.name.get():
                cmd.extend(["--name", self.name.get()])
            
            # 选项
            if self.onefile.get():
                cmd.append("--onefile")
            
            if self.windowed.get():
                cmd.append("--windowed")
            
            if self.clean.get():
                cmd.append("--clean")
            
            # 添加脚本路径
            cmd.append(script)
            
            self.log("=" * 60)
            self.log("开始打包...")
            self.log(f"命令: {' '.join(cmd)}")
            self.log("=" * 60)
            
            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 实时输出日志
            for line in process.stdout:
                self.log(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log("=" * 60)
                self.log("打包成功！")
                output_path = self.output_dir.get() or "dist"
                self.log(f"输出目录: {os.path.abspath(output_path)}")
                messagebox.showinfo("成功", f"打包完成！\n输出目录: {os.path.abspath(output_path)}")
            else:
                self.log("=" * 60)
                self.log("打包失败！")
                messagebox.showerror("错误", "打包失败，请查看日志信息！")
                
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("错误", error_msg)
    
    def start_build(self):
        """在新线程中开始打包"""
        thread = threading.Thread(target=self.build_exe, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

