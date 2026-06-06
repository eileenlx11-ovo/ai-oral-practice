/**
 * Classify UI errors into stable user-facing messages.
 * @param {Error|string} error
 * @param {number|undefined} statusCode
 * @returns {{type: string, title: string, message: string, action: 'retry'|'refresh'|'wait'}}
 */
export function classifyError(error, statusCode) {
  const msg = typeof error === 'string' ? error : error?.message || ''
  const offline = typeof navigator !== 'undefined' && !navigator.onLine

  if (offline || msg.includes('network') || msg.includes('Failed to fetch')) {
    return { type: 'network', title: '网络连接失败', message: '请检查网络连接后重试', action: 'retry' }
  }
  if (msg.includes('timeout') || msg.includes('Timeout')) {
    return { type: 'timeout', title: '响应超时', message: '服务器繁忙，请稍后重试', action: 'retry' }
  }
  if (statusCode === 429) {
    return { type: 'quota', title: '请求过于频繁', message: '请等待几秒后再试', action: 'wait' }
  }
  if (statusCode === 503) {
    return { type: 'server', title: '评测服务未就绪', message: '服务正在启动，请稍后刷新', action: 'refresh' }
  }
  if (statusCode && statusCode >= 500) {
    return { type: 'server', title: '服务暂时不可用', message: '请刷新页面后重试', action: 'refresh' }
  }
  return { type: 'unknown', title: '发生错误', message: msg || '未知错误，请重试', action: 'retry' }
}
