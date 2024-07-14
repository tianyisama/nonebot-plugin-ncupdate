# nonebot-plugin-ncupdate
指令更新nc的全自动懒人插件，通过指令`更新nc`即可全自动更新nc并自动重连

# ⚠警告
由于NTQQ在9.9.12发生了大范围改动，NapCat的启动方式变化巨大且不支持快速登录和重启，本插件暂不适用于9.9.12版本及以上的NTQQ

如果你的NTQQ版本为9.9.11及以前，本插件仍然适用

一拳把企鹅🐎打飞😡👊

拾雪说老启动方法会复活，所以先咕咕咕 Ciallo～(∠・ω< )⌒★!
## 更新
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
~~没上传到商店也没有pypi，有需要可以自行下载替换~~

**目前只支持1.5.2及以上版本的NapCat**，此前版本没有重启nc端的功能，请手动将版本升级到1.5.2以确保后续版本的自动更新

支持linux，支持自身触发更新或重启，支持选择代理


**请打开你的napcat的http服务，否则无法重启nc**，前往nc的账号配置文件(如onebot11_123456789.json)，将下部分内容的`enable`设置为`true`，`port`与配置项`nc_http_port`设为一致
```json
"http": {
    "enable": true,
    "host": "",
    "port": 3000,
    "secret": "",
    "enableHeart": false,
    "enablePost": false,
    "postUrls": []
  },
```
支持断线重连（默认关闭，目前仅支持Windows），**不是开机自连，~~也不支持闪退重连~~**（nc都闪退了系统也该埋了x）

### 指令


- 更新nc（仅超级用户可用）

- 重启nc（仅超级用户可用）

- 柚子更新nc（自身作为bot触发的更新指令）

- 柚子重启nc（自身作为bot触发的重启指令）

如果你需要使用`柚子更新nc`和`柚子更新nc`，则应当在nc的账号配置文件里打开自身消息上报(设置为true)
```json
  "reportSelfMessage": true,
```
### 配置项

> 以下配置项可在 `.env.*` 文件中设置，具体参考 [NoneBot 配置方式](https://nonebot.dev/docs/appendices/config)

#### `base_path`

- 默认：`C:\\napcat`
- 说明：napcat运行目录的上级目录路径，例如原运行于`E:\111\NapCat.win32.x64`，则填写`E:\\111`
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

#### `nc_http_port`

- 默认：`3000`
- 说明：napcat的http服务运行端口
- 必填：否

#### `nc_self_update`

- 默认：`"柚子更新nc"`
- 说明：当bot是自己的时候触发的更新指令
- 必填：否

#### `nc_self_restart`

- 默认：`"柚子重启nc"`
- 说明：当bot是自己的时候触发的重启指令
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
nc_http_port=3000
nc_self_update="橘子更新nc"
nc_self_restart="橘子重启nc"
nc_reconnect=true
```
#### Linux配置示例
```ini
base_path=/root
topfolder=NapCat.linux.x64
napcat_mode=linux
nc_proxy=true
nc_proxy_port=11451
nc_http_port=3000
nc_self_update="橘子更新nc"
nc_self_restart="橘子重启nc"
nc_reconnect=false
```
## 挖坑
- 准备实现linux断线重连
- ~~准备上传到商店~~

## 致谢


- [Napcat](https://github.com/NapNeko/NapCatQQ)