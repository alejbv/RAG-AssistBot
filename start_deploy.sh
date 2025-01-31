#! /bin/bash
docker run -itd --rm --name postgres -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=lawyer_db   --mount type=volume,source=pg_data,target=/var/lib/postgresql/data postgres
docker run -itd --rm --name redis -p 6379:6379 -v redis:/data redis/redis-stack:latest