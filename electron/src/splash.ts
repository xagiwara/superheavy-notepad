import { BrowserWindow, protocol } from "electron";
import path from 'node:path';
import fs from 'node:fs/promises';
import mime from 'mime';
import { env } from './env.js';

export const openSplashWindow = () => {
  protocol.handle('webui', async (request) => {
    const urlPath = new URL(request.url).pathname;
    const filePath = path.join(env.WEBUI_PATH, urlPath);

    if (!filePath.startsWith(env.WEBUI_PATH)) {
      return new Response('Forbidden', { status: 403 });
    }

    try {
      const data = await fs.readFile(filePath);
      return new Response(data, {
        headers: {
          'content-type': mime.getType(filePath) ?? 'application/octet-stream',
        },
      });
    } catch (error) {
      return new Response('Not Found', { status: 404 });
    }
  });

  const win = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    // transparent: true,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  win.loadURL('webui://a/splash.html');
  return win;
};
