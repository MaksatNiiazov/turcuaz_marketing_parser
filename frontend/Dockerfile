FROM node:22-alpine

WORKDIR /workspace

COPY turkuaz-ui/package.json ./turkuaz-ui/package.json
COPY turkuaz-ui/src ./turkuaz-ui/src
COPY marketing_parser/frontend/.npmrc ./marketing_parser/frontend/.npmrc
COPY marketing_parser/frontend/package.json marketing_parser/frontend/package-lock.json* ./marketing_parser/frontend/

WORKDIR /workspace/marketing_parser/frontend
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
RUN ln -s /workspace/marketing_parser/frontend/node_modules /workspace/turkuaz-ui/node_modules

COPY marketing_parser/frontend ./

EXPOSE 7503

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "7503"]
