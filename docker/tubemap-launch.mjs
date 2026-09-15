// TAFFISH 服务监督入口；上游 start() 同时完成 HTTP、WebSocket 和 fs watcher。
import fs from 'node:fs';
if (process.env.TAFFISH_VG_ALLOW_REMOTE !== '1') {
  globalThis.fetch = async () => { throw new Error('Remote URL downloads are disabled; restart vg-tubemap --allow-remote only for trusted URLs.'); };
}
process.on('uncaughtException', error => {
  console.error('tubemap component failure:', error.stack || error);
  process.exit(1);
});
process.on('unhandledRejection', error => {
  console.error('tubemap component failure:', error.stack || error);
  process.exit(1);
});
const { start } = await import('./src/server.mjs');
const service = await start();
fs.writeFileSync('ready.json', JSON.stringify({pid:process.pid, token:process.env.TAFFISH_VG_SESSION_TOKEN, url:service.getUrl()}), {flag:'wx',mode:0o600});
