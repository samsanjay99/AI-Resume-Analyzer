# Learning Dashboard - Visual Guide

## User Flow

### Step 1: Resume Analysis Detects Missing Skills
```
┌──────────────────────────────────────────┐
│  📊 Resume Analysis Results              │
│                                          │
│  ATS Score: 75%                          │
│  Format Score: 85%                       │
│                                          │
│  🎯 Missing Skills:                      │
│  • Python                                │
│  • SQL                                   │
│  • Docker                                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ 🎓 Want to learn these skills?     │ │
│  │ We've generated personalized       │ │
│  │ YouTube course recommendations!    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  [📚 View Learning Recommendations]     │
└──────────────────────────────────────────┘
```

### Step 2: Learning Dashboard Overview
```
┌────────────────────────────────────────────────────────┐
│  📚 Learning Dashboard                                 │
│  Personalized YouTube courses based on your skill gaps │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Filter Courses                                        │
│  [All Skills ▼]  [☑ Show Watched]  [☐ Bookmarked]    │
│                                                        │
│  📺 6 Courses Available                                │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Course 1 │  │ Course 2 │  │ Course 3 │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Course 4 │  │ Course 5 │  │ Course 6 │           │
│  └──────────┘  └──────────┘  └──────────┘           │
└────────────────────────────────────────────────────────┘
```

### Step 3: Video Card Design
```
┌─────────────────────────────────────────┐
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │     [YouTube Thumbnail]           │  │
│  │                                   │  │
│  │         ┌──────┐                  │  │
│  │         │  ▶   │  Play Overlay    │  │
│  │         └──────┘                  │  │
│  │                                   │  │
│  │  ⏱ 4:20:44              ★        │  │ ← Duration + Bookmark
│  └───────────────────────────────────┘  │
│                                         │
│  SQL Full Course for Beginners         │ ← Title
│  freeCodeCamp.org                      │ ← Channel
│                                         │
│  [Skill: SQL]                          │ ← Skill Badge
│                                         │
│  [▶ Watch on YouTube]         [★]     │ ← Action Buttons
└─────────────────────────────────────────┘
```

## Visual States

### Hover State
```
┌─────────────────────────────────────────┐
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │     [Thumbnail - Lifted]          │  │ ← Card lifts up
│  │                                   │  │
│  │         ┌──────┐                  │  │
│  │         │  ▶   │  ← Scales up     │  │
│  │         └──────┘                  │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ✨ Green glow shadow ✨               │ ← Glow effect
└─────────────────────────────────────────┘
```

### Bookmarked State
```
┌─────────────────────────────────────────┐
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │     [Thumbnail]                   │  │
│  │                                   │  │
│  │  ⏱ 4:20:44              ★        │  │ ← Gold star (filled)
│  └───────────────────────────────────┘  │
│                                         │
│  Python Full Course                    │
│  Programming with Mosh                 │
│  [Skill: Python]                       │
│                                         │
│  [▶ Watch on YouTube]         [★]     │ ← Gold button
└─────────────────────────────────────────┘
```

### Watched State
```
┌─────────────────────────────────────────┐
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │     [Thumbnail - Dimmed]          │  │ ← Slightly dimmed
│  │                                   │  │
│  │  ⏱ 4:20:44              ☆        │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ✓ JavaScript Full Course              │ ← Checkmark
│  freeCodeCamp.org                      │
│  [Skill: JavaScript]                   │
│                                         │
│  [✓ Watched]                  [☆]     │ ← Different button
└─────────────────────────────────────────┘
```

## Responsive Layouts

### Desktop (3 Columns)
```
┌────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │          │  │          │  │          │            │
│  │ Course 1 │  │ Course 2 │  │ Course 3 │            │
│  │          │  │          │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │          │  │          │  │          │            │
│  │ Course 4 │  │ Course 5 │  │ Course 6 │            │
│  │          │  │          │  │          │            │
│  └──────────┘  └──────────┘  └──────────┘            │
└────────────────────────────────────────────────────────┘
```

### Tablet (2 Columns)
```
┌──────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐     │
│  │          │  │          │     │
│  │ Course 1 │  │ Course 2 │     │
│  │          │  │          │     │
│  └──────────┘  └──────────┘     │
│                                  │
│  ┌──────────┐  ┌──────────┐     │
│  │          │  │          │     │
│  │ Course 3 │  │ Course 4 │     │
│  │          │  │          │     │
│  └──────────┘  └──────────┘     │
└──────────────────────────────────┘
```

