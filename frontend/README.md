# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

## API Environment

Frontend API endpoint is controlled by environment variables:

- `VITE_API_BASE_URL`: used by axios/fetch requests
- `VITE_API_PROXY_TARGET`: used by Vite `/api` dev proxy

Available presets:

- `.env.development` (local backend): `http://localhost:8000`
- `.env.frp` (FRP/public test): `http://143.198.217.196:30880`

Run commands:

```bash
# local mode (default)
npm run dev

# frp mode
npm run dev -- --mode frp

# build with frp config
npm run build -- --mode frp
```
