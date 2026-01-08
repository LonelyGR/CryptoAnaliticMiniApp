const https = require('https');
const http = require('http');

const url = process.argv[2] || 'https://cold-rice-yawn.loca.lt';

console.log('============================================================');
console.log('ПРОВЕРКА ДОСТУПНОСТИ API');
console.log('============================================================');
console.log(`\nПроверяю: ${url}\n`);

const urlObj = new URL(url);
const isHttps = urlObj.protocol === 'https:';
const client = isHttps ? https : http;

const options = {
  hostname: urlObj.hostname,
  port: urlObj.port || (isHttps ? 443 : 80),
  path: '/',
  method: 'GET',
  timeout: 5000
};

const req = client.request(options, (res) => {
  console.log(`✅ Статус: ${res.statusCode}`);
  console.log(`✅ Заголовки:`, res.headers);
  
  if (res.statusCode === 200) {
    console.log('\n✅ СЕРВЕР ДОСТУПЕН!');
    console.log('\nПроверьте в браузере:');
    console.log(`   ${url}/docs`);
  } else {
    console.log(`\n⚠️ Сервер отвечает, но статус: ${res.statusCode}`);
  }
  
  process.exit(0);
});

req.on('error', (error) => {
  console.log(`\n❌ ОШИБКА: ${error.message}`);
  console.log('\nВозможные причины:');
  console.log('1. Backend не запущен');
  console.log('2. localtunnel не запущен');
  console.log('3. URL изменился (localtunnel дает новый URL при каждом запуске)');
  console.log('\nПроверьте:');
  console.log('- Запущен ли backend: cd backend && python run.py');
  console.log('- Запущен ли localtunnel: lt --port 8000');
  console.log('- Обновлен ли .env с правильным URL');
  process.exit(1);
});

req.on('timeout', () => {
  console.log('\n❌ ТАЙМАУТ: Сервер не отвечает');
  req.destroy();
  process.exit(1);
});

req.end();
