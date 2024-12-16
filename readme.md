# 神经网络设计平台

一个基于Django + Vue.js的神经网络设计与训练平台,提供直观的可视化界面来设计、训练和管理深度学习模型。

## 功能特点

### 1. 可视化模型设计
- 拖拽式神经网络层设计
- 支持多种预定义层类型(卷积层、池化层等)
- 实时模型结构验证
- 模型导入/导出功能
- 层参数可视化配置

### 2. 数据预处理
- 支持多种数据格式(CSV、Excel、JSON)
- 可视化数据预览
- 丰富的预处理操作:
  - 数据清洗
  - 特征转换
  - 编码转换
  - 数据缩放
  - 数据集分割
- 预处理模板管理
- 数据可视化分析

### 3. 模型训练
- 实时训练监控
- 可视化训练指标(损失函数、准确率等)
- 训练过程控制(启动/暂停/恢复)
- 训练日志记录
- 模型性能评估

### 4. 系统功能
- 用户认证与授权
- 实时通知系统
- 资源监控
- 个人设置管理
- RESTful API接口

## 技术栈

### 后端
- Django 5.1.4
- Django REST Framework
- Simple JWT
- Channels (WebSocket)
- SQLite3

### 前端
- Vue.js 3
- Element Plus
- ECharts
- Vuex
- Vue Router
- Axios

## 系统要求

- Python 3.8+
- Node.js 14+
- NPM 6+

## 安装部署

### 1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

### 2. 后端设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 项目结构
```
Net_in_Django/
├── apps/                    # Django应用目录
│   ├── authentication/      # 用户认证
│   ├── dashboard/          # 仪表板
│   ├── data_preprocessing/ # 数据预处理
│   ├── model_editor/      # 模型编辑器
│   ├── model_training/    # 模型训练
│   ├── notifications/     # 通知系统
│   └── visualization/     # 数据可视化
├── frontend/              # Vue.js前端项目
│   ├── src/
│   │   ├── components/   # Vue组件
│   │   ├── views/       # 页面视图
│   │   ├── store/       # Vuex状态管理
│   │   ├── router/      # 路由配置
│   │   └── utils/       # 工具函数
│   └── public/          # 静态资源
└── Net_in_Django/       # Django项目配置
```

## API文档

### 认证接口
```
POST /api/auth/register/     # 用户注册
POST /api/auth/login/        # 用户登录
POST /api/auth/logout/       # 用户登出
PUT  /api/auth/settings/     # 更新用户设置
```

