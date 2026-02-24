/**
 * Interpretation Store
 *
 * Pinia store for managing contract interpretation state including file upload,
 * API submission, and analysis results.
 *
 * @module stores/interpretation
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { InterpretationResponse } from '@/types/insurance'
import { uploadContractForInterpretation } from '@/api/insurance'

/**
 * Uploaded file interface
 */
interface UploadedFile {
  /** File name */
  name: string
  /** File size in bytes */
  size: number
  /** Local file path */
  path: string
  /** File type (pdf, image, etc.) */
  type: string
}

/**
 * Interpretation store state management
 */
export const useInterpretationStore = defineStore('interpretation', () => {
  // ==================== State ====================

  /**
   * Uploaded file state
   */
  const uploadedFile = ref<UploadedFile | null>(null)

  /**
   * Loading state for analysis
   */
  const isLoading = ref(false)

  /**
   * Error message from failed analysis
   */
  const analysisError = ref<string | null>(null)

  /**
   * Interpretation result from API
   */
  const interpretationResult = ref<InterpretationResponse | null>(null)

  /**
   * Flag indicating if analysis has been completed
   */
  const hasAnalyzed = ref(false)

  // ==================== Actions ====================

  /**
   * Set uploaded file
   *
   * @param file - File info object
   */
  const setUploadedFile = (file: UploadedFile | null) => {
    uploadedFile.value = file
    // Clear previous result when new file is uploaded
    if (file) {
      clearResult()
    }
  }

  /**
   * Get file type from file name
   *
   * @param fileName - Name of the file
   * @returns File type (pdf, image, or unknown)
   */
  const getFileType = (fileName: string): string => {
    const ext = fileName.toLowerCase().split('.').pop()
    if (ext === 'pdf') return 'pdf'
    if (['jpg', 'jpeg', 'png'].includes(ext || '')) return 'image'
    return 'unknown'
  }

  /**
   * Validate file size (10MB max)
   *
   * @param fileSize - File size in bytes
   * @returns true if valid, false otherwise
   */
  const validateFileSize = (fileSize: number): boolean => {
    const maxSize = 10 * 1024 * 1024 // 10MB
    return fileSize <= maxSize
  }

  /**
   * Handle file selection and validation
   *
   * @param file - File from uni.chooseMessageFile
   * @returns true if file is valid and set, false otherwise
   */
  const handleFileSelection = (file: { name: string; size: number; path: string }): boolean => {
    // Validate file size
    if (!validateFileSize(file.size)) {
      uni.showToast({
        title: '文件大小不能超过10MB',
        icon: 'none',
        duration: 2000,
      })
      return false
    }

    // Set uploaded file
    uploadedFile.value = {
      name: file.name,
      size: file.size,
      path: file.path,
      type: getFileType(file.name),
    }

    return true
  }

  /**
   * Submit contract for interpretation to backend API
   *
   * @throws Error if no file is selected or submission fails
   */
  const analyzeContract = async () => {
    // Reset states
    analysisError.value = null
    hasAnalyzed.value = false

    // Check if file is selected
    if (!uploadedFile.value) {
      analysisError.value = '请先选择文件'
      uni.showToast({
        title: '请先选择文件',
        icon: 'none',
        duration: 2000,
      })
      throw new Error('未选择文件')
    }

    isLoading.value = true

    try {
      const response = await uploadContractForInterpretation(uploadedFile.value.path)

      // Store result
      interpretationResult.value = response
      hasAnalyzed.value = true

      // Show success message
      uni.showToast({
        title: '解读完成',
        icon: 'success',
        duration: 2000,
      })

      return response
    } catch (error) {
      // Handle error
      const errorMessage =
        error instanceof Error ? error.message : '解读失败，请稍后重试'
      analysisError.value = errorMessage

      // Show error toast
      uni.showToast({
        title: '解读失败',
        icon: 'none',
        duration: 2000,
      })

      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Remove uploaded file and clear results
   */
  const removeFile = () => {
    uploadedFile.value = null
    clearResult()
  }

  /**
   * Clear interpretation result
   */
  const clearResult = () => {
    interpretationResult.value = null
    hasAnalyzed.value = false
    analysisError.value = null
  }

  /**
   * Reset store to initial state
   */
  const resetStore = () => {
    uploadedFile.value = null
    isLoading.value = false
    analysisError.value = null
    interpretationResult.value = null
    hasAnalyzed.value = false
  }

  // ==================== Getters ====================

  /**
   * Check if a file is currently uploaded
   */
  const hasFile = computed(() => {
    return uploadedFile.value !== null
  })

  /**
   * Check if analysis was successful
   */
  const isSuccessful = computed(() => {
    return hasAnalyzed.value && interpretationResult.value?.success === true
  })

  /**
   * Get summary from interpretation result
   */
  const summary = computed(() => {
    return interpretationResult.value?.summary || ''
  })

  /**
   * Get key terms from interpretation result
   */
  const keyTerms = computed(() => {
    return interpretationResult.value?.key_terms || []
  })

  /**
   * Get activation conditions from interpretation result
   */
  const activationConditions = computed(() => {
    return interpretationResult.value?.activation_conditions || []
  })

  /**
   * Get payout details from interpretation result
   */
  const payoutDetails = computed(() => {
    return interpretationResult.value?.payout_details
  })

  /**
   * Get important notes from interpretation result
   */
  const importantNotes = computed(() => {
    return interpretationResult.value?.important_notes || []
  })

  /**
   * Get suggested questions from interpretation result
   */
  const suggestedQuestions = computed(() => {
    return interpretationResult.value?.suggested_questions || []
  })

  // ==================== Return ====================

  return {
    // State
    uploadedFile,
    isLoading,
    analysisError,
    interpretationResult,
    hasAnalyzed,

    // Actions
    setUploadedFile,
    getFileType,
    validateFileSize,
    handleFileSelection,
    analyzeContract,
    removeFile,
    clearResult,
    resetStore,

    // Getters
    hasFile,
    isSuccessful,
    summary,
    keyTerms,
    activationConditions,
    payoutDetails,
    importantNotes,
    suggestedQuestions,
  }
})
