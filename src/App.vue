<template>
  <div class="app-container">
    <h1 class="app-title">小鲁班自验证工具</h1>
    <p class="app-subtitle">自动化测试与部署平台</p>
    
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
</template>

<script setup>
import { ref, computed } from 'vue'

const currentAction = ref('')
const selectedEnv = ref('')
const buildVersion = ref('')
const selectedMode = ref('')
const resultMessage = ref('')
const resultType = ref('')

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
    const response = await fetch('/api/execute', {
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
    const response = await fetch('/api/execute', {
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
    const response = await fetch('/api/execute', {
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
</script>

<style scoped>
.app-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}
</style>