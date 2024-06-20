
  
# API для работы с коллекцией мемов  
Функциональность:  
  
●  GET /memes: Получить список всех мемов.  
  
●  GET /memes/{id}: Получить конкретный мем по его ID.  
  
●  POST /memes: Добавить новый мем (с картинкой и текстом).  
  
●  PUT /memes/{id}: Обновить существующий мем.                                          
  
●  DELETE /memes/{id}: Удалить мем.   
  
## Пререквизиты  
- Docker  

## Подготовка окружения
В директории с проектом cоздайте файл .env. Пример наполнения:  
  
 ENV=dev    POSTGRES_DB=memes    
    POSTGRES_USER=memes_user    
    POSTGRES_PASSWORD=    
    POSTGRES_HOST=db    
    POSTGRES_PORT=5432    
    MINIO_ENDPOINT=http://minio:9000    
    MINIO_ROOT_USER=minioadmin    
    MINIO_ROOT_PASSWORD=minioadmin    
    MINIO_PATH = http://127.0.0.1:9000    
    MINIO_DEFAULT_BUCKETS=media-storage    
    STORAGE_API_URL=http://storageapi:8001  
  
## Установка  
Из директории с проектом запустите команду  
  
 docker compose up -d --buildПубличный сервис доступен по адресу http://127.0.0.1:8000, MinIO по адресам http://127.0.0.1:9001 и http://127.0.0.1:9000  
  
  
## Миграции  
Чтобы создать базу данных, запустите в командной строке  
  
 psql -h localhost -U <POSTGRES_USER>Введите пароль, а затем команду  
  
 create database <POSTGRES_DB>;В директории проекта выполните для применения миграций  
  
 docker exec storageapi alembic upgrade head  
  
## Тестирование  
Для заполнения базы данных тестовыми данными  
  
 docker exec storageapi python database/populate_db.py  
Для запуска тестов  
  
 docker exec storageapi python -m pytest tests/