### Mobile (1 Column)
```
┌──────────────┐
│  ┌──────────┐│
│  │          ││
│  │ Course 1 ││
│  │          ││
│  └──────────┘│
│              │
│  ┌──────────┐│
│  │          ││
│  │ Course 2 ││
│  │          ││
│  └──────────┘│
│              │
│  ┌──────────┐│
│  │          ││
│  │ Course 3 ││
│  │          ││
│  └──────────┘│
└──────────────┘
```

## Filter States

### All Skills
```
┌────────────────────────────────────┐
│  Filter by Skill: [All Skills ▼]  │
│                                    │
│  Showing: 10 courses               │
│  • 3 Python courses                │
│  • 2 SQL courses                   │
│  • 2 JavaScript courses            │
│  • 1 React course                  │
│  • 1 Docker course                 │
│  • 1 Git course                    │
└────────────────────────────────────┘
```

### Filtered by Python
```
┌────────────────────────────────────┐
│  Filter by Skill: [Python ▼]      │
│                                    │
│  Showing: 3 courses                │
│  • Python Full Course              │
│  • Python for Data Science         │
│  • Advanced Python Programming     │
└────────────────────────────────────┘
```

### Bookmarked Only
```
┌────────────────────────────────────┐
│  [All Skills ▼]  [☑ Bookmarked]   │
│                                    │
│  Showing: 2 bookmarked courses     │
│  ★ Python Full Course              │
│  ★ SQL Full Course                 │
└────────────────────────────────────┘
```

## Empty States

### No Recommendations Yet
```
┌────────────────────────────────────────┐
│                                        │
│              🎓                        │
│                                        │
│    No Course Recommendations Yet      │
│                                        │
│    Complete a resume analysis to get  │
│    personalized learning              │
│    recommendations!                   │
│                                        │
│    [🔍 Go to Resume Analyzer]         │
│                                        │
└────────────────────────────────────────┘
```

### No Matches for Filter
```
┌────────────────────────────────────────┐
│  Filter by Skill: [Kubernetes ▼]      │
│                                        │
│  ℹ️ No courses match your filters     │
│                                        │
│  Try:                                  │
│  • Selecting "All Skills"              │
│  • Unchecking "Bookmarked Only"        │
│  • Completing more resume analyses     │
└────────────────────────────────────────┘
```

## Color Palette

### Primary Colors
```
Background:     #1e1e1e → #2d2d2d (gradient)
Primary:        #4CAF50 (green)
Accent:         #FF0000 (YouTube red)
Text:           #FFFFFF (white)
Subtext:        #AAAAAA (gray)
Border:         rgba(255,255,255,0.1)
```

### State Colors
```
Hover:          rgba(76,175,80,0.3) (green glow)
Bookmark:       #FFD700 (gold)
Watched:        rgba(255,255,255,0.5) (dimmed)
Badge:          rgba(76,175,80,0.2) (light green)
```

## Animation Effects

### Card Hover
```
Before:  translateY(0)
After:   translateY(-8px)
Shadow:  0 12px 24px rgba(76,175,80,0.3)
Time:    0.3s ease
```

### Play Button Hover
```
Before:  scale(1)
After:   scale(1.1)
Color:   rgba(255,0,0,0.9) → rgba(255,0,0,1)
Time:    0.3s ease
```

### Bookmark Toggle
```
Empty:   ☆ (outline)
Filled:  ★ (solid)
Color:   white → gold
Time:    0.3s ease
```

## Navigation Flow

```
Home
  ↓
Resume Analyzer
  ↓
Upload Resume
  ↓
Analysis Complete
  ↓
Missing Skills Detected
  ↓
[View Learning Recommendations] ← Button appears
  ↓
Learning Dashboard
  ↓
Browse Courses
  ↓
[Watch on YouTube] ← Opens new tab
  ↓
YouTube Video
```

## Quick Actions

### From Analysis Results
```
1. Click "View Learning Recommendations"
2. Dashboard opens with personalized courses
3. Courses match detected skill gaps
```

### From Navigation
```
1. Click "🎓 LEARNING" in sidebar
2. Dashboard shows all saved recommendations
3. Filter and browse courses
```

### Watch Course
```
1. Click "▶ Watch on YouTube" button
2. Course marked as watched
3. Opens YouTube in new tab
4. Continue learning!
```

### Bookmark Course
```
1. Click ★ icon on card
2. Star fills with gold color
3. Course saved to bookmarks
4. Filter to see bookmarked only
```

---

**Last Updated**: March 5, 2026
**Status**: Production Ready ✅
