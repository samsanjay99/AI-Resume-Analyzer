# Template Selection UI - Visual Preview

## What Users Will See

### Step 1: Upload Resume
```
┌─────────────────────────────────────────────────────────┐
│  📄 Upload Your Resume                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  🎨 Professional Tech Portfolio               │    │
│  │  Modern, responsive design optimized for      │    │
│  │  developers and tech professionals            │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  [Choose your resume file]  📎                         │
│                                                         │
│  ✅ File uploaded: resume.pdf                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Step 2: Choose Template (NEW!)
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎨 Choose Your Portfolio Style                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Tech Style   │  │ Dark         │  │ Creative     │  │ Professional │  │
│  │              │  │ Developer    │  │ Portfolio    │  │              │  │
│  │ Modern tech  │  │ Sleek dark   │  │ Creative and │  │ Clean        │  │
│  │ portfolio    │  │ theme for    │  │ colorful     │  │ professional │  │
│  │ with dark    │  │ developers   │  │ design       │  │ layout       │  │
│  │ theme        │  │              │  │              │  │              │  │
│  │              │  │              │  │              │  │              │  │
│  │ [✓ Selected] │  │  [ Select ]  │  │  [ Select ]  │  │  [ Select ]  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│   🔵 SELECTED       ⚪ Available      ⚪ Available      ⚪ Available      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Visual States

#### Selected Template Card
```
┌────────────────────────────────────┐
│ 🔵 SELECTED                        │
├────────────────────────────────────┤
│  Background: rgba(0, 212, 255, 0.1)│
│  Border: 2px solid #00d4ff (cyan)  │
│                                    │
│  Tech Style                        │
│  Modern tech portfolio with        │
│  dark theme                        │
│                                    │
│  [✓ Selected] (disabled, primary)  │
└────────────────────────────────────┘
```

#### Unselected Template Card
```
┌────────────────────────────────────┐
│ ⚪ AVAILABLE                       │
├────────────────────────────────────┤
│  Background: rgba(255,255,255,0.05)│
│  Border: 2px solid #333 (gray)     │
│                                    │
│  Dark Developer                    │
│  Sleek dark theme for              │
│  developers                        │
│                                    │
│  [ Select ] (enabled, secondary)   │
└────────────────────────────────────┘
```

### Step 3: Generate Portfolio
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              ┌─────────────────────────┐               │
│              │  🚀 Generate Portfolio  │               │
│              └─────────────────────────┘               │
│                                                         │
│  🔄 Generating your portfolio...                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Step 4: View Result with Template Info (NEW!)
```
┌─────────────────────────────────────────────────────────┐
│  🎯 Your Previously Generated Portfolio                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  🎨 Template: Tech Style                      │    │
│  └───────────────────────────────────────────────┘    │
│  (Purple gradient banner showing selected template)    │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐          │
│  │ 📥 Download      │  │ 🚀 Host Portfolio│          │
│  │ Portfolio (.zip) │  │ Online           │          │
│  └──────────────────┘  └──────────────────┘          │
│                                                         │
│  ┌─────────────────────────────────────────────┐      │
│  │  🖥️ Preview    │    ℹ️ Portfolio Info      │      │
│  ├─────────────────────────────────────────────┤      │
│  │                                             │      │
│  │  [Portfolio preview iframe here]            │      │
│  │                                             │      │
│  └─────────────────────────────────────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Color Scheme

### Selected Template
- **Border**: `#00d4ff` (Bright Cyan)
- **Background**: `rgba(0, 212, 255, 0.1)` (Light Cyan Tint)
- **Button**: Primary (Blue)
- **Text**: `#00d4ff` (Cyan)

### Unselected Template
- **Border**: `#333` (Dark Gray)
- **Background**: `rgba(255, 255, 255, 0.05)` (Subtle White Tint)
- **Button**: Secondary (Gray)
- **Text**: `#b0b0b0` (Light Gray)

### Template Info Banner
- **Background**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` (Purple Gradient)
- **Text**: White
- **Icon**: 🎨

---

## Interaction Flow

### 1. Initial State
- Default template: "Tech Style" is pre-selected
- Session state: `st.session_state.selected_template = 'tech-style'`
- All other templates show "Select" button

### 2. User Clicks "Select" on Different Template
```python
if st.button("Select", key=f"template_{template_key}"):
    st.session_state.selected_template = template_key
    st.rerun()  # Refresh UI to show new selection
