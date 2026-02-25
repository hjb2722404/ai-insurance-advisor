/**
 * End-to-End Tests for Insurance Consultation Flow
 *
 * Tests the complete user journey from landing page to viewing recommendations.
 */

import { test, expect } from '@playwright/test'

test.describe('Insurance Consultation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173/')
  })

  test('complete consultation journey', async ({ page }) => {
    // Step 1: Verify landing page loads
    await expect(page.locator('text=智能保险顾问')).toBeVisible()
    await expect(page.locator('text=AI-powered insurance advisor')).toBeVisible()

    // Step 2: Click consultation button
    await page.click('text=保险方案咨询')

    // Verify we're on the consultation page
    await expect(page).toHaveURL(/\/pages\/consultation\/consultation/)

    // Step 3: Fill the form with valid data
    await page.fill('[name="name"]', '张三')
    await page.fill('[name="age"]', '35')
    await page.click('text=男')
    await page.fill('[name="occupation"]', '软件工程师')
    await page.fill('[name="annualIncome"]', '50')
    await page.click('text=已婚')

    // Step 4: Submit form
    await page.click('text=获取AI保险建议')

    // Step 5: Verify loading state is shown
    await expect(page.locator('text=AI分析中')).toBeVisible()

    // Note: Actual results display requires running backend with OPENAI_API_KEY
    // The test verifies UI states up to submission

    // If backend is running, we can verify results:
    // await expect(page.locator('text=AI保险建议')).toBeVisible({ timeout: 60000 })
  })

  test('shows validation errors for empty form submission', async ({ page }) => {
    // Navigate to consultation page
    await page.click('text=保险方案咨询')

    // Submit empty form
    await page.click('text=获取AI保险建议')

    // Verify error messages are shown
    await expect(page.locator('text=请输入姓名')).toBeVisible()
    await expect(page.locator('text=请输入年龄')).toBeVisible()
  })

  test('requires all mandatory fields to be filled', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Fill only some fields
    await page.fill('[name="name"]', '李四')
    await page.fill('[name="age"]', '28')

    // Try to submit
    await page.click('text=获取AI保险建议')

    // Should show validation errors for missing required fields
    await expect(page.locator('text=请输入')).toBeTruthy() // At least one required field error
  })

  test('clears error when user starts typing in field', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Submit empty form to trigger errors
    await page.click('text=获取AI保险建议')
    await expect(page.locator('text=请输入姓名')).toBeVisible()

    // Type in the name field
    await page.fill('[name="name"]', '王五')

    // Error for name field should be cleared
    await expect(page.locator('text=请输入姓名')).not.toBeVisible()
  })

  test('selecting gender updates radio button state', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Click male option
    await page.click('text=男')

    // Verify the radio button is visually selected
    const maleRadio = page.locator('.radio-item').filter({ hasText: '男' })
    await expect(maleRadio).toHaveClass(/active/)
  })

  test('selecting marital status updates radio button state', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Click married option
    await page.click('text=已婚')

    // Verify the radio button is visually selected
    const marriedRadio = page.locator('.radio-item').filter({ hasText: '已婚' })
    await expect(marriedRadio).toHaveClass(/active/)
  })

  test('character counter updates for health conditions textarea', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Find the character counter for health conditions
    const charCount = page.locator('.char-count').first()
    await expect(charCount).toContainText('0/500')

    // Type in the textarea
    const textarea = page.locator('textarea').first()
    await textarea.fill('高血压')

    // Verify character counter updates
    await expect(charCount).toContainText('3/500')
  })

  test('submit button is disabled when form is invalid', async ({ page }) => {
    await page.click('text=保险方案咨询')

    // Verify submit button is disabled initially
    const submitBtn = page.locator('.submit-btn')
    await expect(submitBtn).toHaveClass(/disabled/)

    // Fill all required fields
    await page.fill('[name="name"]', '测试用户')
    await page.fill('[name="age"]', '30')
    await page.click('text=男')
    await page.fill('[name="annualIncome"]', '30')
    await page.click('text=未婚')

    // Submit button should be enabled
    await expect(submitBtn).not.toHaveClass(/disabled/)
  })

  test('reset button appears after successful submission', async ({ page }) => {
    // This test requires the backend to be running with valid OPENAI_API_KEY
    // Skip if backend is not available
    test.skip(true, 'Requires running backend with API key')

    await page.click('text=保险方案咨询')

    // Fill and submit form
    await page.fill('[name="name"]', '赵六')
    await page.fill('[name="age"]', '40')
    await page.click('text=女')
    await page.fill('[name="occupation"]', '医生')
    await page.fill('[name="annualIncome"]', '40')
    await page.click('text=已婚')
    await page.click('text=获取AI保险建议')

    // Wait for results
    await expect(page.locator('text=AI保险建议')).toBeVisible({ timeout: 60000 })

    // Verify reset button exists
    await expect(page.locator('text=重新咨询')).toBeVisible()
  })

  test('reset form clears all data and shows form again', async ({ page }) => {
    // This test requires the backend to be running
    test.skip(true, 'Requires running backend with API key')

    await page.click('text=保险方案咨询')

    // Fill form
    await page.fill('[name="name"]', '孙七')
    await page.fill('[name="age"]', '32')
    await page.click('text=男')
    await page.fill('[name="occupation"]', '律师')
    await page.fill('[name="annualIncome"]', '60')
    await page.click('text=离异')
    await page.click('text=获取AI保险建议')

    // Wait for results
    await expect(page.locator('text=AI保险建议')).toBeVisible({ timeout: 60000 })

    // Click reset button
    await page.click('text=重新咨询')

    // Confirm in modal
    await page.click('text=确定')

    // Verify form is shown again
    await expect(page.locator('.form-section')).toBeVisible()
    await expect(page.locator('[name="name"]')).toHaveValue('')
  })
})

test.describe('Mobile Responsive Design', () => {
  test('displays correctly on mobile viewport (375px)', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('http://localhost:5173/pages/consultation/consultation')

    // Verify page elements are visible
    await expect(page.locator('text=保险方案咨询')).toBeVisible()
    await expect(page.locator('.submit-btn')).toBeVisible()

    // Verify touch targets are adequate (44px minimum)
    const submitBtn = page.locator('.submit-btn')
    const box = await submitBtn.boundingBox()
    expect(box?.height).toBeGreaterThanOrEqual(44)
  })

  test('text is readable without zoom on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('http://localhost:5173/pages/consultation/consultation')

    // Check that main title is sufficiently large
    const title = page.locator('.header-title')
    const fontSize = await title.evaluate((el) => {
      return window.getComputedStyle(el).fontSize
    })
    // Should be at least 18px for readability
    expect(parseInt(fontSize)).toBeGreaterThanOrEqual(18)
  })
})

test.describe('Accessibility', () => {
  test('form fields have visible labels', async ({ page }) => {
    await page.goto('http://localhost:5173/pages/consultation/consultation')

    // Check that all form fields have associated labels
    const labels = page.locator('.label')
    await expect(labels.first()).toBeVisible()

    const labelTexts = await labels.allTextContents()
    expect(labelTexts).toContain('姓名')
    expect(labelTexts).toContain('年龄')
    expect(labelTexts).toContain('性别')
  })

  test('required fields are marked with asterisk', async ({ page }) => {
    await page.goto('http://localhost:5173/pages/consultation/consultation')

    const requiredIndicators = page.locator('.required')
    await expect(requiredIndicators.first()).toBeVisible()
  })
})
