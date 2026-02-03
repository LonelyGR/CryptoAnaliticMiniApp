import React, { useEffect, useMemo, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';

// iOS Telegram WebView: PDF.js can throw if workerSrc is not set,
// even when we request `disableWorker: true`.
// Point to the exact package version on a reliable CDN.
if (!pdfjsLib.GlobalWorkerOptions.workerSrc) {
    pdfjsLib.GlobalWorkerOptions.workerSrc =
        'https://unpkg.com/pdfjs-dist@5.4.624/build/pdf.worker.min.mjs';
}

export default function Prezentation() {
    const pdfPath = '/preza.pdf';
    const containerRef = useRef(null);
    const [numPages, setNumPages] = useState(0);
    const [status, setStatus] = useState('loading'); // loading | ready | error
    const [errorText, setErrorText] = useState('');
    const [scale, setScale] = useState(1);
    const [renderTick, setRenderTick] = useState(0);

    const pdfUrl = useMemo(() => {
        try {
            return new URL(pdfPath, window.location.href).toString();
        } catch {
            return pdfPath;
        }
    }, []);

    const openPdfExternally = () => {
        if (window.Telegram?.WebApp?.openLink) {
            window.Telegram.WebApp.openLink(pdfUrl);
            return;
        }
        window.open(pdfUrl, '_blank', 'noopener,noreferrer');
    };

    // Re-render on resize to keep fit-to-width
    useEffect(() => {
        const onResize = () => setRenderTick((t) => t + 1);
        window.addEventListener('resize', onResize);
        return () => window.removeEventListener('resize', onResize);
    }, []);

    useEffect(() => {
        let cancelled = false;

        const run = async () => {
            setStatus('loading');
            setErrorText('');

            try {
                const container = containerRef.current;
                if (!container) return;

                // Clear previous renders
                container.innerHTML = '';

                const resp = await fetch(pdfPath, { cache: 'no-cache' });
                if (!resp.ok) {
                    throw new Error(`Не удалось загрузить PDF (${resp.status})`);
                }

                const data = await resp.arrayBuffer();
                // Telegram WebView / CRA: worker setup can be finicky.
                // Disable worker for maximum compatibility (slower but stable).
                const loadingTask = pdfjsLib.getDocument({ data, disableWorker: true });
                const pdf = await loadingTask.promise;
                if (cancelled) return;

                setNumPages(pdf.numPages);

                const containerWidth = container.clientWidth || window.innerWidth || 360;

                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
                    if (cancelled) return;

                    const page = await pdf.getPage(pageNum);

                    // Fit-to-width calculation (use unscaled viewport width)
                    const baseViewport = page.getViewport({ scale: 1 });
                    const fitScale = (containerWidth / baseViewport.width) * scale;
                    const viewport = page.getViewport({ scale: fitScale });

                    const pageWrap = document.createElement('div');
                    pageWrap.style.margin = '10px 0';
                    pageWrap.style.borderRadius = '14px';
                    pageWrap.style.overflow = 'hidden';
                    pageWrap.style.border = '1px solid rgba(255,255,255,0.12)';
                    pageWrap.style.background = 'rgba(255,255,255,0.04)';

                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d', { alpha: false });
                    if (!ctx) throw new Error('Canvas не поддерживается');

                    // Better quality on high DPI
                    const dpr = window.devicePixelRatio || 1;
                    canvas.width = Math.floor(viewport.width * dpr);
                    canvas.height = Math.floor(viewport.height * dpr);
                    canvas.style.width = `${Math.floor(viewport.width)}px`;
                    canvas.style.height = `${Math.floor(viewport.height)}px`;

                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

                    pageWrap.appendChild(canvas);
                    container.appendChild(pageWrap);

                    await page.render({
                        canvasContext: ctx,
                        viewport,
                        intent: 'display',
                    }).promise;
                }

                if (!cancelled) setStatus('ready');
            } catch (e) {
                if (cancelled) return;
                setStatus('error');
                setErrorText(e?.message || 'Ошибка загрузки презентации');
            }
        };

        run();

        return () => {
            cancelled = true;
        };
    }, [pdfPath, renderTick, scale]);

    return (
        <div style={{ height: '100vh', width: '100vw', margin: 0, paddingBottom: 96, boxSizing: 'border-box' }}>
            <div style={{ padding: 12, display: 'flex', gap: 10, alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ fontSize: 13, opacity: 0.85 }}>
                    Презентация {numPages ? `(${numPages} стр.)` : ''}
                </div>

                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <button
                        onClick={() => setScale((s) => Math.max(0.75, Math.round((s - 0.1) * 10) / 10))}
                        style={{
                            border: '1px solid rgba(255,255,255,0.18)',
                            background: 'rgba(255,255,255,0.08)',
                            color: '#fff',
                            borderRadius: 12,
                            padding: '10px 12px',
                            fontWeight: 800,
                            cursor: 'pointer'
                        }}
                        aria-label="Zoom out"
                    >
                        −
                    </button>
                    <div style={{ fontSize: 12, opacity: 0.8, minWidth: 46, textAlign: 'center' }}>
                        {Math.round(scale * 100)}%
                    </div>
                    <button
                        onClick={() => setScale((s) => Math.min(2, Math.round((s + 0.1) * 10) / 10))}
                        style={{
                            border: '1px solid rgba(255,255,255,0.18)',
                            background: 'rgba(255,255,255,0.08)',
                            color: '#fff',
                            borderRadius: 12,
                            padding: '10px 12px',
                            fontWeight: 800,
                            cursor: 'pointer'
                        }}
                        aria-label="Zoom in"
                    >
                        +
                    </button>

                    <button
                        onClick={openPdfExternally}
                        style={{
                            border: '1px solid rgba(255,255,255,0.18)',
                            background: 'rgba(255,255,255,0.08)',
                            color: '#fff',
                            borderRadius: 12,
                            padding: '10px 14px',
                            fontWeight: 700,
                            cursor: 'pointer'
                        }}
                    >
                        Открыть в браузере
                    </button>
                </div>
            </div>

            {status === 'loading' && (
                <div style={{ padding: 16, opacity: 0.8, fontSize: 13 }}>
                    Загружаю презентацию…
                </div>
            )}

            {status === 'error' && (
                <div style={{ padding: 16 }}>
                    <div style={{ fontSize: 14, fontWeight: 800, marginBottom: 6 }}>
                        Не получилось открыть презентацию
                    </div>
                    <div style={{ fontSize: 13, opacity: 0.8, marginBottom: 12 }}>
                        {errorText}
                    </div>
                    <button
                        onClick={openPdfExternally}
                        style={{
                            border: '1px solid rgba(255,255,255,0.18)',
                            background: 'rgba(255,255,255,0.08)',
                            color: '#fff',
                            borderRadius: 12,
                            padding: '10px 14px',
                            fontWeight: 700,
                            cursor: 'pointer'
                        }}
                    >
                        Открыть PDF в браузере
                    </button>
                </div>
            )}

            <div
                ref={containerRef}
                style={{
                    padding: '0 12px 16px',
                    overflowY: 'auto',
                    height: 'calc(100% - 56px)',
                    WebkitOverflowScrolling: 'touch',
                }}
            />
        </div>
    );
}