```

### 3. Visual Feedback
- Previously selected card: Border changes to gray, button becomes "Select"
- Newly selected card: Border changes to cyan, button becomes "✓ Selected"
- Button is disabled for selected template

### 4. Generation
- Selected template is passed to generator
- Template style stored in result: `result['template_style']`

### 5. Result Display
- Purple banner shows: "🎨 Template: [Template Name]"
- User can see which template was used

---

## Responsive Design

### Desktop (4 Columns)
```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Template│ │Template│ │Template│ │Template│
│   1    │ │   2    │ │   3    │ │   4    │
└────────┘ └────────┘ └────────┘ └────────┘
```

### Tablet (2 Columns)
```
┌────────┐ ┌────────┐
│Template│ │Template│
│   1    │ │   2    │
└────────┘ └────────┘
┌────────┐ ┌────────┐
│Template│ │Template│
│   3    │ │   4    │
└────────┘ └────────┘
```

### Mobile (1 Column)
```
┌────────┐
│Template│
│   1    │
└────────┘
┌────────┐
│Template│
│   2    │
└────────┘
┌────────┐
│Template│
│   3    │
└────────┘
┌────────┐
│Template│
│   4    │
└────────┘
```

---

## Code Implementation

### Template Card Component
```python
for idx, (template_key, template_info) in enumerate(available_templates.items()):
    with template_cols[idx]:
        # Determine if selected
        is_selected = st.session_state.selected_template == template_key
        
        # Set colors based on selection
        border_color = "#00d4ff" if is_selected else "#333"
        bg_color = "rgba(0, 212, 255, 0.1)" if is_selected else "rgba(255, 255, 255, 0.05)"
        
        # Display card
        st.markdown(f"""
        <div style='background: {bg_color}; 
                    padding: 15px; 
                    border-radius: 12px; 
                    border: 2px solid {border_color};
                    text-align: center;'>
            <h4>{template_info['name']}</h4>
            <p>{template_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Selection button
        if st.button(
            "✓ Selected" if is_selected else "Select",
            key=f"template_{template_key}",
            type="primary" if is_selected else "secondary",
            disabled=is_selected
        ):
            st.session_state.selected_template = template_key
            st.rerun()
```

---

## User Experience Benefits

### ✅ Clear Visual Feedback
- Users immediately see which template is selected
- Color coding makes selection obvious
- Disabled button prevents accidental re-selection

### ✅ Easy Comparison
- All 4 templates visible at once
- Short descriptions help users decide
- No need to navigate between pages

### ✅ Persistent Selection
- Selection saved in session state
- Survives page interactions
- Used automatically during generation

### ✅ Template Confirmation
- Purple banner shows which template was used
- Users can verify their choice
- Helps with troubleshooting

---

## Accessibility

### Keyboard Navigation
- All buttons are keyboard accessible
- Tab through template cards
- Enter/Space to select

### Screen Readers
- Template names announced
- Selection state announced
- Button states clear

### Color Contrast
- High contrast between text and background
- Selected state clearly distinguishable
- Meets WCAG AA standards

---

## Testing Checklist

- [ ] All 4 template cards display correctly
- [ ] Default selection (Tech Style) shows as selected
- [ ] Clicking "Select" changes selection
- [ ] Only one template selected at a time
- [ ] Selected template has cyan border
- [ ] Unselected templates have gray border
- [ ] "✓ Selected" button is disabled
- [ ] "Select" buttons are enabled
- [ ] Selection persists during generation
- [ ] Purple banner shows correct template name
- [ ] Responsive layout works on mobile
- [ ] Keyboard navigation works
- [ ] Screen reader announces states

---

## Summary

The template selection UI provides:
- **Visual clarity** - Easy to see which template is selected
- **User control** - Simple one-click selection
- **Feedback** - Immediate visual response
- **Confirmation** - Template name shown in results
- **Accessibility** - Keyboard and screen reader support

Users can now easily choose between 4 professional portfolio templates with a clean, intuitive interface!
