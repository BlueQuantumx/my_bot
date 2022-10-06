# my_bot

Bingyan Internship Program by BlueQuantum（周陆延）

## 10.1

由于换了新电脑一直没装 Linux，先装 Linux，本来我装 Archlinux 都驾轻就熟的，但是没想到栽在了 Redmibook Pro 15 2022 Intel+Nvidia 上，奶奶滴我再买 Nvidia 就是狗（以后万一搞 CUDA 就打脸了）。然后安装了 Docker，头一次用还没太搞清楚逻辑，而且由于搞 Linux 时间已经过去好久了，遂放弃。

## 10.2

正式开搞，参考了 nonebot 选用 reverse-websocket 这样确实还能搞多账号，期间在 websocket 消息格式上卡了好久，我以为要把 JSON 对象转成 byte 流 send ，然后感觉 go-cqhttp 给的错误提示也不是很友好看了半天没发现问题出在这里，我翻了好久 nonebot 的源码才发现传 str 就好了，然后非常顺利的完成了 Stage 0。我还搞了个压（bushi）测群（其实就是几个关系不错的同学）还真有个测试带师（他搞 oi 的而且懂后端）给我测出来个 bug

## 10.3

搞完了 Stage 1，但是逻辑貌似有问题，以及还没有考虑缓存问题，也没有持久化

## 10.4-6

这几天进度出奇的慢。。。赶了几个学校课程和 ACM 的 ddl 感觉要完蛋了（）终于写完了 Stage 2（但是 rank 和 进阶都还没写，图片的缓存问题也还没处理，rank 感觉我由于没用数据库所以不是很好写，手动记录时间戳太麻烦了，所以扬了吧，以后也不打算写了。明天 Rush！
