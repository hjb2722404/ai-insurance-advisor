<!-- AI Insurance Advisor - Root App Component -->

<script setup lang="ts">
/**
 * Root component for the AI Insurance Advisor application
 *
 * This component serves as the root of the application tree.
 * In uni-app, pages are rendered within the layout defined here.
 * Global styles and app-level lifecycle hooks can be added here.
 */
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

/**
 * App lifecycle - triggered when app initializes
 * Called only once when the app first launches
 */
onLaunch(() => {
  // Initialize app-level configurations
  // Note: Use uni.* APIs for cross-platform compatibility
})

/**
 * App lifecycle - triggered when app enters foreground
 * Called when app starts or returns from background
 */
onShow(() => {
  // Handle app becoming visible
})

/**
 * App lifecycle - triggered when app enters background
 * Called when user switches away from the app
 */
onHide(() => {
  // Handle app becoming hidden
})
</script>

<style lang="scss">
/* Global Styles for AI Insurance Advisor */

/* Reset default margins and padding */
page,
view,
text {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Use rpx units for responsive design across different screen sizes */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 28rpx;
  line-height: 1.6;
  color: #333333;
  background-color: #f5f5f5;
}

/* Common utility classes */
.container {
  width: 100%;
  padding: 30rpx;
}

.page-container {
  min-height: 100vh;
  padding: 30rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 30rpx;
}

.card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* Button styles */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #4a90e2;
  color: #ffffff;
}

.btn-primary:active {
  background-color: #3a7bc8;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333333;
}

.btn-secondary:active {
  background-color: #e0e0e0;
}

/* Form input styles */
.input-wrapper {
  margin-bottom: 30rpx;
}

.input-label {
  font-size: 28rpx;
  color: #666666;
  margin-bottom: 12rpx;
  display: block;
}

.input-error {
  font-size: 24rpx;
  color: #ff4d4f;
  margin-top: 8rpx;
}

/* Loading state */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  color: #999999;
  font-size: 28rpx;
}

/* Error message */
.error-message {
  padding: 30rpx;
  background-color: #fff2f0;
  border-radius: 12rpx;
  color: #ff4d4f;
  font-size: 28rpx;
  text-align: center;
}

/* Success message */
.success-message {
  padding: 30rpx;
  background-color: #f6ffed;
  border-radius: 12rpx;
  color: #52c41a;
  font-size: 28rpx;
  text-align: center;
}
</style>
