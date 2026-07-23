<template>
  <div class="app-container">
    <div v-if="!isLoggedIn" class="login-page">
      <h1 class="app-title">小鲁班自验证工具</h1>
      <p class="app-subtitle">自动化测试和环境排队平台</p>
      
      <div class="login-panel">
        <div class="panel-title">W3 账号登录</div>
        
        <div class="param-group">
          <label class="param-label">W3 账号</label>
          <input 
            type="text" 
            class="input-field"
            v-model="loginUid"
            placeholder="请输入 W3 账号"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <div class="param-group">
          <label class="param-label">密码</label>
          <input 
            type="password" 
            class="input-field"
            v-model="loginPassword"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
        </div>
        
        <button 
          class="submit-button" 
          @click="handleLogin"
          :disabled="isLoggingIn || !loginUid || !loginPassword"
        >
          {{ isLoggingIn ? '登录中...' : '登录' }}
        </button>
        
        <div v-if="loginError" class="result-message error">
          {{ loginError }}
        </div>
      </div>
    </div>
    
    <template v-else>
      <div class="header-bar">
        <div class="header-left">
          <h1 class="app-title">小鲁班自验证工具</h1>
          <p class="app-subtitle">自动化测试和环境排队平台</p>
        </div>
        <div class="header-right">
          <span class="user-info">当前用户: {{ currentUser }}</span>
          <button class="logout-button" @click="handleLogout">退出登录</button>
        </div>
      </div>
      
      <div class="tab-container">
      <button 
        class="tab-button"
        :class="{ active: activeTab === 'roce' }"
        @click="activeTab = 'roce'"
      >
        RoCE环境排队
      </button>
      <button 
        class="tab-button"
        :class="{ active: activeTab === 'tool' }"
        @click="activeTab = 'tool'"
      >
        工具操作
      </button>
    </div>

    <div v-if="activeTab === 'tool'" class="tool-page">
      <div class="button-group">
        <button 
          class="action-button"
          :class="{ active: currentAction === 'upgrade' }"
          @click="selectAction('upgrade')"
        >
          升级
        </button>
        <button 
          class="action-button"
          :class="{ active: currentAction === 'test' }"
          @click="selectAction('test')"
        >
          测试
        </button>
        <button 
          class="action-button"
          :class="{ active: currentAction === 'reset' }"
          @click="selectAction('reset')"
        >
          复位
        </button>
      </div>

      <div v-if="currentAction" class="parameter-panel">
        <div v-if="currentAction === 'upgrade'">
          <div class="panel-title">升级参数配置</div>
          
          <div class="param-group">
            <label class="param-label">选择环境</label>
            <div class="env-grid">
              <button
                v-for="env in environments"
                :key="env"
                class="env-option"
                :class="{ selected: selectedEnv === env }"
                @click="selectedEnv = env"
              >
                {{ env }}
              </button>
            </div>
          </div>

          <div class="param-group">
            <label class="param-label">流水线构建 Build Version</label>
            <input 
              type="text" 
              class="input-field"
              v-model="buildVersion"
              placeholder="请输入 build_version，例如: 30048100"
            />
          </div>

          <div class="param-group">
            <label class="param-label">升级方式</label>
            <div class="upgrade-mode-grid">
              <button
                v-for="mode in upgradeModes"
                :key="mode.value"
                class="mode-option"
                :class="{ selected: selectedMode === mode.value }"
                @click="selectedMode = mode.value"
              >
                {{ mode.label }}
              </button>
            </div>
          </div>

          <div v-if="generatedCommand" class="command-preview">
            <div class="command-label">生成的命令：</div>
            <div class="command-text">{{ generatedCommand }}</div>
          </div>

          <button 
            class="submit-button"
            :disabled="!canSubmit"
            @click="executeCommand"
          >
            提交执行
          </button>

          <div v-if="resultMessage" :class="['result-message', resultType]">
            {{ resultMessage }}
          </div>
        </div>

        <div v-else-if="currentAction === 'test'">
          <div class="panel-title">测试功能</div>
          <div class="test-form">
            <div class="test-info">
              <p>测试功能将执行自验证测试流程</p>
              <p style="margin-top: 12px; color: var(--text-secondary);">点击下方按钮开始测试</p>
            </div>
            <button 
              class="submit-button"
              @click="executeTest"
            >
              开始测试
            </button>
            <div v-if="resultMessage" :class="['result-message', resultType]">
              {{ resultMessage }}
            </div>
          </div>
        </div>

        <div v-else-if="currentAction === 'reset'">
          <div class="panel-title">复位功能</div>
          <div class="reset-form">
            <div class="reset-info">
              <p>复位功能将恢复系统至初始状态</p>
              <p style="margin-top: 12px; color: var(--text-secondary);">点击下方按钮执行复位</p>
            </div>
            <button 
              class="submit-button"
              @click="executeReset"
            >
              执行复位
            </button>
            <div v-if="resultMessage" :class="['result-message', resultType]">
              {{ resultMessage }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="activeTab === 'roce'" class="roce-page">
      <div class="roce-header">
        <button class="edit-button" @click="showEditModal = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          编辑环境
        </button>
      </div>

      <div class="roce-content">
        <div class="environments-grid">
          <div 
            v-for="env in roceEnvironments" 
            :key="env.id" 
            class="env-card"
            :class="{ occupied: env.occupied, mine: env.occupiedBy === currentUser, queued: isInQueue(env) }"
            @click="toggleEnvironment(env)"
          >
            <div class="env-status-dot" :class="env.occupied ? 'occupied' : 'free'"></div>
            <div class="env-name">{{ env.name }}</div>
            
            <!-- 备注信息显示 -->
            <div v-if="env.description" class="env-description-wrapper">
              <div 
                class="env-description"
                :class="{ 'has-more': isTextOverflow(env.description) }"
              >
                {{ truncateText(env.description) }}
                
                <!-- 备注信息tooltip -->
                <div v-if="isTextOverflow(env.description)" class="desc-tooltip">
                  <div class="desc-tooltip-header">
                    <span>完整备注信息</span>
                  </div>
                  <div class="desc-tooltip-content">{{ env.description }}</div>
                </div>
              </div>
              
              <!-- 复制按钮 -->
              <button 
                class="copy-desc-button"
                @click.stop="copyToClipboard(env.description)"
                title="复制备注"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
            <div v-else class="env-description">无备注</div>
            
            <!-- 占用状态显示 -->
            <div v-if="env.occupied" class="env-user">
              <span v-if="env.occupiedBy === currentUser" class="env-status-mine">正在占用</span>
              <span v-else>当前占用人: {{ env.occupiedBy }}</span>
            </div>
            
            <!-- 排队信息显示 -->
            <template v-if="env.queued_users && env.queued_users.length > 0">
              <!-- 自己占用时，显示排队人数 -->
              <div v-if="env.occupiedBy === currentUser" class="env-queue queue-info-wrapper">
                <span class="queue-info-text">
                  排队人数: {{ env.queued_users.length }}人
                  <span class="queue-tooltip">
                    <div v-for="(user, index) in env.queued_users" :key="index" class="queue-user-item">
                      {{ index + 1 }}. {{ user }}
                    </div>
                  </span>
                </span>
              </div>
              <!-- 自己在排队时，显示前面还有几位 -->
              <div v-else-if="isInQueue(env)" class="env-queue-mine queue-info-wrapper">
                <span class="queue-info-text">
                  前面还有 {{ getQueuePosition(env) }} 位
                  <span class="queue-tooltip">
                    <div v-for="(user, index) in env.queued_users" :key="index" class="queue-user-item">
                      {{ index + 1 }}. {{ user }}
                    </div>
                  </span>
                </span>
              </div>
              <!-- 其他人占用，显示排队列表 -->
              <div v-else class="env-queue queue-info-wrapper">
                <span class="queue-info-text">
                  排队: {{ env.queued_users.length }}人
                  <span class="queue-tooltip">
                    <div v-for="(user, index) in env.queued_users" :key="index" class="queue-user-item">
                      {{ index + 1 }}. {{ user }}
                    </div>
                  </span>
                </span>
              </div>
            </template>
            
            <div v-if="env.occupiedAt" class="env-time">{{ formatTime(env.occupiedAt) }}</div>
          </div>
        </div>

        <div class="history-panel">
          <div class="panel-title">占用历史记录</div>
          <select v-model="selectedHistoryEnv" class="env-select">
            <option value="">选择环境查看历史</option>
            <option v-for="env in roceEnvironments" :key="env.id" :value="env.name">
              {{ env.name }}
            </option>
          </select>
          
          <div v-if="selectedHistoryEnv && historyData.length > 0" class="usage-list">
            <div 
              v-for="item in historyData" 
              :key="item.id" 
              class="usage-item"
            >
              <div class="usage-header">
                <span class="usage-occupant">{{ item.occupant }}</span>
                <span class="usage-time">{{ formatDateTime(item.occupy_time) }}</span>
              </div>
              <div class="usage-details">
                <span class="usage-label">占用时间:</span> {{ formatFullDateTime(item.occupy_time) }}
                <br>
                <span class="usage-label">释放时间:</span> {{ item.release_time ? formatFullDateTime(item.release_time) : '未释放' }}
                <br>
                <span class="usage-label">释放方式:</span> {{ item.is_manual_release === 'manual' ? '手动释放' : '自动释放' }}
              </div>
            </div>
          </div>
          
          <div v-else-if="selectedHistoryEnv" class="no-data">
            暂无占用记录
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>编辑环境</h3>
          <button class="close-button" @click="showEditModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="add-form">
            <input 
              type="text" 
              v-model="newEnvName" 
              placeholder="环境名称（如: 25151）"
              class="input-field"
            />
            <textarea 
              v-model="newEnvDesc" 
              placeholder="备注信息（支持换行）"
              class="input-field textarea-field"
              rows="3"
            ></textarea>
            <button class="submit-button" @click="addEnvironment">添加环境</button>
          </div>

          <div class="existing-envs">
            <div v-for="env in roceEnvironments" :key="env.id" class="env-item">
              <div class="env-item-info">
                <span class="env-item-name">{{ env.name }}</span>
                <span class="env-item-desc">{{ env.description }}</span>
              </div>
              <div class="env-item-actions">
                <button class="edit-env-button" @click="openEditEnvModal(env)">编辑</button>
                <button class="delete-button" @click="deleteEnvironment(env.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑环境信息模态框 -->
    <div v-if="showEditEnvModal" class="modal-overlay" @click.self="showEditEnvModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>编辑环境信息</h3>
          <button class="close-button" @click="showEditEnvModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <div class="add-form">
            <input 
              type="text" 
              v-model="editEnvName" 
              placeholder="环境名称"
              class="input-field"
            />
            <textarea 
              v-model="editEnvDesc" 
              placeholder="备注信息（支持换行）"
              class="input-field textarea-field"
              rows="3"
            ></textarea>
            <div class="form-actions">
              <button class="cancel-button" @click="showEditEnvModal = false">取消</button>
              <button class="submit-button" @click="updateEnvironment">保存</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast 通知组件 -->
    <div v-if="toast.show" class="toast-container">
      <div :class="['toast', `toast-${toast.type}`]">
        <div class="toast-icon">
          <svg v-if="toast.type === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <svg v-else-if="toast.type === 'error'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div class="toast-content">{{ toast.message }}</div>
        <button class="toast-close" @click="toast.show = false">×</button>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const activeTab = ref('roce')
const currentAction = ref('')
const selectedEnv = ref('')
const buildVersion = ref('')
const selectedMode = ref('')
const resultMessage = ref('')
const resultType = ref('')

const isLoggedIn = ref(!!localStorage.getItem('xiaoluban_user'))
const currentUser = ref(localStorage.getItem('xiaoluban_user') || '')
const loginUid = ref('')
const loginPassword = ref('')
const loginError = ref('')
const isLoggingIn = ref(false)

const roceEnvironments = ref([])
const showEditModal = ref(false)
const newEnvName = ref('')
const newEnvDesc = ref('')
const selectedHistoryEnv = ref('')
const historyData = ref([])

// 编辑环境信息相关状态
const showEditEnvModal = ref(false)
const editEnvId = ref(null)
const editEnvName = ref('')
const editEnvDesc = ref('')

// Toast 通知状态
const toast = ref({
  show: false,
  message: '',
  type: 'info' // success, error, info
})

const environments = ['25151', '25152', '2516', '2503', '2514', '2511', '2599', '2521']

const upgradeModes = [
  { label: '纯升级', value: '' },
  { label: '流水线取包+升级', value: '1' },
  { label: '升级（压缩包版）', value: '2' },
  { label: 'CMC快照版本升级', value: '3' }
]

const generatedCommand = computed(() => {
  if (!selectedEnv.value || !buildVersion.value) return ''
  
  const versionSuffix = selectedMode.value 
    ? `${buildVersion.value}_${selectedMode.value}` 
    : buildVersion.value
  
  return `sh update.sh ${selectedEnv.value} ${versionSuffix}`
})

const canSubmit = computed(() => {
  return selectedEnv.value && buildVersion.value
})

const last7Days = computed(() => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  return days
})

