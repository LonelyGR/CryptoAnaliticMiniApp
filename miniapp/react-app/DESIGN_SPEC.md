# Copy Trading Home Page - Design Specification

This document provides comprehensive design specifications for the Telegram Mini App Copy Trading Home page, suitable for implementation in Figma or any design tool.

## Design System Overview

### Color Palette

#### Dark Mode (Default)
- **Primary Background**: Linear gradient `#0F172A` → `#1E293B`
- **Card Background**: `#1E293B`
- **Accent Green**: `#00FF9D` (profits, bonuses, CTAs)
- **Accent Gold**: `#FFD700` (ranks, medals)
- **Text Primary**: `#FFFFFF`
- **Text Secondary**: `rgba(255, 255, 255, 0.7)`
- **Text Tertiary**: `rgba(255, 255, 255, 0.5)`
- **Borders**: `rgba(255, 255, 255, 0.1)`
- **Shadows**: `rgba(0, 0, 0, 0.2)` to `rgba(0, 0, 0, 0.5)`

#### Light Mode (Optional)
- **Primary Background**: Linear gradient `#F0F4F8` → `#FFFFFF`
- **Card Background**: `#FFFFFF`
- **Accent Green**: `#00CC7A`
- **Text Primary**: `#000000`
- **Text Secondary**: `rgba(0, 0, 0, 0.7)`

### Typography

- **Font Family**: System fonts (SF Pro for iOS, Roboto for Android)
- **Headings (H1)**: Bold, 18-24pt
- **Headings (H2)**: Bold, 20pt
- **Body Text**: Regular, 14-16pt
- **Small Text**: Regular, 12pt
- **Labels**: Medium, 10-12pt
- **Line Height**: 1.5 for body, 1.2 for headings

### Spacing System

- **Base Unit**: 4px
- **Section Gutter**: 16px
- **Card Padding**: 12-16px
- **Element Gap**: 8-12px
- **Safe Area Top**: 44px (for notch)
- **Safe Area Bottom**: 34px (for home indicator)

### Border Radius

- **Small**: 8px (buttons, badges)
- **Medium**: 12px (cards)
- **Large**: 20px (modals, banners)
- **Full**: 50% (avatars, circular elements)

## Component Specifications

### 1. Header Component

**Dimensions:**
- Height: 56px (fixed)
- Padding: 0 16px
- Background: `#0F172A`
- Border: Bottom 1px `rgba(255, 255, 255, 0.1)`
- Shadow: `0 2px 8px rgba(0, 0, 0, 0.2)`

**Layout:**
- Left: Bitunix logo (🍃) 24px + "×" + CryptoSensei logo (⛩️) 24px
- Center: "Copy Trading Home" text, Bold 18pt
- Right: "Deposit" button, 80px width, 32px height

**Deposit Button:**
- Background: `#00FF9D`
- Text: Black, Bold 14pt
- Border Radius: 16px
- Padding: 0 16px
- Shadow: `0 2px 8px rgba(0, 255, 157, 0.3)`

### 2. Promo Banner Component

**Dimensions:**
- Height: Auto (200-250px typical)
- Margin: 16px (sides), 72px (top for header)
- Border Radius: 20px
- Padding: 20px

**Background:**
- Base: `#000000`
- Gradient: Radial from center, `rgba(0, 255, 157, 0.2)` to transparent
- Border: 1px `rgba(255, 255, 255, 0.1)`

**Content Structure:**
1. **Title**: Bold 16pt, White
2. **Subtitle**: Regular 12pt, `#A0A0A0`
3. **Description**: Regular 14pt, White (green highlight for numbers)
4. **Divider**: 1px `rgba(255, 255, 255, 0.2)`, 16px margin
5. **Bar Chart** (if expanded):
   - Container: Flex row, space-between
   - Bars: Proportional heights (40px to 160px)
   - Bar Color: Linear gradient `#00FF9D` → `#00CC7A`
   - Bar Width: 50px max
   - Glow Effect: `0 0 16px rgba(0, 255, 157, 0.4)`
   - Labels: 10pt below bars
6. **Time Range**: Bold 12pt, `#FFD700`, centered, uppercase
7. **CTA Button**: Full width, 48px height, green gradient

**Bar Chart Tiers:**
- 100 USDT → 20 USDT (smallest)
- 200 USDT → 40 USDT
- 500 USDT → 100 USDT
- 1000 USDT → 200 USDT
- 2000 USDT → 400 USDT (tallest)

### 3. Top Performers Section

**Section Header:**
- Title: Bold 20pt, White, margin-bottom 4px
- Subtitle: Regular 14pt, `rgba(255, 255, 255, 0.7)`
- Margin: 24px 16px (top), 16px (bottom)

**Trader Card:**

