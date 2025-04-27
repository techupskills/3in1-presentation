```mermaid
flowchart TD
    %% No classDefs because GitHub might not like extra styling unless needed

    A[User Prompt] --> B[Search ChromaDB for RAG Retrieval]
    B --> C[LLM Receives Prompt and Context]
    C --> D{LLM Decides if Tool Needed}
    
    D -- Yes --> E[Run Tool for Locations]
    D -- No --> L[Generate Direct Answer]

    E --> F[Geocode and Calculate Distance]
    F --> G[Insert Tool Results into Conversation]
    G --> H[LLM Reasons with Context and Tools]
    H --> I[Assistant Final Response]

    L --> I
