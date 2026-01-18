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
    const requestBody = {
      username: userData.username || null,
      first_name: userData.first_name || null,
      last_name: userData.last_name || null,
      photo_url: userData.photo_url || null,
    };
    
    console.log(`Creating/updating user with telegram_id: ${telegramId}`, requestBody);
    
    const response = await fetch(`${API_BASE_URL}/users/telegram/${telegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('User created/updated successfully:', result);
    return result;
  } catch (error) {
    console.error('Failed to create/update user:', error);
    console.error('Error details:', error.message, error.stack);
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
 * Получить реферальную информацию пользователя
 */
export async function getReferralInfo(telegramId) {
  try {
    return await apiRequest(`/referrals/${telegramId}`);
  } catch (error) {
    console.error('Failed to get referral info:', error);
    return null;
  }
}

/**
 * Создать запись на вебинар или консультацию
 */
export async function createBooking(bookingData) {
  try {
    console.log('Creating booking:', bookingData);
    
    const response = await fetch(`${API_BASE_URL}/bookings/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bookingData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('Booking created successfully:', result);
    return result;
  } catch (error) {
    console.error('Failed to create booking:', error);
    console.error('Error details:', error.message, error.stack);
    throw error;
  }
}

/**
 * Получить все консультации (только для админов)
 */
export async function getConsultations(adminTelegramId) {
  try {
    return await apiRequest(`/bookings/consultations?admin_telegram_id=${adminTelegramId}`);
  } catch (error) {
    console.error('Failed to get consultations:', error);
    return [];
  }
}

/**
 * Получить все обращения в поддержку (только для админов)
 */
export async function getSupportTickets(adminTelegramId) {
  try {
    return await apiRequest(`/bookings/support-tickets?admin_telegram_id=${adminTelegramId}`);
  } catch (error) {
    console.error('Failed to get support tickets:', error);
    return [];
  }
}

/**
 * Удалить тикет (только для админов)
 */
export async function deleteTicket(ticketId, adminTelegramId) {
  try {
    const response = await fetch(`${API_BASE_URL}/bookings/${ticketId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to delete ticket:', error);
    throw error;
  }
}

/**
 * Ответить на консультацию (только для админов)
 */
export async function respondToConsultation(bookingId, adminTelegramId, response) {
  try {
    const response_data = await fetch(`${API_BASE_URL}/bookings/${bookingId}/respond?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        admin_response: response,
        admin_id: 0, // Игнорируется на бэкенде, используется admin_telegram_id
      }),
    });

    if (!response_data.ok) {
      const errorText = await response_data.text();
      console.error(`HTTP error! status: ${response_data.status}, body: ${errorText}`);
      throw new Error(`HTTP error! status: ${response_data.status}`);
    }

    return await response_data.json();
  } catch (error) {
    console.error('Failed to respond to consultation:', error);
    throw error;
  }
}

/**
 * Создать вебинар (только для админов)
 */
export async function createWebinar(adminTelegramId, webinarData) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinars/?admin_telegram_id=${adminTelegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(webinarData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create webinar:', error);
    throw error;
  }
}

/**
 * Обновить вебинар (только для админов)
 */
export async function updateWebinar(webinarId, adminTelegramId, webinarData) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinars/${webinarId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(webinarData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update webinar:', error);
    throw error;
  }
}

/**
 * Удалить вебинар (только для админов)
 */
export async function deleteWebinar(webinarId, adminTelegramId) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinars/${webinarId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to delete webinar:', error);
    throw error;
  }
}

/**
 * Получить список всех админов
 */
export async function getAdmins() {
  try {
    return await apiRequest('/admins/');
  } catch (error) {
    console.error('Failed to get admins:', error);
    return [];
  }
}

/**
 * Получить список всех пользователей
 */
export async function getUsers() {
  try {
    return await apiRequest('/users/');
  } catch (error) {
    console.error('Failed to get users:', error);
    return [];
  }
}

