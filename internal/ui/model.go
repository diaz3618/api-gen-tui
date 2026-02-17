package ui

import (
	"strings"

	"github.com/diaz3618/api-gen-tui/internal/ui/components"

	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type State int

const (
	StateCategoryList State = iota
	StateGeneratorList
	StateForm
)

type MainModel struct {
	state           State
	categoryList    list.Model
	generatorList   list.Model
	activeForm      components.FormModel
	generatedResult string         // Generated content as plain string
	pageView        viewport.Model // Viewport for entire form page
	header          components.Header
	breadcrumb      components.Breadcrumb
	activeCategory  string
	activeGenID     string
	width, height   int
	err             error
}

func NewModel() MainModel {
	// Create custom delegate for better list styling
	delegate := list.NewDefaultDelegate()
	delegate.Styles.SelectedTitle = delegate.Styles.SelectedTitle.
		Foreground(components.ColorSelected).
		Background(components.ColorSelectedBg).
		Bold(true)
	delegate.Styles.SelectedDesc = delegate.Styles.SelectedDesc.
		Foreground(components.ColorMuted).
		Background(components.ColorSelectedBg)

	l := list.New(Categories, delegate, 0, 0)
	l.Title = "$ ls ~/categories"
	l.SetShowHelp(true)
	l.Styles.Title = lipgloss.NewStyle().
		Foreground(components.ColorAccent).
		Bold(true).
		Padding(0, 0, 1, 0)

	pageVp := viewport.New(0, 0)
	header := components.NewHeader("random-gen", "1.0.0")
	breadcrumb := components.NewBreadcrumb("Home")

	return MainModel{
		state:         StateCategoryList,
		categoryList:  l,
		generatorList: list.New([]list.Item{}, delegate, 0, 0),
		pageView:      pageVp,
		header:        header,
		breadcrumb:    breadcrumb,
		width:         80,
		height:        24,
	}
}

func (m MainModel) Init() tea.Cmd {
	return nil
}

func (m MainModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height

		// Update header width
		m.header.SetWidth(m.width)

		// Calculate available space for content
		headerHeight := lipgloss.Height(m.header.Render())
		breadcrumbHeight := lipgloss.Height(m.breadcrumb.Render())
		helpHeight := 3
		contentHeight := m.height - headerHeight - breadcrumbHeight - helpHeight

		m.categoryList.SetSize(m.width-4, contentHeight)
		m.generatorList.SetSize(m.width-4, contentHeight)
		// Page viewport gets ALL available space - it handles all scrolling
		m.pageView.Width = m.width - 4
		m.pageView.Height = contentHeight

	case tea.KeyMsg:
		if msg.String() == "ctrl+c" || msg.String() == "q" {
			return m, tea.Quit
		}
		if msg.String() == "esc" {
			if m.state > StateCategoryList {
				m.state--
				m.err = nil
				m.breadcrumb.Pop()
				return m, nil
			}
			return m, tea.Quit
		}

	case components.FormSubmittedMsg:
		cfg, ok := GeneratorRegistry[m.activeGenID]
		if ok {
			res, err := cfg.Generate(msg.Values)
			if err != nil {
				m.err = err
			} else {
				// Store result as plain string
				m.generatedResult = res
				m.err = nil
			}
		}
	}

	// Update active component based on state
	switch m.state {
	case StateCategoryList:
		return m.updateCategoryList(msg)
	case StateGeneratorList:
		return m.updateGeneratorList(msg)
	case StateForm:
		return m.updateFormState(msg)
	}

	return m, nil
}

func (m MainModel) updateCategoryList(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "enter" {
			i, ok := m.categoryList.SelectedItem().(CategoryItem)
			if ok {
				// Create generator list for this category
				items := []list.Item{}
				for id, cfg := range GeneratorRegistry {
					if cfg.Category == i.ID {
						items = append(items, GeneratorDefinition{
							ID:       id,
							TitleStr: cfg.Title,
							DescStr:  cfg.Description,
						})
					}
				}
				m.generatorList.SetItems(items)
				m.generatorList.Title = "$ ls ./" + strings.ToLower(i.TitleStr)
				m.generatorList.Styles.Title = lipgloss.NewStyle().
					Foreground(components.ColorAccent).
					Bold(true).
					Padding(0, 0, 1, 0)
				m.activeCategory = i.ID
				m.breadcrumb.Push(i.TitleStr)
				m.state = StateGeneratorList
			}
			return m, nil
		}
	}
	var cmd tea.Cmd
	m.categoryList, cmd = m.categoryList.Update(msg)
	return m, cmd
}

