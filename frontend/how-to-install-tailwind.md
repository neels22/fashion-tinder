# How to Install Tailwind CSS (NativeWind) in Expo React Native

## 📋 Project Context

**Project Setup:**
- Framework: Expo SDK 54
- React Native: 0.81.5
- React: 19.1.0
- Package Manager: Bun
- TypeScript: Yes
- Router: Expo Router (app directory structure)

**Goal:** Add Tailwind CSS styling to a React Native Expo project using NativeWind v4.

---

## 🚀 Installation Journey

### Phase 1: Initial Assessment

Before installation, we verified:
- ✅ Expo project structure with `app/` directory (Expo Router)
- ✅ Existing dependencies already included `react-native-reanimated` and `react-native-safe-area-context`
- ✅ No existing `babel.config.js` (Expo manages Babel by default)
- ✅ No Tailwind configuration

**Initial Assumption (WRONG):** "Expo doesn't need Babel config, just install NativeWind and it'll work"

---

### Phase 2: Package Installation

#### Step 1: Install NativeWind
```bash
bun add nativewind
```

**Result:** ✅ Installed `nativewind@4.2.1`

**Warning Appeared:**
```
warn: incorrect peer dependency "tailwindcss@4.1.18"
```

This was our first clue that version compatibility would be an issue.

---

#### Step 2: Install Tailwind CSS (First Attempt - FAILED)
```bash
bun add --dev tailwindcss
```

**Result:** ❌ Installed `tailwindcss@4.1.18`

**Problem:** Bun installed the latest version (v4.x) by default, but NativeWind v4 only supports Tailwind CSS v3.x.

**Attempted Commands (All Failed):**
```bash
bunx tailwind init        # Error: could not determine executable
bunx tailwindcss init     # Error: could not determine executable
bun run tailwindcss init  # Error: Script not found
```

**Root Cause:** Tailwind CSS v4 has a different architecture and doesn't package CLI binaries the same way as v3.

---

#### Step 3: Fix Tailwind Version (SUCCESS)
```bash
# Remove wrong version
bun remove tailwindcss

# Install correct version
bun add --dev tailwindcss@3
```

**Result:** ✅ Installed `tailwindcss@3.4.19`

**Success Indicator:**
```
installed tailwindcss@3.4.19 with binaries:
 - tailwind
 - tailwindcss
```

Now the CLI tools were available!

---

#### Step 4: Initialize Tailwind Config
```bash
npx tailwindcss init
```

**Result:** ✅ `Created Tailwind CSS config file: tailwind.config.js`

**Key Lesson:** Use `npx` (not `bunx`) for running package binaries - it's more reliable.

---

### Phase 3: Configuration (Multiple Iterations Required)

#### Attempt 1: Basic Tailwind Config (INCOMPLETE)

**Created `tailwind.config.js`:**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Problem:** Missing NativeWind preset (discovered later).

---

#### Attempt 2: Babel Config (WRONG STRUCTURE)

**Created `babel.config.js`:**
```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: ['nativewind/babel'],  // ❌ WRONG LOCATION
  };
};
```

**Result:** Server started, but got error:
```
ERROR: [BABEL] .plugins is not a valid Plugin property
```

**Root Cause:** For NativeWind v4, `nativewind/babel` must be in `presets` array, NOT `plugins` array.

---

#### Attempt 3: Fix Babel Config (PARTIAL SUCCESS)

**Corrected `babel.config.js`:**
```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",  // ✅ Moved to presets
    ],
    plugins: [
      "react-native-reanimated/plugin",  // ✅ Added
    ],
  };
};
```

**Why This Works:**
- NativeWind v4 requires its transformer as a preset, not a plugin
- The `jsxImportSource` option tells Babel to handle JSX properly
- Reanimated plugin must be in plugins array (and should be last)

---

#### Issue: React Native Reanimated Version Mismatch

**Warning:**
```
react-native-reanimated@4.2.1 - expected version: ~4.1.1
Your project may not work correctly
```

**Solution:**
```bash
bun remove react-native-reanimated
bun add react-native-reanimated@~4.1.1
```

**Result:** ✅ Installed `react-native-reanimated@4.1.6` (compatible with Expo SDK 54)

