FROM node:slim

RUN apt-get update \
 && apt-get install -y curl \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app/frontend

ADD frontend/package.json /app/frontend/package.json
ADD frontend/package-lock.json /app/frontend/package-lock.json

RUN npm ci

ADD frontend/env.d.ts /app/frontend/env.d.ts
ADD frontend/eslint.config.ts /app/frontend/eslint.config.ts
ADD frontend/index.html /app/frontend/index.html
ADD frontend/tsconfig.app.json /app/frontend/tsconfig.app.json
ADD frontend/tsconfig.json /app/frontend/tsconfig.json
ADD frontend/tsconfig.node.json /app/frontend/tsconfig.node.json
ADD frontend/vite.config.ts /app/frontend/vite.config.ts
ADD frontend/public /app/frontend/public

CMD ["npm", "run", "dev", "--", "--host"]
