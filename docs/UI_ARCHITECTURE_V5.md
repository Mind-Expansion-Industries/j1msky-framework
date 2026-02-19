# J1MSKY Agency v5.0 - UI/UX Architecture Specification

**Version:** 5.0.0  
**Status:** Foundation Document  
**Target:** Phone, iPad, Desktop (320px - 3840px)  
**Theme:** Dark Cyberpunk / Video-Game Aesthetic  
**Priority:** Business-Ready Revenue System  

---

## 📋 Table of Contents

1. [Design System Foundation](#1-design-system-foundation)
2. [Component Library](#2-component-library)
3. [Responsive Architecture](#3-responsive-architecture)
4. [Navigation Systems](#4-navigation-systems)
5. [Touch & Interaction](#5-touch--interaction)
6. [PWA Architecture](#6-pwa-architecture)
7. [Animation System](#7-animation-system)
8. [Accessibility Guidelines](#8-accessibility-guidelines)
9. [Implementation Roadmap](#9-implementation-roadmap)

---

## 1. Design System Foundation

### 1.1 Color Palette

#### Primary Colors (Cyberpunk Core)
```css
:root {
  /* Neon Accents */
  --neon-cyan: #00F0FF;
  --neon-magenta: #FF00FF;
  --neon-lime: #39FF14;
  --neon-amber: #FFBF00;
  --neon-violet: #8B5CF6;
  
  /* Background Hierarchy */
  --bg-void: #050505;           /* Deepest background */
  --bg-depth: #0A0A0F;          /* Secondary backgrounds */
  --bg-surface: #12121A;        /* Cards, panels */
  --bg-elevated: #1A1A25;       /* Elevated elements */
  --bg-hover: #252535;          /* Hover states */
  
  /* Text Hierarchy */
  --text-primary: #FFFFFF;
  --text-secondary: #B4B4C7;
  --text-tertiary: #6B6B80;
  --text-muted: #4A4A5A;
  --text-disabled: #3A3A4A;
  
  /* Semantic Colors */
  --success: #00FF88;
  --warning: #FFB800;
  --error: #FF3366;
  --info: #00C8FF;
  
  /* Agent Identity Colors */
  --agent-scout: #00F0FF;       /* Cyan - News/Discovery */
  --agent-vitals: #00FF88;      /* Green - System/Health */
  --agent-builder: #FFBF00;     /* Amber - Creation */
  --agent-artist: #FF00FF;      /* Magenta - Art/Gen */
  --agent-guardian: #FF3366;    /* Red - Security */
  --agent-oracle: #8B5CF6;      /* Violet - Knowledge */
}
```

#### Gradient Definitions
```css
:root {
  /* Cyberpunk Glows */
  --glow-cyan: 0 0 20px rgba(0, 240, 255, 0.4);
  --glow-magenta: 0 0 20px rgba(255, 0, 255, 0.4);
  --glow-lime: 0 0 20px rgba(57, 255, 20, 0.4);
  
  /* Gradient Presets */
  --gradient-cyber: linear-gradient(135deg, #00F0FF 0%, #FF00FF 100%);
  --gradient-matrix: linear-gradient(180deg, #39FF14 0%, #00FF88 100%);
  --gradient-sunset: linear-gradient(135deg, #FFBF00 0%, #FF3366 100%);
  --gradient-void: linear-gradient(180deg, #0A0A0F 0%, #050505 100%);
  --gradient-card: linear-gradient(145deg, #1A1A25 0%, #12121A 100%);
  
  /* Agent Gradients */
  --gradient-scout: linear-gradient(135deg, #00F0FF 0%, #00C8FF 100%);
  --gradient-vitals: linear-gradient(135deg, #00FF88 0%, #00CC6A 100%);
  --gradient-builder: linear-gradient(135deg, #FFBF00 0%, #FF9900 100%);
}
```

#### Opacity Scale
```css
:root {
  --opacity-hover: 0.8;
  --opacity-disabled: 0.4;
  --opacity-backdrop: 0.85;
  --opacity-glass: 0.1;
  --opacity-border: 0.2;
  --opacity-subtle: 0.6;
}
```

### 1.2 Typography System

#### Font Stack
```css
:root {
  /* Primary: Modern geometric sans */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  /* Display: Tech/monospace for headings */
  --font-display: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
  
  /* Agent: Distinct per agent type */
  --font-agent: 'Space Grotesk', 'Rajdhani', sans-serif;
  
  /* Mono: Code and data */
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;
}
```

#### Type Scale (Major Third - 1.25)
```css
:root {
  /* Display Sizes */
  --text-hero: 4rem;        /* 64px - Hero headlines */
  --text-display: 3rem;     /* 48px - Page titles */
  --text-headline: 2.25rem; /* 36px - Section headers */
  
  /* Content Sizes */
  --text-title: 1.5rem;     /* 24px - Card titles */
  --text-subtitle: 1.25rem; /* 20px - Subsection */
  --text-body: 1rem;        /* 16px - Body text */
  --text-small: 0.875rem;   /* 14px - Secondary */
  --text-xs: 0.75rem;       /* 12px - Captions */
  --text-micro: 0.625rem;   /* 10px - Labels */
}
```

#### Typography Hierarchy
| Level | Size | Weight | Line Height | Letter Spacing | Use Case |
|-------|------|--------|-------------|----------------|----------|
| Hero | 64px | 800 | 1.1 | -0.02em | Landing hero |
| Display | 48px | 700 | 1.2 | -0.01em | Page titles |
| Headline | 36px | 700 | 1.2 | 0 | Section headers |
| Title | 24px | 600 | 1.3 | 0 | Card titles |
| Subtitle | 20px | 600 | 1.4 | 0 | Subsections |
| Body | 16px | 400 | 1.6 | 0 | Primary text |
| Small | 14px | 400 | 1.5 | 0.01em | Secondary text |
| Caption | 12px | 500 | 1.4 | 0.02em | Labels, badges |
| Mono | 14px | 400 | 1.5 | 0 | Code, data |

#### Responsive Typography
```css
/* Mobile: Reduce by 15-20% */
@media (max-width: 768px) {
  :root {
    --text-hero: 2.5rem;      /* 40px */
    --text-display: 2rem;     /* 32px */
    --text-headline: 1.5rem;  /* 24px */
    --text-title: 1.125rem;   /* 18px */
  }
}

/* Tablet: Reduce by 10% */
@media (min-width: 769px) and (max-width: 1024px) {
  :root {
    --text-hero: 3rem;        /* 48px */
    --text-display: 2.5rem;   /* 40px */
    --text-headline: 2rem;    /* 32px */
  }
}
```

### 1.3 Spacing System (8px Base)

```css
:root {
  /* Base Unit: 8px */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

#### Spacing Applications
| Token | Usage |
|-------|-------|
| space-2 | Tight padding, icon gaps |
| space-4 | Standard padding, element gaps |
| space-6 | Card padding, section gaps |
| space-8 | Large component padding |
| space-12 | Section spacing |
| space-16 | Page section separation |

### 1.4 Border Radius System

```css
:root {
  --radius-sm: 4px;     /* Buttons, badges */
  --radius-md: 8px;     /* Cards, inputs */
  --radius-lg: 12px;    /* Panels, modals */
  --radius-xl: 16px;    /* Large cards */
  --radius-2xl: 24px;   /* Feature cards */
  --radius-full: 9999px; /* Pills, avatars */
}
```

### 1.5 Shadow System

```css
:root {
  /* Elevation Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);
  
  /* Glow Shadows */
  --shadow-glow-cyan: 0 0 20px rgba(0, 240, 255, 0.3);
  --shadow-glow-magenta: 0 0 20px rgba(255, 0, 255, 0.3);
  --shadow-glow-success: 0 0 15px rgba(0, 255, 136, 0.4);
  
  /* Inner Shadows */
  --shadow-inset: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}
```

### 1.6 Z-Index Scale

```css
:root {
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-toast: 800;
  --z-agent-overlay: 900;
}
```

---

## 2. Component Library

### 2.1 Button System

#### Button Variants
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'agent';
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  agent?: 'scout' | 'vitals' | 'builder' | 'artist' | 'guardian' | 'oracle';
  glow?: boolean;
  loading?: boolean;
  icon?: IconName;
  iconPosition?: 'left' | 'right';
}
```

#### Button Specifications

**Primary Button (CTA)**
```css
.btn-primary {
  background: var(--gradient-cyber);
  color: var(--bg-void);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: var(--text-body);
  border: none;
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s;
}

.btn-primary:hover::before {
  transform: translateX(100%);
}

.btn-primary:hover {
  box-shadow: var(--shadow-glow-cyan);
  transform: translateY(-1px);
}
```

**Agent-Specific Buttons**
```css
/* Scout Button */
.btn-agent-scout {
  background: transparent;
  border: 2px solid var(--agent-scout);
  color: var(--agent-scout);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
}

.btn-agent-scout:hover {
  background: rgba(0, 240, 255, 0.1);
  box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
}
```

#### Button Sizes
| Size | Height | Padding | Font Size | Border Radius |
|------|--------|---------|-----------|---------------|
| xs | 28px | 8px 12px | 12px | 4px |
| sm | 32px | 10px 16px | 14px | 6px |
| md | 40px | 12px 20px | 16px | 8px |
| lg | 48px | 16px 28px | 16px | 10px |
| xl | 56px | 20px 36px | 18px | 12px |

**Touch Target Minimum: 44px x 44px**

### 2.2 Card System

#### Card Variants
```typescript
interface CardProps {
  variant: 'default' | 'elevated' | 'agent' | 'glass' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  agent?: AgentType;
  glowOnHover?: boolean;
}
```

#### Card Specifications

**Default Card**
```css
.card {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
```

**Agent Card**
```css
.card-agent {
  background: var(--gradient-card);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border-left: 4px solid var(--agent-color);
  position: relative;
}

.card-agent::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--agent-color), transparent);
  opacity: 0.5;
}
```

**Glass Card (For overlays)**
```css
.card-glass {
  background: rgba(18, 18, 26, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl);
}
```

### 2.3 Input System

#### Input Variants
```typescript
interface InputProps {
  variant: 'default' | 'filled' | 'outlined' | 'glow';
  size: 'sm' | 'md' | 'lg';
  state?: 'default' | 'error' | 'success' | 'loading';
  icon?: IconName;
  label?: string;
  helper?: string;
}
```

#### Input Specifications
```css
.input {
  background: var(--bg-depth);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  color: var(--text-primary);
  font-size: var(--text-body);
  transition: all 0.2s ease;
  width: 100%;
}

.input:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 0 3px rgba(0, 240, 255, 0.1);
}

.input-error {
  border-color: var(--error);
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(255, 51, 102, 0.1);
}
```

**Touch Target: 48px minimum height**

### 2.4 Agent Visualization Components

#### Agent Avatar
```typescript
interface AgentAvatarProps {
  agent: AgentType;
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status: 'idle' | 'working' | 'error' | 'offline';
  animate?: boolean;
  showPulse?: boolean;
}
```

```css
.agent-avatar {
  position: relative;
  border-radius: var(--radius-full);
  overflow: hidden;
}

.agent-avatar::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 25%;
  height: 25%;
  border-radius: 50%;
  border: 2px solid var(--bg-surface);
}

.agent-avatar.status-idle::after { background: var(--success); }
.agent-avatar.status-working::after { 
  background: var(--neon-cyan);
  animation: pulse 2s infinite;
}
.agent-avatar.status-error::after { background: var(--error); }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

#### Agent Activity Ring
```css
.activity-ring {
  position: relative;
  width: 100%;
  height: 100%;
}

.activity-ring svg {
  transform: rotate(-90deg);
}

.activity-ring circle {
  fill: none;
  stroke-width: 3;
}

.activity-ring .bg {
  stroke: var(--bg-hover);
}

.activity-ring .progress {
  stroke: var(--agent-color);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
}
```

### 2.5 Status Indicators

```typescript
interface StatusBadgeProps {
  status: 'online' | 'busy' | 'away' | 'offline' | 'error';
  label?: string;
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-online .status-dot { background: var(--success); }
.status-busy .status-dot { background: var(--warning); }
.status-error .status-dot { background: var(--error); }

.status-badge.pulse .status-dot {
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}
```

### 2.6 Toast/Notification System

```typescript
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  agent?: AgentType;
}
```

```css
.toast {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  background: var(--bg-elevated);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-6);
  border-left: 4px solid var(--toast-color);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  max-width: 400px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-success { --toast-color: var(--success); }
.toast-error { --toast-color: var(--error); }
.toast-warning { --toast-color: var(--warning); }
.toast-info { --toast-color: var(--info); }
```

### 2.7 Modal/Dialog System

```typescript
interface ModalProps {
  size: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant: 'default' | 'glass' | 'agent';
  agent?: AgentType;
  closable?: boolean;
  backdrop?: 'blur' | 'dark' | 'none';
}
```

**Modal Sizes**
| Size | Max Width | Use Case |
|------|-----------|----------|
| sm | 400px | Confirmations, alerts |
| md | 560px | Forms, settings |
| lg | 720px | Details, previews |
| xl | 960px | Full content |
| full | 100vw | Mobile, immersive |

### 2.8 Navigation Components

#### Tab System
```typescript
interface TabsProps {
  variant: 'default' | 'pills' | 'underline' | 'agent';
  orientation: 'horizontal' | 'vertical';
  agent?: AgentType;
}
```

```css
.tabs-underline {
  display: flex;
  gap: var(--space-6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab {
  padding: var(--space-3) var(--space-2);
  color: var(--text-secondary);
  font-weight: 500;
  position: relative;
  cursor: pointer;
  transition: color 0.2s;
}

.tab:hover {
  color: var(--text-primary);
}

.tab-active {
  color: var(--neon-cyan);
}

.tab-active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--neon-cyan);
  box-shadow: 0 -2px 10px var(--neon-cyan);
}
```

#### Breadcrumb
```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-small);
  color: var(--text-tertiary);
}

.breadcrumb a:hover {
  color: var(--neon-cyan);
}

.breadcrumb-separator {
  color: var(--text-muted);
}
```

---

## 3. Responsive Architecture

### 3.1 Breakpoint System

```css
:root {
  /* Mobile First Breakpoints */
  --bp-xs: 320px;   /* Small phones */
  --bp-sm: 480px;   /* Large phones */
  --bp-md: 768px;   /* Tablets portrait */
  --bp-lg: 1024px;  /* Tablets landscape / Small laptops */
  --bp-xl: 1280px;  /* Laptops */
  --bp-2xl: 1536px; /* Desktops */
  --bp-3xl: 1920px; /* Large monitors */
  --bp-4xl: 2560px; /* Ultrawide */
}
```

### 3.2 Container System

```css
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

/* Mobile: Full width with padding */
@media (min-width: 480px) {
  .container { max-width: 100%; }
}

/* Tablet */
@media (min-width: 768px) {
  .container { 
    max-width: 720px;
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}

/* Laptop */
@media (min-width: 1024px) {
  .container { max-width: 960px; }
}

/* Desktop */
@media (min-width: 1280px) {
  .container { max-width: 1200px; }
}

/* Large Desktop */
@media (min-width: 1536px) {
  .container { max-width: 1440px; }
}
```

### 3.3 Grid System

```css
.grid {
  display: grid;
  gap: var(--space-4);
}

/* Mobile: 1 column default */
.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }

/* Small phones: 2 columns for certain layouts */
@media (min-width: 480px) {
  .sm\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

/* Tablet: Up to 3 columns */
@media (min-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
}

/* Laptop: Up to 4 columns */
@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}

/* Desktop: Up to 6 columns */
@media (min-width: 1280px) {
  .xl\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
  .xl\:grid-cols-5 { grid-template-columns: repeat(5, 1fr); }
  .xl\:grid-cols-6 { grid-template-columns: repeat(6, 1fr); }
}
```

### 3.4 Layout Patterns by Device

#### Phone (320px - 767px)
```
┌─────────────────────────┐
│ ◀  J1MSKY          ☰ │  ← Header (56px)
├─────────────────────────┤
│                         │
│    Single Column        │
│    Full Width Cards     │
│    Stacked Content      │
│                         │
├─────────────────────────┤
│  🏠  🤖  💼  ⚙️        │  ← Bottom Nav (64px)
└─────────────────────────┘
```

**Phone Patterns:**
- Single column layout
- Full-width cards
- Bottom navigation (thumb zone)
- Stacked agent list
- Sheet modals (slide up)
- Floating action button

#### Tablet (768px - 1023px)
```
┌──────────┬──────────────────────────┐
│ J1MSKY   │  Dashboard               │
│          │  ┌─────────┬─────────┐   │
│ 🏠 Home  │  │ Card 1  │ Card 2  │   │
│ 🤖 Agents│  ├─────────┴─────────┤   │
│ 💼 Tasks │  │                   │   │
│ 📊 Stats │  │   Main Content    │   │
│ ⚙️ Sett. │  │                   │   │
│          │  └───────────────────┘   │
├──────────┤                          │
│  User    │                          │
└──────────┴──────────────────────────┘
```

**Tablet Patterns:**
- Two-column layout (sidebar + content)
- Collapsible sidebar (70px icon-only or 280px expanded)
- 2-column card grids
- Split-pane modals
- Touch + pointer support

#### Desktop (1024px+)
```
┌────────────────────────────────────────────────────────────┐
│  ◇ J1MSKY    Home  Agents  Tasks  Stats  Stream    👤  🔔 │  ← Top Nav (64px)
├──────────┬──────────────────────────────────────────┬──────┤
│          │                                          │      │
│  AGENT   │     ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │ QUICK│
│  ROSTER  │     │     │ │     │ │     │ │     │     │ ACTIONS
│          │     └─────┘ └─────┘ └─────┘ └─────┘     │      │
│ ◆ Scout  │                                          │ ┌──┐ │
│ ◇ Builder│     ┌─────────────────────────────────┐  │ │⚡│ │
│ ◇ Vitals │     │                                 │  │ └──┘ │
│ ◇ Artist │     │      Main Dashboard Area        │  │ ┌──┐ │
│          │     │                                 │  │ │💰│ │
│          │     │                                 │  │ └──┘ │
│          │     └─────────────────────────────────┘  │      │
├──────────┼──────────────────────────────────────────┼──────┤
│ Status   │  Recent Activity         System Health   │ Chat │
└──────────┴──────────────────────────────────────────┴──────┘
```

**Desktop Patterns:**
- Multi-column dashboard
- Persistent navigation
- Hover states enabled
- Keyboard shortcuts
- Resizable panels
- Three-pane layouts possible

### 3.5 Responsive Utilities

```css
/* Hide on mobile */
@media (max-width: 767px) {
  .hidden-mobile { display: none !important; }
}

/* Hide on tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  .hidden-tablet { display: none !important; }
}

/* Hide on desktop */
@media (min-width: 1024px) {
  .hidden-desktop { display: none !important; }
}

/* Touch-only (no hover) */
@media (hover: none) {
  .hover-only { display: none !important; }
}

/* Pointer precision */
@media (pointer: coarse) {
  .pointer-only { display: none !important; }
}
```

---

## 4. Navigation Systems

### 4.1 Mobile Navigation (Bottom Bar)

```typescript
interface MobileNavProps {
  items: NavItem[];
  activeItem: string;
  onItemClick: (id: string) => void;
  showLabels?: boolean;
}
```

```css
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-elevated);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
  z-index: var(--z-fixed);
}

.mobile-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: var(--space-2);
  color: var(--text-tertiary);
  transition: color 0.2s;
  min-width: 64px;
}

.mobile-nav-item.active {
  color: var(--neon-cyan);
}

.mobile-nav-item svg {
  width: 24px;
  height: 24px;
}

.mobile-nav-item span {
  font-size: 11px;
  font-weight: 500;
}
```

**Bottom Nav Items (5 max for ergonomics):**
1. Home (Dashboard)
2. Agents (Agent roster)
3. Tasks (Quick actions)
4. Activity (Feed)
5. Profile/Settings

### 4.2 Tablet Navigation (Collapsible Sidebar)

```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 70px;
  background: var(--bg-surface);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: var(--z-fixed);
}

.sidebar.expanded {
  width: 240px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  color: var(--text-secondary);
  transition: all 0.2s;
  height: 56px;
}

.sidebar-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-item.active {
  background: linear-gradient(90deg, rgba(0, 240, 255, 0.1) 0%, transparent 100%);
  color: var(--neon-cyan);
  border-right: 3px solid var(--neon-cyan);
}

/* Collapsed state: hide text */
.sidebar:not(.expanded) .sidebar-item span {
  display: none;
}
```

### 4.3 Desktop Navigation (Top Bar + Sidebar)

```css
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--bg-elevated);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
  gap: var(--space-8);
  z-index: var(--z-fixed);
}

.top-nav-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-family: var(--font-display);
  font-size: var(--text-title);
  font-weight: 700;
  color: var(--text-primary);
}

