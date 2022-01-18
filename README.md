# 崩坏3米游社查询
仿[egenshin的player_info](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin/player_info)样式做的崩坏3角色卡片.

## 安装
- 在hoshino的modules文件夹下clone本仓库
    ``` bash
    git clone https://github.com/chingkingm/honkai_mys.git
    ```
- 安装依赖
    ``` bash
    pip install -r requirements.txt
    ```
- 重命名 `config_example.yaml` 为 `config.yaml`,并按照格式填入cookie
- 修改__bot__.py,加入插件,重启bot

## 使用
1. 通过游戏uid加服务器查询
   - `bh#<uid><服务器>`,如`bh#100074751b`.
2. 通过米游社id查询
   - `bh#<id><米游社>`,即在提供米游社ID的同时加上"米游社"或"mys",如`bh#75098978米游社`
3. 不提供id
   - `bh#`,会查询用户上一次查询的UID信息

ps:每个uid只有首次查询的时候需要提供服务器.

<details>
<summary>示意图</summary>
![im](./assets/example.png)
</details>

## TODO
- [ ] ~~cookie检测及切换cookie(崩坏3这边没有查询次数的限制,鸽了~~
- [ ] ~~兼容egenshin yss绑定的cookie(同上,鸽了~~
- [ ] 水晶手账
