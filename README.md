# 崩坏3米游社查询
仿[egenshin的player_info](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin/player_info)样式做的崩坏3角色卡片.
- [崩坏3米游社查询](#崩坏3米游社查询)
  - [安装](#安装)
  - [使用](#使用)
  - [更新日志](#更新日志)
    - [2022/3/31](#2022331)
    - [2022/3/17](#2022317)
    - [2022/2/16](#2022216)
    - [2022/2/13](#2022213)
    - [2022/1/28](#2022128)
    - [2022/1/23](#2022123)
  - [致谢](#致谢)
## 安装
- 在插件文件夹下clone本仓库
    ``` bash
    git clone -b nonebot https://github.com/chingkingm/honkai_mys.git
    ```
- 安装依赖
    ``` bash
    pip install -r requirements.txt
    ```
- 重命名 `config_example.yaml` 为 `config.yaml`,并按照格式填入cookie
- 配置语音资源
  - 前往[B站视频](https://www.bilibili.com/video/BV16J41157du)，根据简介下载语音文件
  - 完全解压后放到./assets/record文件夹下
  - ps:5.5版本有一个语音命名有问题，参照[说明](./guess_voice/readme.md)进行重命名
- 修改相应文件以加载插件
- 按需[配置](./autosign/README.md)邮箱

## 使用
| 命令                   | 功能                         | 备注                   |
| ---------------------- | ---------------------------- | ---------------------- |
| bh#                    | 玩家卡片                     |
| bhv#                   | 所有女武神                   |
| bhf                    | 手账                         | 不需要uid              |
| 崩坏3猜语音            | 正常语音                     |
| 崩坏3猜语音困难        | 语气及拟声词                 |
| 崩坏3语音+名字         | 随机发送指定角色或人偶的语音 |
| 更新崩坏3语音列表      |                              | 首次或语音更新后使用   |
| 开启/关闭崩坏3自动签到 |                              | 开启后每天定时自动签到 |
| 崩坏3自动签到          |                              | 手动触发签到           |
1. 通过游戏uid加服务器查询
   - `命令<uid><服务器>`,如`bh#100074751b`.
2. 通过米游社id查询
   - `命令<id><米游社>`,即在提供米游社ID的同时加上"米游社"或"mys",如`bh#75098978米游社`
3. 不提供id
   - `命令`,会查询用户上一次查询的UID信息,如`bh#`

ps:每个uid只有首次查询的时候需要提供服务器.

<details>
<summary>玩家卡片示意图</summary>

![image](./assets/example.png)

</details>

<details>
<summary>女武神卡片示意图</summary>

![image](./assets/example_valk.png)

</details>

<details>
<summary>手账示意图</summary>

![alt](./assets/example_finance.png)

</details>

## 更新日志
### 2022/3/31
1. 新增米游社福利补给自动签到[#26](https://github.com/chingkingm/honkai_mys/issues/26)
   1. 开启后每日4:10或16:10自动执行签到
   2. 签到结果通过私聊发送，如果未添加bot好友，则通过邮件发送(需要[配置smtp](./autosign/README.md)，不配置或不可用则发送给SUPERUSER)
### 2022/3/17
1. 适配乐土、量子流形改动
2. 调整代码结构
3. fix：角色卡片右上角UID超出图片的问题
4. 超弦空间加杯时显示+号
### 2022/2/16
1. 更改了女武神卡片的样式，增加了抬头
2. 调整了装备星级图片的逻辑，现在会保存图片以重复使用
### 2022/2/13
1. 新增猜语音，发送指定角色语音
   1. 初次使用前或资源更新后，发送`更新崩坏3语音列表`以生成或更新语音列表
   2. 语音的分类有些粗犷，会出现例如缭乱星棘不是丽塔这种问题，可以自行调整answer.json或使用`崩坏3语音新增答案缭乱星棘:丽塔`进行添加。
### 2022/1/28
1. 新增查询手账
   1. 支持使用egenshin已绑定的cookie,需要在config中填写配置,详见[config_example.yaml](config_example.yaml)
   2. 支持单独绑定,发送`bhf?`获取帮助
### 2022/1/23
1. 新增查询所有女武神,命令为`bhv#`,注意:第一次生成图片时,因为要下载圣痕,武器的素材,所以耗费的时间较长,可以下载release里的压缩包来减少届时的下载延迟
2. 调整了部分导入,方便调试
3. 新增了水晶手账相关代码,但具体样式未实现,该功能不可用
4. 更新了README,加入了更新日志
5. 完善渠道信息
6. 优化初次查询时的报错信息
## 致谢
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin),用了部分艾琳佬造好的轮子
- [YSJS有所建树](https://space.bilibili.com/402667766)整理的语音素材
- [genshinhelper2](https://github.com/y1ndan/genshinhelper2)