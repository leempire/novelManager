# novelManager
书架管理、书籍下载、小说阅读

**环境需求**

python 3.10

```commandline
pip install -r requirements.txt
```

命令行运行`python main.py`启动程序

## 2024-10-5 V1.0 实现书架管理及书城爬虫功能
- shelf show
- shelf add
- shelf search
- shelf remove
- city search
- city add
- city update
- help 
- exit

## 2024-10-6 V1.1 更新了阅读功能
- 修复了书城爬虫无法爬到完整内容的bug
- shelf export 书籍导出
- shelf read 阅读

## 2024-10-7 V1.2 新增了网页阅读器
- shelf hread 使用网页阅读器阅读小说，详情请使用指令 help shelf hread

## 提供的指令：
- shelf
  - `shelf show`
    - 显示书架中的所有书籍
  - `shelf add [bookName=all] [author=匿名]`
    - 将要添加的书籍文件（bookName.txt）放入./data/import/目录下，执行命令后可添加到书架
    - bookName=all时，将./data/import/目录下所有文件添加到书架
  - `shelf search [keywords]`
    - 书架内关键字查找
  - `shelf remove [index]`
    - 使用shelf search/show后，在书架中删除index项
  - `shelf export [index=None]`
    - 使用 shelf search/show 后，将index项导出到 ./data/export/ 文件夹
    - index取默认值时导出全部书籍
  - `shelf read [index] [chapter=None]`
    - 使用 shelf search/show 后，阅读index项书籍
    - chapter取默认值时为当前阅读进度
  - `shelf hread [index] [chapter=None]`
    - 使用shelf search/show 后，使用html阅读index项书籍
    - html阅读器的阅读进度单独存储，不与novelManager的阅读进度共享
    - 当novelManager阅读进度发生变化时，使用hread将自动同步到novelManager的进度
    - 使用hread后将在 ./data/export/ 中产生html文件，下次阅读时可直接打开该文件
- city
  - `city search [keywords]`
    - 通过爬虫在书城中搜索关键字
  - `city add [index]`
    - 将书城搜索的结果序号对应的书籍添加到书城
  - `city update`
    - 更新书架上所有从书城中添加的书籍
    - 每更新5章会自动保存，可以随时中断程序
- `help [orderName=help]`
  - 查看orderName指令的帮助，支持长指令如`help shelf show`
- `exit`
  - 安全退出程序

## 阅读器操作说明

使用`shelf read`指令进入阅读状态，在阅读状态下可使用以下快捷键进行控制
- +/- 键控制阅读速度
- 方向 ←/→ 切换到上（下）一章
- 方向 ↓ 快进5秒
- 空格 暂停/开始
- esc 退出阅读模式

## 使用示例
在书城中搜索《十日终焉》，将搜索到的第一个结果添加到书架，并下载到最新章节
```commandline
city search 十日终焉
city add 1
city update
```

在书架中查找刚刚添加的《十日终焉》，并开启命令行阅读模式，然后按esc退出，并开启网页阅读器
```commandline
shelf search 十日终焉
shelf read 1
shelf hread 1
```

将《十日终焉》导出为txt文件，导出后可在 ./data/export/ 文件夹中获取文件
```commandline
shelf search 十日终焉
shelf export 1
```

将《十日终焉》从书架中移除，然后将刚刚导出的 十日终焉.txt 导入到书架\
首先将 十日终焉.txt 放入 ./data/import/ 文件夹内，然后执行下面的命令
```commandline
shelf search 十日终焉
shelf remove 1
shelf add
```
