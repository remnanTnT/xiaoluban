import express from 'express';
import cors from 'cors';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, '../dist')));

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

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`工作目录: /home/public`);
});