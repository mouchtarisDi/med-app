import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    include: ['tests/auth-provider.test.tsx', 'tests/login-page.test.tsx'],
    setupFiles: ['tests/setup-react.ts'],
  },
});
