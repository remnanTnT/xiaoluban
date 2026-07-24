-- =====================================================
-- 数据库时间字段回滚脚本
-- 将timezone-aware datetime转回naive datetime
-- （仅在需要回滚时使用）
-- =====================================================

-- =====================================================
-- 1. xiaoluban_environments 表
-- =====================================================

ALTER TABLE xiaoluban_environments 
ALTER COLUMN offline_time TYPE timestamp without time zone 
USING offline_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environments 
ALTER COLUMN created_at TYPE timestamp without time zone 
USING created_at AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environments 
ALTER COLUMN updated_at TYPE timestamp without time zone 
USING updated_at AT TIME ZONE 'Asia/Shanghai';

-- =====================================================
-- 2. xiaoluban_history 表
-- =====================================================

ALTER TABLE xiaoluban_history 
ALTER COLUMN timestamp TYPE timestamp without time zone 
USING timestamp AT TIME ZONE 'Asia/Shanghai';

-- =====================================================
-- 3. xiaoluban_environment_usage 表
-- =====================================================

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN occupy_time TYPE timestamp without time zone 
USING occupy_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN release_time TYPE timestamp without time zone 
USING release_time AT TIME ZONE 'Asia/Shanghai';

ALTER TABLE xiaoluban_environment_usage 
ALTER COLUMN created_at TYPE timestamp without time zone 
USING created_at AT TIME ZONE 'Asia/Shanghai';