**Dimensions:**
- Height: 80-100px (min)
- Padding: 16px
- Border Radius: 12px
- Gap: 12px between elements

**Layout (Left to Right):**
1. **Rank Badge** (Top 3 only):
   - Position: Absolute, top -8px, left 12px
   - Size: 32px × 32px
   - Border: 2px (Gold/Silver/Bronze)
   - Background: `#0F172A`
   - Content: Medal icon + rank number

2. **Avatar:**
   - Size: 48px × 48px
   - Border Radius: 50%
   - Border: 2px `rgba(255, 255, 255, 0.1)`
   - Glow (Top 3): Animated pulse, 2px border

3. **Trader Info:**
   - Name: Bold 16pt, White
   - Rank Badge: 11pt, `rgba(255, 255, 255, 0.1)` background
   - P&L Lines:
     - Label: 12pt, `rgba(255, 255, 255, 0.7)`
     - Value: 13-14pt, `#00FF9D`, Bold
     - Gap: 8px between label and value

4. **Action Button:**
   - Width: 80px min
   - Height: 32px
   - Background: `#FFD700` (default) or `#00FF9D` (following)
   - Text: Black, Bold 13pt
   - Border Radius: 16px

**Top 3 Special Styling:**
- Border: 2px `rgba(255, 215, 0, 0.3)`
- Background: Gradient `#1E293B` → `#2D3748`
- Rank badge with medal icon

### 4. Modal Component

**Overlay:**
- Background: `rgba(0, 0, 0, 0.7)`
- Backdrop Blur: 4px
- Full screen coverage

**Modal Content:**
- Width: 100% (max 400px)
- Max Height: 90vh
- Background: `#1E293B`
- Border Radius: 20px
- Padding: 20px
- Shadow: `0 8px 32px rgba(0, 0, 0, 0.5)`

**Structure:**
1. **Header**: Title (Bold 20pt) + Close button (32px circle)
2. **Body**: Trader summary + Form input + Info text
3. **Footer**: Cancel + Confirm buttons (flex, equal width)

### 5. Bottom Navigation

**Dimensions:**
- Height: 64px
- Position: Fixed, bottom 16px
- Padding: 0 16px
- Background: `#0F172A`
- Border: Top 1px `rgba(255, 255, 255, 0.1)`

**Nav Items:**
- Layout: Flex row, space-around
- Each item: Flex column, center aligned
- Icon: 22px
- Label: 10pt, `rgba(255, 255, 255, 0.7)`
- Active: Icon `#00FF9D`, Label Bold, Green

**Indicator:**
- Size: 56px × 48px
- Position: Absolute, bottom 8px
- Background: `rgba(0, 255, 157, 0.2)`
- Border: 1px `rgba(0, 255, 157, 0.3)`
- Border Radius: 18px
- Transitions between positions

## Interactive States

### Buttons
- **Default**: Full opacity
- **Hover/Tap**: Opacity 0.8, scale 0.95-0.98
- **Disabled**: Opacity 0.5

### Cards
- **Default**: Full opacity
- **Tap**: Scale 0.98, opacity 0.9
- **Top 3**: Additional glow animation

### Animations
- **Fade In**: 0.2s ease
- **Slide Up**: 0.3s ease (modals)
- **Pulse**: 2s infinite (rank glow)
- **Spin**: 1s linear infinite (loading)
- **Glow**: 2s infinite alternate (bars)

## Responsive Breakpoints

- **Small (≤375px)**: Reduced font sizes, tighter spacing
- **Standard (375-414px)**: Default specifications
- **Large (≥414px)**: Slightly increased spacing

## Accessibility

- **Contrast Ratio**: Minimum AA (4.5:1 for text)
- **Touch Targets**: Minimum 44px × 44px
- **Focus States**: Visible outline for keyboard navigation
- **Alt Text**: All images and icons
- **Semantic HTML**: Proper heading hierarchy

## Implementation Notes

1. **Safe Areas**: Use CSS `env(safe-area-inset-*)` for notch/home indicator
2. **Performance**: Use CSS transforms for animations (GPU accelerated)
3. **Telegram Integration**: Adapt to Telegram's theme colors when available
4. **Loading States**: Show skeleton screens or spinners
5. **Error States**: Clear error messages with retry options
6. **Empty States**: Helpful messages when no data available

## Figma Setup Recommendations

1. **Frames**: Create device frames (iPhone 14, Samsung S23)
2. **Auto Layout**: Use for all components (responsive)
3. **Components**: Create reusable components for cards, buttons, etc.
4. **Variants**: Create dark/light mode variants
5. **Prototyping**: Link interactions (taps, swipes, modals)
6. **Design Tokens**: Use variables for colors, spacing, typography
7. **Constraints**: Set proper constraints for responsive behavior