---

#### Attempt 4: TypeScript Configuration

**Created `nativewind-env.d.ts`:**
```typescript
/// <reference types="nativewind/types" />
```

**Updated `tsconfig.json`:**
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "paths": {
      "@/*": ["./"]
    }
  },
  "include": [
    "**/*.ts",
    "**/*.tsx",
    ".expo/types/**/*.ts",
    "expo-env.d.ts",
    "nativewind-env.d.ts"  // ✅ Added this line
  ]
}
```

**Why Needed:** Provides TypeScript intellisense for `className` prop on React Native components.

---

### Phase 4: The Metro Config Mystery

#### Problem: Styles Not Applying

After all configuration, server ran without errors, but styles weren't applying to components.

**Added Verification Code:**
```typescript
import { verifyInstallation } from 'nativewind';

export default function Index() {
  verifyInstallation();
  // ...
}
```

**Result:** Error appeared:
```
ERROR: Your 'metro.config.js' has overridden the 'config.resolver.resolveRequest' 
config setting in a non-composable manner. Your styles will not work until this 
issue is resolved.
```

**Discovery:** We were missing `metro.config.js` entirely!

---

#### Solution: Create Metro Config

**Created `metro.config.js`:**
```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

**Why Needed:** NativeWind v4 requires custom Metro configuration to process CSS files and transform className props.

---

#### Problem: Missing CSS File

**Error:**
```
Tailwind CSS has not been configured with the NativeWind preset
```

**Solution 1: Create `global.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Solution 2: Import in `app/_layout.tsx`:**
```typescript
import { Stack } from "expo-router";
import "../global.css";  // ✅ Added this line

export default function RootLayout() {
  return <Stack />;
}
```

---

#### Problem: Missing NativeWind Preset in Tailwind Config

**Error (again):**
```
Tailwind CSS has not been configured with the NativeWind preset
```

**Final Fix to `tailwind.config.js`:**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  presets: [require("nativewind/preset")],  // ✅ Added this line!
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Why Critical:** The NativeWind preset configures Tailwind to work with React Native's styling system.

---

### Phase 5: Success!

**Final Restart:**
```bash
npx expo start --clear
```

**Console Output:**
```
✅ LOG  NativeWind verifyInstallation() found no errors
```

**Visual Confirmation:**
Testing with obvious styles:
```typescript
<View className="bg-blue-500 p-4 rounded-lg mb-4">
  <Text className="text-3xl font-bold text-white">Hello!</Text>
  <Text className="text-sm text-yellow-300 mt-2">NativeWind working!</Text>
</View>
```

Result: Blue box with white and yellow text appeared! 🎉

---

## 🎯 The Correct Installation Process

Here's the complete, correct process without the trial-and-error:

### Step 1: Install Dependencies

```bash
cd frontend
bun add nativewind
bun add --dev tailwindcss@3
bun add react-native-reanimated@~4.1.1
```

**Important:** 
- Use Tailwind CSS v3, NOT v4
- Match Reanimated version to your Expo SDK

---

### Step 2: Initialize Tailwind

```bash
npx tailwindcss init
```

---

### Step 3: Configure Tailwind with NativeWind Preset

**Update `tailwind.config.js`:**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  presets: [require("nativewind/preset")],  // ⚠️ CRITICAL
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

### Step 4: Create Babel Configuration

**Create `babel.config.js`:**

```javascript
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",  // ⚠️ Must be in presets, not plugins
    ],
    plugins: [
      "react-native-reanimated/plugin",
    ],
  };
};
```

---

### Step 5: Create Metro Configuration

**Create `metro.config.js`:**

```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

---

### Step 6: Create Global CSS

**Create `global.css`:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

### Step 7: Import Global CSS

**Update `app/_layout.tsx`:**

```typescript
import { Stack } from "expo-router";
import "../global.css";  // ⚠️ Add this import

export default function RootLayout() {
  return <Stack />;
}
```

---

### Step 8: Add TypeScript Support

**Create `nativewind-env.d.ts`:**

```typescript
/// <reference types="nativewind/types" />
```

**Update `tsconfig.json`:**

