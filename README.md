# AutoXue 3.0 beta

使用 Appuim 轮子实现學習自动化，用起来十分舒适、快速

> **题库** [在线版文档](./study/sources/exports/data-doc.md) | [在线版表格](./study/sources/exports/data-grid.md)

## 程序功能
- **检测当日积分情况**：读取积分页面
- **登录**：无需实现
- **每日答题**：根据积分情况智能执行每日答题
- **挑战答题**：根据积分情况智能执行每日答题
- **每周答题**：暂不实现
- **专项答题**：暂不实现
- **新闻学习**：根据积分情况智能执行新闻学习
- **视听学习**：根据积分情况智能执行视听学习
- **订阅**：暂不实现
- **收藏** (*立即取消收藏 可选*)：根据配置收藏文章
- **分享** (*立即取消分享 默认*)：自动分享文章
- **留言** (*立即删除留言 可选*)：根据配置留言文章

## 环境依赖
> Appium 环境配置实在太糟心了，网上教程很多，如果被 Appium 环境配置劝退了，我只能说一声“朋友再见”

下面介绍一下通过测试的软件版本号
> 作者使用 MuMu模拟器发现无法获取 content-desc 内容，故转用 Nox,其他模拟器未测试

|项目|版本号|
|----|:-----|
|OS|Windows 10 professional 1903|
|JDK|1.8.0_05|
|ADB|1.0.41|
|Appium|1.13.0|
|node|10.16.3|
|python|3.7.4|
|Nox|6.3.0 (Android ver: 5.1.1)|
|apk|2.5.1|

## 配置方法
在./study/config/下新建[custom.ini](./study/config/custom.ini)配置文件，参考[default.ini](./study/config/default.ini)进行个性化配置，推荐编辑器vscode、notepad++等

## 使用方法
0. 打开 Appium 服务器
1. 打开 Nox 模拟器
2. $:adb connect 127.0.0.1:62001
3. (venv)$:python -m study


## 常见问题
- 无法连接模拟器，请在shell手动连接adb connect 127.0.0.1:62001
- 请不要忘记安装脚本依赖库
- Appium 的 socket 2分钟释放，请确保重开时间间隔大于2分钟
- 如果 Appium 安装在C:\Program Files，请给整个 Appium 目类权限，否则可能导致 Uiautomator2 报错
- 其他运行时错误请结合日志文件和报错信息分析

## 未来展望
- 计时器功能已实现，有待加入程序中
- 采用 Docker 打包依赖和程序，简化环境配置工作
- 将题库查询独立出来，采用 RESTful 实现
> 没玩过 Docker，欢迎会 Docker 的童鞋指导一下