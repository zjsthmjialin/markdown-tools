import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ActionBar from '../components/ActionBar'

describe('ActionBar', () => {
  const defaultProps = {
    outputPath: '/tmp/output',
    onBrowse: vi.fn(),
    onConvert: vi.fn(),
    onCancel: vi.fn(),
    onReset: vi.fn(),
    disabled: false,
    isConverting: false,
    hasCompleted: false
  }

  it('shows convert button when idle', () => {
    render(<ActionBar {...defaultProps} />)
    expect(screen.getByText('开始转换')).toBeInTheDocument()
  })

  it('disables convert button when disabled', () => {
    render(<ActionBar {...defaultProps} disabled={true} />)
    expect(screen.getByText('开始转换')).toBeDisabled()
  })

  it('shows cancel button during conversion', () => {
    render(<ActionBar {...defaultProps} isConverting={true} />)
    expect(screen.getByText('取消')).toBeInTheDocument()
    expect(screen.queryByText('开始转换')).not.toBeInTheDocument()
  })

  it('shows reset button after completion', () => {
    render(<ActionBar {...defaultProps} hasCompleted={true} />)
    expect(screen.getByText('重置')).toBeInTheDocument()
    expect(screen.queryByText('开始转换')).not.toBeInTheDocument()
  })

  it('calls onConvert when convert button clicked', () => {
    const onConvert = vi.fn()
    render(<ActionBar {...defaultProps} onConvert={onConvert} />)
    fireEvent.click(screen.getByText('开始转换'))
    expect(onConvert).toHaveBeenCalled()
  })

  it('calls onCancel when cancel button clicked', () => {
    const onCancel = vi.fn()
    render(<ActionBar {...defaultProps} isConverting={true} onCancel={onCancel} />)
    fireEvent.click(screen.getByText('取消'))
    expect(onCancel).toHaveBeenCalled()
  })

  it('calls onReset when reset button clicked', () => {
    const onReset = vi.fn()
    render(<ActionBar {...defaultProps} hasCompleted={true} onReset={onReset} />)
    fireEvent.click(screen.getByText('重置'))
    expect(onReset).toHaveBeenCalled()
  })
})
