const axios = require('axios');
const fs = require('fs');

// 财联社网站URL
const CLS_URL = 'https://www.cls.cn';

// 获取页面内容
async function fetchPage(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取页面失败:', error.message);
    return null;
  }
}

// 保存HTML到文件
async function saveHtml() {
  const html = await fetchPage(CLS_URL);
  if (html) {
    fs.writeFileSync('cls.html', html);
    console.log('HTML已保存到 cls.html 文件');
  } else {
    console.error('无法获取HTML内容');
  }
}

// 运行
saveHtml();