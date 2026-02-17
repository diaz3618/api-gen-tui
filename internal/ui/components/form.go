package components

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// FieldType defines the widget type.
type FieldType int

const (
	TypeTextInput FieldType = iota
	TypeIntInput
	TypeSelect
	TypeToggle
	TypeTextArea
	TypeRange
)

// Field represents a single form element.
type Field struct {
	Type        FieldType
	Label       string
	Key         string   // Identifier for the result map
	Value       any      // Current value (string for Text/Select, bool for Toggle)
	Placeholder string   // For text inputs
	Options     []string // For Select
	HelpText    string   // Optional help text displayed below field
	MinValue    int      // For TypeRange
	MaxValue    int      // For TypeRange

	// Internal models
	textInput textinput.Model
}

func NewTextField(key, label, placeholder, defaultVal string) Field {
	ti := textinput.New()
	ti.Placeholder = placeholder
	ti.SetValue(defaultVal)
	ti.Width = 40
	return Field{Type: TypeTextInput, Key: key, Label: label, Value: defaultVal, Placeholder: placeholder, textInput: ti}
}

func NewTextFieldWithHelp(key, label, placeholder, defaultVal, helpText string) Field {
	f := NewTextField(key, label, placeholder, defaultVal)
	f.HelpText = helpText
	return f
}

func NewIntField(key, label string, defaultVal int) Field {
	ti := textinput.New()
	ti.SetValue(fmt.Sprintf("%d", defaultVal))
	ti.Width = 20
	return Field{Type: TypeIntInput, Key: key, Label: label, Value: defaultVal, textInput: ti}
}

func NewIntFieldWithHelp(key, label string, defaultVal int, helpText string) Field {
	f := NewIntField(key, label, defaultVal)
	f.HelpText = helpText
	return f
}

func NewRangeField(key, label string, minVal, maxVal, defaultVal int) Field {
	ti := textinput.New()
	ti.SetValue(fmt.Sprintf("%d", defaultVal))
	ti.Width = 20
	return Field{
		Type:      TypeRange,
		Key:       key,
		Label:     label,
		Value:     defaultVal,
		MinValue:  minVal,
		MaxValue:  maxVal,
		textInput: ti,
	}
}

func NewSelectField(key, label string, options []string, defaultIdx int) Field {
	val := ""
	if len(options) > defaultIdx {
		val = options[defaultIdx]
	}
	return Field{Type: TypeSelect, Key: key, Label: label, Options: options, Value: val}
}

func NewSelectFieldWithHelp(key, label string, options []string, defaultIdx int, helpText string) Field {
	f := NewSelectField(key, label, options, defaultIdx)
	f.HelpText = helpText
	return f
}

func NewToggleField(key, label string, defaultVal bool) Field {
	return Field{Type: TypeToggle, Key: key, Label: label, Value: defaultVal}
}

func NewToggleFieldWithHelp(key, label string, defaultVal bool, helpText string) Field {
	f := NewToggleField(key, label, defaultVal)
	f.HelpText = helpText
	return f
}

func NewTextArea(key, label, placeholder, defaultVal string) Field {
	ti := textinput.New()
	ti.Placeholder = placeholder
	ti.SetValue(defaultVal)
	ti.Width = 50
	return Field{Type: TypeTextArea, Key: key, Label: label, Value: defaultVal, Placeholder: placeholder, textInput: ti}
}

// FormModel manages a list of fields.
type FormModel struct {
	Fields []Field
	Focus  int
}

func NewForm(fields []Field) FormModel {
	return FormModel{
		Fields: fields,
		Focus:  0,
	}
}

func (m FormModel) Init() tea.Cmd {
	return nil
}