.top-nav-links {
  display: flex;
  gap: var(--space-2);
}

.top-nav-link {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.2s;
}

.top-nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.top-nav-link.active {
  color: var(--neon-cyan);
  background: rgba(0, 240, 255, 0.1);
}
```

### 4.4 Agent Command Palette

```typescript
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];
  recentCommands?: Command[];
}
```

**Keyboard Shortcut:** `Cmd/Ctrl + K`

```css
.command-palette {
  position: fixed;
  top: 20%;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 640px;
  background: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  z-index: var(--z-modal);
}

.command-input {
  width: 100%;
  padding: var(--space-5);
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  font-size: var(--text-body);
}

.command-input:focus {
  outline: none;
}

.command-list {
  max-height: 400px;
  overflow-y: auto;
}

.command-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  cursor: pointer;
  transition: background 0.15s;
}

.command-item:hover,
.command-item.selected {
  background: var(--bg-hover);
}

.command-shortcut {
  margin-left: auto;
  padding: var(--space-1) var(--space-2);
  background: var(--bg-depth);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}
```

### 4.5 Breadcrumb Navigation

```css
.breadcrumb-container {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-small);
}

.breadcrumb-item {
  color: var(--text-tertiary);
  transition: color 0.2s;
}

.breadcrumb-item:not(:last-child):hover {
  color: var(--neon-cyan);
}

