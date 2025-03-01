import { app, BrowserWindow, dialog } from 'electron';
import { env } from './env.js';
import { startServer } from './server.js';
import { openSplashWindow } from './splash.js';

console.log("config", env);

const createWindow = (port: number) => {
  const win = new BrowserWindow({
  })
  win.menuBarVisible = false;

  win.loadURL(`http://localhost:${port}/index.html`);
  win.webContents.on('will-prevent-unload', (e) => {
    const response = dialog.showMessageBoxSync(win, {
      type: 'question',
      buttons: ['キャンセル', '破棄する'],
      message: '破棄の確認',
      detail: '編集中の内容が破棄されます。よろしいですか？',
    })
    if (response === 1) e.preventDefault();
  });
  return win;
}

(async () => {
  await app.whenReady();
  const splash = openSplashWindow()
  const [port] = await Promise.all([
    startServer(),
    new Promise((resolve) => setTimeout(resolve, 1000)),
  ]);

  const win = createWindow(port);
  win.once('ready-to-show', () => splash.close());
})();