function selectAction(action) {
  currentAction.value = action
  resultMessage.value = ''
  resultType.value = ''
  
  if (action !== 'upgrade') {
    selectedEnv.value = ''
    buildVersion.value = ''
    selectedMode.value = ''
  }
}

// Toast 通知函数
function showToast(message, type = 'info') {
  toast.value = {
    show: true,
    message,
    type
  }
  
  // 3秒后自动关闭
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

async function executeCommand() {
  if (!canSubmit.value) return
  
  resultMessage.value = '正在执行命令...'
  resultType.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/api/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: generatedCommand.value,
        cwd: '/home/public'
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      resultMessage.value = `执行成功！\n命令: ${generatedCommand.value}\n输出: ${data.output || '无输出'}`
      resultType.value = 'success'
    } else {
      resultMessage.value = `执行失败: ${data.error || '未知错误'}`
      resultType.value = 'error'
    }
  } catch (error) {
    resultMessage.value = `请求失败: ${error.message}`
    resultType.value = 'error'
  }
}

async function executeTest() {
  resultMessage.value = '正在执行测试...'
  resultType.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/api/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: 'sh test.sh',
        cwd: '/home/public'
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      resultMessage.value = `测试完成！\n输出: ${data.output || '无输出'}`
      resultType.value = 'success'
    } else {
      resultMessage.value = `测试失败: ${data.error || '未知错误'}`
      resultType.value = 'error'
    }
  } catch (error) {
    resultMessage.value = `请求失败: ${error.message}`
    resultType.value = 'error'
  }
}

