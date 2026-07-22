# 小鲁班前端

小鲁班自验证工具的前端应用，基于 Vue 3 + Vite 构建。

## 技术栈

- **框架**：Vue 3
- **构建工具**：Vite 5
- **样式**：原生 CSS（深色科技主题）

## 目录结构

```
frontend/
├── src/
│   ├── App.vue          # 主组件
│   ├── main.js          # 应用入口
│   └── style.css        # 全局样式
├── index.html           # HTML 入口
├── vite.config.js       # Vite 配置
├── package.json         # 依赖配置
└── .env.example         # 环境变量示例
```

## 开发指南

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制环境变量示例：

```bash
cp .env.example .env
```

修改 `.env` 文件，配置后端 API 地址：

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

构建产物位于 `dist/` 目录。

## API 集成

前端通过 `VITE_API_BASE_URL` 环境变量连接后端 API：

| 端点 | 说明 |
|------|------|
| `GET /api/environments` | 获取环境列表 |
| `POST /api/environments/add` | 添加环境 |
| `POST /api/environments/remove` | 移除环境 |
| `POST /api/execute` | 执行命令 |
| `GET /api/history` | 获取历史记录 |

## 部署说明

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

**相关文档：**
- [后端 API 文档](../backend/docs/API.md)
- [部署指南](../backend/docs/DEPLOYMENT.md)