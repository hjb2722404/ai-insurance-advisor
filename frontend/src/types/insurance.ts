/**
 * Insurance Domain Type Definitions
 *
 * This file contains all TypeScript type definitions for the AI Insurance Advisor application.
 * These types mirror the backend Pydantic models to ensure type safety across the frontend.
 *
 * @module types/insurance
 */

/**
 * Gender options for consultation request.
 * Matches backend GenderEnum.
 */
export type Gender = 'male' | 'female' | 'other'

/**
 * Marital status options for consultation request.
 * Matches backend MaritalStatusEnum.
 */
export type MaritalStatus = 'single' | 'married' | 'divorced' | 'widowed'

/**
 * Priority level for insurance recommendations.
 */
export type Priority = 'high' | 'medium' | 'low'

/**
 * Importance level for contract terms.
 */
export type Importance = 'critical' | 'high' | 'medium' | 'low'

/**
 * Consultation request payload.
 * Used when submitting user information for AI insurance recommendations.
 *
 * @example
 * ```typescript
 * const request: ConsultationRequest = {
 *   name: '张三',
 *   age: 35,
 *   gender: 'male',
 *   occupation: '软件工程师',
 *   annual_income: 500000,
 *   marital_status: 'married',
 *   num_dependents: 2,
 *   health_conditions: ['高血压'],
 *   existing_insurance: ['社会保险'],
 *   additional_notes: '希望增加重疾险保障'
 * }
 * ```
 */
export interface ConsultationRequest {
  /** User's full name (1-100 characters) */
  name: string
  /** User's age in years (0-150) */
  age: number
  /** User's gender */
  gender: Gender
  /** User's occupation (1-100 characters) */
  occupation: string
  /** Annual income in local currency (non-negative) */
  annual_income: number
  /** User's marital status */
  marital_status: MaritalStatus
  /** Number of dependents (children, elderly parents, etc.) */
  num_dependents?: number
  /** List of existing health conditions or disabilities */
  health_conditions?: string[]
  /** List of existing insurance policies */
  existing_insurance?: string[]
  /** Any additional information or specific requirements (max 1000 characters) */
  additional_notes?: string
}

/**
 * Single insurance recommendation item.
 * Part of the consultation response.
 */
export interface InsuranceRecommendation {
  /** Type of insurance (e.g., '健康保险', '意外保险', '养老保险', '年金保险') */
  insurance_type: string
  /** Recommended coverage amount or limit */
  recommended_coverage: string
  /** Explanation for why this insurance is recommended */
  reason: string
  /** Priority level */
  priority?: Priority
}

/**
 * Consultation response payload.
 * Received from backend after submitting consultation request.
 */
export interface ConsultationResponse {
  /** Indicates if the consultation was successful */
  success: boolean
  /** List of recommended insurance plans */
  recommendations: InsuranceRecommendation[]
  /** Overall reasoning and explanation for the recommendations */
  reasoning: string
  /** Estimated total annual premium for all recommended plans */
  total_estimated_annual_premium?: string
  /** Suggested next steps for the user */
  next_steps: string[]
}

/**
 * Key term from insurance contract.
 */
export interface ContractTerm {
  /** The term or clause name */
  term: string
  /** Plain-language explanation of the term */
  explanation: string
  /** Importance level */
  importance?: Importance
}

/**
 * Condition for insurance payout.
 */
export interface PayoutCondition {
  /** The payout condition */
  condition: string
  /** Detailed description of when this applies */
  description: string
  /** Documents required to claim this payout */
  required_documents?: string[]
}

/**
 * Detailed payout information.
 */
export interface PayoutDetails {
  /** How the payout is calculated/delivered */
  payout_method: string
  /** Payout amount or calculation method */
  payout_amount: string
  /** Expected timeline for payout */
  payout_timeline: string
  /** Any limitations or exclusions on payouts */
  limitations?: string[]
}

/**
 * Contract interpretation response payload.
 * Received from backend after uploading and analyzing insurance contract PDF.
 */
export interface InterpretationResponse {
  /** Indicates if the interpretation was successful */
  success: boolean
  /** Brief summary of the insurance contract */
  summary: string
  /** Important terms and their explanations */
  key_terms: ContractTerm[]
  /** Conditions that activate the insurance coverage */
  activation_conditions: PayoutCondition[]
  /** Detailed information about payouts */
  payout_details: PayoutDetails
  /** Important notes and warnings about the contract */
  important_notes: string[]
  /** Questions to ask the insurance provider */
  suggested_questions: string[]
}

/**
 * File upload metadata for interpretation.
 */
export interface FileUploadInfo {
  /** File name */
  name: string
  /** File size in bytes */
  size: number
  /** File type (MIME type) */
  type: string
  /** File path or URL (after upload) */
  path?: string
}

/**
 * API error response structure.
 */
export interface ApiErrorResponse {
  /** Error message */
  error: string
  /** Optional error details */
  details?: string
  /** HTTP status code */
  status?: number
}

/**
 * Form data interface used in consultation page.
 * Similar to ConsultationRequest but uses string types for form inputs.
 */
export interface ConsultationFormData {
  name: string
  age: string
  gender: Gender | ''
  occupation: string
  annualIncome: string
  maritalStatus: MaritalStatus | ''
  dependents: string
  healthConditions: string
  existingInsurance: string
}

/**
 * Validation errors record.
 * Maps field names to error messages.
 */
export interface ValidationErrors {
  [key: string]: string
}
