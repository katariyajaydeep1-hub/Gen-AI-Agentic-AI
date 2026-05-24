### 4.1 Retrival Augmented Generation [15 min][Groq][10 Marks]

- Use 19-rag-project\rag-app-v1.11
- Ingest the data
    - python ingest_upgraded.py
- Test retrieval
    - python retrieval.py
- Test the RAG pipeline
    - python rag-with-rrrgv.py
- Make it available as a service
    - (pip install fastapi uvicorn)
    - uvicorn api:app 
    - In the browser 127.0.0.1:8000/ask?q=What%20is%20diabetes?

Deliverables (upload to sharepoint):

- zip file of 19-rag-project\rag-app-v1.11
- transcript of all the above runs in transcript.txt file

--------------------------------------------------------------------------
Break: 11:25 - 11:45
Project execution: 11:45 - 12:00
--------------------------------------------------------------------------


### 4.2 Run the agent demos with OpenAI keys [15 mins][OpenAI][10 Marks]

- Use 21-agents\01-demo-basic and 21-agents\02-demo-basic-autonomous-react
- Upgrade the examples to use OpenAI keys
- Run the examples
- Review the core agentic architecture

Ref: 07-simple-application\infer-from-openai.py

--------------------------------------------------------------------------
Break: 1:40 - 2:25
Project execution: 2:25 - 2:40
--------------------------------------------------------------------------

--------------------------------------------------------------------------
Break: 4:20 - 4:40 
Run 22-tools-deep-dive\01-langchain-tools-and-agents.ipynb: 4:40 - 4:45
--------------------------------------------------------------------------