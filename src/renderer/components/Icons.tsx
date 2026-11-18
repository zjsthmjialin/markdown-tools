// 线条图标（替代原来的 emoji，跨系统显示一致）
type IconProps = { size?: number; strokeWidth?: number }

const base = (size: number, strokeWidth: number) => ({
  width: size,
  height: size,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true
})

export const MarkdownIcon = ({ size = 34, strokeWidth = 1.8 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <rect x="2" y="5" width="20" height="14" rx="3" />
    <path d="M6 15V9l3 3 3-3v6" />
    <path d="M17 9v6" />
    <path d="M14.5 12.5L17 15l2.5-2.5" />
  </svg>
)

export const UploadIcon = ({ size = 22, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M12 16V4" />
    <path d="M7 9l5-5 5 5" />
    <path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </svg>
)

export const FileIcon = ({ size = 26, strokeWidth = 1.6 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
    <path d="M14 3v5h5" />
  </svg>
)

export const ArrowRightIcon = ({ size = 22, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M5 12h14" />
    <path d="M13 6l6 6-6 6" />
  </svg>
)

export const CheckIcon = ({ size = 14, strokeWidth = 2.4 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M5 12l5 5 9-10" />
  </svg>
)

export const CloseIcon = ({ size = 12, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
)

export const MinimizeIcon = ({ size = 12, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M5 12h14" />
  </svg>
)

export const MaximizeIcon = ({ size = 12, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <rect x="5" y="5" width="14" height="14" rx="1" />
  </svg>
)

export const FolderIcon = ({ size = 16, strokeWidth = 1.8 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </svg>
)

export const PlayIcon = ({ size = 14, strokeWidth = 2 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <path d="M7 5l12 7-12 7z" />
  </svg>
)

export const InfoIcon = ({ size = 18, strokeWidth = 1.8 }: IconProps) => (
  <svg {...base(size, strokeWidth)}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5" />
    <path d="M12 8h.01" />
  </svg>
)
