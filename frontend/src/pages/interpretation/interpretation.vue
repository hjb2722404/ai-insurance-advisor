<!-- AI Insurance Advisor - Contract Interpretation Page -->
<template>
  <view class="page-container">
    <!-- Header Section -->
    <view class="header">
      <text class="header-title">保单解读</text>
      <text class="header-subtitle">上传保险合同，AI将为您详细解读条款、理赔条件及赔付详情</text>
    </view>

    <!-- Upload Section -->
    <view class="upload-section">
      <view class="upload-card">
        <view class="upload-icon">📄</view>
        <text class="upload-title">上传保险合同</text>
        <text class="upload-description"
          >支持图片格式（JPG、PNG）和PDF格式，文件大小不超过10MB</text
        >

        <!-- File Upload Button -->
        <view class="upload-btn" @tap="chooseFile">
          <text class="upload-btn-text">{{ uploadedFile ? '重新选择' : '选择文件' }}</text>
        </view>

        <!-- Selected File Info -->
        <view v-if="uploadedFile" class="file-info">
          <view class="file-item">
            <text class="file-icon">📎</text>
            <view class="file-details">
              <text class="file-name">{{ uploadedFile.name }}</text>
              <text class="file-size">{{ formatFileSize(uploadedFile.size) }}</text>
            </view>
            <view class="file-remove" @tap="handleRemoveFile">
              <text class="remove-icon">×</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Analysis Button -->
      <view
        v-if="uploadedFile"
        class="analyze-btn"
        :class="{ disabled: isLoading }"
        @tap="handleAnalyze"
      >
        <text v-if="!isLoading" class="analyze-text">开始解读</text>
        <text v-else class="analyze-text">分析中...</text>
      </view>
    </view>

    <!-- Results Section -->
    <view v-if="isSuccessful && interpretationResult" class="results-section">
      <view class="results-card">
        <view class="results-header">
          <text class="results-title">解读结果</text>
          <view class="results-icon">✨</view>
        </view>

        <!-- Summary -->
        <view v-if="interpretationResult.summary" class="result-group">
          <text class="result-group-title">合同概要</text>
          <view class="result-content">
            <text class="summary-text">{{ interpretationResult.summary }}</text>
          </view>
        </view>

        <!-- Key Terms -->
        <view v-if="keyTerms.length > 0" class="result-group">
          <text class="result-group-title">重要条款</text>
          <view class="result-content">
            <view
              v-for="(term, index) in keyTerms"
              :key="index"
              class="term-item"
              :class="`importance-${term.importance || 'medium'}`"
            >
              <view class="term-header">
                <text class="term-name">{{ term.term }}</text>
                <view v-if="term.importance" class="importance-badge" :class="term.importance">
                  <text class="importance-text">{{ getImportanceLabel(term.importance) }}</text>
                </view>
              </view>
              <text class="term-explanation">{{ term.explanation }}</text>
            </view>
            <text v-if="!keyTerms.length" class="empty-text">暂无条款信息</text>
          </view>
        </view>

        <!-- Activation Conditions -->
        <view v-if="activationConditions.length > 0" class="result-group">
          <text class="result-group-title">保障生效条件</text>
          <view class="result-content">
            <view
              v-for="(condition, index) in activationConditions"
              :key="index"
              class="condition-item"
            >
              <view class="condition-header">
                <text class="condition-icon">📋</text>
                <text class="condition-name">{{ condition.condition }}</text>
              </view>
              <text class="condition-description">{{ condition.description }}</text>
              <view v-if="condition.required_documents?.length" class="required-docs">
                <text class="docs-label">所需材料：</text>
                <text
                  v-for="(doc, docIndex) in condition.required_documents"
                  :key="docIndex"
                  class="doc-item"
                >
                  {{ doc }}<template v-if="docIndex < condition.required_documents!.length - 1"
                    >、</template
                  >
                </text>
              </view>
            </view>
            <text v-if="!activationConditions.length" class="empty-text"
              >暂无生效条件信息</text
            >
          </view>
        </view>

        <!-- Payout Details -->
        <view v-if="payoutDetails" class="result-group">
          <text class="result-group-title">赔付详情</text>
          <view class="result-content">
            <view class="payout-item">
              <text class="payout-label">赔付方式</text>
              <text class="payout-value">{{ payoutDetails.payout_method }}</text>
            </view>
            <view class="payout-item">
              <text class="payout-label">赔付金额</text>
              <text class="payout-value">{{ payoutDetails.payout_amount }}</text>
            </view>
            <view class="payout-item">
              <text class="payout-label">赔付时效</text>
              <text class="payout-value">{{ payoutDetails.payout_timeline }}</text>
            </view>
            <view
              v-if="payoutDetails.limitations?.length"
              class="payout-limitations"
            >
              <text class="limitations-label">限制条件：</text>
              <view
                v-for="(limitation, index) in payoutDetails.limitations"
                :key="index"
                class="limitation-item"
              >
                <text class="limitation-text">{{ limitation }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- Important Notes -->
        <view v-if="importantNotes.length > 0" class="result-group">
          <text class="result-group-title">重要提示</text>
          <view class="result-content">
            <view
              v-for="(note, index) in importantNotes"
              :key="index"
              class="note-item"
            >
              <text class="note-icon">💡</text>
              <text class="note-text">{{ note }}</text>
            </view>
            <text v-if="!importantNotes.length" class="empty-text">暂无重要提示</text>
          </view>
        </view>

        <!-- Suggested Questions -->
        <view v-if="suggestedQuestions.length > 0" class="result-group">
          <text class="result-group-title">建议咨询问题</text>
          <view class="result-content">
            <view
              v-for="(question, index) in suggestedQuestions"
              :key="index"
              class="question-item"
            >
              <text class="question-icon">❓</text>
              <text class="question-text">{{ question }}</text>
            </view>
            <text v-if="!suggestedQuestions.length" class="empty-text">暂无建议问题</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * Contract Interpretation Page
 *
 * This page allows users to upload insurance contract documents (images or PDFs)
 * and receive AI-powered analysis including:
 * - Contract summary
 * - Key terms with explanations
 * - Activation conditions
 * - Payout details
 * - Important notes
 * - Suggested questions
 */
import { onReady } from '@dcloudio/uni-app'
import { storeToRefs } from 'pinia'
import { useInterpretationStore } from '@/stores/interpretation'
import type { Importance } from '@/types/insurance'

/**
 * Initialize interpretation store
 */
const interpretationStore = useInterpretationStore()

/**
 * Extract reactive state and getters from store
 */
const {
  uploadedFile,
  isLoading,
  isSuccessful,
  interpretationResult,
  keyTerms,
  activationConditions,
  payoutDetails,
  importantNotes,
  suggestedQuestions,
} = storeToRefs(interpretationStore)

/**
 * Extract actions from store (non-reactive)
 */
const {
  handleFileSelection,
  analyzeContract,
  removeFile: handleRemoveFileStore,
} = interpretationStore

/**
 * Page lifecycle - triggered when page is ready
 */
onReady(() => {
  uni.setNavigationBarTitle({
    title: '保单解读'
  })
})

/**
 * Get importance label in Chinese
 */
const getImportanceLabel = (importance: Importance): string => {
  const labels: Record<Importance, string> = {
    critical: '关键',
    high: '重要',
    medium: '中等',
    low: '一般',
  }
  return labels[importance] || '普通'
}

/**
 * Choose file from device
 */
const chooseFile = () => {
  uni.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['jpg', 'jpeg', 'png', 'pdf'],
    success: (res) => {
      const file = res.tempFiles[0]
      handleFileSelection(file)
    },
    fail: (err) => {
      // User cancelled selection, ignore error
      if (err.errMsg?.includes('cancel')) {
        return
      }
      uni.showToast({
        title: '文件选择失败',
        icon: 'none',
        duration: 2000
      })
    }
  })
}

