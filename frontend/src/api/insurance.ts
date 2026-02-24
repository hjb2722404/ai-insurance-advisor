/**
 * Insurance API Client
 *
 * Provides uni.request wrapper methods for communicating with the backend API.
 * All methods use uni-app APIs for cross-platform compatibility (H5, WeChat Mini Program).
 *
 * @module api/insurance
 */

import type {
  ConsultationRequest,
  ConsultationResponse,
  InterpretationResponse,
  ApiErrorResponse,
} from '@/types/insurance'

/**
 * Base URL for the backend API.
 * In production, this should be configured via environment variables.
 */
const API_BASE_URL = 'http://localhost:8000'

/**
 * Default timeout for API requests in milliseconds (30 seconds).
 */
const DEFAULT_TIMEOUT = 30000

/**
 * API request options interface.
 */
interface RequestOptions {
  /** Request timeout in milliseconds */
  timeout?: number
  /** Custom headers */
  header?: Record<string, string>
}

/**
 * Wraps uni.request in a Promise for easier async/await usage.
 *
 * @param url - The API endpoint URL
 * @param method - HTTP method
 * @param data - Request body data
 * @param options - Additional request options
 * @returns Promise resolving to the response data
 * @throws Error with status code and message if request fails
 */
async function request<T>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  data?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const { timeout = DEFAULT_TIMEOUT, header = {} } = options

  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
      timeout,
      success: (res: UniApp.RequestSuccessCallbackResult) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 422) {
          // Validation error
          const errorData = res.data as ApiErrorResponse
          reject(new Error(errorData.details || errorData.error || '请求参数验证失败'))
        } else if (res.statusCode === 502) {
          // Bad gateway - AI service error
          const errorData = res.data as ApiErrorResponse
          reject(new Error(errorData.details || errorData.error || 'AI服务暂时不可用，请稍后重试'))
        } else if (res.statusCode === 500) {
          // Internal server error
          const errorData = res.data as ApiErrorResponse
          reject(new Error(errorData.details || errorData.error || '服务器内部错误，请稍后重试'))
        } else {
          const errorData = res.data as ApiErrorResponse
          reject(new Error(errorData.error || `请求失败 (状态码: ${res.statusCode})`))
        }
      },
      fail: (err: UniApp.GeneralCallbackResult) => {
        // Network error or request timeout
        reject(new Error('网络连接失败，请检查网络设置后重试'))
      },
    })
  })
}

/**
 * Submits a consultation request to get personalized insurance recommendations.
 *
 * @param requestData - User's personal and family information
 * @param options - Additional request options
 * @returns Promise resolving to consultation response with recommendations
 *
 * @example
 * ```typescript
 * const response = await submitConsultation({
 *   name: '张三',
 *   age: 35,
 *   gender: 'male',
 *   occupation: '软件工程师',
 *   annual_income: 500000,
 *   marital_status: 'married',
 *   num_dependents: 2
 * })
 * console.log(response.recommendations)
 * ```
 */
export async function submitConsultation(
  requestData: ConsultationRequest,
  options: RequestOptions = {}
): Promise<ConsultationResponse> {
  try {
    const response = await request<ConsultationResponse>(
      '/api/consultation',
      'POST',
      requestData,
      options
    )
    return response
  } catch (error) {
    // Re-throw with more context
    if (error instanceof Error) {
      throw new Error(`保险方案咨询失败：${error.message}`)
    }
    throw new Error('保险方案咨询失败，请稍后重试')
  }
}

/**
 * Uploads an insurance contract PDF for AI-powered interpretation.
 *
 * @param filePath - Local path to the PDF file (from uni.chooseMessageFile)
 * @param options - Additional request options
 * @returns Promise resolving to interpretation response with contract analysis
 *
 * @example
 * ```typescript
 * // First, let user select a file
 * const { tempFilePath } = await uni.chooseMessageFile({
 *   count: 1,
 *   extension: ['pdf']
 * })
 *
 * // Then upload and analyze
 * const result = await uploadContractForInterpretation(tempFilePath)
 * console.log(result.summary, result.key_terms)
 * ```
 */
export async function uploadContractForInterpretation(
  filePath: string,
  options: RequestOptions = {}
): Promise<InterpretationResponse> {
  return new Promise<InterpretationResponse>((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}/api/interpretation`,
      filePath,
      name: 'file',
      header: {
        ...options.header,
      },
      timeout: options.timeout || 60000, // 60 seconds for PDF upload and processing
      success: (res: UniApp.UploadFileSuccessCallbackResult) => {
        if (res.statusCode === 200) {
          try {
            const data = JSON.parse(res.data) as InterpretationResponse
            resolve(data)
          } catch {
            reject(new Error('解析服务器响应失败'))
          }
        } else if (res.statusCode === 422) {
          // Validation error (file type, size, etc.)
          try {
            const errorData = JSON.parse(res.data) as ApiErrorResponse
            reject(new Error(errorData.details || errorData.error || '文件验证失败'))
          } catch {
            reject(new Error('文件验证失败，请确保上传的是有效的PDF文件'))
          }
        } else if (res.statusCode === 502) {
          // Bad gateway - AI or PDF service error
          try {
            const errorData = JSON.parse(res.data) as ApiErrorResponse
            reject(new Error(errorData.details || errorData.error || '文件处理服务暂时不可用'))
          } catch {
            reject(new Error('文件处理失败，请稍后重试'))
          }
        } else if (res.statusCode === 500) {
          // Internal server error
          reject(new Error('服务器内部错误，请稍后重试'))
        } else {
          reject(new Error(`文件上传失败 (状态码: ${res.statusCode})`))
        }
      },
      fail: (err: UniApp.GeneralCallbackResult) => {
        // Network error or request timeout
        reject(new Error('网络连接失败，请检查网络设置后重试'))
      },
    })
  })
}

/**
 * API client object for convenient imports.
 */
export const insuranceApi = {
  submitConsultation,
  uploadContractForInterpretation,
}

/**
 * Default export for compatibility.
 */
export default insuranceApi
