/**
 * Consultation Store
 *
 * Pinia store for managing consultation state including form data,
 * validation, API submission, and results.
 *
 * @module stores/consultation
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ConsultationRequest,
  ConsultationResponse,
  ConsultationFormData,
  ValidationErrors,
  Gender,
  MaritalStatus,
} from '@/types/insurance'
import { submitConsultation } from '@/api/insurance'

/**
 * Consultation store state management
 */
export const useConsultationStore = defineStore('consultation', () => {
  // ==================== State ====================

  /**
   * Form data for consultation request
   */
  const formData = ref<ConsultationFormData>({
    name: '',
    age: '',
    gender: '',
    occupation: '',
    annualIncome: '',
    maritalStatus: '',
    dependents: '',
    healthConditions: '',
    existingInsurance: '',
  })

  /**
   * Validation errors for form fields
   */
  const errors = ref<ValidationErrors>({})

  /**
   * Loading state for form submission
   */
  const isLoading = ref(false)

  /**
   * Error message from failed submission
   */
  const submissionError = ref<string | null>(null)

  /**
   * Consultation response data
   */
  const consultationResult = ref<ConsultationResponse | null>(null)

  /**
   * Flag indicating if form has been submitted
   */
  const hasSubmitted = ref(false)

  // ==================== Actions ====================

  /**
   * Set a form field value
   *
   * @param field - Field name
   * @param value - Field value
   */
  const setField = (field: keyof ConsultationFormData, value: string) => {
    formData.value[field] = value as never
    // Clear error for this field when value changes
    if (errors.value[field]) {
      delete errors.value[field]
    }
  }

  /**
   * Set gender value
   *
   * @param gender - Gender value
   */
  const setGender = (gender: Gender) => {
    setField('gender', gender)
  }

  /**
   * Set marital status value
   *
   * @param status - Marital status value
   */
  const setMaritalStatus = (status: MaritalStatus) => {
    setField('maritalStatus', status)
  }

  /**
   * Validate a single form field
   *
   * @param field - Field name to validate
   * @returns true if field is valid, false otherwise
   */
  const validateField = (field: keyof ConsultationFormData): boolean => {
    delete errors.value[field]

    switch (field) {
      case 'name':
        if (!formData.value.name.trim()) {
          errors.value.name = '请输入姓名'
          return false
        }
        if (formData.value.name.trim().length < 2) {
          errors.value.name = '姓名至少需要2个字符'
          return false
        }
        if (formData.value.name.trim().length > 100) {
          errors.value.name = '姓名不能超过100个字符'
          return false
        }
        break

      case 'age':
        if (!formData.value.age) {
          errors.value.age = '请输入年龄'
          return false
        }
        const age = parseInt(formData.value.age)
        if (isNaN(age) || age < 0 || age > 150) {
          errors.value.age = '请输入有效的年龄（0-150岁）'
          return false
        }
        break

      case 'gender':
        if (!formData.value.gender) {
          errors.value.gender = '请选择性别'
          return false
        }
        break

      case 'occupation':
        // Optional field, but validate if provided
        if (formData.value.occupation && formData.value.occupation.trim().length > 100) {
          errors.value.occupation = '职业不能超过100个字符'
          return false
        }
        break

      case 'annualIncome':
        if (!formData.value.annualIncome.trim()) {
          errors.value.annualIncome = '请输入年收入'
          return false
        }
        const income = parseFloat(formData.value.annualIncome)
        if (isNaN(income) || income < 0) {
          errors.value.annualIncome = '请输入有效的年收入'
          return false
        }
        break

      case 'maritalStatus':
        if (!formData.value.maritalStatus) {
          errors.value.maritalStatus = '请选择婚姻状况'
          return false
        }
        break

      case 'dependents':
        // Optional field, but validate if provided
        if (formData.value.dependents) {
          const deps = parseInt(formData.value.dependents)
          if (isNaN(deps) || deps < 0 || deps > 50) {
            errors.value.dependents = '请输入有效的被抚养人数（0-50）'
            return false
          }
        }
        break
    }

    return true
  }

  /**
   * Validate all form fields
   *
   * @returns true if all fields are valid, false otherwise
   */
  const validateForm = (): boolean => {
    let isValid = true

    // Validate required fields
    const requiredFields: (keyof ConsultationFormData)[] = [
      'name',
      'age',
      'gender',
      'annualIncome',
      'maritalStatus',
    ]

    for (const field of requiredFields) {
      if (!validateField(field)) {
        isValid = false
      }
    }

    return isValid
  }

  /**
   * Convert form data to consultation request format
   *
   * @returns Consultation request object
   */
  const buildRequest = (): ConsultationRequest => {
    const request: ConsultationRequest = {
      name: formData.value.name.trim(),
      age: parseInt(formData.value.age),
      gender: formData.value.gender as Gender,
      occupation: formData.value.occupation.trim() || '未填写',
      annual_income: parseFloat(formData.value.annualIncome) * 10000, // Convert to yuan
      marital_status: formData.value.maritalStatus as MaritalStatus,
    }

    // Add optional fields
    if (formData.value.dependents) {
      request.num_dependents = parseInt(formData.value.dependents)
    }

    if (formData.value.healthConditions.trim()) {
      // Split by newlines or commas for array
      request.health_conditions = formData.value.healthConditions
        .trim()
        .split(/[,，\n]+/)
        .filter(s => s.trim())
        .map(s => s.trim())
    }

    if (formData.value.existingInsurance.trim()) {
      // Split by newlines or commas for array
      request.existing_insurance = formData.value.existingInsurance
        .trim()
        .split(/[,，\n]+/)
        .filter(s => s.trim())
        .map(s => s.trim())
    }

    return request
  }

  /**
   * Submit consultation request to backend API
   *
   * @throws Error if validation fails or submission fails
   */
  const submitConsultationRequest = async () => {
    // Reset states
    submissionError.value = null
    hasSubmitted.value = false

    // Validate form
    if (!validateForm()) {
      submissionError.value = '请检查表单填写是否完整和正确'
      throw new Error('表单验证失败')
    }

    isLoading.value = true

    try {
      const request = buildRequest()
      const response = await submitConsultation(request)

      // Store result
      consultationResult.value = response
      hasSubmitted.value = true

      // Show success message
      uni.showToast({
        title: '咨询成功',
        icon: 'success',
        duration: 2000,
      })

      return response
    } catch (error) {
      // Handle error
      const errorMessage =
        error instanceof Error ? error.message : '提交失败，请稍后重试'
      submissionError.value = errorMessage

      // Show error toast
      uni.showToast({
        title: '提交失败',
        icon: 'none',
        duration: 2000,
      })

      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Reset form to initial state
   */
  const resetForm = () => {
    formData.value = {
      name: '',
      age: '',
      gender: '',
      occupation: '',
      annualIncome: '',
      maritalStatus: '',
      dependents: '',
      healthConditions: '',
      existingInsurance: '',
    }
    errors.value = {}
    submissionError.value = null
    consultationResult.value = null
    hasSubmitted.value = false
  }

  /**
   * Clear consultation result
   */
  const clearResult = () => {
    consultationResult.value = null
    hasSubmitted.value = false
  }

  // ==================== Getters ====================

  /**
   * Check if form is valid (all required fields filled)
   */
  const isFormValid = computed(() => {
    return (
      formData.value.name.trim() &&
      formData.value.age &&
      formData.value.gender &&
      formData.value.annualIncome.trim() &&
      formData.value.maritalStatus
    )
  })

  /**
   * Check if form has any validation errors
   */
  const hasErrors = computed(() => {
    return Object.keys(errors.value).length > 0
  })

  /**
   * Check if consultation was successful
   */
  const isSuccessful = computed(() => {
    return hasSubmitted.value && consultationResult.value?.success === true
  })

  /**
   * Get recommended insurance plans
   */
  const recommendations = computed(() => {
    return consultationResult.value?.recommendations || []
  })

  /**
   * Get reasoning for recommendations
   */
  const reasoning = computed(() => {
    return consultationResult.value?.reasoning || ''
  })

  /**
   * Get total estimated annual premium
   */
  const estimatedPremium = computed(() => {
    return consultationResult.value?.total_estimated_annual_premium || ''
  })

  /**
   * Get next steps
   */
  const nextSteps = computed(() => {
    return consultationResult.value?.next_steps || []
  })

  // ==================== Return ====================

  return {
    // State
    formData,
    errors,
    isLoading,
    submissionError,
    consultationResult,
    hasSubmitted,

    // Actions
    setField,
    setGender,
    setMaritalStatus,
    validateField,
    validateForm,
    submitConsultationRequest,
    resetForm,
    clearResult,

    // Getters
    isFormValid,
    hasErrors,
    isSuccessful,
    recommendations,
    reasoning,
    estimatedPremium,
    nextSteps,
  }
})