/**
 * Заблокировать/разблокировать пользователя (только для разработчика)
 */
export async function updateUserBlocked(userId, adminTelegramId, isBlocked) {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}/block?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_blocked: isBlocked }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update user block status:', error);
    throw error;
  }
}

/**
 * Создать админа (только для разработчика)
 */
export async function createAdmin(adminData) {
  try {
    const response = await fetch(`${API_BASE_URL}/admins/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(adminData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create admin:', error);
    throw error;
  }
}

/**
 * Обновить админа (изменить роль)
 */
export async function updateAdmin(adminId, adminData) {
  try {
    const response = await fetch(`${API_BASE_URL}/admins/${adminId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        role: adminData.role
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update admin:', error);
    throw error;
  }
}

/**
 * Удалить админа
 */
export async function deleteAdmin(adminId) {
  try {
    const response = await fetch(`${API_BASE_URL}/admins/${adminId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to delete admin:', error);
    throw error;
  }
}

/**
 * Полная очистка базы данных (только для разработчика)
 */
export async function clearDatabase(adminTelegramId) {
  try {
    const response = await fetch(`${API_BASE_URL}/admins/clear-db?admin_telegram_id=${adminTelegramId}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to clear database:', error);
    throw error;
  }
}

/**
 * Получить все посты
 */
export async function getPosts() {
  try {
    return await apiRequest('/posts/');
  } catch (error) {
    console.error('Failed to get posts:', error);
    return [];
  }
}

/**
 * Создать пост (только для админов и разработчиков)
 */
export async function createPost(adminTelegramId, postData) {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/?admin_telegram_id=${adminTelegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create post:', error);
    throw error;
  }
}

/**
 * Обновить пост (только для админов и разработчиков)
 */
export async function updatePost(postId, adminTelegramId, postData) {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update post:', error);
    throw error;
  }
}

/**
 * Удалить пост (только для админов и разработчиков)
 */
export async function deletePost(postId, adminTelegramId) {
  try {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to delete post:', error);
    throw error;
  }
}

/**
 * Создать платеж
 */
export async function createPayment(paymentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/payments/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create payment:', error);
    throw error;
  }
}

/**
 * Получить платежи по booking_id
 */
export async function getPaymentsByBooking(bookingId) {
  try {
    return await apiRequest(`/payments/booking/${bookingId}`);
  } catch (error) {
    console.error('Failed to get payments:', error);
    return [];
  }
}

/**
 * Получить платежи пользователя
 */
export async function getUserPayments(userId) {
  try {
    return await apiRequest(`/payments/user/${userId}`);
  } catch (error) {
    console.error('Failed to get user payments:', error);
    return [];
  }
}

/**
 * Обновить статус платежа (только для админов)
 */
export async function updatePayment(paymentId, adminTelegramId, paymentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/payments/${paymentId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(paymentData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update payment:', error);
    throw error;
  }
}

/**
 * Получить материалы вебинара
 */
export async function getWebinarMaterials(webinarId) {
  try {
    return await apiRequest(`/webinar-materials/webinar/${webinarId}`);
  } catch (error) {
    console.error('Failed to get webinar materials:', error);
    return [];
  }
}

/**
 * Создать материал вебинара (только для админов)
 */
export async function createWebinarMaterial(adminTelegramId, materialData) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinar-materials/?admin_telegram_id=${adminTelegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(materialData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to create webinar material:', error);
    throw error;
  }
}

/**
 * Обновить материал вебинара (только для админов)
 */
export async function updateWebinarMaterial(materialId, adminTelegramId, materialData) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinar-materials/${materialId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(materialData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to update webinar material:', error);
    throw error;
  }
}

/**
 * Удалить материал вебинара (только для админов)
 */
export async function deleteWebinarMaterial(materialId, adminTelegramId) {
  try {
    const response = await fetch(`${API_BASE_URL}/webinar-materials/${materialId}?admin_telegram_id=${adminTelegramId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to delete webinar material:', error);
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

