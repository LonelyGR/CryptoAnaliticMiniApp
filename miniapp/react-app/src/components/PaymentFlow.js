import { useEffect, useMemo, useState } from 'react';

const SUCCESS_STATUSES = new Set(['confirmed', 'finished']);
const FAILURE_STATUSES = new Set(['failed', 'expired', 'refunded']);
const REQUEST_TIMEOUT_MS = 25000;

function formatAmount5(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return Number(value).toFixed(5);
}

function formatTimer(secondsLeft) {
  const minutes = Math.floor(secondsLeft / 60)
    .toString()
    .padStart(2, '0');
  const seconds = Math.floor(secondsLeft % 60)
    .toString()
    .padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function getStatusView(statusRaw) {
  const status = (statusRaw || '').toLowerCase();
  if (SUCCESS_STATUSES.has(status)) return { icon: '🟢', text: 'Оплата получена', tone: 'success' };
  if (status === 'confirming') return { icon: '🔵', text: 'Подтверждение сети', tone: 'info' };
  if (FAILURE_STATUSES.has(status)) return { icon: '🔴', text: 'Время истекло / платеж отменён', tone: 'danger' };
  return { icon: '🟡', text: 'Ожидаем оплату', tone: 'warning' };
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      return true;
    } catch {
      return false;
    }
  }
}

