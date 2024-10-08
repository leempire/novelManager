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
**V1.2.0**
- shelf hread 使用网页阅读器阅读小说，详情请使用指令 help shelf hread

**V1.2.1**
- 修复了网页阅读器模板文件缺失的bug

**V1.2.2**
- 增加报错功能，解决程序异常退出的情况
- 修复了阅读器中的一些bug
- 将搜索功能（shelf search, city search）修改为支持空格
- shelf read, shelf hread, shelf remove, shelf export 现在支持搜索index并将最匹配的结果作为输入了
- 修复了shelf add会重复添加已添加过的书籍的bug

**V1.2.3**
- 修复了shelf hread的chapter参数超出合法范围导致无法阅读的bug
- 调整了项目代码的结构

## 2024-10-8 V1.3 新增了设置功能
**V1.3.0**
- 新增set 修改设置，可修改默认阅读速度和是否自动清空命令行
- 优化了结果输出格式
- 修复了 city add 可重复添加已添加过的书籍的bug
- 将shelf下的部分二级指令改为一级指令，详情使用help查看可用指令

## 提供的指令：
- shelf
  - `shelf show`
    - 显示书架中的所有书籍
  - `shelf add [bookName=all] [author=匿名]`
    - 将要添加的书籍文件（bookName.txt）放入./data/import/目录下，执行命令后可添加到书架
    - bookName=all时，将./data/import/目录下所有文件添加到书架
  - `shelf search [keywords]`
    - 书架内关键字查找
    - keywords支持空格
  - `shelf remove [index]`
    - 使用shelf search/show后，在书架中删除index项
    - 当index非数字时，使用搜索到匹配程度最高的结果作为目标
- city
  - `city search [keywords]`
    - 通过爬虫在书城中搜索关键字
    - keywords支持空格
  - `city add [index]`
    - 将书城搜索的结果序号对应的书籍添加到书城
  - `city update`
    - 更新书架上所有从书城中添加的书籍
    - 每更新5章会自动保存，可以随时中断程序
- `set [key] [value]`
  - 修改默认设置，支持以下设置项
  - readSpeed: float 命令行阅读器阅读速度（字/秒）
  - autoCls: 0/1 是否开启命令行自动刷新
- `help [orderName=help]`
  - 查看orderName指令的帮助，支持长指令如`help shelf show`
- `read [index] [chapter=None]`
  - 使用 shelf search/show 后，阅读index项书籍
  - 当index非数字时，使用搜索到匹配程度最高的结果作为目标
  - chapter取默认值时为当前阅读进度
- `hread [index] [chapter=None]`
  - 使用shelf search/show 后，使用html阅读index项书籍
  - 当index非数字时，使用搜索到匹配程度最高的结果作为目标
  - html阅读器的阅读进度单独存储，不与novelManager的阅读进度共享
  - 当novelManager阅读进度发生变化时，使用hread将自动同步到novelManager的进度
  - 使用hread后将在 ./data/export/ 中产生html文件，下次阅读时可直接打开该文件
- `export [index=None]`
  - 使用 shelf search/show 后，将index项导出到 ./data/export/ 文件夹
  - 当index非数字时，使用搜索到匹配程度最高的结果作为目标
  - index取默认值时导出全部书籍
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
从书城下载书籍
```commandline
# 在书城中搜索《十日终焉》
city search 十日终焉

# 将搜索到的第一个结果添加到书架
city add 1

# 更新书架中所有来自书城的小说
city update
# 每更新五章会自动保存，更新过程中可以随时关闭程序
```

查看书架，并阅读书架中的书籍
```commandline
# 查看书架所有书籍
shelf show
# 在书架中查找《十日终焉》
shelf search 十日终焉

# 使用命令行阅读器，阅读搜索到的第一个结果
read 1
# 按esc键退出阅读模式

# 使用html阅读器，阅读十日终焉
hread 十日终焉
```

书籍导出
```commandline
export 十日终焉
# 查看 ./data/export/ 文件夹，发现刚刚导出的文件 十日终焉.txt
```

书架删除
```commandline
shelf remove 十日终焉
```

从文件中导入书籍
```commandline
# 将 xx.txt 书籍文件放入 ./data/import/ 文件夹
shelf add  # 导入 ./data/import/ 文件夹下的所有书籍文件
shelf add 十日终焉  # 导入 十日终焉.txt
```