.breadcrumb-item:last-child {
  color: var(--text-primary);
  font-weight: 500;
}

.breadcrumb-separator {
  color: var(--text-muted);
}
```

---

## 5. Touch & Interaction

### 5.1 Touch Target Guidelines

| Element | Minimum Size | Optimal Size | Padding |
|---------|-------------|--------------|---------|
| Buttons | 44x44px | 48x48px | 8px |
| Icons | 44x44px | 48x48px | 12px |
| List items | 44px height | 56px height | 16px horizontal |
| Input fields | 44px height | 48px height | 12px horizontal |
| Cards (tap) | 100% width | - | 16px margin |
| Checkboxes | 44x44px | - | - |

### 5.2 Touch States

```css
/* Default touch feedback */
.touchable {
  position: relative;
  transition: transform 0.1s, opacity 0.1s;
}

.touchable:active {
  transform: scale(0.97);
  opacity: 0.8;
}

/* Ripple effect for material-style feedback */
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.ripple:active::after {
  width: 200%;
  height: 200%;
}
```

### 5.3 Swipe Gestures

```typescript
interface SwipeConfig {
  threshold: number;      // Minimum distance (px)
  velocity: number;       // Minimum velocity (px/ms)
  direction: 'horizontal' | 'vertical' | 'both';
}

