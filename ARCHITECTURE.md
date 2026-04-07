# Dialogus Architecture

## Architecture Chosen

Dialogus uses a Layered Modular Monolith architecture.

### Explanation

The system is implemented as one deployable backend service (FastAPI) and one frontend web app (Next.js), with clear internal module boundaries:
- API layer: request handling and HTTP contracts
- Application/service layer: ranking and import logic
- Data access layer: SQLAlchemy models and DB session handling
- Presentation layer: frontend pages/components that consume backend APIs

This architecture was chosen because it gives:
- Fast development for an early product iteration
- Low operational complexity compared to microservices
- Clear separation of concerns inside one codebase
- Easy path to scale later (move to Postgres, add cache, split services if needed)

## UML Diagrams

### 1. Use Case Diagram
```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam shadowing false
skinparam usecase {
  BackgroundColor #F5E6D6
  BorderColor #333333
}

actor Reader
actor "Google Identity Provider" as Google

rectangle "Dialogus System Boundary" {
  usecase "Authenticate User" as UC_AUTH
  usecase "Register Account" as UC_SIGNUP
  usecase "Log In with Email Password" as UC_LOGIN
  usecase "Log In with Google" as UC_GOOGLE
  usecase "Browse Library" as UC_BROWSE
  usecase "Search Books" as UC_SEARCH
  usecase "View Book Details" as UC_BOOK
  usecase "View Book Discussions" as UC_DISC
}

Reader --> UC_AUTH : initiates
Reader --> UC_BROWSE : initiates
Reader --> UC_SEARCH : initiates
Reader --> UC_BOOK : initiates
Reader --> UC_DISC : initiates

UC_AUTH .> UC_SIGNUP : <<include>>
UC_AUTH .> UC_LOGIN : <<include>>
UC_AUTH .> UC_GOOGLE : <<include>>
UC_BOOK .> UC_DISC : <<include>>

Google --> UC_GOOGLE : validates identity
@enduml
```

### 2. Component Diagram
```plantuml
@startuml
left to right direction
skinparam componentStyle rectangle
skinparam shadowing false

package "Frontend Subsystem (Next.js)" as FE {
  [Pages] as Pages
  [UI Components] as UI
  [API Client] as APIClient
  [Token Store] as TokenStore

  Pages --> UI : renders
  Pages --> APIClient : calls
  Pages --> TokenStore : read/write token
}

package "Backend Subsystem (FastAPI)" as BE {
  [Auth API] as AuthAPI
  [Discovery API] as DiscoveryAPI
  [Books API] as BooksAPI
  [Security Service] as SecuritySvc
  [Semantic Ranking Service] as RankingSvc
  [Book Import Service] as ImportSvc

  AuthAPI --> SecuritySvc : uses
  DiscoveryAPI --> RankingSvc : uses
  BooksAPI --> RankingSvc : uses
}

database "SQLite / Postgres" as DB
component "Google Identity" as Google
component "Open Library" as OpenLib

APIClient --> AuthAPI : REST/JSON
APIClient --> DiscoveryAPI : REST/JSON
APIClient --> BooksAPI : REST/JSON

AuthAPI --> DB : users CRUD
DiscoveryAPI --> DB : reads books/discussions
BooksAPI --> DB : reads books/discussions
AuthAPI --> Google : verify ID token
ImportSvc --> OpenLib : ingest metadata
ImportSvc --> DB : insert books
@enduml
```

### 3. Package Diagram
```plantuml
@startuml
top to bottom direction
skinparam packageStyle rectangle
skinparam shadowing false

package "backend.app" as ROOT {
  package "main" as MAIN
  package "api" as API
  package "core" as CORE
  package "db" as DBPKG
  package "deps" as DEPS
  package "models" as MODELS
  package "schemas" as SCHEMAS
  package "services" as SERVICES
  package "seed" as SEED
}

MAIN ..> API : depends on
MAIN ..> DBPKG : depends on
MAIN ..> SEED : depends on
API ..> DEPS : depends on
API ..> SCHEMAS : depends on
API ..> MODELS : depends on
API ..> SERVICES : depends on
DEPS ..> CORE : depends on
DEPS ..> DBPKG : depends on
DEPS ..> MODELS : depends on
SERVICES ..> MODELS : depends on
SEED ..> MODELS : depends on
SEED ..> SERVICES : depends on
@enduml
```

