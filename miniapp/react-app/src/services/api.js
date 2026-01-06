// API конфигурация
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Логируем используемый URL для отладки
console.log('API Base URL configured:', API_BASE_URL);
console.log('REACT_APP_API_URL env:', process.env.REACT_APP_API_URL);

/**
 * Универсальная функция для выполнения API запросов с обработкой ошибок
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Получить пользователя по Telegram ID
 */
export async function getUserByTelegramId(telegramId) {
  try {
    return await apiRequest(`/users/telegram/${telegramId}`);
  } catch (error) {
    console.error('Failed to get user:', error);
    return null;
  }
}

/**
 * Создать или обновить пользователя
 */
export async function createOrUpdateUser(telegramId, userData) {
  try {
    const response = await fetch(`${API_BASE_URL}/users/telegram/${telegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: userData.username,
        first_name: userData.first_name,
        last_name: userData.last_name,
        photo_url: userData.photo_url,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create/update user:', error);
    return null;
  }
}

/**
 * Получить все вебинары
 */
export async function getWebinars() {
  try {
    return await apiRequest('/webinars/');
  } catch (error) {
    console.error('Failed to get webinars:', error);
    return [];
  }
}

/**
 * Получить записи пользователя по Telegram ID
 */
export async function getUserBookings(telegramId) {
  try {
    return await apiRequest(`/bookings/telegram/${telegramId}`);
  } catch (error) {
    console.error('Failed to get user bookings:', error);
    return [];
  }
}

/**
 * Создать запись на вебинар или консультацию
 */
export async function createBooking(bookingData) {
  try {
    const response = await fetch(`${API_BASE_URL}/bookings/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookingData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create booking:', error);
    throw error;
  }
}

/**
 * Проверка доступности API
 */
export async function checkApiHealth() {
  try {
    console.log('Checking API health at:', API_BASE_URL);
    
    // Создаем AbortController для timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 секунд timeout
    
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    const isOk = response.ok;
    console.log('API health check result:', isOk, response.status);
    if (isOk) {
      const data = await response.json();
      console.log('API response:', data);
    }
    return isOk;
  } catch (error) {
    console.error('API health check failed:', error.message);
    console.error('API_BASE_URL:', API_BASE_URL);
    console.error('Error type:', error.name);
    if (error.name === 'AbortError') {
      console.error('Request timeout - сервер не отвечает в течение 5 секунд');
      console.error('Проверьте, что сервер запущен на:', API_BASE_URL);
    } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      console.error('Network error - возможно сервер не запущен или недоступен по адресу:', API_BASE_URL);
      console.error('Попробуйте:');
      console.error('1. Проверить, что backend запущен: cd backend && python run.py');
      console.error('2. Открыть http://localhost:8000 в браузере');
      console.error('3. Проверить файрвол/антивирус');
    } else {
      console.error('Другая ошибка:', error);
    }
    return false;
  }
}