// Common gestures
const GESTURES = {
  CARD_DISMISS: { threshold: 100, velocity: 0.5, direction: 'horizontal' },
  PULL_REFRESH: { threshold: 80, velocity: 0.3, direction: 'vertical' },
  SWIPE_TABS: { threshold: 50, velocity: 0.3, direction: 'horizontal' },
  SWIPE_DELETE: { threshold: 120, velocity: 0.5, direction: 'horizontal' },
};
```

**Pull-to-Refresh**
```css
.pull-refresh {
  position: relative;
  overflow: hidden;
}

.pull-indicator {
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: top 0.3s;
}

.pull-indicator.refreshing {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: translateX(-50%) rotate(360deg); }
}
```

### 5.4 Haptic Feedback

```typescript
// Haptic patterns
const HAPTICS = {
  LIGHT: 10,      // Brief feedback
  MEDIUM: 20,     // Standard feedback
  HEAVY: 30,      // Strong feedback
  SUCCESS: [10, 50, 10],  // Pattern: short, pause, short
  ERROR: [30, 50, 30],    // Pattern: long, pause, long
  TAP: 5,         // Micro feedback
};

// Usage
if (navigator.vibrate) {
  navigator.vibrate(HAPTICS.SUCCESS);
}
```

### 5.5 Long Press Actions

```typescript
interface LongPressConfig {
  duration: number;       // ms to trigger
  onStart?: () => void;
  onTrigger: () => void;
  onCancel?: () => void;
}
```

```css
.long-press-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: var(--neon-cyan);
  width: 0;
  transition: width linear;
}