async function executeReset() {
  resultMessage.value = '正在执行复位...'
  resultType.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/api/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: 'sh reset.sh',
        cwd: '/home/public'
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      resultMessage.value = `复位完成！\n输出: ${data.output || '无输出'}`
      resultType.value = 'success'
    } else {
      resultMessage.value = `复位失败: ${data.error || '未知错误'}`
      resultType.value = 'error'
    }
  } catch (error) {
    resultMessage.value = `请求失败: ${error.message}`
    resultType.value = 'error'
  }
}

async function loadEnvironments() {
  try {
    const response = await fetch(`${API_BASE}/api/environments`)
    const data = await response.json()
    if (data.success) {
      const envMap = {}
      data.environments.forEach(env => {
        envMap[env.name] = {
          ...env,
          occupied: env.status === 'occupied',
          occupiedBy: env.occupant || ''
        }
      })
      
      const existingOrder = roceEnvironments.value.map(e => e.name)
      const newOrder = data.environments.map(e => e.name)
      
      if (existingOrder.length > 0 && existingOrder.join(',') === newOrder.join(',')) {
        roceEnvironments.value = roceEnvironments.value.map(env => ({
          ...envMap[env.name],
          id: env.id
        }))
      } else {
        roceEnvironments.value = data.environments
          .sort((a, b) => a.name.localeCompare(b.name))
          .map(env => ({
            ...env,
            occupied: env.status === 'occupied',
            occupiedBy: env.occupant || ''
          }))
      }
      
      // 默认选择第一个环境查看历史记录
      if (!selectedHistoryEnv.value && roceEnvironments.value.length > 0) {
        selectedHistoryEnv.value = roceEnvironments.value[0].name
      }
    }
  } catch (error) {
    console.error('加载环境失败:', error)
  }
}

