FROM python:3.9.4-alpine
EXPOSE 80/tcp
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["waitress-serve", "--port=80", "alice_battleship.skill:app"]
