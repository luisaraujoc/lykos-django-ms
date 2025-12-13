verifique os `.env.example` e `docker-compose.example.yaml` para ver as variáveis de ambiente necessárias.

além desses dois, o `jwt-middleware.example.yaml` para alinhar a mesma key jwt do `.env` nele.

crie arquivos tirando o `example` do nome e ajuste as variáveis de ambiente necessárias e faça as modificações nos arquivos novos, esses não serão enviados no seus commits.

para iniciar os containers use o comando `docker compose up -d`.

---

A espera de estrutura de pastas que estão previstas para esse monorepo é:
```bash
lykos-django/
├── docker-compose.yml                 
├── .env                               
├── traefik/                           
│   ├── traefik.yml                    
│   ├── dynamic/                       
│   │   ├── jwt-middleware.yml
│   │   └── rate-limit.yml
│   └── acme.json                      
│
├── services/
│   ├── auth-service/                  ← Login, cadastro, JWT
│   │   ├── manage.py
│   │   ├── auth_service/
│   │   │   ├── settings.py
│   │   │   ├── urls.py
│   │   │   └── asgi.py
│   │   └── users/
│   │       ├── models.py
│   │       └── views.py
│   │
│   ├── profile-service/               ← Freelancer, portfólio, uploads
│   ├── catalog-service/               ← Pacotes, categorias
│   ├── booking-service/               ← Contratações, AbacatePay, agendamentos
│   ├── review-service/                ← Avaliações
│   └── notification-service/         ← Emails, futuras push
│
├── shared/                            ← Pacote Python compartilhado
│   ├── pyproject.toml
│   └── shared/
│       ├── __init__.py
│       ├── constants.py
│       ├── enums.py                   
│       ├── utils.py
│       ├── middlewares.py
│       └── utils.py
│
├── minio/                             ← Armazenamento de arquivos
├── postgres/                          ← Volumes de dados
└── docs/                              ← OpenAPI agregado
```