func (m MainModel) updateGeneratorList(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		if msg.String() == "enter" {
			i, ok := m.generatorList.SelectedItem().(GeneratorDefinition)
			if ok {
				cfg := GeneratorRegistry[i.ID]
				m.activeGenID = i.ID
				m.activeForm = cfg.BuildForm()
				m.breadcrumb.Push(i.TitleStr)
				m.state = StateForm
				m.generatedResult = ""    // Clear previous result
				m.pageView.SetContent("") // Clear page viewport
				m.pageView.GotoTop()      // Reset scroll
				m.err = nil
			}
			return m, nil
		}
	}
	var cmd tea.Cmd
	m.generatorList, cmd = m.generatorList.Update(msg)
	return m, cmd
}

func (m MainModel) updateFormState(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	// Handle page scrolling with arrow keys
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k":
			// If we're not at the top of the page viewport, scroll up
			if m.pageView.YOffset > 0 {
				m.pageView.LineUp(1)
				return m, nil
			}
			// Otherwise, let form handle navigation
		case "down", "j":
			// If we can scroll down in page viewport, do that
			if m.pageView.YOffset < m.pageView.TotalLineCount()-m.pageView.Height {
				m.pageView.LineDown(1)
				return m, nil
			}
			// Otherwise, let form handle navigation
		case "pgup":
			m.pageView.ViewUp()
			return m, nil
		case "pgdown":
			m.pageView.ViewDown()
			return m, nil
		}
	}

	// Update the form for other keys and navigation within form
	m.activeForm, cmd = m.activeForm.Update(msg)
	return m, cmd
}

func (m MainModel) View() string {
	// Header
	header := m.header.Render()

	// Breadcrumb
	breadcrumb := m.breadcrumb.Render()

	// Main content
	var content string
	switch m.state {
	case StateCategoryList:
		content = m.categoryList.View()
	case StateGeneratorList:
		content = m.generatorList.View()
	case StateForm:
		cfg := GeneratorRegistry[m.activeGenID]

		// SkillsMP-style title with code formatting
		// export const generatePassword = () => { ... }
		titleStyle := lipgloss.NewStyle().
			Foreground(components.ColorAccent).
			Bold(true)

		exportStyle := lipgloss.NewStyle().
			Foreground(components.ColorPrimary)

		descStyle := lipgloss.NewStyle().
			Foreground(components.ColorMuted).
			Italic(true).
			Padding(0, 0, 1, 0)

		title := exportStyle.Render("export ") + titleStyle.Render(cfg.Title)
		desc := descStyle.Render("// " + cfg.Description)

		// Form
		formView := m.activeForm.View()

		// Result or error section
		resultSection := ""
		if m.err != nil {
			errMsg := components.ErrorStyle.Render("❌ error: " + m.err.Error())
			resultSection = "\n" + errMsg
		} else if m.generatedResult != "" {
			resultHeader := lipgloss.NewStyle().
				Foreground(components.ColorSuccess).
				Render("// generated successfully:")

			// Render result directly in a box
			// Width constrained to fit pageView, no height constraint
			resultBox := components.ResultPanelStyle.
				Width(m.pageView.Width - 4).
				Render(m.generatedResult)
			resultSection = "\n\n" + resultHeader + "\n" + resultBox
		}

		// Help text
		helpText := components.RenderHelp(
			components.RenderKey("↑↓/tab") + " navigate  " +
				components.RenderKey("enter") + " generate  " +
				components.RenderKey("↑↓/pgup/pgdn") + " scroll  " +
				components.RenderKey("esc") + " back  " +
				components.RenderKey("q") + " quit",
		)

		// Build full page content
		pageContent := title + "\n" + desc + "\n\n" + formView + resultSection + "\n\n" + helpText

		// Set page viewport content
		m.pageView.SetContent(pageContent)

		// Render the viewport
		content = m.pageView.View()
	}

	// Combine everything
	view := lipgloss.JoinVertical(
		lipgloss.Left,
		header,
		breadcrumb,
		components.DocStyle.Render(content),
	)

	return view
}