function isInQueue(env) {
  return env.queued_users && env.queued_users.includes(currentUser.value)
}

function getQueuePosition(env) {
  if (!env.queued_users) return 0
  const index = env.queued_users.indexOf(currentUser.value)
  return index >= 0 ? index : 0
}

// 截取文本前3行，并对每行进行字符限制
function truncateText(text, maxLines = 3, maxCharsPerLine = 50) {
  if (!text) return ''
  const lines = text.split('\n')
  
  // 截取行数
  const truncatedLines = lines.slice(0, maxLines)
  
  // 对每行进行字符限制
  const processedLines = truncatedLines.map(line => {
    if (line.length > maxCharsPerLine) {
      return line.substring(0, maxCharsPerLine) + '...'
    }
    return line
  })
  
  // 如果总行数超过maxLines，添加省略号
  if (lines.length > maxLines) {
    return processedLines.join('\n') + '...'
  }
  
  return processedLines.join('\n')
}

// 判断文本是否超过指定行数或单行字符数限制
function isTextOverflow(text, maxLines = 3, maxCharsPerLine = 50) {
  if (!text) return false
  const lines = text.split('\n')
  
  // 检查行数是否超过
  if (lines.length > maxLines) return true
  
  // 检查是否有单行字符数超过限制
  for (const line of lines) {
    if (line.length > maxCharsPerLine) return true
  }
  
  return false
}

