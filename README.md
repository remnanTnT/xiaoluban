# 小鲁班自验证工具

一个简洁科技感的Web界面，用于在服务器上执行shell命令。

## 功能特性

- **升级功能**: 支持选择环境、输入build_version、选择升级方式
- **测试功能**: 执行自动化测试
- **复位功能**: 恢复系统初始状态

## 项目结构

```
xiaoluban/
├── src/                # Vue前端源码
│   ├── App.vue         # 主组件
│   ├── main.js         # 入口文件
│   └── style.css       # 样式文件
├── server/             # 后端服务
│   ├── package.json    # 后端依赖
│   └── server.js       # Express服务器
├── index.html          # HTML入口
├── package.json        # 前端依赖
└── vite.config.js      # Vite配置
```

## 部署步骤

### 1. 安装依赖

前端:
```bash
npm install
```

后端:
```bash
cd server
npm install
```

### 2. 构建前端

```bash
npm run build
```

生成的文件会在 `dist/` 目录下。

### 3. 部署到服务器

将整个项目上传到服务器:

```bash
scp -r xiaoluban/ user@server:/home/public/
```

或者在服务器上:
```bash
cd /home/public
git clone <your-repo>
cd xiaoluban
npm install
npm run build
cd server
npm install
```

### 4. 启动服务

在服务器上启动Node.js服务:

```bash
cd /home/public/xiaoluban/server
npm run server
```

默认端口: 3000

## 命令示例

升级功能会根据参数生成对应的shell命令:

- 环境号: 25151
- Build Version: 30048100
- 升级方式: CMC快照版本升级 (后缀_3)

生成命令:
```bash
sh update.sh 25151 30048100_3
```

在 `/home/public` 目录下执行。

## 配置说明

### 环境列表
- 25151
- 25152
- 2516
- 2503
- 2514
- 2511
- 2599
- 2521

### 升级方式
- 纯升级: 无后缀
- 流水线取包+升级: 后缀 `_1`
- 升级（压缩包版）: 后缀 `_2`
- CMC快照版本升级: 后缀 `_3`

## 自定义配置

修改 `src/App.vue` 中的配置:

```javascript
const environments = ['25151', '25152', '2516', '2503', '2514', '2511', '2599', '2521']

const upgradeModes = [
  { label: '纯升级', value: '' },
  { label: '流水线取包+升级', value: '1' },
  { label: '升级（压缩包版）', value: '2' },
  { label: 'CMC快照版本升级', value: '3' }
]
```

修改 `server/server.js` 中的工作目录:

```javascript
const workDir = cwd || '/home/public';
```

## 生产部署建议

使用 PM2 管理进程:

```bash
npm install -g pm2
cd /home/public/xiaoluban/server
pm2 start server.js --name xiaoluban
pm2 save
pm2 startup
```

## 开发调试

前端开发模式:
```bash
npm run dev
```

访问: http://localhost:3000