```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "paths": {
      "@/*": ["./"]
    }
  },
  "include": [
    "**/*.ts",
    "**/*.tsx",
    ".expo/types/**/*.ts",
    "expo-env.d.ts",
    "nativewind-env.d.ts"  // ⚠️ Add this line
  ]
}
```

---

### Step 9: Clear Cache and Start

```bash
npx expo start --clear
```

**Note:** The `--clear` flag is essential after configuration changes to clear Metro bundler cache.

---

### Step 10: Test Your Installation

Add this temporarily to verify:

```typescript
import { verifyInstallation } from 'nativewind';

export default function Index() {
  verifyInstallation();  // Will log to console
  
  return (
    <View className="flex-1 justify-center items-center bg-white">
      <View className="bg-blue-500 p-4 rounded-lg">
        <Text className="text-white font-bold text-xl">
          NativeWind is working!
        </Text>
      </View>
    </View>
  );
}
```

**Success Indicators:**
- Console shows: `NativeWind verifyInstallation() found no errors`
- Blue box with white text appears on screen
- No Babel errors in terminal

---

## 📊 Files Created/Modified Summary

| File | Action | Purpose |
|------|--------|---------|
| `tailwind.config.js` | Created | Configure Tailwind with NativeWind preset |
| `babel.config.js` | Created | Enable NativeWind Babel transformations |
| `metro.config.js` | Created | Integrate NativeWind with Metro bundler |
| `global.css` | Created | Tailwind CSS directives |
| `nativewind-env.d.ts` | Created | TypeScript type definitions |
| `app/_layout.tsx` | Modified | Import global CSS |
| `tsconfig.json` | Modified | Include NativeWind types |
| `package.json` | Modified | Install dependencies |

---

## 🔑 Key Lessons Learned

### 1. Version Compatibility is Critical

| Package | Version | Why This Version? |
|---------|---------|-------------------|
| `nativewind` | `^4.2.1` | Latest stable for NativeWind v4 |
| `tailwindcss` | `3.4.19` | NativeWind v4 requires Tailwind v3, NOT v4 |
| `react-native-reanimated` | `~4.1.1` | Must match Expo SDK 54 compatibility |

**Lesson:** Always check peer dependencies and Expo SDK compatibility charts.

---

### 2. NativeWind v4 Configuration Differs from v2

| Aspect | NativeWind v2 | NativeWind v4 |
|--------|---------------|---------------|
| Babel | Plugin in `plugins` array | Preset in `presets` array |
| Metro Config | Not required | **Required** with `withNativeWind` |
| Global CSS | Not required | **Required** |
| Tailwind Preset | Not mentioned | **Required** in tailwind.config.js |

**Lesson:** Documentation online might be for v2 - always verify version-specific requirements.

---

### 3. Babel Configuration Structure Matters

❌ **Wrong:**
```javascript
plugins: ['nativewind/babel']
```

✅ **Correct:**
```javascript
presets: [
  ["babel-preset-expo", { jsxImportSource: "nativewind" }],
  "nativewind/babel"
]
```

**Lesson:** NativeWind's transformer is a preset, not a plugin. The distinction is important for how Babel processes the code.

---

### 4. Cache Clearing is Essential

**When to clear cache:**
- After creating/modifying `babel.config.js`
- After creating/modifying `metro.config.js`
- After installing new dependencies
- When styles aren't applying

**Command:**
```bash
npx expo start --clear
```

**Lesson:** Metro bundler aggressively caches configurations. Always use `--clear` flag after config changes.

---

### 5. Package Manager Differences

| Operation | npm | bun | Note |
|-----------|-----|-----|------|
| Install specific version | `npm install pkg@version` | `bun add pkg@version` | Same syntax |
| Run package binary | `npx command` | `bunx command` | `npx` more reliable for some tools |
| Install dependencies | `npm install` | `bun install` | Bun is faster |

**Lesson:** Use `npx` for running CLI tools (like `tailwindcss init`), even if using Bun as package manager.

---

## ❌ Common Errors and Solutions

### Error 1: "could not determine executable"

**Error:**
```
bunx tailwindcss init
error: could not determine executable to run for package tailwindcss
```

**Cause:** Tailwind CSS v4 installed instead of v3, or package not installed yet.