// 复制文本到剪贴板
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    showToast('备注信息已复制到剪贴板', 'success')
  } catch (error) {
    console.error('复制失败:', error)
    showToast('复制失败，请手动复制', 'error')
  }
}

async function toggleEnvironment(env) {
  try {
    // 如果环境被自己占用，释放
    if (env.occupied && env.occupiedBy === currentUser.value) {
      const response = await fetch(`${API_BASE}/api/environments/release`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: env.name })
      })
      const data = await response.json()
      if (data.success) {
        await loadEnvironments()
        if (selectedHistoryEnv.value === env.name) {
          await loadHistory()
        }
        showToast('环境已成功释放', 'success')
      } else {
        showToast('释放失败: ' + data.error, 'error')
      }
    } else {
      // 其他情况都调用 occupy 接口，后端会处理排队逻辑
      const response = await fetch(`${API_BASE}/api/environments/occupy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: env.name, occupant: currentUser.value })
      })
      const data = await response.json()
      if (data.success) {
        await loadEnvironments()
        if (selectedHistoryEnv.value === env.name) {
          await loadHistory()
        }
        // 显示操作结果
        if (data.action === 'queued') {
          showToast(`已加入排队，当前排队位置: 第 ${data.queue_position} 位`, 'info')
        } else if (data.action === 'queue_cancelled') {
          showToast('已取消排队', 'info')
        } else if (data.action === 'occupied') {
          showToast('环境占用成功', 'success')
        }
      } else {
        showToast('操作失败: ' + data.error, 'error')
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    showToast('操作失败: ' + error.message, 'error')
  }
}

async function addEnvironment() {
  if (!newEnvName.value) return
  
  try {
    const response = await fetch(`${API_BASE}/api/environments/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newEnvName.value,
        description: newEnvDesc.value
      })
    })
    const data = await response.json()
    if (data.success) {
      newEnvName.value = ''
      newEnvDesc.value = ''
      await loadEnvironments()
    }
  } catch (error) {
    console.error('添加环境失败:', error)
  }
}

async function deleteEnvironment(id) {
  try {
    const response = await fetch(`${API_BASE}/api/environments/${id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.success) {
      await loadEnvironments()
    }
  } catch (error) {
    console.error('删除环境失败:', error)
  }
}

function openEditEnvModal(env) {
  editEnvId.value = env.id
  editEnvName.value = env.name
  editEnvDesc.value = env.description || ''
  showEditEnvModal.value = true
}

async function updateEnvironment() {
  if (!editEnvName.value.trim()) {
    showToast('环境名称不能为空', 'error')
    return
  }
  
  try {
    const response = await fetch(`${API_BASE}/api/environments/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: editEnvId.value,
        name: editEnvName.value.trim(),
        description: editEnvDesc.value.trim()
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      showEditEnvModal.value = false
      await loadEnvironments()
      showToast('环境信息已更新', 'success')
    } else {
      showToast('更新失败: ' + (data.error || '未知错误'), 'error')
    }
  } catch (error) {
    console.error('更新环境失败:', error)
    showToast('更新环境失败: ' + error.message, 'error')
  }
}

