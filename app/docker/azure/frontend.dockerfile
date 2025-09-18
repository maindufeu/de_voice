FROM node:lts-alpine

WORKDIR /app/frontend

# Copiar los archivos de configuración de dependencias
COPY ./app/ui/package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código fuente
COPY ./app/ui ./

COPY ./app/ui/.env ./

# Cargar las variables de entorno
ENV $(cat .env | xargs)


EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