export default function PaymentFlow({
  orderId,
  amount,
  priceCurrency = 'usd',
  backendUrl,
  fixedPayCurrency = 'usdttrc20',
  paymentId,
  onClose,
  onComplete,
  title,
  orderDescription,
  webinarTitle
}) {
  const apiBase = backendUrl || process.env.REACT_APP_API_URL || '/api';
  const [payment, setPayment] = useState(null);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);
  const [loadingExisting, setLoadingExisting] = useState(false);
  const [expiresAt, setExpiresAt] = useState(null);
  const [nowSec, setNowSec] = useState(Math.floor(Date.now() / 1000));

  const tgInitData = useMemo(() => {
    try {
      return (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initData) || '';
    } catch {
      return '';
    }
  }, []);

  const headers = useMemo(() => {
    const h = { 'Content-Type': 'application/json' };
    if (tgInitData) h['X-Telegram-Init-Data'] = tgInitData;
    return h;
  }, [tgInitData]);

  const statusView = useMemo(() => getStatusView(payment?.payment_status), [payment?.payment_status]);
  const isSuccess = SUCCESS_STATUSES.has((payment?.payment_status || '').toLowerCase());
  const isFailure = FAILURE_STATUSES.has((payment?.payment_status || '').toLowerCase());

  const payAddress = payment?.pay_address || '';
  const payAmount = payment?.pay_amount;
  const payCurrency = (payment?.pay_currency || fixedPayCurrency || '').toUpperCase();

  const secondsLeft = useMemo(() => {
    if (!expiresAt) return 15 * 60;
    const diff = expiresAt - nowSec;
    return Math.max(diff, 0);
  }, [expiresAt, nowSec]);

  const formattedTimer = useMemo(() => formatTimer(secondsLeft), [secondsLeft]);

  const walletUri = useMemo(() => {
    if (!payAddress) return '';
    const lower = (payment?.pay_currency || fixedPayCurrency || '').toLowerCase();
    if (lower.includes('trc20') || payAddress.startsWith('T')) {
      return `tron:${payAddress}${payAmount ? `?amount=${payAmount}` : ''}`;
    }
    return payAddress;
  }, [payAddress, payAmount, payment?.pay_currency, fixedPayCurrency]);

  const qrValue = useMemo(() => {
    // QR должен содержать адрес + сумму (для кошельков это чаще всего deep-link)
    return walletUri || payAddress;
  }, [walletUri, payAddress]);

  useEffect(() => {
    const t = setInterval(() => setNowSec(Math.floor(Date.now() / 1000)), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!payment) return;
    if (isSuccess || isFailure) {
      onComplete?.(payment, isSuccess);
    }
  }, [payment, isSuccess, isFailure, onComplete]);

  // 1) если есть paymentId — подгружаем существующий платёж
  useEffect(() => {
    if (!paymentId) return;
    let mounted = true;
    const load = async () => {
      setLoadingExisting(true);
      setError(null);
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
        const resp = await fetch(`${apiBase}/payments/payment/${paymentId}`, { headers, signal: controller.signal });
        clearTimeout(timeoutId);
        if (!resp.ok) throw new Error('Не удалось получить платеж');
        const data = await resp.json();
        if (!mounted) return;
        setPayment(data);
        if (data?.expiration_estimate_date) {
          const sec = Math.floor(new Date(data.expiration_estimate_date).getTime() / 1000);
          setExpiresAt(sec);
        } else {
          setExpiresAt(Math.floor(Date.now() / 1000) + 15 * 60);
        }
      } catch (e) {
        if (mounted) {
          const msg = e && e.name === 'AbortError'
            ? 'Сервер не ответил вовремя. Попробуйте ещё раз.'
            : (e instanceof Error ? e.message : 'Ошибка загрузки платежа');
          setError(msg);
        }
      } finally {
        if (mounted) setLoadingExisting(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [apiBase, headers, paymentId]);

  // 2) если paymentId нет — создаём платеж автоматически (один экран, минимум действий)
  useEffect(() => {
    if (paymentId) return;
    if (payment || creating) return;
    let mounted = true;

    const create = async () => {
      setCreating(true);
      setError(null);
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
        const resp = await fetch(`${apiBase}/payments/create`, {
          method: 'POST',
          headers,
          signal: controller.signal,
          body: JSON.stringify({
            amount,
            price_currency: priceCurrency,
            pay_currency: fixedPayCurrency,
            order_id: orderId,
            order_description: orderDescription || title || webinarTitle || `Order ${orderId}`
          })
        });
        clearTimeout(timeoutId);
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
          const detail = data?.detail || data?.message;
          throw new Error(detail || 'Не удалось создать платеж');
        }
        if (!mounted) return;
        setPayment(data);
        if (data?.expiration_estimate_date) {
          const sec = Math.floor(new Date(data.expiration_estimate_date).getTime() / 1000);
          setExpiresAt(sec);
        } else {
          setExpiresAt(Math.floor(Date.now() / 1000) + 15 * 60);
        }
      } catch (e) {
        if (mounted) {
          const msg = e && e.name === 'AbortError'
            ? 'Сервер не ответил вовремя. Попробуйте ещё раз.'
            : (e instanceof Error ? e.message : 'Ошибка создания платежа');
          setError(msg);
        }
      } finally {
        if (mounted) setCreating(false);
      }
    };

    create();
    return () => {
      mounted = false;
    };
  }, [apiBase, amount, creating, fixedPayCurrency, headers, orderDescription, orderId, payment, paymentId, priceCurrency, title, webinarTitle]);

  // 3) авто-обновление статуса
  useEffect(() => {
    if (!payment?.payment_id) return;
    if (isSuccess || isFailure) return;
    const id = payment.payment_id;
    const interval = setInterval(async () => {
      try {
        const resp = await fetch(`${apiBase}/payments/payment/${id}`, { headers });
        if (!resp.ok) return;
        const data = await resp.json();
        setPayment((prev) => ({ ...(prev || {}), ...data }));
        if (data?.expiration_estimate_date) {
          const sec = Math.floor(new Date(data.expiration_estimate_date).getTime() / 1000);
          setExpiresAt(sec);
        }
      } catch {
        // не спамим ошибками в UI — статус может временно не обновиться
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [apiBase, headers, isFailure, isSuccess, payment?.payment_id]);

  const handleCopyAddress = async () => {
    if (!payAddress) return;
    const ok = await copyToClipboard(payAddress);
    if (!ok) setError('Не удалось скопировать адрес');
  };

  const handleCopyAmount = async () => {
    if (payAmount === null || payAmount === undefined) return;
    const ok = await copyToClipboard(formatAmount5(payAmount));
    if (!ok) setError('Не удалось скопировать сумму');
  };

  const handleOpenWallet = () => {
    if (!walletUri) return;
    try {
      // Для deep-links (tron:) лучше прямой переход
      window.location.href = walletUri;
    } catch {
      // ignore
    }
  };

  const displayTitle = title || webinarTitle || '';
  const titleLine = displayTitle ? displayTitle : `Заказ ${orderId}`;
  const currency = (priceCurrency || '').toLowerCase();
  const numericAmount = typeof amount === 'number' ? amount : Number(amount || 0);
  const currencyLabel = currency ? currency.toUpperCase() : 'USD';
  const priceLine = currency === 'usd'
    ? `$${numericAmount}`
    : (currency === 'eur' ? `€${numericAmount}` : `${numericAmount} ${currencyLabel}`);

  return (
    <div className="pay-modern">
      <div className="pay-modern__header">
        <div>
          <div className="pay-modern__title">{titleLine}</div>
          <div className="pay-modern__price">{priceLine}</div>
        </div>
        {onClose && (
          <button type="button" className="pay-modern__close" onClick={onClose} aria-label="Закрыть">
            ×
          </button>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {error && !payment && (
        <button
          type="button"
          className="pay-modern__btn pay-modern__btn--primary"
          onClick={() => window.location.reload()}
          style={{ width: '100%' }}
        >
          Повторить
        </button>
      )}

      {(creating || loadingExisting) && !payment && (
        <div className="pay-modern__loading">
          <div className="loading-spinner" />
          <div>Готовим платёж…</div>
        </div>
      )}

      {payment && (
        <>
          <div className={`pay-modern__status pay-modern__status--${statusView.tone}`}>
            <span className="pay-modern__statusIcon">{statusView.icon}</span>
            <div>
              <div className="pay-modern__statusText">{statusView.text}</div>
              {!isSuccess && !isFailure && (
                <div className="pay-modern__timer">
                  Таймер оплаты: <strong>{formattedTimer}</strong>
                </div>
              )}
            </div>
          </div>

          <div className="pay-modern__method">
            Оплата <span className="pay-modern__pill">USDT</span> в сети{' '}
            <span className="pay-modern__pill pay-modern__pill--network">TRC20</span>
          </div>

          <div className="pay-modern__warning">
            Отправляйте <strong>ТОЛЬКО USDT</strong> в сети <strong>TRC20</strong>. Другие сети не принимаются.
          </div>

          <div className="pay-modern__grid">
            <div className="pay-modern__card">
              <div className="pay-modern__label">Сумма к оплате</div>
              <div className="pay-modern__valueRow">
                <div className="pay-modern__value">
                  {formatAmount5(payAmount)} <span className="pay-modern__unit">{payCurrency}</span>
                </div>
                <button type="button" className="pay-modern__btn" onClick={handleCopyAmount} disabled={payAmount == null}>
                  Скопировать
                </button>
              </div>
              <div className="pay-modern__hint">Оплатите ровно эту сумму.</div>
            </div>

            <div className="pay-modern__card">
              <div className="pay-modern__label">Адрес для оплаты</div>
              <div className="pay-modern__address">{payAddress || 'Ожидаем адрес…'}</div>
              <div className="pay-modern__actions">
                <button type="button" className="pay-modern__btn pay-modern__btn--primary" onClick={handleCopyAddress} disabled={!payAddress}>
                  Скопировать
                </button>
                <button type="button" className="pay-modern__btn" onClick={handleOpenWallet} disabled={!walletUri}>
                  Открыть кошелёк
                </button>
              </div>
            </div>
          </div>

          <div className="pay-modern__qrWrap">
            <div className="pay-modern__label">QR‑код</div>
            <div className="pay-modern__qr">
              {qrValue ? (
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(qrValue)}`}
                  alt="QR код для оплаты"
                />
              ) : (
                <div className="pay-modern__hint">QR ещё формируется…</div>
              )}
            </div>
          </div>

          <div className="pay-modern__faq">
            <details>
              <summary>Как скопировать адрес?</summary>
              <div>Нажмите кнопку «Скопировать» рядом с адресом и вставьте его в кошелёк/биржу.</div>
            </details>
            <details>
              <summary>Что если не уверены в сети?</summary>
              <div>Платёж принимается только в сети <strong>TRC20</strong>. Если выберете другую сеть — средства могут быть потеряны.</div>
            </details>
            <details>
              <summary>Поддержка</summary>
              <div>Если возникли вопросы — напишите в поддержку (контакт добавьте в UI/боте).</div>
            </details>
          </div>
        </>
      )}
    </div>
  );
}