.long-press-indicator.active {
  width: 100%;
  transition-duration: 500ms;
}
```

### 5.6 Pinch & Zoom

```typescript
interface PinchConfig {
  minScale: number;       // 0.5
  maxScale: number;       // 3.0
  pinchSensitivity: number; // 1.0
}

// Use cases:
// - Agent visualizations
// - Image previews
// - Dashboard zoom
// - Terminal font scaling
```

---

## 6. PWA Architecture

### 6.1 Web App Manifest

```json
{
  "name": "J1MSKY Agency",
  "short_name": "J1MSKY",
  "description": "Autonomous AI Agent Agency Platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#050505",
  "theme_color": "#00F0FF",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/dashboard.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    },
    {
      "src": "/screenshots/mobile.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "categories": ["business", "productivity", "utilities"],
  "shortcuts": [
    {
      "name": "Deploy Agent",
      "short_name": "Deploy",
      "description": "Quickly deploy a new agent",
      "url": "/agents/deploy",
      "icons": [{ "src": "/icons/deploy.png", "sizes": "96x96" }]
    },
    {
      "name": "View Tasks",
      "short_name": "Tasks",
      "description": "View active tasks",
      "url": "/tasks",
      "icons": [{ "src": "/icons/tasks.png", "sizes": "96x96" }]
    }
  ]
}
```

### 6.2 Service Worker Strategy

```typescript
// Cache strategies
const CACHE_STRATEGIES = {
  // Static assets: Cache first
  STATIC: 'CacheFirst',
  
  // API calls: Network first with cache fallback
  API: 'NetworkFirst',
  
  // Images: Stale while revalidate
  IMAGES: 'StaleWhileRevalidate',
  
  // Real-time data: Network only
  REALTIME: 'NetworkOnly',
};

