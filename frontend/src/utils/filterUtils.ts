/**
 * Filter utilities for API requests
 * 統一處理 API 請求的濾波器參數
 */

/**
 * 移除空值、空字串、undefined 的參數
 * @param filters - 原始濾波器物件
 * @returns 清理後的濾波器物件
 */
export function cleanFilters<T extends object>(filters?: T): Partial<T> {
  if (!filters) return {}

  const cleaned: Partial<T> = {}

  for (const [key, value] of Object.entries(filters)) {
    // 保留數字 0 和 false
    if (value === 0 || value === false) {
      (cleaned as Record<string, unknown>)[key] = value
      continue
    }

    // 跳過 null, undefined, 空字串
    if (value === null || value === undefined) continue
    if (typeof value === 'string' && !value.trim()) continue

    // 保留其他有效值
    (cleaned as Record<string, unknown>)[key] = value
  }

  return cleaned
}

/**
 * 建立分頁參數
 * @param page - 頁碼 (1-based)
 * @param pageSize - 每頁筆數
 * @returns skip 和 limit 參數
 */
export function paginationParams(page: number, pageSize: number): { skip: number; limit: number } {
  return {
    skip: (page - 1) * pageSize,
    limit: pageSize,
  }
}

/**
 * 合併濾波器與分頁參數
 * @param filters - 濾波器物件
 * @param page - 頁碼 (1-based)
 * @param pageSize - 每頁筆數
 * @returns 合併後的參數
 */
export function withPagination<T extends object>(
  filters: T | undefined,
  page: number,
  pageSize: number
): Partial<T> & { skip: number; limit: number } {
  return {
    ...cleanFilters(filters),
    ...paginationParams(page, pageSize),
  }
}
