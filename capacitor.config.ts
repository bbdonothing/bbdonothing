import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.webviewapp',
  appName: 'Webview App',
  webDir: 'www',
  server: {
    androidScheme: 'https'
  }
};

export default config;