func (m FormModel) Update(msg tea.Msg) (FormModel, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "tab", "down":
			m.Focus = (m.Focus + 1) % (len(m.Fields) + 1) // +1 for Submit button
		case "shift+tab", "up":
			m.Focus--
			if m.Focus < 0 {
				m.Focus = len(m.Fields)
			}
		case "enter":
			if m.Focus == len(m.Fields) {
				return m, func() tea.Msg { return FormSubmittedMsg{Values: m.GetValues()} }
			}
		case " ":
			if m.Focus < len(m.Fields) {
				f := &m.Fields[m.Focus]
				if f.Type == TypeToggle {
					f.Value = !f.Value.(bool)
				} else if f.Type == TypeSelect {
					// Cycle options forward
					curr := f.Value.(string)
					idx := -1
					for i, o := range f.Options {
						if o == curr {
							idx = i
							break
						}
					}
					idx = (idx + 1) % len(f.Options)
					f.Value = f.Options[idx]
				}
			}
		case "right":
			if m.Focus < len(m.Fields) {
				f := &m.Fields[m.Focus]
				if f.Type == TypeSelect {
					// Cycle options forward
					curr := f.Value.(string)
					idx := -1
					for i, o := range f.Options {
						if o == curr {
							idx = i
							break
						}
					}
					idx = (idx + 1) % len(f.Options)
					f.Value = f.Options[idx]
				} else if f.Type == TypeToggle {
					f.Value = true
				}
			}
		case "left":
			if m.Focus < len(m.Fields) {
				f := &m.Fields[m.Focus]
				if f.Type == TypeSelect {
					// Cycle options backward
					curr := f.Value.(string)
					idx := -1
					for i, o := range f.Options {
						if o == curr {
							idx = i
							break
						}
					}
					idx--
					if idx < 0 {
						idx = len(f.Options) - 1
					}
					f.Value = f.Options[idx]
				} else if f.Type == TypeToggle {
					f.Value = false
				}
			}
		}
	}

	// Update text inputs
	if m.Focus < len(m.Fields) {
		f := &m.Fields[m.Focus]
		if f.Type == TypeTextInput || f.Type == TypeIntInput || f.Type == TypeTextArea || f.Type == TypeRange {
			f.textInput.Focus()
			f.textInput, cmd = f.textInput.Update(msg)
			if f.Type == TypeTextInput || f.Type == TypeTextArea {
				f.Value = f.textInput.Value()
			} else if f.Type == TypeRange || f.Type == TypeIntInput {
				// Convert string to int for range/int fields
				strVal := f.textInput.Value()
				if intVal, err := strconv.Atoi(strVal); err == nil {
					f.Value = intVal
				}
			}
		}
	}

	// Blur others
	for i := range m.Fields {
		if i != m.Focus && (m.Fields[i].Type == TypeTextInput ||
			m.Fields[i].Type == TypeIntInput ||
			m.Fields[i].Type == TypeTextArea ||
			m.Fields[i].Type == TypeRange) {
			m.Fields[i].textInput.Blur()
		}
	}

	return m, cmd
}

type FormSubmittedMsg struct {
	Values map[string]any
}

func (m FormModel) GetValues() map[string]any {
	res := make(map[string]any)
	for _, f := range m.Fields {
		res[f.Key] = f.Value
	}
	return res
}

func (m FormModel) View() string {
	var b strings.Builder

	for i, f := range m.Fields {
		// Label
		var labelStyle lipgloss.Style
		if i == m.Focus {
			labelStyle = LabelFocusedStyle
		} else {
			labelStyle = LabelStyle
		}
		b.WriteString(labelStyle.Render(f.Label) + " ")

		// Input
		switch f.Type {
		case TypeTextInput, TypeIntInput, TypeTextArea:
			if i == m.Focus {
				b.WriteString(InputFocusedStyle.Render(f.textInput.View()))
			} else {
				b.WriteString(InputStyle.Render(f.textInput.View()))
			}
		case TypeRange:
			rangeStr := fmt.Sprintf("%s (%d - %d)", f.textInput.View(), f.MinValue, f.MaxValue)
			if i == m.Focus {
				b.WriteString(InputFocusedStyle.Render(rangeStr))
			} else {
				b.WriteString(InputStyle.Render(rangeStr))
			}
		case TypeSelect:
			// Show all options with current selected highlighted
			optStr := ""
			for oi, opt := range f.Options {
				if opt == f.Value.(string) {
					optStr += lipgloss.NewStyle().
						Foreground(ColorPrimary).
						Bold(true).
						Render(fmt.Sprintf("[%s]", opt))
				} else {
					optStr += lipgloss.NewStyle().
						Foreground(ColorMuted).
						Render(opt)
				}
				if oi < len(f.Options)-1 {
					optStr += lipgloss.NewStyle().Foreground(ColorDim).Render(" | ")
				}
			}

			if i == m.Focus {
				hint := lipgloss.NewStyle().
					Foreground(ColorSubtitle).
					Italic(true).
					Render(" ← →")
				b.WriteString(optStr + hint)
			} else {
				b.WriteString(optStr)
			}
		case TypeToggle:
			checkmark := "☐"
			if f.Value.(bool) {
				checkmark = "☑"
			}

			toggleStr := checkmark + " " + f.Label
			if i == m.Focus {
				b.WriteString(InputFocusedStyle.Render(toggleStr))
			} else {
				b.WriteString(InputStyle.Render(toggleStr))
			}
		}

		// Help text
		if f.HelpText != "" {
			helpStyle := lipgloss.NewStyle().
				Foreground(ColorSubtitle).
				Italic(true).
				PaddingLeft(26)
			b.WriteString("\n" + helpStyle.Render("  ↳ "+f.HelpText))
		}

		b.WriteString("\n\n")
	}

	// Submit Button
	var btn string
	if m.Focus == len(m.Fields) {
		btn = ButtonFocusedStyle.Render(" ▶ GENERATE ")
	} else {
		btn = ButtonDimStyle.Render(" ▶ GENERATE ")
	}
	b.WriteString("\n" + btn + "\n")

	return b.String()
}