/**
 * Format file size to human readable format
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Remove uploaded file
 */
const handleRemoveFile = () => {
  handleRemoveFileStore()
}

/**
 * Handle analysis
 */
const handleAnalyze = async () => {
  try {
    await analyzeContract()
  } catch (error) {
    // Error is already handled by the store (toast shown)
    // Just log for debugging
    console.error('Analysis failed:', error)
  }
}
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 30rpx;
}

/* Header Section */
.header {
  padding: 40rpx 30rpx 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  color: #ffffff;
}

.header-title {
  display: block;
  font-size: 40rpx;
  font-weight: 600;
  margin-bottom: 12rpx;
}

.header-subtitle {
  display: block;
  font-size: 24rpx;
  opacity: 0.9;
  line-height: 1.5;
}

/* Upload Section */
.upload-section {
  padding: 30rpx;
}

.upload-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 50rpx 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  text-align: center;
}

.upload-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.upload-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 12rpx;
}

.upload-description {
  display: block;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.5;
  margin-bottom: 40rpx;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  border-radius: 50rpx;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.95);
  }
}

.upload-btn-text {
  font-size: 28rpx;
  font-weight: 500;
  color: #ffffff;
}

/* File Info */
.file-info {
  margin-top: 30rpx;
}

.file-item {
  display: flex;
  align-items: center;
  background-color: #f0f5ff;
  border-radius: 12rpx;
  padding: 20rpx;
}

.file-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  display: block;
  font-size: 26rpx;
  font-weight: 500;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  display: block;
  font-size: 22rpx;
  color: #999999;
  margin-top: 4rpx;
}

.file-remove {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 77, 79, 0.1);
  border-radius: 50%;
  margin-left: 12rpx;
}

.remove-icon {
  font-size: 32rpx;
  color: #ff4d4f;
  line-height: 1;
}

/* Analyze Button */
.analyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  border-radius: 12rpx;
  margin-top: 24rpx;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
  }

  &.disabled {
    opacity: 0.5;
    pointer-events: none;
  }
}

.analyze-text {
  font-size: 32rpx;
  font-weight: 500;
  color: #ffffff;
}

/* Results Section */
.results-section {
  padding: 0 30rpx 30rpx;
}

.results-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #f0f0f0;
  margin-bottom: 30rpx;
}

