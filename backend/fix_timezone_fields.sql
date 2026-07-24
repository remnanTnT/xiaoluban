-- =====================================================
-- 数据库时间字段修复脚本
-- 将所有naive datetime转换为timezone-aware datetime
-- =====================================================

-- 说明：
-- PostgreSQL的timestamp类型有两种：
-- 1. timestamp without time zone（naive datetime）
-- 2. timestamp with time zone（timezone-aware datetime）
-- 
-- Django设置 USE_TZ=True 时，期望所有字段都是 timezone-aware
-- 但历史数据存储的是 naive datetime（无时区）
-- 
-- 修复策略：
-- 1. 将所有时间字段从 timestamp without time zone 转换为 timestamp with time zone
-- 2. 转换时假设原数据为北京时间（Asia/Shanghai, UTC+8）
-- 3. 这样数据本身不变，但添加了时区信息

-- =====================================================
-- 1. xiaoluban_environments 表
-- =====================================================

-- 添加时区信息（假设原数据为北京时间）
ALTER TABLE xiaoluban_environments 
ALTER COLUMN offline_time TYPE timestamp with time zone 
USING offline_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environments 
ALTER COLUMN created_at TYPE timestamp with time zone 
USING created_at AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environments 
ALTER COLUMN updated_at TYPE timestamp with time zone 
USING updated_at AT TIME ZONE 'Asia/Shanghai';

-- =====================================================
-- 2. xiaoluban_history 表
-- =====================================================

ALTER TABLE xiaoluban_history 
ALTER COLUMN timestamp TYPE timestamp with time zone 
USING timestamp AT TIME ZONE 'Asia/Shanghai';

-- =====================================================
-- 3. xiaoluban_environment_usage 表
-- =====================================================

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN occupy_time TYPE timestamp with time zone 
USING occupy_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN release_time TYPE timestamp with time zone 
USING release_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN created_at TYPE timestamp with time zone 
USING created_at AT TIME ZONE 'Asia/Shanghai';

-- =====================================================
-- 验证修复结果
-- =====================================================

-- 检查字段类型是否已改变
SELECT 
    table_name,
    column_name,
    data_type,
    datetime_precision
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name IN ('xiaoluban_environments', 'xiaoluban_history', 'xiaoluban_environment_usage')
  AND data_type LIKE 'timestamp%'
ORDER BY table_name, column_name;

-- 检查数据是否正确（应该显示时间+08:00时区）
SELECT 'xiaoluban_environments' as table_name, id, created_at, updated_at 
FROM xiaoluban_environments LIMIT 5;

SELECT 'xiaoluban_environment_usage' as table_name, id, occupy_time, release_time 
FROM xiaoluban_environment_usage ORDER BY id DESC LIMIT 5;