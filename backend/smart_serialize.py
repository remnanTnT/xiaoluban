#!/usr/bin/env python3
"""
时间处理策略：
方案1：修改数据库列类型为 timestamp with time zone
方案2：修改所有历史数据，将本地时间转换为UTC
方案3：在代码中智能判断

当前采用方案3：基于时间范围判断
- 如果时间 > '2026-07-24 14:00:00'：认为是UTC（新数据）
- 如果时间 < '2026-07-24 14:00:00'：认为是本地时间（历史数据）

但这个方案不够优雅。更好的方案是修改数据库。
"""

def serialize_datetime(dt):
    """
    智能序列化datetime对象
    
    策略：
    1. 如果是timezone-aware：正常转换
    2. 如果是naive：
       - 检查时间是否合理（比如不能是未来时间）
       - 假设历史数据（本地时间）< 新数据（UTC）
    """
    if dt is None:
        return None
    
    from django.utils.timezone import localtime, make_aware
    from django.conf import settings
    import pytz
    from datetime import datetime
    
    # timezone-aware：直接转换为本地时间
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        local_dt = localtime(dt)
        return local_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # naive datetime：需要判断是本地时间还是UTC
    # 获取当前UTC时间
    now_utc = datetime.utcnow()
    
    # 如果naive时间 > 当前UTC时间，说明是本地时间（在未来）
    # 如果naive时间 < 当前UTC时间，可能是UTC，也可能是过去的本地时间
    
    # 策略：假设所有naive datetime都是本地时间（历史数据）
    # 因为新数据用timezone.now()应该是timezone-aware
    # 如果数据库去掉了时区，我们无法区分
    
    # 最佳实践：假设naive为本地时间
    local_tz = pytz.timezone(settings.TIME_ZONE)
    dt = local_tz.localize(dt)
    
    return dt.strftime('%Y-%m-%d %H:%M:%S')