# Example Reports

Real-world examples of design review reports.

---

## Example 1: High-Quality Component (Score: 83.1)

### Component: Button / Lead / Send Message

```markdown
## 🎯 Component Evaluation: Button / Lead / Send Message

### 1️⃣ Style Guide Implementation: **78/100**

**Strengths:**
- ✅ Excellent variants structure (Size × State × Style = 18 variations)
- ✅ Consistent use of CSS Variables for tokens (`--color/azure/48`, `--font-family/font-1`)
- ✅ Clear naming convention (`Size=Full, State=Hover, Style=Primary`)
- ✅ Well-defined TypeScript interface
- ✅ Semantic color system (Azure, Denim, Pale Sky)
- ✅ Consistent typography (Quicksand SemiBold 16/24)

**Weaknesses:**
- ⚠️ `translate-x-[-50%]` on some variants - appears to be an artifact that shouldn't be in production code
- ⚠️ Inconsistency in font-weight (500 vs 600 in some cases)
- ⚠️ Significant code duplication - logic could be consolidated
- ⚠️ Missing Focus states for keyboard accessibility
- ⚠️ Missing Disabled variants for Compact size

---

### 2️⃣ LLM Metadata Accessibility: **95/100** 🌟

**Excellent! Includes:**
- ✅ Detailed component description with use case
- ✅ Searchable tags (`button, cta, lead, homepage, hero, conversion`)
- ✅ Defined `ariaLabel`
- ✅ `testId` for automated testing
- ✅ `analytics` event name
- ✅ `category` and `level` (atom)
- ✅ `priority` (critical)
- ✅ Detailed **Do's and Don'ts**
- ✅ Documented **Design tokens**
- ✅ Linked **Related components**
- ✅ Precise **Specs** (minWidth, minHeight, touchTarget, contrast)
- ✅ Detailed **A11y guidelines**
- ✅ Description for each variant separately

This is one of the most comprehensive component documentations I've seen in Figma.

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **78** | 70% | 54.6 |
| LLM Accessibility | **95** | 30% | 28.5 |
| **Total Weighted** | | | **83.1/100** |

---

### 💡 Recommendations for Improvement:

1. **Remove `translate-x-[-50%]`** - This shouldn't be in production code
2. **Add Focus states** - Essential for keyboard accessibility
3. **Complete Compact/Disabled variants** - For system completeness
4. **Consolidate duplicate code** - Lots of repeating logic that could be centralized

**Overall - excellent work!** Especially the metadata section which is at a very high level and will greatly help any LLM understand the context and generate correct code.
```

---

## Example 2: Needs Improvement (Score: 62.4)

### Component: Card / Product

```markdown
## 🎯 Component Evaluation: Card / Product

### 1️⃣ Style Guide Implementation: **58/100**

**Strengths:**
- ✅ Basic variant structure exists (3 sizes)
- ✅ Some CSS Variables used for primary colors
- ✅ Responsive layout with flexbox

**Weaknesses:**
- ⚠️ **Missing Focus state** - Critical for accessibility
- ⚠️ **Missing Hover state** - No visual feedback on interaction
- ⚠️ **Hardcoded colors** - 60% of colors are hex values
- ⚠️ **Inconsistent padding** - Small: 12px, Medium: 16px, Large: 18px (not on scale)
- ⚠️ **No TypeScript interface** - Props not typed
- ⚠️ **Fixed widths** - Uses px instead of responsive units

---

### 2️⃣ LLM Metadata Accessibility: **72/100**

**Good foundation, missing key elements:**
- ✅ Basic description present
- ✅ Category defined (card)
- ✅ Level defined (molecule)
- ✅ Basic tags present

**Missing:**
- ❌ No `testId` for testing
- ❌ No `ariaLabel` defined
- ❌ No `analytics` event name
- ❌ Do's and Don'ts missing
- ❌ Technical specs incomplete
- ❌ A11y requirements not documented

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **58** | 70% | 40.6 |
| LLM Accessibility | **72** | 30% | 21.6 |
| **Total Weighted** | | | **62.2/100** |

---

### 💡 Recommendations for Improvement:

1. **🔴 CRITICAL: Add Focus state** - Without this, component is not accessible
2. **🔴 CRITICAL: Add Hover state** - Users need interaction feedback
3. **Convert hardcoded colors to tokens** - Consistency and maintainability
4. **Standardize padding to scale** - Use 8px scale (8, 16, 24, not 12, 18)
5. **Add TypeScript interface** - Type safety and documentation
6. **Complete metadata** - Add testId, ariaLabel, do's/don'ts

**Status: ❌ NOT READY FOR EXPORT** - Address critical issues first.
```