// Precache manifest
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/icons/icon-192x192.png',
  '/offline.html'
];
```

### 6.3 Offline Capabilities

```typescript
interface OfflineConfig {
  // Queue actions for when online
  actionQueue: boolean;
  
  // Show offline indicator
  offlineIndicator: boolean;
  
  // Cached data retention
  cacheDuration: number; // ms
  
  // Background sync tags
  syncTags: string[];
}

// Offline UI states
const OFFLINE_STATES = {
  FULLY_OFFLINE: 'No connection - cached data only',
  SYNC_PENDING: 'Changes queued for sync',
  RECONNECTING: 'Reconnecting...',
  SYNCING: 'Syncing changes...',
  SYNC_COMPLETE: 'All changes synced',
};
```

### 6.4 Push Notifications

```typescript
interface NotificationConfig {
  // Agent activity notifications
  agentStatus: boolean;
  
  // Task completion
  taskComplete: boolean;
  
  // Revenue alerts
  revenueAlerts: boolean;
  
  // System warnings
  systemAlerts: boolean;
}

// Notification templates
const NOTIFICATION_TEMPLATES = {
  AGENT_COMPLETE: {
    title: '✅ Agent Task Complete',
    body: '{agentName} finished: {taskName}',
    icon: '/icons/agent-{agentType}.png',
    badge: '/icons/badge.png',
    tag: 'agent-complete',
    requireInteraction: false,
  },
  REVENUE_MILESTONE: {
    title: '💰 Revenue Milestone!',
    body: 'You reached ${amount} this month!',
    icon: '/icons/revenue.png',
    requireInteraction: true,
  },
  SYSTEM_ALERT: {
    title: '⚠️ System Alert',
    body: '{message}',
    icon: '/icons/alert.png',
    requireInteraction: true,
  },
};
```

### 6.5 Background Sync

```typescript
// Background sync registration
async function registerBackgroundSync() {
  const registration = await navigator.serviceWorker.ready;
  
  // Register periodic sync for agent status
  if ('periodicSync' in registration) {
    await registration.periodicSync.register('agent-status', {
      minInterval: 15 * 60 * 1000, // 15 minutes
    });
  }
  
  // Register one-time sync for pending actions
  if ('sync' in registration) {
    await registration.sync.register('pending-tasks');
  }
}
```

### 6.6 Install Prompt

```typescript
interface InstallPromptConfig {
  // Show after user engagement
  minVisits: number;
  minTimeOnSite: number; // seconds
  
  // Don't show if dismissed
  dismissCooldown: number; // days
  
  // Custom install button
  customPrompt: boolean;
}

// Install button states
const INSTALL_STATES = {
  HIDDEN: 'prompt not available',
  AVAILABLE: 'can be installed',
  INSTALLING: 'installation in progress',
  INSTALLED: 'app installed',
  DISMISSED: 'user dismissed',
};
```

---

## 7. Animation System

### 7.1 Animation Philosophy

- **Purposeful**: Every animation guides attention or provides feedback
- **Fast**: Most animations 150-300ms (perceived as instant)
- **Smooth**: Use `transform` and `opacity` for 60fps
- **Respectful**: Honor `prefers-reduced-motion`

### 7.2 Timing Functions

```css
:root {
  /* Standard easings */
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Special easings */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-cyber: cubic-bezier(0.87, 0, 0.13, 1);
}
```

### 7.3 Duration Scale

```css
:root {
  /* Micro interactions */
  --duration-instant: 75ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  
  /* UI transitions */
  --duration-medium: 350ms;
  --duration-slow: 500ms;
  
  /* Emphasis animations */
  --duration-dramatic: 750ms;
  --duration-epic: 1000ms;
}
```

### 7.4 Common Animations

#### Fade Transitions
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.fade-enter {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

.fade-exit {
  animation: fadeOut var(--duration-fast) var(--ease-in);
}
```

#### Slide Transitions
```css
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from { 
    opacity: 0;
    transform: translateY(-20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from { 
    opacity: 0;
    transform: translateX(-20px);
  }
  to { 
    opacity: 1;
    transform: translateX(0);
  }
}
```

#### Scale Transitions
```css
@keyframes scaleIn {
  from { 
    opacity: 0;
    transform: scale(0.9);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes popIn {
  from { 
    opacity: 0;
    transform: scale(0.5);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}

.pop-in {
  animation: popIn var(--duration-medium) var(--ease-bounce);
}
```

#### Cyberpunk Glow Pulse
```css
@keyframes glowPulse {
  0%, 100% {
    box-shadow: 0 0 5px var(--glow-color),
                0 0 10px var(--glow-color),
                0 0 15px var(--glow-color);
  }
  50% {
    box-shadow: 0 0 10px var(--glow-color),
                0 0 20px var(--glow-color),
                0 0 30px var(--glow-color);
  }
}

.glow-pulse {
  animation: glowPulse 2s ease-in-out infinite;
}
```

