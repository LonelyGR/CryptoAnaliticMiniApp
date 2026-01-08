/**
 * Диагностический скрипт для проверки подключения к API
 * Запустите: node diagnose_connection.js
 */

const fs = require('fs');
const path = require('path');

console.log('='.repeat(60));
console.log('ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К API');
console.log('='.repeat(60));
console.log();

// 1. Проверка .env файла
console.log('[1/5] Проверка .env файла...');
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  console.log('✓ Файл .env существует');
  const content = fs.readFileSync(envPath, 'utf8');
  console.log('Содержимое:');
  console.log(content);
  
  // Проверка формата
  const lines = content.split('\n').filter(line => line.trim());
  let foundApiUrl = false;
  let apiUrl = null;
  
  for (const line of lines) {
    if (line.includes('REACT_APP_API_URL')) {
      foundApiUrl = true;
      const match = line.match(/REACT_APP_API_URL\s*=\s*(.+)/);
      if (match) {
        apiUrl = match[1].trim();
        // Убираем кавычки если есть
        apiUrl = apiUrl.replace(/^["']|["']$/g, '');
        console.log(`✓ Найден URL: ${apiUrl}`);
        
        // Проверка формата
        if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
          console.log('⚠ ПРЕДУПРЕЖДЕНИЕ: URL должен начинаться с http:// или https://');
        }
        if (apiUrl.includes('localhost') && apiUrl.includes('ngrok')) {
          console.log('⚠ ПРЕДУПРЕЖДЕНИЕ: Используется localhost, но должен быть ngrok URL для Telegram');
        }
      } else {
        console.log('✗ ОШИБКА: Неправильный формат строки REACT_APP_API_URL');
        console.log('Должно быть: REACT_APP_API_URL=https://url.com');
      }
    }
  }
  
  if (!foundApiUrl) {
    console.log('✗ ОШИБКА: Переменная REACT_APP_API_URL не найдена в .env');
  }
} else {
  console.log('✗ ФАЙЛ .env НЕ НАЙДЕН!');
  console.log('Создайте файл miniapp/react-app/.env');
  console.log('С содержимым:');
  console.log('REACT_APP_API_URL=https://ваш-backend-url.com');
}

console.log();

// 2. Проверка api.js
console.log('[2/5] Проверка api.js...');
const apiPath = path.join(__dirname, 'src', 'services', 'api.js');
if (fs.existsSync(apiPath)) {
  console.log('✓ Файл api.js существует');
  const apiContent = fs.readFileSync(apiPath, 'utf8');
  
  if (apiContent.includes('process.env.REACT_APP_API_URL')) {
    console.log('✓ Используется process.env.REACT_APP_API_URL');
  } else {
    console.log('✗ ОШИБКА: process.env.REACT_APP_API_URL не используется');
  }
  
  if (apiContent.includes('API_BASE_URL')) {
    console.log('✓ Переменная API_BASE_URL определена');
  }
} else {
  console.log('✗ Файл api.js не найден!');
}

console.log();

// 3. Проверка структуры проекта
console.log('[3/5] Проверка структуры проекта...');
const expectedPaths = [
  { path: path.join(__dirname, 'src', 'services', 'api.js'), name: 'api.js' },
  { path: path.join(__dirname, 'src', 'App.js'), name: 'App.js' },
  { path: path.join(__dirname, 'package.json'), name: 'package.json' },
];

for (const item of expectedPaths) {
  if (fs.existsSync(item.path)) {
    console.log(`✓ ${item.name} найден`);
  } else {
    console.log(`✗ ${item.name} НЕ найден!`);
  }
}

console.log();

// 4. Проверка импортов
console.log('[4/5] Проверка импортов в App.js...');
const appPath = path.join(__dirname, 'src', 'App.js');
if (fs.existsSync(appPath)) {
  const appContent = fs.readFileSync(appPath, 'utf8');
  if (appContent.includes("from './services/api'") || appContent.includes("from \"./services/api\"")) {
    console.log('✓ App.js импортирует api.js');
  } else {
    console.log('✗ App.js НЕ импортирует api.js');
  }
  
  if (appContent.includes('checkApiHealth')) {
    console.log('✓ Используется checkApiHealth');
  }
} else {
  console.log('✗ App.js не найден!');
}

console.log();

// 5. Рекомендации
console.log('[5/5] Рекомендации...');
console.log();
console.log('ПРОВЕРЬТЕ:');
console.log('1. Файл .env находится в miniapp/react-app/.env (не в src/)');
console.log('2. Формат: REACT_APP_API_URL=https://url.com (без пробелов)');
console.log('3. После изменения .env ПЕРЕЗАПУСТИТЕ приложение (npm start)');
console.log('4. В консоли браузера должно быть:');
console.log('   API Base URL configured: ваш-url');
console.log('   REACT_APP_API_URL env: ваш-url');
console.log();
console.log('ДЛЯ TELEGRAM WEBAPP:');
console.log('- URL должен быть HTTPS (не http://localhost)');
console.log('- Используйте ngrok, localtunnel или другой туннель');
console.log('- Проверьте, что backend доступен по этому URL');
console.log();

console.log('='.repeat(60));
console.log('ДИАГНОСТИКА ЗАВЕРШЕНА');
console.log('='.repeat(60));

