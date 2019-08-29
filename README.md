# AutoXue 3.0-alpha

针对混合应用采取的appuim自动化策略

> 题库 [在线版文档](./xuexi/sources/exports/data-doc.md) | [在线版表格](./xuexi/sources/exports/data-grid.md)

## 程序功能
- 检测当日积分情况
- 每日答题
- 挑战答题
- 每周答题
- 专项答题
- 新闻学习
- 视听学习
- 收藏 (*立即取消收藏 可选*)
- 分享 (*立即取消分享 默认*)
- 留言 (*立即删除留言 可选*)

## 环境依赖
- [JDK](./README.md)
- [SDK](./README.md)
- [node](./README.md)
- [appium](./README.md)
- [python](./README.md)
- [nox](./README.md)

## 配置方法
在./xuexi/config/下新建custom.ini配置文件，参考./xuexi/config/default.ini进行个性化配置

## 使用方法
```
(venv)$:python -m xuexi
```

## 未来展望
- 采用docker打包依赖和程序，简化环境配置工作
- 将题库查询独立出来，采用RESTful API实现