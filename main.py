import json
import os
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import windnd

VERSION = "1.2.1"
DATE = "2023/8/28"


def deco(func):
    # 线程装饰器
    def wrapper(*args):
        t = threading.Thread(target=func, args=(*args,))
        t.start()

    return wrapper


class Window:
    def __init__(self, root_obj):
        self.root = root_obj
        self.root.title(f'Realme adb Tool v{VERSION}')
        # self.root.resizable(width=False, height=False)
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (700, 600, (screenwidth - 650) / 2, (screenheight - 600) / 2)
        self.root.geometry(size)
        self.notebookStatus = False
        self.currentSecondUser = False
        self.init_ui()

    def init_ui(self):
        # 主界面Frame
        frame_root = tk.Frame(self.root, bg='lightgrey')
        frame_status = tk.Frame(self.root)
        frame_root.pack(fill='both', expand=True)
        frame_status.pack(fill='x')
        ttk.Separator(frame_status).pack(fill='x', padx=0)
        tk.Label(frame_status, text='作者：小小张').pack(side='left')

        # 主界面中的小Frame
        with open("help.txt", 'r', encoding="utf-8") as f:
            info = f.read().strip()
        label_help = tk.Label(frame_root, text=info, justify='left', anchor='w')
        label_help.pack(fill='x', ipady=10)
        frame_inf = tk.Frame(frame_root, bg='lightgrey')
        frame_inf.pack(pady=10)

        # 小组件
        self.deviceName = tk.StringVar()
        tk.Label(frame_inf, text='连接手机：', bg='lightgrey').pack(side='left')
        self.l2 = tk.Label(frame_inf, bg='lightgrey', fg='red', textvariable=self.deviceName)
        self.l2.pack(side='left', padx=5)
        ttk.Button(frame_inf, text='刷新设备', command=self.loadDevice).pack(side='left')

        self.notebook = ttk.Notebook(frame_root, padding=5)
        self.frame_double = tk.Frame()

        frame_double_1 = tk.Frame(self.frame_double)
        frame_double_2 = tk.Frame(self.frame_double)
        frame_double_3 = tk.Frame(self.frame_double)

        self.secondUserID = tk.StringVar()
        l3 = tk.Label(frame_double_1, text='分身 user ID：')
        self.l4 = tk.Label(frame_double_1, textvariable=self.secondUserID, fg='red')
        b2 = ttk.Button(frame_double_1, text='刷新', command=self.loadSecondUser)
        l3.pack(side='left', pady=5)
        self.l4.pack(side='left')
        b2.pack(side='left', padx=20)

        frame_mainApp = tk.LabelFrame(frame_double_2, text='已安装App', relief='sunken', bd=1)
        frame_secondApp = tk.LabelFrame(frame_double_2, text='已分身App', relief='sunken', bd=1)
        frame_mainApp.pack(side='left', fill='both', expand=True)
        frame_secondApp.pack(side='right', fill='both', expand=True)
        for k in (frame_mainApp, frame_secondApp):
            for i in range(3):
                k.columnconfigure(i, weight=1)
            k.rowconfigure(0, weight=1)

        mainAppListBar = tk.Scrollbar(frame_mainApp, orient=tk.VERTICAL)
        secondAppListBar = tk.Scrollbar(frame_secondApp, orient=tk.VERTICAL)

        self.mainAppList = tk.Listbox(frame_mainApp, yscrollcommand=mainAppListBar.set, relief='flat', bg='lightgrey')
        self.secondAppList = tk.Listbox(frame_secondApp, yscrollcommand=secondAppListBar.set, relief='flat',
                                        bg='lightgrey')
        self.mainAppList.grid(row=0, column=0, columnspan=3, sticky='ewns')
        self.secondAppList.grid(row=0, column=0, columnspan=3, sticky='ewns')
        mainAppListBar.grid(row=0, column=3, sticky='ns')
        secondAppListBar.grid(row=0, column=3, sticky='ns')
        mainAppListBar.config(command=self.mainAppList.yview)
        secondAppListBar.config(command=self.secondAppList.yview)
        ttk.Button(frame_mainApp, text='刷新列表', width=8, command=self.loadMainPackages).grid(row=1, column=0)
        ttk.Button(frame_mainApp, text='卸载选中', width=8, command=self.uninstallMainApp).grid(row=1, column=1)
        ttk.Button(frame_mainApp, text='分身选中', width=8, command=self.doubleMyApp).grid(row=1, column=2)

        ttk.Button(frame_secondApp, text='刷新列表', width=8, command=self.loadSecondPackages).grid(row=1, column=0)
        ttk.Button(frame_secondApp, text='卸载选中', width=8, command=self.uninstallSecondApp).grid(row=1, column=1)
        ttk.Button(frame_secondApp, text='重新安装', width=8, command=self.reloadMyApp).grid(row=1, column=2)

        frame_double_1.pack()
        frame_double_2.pack(fill='both', expand=True)
        frame_double_3.pack(fill='x')

        self.frame_install = tk.Frame()
        frame_install_1 = tk.LabelFrame(self.frame_install, text='安装App（请拖放文件到此处），不支持中文')
        frame_install_2 = tk.LabelFrame(self.frame_install,
                                        text='传送文件到手机Download目录（请拖放文件到此处），不支持中文')
        frame_install_1.pack(fill='x', pady=10)
        frame_install_2.pack(fill='x', pady=10)

        for k in (frame_install_1, frame_install_2):
            k.columnconfigure(0, weight=1)
        self.text_path_app = tk.Text(frame_install_1, height=6, font=('等线', 10), state='disabled')
        self.text_path_file = tk.Text(frame_install_2, height=6, font=('等线', 10), state='disabled')
        self.text_path_app.grid(row=0, column=0, rowspan=2, columnspan=1, sticky='nsew')
        self.text_path_file.grid(row=0, column=0, rowspan=2, columnspan=1, sticky='nsew')
        windnd.hook_dropfiles(self.text_path_app, self.dropAppFile)
        windnd.hook_dropfiles(self.text_path_file, self.dropFile)
        ttk.Button(frame_install_1, text='安装', command=self.installApps).grid(row=0, column=1, rowspan=1,
                                                                                columnspan=1, padx=10)
        ttk.Button(frame_install_1, text='降级安装', command=self.installAppsWithData).grid(row=1, column=1, rowspan=1,
                                                                                            columnspan=1, padx=10)
        ttk.Button(frame_install_2, text='传送', command=self.transferFiles).grid(row=0, column=1, rowspan=1,
                                                                                  columnspan=1, padx=10)

        self.frame_restart = tk.Frame()
        ttk.Button(self.frame_restart, text='重启手机', command=self.reboot).grid(row=0, column=0, padx=30, pady=10,
                                                                                  sticky='we')
        ttk.Button(self.frame_restart, text='关机', command=self.shutdown).grid(row=1, column=0, padx=30, pady=10,
                                                                                sticky='we')
        ttk.Button(self.frame_restart, text='重启到Recovery', command=self.rebootRecovery).grid(row=2, column=0,
                                                                                                padx=30, pady=10,
                                                                                                sticky='we')
        ttk.Button(self.frame_restart, text='重启到Bootloader', command=self.rebootBootloader).grid(row=3, column=0,
                                                                                                    padx=30, pady=10,
                                                                                                    sticky='we')

        self.frame_about = tk.Frame()
        frame_about_1 = tk.Frame(self.frame_about)
        frame_about_2 = tk.LabelFrame(self.frame_about, text='打赏作者', fg='blue')
        frame_about_1.pack(pady=2)
        frame_about_2.pack(pady=2)
        inf = [f'版本\t：{VERSION}\t\t\t日期\t：{DATE}', '作者邮箱\t：xxzh1020@qq.com\tB站\t：@小晓张']
        for i in inf:
            tk.Label(frame_about_1, text=i, anchor='w', font=('微软雅黑', 10)).pack(fill='x')

        img_gif = tk.PhotoImage(file=r'pyData.dll')
        aaa = tk.Label(frame_about_2, text='微信', image=img_gif, anchor='w')
        aaa.pack(fill='x')
        aaa.image = img_gif

        self.notebook.pack(expan=True, fill='both', expand=True)
        self.loadDevice()

    def dropAppFile(self, files):
        self.text_path_app.config(state='normal')
        self.text_path_app.delete(0.0, 'end')
        myfile = [x.decode('gbk') for x in files if x.decode('gbk').lower().endswith('.apk')]
        self.text_path_app.insert('end', '\n'.join(myfile))
        self.text_path_app.config(state='disabled')

    def dropFile(self, files):
        self.text_path_file.config(state='normal')
        self.text_path_file.delete(0.0, 'end')
        myfile = [os.path.abspath(x.decode('gbk')) for x in files]
        self.text_path_file.insert('end', '\n'.join(myfile))
        self.text_path_file.config(state='disabled')

    def loadTab(self, status=False):
        myTab = {
            self.frame_double: '双开/卸载App',
            self.frame_install: '安装App/传送文件',
            self.frame_restart: '重启选项',
            self.frame_about: '关于'}

        if status:
            for i in myTab:
                self.notebook.add(i, text=myTab[i])
            self.notebookStatus = True
        elif self.notebookStatus:
            for i in myTab:
                self.notebook.hide(i)
            self.notebookStatus = False

    def loadDevice(self):
        result = os.popen('adb devices').read().strip()
        print(result)
        deviceReg = re.search('(.*)\\tdevice', result)
        if deviceReg:
            self.deviceName.set(deviceReg.group(1))
            self.l2.config(fg='green')
            self.loadTab(True)
            self.loadSecondUser()
            self.loadMainPackages()
            self.loadSecondPackages()
            return True
        else:
            self.deviceName.set('请检查')
            self.l2.config(fg='red')
            self.loadTab(False)
            return False

    def loadSecondUser(self):
        result = os.popen('adb shell pm list users').read().strip()
        print(result)
        user_reg = re.findall(r'UserInfo\{(\d+):(.+?):.+\} running', result)
        if user_reg:
            user_ids, user_names = tuple(zip(*user_reg))
            print(user_ids, user_names)
            if "999" in user_ids:
                self.secondUserID.set('999')
                self.l4.config(fg='green')
                self.currentSecondUser = '999'
                return True
            for index, name in enumerate(user_names):
                if re.search(r"Multi.*App", name, re.I):
                    self.secondUserID.set('999')
                    self.l4.config(fg='green')
                    self.currentSecondUser = '999'
                    return True

        if len(user_reg) < 1:
            self.secondUserID.set('未识别')
            self.l4.config(fg='red')
            self.currentSecondUser = False
        else:
            self.secondUserID.set(f'没有识别到分身用户ID“999”')
            self.l4.config(fg='orange')
            self.currentSecondUser = False

    @deco
    def loadMainPackages(self):
        result = os.popen('adb shell pm list packages -3').read()
        packages = [re.search('package:(.*)', x).group(1) for x in result.split('\n') if re.search('package:(.*)', x)]
        packages.sort()
        with open('AppNames.json', 'r', encoding='UTF-8') as f:
            NameDict = json.load(f)
        self.mainAppList.delete(0, 'end')
        for i in packages:
            if i in NameDict:
                if NameDict[i]:
                    self.mainAppList.insert('end', f'{i}({NameDict[i]})')
                    continue
            self.mainAppList.insert('end', i)
        return packages
        # for i in range(10):
        #     self.mainAppList.insert('end',i)

    @deco
    def loadSecondPackages(self):
        try:
            result = os.popen(f'adb shell pm list packages -3 --user {self.currentSecondUser}').read()
            packages = [re.search('package:(.*)', x).group(1) for x in result.split('\n') if
                        re.search('package:(.*)', x)]
            with open('AppNames.json', 'r', encoding='UTF-8') as f:
                NameDict = json.load(f)
            self.secondAppList.delete(0, 'end')
            packages.sort()
            for i in packages:
                if i in NameDict:
                    if NameDict[i]:
                        self.secondAppList.insert('end', f'{i}({NameDict[i]})')
                        continue
                self.secondAppList.insert('end', i)
        except:
            return False
        return packages
        # for i in range(10):
        #     self.mainAppList.insert('end',i)

    @deco
    def uninstallMainApp(self):
        sellection = self.mainAppList.curselection()
        if len(sellection) != 1:
            messagebox.showwarning(title='提示信息', message='请选择你要卸载的App包名，然后再试')
            return False
        appName = self.mainAppList.get(sellection[0]).split('(')[0]
        a = messagebox.askokcancel(title='确认信息', message=f'你确定要卸载{appName}吗？')
        if a:
            command = ['adb', 'uninstall', appName]
            result = os.popen(' '.join(command)).read().strip()
            messagebox.showinfo(title='提示', message=f'卸载 {appName}\n{result}')

        self.loadMainPackages()

    @deco
    def uninstallSecondApp(self):
        sellection = self.secondAppList.curselection()
        if len(sellection) != 1:
            messagebox.showwarning(title='提示信息', message='请选择你要卸载的App包名，然后再试')
            return False
        appName = self.secondAppList.get(sellection[0]).split('(')[0]
        a = messagebox.askokcancel(title='确认信息', message=f'你确定要卸载{appName}吗？')
        if a:
            command = ['adb', 'uninstall', '--user', self.currentSecondUser, appName]
            result = os.popen(' '.join(command)).read().strip()
            messagebox.showinfo(title='提示信息', message=f'卸载{appName}\n{result}')
        self.loadSecondPackages()

    def doubleMyApp(self):
        sellection = self.mainAppList.curselection()
        if len(sellection) != 1:
            messagebox.showwarning(title='提示信息', message='请选择你要双开的App包名，然后再试')
            return False
        appName = self.mainAppList.get(sellection[0]).split('(')[0]
        if self.currentSecondUser == False:
            messagebox.showwarning(title='提示信息', message='请先找到分身用户ID')
        else:
            result = os.popen(f'adb -d shell pm path {appName}').read().strip()
            path = result.split(':')[1]
            result = os.popen(f'adb -d shell pm install -r --user {self.currentSecondUser} {path}').read().strip()
            messagebox.showinfo(title='提示信息', message=f'双开  {appName}\n{result}')
        self.loadSecondPackages()

    def reloadMyApp(self):
        sellection = self.secondAppList.curselection()

        if len(sellection) != 1:
            messagebox.showwarning(title='提示信息', message='请选择你要双开的App包名，然后再试')
            return False
        appName = self.secondAppList.get(sellection[0]).split('(')[0]

        if self.currentSecondUser == False:
            messagebox.showwarning(title='提示信息', message='请先找到分身用户ID')
        else:
            result = os.popen(f'adb -d shell pm path {appName}').read().strip()
            path = result.split(':')[1]
            result = os.popen(f'adb -d shell pm install -r --user {self.currentSecondUser} {path}').read().strip()
            messagebox.showinfo(title='提示信息', message=f'重新安装 {appName}\n{result}')
        self.loadSecondPackages()

    @deco
    def transferFiles(self):
        files = self.text_path_file.get('0.0', 'end').strip()
        filelist = [x for x in files.split('\n') if os.path.isfile(x)]
        mResult = list()
        if len(filelist) < 1:
            messagebox.showwarning(title='警告', message='文件数量为空')
            return False
        for each in filelist:
            command = f'adb push \"{each}\" /storage/emulated/0/Download/'
            print(command)
            try:
                result = os.popen(command).read()
                mResult.append(result)
                print(result)
            except Exception as e:
                print(repr(e))
        messagebox.showinfo(title='提示', message='\n'.join(mResult))

    @deco
    def installApps(self):
        files = self.text_path_app.get('0.0', 'end').strip()
        filelist = [x for x in files.split('\n') if os.path.isfile(x)]
        mResult = list()
        if len(filelist) < 1:
            messagebox.showwarning(title='警告', message='APK数量为空')
            return False
        for each in filelist:
            command = ['adb', 'install', '-r', each]
            result = os.popen(' '.join(command)).read()
            print(result)
            mResult.append(result)
        messagebox.showinfo(title='提示', message='\n'.join(mResult))

    @deco
    def installAppsWithData(self):
        files = self.text_path_app.get('0.0', 'end').strip()
        filelist = [x for x in files.split('\n') if os.path.isfile(x)]
        if len(filelist) < 1:
            messagebox.showwarning(title='警告', message='APK数量为空')
            return False
        for each in filelist:
            command = ['adb', 'uninstall', '-k', each]
            result = os.popen(' '.join(command))
            print(result)
            command = ['adb', 'install', '-r', each]
            result = os.popen(' '.join(command))
            print(result)

    def reboot(self):
        a = messagebox.askokcancel(title='确认信息', message='你确定要重启手机吗？')
        if a:
            result = os.popen('adb reboot')

    def shutdown(self):
        a = messagebox.askokcancel(title='确认信息', message='你确定要关机吗？')
        if a:
            result = os.popen('adb shell reboot -p')

    def rebootRecovery(self):
        a = messagebox.askokcancel(title='确认信息', message='你确定要重启到Recovery吗？')
        if a:
            result = os.popen('adb reboot recovery')

    def rebootBootloader(self):
        a = messagebox.askokcancel(title='确认信息', message='你确定要重启到Bootloader吗？')
        if a:
            result = os.popen('adb reboot bootloader')


if __name__ == '__main__':
    root = tk.Tk()
    root.iconbitmap(default='pyico.dll')
    app = Window(root)
    root.mainloop()
