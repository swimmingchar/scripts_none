#!/usr/bin/env python
# coding:utf-8


import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """
        打印JSON结果
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

# 由于api是为cli构造的，因此它希望始终设置某些选项，命名为tuple“fakes”args analysing options对象
Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
options = Options(connection='local', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False)

# 初始化对象
loader = DataLoader() # Takes care of finding and reading yaml, json and ini files
passwords = dict(vault_pass='secret')

# 实例化resultcallback
results_callback = ResultCallback()

# host清单创建，配置路径或者使用都好风格的字符串作为主机清单
inventory = InventoryManager(loader=loader, sources='localhost,')

# 变量管理器负责合并所有不同的源，为您提供每个上下文中可用变量的统一视图
variable_manager = VariableManager(loader=loader, inventory=inventory)

# 创建playbook脚本的数据结构
play_source =  dict(
        name = "Ansible Play",
        hosts = '172.10.1.31,172.10.1.32',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args='echo $(date +%F" | "%T) > /tmp/test-20190417'), register='创建文件'),
            dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
         ]
    )

# 创建play对象，palybook对象使用 load而不是init或者new的方法。根据play_source中提供的信息自动创建对象
play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

# 实例化任务队列管理器，负责所有设置对象，以便在主机列表和任务上迭代
tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              # 使用自定已回调，不是打印到stdout的默认回调
              stdout_callback=results_callback,
          )
    # 大多有用的数据会发送至回调模块 callback's methods
    result = tqm.run(play)
finally:
    # 清理子进程
    if tqm is not None:
        tqm.cleanup()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