### 4. Deployment Diagram
```plantuml
@startuml
left to right direction
skinparam shadowing false

node "Docker Host" as Host {
  node "docker-compose" as Compose {
    artifact "Frontend Container\nNode 20 + Next.js\n:3000" as FE
    artifact "Backend Container\nFastAPI + Uvicorn\n:8000" as BE
  }
}

database "SQLite file / Postgres" as DB
cloud "Google Identity" as Google
cloud "Open Library API" as OpenLib
node "User Browser" as User

User --> FE : HTTP
FE --> BE : REST/JSON
BE --> DB : read/write
BE --> Google : verify OAuth token
BE --> OpenLib : fetch catalog metadata
@enduml
```

### 5. Class Diagram (Domain and Service Classes)
```plantuml
@startuml
skinparam shadowing false
skinparam class {
  BackgroundColor #D9EDF7
  BorderColor #333333
  ArrowColor #333333
}

hide circle

class User {
  +id: int
  +full_name: string
  +email: string
  +hashed_password: string
  +created_at: datetime
  --
  +toUserResponse(): UserResponse
}

class Book {
  +id: int
  +title: string
  +author: string
  +genre: string
  +description: text
  +cover_url: string
  +rating: float
  +publication_year: int
  +language: string
  +pages: int
  --
  +toBookCardResponse(): BookCardResponse
  +toBookDetailResponse(): BookDetailResponse
}

class Discussion {
  +id: int
  +book_id: int
  +title: string
  +excerpt: text
  +replies: int
  +created_at: datetime
  --
  +toDiscussionResponse(): DiscussionResponse
}

class AuthController {
  +signup(payload, db): TokenResponse
  +login(payload, db): TokenResponse
  +google_login(payload, db): TokenResponse
  +me(current_user): UserResponse
}

class BooksController {
  +list_books(q, db): List~BookCardResponse~
  +get_book(book_id, db): BookDetailResponse
}

class DiscoveryController {
  +get_home_data(q, db, current_user): HomeResponse
}

class SecurityService {
  +hash_password(password): string
  +verify_password(plain, hashed): bool
  +create_access_token(subject): string
  +decode_access_token(token): string
}

class SemanticSearchService {
  +rank_books_semantically(books, query): List~Book~
}

class BookImportService {
  +ingest_open_library_books(db, per_subject): void
}

Book "1" *-- "0..*" Discussion : contains
AuthController ..> User : creates/reads
AuthController ..> SecurityService : uses
BooksController ..> Book : reads
BooksController ..> SemanticSearchService : uses
DiscoveryController ..> Book : reads
DiscoveryController ..> Discussion : reads
DiscoveryController ..> SemanticSearchService : uses
BookImportService ..> Book : creates
@enduml
```

### 6. Sequence Diagram (Login and Home Load)
```plantuml
@startuml
skinparam shadowing false

actor Reader
participant Frontend
participant "Auth API" as AuthAPI
participant "Discovery API" as DiscoveryAPI
database Database

Reader -> Frontend : Enter email/password
Frontend -> AuthAPI : POST /api/auth/login
AuthAPI -> Database : Query user by email
Database --> AuthAPI : User row
AuthAPI -> AuthAPI : Verify password\nIssue JWT
AuthAPI --> Frontend : access_token
Frontend -> Frontend : Persist token

Reader -> Frontend : Open Home
Frontend -> DiscoveryAPI : GET /api/discovery/home\nBearer token
DiscoveryAPI -> Database : Load books + discussions
Database --> DiscoveryAPI : Result set

loop For recommendation ranking
  DiscoveryAPI -> DiscoveryAPI : Score and rank books
end

DiscoveryAPI --> Frontend : Home payload
Frontend --> Reader : Render dashboard
@enduml
```

### 7. Activity Diagram (Book Discovery)
```plantuml
@startuml
skinparam shadowing false
skinparam activity {
  BackgroundColor #8CCBEA
  BorderColor #333333
}

start

partition Frontend {
  :Open Home or Browse;
  if (JWT available?) then (yes)
    :Send discovery request;
  else (no)
    :Redirect to Login;
    stop
  endif
}

partition Backend {
  :Validate token;
  :Fetch books and discussions;
  if (Search query present?) then (yes)
    :Run semantic ranking;
  else (no)
    :Run default ranking;
  endif
  :Build response payload;
}

partition Frontend {
  :Render books and discussions;
}

stop
@enduml
```