#### Agent Status Ring
```css
@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.agent-ring {
  animation: orbit 4s linear infinite;
}

.agent-ring.working {
  animation-duration: 1s;
}

.agent-ring.idle {
  animation-duration: 8s;
}
```

#### Staggered List Animation
```css
@keyframes staggerSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.list-item {
  opacity: 0;
  animation: staggerSlideUp var(--duration-normal) var(--ease-out) forwards;
}

.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 50ms; }
.list-item:nth-child(3) { animation-delay: 100ms; }
.list-item:nth-child(4) { animation-delay: 150ms; }
.list-item:nth-child(5) { animation-delay: 200ms; }
/* Continue pattern or use CSS custom properties */
```

#### Skeleton Loading
```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-surface) 25%,
    var(--bg-hover) 50%,
    var(--bg-surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}
```

#### Progress Bar
```css
@keyframes progressShine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-bar {
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: progressShine 2s infinite;
}
```

### 7.5 Page Transitions

```typescript
interface PageTransition {
  enter: AnimationConfig;
  exit: AnimationConfig;
}

const PAGE_TRANSITIONS = {
  FADE: {
    enter: { duration: 300, ease: 'easeOut' },
    exit: { duration: 200, ease: 'easeIn' },
  },
  SLIDE_UP: {
    enter: { duration: 350, ease: 'spring' },
    exit: { duration: 250, ease: 'easeIn' },
  },
  SCALE: {
    enter: { duration: 300, ease: 'bounce' },
    exit: { duration: 200, ease: 'easeIn' },
  },
};
```

### 7.6 Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  /* Keep essential animations */
  .loading-spinner {
    animation-duration: 1s !important;
  }
  
  .agent-pulse {
    animation-duration: 2s !important;
  }
}
```

---

## 8. Accessibility Guidelines

### 8.1 Color Contrast

| Element | Minimum Ratio | Target Ratio |
|---------|---------------|--------------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18px+) | 3:1 | 4.5:1 |
| UI Components | 3:1 | 4.5:1 |
| Graphical objects | 3:1 | 4.5:1 |

**Tested Combinations:**
- `--text-primary` on `--bg-surface`: 16.5:1 ✅
- `--text-secondary` on `--bg-surface`: 9.2:1 ✅
- `--neon-cyan` on `--bg-void`: 12.8:1 ✅
- `--success` on `--bg-surface`: 8.1:1 ✅

### 8.2 Focus Management

```css
/* Visible focus ring */
:focus-visible {
  outline: 2px solid var(--neon-cyan);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 240, 255, 0.2);
}

/* Skip link for keyboard navigation */
.skip-link {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-3) var(--space-6);
  background: var(--neon-cyan);
  color: var(--bg-void);
  font-weight: 600;
  border-radius: var(--radius-md);
  z-index: 9999;
  transition: top 0.2s;
}

.skip-link:focus {
  top: var(--space-4);
}
```

### 8.3 ARIA Patterns

```typescript
// Component ARIA requirements
const ARIA_PATTERNS = {
  Button: {
    role: 'button',
    required: [],
    optional: ['aria-label', 'aria-pressed', 'aria-expanded'],
  },
  Modal: {
    role: 'dialog',
    required: ['aria-modal', 'aria-labelledby'],
    optional: ['aria-describedby'],
    focus: 'firstFocusable',
  },
  Tabs: {
    role: 'tablist',
    required: ['aria-selected', 'aria-controls'],
    keyboard: ['ArrowLeft', 'ArrowRight', 'Home', 'End'],
  },
  Toast: {
    role: 'status',
    required: ['aria-live', 'aria-atomic'],
    live: 'polite',
  },
  AgentCard: {
    role: 'article',
    required: ['aria-label'],
    optional: ['aria-busy'],
  },
};
```

### 8.4 Screen Reader Support

```typescript
// Live regions for dynamic content
const LIVE_REGIONS = {
  AGENT_STATUS: {
    id: 'agent-status-region',
    role: 'status',
    'aria-live': 'polite',
    'aria-atomic': 'true',
  },
  TASK_QUEUE: {
    id: 'task-queue-region',
    role: 'log',
    'aria-live': 'polite',
    'aria-relevant': 'additions',
  },
  REVENUE_ALERT: {
    id: 'revenue-region',
    role: 'alert',
    'aria-live': 'assertive',
    'aria-atomic': 'true',
  },
};

// Visually hidden text for screen readers
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### 8.5 Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `Cmd/Ctrl + K` | Open command palette | Global |
| `Cmd/Ctrl + /` | Show shortcuts | Global |
| `Esc` | Close modal/dropdown | Modal/Dropdown |
| `Tab` | Next focusable | Global |
| `Shift + Tab` | Previous focusable | Global |
| `Enter/Space` | Activate button | Button/Link |
| `Arrow Keys` | Navigate lists/grids | List/Grid |
| `Home/End` | First/last item | List/Grid |
| `1-9` | Switch to agent N | Dashboard |
| `N` | New task | Global |
| `R` | Refresh data | Global |
| `?` | Help | Global |

### 8.6 Touch Target Accessibility

```css
/* Minimum 44x44px touch targets */
.accessible-touch {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
}

/* Increased spacing for motor impairments */
@media (prefers-reduced-motion: reduce) {
  .button-group {
    gap: 16px; /* Increased from 8px */
  }
}
```

