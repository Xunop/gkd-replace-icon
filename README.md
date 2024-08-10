# 将 GKD 的图标替换成旧版
新图标（左）的颜色和我文件夹里其他几个应用不搭，强迫症犯了。我选择换成旧版图标。

<img src="theme.png" width="500px">

## ~~直接下载~~
~~在 [Releases](https://github.com/zetaloop/gkd-replace-icon/releases) 中下载修改完成的版本。~~

~~注意，由于签名不一致，您需要卸载原版，然后安装该版本。原本的数据会丢失，请做好备份。~~

根据 [原版的分发要求](https://github.com/orgs/gkd-kit/discussions/679)，无法发布修改后的 apk，请按下方教程自行修改。

## 自己运行
### 依赖：
需要有 Windows、Python、Java，其余工具都已自带。

### 用法：
传入要修改的 apk 文件 _（或者，直接将 apk 拖到脚本上）_
```shell
python replace_icon.py gkd-vxxx.apk
```
然后你会获得一个修改好的 `gkd-vxxx_replaced.apk`。

签名使用公开的 `freekey.keystore`，这样以后如果不用这个版本了，可以自己给其他版本签名，然后覆盖安装。

## 解释
分叉编译整个项目开销过大，本工具只是简单替换几个图标文件。

问题反馈请使用原版。
