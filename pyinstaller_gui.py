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
    """PyInstaller GUI打包工具主类"""
    
    # 默认需要安装的库列表
    DEFAULT_LIBRARIES = [
        'pyinstaller',
        'setuptools',
        'wheel',
        'pefile',
        'altgraph',
        'pyinstaller-hooks-contrib',
    ]
    
    def __init__(self, root):
        self.root = root
        self._init_window()
        self._init_variables()
        self._init_ui()
        
        # 仅在开发环境检查默认库（exe环境中已包含）
        if not getattr(sys, 'frozen', False):
            self._check_default_libs()
    
    def _init_window(self):
        """初始化窗口"""
        self.root.title("PythonCompiler - EXE打包工具")
        self.root.geometry("750x750")
        self.root.resizable(True, True)
        
        # 设置窗口图标（支持打包后的exe环境）
        self._set_window_icon()
    
    def _get_resource_path(self, filename):
        """获取资源文件路径（支持打包后的exe环境）"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            base_path = sys._MEIPASS
        else:
            # 开发环境
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, filename)
    
    def _set_window_icon(self, icon_path=None):
        """设置窗口图标"""
        if icon_path is None:
            # 使用默认图标
            icon_path = self._get_resource_path("favicon.ico")
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
    
    def _init_variables(self):
        """初始化变量"""
        self.script_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.name = tk.StringVar()
        self.onefile = tk.BooleanVar(value=True)
        self.windowed = tk.BooleanVar(value=False)
        self.clean = tk.BooleanVar(value=True)
        self.auto_install = tk.BooleanVar(value=True)
        self.pack_directory = tk.BooleanVar(value=False)  # 是否打包整个目录
        self.main_script = tk.StringVar()  # 目录模式下的主入口文件
    
    def _init_ui(self):
        """初始化用户界面"""
        # 标题区域
        self._create_header()
        
        # 基本配置区域
        self._create_basic_config()
        
        # 依赖库区域
        self._create_dependencies_section()
        
        # 打包选项区域
        self._create_options_section()
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 日志输出区域
        self._create_log_section()
    
    def _create_header(self):
        """创建标题区域"""
        header = tk.Frame(self.root)
        header.pack(pady=15)
        
        title = tk.Label(header, text="PythonCompiler", 
                        font=("Arial", 18, "bold"))
        title.pack()
        
        subtitle = tk.Label(header, text="Python脚本打包成EXE工具", 
                           font=("Arial", 10))
        subtitle.pack(pady=(5, 0))
    
    def _create_basic_config(self):
        """创建基本配置区域"""
        config_frame = tk.LabelFrame(self.root, text="基本配置", padx=15, pady=10)
        config_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 打包模式选择
        mode_frame = tk.Frame(config_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        tk.Label(mode_frame, text="打包模式:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="单个文件", variable=self.pack_directory, 
                      value=False, command=self._on_mode_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="整个目录", variable=self.pack_directory, 
                      value=True, command=self._on_mode_change).pack(side=tk.LEFT, padx=10)
        
        # Python脚本/目录
        self._create_file_input(config_frame, "Python脚本:", 
                               self.script_path, self._browse_script)
        
        # 主入口文件（仅在目录模式下显示）
        self.main_script_frame = tk.Frame(config_frame)
        self._create_file_input(self.main_script_frame, "主入口文件:", 
                               self.main_script, self._browse_main_script)
        self.main_script_frame.pack_forget()  # 默认隐藏
        
        # 输出目录
        self._create_file_input(config_frame, "输出目录:", 
                               self.output_dir, self._browse_output, is_dir=True)
        
        # 图标文件
        icon_frame = tk.Frame(config_frame)
        icon_frame.pack(fill=tk.X, pady=5)
        tk.Label(icon_frame, text="图标文件:", width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(icon_frame, textvariable=self.icon_path, width=45).pack(side=tk.LEFT, padx=5)
        tk.Button(icon_frame, text="浏览", command=self._browse_icon, width=8).pack(side=tk.LEFT)
        tk.Button(icon_frame, text="清除", command=self._clear_icon, width=8).pack(side=tk.LEFT, padx=2)
        
        # 程序名称
        self._create_file_input(config_frame, "程序名称:", self.name)
    
    def _create_file_input(self, parent, label_text, variable, browse_cmd=None, is_dir=False):
        """创建文件输入框"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label_text, width=12, anchor="w").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable, width=45).pack(side=tk.LEFT, padx=5)
        
        if browse_cmd:
            tk.Button(frame, text="浏览", command=browse_cmd, width=8).pack(side=tk.LEFT)
    
    def _create_dependencies_section(self):
        """创建依赖库区域"""
        deps_frame = tk.LabelFrame(self.root, text="依赖库管理", padx=15, pady=10)
        deps_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(deps_frame, 
                text="输入需要安装的库名称（多个库用逗号或换行分隔）",
                font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 5))
        
        self.deps_text = tk.Text(deps_frame, height=4, font=("Consolas", 9))
        self.deps_text.pack(fill=tk.X, pady=5)
        
        controls = tk.Frame(deps_frame)
        controls.pack(fill=tk.X)
        
        tk.Checkbutton(controls, text="打包前自动安装依赖库", 
                      variable=self.auto_install).pack(side=tk.LEFT)
        tk.Button(controls, text="立即安装", command=self._install_dependencies,
                 bg="#2196F3", fg="white", width=12).pack(side=tk.RIGHT)
    
    def _create_options_section(self):
        """创建打包选项区域"""
        options_frame = tk.LabelFrame(self.root, text="打包选项", padx=15, pady=10)
        options_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Checkbutton(options_frame, text="单文件模式 (--onefile)", 
                      variable=self.onefile).pack(anchor=tk.W, pady=3)
        tk.Checkbutton(options_frame, text="窗口模式 (--windowed, 无控制台)", 
                      variable=self.windowed).pack(anchor=tk.W, pady=3)
        tk.Checkbutton(options_frame, text="清理临时文件 (--clean)", 
                      variable=self.clean).pack(anchor=tk.W, pady=3)
    
    def _create_action_buttons(self):
        """创建操作按钮区域"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="开始打包", command=self._start_build,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="清空日志", command=self._clear_log,
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
    
    def _create_log_section(self):
        """创建日志输出区域"""
        log_frame = tk.LabelFrame(self.root, text="打包日志", padx=15, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                  font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    # ========== 文件浏览方法 ==========
    
    def _on_mode_change(self):
        """打包模式改变时的回调"""
        if self.pack_directory.get():
            # 目录模式
            self.main_script_frame.pack(fill=tk.X, pady=5)
            # 更新标签
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.LabelFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label) and subchild.cget("text") == "Python脚本:":
                                    subchild.config(text="项目目录:")
        else:
            # 单文件模式
            self.main_script_frame.pack_forget()
            # 恢复标签
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.LabelFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label) and subchild.cget("text") == "项目目录:":
                                    subchild.config(text="Python脚本:")
    
    def _browse_script(self):
        """浏览选择Python脚本或目录"""
        if self.pack_directory.get():
            # 目录模式：选择目录
            directory = filedialog.askdirectory(title="选择项目目录")
            if directory:
                self.script_path.set(directory)
                if not self.output_dir.get():
                    self.output_dir.set(directory)
                if not self.name.get():
                    self.name.set(os.path.basename(directory))
                
                # 自动查找主入口文件
                main_files = ['main.py', '__main__.py', 'app.py', 'run.py']
                for main_file in main_files:
                    main_path = os.path.join(directory, main_file)
                    if os.path.exists(main_path):
                        self.main_script.set(main_path)
                        break
        else:
            # 单文件模式：选择文件
            filename = filedialog.askopenfilename(
                title="选择Python脚本",
                filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
            )
            if filename:
                self.script_path.set(filename)
                if not self.output_dir.get():
                    self.output_dir.set(os.path.dirname(filename))
                if not self.name.get():
                    base_name = os.path.splitext(os.path.basename(filename))[0]
                    self.name.set(base_name)
    
    def _browse_output(self):
        """浏览选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def _browse_main_script(self):
        """浏览选择主入口文件"""
        # 如果已选择项目目录，限制在项目目录内选择
        project_dir = self.script_path.get()
        if project_dir and os.path.isdir(project_dir):
            initial_dir = project_dir
        else:
            initial_dir = None
        
        filename = filedialog.askopenfilename(
            title="选择主入口文件",
            initialdir=initial_dir,
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        if filename:
            # 验证文件是否在项目目录内
            if project_dir and os.path.isdir(project_dir):
                try:
                    common_path = os.path.commonpath([os.path.abspath(project_dir), os.path.abspath(filename)])
                    if common_path != os.path.abspath(project_dir):
                        messagebox.showwarning("警告", "主入口文件必须在项目目录内！")
                        return
                except ValueError:
                    messagebox.showwarning("警告", "主入口文件必须在项目目录内！")
                    return
            self.main_script.set(filename)
    
    def _browse_icon(self):
        """浏览选择图标文件（仅用于打包，不影响窗口图标）"""
        filename = filedialog.askopenfilename(
            title="选择图标文件",
            filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
        )
        if filename:
            self.icon_path.set(filename)
            # 注意：不更新窗口图标，窗口图标始终使用favicon.ico
    
    def _clear_icon(self):
        """清除图标文件"""
        self.icon_path.set("")
        # 窗口图标保持不变（始终使用favicon.ico）
    
    # ========== 日志方法 ==========
    
    def _log(self, message):
        """在日志区域输出信息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    # ========== 库检查与安装方法 ==========
    
    def _is_package_installed(self, package_name):
        """检查包是否已安装"""
        try:
            if package_name in ['pyinstaller', 'setuptools', 'wheel', 'pip']:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                return result.returncode == 0
            
            import_name = package_name.replace('-', '_')
            spec = importlib.util.find_spec(import_name)
            if spec is None:
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
    
    def _check_default_libs(self):
        """检查并安装默认库"""
        libraries_to_check = [
            lib for lib in self.DEFAULT_LIBRARIES
            if not (lib == 'pywin32-ctypes' and sys.platform != 'win32')
        ]
        
        missing_libs = [
            lib for lib in libraries_to_check
            if not self._is_package_installed(lib)
        ]
        
        if missing_libs:
            self._log("=" * 60)
            self._log("检测到缺少必要的库，正在自动安装...")
            self._log(f"需要安装: {', '.join(missing_libs)}")
            self._log("=" * 60)
            
            thread = threading.Thread(
                target=self._install_libs,
                args=(missing_libs,),
                daemon=True
            )
            thread.start()
        else:
            self._log("=" * 60)
            self._log("所有默认库已安装 ✓")
            self._log("=" * 60)
    
    def _install_libs(self, libs):
        """安装库（在后台线程中执行）"""
        failed_libs = []
        for lib in libs:
            try:
                self._log(f"\n正在安装: {lib}")
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
                    self._log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self._log(f"✓ {lib} 安装成功")
                else:
                    self._log(f"✗ {lib} 安装失败")
                    failed_libs.append(lib)
            except Exception as e:
                self._log(f"安装 {lib} 时发生错误: {str(e)}")
                failed_libs.append(lib)
        
        self._log("=" * 60)
        if not failed_libs:
            self._log("所有库安装完成！")
        else:
            self._log(f"以下库安装失败: {', '.join(failed_libs)}")
        self._log("=" * 60)
    
    def _parse_dependencies(self):
        """解析依赖库列表"""
        deps_text = self.deps_text.get(1.0, tk.END).strip()
        if not deps_text:
            return []
        
        deps = []
        for line in deps_text.split('\n'):
            line = line.strip()
            if line:
                for dep in line.split(','):
                    dep = dep.strip()
                    if dep:
                        deps.append(dep)
        
        return list(set(deps))
    
    def _install_dependencies(self):
        """安装用户指定的依赖库"""
        deps = self._parse_dependencies()
        if not deps:
            messagebox.showwarning("警告", "请输入要安装的库名称！")
            return
        
        self._log("=" * 60)
        self._log("开始安装依赖库...")
        self._log(f"需要安装的库: {', '.join(deps)}")
        self._log("=" * 60)
        
        thread = threading.Thread(
            target=self._install_libs_with_feedback,
            args=(deps,),
            daemon=True
        )
        thread.start()
    
    def _install_libs_with_feedback(self, deps):
        """安装依赖库并显示反馈"""
        failed_deps = []
        for dep in deps:
            try:
                self._log(f"\n正在安装: {dep}")
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
                    self._log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self._log(f"✓ {dep} 安装成功")
                else:
                    self._log(f"✗ {dep} 安装失败")
                    failed_deps.append(dep)
            except Exception as e:
                self._log(f"安装 {dep} 时发生错误: {str(e)}")
                failed_deps.append(dep)
        
        self._log("=" * 60)
        if not failed_deps:
            self._log("所有依赖库安装完成！")
            self.root.after(0, lambda: messagebox.showinfo("成功", "所有依赖库安装完成！"))
        else:
            self._log(f"以下库安装失败: {', '.join(failed_deps)}")
            self.root.after(0, lambda: messagebox.showwarning(
                "警告", f"以下库安装失败:\n{', '.join(failed_deps)}"))
        self._log("=" * 60)
    
    # ========== 打包方法 ==========
    
    def _start_build(self):
        """在新线程中开始打包"""
        thread = threading.Thread(target=self._build_exe, daemon=True)
        thread.start()
    
    def _find_python_files(self, directory):
        """查找目录中的所有Python文件"""
        python_files = []
        for root, dirs, files in os.walk(directory):
            # 排除常见的非打包目录
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', '.venv', 'node_modules', 'dist', 'build']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def _build_exe(self):
        """执行打包操作"""
        try:
            script = self.script_path.get()
            if not script or not os.path.exists(script):
                error_msg = "请选择有效的Python脚本文件！" if not self.pack_directory.get() else "请选择有效的项目目录！"
                messagebox.showerror("错误", error_msg)
                return
            
            # 如果是目录模式，需要主入口文件
            if self.pack_directory.get():
                if not os.path.isdir(script):
                    messagebox.showerror("错误", "请选择有效的项目目录！")
                    return
                
                main_script = self.main_script.get()
                if not main_script or not os.path.exists(main_script):
                    messagebox.showerror("错误", "请指定主入口文件！")
                    return
                
                # 确保主入口文件在项目目录内
                if not os.path.commonpath([script, main_script]) == os.path.abspath(script):
                    messagebox.showerror("错误", "主入口文件必须在项目目录内！")
                    return
                
                entry_script = main_script
            else:
                if not os.path.isfile(script):
                    messagebox.showerror("错误", "请选择有效的Python脚本文件！")
                    return
                entry_script = script
            
            # 自动安装依赖库
            if self.auto_install.get():
                deps = self._parse_dependencies()
                if deps:
                    self._log("=" * 60)
                    self._log("自动安装依赖库...")
                    self._log("=" * 60)
                    
                    failed_deps = []
                    for dep in deps:
                        try:
                            self._log(f"正在安装: {dep}")
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
                                self._log(line.rstrip())
                            
                            process.wait()
                            
                            if process.returncode == 0:
                                self._log(f"✓ {dep} 安装成功")
                            else:
                                self._log(f"✗ {dep} 安装失败")
                                failed_deps.append(dep)
                        except Exception as e:
                            self._log(f"安装 {dep} 时发生错误: {str(e)}")
                            failed_deps.append(dep)
                    
                    if failed_deps:
                        self._log(f"警告: 以下库安装失败: {', '.join(failed_deps)}")
                        self._log("将继续尝试打包...")
                    else:
                        self._log("所有依赖库安装完成！")
                    
                    self._log("=" * 60)
            
            # 构建pyinstaller命令
            cmd = ["pyinstaller"]
            
            if self.output_dir.get():
                cmd.extend(["--distpath", self.output_dir.get()])
            
            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                cmd.extend(["--icon", self.icon_path.get()])
            
            if self.name.get():
                cmd.extend(["--name", self.name.get()])
            
            if self.onefile.get():
                cmd.append("--onefile")
            
            if self.windowed.get():
                cmd.append("--windowed")
            
            if self.clean.get():
                cmd.append("--clean")
            
            # 如果是目录模式，添加项目路径和所有文件
            if self.pack_directory.get():
                # 添加项目目录到Python路径，让PyInstaller自动发现模块
                cmd.extend(["--paths", script])
                
                # 添加项目目录中的所有非Python文件（数据文件）
                # 使用--add-data将整个目录包含进去
                separator = ";" if sys.platform == "win32" else ":"
                cmd.extend(["--add-data", f"{script}{separator}."])
                
                # 添加所有Python模块作为隐藏导入（确保都被包含）
                python_files = self._find_python_files(script)
                imported_modules = set()
                for py_file in python_files:
                    rel_path = os.path.relpath(py_file, script)
                    # 转换为模块名
                    parts = rel_path.replace('.py', '').split(os.sep)
                    if parts and parts[0]:
                        # 构建模块路径
                        module_parts = []
                        for part in parts:
                            if part and part != '__pycache__':
                                module_parts.append(part)
                        if module_parts:
                            module_name = '.'.join(module_parts)
                            if module_name not in imported_modules:
                                imported_modules.add(module_name)
                                cmd.extend(["--hidden-import", module_name])
            
            cmd.append(entry_script)
            
            self._log("=" * 60)
            self._log("开始打包...")
            self._log(f"命令: {' '.join(cmd)}")
            self._log("=" * 60)
            
            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            for line in process.stdout:
                self._log(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self._log("=" * 60)
                self._log("打包成功！")
                output_path = self.output_dir.get() or "dist"
                self._log(f"输出目录: {os.path.abspath(output_path)}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "成功", f"打包完成！\n输出目录: {os.path.abspath(output_path)}"))
            else:
                self._log("=" * 60)
                self._log("打包失败！")
                self.root.after(0, lambda: messagebox.showerror(
                    "错误", "打包失败，请查看日志信息！"))
                
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            self._log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))


def main():
    """主函数"""
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
