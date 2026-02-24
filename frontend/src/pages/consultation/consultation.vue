<!-- AI Insurance Advisor - Consultation Form Page -->
<template>
  <view class="page-container">
    <!-- Header Section -->
    <view class="header">
      <text class="header-title">保险方案咨询</text>
      <text class="header-subtitle">请填写您和家人的信息，AI将为您推荐最适合的保险方案</text>
    </view>

    <!-- Loading Indicator -->
    <view v-if="isLoading" class="loading-overlay">
      <view class="loading-content">
        <text class="loading-text">AI分析中，请稍候...</text>
      </view>
    </view>

    <!-- Results Section (shown after successful submission) -->
    <view v-if="isSuccessful" class="results-section">
      <view class="results-header">
        <text class="results-title">AI保险建议</text>
        <view class="close-btn" @tap="handleReset">
          <text class="close-text">重新咨询</text>
        </view>
      </view>

      <!-- Recommendations List -->
      <view class="result-group">
        <text class="result-group-title">推荐保险方案</text>
        <view
          v-for="(rec, index) in recommendations"
          :key="index"
          class="recommendation-card"
          :class="`priority-${rec.priority || 'medium'}`"
        >
          <view class="rec-header">
            <text class="rec-type">{{ rec.insurance_type }}</text>
            <view v-if="rec.priority" class="priority-badge" :class="rec.priority">
              <text class="priority-text">{{ getPriorityLabel(rec.priority) }}</text>
            </view>
          </view>
          <text class="rec-coverage">建议保额：{{ rec.recommended_coverage }}</text>
          <text class="rec-reason">{{ rec.reason }}</text>
        </view>
      </view>

      <!-- Reasoning -->
      <view v-if="reasoning" class="result-group">
        <text class="result-group-title">分析说明</text>
        <view class="reasoning-card">
          <text class="reasoning-text">{{ reasoning }}</text>
        </view>
      </view>

      <!-- Estimated Premium -->
      <view v-if="estimatedPremium" class="result-group">
        <text class="result-group-title">预估保费</text>
        <view class="premium-card">
          <text class="premium-amount">{{ estimatedPremium }}</text>
        </view>
      </view>

      <!-- Next Steps -->
      <view v-if="nextSteps.length > 0" class="result-group">
        <text class="result-group-title">下一步建议</text>
        <view class="steps-card">
          <view
            v-for="(step, index) in nextSteps"
            :key="index"
            class="step-item"
          >
            <view class="step-bullet">
              <text class="step-number">{{ index + 1 }}</text>
            </view>
            <text class="step-text">{{ step }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Form Section (hidden when showing results) -->
    <view v-else class="form-section">
      <!-- Basic Information -->
      <view class="form-group">
        <text class="group-title">基本信息</text>

        <!-- Name -->
        <view class="form-item">
          <text class="label">姓名 <text class="required">*</text></text>
          <input
            class="input"
            :value="formData.name"
            @input="(e: any) => handleInputChange('name', e.detail.value)"
            placeholder="请输入您的姓名"
          />
          <text v-if="errors.name" class="error-text">{{ errors.name }}</text>
        </view>

        <!-- Age -->
        <view class="form-item">
          <text class="label">年龄 <text class="required">*</text></text>
          <input
            class="input"
            :value="formData.age"
            @input="(e: any) => handleInputChange('age', e.detail.value)"
            type="number"
            placeholder="请输入您的年龄"
          />
          <text v-if="errors.age" class="error-text">{{ errors.age }}</text>
        </view>

        <!-- Gender -->
        <view class="form-item">
          <text class="label">性别 <text class="required">*</text></text>
          <view class="radio-group">
            <view
              class="radio-item"
              :class="{ active: formData.gender === 'male' }"
              @tap="selectGender('male')"
            >
              <text class="radio-text">男</text>
            </view>
            <view
              class="radio-item"
              :class="{ active: formData.gender === 'female' }"
              @tap="selectGender('female')"
            >
              <text class="radio-text">女</text>
            </view>
          </view>
          <text v-if="errors.gender" class="error-text">{{ errors.gender }}</text>
        </view>

        <!-- Occupation -->
        <view class="form-item">
          <text class="label">职业</text>
          <input
            class="input"
            :value="formData.occupation"
            @input="(e: any) => handleInputChange('occupation', e.detail.value)"
            placeholder="请输入您的职业"
          />
        </view>

        <!-- Annual Income -->
        <view class="form-item">
          <text class="label">年收入（万元） <text class="required">*</text></text>
          <input
            class="input"
            :value="formData.annualIncome"
            @input="(e: any) => handleInputChange('annualIncome', e.detail.value)"
            type="digit"
            placeholder="请输入您的年收入"
          />
          <text v-if="errors.annualIncome" class="error-text">{{ errors.annualIncome }}</text>
        </view>
      </view>

      <!-- Family Information -->
      <view class="form-group">
        <text class="group-title">家庭信息</text>

        <!-- Marital Status -->
        <view class="form-item">
          <text class="label">婚姻状况 <text class="required">*</text></text>
          <view class="radio-group">
            <view
              class="radio-item"
              :class="{ active: formData.maritalStatus === 'single' }"
              @tap="selectMaritalStatus('single')"
            >
              <text class="radio-text">未婚</text>
            </view>
            <view
              class="radio-item"
              :class="{ active: formData.maritalStatus === 'married' }"
              @tap="selectMaritalStatus('married')"
            >
              <text class="radio-text">已婚</text>
            </view>
            <view
              class="radio-item"
              :class="{ active: formData.maritalStatus === 'divorced' }"
              @tap="selectMaritalStatus('divorced')"
            >
              <text class="radio-text">离异</text>
            </view>
            <view
              class="radio-item"
              :class="{ active: formData.maritalStatus === 'widowed' }"
              @tap="selectMaritalStatus('widowed')"
            >
              <text class="radio-text">丧偶</text>
            </view>
          </view>
          <text v-if="errors.maritalStatus" class="error-text">{{ errors.maritalStatus }}</text>
        </view>

        <!-- Number of Dependents -->
        <view class="form-item">
          <text class="label">被抚养人数</text>
          <input
            class="input"
            :value="formData.dependents"
            @input="(e: any) => handleInputChange('dependents', e.detail.value)"
            type="number"
            placeholder="请输入需要抚养的人数（包括子女、老人等）"
          />
          <text v-if="errors.dependents" class="error-text">{{ errors.dependents }}</text>
        </view>
      </view>

      <!-- Health & Insurance Information -->
      <view class="form-group">
        <text class="group-title">健康与保险信息</text>

        <!-- Health Conditions -->
        <view class="form-item">
          <text class="label">健康状况</text>
          <textarea
            class="textarea"
            :value="formData.healthConditions"
            @input="(e: any) => handleInputChange('healthConditions', e.detail.value)"
            placeholder="请描述您或家人的健康状况，如有慢性病、既往病史等请说明"
            :maxlength="500"
          />
          <text class="char-count">{{ formData.healthConditions.length }}/500</text>
        </view>

        <!-- Existing Insurance -->
        <view class="form-item">
          <text class="label">已有保险</text>
          <textarea
            class="textarea"
            :value="formData.existingInsurance"
            @input="(e: any) => handleInputChange('existingInsurance', e.detail.value)"
            placeholder="请列出您已购买的保险及保额，如：寿险50万、重疾险30万等"
            :maxlength="500"
          />
          <text class="char-count">{{ formData.existingInsurance.length }}/500</text>
        </view>
      </view>
    </view>

    <!-- Submit Button -->
    <view class="submit-section">
      <view
        class="submit-btn"
        :class="{ disabled: !isFormValid || isLoading }"
        @tap="handleSubmit"
      >
        <text v-if="!isLoading" class="submit-text">获取AI保险建议</text>
        <text v-else class="submit-text">提交中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * Consultation Form Page
 *
 * This page collects user and family information for AI-powered insurance recommendations.
 * Fields include: name, age, gender, occupation, annual income, marital status,
 * number of dependents, health conditions, and existing insurance coverage.
 *
 * After submission, displays AI-generated insurance recommendations.
 */
import { onReady } from '@dcloudio/uni-app'
import { useConsultationStore } from '@/stores/consultation'
import { storeToRefs } from 'pinia'
import type { Priority } from '@/types/insurance'

/**
 * Initialize consultation store
 */
const consultationStore = useConsultationStore()

/**
 * Extract reactive state and getters from store
 */
const {
  formData,
  errors,
  isLoading,
  isFormValid,
  isSuccessful,
  recommendations,
  reasoning,
  estimatedPremium,
  nextSteps,
} = storeToRefs(consultationStore)

/**
 * Extract actions from store (non-reactive)
 */
const {
  setField,
  setGender,
  setMaritalStatus,
  validateField,
  validateForm,
  submitConsultationRequest,
  resetForm,
} = consultationStore

/**
 * Page lifecycle - triggered when page is ready
 */
onReady(() => {
  uni.setNavigationBarTitle({
    title: '保险咨询'
  })
})

/**
 * Get priority label in Chinese
 */
const getPriorityLabel = (priority: Priority): string => {
  const labels: Record<Priority, string> = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级',
  }
  return labels[priority] || '推荐'
}

