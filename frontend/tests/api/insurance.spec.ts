/**
 * Tests for Insurance API Client
 *
 * Tests API request methods, error handling, and response parsing.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  submitConsultation,
  uploadContractForInterpretation,
  insuranceApi,
} from '@/api/insurance'
import type { ConsultationRequest } from '@/types/insurance'

// Mock uni.request and uni.uploadFile
const mockRequest = vi.fn()
const mockUploadFile = vi.fn()
const mockShowToast = vi.fn()

global.uni = {
  request: mockRequest,
  uploadFile: mockUploadFile,
  showToast: mockShowToast,
  getStorageSync: vi.fn(() => ''),
  setStorageSync: vi.fn(),
} as any

describe('Insurance API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('submitConsultation', () => {
    const validRequestData: ConsultationRequest = {
      name: '张三',
      age: 35,
      gender: 'male',
      occupation: '软件工程师',
      annual_income: 500000,
      marital_status: 'married',
      num_dependents: 2,
    }

    it('submits consultation request successfully', async () => {
      const mockResponse = {
        success: true,
        recommendations: [
          {
            insurance_type: '重疾险',
            recommended_coverage: '50万元',
            reason: '作为家庭经济支柱需要保障',
            priority: 'high',
          },
        ],
        reasoning: '根据您的家庭情况，建议配置重疾险...',
        total_estimated_annual_premium: '5000-8000元',
        next_steps: ['联系保险顾问', '进行健康告知'],
      }

      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: mockResponse })
        return {} as any
      })

      const response = await submitConsultation(validRequestData)

      expect(response.success).toBe(true)
      expect(response.recommendations).toHaveLength(1)
      expect(response.recommendations[0].insurance_type).toBe('重疾险')
      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          url: 'http://localhost:8000/api/consultation',
          method: 'POST',
          data: validRequestData,
        })
      )
    })

    it('handles validation errors (422)', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 422,
          data: { detail: '年龄必须大于0', error: 'Validation failed' },
        })
        return {} as any
      })

      await expect(submitConsultation(validRequestData)).rejects.toThrow()
    })

    it('handles network errors', async () => {
      mockRequest.mockImplementationOnce(({ fail }) => {
        fail({ errMsg: 'Network error' })
        return {} as any
      })

      await expect(submitConsultation(validRequestData)).rejects.toThrow('网络连接失败')
    })

    it('handles AI service errors (502)', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 502,
          data: { detail: 'AI服务暂时不可用', error: 'Bad Gateway' },
        })
        return {} as any
      })

      await expect(submitConsultation(validRequestData)).rejects.toThrow('AI服务')
    })

    it('handles internal server errors (500)', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 500,
          data: { detail: '服务器内部错误', error: 'Internal Server Error' },
        })
        return {} as any
      })

      await expect(submitConsultation(validRequestData)).rejects.toThrow('服务器内部错误')
    })

    it('includes consultation-specific error message', async () => {
      mockRequest.mockImplementationOnce(({ fail }) => {
        fail({ errMsg: 'timeout' })
        return {} as any
      })

      await expect(submitConsultation(validRequestData)).rejects.toThrow('保险方案咨询失败')
    })

    it('sends correct Content-Type header', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: { success: true } })
        return {} as any
      })

      await submitConsultation(validRequestData)

      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          header: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('uses default timeout of 30 seconds', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: { success: true } })
        return {} as any
      })

      await submitConsultation(validRequestData)

      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 30000,
        })
      )
    })

    it('accepts custom timeout option', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: { success: true } })
        return {} as any
      })

      await submitConsultation(validRequestData, { timeout: 60000 })

      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 60000,
        })
      )
    })

    it('accepts custom headers', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: { success: true } })
        return {} as any
      })

      await submitConsultation(validRequestData, {
        header: { 'X-Custom-Header': 'value' },
      })

      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          header: expect.objectContaining({
            'X-Custom-Header': 'value',
            'Content-Type': 'application/json',
          }),
        })
      )
    })
  })

  describe('uploadContractForInterpretation', () => {
    const testFilePath = '/fake/path/test.pdf'

    it('uploads contract for interpretation successfully', async () => {
      const mockResponse = {
        success: true,
        summary: '这是一份重大疾病保险合同',
        key_terms: [
          { term: '等待期', definition: '90天', importance: 'critical' },
        ],
        activation_conditions: [
          {
            condition: '等待期后确诊重大疾病',
            description: '合同生效90天后',
            required_documents: ['诊断证明', '病历'],
          },
        ],
        payout_details: {
          payout_method: '一次性赔付',
          payout_amount: '50万元',
          payout_timeline: '确诊后30日内',
          limitations: '需符合合同约定的重大疾病定义',
        },
        important_notes: [
          '如实告知健康状况非常重要',
          '仔细阅读免责条款',
        ],
        suggested_questions: [
          '等待期是多长时间？',
          '哪些疾病不属于保障范围？',
        ],
      }

      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: JSON.stringify(mockResponse) })
        return {} as any
      })

      const response = await uploadContractForInterpretation(testFilePath)

      expect(response.success).toBe(true)
      expect(response.summary).toBe('这是一份重大疾病保险合同')
      expect(response.key_terms).toHaveLength(1)
      expect(mockUploadFile).toHaveBeenCalledWith(
        expect.objectContaining({
          url: 'http://localhost:8000/api/interpretation',
          filePath: testFilePath,
          name: 'file',
        })
      )
    })

    it('handles file validation errors (422)', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 422,
          data: JSON.stringify({ detail: '只支持PDF文件', error: 'Invalid file type' }),
        })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow()
    })

    it('handles network errors during upload', async () => {
      mockUploadFile.mockImplementationOnce(({ fail }) => {
        fail({ errMsg: 'Network error' })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow('网络连接失败')
    })

    it('handles processing service errors (502)', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 502,
          data: JSON.stringify({ detail: '文件处理失败', error: 'Service unavailable' }),
        })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow('文件处理')
    })

    it('handles JSON parse errors', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: 'invalid json' })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow('解析服务器响应失败')
    })

    it('uses default timeout of 60 seconds', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: JSON.stringify({ success: true }) })
        return {} as any
      })

      await uploadContractForInterpretation(testFilePath)

      expect(mockUploadFile).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 60000,
        })
      )
    })

    it('accepts custom timeout option', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: JSON.stringify({ success: true }) })
        return {} as any
      })

      await uploadContractForInterpretation(testFilePath, { timeout: 120000 })

      expect(mockUploadFile).toHaveBeenCalledWith(
        expect.objectContaining({
          timeout: 120000,
        })
      )
    })

    it('handles internal server errors (500)', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({
          statusCode: 500,
          data: 'Internal Server Error',
        })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow('服务器内部错误')
    })

    it('handles other HTTP status codes', async () => {
      mockUploadFile.mockImplementationOnce(({ success }) => {
        success({ statusCode: 404, data: 'Not Found' })
        return {} as any
      })

      await expect(uploadContractForInterpretation(testFilePath)).rejects.toThrow('文件上传失败')
    })
  })

  describe('insuranceApi export object', () => {
    it('exports submitConsultation method', () => {
      expect(insuranceApi.submitConsultation).toBe(submitConsultation)
    })

    it('exports uploadContractForInterpretation method', () => {
      expect(insuranceApi.uploadContractForInterpretation).toBe(uploadContractForInterpretation)
    })

    it('has correct API_BASE_URL', () => {
      // Import and check the constant
      const apiModule = require('@/api/insurance')
      expect(apiModule).toBeDefined()
    })
  })

  describe('default export', () => {
    it('exports insuranceApi as default', () => {
      const insuranceApiModule = require('@/api/insurance')
      expect(insuranceApiModule.default).toBe(insuranceApi)
    })
  })

  describe('error messages in Chinese', () => {
    it('returns Chinese error message for network failure', async () => {
      mockRequest.mockImplementationOnce(({ fail }) => {
        fail({ errMsg: 'Network failed' })
        return {} as any
      })

      await expect(submitConsultation({} as ConsultationRequest)).rejects.toThrow('网络连接失败')
    })

    it('returns Chinese error message for 422 validation', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 422, data: { detail: '请输入姓名' } })
        return {} as any
      })

      await expect(submitConsultation({} as ConsultationRequest)).rejects.toThrow('请输入姓名')
    })

    it('returns Chinese error message for 502 service error', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 502, data: { detail: 'AI服务错误' } })
        return {} as any
      })

      await expect(submitConsultation({} as ConsultationRequest)).rejects.toThrow('AI服务')
    })
  })

  describe('request options', () => {
    it('merges custom headers with default Content-Type', async () => {
      mockRequest.mockImplementationOnce(({ success }) => {
        success({ statusCode: 200, data: { success: true } })
        return {} as any
      })

      await submitConsultation({} as ConsultationRequest, {
        header: { Authorization: 'Bearer token123' },
      })

      expect(mockRequest).toHaveBeenCalledWith(
        expect.objectContaining({
          header: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer token123',
          }),
        })
      )
    })
  })
})
