<!-- AI Insurance Advisor - Landing Page -->
<template>
  <view class="page-container">
    <!-- Header Section -->
    <view class="header">
      <view class="logo-container">
        <text class="logo-icon">🛡️</text>
      </view>
      <text class="app-name">智能保险顾问</text>
      <text class="app-slogan">AI驱动的专业保险咨询与解读服务</text>
    </view>

    <!-- Features Section -->
    <view class="features-section">
      <text class="section-title">选择服务</text>

      <!-- Consultation Feature Card -->
      <view class="feature-card" @tap="navigateToConsultation">
        <view class="feature-icon consultation-icon">💬</view>
        <view class="feature-content">
          <text class="feature-title">保险方案咨询</text>
          <text class="feature-description"
            >根据您和家人的情况，AI智能推荐最适合的保险方案</text
          >
          <view class="feature-tags">
            <text class="tag">个性化推荐</text>
            <text class="tag">专业分析</text>
          </view>
        </view>
        <view class="feature-arrow">→</view>
      </view>

      <!-- Interpretation Feature Card -->
      <view class="feature-card" @tap="navigateToInterpretation">
        <view class="feature-icon interpretation-icon">📄</view>
        <view class="feature-content">
          <text class="feature-title">保险合同解读</text>
          <text class="feature-description"
            >上传保险合同，AI为您详细解读条款、理赔条件及赔付详情</text
          >
          <view class="feature-tags">
            <text class="tag">条款解析</text>
            <text class="tag">智能解读</text>
          </view>
        </view>
        <view class="feature-arrow">→</view>
      </view>
    </view>

    <!-- Info Section -->
    <view class="info-section">
      <view class="info-item">
        <text class="info-icon">✓</text>
        <text class="info-text">支持健康险、意外险、养老保险、年金险</text>
      </view>
      <view class="info-item">
        <text class="info-icon">✓</text>
        <text class="info-text">AI智能分析，专业可靠</text>
      </view>
      <view class="info-item">
        <text class="info-icon">✓</text>
        <text class="info-text">隐私安全，数据加密保护</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
/**
 * Landing Page - Feature Selection
 *
 * This is the main entry point of the application where users can:
 * 1. Navigate to Insurance Consultation feature
 * 2. Navigate to Contract Interpretation feature
 */
import { onReady } from '@dcloudio/uni-app'

/**
 * Page lifecycle - triggered when page is ready
 */
onReady(() => {
  // Set navigation bar title
  uni.setNavigationBarTitle({
    title: '智能保险顾问'
  })
})

/**
 * Navigate to consultation page
 */
const navigateToConsultation = () => {
  uni.navigateTo({
    url: '/pages/consultation/consultation'
  })
}

/**
 * Navigate to interpretation page
 */
const navigateToInterpretation = () => {
  uni.navigateTo({
    url: '/pages/interpretation/interpretation'
  })
}
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #4a90e2 100%);
  padding: 0;
  display: flex;
  flex-direction: column;
}

/* Header Section */
.header {
  padding: 80rpx 40rpx 60rpx;
  text-align: center;
  color: #ffffff;
}

.logo-container {
  width: 160rpx;
  height: 160rpx;
  margin: 0 auto 30rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.logo-icon {
  font-size: 80rpx;
}

.app-name {
  display: block;
  font-size: 48rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
  letter-spacing: 2rpx;
}

.app-slogan {
  display: block;
  font-size: 28rpx;
  opacity: 0.9;
  line-height: 1.5;
}

/* Features Section */
.features-section {
  flex: 1;
  background-color: #f5f5f5;
  border-radius: 40rpx 40rpx 0 0;
  padding: 50rpx 30rpx 30rpx;
}

.section-title {
  display: block;
  font-size: 36rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 30rpx;
  text-align: center;
}

.feature-card {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(74, 144, 226, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6rpx;
  background: linear-gradient(180deg, #4a90e2 0%, #667eea 100%);
}

.feature-card:active {
  transform: scale(0.98);
  box-shadow: 0 4rpx 12rpx rgba(74, 144, 226, 0.15);
}

.feature-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.consultation-icon {
  background: linear-gradient(135deg, #e0f2ff 0%, #bae7ff 100%);
}

.interpretation-icon {
  background: linear-gradient(135deg, #f0f5ff 0%, #d6e4ff 100%);
}

.feature-content {
  flex: 1;
  min-width: 0;
}

.feature-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8rpx;
}

.feature-description {
  display: block;
  font-size: 24rpx;
  color: #666666;
  line-height: 1.5;
  margin-bottom: 12rpx;
}

.feature-tags {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 6rpx 16rpx;
  background-color: #f0f5ff;
  color: #4a90e2;
  font-size: 20rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.feature-arrow {
  font-size: 32rpx;
  color: #4a90e2;
  margin-left: 12rpx;
  flex-shrink: 0;
}

/* Info Section */
.info-section {
  padding: 30rpx;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.info-icon {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background-color: #52c41a;
  color: #ffffff;
  font-size: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
  flex-shrink: 0;
}

.info-text {
  font-size: 24rpx;
  color: #666666;
  line-height: 1.5;
}
</style>