/**
 * Handle input field changes
 */
const handleInputChange = (field: keyof typeof formData.value, value: string) => {
  setField(field, value)
  validateField(field)
}

/**
 * Select gender
 */
const selectGender = (gender: 'male' | 'female') => {
  setGender(gender)
}

/**
 * Select marital status
 */
const selectMaritalStatus = (status: 'single' | 'married' | 'divorced' | 'widowed') => {
  setMaritalStatus(status)
}

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  try {
    await submitConsultationRequest()
  } catch (error) {
    // Error is already handled by the store (toast shown)
    // Just log for debugging
    console.error('Submission failed:', error)
  }
}

/**
 * Handle reset form (for new consultation)
 */
const handleReset = () => {
  uni.showModal({
    title: '重新咨询',
    content: '确定要重新开始咨询吗？当前结果将被清空。',
    success: (res) => {
      if (res.confirm) {
        resetForm()
      }
    },
  })
}
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
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

/* Form Section */
.form-section {
  padding: 30rpx;
}

.form-group {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.group-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 30rpx;
  padding-bottom: 16rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.form-item {
  margin-bottom: 30rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.label {
  display: block;
  font-size: 28rpx;
  color: #333333;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.input {
  width: 100%;
  height: 80rpx;
  padding: 0 20rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333333;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;

  &:focus {
    background-color: #ffffff;
    border-color: #4a90e2;
  }
}

.textarea {
  width: 100%;
  min-height: 160rpx;
  padding: 16rpx 20rpx;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333333;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;

  &:focus {
    background-color: #ffffff;
    border-color: #4a90e2;
  }
}

.char-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #999999;
  margin-top: 8rpx;
}

/* Radio Group */
.radio-group {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.radio-item {
  flex: 1;
  min-width: 140rpx;
  height: 70rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 8rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;

  &.active {
    background-color: #e6f7ff;
    border-color: #4a90e2;
  }

  &:active {
    transform: scale(0.95);
  }
}

.radio-text {
  font-size: 26rpx;
  color: #333333;

  .active & {
    color: #4a90e2;
    font-weight: 500;
  }
}

/* Error Text */
.error-text {
  display: block;
  font-size: 22rpx;
  color: #ff4d4f;
  margin-top: 8rpx;
}

/* Submit Section */
.submit-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  background-color: #ffffff;
  border-top: 1rpx solid #f0f0f0;
  box-shadow: 0 -4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  border-radius: 12rpx;
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
  }

  &.disabled {
    opacity: 0.5;
    pointer-events: none;
  }
}

