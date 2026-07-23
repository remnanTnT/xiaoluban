-- 初始化数据库表结构
-- 小鲁班环境管理系统

-- 1. 环境配置表
CREATE TABLE IF NOT EXISTS xiaoluban_environments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'idle',
    occupant VARCHAR(100),
    queued_users TEXT,
    is_used BOOLEAN DEFAULT TRUE,
    offline_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 操作历史表
CREATE TABLE IF NOT EXISTS xiaoluban_history (
    id BIGSERIAL PRIMARY KEY,
    env_id BIGINT,
    action VARCHAR(50),
    command TEXT,
    user VARCHAR(100) DEFAULT 'anonymous',
    success BOOLEAN DEFAULT FALSE,
    output TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 环境占用记录表
CREATE TABLE IF NOT EXISTS xiaoluban_environment_usage (
    id BIGSERIAL PRIMARY KEY,
    env_name VARCHAR(100),
    occupant VARCHAR(100),
    occupy_time TIMESTAMP,
    release_time TIMESTAMP,
    is_manual_release VARCHAR(10) DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_environments_name ON xiaoluban_environments(name);
CREATE INDEX IF NOT EXISTS idx_environments_status ON xiaoluban_environments(status);
CREATE INDEX IF NOT EXISTS idx_environments_type ON xiaoluban_environments(type);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON xiaoluban_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_usage_env_name ON xiaoluban_environment_usage(env_name);
CREATE INDEX IF NOT EXISTS idx_usage_occupy_time ON xiaoluban_environment_usage(occupy_time DESC);

-- 添加注释
COMMENT ON TABLE xiaoluban_environments IS '环境配置表';
COMMENT ON TABLE xiaoluban_history IS '操作历史表';
COMMENT ON TABLE xiaoluban_environment_usage IS '环境占用记录表';