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
            :class="{ occupied: env.occupied, mine: env.occupiedBy === currentUser }"
            @click="toggleEnvironment(env)"
          >
            <div class="env-status-dot" :class="env.occupied ? 'occupied' : 'free'"></div>
            <div class="env-name">{{ env.name }}</div>
            <div class="env-description">{{ env.description || '无备注' }}</div>
            <div v-if="env.occupied" class="env-user">占用: {{ env.occupiedBy }}</div>
            <div v-if="env.queued_users && env.queued_users.length > 0" class="env-queue">
              排队: {{ env.queued_users.join(', ') }}
            </div>
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
            <input 
              type="text" 
              v-model="newEnvDesc" 
              placeholder="备注信息"
              class="input-field"
            />
            <button class="submit-button" @click="addEnvironment">添加环境</button>
          </div>

          <div class="existing-envs">
            <div v-for="env in roceEnvironments" :key="env.id" class="env-item">
              <div class="env-item-info">
                <span class="env-item-name">{{ env.name }}</span>
                <span class="env-item-desc">{{ env.description }}</span>
              </div>
              <button class="delete-button" @click="deleteEnvironment(env.id)">删除</button>
            </div>
          </div>
        </div>
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
      } else {
        alert('释放失败: ' + data.error)
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
          alert(`已加入排队，当前排队位置: 第 ${data.queue_position} 位`)
        } else if (data.action === 'queue_cancelled') {
          alert('已取消排队')
        }
      } else {
        alert('操作失败: ' + data.error)
      }
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败: ' + error.message)
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
}

.env-user {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.env-queue {
  font-size: 0.85rem;
  color: #ffa502;
  margin-top: 4px;
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