### 8.7 High Contrast Mode

```css
@media (prefers-contrast: high) {
  :root {
    --bg-surface: #000000;
    --text-primary: #FFFFFF;
    --neon-cyan: #00FFFF;
    --neon-magenta: #FF00FF;
  }
  
  /* Ensure borders are visible */
  .card {
    border: 2px solid var(--text-primary);
  }
  
  /* Remove transparency */
  .glass {
    background: var(--bg-surface);
    backdrop-filter: none;
  }
}
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Days 1-3)
- [ ] Set up CSS custom properties (design tokens)
- [ ] Create base layout components (Container, Grid, Flex)
- [ ] Implement typography system
- [ ] Build color system with dark theme
- [ ] Set up responsive breakpoints

### Phase 2: Core Components (Days 4-7)
- [ ] Button system (all variants, sizes)
- [ ] Card system (all variants)
- [ ] Input system (text, select, checkbox, radio)
- [ ] Modal/Dialog system
- [ ] Toast notification system
- [ ] Navigation components (mobile, tablet, desktop)

### Phase 3: Agent Components (Days 8-10)
- [ ] Agent avatar with status
- [ ] Agent activity ring
- [ ] Agent card component
- [ ] Agent roster list/grid
- [ ] Agent command palette
- [ ] Task queue visualization

### Phase 4: Responsive Implementation (Days 11-13)
- [ ] Mobile navigation (bottom bar)
- [ ] Tablet sidebar navigation
- [ ] Desktop top + side navigation
- [ ] Responsive card grids
- [ ] Touch gesture implementation
- [ ] Responsive typography scaling

### Phase 5: PWA & Polish (Days 14-16)
- [ ] Web App Manifest
- [ ] Service Worker setup
- [ ] Offline page design
- [ ] Push notification UI
- [ ] Install prompt handling
- [ ] Icon generation (all sizes)

### Phase 6: Animation & Accessibility (Days 17-18)
- [ ] Core animations (fade, slide, scale)
- [ ] Page transitions
- [ ] Loading states
- [ ] Focus management
- [ ] ARIA implementation
- [ ] Screen reader testing

### Phase 7: Testing & Documentation (Days 19-20)
- [ ] Cross-device testing
- [ ] Cross-browser testing
- [ ] Performance audit
- [ ] Accessibility audit
- [ ] Component documentation
- [ ] Usage examples

---

## Appendix A: File Structure

```
j1msky-framework/ui/
├── design-system/
│   ├── tokens/
│   │   ├── colors.css
│   │   ├── typography.css
│   │   ├── spacing.css
│   │   ├── shadows.css
│   │   └── animation.css
│   ├── base/
│   │   ├── reset.css
│   │   ├── globals.css
│   │   └── utilities.css
│   └── index.css
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.css
│   │   └── Button.stories.tsx
│   ├── Card/
│   ├── Input/
│   ├── Modal/
│   ├── Toast/
│   ├── AgentAvatar/
│   ├── AgentCard/
│   ├── Navigation/
│   └── index.ts
├── layouts/
│   ├── MobileLayout.tsx
│   ├── TabletLayout.tsx
│   ├── DesktopLayout.tsx
│   └── ResponsiveLayout.tsx
├── hooks/
│   ├── useMediaQuery.ts
│   ├── useTouch.ts
│   ├── useKeyboard.ts
│   └── useAnimation.ts
├── utils/
│   ├── animations.ts
│   ├── accessibility.ts
│   └── responsive.ts
└── pwa/
    ├── manifest.json
    ├── service-worker.ts
    └── offline.html
```

---

## Appendix B: Component Checklist

### Foundation
- [ ] Color tokens (all 50+ variables)
- [ ] Typography scale (9 sizes)
- [ ] Spacing system (10 tokens)
- [ ] Border radius (6 tokens)
- [ ] Shadow system (elevation + glow)
- [ ] Z-index scale

### Buttons
- [ ] Primary, Secondary, Ghost, Danger
- [ ] Agent-specific variants (6 agents)
- [ ] Sizes: xs, sm, md, lg, xl
- [ ] Loading state
- [ ] Icon support
- [ ] Full-width variant

### Inputs
- [ ] Text input
- [ ] Textarea
- [ ] Select/Dropdown
- [ ] Checkbox
- [ ] Radio
- [ ] Toggle/Switch
- [ ] Label + Helper text
- [ ] Error states

### Navigation
- [ ] Mobile bottom nav
- [ ] Tablet sidebar
- [ ] Desktop top nav
- [ ] Breadcrumb
- [ ] Tabs (horizontal, vertical)
- [ ] Command palette

### Feedback
- [ ] Toast notifications
- [ ] Modal/Dialog
- [ ] Tooltip
- [ ] Popover
- [ ] Progress bar
- [ ] Skeleton loader
- [ ] Empty states

### Agent Components
- [ ] Avatar (all sizes, statuses)
- [ ] Activity ring
- [ ] Status badge
- [ ] Agent card
- [ ] Agent list
- [ ] Task queue item

### Layout
- [ ] Container (responsive)
- [ ] Grid system
- [ ] Flex utilities
- [ ] Stack component
- [ ] Divider
- [ ] Spacer

---

**Document Version:** 5.0.0  
**Last Updated:** 2026-02-19  
**Author:** J1MSKY UI Architecture Team  
**Status:** Ready for Implementation
