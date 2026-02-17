package components

import "github.com/charmbracelet/lipgloss"

var (
	// SkillsMP-inspired color palette - muted, professional terminal colors
	ColorPrimary    = lipgloss.Color("#7aa2f7") // Soft blue
	ColorSecondary  = lipgloss.Color("#bb9af7") // Soft purple
	ColorAccent     = lipgloss.Color("#73daca") // Soft cyan
	ColorForeground = lipgloss.Color("#c0caf5") // Light blue-white
	ColorBackground = lipgloss.Color("#1a1b26") // Dark blue-black
	ColorMuted      = lipgloss.Color("#565f89") // Muted blue-gray
	ColorDim        = lipgloss.Color("#414868") // Dim blue-gray
	ColorSuccess    = lipgloss.Color("#9ece6a") // Soft green
	ColorError      = lipgloss.Color("#f7768e") // Soft red
	ColorWarning    = lipgloss.Color("#e0af68") // Soft yellow
	ColorInfo       = lipgloss.Color("#7dcfff") // Soft cyan
	ColorBorder     = lipgloss.Color("#3b4261") // Subtle border
	ColorBorderDim  = lipgloss.Color("#24283b") // Very subtle
	ColorTitle      = lipgloss.Color("#7aa2f7") // Soft blue
	ColorSubtitle   = lipgloss.Color("#565f89") // Muted
	ColorSelected   = lipgloss.Color("#bb9af7") // Soft purple
	ColorSelectedBg = lipgloss.Color("#292e42") // Subtle highlight
)

var (
	DocStyle           = lipgloss.NewStyle().Padding(0, 1)
	HeaderStyle        = lipgloss.NewStyle().Bold(true).Foreground(ColorPrimary).BorderStyle(lipgloss.NormalBorder()).BorderBottom(true).BorderForeground(ColorBorder).Padding(0, 1).MarginBottom(1)
	TitleStyle         = lipgloss.NewStyle().Bold(true).Foreground(ColorTitle).MarginRight(2)
	SubtitleStyle      = lipgloss.NewStyle().Foreground(ColorSubtitle).Italic(true)
	PanelStyle         = lipgloss.NewStyle().BorderStyle(lipgloss.RoundedBorder()).BorderForeground(ColorBorder).Padding(1, 2).MarginBottom(1)
	PanelDimStyle      = lipgloss.NewStyle().BorderStyle(lipgloss.RoundedBorder()).BorderForeground(ColorBorderDim).Padding(1, 2).MarginBottom(1)
	ItemStyle          = lipgloss.NewStyle().Foreground(ColorForeground).PaddingLeft(2)
	SelectedItemStyle  = lipgloss.NewStyle().Foreground(ColorSelected).Background(ColorSelectedBg).Bold(true).PaddingLeft(1)
	LabelStyle         = lipgloss.NewStyle().Foreground(ColorMuted).Width(24).Align(lipgloss.Right).MarginRight(2)
	LabelFocusedStyle  = lipgloss.NewStyle().Foreground(ColorPrimary).Bold(true).Width(24).Align(lipgloss.Right).MarginRight(2)
	InputStyle         = lipgloss.NewStyle().Foreground(ColorForeground)
	InputFocusedStyle  = lipgloss.NewStyle().Foreground(ColorPrimary).Bold(true)
	ButtonStyle        = lipgloss.NewStyle().Foreground(ColorBackground).Background(ColorPrimary).Padding(0, 3).Bold(true).MarginTop(1)
	ButtonFocusedStyle = lipgloss.NewStyle().Foreground(ColorBackground).Background(ColorSecondary).Padding(0, 3).Bold(true).MarginTop(1).Underline(true)
	ButtonDimStyle     = lipgloss.NewStyle().Foreground(ColorDim).Border(lipgloss.NormalBorder()).BorderForeground(ColorDim).Padding(0, 3).MarginTop(1)
	ResultPanelStyle   = lipgloss.NewStyle().BorderStyle(lipgloss.DoubleBorder()).BorderForeground(ColorSecondary).Padding(1).MarginTop(1)
	ResultTextStyle    = lipgloss.NewStyle().Foreground(ColorForeground).Background(ColorBackground)
	ErrorStyle         = lipgloss.NewStyle().Foreground(ColorError).Bold(true).Padding(1, 2).Border(lipgloss.RoundedBorder()).BorderForeground(ColorError)
	SuccessStyle       = lipgloss.NewStyle().Foreground(ColorSuccess).Bold(true)
	InfoStyle          = lipgloss.NewStyle().Foreground(ColorInfo).Italic(true)
	HelpStyle          = lipgloss.NewStyle().Foreground(ColorMuted).Italic(true).MarginTop(1)
	KeyStyle           = lipgloss.NewStyle().Foreground(ColorSecondary).Bold(true)
	BadgeStyle         = lipgloss.NewStyle().Foreground(ColorBackground).Background(ColorSecondary).Padding(0, 1).Bold(true).MarginRight(1)
)

func RenderKey(key string) string {
	return KeyStyle.Render("[" + key + "]")
}

func RenderHelp(text string) string {
	return HelpStyle.Render(text)
}