.submit-text {
  font-size: 32rpx;
  font-weight: 500;
  color: #ffffff;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 60rpx 80rpx;
  text-align: center;
}

.loading-text {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}

/* Results Section */
.results-section {
  padding: 30rpx;
  padding-bottom: 120rpx;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.results-title {
  font-size: 40rpx;
  font-weight: 600;
  color: #1a1a1a;
}

.close-btn {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  border-radius: 8rpx;
}

.close-text {
  font-size: 26rpx;
  color: #ffffff;
  font-weight: 500;
}

.result-group {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.result-group-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 24rpx;
}

/* Recommendation Card */
.recommendation-card {
  background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  border-left: 6rpx solid #4a90e2;

  &:last-child {
    margin-bottom: 0;
  }

  &.priority-high {
    border-left-color: #ff4d4f;
    background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
  }

  &.priority-medium {
    border-left-color: #faad14;
    background: linear-gradient(135deg, #fffbe6 0%, #ffffff 100%);
  }

  &.priority-low {
    border-left-color: #52c41a;
    background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  }
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.rec-type {
  font-size: 30rpx;
  font-weight: 600;
  color: #1a1a1a;
}

.priority-badge {
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  font-size: 22rpx;
  font-weight: 500;

  &.high {
    background-color: #ff4d4f;
    color: #ffffff;
  }

  &.medium {
    background-color: #faad14;
    color: #ffffff;
  }

  &.low {
    background-color: #52c41a;
    color: #ffffff;
  }
}

.priority-text {
  font-size: 22rpx;
}

.rec-coverage {
  display: block;
  font-size: 26rpx;
  color: #4a90e2;
  font-weight: 500;
  margin-bottom: 12rpx;
}

.rec-reason {
  display: block;
  font-size: 26rpx;
  color: #666666;
  line-height: 1.6;
}

/* Reasoning Card */
.reasoning-card {
  background-color: #f6f8fb;
  border-radius: 12rpx;
  padding: 24rpx;
}

.reasoning-text {
  font-size: 26rpx;
  color: #333333;
  line-height: 1.6;
}

/* Premium Card */
.premium-card {
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  border-radius: 12rpx;
  padding: 30rpx;
  text-align: center;
}

.premium-amount {
  font-size: 36rpx;
  font-weight: 600;
  color: #ffffff;
}

/* Steps Card */
.steps-card {
  background-color: #f6f8fb;
  border-radius: 12rpx;
  padding: 24rpx;
}

.step-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.step-bullet {
  flex-shrink: 0;
  width: 40rpx;
  height: 40rpx;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.step-number {
  font-size: 22rpx;
  font-weight: 600;
  color: #ffffff;
}

.step-text {
  flex: 1;
  font-size: 26rpx;
  color: #333333;
  line-height: 1.6;
  padding-top: 6rpx;
}
</style>
