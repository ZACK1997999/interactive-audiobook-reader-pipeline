export default {
  testDir: './browser_tests',
  timeout: 30_000,
  use: { browserName: 'chromium', headless: true },
  reporter: 'line',
};
