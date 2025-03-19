module.exports = {
  content: [
    // ... 기존 content 설정 ...
  ],
  theme: {
    // ... 기존 theme 설정 ...
  },
  plugins: [
    require('tailwind-scrollbar')({ nocompatible: true }),
    // ... 다른 플러그인들 ...
  ],
} 