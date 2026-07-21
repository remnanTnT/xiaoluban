import express from 'express';
import cors from 'cors';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';
import cron from 'node-cron';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DATA_FILE = path.join(__dirname, 'data.json');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, '../dist')));

async function loadData() {
  try {
    const data = await fs.readFile(DATA_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    const defaultData = {
      environments: [],
      history: []
    };
    await fs.writeFile(DATA_FILE, JSON.stringify(defaultData, null, 2));
    return defaultData;
  }
}

async function saveData(data) {
  await fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2));
}

async function addHistory(envId, action, user) {
  const data = await loadData();
  data.history.push({
    id: Date.now(),
    envId,
    action,
    user: user || 'anonymous',
    timestamp: new Date().toISOString()
  });
  await saveData(data);
}

app.post('/api/execute', async (req, res) => {
  const { command, cwd } = req.body;
  
  if (!command) {
    return res.status(400).json({ 
      success: false, 
      error: '命令不能为空' 
    });
  }
  
  const workDir = cwd || '/home/public';
  
  console.log(`执行命令: ${command}`);
  console.log(`工作目录: ${workDir}`);
  
  try {
    const { stdout, stderr } = await execAsync(command, {
      cwd: workDir,
      maxBuffer: 1024 * 1024 * 10,
      timeout: 300000
    });
    
    console.log('执行成功');
    console.log('输出:', stdout);
    if (stderr) console.log('错误输出:', stderr);
    
    res.json({
      success: true,
      output: stdout || stderr || '命令执行完成'
    });
  } catch (error) {
    console.error('执行失败:', error.message);
    
    res.json({
      success: false,
      error: error.message,
      output: error.stdout || error.stderr || ''
    });
  }
});

app.get('/api/environments', async (req, res) => {
  try {
    const data = await loadData();
    res.json({ success: true, environments: data.environments });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/environments/add', async (req, res) => {
  try {
    const { name, description } = req.body;
    
    if (!name) {
      return res.status(400).json({ 
        success: false, 
        error: '环境名称不能为空' 
      });
    }
    
    const data = await loadData();
    
    const newEnv = {
      id: Date.now(),
      name,
      description: description || '',
      occupied: false,
      occupiedBy: null,
      occupiedAt: null
    };
    
    data.environments.push(newEnv);
    await saveData(data);
    
    res.json({ success: true, environment: newEnv });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.delete('/api/environments/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const data = await loadData();
    
    const index = data.environments.findIndex(env => env.id === parseInt(id));
    if (index === -1) {
      return res.status(404).json({ 
        success: false, 
        error: '环境不存在' 
      });
    }
    
    data.environments.splice(index, 1);
    await saveData(data);
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/environments/occupy/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { user } = req.body;
    
    const data = await loadData();
    const env = data.environments.find(env => env.id === parseInt(id));
    
    if (!env) {
      return res.status(404).json({ 
        success: false, 
        error: '环境不存在' 
      });
    }
    
    if (env.occupied) {
      return res.status(400).json({ 
        success: false, 
        error: '环境已被占用' 
      });
    }
    
    env.occupied = true;
    env.occupiedBy = user || 'anonymous';
    env.occupiedAt = new Date().toISOString();
    
    await saveData(data);
    await addHistory(env.id, 'occupy', user);
    
    res.json({ success: true, environment: env });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/environments/release/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { user } = req.body;
    
    const data = await loadData();
    const env = data.environments.find(env => env.id === parseInt(id));
    
    if (!env) {
      return res.status(404).json({ 
        success: false, 
        error: '环境不存在' 
      });
    }
    
    if (!env.occupied) {
      return res.status(400).json({ 
        success: false, 
        error: '环境未被占用' 
      });
    }
    
    env.occupied = false;
    env.occupiedBy = null;
    env.occupiedAt = null;
    
    await saveData(data);
    await addHistory(env.id, 'release', user);
    
    res.json({ success: true, environment: env });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/environments/:id/history', async (req, res) => {
  try {
    const { id } = req.params;
    const data = await loadData();
    
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    const history = data.history.filter(h => 
      h.envId === parseInt(id) && 
      new Date(h.timestamp) >= sevenDaysAgo
    ).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    res.json({ success: true, history });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

cron.schedule('0 0 * * *', async () => {
  console.log('定时任务：释放所有环境');
  try {
    const data = await loadData();
    data.environments.forEach(env => {
      if (env.occupied) {
        addHistory(env.id, 'release', 'system');
        env.occupied = false;
        env.occupiedBy = null;
        env.occupiedAt = null;
      }
    });
    await saveData(data);
    console.log('所有环境已释放');
  } catch (error) {
    console.error('释放环境失败:', error);
  }
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`工作目录: /home/public`);
});