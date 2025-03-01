import { execFile } from "node:child_process";
import { env } from "./env.js";
import { app } from "electron";
import path from "node:path";
import fs from 'node:fs/promises';
import { exit } from "node:process";

export const startServer = async () => {
  console.log("Starting server");
  const portFile = path.join(app.getPath('userData'), "ports", process.pid.toString());
  await fs.mkdir(path.dirname(portFile), { recursive: true });

  const proc = execFile(env.PYTHON_EXE, ["-I", "main.py", "--port-file", portFile], {
    cwd: env.SERVER_DIR,
    env: {
      ...process.env,
      ...env,
    },
  });
  console.log("subprocess:", proc.pid);
  proc.stdout?.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });
  proc.stderr?.on('data', (data) => {
    console.log(`stderr: ${data}`);
  });
  proc.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    if (code !== 0) {
      exit(code);
    }
  });
  proc.on('exit', (code) => {
    console.log("exit", code);
  });
  process.once('exit', () => proc.kill());

  for(;;) {
    try {
      const text = await fs.readFile(portFile, 'utf-8');
      if (text) {
        const port = parseInt(text);
        console.log("Server started on port", port);
        return port;
      }
    } catch (e) {
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
};
