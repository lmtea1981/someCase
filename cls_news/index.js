const axios = require('axios');
const cheerio = require('cheerio');
const readline = require('readline');

// 创建readline接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 财联社网站URL
const CLS_URL = 'https://www.cls.cn';

// 获取页面内容
async function fetchPage(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取页面失败:', error.message);
    return null;
  }
}

// 提取头条新闻
function extractHeadlines(html) {
  const $ = cheerio.load(html);
  const headlines = [];
  
  // 从首页提取新闻链接
  $('a').each((index, element) => {
    const title = $(element).text().trim();
    const link = $(element).attr('href');
    // 筛选有效的新闻链接
    if (title && link && link.includes('/detail/') && title.length > 10) {
      headlines.push({
        title,
        link: link.startsWith('http') ? link : CLS_URL + link
      });
    }
  });
  
  // 去重
  const uniqueHeadlines = [];
  const seenTitles = new Set();
  for (const headline of headlines) {
    if (!seenTitles.has(headline.title)) {
      seenTitles.add(headline.title);
      uniqueHeadlines.push(headline);
    }
  }
  
  // 限制数量
  return uniqueHeadlines.slice(0, 10);
}

// 提取电报信息
function extractTelegrams(html) {
  const $ = cheerio.load(html);
  const telegrams = [];
  
  // 从首页提取新闻链接
  $('a').each((index, element) => {
    const title = $(element).text().trim();
    const link = $(element).attr('href');
    // 筛选有效的新闻链接
    if (title && link && link.includes('/detail/') && title.length > 10) {
      telegrams.push({
        title,
        link: link.startsWith('http') ? link : CLS_URL + link
      });
    }
  });
  
  // 去重
  const uniqueTelegrams = [];
  const seenTitles = new Set();
  for (const telegram of telegrams) {
    if (!seenTitles.has(telegram.title)) {
      seenTitles.add(telegram.title);
      uniqueTelegrams.push(telegram);
    }
  }
  
  // 限制数量
  return uniqueTelegrams.slice(0, 10);
}

// 获取新闻详细内容
async function getNewsDetail(url) {
  try {
    const html = await fetchPage(url);
    if (!html) return '获取详细内容失败';
    
    const $ = cheerio.load(html);
    // 根据财联社网站的实际HTML结构来提取详细内容
    let content = '';
    
    // 尝试不同的选择器
    if ($('.article-content').length > 0) {
      content = $('.article-content').text().trim();
    } else if ($('.content').length > 0) {
      content = $('.content').text().trim();
    } else if ($('.news-content').length > 0) {
      content = $('.news-content').text().trim();
    } else if ($('.article-body').length > 0) {
      content = $('.article-body').text().trim();
    } else if ($('.body').length > 0) {
      content = $('.body').text().trim();
    } else {
      // 尝试提取所有段落
      $('p').each((index, element) => {
        content += $(element).text().trim() + '\n';
      });
      
      // 如果还是没有内容，尝试提取所有文本
      if (!content) {
        content = $('body').text().trim().substring(0, 1000) + '...';
      }
    }
    
    return content || '暂无详细内容';
  } catch (error) {
    console.error('获取详细内容失败:', error.message);
    return '获取详细内容失败';
  }
}

// 显示头条新闻
function displayHeadlines(headlines) {
  console.log('\n=== 财联社头条新闻 ===');
  headlines.forEach((headline, index) => {
    console.log(`${index + 1}. ${headline.title}`);
  });
  console.log('\n');
}

// 显示电报信息
function displayTelegrams(telegrams) {
  console.log('\n=== 财联社电报 ===');
  telegrams.forEach((telegram, index) => {
    console.log(`${index + 1}. ${telegram.title}`);
  });
  console.log('\n');
}

// 主函数
async function main() {
  console.log('正在获取财联社新闻信息...');
  
  // 直接从首页获取新闻信息
  const homeHtml = await fetchPage(CLS_URL);
  let headlines = [];
  let telegrams = [];
  
  if (homeHtml) {
    // 从首页提取头条新闻
    headlines = extractHeadlines(homeHtml);
    // 从首页提取电报信息
    telegrams = extractTelegrams(homeHtml);
  }
  
  // 如果首页没有找到，尝试从电报页面提取
  if (telegrams.length === 0) {
    const telegramHtml = await fetchPage(CLS_URL + '/telegraph');
    if (telegramHtml) {
      telegrams = extractTelegrams(telegramHtml);
    }
  }
  
  // 交互式查询 - 先选择内容类型
  rl.question('请选择要查看的内容类型（1.头条 2.电报），或输入0退出: ', async (typeChoice) => {
    if (typeChoice === '0') {
      rl.close();
      return;
    }
    
    let items;
    let displayFunction;
    
    if (typeChoice === '1') {
      items = headlines;
      displayFunction = displayHeadlines;
      if (items.length === 0) {
        console.log('没有头条新闻可查看');
        rl.close();
        return;
      }
    } else if (typeChoice === '2') {
      items = telegrams;
      displayFunction = displayTelegrams;
      if (items.length === 0) {
        console.log('没有电报信息可查看');
        rl.close();
        return;
      }
    } else {
      console.log('输入有误，请重新运行程序');
      rl.close();
      return;
    }
    
    // 显示对应类型的标题
    displayFunction(items);
    
    // 选择标题
    rl.question('请输入要查看的序号: ', async (indexChoice) => {
      const index = parseInt(indexChoice) - 1;
      if (index >= 0 && index < items.length) {
        const item = items[index];
        console.log(`\n正在获取详细内容: ${item.title}`);
        const detail = await getNewsDetail(item.link);
        console.log('\n=== 详细内容 ===');
        console.log(detail);
        console.log('\n');
      } else {
        console.log('输入的序号有误');
      }
      rl.close();
    });
  });
}

// 运行主函数
main();