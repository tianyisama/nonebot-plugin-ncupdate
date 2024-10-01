# nonebot-plugin-ncupdate
管理nc的全自动懒人插件，主要应用于Windows
# ⚠警告
本插件含有大量屎山代码

由于我本人非常懒，因此Linux只支持更新及重启

新增的配置项`nc_restart_way`很重要

建议Windows用户选择2或3的启动方式

断线重连只支持2和3的启动方式

~~查看qq版本只支持Windows~~
## 更新
### 10.1
- 添加了Linux查看qq版本（支持Ubuntu，Centos，Rocky，Debian）
### 9.16
- 添加了2.x版本的适配
- 移除了配置项`nc_http_port`，新增了配置项`nc_restart_way` `nc_self_qq_version` `nc_self_restart`
- 新增了指令`nc检查更新` `查看qq/QQ版本` `柚子检查更新` `柚子查看qq版本`，指令`(柚子)更新nc`新增可指定版本，例如`(柚子)更新nc1.8.2`
- 新增内置判断napcat是否与ntqq兼容，不兼容会终止更新
- 新增多种可选的启动方式
### 7.29
- 由于nb端改代码导致的reload也会触发重连，而且被硬控十秒(nb会在执行完代码后再关闭)。欸🤓👆，我有个好点子
- 添加了自动重连的窗口，可选择是否立即重启或取消重启
### 7.14
- 适配了9.9.12版本的ntqq
### 6.28
- 修复了由于nc突然支持win32导致的win64位下载出错的问题. ~~说好的没有支持win32的打算呢(话说真的还有人在用win32吗)~~
- 新增win系统cmd闪退发起重连（手动关掉cmd也会触发重连请求）
- 新增断线10s后再发起重连

## 安装
<details>
<summary>使用nb-cli安装(推荐)</summary>


    nb plugin install nonebot-plugin-ncupdate
    

</details>

<details>
<summary>使用PIP安装</summary>


    pip install nonebot-plugin-ncupdate
    
若安装了虚拟环境，请在虚拟环境中操作。安装完成后，请在你的`bot.py`文件中添加以下代码来导入插件：
 `nonebot.load_plugin("nonebot_plugin_ncupdate")`
</details>

## 说明


支持自身触发更新或重启，支持选择代理，支持获取QQ版本且自行判断是否适用新版napcat（目前仅判断到2.5.4）

支持断线重连（默认关闭，目前仅支持Windows，且只支持初版bat登录法和way03方法）

### 指令

- 指令皆只有超级用户或自身可用

- 更新nc

- 重启nc

- 查看qq(QQ)版本/qqv

- nc检查更新

- 柚子更新nc（自身作为bot触发的更新指令）

- 柚子重启nc（自身作为bot触发的重启指令）

如果你需要使用`柚子更新nc`和`柚子更新nc`，则应当在nc的账号配置文件里打开自身消息上报(设置为true)
```json
  "reportSelfMessage": true,
```
### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `nc_restart_way` （重要新增）

- 默认：`1`
- 说明：napcat触发更新或重启时的重启方式
- 可选：

1.onebot接口的重启方式，部分napcat版本接口是坏的，Linux只可选用此方式（因为其他的没写）
  
2.旧时代版本napcat-utf8.bat的启动方式，QQ版本9.12之后此方法已失效
  
3.way03：QQ.exe的启动方式，需要更改qq文件并配置补丁，具体参考 [way03启动方式](https://napneko.github.io/zh-CN/guide/boot/shell/BootWay03)
  
4.way05：ps1的启动方式，无需更改文件但需要替换补丁，具体参考 [way05启动方式](https://napneko.github.io/zh-CN/guide/boot/shell/BootWay05)
  
- 必填：否
- 警告：Linux请选1，Windows：最好不要选1，因为部分版本接口坏了用不了，3和4的启动方式只可选择一个（因为启用了way05后，way03方法会失效）

#### `base_path`

- 默认：`C:\\napcat`
- 说明：napcat运行目录的上级目录路径，例如原运行于`E:\111\NapCat.win32.x64`，则填写`E:\111`
- 必填：否

#### `topfolder`

- 默认：`NapCat.win32.x64`
- 说明：napcat运行目录的顶级目录名称，例如原运行于`E:\111\NapCat`，则填写`NapCat`
- 必填：否

#### `napcat_mode`

- 默认：`win`
- 说明：napcat的运行系统类型
- 可选：win，win_32，linux，linux_arm
- 必填：否

#### `nc_proxy`

- 默认：`false`
- 说明：是否通过代理请求GitHub更新
- 可选：true，false
- 必填：否

#### `nc_proxy_port`

- 默认：`11451`
- 说明：代理使用的端口
- 必填：否

#### `nc_self_update`

- 默认：`"柚子更新nc"`
- 说明：当bot是自己的时候触发的更新指令
- 必填：否

#### `nc_self_restart`

- 默认：`"柚子重启nc"`
- 说明：当bot是自己的时候触发的重启指令
- 必填：否

#### `nc_self_restart`

- 默认：`"柚子检查更新"`
- 说明：当bot是自己的时候触发的检查更新
- 必填：否

#### `nc_self_qq_version`

- 默认：`"柚子查看qq版本"`
- 说明：当bot是自己的时候触发的查看qq版本
- 必填：否

#### `nc_reconnect`

- 默认：`false`
- 说明：是否开启napcat掉线重连（目前只支持Windows）
- 可选：true，false
- 必填：否

### 配置示例
> 只有要用到的才填写，如果用不到或者不知道怎么设置，把你的napcat运行目录变成`C:\napcat\NapCat.win32.x64`就可以了
#### Windows配置示例
```ini
base_path=C:\\
topfolder=NapCat
napcat_mode=win
nc_proxy=true
nc_proxy_port=11451
nc_self_update="橘子更新nc"
nc_self_restart="橘子重启nc"
nc_reconnect=true
nc_self_check_update="柚子检查更新"
nc_self_qq_version="柚子查看qq版本"
nc_restart_way=1
```
如果你使用的是9.9.12版本的ntqq，那么他应该类似于这样
```ini
base_path=D:\qqnt\resources\app\app_launcher
topfolder=napcat
```
#### Linux配置示例
```ini
base_path=/root
topfolder=NapCat.linux.x64
napcat_mode=linux
nc_proxy=true
nc_proxy_port=11451
nc_self_update="橘子更新nc"
nc_self_restart="橘子重启nc"
nc_reconnect=false
nc_self_check_update="柚子检查更新"
nc_self_qq_version="柚子查看qq版本"
nc_restart_way=1
```
## 挖坑
- 准备实现linux断线重连和相关功能
- 准备增加初始一键安装napcat
- 准备将最新的启动方式加进去

## 致谢


- [Napcat](https://github.com/NapNeko/NapCatQQ)
