/**
 * Tests for Consultation Form Component
 *
 * Tests component rendering, form validation, and user interactions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ConsultationForm from '@/pages/consultation/consultation.vue'

// Mock uni-app APIs
global.uni = {
  request: vi.fn(),
  uploadFile: vi.fn(),
  showToast: vi.fn(),
  showModal: vi.fn(),
  navigateTo: vi.fn(),
  setNavigationBarTitle: vi.fn(),
  chooseMessageFile: vi.fn(),
  getStorageSync: vi.fn(() => ''),
  setStorageSync: vi.fn(),
} as any

describe('ConsultationForm', () => {
  let wrapper: VueWrapper
  let pinia: any

  beforeEach(() => {
    // Create fresh pinia instance for each test
    pinia = createPinia()
    setActivePinia(pinia)

    // Clear all mocks before each test
    vi.clearAllMocks()
  })

  it('component mounts successfully', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays page header with title and subtitle', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    // Check that header section exists
    const header = wrapper.find('.header')
    expect(header.exists()).toBe(true)

    // Check title is displayed
    expect(wrapper.text()).toContain('保险方案咨询')
    expect(wrapper.text()).toContain('请填写您和家人的信息')
  })

  it('displays all form input fields', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    // Check for form sections
    expect(wrapper.text()).toContain('基本信息')
    expect(wrapper.text()).toContain('家庭信息')
    expect(wrapper.text()).toContain('健康与保险信息')

    // Check for required field labels
    expect(wrapper.text()).toContain('姓名')
    expect(wrapper.text()).toContain('年龄')
    expect(wrapper.text()).toContain('性别')
    expect(wrapper.text()).toContain('职业')
    expect(wrapper.text()).toContain('年收入')
    expect(wrapper.text()).toContain('婚姻状况')
  })

  it('displays submit button', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const submitText = wrapper.text()
    expect(submitText).toContain('获取AI保险建议')
  })

  it('has gender radio options', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    expect(wrapper.text()).toContain('男')
    expect(wrapper.text()).toContain('女')
  })

  it('has marital status radio options', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    expect(wrapper.text()).toContain('未婚')
    expect(wrapper.text()).toContain('已婚')
    expect(wrapper.text()).toContain('离异')
    expect(wrapper.text()).toContain('丧偶')
  })

  it('has textarea fields for health conditions and existing insurance', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    expect(wrapper.text()).toContain('健康状况')
    expect(wrapper.text()).toContain('已有保险')
  })

  it('displays character counter for textarea fields', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const charCounts = wrapper.findAll('.char-count')
    expect(charCounts.length).toBeGreaterThan(0)
  })

  it('shows loading indicator when isLoading is true', async () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    // Get the consultation store and set loading state
    const { useConsultationStore } = require('@/stores/consultation')
    const store = useConsultationStore()

    // Force loading state
    store.isLoading = true

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('AI分析中')
  })

  it('displays results section when submission is successful', async () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const { useConsultationStore } = require('@/stores/consultation')
    const store = useConsultationStore()

    // Mock successful response
    store.consultationResult = {
      success: true,
      recommendations: [
        {
          insurance_type: '重疾险',
          recommended_coverage: '50万元',
          reason: '作为家庭经济支柱，需要防范重大疾病风险',
          priority: 'high',
        },
      ],
      reasoning: '根据您的情况，建议配置重疾险...',
      total_estimated_annual_premium: '5000-8000元',
      next_steps: ['联系保险顾问详细了解产品', '进行健康告知'],
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('AI保险建议')
    expect(wrapper.text()).toContain('推荐保险方案')
    expect(wrapper.text()).toContain('重疾险')
  })

  it('has required field indicators', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    // Required fields should have asterisk indicators
    expect(wrapper.html()).toContain('*')
  })

  it('displays error messages for validation errors', async () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const { useConsultationStore } = require('@/stores/consultation')
    const store = useConsultationStore()

    // Set validation error
    store.errors = {
      name: '请输入姓名',
      age: '请输入年龄',
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('请输入姓名')
    expect(wrapper.text()).toContain('请输入年龄')
  })

  it('has reset button for new consultation after successful submission', async () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const { useConsultationStore } = require('@/stores/consultation')
    const store = useConsultationStore()

    // Mock successful response
    store.consultationResult = {
      success: true,
      recommendations: [],
      reasoning: 'Test reasoning',
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('重新咨询')
  })

  it('displays priority badges for recommendations', async () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const { useConsultationStore } = require('@/stores/consultation')
    const store = useConsultationStore()

    // Mock recommendations with different priorities
    store.consultationResult = {
      success: true,
      recommendations: [
        {
          insurance_type: '重疾险',
          recommended_coverage: '50万元',
          reason: 'High priority',
          priority: 'high',
        },
        {
          insurance_type: '意外险',
          recommended_coverage: '100万元',
          reason: 'Medium priority',
          priority: 'medium',
        },
      ],
      reasoning: 'Test',
    }

    await wrapper.vm.$nextTick()

    const html = wrapper.html()
    expect(html).toContain('priority-high')
    expect(html).toContain('priority-medium')
  })

  it('renders submit section with proper classes', () => {
    wrapper = mount(ConsultationForm, {
      global: {
        plugins: [pinia],
      },
    })

    const submitSection = wrapper.find('.submit-section')
    expect(submitSection.exists()).toBe(true)

    const submitBtn = wrapper.find('.submit-btn')
    expect(submitBtn.exists()).toBe(true)
  })

  describe('Form Field Structure', () => {
    it('has name input field', () => {
      wrapper = mount(ConsultationForm, {
        global: {
          plugins: [pinia],
        },
      })

      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThan(0)
    })

    it('has textarea for health conditions', () => {
      wrapper = mount(ConsultationForm, {
        global: {
          plugins: [pinia],
        },
      })

      const textareas = wrapper.findAll('textarea')
      expect(textareas.length).toBeGreaterThan(0)
    })
  })

  describe('Result Display', () => {
    it('displays reasoning section', async () => {
      wrapper = mount(ConsultationForm, {
        global: {
          plugins: [pinia],
        },
      })

      const { useConsultationStore } = require('@/stores/consultation')
      const store = useConsultationStore()

      store.consultationResult = {
        success: true,
        recommendations: [],
        reasoning: '这是一个综合性的保险建议...',
      }

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('分析说明')
      expect(wrapper.text()).toContain('这是一个综合性的保险建议')
    })

    it('displays estimated premium section', async () => {
      wrapper = mount(ConsultationForm, {
        global: {
          plugins: [pinia],
        },
      })

      const { useConsultationStore } = require('@/stores/consultation')
      const store = useConsultationStore()

      store.consultationResult = {
        success: true,
        recommendations: [],
        reasoning: 'Test',
        total_estimated_annual_premium: '5000-8000元',
      }

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('预估保费')
      expect(wrapper.text()).toContain('5000-8000元')
    })

    it('displays next steps section', async () => {
      wrapper = mount(ConsultationForm, {
        global: {
          plugins: [pinia],
        },
      })

      const { useConsultationStore } = require('@/stores/consultation')
      const store = useConsultationStore()

      store.consultationResult = {
        success: true,
        recommendations: [],
        reasoning: 'Test',
        next_steps: ['联系保险顾问', '进行健康告知', '完成投保申请'],
      }

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('下一步建议')
      expect(wrapper.text()).toContain('联系保险顾问')
    })
  })
})
