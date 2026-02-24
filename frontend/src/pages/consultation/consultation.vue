<!-- AI Insurance Advisor - Consultation Form Page -->
<template>
  <view class="page-container">
    <!-- Header Section -->
    <view class="header">
      <text class="header-title">保险方案咨询</text>
      <text class="header-subtitle">请填写您和家人的信息，AI将为您推荐最适合的保险方案</text>
    </view>

    <!-- Form Section -->
    <view class="form-section">
      <!-- Basic Information -->
      <view class="form-group">
        <text class="group-title">基本信息</text>

        <!-- Name -->
        <view class="form-item">
          <text class="label">姓名 <text class="required">*</text></text>
          <input
            class="input"
            v-model="formData.name"
            placeholder="请输入您的姓名"
            @input="validateField('name')"
          />
          <text v-if="errors.name" class="error-text">{{ errors.name }}</text>
        </view>

        <!-- Age -->
        <view class="form-item">
          <text class="label">年龄 <text class="required">*</text></text>
          <input
            class="input"
            v-model="formData.age"
            type="number"
            placeholder="请输入您的年龄"
            @input="validateField('age')"
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
            v-model="formData.occupation"
            placeholder="请输入您的职业"
          />
        </view>

        <!-- Annual Income -->
        <view class="form-item">
          <text class="label">年收入（万元） <text class="required">*</text></text>
          <input
            class="input"
            v-model="formData.annualIncome"
            type="digit"
            placeholder="请输入您的年收入"
            @input="validateField('annualIncome')"
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
            v-model="formData.dependents"
            type="number"
            placeholder="请输入需要抚养的人数（包括子女、老人等）"
          />
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
            v-model="formData.healthConditions"
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
            v-model="formData.existingInsurance"
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
        :class="{ disabled: !isFormValid || isSubmitting }"
        @tap="handleSubmit"
      >
        <text v-if="!isSubmitting" class="submit-text">获取AI保险建议</text>
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
 */
import { onReady } from '@dcloudio/uni-app'
import { ref, computed } from 'vue'

/**
 * Form data interface
 */
interface ConsultationFormData {
  name: string
  age: string
  gender: 'male' | 'female' | ''
  occupation: string
  annualIncome: string
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed' | ''
  dependents: string
  healthConditions: string
  existingInsurance: string
}

/**
 * Form data state
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
  existingInsurance: ''
})

/**
 * Validation errors state
 */
const errors = ref<Record<string, string>>({})

/**
 * Submitting state
 */
const isSubmitting = ref(false)

/**
 * Page lifecycle - triggered when page is ready
 */
onReady(() => {
  uni.setNavigationBarTitle({
    title: '保险咨询'
  })
})

/**
 * Validate individual field
 */
const validateField = (field: string): boolean => {
  errors.value[field] = ''

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
      break

    case 'age':
      if (!formData.value.age) {
        errors.value.age = '请输入年龄'
        return false
      }
      const age = parseInt(formData.value.age)
      if (isNaN(age) || age < 0 || age > 120) {
        errors.value.age = '请输入有效的年龄（0-120岁）'
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
  }

  return true
}

/**
 * Validate all form fields
 */
const validateForm = (): boolean => {
  let isValid = true

  // Validate required fields
  if (!validateField('name')) isValid = false
  if (!validateField('age')) isValid = false
  if (!validateField('annualIncome')) isValid = false

  if (!formData.value.gender) {
    errors.value.gender = '请选择性别'
    isValid = false
  } else {
    delete errors.value.gender
  }

  if (!formData.value.maritalStatus) {
    errors.value.maritalStatus = '请选择婚姻状况'
    isValid = false
  } else {
    delete errors.value.maritalStatus
  }

  return isValid
}

/**
 * Check if form is valid
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
 * Select gender
 */
const selectGender = (gender: 'male' | 'female') => {
  formData.value.gender = gender
  delete errors.value.gender
}

/**
 * Select marital status
 */
const selectMaritalStatus = (status: 'single' | 'married' | 'divorced' | 'widowed') => {
  formData.value.maritalStatus = status
  delete errors.value.maritalStatus
}

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  // Validate form
  if (!validateForm()) {
    uni.showToast({
      title: '请检查表单填写',
      icon: 'none',
      duration: 2000
    })
    return
  }

  isSubmitting.value = true

  try {
    // TODO: Integrate with backend API
    // For now, simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Show success message
    uni.showToast({
      title: '提交成功',
      icon: 'success',
      duration: 2000
    })

    // TODO: Navigate to results page
    // uni.navigateTo({
    //   url: '/pages/consultation/result'
    // })
  } catch (error) {
    uni.showToast({
      title: '提交失败，请重试',
      icon: 'none',
      duration: 2000
    })
  } finally {
    isSubmitting.value = false
  }
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
</style>
