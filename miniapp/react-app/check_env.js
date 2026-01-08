/**
 * Скрипт для проверки переменных окружения
 * Запустите: node check_env.js
 */
console.log('Проверка переменных окружения...\n');

// В Node.js можно проверить переменные окружения
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL || 'НЕ НАЙДЕНО');
console.log('NODE_ENV:', process.env.NODE_ENV || 'НЕ НАЙДЕНО');

console.log('\nПроверка файла .env:');
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  console.log('✓ Файл .env существует');
  const content = fs.readFileSync(envPath, 'utf8');
  console.log('\nСодержимое .env:');
  console.log(content);
  
  // Проверка формата
  if (content.includes('REACT_APP_API_URL')) {
    console.log('\n✓ Переменная REACT_APP_API_URL найдена в .env');
    const match = content.match(/REACT_APP_API_URL\s*=\s*(.+)/);
    if (match) {
      const url = match[1].trim();
      console.log('✓ URL:', url);
      if (url.startsWith('http://') || url.startsWith('https://')) {
        console.log('✓ URL имеет правильный формат');
      } else {
        console.log('⚠ URL должен начинаться с http:// или https://');
      }
    }
  } else {
    console.log('\n✗ Переменная REACT_APP_API_URL НЕ найдена в .env');
  }
} else {
  console.log('✗ Файл .env НЕ существует');
  console.log('\nСоздайте файл .env в папке miniapp/react-app/');
  console.log('С содержимым:');
  console.log('REACT_APP_API_URL=http://localhost:8000');
}

console.log('\n' + '='.repeat(50));
console.log('ВАЖНО:');
console.log('1. Файл должен называться именно .env (с точкой)');
console.log('2. Переменные должны начинаться с REACT_APP_');
console.log('3. НЕ должно быть пробелов вокруг знака =');
console.log('4. После изменения .env нужно ПЕРЕЗАПУСТИТЬ приложение!');
console.log('='.repeat(50));

