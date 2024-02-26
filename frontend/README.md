# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default {
  // other rules...
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    project: ['./tsconfig.json', './tsconfig.node.json'],
    tsconfigRootDir: __dirname,
  },
}
```

- Replace `plugin:@typescript-eslint/recommended` to `plugin:@typescript-eslint/recommended-type-checked` or `plugin:@typescript-eslint/strict-type-checked`
- Optionally add `plugin:@typescript-eslint/stylistic-type-checked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and add `plugin:react/recommended` & `plugin:react/jsx-runtime` to the `extends` list




### Initial Setup

#### Project Setup
https://vitejs.dev/guide/

https://tailwindcss.com/docs/guides/vite

https://tanstack.com/query/latest/docs/framework/react/installation

https://ui.shadcn.com/docs/installation/vite

#### IDE Setup

https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss#recommended-vs-code-settings

You definitely want at least these:

    "editor.quickSuggestions": {
      "strings": "on"
    },
    "files.associations": {
      "*.css": "tailwindcss"
    },
 
 Also This:

    npm install -D prettier prettier-plugin-tailwindcss

prettier.config.js

    // prettier.config.js
    module.exports = {
      plugins: ['prettier-plugin-tailwindcss'],
    }