**Solution:**
```bash
bun remove tailwindcss
bun add --dev tailwindcss@3
npx tailwindcss init  # Use npx, not bunx
```

---

### Error 2: ".plugins is not a valid Plugin property"

**Error:**
```
[BABEL] .plugins is not a valid Plugin property
```

**Cause:** `nativewind/babel` in wrong location (plugins instead of presets).

**Solution:**
Move to presets array:
```javascript
presets: [
  ["babel-preset-expo", { jsxImportSource: "nativewind" }],
  "nativewind/babel"
]
```

---

### Error 3: "metro.config.js has overridden config.resolver.resolveRequest"

**Error:**
```
Your 'metro.config.js' has overridden the 'config.resolver.resolveRequest' 
config setting in a non-composable manner
```

**Cause:** Either missing `metro.config.js` or not using `withNativeWind` wrapper.

**Solution:**
Create proper metro.config.js with `withNativeWind`:
```javascript
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);
module.exports = withNativeWind(config, { input: './global.css' });
```

---

### Error 4: "Tailwind CSS has not been configured with the NativeWind preset"

**Error:**
```
Tailwind CSS has not been configured with the NativeWind preset
```

**Cause:** Missing `presets: [require("nativewind/preset")]` in tailwind.config.js.

**Solution:**
Add to tailwind.config.js:
```javascript
module.exports = {
  presets: [require("nativewind/preset")],  // Add this
  content: [...],
  // ...
}
```

---

### Error 5: Styles Not Applying (No Error)

**Symptom:** Server runs fine, no errors, but className styles don't show.

**Common Causes:**
1. Forgot to import `global.css` in `_layout.tsx`
2. TypeScript not configured (missing nativewind-env.d.ts)
3. Metro cache not cleared
4. App not reloaded on device

**Solution Checklist:**
```typescript
// 1. Check _layout.tsx has import
import "../global.css";

// 2. Verify tsconfig.json includes
"include": ["nativewind-env.d.ts"]

// 3. Clear cache and restart
npx expo start --clear

// 4. On device: shake and press "Reload"
```

---

## 🧪 Verification Checklist

Use this checklist to verify your installation:

- [ ] **Packages Installed:**
  - [ ] `nativewind@^4.2.1`
  - [ ] `tailwindcss@3.x.x` (NOT v4)
  - [ ] `react-native-reanimated` (version matches Expo SDK)

- [ ] **Files Created:**
  - [ ] `tailwind.config.js` with NativeWind preset
  - [ ] `babel.config.js` with nativewind/babel in presets
  - [ ] `metro.config.js` with withNativeWind wrapper
  - [ ] `global.css` with @tailwind directives
  - [ ] `nativewind-env.d.ts` with type reference

- [ ] **Files Modified:**
  - [ ] `app/_layout.tsx` imports global.css
  - [ ] `tsconfig.json` includes nativewind-env.d.ts

- [ ] **Testing:**
  - [ ] Server starts without errors
  - [ ] `verifyInstallation()` logs no errors
  - [ ] Test styles (blue box) visible on device
  - [ ] No Babel or Metro errors in console

---

## 📱 Usage Examples

### Basic Styling

```typescript
// Before (StyleSheet)
<View style={styles.container}>
  <Text style={styles.title}>Hello</Text>
</View>

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});

// After (NativeWind)
<View className="flex-1 bg-white p-4">
  <Text className="text-2xl font-bold">Hello</Text>
</View>
```

---

### Responsive Design

```typescript
<View className="p-4 sm:p-6 md:p-8">
  <Text className="text-lg sm:text-xl md:text-2xl">
    Responsive Text
  </Text>
</View>
```

---

### Dark Mode

```typescript
<View className="bg-white dark:bg-gray-900">
  <Text className="text-black dark:text-white">
    Auto dark mode
  </Text>
</View>
```

---

### Custom Colors

Update `tailwind.config.js`:
```javascript
module.exports = {
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
      }
    },
  },
}
```

Use in components:
```typescript
<View className="bg-primary">
  <Text className="text-secondary">Custom colors!</Text>
</View>
```

---

## 🔄 Migration Strategy

If you have an existing app with StyleSheet:

