# nonebot-plugin-ncupdate
指令更新nc的全自动懒人插件，通过指令`更新nc`即可全自动更新nc并自动重连

## 更新
## 6.28
- 修复了由于nc突然支持win32导致的win64位下载出错的问题. ~~说好的没有支持win32的打算呢(话说真的还有人在用win32吗)~~
- 新增win系统cmd闪退发起重连（手动关掉cmd也会触发重连请求）
- 新增断线10s后再发起重连
## 说明
没上传到商店也没有pypi，有需要可以自行下载替换

**目前只支持1.5.2及以上版本**，此前版本没有重启nc端的功能，请手动将版本升级到1.5.2以确保后续版本的自动更新

支持linux，支持自身触发更新或重启 ~~（linux似乎不支持快速重启？）~~，支持选择代理

~~忘了是不是需要安装依赖了，如果有需要的话你会安装的吧~~需要安装`aiofiles`和`psutil`

**请打开你的napcat的http服务，否则无法重启nc**

支持断线重连（默认关闭，目前仅支持Windows），**不是开机自连，~~也不支持闪退重连~~**（nc都闪退了系统也该埋了x）

### 指令


- 更新nc（仅超级用户可用）

- 重启nc（仅超级用户可用）

- 柚子更新nc（bot自身触发的更新指令）

- 柚子重启nc（bot自身触发的重启指令）


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
- 说明：napcat的http服务运行端口，不懂可以不用管
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

## 挖坑
- 准备实现linux断线重连
- 准备上传到商店

## 致谢


- [Napcat](https://github.com/NapNeko/NapCatQQ)