---

## Example 3: Excellent Component (Score: 91.2)

### Component: Input / Text Field

```markdown
## 🎯 Component Evaluation: Input / Text Field

### 1️⃣ Style Guide Implementation: **89/100**

**Strengths:**
- ✅ Complete variant matrix (Size × State × Validation = 36 variants)
- ✅ All CSS Variables with semantic naming
- ✅ Full TypeScript interface with JSDoc comments
- ✅ Focus state with clear visible ring
- ✅ Disabled state properly implemented
- ✅ Error/Success validation states
- ✅ Consistent 8px spacing scale
- ✅ Clean, DRY code structure

**Minor Issues:**
- ⚠️ Label positioning slightly inconsistent between sizes
- ⚠️ Helper text could use more contrast

---

### 2️⃣ LLM Metadata Accessibility: **96/100** 🌟

**Exceptional documentation:**
- ✅ Comprehensive description with validation use cases
- ✅ Rich tags: `input, text-field, form, validation, required, email`
- ✅ `testId`: input-text-field
- ✅ `ariaLabel`: Dynamic based on label prop
- ✅ `analytics`: form_field_interaction
- ✅ Complete Do's (5 items) and Don'ts (4 items)
- ✅ All tokens documented
- ✅ Detailed specs including character limits
- ✅ A11y: label association, error announcements, focus management

---

## 📊 Final Weighted Score

| Criterion | Score | Weight | Contribution |
|-----------|-------|--------|--------------|
| Style Guide Implementation | **89** | 70% | 62.3 |
| LLM Accessibility | **96** | 30% | 28.8 |
| **Total Weighted** | | | **91.1/100** |

---

### 💡 Minor Recommendations:

1. **Adjust label positioning** - Ensure consistent vertical alignment
2. **Increase helper text contrast** - Current 3.8:1, target 4.5:1

**Status: ✅ READY FOR EXPORT** - Excellent quality, ship it!
```

---

## Score Distribution Examples

### Grade: 🌟 Excellent (90-100)

```
Implementation: 85-95
LLM: 90-100
Weighted: 90+

Characteristics:
- Complete variants
- All states (including Focus)
- Full token coverage
- Comprehensive metadata
- Detailed specs
```

### Grade: ✅ Good (80-89)

```
Implementation: 75-85
LLM: 80-95
Weighted: 80-89

Characteristics:
- Most variants present
- Key states exist
- Good token usage
- Solid metadata
- Some gaps in specs
```

### Grade: ⚠️ Acceptable (70-79)

```
Implementation: 65-80
LLM: 60-80
Weighted: 70-79

Characteristics:
- Basic variants
- Missing some states
- Partial token usage
- Basic metadata
- Incomplete documentation
```

### Grade: 🔶 Needs Work (60-69)

```
Implementation: 50-70
LLM: 50-70
Weighted: 60-69

Characteristics:
- Incomplete variants
- Missing critical states
- Hardcoded values
- Minimal metadata
- Poor documentation
```

### Grade: ❌ Poor (<60)

```
Implementation: <60
LLM: <60
Weighted: <60

Characteristics:
- Few variants
- No accessibility states
- No tokens
- No metadata
- Not ready for development
```