async function handleLogin() {
  if (!loginUid.value || !loginPassword.value) {
    loginError.value = '请输入账号和密码'
    return
  }
  
  isLoggingIn.value = true
  loginError.value = ''
  
  try {
    const response = await fetch(`${API_BASE}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uid: loginUid.value,
        password: loginPassword.value
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      currentUser.value = data.uid
      isLoggedIn.value = true
      localStorage.setItem('xiaoluban_user', data.uid)
      loginUid.value = ''
      loginPassword.value = ''
    } else {
      loginError.value = data.error || '登录失败'
    }
  } catch (error) {
    loginError.value = '网络错误，请稍后重试'
  } finally {
    isLoggingIn.value = false
  }
}

function handleLogout() {
  currentUser.value = ''
  isLoggedIn.value = false
  localStorage.removeItem('xiaoluban_user')
}

async function loadHistory() {
  if (!selectedHistoryEnv.value) {
    historyData.value = []
    return
  }
  
  try {
    const response = await fetch(`${API_BASE}/api/environments/usage?env_name=${encodeURIComponent(selectedHistoryEnv.value)}&limit=10`)
    const data = await response.json()
    if (data.success) {
      historyData.value = data.usages
    }
  } catch (error) {
    console.error('加载历史失败:', error)
  }
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function formatDateTime(timestamp) {
  const date = new Date(timestamp)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function formatFullDateTime(timestamp) {
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

function getTimelineStyle(item) {
  const timestamp = new Date(item.timestamp)
  const now = new Date()
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  
  const totalMs = now.getTime() - sevenDaysAgo.getTime()
  const itemMs = timestamp.getTime() - sevenDaysAgo.getTime()
  const percentage = (itemMs / totalMs) * 100
  
  return {
    left: `${Math.max(0, Math.min(100, percentage))}%`
  }
}

watch(selectedHistoryEnv, loadHistory)

onMounted(() => {
  loadEnvironments()
})
</script>

<style scoped>
/* 科技感滚动条样式 - 全局样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 212, 255, 0.5) rgba(0, 0, 0, 0.1);
}

*::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

*::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

*::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.6) 0%, rgba(138, 43, 226, 0.6) 100%);
  border-radius: 4px;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

*::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.8) 0%, rgba(138, 43, 226, 0.8) 100%);
  box-shadow: 0 0 8px rgba(0, 212, 255, 0.5);
}

*::-webkit-scrollbar-corner {
  background: transparent;
}

.app-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.tab-container {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  justify-content: center;
}

.tab-button {
  padding: 12px 32px;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid var(--border-color);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button:hover {
  border-color: var(--primary-color);
  background: rgba(0, 212, 255, 0.05);
}

.tab-button.active {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: var(--bg-dark);
}

.roce-page {
  padding: 20px;
}

.roce-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.edit-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-button:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--primary-color);
}

.roce-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  align-items: start;
}

.environments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.env-card {
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  min-height: 140px;
}

.env-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.env-card.occupied {
  border-color: #ff4757;
  background: rgba(255, 71, 87, 0.05);
}

.env-card.mine {
  border-color: var(--success-color);
  background: rgba(0, 255, 136, 0.05);
}

.env-card.queued {
  border-color: var(--primary-color);
  background: rgba(0, 212, 255, 0.05);
}

.env-status-dot {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.env-status-dot.free {
  background: var(--success-color);
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
}

.env-status-dot.occupied {
  background: #ff4757;
  box-shadow: 0 0 12px rgba(255, 71, 87, 0.6);
}

.env-name {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.env-description {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
}

.env-description-wrapper {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.env-description-wrapper .env-description {
  flex: 1;
  margin-bottom: 0;
}

.env-description.has-more {
  cursor: help;
  position: relative;
}

.env-description:hover .desc-tooltip {
  display: block;
}

.desc-tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 0;
  min-width: 350px;
  max-width: 500px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 12px;
  z-index: 10;
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  animation: tooltipFadeIn 0.2s ease-out;
  max-height: 300px;
  overflow-y: auto;
}

.desc-tooltip-header {
  font-size: 0.75rem;
  color: rgba(0, 212, 255, 0.9);
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.desc-tooltip-content {
  font-size: 0.85rem;
  color: white;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
}

.copy-desc-button {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.copy-desc-button:hover {
  background: var(--primary-color);
  color: white;
  opacity: 1;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.5);
}

.env-user {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.env-status-mine {
  color: var(--success-color);
  font-weight: 600;
}

.env-queue {
  font-size: 0.85rem;
  color: #ffa502;
  margin-top: 4px;
}

.queue-info-wrapper {
  position: relative;
}

.queue-info-text {
  cursor: help;
  position: relative;
  display: inline-block;
}

.queue-info-text:hover .queue-tooltip {
  display: block;
}

.queue-tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%);
  backdrop-filter: blur(10px);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 0.85rem;
  min-width: 180px;
  max-width: 280px;
  z-index: 100;
  margin-bottom: 12px;
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  animation: tooltipFadeIn 0.2s ease-out;
}

.queue-tooltip::before {
  content: '排队用户';
  display: block;
  font-size: 0.75rem;
  color: rgba(0, 212, 255, 0.9);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.queue-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid rgba(0, 212, 255, 0.3);
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.queue-user-item {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}

.queue-user-item:last-child {
  border-bottom: none;
}

.queue-user-item::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-color);
  box-shadow: 0 0 8px var(--primary-color);
  flex-shrink: 0;
}

.queue-user-item:last-child {
  border-bottom: none;
}

.env-queue-mine {
  font-size: 0.85rem;
  color: var(--primary-color);
  margin-top: 4px;
  font-weight: 500;
}

.env-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.history-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.history-panel::-webkit-scrollbar {
  width: 6px;
}

.history-panel::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}

.history-panel::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.history-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}

.env-select {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 0.95rem;
  margin-top: 16px;
  cursor: pointer;
}

.env-select option {
  background: var(--bg-card);
  color: var(--text-primary);
}

.history-chart {
  margin-top: 20px;
}

.chart-container {
  position: relative;
  padding: 20px 0;
}

.timeline-axis {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.day-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.timeline-items {
  position: relative;
  height: 60px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.timeline-item {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
}

.timeline-item.occupy {
  background: #ff4757;
  box-shadow: 0 0 8px rgba(255, 71, 87, 0.6);
}

.timeline-item.release {
  background: var(--success-color);
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
}

.timeline-item:hover {
  transform: translateY(-50%) scale(1.5);
}

.timeline-item:hover .tooltip {
  display: block;
}

.tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 10;
  margin-bottom: 8px;
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  color: var(--primary-color);
  font-size: 1.3rem;
}

.close-button {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.existing-envs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.env-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.env-item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.env-item-name {
  font-weight: 600;
  color: var(--primary-color);
}

.env-item-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.3;
}

.textarea-field {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.delete-button {
  padding: 6px 16px;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid #ff4757;
  color: #ff4757;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.delete-button:hover {
  background: #ff4757;
  color: white;
}

.env-item-actions {
  display: flex;
  gap: 8px;
}

.edit-env-button {
  padding: 6px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.edit-env-button:hover {
  background: var(--primary-color);
  color: white;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.cancel-button {
  flex: 1;
  padding: 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--text-secondary);
}

/* Toast 通知样式 */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  animation: toastSlideIn 0.3s ease-out;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: white;
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  min-width: 300px;
  max-width: 500px;
}

.toast-success {
  border-color: rgba(0, 255, 136, 0.5);
  box-shadow: 
    0 0 20px rgba(0, 255, 136, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.toast-error {
  border-color: rgba(255, 71, 87, 0.5);
  box-shadow: 
    0 0 20px rgba(255, 71, 87, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.toast-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-success .toast-icon {
  color: var(--success-color);
}

.toast-error .toast-icon {
  color: #ff4757;
}

.toast-content {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.4;
}

.toast-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

@media (max-width: 1024px) {
  .roce-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .environments-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>