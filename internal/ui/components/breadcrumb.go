package components

import (
	"strings"

	"github.com/charmbracelet/lipgloss"
)

type Breadcrumb struct {
	Items []string
}

func NewBreadcrumb(items ...string) Breadcrumb {
	return Breadcrumb{Items: items}
}

func (b Breadcrumb) Render() string {
	if len(b.Items) == 0 {
		return ""
	}

	// SkillsMP-style: $ cd ~/categories/authentication
	promptStyle := lipgloss.NewStyle().Foreground(ColorAccent).Bold(true)
	pathStyle := lipgloss.NewStyle().Foreground(ColorMuted)
	currentStyle := lipgloss.NewStyle().Foreground(ColorPrimary)

	prompt := promptStyle.Render("$") + " "
	command := pathStyle.Render("cd ") + currentStyle.Render("~/")

	parts := make([]string, 0)
	for i, item := range b.Items {
		if i == len(b.Items)-1 {
			parts = append(parts, currentStyle.Render(strings.ToLower(item)))
		} else {
			parts = append(parts, pathStyle.Render(strings.ToLower(item)))
		}
	}

	path := strings.Join(parts, "/")

	return lipgloss.NewStyle().MarginBottom(1).Render(prompt + command + path)
}

func (b *Breadcrumb) Push(item string) {
	b.Items = append(b.Items, item)
}

func (b *Breadcrumb) Pop() {
	if len(b.Items) > 0 {
		b.Items = b.Items[:len(b.Items)-1]
	}
}