.results-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
}

.results-icon {
  font-size: 36rpx;
}

.result-group {
  margin-bottom: 30rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.result-group-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 16rpx;
}

.result-content {
  background-color: #f5f5f5;
  border-radius: 12rpx;
  padding: 20rpx;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;

  &:not(:last-child) {
    border-bottom: 1rpx solid #e8e8e8;
  }
}

.result-label {
  font-size: 26rpx;
  color: #666666;
}

.result-value {
  font-size: 26rpx;
  font-weight: 500;
  color: #1a1a1a;
  text-align: right;
  max-width: 400rpx;
}

/* Coverage Item */
.coverage-item {
  padding: 16rpx;
  background-color: #ffffff;
  border-radius: 8rpx;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.coverage-title {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8rpx;
}

.coverage-description {
  display: block;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.5;
  margin-bottom: 8rpx;
}

.coverage-amount {
  display: block;
  font-size: 24rpx;
  font-weight: 500;
  color: #4a90e2;
}

/* Condition Item */
.condition-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.condition-icon {
  font-size: 20rpx;
  color: #4a90e2;
  margin-right: 8rpx;
  line-height: 1.8;
}

.condition-text {
  flex: 1;
  font-size: 24rpx;
  color: #333333;
  line-height: 1.8;
}

/* Exclusion Item */
.exclusion-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.exclusion-icon {
  font-size: 20rpx;
  margin-right: 8rpx;
  line-height: 1.8;
}

.exclusion-text {
  flex: 1;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.8;
}

/* Note Item */
.note-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.note-icon {
  font-size: 20rpx;
  margin-right: 8rpx;
  line-height: 1.8;
}

.note-text {
  flex: 1;
  font-size: 24rpx;
  color: #333333;
  line-height: 1.8;
}

/* Empty Text */
.empty-text {
  display: block;
  font-size: 24rpx;
  color: #999999;
  text-align: center;
  padding: 20rpx 0;
}

/* Summary Text */
.summary-text {
  display: block;
  font-size: 26rpx;
  color: #333333;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* Term Item */
.term-item {
  padding: 16rpx;
  background-color: #ffffff;
  border-radius: 8rpx;
  margin-bottom: 12rpx;
  border-left: 4rpx solid #4a90e2;

  &:last-child {
    margin-bottom: 0;
  }

  &.importance-critical {
    border-left-color: #ff4d4f;
    background: linear-gradient(to right, #fff5f5 0%, #ffffff 50%);
  }

  &.importance-high {
    border-left-color: #faad14;
    background: linear-gradient(to right, #fffbe6 0%, #ffffff 50%);
  }

  &.importance-medium {
    border-left-color: #4a90e2;
    background: linear-gradient(to right, #e6f7ff 0%, #ffffff 50%);
  }

  &.importance-low {
    border-left-color: #52c41a;
    background: linear-gradient(to right, #f6ffed 0%, #ffffff 50%);
  }
}

.term-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.term-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
}

.importance-badge {
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  font-size: 20rpx;
  font-weight: 500;

  &.critical {
    background-color: #ff4d4f;
    color: #ffffff;
  }

  &.high {
    background-color: #faad14;
    color: #ffffff;
  }

  &.medium {
    background-color: #4a90e2;
    color: #ffffff;
  }

  &.low {
    background-color: #52c41a;
    color: #ffffff;
  }
}

.importance-text {
  font-size: 20rpx;
}

.term-explanation {
  display: block;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.6;
}

/* Condition Item */
.condition-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8rpx;
}

.condition-icon {
  font-size: 20rpx;
  margin-right: 8rpx;
  line-height: 1.8;
}

.condition-name {
  flex: 1;
  font-size: 26rpx;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.8;
}

.condition-description {
  display: block;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.6;
  margin-bottom: 8rpx;
  padding-left: 28rpx;
}

.required-docs {
  padding-left: 28rpx;
}

.docs-label {
  font-size: 22rpx;
  color: #999999;
  margin-right: 4rpx;
}

.doc-item {
  font-size: 22rpx;
  color: #4a90e2;
}

/* Payout Item */
.payout-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;

  &:not(:last-child) {
    border-bottom: 1rpx solid #e8e8e8;
  }
}

.payout-label {
  font-size: 26rpx;
  color: #666666;
  font-weight: 500;
}

.payout-value {
  font-size: 26rpx;
  font-weight: 500;
  color: #1a1a1a;
  text-align: right;
  max-width: 400rpx;
}

.payout-limitations {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #e8e8e8;
}

.limitations-label {
  display: block;
  font-size: 22rpx;
  color: #999999;
  margin-bottom: 8rpx;
}

.limitation-item {
  padding-left: 16rpx;
}

.limitation-text {
  font-size: 22rpx;
  color: #666666;
  line-height: 1.6;
}

/* Question Item */
.question-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.question-icon {
  font-size: 20rpx;
  margin-right: 8rpx;
  line-height: 1.8;
}

.question-text {
  flex: 1;
  font-size: 24rpx;
  color: #333333;
  line-height: 1.8;
}
</style>
