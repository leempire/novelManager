# novelManager
manage your shelf

## 2024-10-5 实现书架管理及书城爬虫功能
提供的指令：
- shelf
  - show
    - 显示书架中的所有书籍
  - add [bookName]
    - 将要添加的书籍文件（bookName.txt）放入./data/import/目录下，执行命令后可添加到书架
  - search [keywords]
    - 书架内关键字查找
  - remove [index]
    - 删除shelf show或shelf search的结果index对应的书籍
- city
  - search [keywords]
    - 通过爬虫在书城中搜索关键字
  - add [index]
    - 将city search的搜索结果的index项添加到书架中
  - update
    - 更新书架上所有从书城中添加的书籍
    - 每更新5章会自动保存，可以随时中断程序
- exit
  - 退出
