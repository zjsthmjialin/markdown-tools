import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import DropZone from '../components/DropZone'

const mockSelectFiles = vi.fn()
const mockSelectDirectory = vi.fn()
const mockConvertFile = vi.fn()
const mockGetPathForFile = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
  ;(window as any).electronAPI = {
    selectFiles: mockSelectFiles,
    selectDirectory: mockSelectDirectory,
    convertFile: mockConvertFile,
    getPathForFile: mockGetPathForFile
  }
})

describe('DropZone', () => {
  it('renders drop zone text', () => {
    const onFiles = vi.fn()
    const onDialog = vi.fn()
    render(<DropZone onFilesSelected={onFiles} onFilesSelectedViaDialog={onDialog} />)
    expect(screen.getByText('拖放文件到此处')).toBeInTheDocument()
    expect(screen.getByText(/点击选择文件/)).toBeInTheDocument()
  })

  it('calls selectFiles on click', async () => {
    mockSelectFiles.mockResolvedValue([])
    const onFiles = vi.fn()
    const onDialog = vi.fn()
    render(<DropZone onFilesSelected={onFiles} onFilesSelectedViaDialog={onDialog} />)
    fireEvent.click(screen.getByText('拖放文件到此处'))
    expect(mockSelectFiles).toHaveBeenCalled()
  })

  it('calls onFilesSelectedViaDialog with selected files', async () => {
    const selectedFiles = [
      { name: 'test.pdf', path: '/path/test.pdf', size: 1024, extension: '.pdf' }
    ]
    mockSelectFiles.mockResolvedValue(selectedFiles)
    const onFiles = vi.fn()
    const onDialog = vi.fn()
    render(<DropZone onFilesSelected={onFiles} onFilesSelectedViaDialog={onDialog} />)
    fireEvent.click(screen.getByText('拖放文件到此处'))
    await vi.waitFor(() => {
      expect(onDialog).toHaveBeenCalledWith(selectedFiles)
    })
  })

  it('handles drag events', () => {
    const onFiles = vi.fn()
    const onDialog = vi.fn()
    render(<DropZone onFilesSelected={onFiles} onFilesSelectedViaDialog={onDialog} />)
    const zone = screen.getByText('拖放文件到此处').closest('.drop-zone')!
    fireEvent.dragOver(zone, { preventDefault: vi.fn() })
    expect(zone.classList.contains('dragover')).toBe(true)
    fireEvent.dragLeave(zone, { preventDefault: vi.fn() })
    expect(zone.classList.contains('dragover')).toBe(false)
  })
})
