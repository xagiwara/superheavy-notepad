import path from 'node:path';
import dotenv from 'dotenv';
dotenv.config();

export const env = {
  WEBUI_PATH: path.resolve(process.env.WEBUI_PATH ?? './data/ui'),
  HF_HUB_CACHE: path.resolve(process.env.HF_HUB_CACHE ?? './data/models/hf'),
  FINETUNED_DIR: path.resolve(process.env.FINETUNED_DIR ?? './data/models/finetuned'),
  PYTHONHOME: path.resolve(process.env.PYTHONHOME ?? './data/python/site-packages'),
  PYTHON_EXE: path.resolve(process.env.PYTHON_EXE ?? './data/python/python.exe'),
  SERVER_DIR: path.resolve(process.env.SERVER_DIR ?? './data/server'),
};
