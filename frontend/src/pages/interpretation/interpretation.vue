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
            <view class="file-remove" @tap="removeFile">
              <text class="remove-icon">×</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Analysis Button -->
      <view
        v-if="uploadedFile"
        class="analyze-btn"
        :class="{ disabled: isAnalyzing }"
        @tap="handleAnalyze"
      >
        <text v-if="!isAnalyzing" class="analyze-text">开始解读</text>
        <text v-else class="analyze-text">分析中...</text>
      </view>
    </view>

    <!-- Results Section -->
    <view v-if="analysisResult" class="results-section">
      <view class="results-card">
        <view class="results-header">
          <text class="results-title">解读结果</text>
          <view class="results-icon">✨</view>
        </view>

        <!-- Policy Overview -->
        <view class="result-group">
          <text class="result-group-title">保单概览</text>
          <view class="result-content">
            <view class="result-item">
              <text class="result-label">保险产品名称</text>
              <text class="result-value">{{ analysisResult.productName || '暂无信息' }}</text>
            </view>
            <view class="result-item">
              <text class="result-label">保险公司</text>
              <text class="result-value">{{ analysisResult.company || '暂无信息' }}</text>
            </view>
            <view class="result-item">
              <text class="result-label">保险类型</text>
              <text class="result-value">{{ analysisResult.type || '暂无信息' }}</text>
            </view>
          </view>
        </view>

        <!-- Coverage Details -->
        <view class="result-group">
          <text class="result-group-title">保障内容</text>
          <view class="result-content">
            <view
              v-for="(coverage, index) in analysisResult.coverages"
              :key="index"
              class="coverage-item"
            >
              <text class="coverage-title">{{ coverage.title }}</text>
              <text class="coverage-description">{{ coverage.description }}</text>
              <text v-if="coverage.amount" class="coverage-amount"
                >保额：{{ coverage.amount }}</text
              >
            </view>
            <text v-if="!analysisResult.coverages?.length" class="empty-text"
              >暂无保障信息</text
            >
          </view>
        </view>

        <!-- Claim Conditions -->
        <view class="result-group">
          <text class="result-group-title">理赔条件</text>
          <view class="result-content">
            <view
              v-for="(condition, index) in analysisResult.claimConditions"
              :key="index"
              class="condition-item"
            >
              <text class="condition-icon">•</text>
              <text class="condition-text">{{ condition }}</text>
            </view>
            <text v-if="!analysisResult.claimConditions?.length" class="empty-text"
              >暂无理赔条件信息</text
            >
          </view>
        </view>

        <!-- Exclusions -->
        <view class="result-group">
          <text class="result-group-title">责任免除</text>
          <view class="result-content">
            <view
              v-for="(exclusion, index) in analysisResult.exclusions"
              :key="index"
              class="exclusion-item"
            >
              <text class="exclusion-icon">⚠️</text>
              <text class="exclusion-text">{{ exclusion }}</text>
            </view>
            <text v-if="!analysisResult.exclusions?.length" class="empty-text"
              >暂无免责条款信息</text
            >
          </view>
        </view>

        <!-- Important Notes -->
        <view class="result-group">
          <text class="result-group-title">重要提示</text>
          <view class="result-content">
            <view
              v-for="(note, index) in analysisResult.importantNotes"
              :key="index"
              class="note-item"
            >
              <text class="note-icon">💡</text>
              <text class="note-text">{{ note }}</text>
            </view>
            <text v-if="!analysisResult.importantNotes?.length" class="empty-text"
              >暂无重要提示</text
            >
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
 * - Policy overview (product name, company, type)
 * - Coverage details
 * - Claim conditions
 * - Exclusions
 * - Important notes
 */
import { onReady } from '@dcloudio/uni-app'
import { ref } from 'vue'

/**
 * Uploaded file interface
 */
interface UploadedFile {
  name: string
  size: number
  path: string
  type: string
}

/**
 * Analysis result interface
 */
interface AnalysisResult {
  productName: string
  company: string
  type: string
  coverages: Array<{
    title: string
    description: string
    amount?: string
  }>
  claimConditions: string[]
  exclusions: string[]
  importantNotes: string[]
}

/**
 * Uploaded file state
 */
const uploadedFile = ref<UploadedFile | null>(null)

/**
 * Analysis result state
 */
const analysisResult = ref<AnalysisResult | null>(null)

/**
 * Analyzing state
 */
const isAnalyzing = ref(false)

/**
 * Page lifecycle - triggered when page is ready
 */
onReady(() => {
  uni.setNavigationBarTitle({
    title: '保单解读'
  })
})

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

      // Validate file size (10MB max)
      const maxSize = 10 * 1024 * 1024
      if (file.size > maxSize) {
        uni.showToast({
          title: '文件大小不能超过10MB',
          icon: 'none',
          duration: 2000
        })
        return
      }

      uploadedFile.value = {
        name: file.name,
        size: file.size,
        path: file.path,
        type: getFileType(file.name)
      }

      // Reset previous analysis result when new file is selected
      analysisResult.value = null
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
 * Get file type from file name
 */
const getFileType = (fileName: string): string => {
  const ext = fileName.toLowerCase().split('.').pop()
  if (ext === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png'].includes(ext || '')) return 'image'
  return 'unknown'
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
const removeFile = () => {
  uploadedFile.value = null
  analysisResult.value = null
}

/**
 * Handle analysis
 */
const handleAnalyze = async () => {
  if (!uploadedFile.value) {
    uni.showToast({
      title: '请先选择文件',
      icon: 'none',
      duration: 2000
    })
    return
  }

  isAnalyzing.value = true

  try {
    // TODO: Integrate with backend API
    // For now, simulate API call with mock data
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Mock analysis result
    analysisResult.value = {
      productName: '重大疾病保险',
      company: '示例保险公司',
      type: '健康险',
      coverages: [
        {
          title: '重大疾病保障',
          description: '涵盖100种重大疾病，确诊后一次性赔付保险金',
          amount: '50万元'
        },
        {
          title: '轻症疾病保障',
          description: '涵盖50种轻症疾病，赔付基本保额的30%',
          amount: '15万元'
        },
        {
          title: '身故保障',
          description: '被保险人身故，赔付基本保额',
          amount: '50万元'
        }
      ],
      claimConditions: [
        '确诊合同约定的重大疾病，需提供医院出具的诊断证明',
        '轻症疾病需经保险公司认可的医疗机构确诊',
        '申请理赔时需提供完整病历、检查报告等材料',
        '理赔申请应在确诊后30日内提出'
      ],
      exclusions: [
        '投保人对被保险人的故意杀害、故意伤害',
        '被保险人故意自伤、故意犯罪或抗拒依法采取的刑事强制措施',
        '被保险人主动吸食或注射毒品',
        '酒后驾驶、无合法有效驾驶证驾驶，或驾驶无有效行驶证的机动车',
        '战争、军事冲突、暴乱或武装叛乱',
        '核爆炸、核辐射或核污染',
        '遗传性疾病、先天性畸形、变形或染色体异常'
      ],
      importantNotes: [
        '本合同有90天等待期，等待期内确诊不承担保险责任',
        '轻症赔付后，重大疾病保额不变，但需继续缴纳保费',
        '重疾赔付后，合同终止',
        '请如实告知健康状况，否则可能影响理赔',
        '建议仔细阅读保险条款，了解具体保障范围'
      ]
    }

    uni.showToast({
      title: '解读完成',
      icon: 'success',
      duration: 2000
    })
  } catch (error) {
    uni.showToast({
      title: '解读失败，请重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    isAnalyzing.value = false
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
</style>
