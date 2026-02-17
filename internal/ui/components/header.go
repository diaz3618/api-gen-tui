package components

import (
	"github.com/charmbracelet/lipgloss"
)

type Header struct {
	Title   string
	Version string
	Width   int
}

func NewHeader(title, version string) Header {
	return Header{Title: title, Version: version}
}

func (h Header) Render() string {
	// SkillsMP-style header with terminal aesthetic
	titleStyle := lipgloss.NewStyle().
		Foreground(ColorPrimary).
		Bold(true)

	versionStyle := lipgloss.NewStyle().
		Foreground(ColorMuted).
		Italic(true)

	subtitleStyle := lipgloss.NewStyle().
		Foreground(ColorSubtitle)

	promptStyle := lipgloss.NewStyle().
		Foreground(ColorAccent).
		Bold(true)

	// Format: random-gen $ v1.0.0
	title := titleStyle.Render(h.Title) + " " + promptStyle.Render("$") + " " + versionStyle.Render("v"+h.Version)
	subtitle := subtitleStyle.Render("// terminal-based random data generator")

	borderStyle := lipgloss.NewStyle().
		BorderBottom(true).
		BorderForeground(ColorBorder).
		PaddingBottom(0).
		MarginBottom(1)

	return borderStyle.Render(title + "\n" + subtitle)
}

func (h *Header) SetWidth(width int) {
	h.Width = width
}
