# Webview App Shell

This repository contains a minimal Capacitor setup for wrapping web content inside native iOS and Android webviews. The static assets live in `src/` and are copied to `www/` for bundling into the native shells.

## Getting started
1. Install dependencies:
   ```bash
   npm install
   ```
2. Build the web assets into `www/`:
   ```bash
   npm run build
   ```
3. Initialize the native projects (only needed the first time):
   ```bash
   npx cap add android
   npx cap add ios
   ```
4. Sync and launch the platform projects:
   ```bash
   npm run android  # opens Android Studio
   npm run ios      # opens Xcode
   ```

## How it works
- `capacitor.config.ts` configures the app ID, name, and the `www` directory that holds the built assets.
- The `src/` folder contains a lightweight HTML/CSS/JS experience that will render inside the webview on both platforms.
- The `build` script copies everything from `src/` into `www/` so that Capacitor can package the assets into the native projects.

## Development tips
- Modify the HTML, CSS, or JS in `src/` and rebuild with `npm run build` before syncing.
- If you change the app ID or name, update it in `capacitor.config.ts` before running `npx cap sync`.
- Use Android Studio or Xcode simulators/emulators to verify the webview renders correctly on each platform.