### Gradual Migration Approach

1. **Don't Remove StyleSheet Immediately**
   ```typescript
   // Both can coexist
   <View style={styles.container} className="mt-4">
   ```

2. **Start with New Components**
   - Use NativeWind for all new components
   - Refactor old components gradually

3. **Prioritize Common Patterns**
   - Spacing: `m-4, p-2, mt-1`
   - Flex: `flex-1, flex-row, justify-center`
   - Text: `text-lg, font-bold, text-gray-600`

4. **Test Thoroughly**
   - Test on both iOS and Android
   - Check dark mode if applicable
   - Verify responsive breakpoints

---

## 🐛 Troubleshooting Guide

### Styles Not Showing

**Check 1: Babel Config**
```bash
# Restart with clear cache
npx expo start --clear
```

**Check 2: Metro Config**
```javascript
// Verify metro.config.js exists and uses withNativeWind
module.exports = withNativeWind(config, { input: './global.css' });
```

**Check 3: Global CSS Import**
```typescript
// app/_layout.tsx must have:
import "../global.css";
```

**Check 4: Device Cache**
- Shake device → "Reload"
- Or close Expo Go completely and reopen

---

### TypeScript Errors

**Error:** `Property 'className' does not exist on type...`

**Solution:**
1. Verify `nativewind-env.d.ts` exists
2. Check `tsconfig.json` includes it
3. Restart TypeScript server in IDE
4. Rebuild: `npx expo start --clear`

---

### Build Errors

**For iOS:**
```bash
cd ios
pod install
cd ..
npx expo run:ios
```

**For Android:**
```bash
npx expo run:android
```

---

## 📚 Additional Resources

### Official Documentation
- [NativeWind v4 Docs](https://www.nativewind.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [Tailwind CSS v3 Docs](https://v3.tailwindcss.com/)

### Version Compatibility
- [Expo SDK Compatibility](https://docs.expo.dev/versions/latest/)
- [React Native Reanimated Compatibility](https://docs.swmansion.com/react-native-reanimated/)

### Community
- [NativeWind GitHub Issues](https://github.com/nativewind/nativewind/issues)
- [Expo Forums](https://forums.expo.dev/)

---

## 🎓 Final Notes

### What We Got Wrong Initially

1. **Babel not needed for Expo** → WRONG for NativeWind
2. **Just install and it works** → WRONG, needs 6+ config files
3. **Latest Tailwind is fine** → WRONG, needs v3 specifically
4. **Metro config optional** → WRONG, absolutely required for v4
5. **Tailwind preset optional** → WRONG, critical for NativeWind

### What's Actually Required

NativeWind v4 is more complex than v2 but more powerful:
- Requires custom Babel, Metro, and Tailwind configs
- Needs global CSS file (like web development)
- Requires specific version combinations
- Must clear cache after config changes

### Time Investment

- Initial installation (knowing the right way): **~10 minutes**
- Troubleshooting without guide (our experience): **~2 hours**
- Learning to use effectively: **Ongoing**

### Worth It?

**Yes!** Because:
- ✅ Faster development (no StyleSheet boilerplate)
- ✅ Consistent design system
- ✅ Responsive design built-in
- ✅ Dark mode support
- ✅ Familiar syntax (if you know Tailwind)
- ✅ Easier to maintain

---

## ✅ Quick Reference

**Install Command:**
```bash
bun add nativewind && bun add --dev tailwindcss@3 && npx tailwindcss init
```

**Required Files:**
1. `babel.config.js` - NativeWind preset
2. `metro.config.js` - withNativeWind wrapper
3. `tailwind.config.js` - NativeWind preset
4. `global.css` - Tailwind directives
5. `nativewind-env.d.ts` - TypeScript types
6. Updated `_layout.tsx` - Import global.css
7. Updated `tsconfig.json` - Include types

**Start Command:**
```bash
npx expo start --clear
```

---

**Document Version:** 1.0  
**Date:** December 2024  
**Expo SDK:** 54  
**NativeWind Version:** 4.2.1  
**Tailwind CSS Version:** 3.4.19

---

*This guide was created based on real troubleshooting experience and documents both the correct process and common pitfalls to help future developers avoid the same challenges.*

