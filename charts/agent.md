```mermaid
flowchart TD
    %% No classDefs needed for GitHub compatibility

    subgraph Reasoning Phase
        B1[LLM Receives Prompt]
        B1 --> B2{LLM Decides if Tool Call is Needed}
    end

    subgraph Tooling Phase
        C1[Run Distance Tool for Locations]
        C1 --> C2[Geocode Destination and Calculate Distance]
        C2 --> C3[Insert Tool Results into Conversation]
    end

    subgraph Final Answer Phase
        D1[LLM Reasons with Context + Tool Outputs]
        D1 --> D2[Assistant Final Response: Facts and Distance]
    end

    %% Linking subgraphs
    A3 --> B1
    B2 -- Yes --> C1
    B2 -- No --> D2
    C3 --> D1
    D1 --> D2    
